from __future__ import annotations

from app.services.matching_service import (
    DATA_TIDAK_DITEMUKAN,
    EXAM_ALIAS_DRAFT,
    EXAM_ALIAS_STATUS,
    PENDING,
    PERLU_VERIFIKASI,
    TIDAK_LULUS,
    VALID,
    _cross_validate_exam,
    _find_certiport_candidates_fuzzy,
    _is_exam_alias_match,
    build_certiport_name_index,
    match_sitasi_to_certiport,
    match_wisuda_to_sitasi,
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
    certification_name: str = "Word 2019",
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


def _run_pipeline(wisuda, sitasi, certiport):
    ws = match_wisuda_to_sitasi(wisuda, sitasi, import_id="sit-batch")
    return match_sitasi_to_certiport(ws, certiport, certiport_import_id="cert-batch")


# ---------------------------------------------------------------------------
# Alias matching
# ---------------------------------------------------------------------------

def test_alias_exact_match():
    ok, reason = _is_exam_alias_match("Word", "Word")
    assert ok
    assert reason == "exact_match"


def test_alias_draft_forward():
    ok, reason = _is_exam_alias_match("Word", "Word 2019")
    assert ok
    assert "draft" in reason.lower()


def test_alias_draft_reverse():
    ok, reason = _is_exam_alias_match("Word", "Microsoft Word 2019")
    assert ok
    assert "draft" in reason.lower()


def test_alias_no_match_different_exam():
    ok, _ = _is_exam_alias_match("Word", "Excel 2019")
    assert not ok


def test_alias_azure():
    ok, reason = _is_exam_alias_match("Azure AI-900", "Microsoft Azure AI Fundamentals")
    assert ok
    assert "draft" in reason.lower()


# ---------------------------------------------------------------------------
# Certiport name index
# ---------------------------------------------------------------------------

def test_build_certiport_name_index():
    rows = [
        certiport_row(id=1, full_name="MAHASISWA CONTOH"),
        certiport_row(id=2, full_name="MAHASISWA CONTOH"),
        certiport_row(id=3, full_name="ORANG LAIN"),
    ]
    index = build_certiport_name_index(rows)
    assert len(index) == 2
    key = normalize_name("MAHASISWA CONTOH")
    assert len(index[key]) == 2


# ---------------------------------------------------------------------------
# Fuzzy candidates
# ---------------------------------------------------------------------------

def test_fuzzy_exact_name_returns_candidate():
    index = build_certiport_name_index([certiport_row(full_name="MAHASISWA CONTOH")])
    candidates = _find_certiport_candidates_fuzzy(normalize_name("MAHASISWA CONTOH"), index)
    assert len(candidates) == 1
    assert candidates[0]["score"] == 100
    assert candidates[0]["reason"] == "exact_name"


def test_fuzzy_below_threshold_no_candidate():
    index = build_certiport_name_index([certiport_row(full_name="NAMA SANGAT BERBEDA SEKALI")])
    candidates = _find_certiport_candidates_fuzzy(normalize_name("ANDI BUDIMAN"), index)
    assert len(candidates) == 0


# ---------------------------------------------------------------------------
# Full pipeline: happy path VALID
# ---------------------------------------------------------------------------

def test_valid_sitasi_lulus_certiport_pass_exact_alias():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [certiport_row(
        full_name="MAHASISWA CONTOH",
        program_name="Microsoft Office Specialist",
        certification_name="Word",
        result="Pass",
    )]
    results = _run_pipeline(wisuda, sitasi, certiport)
    r = results[0]
    exam = r["exams"][0]
    cv = exam["certiport_validation"]
    assert cv["combined_status"] == VALID
    assert cv["reason"] == "SITASI LULUS (NIM+nama cocok); status cukup tanpa Certiport PASS."


# ---------------------------------------------------------------------------
# DRAFT alias => PERLU_VERIFIKASI even when both pass
# ---------------------------------------------------------------------------

def test_draft_alias_forces_perlu_verifikasi():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [certiport_row(
        full_name="MAHASISWA CONTOH",
        program_name="Microsoft Office Specialist",
        certification_name="Word 2019",
        result="Pass",
    )]
    results = _run_pipeline(wisuda, sitasi, certiport)
    cv = results[0]["exams"][0]["certiport_validation"]
    assert cv["combined_status"] == PERLU_VERIFIKASI
    assert "DRAFT" in cv["reason"] or "draft" in cv["reason"].lower()


# ---------------------------------------------------------------------------
# Same name, multiple persons (ambiguity)
# ---------------------------------------------------------------------------

def test_same_name_multiple_unique_names_perlu_verifikasi():
    wisuda = [wisuda_row(nama="ANDI BUDIMAN")]
    sitasi = [sitasi_row(nim="209900001", nama="ANDI BUDIMAN", sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [
        certiport_row(id=100, full_name="ANDI BUDIMAN", result="Pass"),
        certiport_row(id=101, full_name="ANDI BUDIMAN S", result="Pass"),
    ]
    results = _run_pipeline(wisuda, sitasi, certiport)
    r = results[0]
    assert r["certiport_match"]["status"] == PERLU_VERIFIKASI
    assert "nama" in r["certiport_match"]["reason"].lower() or "salah orang" in r["certiport_match"]["reason"].lower()


# ---------------------------------------------------------------------------
# Same name, same person, multiple records — unique candidate OK
# ---------------------------------------------------------------------------

def test_same_name_multiple_records_conflicting_fail_perlu_verifikasi():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [
        certiport_row(id=100, full_name="MAHASISWA CONTOH",
                      certification_name="Word", result="Pass"),
        certiport_row(id=101, full_name="MAHASISWA CONTOH",
                      certification_name="Word", result="Fail"),
    ]
    results = _run_pipeline(wisuda, sitasi, certiport)
    cv = results[0]["exams"][0]["certiport_validation"]
    # SITASI LULUS tapi ada rekaman Certiport FAIL pada ujian sama → konflik.
    assert cv["combined_status"] == PERLU_VERIFIKASI


# ---------------------------------------------------------------------------
# Cross-program mismatch: MOS Word vs MCF exam
# ---------------------------------------------------------------------------

def test_cross_program_mismatch_perlu_verifikasi():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [certiport_row(
        full_name="MAHASISWA CONTOH",
        program_name="Microsoft Certified Fundamentals",
        certification_name="Microsoft Azure AI Fundamentals",
        result="Pass",
    )]
    results = _run_pipeline(wisuda, sitasi, certiport)
    cv = results[0]["exams"][0]["certiport_validation"]
    assert cv["certiport_status"] == DATA_TIDAK_DITEMUKAN
    # SITASI MOS Word LULUS (NIM+nama cocok) → cukup, tetap VALID.
    assert cv["combined_status"] == VALID


# ---------------------------------------------------------------------------
# SITASI LULUS + Certiport FAIL => PERLU_VERIFIKASI (conflict)
# ---------------------------------------------------------------------------

def test_sitasi_lulus_certiport_fail_conflict():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [certiport_row(
        full_name="MAHASISWA CONTOH",
        program_name="Microsoft Office Specialist",
        certification_name="Word",
        result="Fail",
    )]
    results = _run_pipeline(wisuda, sitasi, certiport)
    cv = results[0]["exams"][0]["certiport_validation"]
    assert cv["combined_status"] == PERLU_VERIFIKASI
    assert "konflik" in cv["reason"].lower() or "tidak ada PASS" in cv["reason"]


# ---------------------------------------------------------------------------
# SITASI not lulus + Certiport PASS => PERLU_VERIFIKASI (conflict)
# ---------------------------------------------------------------------------

def test_sitasi_gagal_certiport_pass_conflict():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(sertifikasi="MOS", sub_program="Word", status="TIDAK LULUS")]
    certiport = [certiport_row(
        full_name="MAHASISWA CONTOH",
        program_name="Microsoft Office Specialist",
        certification_name="Word",
        result="Pass",
    )]
    results = _run_pipeline(wisuda, sitasi, certiport)
    cv = results[0]["exams"][0]["certiport_validation"]
    assert cv["combined_status"] == PERLU_VERIFIKASI


# ---------------------------------------------------------------------------
# Both fail => TIDAK_LULUS
# ---------------------------------------------------------------------------

def test_both_fail_tidak_lulus():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(sertifikasi="MOS", sub_program="Word", status="TIDAK LULUS")]
    certiport = [certiport_row(
        full_name="MAHASISWA CONTOH",
        program_name="Microsoft Office Specialist",
        certification_name="Word",
        result="Fail",
    )]
    results = _run_pipeline(wisuda, sitasi, certiport)
    cv = results[0]["exams"][0]["certiport_validation"]
    assert cv["combined_status"] == TIDAK_LULUS


# ---------------------------------------------------------------------------
# No Certiport data at all
# ---------------------------------------------------------------------------

def test_no_certiport_data():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(sertifikasi="MOS", sub_program="Word", status="LULUS")]
    results = _run_pipeline(wisuda, sitasi, [])
    r = results[0]
    assert r["certiport_match"]["status"] == DATA_TIDAK_DITEMUKAN
    cv = r["exams"][0]["certiport_validation"]
    assert cv["combined_status"] == VALID


