# 18 — Changelog Dokumentasi dan Pengembangan

Format catatan: tanggal, versi, perubahan, alasan, bukti atau keterbatasan. Bedakan pembuatan dokumen dengan penyelesaian program.

## 2026-09-30 — 1.0-draft — Paket awal dokumentasi
- Menyusun PRD, SRS, arsitektur, kamus data, algoritma matching, model database target, kontrak API, UI, test plan, privasi, roadmap, panduan laporan, ADR, acceptance, glosarium, panduan operasional dan AGENTS.md.
- Menyesuaikan nama sheet dan header dengan contoh Excel yang tersedia.
- Mempertahankan scope Phase 1–4 dan menandai Phase 4 hanya sebagai starter kode, bukan sistem selesai.
- Mengunci kebutuhan review untuk kandidat Certiport yang ambigu dan pemisahan validasi per ujian.
- Mencatat keputusan tertunda terkait `Sertifikasi MOS`, `Sertifikasi MCF`, `Title Microsoft`, alias ujian dan retensi.

### Belum dikerjakan pada rilis dokumentasi
- Tidak membuat atau mengubah database Supabase pengguna.
- Tidak menjalankan kode starter terhadap database pengguna.
- Tidak membuat/menjalankan engine sinkronisasi Wisuda Phase 5.
- Tidak menulis laporan hasil uji palsu.

## Template perubahan berikutnya
```text
Tanggal:
Versi / commit:
Dokumen atau kode berubah:
Alasan perubahan:
Test dijalankan:
Hasil aktual:
Keputusan terbuka / risiko:
Penanggung jawab:
```

## 2026-09-30 — Aturan agent dan struktur dokumentasi

- Memindahkan paket dokumentasi dari root semu `docs-wisuda-sync/docs` ke folder root `docs` agar repository tidak memiliki dua root bersarang.
- Menggabungkan aturan kerja, arsitektur, keamanan, hemat token, playbook, dan kontrak respons ke root `AGENTS.md`.
- Menambahkan checkpoint `docs/19_AI_PROGRESS.md` untuk mencatat status tahap dan bukti pengujian.
- Perubahan hanya menyentuh dokumentasi dan instruksi agent; source aplikasi tidak diubah.
- Validasi: seluruh sumber wajib ditemukan, tautan indeks diperiksa, dan `git diff --check` dijalankan.

## 2026-09-30 — Tahap 01 audit starter dan pemulihan frontend

- Mengaudit kesesuaian starter Phase 4 terhadap PRD, SRS, arsitektur, dan keputusan terbuka.
- Mengonfirmasi import SITASI/Certiport sudah tersambung di kode dari UI ke FastAPI lalu Supabase, tetapi belum diverifikasi end-to-end pada environment berizin.
- Mengonfirmasi endpoint master belum memakai auth dan pergantian batch aktif masih terdiri dari dua operasi update.
- Menambahkan fondasi Next.js App Router, TypeScript, dan Tailwind minimum agar `npm install`, typecheck, dan production build frontend dapat dijalankan.
- Mencatat credential nyata pada file contoh sebagai blocker keamanan P0 tanpa menyalin nilainya ke dokumentasi.
- Bukti: `npm install`, `npm run typecheck`, `npm run build`, `npm audit`, dan tiga pemeriksaan normalisasi backend.

## 2026-09-30 — Tahap 02 fondasi lokal

- Menambahkan instruksi PowerShell Windows untuk membuat virtualenv, memasang dependency terkunci, menjalankan FastAPI/Next.js, dan melakukan pemeriksaan lokal.
- Mengunci dependency produksi Python pada `requirements.txt`, menambah dependency pengujian, dan membuat `requirements.lock.txt` dari environment Python 3.12 yang tervalidasi.
- Mengganti template backend dengan URL/key dummy, menambahkan root `.gitignore`, dan membatasi CORS ke origin frontend terkonfigurasi serta metode/header yang diperlukan.
- Menambahkan test health dan CORS tanpa koneksi Supabase maupun data asli.
- Mempertahankan alur frontend ke FastAPI melalui `NEXT_PUBLIC_API_URL`; business rules, parser, import, dan database tidak diubah.
- Bukti: 6 test backend lulus, health server nyata mengembalikan HTTP 200, CORS localhost diterima dan origin lain ditolak, `npm ci`, typecheck, build, audit dependency, serta smoke Next.js `/sitasi` HTTP 200 lulus.

