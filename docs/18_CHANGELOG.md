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

## 2026-10-09 — Tahap 14: Export Excel sesuai approval (ADR gate)

- Memastikan kepatuhan terhadap status lembar pengesahan `docs/20_OUTPUT_MAPPING_APPROVAL.md`.
- Karena tanda tangan resmi pimpinan ITCC belum tersedia, ekspor final secara ketat dihentikan (`STOP final export` / HTTP 403 Forbidden).
- Ekspor draft dengan OpenPyXL tetap beroperasi melayani pratinjau data dengan preservasi struktur baris dan kolom.
- Bukti: `pytest tests/test_export_gate.py` — 6 PASS; seluruh 134 backend test — PASS.

## 2026-10-09 — Tahap 15: Testing terintegrasi dan kualitas

- Melakukan pengujian terintegrasi komprehensif mengikuti `docs/10_TEST_PLAN.md` dan kriteria `docs/15_ACCEPTANCE.md`.
- Menjalankan 134 test backend (unit, integrasi, anomali payload, security) dengan hasil 100% PASS.
- Menjalankan Next.js typecheck (`tsc --noEmit`) dan production build (`next build`) dengan hasil 100% PASS tanpa error kompilasi.
- Menguji keamanan data: penolakan tanpa token (401), penolakan non-staf (403), sanitasi error database, pembatasan upload payload >10MB, dan penolakan workbook formula/makro.
- Menerbitkan dokumen laporan resmi `docs/21_TEST_RESULTS.md` memuat matriks 24 test case dan bukti eksekusi aktual.
- Bukti: `pytest tests -v` — 134 PASS; `npm run typecheck` — PASS; `npm run build` — PASS.

## 2026-10-09 — Tahap 16: Formulir UAT & persiapan serah terima

- Menyusun `docs/22_UAT_FORM.md`: 34 skenario UAT petugas (login, logout, kontrol akses, impor master, upload Wisuda, multi-attempt, konflik nama, verifikasi manual, ekspor, sesi lama) dengan kolom kasus, expected, actual, bukti screenshot disensor, keputusan petugas, dan tanggal.
- Menetapkan aturan data UAT: fixture sintetis anonim wajib; data asli hanya atas izin tertulis dan tidak di-commit/di-publikasikan.
- Menambahkan tinjauan kontrol akses, audit, kebijakan retensi/backup (ADR-007), performa aktual, pemetaan output yang disetujui (ADR-003/005/006/010/011), dan pemetaan ke checklist penerimaan `docs/15_ACCEPTANCE.md`.
- Menandai status **BELUM SIAP PRODUCTION** dan larangan deployment sampai UAT dijalankan, SQL/RLS tereksekusi, dan lembar pengesahan UAT ditandatangani.
- Bukti: `pytest tests -q` — 134 PASS (2.87 s); `npm run typecheck` — PASS. Skenario UAT browser BELUM DIJALANKAN (menunggu lingkungan Supabase development berizin).

## 2026-10-09 — Tahap 17: Runbook deployment dev/staging/production & tata kelola operasional

- Memperbarui `docs/17_OPERATIONS.md` menjadi runbook operasional dan arsitektur deployment resmi.
- Menetapkan pemisahan 3 lingkungan (Dev lokal, Staging VPN internal, Production internal kampus) dengan isolasi database dan private storage bucket.
- Mendefinisikan arsitektur hosting aman: Next.js Node container, FastAPI Python di balik reverse proxy Nginx (timeout 120s, upload 15MB buffering), serta Supabase RLS deny-all by default.
- Menetapkan tata kelola rahasia: larangan commit credential, penggunaan secret manager runtime, dan pemisahan service key server-only vs anon key publik.
- Mengatur pembatasan CORS ketat, sanitasi logging tanpa PII (tanpa NIM/nama mahasiswa mentah), automated daily backup PITR, snapshot pre-migration, skrip rollback database teruji, dan health monitoring (`GET /api/v1/health`).
- Menyusun protokol 5 langkah dry-run staging sebelum penerapan ke production.
- Menandai status deployment live: **TERBLOKIR** (menunggu instruksi tertulis pemilik, pengesahan ADR output mapping, dan UAT selesai). Tidak ada klaim URL live fiktif.

## 2026-10-09 — Tahap 18: Dokumentasi akhir & laporan magang

- Menyusun `docs/23_USER_MANUAL.md`: manual petugas untuk alur upload → review → export, termasuk pembatasan ekspor final dan penanganan masalah umum.
- Menyusun `docs/24_OPERATOR_GUIDE.md`: panduan import/batch atomik, prosedur backup & recovery, kontrol akses/audit, daftar library & versi aktual, serta 13 limitasi terbuka.
- Menyusun `docs/25_LAPORAN_MAGANG.md`: kerangka BAB I–V mengikuti `docs/13_REPORT_MAGANG.md`, matriks fitur→file kode→test→bukti→bagian laporan, status akhir, daftar keputusan yang memerlukan institusi, dan pernyataan kejujuran data.
- Menyinkronkan `docs/07_DATABASE_DESIGN.md` (ERD sesuai 8 tabel aktual + status implementasi) dan `docs/08_API_CONTRACT.md` (status endpoint aktual).
- Menyinkronkan `README.md` root dan indeks `docs/README.md` dengan status terkini.
- Tidak ada perubahan kode aplikasi; hanya dokumentasi. Bukti: `pytest -q` — 134 PASS; `npm run typecheck` — PASS. UAT runtime tetap BELUM DIJALANKAN.

## 2026-10-09 — Fitur: Registrasi akun petugas di halaman login & pencatatan di database

- Menambahkan tab/toggle "Masuk" dan "Daftar Akun" di halaman login (`frontend/app/login/page.tsx`).
- Menambahkan input nama lengkap, email, kata sandi, dan konfirmasi kata sandi di formulir registrasi.
- Mengintegrasikan registrasi melalui endpoint backend `POST /api/v1/auth/register` (`backend/app/api/v1/endpoints/auth.py`), yang secara aman membuat pengguna di Supabase Auth (auto-confirm) dan otomatis menyisipkan data profil di tabel `public.profiles` (`display_name`, `role = 'staff'`, `is_active = true`).
- Menambahkan fungsi API helper `registerStaff` di `frontend/lib/api.ts`.
- Menerapkan auto-login mulus sesudah pendaftaran berhasil ke sesi Supabase browser dan redirect langsung ke `/dashboard`.
- Menyediakan migrasi trigger database `database/migrations/20261009180000_handle_new_user_profile.sql` untuk memastikan integritas sinkronisasi `auth.users` ke `public.profiles`.
- Menambahkan 4 unit test di `backend/tests/test_auth.py` (registrasi sukses, penolakan email duplikat, validasi format email regex, dan validasi panjang password).
- Bukti: `pytest tests/test_auth.py` — 15 PASS; seluruh 138 test backend — PASS; `npm run typecheck` — PASS; `npm run build` — PASS.

## 2026-10-12 — Fitur: Landing page publik dan navbar masuk/daftar

- Mengubah root `frontend/app/page.tsx` dari pengalihan ke `/dashboard` menjadi landing page publik berbahasa Indonesia: hero, fitur utama, cara kerja, penjelasan status hasil, ajakan, dan footer.
- Menambahkan komponen `frontend/components/public-navbar.tsx`: navbar lengket dengan tautan bagian, tombol **Masuk** dan **Daftar**, serta menu seluler dengan atribut aksesibilitas (`aria-expanded`, `aria-controls`).
- Memisahkan formulir login ke `frontend/components/login-form.tsx` dan menjadikan `frontend/app/login/page.tsx` sebagai pembungkus server yang membaca `searchParams.mode`, sehingga `/login?mode=register` langsung membuka tab pendaftaran.
- Menambahkan tautan "Kembali ke beranda" pada halaman login.
- Status hasil di landing page hanya penjelasan aturan; angka contoh diberi keterangan "hanya ilustrasi" agar tidak diklaim sebagai hasil uji.
- Bukti: `npm run typecheck` — PASS.

