from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.core.supabase_client import get_supabase
from app.services.import_service import ImportValidationError, import_master_data
from app.services.master_query_service import list_certiport

router = APIRouter(prefix="/certiport", tags=["Certiport"])


@router.post("/import")
def import_certiport(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File harus berformat .xlsx")

    try:
        result = import_master_data(
            supabase=get_supabase(),
            data_type="CERTIPORT",
            file_name=file.filename,
            file_obj=file.file,
        )
        return {
            "success": True,
            "message": "Data Certiport berhasil diimpor",
            "data": result,
        }
    except ImportValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Import Certiport gagal: {exc}") from exc


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
