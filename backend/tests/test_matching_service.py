from __future__ import annotations

from app.services.matching_service import (
    DATA_TIDAK_DITEMUKAN,
    PENDING,
    PERLU_VERIFIKASI,
    TIDAK_LULUS,
    VALID,
    build_sitasi_index,
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
    """Builder untuk record SITASI yang tersimpan di database."""
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
    """Builder untuk baris wisuda dari workbook Excel."""
    return {"source_row": source_row, "nim": nim, "nama": nama}


# ---------------------------------------------------------------------------
# Test: Single NIM dengan banyak attempt
# ---------------------------------------------------------------------------

def test_single_nim_many_attempts_groups_by_exam_and_preserves_all():
    """Satu NIM dengan banyak attempt di beberapa ujian — semua attempt tetap terlacak."""
    sitasi = [
        sitasi_row(id=1, source_row=2, nim="209900001", nama="MAHASISWA CONTOH",
                   sertifikasi="MOS", sub_program="Word", nilai=700, status="LULUS"),
        sitasi_row(id=2, source_row=3, nim="209900001", nama="MAHASISWA CONTOH",
                   sertifikasi="MOS", sub_program="Word", nilai=400, status="Gagal"),
        sitasi_row(id=3, source_row=4, nim="209900001", nama="MAHASISWA CONTOH",
                   sertifikasi="MOS", sub_program="Excel", nilai=800, status="LULUS"),
        sitasi_row(id=4, source_row=5, nim="209900001", nama="MAHASISWA CONTOH",
                   sertifikasi="MCF", sub_program="AI-900", nilai=850, status="LULUS"),
        sitasi_row(id=5, source_row=6, nim="209900001", nama="MAHASISWA CONTOH",
                   sertifikasi="MOS", sub_program="Word", nilai=350, status="Gagal"),
    ]
    wisuda = [wisuda_row(nim="209900001", nama="MAHASISWA CONTOH")]

    results = match_wisuda_to_sitasi(wisuda, sitasi, import_id="batch-test")
    result = results[0]

    assert result["overall_status"] == PERLU_VERIFIKASI
    assert len(result["exams"]) == 3

    word_exam = next(e for e in result["exams"] if e["sertifikasi"] == "MOS" and e["sub_program"] == "Word")
    assert len(word_exam["attempts"]) == 3
    assert word_exam["has_lulus"] is True
    assert word_exam["lulus_evidence"]["id"] == 1
    assert word_exam["lulus_evidence"]["source_row"] == 2
    assert word_exam["lulus_evidence"]["status"] == "LULUS"

    excel_exam = next(e for e in result["exams"] if e["sub_program"] == "Excel")
    assert len(excel_exam["attempts"]) == 1
    assert excel_exam["has_lulus"] is True

    mcf_exam = next(e for e in result["exams"] if e["sertifikasi"] == "MCF")
    assert mcf_exam["sub_program"] == "AI-900"
    assert mcf_exam["has_lulus"] is True

    assert result["evidence"]["matched_rows"] == 5
    assert result["evidence"]["source"] == "SITASI"
    assert result["evidence"]["import_id"] == "batch-test"


# ---------------------------------------------------------------------------
# Test: LULUS tidak tertimpa oleh attempt gagal pada ujian yang sama
# ---------------------------------------------------------------------------

def test_lulus_not_overwritten_by_fail_on_same_exam():
    """Jika ada attempt LULUS dan Gagal pada ujian yang sama, bukti LULUS tetap ada."""
    sitasi = [
        sitasi_row(id=10, source_row=2, status="Gagal", nilai=300),
        sitasi_row(id=11, source_row=3, status="Lulus", nilai=700),
        sitasi_row(id=12, source_row=4, status="Gagal", nilai=200),
    ]
    wisuda = [wisuda_row()]

    results = match_wisuda_to_sitasi(wisuda, sitasi)
    result = results[0]

    exam = result["exams"][0]
    assert len(exam["attempts"]) == 3
    assert exam["has_lulus"] is True
    assert exam["lulus_evidence"]["id"] == 11
    assert exam["lulus_evidence"]["nilai"] == 700
    assert exam["exam_status"] == PERLU_VERIFIKASI


# ---------------------------------------------------------------------------
# Test: Semua attempt gagal
# ---------------------------------------------------------------------------

def test_all_failed_yields_tidak_lulus():
    """Semua attempt gagal/tidak lulus → status TIDAK_LULUS."""
    sitasi = [
        sitasi_row(id=1, source_row=2, sertifikasi="MOS", sub_program="Word", status="Gagal", nilai=300),
        sitasi_row(id=2, source_row=3, sertifikasi="MOS", sub_program="Word", status="Tidak Lulus", nilai=350),
        sitasi_row(id=3, source_row=4, sertifikasi="MCF", sub_program="AI-900", status="Gagal", nilai=400),
    ]
    wisuda = [wisuda_row()]

    results = match_wisuda_to_sitasi(wisuda, sitasi)
    result = results[0]

    assert result["overall_status"] == TIDAK_LULUS
    for exam in result["exams"]:
        assert exam["exam_status"] == TIDAK_LULUS
        assert exam["has_lulus"] is False


# ---------------------------------------------------------------------------
# Test: Pending
# ---------------------------------------------------------------------------

def test_pending_status():
    """Ada attempt PENDING tanpa LULUS → status PENDING."""
    sitasi = [
        sitasi_row(id=1, source_row=2, status="Pending"),
        sitasi_row(id=2, source_row=3, status="Gagal", nilai=300),
    ]
    wisuda = [wisuda_row()]

    results = match_wisuda_to_sitasi(wisuda, sitasi)
    result = results[0]

    assert result["overall_status"] == PENDING
    exam = result["exams"][0]
    assert exam["has_pending"] is True
    assert exam["exam_status"] == PENDING


def test_pending_does_not_override_lulus():
    """LULUS tetap prioritas — meski ada PENDING di attempt lain, LULUS tetap disimpan."""
    sitasi = [
        sitasi_row(id=1, source_row=2, status="Pending"),
        sitasi_row(id=2, source_row=3, status="Lulus", nilai=700),
    ]
    wisuda = [wisuda_row()]

    results = match_wisuda_to_sitasi(wisuda, sitasi)
    result = results[0]

    exam = result["exams"][0]
    assert exam["has_lulus"] is True
    assert exam["lulus_evidence"]["id"] == 2
    # LULUS → PERLU_VERIFIKASI (butuh Certiport)
    assert exam["exam_status"] == PERLU_VERIFIKASI


# ---------------------------------------------------------------------------
# Test: NIM tidak ditemukan
# ---------------------------------------------------------------------------

def test_nim_not_found_returns_data_tidak_ditemukan():
    """NIM wisuda tidak ada di batch SITASI aktif → DATA_TIDAK_DITEMUKAN."""
    sitasi = [
        sitasi_row(id=1, source_row=2, nim="111111111", nama="ORANG LAIN"),
    ]
    wisuda = [wisuda_row(nim="999999999", nama="MAHASISWA CONTOH")]

    results = match_wisuda_to_sitasi(wisuda, sitasi)
    result = results[0]

    assert result["overall_status"] == DATA_TIDAK_DITEMUKAN
    assert len(result["exams"]) == 0
    assert result["evidence"]["matched_rows"] == 0
    assert "tidak ditemukan" in result["reason"].lower()


def test_empty_sitasi_batch_all_nim_not_found():
    """Batch SITASI kosong → semua wisuda DATA_TIDAK_DITEMUKAN."""
    wisuda = [
        wisuda_row(nim="209900001", nama="MAHASISWA CONTOH"),
        wisuda_row(nim="209900002", nama="MAHASISWA DUA"),
    ]

    results = match_wisuda_to_sitasi(wisuda, [])

    assert all(r["overall_status"] == DATA_TIDAK_DITEMUKAN for r in results)
    assert len(results) == 2


# ---------------------------------------------------------------------------
# Test: Nama berbeda
# ---------------------------------------------------------------------------

def test_different_name_flagged_not_rejected():
    """NIM sama tapi nama berbeda — name_match=DIFFERENT, tapi matching tetap berdasarkan NIM."""
    sitasi = [
        sitasi_row(id=1, source_row=2, nim="209900001", nama="MAHASISWA CONTOH", status="Lulus"),
    ]
    sitasi[0]["nama_normalized"] = normalize_name("MAHASISWA CONTOH")
    wisuda = [wisuda_row(nim="209900001", nama="MAHASISWA LAIN YANG BEDA")]

    results = match_wisuda_to_sitasi(wisuda, sitasi)
    result = results[0]

    assert result["name_match"] == "DIFFERENT"
    # NIM match tetap berhasil — nama hanya flag
    assert result["overall_status"] == PERLU_VERIFIKASI
    assert result["evidence"]["matched_rows"] == 1


def test_exact_name_match():
    """Nama sama setelah normalisasi → name_match=EXACT."""
    sitasi = [
        sitasi_row(id=1, source_row=2, nim="209900001", nama="MAHASISWA CONTOH", status="Lulus"),
    ]
    wisuda = [wisuda_row(nim="209900001", nama="mahasiswa contoh")]  # huruf kecil

    results = match_wisuda_to_sitasi(wisuda, sitasi)
    result = results[0]

    assert result["name_match"] == "EXACT"


def test_name_with_punctuation_normalized():
    """Nama dengan titik/spasi ekstra → tetap dianggap EXACT setelah normalisasi."""
    sitasi = [
        sitasi_row(id=1, source_row=2, nim="209900001", nama="A. MUH. FADEL OMAR", status="Lulus"),
    ]
    wisuda = [wisuda_row(nim="209900001", nama="A. MUH. FADEL OMAR")]

    results = match_wisuda_to_sitasi(wisuda, sitasi)
    result = results[0]

    assert result["name_match"] == "EXACT"


# ---------------------------------------------------------------------------
# Test: Sertifikasi campuran (MOS + MCF + MTCNA)
# ---------------------------------------------------------------------------

def test_mixed_certifications_grouped_separately():
    """SITASI dengan sertifikasi campuran — setiap ujian dikelompokkan terpisah."""
    sitasi = [
        sitasi_row(id=1, source_row=2, sertifikasi="MOS", sub_program="Word", status="Lulus"),
        sitasi_row(id=2, source_row=3, sertifikasi="MOS", sub_program="Excel", status="Gagal", nilai=400),
        sitasi_row(id=3, source_row=4, sertifikasi="MCF", sub_program="Azure AI-900", status="Lulus", nilai=850),
        sitasi_row(id=4, source_row=5, sertifikasi="MTCNA", sub_program="MTCNA", status="Pending"),
    ]
    wisuda = [wisuda_row()]

    results = match_wisuda_to_sitasi(wisuda, sitasi)
    result = results[0]

    assert len(result["exams"]) == 4
    assert result["evidence"]["matched_rows"] == 4

    exam_keys = {(e["sertifikasi"], e["sub_program"]) for e in result["exams"]}
    assert exam_keys == {("MOS", "Word"), ("MOS", "Excel"), ("MCF", "Azure AI-900"), ("MTCNA", "MTCNA")}


# ---------------------------------------------------------------------------
# Test: NIM kosong / tidak valid
# ---------------------------------------------------------------------------

def test_empty_nim_not_rejected_by_match():
    """Baris wisuda dengan NIM kosong — tidak crash, status DATA_TIDAK_DITEMUKAN."""
    wisuda = [wisuda_row(nim=None, nama="MAHASISWA CONTOH")]
    results = match_wisuda_to_sitasi(wisuda, [])

    result = results[0]
    assert result["name_match"] == "NO_NIM"
    assert result["overall_status"] == DATA_TIDAK_DITEMUKAN


# ---------------------------------------------------------------------------
# Test: Normalisasi NIM (float/string)
# ---------------------------------------------------------------------------

def test_nim_normalized_before_join():
    """NIM yang disimpan sebagai float/string tetap match setelah normalisasi."""
    sitasi = [
        sitasi_row(id=1, source_row=2, nim="209900001", status="Lulus"),
    ]
    # Wisuda NIM sebagai float (misal dibaca Excel sebagai 209900001.0)
    wisuda = [wisuda_row(nim=209900001.0, nama="MAHASISWA CONTOH")
              if isinstance(209900001.0, object) else wisuda_row(nim="209900001")]

    results = match_wisuda_to_sitasi(wisuda, sitasi)
    result = results[0]

    assert result["nim_normalized"] == "209900001"
    assert result["overall_status"] != DATA_TIDAK_DITEMUKAN


def test_nim_string_with_dot_zero():
    """NIM string '209900001.0' tetap match dengan '209900001'."""
    sitasi = [
        sitasi_row(id=1, source_row=2, nim="209900001", status="Lulus"),
    ]
    wisuda = [wisuda_row(nim="209900001.0", nama="MAHASISWA CONTOH")]

    results = match_wisuda_to_sitasi(wisuda, sitasi)
    result = results[0]

    assert result["nim_normalized"] == "209900001"
    assert result["overall_status"] == PERLU_VERIFIKASI


# ---------------------------------------------------------------------------
# Test: build_sitasi_index
# ---------------------------------------------------------------------------

def test_build_sitasi_index_groups_by_nim():
    """Indeks NIM -> daftar record bekerja dengan benar."""
    sitasi = [
        sitasi_row(id=1, source_row=2, nim="209900001"),
        sitasi_row(id=2, source_row=3, nim="209900001"),
        sitasi_row(id=3, source_row=4, nim="209900002"),
    ]
    index = build_sitasi_index(sitasi)

    assert len(index["209900001"]) == 2
    assert len(index["209900002"]) == 1
    assert {r["id"] for r in index["209900001"]} == {1, 2}


# ---------------------------------------------------------------------------
# Test: Multiple wisda rows processed independently
# ---------------------------------------------------------------------------

def test_multiple_wisda_rows_processed_independently():
    """Beberapa baris wisuda diproses secara independen."""
    sitasi = [
        sitasi_row(id=1, source_row=2, nim="209900001", status="Lulus"),
        sitasi_row(id=2, source_row=3, nim="209900002", status="Gagal"),
    ]
    wisda = [
        wisuda_row(source_row=2, nim="209900001", nama="MAHASISWA CONTOH"),
        wisuda_row(source_row=3, nim="209900002", nama="MAHASISWA DUA"),
        wisuda_row(source_row=4, nim="999999999", nama="MAHASISWA TIGA"),
    ]

    results = match_wisuda_to_sitasi(wisda, sitasi)

    assert len(results) == 3
    assert results[0]["overall_status"] == PERLU_VERIFIKASI
    assert results[1]["overall_status"] == TIDAK_LULUS
    assert results[2]["overall_status"] == DATA_TIDAK_DITEMUKAN


# ---------------------------------------------------------------------------
# Test: Evidence contains source, id, source_row, reason
# ---------------------------------------------------------------------------

def test_evidence_contains_source_id_row_and_reason():
    """Hasil internal menyimpan evidence sumber, id, baris, dan alasan."""
    sitasi = [
        sitasi_row(id=42, source_row=7, nim="209900001", status="Lulus", nilai=700),
        sitasi_row(id=43, source_row=8, nim="209900001", status="Gagal", nilai=300),
    ]
    wisda = [wisuda_row(source_row=2, nim="209900001", nama="MAHASISWA CONTOH")]

    results = match_wisuda_to_sitasi(wisda, sitasi, import_id="batch-001")
    result = results[0]

    assert result["evidence"]["source"] == "SITASI"
    assert result["evidence"]["import_id"] == "batch-001"
    assert result["evidence"]["matched_rows"] == 2

    exam = result["exams"][0]
    assert exam["lulus_evidence"]["source"] == "SITASI"
    assert exam["lulus_evidence"]["id"] == 42
    assert exam["lulus_evidence"]["source_row"] == 7
    assert exam["lulus_evidence"]["nilai"] == 700

    for attempt in exam["attempts"]:
        assert "source" in attempt
        assert "id" in attempt
        assert "source_row" in attempt

    assert result["reason"]


# ---------------------------------------------------------------------------
# Test: Tidak menyimpulkan persyaratan lulus wisda
# ---------------------------------------------------------------------------

def test_does_not_conclude_graduation_requirements():
    """LULUS SITASI saja tidak otomatis VALID — butuh Certiport."""
    sitasi = [
        sitasi_row(id=1, source_row=2, status="Lulus"),
        sitasi_row(id=2, source_row=3, sertifikasi="MCF", sub_program="AI-900", status="Lulus"),
    ]
    wisda = [wisuda_row()]

    results = match_wisuda_to_sitasi(wisda, sitasi)
    result = results[0]

    assert result["overall_status"] != VALID
    assert result["overall_status"] == PERLU_VERIFIKASI


def test_unknown_status_marked_perlu_verifikasi():
    """Status SITASI tidak dikenal → PERLU_VERIFIKASI, tidak crash."""
    sitasi = [
        sitasi_row(id=1, source_row=2, status="Aneh"),
    ]
    wisda = [wisuda_row()]

    results = match_wisuda_to_sitasi(wisda, sitasi)
    result = results[0]

    assert result["overall_status"] == PERLU_VERIFIKASI
    exam = result["exams"][0]
    assert exam["exam_status"] == PERLU_VERIFIKASI
    assert exam["has_lulus"] is False
    assert exam["has_pending"] is False
    assert exam["has_fail"] is False


# ---------------------------------------------------------------------------
# Test: Mixed LULUS dan FAIL pada ujian berbeda
# ---------------------------------------------------------------------------

def test_mixed_lulus_and_fail_across_different_exams():
    """Exam A LULUS, Exam B GAGAL — keduanya tetap terlacak dengan status masing-masing."""
    sitasi = [
        sitasi_row(id=1, source_row=2, sertifikasi="MOS", sub_program="Word", status="Lulus"),
        sitasi_row(id=2, source_row=3, sertifikasi="MOS", sub_program="Excel", status="Gagal", nilai=300),
    ]
    wisda = [wisuda_row()]

    results = match_wisuda_to_sitasi(wisda, sitasi)
    result = results[0]

    assert len(result["exams"]) == 2
    word_exam = next(e for e in result["exams"] if e["sub_program"] == "Word")
    excel_exam = next(e for e in result["exams"] if e["sub_program"] == "Excel")

    assert word_exam["exam_status"] == PERLU_VERIFIKASI
    assert word_exam["has_lulus"] is True
    assert excel_exam["exam_status"] == TIDAK_LULUS
    assert excel_exam["has_lulus"] is False
    # Overall → PERLU_VERIFIKASI karena ada ujian perlu verifikasi
    assert result["overall_status"] == PERLU_VERIFIKASI


def test_all_exams_pending_yields_pending_overall():
    """Semua ujian PENDING → overall PENDING."""
    sitasi = [
        sitasi_row(id=1, source_row=2, sertifikasi="MOS", sub_program="Word", status="Pending"),
        sitasi_row(id=2, source_row=3, sertifikasi="MCF", sub_program="AI-900", status="Pending"),
    ]
    wisda = [wisuda_row()]

    results = match_wisuda_to_sitasi(wisda, sitasi)
    result = results[0]

    assert result["overall_status"] == PENDING
    assert all(e["exam_status"] == PENDING for e in result["exams"])
