from __future__ import annotations

from collections import defaultdict
from typing import Any

from rapidfuzz import fuzz
from supabase import Client

from app.services.import_service import get_active_import_id
from app.services.normalization_service import (
    clean_text,
    normalize_code,
    normalize_name,
    normalize_upper,
)
from app.core.prodi import is_mcf_relevant, resolve_kode_prodi, resolve_program_studi

# Status hasil matching (sesuai AGENTS.md §4.5)
VALID = "VALID"
PERLU_VERIFIKASI = "PERLU_VERIFIKASI"
TIDAK_LULUS = "TIDAK_LULUS"
PENDING = "PENDING"
DATA_TIDAK_DITEMUKAN = "DATA_TIDAK_DITEMUKAN"

# Label bahasa manusia untuk tampilan laporan/ekspor pratinjau.
# Status inti tetap 5 nilai di atas; label ini hanya untuk presentation layer.
STATUS_LABELS: dict[str, str] = {
    VALID: "Lulus",
    TIDAK_LULUS: "Tidak Lulus",
    DATA_TIDAK_DITEMUKAN: "Tidak Ada",
    PERLU_VERIFIKASI: "Perlu Verifikasi",
    PENDING: "Menunggu Hasil",
}

# Label untuk status per programmatically yang belum dipetakan.
STATUS_LABEL_UNKNOWN = "-"


def status_label(status: Any) -> str:
    """Terjemahkan status matching ke label bahasa manusia.

    Status yang tidak dikenal (mis. None atau kode baru) tidak ditebak:
    dikembalikan sebagai "—" supaya tidak menyesatkan pembaca laporan.
    """
    if status is None:
        return STATUS_LABEL_UNKNOWN
    return STATUS_LABELS.get(str(status).strip().upper(), STATUS_LABEL_UNKNOWN)

# Nilai status SITASI (sudah uppercase saat impor, tapi normalisasi untuk robust)
LULUS_STATUSES = {"LULUS"}
FAIL_STATUSES = {"TIDAK LULUS", "GAGAL"}
PENDING_STATUSES = {"PENDING"}

# Source identifier untuk evidence
SITASI_SOURCE = "SITASI"
CERTIPORT_SOURCE = "CERTIPORT"

CERTIPORT_REQUIRED_FIELDS = (
    "id",
    "source_row",
    "full_name",
    "full_name_normalized",
    "program_name",
    "certification_name",
    "score",
    "result",
)

CERTIPORT_PASS = {"PASS"}
CERTIPORT_FAIL = {"FAIL"}

FUZZY_THRESHOLD = 85
FUZZY_STRONG_THRESHOLD = 95
FUZZY_TOP_N = 5

# Pencocokan nama Certiport: kandidat hanya dianggap plausibel bila nama lengkap
# berbagi minimal 2 kata (mis. "DAVID GABRIEL SEMBIRING" ~ "DAVID SEMBIRING").
# Kurang dari 2 kata cocok → bukan kandidat (DATA_TIDAK_DITEMUKAN).
NAME_MIN_MATCHING_WORDS = 2
# Toleransi typo ringan per kata saat menghitung kata yang cocok.
NAME_WORD_MATCH_THRESHOLD = 85

CATEGORY_MAP: dict[str, str] = {
    "MOS": "MICROSOFT OFFICE SPECIALIST",
    "MCF": "MICROSOFT CERTIFIED FUNDAMENTALS",
}
CATEGORY_MAP_REVERSE: dict[str, str] = {v: k for k, v in CATEGORY_MAP.items()}

EXAM_ALIAS_DRAFT: dict[str, set[str]] = {
    "WORD": {"WORD 2019", "MICROSOFT WORD 2019"},
    "EXCEL": {"EXCEL 2019", "MICROSOFT EXCEL 2019"},
    "POWERPOINT": {"POWERPOINT 2019", "MICROSOFT POWERPOINT 2019"},
    "AZURE AI-900": {"MICROSOFT AZURE AI FUNDAMENTALS"},
    "AZURE AZ-900": {"MICROSOFT AZURE FUNDAMENTALS"},
    "AZURE DP-900": {"MICROSOFT AZURE DATA FUNDAMENTALS"},
    "AZURE SC-900": {"MICROSOFT SECURITY COMPLIANCE AND IDENTITY FUNDAMENTALS"},
}
EXAM_ALIAS_STATUS = "APPROVED"

# Sub-program placeholder pendaftaran awal SITASI yang belum memiliki sub-ujian riil
PLACEHOLDER_SUB_PROGRAMS: set[str] = {
    "TIDAK DIKETAHUI",
    "UNKNOWN",
    "",
    "PENDAFTARAN",
    "BELUM UJIAN",
}

# Kolom yang dibutuhkan dari tabel sitasi_data
SITASI_REQUIRED_FIELDS = (
    "id",
    "source_row",
    "nim",
    "nama",
    "nama_normalized",
    "sertifikasi",
    "sub_program",
    "nilai",
    "status",
)


