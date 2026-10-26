from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.auth import StaffPrincipal, require_staff
from app.core.config import get_settings
from app.core.supabase_client import get_supabase
from app.services.import_service import ImportValidationError, UploadTooLargeError
from app.services.master_query_service import get_active_import_summary
from app.services.sync_service import (
    ExportBlockedByPolicyError,
    ReviewPolicyBlockedError,
    ReviewValidationError,
    SyncBatchMissingError,
    SyncExecutionError,
    SyncSessionNotFoundError,
    create_and_execute_sync,
    generate_sync_export_workbook,
    get_sync_result_detail,
    get_sync_session,
    list_sync_results,
    list_sync_sessions,
    submit_review,
)
from app.services.wisuda_validation_service import validate_wisuda_workbook

router = APIRouter(prefix="/sync", tags=["Sinkronisasi"], dependencies=[Depends(require_staff)])


class ReviewDecisionRequest(BaseModel):
    decision: str = Field(..., description="Keputusan review: KONFIRMASI_COCOK, TIDAK_COCOK, atau TUNDA_VERIFIKASI")
    note: str = Field(..., min_length=1, description="Catatan penjelasan wajib dari reviewer")
    target_program: str | None = Field(default=None, description="Target sertifikasi: ALL, MOS, atau MCF")


@router.post("/validate")
def validate_wisuda_upload(file: UploadFile = File(...)):
    """Validasi format workbook Wisuda tanpa menyimpan atau mengubah database."""
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File harus berformat .xlsx")

    try:
        validation = validate_wisuda_workbook(
            file.file,
            file.filename,
            max_upload_bytes=get_settings().max_upload_size_bytes,
        )
        masters = {
            "sitasi": get_active_import_summary(get_supabase(), "SITASI"),
            "certiport": get_active_import_summary(get_supabase(), "CERTIPORT"),
        }
        return {"success": True, "data": {**validation, "active_masters": masters}}
    except UploadTooLargeError:
        raise HTTPException(status_code=413, detail="Ukuran file melebihi batas upload.") from None
    except ImportValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    except Exception:
        raise HTTPException(status_code=503, detail="Validasi atau sumber batch aktif belum tersedia.") from None


@router.post("", status_code=status.HTTP_201_CREATED)
def start_sync(
    file: UploadFile = File(...),
    current_user: StaffPrincipal = Depends(require_staff),
):
    """Jalankan proses sinkronisasi wisuda terhadap batch master aktif."""
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File harus berformat .xlsx")

    supabase = get_supabase()
    settings = get_settings()

    try:
        result = create_and_execute_sync(
            supabase=supabase,
            file_obj=file.file,
            file_name=file.filename,
            max_upload_bytes=settings.max_upload_size_bytes,
            user_id=current_user.user_id,
        )
        return {"success": True, "data": result}
    except UploadTooLargeError:
        raise HTTPException(status_code=413, detail="Ukuran file melebihi batas upload.") from None
    except ImportValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    except SyncBatchMissingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except SyncExecutionError as exc:
        raise HTTPException(status_code=500, detail="Proses sinkronisasi gagal dijalankan.") from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal.") from None


@router.get("")
def get_sync_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Riwayat sesi sinkronisasi dengan paginasi."""
    try:
        data = list_sync_sessions(get_supabase(), page=page, limit=limit)
        return {"success": True, "data": data}
    except Exception:
        raise HTTPException(status_code=503, detail="Layanan riwayat sinkronisasi sementara tidak tersedia.") from None


@router.get("/{session_id}")
def get_session_summary(session_id: str):
    """Ringkasan metadata satu sesi sinkronisasi."""
    try:
        session = get_sync_session(get_supabase(), session_id)
        return {"success": True, "data": session}
    except SyncSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except Exception:
        raise HTTPException(status_code=503, detail="Layanan sesi sementara tidak tersedia.") from None


@router.get("/{session_id}/results")
def get_session_results(
    session_id: str,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    needs_review: Optional[bool] = Query(default=None),
    program: Optional[str] = Query(default=None),
):
    """Daftar baris hasil sinkronisasi dengan paginasi, pencarian, dan filter status/program."""
    try:
        results = list_sync_results(
            get_supabase(),
            session_id=session_id,
            page=page,
            limit=limit,
            status=status,
            search=search,
            needs_review=needs_review,
            program=program,
        )
        return {"success": True, "data": results}
    except SyncSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except Exception:
        raise HTTPException(status_code=503, detail="Layanan hasil sinkronisasi sementara tidak tersedia.") from None


@router.get("/{session_id}/results/{result_id}")
def get_result_detail(session_id: str, result_id: str):
    """Detail satu baris hasil sinkronisasi dan evidence pendukung dari SITASI/Certiport."""
    try:
        detail = get_sync_result_detail(get_supabase(), session_id=session_id, result_id=result_id)
        return {"success": True, "data": detail}
    except SyncSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except Exception:
        raise HTTPException(status_code=503, detail="Layanan detail hasil sementara tidak tersedia.") from None


@router.patch("/{session_id}/results/{result_id}/review")
def review_sync_result(
    session_id: str,
    result_id: str,
    payload: ReviewDecisionRequest,
    current_user: StaffPrincipal = Depends(require_staff),
):
    """Simpan keputusan review manual petugas dengan jejak audit append-only."""
    try:
        result = submit_review(
            supabase=get_supabase(),
            session_id=session_id,
            result_id=result_id,
            decision=payload.decision,
            note=payload.note,
            target_program=payload.target_program,
            user_id=current_user.user_id,
            user_name=current_user.display_name,
            user_role=current_user.role,
        )
        return {
            "success": True,
            "message": "Keputusan review berhasil disimpan.",
            "data": result,
        }
    except ReviewValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    except ReviewPolicyBlockedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except SyncSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except Exception:
        raise HTTPException(status_code=500, detail="Gagal menyimpan keputusan review.") from None


@router.get("/{session_id}/export")
def export_sync_workbook(
    session_id: str,
    mode: str = Query(default="final", description="Mode ekspor: 'final' (isi LULUS saja) atau 'draft' (pratinjau berlabel)"),
):
    """Ekspor workbook hasil sinkronisasi dengan perlindungan gate keputusan bisnis ADR."""
    try:
        buffer = generate_sync_export_workbook(
            supabase=get_supabase(),
            session_id=session_id,
            mode=mode,
        )
        filename = f"wisuda_sync_{mode}_{session_id[:8]}.xlsx"
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ExportBlockedByPolicyError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except SyncSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except Exception:
        raise HTTPException(status_code=500, detail="Gagal menghasilkan berkas ekspor.") from None


