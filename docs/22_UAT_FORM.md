# 22 — Formulir UAT (User Acceptance Test) & Serah Terima

> ## STATUS: **BELUM SIAP PRODUCTION**
> Formulir ini **belum dijalankan** pada lingkungan berizin dan **belum ditandatangani** petugas ITCC. Sistem **tidak boleh di-deploy** ke production sampai seluruh kasus UAT di bawah berstatus `PASS` serta lembar pengesahan (Bagian 12) ditandatangani. Ekspor final aktif sejak 2026-10-23 dan hanya mengisi status LULUS.

Dokumen ini adalah lembar kerja UAT petugas ITCC untuk ITCC Wisuda Sync, mengikuti `docs/10_TEST_PLAN.md`, `docs/15_ACCEPTANCE.md`, `docs/11_SECURITY_PRIVACY.md`, dan hasil pengujian teknis Tahap 15 (`docs/21_TEST_RESULTS.md`). UAT menguji skenario nyata petugas di browser, berbeda dari unit/integration test yang sudah dijalankan.

- **Tanggal penyusunan:** 2026-10-09
- **Tahap:** 16 — UAT & persiapan serah terima
- **Peran penguji:** Petugas ITCC (browser) + pendamping teknis (backend/log)
- **Lingkungan target:** Supabase development **berizin** + backend FastAPI + frontend Next.js

---

## 1. Petunjuk Pengisian & Aturan Data

1. Isi kolom **Hasil Aktual**, **Bukti Screenshot (disensor)**, **Keputusan Petugas**, dan **Tanggal** hanya setelah kasus benar-benar dijalankan. Jangan menulis `PASS` untuk kasus yang belum dijalankan.
2. **Data sintetis wajib** digunakan untuk seluruh latihan: gunakan fixture anonim (contoh `NIM=209900001`, `Nama=MAHASISWA CONTOH`).
3. **Data asli hanya atas izin tertulis** dari ITCC/BAA. Jika digunakan: simpan di lingkungan internal berizin, jangan commit, jangan unggah ke hosting publik, dan sensor (blur) seluruh NIM/nama pada screenshot.
4. Setiap screenshot disensor di kolom **Bukti** (tulis nama file, mis. `bukti/UAT-MATCH-02_disensor.png`) — jangan tempel data pribadi di dokumen ini.
5. Status yang diperbolehkan per kasus: `PASS`, `FAIL`, `SEBAGIAN`, `BELUM DIJALANKAN`, `TIDAK RELEVAN`. Kegagalan wajib dicatat: severity, langkah reproduksi, dampak, bukti.
6. Simpan versi kode/commit yang diuji pada Bagian 3 agar hasil dapat direproduksi.

---

## 2. Lingkungan & Prasyarat UAT

| Item | Nilai | Bukti |
|---|---|---|
| Versi kode / commit | `______________` | `git rev-parse HEAD` |
| Tanggal & waktu uji | `______________` | — |
| URL frontend | `______________` | — |
| URL backend API | `______________` | — |
| Project Supabase (dev berizin) | `______________` | — |
| Rotasi service-role key lama | `Sudah / Belum` | Konfirmasi pemilik (temuan P0) |
| Migration SQL dijalankan di DB dev | `Sudah / Belum` | `database/migrations/*` |
| Akun petugas `staff` (fixture) | `______________` | — |
| Akun `admin` (fixture) | `______________` | — |
| Dataset: master SITASI | `sitasi_dummy.xlsx` (sintetis) | — |
| Dataset: master Certiport | `certiport_dummy.xlsx` (sintetis) | — |
| Dataset: Wisuda | `wisuda_dummy.xlsx` (sintetis) | — |

Prasyarat teknis (dari Tahap 15, sudah lulus lokal): 134 backend test **PASS** (2.87 s), `npm run typecheck` **PASS**, `npm run build` **PASS**. Runtime SQL Supabase dan smoke test browser **BELUM DIJALANKAN** karena kredensial dev berizin belum tersedia.

---

## 3. Matriks Skenario UAT Petugas

Kolom wajib: **Kasus · Expected · Actual · Bukti Screenshot (disensor) · Keputusan Petugas · Tanggal.**

### A. Autentikasi & Sesi

