from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.core.auth import require_staff
from app.core.config import get_settings
from app.core.supabase_client import get_supabase
from app.services.import_service import (
    ImportValidationError,
    UploadTooLargeError,
    import_master_data,
    parse_certiport,
)
from app.services.master_query_service import get_active_import_summary, list_certiport

router = APIRouter(prefix="/certiport", tags=["Certiport"], dependencies=[Depends(require_staff)])


@router.get("/batch")
def get_certiport_active_batch():
    return {"success": True, "data": get_active_import_summary(get_supabase(), "CERTIPORT")}


@router.post("/import")
def import_certiport(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File harus berformat .xlsx")

    try:
        parsed = parse_certiport(
            file.file,
            file.filename,
            max_upload_bytes=get_settings().max_upload_size_bytes,
        )
        result = import_master_data(
            supabase=get_supabase(),
            data_type="CERTIPORT",
            file_name=file.filename,
            file_obj=file.file,
            parsed_workbook=parsed,
        )
        return {
            "success": True,
            "message": "Data Certiport berhasil diimpor",
            "data": result,
        }
    except UploadTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from None
    except ImportValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Import Certiport gagal diproses.") from None


@router.get("")
def get_certiport(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    nama: str | None = None,
    program: str | None = None,
    result: str | None = None,
):
    return {
        "success": True,
        "data": list_certiport(
            get_supabase(),
            page=page,
            limit=limit,
            search_name=nama,
            program_name=program,
            result=result,
        ),
    }
