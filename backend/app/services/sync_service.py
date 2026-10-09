from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from typing import Any, BinaryIO
import uuid

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from supabase import Client

from app.services.import_service import ImportValidationError, get_active_import_id
from app.services.matching_service import (
    DATA_TIDAK_DITEMUKAN,
    PENDING,
    PERLU_VERIFIKASI,
    TIDAK_LULUS,
    VALID,
    fetch_active_certiport_rows,
    fetch_active_sitasi_rows,
    validate_wisuda_complete,
)
from app.services.wisuda_validation_service import parse_wisuda_for_sync


class SyncBatchMissingError(ValueError):
    """Batch master SITASI atau Certiport aktif belum tersedia."""


class SyncSessionNotFoundError(ValueError):
    """Sesi sinkronisasi tidak ditemukan."""


class SyncExecutionError(RuntimeError):
    """Kegagalan selama proses sinkronisasi."""


class ReviewPolicyBlockedError(PermissionError):
    """ADR-009: Kebijakan penunjukan reviewer belum disahkan."""


class ReviewValidationError(ValueError):
    """Input keputusan atau catatan review tidak valid."""


class ExportBlockedByPolicyError(PermissionError):
    """ADR-003/005/006/010/011: Ekspor final diblokir sebelum pengesahan resmi ITCC."""


ALLOWED_REVIEW_DECISIONS = ("KONFIRMASI_COCOK", "TIDAK_COCOK", "TUNDA_VERIFIKASI")
ADR_009_REVIEWER_POLICY_APPROVED = False  # ADR-009 berstatus TERBUKA per docs/14_DECISIONS.md
ADR_OUTPUT_MAPPING_APPROVED = False  # ADR-003, 005, 006, 010, 011 berstatus TERBUKA per docs/20_OUTPUT_MAPPING_APPROVAL.md