| ID | Kasus (Langkah) | Expected | Actual | Bukti (disensor) | Keputusan Petugas | Tanggal |
|---|---|---|---|---|---|---|
| UAT-AUTH-01 | Login dengan akun petugas `staff` sah | Masuk `/dashboard`, token Supabase aktif, `/auth/me` mengembalikan profil | _Belum dijalankan_ | — | — | — |
| UAT-AUTH-02 | Logout dari aplikasi | Sesi dihapus; akses `/dashboard` dialihkan ke `/login` | _Belum dijalankan_ | — | — | — |
| UAT-AUTH-03 | Buka halaman terproteksi tanpa login | Dialihkan ke `/login`; API tanpa token mengembalikan `401` | _Belum dijalankan_ | — | — | — |
| UAT-AUTH-04 | Login dengan akun non-petugas (tanpa profil berizin) | Akses ke `/unauthorized`; API mengembalikan `403` | _Belum dijalankan_ | — | — | — |
| UAT-AUTH-05 | Token kedaluwarsa (tunggu/paksa kedaluwarsa) | Sesi diperbarui atau dialihkan ke login; tanpa kebocoran token di layar | _Belum dijalankan_ | — | — | — |

### B. Impor Data Master

| ID | Kasus (Langkah) | Expected | Actual | Bukti (disensor) | Keputusan Petugas | Tanggal |
|---|---|---|---|---|---|---|
| UAT-MASTER-01 | Impor `sitasi_dummy.xlsx` (sheet `Master_Data`, 10 header) | Batch `COMPLETED`; jumlah baris & `source_row` sesuai; NIM nol awal utuh | _Belum dijalankan_ | — | — | — |
| UAT-MASTER-02 | Impor `certiport_dummy.xlsx` (sheet `Results (264) Plus`) | Batch `COMPLETED`; nama & result dinormalisasi | _Belum dijalankan_ | — | — | — |
| UAT-MASTER-03 | Impor file dengan header/sheet salah (mis. `Sub Program` dihapus) | Ditolak dengan pesan jelas; batch tidak aktif | _Belum dijalankan_ | — | — | — |
| UAT-MASTER-04 | Impor file rusak / >10 MiB / bermacro `.xlsm` | Ditolak (`400`/`413`); batch aktif lama tetap utuh | _Belum dijalankan_ | — | — | — |
| UAT-MASTER-05 | Pencarian/filter/paginasi pada halaman SITASI & Certiport | Hanya batch **aktif** yang tampil; filter `nim`/`nama`/`sertifikasi`/`status` benar | _Belum dijalankan_ | — | — | — |

### C. Upload Wisuda & Validasi

| ID | Kasus (Langkah) | Expected | Actual | Bukti (disensor) | Keputusan Petugas | Tanggal |
|---|---|---|---|---|---|---|
| UAT-WIS-01 | Upload `wisuda_dummy.xlsx` lalu "Validasi file" | Ringkasan baris, susunan 8 kolom, masalah per baris tanpa PII; batch master aktif tampil | _Belum dijalankan_ | — | — | — |
| UAT-WIS-02 | Upload file dengan NIM kosong/ganda/formula | Ditandai masalah (`INVALID_NIM`/`DUPLICATE_NIM`/`REQUIRED_VALUE`); tidak dikarang | _Belum dijalankan_ | — | — | — |
| UAT-WIS-03 | Proses sinkronisasi penuh (tombol "Proses Sinkronisasi") | Sesi dibuat `COMPLETED`, arahkan ke `/sinkronisasi/[id]`; snapshot batch SITASI & Certiport tercatat | _Belum dijalankan_ | — | — | — |
| UAT-WIS-04 | Proses saat salah satu batch master belum ada | Ditolak dengan pesan "batch aktif belum lengkap"; tidak ada sesi separuh jadi | _Belum dijalankan_ | — | — | — |

### D. Matching: Multi-Attempt, Konflik Nama, Verifikasi