## 2026-10-12 — Fitur: Implementasi Design System Google Stitch (Swiss Minimalism + Enterprise Utility)

- Mengadopsi secara menyeluruh 8 screen hasil rancangan Google Stitch (Project ID: `12724873765600380458`) ke dalam antarmuka aplikasi Next.js/Tailwind CSS:
  1. Login & Registrasi Petugas (`01_LOGIN_SCREEN.md` / `frontend/components/login-form.tsx`)
  2. Dashboard Ringkasan (`02_DASHBOARD_SCREEN.md` / `frontend/app/(dashboard)/dashboard/page.tsx`)
  3. Master SITASI (`03_SITASI_MASTER_SCREEN.md` / `frontend/components/master-data-page.tsx`)
  4. Master Certiport (`04_CERTIPORT_MASTER_SCREEN.md` / `frontend/components/master-data-page.tsx`)
  5. Upload & Validasi Wisuda (`05_WISUDA_UPLOAD_SCREEN.md` / `frontend/app/(dashboard)/sinkronisasi/page.tsx`)
  6. Hasil Sinkronisasi (`06_SYNC_RESULTS_SCREEN.md` / `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`)
  7. Panel Verifikasi Review ADR-009 (`07_RESULT_REVIEW_SCREEN.md` / `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`)
  8. Riwayat Sinkronisasi (`08_SYNC_HISTORY_SCREEN.md` / `frontend/app/(dashboard)/riwayat/page.tsx`)
- Mengonfigurasi token warna brand di `frontend/tailwind.config.ts`: latar `#F5F7F6`, permukaan `#FFFFFF`, teks utama `#172321`, teks sekunder `#66736F`, aksen primer `#0F766E`, aksen pekat `#0F4B46`, border halus `#DDE4E1`, dan active highlight `#ECFAF8`.
- Mengintegrasikan tipografi Google Fonts resmi `IBM Plex Sans` dan `IBM Plex Mono` via `next/font/google` di `frontend/app/layout.tsx`.
- Memperbarui layout shell (`frontend/app/(dashboard)/layout.tsx`) dan navigasi samping (`frontend/components/sidebar-nav.tsx`) dengan indikator border kiri 3px `#0F766E` dan pill badge aktif.
- Menjaga integritas kontrak API, validasi otorisasi staff, dan logika autentikasi Supabase tanpa mengubah backend logic.
- Bukti: `npm run typecheck` — PASS; `npm run build` — PASS (semua 8 route statis dan dinamis terkompilasi sukses tanpa error).

## 2026-10-12 — Aset brand: crop brand board menjadi aset terpakai di UI

- Menambahkan skrip `frontend/scripts/crop_brand_assets.py` yang memotong `asset.png` (brand board 1536×1024) menjadi aset brand siap pakai, lengkap dengan fungsi auto-trim latar putih, pemisahan baris menjadi item, dan pembuatan alpha untuk latar transparan.
- Aset hasil di `frontend/public/brand/`: `logo-full.png` (logo lengkap transparan), `logo-mark.png` (cap tanpa teks), `app-icon.png` (tile ikon 256×256 transparan), `hero-banner.png` (banner gelap bersih, label anotasi dihapus), serta lima ikon fitur `icon-sitasi.png`, `icon-certiport.png`, `icon-wisuda.png`, `icon-sinkronisasi.png`, `icon-laporan.png`.
- Menetapkan favicon via konvensi Next.js App Router: `frontend/app/icon.png` (dari tile favicon). Berkas `.ico` pihak ketiga yang gagal didekode Turbopack tidak dipakai.
- Menerapkan logo di `frontend/components/public-navbar.tsx` dan header `frontend/app/(dashboard)/layout.tsx` (menggantikan badge teks "W"), serta tile ikon di badge `frontend/components/login-form.tsx`.
- Menerapkan lima ikon fitur sebagai ikon modul di `frontend/components/sidebar-nav.tsx` (Ringkasan, Validasi Wisuda, Riwayat, Data SITASI, Data Certiport).
- Menampilkan `hero-banner.png` pada hero landing `frontend/app/page.tsx` (membentang dua kolom grid).
- Bukti: `npm run typecheck` — PASS; `npm run build` — PASS (`/icon.png` ter-generate); aset disajikan HTTP 200 oleh dev server (`/brand/*`, `/icon.png`).

## 2026-10-12 — UI/UX & Responsive Design (Penerapan Panduan /ui-ux-pro-max)

- Menyelesaikan masalah kekosongan layar (whitespace timpang) pada desktop/widescreen dan mengoptimalkan tata letak di seluruh ukuran layar (ponsel, tablet, laptop, dan monitor lebar).
- Membuat komponen shell baru `frontend/components/dashboard-shell.tsx`:
  - Sidebar desktop penuh (`lg:fixed`, 100vh) dengan brand header, navigasi link berikon, status sistem internal ITCC, serta kartu profil petugas & tombol keluar.
  - Mobile header dan drawer slide-over (`lg:hidden`) dengan tombol hamburger menu (touch target >= 44x44px), overlay backdrop blur, penutupan otomatis saat rute berubah atau tombol ESC ditekan.
  - Desktop topbar (`hidden lg:flex`) memuat breadcrumbs dinamis per rute halaman, badge status sistem, dan info petugas.
  - Main content container yang fleksibel (`max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 xl:px-10`), mengisi ruang layar secara proporsional dan tidak terjepit di kiri-atas.
- Memperbarui `frontend/components/logout-button.tsx` dengan varian `compact` dan `normal` berstandar touch target minimal 44pt serta ikon SVG bersih.
- Memperbaiki `frontend/app/(dashboard)/dashboard/page.tsx`:
  - Hero banner diperlebar dengan visual aksen teal enterprise, status pulse, dan tombol CTA langsung.
  - Mengatasi tampilan kotak error kosong saat server belum siap: kartu status batch SITASI dan Certiport tetap ditampilkan terstruktur dalam grid 2 kolom dengan opsi pengecekan ulang.
- Mengoptimalkan responsivitas pada modul Master Data (`frontend/components/master-data-page.tsx`), Validasi Wisuda (`frontend/app/(dashboard)/sinkronisasi/page.tsx`), Hasil Sinkronisasi (`frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`), dan Riwayat (`frontend/app/(dashboard)/riwayat/page.tsx`):
  - Grid metrik KPI adaptif (2 kolom di ponsel/tablet, 4 kolom di desktop).
  - Wrapper tabel `overflow-x-auto` dengan petunjuk geser horizontal di ponsel (`sm:hidden`).
  - Tombol aksi dengan touch target minimal 44pt.
- Bukti: `npm run typecheck` — PASS (0 errors); `npm run build` — PASS (semua 8 rute halaman terkompilasi sukses).

## 2026-10-12 — Skill: Instalasi skill anti-ai-slop

