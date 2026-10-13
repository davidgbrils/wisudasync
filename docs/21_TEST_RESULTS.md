# 21 — Laporan Hasil Pengujian Terintegrasi & Kualitas (Test Results)

Dokumen ini mencatat bukti eksekusi pengujian aktual sistem ITCC Wisuda Sync sesuai `docs/10_TEST_PLAN.md` dan `docs/15_ACCEPTANCE.md`.

- **Tanggal Pengujian:** 2026-10-09
- **Lingkungan Pengujian:** Lokal (Node.js 20+, Python 3.12, Windows 11)
- **Dataset Pengujian:** Fixture sintetis anonim (tanpa data pribadi mahasiswa nyata)

---

## 1. Ringkasan Eksekusi Suite Pengujian

| Kategori Pengujian | Perintah Eksekusi | Jumlah Kasus | Status | Waktu Eksekusi |
|---|---|---|---|---|
| **Backend Unit & API** | `venv\Scripts\python.exe -m pytest tests -v` | 134 test | **PASS** | 2.74s |
| **Frontend Typecheck** | `npm run typecheck` | Seluruh codebase TS | **PASS** | ~2.5s |
| **Frontend Production Build** | `npm run build` | Next.js 16 Turbopack | **PASS** | ~11.7s |
| **Security & Auth Guard** | `pytest tests/test_auth.py tests/test_review.py -v` | 20 test | **PASS** | 2.1s |
| **Excel Parser & Anomali** | `pytest tests/test_import_service.py tests/test_wisuda_validation.py -v` | 17 test | **PASS** | 1.8s |
| **Matching & Validation Engine** | `pytest tests/test_matching_service.py tests/test_certiport_matching.py tests/test_validation_engine.py -v` | 67 test | **PASS** | 3.2s |
| **Sync Persistence & Review** | `pytest tests/test_sync_service.py tests/test_sync_api.py tests/test_review.py -v` | 27 test | **PASS** | 2.4s |
| **Export Gate (ADR Policy)** | `pytest tests/test_export_gate.py -v` | 6 test | **PASS** | 1.8s |

---

## 2. Rincian Matriks Kasus Uji Sesuai `docs/10_TEST_PLAN.md`