| ID | Kasus (Langkah) | Expected | Actual | Bukti (disensor) | Keputusan Petugas | Tanggal |
|---|---|---|---|---|---|---|
| UAT-MATCH-01 | NIM dengan banyak attempt (FAIL, FAIL, LULUS) ujian sama | Seluruh attempt terambil; bukti LULUS tidak tertimpa; status per ujian sesuai | _Belum dijalankan_ | — | — | — |
| UAT-MATCH-02 | Konflik nama: nama Wisuda berbeda dari SITASI (NIM sama) | Perbedaan dicatat sebagai flag; NIM tetap kunci; `needs_review` menyala bila bermakna | _Belum dijalankan_ | — | — | — |
| UAT-MATCH-03 | Dua kandidat Certiport nama identik | Ambigu → `PERLU_VERIFIKASI`; **tidak** auto `VALID` | _Belum dijalankan_ | — | — | — |
| UAT-MATCH-04 | Kandidat hanya cocok fuzzy (skor tinggi) | `PERLU_VERIFIKASI`; skor fuzzy bukan kepastian identitas | _Belum dijalankan_ | — | — | — |
| UAT-MATCH-05 | NIM tidak ada di SITASI | `DATA_TIDAK_DITEMUKAN`; SITASI tidak dilewati otomatis | _Belum dijalankan_ | — | — | — |
| UAT-MATCH-06 | SITASI `LULUS` + Certiport `PASS` + alias ujian cocok | `VALID` hanya bila alias disahkan; alias `DRAFT` → `PERLU_VERIFIKASI` | _Belum dijalankan_ | — | — | — |
| UAT-MATCH-07 | SITASI gagal + Certiport `PASS` (konflik sumber) | `PERLU_VERIFIKASI` dengan reason code | _Belum dijalankan_ | — | — | — |
| UAT-MATCH-08 | Buka modal detail bukti per baris | Menampilkan bukti SITASI & Certiport, source_row, skor, alasan deterministik | _Belum dijalankan_ | — | — | — |

### E. Verifikasi Manual (Review) & Audit

| ID | Kasus (Langkah) | Expected | Actual | Bukti (disensor) | Keputusan Petugas | Tanggal |
|---|---|---|---|---|---|---|
| UAT-REVIEW-01 | Petugas pilih `TUNDA_VERIFIKASI` / `TIDAK_COCOK` + catatan | Status terbarui; catatan & identitas petugas + waktu tersimpan | _Belum dijalankan_ | — | — | — |
| UAT-REVIEW-02 | Staf biasa pilih `KONFIRMASI_COCOK` saat ADR-009 belum disahkan | Ditolak (mode pending/read-only) `403` | _Belum dijalankan_ | — | — | — |
| UAT-REVIEW-03 | Admin melakukan `KONFIRMASI_COCOK` | Boleh; konfirmasi identitas **tidak** mengubah FAIL menjadi PASS | _Belum dijalankan_ | — | — | — |
| UAT-REVIEW-04 | Submit keputusan tanpa catatan | Ditolak validasi `422` | _Belum dijalankan_ | — | — | — |
| UAT-REVIEW-05 | Review bertahap dua kali pada baris sama | Setiap transisi tercatat append-only; bukti sumber tidak berubah | _Belum dijalankan_ | — | — | — |

### F. Ekspor

| ID | Kasus (Langkah) | Expected | Actual | Bukti (disensor) | Keputusan Petugas | Tanggal |
|---|---|---|---|---|---|---|
| UAT-EXP-01 | Unduh Excel Final | Berkas `.xlsx` delapan kolom Wisuda; kolom target terisi hanya untuk LULUS | _Belum dijalankan_ | — | — | — |
| UAT-EXP-02 | Periksa baris tidak lulus | Kolom `Sertifikasi MOS`, `MCF`, dan `Title Microsoft` kosong | _Belum dijalankan_ | — | — | — |
| UAT-EXP-03 | Unduh pratinjau DRAFT | Berkas berlabel `[DRAFT]`; susunan kolom dipertahankan | _Belum dijalankan_ | — | — | — |
| UAT-EXP-04 | Periksa sel target yang sudah terisi sebelumnya | Berkas keluaran baru; `data_wisuda.xlsx` asli tidak ditimpa (ADR-010) | _Belum dijalankan_ | — | — | — |

### G. Sesi Lama & Riwayat

| ID | Kasus (Langkah) | Expected | Actual | Bukti (disensor) | Keputusan Petugas | Tanggal |
|---|---|---|---|---|---|---|
| UAT-HIST-01 | Aktifkan batch master baru, lalu buka sesi lama di `/riwayat` | Detail sesi lama tetap merujuk snapshot `sitasi_import_id`/`certiport_import_id` lama | _Belum dijalankan_ | — | — | — |
| UAT-HIST-02 | Buka dua sesi berbeda | Riwayat terpisah; filter status/perlu review & paginasi konsisten | _Belum dijalankan_ | — | — | — |
| UAT-HIST-03 | Logout lalu login lagi dan buka riwayat | Data sesi tetap ada; akses terkontrol | _Belum dijalankan_ | — | — | — |

**Ringkasan skenario:** 5 (auth) + 5 (master) + 4 (wisuda) + 8 (matching) + 5 (review) + 4 (ekspor) + 3 (sesi lama) = **34 kasus**.

---

