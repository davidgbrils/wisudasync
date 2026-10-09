from supabase import Client

from app.services.import_service import get_active_import_id


def get_active_import_summary(supabase: Client, data_type: str) -> dict | None:
    response = (
        supabase.table("data_imports")
        .select("id,data_type,total_rows,imported_rows,status,created_at,completed_at")
        .eq("data_type", data_type)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    batch = response.data[0]
    return {
        field: batch.get(field)
        for field in (
            "id",
            "data_type",
            "total_rows",
            "imported_rows",
            "status",
            "created_at",
            "completed_at",
        )
    }


def list_sitasi(
    supabase: Client,
    page: int = 1,
    limit: int = 50,
    search_nim: str | None = None,
    search_name: str | None = None,
    sertifikasi: str | None = None,
    status: str | None = None,
) -> dict:
    import_id = get_active_import_id(supabase, "SITASI")
    if not import_id:
        return {"items": [], "total": 0, "page": page, "limit": limit}

    start = (page - 1) * limit
    end = start + limit - 1

    query = (
        supabase.table("sitasi_data")
        .select(
            "id,source_row,nim,nama,fakultas,kode_nim,program_studi,angkatan,sertifikasi,sub_program,nilai,status",
            count="exact",
        )
        .eq("import_id", import_id)
    )

    if search_nim:
        query = query.ilike("nim", f"%{search_nim.strip()}%")
    if search_name:
        query = query.ilike("nama_normalized", f"%{search_name.strip().upper()}%")
    if sertifikasi:
        query = query.eq("sertifikasi", sertifikasi.strip().upper())
    if status:
        query = query.eq("status", status.strip().upper())

    response = query.order("source_row").range(start, end).execute()
    return {
        "items": response.data or [],
        "total": response.count or 0,
        "page": page,
        "limit": limit,
        "import_id": import_id,
    }


def list_certiport(
    supabase: Client,
    page: int = 1,
    limit: int = 50,
    search_name: str | None = None,
    program_name: str | None = None,
    result: str | None = None,
) -> dict:
    import_id = get_active_import_id(supabase, "CERTIPORT")
    if not import_id:
        return {"items": [], "total": 0, "page": page, "limit": limit}

    start = (page - 1) * limit
    end = start + limit - 1

    query = (
        supabase.table("certiport_data")
        .select(
            "id,source_row,first_name,last_name,full_name,program_name,certification_name,score,result",
            count="exact",
        )
        .eq("import_id", import_id)
    )

    if search_name:
        query = query.ilike("full_name_normalized", f"%{search_name.strip().upper()}%")
    if program_name:
        query = query.ilike("program_name", f"%{program_name.strip()}%")
    if result:
        query = query.eq("result", result.strip().upper())

    response = query.order("source_row").range(start, end).execute()
    return {
        "items": response.data or [],
        "total": response.count or 0,
        "page": page,
        "limit": limit,
        "import_id": import_id,
    }