def create_and_execute_sync(
    supabase: Client,
    file_obj: BinaryIO,
    file_name: str,
    max_upload_bytes: int,
    user_id: str | None = None,
) -> dict:
    """Eksekusi sinkronisasi wisuda end-to-end dengan persistensi sesi, hasil, dan bukti.

    Alur:
    1. Parse dan validasi baris wisuda (menolak formula, duplikat, dsb.)
    2. Cek batch SITASI dan Certiport aktif. Catat snapshot ID batch pada sesi.
    3. Simpan sesi awal dengan status PROCESSING.
    4. Ambil master data batch aktif terkait.
    5. Jalankan validasi silang lengkap (validate_wisuda_complete).
    6. Persistensi hasil ke sync_results dan detail bukti ke sync_evidence.
    7. Perbarui status sesi menjadi COMPLETED beserta ringkasan total.
    8. Jika gagal di tengah, status sesi diubah menjadi FAILED beserta pesan error aman.
    """
    wisuda_rows = parse_wisuda_for_sync(file_obj, file_name, max_upload_bytes)

    sitasi_import_id = get_active_import_id(supabase, "SITASI")
    certiport_import_id = get_active_import_id(supabase, "CERTIPORT")

    if not sitasi_import_id or not certiport_import_id:
        missing = []
        if not sitasi_import_id:
            missing.append("SITASI")
        if not certiport_import_id:
            missing.append("CERTIPORT")
        raise SyncBatchMissingError(
            f"Batch master aktif belum lengkap ({', '.join(missing)}). "
            f"Unggah dan aktifkan batch master terlebih dahulu."
        )

    session_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    session_data = {
        "id": session_id,
        "file_name": file_name,
        "sitasi_import_id": sitasi_import_id,
        "certiport_import_id": certiport_import_id,
        "total_rows": len(wisuda_rows),
        "total_valid": 0,
        "total_review": 0,
        "total_not_found": 0,
        "status": "PROCESSING",
        "created_by": user_id,
        "created_at": now_iso,
    }

    supabase.table("sync_sessions").insert(session_data).execute()

    try:
        _, sitasi_rows = fetch_active_sitasi_rows(supabase)
        _, certiport_rows = fetch_active_certiport_rows(supabase)

        validated_rows = validate_wisuda_complete(
            wisuda_rows,
            sitasi_rows,
            certiport_rows,
            sitasi_import_id=sitasi_import_id,
            certiport_import_id=certiport_import_id,
        )

        results_to_insert: list[dict] = []
        evidence_to_insert: list[dict] = []

        total_valid = 0
        total_review = 0
        total_not_found = 0

        for r in validated_rows:
            result_id = str(uuid.uuid4())
            v_status = r.get("validation_status", PERLU_VERIFIKASI)
            needs_review = bool(r.get("needs_review", False))

            if v_status == VALID:
                total_valid += 1
            elif v_status == DATA_TIDAK_DITEMUKAN:
                total_not_found += 1
            else:
                total_review += 1

            review_flags = r.get("review_flags", [])
            review_note = "; ".join(review_flags) if review_flags else None

            prog_summary = r.get("program_summary", {})
            mos_programs = prog_summary.get("MOS")
            mcf_programs = prog_summary.get("MCF")

            nama_sitasi = None
            exams = r.get("exams", [])
            for exam in exams:
                for att in exam.get("attempts", []):
                    if att.get("nama"):
                        nama_sitasi = att["nama"]
                        break
                if nama_sitasi:
                    break

            results_to_insert.append({
                "id": result_id,
                "sync_session_id": session_id,
                "source_row": r["source_row"],
                "nim": str(r["nim"]),
                "nama_wisuda": str(r["nama"]),
                "nama_sitasi": nama_sitasi,
                "name_match_type": r.get("name_match"),
                "mos_status": r.get("mos_status"),
                "mcf_status": r.get("mcf_status"),
                "mos_programs": mos_programs,
                "mcf_programs": mcf_programs,
                "validation_status": v_status,
                "needs_review": needs_review,
                "review_note": review_note,
                "created_at": now_iso,
            })

            for exam in exams:
                cat = exam.get("sertifikasi")
                sub = exam.get("sub_program")
                cv = exam.get("certiport_validation", {})
                e_status = cv.get("combined_status", exam.get("exam_status"))
                e_reason = cv.get("reason", exam.get("reason", ""))

                sitasi_ev = exam.get("lulus_evidence") or (exam.get("attempts", [{}])[0] if exam.get("attempts") else {})
                sit_row_id = sitasi_ev.get("id")

                cert_ev_list = cv.get("certiport_evidence", [])
                cert_row_id = cert_ev_list[0].get("id") if cert_ev_list else None
                score = cert_ev_list[0].get("score") if cert_ev_list else None

                evidence_to_insert.append({
                    "id": str(uuid.uuid4()),
                    "result_id": result_id,
                    "category": cat,
                    "exam": sub,
                    "sitasi_row_id": sit_row_id,
                    "certiport_row_id": cert_row_id,
                    "match_method": "NIM_EXACT+NAME_FUZZY",
                    "match_score": score,
                    "evidence_status": e_status,
                    "reason": e_reason,
                    "created_at": now_iso,
                })

        batch_size = 500
        for i in range(0, len(results_to_insert), batch_size):
            chunk = results_to_insert[i : i + batch_size]
            supabase.table("sync_results").insert(chunk).execute()

        for i in range(0, len(evidence_to_insert), batch_size):
            chunk = evidence_to_insert[i : i + batch_size]
            supabase.table("sync_evidence").insert(chunk).execute()

        completed_at = datetime.now(timezone.utc).isoformat()
        supabase.table("sync_sessions").update({
            "status": "COMPLETED",
            "total_valid": total_valid,
            "total_review": total_review,
            "total_not_found": total_not_found,
            "completed_at": completed_at,
        }).eq("id", session_id).execute()

        return {
            "session_id": session_id,
            "status": "COMPLETED",
            "file_name": file_name,
            "total_rows": len(wisuda_rows),
            "total_valid": total_valid,
            "total_review": total_review,
            "total_not_found": total_not_found,
            "sitasi_import_id": sitasi_import_id,
            "certiport_import_id": certiport_import_id,
            "completed_at": completed_at,
        }

    except Exception as exc:
        try:
            supabase.table("sync_sessions").update({
                "status": "FAILED",
                "error_message": "Terjadi kesalahan saat memproses data sinkronisasi.",
            }).eq("id", session_id).execute()
        except Exception:
            pass
        raise SyncExecutionError("Proses sinkronisasi gagal diproses.") from exc