def fetch_active_sitasi_rows(
    supabase: Client,
    page_size: int = 1000,
) -> tuple[str | None, list[dict]]:
    """Ambil seluruh record dari batch SITASI aktif via pagination.

    Mengembalikan (import_id, list_of_rows). import_id None jika belum ada batch aktif.
    Bukan pure — hanya wrapper query database; matching logic ada di match_wisuda_to_sitasi.
    """
    import_id = get_active_import_id(supabase, "SITASI")
    if not import_id:
        return None, []

    rows: list[dict] = []
    offset = 0
    while True:
        response = (
            supabase.table("sitasi_data")
            .select(",".join(SITASI_REQUIRED_FIELDS))
            .eq("import_id", import_id)
            .order("source_row")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        batch = response.data or []
        rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size

    return import_id, rows


def build_sitasi_index(sitasi_rows: list[dict]) -> dict[str, list[dict]]:
    """Bangun indeks NIM (ter-normalisasi) -> daftar record SITASI dari batch aktif."""
    index: dict[str, list[dict]] = defaultdict(list)
    for row in sitasi_rows:
        nim = normalize_code(row.get("nim"))
        if nim:
            index[nim].append(row)
    return dict(index)


def _normalize_sitasi_status(status: Any) -> str | None:
    """Normalisasi status SITASI untuk agregasi attempt."""
    if status is None:
        return None
    text = str(status).strip().upper()
    if not text or text in {"NAN", "NONE", "NULL", "NAT"}:
        return None
    return text


def _get_nama_normalized(record: dict) -> str:
    """Dapatkan nama ter-normalisasi dari record SITASI.

    Selalu normalisasi ulang (idempoten) terhadap nilai tersimpan maupun kolom
    nama mentah. Ini menjaga nama satu kata yang ditulis berhias tanda baca,
    mis. "( DAVID.)" atau "DAVID.", tetap setara dengan "DAVID".
    """
    stored = record.get("nama_normalized")
    normalized = normalize_name(stored) if stored else None
    if normalized:
        return normalized
    return normalize_name(record.get("nama")) or ""


def _group_sitasi_by_exam(sitasi_rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """Kelompokkan record SITASI berdasarkan (sertifikasi, sub_program).

    Setiap kombinasi (sertifikasi, sub_program) merepresentasikan satu ujian.
    Misalnya: (MOS, Word), (MOS, Excel), (MCF, Azure AI-900).
    """
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in sitasi_rows:
        sertifikasi = normalize_upper(row.get("sertifikasi")) or ""
        sub_program = clean_text(row.get("sub_program")) or ""
        groups[(sertifikasi, sub_program)].append(row)
    return dict(groups)


def _build_attempt_evidence(attempt: dict) -> dict:
    """Bangun evidence sumber/id/baris untuk satu attempt SITASI."""
    return {
        "source": SITASI_SOURCE,
        "id": attempt.get("id"),
        "source_row": attempt.get("source_row"),
        "nim": normalize_code(attempt.get("nim")),
        "nama": attempt.get("nama"),
        "sertifikasi": normalize_upper(attempt.get("sertifikasi")),
        "sub_program": clean_text(attempt.get("sub_program")),
        "nilai": attempt.get("nilai"),
        "status": _normalize_sitasi_status(attempt.get("status")),
    }


def _parse_numeric_score(val: Any) -> float | int | None:
    """Parse nilai ujian ke bentuk numerik (int atau float) untuk evaluasi peringkat dan tampilan."""
    if val is None:
        return None
    try:
        s = str(val).strip().replace(",", ".")
        if not s or s.upper() in {"NAN", "NONE", "NULL", "NAT"}:
            return None
        f = float(s)
        return int(f) if f.is_integer() else f
    except (ValueError, TypeError):
        return None


def _aggregate_exam_attempts(attempts: list[dict]) -> dict:
    """Agregasi attempt untuk satu ujian (sertifikasi + sub_program).

    Aturan:
    - Jika mahasiswa memiliki beberapa percobaan dan ada yang LULUS, pilih percobaan yang
      LULUS dengan skor tertinggi (memprioritaskan status kelulusan).
    - Jika belum lulus (hanya 1 data atau semua percobaan gagal/pending), pilih percobaan
      dengan skor tertinggi yang ada agar petugas tetap dapat melihat capaian nilainya.
    - Semua attempt (LULUS, GAGAL, PENDING, dsb.) tetap dilacak di daftar 'attempts'.
    """
    has_lulus = False
    has_pending = False
    has_fail = False

    processed_attempts = [_build_attempt_evidence(a) for a in attempts]

    lulus_attempts: list[dict] = []
    pending_attempts: list[dict] = []
    fail_attempts: list[dict] = []

    for evidence in processed_attempts:
        status = evidence["status"]
        if status in LULUS_STATUSES:
            has_lulus = True
            lulus_attempts.append(evidence)
        elif status in PENDING_STATUSES:
            has_pending = True
            pending_attempts.append(evidence)
        elif status in FAIL_STATUSES:
            has_fail = True
            fail_attempts.append(evidence)

    if has_lulus:
        exam_status = PERLU_VERIFIKASI
    elif has_pending:
        exam_status = PENDING
    elif has_fail:
        exam_status = TIDAK_LULUS
    else:
        exam_status = PERLU_VERIFIKASI

    # Pemilihan selected_attempt dan best_score:
    selected_attempt: dict | None = None
    if lulus_attempts:
        # Dari setiap percobaan mahasiswa yang lulus, cari yang skornya tertinggi
        selected_attempt = max(
            lulus_attempts,
            key=lambda a: _parse_numeric_score(a.get("nilai")) if _parse_numeric_score(a.get("nilai")) is not None else -1.0,
        )
    elif processed_attempts:
        # Jika belum lulus (1 data atau multi-attempt gagal), ambil percobaan dengan skor tertinggi
        selected_attempt = max(
            processed_attempts,
            key=lambda a: _parse_numeric_score(a.get("nilai")) if _parse_numeric_score(a.get("nilai")) is not None else -1.0,
        )

    best_score = _parse_numeric_score(selected_attempt.get("nilai")) if selected_attempt else None

    result = {
        "has_lulus": has_lulus,
        "has_pending": has_pending,
        "has_fail": has_fail,
        "exam_status": exam_status,
        "score": best_score,
        "selected_attempt": selected_attempt,
        "attempts": processed_attempts,
    }
    if has_lulus and selected_attempt:
        result["lulus_evidence"] = selected_attempt

    return result


def _aggregate_overall_status(exam_results: list[dict]) -> str:
    """Tentukan status keseluruhan per baris wisuda dari hasil ujian.

    Prioritas: PERLU_VERIFIKASI (ada LULUS/unknown) > PENDING > TIDAK_LULUS.
    Jangan menyimpulkan syarat kelulusan wisuda — VALID membutuhkan Certiport.
    """
    if not exam_results:
        return DATA_TIDAK_DITEMUKAN

    statuses = [e["exam_status"] for e in exam_results]

    if PERLU_VERIFIKASI in statuses:
        return PERLU_VERIFIKASI
    if PENDING in statuses:
        return PENDING
    if all(s == TIDAK_LULUS for s in statuses):
        return TIDAK_LULUS
    return PERLU_VERIFIKASI


def match_wisuda_to_sitasi(
    wisuda_rows: list[dict],
    sitasi_rows: list[dict],
    import_id: str | None = None,
) -> list[dict]:
    """Match baris wisuda ke batch SITASI aktif memakai exact NIM.

    Fungsi murni — tidak mengakses database. Menerima list of dicts
    untuk wisuda dan SITASI, mengembalikan hasil per-baris beserta evidence.

    Args:
        wisuda_rows: List of dicts dengan minimal 'source_row', 'nim', 'nama'.
        sitasi_rows: List of dicts dari query batch SITASI aktif.
        import_id: ID batch SITASI aktif untuk evidence (opsional).

    Returns:
        List[dict] hasil matching per baris wisuda, setiap elemen berisi:
        - source_row, nim, nim_normalized, nama
        - name_match: "EXACT" / "PARTIAL" / "DIFFERENT" / "MISSING" / None
        - overall_status: VALID / PERLU_VERIFIKASI / TIDAK_LULUS / PENDING / DATA_TIDAK_DITEMUKAN
        - exams: daftar hasil per ujian (sertifikasi, sub_program)
        - evidence: {source, import_id, matched_rows}
        - reason: penjelasan status
    """
    index = build_sitasi_index(sitasi_rows)
    results: list[dict] = []

    for row in wisuda_rows:
        source_row = row.get("source_row")
        raw_nim = row.get("nim")
        raw_nama = row.get("nama")

        nim = normalize_code(raw_nim)
        wisuda_nama_norm = normalize_name(raw_nama) or ""

        kp = resolve_kode_prodi(nim, row.get("kode_prodi"))
        ps = resolve_program_studi(kp, row.get("program_studi"))

        result: dict[str, Any] = {
            "source_row": source_row,
            "nim": raw_nim if raw_nim is not None else None,
            "nim_normalized": nim,
            "nama": raw_nama,
            "kode_prodi": kp,
            "program_studi": ps,
            "name_match": None,
            "sitasi_matched": False,
            "overall_status": DATA_TIDAK_DITEMUKAN,
            "exams": [],
            "evidence": {
                "source": SITASI_SOURCE,
                "import_id": import_id,
                "matched_rows": 0,
            },
            "reason": "",
        }

        # Case: NIM tidak valid / kosong
        if not nim:
            result["name_match"] = "NO_NIM"
            result["reason"] = "NIM tidak valid pada baris wisuda."
            results.append(result)
            continue

        # Exact join NIM ke semua record SITASI
        sitasi_records = index.get(nim, [])

        if not sitasi_records:
            result["reason"] = f"NIM {nim} tidak ditemukan pada batch SITASI aktif."
            results.append(result)
            continue

        result["evidence"]["matched_rows"] = len(sitasi_records)

        # Cek kesamaan nama — flag, bukan kunci utama
        name_checks = []
        for rec in sitasi_records:
            rec_name = _get_nama_normalized(rec)
            if rec_name and wisuda_nama_norm and rec_name == wisuda_nama_norm:
                name_checks.append(True)
            else:
                name_checks.append(False)

        if not wisuda_nama_norm:
            result["name_match"] = "MISSING"
        elif name_checks and all(name_checks):
            result["name_match"] = "EXACT"
        elif any(name_checks):
            result["name_match"] = "PARTIAL"
        else:
            result["name_match"] = "DIFFERENT"

        # Ketentuan: cocok di SITASI hanya bila NIM DAN nama sama.
        result["sitasi_matched"] = result["name_match"] == "EXACT"

        # Kelompokkan attempt per ujian (sertifikasi + sub_program)
        exam_groups = _group_sitasi_by_exam(sitasi_records)
        exam_results = []

        for (sertifikasi, sub_program), attempts in exam_groups.items():
            agg = _aggregate_exam_attempts(attempts)
            exam_result = {
                "sertifikasi": sertifikasi,
                "sub_program": sub_program,
                "exam_status": agg["exam_status"],
                "has_lulus": agg["has_lulus"],
                "has_pending": agg["has_pending"],
                "has_fail": agg["has_fail"],
                "score": agg.get("score"),
                "selected_attempt": agg.get("selected_attempt"),
                "attempts": agg["attempts"],
                "lulus_evidence": agg.get("lulus_evidence"),
                "evidence": {
                    "source": SITASI_SOURCE,
                    "import_id": import_id,
                    "attempt_count": len(agg["attempts"]),
                },
            }
            exam_results.append(exam_result)

        result["exams"] = exam_results
        result["overall_status"] = _aggregate_overall_status(exam_results)
        result["reason"] = (
            f"NIM ditemukan pada batch SITASI aktif "
            f"({result['evidence']['matched_rows']} record, "
            f"{len(exam_results)} ujian); name_match={result['name_match']}."
        )
        results.append(result)

    return results


# ---------------------------------------------------------------------------
# Tahap 09: SITASI↔Certiport matching
# ---------------------------------------------------------------------------


def fetch_active_certiport_rows(
    supabase: Client,
    page_size: int = 1000,
) -> tuple[str | None, list[dict]]:
    """Ambil seluruh record dari batch Certiport aktif via pagination."""
    import_id = get_active_import_id(supabase, "CERTIPORT")
    if not import_id:
        return None, []

    rows: list[dict] = []
    offset = 0
    while True:
        response = (
            supabase.table("certiport_data")
            .select(",".join(CERTIPORT_REQUIRED_FIELDS))
            .eq("import_id", import_id)
            .order("source_row")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        batch = response.data or []
        rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size

    return import_id, rows


def build_certiport_name_index(
    certiport_rows: list[dict],
) -> dict[str, list[dict]]:
    """Indeks nama normalized -> daftar record Certiport.

    Selalu menormalkan ulang (idempoten) nilai tersimpan agar nama berhias
    tanda baca/kurung, mis. "( DAVID.)", tetap terindeks sebagai "DAVID".
    """
    index: dict[str, list[dict]] = defaultdict(list)
    for row in certiport_rows:
        raw = row.get("full_name_normalized") or row.get("full_name")
        name = normalize_name(raw)
        if name:
            index[name].append(row)
    return dict(index)


def _normalize_certiport_result(result: Any) -> str | None:
    if result is None:
        return None
    text = str(result).strip().upper()
    if not text or text in {"NAN", "NONE", "NULL", "NAT"}:
        return None
    return text


def _map_category(sitasi_sertifikasi: str) -> str | None:
    """Map SITASI sertifikasi ke Certiport program_name (uppercase)."""
    return CATEGORY_MAP.get(sitasi_sertifikasi)


def _map_category_reverse(certiport_program: str) -> str | None:
    """Map Certiport program_name ke SITASI sertifikasi (MOS/MCF)."""
    if not certiport_program:
        return None
    p = str(certiport_program).strip().upper()
    if "OFFICE SPECIALIST" in p or p == "MOS":
        return "MOS"
    if "FUNDAMENTALS" in p or p == "MCF":
        return "MCF"
    return CATEGORY_MAP_REVERSE.get(p)


def _canonical_exam_name(cert_name: str) -> str:
    """Ambil nama ujian kanonikal dari nama sertifikasi Certiport."""
    cleaned = clean_text(cert_name) or ""
    c_upper = cleaned.upper()
    for canonical, aliases in EXAM_ALIAS_DRAFT.items():
        if c_upper == canonical or c_upper in aliases:
            return canonical.title() if canonical in ("WORD", "EXCEL", "POWERPOINT") else canonical
    return cleaned


def _is_exam_alias_match(
    sitasi_sub: str, certiport_cert: str,
) -> tuple[bool, str]:
    """Cek apakah sub_program SITASI dan certification_name Certiport ekuivalen.

    Returns (match, reason). Alias DRAFT bukan auto-valid.
    """
    s = sitasi_sub.strip().upper()
    c = certiport_cert.strip().upper()

    if s == c:
        return True, "exact_match"

    status_label = EXAM_ALIAS_STATUS.lower()
    aliases = EXAM_ALIAS_DRAFT.get(s, set())
    if c in aliases:
        return True, f"alias_{status_label}:{EXAM_ALIAS_STATUS}"

    for key, val_set in EXAM_ALIAS_DRAFT.items():
        if s in val_set and c == key:
            return True, f"alias_{status_label}_reverse:{EXAM_ALIAS_STATUS}"
        if s in val_set and c in val_set:
            return True, f"alias_{status_label}_both:{EXAM_ALIAS_STATUS}"

    return False, "no_match"


def _fuzzy_name_score(target: str, candidate: str) -> int:
    """Skor kemiripan nama tahan typo & urutan suku kata (fuzzy per kata).

    Mengambil skor maksimum dari beberapa metrik: kemiripan menyeluruh,
    kecocokan bagian, dan perbandingan berbasis kata (token). Cocok untuk
    mendeteksi variasi urutan suku kata maupun salah ketik ringan.
    """
    return int(
        max(
            fuzz.ratio(target, candidate),
            fuzz.partial_ratio(target, candidate),
            fuzz.token_sort_ratio(target, candidate),
            fuzz.token_set_ratio(target, candidate),
        )
    )


def _name_word_tokens(name: str) -> list[str]:
    """Pecah nama menjadi token kata, tahan tanda baca/kurung.

    Menormalkan ulang (idempoten) sehingga "( DAVID.)" dan "david" sama-sama
    menghasilkan token ["DAVID"]. Nama satu kata tetap satu token.
    """
    if not name:
        return []
    normalized = normalize_name(name) or ""
    return [token for token in normalized.split() if token]


def _count_matching_name_words(
    target: str,
    candidate: str,
    word_threshold: int = NAME_WORD_MATCH_THRESHOLD,
) -> int:
    """Hitung banyak kata target yang punya padanan kata kandidat (toleran typo).

    Contoh: "DAVID GABRIEL SEMBIRING" vs "DAVID SEMBIRING" → 2 kata cocok
    (DAVID, SEMBIRING), meski urutan atau panjang nama berbeda.
    """
    target_words = _name_word_tokens(target)
    candidate_words = _name_word_tokens(candidate)
    if not target_words or not candidate_words:
        return 0
    matched = 0
    for target_word in target_words:
        if any(
            int(fuzz.ratio(target_word, candidate_word)) >= word_threshold
            for candidate_word in candidate_words
        ):
            matched += 1
    return matched


def _find_certiport_candidates_fuzzy(
    target_name: str,
    certiport_index: dict[str, list[dict]],
    threshold: int = FUZZY_THRESHOLD,
) -> list[dict]:
    """Cari kandidat Certiport berdasar nama normalized + skor fuzzy per kata.

    Kandidat hanya lolos bila nama berbagi minimal `NAME_MIN_MATCHING_WORDS` kata
    dengan nama lengkap target. Nama pendek (mis. satu kata) memakai batas
    min(jumlah kata target, 2) agar nama tunggal yang sah tetap bisa dicocokkan.
    Kurang dari batas kata → bukan kandidat (mengarah ke DATA_TIDAK_DITEMUKAN).

    Mengembalikan list of {name, score, reason, matched_words, records}
    diurutkan score descending. Nama identik (score 100) tetap kandidat, bukan auto-valid.
    """
    target_words = _name_word_tokens(target_name)
    if not target_words:
        return []

    required_words = min(NAME_MIN_MATCHING_WORDS, len(target_words))

    candidates: list[dict] = []
    for name, records in certiport_index.items():
        score = _fuzzy_name_score(target_name, name)
        if score < threshold:
            continue
        matched_words = _count_matching_name_words(target_name, name)
        if matched_words < required_words:
            continue
        reason = "exact_name" if name == target_name else "fuzzy_candidate"
        candidates.append({
            "name": name,
            "score": score,
            "reason": reason,
            "matched_words": matched_words,
            "records": records,
        })
    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates


def _sitasi_only_combined(exam: dict, sitasi_matched: bool) -> str:
    """Status ujian bila hanya ada bukti SITASI (tanpa Certiport).

    Cocok NIM+nama di SITASI → status SITASI sudah cukup (LULUS/TIDAK LULUS/PENDING).
    """
    if not sitasi_matched:
        return PERLU_VERIFIKASI
    if exam.get("has_lulus"):
        return VALID
    if exam.get("has_pending"):
        return PENDING
    if exam.get("exam_status") == TIDAK_LULUS or exam.get("has_fail"):
        return TIDAK_LULUS
    return PERLU_VERIFIKASI


def _cross_validate_exam(
    sitasi_exam: dict,
    certiport_records: list[dict],
    alias_status: str = EXAM_ALIAS_STATUS,
    sitasi_matched: bool = False,
) -> dict:
    """Validasi silang satu ujian SITASI terhadap record Certiport kandidat.

    Mengembalikan dict dengan certiport_status, combined_status, evidence, reason.
    Cocok NIM+nama di SITASI → status SITASI cukup; Certiport hanya bukti silang.
    """
    sitasi_sertifikasi = sitasi_exam.get("sertifikasi", "")
    sitasi_sub = sitasi_exam.get("sub_program", "")
    sitasi_status = sitasi_exam.get("exam_status", "")
    has_sitasi_lulus = sitasi_exam.get("has_lulus", False)

    expected_program = _map_category(sitasi_sertifikasi)

    matching_certiport: list[dict] = []
    exam_match_reasons: list[str] = []

    for rec in certiport_records:
        prog = normalize_upper(rec.get("program_name")) or ""
        cert_name = clean_text(rec.get("certification_name")) or ""

        if expected_program and prog != expected_program:
            continue

        alias_match, alias_reason = _is_exam_alias_match(sitasi_sub, cert_name)
        if not alias_match:
            continue

        matching_certiport.append(rec)
        exam_match_reasons.append(alias_reason)

    if not matching_certiport:
        return {
            "certiport_status": DATA_TIDAK_DITEMUKAN,
            "combined_status": _sitasi_only_combined(sitasi_exam, sitasi_matched),
            "certiport_evidence": [],
            "reason": "Tidak ditemukan record Certiport dengan program dan ujian yang sesuai.",
        }

    has_cert_pass = False
    has_cert_fail = False
    cert_evidence = []
    for i, rec in enumerate(matching_certiport):
        result = _normalize_certiport_result(rec.get("result"))
        is_pass = result in CERTIPORT_PASS
        is_fail = result in CERTIPORT_FAIL
        if is_pass:
            has_cert_pass = True
        if is_fail:
            has_cert_fail = True
        cert_evidence.append({
            "source": CERTIPORT_SOURCE,
            "id": rec.get("id"),
            "source_row": rec.get("source_row"),
            "full_name": rec.get("full_name"),
            "program_name": rec.get("program_name"),
            "certification_name": rec.get("certification_name"),
            "score": rec.get("score"),
            "result": result,
            "exam_alias_reason": exam_match_reasons[i] if i < len(exam_match_reasons) else None,
        })

    uses_draft_alias = any("draft" in r.lower() for r in exam_match_reasons if r)

    if sitasi_matched:
        if has_sitasi_lulus and has_cert_fail:
            combined = PERLU_VERIFIKASI
            reason = "SITASI LULUS tapi Certiport FAIL; konflik sumber."
        elif has_sitasi_lulus:
            if has_cert_pass and uses_draft_alias:
                combined = PERLU_VERIFIKASI
                reason = "SITASI LULUS + Certiport PASS, tapi alias ujian masih DRAFT (ADR-005)."
            else:
                combined = VALID
                reason = "SITASI LULUS (NIM+nama cocok); status cukup tanpa Certiport PASS."
        elif not has_sitasi_lulus and has_cert_pass:
            combined = PERLU_VERIFIKASI
            reason = "Certiport PASS tapi SITASI tidak ada LULUS; konflik sumber."
        elif sitasi_status == PENDING:
            combined = PENDING
            reason = "SITASI masih PENDING."
        elif has_cert_fail and sitasi_status == TIDAK_LULUS:
            combined = TIDAK_LULUS
            reason = "SITASI dan Certiport keduanya tidak lulus."
        else:
            combined = PERLU_VERIFIKASI
            reason = "Bukti belum cukup untuk kesimpulan."
    else:
        # NIM+nama tidak cocok di SITASI → Certiport jadi penentu (nama harus cocok).
        if has_cert_pass:
            combined = VALID
            reason = "Certiport PASS dan nama cocok; tidak cocok pada SITASI."
        elif has_cert_fail:
            combined = TIDAK_LULUS
            reason = "Certiport FAIL dan nama cocok; tidak cocok pada SITASI."
        else:
            combined = PERLU_VERIFIKASI
            reason = "Bukti Certiport belum cukup (INCO/kosong)."

    return {
        "certiport_status": "PASS" if has_cert_pass else ("FAIL" if has_cert_fail else PERLU_VERIFIKASI),
        "combined_status": combined,
        "certiport_evidence": cert_evidence,
        "reason": reason,
    }


def _build_certiport_only_exam(
    rec: dict,
    certiport_import_id: str | None = None,
    fuzzy: bool = False,
) -> dict:
    """Bangun entri ujian dari rekaman Certiport yang belum tercatat di data SITASI."""
    prog_raw = rec.get("program_name") or ""
    cat = _map_category_reverse(prog_raw) or ("MOS" if "OFFICE" in prog_raw.upper() or "MOS" in prog_raw.upper() else ("MCF" if "FUNDAMENTAL" in prog_raw.upper() or "MCF" in prog_raw.upper() else "OTHER"))
    cert_name = rec.get("certification_name") or ""
    sub_prog = _canonical_exam_name(cert_name)
    result_val = _normalize_certiport_result(rec.get("result"))
    is_pass = result_val in CERTIPORT_PASS
    is_fail = result_val in CERTIPORT_FAIL

    if fuzzy:
        reason = f"Kandidat fuzzy pada Certiport ({result_val}); belum ada rekaman attempt di data SITASI."
    elif is_pass:
        reason = "Sertifikasi tercatat di Certiport (PASS), namun belum ada rekaman attempt di data SITASI."
    elif is_fail:
        reason = "Ujian tercatat di Certiport (FAIL), tidak ada rekaman attempt di data SITASI."
    else:
        reason = f"Ujian tercatat di Certiport ({result_val}), belum ada rekaman attempt di data SITASI."

    cert_evidence = [{
        "source": CERTIPORT_SOURCE,
        "id": rec.get("id"),
        "source_row": rec.get("source_row"),
        "full_name": rec.get("full_name"),
        "program_name": rec.get("program_name"),
        "certification_name": rec.get("certification_name"),
        "score": rec.get("score"),
        "result": result_val,
        "exam_alias_reason": "certiport_direct_read",
    }]

    if fuzzy:
        combined = PERLU_VERIFIKASI
    elif is_pass:
        combined = VALID
    elif is_fail:
        combined = TIDAK_LULUS
    else:
        combined = PERLU_VERIFIKASI

    return {
        "sertifikasi": cat,
        "sub_program": sub_prog,
        "exam_status": combined,
        "has_lulus": False,
        "has_pending": False,
        "has_fail": is_fail,
        "score": _parse_numeric_score(rec.get("score")),
        "attempts": [],
        "certiport_only": True,
        "certiport_validation": {
            "certiport_status": "PASS" if is_pass else ("FAIL" if is_fail else PERLU_VERIFIKASI),
            "combined_status": combined,
            "certiport_evidence": cert_evidence,
            "reason": reason,
        },
        "evidence": {
            "source": CERTIPORT_SOURCE,
            "import_id": certiport_import_id,
            "attempt_count": 0,
        },
    }


def match_sitasi_to_certiport(
    wisuda_sitasi_results: list[dict],
    certiport_rows: list[dict],
    certiport_import_id: str | None = None,
) -> list[dict]:
    """Cross-validate hasil Wisuda→SITASI terhadap batch Certiport aktif.

    Mengecek NIM di SITASI dan Nama di Certiport secara langsung. Jika data
    mahasiswa atau ujian tidak ada di SITASI tetapi ada di Certiport, data Certiport
    tetap dibaca dan dicatat sebagai bukti verifikasi.
    """
    cert_index = build_certiport_name_index(certiport_rows)
    results: list[dict] = []

    for ws_result in wisuda_sitasi_results:
        enriched = {**ws_result}
        enriched["certiport_import_id"] = certiport_import_id
        exams = list(ws_result.get("exams", []))
        enriched["exams"] = exams

        nama_wisuda = normalize_name(ws_result.get("nama"))
        sitasi_matched = bool(ws_result.get("sitasi_matched", False))

        nama_sitasi_set: set[str] = set()
        for exam in exams:
            for att in exam.get("attempts", []):
                n = normalize_name(att.get("nama"))
                if n:
                    nama_sitasi_set.add(n)

        search_names: list[str] = []
        if nama_wisuda:
            search_names.append(nama_wisuda)
        for n in sorted(nama_sitasi_set):
            if n not in search_names:
                search_names.append(n)

        all_candidates: list[dict] = []
        seen_names: set[str] = set()
        for search_name in search_names:
            candidates = _find_certiport_candidates_fuzzy(search_name, cert_index)
            for c in candidates:
                if c["name"] not in seen_names:
                    all_candidates.append(c)
                    seen_names.add(c["name"])

        unique_persons = set()
        all_candidate_records: list[dict] = []
        for c in all_candidates:
            # Ambiguity dinilai hanya dari kandidat sangat mirip (>= 95),
            # sedangkan daftar saran tetap memakai ambang lebih longgar (85).
            if c["score"] >= FUZZY_STRONG_THRESHOLD:
                unique_persons.add(c["name"])
            for rec in c["records"]:
                all_candidate_records.append(rec)

        candidate_summary = [
            {"name": c["name"], "score": c["score"], "reason": c["reason"], "record_count": len(c["records"])}
            for c in all_candidates
        ]

        if not all_candidates:
            enriched["certiport_match"] = {
                "status": DATA_TIDAK_DITEMUKAN,
                "reason": "Tidak ditemukan kandidat Certiport berdasar nama.",
                "candidates": [],
            }
            if not exams:
                enriched["overall_status"] = DATA_TIDAK_DITEMUKAN
                results.append(enriched)
                continue

            for exam in exams:
                exam["certiport_validation"] = {
                    "combined_status": _sitasi_only_combined(exam, sitasi_matched),
                    "certiport_status": DATA_TIDAK_DITEMUKAN,
                    "certiport_evidence": [],
                    "reason": "Tidak ada kandidat Certiport.",
                }
            enriched["overall_status"] = _compute_combined_overall(exams)
            results.append(enriched)
            continue

        if len(unique_persons) > 1:
            enriched["certiport_match"] = {
                "status": PERLU_VERIFIKASI,
                "reason": f"Ditemukan {len(unique_persons)} nama berbeda sebagai kandidat; risiko salah orang.",
                "candidates": candidate_summary,
            }
            for exam in exams:
                exam["certiport_validation"] = {
                    "combined_status": PERLU_VERIFIKASI,
                    "certiport_status": PERLU_VERIFIKASI,
                    "certiport_evidence": [],
                    "reason": "Kandidat nama ganda; perlu review manusia.",
                }
            enriched["overall_status"] = PERLU_VERIFIKASI
            results.append(enriched)
            continue

        exact_names = set(search_names)
        exact_records = []
        for c in all_candidates:
            if c["name"] in exact_names:
                exact_records.extend(c["records"])

        if not exact_records:
            enriched["certiport_match"] = {
                "status": PERLU_VERIFIKASI if not sitasi_matched else "FUZZY_ONLY",
                "reason": (
                    "Hanya kandidat fuzzy (bukan exact name); perlu review manusia."
                    if not sitasi_matched
                    else "Hanya kandidat Certiport mirip; SITASI sudah cocok (NIM+nama)."
                ),
                "candidates": candidate_summary,
            }
            if not sitasi_matched:
                target_records = all_candidate_records
                matched_cert_ids = set()
                for exam in exams:
                    validation = _cross_validate_exam(exam, target_records, sitasi_matched=False)
                    validation["combined_status"] = PERLU_VERIFIKASI
                    exam["certiport_validation"] = validation
                    for ev in validation.get("certiport_evidence", []):
                        matched_cert_ids.add(ev.get("id"))

                for rec in target_records:
                    if rec.get("id") not in matched_cert_ids:
                        matched_cert_ids.add(rec.get("id"))
                        extra_exam = _build_certiport_only_exam(rec, certiport_import_id, fuzzy=True)
                        exams.append(extra_exam)

                enriched["overall_status"] = PERLU_VERIFIKASI
            else:
                # SITASI sudah cocok (NIM+nama) → status SITASI cukup; kandidat mirip hanya saran.
                for exam in exams:
                    exam["certiport_validation"] = _cross_validate_exam(exam, [], sitasi_matched=True)
                enriched["overall_status"] = _compute_combined_overall(exams)
            results.append(enriched)
            continue

        enriched["certiport_match"] = {
            "status": "MATCHED",
            "reason": "Satu kandidat exact name ditemukan.",
            "candidates": candidate_summary,
        }

        matched_cert_ids = set()
        for exam in exams:
            validation = _cross_validate_exam(exam, exact_records, sitasi_matched=sitasi_matched)
            exam["certiport_validation"] = validation
            for ev in validation.get("certiport_evidence", []):
                matched_cert_ids.add(ev.get("id"))

        # Baca seluruh record Certiport yang belum ada di SITASI
        for rec in exact_records:
            if rec.get("id") not in matched_cert_ids:
                matched_cert_ids.add(rec.get("id"))
                extra_exam = _build_certiport_only_exam(rec, certiport_import_id, fuzzy=False)
                exams.append(extra_exam)

        enriched["overall_status"] = _compute_combined_overall(exams)
        results.append(enriched)

    return results



def _compute_combined_overall(exams: list[dict]) -> str:
    """Hitung overall status dari combined_status per exam setelah Certiport validation."""
    if not exams:
        return DATA_TIDAK_DITEMUKAN

    statuses = []
    for e in exams:
        cv = e.get("certiport_validation", {})
        statuses.append(cv.get("combined_status", e.get("exam_status", PERLU_VERIFIKASI)))

    if PERLU_VERIFIKASI in statuses:
        return PERLU_VERIFIKASI
    if PENDING in statuses:
        return PENDING
    if all(s == VALID for s in statuses):
        return VALID
    if all(s == TIDAK_LULUS for s in statuses):
        return TIDAK_LULUS
    return PERLU_VERIFIKASI


def _overall_from_statuses(statuses: list[str]) -> str:
    """Prioritas status keseluruhan dari daftar status program (relevan)."""
    if not statuses:
        return PERLU_VERIFIKASI
    if PERLU_VERIFIKASI in statuses:
        return PERLU_VERIFIKASI
    if PENDING in statuses:
        return PENDING
    if all(s == VALID for s in statuses):
        return VALID
    if all(s == TIDAK_LULUS for s in statuses):
        return TIDAK_LULUS
    return PERLU_VERIFIKASI


# ---------------------------------------------------------------------------
# Tahap 10: Validation engine — per-program summary + review flags
# ---------------------------------------------------------------------------

REASON_CODES = {
    "R01_VALID": "SITASI LULUS + Certiport PASS + identitas unik + mapping ujian sesuai.",
    "R02_DRAFT_ALIAS": "Bukti konsisten tapi alias ujian masih DRAFT (ADR-005); perlu pengesahan.",
    "R03_NO_CERTIPORT_CANDIDATE": "Tidak ditemukan kandidat Certiport; bukti eksternal belum ada.",
    "R04_CERTIPORT_NO_PASS": "SITASI LULUS tapi Certiport tidak ada PASS; konflik sumber.",
    "R05_SITASI_NO_LULUS_CERT_PASS": "Certiport PASS tapi SITASI tidak ada LULUS; konflik sumber.",
    "R06_BOTH_FAIL": "SITASI dan Certiport keduanya tidak lulus.",
    "R07_PENDING": "SITASI masih PENDING; bukti belum cukup.",
    "R08_MULTIPLE_CANDIDATES": "Kandidat nama ganda; risiko salah orang.",
    "R09_FUZZY_ONLY": "Hanya kandidat fuzzy (bukan exact name); perlu review manusia.",
    "R10_EXAM_MISMATCH": "Kategori program sama tapi ujian berbeda; bukan validasi silang.",
    "R11_NO_SITASI": "Data tidak ditemukan pada batch SITASI maupun Certiport aktif.",
    "R12_INCO": "Hasil Certiport INCO/kosong; bukti tidak cukup.",
    "R13_UNKNOWN_STATUS": "Status tidak dikenali; perlu review.",
    "R14_CERTIPORT_ONLY": "Sertifikasi tercatat di Certiport (PASS), namun belum ada rekaman attempt di data SITASI.",
}


def _classify_reason_code(certiport_validation: dict, certiport_match: dict | None = None) -> str:
    combined = certiport_validation.get("combined_status", "")
    reason_text = certiport_validation.get("reason", "")
    cert_status = certiport_validation.get("certiport_status", "")

    if "belum ada rekaman attempt di data SITASI" in reason_text or "belum tercatat di data SITASI" in reason_text:
        return "R14_CERTIPORT_ONLY"
    if combined == VALID:
        return "R01_VALID"
    if "DRAFT" in reason_text or "draft" in reason_text.lower():
        return "R02_DRAFT_ALIAS"
    if cert_status == DATA_TIDAK_DITEMUKAN:
        if certiport_match and certiport_match.get("status") == DATA_TIDAK_DITEMUKAN:
            return "R03_NO_CERTIPORT_CANDIDATE"
        return "R10_EXAM_MISMATCH"
    if certiport_match and certiport_match.get("status") == PERLU_VERIFIKASI:
        match_reason = certiport_match.get("reason", "")
        if "nama" in match_reason.lower() or "salah orang" in match_reason.lower():
            return "R08_MULTIPLE_CANDIDATES"
        if "fuzzy" in match_reason.lower():
            return "R09_FUZZY_ONLY"
    if "konflik" in reason_text.lower() or "tidak ada PASS" in reason_text:
        if "SITASI LULUS" in reason_text:
            return "R04_CERTIPORT_NO_PASS"
        return "R05_SITASI_NO_LULUS_CERT_PASS"
    if combined == TIDAK_LULUS:
        return "R06_BOTH_FAIL"
    if combined == PENDING:
        return "R07_PENDING"

    evidence = certiport_validation.get("certiport_evidence", [])
    for ev in evidence:
        r = ev.get("result")
        if r and r not in ("PASS", "FAIL"):
            return "R12_INCO"

    return "R13_UNKNOWN_STATUS"


def _build_program_summary(exams: list[dict]) -> dict[str, dict]:
    """Bangun ringkasan per program (MOS, MCF, dll.) dari exam results.

    Setiap program berisi: status, exam_details, reason_codes, needs_review.
    Status per program dihitung independen — tidak saling menimpa.
    """
    program_groups: dict[str, list[dict]] = defaultdict(list)
    for exam in exams:
        cert = exam.get("sertifikasi", "")
        program_groups[cert].append(exam)

    summary: dict[str, dict] = {}
    for program, program_exams in sorted(program_groups.items()):
        if not program:
            program = "UNKNOWN"

        statuses = []
        exam_details = []
        reason_codes = []
        needs_review = False
        program_scores: list[float | int] = []
        exam_scores_map: dict[str, Any] = {}

        # Cek apakah ada ujian konkret (bukan placeholder pendaftaran) pada program ini
        has_concrete_exams = any(
            (normalize_upper(e.get("sub_program")) or "") not in PLACEHOLDER_SUB_PROGRAMS
            for e in program_exams
        )

        for exam in program_exams:
            cv = exam.get("certiport_validation", {})
            combined = cv.get("combined_status", exam.get("exam_status", PERLU_VERIFIKASI))

            rc = _classify_reason_code(cv, exam.get("_certiport_match_ref"))

            sub_name = exam.get("sub_program", "")
            sub_norm = normalize_upper(sub_name) or ""
            is_placeholder_pending = (sub_norm in PLACEHOLDER_SUB_PROGRAMS) and (
                combined == PENDING or exam.get("has_pending")
            )

            # Jika mahasiswa sudah memiliki ujian konkret, rekaman pendaftaran awal (Tidak Diketahui / PENDING)
            # tidak boleh menurunkan status program menjadi PENDING atau memaksa needs_review.
            if not (has_concrete_exams and is_placeholder_pending):
                statuses.append(combined)
                reason_codes.append(rc)
                if combined != VALID:
                    needs_review = True

            is_cert_only = exam.get("certiport_only", False)
            sit_score = None if is_cert_only else exam.get("score")
            cert_ev = cv.get("certiport_evidence", [])
            cert_score = _parse_numeric_score(cert_ev[0].get("score")) if cert_ev else (_parse_numeric_score(exam.get("score")) if is_cert_only else None)
            effective_score = cert_score if is_cert_only else (sit_score if sit_score is not None else cert_score)

            sub_name = exam.get("sub_program", "")
            if effective_score is not None:
                program_scores.append(effective_score)
                exam_scores_map[sub_name] = effective_score

            selected_att = exam.get("selected_attempt") or (exam.get("attempts", [{}])[0] if exam.get("attempts") else {})
            sitasi_name = None if is_cert_only else selected_att.get("nama")
            sitasi_status = None if is_cert_only else selected_att.get("status")

            certiport_name = cert_ev[0].get("full_name") if cert_ev else None
            certiport_result = cert_ev[0].get("result") if cert_ev else None

            exam_details.append({
                "sub_program": sub_name,
                "exam_status": exam.get("exam_status", ""),
                "combined_status": combined,
                "score": effective_score,
                "sitasi_score": sit_score,
                "sitasi_name": sitasi_name,
                "sitasi_status": sitasi_status,
                "certiport_score": cert_score,
                "certiport_name": certiport_name,
                "certiport_status": certiport_result,
                "reason_code": rc,
                "has_lulus": exam.get("has_lulus", False),
                "certiport_evidence": cert_ev,
                "sitasi_attempt_count": len(exam.get("attempts", [])),
                "certiport_only": exam.get("certiport_only", False),
            })

        if PERLU_VERIFIKASI in statuses:
            program_status = PERLU_VERIFIKASI
        elif PENDING in statuses:
            program_status = PENDING
        elif all(s == VALID for s in statuses):
            program_status = VALID
        elif all(s == TIDAK_LULUS for s in statuses):
            program_status = TIDAK_LULUS
        else:
            program_status = PERLU_VERIFIKASI

        best_program_score = max(program_scores) if program_scores else None
        sitasi_names = [ed["sitasi_name"] for ed in exam_details if ed.get("sitasi_name")]
        certiport_names = [ed["certiport_name"] for ed in exam_details if ed.get("certiport_name")]
        summary[program] = {
            "status": program_status,
            "score": best_program_score,
            "scores": exam_scores_map,
            "sitasi_name": sitasi_names[0] if sitasi_names else None,
            "certiport_name": certiport_names[0] if certiport_names else None,
            "exam_count": len(program_exams),
            "exam_details": exam_details,
            "reason_codes": sorted(set(reason_codes)),
            "needs_review": needs_review,
        }

    return summary


def validate_wisuda_complete(
    wisuda_rows: list[dict],
    sitasi_rows: list[dict],
    certiport_rows: list[dict],
    sitasi_import_id: str | None = None,
    certiport_import_id: str | None = None,
) -> list[dict]:
    """Pipeline validasi lengkap per baris wisuda: SITASI matching → Certiport cross-validation → program summary.

    Pure function. Mengembalikan list of dicts dengan:
    - Semua field dari match_wisuda_to_sitasi + match_sitasi_to_certiport
    - program_summary: {MOS: {status, exam_details, ...}, MCF: {...}}
    - mos_status, mcf_status: shortcut status per program
    - validation_status: overall
    - reason_codes: semua reason code dari semua ujian
    - needs_review: bool
    - review_flags: list alasan review
    """
    ws_results = match_wisuda_to_sitasi(wisuda_rows, sitasi_rows, import_id=sitasi_import_id)
    enriched_results = match_sitasi_to_certiport(ws_results, certiport_rows, certiport_import_id=certiport_import_id)

    final: list[dict] = []
    for row in enriched_results:
        validated = {**row}

        if row["overall_status"] == DATA_TIDAK_DITEMUKAN:
            validated["program_summary"] = {}
            validated["mos_score"] = None
            validated["mcf_score"] = None
            if not row.get("nim_normalized"):
                validated["mos_status"] = None
                validated["mcf_status"] = None
                validated["validation_status"] = PERLU_VERIFIKASI
                validated["reason_codes"] = ["R13_UNKNOWN_STATUS"]
                validated["needs_review"] = True
                validated["review_flags"] = ["NIM tidak valid/kosong pada baris wisuda"]
            else:
                validated["mos_status"] = DATA_TIDAK_DITEMUKAN
                validated["mcf_status"] = DATA_TIDAK_DITEMUKAN
                validated["validation_status"] = DATA_TIDAK_DITEMUKAN
                validated["reason_codes"] = ["R11_NO_SITASI"]
                validated["needs_review"] = True
                validated["review_flags"] = ["Data tidak ditemukan di SITASI maupun Certiport"]
            final.append(validated)
            continue

        certiport_match = row.get("certiport_match", {})
        for exam in row.get("exams", []):
            exam["_certiport_match_ref"] = certiport_match

        program_summary = _build_program_summary(row.get("exams", []))

        for exam in row.get("exams", []):
            exam.pop("_certiport_match_ref", None)

        # MCF hanya relevan untuk prodi tertentu (mis. 31 Informatika, 32 Sistem Informasi).
        mcf_relevant = is_mcf_relevant(row.get("kode_prodi"))

        validated["program_summary"] = program_summary
        validated["mos_status"] = program_summary.get("MOS", {}).get("status", DATA_TIDAK_DITEMUKAN)
        validated["mos_score"] = program_summary.get("MOS", {}).get("score")
        if mcf_relevant:
            validated["mcf_status"] = program_summary.get("MCF", {}).get("status", DATA_TIDAK_DITEMUKAN)
            validated["mcf_score"] = program_summary.get("MCF", {}).get("score")
        else:
            validated["mcf_status"] = None
            validated["mcf_score"] = None

        all_reason_codes: list[str] = []
        needs_review = False
        review_flags: list[str] = []

        for prog_name, prog_data in program_summary.items():
            if prog_name == "MCF" and not mcf_relevant:
                continue
            all_reason_codes.extend(prog_data.get("reason_codes", []))
            if prog_data.get("needs_review"):
                needs_review = True
                review_flags.append(f"{prog_name}: perlu review")

        relevant_statuses: list[str] = []
        for prog_name, prog_data in program_summary.items():
            if prog_name == "MCF" and not mcf_relevant:
                continue
            relevant_statuses.append(prog_data.get("status") or "")
        relevant_statuses = [s for s in relevant_statuses if s]
        overall = (
            _overall_from_statuses(relevant_statuses)
            if relevant_statuses
            else row.get("overall_status", PERLU_VERIFIKASI)
        )

        if row.get("name_match") in ("DIFFERENT", "PARTIAL"):
            needs_review = True
            review_flags.append(f"Nama tidak cocok persis di SITASI: name_match={row['name_match']}")

        certiport_only_exams = [e for e in row.get("exams", []) if e.get("certiport_only")]
        if certiport_only_exams:
            needs_review = True
            review_flags.append("Sertifikasi terbaca dari Certiport (tanpa rekaman SITASI)")

        cm_status = certiport_match.get("status", "")
        if cm_status == PERLU_VERIFIKASI:
            needs_review = True
            cm_reason = certiport_match.get("reason", "")
            if "nama" in cm_reason.lower() or "salah orang" in cm_reason.lower():
                review_flags.append("Kandidat Certiport nama ganda")
            elif "fuzzy" in cm_reason.lower() or "mirip" in cm_reason.lower():
                review_flags.append("Kandidat Certiport hanya mirip (fuzzy)")
            candidates = certiport_match.get("candidates", []) or []
            if candidates:
                top = candidates[:FUZZY_TOP_N]
                review_flags.append(
                    "Kandidat Certiport mirip: "
                    + ", ".join(f"{c.get('name')} ({c.get('score')})" for c in top)
                )

        validated["reason_codes"] = sorted(set(all_reason_codes))
        validated["needs_review"] = needs_review
        validated["review_flags"] = review_flags
        validated["validation_status"] = overall

        final.append(validated)

    return final
