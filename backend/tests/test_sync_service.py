from __future__ import annotations

from io import BytesIO
from typing import Any
import uuid

import pytest
from openpyxl import Workbook

from app.services.matching_service import VALID, PERLU_VERIFIKASI, TIDAK_LULUS, DATA_TIDAK_DITEMUKAN
from app.services.sync_service import (
    SyncBatchMissingError,
    SyncExecutionError,
    SyncSessionNotFoundError,
    create_and_execute_sync,
    dedupe_evidence_for_display,
    get_sync_result_detail,
    get_sync_session,
    list_sync_results,
    list_sync_sessions,
)

HEADERS = ["No", "Kode Prodi", "Program Studi", "NIM", "Nama", "Sertifikasi MOS", "Sertifikasi MCF", "Title Microsoft"]


def create_wisuda_file(rows: list[list[Any]]) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Wisuda"
    ws.append(HEADERS)
    for r in rows:
        ws.append(r)
    buf = BytesIO()
    wb.save(buf)
    wb.close()
    buf.seek(0)
    return buf


class MockQuery:
    def __init__(self, client: MockSupabase, table_name: str):
        self.client = client
        self.table_name = table_name
        self._filters: list[tuple[str, Any, Any]] = []
        self._or_filter: str | None = None
        self._order: tuple[str, bool] | None = None
        self._range: tuple[int, int] | None = None
        self._limit: int | None = None
        self._count_mode: str | None = None
        self._update_data: dict | None = None

    def select(self, columns: str = "*", count: str | None = None):
        self._count_mode = count
        return self

    def insert(self, data: dict | list[dict]):
        if self.client.fail_insert_table == self.table_name:
            raise RuntimeError(f"Simulated DB failure on insert to {self.table_name}")
        items = data if isinstance(data, list) else [data]
        for item in items:
            self.client.storage[self.table_name].append(dict(item))
        return self

    def update(self, data: dict):
        self._update_data = data
        return self

    def eq(self, column: str, value: Any):
        self._filters.append(("eq", column, value))
        return self

    def in_(self, column: str, values: list[Any]):
        self._filters.append(("in", column, list(values)))
        return self

    def order(self, column: str, desc: bool = False):
        self._order = (column, desc)
        return self

    def range(self, start: int, end: int):
        self._range = (start, end)
        return self

    def limit(self, count: int):
        self._limit = count
        return self

    def or_(self, expr: str):
        self._or_filter = expr
        return self

    def execute(self):
        rows = self.client.storage.get(self.table_name, [])

        if self._update_data is not None:
            updated_count = 0
            for r in rows:
                match = True
                for op, col, val in self._filters:
                    if op == "eq" and r.get(col) != val:
                        match = False
                        break
                if match:
                    r.update(self._update_data)
                    updated_count += 1
            return MockResponse(data=[self._update_data], count=updated_count)

        filtered = []
        for r in rows:
            match = True
            for op, col, val in self._filters:
                if op == "eq" and r.get(col) != val:
                    match = False
                    break
                if op == "in" and r.get(col) not in val:
                    match = False
                    break
            if match and self._or_filter:
                # Simple parser for "nim.ilike.%s%,nama_wisuda.ilike.%s%"
                term = self._or_filter.split("%")[1].lower()
                nim_val = str(r.get("nim", "")).lower()
                nama_val = str(r.get("nama_wisuda", "")).lower()
                if term not in nim_val and term not in nama_val:
                    match = False
            if match:
                filtered.append(r)

        total_count = len(filtered)

        if self._order:
            col, desc = self._order
            filtered.sort(key=lambda x: str(x.get(col, "")), reverse=desc)

        if self._range:
            start, end = self._range
            filtered = filtered[start : end + 1]
        elif self._limit:
            filtered = filtered[: self._limit]

        return MockResponse(data=filtered, count=total_count if self._count_mode else None)


class MockResponse:
    def __init__(self, data: Any = None, count: int | None = None):
        self.data = data
        self.count = count


class MockSupabase:
    def __init__(self):
        self.storage: dict[str, list[dict]] = {
            "data_imports": [],
            "sitasi_data": [],
            "certiport_data": [],
            "sync_sessions": [],
            "sync_results": [],
            "sync_evidence": [],
            "review_audit": [],
        }
        self.fail_insert_table: str | None = None

    def table(self, table_name: str):
        return MockQuery(self, table_name)


# ---------------------------------------------------------------------------
# Fixture data
# ---------------------------------------------------------------------------

