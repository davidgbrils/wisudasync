from __future__ import annotations

from app.services.matching_service import (
    DATA_TIDAK_DITEMUKAN,
    PENDING,
    PERLU_VERIFIKASI,
    TIDAK_LULUS,
    VALID,
    validate_wisuda_complete,
)
from app.services.normalization_service import normalize_name


def sitasi_row(
    *,
    id: int = 1,
    source_row: int = 2,
    nim: str = "209900001",
    nama: str = "MAHASISWA CONTOH",
    sertifikasi: str = "MOS",
    sub_program: str = "Word",
    nilai: int | float | None = 700,
    status: str = "LULUS",
) -> dict:
    return {
        "id": id,
        "source_row": source_row,
        "nim": nim,
        "nama": nama,
        "nama_normalized": normalize_name(nama),
        "sertifikasi": sertifikasi,
        "sub_program": sub_program,
        "nilai": nilai,
        "status": status,
    }


def wisuda_row(
    *,
    source_row: int = 2,
    nim: str = "209900001",
    nama: str = "MAHASISWA CONTOH",
    kode_prodi: str | None = None,
) -> dict:
    row = {"source_row": source_row, "nim": nim, "nama": nama}
    if kode_prodi is not None:
        row["kode_prodi"] = kode_prodi
    return row


def certiport_row(
    *,
    id: int = 100,
    source_row: int = 2,
    full_name: str = "MAHASISWA CONTOH",
    program_name: str = "Microsoft Office Specialist",
    certification_name: str = "Word",
    score: int | None = 700,
    result: str = "Pass",
) -> dict:
    return {
        "id": id,
        "source_row": source_row,
        "full_name": full_name,
        "full_name_normalized": normalize_name(full_name),
        "program_name": program_name,
        "certification_name": certification_name,
        "score": score,
        "result": result,
    }


def _validate(wisuda, sitasi, certiport):
    return validate_wisuda_complete(
        wisuda, sitasi, certiport,
        sitasi_import_id="sit-batch",
        certiport_import_id="cert-batch",
    )


# ===================================================================
# §6 Matriks validasi — 9 baris tabel keputusan
# ===================================================================

# Baris 1: SITASI LULUS + Certiport PASS => VALID
def test_dt_row1_sitasi_lulus_certiport_pass():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(status="LULUS")],
        [certiport_row(result="Pass")],
    )[0]
    assert r["validation_status"] == VALID
    assert r["mos_status"] == VALID
    assert r["needs_review"] is False
    assert "R01_VALID" in r["reason_codes"]


# Baris 2: SITASI LULUS (NIM+nama cocok) TANPA Certiport => VALID (SITASI cukup)
def test_dt_row2_sitasi_lulus_no_certiport_candidate():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(status="LULUS")],
        [],
    )[0]
    assert r["validation_status"] == VALID
    assert r["mos_status"] == VALID
    assert r["needs_review"] is False
    assert "R01_VALID" in r["reason_codes"]


# Baris 3: SITASI FAIL + Certiport FAIL => TIDAK_LULUS
def test_dt_row3_both_fail():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(status="TIDAK LULUS")],
        [certiport_row(result="Fail")],
    )[0]
    assert r["validation_status"] == TIDAK_LULUS
    assert r["mos_status"] == TIDAK_LULUS
    assert "R06_BOTH_FAIL" in r["reason_codes"]


# Baris 4: SITASI no LULUS + Certiport PASS => PERLU_VERIFIKASI (konflik)
def test_dt_row4_no_sitasi_lulus_certiport_pass():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(status="TIDAK LULUS")],
        [certiport_row(result="Pass")],
    )[0]
    assert r["validation_status"] == PERLU_VERIFIKASI
    assert "R05_SITASI_NO_LULUS_CERT_PASS" in r["reason_codes"]


# Baris 5: SITASI PENDING + no Certiport PASS => PENDING
def test_dt_row5_sitasi_pending():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(status="PENDING")],
        [certiport_row(result="Fail")],
    )[0]
    assert r["validation_status"] == PENDING
    assert r["mos_status"] == PENDING
    assert "R07_PENDING" in r["reason_codes"]


