from __future__ import annotations

from io import BytesIO
from numbers import Integral, Real
from typing import BinaryIO

from openpyxl import load_workbook

from app.services.import_service import ImportValidationError, _read_upload

WISUDA_SHEET = "Wisuda"
WISUDA_COLUMNS = [
    "No",
    "Kode Prodi",
    "Program Studi",
    "NIM",
    "Nama",
    "Sertifikasi MOS",
    "Sertifikasi MCF",
    "Title Microsoft",
]
REQUIRED_COLUMNS = ("NIM", "Nama")
HEADER_SEARCH_ROWS = 10
MAX_ISSUES = 100


def _header_row(worksheet) -> tuple[int, list[str]]:
    for row_number in range(1, min(worksheet.max_row or 0, HEADER_SEARCH_ROWS) + 1):
        values = next(
            worksheet.iter_rows(
                min_row=row_number,
                max_row=row_number,
                values_only=True,
            )
        )
        headers = [str(value).strip() if value is not None else "" for value in values]
        present_headers = [header for header in headers if header]
        if len(present_headers) != len(set(present_headers)):
            raise ImportValidationError("Header workbook mengandung nama kolom ganda.")
        if any(header in REQUIRED_COLUMNS for header in headers):
            return row_number, headers
    if worksheet.max_row:
        values = next(worksheet.iter_rows(min_row=1, max_row=1, values_only=True))
        return 1, [str(value).strip() if value is not None else "" for value in values]
    return 1, []


def _empty(value) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _nim_text(cell) -> str:
    value = cell.value
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, bool) or not isinstance(value, (Integral, Real)):
        raise ValueError
    number = float(value)
    if not number.is_integer():
        raise ValueError
    digits = str(int(number))
    if len(digits.lstrip("-")) > 15:
        raise ValueError
    number_format = cell.number_format
    if number_format and set(number_format) == {"0"}:
        digits = digits.zfill(len(number_format))
    return digits


def validate_wisuda_workbook(
    file_obj: BinaryIO,
    file_name: str,
    max_upload_bytes: int,
) -> dict:
    content = _read_upload(file_name, file_obj, max_upload_bytes)
    try:
        workbook = load_workbook(
            BytesIO(content),
            read_only=True,
            data_only=False,
            keep_links=False,
        )
    except Exception:
        raise ImportValidationError("Workbook tidak dapat dibaca.") from None

    if WISUDA_SHEET not in workbook.sheetnames:
        workbook.close()
        raise ImportValidationError("Sheet wajib 'Wisuda' tidak ditemukan.")

    worksheet = workbook[WISUDA_SHEET]
    header_row, columns = _header_row(worksheet)
    header_positions = {name: index for index, name in enumerate(columns) if name}
    missing_columns = [name for name in REQUIRED_COLUMNS if name not in header_positions]
    issues: list[dict] = []
    empty_rows: list[int] = []
    empty_row_count = 0
    seen_nim: dict[str, int] = {}
    student_count = 0
    try:
        for row_number, row in enumerate(
            worksheet.iter_rows(min_row=header_row + 1),
            start=header_row + 1,
        ):
            if all(_empty(cell.value) for cell in row):
                empty_row_count += 1
                if len(empty_rows) < MAX_ISSUES:
                    empty_rows.append(row_number)
                continue

            student_count += 1
            for field in missing_columns:
                if len(issues) < MAX_ISSUES:
                    issues.append(
                        {
                            "source_row": row_number,
                            "field": field,
                            "code": "MISSING_COLUMN",
                            "message": f"Kolom wajib {field} tidak ditemukan.",
                        }
                    )
            if missing_columns:
                continue

            nim_cell = row[header_positions["NIM"]]
            name_cell = row[header_positions["Nama"]]
            if nim_cell.data_type == "f":
                nim = None
                nim_error = True
            else:
                try:
                    nim = _nim_text(nim_cell)
                    nim_error = not nim
                except (ValueError, OverflowError):
                    nim = None
                    nim_error = True

            if nim_error and len(issues) < MAX_ISSUES:
                issues.append(
                    {
                        "source_row": row_number,
                        "field": "NIM",
                        "code": "INVALID_NIM",
                        "message": "NIM wajib berupa teks atau angka bulat maksimal 15 digit.",
                    }
                )
            elif nim:
                if nim in seen_nim and len(issues) < MAX_ISSUES:
                    issues.append(
                        {
                            "source_row": row_number,
                            "field": "NIM",
                            "code": "DUPLICATE_NIM",
                            "message": f"NIM duplikat; pertama tercatat pada baris {seen_nim[nim]}.",
                        }
                    )
                else:
                    seen_nim[nim] = row_number

            if name_cell.data_type == "f" or _empty(name_cell.value):
                if len(issues) < MAX_ISSUES:
                    issues.append(
                        {
                            "source_row": row_number,
                            "field": "Nama",
                            "code": "REQUIRED_VALUE",
                            "message": "Nama wajib diisi sebagai teks, bukan formula.",
                        }
                    )
    finally:
        workbook.close()

    if student_count == 0:
        issues.append(
            {
                "source_row": None,
                "field": "Wisuda",
                "code": "EMPTY_FILE",
                "message": "Sheet Wisuda belum berisi baris mahasiswa.",
            }
        )

    return {
        "is_valid": not missing_columns and student_count > 0 and not issues,
        "sheet_name": WISUDA_SHEET,
        "header_row": header_row,
        "columns": columns,
        "layout_matches_template": columns[: len(WISUDA_COLUMNS)] == WISUDA_COLUMNS,
        "missing_columns": missing_columns,
        "student_count": student_count,
        "empty_row_count": empty_row_count,
        "empty_rows": empty_rows,
        "empty_rows_truncated": empty_row_count > MAX_ISSUES,
        "issues": issues,
        "issues_truncated": len(issues) >= MAX_ISSUES,
    }