def list_sync_sessions(
    supabase: Client,
    page: int = 1,
    limit: int = 50,
) -> dict:
    """Daftar riwayat sesi sinkronisasi dengan paginasi."""
    limit = max(1, min(limit, 100))
    offset = max(0, (page - 1) * limit)

    response = (
        supabase.table("sync_sessions")
        .select("*", count="exact")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    items = response.data or []
    total = response.count if response.count is not None else len(items)

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
    }


def get_sync_session(
    supabase: Client,
    session_id: str,
) -> dict:
    """Ambil ringkasan satu sesi sinkronisasi berdasarkan ID."""
    response = (
        supabase.table("sync_sessions")
        .select("*")
        .eq("id", session_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise SyncSessionNotFoundError(f"Sesi sinkronisasi {session_id} tidak ditemukan.")
    return response.data[0]


def list_sync_results(
    supabase: Client,
    session_id: str,
    page: int = 1,
    limit: int = 50,
    status: str | None = None,
    search: str | None = None,
    needs_review: bool | None = None,
) -> dict:
    """Ambil daftar hasil per baris dengan paginasi dan filter."""
    get_sync_session(supabase, session_id)

    limit = max(1, min(limit, 100))
    offset = max(0, (page - 1) * limit)

    query = (
        supabase.table("sync_results")
        .select("*", count="exact")
        .eq("sync_session_id", session_id)
    )

    if status:
        query = query.eq("validation_status", status.strip().upper())

    if needs_review is not None:
        query = query.eq("needs_review", needs_review)

    if search:
        s = search.strip()
        query = query.or_(f"nim.ilike.%{s}%,nama_wisuda.ilike.%{s}%")

    query = query.order("source_row", desc=False).range(offset, offset + limit - 1)
    response = query.execute()

    items = response.data or []
    total = response.count if response.count is not None else len(items)

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
    }


def get_sync_result_detail(
    supabase: Client,
    session_id: str,
    result_id: str,
) -> dict:
    """Ambil detail satu baris hasil sinkronisasi beserta seluruh evidence sumber."""
    res_resp = (
        supabase.table("sync_results")
        .select("*")
        .eq("id", result_id)
        .eq("sync_session_id", session_id)
        .limit(1)
        .execute()
    )
    if not res_resp.data:
        raise SyncSessionNotFoundError("Hasil sinkronisasi tidak ditemukan.")

    result_row = res_resp.data[0]

    ev_resp = (
        supabase.table("sync_evidence")
        .select("*")
        .eq("result_id", result_id)
        .order("created_at")
        .execute()
    )
    result_row["evidence"] = ev_resp.data or []

    audit_resp = (
        supabase.table("review_audit")
        .select("*")
        .eq("result_id", result_id)
        .order("created_at", desc=True)
        .execute()
    )
    result_row["review_history"] = audit_resp.data or []

    return result_row


def get_review_history(supabase: Client, result_id: str) -> list[dict]:
    """Ambil riwayat audit keputusan review untuk satu hasil sinkronisasi."""
    response = (
        supabase.table("review_audit")
        .select("*")
        .eq("result_id", result_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def submit_review(
    supabase: Client,
    session_id: str,
    result_id: str,
    decision: str,
    note: str,
    user_id: str | None = None,
    user_name: str | None = None,
    user_role: str = "staff",
) -> dict:
    """Simpan keputusan review manual petugas dengan audit trail lengkap.

    Aturan:
    - Keputusan harus salah satu dari: KONFIRMASI_COCOK, TIDAK_COCOK, TUNDA_VERIFIKASI.
    - Catatan (note) wajib diisi.
    - Otorisasi reviewer mengikuti ADR-009:
      Jika kebijakan belum disahkan dan user bukan admin, KONFIRMASI_COCOK ditolak
      (mode read-only / tunda verifikasi) untuk mencegah status VALID tanpa izin institusi.
    - Review bersifat append-only di review_audit; bukti asli di sync_evidence TIDAK dihapus.
    - Review ganda mencatat status sebelumnya dan status baru secara berurutan.
    """
    decision_clean = decision.strip().upper() if decision else ""
    if decision_clean not in ALLOWED_REVIEW_DECISIONS:
        raise ReviewValidationError(
            f"Keputusan '{decision}' tidak valid. Pilihan: {', '.join(ALLOWED_REVIEW_DECISIONS)}."
        )

    note_clean = note.strip() if note else ""
    if not note_clean:
        raise ReviewValidationError("Catatan review wajib diisi.")

    # ADR-009 check: Kebijakan penunjukan reviewer belum disahkan
    if decision_clean == "KONFIRMASI_COCOK":
        if user_role != "admin" and not ADR_009_REVIEWER_POLICY_APPROVED:
            raise ReviewPolicyBlockedError(
                "Kebijakan penunjukan reviewer (ADR-009) belum disahkan institusi. "
                "Konfirmasi final dibatasi bagi penanggung jawab resmi/admin. "
                "Gunakan 'TUNDA_VERIFIKASI' atau 'TIDAK_COCOK'."
            )

    res_resp = (
        supabase.table("sync_results")
        .select("*")
        .eq("id", result_id)
        .eq("sync_session_id", session_id)
        .limit(1)
        .execute()
    )
    if not res_resp.data:
        raise SyncSessionNotFoundError("Hasil sinkronisasi tidak ditemukan.")

    current_result = res_resp.data[0]
    previous_status = current_result.get("validation_status", "PERLU_VERIFIKASI")

    if decision_clean == "KONFIRMASI_COCOK":
        new_status = VALID
        needs_review = False
    elif decision_clean == "TIDAK_COCOK":
        new_status = TIDAK_LULUS
        needs_review = False
    else:  # TUNDA_VERIFIKASI
        new_status = PERLU_VERIFIKASI
        needs_review = True

    audit_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        "id": audit_id,
        "result_id": result_id,
        "reviewed_by": user_id,
        "reviewer_name": user_name or "Petugas",
        "decision": decision_clean,
        "note": note_clean,
        "previous_status": previous_status,
        "new_status": new_status,
        "created_at": now_iso,
    }
    supabase.table("review_audit").insert(audit_entry).execute()

    supabase.table("sync_results").update({
        "validation_status": new_status,
        "needs_review": needs_review,
        "review_note": f"[{decision_clean}] {note_clean}",
    }).eq("id", result_id).execute()

    # Recalculate session totals
    all_res = (
        supabase.table("sync_results")
        .select("validation_status, needs_review")
        .eq("sync_session_id", session_id)
        .execute()
    )
    items = all_res.data or []
    tot_valid = sum(1 for x in items if x.get("validation_status") == VALID)
    tot_nf = sum(1 for x in items if x.get("validation_status") == DATA_TIDAK_DITEMUKAN)
    tot_rev = sum(1 for x in items if x.get("needs_review") or x.get("validation_status") in (PERLU_VERIFIKASI, PENDING))

    supabase.table("sync_sessions").update({
        "total_valid": tot_valid,
        "total_review": tot_rev,
        "total_not_found": tot_nf,
    }).eq("id", session_id).execute()

    return {
        "result_id": result_id,
        "session_id": session_id,
        "decision": decision_clean,
        "note": note_clean,
        "previous_status": previous_status,
        "new_status": new_status,
        "audit_id": audit_id,
        "created_at": now_iso,
    }


def generate_sync_export_workbook(
    supabase: Client,
    session_id: str,
    mode: str = "draft",
) -> BytesIO:
    """Hasilkan berkas export workbook Wisuda dengan perlindungan gate keputusan bisnis.

    Aturan ADR-003, ADR-005, ADR-006, ADR-010, ADR-011:
    - Mode 'final' DIBLOKIR selama kebijakan output mapping belum disahkan tertulis oleh ITCC.
    - Mode 'draft' menghasilkan berkas pratinjau yang aman:
      - Memuat label eksplisit '[DRAFT - PRATINJAU BELUM DISAHKAN]'.
      - Menyertakan lembar audit sesi terpisah dengan catatan peringatan administratif.
      - Menjaga keutuhan urutan baris sumber dan nilai mahasiswa.
    """
    mode_clean = mode.strip().lower() if mode else "draft"

    if mode_clean == "final":
        if not ADR_OUTPUT_MAPPING_APPROVED:
            raise ExportBlockedByPolicyError(
                "Ekspor final diblokir: Menunggu pengesahan keputusan bisnis ITCC "
                "(ADR-003, ADR-005, ADR-006, ADR-010, ADR-011). "
                "Silakan gunakan ekspor pratinjau DRAFT. Lihat docs/20_OUTPUT_MAPPING_APPROVAL.md."
            )

    session = get_sync_session(supabase, session_id)

    res_resp = (
        supabase.table("sync_results")
        .select("*")
        .eq("sync_session_id", session_id)
        .order("source_row")
        .execute()
    )
    results = res_resp.data or []

    wb = Workbook()

    # Sheet 1: Pratinjau Wisuda DRAFT
    ws_wisuda = wb.active
    ws_wisuda.title = "Wisuda (DRAFT Preview)"

    draft_notice_fill = PatternFill(start_color="FFFBEB", end_color="FFFBEB", fill_type="solid")
    header_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    bold_font = Font(bold=True)

    headers = [
        "No",
        "Kode Prodi",
        "Program Studi",
        "NIM",
        "Nama",
        "Sertifikasi MOS [DRAFT]",
        "Sertifikasi MCF [DRAFT]",
        "Title Microsoft [DRAFT]",
        "Status Validasi",
        "Catatan Review",
    ]
    ws_wisuda.append(headers)
    for col_num in range(1, len(headers) + 1):
        cell = ws_wisuda.cell(row=1, column=col_num)
        cell.font = bold_font
        cell.fill = header_fill

    for idx, r in enumerate(results, start=1):
        mos_status = r.get("mos_status")
        mcf_status = r.get("mcf_status")
        val_status = r.get("validation_status", "")

        # Format DRAFT sementara per ADR-003
        if mos_status == VALID:
            mos_text = "[DRAFT] MOS (Lulus)"
        elif mos_status:
            mos_text = f"[DRAFT] {mos_status}"
        else:
            mos_text = "—"

        if mcf_status == VALID:
            mcf_text = "[DRAFT] MCF (Lulus)"
        elif mcf_status:
            mcf_text = f"[DRAFT] {mcf_status}"
        else:
            mcf_text = "—"

        title_text = "[DRAFT] MOS" if mos_status == VALID else ("—" if not mcf_status == VALID else "[DRAFT] MCF")

        row_values = [
            idx,
            "",  # Kode Prodi
            "",  # Program Studi
            r.get("nim", ""),
            r.get("nama_wisuda", ""),
            mos_text,
            mcf_text,
            title_text,
            val_status,
            r.get("review_note") or "",
        ]
        ws_wisuda.append(row_values)
        if val_status != VALID:
            for c_idx in range(6, 9):
                ws_wisuda.cell(row=idx + 1, column=c_idx).fill = draft_notice_fill

    # Sheet 2: Ringkasan Sesi & Audit
    ws_audit = wb.create_sheet(title="Ringkasan & Gate ADR")
    ws_audit.append(["PARAMETER", "NILAI"])
    ws_audit.cell(row=1, column=1).font = bold_font
    ws_audit.cell(row=1, column=2).font = bold_font

    audit_meta = [
        ("Status Berkas", "DRAFT - PRATINJAU BELUM DISAHKAN"),
        ("Dasar Kebijakan", "Menunggu pengesahan docs/20_OUTPUT_MAPPING_APPROVAL.md"),
        ("Session ID", session.get("id")),
        ("Nama File Asli", session.get("file_name")),
        ("Batch SITASI Terpakai", session.get("sitasi_import_id")),
        ("Batch Certiport Terpakai", session.get("certiport_import_id")),
        ("Total Mahasiswa", session.get("total_rows")),
        ("Total Valid", session.get("total_valid")),
        ("Total Perlu Verifikasi", session.get("total_review")),
        ("Total Tidak Ditemukan", session.get("total_not_found")),
        ("Waktu Sinkronisasi", session.get("created_at")),
        ("Peringatan", "DILARANG menggunakan berkas ini sebagai acuan resmi wisuda sebelum ditandatangani ITCC."),
    ]
    for param, val in audit_meta:
        ws_audit.append([param, str(val)])

    buf = BytesIO()
    wb.save(buf)
    wb.close()
    buf.seek(0)
    return buf
