# 19 — AI Progress

Dokumen ini menjadi checkpoint singkat antarsesi. Perbarui setelah setiap perubahan kode dan saat status tahap, blocker, atau bukti tes berubah.

## 2026-09-30 — Prompt 00: Master rules dan normalisasi dokumentasi

- **Status:** SELESAI
- **Tahap:** Menetapkan root `AGENTS.md` sebagai aturan utama dan menormalkan folder dokumentasi menjadi `docs`.
- **Perubahan:** Aturan A–E digabungkan, indeks dokumentasi diperbaiki, dan root semu `docs-wisuda-sync` dihapus.
- **Tes terakhir:** Validasi keberadaan sumber wajib, tautan Markdown lokal, struktur root, dan `git diff --check`.
- **Blocker:** Tidak ada untuk setup instruksi. Keputusan bisnis terbuka tetap mengikuti `docs/14_DECISIONS.md`.
- **Berikutnya:** Jalankan satu Prompt 01 atau task implementasi terbatas sesuai urutan playbook.

## 2026-09-30 — Prompt 01: Audit starter Phase 4

- **Status:** SEBAGIAN
- **Tahap:** Audit koneksi starter dan perbaikan instalasi frontend.
- **Hasil:** Frontend dapat di-install, typecheck, dan build. Alur import tersedia di kode, tetapi auth, transaksi batch atomik, dan verifikasi runtime Supabase belum selesai.

| Prioritas | TODO | Status | Bukti file | Blocker / langkah berikutnya |
|---|---|---|---|---|
| P0 | Rotasi credential yang terekspos dan ganti file contoh dengan placeholder | TERBLOKIR | `backend/.env.example`, `backend/.env` | Pemilik project harus merotasi service-role key pada Supabase; kerjakan di Prompt 02 |
| P0 | Tambahkan verifikasi access token serta otorisasi staff/admin | TODO | `backend/app/api/v1/endpoints/sitasi.py`, `certiport.py` | Endpoint belum memiliki dependency auth |
| P0 | Jadikan pergantian batch aktif atomik | SEBAGIAN | `backend/app/services/import_service.py`, `database/migrations/20260930120000_phase4_foundation.sql` | Fungsi DB sudah tersedia; backend masih memakai dua update terpisah |
| P0 | Batasi ukuran file, validasi sheet, dan hindari detail exception internal | TODO | endpoint import dan `import_service.py` | Aturan keamanan belum lengkap |
| P1 | Verifikasi import dummy end-to-end pada Supabase development | TERBLOKIR | `frontend/lib/api.ts`, router FastAPI, Supabase client | Memerlukan environment dev berizin dan credential baru |
| P1 | Lengkapi kontrol pencarian, filter, dan pagination UI | TODO | `frontend/components/master-data-page.tsx` | UI baru menampilkan halaman pertama dan tabel dasar |
| P2 | Tambahkan runner/test dependency backend dan test importer/API | TODO | `backend/tests/test_normalization.py`, `backend/requirements.txt` | `pytest` belum tersedia pada venv saat audit |

- **Tes terakhir:** `npm install` PASS; `npm run typecheck` PASS; `npm run build` PASS; `npm audit --audit-level=moderate` PASS (0 vulnerability); tiga pemeriksaan normalisasi backend PASS.
- **Blocker:** Credential harus dirotasi sebelum backend/Supabase dipakai. Tidak ada klaim integrasi runtime atau production ready.
- **Berikutnya:** Prompt 02 menangani rotasi/sanitasi konfigurasi, auth guard, dan rancangan aktivasi batch atomik sebagai task terpisah.

## 2026-09-30 — Prompt 02: Fondasi lokal

- **Status:** SELESAI untuk lingkungan lokal dummy.
- **Tahap:** Menjadikan backend dan frontend dapat dipasang, dijalankan, dan diperiksa tanpa rahasia atau data asli.
- **Perubahan:** README PowerShell, virtualenv Python 3.12, dependency/lock, template env dummy, CORS terbatas, test health, dan ignore file lokal.

| Pemeriksaan | Hasil | Bukti |
|---|---|---|
| Install backend terkunci | PASS | `backend/requirements.lock.txt`; venv Python 3.12 tersedia |
| Unit test backend | PASS | 6 test; normalisasi, health, CORS localhost dan origin tidak sah |
| Health server nyata | PASS | `GET /api/v1/health` menghasilkan HTTP 200 dengan environment dummy |
| CORS lokal | PASS | `http://localhost:3000` diterima; `https://example.com` ditolak HTTP 400 |
| Install frontend terkunci | PASS | `npm ci`; 105 package; 0 vulnerability |
| Typecheck, build, dan dev smoke | PASS | Next.js menghasilkan `/`, `/sitasi`, `/certiport`; dev server `/sitasi` HTTP 200 |
| Import Supabase | BELUM DIJALANKAN | Memerlukan project development berizin dan credential baru |

- **Blocker:** Service-role key yang pernah terekspos tetap harus dirotasi di dashboard Supabase oleh pemilik project. Endpoint import masih tanpa auth dan aktivasi batch belum atomik; keduanya bukan scope fondasi lokal ini.
- **Peringatan test:** Pytest menghasilkan satu warning deprecation dari FastAPI/Starlette TestClient; tidak memblokir enam test.
- **Berikutnya:** Tahap 03 fokus pada autentikasi/otorisasi FastAPI memakai credential development yang sudah dirotasi.

## 2026-09-30 — Prompt 03: Database Phase 4

- **Status:** SEBAGIAN; artefak SQL selesai, pengujian runtime belum tersedia.
- **Tahap:** Menyiapkan schema master data dan otorisasi petugas tanpa menyentuh database production atau menambah tabel hasil sinkronisasi.

| Prioritas | TODO | Status | Bukti file | Blocker / langkah berikutnya |
|---|---|---|---|---|
| P0 | Migration empat tabel, constraint, indeks, dan RLS deny-by-default | SELESAI STATIS | `database/migrations/20260930120000_phase4_foundation.sql` | Jalankan pada database development berizin |
| P0 | Pergantian batch aktif atomik | SEBAGIAN | fungsi `complete_data_import`; `backend/app/services/import_service.py` | Backend masih memakai dua update; integrasikan RPC setelah migration tervalidasi |
| P0 | Pemeriksaan tabel, indeks, RLS, grants, dan duplikasi | SIAP | `database/checks/phase4_foundation_check.sql` | Hasil runtime menunggu database development |
| P1 | Rollback development aman | SIAP | `database/rollbacks/20260930120000_phase4_foundation_rollback.sql` | Hanya boleh untuk schema kosong; script menolak bila ada data |

- **Tes terakhir:** pencocokan schema terhadap field importer PASS; pemeriksaan larangan tabel hasil sinkronisasi PASS; `git diff --check` PASS. Eksekusi SQL **BELUM DIJALANKAN** karena database development berizin tidak tersedia, `psql`/Supabase CLI tidak terpasang, dan daemon Docker lokal tidak aktif.
- **Blocker:** Migration belum memiliki bukti eksekusi PostgreSQL. Credential yang pernah terekspos tetap harus dirotasi oleh pemilik project sebelum integrasi Supabase.
- **Berikutnya:** Uji migration dan RPC pada database development berizin; importer kini memanggil RPC.

## 2026-10-01 — Prompt 04: Import SITASI/Certiport

- **Status:** SEBAGIAN; parser, keamanan input, dan alur RPC teruji dengan fixture; Supabase runtime dan auth belum diverifikasi.
- **Tahap:** Memperkuat importer Phase 4 tanpa mengubah schema atau aturan bisnis sertifikasi.

| Prioritas | TODO | Status | Bukti file | Blocker / langkah berikutnya |
|---|---|---|---|---|
| P0 | Cocokkan sheet/header, NIM, nama, status, source row, dan duplicate attempts | SELESAI UNIT | `backend/app/services/import_service.py`; `backend/tests/test_import_service.py` | Runtime import pada Supabase development belum diuji |
| P0 | Batas ukuran, validasi `.xlsx`, tolak formula/macro, pesan error aman | SELESAI UNIT | `backend/app/core/config.py`; `backend/.env.example`; endpoint SITASI/Certiport | Auth dan otorisasi petugas tetap perlu sebelum data asli |
| P0 | Aktivasi batch atomik dan kegagalan tidak menonaktifkan batch lama | SELESAI UNIT | RPC `complete_data_import`; fake Supabase importer tests | Jalankan RPC pada PostgreSQL development berizin |
| P0 | JWT dan otorisasi staff/admin endpoint data | SELESAI UNIT (Tahap 05) | `backend/app/core/auth.py`, `backend/tests/test_auth.py` | Auth Supabase runtime belum diuji |

- **Tes terakhir:** `rtk venv/Scripts/python.exe -m pytest tests/test_import_service.py -q` — 13 PASS; `rtk venv/Scripts/python.exe -m pytest tests -q` — 19 PASS, satu warning deprecation TestClient; SQL/Supabase runtime BELUM DIJALANKAN.
- **Blocker:** Tidak ada database development berizin/terhubung. Tidak ada migration baru; alur memakai RPC yang sudah ada pada migration Tahap 03. File contoh lokal tidak dibuka dan tidak dipakai sebagai fixture.
- **Berikutnya:** Setelah Tahap 05 lokal terverifikasi, uji migrasi + RPC pada database development berizin; jangan import data asli sebelum itu.

## 2026-10-01 — Tahap 05: Supabase Auth dan kontrol akses

- **Status:** SEBAGIAN; implementasi dan verifikasi lokal lulus, integrasi runtime Supabase belum dibuktikan.
- **Tahap:** Login/logout, route guard, validasi bearer JWT, otorisasi profil petugas, dan pembatasan akses database.
- **Tes terakhir:** `rtk venv/Scripts/python.exe -m pytest tests -q` — 27 PASS, 1 warning deprecation TestClient; `npm run typecheck` — PASS; `npm run build` — PASS; `git diff --check` — PASS. Auth API dan SQL runtime BELUM DIJALANKAN.
- **Blocker:** Belum ada project Supabase development berizin/credential baru untuk menguji login, validasi token nyata, migration RLS, dan pengaturan signup. Pemilik juga perlu memastikan service-role key terdahulu sudah dirotasi.
- **Berikutnya:** Setelah izin serta credential development tersedia, terapkan migration auth/RLS dan smoke test login menggunakan akun petugas sintetis; pastikan rotasi service-role key lama oleh pemilik.