def parse_wisuda_for_sync(
    file_obj: BinaryIO,
    file_name: str,
    max_upload_bytes: int,
) -> list[dict]:
    """Parse workbook Wisuda dan validasi baris mahasiswa untuk sinkronisasi.

    Mengembalikan list of dicts: [{'source_row': int, 'nim': str, 'nama': str}, ...]
    Mengangkat ImportValidationError jika format file, kolom, atau data tidak valid.
    """
    content = _read_upload(file_name, file_obj, max_upload_bytes)
    try:
        workbook = load_workbook(
            BytesIO(content),
            read_only=True,
            data_only=False,
            keep_links=False,
        )
    except Exception:
        raise ImportValidationError("Workbook tidak dapat dibaca.") from None

    if WISUDA_SHEET not in workbook.sheetnames:
        workbook.close()
        raise ImportValidationError("Sheet wajib 'Wisuda' tidak ditemukan.")

    worksheet = workbook[WISUDA_SHEET]
    header_row, columns = _header_row(worksheet)
    header_positions = {name: index for index, name in enumerate(columns) if name}
    missing_columns = [name for name in REQUIRED_COLUMNS if name not in header_positions]
    if missing_columns:
        workbook.close()
        raise ImportValidationError(f"Kolom wajib {', '.join(missing_columns)} tidak ditemukan.")

    rows: list[dict] = []
    seen_nim: dict[str, int] = {}
    try:
        for row_number, row in enumerate(
            worksheet.iter_rows(min_row=header_row + 1),
            start=header_row + 1,
        ):
            if all(_empty(cell.value) for cell in row):
                continue

            nim_cell = row[header_positions["NIM"]]
            name_cell = row[header_positions["Nama"]]

            if nim_cell.data_type == "f":
                raise ImportValidationError(f"Baris {row_number}: NIM tidak boleh berupa formula.")
            try:
                nim = _nim_text(nim_cell)
            except (ValueError, OverflowError):
                raise ImportValidationError(
                    f"Baris {row_number}: NIM wajib berupa teks atau angka bulat maksimal 15 digit."
                ) from None

            if not nim:
                raise ImportValidationError(f"Baris {row_number}: NIM tidak boleh kosong.")

            if nim in seen_nim:
                raise ImportValidationError(
                    f"Baris {row_number}: NIM {nim} duplikat; pertama tercatat pada baris {seen_nim[nim]}."
                )
            seen_nim[nim] = row_number

            if name_cell.data_type == "f" or _empty(name_cell.value):
                raise ImportValidationError(
                    f"Baris {row_number}: Nama wajib diisi sebagai teks, bukan formula."
                )

            name = str(name_cell.value).strip()
            rows.append({"source_row": row_number, "nim": nim, "nama": name})
    finally:
        workbook.close()

    if not rows:
        raise ImportValidationError("Sheet Wisuda belum berisi baris mahasiswa.")

    return rows