@pytest.fixture
def populated_supabase():
    sb = MockSupabase()
    # Active SITASI batch
    sit_batch_id = "batch-sitasi-1"
    sb.storage["data_imports"].append({
        "id": sit_batch_id,
        "data_type": "SITASI",
        "status": "COMPLETED",
        "is_active": True,
        "created_at": "2026-10-01T00:00:00Z",
    })
    # Active Certiport batch
    cert_batch_id = "batch-certiport-1"
    sb.storage["data_imports"].append({
        "id": cert_batch_id,
        "data_type": "CERTIPORT",
        "status": "COMPLETED",
        "is_active": True,
        "created_at": "2026-10-01T00:00:00Z",
    })

    # SITASI records
    sb.storage["sitasi_data"].extend([
        {
            "id": 1,
            "import_id": sit_batch_id,
            "source_row": 2,
            "nim": "209900001",
            "nama": "MAHASISWA SATU",
            "nama_normalized": "MAHASISWA SATU",
            "sertifikasi": "MOS",
            "sub_program": "Word",
            "nilai": 800,
            "status": "LULUS",
        },
        {
            "id": 2,
            "import_id": sit_batch_id,
            "source_row": 3,
            "nim": "209900002",
            "nama": "MAHASISWA DUA",
            "nama_normalized": "MAHASISWA DUA",
            "sertifikasi": "MOS",
            "sub_program": "Excel",
            "nilai": 500,
            "status": "TIDAK LULUS",
        },
    ])

    # Certiport records
    sb.storage["certiport_data"].extend([
        {
            "id": 101,
            "import_id": cert_batch_id,
            "source_row": 2,
            "full_name": "MAHASISWA SATU",
            "full_name_normalized": "MAHASISWA SATU",
            "program_name": "Microsoft Office Specialist",
            "certification_name": "Word",
            "score": 800,
            "result": "Pass",
        },
        {
            "id": 102,
            "import_id": cert_batch_id,
            "source_row": 3,
            "full_name": "MAHASISWA DUA",
            "full_name_normalized": "MAHASISWA DUA",
            "program_name": "Microsoft Office Specialist",
            "certification_name": "Excel",
            "score": 500,
            "result": "Fail",
        },
    ])

    return sb


# ---------------------------------------------------------------------------
# Test: Success flow
# ---------------------------------------------------------------------------

def test_sync_success_creates_session_and_records(populated_supabase):
    file_buf = create_wisuda_file([
        [1, "55201", "TI", "209900001", "MAHASISWA SATU", "", "", ""],
        [2, "55201", "TI", "209900002", "MAHASISWA DUA", "", "", ""],
        [3, "55201", "TI", "999999999", "TIDAK ADA", "", "", ""],
    ])

    res = create_and_execute_sync(
        supabase=populated_supabase,
        file_obj=file_buf,
        file_name="wisuda_ok.xlsx",
        max_upload_bytes=10 * 1024 * 1024,
        user_id="user-123",
    )

    assert res["status"] == "COMPLETED"
    assert res["total_rows"] == 3
    assert res["total_valid"] == 1
    assert res["total_review"] == 1  # TIDAK_LULUS counts as review/action needed
    assert res["total_not_found"] == 1
    assert res["sitasi_import_id"] == "batch-sitasi-1"
    assert res["certiport_import_id"] == "batch-certiport-1"

    # Verify session persisted
    sessions = populated_supabase.storage["sync_sessions"]
    assert len(sessions) == 1
    assert sessions[0]["status"] == "COMPLETED"
    assert sessions[0]["completed_at"] is not None

    # Verify results persisted
    results = populated_supabase.storage["sync_results"]
    assert len(results) == 3
    m1 = next(r for r in results if r["nim"] == "209900001")
    assert m1["validation_status"] == VALID
    assert m1["mos_status"] == VALID
    assert m1["needs_review"] is False

    m2 = next(r for r in results if r["nim"] == "209900002")
    assert m2["validation_status"] == TIDAK_LULUS
    assert m2["mos_status"] == TIDAK_LULUS
    assert m2["needs_review"] is True

    m3 = next(r for r in results if r["nim"] == "999999999")
    assert m3["validation_status"] == DATA_TIDAK_DITEMUKAN
    assert m3["needs_review"] is True

    # Verify evidence persisted
    evidence = populated_supabase.storage["sync_evidence"]
    assert len(evidence) >= 2


# ---------------------------------------------------------------------------
# Test: Missing active batch raises SyncBatchMissingError
# ---------------------------------------------------------------------------

def test_sync_fails_when_active_batch_missing():
    sb = MockSupabase()  # empty imports
    file_buf = create_wisuda_file([[1, "55201", "TI", "209900001", "MAHASISWA SATU", "", "", ""]])

    with pytest.raises(SyncBatchMissingError) as exc_info:
        create_and_execute_sync(sb, file_buf, "wisuda.xlsx", 10 * 1024 * 1024)
    assert "SITASI" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Test: Mid-process failure sets session to FAILED
