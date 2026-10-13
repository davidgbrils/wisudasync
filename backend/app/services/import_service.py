from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from numbers import Integral, Real
from pathlib import Path
from typing import BinaryIO, Literal
from zipfile import BadZipFile, ZipFile, is_zipfile

import pandas as pd
from openpyxl import load_workbook
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
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_WORKBOOK_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
HEADER_SEARCH_ROWS = 10

SITASI_SHEET = "Master_Data"
CERTIPORT_SHEET = "Results (264) Plus"

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

# Kolom certiport yang lazim berisi formula CONCATENATE pada ekspor resmi.
# Nilai dibaca dari cache/last name bila formula belum tersimpan nilainya.
CERTIPORT_FORMULA_COLUMNS = frozenset({"Full Name"})


class ImportValidationError(ValueError):
    """File sumber tidak cocok dengan kontrak impor."""


class UploadTooLargeError(ImportValidationError):
    """Ukuran file melampaui batas impor."""


class ImportStorageError(RuntimeError):
    """Penyimpanan gagal; batch lama tidak diubah."""


class ImportOutcomeUnknownError(RuntimeError):
    """Status pemanggilan aktivasi batch tidak dapat dipastikan."""


@dataclass
class ParsedWorkbook:
    sheet_name: str
    rows: list[dict]


def _read_upload(
    file_name: str,
    file_obj: BinaryIO,
    max_upload_bytes: int,
) -> bytes:
    if Path(file_name).suffix.lower() != ".xlsx":
        raise ImportValidationError("File harus berformat .xlsx.")

    file_obj.seek(0)
    content = file_obj.read(max_upload_bytes + 1)
    if len(content) > max_upload_bytes:
        raise UploadTooLargeError(
            f"Ukuran file melebihi batas {max_upload_bytes} byte."
        )
    if not is_zipfile(BytesIO(content)):
        raise ImportValidationError("File bukan workbook .xlsx yang valid.")

    try:
        with ZipFile(BytesIO(content)) as archive:
            names = set(archive.namelist())
            if "[Content_Types].xml" not in names or "xl/workbook.xml" not in names:
                raise ImportValidationError("Struktur workbook .xlsx tidak valid.")
            if sum(item.file_size for item in archive.infolist()) > MAX_WORKBOOK_UNCOMPRESSED_BYTES:
                raise ImportValidationError("Isi workbook melebihi batas pemrosesan.")
            if any(name.lower().endswith("vbaproject.bin") for name in names):
                raise ImportValidationError("Workbook dengan macro tidak diizinkan.")
            content_types = archive.read("[Content_Types].xml").lower()
            if b"macroenabled" in content_types:
                raise ImportValidationError("Workbook dengan macro tidak diizinkan.")
    except (BadZipFile, KeyError, OSError):
        raise ImportValidationError("File bukan workbook .xlsx yang valid.") from None

    return content


def _header_row(worksheet, required: list[str]) -> tuple[int, list[str]]:
    for row_number in range(1, HEADER_SEARCH_ROWS + 1):
        if worksheet.max_row is not None and row_number > worksheet.max_row:
            break
        headers = [
            str(value).strip() if value is not None else ""
            for value in next(
                worksheet.iter_rows(
                    min_row=row_number,
                    max_row=row_number,
                    values_only=True,
                )
            )
        ]
        present = [header for header in headers if header]
        if len(present) != len(set(present)):
            raise ImportValidationError("Header workbook mengandung nama kolom ganda.")
        if all(column in present for column in required):
            return row_number, headers
    raise ImportValidationError("Sheet tidak memiliki seluruh header wajib.")