# ---------------------------------------------------------------------------
# DATA_TIDAK_DITEMUKAN wisuda (no SITASI match) => certiport skipped
# ---------------------------------------------------------------------------

def test_no_sitasi_match_but_certiport_read_directly():
    wisuda = [wisuda_row(nim="999999999", nama="TIDAK ADA DI SITASI")]
    sitasi = [sitasi_row(nim="209900001")]
    certiport = [certiport_row(full_name="TIDAK ADA DI SITASI", certification_name="Word", result="Pass")]
    results = _run_pipeline(wisuda, sitasi, certiport)
    r = results[0]
    assert r["certiport_match"]["status"] == "MATCHED"
    # Tidak ada di SITASI tapi ada di Certiport dengan nama cocok → pakai Certiport.
    assert r["overall_status"] == VALID
    assert len(r["exams"]) == 1
    assert r["exams"][0]["certiport_only"] is True


def test_no_sitasi_and_no_certiport_data_tidak_ditemukan():
    wisuda = [wisuda_row(nim="999999999", nama="ORANG TIDAK ADA")]
    sitasi = [sitasi_row(nim="209900001")]
    certiport = [certiport_row(full_name="ORANG LAIN")]
    results = _run_pipeline(wisuda, sitasi, certiport)
    r = results[0]
    assert r["certiport_match"]["status"] == DATA_TIDAK_DITEMUKAN
    assert r["overall_status"] == DATA_TIDAK_DITEMUKAN