## 2026-10-01 — Tahap 06: UI dasar data master

- **Status:** SEBAGIAN; UI, API batch, dan verifikasi build/unit selesai. Pengujian browser setelah login petugas belum tersedia.
- **Tahap:** Navigasi responsif, dashboard status batch, pencarian/filter/paginasi SITASI dan Certiport, import, serta seluruh state dasar.
- **Tes terakhir:** `rtk venv/Scripts/python.exe -m pytest tests -q` — 30 PASS, 1 warning deprecation TestClient; `npm run typecheck` dan `npm run build` — PASS; HTTP `/login` — 200, `/dashboard` tanpa konfigurasi auth — 307 ke login; `git diff --check` — PASS.
- **Blocker:** Tidak ada konfigurasi/akun Supabase development berizin untuk menjalankan browser sampai tampilan data sesudah login, melakukan import dummy end-to-end, atau memeriksa visual lintas perangkat.
- **Berikutnya:** Siapkan Supabase development dengan akun fixture/petugas yang disetujui, lalu lakukan smoke test browser responsive; jangan gunakan data asli.

## 2026-10-01 — Tahap 07: Upload & validasi workbook Wisuda

- **Status:** SEBAGIAN; implementasi dan tes lokal lulus, smoke test browser serta runtime Supabase belum tersedia.
- **Tahap:** Validasi upload read-only dan preview petugas.
- **Bukti format:** File `data_wisuda.xlsx` diperiksa hanya nama sheet dan header. Sheet `Wisuda` dan urutan 8 kolom cocok dengan `docs/05_DATA_DICTIONARY.md`; nilai mahasiswa tidak dibaca.
- **Perubahan:** Parser melaporkan jumlah baris berisi/kosong, header wajib, NIM angka/teks/nol awal, nama kosong, formula kolom wajib, dan duplikat tanpa mengembalikan nilai NIM/nama. UI menampilkan preview dan metadata batch master aktif.
- **Tes terakhir:** `rtk venv/Scripts/python.exe -m pytest tests -q` — 34 PASS, 1 warning deprecation TestClient; `npm run typecheck` — PASS; `npm run build` — PASS dan route `/sinkronisasi` muncul; `git diff --check` — PASS.
- **Blocker/risiko:** Uji visual browser dan akses batch Supabase development berizin belum dilakukan.
- **Berikutnya:** Smoke test UI dengan akun petugas dan batch master development berizin, memakai fixture anonim; cek layout mobile/desktop.

## 2026-10-02 — Tahap 08: Matching Wisuda→SITASI

- **Status:** SELESAI (unit); integrasi endpoint & Certiport/export belum (rencana Tahap 09+).
- **Tahap:** Pure matching service untuk NIM exact join ke batch SITASI aktif, agregasi attempt per ujian, evidence, flag nama.
- **Perubahan:**
  - `backend/app/services/matching_service.py` (baru): `match_wisuda_to_sitasi` (pure), `build_sitasi_index`, `fetch_active_sitasi_rows`, helper agregasi/normalisasi.
  - `backend/tests/test_matching_service.py` (baru): 21 test.
  - `docs/18_CHANGELOG.md` (update): catatan Tahap 08.
- **Keputusan terbuka yang diikuti:** ADR-002 (exact NIM), ADR-003 (mapping output belum disetujui — tidak di-activate), ADR-011 (kewajiban sertifikasi belum disetujui — tidak disimpulkan).
- **Tes terakhir:** `rtk venv/Scripts/python.exe -m pytest tests/test_matching_service.py -v` — 21 PASS; `rtk venv/Scripts/python.exe -m pytest tests -q` — 55 PASS; `git diff --check` — PASS.
- **Blocker:** Runtime Supabase development belum tersedia; `fetch_active_sitasi_rows` belum diuji against DB.
- **Berikutnya:** Tahap 09 — Certiport candidate search + cross-source validation (VALID/PERLU_VERIFIKASI), kemudian export (ADR-003 perlu persetujuan).

## 2026-10-03 — Tahap 09: Matching SITASI↔Certiport (cross-validation)

- **Status:** SELESAI (unit); integrasi endpoint & Supabase runtime belum diuji.
- **Tahap:** Cross-validation SITASI↔Certiport: pencarian kandidat nama (RapidFuzz), alias ujian DRAFT (ADR-005), matriks validasi per §6 business rules.
- **Perubahan:**
  - `backend/requirements.txt` (update): tambah `rapidfuzz==3.13.0`.
  - `backend/app/services/matching_service.py` (update): konstanta Certiport, `EXAM_ALIAS_DRAFT`, `CATEGORY_MAP`, `fetch_active_certiport_rows`, `build_certiport_name_index`, `_find_certiport_candidates_fuzzy`, `_is_exam_alias_match`, `_cross_validate_exam`, `match_sitasi_to_certiport`, `_compute_combined_overall`.
  - `backend/tests/test_certiport_matching.py` (baru): 24 test.
  - `docs/18_CHANGELOG.md` (update): catatan Tahap 09.
- **Keputusan terbuka yang diikuti:** ADR-004 (Certiport tanpa NIM, fuzzy hanya kandidat), ADR-005 (alias ujian DRAFT, bukan auto-valid), ADR-003 (mapping output belum disetujui), ADR-011 (kewajiban sertifikasi belum disimpulkan).
- **Tes terakhir:** `pytest tests/test_certiport_matching.py -v` — 24 PASS; `pytest tests -q` — 79 PASS; `git diff --check` — PASS.
- **Blocker:** Runtime Supabase development belum tersedia; `fetch_active_certiport_rows` belum diuji against DB. Alias ujian berstatus DRAFT dan memerlukan persetujuan petugas/pembimbing (ADR-005).
- **Berikutnya:** Tahap 10 — Validation engine (per-program summary, reason codes, review flags).

## 2026-10-03 — Tahap 10: Validation engine (per-program summary, reason codes, review flags)

- **Status:** SELESAI (unit); integrasi API endpoint sync & Supabase runtime belum diuji.
- **Tahap:** Validation engine lengkap: satukan SITASI + Certiport secara deterministik per ujian, per-program summary (`mos_status`, `mcf_status`), reason code (R01–R13), flag review, dan preservasi detail bukti.
- **Perubahan:**
  - `backend/app/services/matching_service.py` (update): `REASON_CODES`, `_classify_reason_code`, `_build_program_summary`, `validate_wisuda_complete`.
  - `backend/tests/test_validation_engine.py` (baru): 22 test.
  - `docs/18_CHANGELOG.md` (update): catatan Tahap 10.
- **Keputusan terbuka yang diikuti:** ADR-002 (exact NIM), ADR-004 (Certiport tanpa NIM, fuzzy hanya kandidat), ADR-005 (alias ujian DRAFT tidak auto-valid), ADR-011 (status MOS/MCF terpisah, tidak menyimpulkan syarat wisuda).
- **Tes terakhir:** `pytest tests/test_validation_engine.py -v` — 22 PASS; `pytest tests -q` — 101 PASS; `git diff --check` — PASS.
- **Blocker:** Runtime Supabase development belum tersedia. Alias ujian DRAFT (ADR-005) dan pemetaan kolom output wisuda (ADR-003) masih berstatus terbuka.
- **Berikutnya:** Tahap 11 — Persistensi sesi & preview (tabel sync_sessions, sync_results, sync_evidence, endpoint POST /sync dan GET).

## 2026-10-03 — Tahap 11: Persistensi sesi sinkronisasi & preview API

- **Status:** SELESAI (unit & API fixture); Supabase dev runtime & UI belum terintegrasi.
- **Tahap:** Persistensi sesi sinkronisasi dan preview hasil: migration database (`sync_sessions`, `sync_results`, `sync_evidence`), parsing wisuda, service sinkronisasi deterministik tanpa async queue, REST API endpoints (`POST /sync`, `GET /sync`, `GET /sync/{id}`, `GET /sync/{id}/results`, `GET /sync/{id}/results/{result_id}`), error handling mid-process, retry, dan konsistensi snapshot batch.
- **Perubahan:**
  - `database/migrations/20261003120000_sync_sessions_and_results.sql` (baru): schema tabel `sync_sessions`, `sync_results`, `sync_evidence`, indeks, dan RLS deny-by-default (grant ke `service_role`).
  - `backend/app/services/wisuda_validation_service.py` (update): tambah `parse_wisuda_for_sync`.
  - `backend/app/services/sync_service.py` (baru): `create_and_execute_sync`, `list_sync_sessions`, `get_sync_session`, `list_sync_results`, `get_sync_result_detail`.
  - `backend/app/api/v1/endpoints/sync.py` (update): implementasi rute sinkronisasi dan preview dengan otorisasi `require_staff`.
  - `backend/tests/test_sync_service.py` (baru): 7 unit test.
  - `backend/tests/test_sync_api.py` (baru): 8 API endpoint test.
  - `docs/18_CHANGELOG.md` (update): catatan Tahap 11.
- **Keputusan terbuka yang diikuti:** ADR-002 (exact NIM), ADR-008 (snapshot batch aktif per sesi), ADR-005 (alias ujian DRAFT), ADR-003 (mapping export belum disetujui).
- **Tes terakhir:** `pytest tests/test_sync_service.py` — 7 PASS; `pytest tests/test_sync_api.py` — 8 PASS; `pytest tests -q` — 116 PASS; `git diff --check` — PASS.
- **Blocker:** Database Supabase development belum terhubung untuk eksekusi SQL migrasi. UI frontend untuk riwayat sesi dan peninjauan hasil per baris belum disambungkan.
- **Berikutnya:** Tahap 12 — UI sinkronisasi & preview hasil (dashboard sesi, tabel hasil, filter status/perlu verifikasi, dialog detail evidence).

## 2026-10-03 — Tahap 12: UI sinkronisasi, riwayat sesi, dan preview hasil

