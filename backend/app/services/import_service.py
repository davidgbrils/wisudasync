from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import BinaryIO, Literal

import pandas as pd
from supabase import Client

from app.services.normalization_service import (
    clean_text,
    normalize_code,
    normalize_name,
    normalize_upper,
    to_number,
)

DataType = Literal["SITASI", "CERTIPORT"]
BATCH_SIZE = 500

SITASI_COLUMNS = [
    "NIM",
    "Nama",
    "Fakultas",
    "Kode NIM",
    "Program Studi",
    "Angkatan",
    "Sertifikasi",
    "Sub Program",
    "Nilai",
    "Status",
]

CERTIPORT_COLUMNS = [
    "First Name",
    "Last Name",
    "Full Name",
    "Program Name",
    "Certification Name",
    "Score",
    "Result",
]


class ImportValidationError(ValueError):
    pass


@dataclass
class ParsedWorkbook:
    sheet_name: str
    rows: list[dict]


def _read_excel(file_obj: BinaryIO) -> tuple[pd.DataFrame, str]:
    file_obj.seek(0)
    excel = pd.ExcelFile(file_obj, engine="openpyxl")
    if not excel.sheet_names:
        raise ImportValidationError("Workbook tidak memiliki sheet.")

    sheet_name = excel.sheet_names[0]
    df = pd.read_excel(excel, sheet_name=sheet_name, dtype=object)
    df.columns = [str(column).strip() for column in df.columns]
    return df, sheet_name


def _validate_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ImportValidationError(
            "Kolom wajib tidak ditemukan: " + ", ".join(missing)
        )


def parse_sitasi(file_obj: BinaryIO) -> ParsedWorkbook:
    df, sheet_name = _read_excel(file_obj)
    _validate_columns(df, SITASI_COLUMNS)

    rows: list[dict] = []
    for index, row in df.iterrows():
        # +2 karena index dimulai 0 dan baris pertama Excel adalah header.
        source_row = int(index) + 2
        nama = clean_text(row["Nama"])
        rows.append(
            {
                "source_row": source_row,
                "nim": normalize_code(row["NIM"]),
                "nama": nama,
                "nama_normalized": normalize_name(nama),
                "fakultas": clean_text(row["Fakultas"]),
                "kode_nim": normalize_code(row["Kode NIM"]),
                "program_studi": clean_text(row["Program Studi"]),
                "angkatan": normalize_code(row["Angkatan"]),
                "sertifikasi": normalize_upper(row["Sertifikasi"]),
                "sub_program": clean_text(row["Sub Program"]),
                "nilai": to_number(row["Nilai"]),
                "status": normalize_upper(row["Status"]),
            }
        )

    return ParsedWorkbook(sheet_name=sheet_name, rows=rows)


def parse_certiport(file_obj: BinaryIO) -> ParsedWorkbook:
    df, sheet_name = _read_excel(file_obj)
    _validate_columns(df, CERTIPORT_COLUMNS)

    rows: list[dict] = []
    for index, row in df.iterrows():
        source_row = int(index) + 2
        full_name = clean_text(row["Full Name"])
        rows.append(
            {
                "source_row": source_row,
                "first_name": clean_text(row["First Name"]),
                "last_name": clean_text(row["Last Name"]),
                "full_name": full_name,
                "full_name_normalized": normalize_name(full_name),
                "program_name": clean_text(row["Program Name"]),
                "certification_name": clean_text(row["Certification Name"]),
                "score": to_number(row["Score"]),
                "result": normalize_upper(row["Result"]),
            }
        )

    return ParsedWorkbook(sheet_name=sheet_name, rows=rows)


def _chunks(rows: list[dict], size: int = BATCH_SIZE):
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def import_master_data(
    supabase: Client,
    data_type: DataType,
    file_name: str,
    file_obj: BinaryIO,
    created_by: str | None = None,
) -> dict:
    parser = parse_sitasi if data_type == "SITASI" else parse_certiport
    table_name = "sitasi_data" if data_type == "SITASI" else "certiport_data"

    parsed = parser(file_obj)

    import_payload = {
        "data_type": data_type,
        "file_name": file_name,
        "sheet_name": parsed.sheet_name,
        "total_rows": len(parsed.rows),
        "imported_rows": 0,
        "status": "PROCESSING",
        "is_active": False,
        "created_by": created_by,
    }

    created = (
        supabase.table("data_imports")
        .insert(import_payload)
        .select("id")
        .execute()
    )
    import_id = created.data[0]["id"]
    imported = 0

    try:
        rows_with_import = [
            {**row, "import_id": import_id}
            for row in parsed.rows
        ]

        for batch in _chunks(rows_with_import):
            supabase.table(table_name).insert(
                batch,
                returning="minimal",
            ).execute()
            imported += len(batch)

        # Import lama baru dinonaktifkan setelah import baru benar-benar selesai.
        (
            supabase.table("data_imports")
            .update({"is_active": False})
            .eq("data_type", data_type)
            .eq("is_active", True)
            .execute()
        )

        (
            supabase.table("data_imports")
            .update(
                {
                    "imported_rows": imported,
                    "status": "COMPLETED",
                    "is_active": True,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            .eq("id", import_id)
            .execute()
        )

        return {
            "import_id": import_id,
            "sheet_name": parsed.sheet_name,
            "total_rows": len(parsed.rows),
            "imported_rows": imported,
        }

    except Exception as exc:
        # Hapus data staging dari import yang gagal agar data master tetap bersih.
        supabase.table(table_name).delete().eq("import_id", import_id).execute()
        (
            supabase.table("data_imports")
            .update(
                {
                    "imported_rows": imported,
                    "status": "FAILED",
                    "is_active": False,
                    "error_message": str(exc)[:2000],
                }
            )
            .eq("id", import_id)
            .execute()
        )
        raise


def get_active_import_id(supabase: Client, data_type: DataType) -> str | None:
    response = (
        supabase.table("data_imports")
        .select("id")
        .eq("data_type", data_type)
        .eq("is_active", True)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    return response.data[0]["id"]