## 4. Tinjauan Kontrol Akses

| Aspek | Kriteria Lulus | Hasil | Bukti |
|---|---|---|---|
| Endpoint tanpa token | `401` pada `/sitasi`, `/certiport`, `/sync*`; hanya `/health` publik | `BELUM DIJALANKAN` (runtime) | `tests/test_auth.py` |
| Non-petugas terautentikasi | `403`; `authenticated` saja tidak cukup | `BELUM DIJALANKAN` (runtime) | `tests/test_auth.py` |
| Secret hanya di backend | Service-role key tidak pernah di frontend/`NEXT_PUBLIC_*` | Perlu verifikasi | `docs/11` §4 |
| RLS tabel publik | Aktif, tanpa policy `anon`/`authenticated`; hanya `service_role` | `BELUM DIJALANKAN` (SQL runtime) | migration + `database/checks` |
| Kepemilikan `result_id` | Detail/export memvalidasi relasi ke `session_id` | `BELUM DIJALANKAN` (runtime) | `tests/test_sync_api.py` |
| Rotasi credential P0 | Service-role key lama sudah dirotasi pemilik | `TERBLOKIR` | `docs/19` Prompt 01 |

## 5. Tinjauan Audit

| Aspek | Kriteria Lulus | Hasil | Bukti |
|---|---|---|---|
| Jejak keputusan review | `review_audit` append-only: pelaku, waktu, keputusan, catatan, transisi status | `BELUM DIJALANKAN` (runtime) | migration `..._review_audit.sql`; `tests/test_review.py` |
| Bukti sumber tidak termutasi | `sync_evidence` tidak berubah oleh review | `BELUM DIJALANKAN` | `tests/test_review.py` |
| Riwayat sesi | `sync_sessions`/`sync_results` terekam dengan snapshot batch | `BELUM DIJALANKAN` | `tests/test_sync_service.py` |
| Token tidak di-log | Tidak ada token/data PII di log server | Perlu verifikasi | `docs/11` §6 |
| Tidak pakai `user_metadata` untuk izin | Otorisasi dari tabel `profiles` | Lulus desain | `backend/app/core/auth.py` |

## 6. Tinjauan Kebijakan Retensi & Backup

| Aspek | Kriteria | Status | Catatan |
|---|---|---|---|
| Lokasi file asli | Tidak di repo/git/hosting publik; tempat internal berizin | **TERBUKA (ADR-007)** | `docs/14`, `docs/11` §7 |
| Lama retensi per jenis data | Ditetapkan ITCC (jangan mengarang 30/90 hari) | **BELUM DITETAPKAN** | Butuh keputusan pembimbing |
| Backup | Lokasi, frekuensi, dan pemulihan ditetapkan | **BELUM DITETAPKAN** | Menunggu kebijakan ITCC |
| Penghapusan batch | Siapa berwenang & mekanisme hapus/retensi | **BELUM DITETAPKAN** | ADR-007 |
| Bucket Storage (jika dipakai) | Private, akses server-side | **BELUM DIVERIFIKASI** | `docs/11` §4 |

> Catatan: selama retensi/backup belum ditetapkan, **jangan** unggah data asli dan **jangan** aktifkan ekspor final.

## 7. Tinjauan Performa Aktual

| Metrik | Nilai Terukur | Metode | Catatan |
|---|---|---|---|
| Backend test suite | 134 PASS dalam **2.87 s** | `pytest -q` (lokal, fixture) | Bukti Tahap 15/16 |
| Frontend typecheck | PASS (~beberapa detik) | `npm run typecheck` | Lokal |
| Frontend production build | PASS | `npm run build` | Lokal (Tahap 15) |
| Waktu proses sinkronisasi (runtime, per N baris) | **BELUM DIUKUR** | UAT di lingkungan berizin | Butuh DB dev |
| Waktu impor master (runtime) | **BELUM DIUKUR** | UAT di lingkungan berizin | Butuh DB dev |
| Ukuran/jumlah baris maksimum aman | **BELUM DIUKUR** | UAT | Batas upload 10 MiB |

> Angka suite test adalah bukti lokal, **bukan** performa sistem berjalan. Catat jumlah baris, waktu proses, konflik, dan pesan error saat UAT berjalan (`docs/10` §6).

## 8. Tinjauan Pemetaan Output yang Disetujui