# ---------------------------------------------------------------------------

def test_sync_mid_process_failure_updates_session_to_failed(populated_supabase):
    populated_supabase.fail_insert_table = "sync_results"
    file_buf = create_wisuda_file([[1, "55201", "TI", "209900001", "MAHASISWA SATU", "", "", ""]])

    with pytest.raises(SyncExecutionError):
        create_and_execute_sync(
            supabase=populated_supabase,
            file_obj=file_buf,
            file_name="wisuda_fail.xlsx",
            max_upload_bytes=10 * 1024 * 1024,
        )

    # Session exists and is marked FAILED
    sessions = populated_supabase.storage["sync_sessions"]
    assert len(sessions) == 1
    assert sessions[0]["status"] == "FAILED"
    assert sessions[0]["error_message"] is not None


# ---------------------------------------------------------------------------
# Test: Retry after failure succeeds
# ---------------------------------------------------------------------------

def test_sync_retry_after_failure_succeeds(populated_supabase):
    populated_supabase.fail_insert_table = "sync_results"
    file_buf = create_wisuda_file([[1, "55201", "TI", "209900001", "MAHASISWA SATU", "", "", ""]])

    with pytest.raises(SyncExecutionError):
        create_and_execute_sync(populated_supabase, file_buf, "wisuda.xlsx", 10 * 1024 * 1024)

    # Now fix the issue and retry
    populated_supabase.fail_insert_table = None
    file_buf.seek(0)
    retry_res = create_and_execute_sync(populated_supabase, file_buf, "wisuda.xlsx", 10 * 1024 * 1024)

    assert retry_res["status"] == "COMPLETED"
    assert retry_res["total_valid"] == 1
    # We now have 2 sessions in history: 1 FAILED, 1 COMPLETED
    sessions = populated_supabase.storage["sync_sessions"]
    assert len(sessions) == 2
    assert sessions[0]["status"] == "FAILED"
    assert sessions[1]["status"] == "COMPLETED"


# ---------------------------------------------------------------------------
# Test: Historical consistency when new active batch arrives
# ---------------------------------------------------------------------------

def test_sync_historical_consistency_when_new_master_active(populated_supabase):
    file_buf = create_wisuda_file([[1, "55201", "TI", "209900001", "MAHASISWA SATU", "", "", ""]])
    res = create_and_execute_sync(populated_supabase, file_buf, "wisuda.xlsx", 10 * 1024 * 1024)
    session_id = res["session_id"]

    # Now simulate a new batch being activated
    new_sitasi_id = "batch-sitasi-2"
    for imp in populated_supabase.storage["data_imports"]:
        if imp["data_type"] == "SITASI":
            imp["is_active"] = False
    populated_supabase.storage["data_imports"].append({
        "id": new_sitasi_id,
        "data_type": "SITASI",
        "status": "COMPLETED",
        "is_active": True,
        "created_at": "2026-10-02T00:00:00Z",
    })

    # Query the old session: snapshot IDs remain unchanged!
    session = get_sync_session(populated_supabase, session_id)
    assert session["sitasi_import_id"] == "batch-sitasi-1"
    assert session["status"] == "COMPLETED"

    # Query results of the old session: they still point to the old session data!
    results = list_sync_results(populated_supabase, session_id)
    assert results["total"] == 1
    assert results["items"][0]["nim"] == "209900001"
    assert results["items"][0]["validation_status"] == VALID


# ---------------------------------------------------------------------------
# Test: List, pagination, and filtering
# ---------------------------------------------------------------------------

def test_list_sync_results_pagination_and_filtering(populated_supabase):
    file_buf = create_wisuda_file([
        [1, "55201", "TI", "209900001", "MAHASISWA SATU", "", "", ""],
        [2, "55201", "TI", "209900002", "MAHASISWA DUA", "", "", ""],
        [3, "55201", "TI", "999999999", "TIDAK ADA", "", "", ""],
    ])
    res = create_and_execute_sync(populated_supabase, file_buf, "wisuda.xlsx", 10 * 1024 * 1024)
    session_id = res["session_id"]

    # All items
    all_res = list_sync_results(populated_supabase, session_id)
    assert all_res["total"] == 3
    assert len(all_res["items"]) == 3

    # Filter status VALID
    valid_res = list_sync_results(populated_supabase, session_id, status="VALID")
    assert valid_res["total"] == 1
    assert valid_res["items"][0]["nim"] == "209900001"

    # Filter needs_review=True
    review_res = list_sync_results(populated_supabase, session_id, needs_review=True)
    assert review_res["total"] == 2

    # Search by NIM
    search_nim = list_sync_results(populated_supabase, session_id, search="209900002")
    assert search_nim["total"] == 1
    assert search_nim["items"][0]["nama_wisuda"] == "MAHASISWA DUA"

    # Pagination: limit 1, page 2
    paged = list_sync_results(populated_supabase, session_id, page=2, limit=1)
    assert paged["page"] == 2
    assert paged["limit"] == 1
    assert len(paged["items"]) == 1
    assert paged["items"][0]["source_row"] == 3