# Baris 6: Kandidat nama ganda => PERLU_VERIFIKASI
def test_dt_row6_multiple_name_candidates():
    r = _validate(
        [wisuda_row(nama="ANDI BUDIMAN")],
        [sitasi_row(nim="209900001", nama="ANDI BUDIMAN", status="LULUS")],
        [
            certiport_row(id=100, full_name="ANDI BUDIMAN", result="Pass"),
            certiport_row(id=101, full_name="ANDI BUDIMAN S", result="Pass"),
        ],
    )[0]
    assert r["validation_status"] == PERLU_VERIFIKASI
    assert r["needs_review"] is True
    assert any("nama ganda" in f.lower() or "Certiport" in f for f in r["review_flags"])


# Baris 7: SITASI MOS Word LULUS; Certiport beda ujian (Excel PASS) => SITASI cukup, VALID
def test_dt_row7_exam_mismatch():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(sertifikasi="MOS", sub_program="Word", status="LULUS")],
        [certiport_row(
            full_name="MAHASISWA CONTOH",
            program_name="Microsoft Office Specialist",
            certification_name="Excel",
            result="Pass",
        )],
    )[0]
    assert r["validation_status"] == VALID
    assert r["mos_status"] == VALID


# Baris 8: Tidak ada di SITASI dan tidak ada di Certiport => DATA_TIDAK_DITEMUKAN
def test_dt_row8_no_sitasi_nim():
    r = _validate(
        [wisuda_row(nim="999999999", nama="ORANG TIDAK ADA")],
        [sitasi_row(nim="209900001", nama="ORANG LAIN")],
        [certiport_row(full_name="ORANG LAIN")],
    )[0]
    assert r["validation_status"] == DATA_TIDAK_DITEMUKAN
    assert r["mos_status"] == DATA_TIDAK_DITEMUKAN
    assert r["mcf_status"] == DATA_TIDAK_DITEMUKAN
    assert "R11_NO_SITASI" in r["reason_codes"]
    assert r["needs_review"] is True


def test_dt_no_sitasi_but_found_in_certiport():
    r = _validate(
        [wisuda_row(nim="999999999", nama="MAHASISWA CERTIPORT")],
        [sitasi_row(nim="209900001", nama="ORANG LAIN")],
        [certiport_row(full_name="MAHASISWA CERTIPORT", certification_name="Word", result="Pass")],
    )[0]
    assert r["validation_status"] == VALID
    assert r["mos_status"] == VALID
    assert "R14_CERTIPORT_ONLY" in r["reason_codes"]
    assert r["needs_review"] is True
    assert any("Certiport" in flag for flag in r["review_flags"])


# Baris 9: SITASI LULUS, Certiport INCO/kosong => SITASI cukup, VALID
def test_dt_row9_certiport_inco():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(status="LULUS")],
        [certiport_row(result="INCO")],
    )[0]
    assert r["validation_status"] == VALID
    assert r["needs_review"] is False


# ===================================================================
# Per-program summary: MOS dan MCF terpisah
# ===================================================================

def test_mos_valid_mcf_ignored_when_prodi_not_relevant():
    r = _validate(
        [wisuda_row()],
        [
            sitasi_row(id=1, sertifikasi="MOS", sub_program="Word", status="LULUS"),
            sitasi_row(id=2, sertifikasi="MCF", sub_program="Azure AI-900", status="LULUS"),
        ],
        [certiport_row(
            id=100,
            full_name="MAHASISWA CONTOH",
            program_name="Microsoft Office Specialist",
            certification_name="Word",
            result="Pass",
        )],
    )[0]
    # Prodi default (209900001 -> kode "90") tidak relevan MCF → mcf_status None.
    assert r["mos_status"] == VALID
    assert r["mcf_status"] is None
    assert r["validation_status"] == VALID
    assert r["program_summary"]["MOS"]["status"] == VALID


def test_mos_and_mcf_both_valid():
    r = _validate(
        [wisuda_row(nim="202331001")],
        [
            sitasi_row(id=1, nim="202331001", sertifikasi="MOS", sub_program="Word", status="LULUS"),
            sitasi_row(id=2, nim="202331001", sertifikasi="MCF", sub_program="Azure AI-900", status="LULUS"),
        ],
        [
            certiport_row(id=100, full_name="MAHASISWA CONTOH",
                          program_name="Microsoft Office Specialist",
                          certification_name="Word", result="Pass"),
            certiport_row(id=101, full_name="MAHASISWA CONTOH",
                          program_name="Microsoft Certified Fundamentals",
                          certification_name="Azure AI-900", result="Pass"),
        ],
    )[0]
    assert r["mos_status"] == VALID
    assert r["mcf_status"] == VALID
    assert r["validation_status"] == VALID
    assert r["needs_review"] is False


