from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.core.auth import require_staff
from app.core.config import get_settings
from app.core.supabase_client import get_supabase
from app.services.import_service import (
    ImportValidationError,
    UploadTooLargeError,
    import_master_data,
    parse_sitasi,
)
from app.services.master_query_service import get_active_import_summary, list_sitasi

router = APIRouter(prefix="/sitasi", tags=["SITASI"], dependencies=[Depends(require_staff)])


@router.get("/batch")
def get_sitasi_active_batch():
    return {"success": True, "data": get_active_import_summary(get_supabase(), "SITASI")}


@router.post("/import")
def import_sitasi(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File harus berformat .xlsx")

    try:
        parsed = parse_sitasi(
            file.file,
            file.filename,
            max_upload_bytes=get_settings().max_upload_size_bytes,
        )
        result = import_master_data(
            supabase=get_supabase(),
            data_type="SITASI",
            file_name=file.filename,
            file_obj=file.file,
            parsed_workbook=parsed,
        )
        return {
            "success": True,
            "message": "Data SITASI berhasil diimpor",
            "data": result,
        }
    except UploadTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from None
    except ImportValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Import SITASI gagal diproses.") from None


@router.get("")
def get_sitasi(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    nim: str | None = None,
    nama: str | None = None,
    sertifikasi: str | None = None,
    status: str | None = None,
):
    return {
        "success": True,
        "data": list_sitasi(
            get_supabase(),
            page=page,
            limit=limit,
            search_nim=nim,
            search_name=nama,
            sertifikasi=sertifikasi,
            status=status,
        ),
    }