## 2026-09-30 — Tahap 03 fondasi database Phase 4

- Mengganti SQL starter tunggal dengan migration versi-terkontrol untuk `profiles`, `data_imports`, `sitasi_data`, dan `certiport_data`; tidak menambahkan tabel hasil sinkronisasi.
- Menambahkan constraint `(import_id, source_row)`, indeks pencarian per batch, indeks unik satu batch aktif per tipe, serta fungsi transaksi `complete_data_import` untuk pergantian batch atomik.
- Mengaktifkan RLS deny-by-default, mencabut akses `PUBLIC`/`anon`/`authenticated`, dan membatasi tabel serta fungsi aktivasi kepada `service_role` backend.
- Menambahkan query pemeriksaan read-only dan rollback development yang membatalkan operasi bila tabel masih berisi data serta tidak memakai `CASCADE`.
- Validasi statis dan `git diff --check` dijalankan. Eksekusi SQL pada PostgreSQL/Supabase belum dijalankan karena tidak tersedia database development berizin, `psql`/Supabase CLI tidak terpasang, dan daemon Docker lokal tidak aktif.
- Backend belum dipindahkan ke fungsi atomik; `import_service.py` masih menjalankan dua update dan harus ditangani setelah migration lulus pada database development.

## 2026-10-01 — Tahap 04 importer SITASI/Certiport

- Menguatkan importer yang ada: sheet wajib sesuai kamus data, header lengkap dicari pada 10 baris awal, file `.xlsx` diperiksa sebagai ZIP workbook, dan formula/macro ditolak.
- Batas upload 10 MiB dapat diatur melalui `MAX_UPLOAD_SIZE_BYTES`; isi workbook terkompresi juga dibatasi untuk mencegah file membengkak saat diproses.
- Mempertahankan nama sumber persis dan menyimpan normalisasi terpisah; NIM teks/nol format Excel dipertahankan, `source_row` mengikuti baris Excel, status Certiport dinormalisasi, dan duplicate attempts tidak dibuang.
- Pergantian batch memakai RPC transaksi `complete_data_import` yang telah dibuat pada migration Tahap 03. Kegagalan upload membersihkan batch staging dan tidak mengubah batch aktif lama; detail exception tidak dikirim ke client.
- Fixture XLSX sintetis dibuat di memori untuk normal, duplicate attempts, header/sheet salah, formula/macro, batas ukuran, serta kegagalan insert/RPC. Tiga workbook lokal yang tidak terlacak dikecualikan dari Git tanpa dibuka.
- Bukti: 13 test importer dan seluruh 19 test backend lulus; `git diff --check` lulus. Uji terhadap Supabase/PostgreSQL development belum dijalankan.
- Risiko tersisa: endpoint import masih belum memiliki JWT dan otorisasi staff/admin; jangan gunakan data asli sampai auth guard dan uji DB development selesai.

## 2026-10-01 — Tahap 05 Supabase Auth dan kontrol akses
- Menambahkan login/logout Supabase tanpa alur signup, Proxy penyegaran sesi Next.js, pemeriksaan route petugas, serta bearer token pada request browser → FastAPI.
- FastAPI memvalidasi access token melalui Supabase Auth lalu memeriksa `profiles` server-side; endpoint SITASI/Certiport dan `/auth/me` hanya mengizinkan profil aktif ber-role `staff`/`admin`. Error Auth/DB tidak membocorkan detail atau token.
- Menambahkan migration penguncian ulang RLS/grants untuk menutup akses langsung role browser dan prosedur penambahan petugas pertama pada environment development.
- Test fixture mencakup tanpa token, token invalid, user tanpa profil berizin, petugas sah, serta health publik. Supabase runtime, migration SQL, signup setting, dan rotasi credential belum diverifikasi.

