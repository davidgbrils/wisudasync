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
) -> dict:
    return {"source_row": source_row, "nim": nim, "nama": nama}


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


# Baris 2: SITASI LULUS + Tidak ada kandidat Certiport unik => PERLU_VERIFIKASI
def test_dt_row2_sitasi_lulus_no_certiport_candidate():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(status="LULUS")],
        [],
    )[0]
    assert r["validation_status"] == PERLU_VERIFIKASI
    assert r["mos_status"] == PERLU_VERIFIKASI
    assert r["needs_review"] is True
    assert "R03_NO_CERTIPORT_CANDIDATE" in r["reason_codes"]


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


# Baris 7: Ujian berbeda (MOS Word vs Certiport Excel) => PERLU_VERIFIKASI
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
    assert r["validation_status"] == PERLU_VERIFIKASI
    assert r["mos_status"] == PERLU_VERIFIKASI


# Baris 8: Tidak ada NIM SITASI => DATA_TIDAK_DITEMUKAN
def test_dt_row8_no_sitasi_nim():
    r = _validate(
        [wisuda_row(nim="999999999")],
        [sitasi_row(nim="209900001")],
        [certiport_row()],
    )[0]
    assert r["validation_status"] == DATA_TIDAK_DITEMUKAN
    assert r["mos_status"] == DATA_TIDAK_DITEMUKAN
    assert r["mcf_status"] == DATA_TIDAK_DITEMUKAN
    assert "R11_NO_SITASI" in r["reason_codes"]
    assert r["needs_review"] is True


# Baris 9: Certiport INCO/kosong => PERLU_VERIFIKASI
def test_dt_row9_certiport_inco():
    r = _validate(
        [wisuda_row()],
        [sitasi_row(status="LULUS")],
        [certiport_row(result="INCO")],
    )[0]
    assert r["validation_status"] == PERLU_VERIFIKASI
    assert r["needs_review"] is True


# ===================================================================
# Per-program summary: MOS dan MCF terpisah
# ===================================================================

def test_mos_valid_mcf_perlu_verifikasi_separate():
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
    assert r["mos_status"] == VALID
    assert r["mcf_status"] == PERLU_VERIFIKASI
    assert r["validation_status"] == PERLU_VERIFIKASI
    assert r["program_summary"]["MOS"]["status"] == VALID
    assert r["program_summary"]["MCF"]["status"] == PERLU_VERIFIKASI


def test_mos_and_mcf_both_valid():
    r = _validate(
        [wisuda_row()],
        [
            sitasi_row(id=1, sertifikasi="MOS", sub_program="Word", status="LULUS"),
            sitasi_row(id=2, sertifikasi="MCF", sub_program="Azure AI-900", status="LULUS"),
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
    r = _validate(
        [wisuda_row(nama="MAHASISWA CONTOH")],
        [sitasi_row(nama="MAHASISWA CONTOH", status="LULUS")],
        [certiport_row(full_name="MAHASISWA CONTOHH", result="Pass")],
    )[0]
    assert r["needs_review"] is True
    assert any("fuzzy" in f.lower() for f in r["review_flags"])


# ===================================================================
# DRAFT alias prevents VALID even with matching results
# ===================================================================

def test_draft_alias_prevents_valid_in_validation_engine():
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
    assert r["mos_status"] == PERLU_VERIFIKASI
    assert r["validation_status"] == PERLU_VERIFIKASI
    assert "R02_DRAFT_ALIAS" in r["reason_codes"]
    assert r["needs_review"] is True


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
    assert r["mos_status"] == PERLU_VERIFIKASI
    assert r["validation_status"] == PERLU_VERIFIKASI


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
    assert r["program_summary"]["MTCNA"]["status"] == PERLU_VERIFIKASI
    assert r["validation_status"] == PERLU_VERIFIKASI


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
    detail = mos_details[0]
    assert detail["has_lulus"] is True
    cert_ev = detail["certiport_evidence"]
    assert len(cert_ev) == 1
    assert cert_ev[0]["id"] == 555
    assert cert_ev[0]["source_row"] == 10
