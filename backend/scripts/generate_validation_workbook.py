"""Generator workbook validasi Wisuda (pratinjau manual, tanpa akses database).

Sumber data (lokal, tidak di-commit):
- data_wisuda.xlsx   sheet "Wisuda"
- data_sitasi.xlsx   sheet "Master_Data"
- data_certiport.xlsx sheet "Results (264) Plus"

Logika pencocokan TIDAK ditulis ulang di sini. Script ini memakai pipeline resmi
`app.services.matching_service.validate_wisuda_complete` agar hasil sama dengan
backend. Yang dilakukan script ini hanya: membaca file, merangkum, dan menulis
workbook pratinjau berlabel DRAFT.

Jalankan dari root repository:
    .\\backend\\venv\\Scripts\\python.exe backend\\scripts\\generate_validation_workbook.py
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.core.prodi import is_mcf_relevant
from app.services.matching_service import (
    DATA_TIDAK_DITEMUKAN,
    PENDING,
    PERLU_VERIFIKASI,
    TIDAK_LULUS,
    VALID,
    _classify_reason_code,
    _count_matching_name_words,
    _fuzzy_name_score,
    status_label,
    validate_wisuda_complete,
)
from app.services.normalization_service import clean_text, normalize_code, normalize_name

# Nama ujian untuk tampilan kolom Sertifikasi MOS/MCF.
# Alias ini disahkan pada ADR-005 (docs/14_DECISIONS.md, 2026-10-19).
EXAM_DISPLAY_NAMES: dict[str, str] = {
    "WORD": "Word 2019",
    "EXCEL": "Excel 2019",
    "POWERPOINT": "PowerPoint 2019",
    "AZURE AI-900": "Microsoft Azure AI Fundamentals",
    "AZURE AZ-900": "Microsoft Azure Fundamentals",
    "AZURE DP-900": "Microsoft Azure Data Fundamentals",
    "AZURE SC-900": "Microsoft Azure Security Fundamentals",
    "TIDAK DIKETAHUI": "Belum Ujian",
}

# Placeholder pendaftaran awal, bukan ujian riil.
PLACEHOLDER_SUB_PROGRAMS = {"TIDAK DIKETAHUI", "UNKNOWN", "", "PENDAFTARAN", "BELUM UJIAN"}

# Label yang boleh muncul pada kolom hasil.
ALLOWED_LABELS = {
    "Lulus",
    "Tidak Lulus",
    "Tidak Ada",
    "Perlu Verifikasi",
    "Menunggu Hasil",
    status_label(None),
    "— (tidak relevan)",
}

DRAFT_PREFIX = "[DRAFT] "

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=10)
TITLE_FONT = Font(color="1F4E78", bold=True, size=16)
SUBTITLE_FONT = Font(color="666666", size=10)
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP_TOP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)

GREEN = "C6EFCE"
YELLOW = "FFEB9C"
RED = "FFC7CE"
BLUE = "BDD7EE"
GREY = "E7E6E6"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def unique_join(values: Any, sep: str = "; ", empty: str = "-") -> str:
    """Gabungkan nilai unik menjadi satu sel."""
    out: list[str] = []
    for value in values:
        text = clean_text(value)
        if text and text not in out:
            out.append(text)
    return sep.join(out) if out else empty


def fmt_score(value: Any) -> Any:
    """Ubah nilai skor menjadi int/float; biarkan non-numerik apa adanya."""
    if value is None:
        return None
    try:
        number = float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return value
    return int(number) if number.is_integer() else number


def exam_display_name(sub_program: Any) -> str:
    """Nama ujian kanonik untuk tampilan (Word -> Word 2019)."""
    text = clean_text(sub_program) or ""
    return EXAM_DISPLAY_NAMES.get(text.upper(), text or "Tanpa Nama Ujian")


def status_fill(value: Any) -> str | None:
    """Warna sel berdasarkan label hasil."""
    text = str(value or "").upper()
    if text == "LULUS":
        return GREEN
    if "PERLU VERIFIKASI" in text or "AMBIGU" in text or "KANDIDAT" in text or "BEDA" in text or "SEBAGIAN" in text:
        return YELLOW
    if "TIDAK LULUS" in text or "FAIL" in text:
        return RED
    if "MENUNGGU" in text or "PENDING" in text:
        return BLUE
    if "TIDAK ADA" in text or text in {status_label(None), "— (TIDAK RELEVAN)"}:
        return GREY
    return None


# ---------------------------------------------------------------------------
# Pembacaan data
# ---------------------------------------------------------------------------
def load_sources(wisuda_path: Path, sitasi_path: Path, certiport_path: Path) -> tuple[list[dict], list[dict], list[dict]]:
    """Baca tiga workbook sumber menjadi list of dict sesuai kebutuhan pipeline."""
    wisuda_df = pd.read_excel(wisuda_path, sheet_name="Wisuda")
    sitasi_df = pd.read_excel(sitasi_path, sheet_name="Master_Data")
    certiport_df = pd.read_excel(certiport_path, sheet_name="Results (264) Plus")

    wisuda_rows: list[dict] = []
    for index, row in wisuda_df.iterrows():
        wisuda_rows.append(
            {
                "source_row": index + 2,
                "no": row.get("No"),
                "kode_prodi": normalize_code(row.get("Kode Prodi")),
                "program_studi": clean_text(row.get("Program Studi")),
                "nim": normalize_code(row.get("NIM")),
                "nama": clean_text(row.get("Nama")),
                "mos_asli": clean_text(row.get("Sertifikasi MOS")),
                "mcf_asli": clean_text(row.get("Sertifikasi MCF")),
                "title_asli": clean_text(row.get("Title Microsoft")),
            }
        )

    sitasi_rows: list[dict] = []
    for index, row in sitasi_df.iterrows():
        nama = clean_text(row.get("Nama"))
        sitasi_rows.append(
            {
                "id": f"SIT-{index + 2}",
                "source_row": index + 2,
                "nim": normalize_code(row.get("NIM")),
                "nama": nama,
                "nama_normalized": normalize_name(nama),
                "fakultas": clean_text(row.get("Fakultas")),
                "kode_nim": normalize_code(row.get("Kode NIM")),
                "program_studi": clean_text(row.get("Program Studi")),
                "angkatan": normalize_code(row.get("Angkatan")),
                "sertifikasi": clean_text(row.get("Sertifikasi")),
                "sub_program": clean_text(row.get("Sub Program")),
                "nilai": row.get("Nilai"),
                "status": clean_text(row.get("Status")),
            }
        )

    certiport_rows: list[dict] = []
    for index, row in certiport_df.iterrows():
        full_name = clean_text(row.get("Full Name"))
        certiport_rows.append(
            {
                "id": f"CERT-{index + 2}",
                "source_row": index + 2,
                "full_name": full_name,
                "full_name_normalized": normalize_name(full_name),
                "program_name": clean_text(row.get("Program Name")),
                "certification_name": clean_text(row.get("Certification Name")),
                "score": row.get("Score"),
                "result": clean_text(row.get("Result")),
            }
        )

    return wisuda_rows, sitasi_rows, certiport_rows


# ---------------------------------------------------------------------------
# Kandidat Certiport
# ---------------------------------------------------------------------------
def cert_search_names(result: dict) -> list[str]:
    """Nama acuan pencarian Certiport: nama Wisuda + nama pada attempt SITASI."""
    names: list[str] = []
    wisuda_name = normalize_name(result.get("nama"))
    if wisuda_name:
        names.append(wisuda_name)
    for exam in result.get("exams", []):
        for attempt in exam.get("attempts", []):
            name = normalize_name(attempt.get("nama"))
            if name and name not in names:
                names.append(name)
    return names


def cert_candidates(result: dict, limit: int = 5) -> list[dict]:
    """Kandidat Certiport milik satu baris wisuda; exact name didahulukan."""
    cert_match = result.get("certiport_match", {}) or {}
    candidates = cert_match.get("candidates", []) or []
    exact_names = set(cert_search_names(result))
    exact = [c for c in candidates if c.get("name") in exact_names]
    if cert_match.get("status") == "MATCHED":
        return exact
    rest = [c for c in candidates if c.get("name") not in exact_names]
    return (exact + rest)[:limit]


def candidate_matched_words(result: dict, candidate_name: str) -> int | None:
    """Jumlah kata yang sama antara nama acuan dan nama kandidat."""
    search_names = cert_search_names(result)
    if not search_names:
        return None
    return max(_count_matching_name_words(name, candidate_name) for name in search_names)


# ---------------------------------------------------------------------------
# Label ringkas
# ---------------------------------------------------------------------------
def sitasi_status_label(result: dict) -> str:
    """Ketersediaan data SITASI untuk satu baris wisuda."""
    nim = result.get("nim_normalized")
    if not nim or not result.get("_sitasi_by_nim", {}).get(nim):
        return "TIDAK ADA"
    name_match = result.get("name_match")
    if name_match == "EXACT":
        return "ADA - NIM & nama cocok"
    if name_match == "PARTIAL":
        return "ADA - NIM cocok, sebagian nama cocok"
    if name_match == "DIFFERENT":
        return "ADA - NIM cocok, nama beda"
    return "ADA - NIM cocok"


def cert_status_label(result: dict) -> str:
    """Ketersediaan data Certiport untuk satu baris wisuda."""
    cert_match = result.get("certiport_match", {}) or {}
    status = cert_match.get("status")
    candidates = cert_candidates(result)
    wisuda_name = normalize_name(result.get("nama"))
    exact_via_wisuda = any(c.get("name") == wisuda_name for c in candidates)
    if status == "MATCHED":
        return "ADA - nama cocok (Wisuda)" if exact_via_wisuda else "ADA - nama cocok (SITASI)"
    if status == PERLU_VERIFIKASI:
        return "AMBIGU - ada nama cocok + kandidat lain" if candidates else "AMBIGU - beberapa kandidat"
    if status == "FUZZY_ONLY":
        return "ADA - kandidat nama mirip"
    return "TIDAK ADA"


def mcf_label(result: dict) -> str:
    """Label hasil MCF; prodi non-31/32 tidak menghitung MCF."""
    mcf_status = result.get("mcf_status")
    if mcf_status is None:
        return "— (tidak relevan)"
    return status_label(mcf_status)


def certiport_status_for_exam(combined_status: str, evidence: list[dict]) -> str:
    """Ringkasan hasil Certiport untuk satu ujian, dalam bahasa manusia.

    Nilai mentah PASS/FAIL tetap tersedia pada kolom 'Hasil Certiport'.
    """
    results = {str(item.get("result") or "").upper() for item in evidence}
    results.discard("")
    if not results:
        return "Tidak Ada"
    if "PASS" in results and "FAIL" in results:
        base = "Lulus + ada FAIL sebelumnya"
    elif "PASS" in results:
        base = "Lulus"
    elif "FAIL" in results:
        base = "Tidak Lulus"
    else:
        base = "Perlu Verifikasi"
    if combined_status == PERLU_VERIFIKASI and base in {"Lulus", "Tidak Lulus"}:
        base = f"{base} (perlu konfirmasi)"
    return base


def corrected_reason(exam: dict, cert_match: dict) -> tuple[str, str]:
    """Kode alasan + keterangan per ujian, dengan koreksi kasus konflik lama.

    Kasus: SITASI LULUS dan Certiport PASS pada ujian yang sama, tetapi Certiport
    juga menyimpan attempt FAIL sebelumnya. Bukti sebenarnya konsisten (VALID),
    namun mesin menandai "konflik sumber" karena presence salah satu FAIL.
    Keterangan diperbaiki menjadi VALID; status tetap 'Perlu Verifikasi' karena
    petugas harus memastikan attempt terakhir.
    """
    validation = exam.get("certiport_validation", {}) or {}
    evidence = validation.get("certiport_evidence", []) or []
    results = [item.get("result") for item in evidence]
    has_lulus = bool(exam.get("has_lulus")) and not exam.get("certiport_only")
    if (
        has_lulus
        and "PASS" in results
        and "FAIL" in results
        and validation.get("combined_status") == PERLU_VERIFIKASI
    ):
        pass_scores = [fmt_score(item.get("score")) for item in evidence if item.get("result") == "PASS"]
        fail_scores = [fmt_score(item.get("score")) for item in evidence if item.get("result") == "FAIL"]
        note = (
            f"VALID: SITASI LULUS (skor {fmt_score(exam.get('score'))}) dan Certiport PASS "
            f"(skor {', '.join(str(score) for score in pass_scores)}) pada ujian yang sama. "
            f"Certiport juga menyimpan attempt FAIL sebelumnya (skor {', '.join(str(score) for score in fail_scores)}), "
            "sehingga status tetap Perlu Verifikasi sampai petugas memastikan attempt terakhir."
        )
        return "R01_VALID", note
    return _classify_reason_code(validation, cert_match), validation.get("reason") or "-"


def corrected_valid_notes(result: dict) -> list[str]:
    """Nama ujian yang buktinya valid (LULUS + PASS) meski ada attempt FAIL lama."""
    cert_match = result.get("certiport_match", {}) or {}
    notes: list[str] = []
    for exam in result.get("exams", []):
        code, _ = corrected_reason(exam, cert_match)
        engine_code = _classify_reason_code(exam.get("certiport_validation", {}) or {}, cert_match)
        if code == "R01_VALID" and engine_code != "R01_VALID":
            notes.append(f"{exam.get('sertifikasi') or '-'} / {exam.get('sub_program') or '-'}")
    return notes


def corrected_row_codes(result: dict) -> list[str]:
    """Kode alasan tingkat baris, diselaraskan dengan koreksi pada level ujian."""
    codes = list(result.get("reason_codes") or [])
    cert_match = result.get("certiport_match", {}) or {}
    corrected = False
    for exam in result.get("exams", []):
        code, _ = corrected_reason(exam, cert_match)
        if code == "R01_VALID" and _classify_reason_code(
            exam.get("certiport_validation", {}) or {}, cert_match
        ) != "R01_VALID":
            corrected = True
    if corrected:
        codes = [code for code in codes if code != "R04_CERTIPORT_NO_PASS"]
        codes.append("R01_VALID")
    return sorted(set(codes))


def sitasi_programs_text(result: dict) -> str:
    """Ringkasan program/ujian SITASI beserta statusnya."""
    parts: list[str] = []
    for exam in result.get("exams", []):
        if exam.get("certiport_only"):
            continue
        score = fmt_score(exam.get("score"))
        parts.append(
            f"{exam.get('sertifikasi') or '-'} / {exam.get('sub_program') or '-'}"
            f" ({status_label(exam.get('exam_status'))}, skor {score if score is not None else '-'})"
        )
    return "; ".join(parts) if parts else "-"


def cert_programs_text(result: dict, cert_by_name: dict[str, list[dict]]) -> str:
    """Ringkasan program/ujian Certiport dari kandidat yang dipakai."""
    parts: list[str] = []
    for candidate in cert_candidates(result):
        for record in cert_by_name.get(candidate.get("name"), []):
            score = fmt_score(record.get("score"))
            parts.append(
                f"{record.get('program_name') or '-'} / {record.get('certification_name') or '-'}"
                f" ({record.get('result') or '-'}, skor {score if score is not None else '-'})"
            )
    return "; ".join(parts) if parts else "-"


def cert_names_text(result: dict) -> str:
    """Nama kandidat Certiport beserta skor kesamaan nama."""
    candidates = cert_candidates(result)
    if not candidates:
        return "-"
    return "; ".join(f"{c.get('name')} ({c.get('score')})" for c in candidates)


def pratinjau_certification_text(result: dict, program: str) -> str:
    """Teks kolom Sertifikasi MOS/MCF untuk pratinjau (format Opsi 1A ADR-003)."""
    summary = (result.get("program_summary") or {}).get(program)
    if not summary:
        return f"{DRAFT_PREFIX}Tidak Ada"
    details = summary.get("exam_details", [])
    concrete = [
        detail
        for detail in details
        if (detail.get("sub_program") or "").strip().upper() not in PLACEHOLDER_SUB_PROGRAMS
    ]
    # Placeholder pendaftaran ("Belum Ujian") tidak ditampilkan bila sudah ada ujian riil.
    used = concrete if concrete else details
    parts: list[str] = []
    for detail in used:
        sub_program = (detail.get("sub_program") or "").strip().upper()
        exam_name = exam_display_name(detail.get("sub_program"))
        label = status_label(detail.get("combined_status"))
        if sub_program in PLACEHOLDER_SUB_PROGRAMS and label == "Perlu Verifikasi":
            label = status_label(PENDING)
        parts.append(f"{program} ({exam_name} - {label})")
    if not parts:
        return f"{DRAFT_PREFIX}Tidak Ada"
    return f"{DRAFT_PREFIX}" + ", ".join(parts)


def pratinjau_title_text(result: dict) -> str:
    """Teks kolom Title Microsoft (Opsi 4A ADR-003, masih TERBUKA)."""
    titles: list[str] = []
    if result.get("mos_status") == VALID:
        titles.append("MOS")
    if result.get("mcf_status") == VALID:
        titles.append("MCF")
    if not titles:
        return "—"
    return f"{DRAFT_PREFIX}" + ", ".join(titles)


# ---------------------------------------------------------------------------
# Penyusun workbook
# ---------------------------------------------------------------------------
def write_table(
    ws,
    headers: list[str],
    rows: list[list[Any]],
    widths: list[int],
    status_cols: tuple[int, ...] = (),
    wrap_cols: tuple[int, ...] = (),
) -> None:
    """Tulis tabel sederhana dengan header, filter, dan pewarnaan status."""
    ws.append(headers)
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER
        cell.border = BORDER
    for row in rows:
        ws.append(row)
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=len(headers)):
        for cell in row:
            cell.border = BORDER
            cell.alignment = WRAP_TOP if cell.column in wrap_cols else Alignment(vertical="top")
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width
    ws.freeze_panes = "A2"
    if ws.max_row >= 1:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{ws.max_row}"
    for col_index in status_cols:
        for row_index in range(2, ws.max_row + 1):
            cell = ws.cell(row=row_index, column=col_index)
            color = status_fill(cell.value)
            if color:
                cell.fill = PatternFill("solid", fgColor=color)
    ws.sheet_view.showGridLines = False


def build_workbook(results: list[dict], wisuda_rows: list[dict], sitasi_rows: list[dict], certiport_rows: list[dict]) -> Workbook:
    """Susun seluruh sheet workbook dari hasil validasi."""
    sitasi_by_nim: dict[str, list[dict]] = defaultdict(list)
    sitasi_by_name: dict[str, list[dict]] = defaultdict(list)
    for row in sitasi_rows:
        if row["nim"]:
            sitasi_by_nim[row["nim"]].append(row)
        if row["nama_normalized"]:
            sitasi_by_name[row["nama_normalized"]].append(row)

    cert_by_name: dict[str, list[dict]] = defaultdict(list)
    for row in certiport_rows:
        if row["full_name_normalized"]:
            cert_by_name[row["full_name_normalized"]].append(row)

    wisuda_by_row = {row["source_row"]: row for row in wisuda_rows}
    for result in results:
        result["_sitasi_by_nim"] = sitasi_by_nim

    wb = Workbook()

    # --- Sheet 1: Ringkasan Validasi ---
    ringkasan_headers = [
        "No", "Baris Excel", "Kode Prodi", "Program Studi (Wisuda)", "Program Studi (dari NIM)",
        "NIM", "Nama (Wisuda)",
        "Status Data SITASI", "Jumlah Baris SITASI", "Nama di SITASI", "Program Studi di SITASI",
        "Program/Ujian SITASI", "Status Ujian SITASI",
        "Status Data Certiport", "Nama di Certiport", "Program/Ujian Certiport",
        "Hasil MOS", "Skor MOS", "Hasil MCF", "Skor MCF",
        "Hasil Validasi", "Kode Alasan", "Perlu Review", "Catatan Review",
        "MOS di file Wisuda", "Title Microsoft di file Wisuda",
    ]
    ringkasan_rows: list[list[Any]] = []
    for result in results:
        wr = wisuda_by_row.get(result.get("source_row"), {})
        nim = result.get("nim_normalized")
        raw_sitasi = sitasi_by_nim.get(nim, []) if nim else []
        review_flags = list(result.get("review_flags") or [])
        if corrected_valid_notes(result):
            review_flags.append(
                "Bukti valid pada "
                + ", ".join(corrected_valid_notes(result))
                + " (SITASI LULUS + Certiport PASS); tetap perlu review karena ada attempt FAIL sebelumnya."
            )
        ringkasan_rows.append(
            [
                wr.get("no"),
                result.get("source_row"),
                wr.get("kode_prodi"),
                wr.get("program_studi"),
                result.get("program_studi"),
                result.get("nim"),
                result.get("nama"),
                sitasi_status_label(result),
                len(raw_sitasi),
                unique_join([x.get("nama") for x in raw_sitasi]),
                unique_join([x.get("program_studi") for x in raw_sitasi]),
                sitasi_programs_text(result),
                unique_join(
                    [
                        f"{exam.get('sertifikasi') or '-'} / {exam.get('sub_program') or '-'}: {status_label(exam.get('exam_status'))}"
                        for exam in result.get("exams", [])
                        if not exam.get("certiport_only")
                    ]
                ),
                cert_status_label(result),
                cert_names_text(result),
                cert_programs_text(result, cert_by_name),
                status_label(result.get("mos_status")),
                fmt_score(result.get("mos_score")),
                mcf_label(result),
                fmt_score(result.get("mcf_score")),
                status_label(result.get("validation_status")),
                ", ".join(corrected_row_codes(result)),
                "Ya" if result.get("needs_review") else "Tidak",
                "; ".join(review_flags) if review_flags else "-",
                wr.get("mos_asli") or "-",
                wr.get("title_asli") or "-",
            ]
        )

    ws = wb.create_sheet("Ringkasan Validasi")
    write_table(
        ws,
        ringkasan_headers,
        ringkasan_rows,
        widths=[6, 8, 8, 28, 28, 13, 32, 32, 9, 40, 28, 55, 55, 30, 40, 55, 14, 10, 20, 10, 18, 30, 10, 65, 40, 20],
        status_cols=(8, 14, 17, 19, 21),
        wrap_cols=(4, 5, 7, 10, 11, 12, 13, 15, 16, 22, 24, 25, 26),
    )

    # --- Sheet 2: Pratinjau Kolom Wisuda ---
    pratinjau_headers = [
        "No", "Kode Prodi", "Program Studi", "NIM", "Nama",
        "Sertifikasi MOS [DRAFT]", "Sertifikasi MCF [DRAFT]", "Title Microsoft [DRAFT]",
        "Sertifikasi MOS (nilai asli file)", "Title Microsoft (nilai asli file)", "Catatan Perbedaan",
    ]
    pratinjau_rows: list[list[Any]] = []
    for result in results:
        wr = wisuda_by_row.get(result.get("source_row"), {})
        mos_text = pratinjau_certification_text(result, "MOS")
        mcf_text = (
            "— (tidak relevan)"
            if not is_mcf_relevant(result.get("kode_prodi"))
            else pratinjau_certification_text(result, "MCF")
        )
        title_text = pratinjau_title_text(result)
        catatan: list[str] = []
        if wr.get("mos_asli") and wr["mos_asli"] not in mos_text:
            catatan.append("Teks MOS pada file asli tidak sama dengan hasil sinkronisasi.")
        if wr.get("title_asli") and wr["title_asli"].upper() not in title_text.upper():
            catatan.append("Title Microsoft pada file asli tidak sama dengan hasil sinkronisasi.")
        if result.get("needs_review"):
            catatan.append("Perlu review petugas: " + "; ".join(result.get("review_flags") or []))
        if corrected_valid_notes(result):
            catatan.append(
                "Bukti valid teridentifikasi pada "
                + ", ".join(corrected_valid_notes(result))
                + " (LULUS + PASS); status tetap Perlu Verifikasi karena ada attempt FAIL sebelumnya."
            )
        pratinjau_rows.append(
            [
                wr.get("no"),
                wr.get("kode_prodi"),
                wr.get("program_studi"),
                result.get("nim"),
                result.get("nama"),
                mos_text,
                mcf_text,
                title_text,
                wr.get("mos_asli") or "-",
                wr.get("title_asli") or "-",
                "; ".join(catatan) if catatan else "-",
            ]
        )

    ws = wb.create_sheet("Pratinjau Kolom Wisuda")
    write_table(
        ws,
        pratinjau_headers,
        pratinjau_rows,
        widths=[6, 8, 28, 13, 32, 46, 46, 22, 40, 24, 70],
        status_cols=(6, 7, 8),
        wrap_cols=(3, 5, 6, 7, 8, 9, 10, 11),
    )

    # --- Sheet 3: Detail Ujian ---
    detail_ujian_headers = [
        "No", "NIM", "Nama (Wisuda)", "Program Studi", "Program", "Sub Program",
        "Status Attempt SITASI", "Skor SITASI", "Nama SITASI", "Jumlah Attempt SITASI",
        "Status Certiport", "Hasil Certiport", "Skor Certiport", "Nama Certiport",
        "Hasil Ujian", "Kode Alasan", "Sumber Bukti", "Catatan",
    ]
    detail_ujian_rows: list[list[Any]] = []
    for result in results:
        wr = wisuda_by_row.get(result.get("source_row"), {})
        cert_match = result.get("certiport_match", {}) or {}
        for exam in result.get("exams", []):
            validation = exam.get("certiport_validation", {}) or {}
            evidence = validation.get("certiport_evidence", []) or []
            selected = exam.get("selected_attempt") or {}
            if exam.get("certiport_only"):
                sitasi_status = "-"
                sitasi_score = None
                sitasi_name = "-"
                attempt_count = 0
                sumber = "Certiport"
            else:
                sitasi_status = selected.get("status") or "-"
                sitasi_score = exam.get("score")
                sitasi_name = selected.get("nama") or "-"
                attempt_count = len(exam.get("attempts", []))
                sumber = "SITASI + Certiport" if evidence else "SITASI"
            detail_ujian_rows.append(
                [
                    wr.get("no"),
                    result.get("nim"),
                    result.get("nama"),
                    result.get("program_studi"),
                    exam.get("sertifikasi") or "-",
                    exam.get("sub_program") or "-",
                    sitasi_status,
                    fmt_score(sitasi_score),
                    sitasi_name,
                    attempt_count,
                    certiport_status_for_exam(validation.get("combined_status", ""), evidence),
                    unique_join([item.get("result") for item in evidence]),
                    unique_join([fmt_score(item.get("score")) for item in evidence]),
                    unique_join([item.get("full_name") for item in evidence]),
                    status_label(validation.get("combined_status") or exam.get("exam_status")),
                    corrected_reason(exam, cert_match)[0],
                    sumber,
                    corrected_reason(exam, cert_match)[1],
                ]
            )

    ws = wb.create_sheet("Detail Ujian")
    write_table(
        ws,
        detail_ujian_headers,
        detail_ujian_rows,
        widths=[6, 13, 32, 28, 10, 22, 18, 10, 32, 10, 16, 12, 10, 32, 18, 22, 20, 60],
        status_cols=(7, 11, 15),
        wrap_cols=(3, 4, 6, 9, 14, 16, 17, 18),
    )

    # --- Sheet 4: Detail SITASI ---
    detail_sitasi_headers = [
        "No", "NIM", "Nama (Wisuda)", "Program Studi (Wisuda)",
        "Baris SITASI", "NIM SITASI", "Nama SITASI", "Fakultas", "Kode NIM",
        "Program Studi SITASI", "Angkatan", "Sertifikasi", "Sub Program",
        "Nilai", "Status", "Kecocokan Nama", "Hasil Validasi",
    ]
    detail_sitasi_rows: list[list[Any]] = []
    for result in results:
        wr = wisuda_by_row.get(result.get("source_row"), {})
        nim = result.get("nim_normalized")
        wisuda_name = normalize_name(result.get("nama")) or ""
        for raw in sitasi_by_nim.get(nim, []) if nim else []:
            record_name = normalize_name(raw.get("nama")) or ""
            if record_name and wisuda_name and record_name == wisuda_name:
                match = "COCOK"
            elif record_name and wisuda_name:
                match = "BEDA"
            else:
                match = "TIDAK ADA NAMA"
            detail_sitasi_rows.append(
                [
                    wr.get("no"),
                    result.get("nim"),
                    result.get("nama"),
                    wr.get("program_studi"),
                    raw.get("source_row"),
                    raw.get("nim"),
                    raw.get("nama"),
                    raw.get("fakultas"),
                    raw.get("kode_nim"),
                    raw.get("program_studi"),
                    raw.get("angkatan"),
                    raw.get("sertifikasi"),
                    raw.get("sub_program"),
                    fmt_score(raw.get("nilai")),
                    raw.get("status"),
                    match,
                    status_label(result.get("validation_status")),
                ]
            )

    ws = wb.create_sheet("Detail SITASI")
    write_table(
        ws,
        detail_sitasi_headers,
        detail_sitasi_rows,
        widths=[6, 13, 32, 28, 8, 13, 32, 14, 8, 28, 8, 10, 22, 8, 12, 18, 18],
        status_cols=(15, 17),
        wrap_cols=(3, 4, 7, 10, 13),
    )

    # --- Sheet 5: Detail Certiport ---
    detail_cert_headers = [
        "No", "NIM", "Nama (Wisuda)", "Program Studi", "Tipe Kecocokan",
        "Nama Kandidat Certiport", "Skor Nama", "Kata Cocok",
        "Baris Certiport", "Program Name", "Certification Name", "Score", "Result",
        "Dipakai Sebagai", "Catatan",
    ]
    detail_cert_rows: list[list[Any]] = []
    for result in results:
        wr = wisuda_by_row.get(result.get("source_row"), {})
        cert_match = result.get("certiport_match", {}) or {}
        status = cert_match.get("status")
        if status == DATA_TIDAK_DITEMUKAN:
            continue
        exact_names = set(cert_search_names(result))
        wisuda_name = normalize_name(result.get("nama"))
        for candidate in cert_candidates(result):
            is_exact = candidate.get("name") in exact_names
            if status == "MATCHED" and candidate.get("name") == wisuda_name:
                tipe = "Nama cocok persis (Wisuda)"
                dipakai = "Bukti utama"
                catatan = "Kandidat tunggal berdasarkan nama Wisuda."
            elif status == "MATCHED":
                tipe = "Nama cocok persis (SITASI)"
                dipakai = "Bukti utama"
                catatan = "Nama cocok dengan nama pada SITASI, bukan nama Wisuda."
            elif is_exact:
                tipe = "Nama cocok persis (ambigu)"
                dipakai = "Kandidat"
                catatan = "Ada nama cocok, tetapi ada kandidat lain; perlu verifikasi."
            else:
                tipe = "Kandidat nama mirip"
                dipakai = "Saran"
                catatan = "Bukan exact name; tidak dipakai otomatis untuk validasi."
            for record in cert_by_name.get(candidate.get("name"), []):
                detail_cert_rows.append(
                    [
                        wr.get("no"),
                        result.get("nim"),
                        result.get("nama"),
                        result.get("program_studi"),
                        tipe,
                        record.get("full_name"),
                        candidate.get("score"),
                        candidate_matched_words(result, candidate.get("name")),
                        record.get("source_row"),
                        record.get("program_name"),
                        record.get("certification_name"),
                        fmt_score(record.get("score")),
                        record.get("result"),
                        dipakai,
                        catatan,
                    ]
                )

    ws = wb.create_sheet("Detail Certiport")
    write_table(
        ws,
        detail_cert_headers,
        detail_cert_rows,
        widths=[6, 13, 32, 28, 28, 34, 8, 8, 8, 38, 42, 8, 8, 16, 55],
        status_cols=(13,),
        wrap_cols=(3, 4, 5, 6, 10, 11, 15),
    )

    # --- Sheet 6: Kandidat Nama SITASI ---
    candidate_headers = [
        "No", "NIM (Wisuda)", "Nama (Wisuda)", "Program Studi",
        "Kandidat Nama SITASI", "Skor Nama", "Kata Cocok",
        "NIM SITASI", "Program Studi SITASI", "Program/Ujian SITASI", "Status Ujian",
        "Catatan",
    ]
    candidate_rows: list[list[Any]] = []
    sitasi_names = list(sitasi_by_name.keys())
    for result in results:
        if result.get("nim_normalized") and sitasi_by_nim.get(result.get("nim_normalized")):
            continue
        wr = wisuda_by_row.get(result.get("source_row"), {})
        target = normalize_name(result.get("nama")) or ""
        if not target:
            continue
        required_words = min(2, len(target.split()))
        found: list[dict] = []
        for candidate_name in sitasi_names:
            score = _fuzzy_name_score(target, candidate_name)
            if score < 85:
                continue
            matched_words = _count_matching_name_words(target, candidate_name)
            if matched_words < required_words:
                continue
            found.append(
                {
                    "name": candidate_name,
                    "score": score,
                    "matched_words": matched_words,
                    "exact": candidate_name == target,
                    "records": sitasi_by_name.get(candidate_name, []),
                }
            )
        found.sort(key=lambda item: (not item["exact"], -item["score"], -item["matched_words"]))
        for candidate in found[:3]:
            nims: list[str] = []
            prodis: list[str] = []
            programs: list[str] = []
            statuses: list[str] = []
            for record in candidate["records"]:
                if record.get("nim") and record["nim"] not in nims:
                    nims.append(record["nim"])
                if record.get("program_studi") and record["program_studi"] not in prodis:
                    prodis.append(record["program_studi"])
                program = f"{record.get('sertifikasi') or '-'} / {record.get('sub_program') or '-'}"
                if program not in programs:
                    programs.append(program)
                status = record.get("status") or "-"
                if status not in statuses:
                    statuses.append(status)
            catatan = (
                "Nama sama, NIM berbeda; perlu verifikasi manual."
                if candidate["exact"]
                else "Kandidat nama mirip; perlu verifikasi manual."
            )
            if len(nims) > 1:
                catatan += " Kandidat memiliki beberapa NIM."
            candidate_rows.append(
                [
                    wr.get("no"),
                    result.get("nim"),
                    result.get("nama"),
                    wr.get("program_studi"),
                    candidate["name"],
                    candidate["score"],
                    candidate["matched_words"],
                    "; ".join(nims[:5]) + (" ..." if len(nims) > 5 else ""),
                    "; ".join(prodis[:3]),
                    "; ".join(programs[:5]) + (" ..." if len(programs) > 5 else ""),
                    "; ".join(statuses),
                    catatan,
                ]
            )

    ws = wb.create_sheet("Kandidat Nama SITASI")
    write_table(
        ws,
        candidate_headers,
        candidate_rows,
        widths=[6, 13, 32, 28, 34, 8, 8, 22, 28, 55, 30, 48],
        wrap_cols=(3, 4, 5, 8, 9, 10, 11, 12),
    )

    # --- Sheet 7: Tidak Ditemukan ---
    notfound_headers = [
        "No", "Baris Excel", "Kode Prodi", "Program Studi", "NIM", "Nama",
        "Status Data SITASI", "Status Data Certiport", "Hasil Validasi", "Catatan",
    ]
    notfound_rows: list[list[Any]] = []
    for result in results:
        if sitasi_status_label(result) != "TIDAK ADA" or cert_status_label(result) != "TIDAK ADA":
            continue
        wr = wisuda_by_row.get(result.get("source_row"), {})
        notfound_rows.append(
            [
                wr.get("no"),
                result.get("source_row"),
                wr.get("kode_prodi"),
                wr.get("program_studi"),
                result.get("nim"),
                result.get("nama"),
                sitasi_status_label(result),
                cert_status_label(result),
                status_label(result.get("validation_status")),
                "Tidak ada data SITASI/Certiport berdasarkan NIM dan nama.",
            ]
        )

    ws = wb.create_sheet("Tidak Ditemukan")
    write_table(
        ws,
        notfound_headers,
        notfound_rows,
        widths=[6, 8, 8, 28, 13, 32, 18, 18, 18, 50],
        status_cols=(7, 8, 9),
        wrap_cols=(4, 6, 10),
    )

    # --- Sheet 8: Rekap Prodi ---
    prodi_stats: dict[str, Counter] = {}
    for row in ringkasan_rows:
        prodi = row[3] or "-"
        stats = prodi_stats.setdefault(prodi, Counter())
        stats["total"] += 1
        if str(row[7]).startswith("ADA"):
            stats["sitasi_nim"] += 1
        if row[7] == "ADA - NIM & nama cocok":
            stats["sitasi_nama"] += 1
        if row[7] in ("ADA - NIM cocok, nama beda", "ADA - NIM cocok, sebagian nama cocok"):
            stats["sitasi_beda"] += 1
        cert_label = str(row[13])
        if cert_label == "ADA - nama cocok (Wisuda)" or cert_label == "ADA - nama cocok (SITASI)":
            stats["cert_cocok"] += 1
        elif "AMBIGU" in cert_label or "KANDIDAT" in cert_label:
            stats["cert_kandidat"] += 1
        else:
            stats["cert_tidak"] += 1
        for label in ("Lulus", "Tidak Lulus", "Perlu Verifikasi", "Tidak Ada", "Menunggu Hasil"):
            if row[16] == label:
                stats[f"mos_{label}"] += 1
            if row[18] == label:
                stats[f"mcf_{label}"] += 1
            if row[20] == label:
                stats[f"overall_{label}"] += 1

    rekap_headers = [
        "Program Studi", "Total",
        "SITASI NIM Ditemukan", "SITASI Nama Cocok", "SITASI Nama Beda",
        "Certiport Nama Cocok", "Certiport Kandidat/Ambigu", "Certiport Tidak Ada",
        "MOS Lulus", "MOS Tidak Lulus", "MOS Perlu Verifikasi", "MOS Tidak Ada",
        "MCF Lulus", "MCF Tidak Lulus", "MCF Perlu Verifikasi", "MCF Tidak Ada",
        "Overall Lulus", "Overall Tidak Lulus", "Overall Perlu Verifikasi",
        "Overall Menunggu Hasil", "Overall Tidak Ada",
    ]
    rekap_rows: list[list[Any]] = []
    for prodi, stats in sorted(prodi_stats.items(), key=lambda item: (-item[1]["total"], item[0])):
        rekap_rows.append(
            [
                prodi,
                stats["total"],
                stats["sitasi_nim"],
                stats["sitasi_nama"],
                stats["sitasi_beda"],
                stats["cert_cocok"],
                stats["cert_kandidat"],
                stats["cert_tidak"],
                stats["mos_Lulus"],
                stats["mos_Tidak Lulus"],
                stats["mos_Perlu Verifikasi"],
                stats["mos_Tidak Ada"],
                stats["mcf_Lulus"],
                stats["mcf_Tidak Lulus"],
                stats["mcf_Perlu Verifikasi"],
                stats["mcf_Tidak Ada"],
                stats["overall_Lulus"],
                stats["overall_Tidak Lulus"],
                stats["overall_Perlu Verifikasi"],
                stats["overall_Menunggu Hasil"],
                stats["overall_Tidak Ada"],
            ]
        )

    ws = wb.create_sheet("Rekap Prodi")
    write_table(ws, rekap_headers, rekap_rows, widths=[30] + [14] * 20, wrap_cols=(1,))

    # --- Sheet 9: Dashboard ---
    ws = wb.active
    ws.title = "Dashboard"
    ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:F1")
    ws["A1"] = "HASIL VALIDASI WISUDA - PRATINJAU"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A2:F2")
    ws["A2"] = (
        "Perbandingan data_wisuda.xlsx dengan data_sitasi.xlsx dan data_certiport.xlsx"
        f" - dibuat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    ws["A2"].font = SUBTITLE_FONT

    overall_counter = Counter(status_label(result.get("validation_status")) for result in results)
    metrics = [
        ("Total mahasiswa (data_wisuda)", len(results)),
        ("SITASI - NIM ditemukan", sum(1 for r in results if r.get("nim_normalized") and sitasi_by_nim.get(r.get("nim_normalized")))),
        ("SITASI - NIM & nama cocok", sum(1 for r in results if r.get("name_match") == "EXACT")),
        ("SITASI - NIM cocok, nama beda/sebagian", sum(1 for r in results if r.get("name_match") in ("DIFFERENT", "PARTIAL"))),
        ("SITASI - tidak ditemukan", sum(1 for r in results if not (r.get("nim_normalized") and sitasi_by_nim.get(r.get("nim_normalized"))))),
        ("Certiport - nama cocok (unik)", sum(1 for r in results if (r.get("certiport_match") or {}).get("status") == "MATCHED")),
        ("Certiport - ambigu / beberapa kandidat", sum(1 for r in results if (r.get("certiport_match") or {}).get("status") == PERLU_VERIFIKASI)),
        ("Certiport - hanya kandidat nama mirip", sum(1 for r in results if (r.get("certiport_match") or {}).get("status") == "FUZZY_ONLY")),
        ("Certiport - tidak ditemukan", sum(1 for r in results if (r.get("certiport_match") or {}).get("status") == DATA_TIDAK_DITEMUKAN)),
    ]
    for label in ("Lulus", "Tidak Lulus", "Perlu Verifikasi", "Menunggu Hasil", "Tidak Ada"):
        metrics.append((f"Hasil Validasi - {label}", overall_counter.get(label, 0)))

    ws["A4"] = "RINGKASAN ANGKA"
    ws["A4"].font = Font(bold=True, size=11, color="1F4E78")
    ws["A5"] = "Metrik"
    ws["B5"] = "Jumlah"
    for cell in (ws["A5"], ws["B5"]):
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER
        cell.border = BORDER
    row_index = 6
    for label, value in metrics:
        ws.cell(row=row_index, column=1, value=label).border = BORDER
        value_cell = ws.cell(row=row_index, column=2, value=value)
        value_cell.border = BORDER
        value_cell.alignment = Alignment(horizontal="center")
        color = status_fill(label.replace("Hasil Validasi - ", ""))
        if label.startswith("Hasil Validasi") and color:
            value_cell.fill = PatternFill("solid", fgColor=color)
        row_index += 1

    row_index += 2
    ws.cell(row=row_index, column=1, value="KETERANGAN LABEL HASIL").font = Font(bold=True, size=11, color="1F4E78")
    legend = [
        ("Lulus", "Ada bukti kelulusan pada sertifikasi yang relevan (VALID)."),
        ("Tidak Lulus", "Bukti menunjukkan tidak lulus (TIDAK_LULUS)."),
        ("Perlu Verifikasi", "Data ada tetapi ambigu/konflik; wajib review petugas (PERLU_VERIFIKASI)."),
        ("Menunggu Hasil", "SITASI masih PENDING; belum ada bukti selesai."),
        ("Tidak Ada", "Tidak ada data yang dapat dihubungkan pada NIM maupun nama."),
    ]
    row_index += 1
    for label, description in legend:
        label_cell = ws.cell(row=row_index, column=1, value=label)
        label_cell.border = BORDER
        label_cell.font = Font(bold=True)
        ws.merge_cells(start_row=row_index, start_column=2, end_row=row_index, end_column=6)
        description_cell = ws.cell(row=row_index, column=2, value=description)
        description_cell.border = BORDER
        description_cell.alignment = WRAP_TOP
        color = status_fill(label)
        if color:
            label_cell.fill = PatternFill("solid", fgColor=color)
        row_index += 1

    row_index += 2
    ws.cell(row=row_index, column=1, value="CATATAN PENTING").font = Font(bold=True, size=11, color="C00000")
    notes = [
        "Pratinjau ini bukan hasil final. Mapping kolom Sertifikasi MOS/MCF/Title Microsoft belum disahkan (ADR-003, ADR-006, ADR-010, ADR-011).",
        "SITASI dicocokkan dengan exact NIM; nama hanya pembanding. Certiport dicocokkan dengan nama; kandidat ambigu tidak otomatis Lulus.",
        "Kandidat nama mirip disediakan untuk review manusia, bukan untuk mengubah status secara otomatis.",
        "Status inti sistem tetap 5 nilai (VALID/PERLU_VERIFIKASI/TIDAK_LULUS/PENDING/DATA_TIDAK_DITEMUKAN); label di atas hanya tampilan.",
    ]
    row_index += 1
    for note in notes:
        ws.cell(row=row_index, column=1, value="- " + note)
        ws.merge_cells(start_row=row_index, start_column=1, end_row=row_index, end_column=6)
        ws.cell(row=row_index, column=1).alignment = WRAP_TOP
        row_index += 1
    ws.column_dimensions["A"].width = 48
    for column in ("B", "C", "D", "E", "F"):
        ws.column_dimensions[column].width = 24

    # --- Sheet 10: Catatan & Metodologi ---
    ws = wb.create_sheet("Catatan & Metodologi")
    ws.sheet_view.showGridLines = False
    ws["A1"] = "CATATAN & METODOLOGI"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:B1")
    notes_rows = [
        ("Sumber data", "data_wisuda.xlsx (sheet Wisuda); data_sitasi.xlsx (sheet Master_Data); data_certiport.xlsx (sheet Results (264) Plus)."),
        ("Jumlah baris", f"Wisuda: {len(wisuda_rows)}; SITASI: {len(sitasi_rows)}; Certiport: {len(certiport_rows)}."),
        ("Mesin pencocokan", "Meng memakai validate_wisuda_complete dari app/services/matching_service.py, sama dengan backend."),
        ("Pencocokan SITASI", "Exact NIM sebagai string; nama dinormalisasi sebagai pembanding. NIM ditemukan tetapi nama berbeda tetap ditampilkan sebagai perlu review."),
        ("Pencocokan Certiport", "Exact/fuzzy nama dengan RapidFuzz. Kandidat nama ganda atau hanya mirip tidak pernah otomatis Lulus."),
        ("Status MCF", "MCF hanya dihitung untuk kode prodi 31 (S1 Teknik Informatika) dan 32 (S1 Sistem Informasi). Prodi lain ditandai tidak relevan."),
        ("Label hasil", "Lulus/Tidak Lulus/Tidak Ada/PPerlu Verifikasi/Menunggu Hasil. Pemetaan: VALID=Lulus, TIDAK_LULUS=Tidak Lulus, DATA_TIDAK_DITEMUKAN=Tidak Ada, PERLU_VERIFIKASI=Perlu Verifikasi, PENDING=Menunggu Hasil."),
        ("Jejak audit", "Kode alasan (R01-R14) dan Catatan Review tetap tersedia sehingga status teknis dapat ditelusuri kembali."),
        ("Pratinjau", "Sheet Pratinjau Kolom Wisuda memakai format Opsi 1A dan Opsi 4A ADR-003 dan seluruh sel target berlabel [DRAFT]."),
        ("Data asli", "Berkas dapat memuat data pribadi. Jangan di-commit, dibagikan bebas, atau dijadikan acuan resmi tanpa persetujuan ITCC."),
    ]
    row_index = 3
    for label, value in notes_rows:
        ws.cell(row=row_index, column=1, value=label).font = Font(bold=True)
        ws.cell(row=row_index, column=1).alignment = WRAP_TOP
        ws.cell(row=row_index, column=2, value=value).alignment = WRAP_TOP
        ws.cell(row=row_index, column=1).border = BORDER
        ws.cell(row=row_index, column=2).border = BORDER
        row_index += 1
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 120

    return wb


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Buat workbook pratinjau validasi Wisuda.")
    parser.add_argument("--wisuda", type=Path, default=REPO_ROOT / "data_wisuda.xlsx")
    parser.add_argument("--sitasi", type=Path, default=REPO_ROOT / "data_sitasi.xlsx")
    parser.add_argument("--certiport", type=Path, default=REPO_ROOT / "data_certiport.xlsx")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "hasil_validasi_wisuda.xlsx")
    args = parser.parse_args()

    for path in (args.wisuda, args.sitasi, args.certiport):
        if not path.exists():
            print(f"File sumber tidak ditemukan: {path}", file=sys.stderr)
            return 1

    print("Membaca file sumber...")
    wisuda_rows, sitasi_rows, certiport_rows = load_sources(args.wisuda, args.sitasi, args.certiport)

    print("Menjalankan validasi...")
    results = validate_wisuda_complete(
        wisuda_rows,
        sitasi_rows,
        certiport_rows,
        sitasi_import_id=f"FILE:{args.sitasi.name}",
        certiport_import_id=f"FILE:{args.certiport.name}",
    )

    print("Menyusun workbook...")
    wb = build_workbook(results, wisuda_rows, sitasi_rows, certiport_rows)

    # Self-check: hasil harus utuh sebelum berkas ditulis.
    assert len(results) == len(wisuda_rows), "Jumlah hasil validasi harus sama dengan jumlah baris wisuda."
    ringkasan = wb["Ringkasan Validasi"]
    assert ringkasan.max_row - 1 == len(wisuda_rows), "Sheet Ringkasan Validasi kehilangan baris."
    for col in (17, 19, 21):
        for row_index in range(2, ringkasan.max_row + 1):
            value = ringkasan.cell(row=row_index, column=col).value
            assert value in ALLOWED_LABELS, f"Label hasil tidak dikenal: {value!r}"
    assert "Pratinjau Kolom Wisuda" in wb.sheetnames, "Sheet Pratinjau Kolom Wisuda tidak terbentuk."

    wb.save(args.output)
    wb.close()
    print(f"Selesai: {args.output.resolve()}")
    print("Hasil validasi: " + ", ".join(f"{label}={count}" for label, count in sorted(Counter(status_label(r.get('validation_status')) for r in results).items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