## 2026-10-01 — Tahap 06 UI data master
- Menambahkan shell responsif dengan sidebar desktop/navigasi seluler, halaman ringkasan, serta status batch aktif SITASI dan Certiport.
- Melengkapi pencarian/filter server-side, paginasi, import `.xlsx`, informasi batch, dan state loading/kosong/error pada halaman data master.
- Menambahkan endpoint FastAPI terlindungi untuk metadata batch aktif; frontend tetap mengambil data hanya melalui FastAPI dengan bearer token. Notifikasi menggunakan pesan aman dan tidak menampilkan isi baris/nama file.
- Metadata batch hanya memuat kolom allowlist; nama file dan kolom lain tidak dikembalikan ke UI.
- Bukti: 30 test backend, typecheck, production build, serta HTTP smoke test login 200 dan dashboard tanpa konfigurasi auth dialihkan ke login. Tampilan dashboard sesudah login petugas belum dapat diuji tanpa kredensial Supabase development.
## 2026-10-01 — Tahap 07 upload & validasi Wisuda
- Endpoint petugas `POST /api/v1/sync/validate` membaca `.xlsx` Wisuda tanpa menyimpan atau mengubah workbook.
- Parser memvalidasi sheet/header NIM dan Nama, baris kosong, data kosong, format NIM angka/teks/nol awal, formula kolom wajib, dan NIM duplikat.
- UI drag-and-drop menampilkan jumlah baris, masalah per baris tanpa nilai PII, urutan kolom, serta batch SITASI/Certiport aktif.
- Test memakai fixture sintetis; pemetaan/penulisan ulang kolom sertifikasi tidak dilakukan. Uji Supabase dan browser visual masih perlu dilakukan.
- Bukti lokal: 34 test backend, typecheck, build frontend, dan `git diff --check` lulus; build menghasilkan route `/sinkronisasi`.

## 2026-10-02 — Tahap 08: Matching Wisuda→SITASI (pure service)

- Membuat `backend/app/services/matching_service.py` (pure function) untuk mencocokkan baris wisuda ke batch SITASI aktif memakai exact NIM.
- Normalisasi NIM via `normalize_code`; build indeks NIM→record; ambil **seluruh** attempt; kelompokkan per (sertifikasi, sub_program) = satu ujian.
- Agregasi per ujian: jika ada attempt `LULUS`, bukti LULUS tetap disimpan dan tidak ditimpa attempt GAGAL. Semua attempt tetap dilacak.
- Cek kesamaan nama sebagai flag (`EXACT`/`PARTIAL`/`DIFFERENT`/`MISSING`), bukan kunci utama. NIM tetap dasar matching.
- Status per ujian: LULUS→`PERLU_VERIFIKASI` (butuh Certiport untuk VALID), semua gagal→`TIDAK_LULUS`, ada PENDING→`PENDING`, tidak dikenal→`PERLU_VERIFIKASI`. Overall mengikuti prioritas PERLU_VERIFIKASI > PENDING > TIDAK_LULUS.
- **Tidak** menyimpulkan syarat kelulusan wisuda. **Tidak** membuat Certiport matching atau export dalam tahap ini.
- Evidence per hasil: source (`SITASI`), id record, source_row, nilai, status, import_id, dan reason.
- Helper `fetch_active_sitasi_rows` memuat seluruh batch SITASI aktif via pagination (bukan pure).
- Test: 21 kasus cakupan — satu NIM banyak attempt, semua gagal, pending, tidak ditemukan, nama berbeda, sertifikasi campuran (MOS/MCF/MTCNA), LULUS tidak tertimpa GAGAL, normalisasi NIM float/string, evidence lengkap, tidak menyimpulkan kelulusan.
- Bukti: `rtk venv/Scripts/python.exe -m pytest tests/test_matching_service.py -v` — 21 PASS; `rtk venv/Scripts/python.exe -m pytest tests -q` — 55 PASS (34 existing + 21 baru); `git diff --check` PASS.