# ===================================================================
# Program summary exam_details structure
# ===================================================================

def test_program_summary_has_exam_details():
    r = _validate(
        [wisuda_row()],
        [
            sitasi_row(id=1, sertifikasi="MOS", sub_program="Word", status="LULUS"),
            sitasi_row(id=2, sertifikasi="MOS", sub_program="Excel", status="LULUS"),
        ],
        [
            certiport_row(id=100, full_name="MAHASISWA CONTOH",
                          program_name="Microsoft Office Specialist",
                          certification_name="Word", result="Pass"),
            certiport_row(id=101, full_name="MAHASISWA CONTOH",
                          program_name="Microsoft Office Specialist",
                          certification_name="Excel", result="Pass"),
        ],
    )[0]
    mos = r["program_summary"]["MOS"]
    assert mos["exam_count"] == 2
    assert len(mos["exam_details"]) == 2
    subs = {d["sub_program"] for d in mos["exam_details"]}
    assert "Word" in subs
    assert "Excel" in subs
    for d in mos["exam_details"]:
        assert d["combined_status"] == VALID
        assert d["reason_code"] == "R01_VALID"


# ===================================================================
# Review flags
# ===================================================================

def test_name_mismatch_flags_review():
    r = _validate(
        [wisuda_row(nama="NAMA BERBEDA")],
        [sitasi_row(nim="209900001", nama="MAHASISWA CONTOH", status="LULUS")],
        [certiport_row(full_name="MAHASISWA CONTOH", result="Pass")],
    )[0]
    assert r["needs_review"] is True
    assert any("nama" in f.lower() or "name_match" in f.lower() for f in r["review_flags"])


def test_fuzzy_only_flags_review():
    # Tidak cocok di SITASI (NIM tidak ada), Certiport hanya mirip → review + saran nama.
    r = _validate(
        [wisuda_row(nim="999999999", nama="MAHASISWA CONTOH")],
        [sitasi_row(nim="209900001", nama="ORANG LAIN", status="LULUS")],
        [certiport_row(full_name="MAHASISWA CONTOHH", result="Pass")],
    )[0]
    assert r["needs_review"] is True
    assert any("fuzzy" in f.lower() or "mirip" in f.lower() for f in r["review_flags"])


def test_name_mismatch_same_nim_without_certiport_perlu_verifikasi():
    r = _validate(
        [wisuda_row(nama="NAMA BEDA")],
        [sitasi_row(nim="209900001", nama="NAMA ASLI", status="LULUS")],
        [],
    )[0]
    # NIM ada tapi nama beda → bukan "cocok SITASI", dan tidak ada di Certiport.
    assert r["validation_status"] == PERLU_VERIFIKASI
    assert r["needs_review"] is True


def test_name_mismatch_same_nim_uses_certiport_when_name_matches():
    r = _validate(
        [wisuda_row(nama="NAMA BEDA")],
        [sitasi_row(nim="209900001", nama="NAMA ASLI", status="LULUS")],
        [certiport_row(full_name="NAMA BEDA", certification_name="Word", result="Pass")],
    )[0]
    # Nama cocok di Certiport → status dari Certiport; tetap ditandai karena nama SITASI beda.
    assert r["validation_status"] == VALID
    assert r["needs_review"] is True


def test_similar_name_suggestions_in_review_flags():
    r = _validate(
        [wisuda_row(nim="999999999", nama="BUDI SANTOSO")],
        [sitasi_row(nim="209900001", nama="ORANG LAIN", status="LULUS")],
        [certiport_row(full_name="SANTOSO BUDI", certification_name="Word", result="Pass")],
    )[0]
    assert r["validation_status"] == PERLU_VERIFIKASI
    assert any("mirip" in f.lower() for f in r["review_flags"])
    assert any("SANTOSO BUDI" in f for f in r["review_flags"])