# ---------------------------------------------------------------------------
# Test: Detail and evidence query
# ---------------------------------------------------------------------------

def test_get_sync_result_detail_includes_evidence(populated_supabase):
    file_buf = create_wisuda_file([[1, "55201", "TI", "209900001", "MAHASISWA SATU", "", "", ""]])
    res = create_and_execute_sync(populated_supabase, file_buf, "wisuda.xlsx", 10 * 1024 * 1024)
    session_id = res["session_id"]

    results = list_sync_results(populated_supabase, session_id)
    result_id = results["items"][0]["id"]

    detail = get_sync_result_detail(populated_supabase, session_id, result_id)
    assert detail["id"] == result_id
    assert detail["nim"] == "209900001"
    assert "evidence" in detail
    assert len(detail["evidence"]) >= 1
    ev = detail["evidence"][0]
    assert ev["category"] == "MOS"
    assert ev["exam"] == "Word"


def test_dedupe_evidence_prefers_pass():
    """Bukti ganda satu sub-ujian: yang lulus ditampilkan, sisanya dihitung."""
    rows = [
        {"id": "e1", "category": "MOS", "exam": "Word", "certiport_status": "FAIL", "evidence_status": PERLU_VERIFIKASI},
        {"id": "e2", "category": "MOS", "exam": "Word", "certiport_status": "PASS", "evidence_status": PERLU_VERIFIKASI},
        {"id": "e3", "category": "MOS", "exam": "Excel", "certiport_status": "FAIL", "evidence_status": PERLU_VERIFIKASI},
    ]
    out = dedupe_evidence_for_display(rows)
    assert len(out) == 2
    word = next(e for e in out if e["exam"] == "Word")
    assert word["id"] == "e2"
    assert word["duplicate_count"] == 1
    assert word["duplicate_ids"] == ["e1"]
    excel = next(e for e in out if e["exam"] == "Excel")
    assert excel["duplicate_count"] == 0


def test_detail_resolves_source_row_and_file_name(populated_supabase):
    """Detail evidence menunjuk baris xlsx + nama file (bukan id database)."""
    sb = populated_supabase
    sb.storage["data_imports"][0]["file_name"] = "data_sitasi.xlsx"
    sb.storage["data_imports"][1]["file_name"] = "data_certiport.xlsx"

    session_id = "sess-src-ref"
    result_id = "res-src-ref"
    sb.storage["sync_sessions"].append({"id": session_id, "status": "COMPLETED"})
    sb.storage["sync_results"].append({
        "id": result_id, "sync_session_id": session_id, "source_row": 2,
        "nim": "209900001", "nama_wisuda": "MAHASISWA SATU", "nama_sitasi": None,
        "mos_programs": {}, "mcf_programs": {},
    })
    # Dua bukti ganda MOS·Word: FAIL (id 102) dan PASS (id 101, baris xlsx 2).
    sb.storage["sync_evidence"].extend([
        {"id": "ev-fail", "result_id": result_id, "category": "MOS", "exam": "Word",
         "sitasi_row_id": None, "certiport_row_id": 102, "match_method": "M",
         "match_score": 500, "evidence_status": PERLU_VERIFIKASI, "reason": "FAIL",
         "created_at": "2026-10-13T00:00:00Z"},
        {"id": "ev-pass", "result_id": result_id, "category": "MOS", "exam": "Word",
         "sitasi_row_id": 1, "certiport_row_id": 101, "match_method": "M",
         "match_score": 800, "evidence_status": PERLU_VERIFIKASI, "reason": "PASS",
         "created_at": "2026-10-13T00:00:01Z"},
    ])

    detail = get_sync_result_detail(sb, session_id, result_id)
    assert len(detail["evidence"]) == 1
    ev = detail["evidence"][0]
    assert ev["id"] == "ev-pass"
    assert ev["duplicate_count"] == 1
    assert ev["certiport_source_row"] == 2
    assert ev["certiport_file_name"] == "data_certiport.xlsx"
    assert ev["sitasi_source_row"] == 2
    assert ev["sitasi_file_name"] == "data_sitasi.xlsx"
