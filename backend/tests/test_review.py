from __future__ import annotations

import os
from typing import Any

os.environ["APP_ENV"] = "test"
os.environ["FRONTEND_URL"] = "http://localhost:3000"
os.environ["SUPABASE_URL"] = "http://127.0.0.1:54321"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "dummy-test-key"

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import sync as sync_endpoint
from app.core.auth import StaffPrincipal, require_staff
from app.main import app
from app.services.matching_service import PERLU_VERIFIKASI, TIDAK_LULUS, VALID
from app.services.sync_service import (
    ReviewPolicyBlockedError,
    ReviewValidationError,
    get_review_history,
    get_sync_result_detail,
    submit_review,
)
from tests.test_sync_service import MockSupabase


@pytest.fixture
def mock_supabase_with_result():
    sb = MockSupabase()
    session_id = "sess-1"
    result_id = "res-1"

    sb.storage["sync_sessions"].append({
        "id": session_id,
        "file_name": "wisuda.xlsx",
        "sitasi_import_id": "sit-1",
        "certiport_import_id": "cert-1",
        "total_rows": 1,
        "total_valid": 0,
        "total_review": 1,
        "total_not_found": 0,
        "status": "COMPLETED",
    })

    sb.storage["sync_results"].append({
        "id": result_id,
        "sync_session_id": session_id,
        "source_row": 2,
        "nim": "209900001",
        "nama_wisuda": "MAHASISWA UJI",
        "nama_sitasi": "MAHASISWA UJI",
        "name_match_type": "EXACT",
        "mos_status": "PERLU_VERIFIKASI",
        "mcf_status": None,
        "validation_status": PERLU_VERIFIKASI,
        "needs_review": True,
        "review_note": "Perlu verifikasi manual",
    })

    sb.storage["sync_evidence"].append({
        "id": "ev-1",
        "result_id": result_id,
        "category": "MOS",
        "exam": "Word",
        "sitasi_row_id": 2,
        "certiport_row_id": 100,
        "match_method": "NIM_EXACT+NAME_FUZZY",
        "match_score": 100,
        "evidence_status": "PERLU_VERIFIKASI",
        "reason": "Alias DRAFT",
    })

    return sb, session_id, result_id


# ---------------------------------------------------------------------------
# Unit tests: submit_review & audit trail
# ---------------------------------------------------------------------------

def test_submit_review_empty_note_raises_validation_error(mock_supabase_with_result):
    sb, session_id, result_id = mock_supabase_with_result
    with pytest.raises(ReviewValidationError) as exc:
        submit_review(sb, session_id, result_id, decision="TUNDA_VERIFIKASI", note="   ")
    assert "Catatan review wajib diisi" in str(exc.value)


def test_submit_review_invalid_decision_raises_validation_error(mock_supabase_with_result):
    sb, session_id, result_id = mock_supabase_with_result
    with pytest.raises(ReviewValidationError) as exc:
        submit_review(sb, session_id, result_id, decision="INVALID_DECISION", note="Catatan sah")
    assert "tidak valid" in str(exc.value)


def test_submit_review_adr009_blocks_staff_from_konfirmasi_cocok(mock_supabase_with_result):
    """Staff biasa tidak boleh melakukan KONFIRMASI_COCOK saat kebijakan ADR-009 belum disahkan."""
    sb, session_id, result_id = mock_supabase_with_result
    with pytest.raises(ReviewPolicyBlockedError) as exc:
        submit_review(
            sb, session_id, result_id,
            decision="KONFIRMASI_COCOK",
            note="Verifikasi identitas",
            user_id="staff-1",
            user_role="staff",
        )
    assert "ADR-009" in str(exc.value)
    # Status tetap PERLU_VERIFIKASI
    assert sb.storage["sync_results"][0]["validation_status"] == PERLU_VERIFIKASI


def test_submit_review_staff_can_tunda_and_tolak(mock_supabase_with_result):
    """Staff dapat melakukan TUNDA_VERIFIKASI dan TIDAK_COCOK."""
    sb, session_id, result_id = mock_supabase_with_result

    # 1. Staff submits TUNDA_VERIFIKASI
    res1 = submit_review(
        sb, session_id, result_id,
        decision="TUNDA_VERIFIKASI",
        note="Menunggu konfirmasi kartu ujian",
        user_id="staff-1",
        user_name="Staff Uji",
        user_role="staff",
    )
    assert res1["new_status"] == PERLU_VERIFIKASI
    assert len(sb.storage["review_audit"]) == 1

    # 2. Staff submits TIDAK_COCOK
    res2 = submit_review(
        sb, session_id, result_id,
        decision="TIDAK_COCOK",
        note="Identitas dipastikan berbeda orang",
        user_id="staff-1",
        user_name="Staff Uji",
        user_role="staff",
    )
    assert res2["previous_status"] == PERLU_VERIFIKASI
    assert res2["new_status"] == TIDAK_LULUS
    assert sb.storage["sync_results"][0]["validation_status"] == TIDAK_LULUS
    assert len(sb.storage["review_audit"]) == 2