## 2026-10-03 — Tahap 09: Matching SITASI↔Certiport (cross-validation)

- Menambahkan `rapidfuzz==3.13.0` ke `requirements.txt` untuk pencarian kandidat nama fuzzy.
- Menambahkan konfigurasi alias ujian DRAFT (`EXAM_ALIAS_DRAFT`) di `matching_service.py` sesuai ADR-005; alias berstatus DRAFT dan tidak pernah menghasilkan `VALID` otomatis.
- Fungsi baru di `matching_service.py`: `fetch_active_certiport_rows`, `build_certiport_name_index`, `_find_certiport_candidates_fuzzy`, `_is_exam_alias_match`, `_cross_validate_exam`, `match_sitasi_to_certiport`, `_compute_combined_overall`.
- Alur: (1) cari kandidat Certiport via nama normalized, (2) cek keunikan kandidat (banyak nama berbeda → PERLU_VERIFIKASI), (3) hanya exact name yang dilanjutkan ke validasi ujian, (4) cocokkan kategori (MOS↔Microsoft Office Specialist, MCF↔Microsoft Certified Fundamentals), (5) cocokkan sub_program↔certification_name via alias, (6) cross-validate result SITASI vs Certiport per matriks §6 business rules.
- Matriks validasi: SITASI LULUS + Certiport PASS + alias exact → `VALID`; alias DRAFT → `PERLU_VERIFIKASI`; sumber konflik → `PERLU_VERIFIKASI`; keduanya gagal → `TIDAK_LULUS`; SITASI PENDING → `PENDING`; Certiport INCO → `PERLU_VERIFIKASI`.
- RapidFuzz hanya menyarankan kandidat dengan skor dan alasan; kandidat fuzzy (non-exact) tidak pernah auto-valid.
- Test baru di `tests/test_certiport_matching.py`: 24 kasus — alias exact/draft/reverse/no-match, Azure alias, name index, fuzzy threshold, happy path VALID, draft alias forces PERLU_VERIFIKASI, same-name ambiguity, same person multiple records, cross-program mismatch, SITASI LULUS + Certiport FAIL, SITASI gagal + Certiport PASS, both fail, no certiport data, no SITASI match skipped, fuzzy only, multiple exams mixed, all exams valid, SITASI pending, Certiport INCO, evidence detail.
- Bukti: `pytest tests/test_certiport_matching.py -v` — 24 PASS; `pytest tests -q` — 79 PASS; `git diff --check` — PASS (hanya warning CRLF Windows).

## 2026-10-03 — Tahap 10: Validation engine (per-program summary, reason codes, review flags)

- Menambahkan `REASON_CODES` (R01–R13) di `matching_service.py` untuk mengidentifikasi penyebab status secara deterministik.
- Menambahkan helper `_classify_reason_code` dan `_build_program_summary`: mengelompokkan hasil per program (`MOS`, `MCF`, dll.), menghitung status program secara independen tanpa saling menimpa, mempertahankan detail per ujian (`sub_program`, `combined_status`, `reason_code`, `has_lulus`, `certiport_evidence`, `sitasi_attempt_count`).
- Menambahkan fungsi top-level `validate_wisuda_complete`: pipeline end-to-end (Wisuda → SITASI → Certiport → Program Summary), menyimpulkan `mos_status`, `mcf_status`, `validation_status`, `reason_codes`, `needs_review` (bool), dan `review_flags` (daftar alasan review).
- Flag review otomatis menyala jika: ada ujian bukan VALID, nama tidak cocok persis (`name_match` DIFFERENT/PARTIAL), kandidat Certiport nama ganda, atau kandidat hanya fuzzy match.
- Test baru di `tests/test_validation_engine.py`: 22 kasus mencakup 9 baris matriks validasi §6 business rules (SITASI LULUS + Certiport PASS, no Certiport candidate, both fail, no SITASI LULUS + Certiport PASS, SITASI pending, multiple name candidates, exam mismatch, no SITASI NIM, Certiport INCO), pemisahan MOS/MCF, exam_details structure, flag review nama/fuzzy, DRAFT alias pencegah VALID, reason code konflik, non-MOS program (MTCNA), input kosong, dan preservasi bukti.
- Bukti: `pytest tests/test_validation_engine.py -v` — 22 PASS; `pytest tests -q` — 101 PASS; `git diff --check` — PASS.

