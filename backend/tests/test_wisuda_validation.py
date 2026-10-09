from __future__ import annotations

import os
from io import BytesIO

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("SUPABASE_URL", "http://127.0.0.1:54321")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "dummy-test-key")

from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.core.auth import require_staff
from app.main import app
from app.services.wisuda_validation_service import validate_wisuda_workbook

TEMPLATE_HEADERS = [
    "No",
    "Kode Prodi",
    "Program Studi",
    "NIM",
    "Nama",
    "Sertifikasi MOS",
    "Sertifikasi MCF",
    "Title Microsoft",
]


def workbook_bytes(headers=TEMPLATE_HEADERS, rows=()):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Wisuda"
    worksheet.append(headers)
    for row in rows:
        worksheet.append(row)
    output = BytesIO()
    workbook.save(output)
    workbook.close()
    return output.getvalue()


def test_validate_preserves_text_leading_zeroes_and_reports_duplicate_and_blank_rows():
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Wisuda"
    sheet.append(TEMPLATE_HEADERS)
    sheet.append([1, "55201", "Informatika", 123, "Anonim Satu", "tetap", "jangan sentuh", "Title"])
    sheet["D2"].number_format = "00000"
    sheet.append([2, "55201", "Informatika", "00123", "Anonim Dua", None, None, None])
    sheet.append([None] * 8)
    output = BytesIO()
    workbook.save(output)
    workbook.close()

    result = validate_wisuda_workbook(BytesIO(output.getvalue()), "wisuda.xlsx", 10 * 1024 * 1024)

    assert result["student_count"] == 2
    assert result["empty_row_count"] == 1
    assert result["empty_rows"] == [4]
    assert result["columns"] == TEMPLATE_HEADERS
    assert result["layout_matches_template"] is True
    assert [(issue["source_row"], issue["code"]) for issue in result["issues"]] == [(3, "DUPLICATE_NIM")]
    assert "00123" not in str(result)


def test_validate_reports_missing_values_and_numeric_precision_without_values():
    data = workbook_bytes(rows=[
        [1, "55201", "Informatika", 1234567890123456, "", None, None, None],
    ])

    result = validate_wisuda_workbook(BytesIO(data), "wisuda.xlsx", 10 * 1024 * 1024)

    assert result["is_valid"] is False
    assert [issue["code"] for issue in result["issues"]] == ["INVALID_NIM", "REQUIRED_VALUE"]
    assert "1234567890123456" not in str(result)


def test_validate_requires_nim_and_name_headers_and_flags_empty_sheet():
    missing = validate_wisuda_workbook(
        BytesIO(workbook_bytes(headers=["No", "Nama"])),
        "wisuda.xlsx",
        10 * 1024 * 1024,
    )
    empty = validate_wisuda_workbook(BytesIO(workbook_bytes()), "wisuda.xlsx", 10 * 1024 * 1024)

    assert missing["missing_columns"] == ["NIM"]
    assert empty["student_count"] == 0
    assert empty["issues"][0]["code"] == "EMPTY_FILE"


def test_validate_endpoint_requires_staff_and_returns_master_sources(monkeypatch):
    from app.api.v1.endpoints import sync as sync_endpoint

    client = TestClient(app)
    data = workbook_bytes(rows=[[1, "55201", "Informatika", "00123", "Anonim", None, None, None]])
    unauthenticated = client.post(
        "/api/v1/sync/validate",
        files={"file": ("wisuda.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert unauthenticated.status_code == 401

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[require_staff] = lambda: object()
    monkeypatch.setattr(sync_endpoint, "get_supabase", lambda: object())
    monkeypatch.setattr(
        sync_endpoint,
        "get_active_import_summary",
        lambda _client, data_type: {"data_type": data_type, "status": "COMPLETED"},
    )
    try:
        response = client.post(
            "/api/v1/sync/validate",
            files={"file": ("wisuda.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)

    assert response.status_code == 200
    result = response.json()["data"]
    assert result["is_valid"] is True
    assert result["student_count"] == 1
    assert result["active_masters"]["sitasi"]["data_type"] == "SITASI"
    assert result["active_masters"]["certiport"]["data_type"] == "CERTIPORT"