def test_submit_review_admin_can_konfirmasi_cocok(mock_supabase_with_result):
    """Admin / penanggung jawab berwenang dapat melakukan KONFIRMASI_COCOK menjadi VALID."""
    sb, session_id, result_id = mock_supabase_with_result
    res = submit_review(
        sb, session_id, result_id,
        decision="KONFIRMASI_COCOK",
        note="Identitas telah diverifikasi via ijazah & kartu peserta",
        user_id="admin-1",
        user_name="Admin ITCC",
        user_role="admin",
    )
    assert res["new_status"] == VALID
    assert sb.storage["sync_results"][0]["validation_status"] == VALID
    assert sb.storage["sync_results"][0]["needs_review"] is False

    # Check audit trail
    audits = get_review_history(sb, result_id)
    assert len(audits) == 1
    assert audits[0]["decision"] == "KONFIRMASI_COCOK"
    assert audits[0]["new_status"] == VALID


def test_review_ganda_preserves_sequential_audit_trail(mock_supabase_with_result):
    """Review bertahap/ganda menyimpan jejak audit lengkap tanpa menimpa histori lama."""
    sb, session_id, result_id = mock_supabase_with_result

    # Review 1: Tunda verifikasi oleh staff
    submit_review(
        sb, session_id, result_id,
        decision="TUNDA_VERIFIKASI",
        note="Berkas fisik belum masuk",
        user_id="staff-1",
        user_name="Staff 1",
        user_role="staff",
    )
    # Review 2: Konfirmasi cocok oleh admin
    submit_review(
        sb, session_id, result_id,
        decision="KONFIRMASI_COCOK",
        note="Berkas fisik diverifikasi resmi",
        user_id="admin-1",
        user_name="Admin 1",
        user_role="admin",
    )

    audits = sb.storage["review_audit"]
    assert len(audits) == 2
    # First audit entry
    assert audits[0]["decision"] == "TUNDA_VERIFIKASI"
    assert audits[0]["previous_status"] == PERLU_VERIFIKASI
    assert audits[0]["new_status"] == PERLU_VERIFIKASI
    # Second audit entry
    assert audits[1]["decision"] == "KONFIRMASI_COCOK"
    assert audits[1]["previous_status"] == PERLU_VERIFIKASI
    assert audits[1]["new_status"] == VALID


def test_review_does_not_delete_or_alter_original_evidence(mock_supabase_with_result):
    """Review tidak menghapus atau mengubah tabel sync_evidence asli."""
    sb, session_id, result_id = mock_supabase_with_result

    submit_review(
        sb, session_id, result_id,
        decision="TIDAK_COCOK",
        note="Tolak",
        user_id="staff-1",
        user_role="staff",
    )

    detail = get_sync_result_detail(sb, session_id, result_id)
    assert len(detail["evidence"]) == 1
    assert detail["evidence"][0]["id"] == "ev-1"
    assert detail["evidence"][0]["exam"] == "Word"


# ---------------------------------------------------------------------------
# API tests: PATCH /api/v1/sync/{session_id}/results/{result_id}/review
# ---------------------------------------------------------------------------

def test_api_review_accessible_without_auth(monkeypatch, mock_supabase_with_result):
    sb, session_id, result_id = mock_supabase_with_result
    monkeypatch.setattr(sync_endpoint, "get_supabase", lambda: sb)
    client = TestClient(app)
    resp = client.patch(
        f"/api/v1/sync/{session_id}/results/{result_id}/review",
        json={"decision": "TUNDA_VERIFIKASI", "note": "Catatan admin"},
    )
    assert resp.status_code == 200


def test_api_review_adr009_blocks_staff_konfirmasi(monkeypatch, mock_supabase_with_result):
    sb, session_id, result_id = mock_supabase_with_result
    monkeypatch.setattr(sync_endpoint, "get_supabase", lambda: sb)

    client = TestClient(app)
    app.dependency_overrides[require_staff] = lambda: StaffPrincipal(
        user_id="staff-user-id",
        display_name="Staff Uji",
        role="staff",
    )
    try:
        resp = client.patch(
            f"/api/v1/sync/{session_id}/results/{result_id}/review",
            json={"decision": "KONFIRMASI_COCOK", "note": "Verifikasi mandiri"},
        )
        assert resp.status_code == 403
        assert "ADR-009" in resp.json()["detail"]
    finally:
        app.dependency_overrides.pop(require_staff, None)