def _open_validated_workbook(
    content: bytes,
    expected_sheet: str,
    required: list[str],
    allow_formula_columns: frozenset[str] = frozenset(),
):
    try:
        workbook = load_workbook(
            BytesIO(content),
            read_only=True,
            data_only=False,
            keep_links=False,
        )
    except Exception:
        raise ImportValidationError("Workbook tidak dapat dibaca.") from None

    if expected_sheet not in workbook.sheetnames:
        workbook.close()
        raise ImportValidationError(f"Sheet wajib '{expected_sheet}' tidak ditemukan.")

    try:
        worksheet = workbook[expected_sheet]
        header_row, headers = _header_row(worksheet, required)
        forbidden_columns = {
            index
            for index, header in enumerate(headers, start=1)
            if header in required and header not in allow_formula_columns
        }
        if forbidden_columns:
            for row in worksheet.iter_rows(min_row=header_row + 1):
                for column_index, cell in enumerate(row, start=1):
                    if column_index in forbidden_columns and getattr(cell, "data_type", None) == "f":
                        raise ImportValidationError(
                            "Workbook dengan formula pada kolom wajib tidak diizinkan."
                        )
        return workbook, worksheet, header_row, headers
    except Exception:
        workbook.close()
        raise


def _normalize_nim(value, number_format: str | None) -> str | None:
    if isinstance(value, str) or value is None:
        return normalize_code(value)

    if isinstance(value, bool):
        return normalize_code(value)

    if isinstance(value, (Integral, Real)):
        number = float(value)
        if not number.is_integer():
            raise ImportValidationError("NIM numerik harus berupa bilangan bulat.")
        digits = str(int(number))
        if len(digits.lstrip("-")) > 15:
            raise ImportValidationError("NIM numerik lebih dari 15 digit harus disimpan sebagai teks.")
        if number_format and set(number_format) == {"0"}:
            return digits.zfill(len(number_format))
        return digits

    return normalize_code(value)


def _original_text(value) -> str | None:
    if clean_text(value) is None:
        return None
    return value if isinstance(value, str) else str(value)


def _read_sheet(
    content: bytes,
    sheet_name: str,
    required: list[str],
    allow_formula_columns: frozenset[str] = frozenset(),
):
    workbook, worksheet, header_row, headers = _open_validated_workbook(
        content,
        sheet_name,
        required,
        allow_formula_columns,
    )
    try:
        df = pd.read_excel(
            BytesIO(content),
            sheet_name=sheet_name,
            header=header_row - 1,
            dtype=object,
            engine="openpyxl",
        )
        df.columns = [str(column).strip() for column in df.columns]
        if not all(column in df.columns for column in required):
            raise ImportValidationError("Sheet tidak memiliki seluruh header wajib.")
        return workbook, worksheet, df, header_row, headers
    except Exception:
        workbook.close()
        raise