| Topik | ADR | Status | Dampak |
|---|---|---|---|
| Format kolom `Sertifikasi MOS` & `MCF` | ADR-003 | **TERBUKA (BLOCKED)** | Ekspor final diblokir |
| Ekuivalensi alias & versi ujian | ADR-005 | **TERBUKA (DRAFT)** | Semua alias → `PERLU_VERIFIKASI` |
| Definisi `Title Microsoft` | ADR-006 | **TERBUKA (BLOCKED)** | Kolom tidak diisi otomatis |
| Perlakuan sel sudah terisi | ADR-010 | **TERBUKA (BLOCKED)** | Dilarang overwrite tanpa persetujuan |
| Syarat sertifikasi per prodi | ADR-011 | **TERBUKA (BLOCKED)** | Sistem tidak menyimpulkan kelulusan wisuda |
| Lembar pengesahan `docs/20_OUTPUT_MAPPING_APPROVAL.md` | — | **BELUM DITANDATANGANI** | Gate ekspor final aktif (403) |

**Kesimpulan:** belum ada satu pun pemetaan output yang disetujui → ekspor final tidak boleh dibuka.

## 9. Checklist Penerimaan (Acceptance) — Ringkasan UAT

Mengacu `docs/15_ACCEPTANCE.md`; centang hanya bila dibuktikan pada UAT.

| Kategori | Item Kunci | Status | Bukti |
|---|---|---|---|
| A. Data master | Impor valid, header salah ditolak, batch gagal aman, normalisasi NIM | `BELUM DIVERIFIKASI END-TO-END` | UAT-MASTER-01..05 |
| B. Keamanan | Login, 401/403, secret server-side, file tidak publik | `BELUM SELESAI DI RUNTIME` | UAT-AUTH-01..05 |
| C. Matching | Multi-attempt, konflik nama, fuzzy→review, VALID bersyarat | `BELUM DIVERIFIKASI END-TO-END` | UAT-MATCH-01..08 |
| D. Review & Ekspor | Catatan+audit, format output disetujui, draft vs final | `SEBAGIAN (ekspor final terkunci)` | UAT-REVIEW/EXP |
| E. Laporan | Screenshot disensor, tabel hasil aktual | `DALAM PERSIAPAN` | folder `bukti/` |

---

## 10. Temuan Selama UAT (Log Defect)

| Defect ID | Kasus Terkait | Severity | Deskripsi | Langkah Reproduksi | Dampak | Status |
|---|---|---|---|---|---|---|
| — | — | — | _Belum ada UAT dijalankan_ | — | — | — |

---

## 11. Ringkasan Eksekusi

| Kelompok | Jumlah Kasus | PASS | FAIL | SEBAGIAN | BELUM DIJALANKAN |
|---|---|---|---|---|---|
| A. Autentikasi & Sesi | 5 | 0 | 0 | 0 | 5 |
| B. Impor Master | 5 | 0 | 0 | 0 | 5 |
| C. Upload Wisuda | 4 | 0 | 0 | 0 | 4 |
| D. Matching | 8 | 0 | 0 | 0 | 8 |
| E. Review & Audit | 5 | 0 | 0 | 0 | 5 |
| F. Ekspor | 4 | 0 | 0 | 0 | 4 |
| G. Sesi Lama | 3 | 0 | 0 | 0 | 3 |
| **Total** | **34** | **0** | **0** | **0** | **34** |

---

## 12. Lembar Pengesahan UAT & Status Production

**Status production saat ini: _BELUM SIAP PRODUCTION_.**

Sistem belum siap production karena: (1) 34 kasus UAT belum dijalankan pada lingkungan berizin; (2) migration SQL & RLS belum pernah dieksekusi pada PostgreSQL Supabase; (3) smoke test browser setelah login belum dilakukan; (4) credential P0 belum dikonfirmasi dirotasi; (5) kebijakan retensi/backup belum ditetapkan (ADR-007); (6) pemetaan output final belum disetujui (`docs/20`). **Jangan lakukan deployment.**

| Pihak | Nama | NIP / Identitas | Tanda Tangan | Tanggal |
|---|---|---|---|---|
| Kepala ITCC | ______________________ | _________________ | [                ] | ____/____/2026 |
| Pembimbing Project | ______________________ | _________________ | [                ] | ____/____/2026 |
| Petugas ITCC (penguji) | ______________________ | _________________ | [                ] | ____/____/2026 |

UAT dapat dinyatakan **lulus** hanya jika seluruh kasus prioritas tinggi berstatus `PASS`, log defect bersih atau defect tersisa ekonomis, dan lembar ini ditandatangani. Sampai saat itu, kesimpulan resmi tetap: **BELUM SIAP PRODUCTION**.