# ===================================================================
# APPROVED alias (ADR-005) produces VALID in validation engine
# ===================================================================

def test_approved_alias_produces_valid_in_validation_engine():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(sertifikasi="MOS", sub_program="Word", status="LULUS")],
        [certiport_row(
            full_name="MAHASISWA CONTOH",
            program_name="Microsoft Office Specialist",
            certification_name="Word 2019",
            result="Pass",
        )],
    )[0]
    assert r["mos_status"] == VALID
    assert r["validation_status"] == VALID
    assert "R01_VALID" in r["reason_codes"]
    assert r["needs_review"] is False


def test_placeholder_tidak_diketahui_pending_does_not_override_passed_exam():
    # Kasus seperti HENDRAWAN: Pendaftaran awal "Tidak Diketahui" (PENDING)
    # tidak boleh menimpa ujian kelulusan riil "Word" (LULUS / skor 792)
    r = _validate(
        [wisuda_row(nim="201911094", nama="HENDRAWAN")],
        [
            sitasi_row(id=1, nim="201911094", nama="HENDRAWAN", sertifikasi="MOS", sub_program="Tidak Diketahui", status="PENDING", nilai=None),
            sitasi_row(id=2, nim="201911094", nama="HENDRAWAN", sertifikasi="MOS", sub_program="Word", status="LULUS", nilai=792),
        ],
        [certiport_row(
            full_name="HENDRAWAN",
            program_name="Microsoft Office Specialist",
            certification_name="Word 2019",
            score=792,
            result="Pass",
        )],
    )[0]
    assert r["mos_status"] == VALID
    assert r["validation_status"] == VALID
    assert r["needs_review"] is False
    assert "R01_VALID" in r["reason_codes"]
    assert r["mos_score"] == 792


# ===================================================================
# SITASI LULUS + Certiport FAIL (konflik) => PERLU_VERIFIKASI
# ===================================================================

def test_sitasi_lulus_certiport_fail_reason_code():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(status="LULUS")],
        [certiport_row(result="Fail")],
    )[0]
    assert r["validation_status"] == PERLU_VERIFIKASI
    assert "R04_CERTIPORT_NO_PASS" in r["reason_codes"]


# ===================================================================
# Cross-program: MOS Word SITASI + MCF Certiport => mismatch
# ===================================================================

def test_cross_program_certiport_not_matching_mos():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(sertifikasi="MOS", sub_program="Word", status="LULUS")],
        [certiport_row(
            full_name="MAHASISWA CONTOH",
            program_name="Microsoft Certified Fundamentals",
            certification_name="Microsoft Azure AI Fundamentals",
            result="Pass",
        )],
    )[0]
    # SITASI MOS Word LULUS (NIM+nama cocok) → cukup; MCF certiport tidak relevan prodi "90".
    assert r["mos_status"] == VALID
    assert r["validation_status"] == VALID


# ===================================================================
# Multiple mahasiswa in single batch
# ===================================================================

def test_multiple_wisuda_rows():
    wisuda = [
        wisuda_row(source_row=2, nim="209900001", nama="MAHASISWA CONTOH"),
        wisuda_row(source_row=3, nim="209900002", nama="ORANG LAIN SEKALI"),
        wisuda_row(source_row=4, nim="999999999", nama="TIDAK ADA"),
    ]
    sitasi = [
        sitasi_row(id=1, nim="209900001", nama="MAHASISWA CONTOH", sertifikasi="MOS", sub_program="Word", status="LULUS"),
        sitasi_row(id=2, nim="209900002", nama="ORANG LAIN SEKALI", sertifikasi="MOS", sub_program="Excel", status="TIDAK LULUS"),
    ]
    certiport = [
        certiport_row(id=100, full_name="MAHASISWA CONTOH",
                      program_name="Microsoft Office Specialist",
                      certification_name="Word", result="Pass"),
        certiport_row(id=101, full_name="ORANG LAIN SEKALI",
                      program_name="Microsoft Office Specialist",
                      certification_name="Excel", result="Fail"),
    ]
    results = _validate(wisuda, sitasi, certiport)
    assert len(results) == 3
    assert results[0]["validation_status"] == VALID
    assert results[1]["validation_status"] == TIDAK_LULUS
    assert results[2]["validation_status"] == DATA_TIDAK_DITEMUKAN