def parse_sitasi(
    file_obj: BinaryIO,
    file_name: str = "upload.xlsx",
    max_upload_bytes: int = MAX_UPLOAD_BYTES,
) -> ParsedWorkbook:
    content = _read_upload(file_name, file_obj, max_upload_bytes)
    workbook, worksheet, df, header_row, headers = _read_sheet(
        content,
        SITASI_SHEET,
        SITASI_COLUMNS,
    )
    nim_column = headers.index("NIM") + 1
    rows: list[dict] = []
    try:
        for index, row in df.iterrows():
            if row.isna().all():
                continue
            source_row = int(index) + header_row + 1
            nim_cell = worksheet.cell(row=source_row, column=nim_column)
            nama = _original_text(row["Nama"])
            rows.append(
                {
                    "source_row": source_row,
                    "nim": _normalize_nim(nim_cell.value, nim_cell.number_format),
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
    finally:
        workbook.close()

    if not rows:
        raise ImportValidationError("Workbook tidak berisi baris data.")
    return ParsedWorkbook(sheet_name=SITASI_SHEET, rows=rows)


def parse_certiport(
    file_obj: BinaryIO,
    file_name: str = "upload.xlsx",
    max_upload_bytes: int = MAX_UPLOAD_BYTES,
) -> ParsedWorkbook:
    content = _read_upload(file_name, file_obj, max_upload_bytes)
    workbook, worksheet, df, header_row, _ = _read_sheet(
        content,
        CERTIPORT_SHEET,
        CERTIPORT_COLUMNS,
        CERTIPORT_FORMULA_COLUMNS,
    )
    rows: list[dict] = []
    try:
        for index, row in df.iterrows():
            if row.isna().all():
                continue
            source_row = int(index) + header_row + 1
            first_name = _original_text(row["First Name"])
            last_name = _original_text(row["Last Name"])
            full_name = _original_text(row["Full Name"])
            if full_name is None:
                parts = [part for part in (first_name, last_name) if part]
                full_name = " ".join(parts) or None
            rows.append(
                {
                    "source_row": source_row,
                    "first_name": first_name,
                    "last_name": last_name,
                    "full_name": full_name,
                    "full_name_normalized": normalize_name(full_name),
                    "program_name": clean_text(row["Program Name"]),
                    "certification_name": clean_text(row["Certification Name"]),
                    "score": to_number(row["Score"]),
                    "result": normalize_upper(row["Result"]),
                }
            )
    finally:
        workbook.close()

    if not rows:
        raise ImportValidationError("Workbook tidak berisi baris data.")
    return ParsedWorkbook(sheet_name=CERTIPORT_SHEET, rows=rows)


def _chunks(rows: list[dict], size: int | None = None):
    if size is None:
        size = BATCH_SIZE
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def _mark_failed(supabase: Client, table_name: str, import_id: str, imported: int) -> None:
    try:
        supabase.table(table_name).delete().eq("import_id", import_id).execute()
    except Exception:
        pass
    try:
        (
            supabase.table("data_imports")
            .update(
                {
                    "imported_rows": imported,
                    "status": "FAILED",
                    "is_active": False,
                    "error_message": "Import gagal; batch sebelumnya tetap aktif.",
                }
            )
            .eq("id", import_id)
            .execute()
        )
    except Exception:
        pass


def _is_active_import(supabase: Client, import_id: str) -> bool:
    response = (
        supabase.table("data_imports")
        .select("id,status,is_active")
        .eq("id", import_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        return False
    current = response.data[0]
    return current.get("status") == "COMPLETED" and current.get("is_active") is True


def _import_result(import_id: str, parsed: ParsedWorkbook) -> dict:
    return {
        "import_id": import_id,
        "sheet_name": parsed.sheet_name,
        "total_rows": len(parsed.rows),
        "imported_rows": len(parsed.rows),
    }


def import_master_data(
    supabase: Client,
    data_type: DataType,
    file_name: str,
    file_obj: BinaryIO,
    created_by: str | None = None,
    parsed_workbook: ParsedWorkbook | None = None,
) -> dict:
    if data_type not in ("SITASI", "CERTIPORT"):
        raise ImportValidationError("Jenis data impor tidak dikenal.")

    parser = parse_sitasi if data_type == "SITASI" else parse_certiport
    table_name = "sitasi_data" if data_type == "SITASI" else "certiport_data"
    if parsed_workbook is None:
        try:
            parsed_workbook = parser(file_obj, file_name)
        except ImportValidationError:
            raise
        except Exception:
            raise ImportValidationError("Workbook gagal divalidasi.") from None
    parsed = parsed_workbook

    import_payload = {
        "data_type": data_type,
        "file_name": Path(file_name).name,
        "sheet_name": parsed.sheet_name,
        "total_rows": len(parsed.rows),
        "imported_rows": 0,
        "status": "PROCESSING",
        "is_active": False,
        "created_by": created_by,
    }

    try:
        created = (
            supabase.table("data_imports")
            .insert(import_payload)
            .select("id")
            .execute()
        )
        import_id = created.data[0]["id"]
    except Exception:
        raise ImportStorageError("Batch impor gagal dibuat.") from None

    imported = 0
    rows_with_import = [{**row, "import_id": import_id} for row in parsed.rows]
    try:
        for batch in _chunks(rows_with_import):
            supabase.table(table_name).insert(batch, returning="minimal").execute()
            imported += len(batch)
    except Exception:
        _mark_failed(supabase, table_name, import_id, imported)
        raise ImportStorageError("Data impor gagal disimpan; batch sebelumnya tetap aktif.") from None

    try:
        supabase.rpc(
            "complete_data_import",
            {"p_import_id": import_id, "p_imported_rows": imported},
        ).execute()
    except Exception:
        try:
            if _is_active_import(supabase, import_id):
                return _import_result(import_id, parsed)
        except Exception:
            raise ImportOutcomeUnknownError(
                "Status aktivasi batch belum dapat dipastikan; periksa riwayat impor."
            ) from None
        _mark_failed(supabase, table_name, import_id, imported)
        raise ImportStorageError("Batch baru gagal diaktifkan; batch sebelumnya tetap aktif.") from None

    return _import_result(import_id, parsed)


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