def test_api_review_staff_tunda_success(monkeypatch, mock_supabase_with_result):
    sb, session_id, result_id = mock_supabase_with_result
    monkeypatch.setattr(sync_endpoint, "get_supabase", lambda: sb)

    client = TestClient(app)
    app.dependency_overrides[require_staff] = lambda: StaffPrincipal(
        user_id="staff-user-id",
        display_name="Staff Uji",
        role="staff",
    )
    try:
        resp = client.patch(
            f"/api/v1/sync/{session_id}/results/{result_id}/review",
            json={"decision": "TUNDA_VERIFIKASI", "note": "Menunggu fotokopi sertifikat"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["decision"] == "TUNDA_VERIFIKASI"
        assert body["data"]["new_status"] == PERLU_VERIFIKASI
    finally:
        app.dependency_overrides.pop(require_staff, None)


def test_api_review_admin_konfirmasi_success(monkeypatch, mock_supabase_with_result):
    sb, session_id, result_id = mock_supabase_with_result
    monkeypatch.setattr(sync_endpoint, "get_supabase", lambda: sb)

    client = TestClient(app)
    app.dependency_overrides[require_staff] = lambda: StaffPrincipal(
        user_id="admin-user-id",
        display_name="Admin ITCC",
        role="admin",
    )
    try:
        resp = client.patch(
            f"/api/v1/sync/{session_id}/results/{result_id}/review",
            json={"decision": "KONFIRMASI_COCOK", "note": "Disahkan berdasarkan surat ITCC"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["decision"] == "KONFIRMASI_COCOK"
        assert body["data"]["new_status"] == VALID
    finally:
        app.dependency_overrides.pop(require_staff, None)


def test_api_review_empty_note_returns_422(monkeypatch, mock_supabase_with_result):
    sb, session_id, result_id = mock_supabase_with_result
    monkeypatch.setattr(sync_endpoint, "get_supabase", lambda: sb)

    client = TestClient(app)
    app.dependency_overrides[require_staff] = lambda: StaffPrincipal(
        user_id="staff-user-id",
        display_name="Staff Uji",
        role="staff",
    )
    try:
        resp = client.patch(
            f"/api/v1/sync/{session_id}/results/{result_id}/review",
            json={"decision": "TUNDA_VERIFIKASI", "note": "   "},
        )
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.pop(require_staff, None)


def test_submit_review_updates_mos_and_mcf_status(mock_supabase_with_result):
    """KONFIRMASI_COCOK harus memperbarui mos_status, mcf_status, dan evidence_status menjadi VALID."""
    sb, session_id, result_id = mock_supabase_with_result
    # Tambahkan mcf_status dan program summary agar lengkap
    sb.storage["sync_results"][0]["mcf_status"] = PERLU_VERIFIKASI
    sb.storage["sync_results"][0]["kode_prodi"] = "31"  # TI (relevan MCF)
    sb.storage["sync_results"][0]["mos_programs"] = {"status": PERLU_VERIFIKASI, "needs_review": True}
    sb.storage["sync_results"][0]["mcf_programs"] = {"status": PERLU_VERIFIKASI, "needs_review": True}

    res = submit_review(
        sb, session_id, result_id,
        decision="KONFIRMASI_COCOK",
        note="Identitas sah tervalidasi",
        user_id="admin-1",
        user_name="Admin ITCC",
        user_role="admin",
    )
    assert res["new_status"] == VALID
    assert res["mos_status"] == VALID
    assert res["mcf_status"] == VALID
    assert sb.storage["sync_results"][0]["validation_status"] == VALID
    assert sb.storage["sync_results"][0]["mos_status"] == VALID
    assert sb.storage["sync_results"][0]["mcf_status"] == VALID
    assert sb.storage["sync_results"][0]["mos_programs"]["status"] == VALID
    assert sb.storage["sync_results"][0]["mcf_programs"]["status"] == VALID
    assert sb.storage["sync_evidence"][0]["evidence_status"] == VALID


def test_submit_review_tidak_cocok_updates_to_tidak_lulus(mock_supabase_with_result):
    """TIDAK_COCOK harus memperbarui status menjadi TIDAK_LULUS."""
    sb, session_id, result_id = mock_supabase_with_result
    res = submit_review(
        sb, session_id, result_id,
        decision="TIDAK_COCOK",
        note="Bukan mahasiswa bersangkutan",
        user_id="staff-1",
        user_name="Staff Uji",
        user_role="staff",
    )
    assert res["new_status"] == TIDAK_LULUS
    assert res["mos_status"] == TIDAK_LULUS
    assert sb.storage["sync_results"][0]["validation_status"] == TIDAK_LULUS
    assert sb.storage["sync_results"][0]["mos_status"] == TIDAK_LULUS
    assert sb.storage["sync_evidence"][0]["evidence_status"] == TIDAK_LULUS
