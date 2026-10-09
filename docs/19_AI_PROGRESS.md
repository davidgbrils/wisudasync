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
- **Berikutnya:** Tahap 14 — Penyempurnaan UAT, skenario uji komprehensif, dan persiapan serah terima ke lingkungan berizin.