# ---------------------------------------------------------------------------
# Fuzzy only (no exact name) => PERLU_VERIFIKASI
# ---------------------------------------------------------------------------

def test_fuzzy_only_no_exact_perlu_verifikasi():
    # Tidak cocok di SITASI (NIM tidak ada) → Certiport hanya mirip → PERLU_VERIFIKASI.
    wisuda = [wisuda_row(nim="999999999", nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(nim="209900001", nama="ORANG LAIN", sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [certiport_row(
        full_name="MAHASISWA CONTOHH",
        program_name="Microsoft Office Specialist",
        certification_name="Word",
        result="Pass",
    )]
    results = _run_pipeline(wisuda, sitasi, certiport)
    r = results[0]
    assert r["certiport_match"]["status"] == PERLU_VERIFIKASI
    assert "fuzzy" in r["certiport_match"]["reason"].lower()


def test_sitasi_matched_with_fuzzy_certiport_stays_valid():
    # SITASI cocok NIM+nama → cukup; kandidat Certiport hanya mirip tidak menurunkan status.
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(nim="209900001", nama="MAHASISWA CONTOH", sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [certiport_row(
        full_name="MAHASISWA CONTOHH",
        program_name="Microsoft Office Specialist",
        certification_name="Word",
        result="Pass",
    )]
    results = _run_pipeline(wisuda, sitasi, certiport)
    assert results[0]["overall_status"] == VALID


# ---------------------------------------------------------------------------
# Multiple exams: MOS Word VALID + MCF Azure PERLU_VERIFIKASI => overall PERLU_VERIFIKASI
# ---------------------------------------------------------------------------

def test_multiple_exams_mixed_status():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [
        sitasi_row(id=1, sertifikasi="MOS", sub_program="Word", status="LULUS"),
        sitasi_row(id=2, sertifikasi="MCF", sub_program="Azure AI-900", status="LULUS"),
    ]
    certiport = [
        certiport_row(id=100, full_name="MAHASISWA CONTOH",
                      program_name="Microsoft Office Specialist",
                      certification_name="Word", result="Pass"),
    ]
    results = _run_pipeline(wisuda, sitasi, certiport)
    r = results[0]
    mos_exam = next(e for e in r["exams"] if e["sertifikasi"] == "MOS")
    mcf_exam = next(e for e in r["exams"] if e["sertifikasi"] == "MCF")
    assert mos_exam["certiport_validation"]["combined_status"] == VALID
    # MCF Azure LULUS di SITASI (nama cocok) → cukup, VALID meski tanpa Certiport.
    assert mcf_exam["certiport_validation"]["combined_status"] == VALID
    assert r["overall_status"] == VALID


# ---------------------------------------------------------------------------
# All exams VALID => overall VALID
# ---------------------------------------------------------------------------

def test_all_exams_valid_overall_valid():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [
        sitasi_row(id=1, sertifikasi="MOS", sub_program="Word", status="LULUS"),
        sitasi_row(id=2, sertifikasi="MOS", sub_program="Excel", status="LULUS"),
    ]
    certiport = [
        certiport_row(id=100, full_name="MAHASISWA CONTOH",
                      program_name="Microsoft Office Specialist",
                      certification_name="Word", result="Pass"),
        certiport_row(id=101, full_name="MAHASISWA CONTOH",
                      program_name="Microsoft Office Specialist",
                      certification_name="Excel", result="Pass"),
    ]
    results = _run_pipeline(wisuda, sitasi, certiport)
    r = results[0]
    assert r["overall_status"] == VALID


# ---------------------------------------------------------------------------
# SITASI PENDING => combined PENDING
# ---------------------------------------------------------------------------

def test_sitasi_pending_combined_pending():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(sertifikasi="MOS", sub_program="Word", status="PENDING")]
    certiport = [certiport_row(
        full_name="MAHASISWA CONTOH",
        program_name="Microsoft Office Specialist",
        certification_name="Word",
        result="Fail",
    )]
    results = _run_pipeline(wisuda, sitasi, certiport)
    cv = results[0]["exams"][0]["certiport_validation"]
    assert cv["combined_status"] == PENDING


# ---------------------------------------------------------------------------
# Certiport INCO result => PERLU_VERIFIKASI
# ---------------------------------------------------------------------------

def test_certiport_inco_keeps_sitasi_valid():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [certiport_row(
        full_name="MAHASISWA CONTOH",
        program_name="Microsoft Office Specialist",
        certification_name="Word",
        result="INCO",
    )]
    results = _run_pipeline(wisuda, sitasi, certiport)
    cv = results[0]["exams"][0]["certiport_validation"]
    # SITASI LULUS (nama cocok) → cukup; Certiport INCO tidak menurunkan status.
    assert cv["combined_status"] == VALID


# ---------------------------------------------------------------------------
# Cross-validate evidence contains source detail
# ---------------------------------------------------------------------------

def test_evidence_contains_source_detail():
    wisuda = [wisuda_row(nama="MAHASISWA CONTOH")]
    sitasi = [sitasi_row(sertifikasi="MOS", sub_program="Word", status="LULUS")]
    certiport = [certiport_row(
        id=555,
        source_row=10,
        full_name="MAHASISWA CONTOH",
        program_name="Microsoft Office Specialist",
        certification_name="Word",
        score=800,
        result="Pass",
    )]
    results = _run_pipeline(wisuda, sitasi, certiport)
    cv = results[0]["exams"][0]["certiport_validation"]
    assert len(cv["certiport_evidence"]) == 1
    ev = cv["certiport_evidence"][0]
    assert ev["source"] == "CERTIPORT"
    assert ev["id"] == 555
    assert ev["source_row"] == 10
    assert ev["result"] == "PASS"