# ===================================================================
# MTCNA (non-MOS/MCF) program — has its own summary
# ===================================================================

def test_mtcna_separate_program():
    r = _validate(
        [wisuda_row()],
        [
            sitasi_row(id=1, sertifikasi="MOS", sub_program="Word", status="LULUS"),
            sitasi_row(id=2, sertifikasi="MTCNA", sub_program="Mikrotik", status="LULUS"),
        ],
        [certiport_row(
            full_name="MAHASISWA CONTOH",
            program_name="Microsoft Office Specialist",
            certification_name="Word",
            result="Pass",
        )],
    )[0]
    assert r["mos_status"] == VALID
    assert "MTCNA" in r["program_summary"]
    assert r["program_summary"]["MTCNA"]["status"] == VALID
    assert r["validation_status"] == VALID


# ===================================================================
# Empty inputs
# ===================================================================

def test_empty_wisuda_returns_empty():
    assert _validate([], [], []) == []


def test_empty_sitasi_all_not_found():
    results = _validate([wisuda_row()], [], [])
    assert results[0]["validation_status"] == DATA_TIDAK_DITEMUKAN


# ===================================================================
# Evidence completeness
# ===================================================================

def test_evidence_preserved_in_program_summary():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(id=42, source_row=5, status="LULUS")],
        [certiport_row(id=555, source_row=10, result="Pass", score=800)],
    )[0]
    mos_details = r["program_summary"]["MOS"]["exam_details"]
    assert len(mos_details) == 1
    assert mos_details[0]["has_lulus"] is True
    assert mos_details[0]["certiport_evidence"][0]["id"] == 555