## 2026-10-03 — Tahap 11: Persistensi sesi sinkronisasi & preview API

- Membuat migration database `database/migrations/20261003120000_sync_sessions_and_results.sql` untuk tabel `sync_sessions`, `sync_results`, dan `sync_evidence` sesuai `docs/07_DATABASE_DESIGN.md` dengan constraint foreign key, indeks pencarian/filter, dan RLS deny-by-default (khusus `service_role`).
- Menambahkan fungsi parser baris wisuda `parse_wisuda_for_sync` di `backend/app/services/wisuda_validation_service.py` untuk mengekstrak baris mahasiswa dan memvalidasi keutuhan data (menolak formula, duplikat NIM, dan nilai kosong).
- Menambahkan service sinkronisasi `backend/app/services/sync_service.py`:
  - `create_and_execute_sync`: proses sinkron sederhana dan deterministik tanpa ketergantungan async queue; mencatat snapshot `sitasi_import_id` dan `certiport_import_id`; status bertahap `PROCESSING` -> `COMPLETED`/`FAILED`; menghitung agregat `total_valid`, `total_review`, `total_not_found`; menyimpan per baris ke `sync_results` dan bukti ke `sync_evidence`.
  - Penanganan error: jika terjadi kegagalan di tengah proses, status sesi diubah menjadi `FAILED` dengan pesan error aman.
  - Dukungan retry: pengulangan sinkronisasi dengan file yang sama membuat sesi baru tanpa merusak histori sesi lama.
  - Konsistensi historis: sesi lama tetap mereferensikan batch snapshot aslinya walaupun ada batch master baru diaktifkan di kemudian hari.
  - Query helper dengan paginasi, filter status/needs_review, dan pencarian: `list_sync_sessions`, `get_sync_session`, `list_sync_results`, `get_sync_result_detail`.
- Mengimplementasikan endpoint RESTful di `backend/app/api/v1/endpoints/sync.py`:
  - `POST /api/v1/sync`: upload dan eksekusi sinkronisasi (HTTP 201).
  - `GET /api/v1/sync`: riwayat sesi sinkronisasi dengan paginasi.
  - `GET /api/v1/sync/{session_id}`: ringkasan satu sesi (HTTP 404 jika tidak ditemukan).
  - `GET /api/v1/sync/{session_id}/results`: daftar hasil per baris dengan filter status, pencarian, dan paginasi.
  - `GET /api/v1/sync/{session_id}/results/{result_id}`: detail satu baris hasil dan seluruh bukti dari SITASI/Certiport.
- Menambahkan pengujian di `tests/test_sync_service.py` (7 test) dan `tests/test_sync_api.py` (8 test) mencakup: alur sukses, penolakan saat batch aktif belum lengkap, kegagalan di tengah proses (status FAILED), retry setelah gagal, konsistensi snapshot historis saat batch baru aktif, paginasi dan filter hasil, detail evidence, serta perlindungan autentikasi `require_staff`.
- Bukti: `pytest tests/test_sync_service.py` — 7 PASS; `pytest tests/test_sync_api.py` — 8 PASS; `pytest tests -q` — 116 PASS; `git diff --check` — PASS.