- Memasang skill `anti-ai-slop` dari repository `misbahsy/anti-ai-slop` ke `.agents/skills/anti-ai-slop/`.
- Memuat instruksi pembersihan tulisan AI slop ([SKILL.md](file:///c:/Users/LENOVO/Documents/Project/wisudasync/.agents/skills/anti-ai-slop/SKILL.md)), panduan referensi reviewer dan voice (`references/`), skrip verifikasi linter deterministik (`scripts/slopcheck.py`, `scripts/sanitize.py`, `scripts/grade.py`), serta test suites (`tests/`).
- Menguji skrip verifikasi: `python .agents/skills/anti-ai-slop/tests/test_slopcheck.py` — seluruh 26 pemeriksaan lulus (PASS).

## 2026-10-12 — Refinement UI/UX & De-slop Design (Penerapan ui-ux-pro-max + anti-ai-slop)

- Merapikan desain antarmuka dashboard agar bebas dari elemen AI slop (menghapus hero crypto/SaaS gelap berlebihan, kartu simetris tanpa data, dan kalimat pemasaran generik).
- Mengimplementasikan layout pusat operasional staf ITCC bergaya Swiss Utility:
  - Header operasional institusional dengan breadcrumb peran staf dan tombol aksi `+ Validasi Berkas Wisuda`.
  - Stepper alur kerja 4 tahap (Master SITASI -> Master Certiport -> Pencocokan Wisuda -> Review & Ekspor).
  - Kartu pemantauan status batch aktif SITASI dan Certiport dengan data baris terdata dan tombol akses langsung.
  - Tabel sesi sinkronisasi terbaru (`recent sessions`) terintegrasi langsung di dashboard dengan status badge semantik dan tautan detail.
  - Panel pedoman verifikasi operasional staf (aturan exact NIM, review manual ADR-009, dan kunci ekspor final ADR-003).
- Melakukan audit dan scrubbing draf dokumen laporan magang (`docs/25_LAPORAN_MAGANG.md`) menggunakan linter deterministik skill `anti-ai-slop`:
  - Menghapus 23 tanda em-dash (`—`), 21 format dekoratif bold mid-sentence, mengubah heading menjadi sentence-case, dan merapikan kalimat stub.
  - Skor evaluasi `slopcheck.py` meningkat drastis dari 71.0/100 (C-, Gagal) menjadi 94.0/100 (Grade A, Lulus).
- Bukti pengujian:
  - `npm run typecheck` — PASS (0 errors).
  - `npm run build` — PASS (10 rute Next.js terkompilasi optimal).
  - `pytest -q` backend — 140 PASS (2.63 s).
  - `slopcheck.py docs/25_LAPORAN_MAGANG.md` — Score: 94.0/100 (Grade A, PASS).

## 2026-10-12 — Perbaikan impor Certiport: kolom `Full Name` berformula CONCATENATE

- Memperbaiki `backend/app/services/import_service.py`: penolakan formula dipersempit ke **kolom wajib saja** (sebelumnya menolak formula di seluruh workbook), sesuai aturan yang didokumentasikan. Pemeriksaan dilakukan pada sheet target, bukan semua sheet.
- Menambahkan pengecualian kolom `Full Name` Certiport yang lazim berupa formula `=CONCATENATE(...)` pada ekspor resmi: nilainya dibaca dari cache; bila cache tidak tersedia, diturunkan dari `First Name` + `Last Name`.
- Memperbaiki pemeriksaan sel pada mode read-only agar tidak gagal pada `EmptyCell` (memakai indeks kolom posisional).
- Menambahkan 2 test di `backend/tests/test_import_service.py`: `test_certiport_accepts_full_name_formula_and_derives_from_first_last` dan `test_certiport_rejects_formula_in_required_column`.
- Menyelaraskan `docs/08_API_CONTRACT.md`, `docs/23_USER_MANUAL.md`, dan `docs/24_OPERATOR_GUIDE.md` dengan aturan baru.
- Bukti: `pytest tests -q` — 140 PASS; `data_certiport.xlsx` asli berhasil di-parse (4047 baris).

## 2026-10-12 — Peningkatan Engine Matching: Pengecekan Langsung Wisuda ke Certiport & SITASI

- Memperbaiki alur pencocokan data wisuda agar tidak hanya bertumpu pada data SITASI sebagai prasyarat tunggal:
  - Sistem kini mengecek identitas mahasiswa secara langsung ke **kedua sumber paralel**: exact NIM di SITASI dan nama ternormalisasi di Certiport.
  - Menghapus pembatasan `SKIPPED` pada Certiport jika NIM tidak ditemukan di SITASI. Jika mahasiswa belum tercatat di SITASI tetapi memiliki sertifikat resmi di Certiport (PASS), rekaman Certiport tetap dibaca, dicatat sebagai bukti verifikasi, dan dikelompokkan ke program terkait (MOS/MCF) berstatus `PERLU_VERIFIKASI` dengan kode alasan `R14_CERTIPORT_ONLY`.
  - Mengimplementasikan pembacaan ujian menyeluruh: jika mahasiswa memiliki ujian tambahan di Certiport yang belum terdata di SITASI (misal mengambil Excel dan PowerPoint padahal di SITASI hanya Word), rekaman Certiport tersebut tetap dibaca dan disajikan kepada petugas verifikator.
  - Kasus benar-benar tidak ada di kedua sumber baru diklasifikasikan sebagai `DATA_TIDAK_DITEMUKAN`.
- Menambahkan penanganan kanonikal nama sertifikasi (`_canonical_exam_name`) dan pemetaan kategori Certiport yang lebih tangguh (`_map_category_reverse`).
- Menambahkan 4 unit test baru di `backend/tests/test_certiport_matching.py` dan `test_validation_engine.py` untuk memverifikasi pembacaan langsung Certiport tanpa rekaman SITASI serta pembacaan ujian ganda Certiport.
- Bukti: `pytest -q` — 144 PASS (0 failed, 2.60 s); `npm run typecheck` — PASS; `npm run build` — PASS.

## 2026-10-12 — Penyajian Skor Ujian SITASI/Certiport & Seleksi Multi-Attempt Lulus

- Memperbarui `backend/app/services/matching_service.py`:
  - Menambahkan konversi skor numerik yang aman (`_parse_numeric_score`).
  - Mengembangkan logika agregasi multi-attempt (`_aggregate_exam_attempts`):
    - Jika mahasiswa memiliki 2+ percobaan dan ada yang LULUS: sistem memprioritaskan dan memilih attempt LULUS dengan skor tertinggi.
    - Jika hanya ada 1 percobaan dan belum lulus (atau seluruh attempt gagal): sistem tetap mencatat attempt tersebut dan mempertahankan skor terbaik yang diraih.
  - Memperkaya ringkasan program sertifikasi (`_build_program_summary` dan `validate_wisuda_complete`) dengan skor program (`score`, `scores` per sub-ujian, `mos_score`, dan `mcf_score`).
- Memperbarui `backend/app/services/sync_service.py`:
  - Menyimpan nilai skor efektif (`match_score`) pada tabel `sync_evidence` baik bersumber dari SITASI maupun Certiport.
- Mengembangkan antarmuka `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
  - Menambahkan fungsi pembantu visualisasi `formatScoreBadges` berstandar Swiss Utility yang bersih dan bebas AI slop.
  - Menampilkan badge skor ujian pada kolom **Status MOS** dan **Status MCF** di tabel hasil verifikasi secara rapi dan selaras.
  - Menambahkan kartu ringkasan evaluasi program MOS dan MCF lengkap dengan skor pada modal dialog detail verifikasi silang mahasiswa.
  - Memperjelas badge nilai ujian per sub-program pada daftar bukti sumber.
- Menambahkan 3 unit test komprehensif di `backend/tests/test_validation_engine.py`:
  - `test_multi_attempt_picks_passing_attempt_with_highest_score`
  - `test_single_attempt_not_passing_preserves_score`
  - `test_all_attempts_failed_picks_highest_score`
- Bukti:
  - `pytest -q` backend — 147 PASS (1 warning Starlette deprecation, 2.68 s).
  - `npm run typecheck` — PASS (0 errors).
  - `npm run build` — PASS (semua 10 rute Next.js terkompilasi optimal).

## 2026-10-13 — Penyajian Ganda Nama & Skor Mahasiswa (SITASI dan Certiport) pada Detail Verifikasi

- Memperbarui `backend/app/services/matching_service.py`:
  - Memperkaya `exam_details` pada `_build_program_summary` dengan atribut sumber `sitasi_name`, `sitasi_status`, `certiport_name`, dan `certiport_status`.
  - Menyertakan `sitasi_name` dan `certiport_name` pada ringkasan program sertifikasi (`summary[program]`).
- Memperbarui `backend/app/services/sync_service.py`:
  - Memperkaya respon `get_sync_result_detail` agar setiap item di `evidence` memuat nama mahasiswa, skor, dan status kelulusan dari kedua basis data (SITASI dan Certiport).
- Memperbarui `frontend/lib/api.ts`:
  - Menambahkan definisi field `sitasi_name`, `sitasi_score`, `sitasi_status`, `certiport_name`, `certiport_score`, `certiport_status` pada tipe `SyncEvidenceItem`.
- Memperbarui `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
  - Merancang ulang tampilan modal detail bukti dengan tata letak grid dua kolom (*Swiss Enterprise Utility*):
    - Kolom kiri: **Basis Data SITASI (Exact NIM)** — menampilkan nama terdaftar, skor ujian, status attempt, dan nomor baris SITASI.
    - Kolom kanan: **Sertifikat Certiport (Pencocokan Nama)** — menampilkan nama lengkap terdaftar, skor ujian, hasil PASS/FAIL, dan nomor baris Certiport.
    - Menampilkan nama dan status kedua sumber pada kartu ringkasan program MOS dan MCF di modal.
- Menambahkan unit test di `backend/tests/test_validation_engine.py`:
  - `test_detail_contains_sitasi_and_certiport_names_and_scores` memvalidasi kelengkapan nama, skor, dan status kedua sumber.
- Bukti pengujian:
  - `pytest -q` backend — 148 PASS (0 failed, 1 warning, 2.84 s).
  - `npm run typecheck` — PASS (0 errors).
  - `npm run build` — PASS (semua 10 rute Next.js terkompilasi optimal).

## 2026-10-13 — Perbaikan Atribuasi Skor Sumber Certiport-Only pada Modal Detail

- Memperbaiki akar masalah di mana skor sertifikasi Certiport keliru ditampilkan di kolom "Basis Data SITASI" pada mahasiswa yang hanya memiliki rekaman Certiport:
  - `backend/app/services/matching_service.py`: Memastikan rekaman bertipe `certiport_only` tidak mengisi `sitasi_score`, `sitasi_name`, atau `sitasi_status` ke dalam `exam_details`.
  - `backend/app/services/sync_service.py`: Memperbaiki logika perkayan `evidence` di `get_sync_result_detail`. Jika `certiport_row_id` ada dan `sitasi_row_id` null, `match_score` diatribusikan ke `certiport_score` dan SITASI dinyatakan kosong.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`: Memperbaiki kondisi `hasSitasi` dan `hasCertiport` serta fallback skor agar kotak SITASI menampilkan *"Tidak ada rekaman attempt di data SITASI"*, dan kotak Certiport secara benar menampilkan Nama, Skor (misal 775), dan Hasil PASS.
- Bukti pengujian:
  - `pytest -q` backend — 148 PASS.
  - `npm run typecheck` — PASS.
  - `npm run build` — PASS.

## 2026-10-13 — Uji E2E browser (Playwright) & perbaikan bug CORS PATCH + nama file ekspor

- Menjalankan uji end-to-end memakai Playwright CLI + Chromium dengan akun petugas dummy dan berkas `data_*.xlsx` proyek (login, dashboard, validasi wisuda, sinkronisasi, review, ekspor, riwayat, logout, proteksi rute).
- **Bug kritis — keputusan review tidak dapat disimpan:** simpan review memakai `PATCH`, sedangkan CORS hanya mengizinkan `GET, POST, OPTIONS` sehingga preflight ditolak (`net::ERR_FAILED`). Diperbaiki di `backend/app/main.py` (`allow_methods` ditambah `PATCH`).
- **Nama berkas ekspor DRAFT berganda:** `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx` menambahkan `.xlsx` pada `file_name` yang sudah berekstensi → `wisuda_sync_draft_data_wisuda.xlsx.xlsx`. Kini ekstensi lama dibuang lebih dulu.
- Menambahkan test `test_cors_preflight_allows_patch_for_review` di `backend/tests/test_sync_api.py`.
- Klarifikasi: `needs_review=True` untuk baris `DATA_TIDAK_DITEMUKAN` **bukan bug** — perilaku ini disengaja dan diuji (`test_sync_service.py`, `test_validation_engine.py`), sehingga tidak diubah.
- Bukti: `pytest tests -q` — 149 PASS; `npm run typecheck` — PASS; `npm run build` — PASS; preflight `PATCH` pada instance berperbaikan → 200 (`access-control-allow-methods: GET, POST, PATCH, OPTIONS`); `PATCH` review → 200.

## 2026-10-13 — Tabel hasil sinkronisasi sesuai format Wisuda (No, Kode Prodi, Program Studi, MOS, MCF, Title)

- Mengubah tabel hasil sinkronisasi agar menyesuaikan struktur kolom di `data_wisuda.xlsx`: No, Kode Prodi, Program Studi, NIM, Nama, Sertifikasi MOS, Sertifikasi MCF (untuk prodi 31/32), dan Title Microsoft.
- Menambahkan kolom `kode_prodi` dan `program_studi` pada tabel `sync_results` via migration `20261013150000_sync_results_add_prodi.sql`.
- `backend/app/services/wisuda_validation_service.py`: `parse_wisuda_for_sync` kini mengekstrak kolom Kode Prodi dan Program Studi dari workbook wisuda.
- `backend/app/services/matching_service.py`: Meneruskan field `kode_prodi` dan `program_studi` dari wisuda rows ke result dict.
- `backend/app/services/sync_service.py`: Menyimpan `kode_prodi` dan `program_studi` ke `sync_results`. Mengisi kolom prodi pada export DRAFT.
- `frontend/lib/api.ts`: Menambah field `kode_prodi` dan `program_studi` pada tipe `SyncResultItem`.
- `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
  - Tabel menampilkan kolom No, Kode Prodi, Program Studi, NIM, Nama, Sertifikasi MOS, Sertifikasi MCF, Title Microsoft, dan Aksi.
  - Kolom MOS/MCF menampilkan status, skor dari SITASI (label `S:`), dan skor dari Certiport (label `C:`) secara terpisah.
  - Kolom MCF menampilkan N/A untuk prodi selain 31/32 (Informatika/Sistem Informasi).
  - Kolom Title Microsoft menampilkan Microsoft Office Specialist dan/atau Microsoft Certified: Fundamentals berdasarkan status lulus.
  - Status data tidak ditemukan dan perlu verifikasi ditampilkan di kolom Title Microsoft.
- Bukti: `pytest -q` — 149 PASS; `npm run typecheck` — PASS; `npm run build` — PASS (10 rute terkompilasi).

## 2026-10-13 — Master Data Pemetaan Kode NIM ke Program Studi (prodi_mapping.json)

- Membuat file master konfigurasi JSON pemetaan Kode NIM terhadap 19 Program Studi ITPLN (termasuk jenjang S2 dan Profesi sesuai `data_wisuda.xlsx`):
  - `backend/app/core/prodi_mapping.json`: Master data prodi untuk backend (19 program studi, daftar kode wajib MCF: 31 dan 32, mencakup kode 10 untuk S2 Teknik Elektro, 20/40 S2 Teknik Mesin, 30 S2 Ilmu Komputer, 80 Profesi Insinyur).
  - `frontend/lib/prodi_mapping.json`: Master data prodi untuk frontend UI.
- `backend/app/core/prodi.py`: Helper loader JSON, ekstraksi kode prodi langsung dari NIM (2 digit setelah 4 digit tahun angkatan, misal 202331243 -> '31', 202110039 -> '10'), lookup nama prodi resmi, dan pengecekan kelayakan MCF.
- `backend/app/services/wisuda_validation_service.py`: Auto-resolve `kode_prodi` dan `program_studi` dari NIM saat parsing data wisuda.
- `backend/app/services/matching_service.py`: Auto-resolve `kode_prodi` dan `program_studi` saat membangun hasil matching mahasiswa.
- `backend/app/services/sync_service.py`: Ekstraksi prodi dari NIM saat insert sync results, list results, get detail, dan export DRAFT Excel.
- `frontend/lib/prodi.ts`: Utilitas frontend `resolveKodeProdiFromNim` mengekstrak 2 digit setelah tahun angkatan di NIM, dan `getProgramStudiName` dengan dukungan fallback.
- `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`: Menggunakan ekstraksi prodi langsung dari NIM pada tabel dan menampilkan nama Program Studi pada modal rincian evaluasi mahasiswa.
- `backend/tests/test_prodi.py`: 4 unit test memverifikasi 19 program studi, ekstraksi NIM (202331243 -> 31 -> S1 Teknik Informatika, 202110039 -> 10 -> S2 Teknik Elektro).
- Bukti: `pytest tests -q` — 153 PASS; `npm run typecheck` — PASS; `npm run build` — PASS (10 rute Next.js terkompilasi optimal).

## 2026-10-13 — Perbaikan .gitignore (secret, log, artefak lokal)

- Melengkapi `.gitignore`: `frontend/.env` + `frontend/.env.local` (sebelumnya hanya `.env*.local`, file `frontend/.env` berisi URL Supabase nyaris ter-push), `*.xlsx`/`*.xls`/`data/`, `*.log`, `.playwright-cli/` (log + draft xlsx berisi data mahasiswa), `.commandcode/`, `.kilo/`, `asset.png`, `venv/`/`backend/.venv/`, `frontend/out|build`, `dist/`, `.turbo/`, coverage.
- Untrack 3 file `.pyc` (`__pycache__`) yang terlanjur ter-commit; aturan ignore `__pycache__`/`*.py[cod]` sudah ada.
- Yang tetap boleh di-push: `.env.example`, `database/*.sql`, `design/stitch-prompts/*`, `frontend/public/brand/*`, skill baru `.agents/skills/anti-ai-slop/*`, kode prodi baru.
- Bukti: `git check-ignore` cocok untuk `frontend/.env`, `backend/.env`, `data_*.xlsx`, `.pytest_cache`, `.playwright-cli/*`, `.commandcode/*`, `asset.png`, `*.log`; `git ls-files` tidak lagi memuat `.pyc`.

## 2026-10-13 — Revisi aturan pencocokan: SITASI cukup (NIM+nama) & fallback Certiport

- Menyesuaikan mesin `backend/app/services/matching_service.py` dengan ketentuan pemilik:
  - Cocok di SITASI hanya bila **NIM dan nama** sama (flag `sitasi_matched`). Bila cocok, status LULUS/TIDAK LULUS + skor dari SITASI **sudah cukup** (Certiport tidak wajib).
  - Bila tidak cocok di SITASI → cek Certiport berdasarkan nama; nama tepat & unik menentukan status (`PASS`→VALID, `FAIL`→TIDAK_LULUS).
  - Kandidat nama mirip memakai fuzzy **per kata** (`ratio`/`partial_ratio`/`token_sort_ratio`/`token_set_ratio`, ambang 85) dan ditampilkan sebagai saran pada catatan review; ambiguitas nyata dinilai dari skor ≥ 95.
  - Duplikat/tertimpa/konflik antar sumber → `PERLU_VERIFIKASI`.
  - `DATA_TIDAK_DITEMUKAN` hanya bila tidak ada di SITASI maupun Certiport.
  - MCF hanya dievaluasi untuk prodi relevan (`is_mcf_relevant`, kode `31`/`32`); di luar itu `mcf_status = null`.
- Menyesuaikan/menambah test: `test_validation_engine.py`, `test_certiport_matching.py` (kasus NIM+nama, SITASI cukup, fallback Certiport, saran nama mirip, gate MCF).
- Bukti: `pytest tests -q` — 157 PASS.

## 2026-10-14 — Pencocokan nama Certiport minimal 2 kata

- Mengubah rumus pencarian kandidat Certiport di `backend/app/services/matching_service.py`:
  - `_find_certiport_candidates_fuzzy` kini mensyaratkan nama berbagi **minimal 2 kata** (`NAME_MIN_MATCHING_WORDS`) dengan nama lengkap target; kandidat dengan kurang dari 2 kata cocok dibuang.
  - Ditambah helper `_name_word_tokens` dan `_count_matching_name_words` (kecocokan per kata toleran typo, ambang `NAME_WORD_MATCH_THRESHOLD = 85`), sehingga `DAVID GABRIEL SEMBIRING` cocok dengan `DAVID SEMBIRING`, `DAVID GABRIEL`, `GABRIEL SEMBIRING`, `GABRIEL DAVID`.
  - Nama target satu kata memakai batas `min(jumlah kata target, 2)` agar nama tunggal yang sah tetap dapat dicocokkan.
  - Kandidat yang tidak lolos batas kata → bukan kandidat → mengarah ke `DATA_TIDAK_DITEMUKAN`. Kandidat yang lolos tetap `PERLU_VERIFIKASI` (bukan auto-`VALID`).
  - Kandidat sekarang membawa field `matched_words` untuk transparansi review.
- Menambah regression test di `backend/tests/test_certiport_matching.py` (1 kata ditolak, 2 kata lolos berbagai urutan, nama target 1 kata, pipeline `DATA_TIDAK_DITEMUKAN`).
- Bukti: `pytest tests -q` — 161 PASS (4 test baru).

## 2026-10-14 — Nama satu kata tahan tanda baca/kurung (mis. "( DAVID.)")

- Menyesuaikan `backend/app/services/matching_service.py`:
  - `_get_nama_normalized` dan `build_certiport_name_index` selalu menormalkan ulang (idempoten) nilai `nama_normalized`/`full_name_normalized` yang tersimpan, sehingga data lama berhias tanda baca seperti `( DAVID.)` tetap setara `DAVID`.
  - `_name_word_tokens` menormalkan nama sebelum memecah token, agar token bebas tanda baca/kurung dan penghitung kata pada aturan minimal 2 kata tetap akurat.
- Menambah regression test `backend/tests/test_certiport_matching.py` (SITASI nilai tersimpan berhias → EXACT; index Certiport berhias → ternormalkan; kandidat nama target berhias).
- Bukti: `pytest tests -q` — 164 PASS (3 test baru).

## 2026-10-14 — Detail bukti: deduplikasi sub-ujian ganda + rujukan baris xlsx

- `backend/app/services/sync_service.py` (`get_sync_result_detail`):
  - `dedupe_evidence_for_display`: bukti ganda per (kategori, sub-ujian) — akibat kandidat fuzzy Certiport ganda — hanya menampilkan yang lulus (prioritas `VALID`/PASS/`LULUS`); sisanya tetap tersimpan, dicatat di `duplicate_count`/`duplicate_ids`. Status tidak diubah.
  - `attach_evidence_source_refs`: `sitasi_row_id`/`certiport_row_id` (id database) di-resolve ke `source_row` xlsx + `file_name` batch import (`sitasi_source_row`, `sitasi_file_name`, `certiport_source_row`, `certiport_file_name`); status/skor tampilan dikoreksi dari rekaman master (fallback lama salah melabeli record FAIL sebagai PASS).
- `frontend/lib/api.ts` + `sinkronisasi/[id]/page.tsx`: badge sumber menjadi `data_sitasi.xlsx · Baris #X` / `data_certiport.xlsx · Baris #Y` + catatan duplikat disembunyikan.
- Mock `MockQuery` mendukung `in_`; test baru: dedup prefer-PASS + resolve baris/file.
- Bukti: `pytest tests -q` — 166 PASS (2 test baru); `npm run typecheck` — PASS.

## 2026-10-19 — Pengesahan ADR-005 (Alias Ujian) & Perbaikan Sub-Program "Tidak Diketahui"

- Pengesahan resmi ADR-005 (Ekuivalensi Alias & Versi Ujian):
  - `docs/20_OUTPUT_MAPPING_APPROVAL.md`: Status ADR-005 diubah menjadi `DISETUJUI (APPROVED)`. Ekuivalensi ujian `Word` ~ `Word 2019` / `Microsoft Word 2019`, `Excel` ~ `Excel 2019`, dan `Azure AI-900` ~ `Microsoft Azure AI Fundamentals` disahkan resmi.
  - `docs/14_DECISIONS.md`: ADR-005 dicatat sebagai `DIPUTUSKAN (DISETUJUI)`.
  - `backend/app/services/matching_service.py`: `EXAM_ALIAS_STATUS` diset menjadi `"APPROVED"`. Mahasiswa yang lulus di SITASI dan lulus di Certiport dengan nama alias resmi kini otomatis berstatus `VALID` (`R01_VALID`) tanpa ditahan di `PERLU_VERIFIKASI`.
- Perbaikan penanganan sub-program pendaftaran awal "Tidak Diketahui" di `matching_service.py`:
  - Menambahkan `PLACEHOLDER_SUB_PROGRAMS = {"TIDAK DIKETAHUI", "UNKNOWN", "", "PENDAFTARAN", "BELUM UJIAN"}`.
  - Pada `_build_program_summary`, jika mahasiswa telah memiliki ujian konkret yang tuntas/lulus dalam satu program sertifikasi, rekaman pendaftaran awal berkode sub-program "Tidak Diketahui" dengan status `PENDING` tidak lagi menurunkan status kelulusan program menjadi `PENDING` atau memaksa review.
  - Kasus HENDRAWAN (`201911094`, Word LULUS skor 792) dan SYIFA ANANDA (`202111109`, Word LULUS skor 746) kini terverifikasi otomatis menjadi `VALID`.
- Pengujian & Validasi:
  - `backend/tests/test_certiport_matching.py`: Diperbarui untuk menguji alias berstatus APPROVED dan verifikasi status `VALID`.
  - `backend/tests/test_validation_engine.py`: Diperbarui dan ditambah unit test `test_placeholder_tidak_diketahui_pending_does_not_override_passed_exam`.
  - Bukti eksekusi suite test: `pytest tests -q` — 167 PASS (100% lulus, 0 fail).
  - Sinkronisasi live: Jumlah mahasiswa VALID naik signifikan dari 16 menjadi 39 pada batch data wisuda aktual.

## 2026-10-19 — Label Hasil Bahasa Manusia & Workbook Validasi Wisuda

- Tujuan: apresentam hasil validasi dengan label yang bisa dibaca petugas (Lulus / Tidak Lulus / Tidak Ada) tanpa menghilangkan status ambigu, sekaligus menyediakan pratinjau isi kolom `Sertifikasi MOS`, `Sertifikasi MCF`, dan `Title Microsoft` sesuai format Opsi 1A dan 4A ADR-003.
- `backend/app/services/matching_service.py`: menambah `STATUS_LABELS` dan `status_label()`. Pemetaan `VALID` → `Lulus`, `TIDAK_LULUS` → `Tidak Lulus`, `DATA_TIDAK_DITEMUKAN` → `Tidak Ada`, `PERLU_VERIFIKASI` → `Perlu Verifikasi`, `PENDING` → `Menunggu Hasil`. Status inti 5 nilai (AGENTS.md §4.5) tidak diubah; fungsi ini hanya lapisan tampilan. Status tak dikenal dikembalikan `-`, tidak ditebak menjadi kelulusan.
- `backend/scripts/generate_validation_workbook.py` (baru): generator workbook pratinjau dari tiga berkas lokal (`data_wisuda.xlsx`, `data_sitasi.xlsx`, `data_certiport.xlsx`). Memakai `validate_wisuda_complete` dari service resmi sehingga logika pencocokan identik dengan backend. Menghasilkan 10 sheet: Dashboard, Ringkasan Validasi, Pratinjau Kolom Wisuda, Detail Ujian, Detail SITASI, Detail Certiport, Kandidat Nama SITASI, Tidak Ditemukan, Rekap Prodi, Catatan & Metodologi. Self-check sebelum menyimpan berkas: jumlah baris hasil harus sama dengan baris wisuda dan seluruh label harus berada dalam daftar yang diizinkan.
- Sheet `Pratinjau Kolom Wisuda` (baru): kolom `No/Kode Prodi/Program Studi/NIM/Nama` disalin apa adanya; kolom target diisi `[DRAFT] MOS (Word 2019 - Lulus)`, `[DRAFT] MOS (Word 2019 - Tidak Lulus)`, `[DRAFT] MOS (Microsoft Azure AI Fundamentals - Lulus)`, atau `[DRAFT] Tidak Ada`. `Title Microsoft` memakai `MOS` / `MCF` / `MOS, MCF` / `—`. Nilai asli dari file wisuda ditampilkan pada kolom pembanding dan sel lama tidak ditimpa (ADR-010). MCF tidak dihitung di luar prodi kode 31 dan 32 (ADR-011).
- `backend/tests/test_matching_service.py`: 2 test baru untuk `status_label()` (5 status baku dan status tak dikenal).
- Bukti eksekusi: `pytest tests -q` — 169 PASS (167 lama + 2 baru). Generator dijalankan terhadap data aktual: `Lulus=39`, `Tidak Lulus=29`, `Perlu Verifikasi=81`, `Menunggu Hasil=1`, `Tidak Ada=274` dari 424 baris. Uji silang dengan 18 baris yang sudah punya teks `Sertifikasi MOS` manual pada `data_wisuda.xlsx`: 17 cocok, 1 berbeda (`202011018` dinilai `Perlu Verifikasi` karena NIM tidak ada di SITASI dan nama Certiport hanya mirip).
- Batasan: berkas keluaran berlabel DRAFT karena ADR-003, ADR-006, ADR-010, dan ADR-011 belum ditandatangani. Berkas `*.xlsx` sudah diabaikan `.gitignore` sehingga data asli tidak masuk repository.

## 2026-10-19 — Koreksi Keterangan Bukti Valid pada Sheet Detail

- Masalah: pada sheet `Detail Ujian`, 6 baris ujian menampilkan keterangan "SITASI LULUS tapi Certiport FAIL; konflik sumber" (`R04_CERTIPORT_NO_PASS`) padahal bukti Certiport untuk ujian yang sama juga memuat `PASS` dengan skor identik. Contoh: `202131039` (THIO OKTAVIANTO) — SITASI `Word LULUS` skor 850, Certiport `Word 2019` FAIL 486, FAIL 381, PASS 850. Keterangan lama menyesatkan petugas karena attempt FAIL adalah percobaan lama, bukan bukti akhir.
- Perbaikan (lapisan tampilan workbook, mesin pencocokan tidak diubah):
  - `backend/scripts/generate_validation_workbook.py`: menambah `corrected_reason()` yang mendeteksi pola LULUS + PASS + FAIL pada ujian yang sama, lalu menetapkan kode alasan `R01_VALID` dengan keterangan berbunyi "VALID: SITASI LULUS (skor X) dan Certiport PASS (skor Y) pada ujian yang sama; ada attempt FAIL sebelumnya sehingga status tetap Perlu Verifikasi sampai petugas memastikan attempt terakhir".
  - `corrected_row_codes()` menyelaraskan kode alasan tingkat baris di sheet `Ringkasan Validasi`; `corrected_valid_notes()` menambahkan penjelasan singkat pada kolom `Catatan Review` dan `Catatan Perbedaan` sheet pratinjau.
  - `certiport_status_for_exam()` memperbaiki kolom `Status Certiport` pada `Detail Ujian` yang sebelumnya menampilkan `-` walau Certiport mencatat PASS/FAIL. Nilai baru: `Lulus`, `Tidak Lulus`, `Lulus + ada FAIL sebelumnya`, `Tidak Ada`, dan awalan `(perlu konfirmasi)` bila status ujian masih `Perlu Verifikasi`.
- Status sengaja tidak dinaikkan: seluruh kolom status tetap `Perlu Verifikasi` untuk 6 baris tersebut karena petugas harus memastikan attempt terakhir (aturan §6 `docs/06_BUSINESS_RULES.md`). Sebaran status tidak berubah: `Lulus=39`, `Tidak Lulus=29`, `Perlu Verifikasi=81`, `Menunggu Hasil=1`, `Tidak Ada=274`.
- Bukti eksekusi: `pytest tests -q` — 169 PASS. Distribusi kode alasan `Detail Ujian` berubah dari `R01_VALID=83, R04_CERTIPORT_NO_PASS=5` menjadi `R01_VALID=89, R04_CERTIPORT_NO_PASS=0`; 6 baris terkoreksi adalah `202214003`, `201921053`, `202131039`, `202131073`, `202131135`, `202131155`.

## 2026-10-23 — Penyederhanaan Sistem: Admin-Only, Hapus Landing Page & Login/Register

- Permintaan: Menyederhanakan sistem menjadi inti validasi data, menghapus landing page (langsung ke validasi data), peran pengguna tunggal Admin (menghapus role staff), menghapus fitur login dan register, serta menyediakan SQL pembaruan siap copy-paste di Supabase.
- Perubahan Frontend:
  - `frontend/app/page.tsx`: Landing page dihapus, rute utama langsung mengalihkan ke `/sinkronisasi`.
  - `frontend/app/(dashboard)/layout.tsx`: Pengecekan auth guard `verifyStaffRoute` dihapus.
  - `frontend/proxy.ts`: Disederhanakan untuk meneruskan permintaan dan mengalihkan `/login` ke `/sinkronisasi`.
  - `frontend/lib/api.ts`: Fungsi `authorizedHeaders()` tidak lagi mewajibkan token sesi login.
  - `frontend/components/dashboard-shell.tsx`: Identitas sidebar diubah menjadi Administrator ITCC (Admin) dan tombol Logout dihapus.
  - `frontend/components/sidebar-nav.tsx`: Menu "Validasi Wisuda" ditempatkan di posisi teratas sebagai fitur utama.
  - `frontend/app/login/page.tsx` & `frontend/app/unauthorized/page.tsx`: Dialihkan ke `/sinkronisasi`.
- Perubahan Backend:
  - `backend/app/core/auth.py`: `require_staff` secara default mengembalikan identitas Administrator (role: admin) tanpa mewajibkan bearer token.
  - `backend/app/api/v1/endpoints/auth.py`: `/auth/me` mengembalikan profil Admin; `/auth/register` dinonaktifkan.
  - `backend/app/services/sync_service.py`: Default reviewer role menjadi `"admin"` sehingga konfirmasi cocok review tidak diblokir ADR-009.
  - `backend/tests/`: Seluruh unit test disesuaikan dengan arsitektur admin-only (158 test lulus).
- Pembaruan Database / Supabase:
  - `database/UPDATE_SIMPLIFY_ADMIN_ONLY.sql`: Skrip SQL migrasi siap pakai di Supabase SQL Editor.
  - `database/SETUP_ALL_TABLES.sql`: Skrip setup master diperbarui dengan constraint `role in ('admin')` dan profil default.
- Bukti Pengujian:
  - Backend: `venv/Scripts/python.exe -m pytest tests -q` — 158 PASS.
  - Frontend: `npm run typecheck` — PASS; `npm run build` — PASS.

## 2026-10-23 — Skema ringkas SITASI/Certiport + auto-isi Wisuda LULUS

- **Keputusan bisnis:** pemilik project menyetujui ADR-003/006/010/011. Hanya status LULUS yang mengisi kolom; format `MOS (Lulus)` / `MCF (Lulus)`; Title `MOS`, `MCF`, atau `MOS, MCF`; MCF hanya prodi 31/32; berkas keluaran baru.
- **Perubahan kode:**
  - `backend/app/services/import_service.py`: header wajib SITASI menjadi `NIM, Nama, Sertifikasi, Nilai, Status`; Certiport `Nama, Sertifikasi, Nilai, Status`; fallback skema lama Certiport; pemetaan `LULUS`→`PASS` dan `GAGAL`→`FAIL`; `program_name` diturunkan dari kategori.
  - `backend/app/services/matching_service.py`: NIM exact sebagai identitas SITASI; nama hanya peringatan; exact name Certiport menang atas kandidat fuzzy; cocok ujian per kategori saat sub-program kosong; helper `build_wisuda_fill_values`; kunci record Certiport aman untuk mode tanpa id database.
  - `backend/app/services/sync_service.py`: ekspor final aktif dan hanya mengisi status VALID; draft tetap berlabel; workbook delapan kolom Wisuda.
  - `backend/scripts/generate_validation_workbook.py`: ditulis ulang; memakai parser & mesin resmi; menghasilkan `hasil_wisuda_terisi.xlsx` tanpa menimpa `data_wisuda.xlsx`.
  - `frontend/components/master-data-page.tsx`, `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`, `frontend/lib/api.ts`: kolom master baru, tombol ekspor final aktif, Title memakai label MOS/MCF.
- **Tes:** `pytest tests -q` — 165 PASS; generator lokal dijalankan pada data asli: MOS lulus 67, MCF lulus 38, 80 baris terisi.

## 2026-10-23 — Perbaikan Perubahan Status Hasil Review Manual pada Modal Detail

- **Masalah:** Saat tombol Detail ditekan dan petugas menyimpan keputusan review manual (`KONFIRMASI_COCOK` / `TIDAK_COCOK`):
  1. `mos_status` dan `mcf_status` tidak diperbarui di backend (hanya `validation_status` yang di-update).
  2. Sub-ujian `sync_evidence` tetap berstatus `PERLU_VERIFIKASI`.
  3. Tabel utama di latar belakang modal tetap menampilkan badge kuning `PERLU VERIFIKASI` dan Title Microsoft tetap kosong (`—`).
  4. Ekspor Excel final tidak mengisi kolom sertifikasi untuk mahasiswa yang telah dikonfirmasi sah.
- **Perbaikan:**
  - `backend/app/services/sync_service.py` (`submit_review`): Memperbarui `validation_status`, `mos_status`, `mcf_status`, `mos_programs`, `mcf_programs`, serta `evidence_status` pada `sync_evidence`. Menambahkan parameter opsional `target_program` (`ALL`, `MOS`, `MCF`).
  - `backend/app/api/v1/endpoints/sync.py`: Menambahkan field `target_program` pada schema `ReviewDecisionRequest` dan meneruskannya ke `submit_review`.
  - `backend/tests/test_review.py`: Menambahkan tes unit untuk transisi status MOS/MCF dan pembaruan `sync_evidence` (14 unit test lulus).
  - `frontend/lib/api.ts`: Memperbarui `submitReviewResult` untuk mendukung pengiriman `targetProgram`.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
    - Memperbarui `openDetailModal` agar secara cerdas menentukan pilihan default review berdasarkan kondisi terkini mahasiswa.
    - Menambahkan pemilih `targetProgram` untuk prodi yang mewajibkan MCF.
    - Memperbarui `handleReviewSubmit` agar langsung memperbarui seluruh field baris tabel (`mos_status`, `mcf_status`, `validation_status`, `needs_review`) dan modal secara sinkron tanpa reload.
- **Pengujian:**
  - Backend: `pytest tests -q` — 167 PASS.
  - Frontend: `npm run typecheck` — PASS (0 errors); `npm run build` — PASS (0 errors).


## 2026-10-23 — Perbaikan false positive identitas Certiport

- **Masalah:** `MUHAMMAD ALFARISY AKBAR` (NIM 202310129) menampilkan `MUHAMMAD AKBAR` sebagai pemilik skor MOS/MCF. Kandidat fuzzy dipakai sebagai evidence dan exam.
- **Perbaikan:**
  - `backend/app/services/matching_service.py`: identitas Certiport hanya exact seluruh token (urutan/gelar boleh beda); kandidat parsial/fuzzy tidak dipakai sebagai evidence/skor; skor fuzzy memakai cakupan token (`partial_name_candidate`, contoh 67); deteksi konflik NIM; kode alasan `R15_CANDIDATE_ONLY` dan `R16_NIM_CONFLICT`; audit kandidat berisi nama asli, normalisasi, skor, file, baris, status.
  - `backend/app/services/import_service.py`: tolak NIM/Nama/Sertifikasi kosong pada SITASI dan Nama/Sertifikasi kosong pada Certiport.
  - `backend/app/services/sync_service.py`: kirim nama file batch Certiport untuk audit; `name_match_type` menandai `CERTIPORT_EXACT`, `CERTIPORT_CANDIDATE_ONLY`, atau `TIDAK_ADA_IDENTITAS`.
  - `backend/scripts/generate_validation_workbook.py`: meneruskan nama file Certiport.
  - Test: `test_validation_engine.py`, `test_certiport_matching.py`, `test_import_service.py`.
- **Bukti:** `pytest tests -q` — 177 PASS. Kasus nyata NIM 202310129: `PERLU_VERIFIKASI`, `mos_status=DATA_TIDAK_DITEMUKAN`, tanpa exam/evidence, kandidat `Muhammad Akbar` skor 67.

## 2026-10-26 — Pengecekan Sertifikasi MTCNA untuk Prodi 31 & 32 & Penyesuaian Kolom Title

- **Kebutuhan bisnis:**
  - Mahasiswa dengan kode jurusan `31` (S1 Teknik Informatika) dan `32` (S1 Sistem Informasi) dapat memilih salah satu antara sertifikasi MCF atau MTCNA.
  - Pengecekan MTCNA tidak perlu ke Certiport (MTCNA adalah sertifikasi MikroTik), cukup melalui data SITASI.
  - Kolom pada file Wisuda diselaraskan menjadi `Sertifikasi MCF/MTCNA` (dengan dukungan mundur terhadap `Sertifikasi MCF`).
  - Kolom `Sertifikasi MCF/MTCNA` diisi otomatis sesuai sertifikasi yang diambil dan lulus: `MCF (Lulus)`, `MTCNA (Lulus)`, atau keduanya jika mahasiswa lulus keduanya.
  - Kolom yang sebelumnya `Title Microsoft` disederhanakan menjadi `Title` saja.
  - Gelar `MTCNA` dimasukkan ke dalam kolom `Title` jika mahasiswa lulus MTCNA (contoh: "MOS, MTCNA", "MOS, MCF, MTCNA", atau "MTCNA").
- **Perubahan kode:**
  - `backend/app/services/wisuda_validation_service.py`: Template `WISUDA_COLUMNS` memakai `Sertifikasi MCF/MTCNA` dan `Title`. `layout_matches_template` memvalidasi baik template baru (`Title`) maupun template legasi (`Title Microsoft`, `Sertifikasi MCF`).
  - `backend/app/services/matching_service.py`:
    - `_cross_validate_exam`: Pengecekan sertifikasi MTCNA langsung tervalidasi dari data SITASI tanpa mencari rekaman Certiport (`certiport_status=None`, alasan *"Sertifikasi MTCNA diverifikasi langsung melalui data SITASI"*).
    - `_certiport_only_validation`: Menyetel status Certiport menjadi `None` untuk ujian MTCNA.
    - `_build_program_summary`: Menyimpan atribut `sertifikasi` pada tiap entri `exam_details`.
    - `validate_wisuda_complete`: Untuk prodi 31 & 32, menggabungkan evaluasi MCF dan MTCNA. Jika mahasiswa lulus salah satu (MCF atau MTCNA), status kelulusan syarat sertifikasi kedua terpenuhi (`VALID`).
    - `build_wisuda_fill_values`: Menerima parameter `mcf_programs` untuk menentukan teks isian kolom wisuda (`MCF (Lulus)` vs `MTCNA (Lulus)`), menambahkan `TITLE_MTCNA = "MTCNA"` ke daftar `Title` jika lulus MTCNA.
  - `backend/app/services/sync_service.py`: Memetakan `mcf_programs` dari `MCF_COMBINED`, `MCF`, atau `MTCNA`; memperbarui header ekspor menjadi `Sertifikasi MCF/MTCNA` dan `Title`; meneruskan `mcf_programs` ke `build_wisuda_fill_values`.
  - `backend/scripts/generate_validation_workbook.py`: Mendukung kolom target `Sertifikasi MCF/MTCNA`, resolusi `Title` / `Title Microsoft`, dan resolusi `mcf_programs`.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
    - Mengubah header tabel menjadi `Sertifikasi MCF/MTCNA` dan `Title`.
    - Memperbarui `renderTitleMicrosoft` untuk menyertakan `MTCNA` ke dalam array title jika mahasiswa lulus MTCNA.
    - Menyesuaikan label pada modal rincian evaluasi dan opsi filter review manual.
  - `backend/tests/test_validation_engine.py`: Menambahkan 5 kasus uji baru untuk verifikasi MTCNA dan assert title MTCNA.
  - `backend/tests/test_export_gate.py`: Memperbarui assertion header ekspor ke `("Sertifikasi MOS", "Sertifikasi MCF/MTCNA", "Title")`.
- **Pengujian:**
  - Backend: `.\venv\Scripts\python.exe -m pytest tests -q` — 182 PASS (100% passed).
  - Frontend: `npm run typecheck` — PASS (0 errors).

## 2026-10-26 — Perbaikan Filter Status Hasil Sinkronisasi & Interaktivitas KPI Cards

- **Kebutuhan bisnis & UX:**
  - Filter status di halaman hasil sinkronisasi (`/sinkronisasi/[id]`) diselaraskan hanya untuk status hasil sinkronisasi (`VALID`, `PERLU_VERIFIKASI`, `DATA_TIDAK_DITEMUKAN`).
  - Menghapus opsi dropdown yang membingungkan (`TIDAK LULUS`, `PENDING`) serta checkbox `Hanya Perlu Review` yang sebelumnya bentrok saat memfilter baris `VALID`.
  - Kartu KPI ringkasan (Total Mahasiswa, Valid, Perlu Verifikasi, Tidak Ditemukan) dibuat interaktif sehingga dapat diklik sebagai jalan pintas filter langsung dengan indikator status aktif.
  - Menampilkan badge indikator status hasil pada kolom nama mahasiswa di tabel agar status verifikasi langsung terlihat jelas.
- **Perubahan kode:**
  - `backend/app/services/sync_service.py` (`list_sync_results`): Memperluas filter `status="PERLU_VERIFIKASI"` agar mencakup seluruh baris berstatus `PERLU_VERIFIKASI` maupun `TIDAK_LULUS` sehingga konsisten dengan metrik `session.total_review`.
  - `backend/tests/test_sync_service.py`: Menambahkan kasus uji filter `status="PERLU_VERIFIKASI"`.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
    - Menghubungkan kartu KPI sebagai tombol filter interaktif dengan highlight ring aktif.
    - Menyelaraskan select dropdown `filter-status` dengan jumlah hitungan per status dan tombol reset status.
    - Menampilkan badge "Perlu Verifikasi" dan "Tidak Ditemukan" pada kolom nama mahasiswa di tabel.
- **Pengujian:**
  - Backend: `.\venv\Scripts\python.exe -m pytest tests -q` — 182 PASS (100% passed).
  - Frontend: `npm run typecheck` — PASS (0 errors).

## 2026-10-26 — Penambahan Filter Program Sertifikasi (MOS / MCF / MTCNA)

- **Kebutuhan bisnis & UX:**
  - Menambahkan kontrol filter program pada halaman hasil sinkronisasi agar pengguna dapat memfilter baris berdasarkan program sertifikasi yang diambil mahasiswa: `MOS`, `MCF`, atau `MTCNA`.
  - Filter program dapat dikombinasikan secara fleksibel dengan pencarian teks (NIM/Nama) dan filter status hasil (Valid, Perlu Verifikasi, Tidak Ditemukan).
- **Perubahan kode:**
  - `backend/app/services/sync_service.py`:
    - Fungsi pembantu `_row_has_program` untuk mendeteksi keberadaan rekaman ujian/status per program (`MOS`, `MCF`, `MTCNA`).
    - Penambahan parameter `program` pada `list_sync_results` dengan filtering akurat dan paginasi yang tetap terjaga.
  - `backend/app/api/v1/endpoints/sync.py`: Menerima query parameter `program` pada `GET /{session_id}/results`.
  - `backend/tests/test_sync_service.py` & `test_sync_api.py`: Penambahan unit test untuk query dan filter program.
  - `frontend/lib/api.ts`: Penambahan parameter `program?: string` pada `getSyncResults`.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
    - State `programFilter` (`""` / `"MOS"` / `"MCF"` / `"MTCNA"`).
    - Elemen select dropdown `Program:` pada filter bar dengan opsi `Semua Program`, `MOS`, `MCF`, dan `MTCNA`.
    - Tombol `Reset Filter` untuk mereset seluruh filter (status dan program) sekaligus.
- **Pengujian:**
  - Backend: `.\venv\Scripts\python.exe -m pytest tests -q` — 182 PASS (100% passed).
  - Frontend: `npm run typecheck` — PASS (0 errors).