def test_sitasi_partial_certiport_has_extra_exams():
    wisuda = [wisuda_row(nim="209900001", nama="MAHASISWA MULTI")]
    sitasi = [sitasi_row(nim="209900001", nama="MAHASISWA MULTI", sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [
        certiport_row(id=101, full_name="MAHASISWA MULTI", program_name="Microsoft Office Specialist", certification_name="Word", result="Pass"),
        certiport_row(id=102, full_name="MAHASISWA MULTI", program_name="Microsoft Office Specialist", certification_name="Excel", result="Pass"),
    ]
    r = _validate(wisuda, sitasi, certiport)[0]
    # Word valid (SITASI cukup), Excel dari Certiport nama cocok → VALID
    assert r["validation_status"] == VALID
    assert r["mos_status"] == VALID
    assert len(r["exams"]) == 2
    word_exam = next(e for e in r["exams"] if e["sub_program"] == "Word")
    excel_exam = next(e for e in r["exams"] if e["sub_program"] == "Excel")
    assert word_exam["certiport_validation"]["combined_status"] == VALID
    assert excel_exam["certiport_validation"]["combined_status"] == VALID
    assert excel_exam.get("certiport_only") is True
    assert excel_exam["certiport_validation"]["certiport_evidence"][0]["id"] == 102


def test_certiport_mcf_direct_read_when_sitasi_only_mos():
    wisuda = [wisuda_row(nim="202331002", nama="MAHASISWA AZURE")]
    sitasi = [sitasi_row(nim="202331002", nama="MAHASISWA AZURE", sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [
        certiport_row(id=101, full_name="MAHASISWA AZURE", program_name="Microsoft Office Specialist", certification_name="Word", result="Pass"),
        certiport_row(id=102, full_name="MAHASISWA AZURE", program_name="Microsoft Certified Fundamentals", certification_name="Microsoft Azure Fundamentals", result="Pass"),
    ]
    r = _validate(wisuda, sitasi, certiport)[0]
    assert r["mos_status"] == VALID
    assert r["mcf_status"] == VALID
    assert "MCF" in r["program_summary"]
    mcf_details = r["program_summary"]["MCF"]["exam_details"]
    assert len(mcf_details) == 1
    assert mcf_details[0]["certiport_only"] is True


def test_multi_attempt_picks_passing_attempt_with_highest_score():
    wisuda = [wisuda_row(nim="209900001", nama="MAHASISWA MULTI ATTEMPT")]
    sitasi = [
        sitasi_row(id=1, nim="209900001", nama="MAHASISWA MULTI ATTEMPT", sertifikasi="MOS", sub_program="Word", nilai=650, status="TIDAK LULUS"),
        sitasi_row(id=2, nim="209900001", nama="MAHASISWA MULTI ATTEMPT", sertifikasi="MOS", sub_program="Word", nilai=750, status="LULUS"),
        sitasi_row(id=3, nim="209900001", nama="MAHASISWA MULTI ATTEMPT", sertifikasi="MOS", sub_program="Word", nilai=850, status="LULUS"),
    ]
    certiport = [
        certiport_row(id=201, full_name="MAHASISWA MULTI ATTEMPT", program_name="Microsoft Office Specialist", certification_name="Word", score=850, result="Pass"),
    ]
    r = _validate(wisuda, sitasi, certiport)[0]
    assert r["mos_status"] == VALID
    assert r["mos_score"] == 850
    assert r["program_summary"]["MOS"]["score"] == 850
    assert r["program_summary"]["MOS"]["scores"]["Word"] == 850
    word_exam = r["exams"][0]
    assert word_exam["has_lulus"] is True
    assert word_exam["selected_attempt"]["id"] == 3
    assert word_exam["selected_attempt"]["nilai"] == 850


def test_single_attempt_not_passing_preserves_score():
    wisuda = [wisuda_row(nim="209900002", nama="MAHASISWA SATU ATTEMPT GAGAL")]
    sitasi = [
        sitasi_row(id=10, nim="209900002", nama="MAHASISWA SATU ATTEMPT GAGAL", sertifikasi="MOS", sub_program="Word", nilai=620, status="TIDAK LULUS"),
    ]
    certiport = []
    r = _validate(wisuda, sitasi, certiport)[0]
    assert r["mos_status"] == TIDAK_LULUS
    assert r["mos_score"] == 620
    assert r["program_summary"]["MOS"]["score"] == 620
    assert r["program_summary"]["MOS"]["scores"]["Word"] == 620
    word_exam = r["exams"][0]
    assert word_exam["has_lulus"] is False
    assert word_exam["score"] == 620


def test_all_attempts_failed_picks_highest_score():
    wisuda = [wisuda_row(nim="209900003", nama="MAHASISWA SEMUA GAGAL")]
    sitasi = [
        sitasi_row(id=21, nim="209900003", nama="MAHASISWA SEMUA GAGAL", sertifikasi="MOS", sub_program="Word", nilai=500, status="TIDAK LULUS"),
        sitasi_row(id=22, nim="209900003", nama="MAHASISWA SEMUA GAGAL", sertifikasi="MOS", sub_program="Word", nilai=640, status="TIDAK LULUS"),
    ]
    certiport = []
    r = _validate(wisuda, sitasi, certiport)[0]
    assert r["mos_status"] == TIDAK_LULUS
    assert r["mos_score"] == 640
    assert r["program_summary"]["MOS"]["score"] == 640
    assert r["program_summary"]["MOS"]["scores"]["Word"] == 640


def test_detail_contains_sitasi_and_certiport_names_and_scores():
    wisuda = [wisuda_row(nim="209900004", nama="BUDI SANTOSO")]
    sitasi = [
        sitasi_row(
            id=31,
            nim="209900004",
            nama="BUDI SANTOSO SITASI",
            sertifikasi="MOS",
            sub_program="Word",
            nilai=825,
            status="LULUS",
        ),
    ]
    certiport = [
        certiport_row(
            id=301,
            full_name="BUDI SANTOSO",
            program_name="Microsoft Office Specialist",
            certification_name="Word",
            score=890,
            result="Pass",
        ),
    ]
    r = _validate(wisuda, sitasi, certiport)[0]
    mos_summary = r["program_summary"]["MOS"]
    assert mos_summary["sitasi_name"] == "BUDI SANTOSO SITASI"
    assert mos_summary["certiport_name"] == "BUDI SANTOSO"

    details = mos_summary["exam_details"]
    assert len(details) == 1
    d = details[0]
    assert d["sitasi_name"] == "BUDI SANTOSO SITASI"
    assert d["sitasi_score"] == 825
    assert d["sitasi_status"] == "LULUS"
    assert d["certiport_name"] == "BUDI SANTOSO"
    assert d["certiport_score"] == 890
    assert d["certiport_status"] == "PASS"