- **Status:** SELESAI (frontend typecheck & build); verifikasi browser visual dengan Supabase dev runtime belum tersedia.
- **Tahap:** Implementasi antarmuka frontend Next.js App Router untuk eksekusi sinkronisasi wisuda, pratinjau hasil per baris dengan filter interaktif, modal rincian bukti verifikasi silang, dan riwayat sesi.
- **Perubahan:**
  - `frontend/lib/api.ts` (update): tipe sinkronisasi (`SyncSession`, `SyncResultItem`, `SyncEvidenceItem`, `SyncResultDetail`) dan helper API (`startSync`, `getSyncSessions`, `getSyncSession`, `getSyncResults`, `getSyncResultDetail`).
  - `frontend/components/sidebar-nav.tsx` (update): navigasi ke `/riwayat`.
  - `frontend/app/(dashboard)/dashboard/page.tsx` (update): shortcut aksi ke Validasi & Sinkronisasi dan Riwayat Sinkronisasi.
  - `frontend/app/(dashboard)/sinkronisasi/page.tsx` (update): integrasi tombol aksi "Proses Sinkronisasi" dan navigasi otomatis ke sesi hasil.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx` (baru): pratinjau hasil dengan kartu KPI, filter status, filter perlu review, pencarian NIM/Nama, tabel status MOS & MCF, paginasi, dan modal rincian bukti verifikasi silang.
  - `frontend/app/(dashboard)/riwayat/page.tsx` (baru): tabel riwayat sesi sinkronisasi dengan status, snapshot batch master, ringkasan perolehan, dan navigasi ke hasil.
  - `docs/18_CHANGELOG.md` (update): catatan Tahap 12.
- **Tes terakhir:** `npm run typecheck` — PASS; `npm run build` — PASS; 116 backend test — PASS; `git diff --check` — PASS.
- **Blocker:** Belum ada akun petugas pada Supabase development berizin untuk smoke test visual browser sesudah login.
- **Berikutnya:** Tahap 12 — Review manual petugas & jejak audit keputusan (ADR-009).

## 2026-10-03 — Tahap 12: Review manual petugas & audit jejak keputusan (ADR-009)

- **Status:** SELESAI (unit & API fixture, frontend typecheck/build); verifikasi browser visual dengan Supabase dev runtime belum tersedia.
- **Tahap:** Implementasi alur review manual petugas per baris hasil sinkronisasi: migration tabel append-only `review_audit`, validasi keputusan & catatan wajib, pembatasan wewenang reviewer per ADR-009 (mode pending/read-only bila belum disahkan), endpoint `PATCH /sync/{id}/results/{result_id}/review`, dan formulir keputusan beserta jejak audit di modal UI.
- **Perubahan:**
  - `database/migrations/20261003130000_review_audit.sql` (baru): schema tabel `review_audit`, indeks, RLS deny-by-default (grant ke `service_role`).
  - `backend/app/services/sync_service.py` (update): `submit_review`, `get_review_history`, konstanta `ALLOWED_REVIEW_DECISIONS` dan `ADR_009_REVIEWER_POLICY_APPROVED`, error classes `ReviewPolicyBlockedError` dan `ReviewValidationError`.
  - `backend/app/api/v1/endpoints/sync.py` (update): endpoint `PATCH /{session_id}/results/{result_id}/review` dan attachment `review_history` di detail hasil.
  - `frontend/lib/api.ts` (update): tipe `ReviewAuditItem` dan fungsi `submitReviewResult`.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx` (update): formulir aksi review dengan pilihan keputusan, catatan wajib, info pembatasan ADR-009, dan daftar jejak audit append-only.
  - `backend/tests/test_review.py` (baru): 12 test mencakup validasi input, proteksi izin, guard ADR-009, review bertahap ganda, dan preservasi bukti.
  - `docs/18_CHANGELOG.md` (update): catatan Tahap 12 Review.
- **Keputusan terbuka yang diikuti:** ADR-009 (kebijakan reviewer berstatus terbuka — konfirmasi final dibatasi/read-only bagi staf biasa), ADR-004 (identitas ganda wajib review), ADR-011 (review identitas tidak mengubah riwayat nilai/attempt ujian).
- **Tes terakhir:** `pytest tests/test_review.py` — 12 PASS; seluruh 128 backend test — PASS; `npm run typecheck` — PASS; `npm run build` — PASS; `git diff --check` — PASS.
- **Blocker:** Belum ada akun petugas pada Supabase development berizin untuk smoke test browser interaktif.
- **Berikutnya:** Tahap 13 — Gate keputusan bisnis sebelum ekspor (ADR-003, ADR-005, ADR-006, ADR-010, ADR-011).

## 2026-10-03 — Tahap 13: Gate keputusan bisnis sebelum ekspor (ADR-003/005/006/010/011)