| Test ID | Skenario Uji | Input Uji Anonim | Ekspektasi | Hasil Aktual | Status |
|---|---|---|---|---|---|
| **TC-AUTH-01** | Akses tanpa token | `POST /sync`, `GET /sync` tanpa auth header | HTTP 401 Unauthorized | HTTP 401 | **PASS** |
| **TC-AUTH-02** | User login non-staf | Token user role non-staff | HTTP 403 Forbidden | HTTP 403 | **PASS** |
| **TC-IMP-01** | XLSX SITASI valid | Header standar 8 kolom, batch valid | Batch selesai, `source_row` akurat | Batch COMPLETED | **PASS** |
| **TC-IMP-02** | XLSX Certiport valid | Header Certiport resmi | Normalisasi nama & hasil | Normalisasi tersimpan | **PASS** |
| **TC-IMP-03** | Header XLSX hilang/salah | Kolom `Sub Program` dihapus | Ditolak sebelum batch aktif | HTTP 400 rejected | **PASS** |
| **TC-NORM-01** | Nama dengan tanda baca | `". NAMA CONTOH "` | Asli utuh, normalized `NAMA CONTOH` | String bersih | **PASS** |
| **TC-NORM-02** | NIM dengan nol awal | String `"001234"` | Nol awal tidak hilang | `"001234"` utuh | **PASS** |
| **TC-BATCH-01** | Import baru gagal | Simulasi error di tengah parsing | Batch aktif lama tetap utuh | Staging dibersihkan | **PASS** |
| **TC-BATCH-02** | Snapshot sesi lama | Master baru diaktifkan sesudah sync | Sesi lama tetap merujuk batch ID lama | Immutability terjaga | **PASS** |
| **TC-WIS-01** | Upload wisuda valid | Header wisuda 8 kolom | Pembacaan baris presisi | Baris terbaca aman | **PASS** |
| **TC-WIS-02** | File wisuda formula/makro | Berkas `.xlsm` atau formula cell | Ditolak demi keamanan formula injection | HTTP 400 rejected | **PASS** |
| **TC-MAT-01** | Exact NIM SITASI | NIM string cocok | Seluruh riwayat attempt diambil | Multi-attempt grouped | **PASS** |
| **TC-MAT-02** | Multiple attempts | FAIL, FAIL, LULUS ujian sama | Status LULUS diprioritaskan | Riwayat tersimpan | **PASS** |
| **TC-MAT-03** | Nama ambigu/fuzzy | Nama mirip skor RapidFuzz tinggi | `PERLU_VERIFIKASI` (bukan auto-valid) | Flag review aktif | **PASS** |
| **TC-MAT-04** | Cross-program mismatch | SITASI MOS Word, Certiport Excel | Tidak cocok lintas sub-ujian | `PERLU_VERIFIKASI` | **PASS** |
| **TC-MAT-05** | Certiport nama ganda | Dua nama berbeda untuk 1 mahasiswa | Ambigu orang berbeda $\rightarrow$ review | Flag nama ganda | **PASS** |
| **TC-VAL-01** | Konflik hasil | SITASI LULUS, Certiport FAIL | Konflik hasil $\rightarrow$ review | Reason R04 / review | **PASS** |
| **TC-VAL-02** | NIM tidak ditemukan | NIM tidak ada di master SITASI | `DATA_TIDAK_DITEMUKAN` | Reason R11 | **PASS** |
| **TC-VAL-03** | Certiport `INCO` | Status hasil tidak lengkap | Status `PERLU_VERIFIKASI` | Flag review aktif | **PASS** |
| **TC-REVIEW-01** | Review staf (tunda/tolak) | Aksi `TUNDA_VERIFIKASI` + catatan | Status terupdate, audit tercatat | Audit append-only | **PASS** |
| **TC-REVIEW-02** | Review catatan kosong | Submit keputusan tanpa teks | Ditolak validasi | HTTP 422 Unprocessable | **PASS** |
| **TC-REVIEW-03** | Guard ADR-009 | Staf konfirmasi cocok tanpa izin | Ditolak kebijakan reviewer | HTTP 403 Forbidden | **PASS** |
| **TC-EXP-01** | Ekspor DRAFT | Endpoint `GET /sync/{id}/export?mode=draft` | File `.xlsx` streaming berlabel `[DRAFT]` | HTTP 200 Excel | **PASS** |
| **TC-EXP-02** | Gate Ekspor Final | Endpoint `GET /sync/{id}/export?mode=final` | Ditolak sebelum pengesahan ADR | HTTP 403 Forbidden | **PASS** |

---

## 3. Bukti Pengujian Input Anomali & Batas Keamanan

1. **File Berukuran Besar (>10MB):**
   - Bukti: `test_import_rejects_oversized_upload` & `test_sitasi_endpoint_returns_413_for_oversized_file`.
   - Hasil: HTTP 413 Payload Too Large; proses dihentikan sebelum membaca memory.
2. **File Mengandung Formula / Macro:**
   - Bukti: `test_import_rejects_formula_workbook` & `test_import_rejects_macro_member`.
   - Hasil: Ditolak dengan pesan kesalahan eksplisit tanpa mengeksekusi rumus Excel.
3. **Penyembunyian Detail Server Internal:**
   - Bukti: `test_sitasi_endpoint_hides_internal_storage_error`.
   - Hasil: Traceback internal tidak diekspos ke klien; pesan generik aman dikembalikan.

---

## 4. Batasan & Lingkungan Pengujian Lanjutan

- **Pengujian Database Runtime:** Migrasi SQL telah diuji konsistensi sintaks dan relasionalnya; eksekusi langsung terhadap PostgreSQL Supabase di lingkungan dev berizin memerlukan credential proyek aktif yang sudah dirotasi oleh pemilik.
- **Pengujian Visual Browser End-to-End:** UI lulus typecheck dan compilation production build Next.js; smoke test visual interaktif pada browser sesudah login membutuhkan akun dev berizin.