## 2026-10-03 — Tahap 12: UI sinkronisasi, riwayat sesi, dan preview hasil

- Menambahkan tipe TypeScript dan API client helper untuk sinkronisasi di `frontend/lib/api.ts`: `SyncSession`, `SyncResultItem`, `SyncEvidenceItem`, `SyncResultDetail`, `startSync`, `getSyncSessions`, `getSyncSession`, `getSyncResults`, dan `getSyncResultDetail`.
- Menambahkan tautan "Riwayat Sinkronisasi" (`/riwayat`) pada `frontend/components/sidebar-nav.tsx` dan shortcut navigasi langsung pada `frontend/app/(dashboard)/dashboard/page.tsx`.
- Memperbarui halaman `frontend/app/(dashboard)/sinkronisasi/page.tsx`:
  - Tombol aksi ganda: "Validasi file" (read-only inspeksi cepat) dan "Proses Sinkronisasi" (eksekusi pencocokan penuh).
  - Alur otomatis: setelah sinkronisasi selesai, sistem langsung mengarahkan ke halaman hasil sesi `/sinkronisasi/[id]`.
- Membuat halaman preview hasil sinkronisasi `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
  - Kartu KPI ringkasan: Total Mahasiswa, Valid, Perlu Verifikasi, dan Tidak Ditemukan.
  - Snapshot informasi batch SITASI dan Certiport yang aktif saat sesi dijalankan.
  - Filter status interaktif (`VALID`, `PERLU_VERIFIKASI`, `TIDAK_LULUS`, `PENDING`, `DATA_TIDAK_DITEMUKAN`) dan filter `Hanya Perlu Review`.
  - Formulir pencarian instan berdasarkan NIM atau Nama.
  - Tabel hasil sinkronisasi dengan pemisahan status MOS dan MCF, status keseluruhan, dan catatan review.
  - Dialog / modal rincian bukti verifikasi silang: menampilkan perbandingan identitas, nama SITASI jika ada perbedaan, dan rincian evidence per ujian (kategori, nama ujian, baris SITASI/Certiport, skor, dan alasan deterministik).
  - Paginasi tabel.
- Membuat halaman riwayat sesi `frontend/app/(dashboard)/riwayat/page.tsx`:
  - Tabel audit riwayat proses dengan waktu, nama file, snapshot batch SITASI & Certiport, total baris, badge status, ringkasan perolehan hasil, dan tautan langsung ke detail hasil.
- Bukti: `npm run typecheck` — PASS; `npm run build` — PASS (menghasilkan route `/riwayat`, `/sinkronisasi`, `/sinkronisasi/[id]`); seluruh 116 backend test — PASS; `git diff --check` — PASS.

## 2026-10-03 — Tahap 12: Review manual petugas & audit jejak keputusan (ADR-009)

- Membuat migration database `database/migrations/20261003130000_review_audit.sql` untuk tabel append-only `review_audit` sesuai `docs/07_DATABASE_DESIGN.md` dan ADR-009, menyimpan riwayat keputusan review (`KONFIRMASI_COCOK`, `TIDAK_COCOK`, `TUNDA_VERIFIKASI`), catatan wajib, identitas reviewer, serta transisi status sebelumnya ke status baru.
- Menambahkan fungsi review di `backend/app/services/sync_service.py`:
  - `submit_review`: memvalidasi keputusan sah, catatan wajib (non-empty), dan menerapkan kebijakan otorisasi ADR-009.
  - Otorisasi ADR-009: bila kebijakan penunjukan reviewer belum disahkan secara institusional (`ADR_009_REVIEWER_POLICY_APPROVED = False`), konfirmasi final (`KONFIRMASI_COCOK` menjadi `VALID`) dibatasi hanya bagi role `admin` / penanggung jawab resmi; staff biasa hanya diizinkan memilih `TUNDA_VERIFIKASI` atau `TIDAK_COCOK` (mode pending/read-only).
  - Preservasi data: keputusan review tidak pernah menghapus atau mengubah rekaman bukti asli di `sync_evidence`.
  - Review ganda: review bertahap secara aman mencatat setiap transisi ke `review_audit` dan memperbarui `review_note` serta ringkasan total sesi.
  - `get_review_history`: mengambil histori keputusan per baris.
- Mengimplementasikan endpoint API `PATCH /api/v1/sync/{session_id}/results/{result_id}/review` pada `backend/app/api/v1/endpoints/sync.py`.
- Memperbarui antarmuka modal detail hasil di `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
  - Formulir keputusan review petugas dengan pilihan status, textarea catatan wajib, dan info pembatasan wewenang ADR-009.
  - Bagian riwayat audit jejak keputusan (append-only) menampilkan seluruh riwayat review yang pernah dilakukan pada baris tersebut beserta nama petugas dan tanggal.
  - Pembaruan status instan pada tabel hasil tanpa reload halaman penuh.