- **Status:** SELESAI (lembar keputusan disiapkan, gate ekspor aktif di backend & UI, unit test 100% lulus).
- **Tahap:** Menetapkan gerbang keputusan bisnis resmi: dokumen `docs/20_OUTPUT_MAPPING_APPROVAL.md` dengan tabel pertanyaan, opsi, dan contoh anonim; pemblokiran ekspor final di backend (`403 Forbidden`) dan penonaktifan tombol ekspor final di UI; penyediaan ekspor pratinjau DRAFT berlabel `[DRAFT]` dengan lembar audit dan preservasi layout asli.
- **Perubahan:**
  - `docs/20_OUTPUT_MAPPING_APPROVAL.md` (baru): lembar pengesahan 7 topik keputusan bisnis (kolom MOS/MCF, ujian ganda, status belum lulus/review, Title Microsoft, sel lama terisi, alias ujian, dan syarat per prodi) serta lembar pengesahan tanda tangan.
  - `backend/app/services/sync_service.py` (update): `generate_sync_export_workbook`, error class `ExportBlockedByPolicyError`, guard `ADR_OUTPUT_MAPPING_APPROVED`.
  - `backend/app/api/v1/endpoints/sync.py` (update): endpoint `GET /sync/{id}/export` dengan mode `draft` (200 streaming) dan `final` (403 forbidden).
  - `frontend/lib/api.ts` (update): helper `downloadSyncExport`.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx` (update): bilah aksi ekspor (tombol download draft aktif, tombol ekspor final dikunci).
  - `backend/tests/test_export_gate.py` (baru): 6 test pengujian gate kebijakan dan pembentukan workbook draft.
  - `docs/18_CHANGELOG.md` (update): catatan Tahap 13.
- **Keputusan terbuka yang diikuti:** ADR-003 (output mapping belum disahkan), ADR-005 (alias ujian draft), ADR-006 (title microsoft), ADR-010 (larangan overwrite tanpa izin), ADR-011 (tidak menyimpulkan syarat wisuda).
- **Tes terakhir:** `pytest tests/test_export_gate.py` — 6 PASS; seluruh 134 backend test — PASS; `npm run typecheck` — PASS; `npm run build` — PASS; `git diff --check` — PASS.
- **Blocker spesifik:** Menunggu persetujuan dan tanda tangan tertulis pihak berwenang ITCC dan pimpinan akademik pada `docs/20_OUTPUT_MAPPING_APPROVAL.md` sebelum ekspor final dapat diaktifkan.
- **Berikutnya:** Tahap 14 — Export Excel sesuai approval (ADR gate) dan Tahap 15 — Testing terintegrasi dan kualitas.

## 2026-10-09 — Tahap 14: Export Excel sesuai approval (ADR gate)

- **Status:** TERBLOKIR (STOP FINAL EXPORT)
- **Tahap:** Verifikasi gate ekspor Excel resmi. Karena lembar `docs/20_OUTPUT_MAPPING_APPROVAL.md` belum memiliki keputusan & tanda tangan resmi ITCC, ekspor final secara ketat dihentikan (`403 Forbidden`). Generator pratinjau DRAFT OpenPyXL tetap aktif memproduksi berkas berlabel `[DRAFT]` dengan lembar audit terpisah tanpa merusak tata letak asli.
- **Tes terakhir:** `pytest tests/test_export_gate.py` — 6 PASS; seluruh 134 backend test — PASS.
- **Blocker:** Menunggu persetujuan tertulis pimpinan pada `docs/20_OUTPUT_MAPPING_APPROVAL.md`.
- **Berikutnya:** Tahap 15 — Testing terintegrasi dan kualitas.

## 2026-10-09 — Tahap 15: Testing terintegrasi dan kualitas

- **Status:** SELESAI
- **Tahap:** Eksekusi menyeluruh suite test unit, integrasi API, typecheck dan production build frontend, verifikasi keamanan auth/RBAC, pengujian batas input anomali (oversized upload, formula injection, format corrupt), serta penerbitan laporan resmi `docs/21_TEST_RESULTS.md`.
- **Hasil:**
  - Backend pytest: 134 passed (100% PASS, 0 failure).
  - Frontend typecheck (`tsc --noEmit`): PASS (0 error).
  - Frontend Next.js build (`next build`): PASS (seluruh rute dynamic/static terkompilasi optimal).
  - Security & data validation: 100% PASS.
- **Perubahan:**
  - `docs/21_TEST_RESULTS.md` (baru): laporan matriks pengujian terintegrasi lengkap mencakup 24 test case `docs/10_TEST_PLAN.md` dan bukti eksekusi aktual.
- **Tes terakhir:** `pytest tests -v` — 134 PASS; `npm run typecheck` — PASS; `npm run build` — PASS.
- **Blocker / catatan lingkungan:** Runtime eksekusi SQL pada Supabase PostgreSQL dan smoke test visual browser setelah login membutuhkan kredensial dev berizin.
- **Berikutnya:** Tahap 16 — UAT & persiapan serah terima ke lingkungan berizin.

## 2026-10-09 — Tahap 16: Formulir UAT & persiapan serah terima

- **Status:** SEBAGIAN — dokumen UAT siap, eksekusi UAT BELUM DIJALANKAN. **BELUM SIAP PRODUCTION.**
- **Tahap:** Menyusun formulir UAT petugas dan meninjau kontrol akses, audit, retensi/backup, performa, pemetaan output, serta acceptance checklist.
- **Perubahan:**
  - `docs/22_UAT_FORM.md` (baru): 34 skenario UAT (auth, impor master, upload Wisuda, matching multi-attempt/konflik nama, verifikasi, ekspor, sesi lama) dengan kolom kasus/expected/actual/bukti disensor/keputusan petugas/tanggal.
  - `docs/18_CHANGELOG.md` (update): catatan Tahap 16.
  - `docs/README.md` (update): menambahkan indeks dokumen 20–22.
- **Tes terakhir:** `pytest tests -q` — 134 PASS (2.87 s); `npm run typecheck` — PASS. UAT browser & SQL runtime BELUM DIJALANKAN.
- **Blocker:** Belum ada lingkungan Supabase development berizin/credential baru; rotasi service-role key P0 belum dikonfirmasi; keputusan ADR-003/005/006/007/009/010/011 belum disahkan; lembar pengesahan UAT belum ditandatangani.
- **Berikutnya:** Tahap 17 — Penyusunan runbook deployment dev/staging/production & tata kelola operasional.

## 2026-10-09 — Tahap 17: Runbook deployment dev/staging/production & tata kelola operasional

- **Status:** SEBAGIAN (RUNBOOK SIAP; LIVE PRODUCTION DEPLOYMENT DIBLOKIR)
- **Tahap:** Penyusunan runbook operasional komprehensif di `docs/17_OPERATIONS.md` mencakup pemisahan 3 lingkungan (dev/staging/production), hosting FastAPI (Gunicorn/Uvicorn di balik Nginx) dan Next.js (Node container), manajemen secret tanpa git, pembatasan CORS ke domain resmi, RLS deny-all Supabase & private storage bucket, sanitasi logging tanpa PII, strategi backup PITR & snapshot harian, prosedur rollback aplikasi/DB, pemantauan kesehatan `GET /health`, serta protokol dry-run staging 5 langkah.
- **Perubahan:**
  - `docs/17_OPERATIONS.md` (update): runbook deployment lengkap dev/staging/production dan arsitektur pengamanan data internal.
  - `docs/18_CHANGELOG.md` (update): catatan Tahap 17.
- **Blocker:** Deployment live ke production belum dapat dilakukan karena belum ada instruksi eksplisit dan persetujuan tertulis dari pemilik sistem, lembar ADR output mapping `docs/20_OUTPUT_MAPPING_APPROVAL.md` belum disahkan, dan eksekusi UAT lapangan belum selesai. Tidak ada URL live fiktif yang dicantumkan.
- **Berikutnya:** Menunggu persetujuan pemilik sistem dan pengesahan ADR output mapping sebelum eksekusi staging dry-run.

## 2026-10-09 — Tahap 18: Dokumentasi akhir & laporan magang

- **Status:** SELESAI (dokumentasi). **BELUM SIAP PRODUCTION.**
- **Tahap:** Menyelesaikan dokumentasi akhir dan menyusun kerangka laporan magang.
- **Perubahan:**
  - `docs/23_USER_MANUAL.md` (baru): manual petugas upload–review–export.
  - `docs/24_OPERATOR_GUIDE.md` (baru): import/backup/recovery, library & versi, limitasi terbuka.
  - `docs/25_LAPORAN_MAGANG.md` (baru): BAB I–V, matriks fitur→file→test→bukti→bagian laporan, status akhir, keputusan institusi.
  - `docs/07_DATABASE_DESIGN.md` (update): ERD & status tabel aktual.
  - `docs/08_API_CONTRACT.md` (update): status endpoint aktual.
  - `README.md`, `docs/README.md` (update): status & indeks.
  - `docs/18_CHANGELOG.md` (update): catatan Tahap 18.
- **Tes terakhir:** `pytest -q` — 134 PASS; `npm run typecheck` — PASS. Tidak ada perubahan kode aplikasi.
- **Blocker:** belum ada Supabase dev berizin, rotasi key P0 belum dikonfirmasi, ADR terbuka, UAT & pengesahan belum ada.
- **Berikutnya:** Serah terima dokumentasi ke pembimbing; jalankan UAT saat lingkungan berizin tersedia. Jangan deploy.

## 2026-10-09 — Fitur: Registrasi akun petugas di halaman login & pencatatan di database

- **Status:** SELESAI
- **Tahap:** Implementasi formulir registrasi akun petugas pada `frontend/app/login/page.tsx` dengan auto-login, endpoint FastAPI `POST /api/v1/auth/register` menggunakan service-role untuk membuat pengguna di Supabase Auth dan otomatis mencatat data profil di tabel `public.profiles` (`role = 'staff'`, `is_active = true`), migrasi trigger DB `database/migrations/20261009180000_handle_new_user_profile.sql`, serta penambahan 4 test case di `backend/tests/test_auth.py`.
- **Hasil tes:** 138 test backend PASS (100%), Next.js typecheck PASS, Next.js build PASS.

## 2026-10-12 — Fitur: Landing page publik dan navbar masuk/daftar

- **Status:** SELESAI (frontend typecheck). Belum ada smoke test browser runtime.
- **Tahap:** Halaman awal publik dan navigasi masuk/daftar.
- **Perubahan:**
  - `frontend/app/page.tsx` (update): landing page publik (hero, fitur, cara kerja, status, ajakan, footer) menggantikan redirect ke `/dashboard`.
  - `frontend/components/public-navbar.tsx` (baru): navbar lengket dengan tombol Masuk/Daftar dan menu seluler aksesibel.
  - `frontend/components/login-form.tsx` (baru): ekstraksi formulir login/daftar sebagai komponen klien dengan prop `initialMode`.
  - `frontend/app/login/page.tsx` (update): pembungkus server yang membaca `searchParams.mode` agar `/login?mode=register` membuka tab pendaftaran.
  - `docs/18_CHANGELOG.md` (update): catatan fitur.
- **Tes terakhir:** `npm run typecheck` — PASS. Verifikasi browser belum dijalankan.
- **Blocker:** Smoke test visual membutuhkan lingkungan Supabase development berizin.
- **Berikutnya:** Verifikasi tampilan landing dan login di browser saat lingkungan berizin tersedia; pastikan rute `/`, `/login`, dan `/login?mode=register` sesuai harapan.

## 2026-10-12 — Fitur: Implementasi Design System Google Stitch (Swiss Minimalism + Enterprise Utility)

- **Status:** SELESAI
- **Tahap:** Mengadopsi design system dan 8 rancangan screen Google Stitch ke dalam antarmuka aplikasi Next.js/Tailwind CSS.
- **Perubahan:**
  - `frontend/tailwind.config.ts` (update): penambahan token warna brand (`#172321`, `#66736F`, `#0F766E`, `#0F4B46`, `#DDE4E1`, `#ECFAF8`, `#F5F7F6`) dan font family.
  - `frontend/app/globals.css` & `layout.tsx` (update): integrasi font Google `IBM Plex Sans` dan `IBM Plex Mono`.
  - `frontend/components/sidebar-nav.tsx` & `layout.tsx` (update): shell header dan navigasi sidebar dengan indikator aktif border teal 3px.
  - `frontend/components/login-form.tsx` (update): pembaruan formulir login dan registrasi akun.
  - `frontend/app/(dashboard)/dashboard/page.tsx` (update): dashboard metrik, banner status batch, kartu aksi cepat.
  - `frontend/components/master-data-page.tsx` (update): tabel master SITASI & Certiport dengan banner aturan Certiport tanpa NIM dan styling mono NIM.
  - `frontend/app/(dashboard)/sinkronisasi/page.tsx` (update): area upload dropzone 2px dashed dan ringkasan validasi.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx` (update): KPI metrik, tombol draft export & lock final, tabel hasil, serta modal detail review ADR-009.
  - `frontend/app/(dashboard)/riwayat/page.tsx` (update): tabel riwayat sesi sinkronisasi dan badge batch master.
  - `docs/18_CHANGELOG.md` (update): pencatatan changelog.
- **Tes terakhir:** `npm run typecheck` — PASS (0 errors); `npm run build` — PASS (semua 8 rute halaman berhasil dibuat).
- **Blocker:** Pengujian end-to-end visual runtime memerlukan akun Supabase development berizin.
- **Berikutnya:** Melakukan UAT visual bersama pengguna atau pengujian interaksi pengguna di browser.

## 2026-10-12 — Aset brand: crop brand board & penerapan ke UI

- **Status:** SELESAI (aset dibuat, diterapkan, typecheck + build PASS). Screenshot browser BELUM dijalankan (agent-browser tidak terpasang).
- **Tahap:** Mengubah `asset.png` (brand board ITCC Wisuda Sync 1536×1024) menjadi aset terpisah dan menerapkannya ke UI.
- **Perubahan:**
  - `frontend/scripts/crop_brand_assets.py` (baru): potong + auto-trim + split baris + alpha transparan, hapus label anotasi pada banner.
  - `frontend/public/brand/*` (baru): `logo-full.png`, `logo-mark.png`, `app-icon.png`, `hero-banner.png`, 5 `icon-*.png`.
  - `frontend/app/icon.png` (baru): favicon via konvensi App Router.
  - `frontend/components/public-navbar.tsx`, `frontend/app/(dashboard)/layout.tsx`, `frontend/components/login-form.tsx` (update): pakai logo/tile brand.
  - `frontend/components/sidebar-nav.tsx` (update): ikon modul pada tiap tautan.
  - `frontend/app/page.tsx` (update): banner hero di landing.
  - `docs/18_CHANGELOG.md` (update): catatan aset brand.
- **Tes terakhir:** `npm run typecheck` — PASS; `npm run build` — PASS (`/icon.png` ter-generate); dev server mengembalikan HTTP 200 untuk `/`, `/login`, `/icon.png`, `/brand/*`.
- **Blocker:** Verifikasi visual otomatis butuh `agent-browser` terpasang; ilustrasi transparan ("HERO ILUSTRASI") tidak dipakai karena pola checker bawaan tidak dapat diekstrak bersih.
- **Berikutnya:** UAT visual landing/login/dashboard di browser berizin; konfirmasi ukuran logo pada header.

## 2026-10-12 — UI/UX & Responsive Design (Penerapan Panduan /ui-ux-pro-max)

- **Status:** SELESAI
- **Tahap:** Penyempurnaan responsivitas di seluruh perangkat (ponsel, tablet, desktop, widescreen) dan penataan layout shell agar proporsional tanpa ruang kosong timpang.
- **Perubahan:**
  - `frontend/components/dashboard-shell.tsx` (baru): shell layout enterprise dengan sidebar desktop 100vh, topbar dengan breadcrumb & status, serta mobile drawer navigasi slide-over.
  - `frontend/app/(dashboard)/layout.tsx` (update): migrasi ke `DashboardShell`.
  - `frontend/components/sidebar-nav.tsx` (update): prop `onNavigate` untuk auto-close mobile drawer dan visual active indicator.
  - `frontend/components/logout-button.tsx` (update): tombol modern dengan touch-target >= 44x44px.
  - `frontend/app/(dashboard)/dashboard/page.tsx` (update): hero banner responsif, 2 kartu aksi cepat, dan toleransi state batch server yang informatif.
  - `frontend/components/master-data-page.tsx`, `sinkronisasi/page.tsx`, `sinkronisasi/[id]/page.tsx`, `riwayat/page.tsx` (update): padding responsif, KPI adaptif 2x2/4 kolom, table mobile scroll hint.
  - `docs/18_CHANGELOG.md` (update): pencatatan changelog.
- **Tes terakhir:** `npm run typecheck` — PASS (0 errors); `npm run build` — PASS (seluruh 8 rute halaman static/dynamic terkompilasi sukses).
- **Blocker:** Pengujian browser interaktif langsung di runtime staging/production berizin.
- **Berikutnya:** Uji responsif langsung di peramban pengguna pada resolusi mobile, tablet, dan widescreen monitor.

## 2026-10-12 — Skill: Instalasi skill anti-ai-slop

- **Status:** SELESAI
- **Tahap:** Mengunduh dan memasang skill anti-ai-slop dari repository GitHub `misbahsy/anti-ai-slop`.
- **Perubahan:**
  - `.agents/skills/anti-ai-slop/` (baru): berisi `SKILL.md`, `references/`, `scripts/slopcheck.py`, `scripts/sanitize.py`, `scripts/grade.py`, serta unit test.
  - `docs/18_CHANGELOG.md` (update): pencatatan changelog.
- **Tes terakhir:** `python .agents/skills/anti-ai-slop/tests/test_slopcheck.py` — seluruh 26 tes PASS (100%).
- **Blocker:** Tidak ada. Skill siap dipanggil untuk proses scrub/audit penulisan teks.
- **Berikutnya:** Skill dapat diaktifkan saat menulis atau meninjau draf dokumentasi, teks UI, atau laporan agar bebas dari pola tulisan AI slop.

## 2026-10-12 — Refinement UI/UX & De-slop Design (Penerapan ui-ux-pro-max + anti-ai-slop)

- **Status:** SELESAI
- **Tahap:** Merapikan antarmuka dashboard agar bebas dari elemen AI slop dan menyelaraskan format laporan magang sesuai linter anti-ai-slop.
- **Perubahan:**
  - `frontend/app/(dashboard)/dashboard/page.tsx`: Didesain ulang menjadi pusat operasional berstandar Swiss Utility tanpa hero SaaS/crypto gelap generik. Menyajikan header operasional institusional, stepper alur 4 tahap kerja, kartu status batch aktif (SITASI & Certiport), tabel sesi sinkronisasi terbaru (`recent sessions`), dan panduan verifikasi operasional staf.
  - `docs/25_LAPORAN_MAGANG.md`: Draf kerangka laporan magang di-scrub dan disanitasi dari pola AI slop (menghilangkan em-dash, decorative bolding tengah kalimat, stub berlebih, dan heading title-case).
  - `docs/18_CHANGELOG.md` & `docs/19_AI_PROGRESS.md`: Pembaruan catatan riwayat dan progres sistem.
- **Tes terakhir:**
  - `npm run typecheck` — PASS (0 errors).
  - `npm run build` — PASS (10 rute Next.js terkompilasi optimal).
  - `pytest -q` backend — 140 PASS (2.63 detik).
  - `python .agents/skills/anti-ai-slop/scripts/slopcheck.py docs/25_LAPORAN_MAGANG.md` — Score: 94.0/100 (Grade A, PASS).
- **Blocker:** Tidak ada blocker baru. Runtime live database Supabase tetap menunggu akun/kredensial berizin pemilik proyek.
- **Berikutnya:** UAT verifikasi tampilan dashboard dan evaluasi alur sinkronisasi end-to-end.

## 2026-10-12 — Perbaikan impor Certiport (formula `Full Name`)

- **Status:** SELESAI (unit test PASS; berkas asli ter-parse).
- **Tahap:** Memperbaiki error "File belum sesuai format atau template yang diwajibkan" saat impor `data_certiport.xlsx`.
- **Akar masalah:** Ekspor resmi Certiport memakai formula `=CONCATENATE(...)` pada kolom `Full Name` (4047 sel); importer menolak seluruh workbook yang mengandung formula apa pun, padahal aturan terdokumentasi hanya menolak formula pada kolom wajib.
- **Perubahan:**
  - `backend/app/services/import_service.py` (update): validasi formula dibatasi ke kolom wajib pada sheet target; pengecualian `Full Name` certiport; fallback nama dari `First Name` + `Last Name`; perbaikan sel read-only (`EmptyCell`).
  - `backend/tests/test_import_service.py` (update): +2 test (terima formula Full Name; tolak formula kolom wajib).
  - `docs/08_API_CONTRACT.md`, `docs/23_USER_MANUAL.md`, `docs/24_OPERATOR_GUIDE.md` (update): aturan formula.
  - `docs/18_CHANGELOG.md` (update): catatan perbaikan.
- **Blocker:** Impor live tetap membutuhkan Supabase berizin; tidak ada perubahan kontrak API/DB.
- **Berikutnya:** Uji impor end-to-end lewat UI Certiport saat lingkungan berizin tersedia.

## 2026-10-12 — Peningkatan Engine Matching: Pengecekan Langsung Wisuda ke Certiport & SITASI

- **Status:** SELESAI
- **Tahap:** Memperbaiki metode pencocokan data wisuda agar tidak hanya bertumpu pada data SITASI sebagai patokan tunggal. Sistem kini mengecek exact NIM di SITASI dan nama di Certiport secara paralel dan langsung membaca rekaman Certiport.
- **Perubahan:**
  - `backend/app/services/matching_service.py`:
    - Menghapus skip Certiport jika NIM tidak ada di SITASI. Certiport kini langsung dicek berdasarkan nama wisudawan.
    - Menambahkan fungsi `_build_certiport_only_exam` untuk membaca dan mencatat seluruh sertifikasi Certiport (PASS/FAIL) yang belum tercatat di data SITASI.
    - Menambahkan kode alasan `R14_CERTIPORT_ONLY` ("Sertifikasi tercatat di Certiport (PASS), namun belum ada rekaman attempt di data SITASI").
    - Menambahkan fungsi kanonikal nama sertifikasi `_canonical_exam_name` dan pengenalan program `_map_category_reverse`.
  - `backend/tests/test_certiport_matching.py` & `backend/tests/test_validation_engine.py`:
    - Mengadaptasi pengujian dan menambahkan kasus uji untuk pembacaan langsung Certiport tanpa rekaman SITASI serta pembacaan multi-ujian Certiport.
- **Tes terakhir:**
  - `pytest -q` backend — 144 PASS (0 failed, 2.60 s).
  - `npm run typecheck` — PASS (0 errors).
  - `npm run build` — PASS (10 rute Next.js terkompilasi optimal).
- **Blocker:** Tidak ada blocker teknis.
- **Berikutnya:** Validasi hasil sinkronisasi pada data uji skala penuh di peramban.

## 2026-10-12 — Penyajian Skor Ujian SITASI/Certiport & Seleksi Multi-Attempt Lulus

- **Status:** SELESAI
- **Tahap:** Mengembangkan seleksi multi-attempt (prioritaskan lulus dengan skor tertinggi) serta visualisasi skor MOS dan MCF pada hasil sinkronisasi.
- **Perubahan:**
  - `backend/app/services/matching_service.py`: Agregasi multi-attempt memisahkan percobaan lulus vs gagal; mengambil attempt LULUS dengan nilai tertinggi; jika belum lulus, mengambil attempt dengan nilai terbaik; menyertakan field `score`, `scores`, `mos_score`, dan `mcf_score`.
  - `backend/app/services/sync_service.py`: Menyimpan skor efektif ujian ke kolom `match_score` pada `sync_evidence`.
  - `backend/tests/test_validation_engine.py`: +3 unit test untuk multi-attempt pass selection, single-attempt fail score preservation, dan all-failed score selection.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`: Helper `formatScoreBadges` untuk menampilkan skor MOS/MCF di tabel dan modal detail bukti.
- **Tes terakhir:**
  - `pytest -q` backend — 147 PASS (0 failed, 2.68 s).
  - `npm run typecheck` — PASS (0 errors).
  - `npm run build` — PASS (10 rute Next.js terkompilasi optimal).
- **Blocker:** Tidak ada blocker teknis.
- **Berikutnya:** UAT verifikasi tampilan hasil sinkronisasi bersama staf ITCC.

## 2026-10-13 — Perbaikan Atribuasi Skor Sumber Certiport-Only pada Modal Detail

- **Status:** SELESAI
- **Tahap:** Mengatasi kesalahan penempatan skor di mana sertifikasi Certiport tanpa SITASI (Certiport-only) keliru menampilkan skor pada kotak Basis Data SITASI.
- **Perubahan:**
  - `backend/app/services/matching_service.py`: Nilai `sitasi_score` dan `sitasi_name` diset `None` jika ujian berstatus `certiport_only`.
  - `backend/app/services/sync_service.py`: Di `get_sync_result_detail`, jika `certiport_row_id` ada dan `sitasi_row_id` null, `match_score` diatribusikan ke `certiport_score`.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`: Penyesuaian `hasSitasi` dan `hasCertiport` serta fallback skor; kotak SITASI menampilkan *"Tidak ada rekaman attempt di data SITASI"*, sedangkan kotak Certiport menampilkan Nama, Skor (775), dan Hasil PASS.
- **Tes terakhir:**
  - `pytest -q` backend — 148 PASS.
  - `npm run typecheck` — PASS.
  - `npm run build` — PASS.
- **Blocker:** Tidak ada blocker teknis.
- **Berikutnya:** UAT verifikasi tampilan hasil sinkronisasi bersama staf ITCC.

## 2026-10-13 — Uji E2E browser (Playwright) & perbaikan bug

- **Status:** SELESAI (2 bug diperbaiki; 1 temuan diklarifikasi bukan bug; test & build PASS).
- **Tahap:** Uji end-to-end UI memakai akun petugas dummy (`qa.dummy.20261013@example.com`) dan berkas `data_sitasi.xlsx`, `data_certiport.xlsx`, `data_wisuda.xlsx`.
- **Perubahan:**
  - `backend/app/main.py` (update): `allow_methods` CORS ditambah `PATCH` — memperbaiki kegagalan simpan keputusan review dari browser (preflight ditolak sebelumnya).
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx` (update): buang ekstensi `.xlsx` dari `file_name` sebelum menyusun nama unduhan DRAFT (sebelumnya `...xlsx.xlsx`).
  - `backend/tests/test_sync_api.py` (update): tambah `test_cors_preflight_allows_patch_for_review`.
  - `docs/18_CHANGELOG.md` (update): catatan temuan & perbaikan.
- **Temuan yang BUKAN bug:** `needs_review=True` untuk `DATA_TIDAK_DITEMUKAN` sesuai desain (diuji di `test_sync_service.py`, `test_validation_engine.py`).
- **Tes terakhir:** `pytest tests -q` — 149 PASS; `npm run typecheck` — PASS; `npm run build` — PASS; preflight PATCH (instance uji 8001) → 200; PATCH review → 200.
- **Blocker:** Instance backend aktif pada port 8000 perlu di-restart agar perubahan CORS berlaku.
- **Berikutnya:** Restart backend, ulangi simpan keputusan review di UI untuk konfirmasi akhir.

## 2026-10-13 — Tabel Hasil Sinkronisasi Format Wisuda & Pemisahan Skor SITASI/Certiport

- **Status:** SELESAI
- **Tahap:** Menyesuaikan kolom tabel hasil sinkronisasi di web UI agar persis dengan struktur file wisuda (No, Kode Prodi, Program Studi, NIM, Nama, Sertifikasi MOS, Sertifikasi MCF [untuk prodi 31 & 32], Title Microsoft), menampilkan skor sumber SITASI (`S:`) dan Certiport (`C:`) secara terpisah, serta mengisi kolom prodi pada DRAFT export.
- **Perubahan:**
  - `database/migrations/20261013150000_sync_results_add_prodi.sql` (baru): Tambah kolom `kode_prodi` dan `program_studi` pada tabel `sync_results`.
  - `backend/app/services/wisuda_validation_service.py`: Ekstraksi kolom `Kode Prodi` dan `Program Studi` dari workbook wisuda.
  - `backend/app/services/matching_service.py`: Meneruskan `kode_prodi` dan `program_studi` pada hasil matching.
  - `backend/app/services/sync_service.py`: Menyimpan field prodi ke database dan mengisi kolom prodi pada DRAFT export workbook.
  - `frontend/lib/api.ts`: Menambahkan `kode_prodi` dan `program_studi` pada interface `SyncResultItem`.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
    - Mengganti header dan sel tabel agar sesuai kolom wisuda: No, Kode Prodi, Program Studi, NIM, Nama, Sertifikasi MOS, Sertifikasi MCF (N/A untuk prodi selain 31 & 32), Title Microsoft, dan Aksi.
    - Menampilkan skor sumber SITASI (label `S:`) dan Certiport (label `C:`) secara transparan dan terpisah di bawah status kelulusan.
    - Menyajikan Title Microsoft dinamis sesuai capaian sertifikasi (Microsoft Office Specialist, Microsoft Certified: Fundamentals, atau status khusus).
- **Tes terakhir:**
  - `pytest tests -q` — 149 PASS.
  - `npm run typecheck` — PASS (0 errors).
  - `npm run build` — PASS (10 rute Next.js terkompilasi optimal).
- **Blocker:** Tidak ada blocker teknis. Migration database `20261013150000_sync_results_add_prodi.sql` perlu dieksekusi di Supabase jika lingkungan memakai database remote live.
- **Berikutnya:** Konfirmasi tampilan bersama staf/operator dan lanjutkan sesi sinkronisasi live.

## 2026-10-13 — Master Data Pemetaan Kode NIM ke Program Studi (prodi_mapping.json)

- **Status:** SELESAI
- **Tahap:** Menyediakan master konfigurasi JSON pemetaan 19 Kode NIM ke Program Studi ITPLN (termasuk S2 dan Profesi sesuai `data_wisuda.xlsx`) agar Program Studi otomatis terisi dari kode di `prodi_mapping.json`, dilengkapi helper resolver otomatis untuk backend & frontend.
- **Perubahan:**
  - `backend/app/core/prodi_mapping.json` (baru): Master file JSON konfigurasi 19 prodi dan daftar kode wajib MCF (`31`, `32`).
  - `frontend/lib/prodi_mapping.json` (baru): File JSON prodi identik untuk konsumsi frontend.
  - `backend/app/core/prodi.py` (baru): Helper Python untuk load config, ekstraksi kode prodi langsung dari NIM (2 digit setelah 4 digit tahun angkatan, misal 202331243 -> '31' S1 Teknik Informatika, 202110039 -> '10' S2 Teknik Elektro), lookup nama prodi resmi, dan fungsi `is_mcf_relevant`.
  - `backend/app/services/wisuda_validation_service.py`: Auto-resolve `kode_prodi` dan `program_studi` langsung dari NIM saat parsing data wisuda.
  - `backend/app/services/matching_service.py`: Auto-resolve `kode_prodi` dan `program_studi` di pipeline matching.
  - `backend/app/services/sync_service.py`: Ekstraksi prodi dari NIM saat insert sync results, list results, get detail, dan export DRAFT Excel.
  - `frontend/lib/prodi.ts` (baru): Helper TypeScript untuk frontend (`resolveKodeProdiFromNim`, `isMcfRelevant`, `getProgramStudiName`).
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`: Integrasi helper prodi untuk ekstraksi NIM di tabel, tampilan Program Studi di tabel dan modal rincian evaluasi.
  - `backend/tests/test_prodi.py` (baru): 4 unit test untuk memverifikasi load config 19 prodi, ekstraksi kode dari contoh NIM (202331243, 202110039), resolusi nama, dan relevansi MCF.
  - `docs/18_CHANGELOG.md`: Pencatatan changelog.
- **Tes terakhir:**
  - `pytest tests -q` — 153 PASS (0 failed).
  - `npm run typecheck` — PASS (0 errors).
  - `npm run build` — PASS (10 rute Next.js terkompilasi optimal).
- **Blocker:** Tidak ada blocker teknis.
- **Berikutnya:** Siap digunakan dalam proses upload data wisuda dan sinkronisasi live.

## 2026-10-13 — Perbaikan .gitignore (secret, log, artefak lokal)

- **Status:** SELESAI
- **Tahap:** Menutup celah push secret/artefak: audit `git status`, `git ls-files`, dan `git check-ignore` lalu melengkapi `.gitignore`.
- **Perubahan:**
  - `.gitignore`: tambah `frontend/.env`, `frontend/.env.local`, `*.xlsx`/`*.xls`/`data/`, `*.log`, `.playwright-cli/`, `.commandcode/`, `.kilo/`, `asset.png`, `venv/`/`backend/.venv/`, `frontend/out|build`, `dist/`, `.turbo/`, coverage.
  - Untrack (staged delete) 3 `.pyc` yang terlanjur ter-commit.
- **Tes terakhir:** `git check-ignore -v` PASS (8 path cocok); `git ls-files | Select-String pyc` kosong; `git diff --check` hanya 1 temuan lama di `test_validation_engine.py:574` (di luar scope).
- **Blocker:** Tidak ada. Perhatian: `backend/.env` (service-role key) wajib dirotasi bila pernah ter-push — keputusan pemilik project.
- **Berikutnya:** Commit `.gitignore` + untrack `.pyc`, lalu lanjutkan antrian Prompt berikutnya.

## 2026-10-13 — Revisi aturan pencocokan Wisuda→SITASI→Certiport

- **Status:** SELESAI (aturan diterapkan, test PASS). Belum UAT visual.
- **Tahap:** Selaraskan aturan pencocokan dengan ketentuan pemilik (hasil klarifikasi).
- **Perubahan:**
  - `backend/app/services/matching_service.py` (update): `sitasi_matched` (NIM+nama), status SITASI cukup, fallback Certiport dengan verifikasi nama, fuzzy per kata + saran kandidat mirip, gate MCF (kode 31/32), konflik → PERLU_VERIFIKASI.
  - `backend/tests/test_validation_engine.py`, `backend/tests/test_certiport_matching.py` (update): harapan lama diperbarui + kasus baru (NIM+nama, SITASI cukup, fallback Certiport, saran nama mirip, gate MCF).
  - Tanpa perubahan skema DB: `mcf_status` disimpan `null` untuk prodi non-relevan.
- **Tes terakhir:** `pytest tests -q` — 157 PASS.
- **Blocker:** Perlu restart backend port 8000 agar berlaku, dan UAT visual.
- **Berikutnya:** `npm run typecheck`/`build`, E2E browser, dan perbarui `docs/06_BUSINESS_RULES.md`.

## 2026-10-14 — Pencocokan nama Certiport wajib minimal 2 kata

- **Status:** SELESAI (aturan + test). Belum UAT visual.
- **Tahap:** Mengetatkan pencocokan nama Certiport agar kandidat dengan hanya 1 kata mirip tidak lagi dianggap kandidat.
- **Perubahan:**
  - `backend/app/services/matching_service.py`: `_find_certiport_candidates_fuzzy` gating minimal 2 kata (`NAME_MIN_MATCHING_WORDS`), helper `_name_word_tokens` + `_count_matching_name_words` (toleran typo, `NAME_WORD_MATCH_THRESHOLD = 85`), field `matched_words` pada kandidat. Nama target 1 kata memakai batas 1.
  - `backend/tests/test_certiport_matching.py`: 4 regression test baru.
  - `docs/06_BUSINESS_RULES.md`: §3 aturan `MIN_TWO_WORDS`.
  - `docs/18_CHANGELOG.md`: entri 2026-10-14.
- **Tes terakhir:** `pytest tests -q` — 161 PASS (4 test baru).
- **Blocker:** Tidak ada blocker teknis. Perlu restart backend port 8000 agar berlaku dan UAT visual. Catatan keputusan terbuka: apakah kandidat yang lolos 2 kata boleh naik ke `VALID` (saat ini tetap `PERLU_VERIFIKASI` sesuai ADR-004).
- **Berikutnya:** Restart backend + UAT visual pada layar review sinkronisasi.

## 2026-10-14 — Nama satu kata tahan tanda baca/kurung

- **Status:** SELESAI (aturan + test). Belum UAT visual.
- **Tahap:** Menangani nama wisuda satu kata (mis. `DAVID`) yang di SITASI/Certiport ditulis berhias, mis. `( DAVID.)`.
- **Perubahan:**
  - `backend/app/services/matching_service.py`: `_get_nama_normalized` + `build_certiport_name_index` menormalkan ulang nilai tersimpan (idempoten); `_name_word_tokens` menormalkan sebelum tokenisasi.
  - `backend/tests/test_certiport_matching.py`: 3 regression test baru.
  - `docs/06_BUSINESS_RULES.md`: aturan `DECORATION_FOLD` (§3.6).
  - `docs/18_CHANGELOG.md`: entri 2026-10-14.
- **Tes terakhir:** `pytest tests -q` — 164 PASS (3 test baru).
- **Blocker:** Tidak ada blocker teknis. Perlu restart backend port 8000 dan UAT visual.
- **Berikutnya:** Restart backend + UAT visual pada layar review sinkronisasi.

## 2026-10-14 — Detail bukti: deduplikasi + rujukan baris xlsx

- **Status:** SELESAI (kode + test). Belum UAT visual.
- **Tahap:** Modal detail menampilkan dua kartu MOS·Word ganda (id database sebagai "Baris #"); kini hanya yang lulus tampil + badge menunjuk file xlsx dan baris aslinya.
- **Perubahan:**
  - `backend/app/services/sync_service.py`: `dedupe_evidence_for_display` (tampil yang lulus, `duplicate_count`) + `attach_evidence_source_refs` (resolve `source_row` + `file_name` master, koreksi label FAIL).
  - `backend/tests/test_sync_service.py`: mock `in_` + 2 test baru.
  - `frontend/lib/api.ts`, `sinkronisasi/[id]/page.tsx`: badge `namafile.xlsx · Baris #X` + catatan duplikat.
  - `docs/18_CHANGELOG.md`: entri 2026-10-14.
- **Tes terakhir:** `pytest tests -q` — 166 PASS; `npm run typecheck` — PASS.
- **Blocker:** Tidak ada. Perlu restart backend + UAT visual modal detail (kasus ELIZA: 1 kartu Word PASS + badge `data_certiport.xlsx · Baris #…`).
- **Berikutnya:** Restart backend + UAT visual, lalu lanjutkan antrian Prompt.

## 2026-10-19 — Pengesahan ADR-005 (Alias Ujian) & Penanganan Sub-Program "Tidak Diketahui"

- **Status:** SELESAI
- **Tahap:** Pengesahan resmi ekuivalensi alias ujian Word 2019 / Excel 2019 / Azure AI-900 (ADR-005) dan eliminasi degradasi status kelulusan akibat rekaman pendaftaran awal "Tidak Diketahui" (PENDING).
- **Perubahan:**
  - `backend/app/services/matching_service.py`: `EXAM_ALIAS_STATUS = "APPROVED"`, `PLACEHOLDER_SUB_PROGRAMS`, logika pengecualian placeholder pending pada `_build_program_summary` ketika mahasiswa memiliki rekaman ujian konkret.
  - `docs/20_OUTPUT_MAPPING_APPROVAL.md` & `docs/14_DECISIONS.md`: Pengesahan resmi ADR-005 dicatat di dokumen tata kelola institusi.
  - `backend/tests/test_certiport_matching.py` & `backend/tests/test_validation_engine.py`: Pembaruan test suite untuk status APPROVED dan penambahan unit test kasus pendaftaran ganda (Hendrawan).
  - `docs/18_CHANGELOG.md`: Pencatatan changelog.
- **Tes terakhir:** `pytest tests -q` — 167 PASS (100% passed); live sync session `717c64be-17df-4040-8901-40f3fb99d647` berhasil memvalidasi 39 mahasiswa ke status `VALID` (naik dari 16).
- **Blocker:** Tidak ada blocker teknis. Persetujuan ADR-003 (format ekspor) tetap menjadi gate untuk ekspor final.
- **Berikutnya:** Pengujian verifikasi visual pada antarmuka web dan persiapan UAT final.

## 2026-10-19 — Label Hasil Bahasa Manusia & Workbook Validasi Wisuda (Lokal)

- **Status:** SELESAI (kode + test + berkas pratinjau lokal). Belum UAT dan belum di-commit.
- **Tahap:** Menyediakan rekap validasi 424 baris wisuda dengan label `Lulus` / `Tidak Lulus` / `Tidak Ada` / `Perlu Verifikasi` / `Menunggu Hasil`, plus pratinjau isi kolom `Sertifikasi MOS`, `Sertifikasi MCF`, dan `Title Microsoft` (format Opsi 1A dan 4A ADR-003) berlabel DRAFT.
- **Perubahan:**
  - `backend/app/services/matching_service.py`: `STATUS_LABELS` + `status_label()` (lapisan tampilan; status inti 5 nilai tidak diubah).
  - `backend/scripts/generate_validation_workbook.py` (baru): generator workbook pratinjau dari tiga berkas lokal memakai `validate_wisuda_complete`; 10 sheet; self-check jumlah baris dan daftar label.
  - `backend/tests/test_matching_service.py`: 2 test baru untuk `status_label()`.
  - `docs/18_CHANGELOG.md`: entri 2026-10-19.
- **Bukti:** `pytest tests -q` — 169 PASS. Generator dijalankan: `Lulus=39`, `Tidak Lulus=29`, `Perlu Verifikasi=81`, `Menunggu Hasil=1`, `Tidak Ada=274`. Uji silang dengan 18 baris berlabel manual pada `data_wisuda.xlsx`: 17 cocok, 1 berbeda (`202011018` → `Perlu Verifikasi`, benar menurut aturan fuzzy tidak auto-valid). Berkas keluaran: `hasil_validasi_wisuda.xlsx` (terabaikan `.gitignore`).
- **Blocker:** Tidak ada blocker teknis. ADR-003/006/010/011 masih terbuka, sehingga isi kolom target pada workbook ini hanya DRAFT dan belum boleh dipakai sebagai berkas wisuda final.
- **Berikutnya:** Konfirmasi ke pembimbing untuk 82 baris berlabel `Perlu Verifikasi`/`Menunggu Hasil` (50 nama Certiport ganda, 21 konflik bukti, 9 nama mirip, 1 PENDING) dan 1 baris yang berbeda dari label manual, lalu tentukan apakah antarmuka web juga memakai label bahasa manusia.

## 2026-10-19 — Koreksi Keterangan Bukti Valid pada Sheet Detail

- **Status:** SELESAI (kode + berkas pratinjau lokal). Belum UAT dan belum di-commit.
- **Tahap:** Memberbaiki keterangan pada sheet detail yang menyebut "konflik sumber" padahal bukti terakhir sebenarnya valid (SITASI LULUS + Certiport PASS dengan skor identik), sementara status tetap `Perlu Verifikasi` sesuai instruksi pemilik.
- **Perubahan:**
  - `backend/scripts/generate_validation_workbook.py`: `corrected_reason()` (kode alasan `R01_VALID` + keterangan "VALID: ..."), `corrected_row_codes()` (selaras kode alasan tingkat baris), `corrected_valid_notes()` (catatan pada `Catatan Review` dan `Catatan Perbedaan`), `certiport_status_for_exam()` (perbaikan kolom `Status Certiport` yang sebelumnya `-`).
  - `docs/18_CHANGELOG.md`: entri 2026-10-19.
  - Mesin pencocokan (`backend/app/services/matching_service.py`) tidak diubah: aturan konflik sumber §6 tetap berlaku, hanya pembacaan keterangannya yang dikoreksi.
- **Bukti:** `pytest tests -q` — 169 PASS. Distribusi `Kode Alasan` pada `Detail Ujian`: `R01_VALID` 83 → 89, `R04_CERTIPORT_NO_PASS` 5 → 0. Status tingkat baris tidak berubah (`Lulus=39`, `Tidak Lulus=29`, `Perlu Verifikasi=81`, `Menunggu Hasil=1`, `Tidak Ada=274`). 6 baris terkoreksi: `202214003`, `201921053`, `202131039`, `202131073`, `202131135`, `202131155`.
- **Blocker:** Tidak ada blocker teknis. Status 6 baris tersebut sengaja tetap `Perlu Verifikasi` sampai petugas memastikan attempt terakhir.
- **Berikutnya:** Petugas memeriksa attempt FAIL lama pada 6 baris tersebut (rincian attempt ada di `Detail Certiport`); bila attempt terakhir memang PASS, status dapat dinaikkan pada tahap berikutnya dengan persetujuan pemilik.

## 2026-10-23 — Penyederhanaan Sistem: Admin-Only, Hapus Landing Page & Login/Register

- **Status:** SELESAI
- **Tahap:** Penyederhanaan seluruh arsitektur sistem menjadi berfokus pada inti validasi data, pengalihan rute awal langsung ke halaman validasi data (`/sinkronisasi`), eliminasi fitur login dan register, penerapan role tunggal Admin, dan pembuatan SQL pembaruan Supabase.
- **Perubahan:**
  - `frontend/app/page.tsx`: Hapus landing page dan alihkan langsung ke `/sinkronisasi`.
  - `frontend/app/(dashboard)/layout.tsx`: Hapus proteksi auth guard `verifyStaffRoute`.
  - `frontend/proxy.ts`: Hapus session cookie check dan alihkan `/login` ke `/sinkronisasi`.
  - `frontend/lib/api.ts`: Hapus login token requirement pada `authorizedHeaders()`.
  - `frontend/components/dashboard-shell.tsx`: Sesuaikan identitas ke Administrator ITCC (Admin) dan hilangkan tombol Logout.
  - `frontend/components/sidebar-nav.tsx`: Letakkan "Validasi Wisuda" di posisi teratas.
  - `frontend/app/login/page.tsx` & `unauthorized/page.tsx`: Alihkan ke `/sinkronisasi`.
  - `backend/app/core/auth.py`: Mengembalikan `DEFAULT_ADMIN_PRINCIPAL` secara langsung tanpa barrier 401/403.
  - `backend/app/api/v1/endpoints/auth.py`: `/auth/me` mengembalikan Admin; `/auth/register` dinonaktifkan (HTTP 400).
  - `backend/app/services/sync_service.py`: Default role submit_review menjadi `"admin"`.
  - `database/UPDATE_SIMPLIFY_ADMIN_ONLY.sql`: Skrip SQL migrasi siap salin-tempel di SQL Editor Supabase.
  - `database/SETUP_ALL_TABLES.sql`: Master SQL diselaraskan dengan constraint role tunggal admin.
- **Tes terakhir:** `venv/Scripts/python.exe -m pytest tests -q` — 158 PASS; `npm run typecheck` — PASS; `npm run build` — PASS.
- **Blocker:** Tidak ada blocker teknis. Pemilik project dapat langsung menyalin isi `database/UPDATE_SIMPLIFY_ADMIN_ONLY.sql` ke SQL Editor Supabase.
- **Berikutnya:** Jalankan skrip SQL di dashboard Supabase jika database aktif ingin diselaraskan dengan schema baru.

## 2026-10-23 — Skema ringkas & auto-isi kolom Wisuda (LULUS saja)

- **Status:** SELESAI (kode + test + generator lokal). UAT browser/Supabase runtime belum.
- **Tahap:** Menyesuaikan sistem dengan `data_sitasi.xlsx` dan `data_certiport.xlsx` yang kini hanya memuat kolom berguna, lalu mengisi `data_wisuda` hanya untuk status LULUS.
- **Perubahan:**
  - `backend/app/services/import_service.py`: parser skema ringkas + fallback Certiport lama.
  - `backend/app/services/matching_service.py`: NIM exact, kategori MOS/MCF, exact name Certiport, helper isian.
  - `backend/app/services/sync_service.py`: ekspor final aktif, hanya VALID yang diisi.
  - `backend/scripts/generate_validation_workbook.py`: generator baru `hasil_wisuda_terisi.xlsx`.
  - `frontend/.../master-data-page.tsx`, `sinkronisasi/[id]/page.tsx`, `lib/api.ts`: kolom & ekspor disesuaikan.
  - Dokumen: `05`, `06`, `08`, `14`, `20`, `23`, `24`.
- **Tes terakhir:** `venv/Scripts/python.exe -m pytest tests -q` — 165 PASS. Generator: total 424, MOS lulus 67, MCF lulus 38, tanpa isian 344.
- **Blocker:** UAT visual browser dan runtime Supabase development berizin belum dijalankan. `npm run typecheck` — PASS; `npm run build` — PASS (10 rute).
- **Berikutnya:** UAT browser dan impor batch asli pada environment berizin.

## 2026-10-23 — Perbaikan Bug Perubahan Status Hasil pada Review Manual Detail

- **Status:** SELESAI
- **Tahap:** Mengatasi bug sinkronisasi status hasil (`validation_status`, `mos_status`, `mcf_status`, `sync_evidence`, serta render tabel dan modal) saat petugas melakukan review manual pada detail mahasiswa.
- **Perubahan:**
  - `backend/app/services/sync_service.py` (`submit_review`): Menyelaraskan status `mos_status`, `mcf_status`, `mos_programs`, `mcf_programs`, serta `evidence_status` pada `sync_evidence`.
  - `backend/app/api/v1/endpoints/sync.py`: Mendukung opsi `target_program` pada schema dan endpoint review.
  - `backend/tests/test_review.py`: Menambahkan tes unit untuk verifikasi pembaruan status MOS/MCF dan evidence (14 PASS).
  - `frontend/lib/api.ts`: Mengirimkan parameter `targetProgram` saat simpan review.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
    - Memperbaiki `openDetailModal` agar status default keputusan review diselaraskan dengan status mahasiswa.
    - Menambahkan pemilih program sertifikasi yang ditargetkan untuk prodi dengan kewajiban MCF.
    - Memperbaiki `handleReviewSubmit` agar langsung memperbarui seluruh properti baris tabel di latar belakang (`mos_status`, `mcf_status`, `validation_status`, `needs_review`) dan modal secara reaktif tanpa perlu me-refresh halaman.
- **Tes terakhir:** `pytest tests -q` — 167 PASS; `npm run typecheck` — PASS; `npm run build` — PASS.
- **Blocker:** Tidak ada blocker teknis.
- **Berikutnya:** Uji coba visual alur konfirmasi dan penolakan manual pada browser.


## 2026-10-23 — Perbaikan identitas Certiport (false positive nama parsial)

- **Status:** SELESAI (kode + unit test + verifikasi kasus nyata). UAT browser belum.
- **Tahap:** Memisahkan pencocokan identitas dari validasi sertifikasi. Kandidat fuzzy tidak lagi menjadi evidence/exam/skor milik mahasiswa.
- **Perubahan:** `matching_service.py` (exact token identity, token-coverage fuzzy score, konflik NIM, R15/R16, audit kandidat), `import_service.py` (validasi nilai wajib kosong), `sync_service.py` (nama file audit + `name_match_type`), generator lokal, test.
- **Tes terakhir:** `venv/Scripts/python.exe -m pytest tests -q` — 177 PASS. Verifikasi kasus NIM 202310129: `PERLU_VERIFIKASI`, `mos_status=DATA_TIDAK_DITEMUKAN`, `exams=[]`, kandidat `Muhammad Akbar` skor 67.
- **Blocker:** UAT visual modal review dan runtime Supabase development berizin belum dijalankan.
- **Berikutnya:** UAT modal review untuk memastikan kandidat tidak tampil sebagai skor mahasiswa; impor batch asli di environment berizin.

## 2026-10-26 — Pengecekan Sertifikasi MTCNA untuk Prodi 31 & 32 & Penyesuaian Kolom Title

- **Status:** SELESAI
- **Tahap:** Mengakomodasi sertifikasi MTCNA bagi mahasiswa S1 Teknik Informatika (31) dan S1 Sistem Informasi (32) sebagai alternatif pilihan selain MCF, pengecekan langsung via data SITASI tanpa Certiport, penyesuaian kolom `Sertifikasi MCF/MTCNA`, penyederhanaan kolom `Title Microsoft` menjadi `Title`, serta pencantuman gelar `MTCNA` pada kolom `Title` jika lulus MTCNA.
- **Perubahan:**
  - `backend/app/services/wisuda_validation_service.py`: Template `WISUDA_COLUMNS` memakai `Sertifikasi MCF/MTCNA` dan `Title`, serta kompatibel mundur dengan template legasi (`Title Microsoft`, `Sertifikasi MCF`).
  - `backend/app/services/matching_service.py`:
    - `_cross_validate_exam` memvalidasi MTCNA langsung dari rekaman SITASI (tanpa mencari ke Certiport).
    - `validate_wisuda_complete` menggabungkan evaluasi MCF & MTCNA untuk prodi 31/32 (lulus salah satu = syarat terpenuhi `VALID`).
    - `build_wisuda_fill_values` menghasilkan `MCF (Lulus)`, `MTCNA (Lulus)`, atau keduanya, dan menambahkan `TITLE_MTCNA = "MTCNA"` ke kolom `Title` jika lulus MTCNA (misal: "MOS, MTCNA", "MOS, MCF, MTCNA", atau "MTCNA").
  - `backend/app/services/sync_service.py`: Pemetaan `mcf_programs` mencakup MTCNA, dan header ekspor diselaraskan ke `Sertifikasi MCF/MTCNA` dan `Title`.
  - `backend/scripts/generate_validation_workbook.py`: Penyelarasan header target `Sertifikasi MCF/MTCNA`, resolusi `Title` / `Title Microsoft`, dan pembacaan `mcf_programs`.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`: Label tabel `Sertifikasi MCF/MTCNA` dan `Title`, pembaruan fungsi title untuk menampilkan badge `MTCNA`, dan modal review target.
  - `backend/tests/test_validation_engine.py`: +5 unit test pengujian kelulusan MTCNA, pemilihan MCF vs MTCNA, kelulusan ganda, proteksi prodi non-relevan, serta validasi gelar Title MTCNA.
  - `backend/tests/test_export_gate.py`: Penyelarasan header ekspor menjadi `("Sertifikasi MOS", "Sertifikasi MCF/MTCNA", "Title")`.
  - `docs/18_CHANGELOG.md`: Pencatatan changelog.
- **Tes terakhir:**
  - `backend/venv/Scripts/python.exe -m pytest tests -q` — 182 PASS (100% passed).
  - `npm run typecheck` — PASS (0 errors).
- **Blocker:** Tidak ada blocker teknis.
- **Berikutnya:** Validasi visual hasil sinkronisasi pada peramban dan ekspor berkas wisuda terisi.

## 2026-10-26 — Perbaikan Filter Status Hasil Sinkronisasi & Interaktivitas KPI Cards

- **Status:** SELESAI
- **Tahap:** Perbaikan filter status pada halaman detail hasil sinkronisasi (`/sinkronisasi/[id]`) agar terpusat pada status hasil sinkronisasi (`VALID`, `PERLU_VERIFIKASI`, `DATA_TIDAK_DITEMUKAN`), menjadikan kartu KPI interaktif sebagai tombol filter langsung, dan menampilkan indikator status hasil pada tabel.
- **Perubahan:**
  - `backend/app/services/sync_service.py` (`list_sync_results`): Filter `status="PERLU_VERIFIKASI"` mencakup baris `PERLU_VERIFIKASI` dan `TIDAK_LULUS` sehingga selaras dengan metrik `session.total_review`.
  - `backend/tests/test_sync_service.py`: Penambahan unit test untuk filter `status="PERLU_VERIFIKASI"`.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`:
    - Kartu KPI ringkasan (Total Mahasiswa, Valid, Perlu Verifikasi, Tidak Ditemukan) kini dapat diklik langsung untuk memfilter tabel dengan ring status aktif.
    - Dropdown filter status diselaraskan menampilkan jumlah baris per kategori serta tombol reset.
    - Menghilangkan bentrok checkbox `needsReviewOnly` dengan filter status.
    - Kolom nama mahasiswa dilengkapi badge status hasil (`Perlu Verifikasi` atau `Tidak Ditemukan`).
- **Tes terakhir:**
  - `backend/venv/Scripts/python.exe -m pytest tests -q` — 182 PASS (100% passed).
  - `npm run typecheck` — PASS (0 errors).
- **Blocker:** Tidak ada blocker teknis.
- **Berikutnya:** UAT interaktif filter status dan kartu KPI pada peramban web.

## 2026-10-26 — Penambahan Filter Program Sertifikasi (MOS / MCF / MTCNA)

- **Status:** SELESAI
- **Tahap:** Penambahan filter program sertifikasi (`MOS`, `MCF`, `MTCNA`) pada halaman detail hasil sinkronisasi agar pengguna dapat memfilter baris mahasiswa berdasarkan sertifikasi yang diambil/dimiliki.
- **Perubahan:**
  - `backend/app/services/sync_service.py`: Deteksi program melalui `_row_has_program` dan penanganan parameter `program` pada `list_sync_results`.
  - `backend/app/api/v1/endpoints/sync.py`: Dukungan query parameter `program` pada endpoint `/results`.
  - `backend/tests/test_sync_service.py` & `test_sync_api.py`: Unit test filter program.
  - `frontend/lib/api.ts`: Penambahan parameter `program` pada `getSyncResults`.
  - `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`: Penambahan select dropdown `Program:` dan integrasi tombol reset filter.
- **Tes terakhir:**
  - `backend/venv/Scripts/python.exe -m pytest tests -q` — 182 PASS (100% passed).
  - `npm run typecheck` — PASS (0 errors).
- **Blocker:** Tidak ada blocker teknis.
- **Berikutnya:** Validasi visual alur filter program gabungan pada peramban web.
