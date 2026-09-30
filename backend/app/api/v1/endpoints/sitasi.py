from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.core.supabase_client import get_supabase
from app.services.import_service import ImportValidationError, import_master_data
from app.services.master_query_service import list_sitasi

router = APIRouter(prefix="/sitasi", tags=["SITASI"])


@router.post("/import")
def import_sitasi(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File harus berformat .xlsx")

    try:
        result = import_master_data(
            supabase=get_supabase(),
            data_type="SITASI",
            file_name=file.filename,
            file_obj=file.file,
        )
        return {
            "success": True,
            "message": "Data SITASI berhasil diimpor",
            "data": result,
        }
    except ImportValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Import SITASI gagal: {exc}") from exc


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
