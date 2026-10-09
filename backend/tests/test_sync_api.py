from __future__ import annotations

import os
from io import BytesIO
from typing import Any

os.environ["APP_ENV"] = "test"
os.environ["FRONTEND_URL"] = "http://localhost:3000"
os.environ["SUPABASE_URL"] = "http://127.0.0.1:54321"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "dummy-test-key"

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.core.auth import StaffPrincipal, require_staff
from app.main import app
from app.api.v1.endpoints import sync as sync_endpoint
from tests.test_sync_service import MockSupabase

HEADERS = ["No", "Kode Prodi", "Program Studi", "NIM", "Nama", "Sertifikasi MOS", "Sertifikasi MCF", "Title Microsoft"]


def create_wisuda_bytes(rows: list[list[Any]]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Wisuda"
    ws.append(HEADERS)
    for r in rows:
        ws.append(r)
    buf = BytesIO()
    wb.save(buf)
    wb.close()
    return buf.getvalue()


@pytest.fixture
def auth_client():
    client = TestClient(app)
    app.dependency_overrides[require_staff] = lambda: StaffPrincipal(
        user_id="synthetic-user-id",
        display_name="Petugas Uji",
        role="staff",
    )
    yield client
    app.dependency_overrides.pop(require_staff, None)


@pytest.fixture
def setup_supabase_mock(monkeypatch):
    sb = MockSupabase()
    # Populate active imports
    sb.storage["data_imports"].extend([
        {
            "id": "sitasi-active-uuid",
            "data_type": "SITASI",
            "status": "COMPLETED",
            "is_active": True,
            "created_at": "2026-10-01T00:00:00Z",
        },
        {
            "id": "certiport-active-uuid",
            "data_type": "CERTIPORT",
            "status": "COMPLETED",
            "is_active": True,
            "created_at": "2026-10-01T00:00:00Z",
        },
    ])
    # SITASI row
    sb.storage["sitasi_data"].append({
        "id": 1,
        "import_id": "sitasi-active-uuid",
        "source_row": 2,
        "nim": "209900001",
        "nama": "CONTOH SISWA",
        "nama_normalized": "CONTOH SISWA",
        "sertifikasi": "MOS",
        "sub_program": "Word",
        "nilai": 850,
        "status": "LULUS",
    })
    # Certiport row
    sb.storage["certiport_data"].append({
        "id": 100,
        "import_id": "certiport-active-uuid",
        "source_row": 2,
        "full_name": "CONTOH SISWA",
        "full_name_normalized": "CONTOH SISWA",
        "program_name": "Microsoft Office Specialist",
        "certification_name": "Word",
        "score": 850,
        "result": "Pass",
    })

    monkeypatch.setattr(sync_endpoint, "get_supabase", lambda: sb)
    return sb


# ---------------------------------------------------------------------------
# Unauthenticated tests
# ---------------------------------------------------------------------------

def test_sync_endpoints_require_auth():
    unauth_client = TestClient(app)
    # Test POST /sync without auth
    resp = unauth_client.post("/api/v1/sync", files={"file": ("wisuda.xlsx", b"dummy")})
    assert resp.status_code == 401

    # Test GET /sync without auth
    resp = unauth_client.get("/api/v1/sync")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/sync tests
# ---------------------------------------------------------------------------

def test_start_sync_rejects_non_xlsx(auth_client, setup_supabase_mock):
    resp = auth_client.post("/api/v1/sync", files={"file": ("data.csv", b"a,b,c")})
    assert resp.status_code == 400
    assert "xlsx" in resp.json()["detail"].lower()


def test_start_sync_success(auth_client, setup_supabase_mock):
    content = create_wisuda_bytes([
        [1, "55201", "TI", "209900001", "CONTOH SISWA", "", "", ""],
    ])

    resp = auth_client.post(
        "/api/v1/sync",
        files={"file": ("wisuda_2026.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "COMPLETED"
    assert data["total_rows"] == 1
    assert data["total_valid"] == 1
    assert data["sitasi_import_id"] == "sitasi-active-uuid"
    assert data["certiport_import_id"] == "certiport-active-uuid"


def test_start_sync_missing_active_batch_returns_400(auth_client, setup_supabase_mock):
    # Empty data imports
    setup_supabase_mock.storage["data_imports"] = []

    content = create_wisuda_bytes([[1, "55201", "TI", "209900001", "CONTOH SISWA", "", "", ""]])
    resp = auth_client.post("/api/v1/sync", files={"file": ("wisuda.xlsx", content)})
    assert resp.status_code == 400
    assert "aktif belum lengkap" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# GET /api/v1/sync (history)
# ---------------------------------------------------------------------------

def test_get_sync_history(auth_client, setup_supabase_mock):
    content = create_wisuda_bytes([[1, "55201", "TI", "209900001", "CONTOH SISWA", "", "", ""]])
    auth_client.post("/api/v1/sync", files={"file": ("wisuda.xlsx", content)})

    resp = auth_client.get("/api/v1/sync?page=1&limit=10")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert len(body["data"]["items"]) == 1


# ---------------------------------------------------------------------------
# GET /api/v1/sync/{session_id}
# ---------------------------------------------------------------------------

def test_get_session_summary_and_not_found(auth_client, setup_supabase_mock):
    content = create_wisuda_bytes([[1, "55201", "TI", "209900001", "CONTOH SISWA", "", "", ""]])
    post_resp = auth_client.post("/api/v1/sync", files={"file": ("wisuda.xlsx", content)})
    session_id = post_resp.json()["data"]["session_id"]

    # Valid session
    resp = auth_client.get(f"/api/v1/sync/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == session_id

    # Non-existent session
    resp = auth_client.get("/api/v1/sync/non-existent-uuid")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/sync/{session_id}/results
# ---------------------------------------------------------------------------

def test_get_session_results_with_filter(auth_client, setup_supabase_mock):
    content = create_wisuda_bytes([
        [1, "55201", "TI", "209900001", "CONTOH SISWA", "", "", ""],
        [2, "55201", "TI", "999999999", "TIDAK ADA", "", "", ""],
    ])
    post_resp = auth_client.post("/api/v1/sync", files={"file": ("wisuda.xlsx", content)})
    session_id = post_resp.json()["data"]["session_id"]

    # All results
    resp = auth_client.get(f"/api/v1/sync/{session_id}/results")
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 2

    # Filter by status VALID
    resp = auth_client.get(f"/api/v1/sync/{session_id}/results?status=VALID")
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1
    assert resp.json()["data"]["items"][0]["nim"] == "209900001"

    # Search by query
    resp = auth_client.get(f"/api/v1/sync/{session_id}/results?search=TIDAK")
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1
    assert resp.json()["data"]["items"][0]["nim"] == "999999999"


# ---------------------------------------------------------------------------
# GET /api/v1/sync/{session_id}/results/{result_id}
# ---------------------------------------------------------------------------

def test_get_result_detail_with_evidence(auth_client, setup_supabase_mock):
    content = create_wisuda_bytes([[1, "55201", "TI", "209900001", "CONTOH SISWA", "", "", ""]])
    post_resp = auth_client.post("/api/v1/sync", files={"file": ("wisuda.xlsx", content)})
    session_id = post_resp.json()["data"]["session_id"]

    results_resp = auth_client.get(f"/api/v1/sync/{session_id}/results")
    result_id = results_resp.json()["data"]["items"][0]["id"]

    detail_resp = auth_client.get(f"/api/v1/sync/{session_id}/results/{result_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()["data"]
    assert detail["id"] == result_id
    assert detail["nim"] == "209900001"
    assert "evidence" in detail
    assert len(detail["evidence"]) >= 1