- Menambahkan pengujian di `tests/test_review.py` (12 test): validasi input catatan kosong, keputusan tidak sah, proteksi akses tanpa token/izin, pembatasan staff pada `KONFIRMASI_COCOK` per ADR-009, konfirmasi admin, review bertahap ganda, dan preservasi bukti sumber asli.
- Bukti: `pytest tests/test_review.py` — 12 PASS; seluruh 128 backend test — PASS; `npm run typecheck` — PASS; `npm run build` — PASS; `git diff --check` — PASS.

## 2026-10-03 — Tahap 13: Gate keputusan bisnis sebelum ekspor (ADR-003/005/006/010/011)

- Menyusun dokumen gate keputusan bisnis resmi `docs/20_OUTPUT_MAPPING_APPROVAL.md` berisi tabel pertanyaan, opsi kebijakan, dan contoh keluaran anonim untuk:
  - Format isi kolom `Sertifikasi MOS` dan `Sertifikasi MCF` (ADR-003).
  - Mahasiswa dengan lebih dari satu ujian dalam satu kategori (ADR-003).
  - Perlakuan mahasiswa belum lulus, pending, atau perlu review (ADR-003/ADR-004).
  - Definisi dan pengisian kolom `Title Microsoft` (ADR-006).
  - Perlindungan sel target wisuda yang sudah terisi sebelumnya agar tidak ditimpa sembarangan (ADR-010).
  - Ekuivalensi alias ujian dan versi tahun produk (ADR-005).
  - Penegasan kriteria kewajiban sertifikasi per program studi (ADR-011) agar sistem tidak mengarang syarat kelulusan wisuda.
  - Template lembar tanda tangan pengesahan resmi ITCC dan akademik.
- Menerapkan penguncian ekspor administratif pada backend (`backend/app/services/sync_service.py` & `sync.py`):
  - Ekspor mode `final` DIBLOKIR (`403 Forbidden`) selama kebijakan belum disahkan secara tertulis.
  - Ekspor mode `draft` menghasilkan workbook `.xlsx` pratinjau dengan label eksplisit `[DRAFT]`, preservasi formula dan sheet asli, serta sheet tambahan `Ringkasan & Gate ADR` berisi metadata audit dan peringatan administratif.
- Memperbarui antarmuka pengguna `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
  - Tombol "Unduh Pratinjau Excel (DRAFT)" aktif untuk verifikasi internal.
  - Tombol "Unduh Excel Final Resmi" dinonaktifkan (disabled) dengan tooltip penjelasan merujuk ke dokumen pengesahan.
- Menambahkan pengujian di `tests/test_export_gate.py` (6 test): penolakan ekspor final 403, keberhasilan ekspor draft dengan watermark label DRAFT, verifikasi dua sheet, dan proteksi otorisasi petugas.
- Bukti: `pytest tests/test_export_gate.py` — 6 PASS; seluruh 134 backend test — PASS; `npm run typecheck` — PASS; `npm run build` — PASS; `git diff --check` — PASS.

(End of file)
