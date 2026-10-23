# 25: Laporan Magang (Kerangka BAB I-V)

Judul usulan: *Perancangan dan Implementasi Sistem Sinkronisasi Data Sertifikasi Mahasiswa pada Data Wisuda Menggunakan SITASI dan Certiport Berbasis Web*

Catatan penulisan: Kerangka ini mengikuti pedoman `docs/13_REPORT_MAGANG.md` dan aturan kampus. Laporan ini tidak memuat klaim penyelesaian fitur atau hasil pengujian yang belum pernah dieksekusi secara nyata, sebagaimana ditegaskan pada bagian Pernyataan Kejujuran Data.

---

## BAB I: Pendahuluan

### 1.1 Latar Belakang
Penyelesaian administrasi wisuda membutuhkan verifikasi sertifikasi kompetensi mahasiswa secara teliti. Petugas akademik harus memadankan daftar calon wisudawan dengan rekaman kelulusan pada dua sumber terpisah: SITASI yang mencatat NIM dan riwayat attempt ujian, serta Certiport yang hanya mencatat nama peserta tanpa informasi NIM.

Proses pemeriksaan manual lintas berkas rentan menimbulkan kesalahan. Satu NIM kerap memiliki beberapa rekaman attempt ujian dengan status kelulusan berbeda. Selain itu, penulisan nama peserta pada Certiport sering memiliki variasi kapitalisasi, singkatan, atau tanda baca, sementara penamaan modul ujian tidak selalu identik antara kedua sistem sumber.

Sistem ini dibangun untuk membantu staf memproses pencocokan data secara berulang, terdokumentasi, dan tetap memberi ruang keputusan verifikasi manual. Pencocokan utama dilakukan berdasarkan exact NIM terhadap basis data SITASI, sedangkunivan data Certiport digunakan sebagai verifikasi sekunder melalui kecocokan nama ternormalisasi dan modul ujian. Seluruh baris yang ambigu ditandai agar ditinjau langsung oleh petugas. Laporan ini tidak mencantumkan klaim efisiensi waktu karena belum dilakukan pengukuran empiris di lapangan.

### 1.2 Rumusan Masalah
1. Bagaimana merancang dan membangun aplikasi web pengolah workbook wisuda berbasis integrasi SITASI dan Certiport?
2. Bagaimana menyusun algoritma pencocokan identitas berbasis NIM serta memvalidasi data ujian Certiport yang tidak memiliki atribut NIM?
3. Bagaimana menyajikan draf hasil verifikasi dan mengelola antrean review manual dalam format berkas Excel?

### 1.3 Batasan Masalah
- Berkas masukan menggunakan format Excel workbook `.xlsx` tanpa macro `.xlsm`, dengan cakupan ujian Microsoft Office Specialist (MOS) dan Microsoft Certified Fundamentals (MCF).
- Impor data SITASI dan Certiport dilakukan secara luring (offline import) dari berkas ekspor resmi tanpa scraping atau koneksi API langsung ke vendor.
- Hak akses sistem dibatasi untuk satu kelompok pengguna, yaitu staf operasional ITCC berwenang.
- Sistem tidak menggunakan modul LLM atau OCR. Pencocokan teks berderajat kemiripan (fuzzy matching) hanya berfungsi memberikan saran kandidat bagi petugas.
- Keputusan administratif kelulusan yudisium tetap berada di bawah wewenang pimpinan fakultas atau universitas.

### 1.4 Tujuan dan Manfaat
Tujuan proyek ini adalah membangun aplikasi web yang mampu mencocokkan data calon wisudawan dengan rekaman SITASI dan Certiport, mendokumentasikan status per sub-ujian secara deterministik, serta menyediakan antrean review dan ekspor draf Excel.

Manfaat potensial sistem mencakup kemudahan penelusuran status sertifikasi, keteraturan pencatatan riwayat sinkronisasi, dan penyediaan draf kerja yang mempercepat tugas verifikasi staf akademik.

---

## BAB II: Gambaran umum tempat magang dan dasar teori

### 2.1 Profil instansi
Bagian ini diisi sesuai data profil resmi unit ITCC dari instansi tempat magang, meliputi struktur organisasi, visi, misi, dan lingkup layanan teknologi informasi kampus.

### 2.2 Tugas dan alur kerja magang
Aktivitas magang difokuskan pada analisis kebutuhan integrasi data wisuda, perancangan skema pangkalan data, implementasi modul pencocokan deterministik di backend, serta pembangunan antarmuka web responsif bagi staf verifikator sesuai log kegiatan mingguan.

### 2.3 Dasar teori
- Konsep rekayasa perangkat lunak berbasis web dan arsitektur client-server.
- Bahasa pemrograman Python dan kerangka kerja FastAPI untuk layanan web berkinerja tinggi.
- Manipulasi data tabular menggunakan pustaka Pandas dan OpenPyXL.
- Kerangka kerja Next.js App Router, TypeScript, dan Tailwind CSS untuk antarmuka pengguna.
- Basis data relasional PostgreSQL dengan platform Supabase untuk autentikasi dan kontrol akses tingkat baris (Row Level Security).
- Teknik pencocokan deterministik, normalisasi string teks, serta algoritma RapidFuzz untuk penentuan kandidat nama.
- Metodologi pengujian perangkat lunak mencakup unit testing, integration testing, dan black-box testing.

---

## BAB III: Analisis dan perancangan

### 3.1 Analisis proses berjalan
Proses verifikasi sertifikasi sebelumnya dilakukan melalui perbandingan visual manual antar-berkas Excel yang membutuhkan ketelitian tinggi dan rentan terhadap inkonsistensi data ketika volume wisudawan meningkat, sebagaimana diuraikan dalam dokumen `docs/01_PROJECT_CHARTER.md` dan `docs/02_PRD.md`.

### 3.2 Kebutuhan fungsional dan nonfungsional
Spesifikasi sistem mengacu pada dokumen `docs/03_SRS.md`, mencakup 20 kebutuhan fungsional (FR-001 hingga FR-020) terkait otentikasi, manajemen master data, validasi berkas, mesin pencocokan, audit review, dan ekspor. Kebutuhan nonfungsional meliputi aspek keamanan, integritas data tanpa penimpaan destruktif, akurasi deterministik, dan ketersediaan jejak audit.

### 3.3 Perancangan sistem
Arsitektur aplikasi menerapkan pola tiga lapis, yaitu browser antarmuka Next.js yang berkomunikasi dengan FastAPI backend, kemudian FastAPI mengakses PostgreSQL Supabase menggunakan service-role key terisolasi (`docs/04_ARCHITECTURE.md`). Algoritma pencocokan mengutamakan exact string NIM untuk data SITASI dengan evaluasi batas nilai 700 pada seluruh rekaman attempt. Data Certiport dipadankan melalui normalisasi nama dan sub-ujian. Kasus ambigu secara otomatis diarahkan ke status PERLU_VERIFIKASI.

### 3.4 Perancangan basis data
Struktur pangkalan data tersusun atas delapan tabel utama, yaitu `profiles`, `data_imports`, `sitasi_data`, `certiport_data`, `sync_sessions`, `sync_results`, `sync_evidence`, dan `review_audit`. Mekanisme pergantian batch master data dijamin konsisten dan atomik melalui stored procedure `complete_data_import` dengan indeks unik parsial pada batch aktif.

### 3.5 Perancangan Antarmuka
Desain antarmuka menerapkan prinsip kegunaan enterprise berbasis palet warna institusi dengan navigasi modul terstruktur, formulir unggah interaktif, tabel data padat informasi, kartu ringkasan status batch, serta panel laci untuk peninjauan bukti verifikasi (`docs/09_UI_UX_SPEC.md`).

---

## BAB IV: Implementasi dan pengujian

### 4.1 Lingkungan Pengembangan
Pengembangan dilakukan menggunakan Python 3.12, Node.js 22, sistem operasi Windows, backend FastAPI dengan Supabase, serta frontend Next.js 16, React 19, dan Tailwind CSS. Detail konfigurasi pustaka tercantum pada dokumen panduan operator `docs/24_OPERATOR_GUIDE.md`.

### 4.2 Implementasi Backend
Backend dibangun dengan pembagian modul yang jelas:
- Autentikasi dan verifikasi token staf di `backend/app/core/auth.py`.
- Manajemen impor berkas dan pergantian batch atomik di `backend/app/services/import_service.py`.
- Mesin validasi berkas wisuda dan logika pencocokan deterministik di `backend/app/services/matching_service.py` dan `backend/app/services/wisuda_validation_service.py`.
- Pengelolaan sesi sinkronisasi, pencatatan review, dan penguncian ekspor di `backend/app/services/sync_service.py`.
- Rute endpoint RESTful di `backend/app/api/v1/endpoints/`.

### 4.3 Implementasi Frontend
Antarmuka pengguna diimplementasikan menggunakan Next.js App Router dengan dukungan rendering terisolasi:
- Shell aplikasi responsif dan navigasi di `frontend/components/dashboard-shell.tsx` dan `frontend/components/sidebar-nav.tsx`.
- Halaman ringkasan operasional di `frontend/app/(dashboard)/dashboard/page.tsx`.
- Modul pengelolaan master data SITASI dan Certiport di `frontend/components/master-data-page.tsx`.
- Alur unggah dan validasi berkas wisuda di `frontend/app/(dashboard)/sinkronisasi/page.tsx`.
- Tampilan detail hasil sinkronisasi, filter status, dan drawer review staf di `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx`.
- Riwayat sesi sinkronisasi di `frontend/app/(dashboard)/riwayat/page.tsx`.

### 4.4 Hasil Pengujian
Seluruh pengujian otomatis dijalankan secara lokal menggunakan berkas pengujian sintetis yang telah disamarkan tanpa menyertakan data pribadi mahasiswa nyata.

| Jenis pengujian | Perintah eksekusi | Hasil | Catatan evaluasi |
|---|---|---|---|
| Unit dan API backend | `pytest -q` | 134 PASS (sekitar 2.87 detik) | Menggunakan mock Supabase dan fixture anonim |
| Typecheck frontend | `npm run typecheck` | PASS (0 kesalahan) | Validasi tipe data TypeScript statis |
| Production build frontend | `npm run build` | PASS (10 rute terkompilasi) | Next.js 16 App Router |
| Matriks uji test plan | Pengujian internal | 24 kasus tercatat di docs/21 | Skenario normal, duplikat, dan batas nilai |
| Runtime DB Supabase | Akses database live | Belum dijalankan | Menunggu alokasi basis data berizin |
| UAT antarmuka peramban | Alur operasional staf | Belum dijalankan | Mengacu pada formulir docs/22_UAT_FORM.md |

Contoh format tabel pengujian fungsional black-box untuk pelaksanaan UAT mendatang:

| ID uji | Skenario pengujian | Berkas masukan | Tindakan staf | Hasil diharapkan | Status uji |
|---|---|---|---|---|---|
| TC-IMP-01 | Impor data master SITASI | `sitasi_dummy.xlsx` | Unggah melalui UI | Batch COMPLETED dan aktif | Belum diuji |
| TC-MAT-02 | Verifikasi mahasiswa multi-attempt | Data uji anonim | Proses sinkronisasi | Nilai tertinggi tersimpan | Belum diuji |
| TC-EXP-02 | Pengamanan ekspor final tanpa izin | Sesi sinkronisasi | Klik ekspor final | Akses ditolak status 403 | Belum diuji |

### 4.5 Bukti tangkapan layar antarmuka
Seluruh tangkapan layar sistem wajib disensor pada bagian identitas pribadi (NIM dan nama mahasiswa) sebelum dilampirkan dalam berkas laporan akhir.

| No | Nama antarmuka | Berkas tangkapan layar | Objek yang wajib disensor |
|---|---|---|---|
| 1 | Halaman login staf | `01_login.png` | Alamat surel petugas |
| 2 | Ringkasan operasional | `02_dashboard.png` | Tidak ada data personal |
| 3 | Kelola data SITASI | `03_sitasi.png` | Kolom NIM dan nama mahasiswa |
| 4 | Kelola data Certiport | `04_certiport.png` | Kolom nama lengkap peserta |
| 5 | Unggah dan validasi wisuda | `05_upload.png` | Nama berkas dan identitas mahasiswa |
| 6 | Hasil sinkronisasi dan filter | `06_hasil.png` | Kolom NIM dan nama wisudawan |
| 7 | Panel review dan bukti verifikasi | `07_review.png` | Rincian identitas mahasiswa |
| 8 | Riwayat sesi sinkronisasi | `08_riwayat.png` | Nama berkas yang memuat informasi sensitif |
| 9 | Ekspor draf dan kunci final | `09_export.png` | Data ringkasan personal |

Pengambilan tangkapan layar aktual dilakukan setelah lingkungan pengujian terhubung dan sesi UAT resmi dilaksanakan bersama pihak unit magang.

---

## BAB V: Penutup

### 5.1 Kesimpulan
Berdasarkan hasil perancangan dan implementasi pada BAB IV, hal yang telah terbukti secara teruji adalah:
1. Layanan backend (autentikasi, impor data, pencocokan deterministik, validasi struktur, audit review, dan proteksi ekspor) beserta antarmuka web frontend berhasil lulus 134 uji otomatis, uji tipe data statis, dan kompilasi produksi dengan data sintetis.
2. Alur logika rekonsiliasi data calon wisudawan berhasil dipetakan secara terstruktur sesuai arsitektur sistem.
Adapun aspek yang belum diuji secara empiris mencakup eksekusi skema basis data pada lingkungan Supabase daring dan pelaksanaan uji penerimaan pengguna (UAT) end-to-end. Oleh sebab itu, status kesiapan sistem dinyatakan belum siap untuk lingkungan produksi langsung.

### 5.2 Keterbatasan
Keterbatasan pengembangan saat ini mencakup penggunaan data uji sintetis dalam pengujian otomatis, belum tersedianya lingkungan pangkalan data daring untuk pengujian akses langsung, ketiadaan data acuan historis untuk menghitung metrik akurasi numerik, format pemetaan keluaran final yang masih menunggu persetujuan pimpinan, serta penetapan kebijakan pencadangan dan retensi data yang belum disahkan.

### 5.3 Saran
Untuk kelanjutan pengembangan sistem, disarankan agar unit kerja menyediakan akses basis data Supabase development yang terisolasi, menyelenggarakan sesi pengujian UAT bersama staf verifikator, meresmikan format baku pemetaan kolom ekspor final, serta mengesahkan prosedur operasional standar mengenai retensi dan pembersihan data wisuda.

---

## Lampiran A: Matriks fitur, kode, pengujian, dan bukti

| Fitur spesifikasi | Berkas kode utama | Pengujian otomatis | Status bukti |
|---|---|---|---|
| Login dan kontrol akses (FR-001/002) | `backend/app/core/auth.py`, `frontend/proxy.ts`, `frontend/app/(dashboard)/layout.tsx` | `tests/test_auth.py` | 20 test PASS, typecheck PASS |
| Impor SITASI dan Certiport (FR-003/004) | `backend/app/services/import_service.py`, `endpoints/sitasi.py`, `endpoints/certiport.py` | `tests/test_import_service.py` | 13 test PASS |
| Batch aktif dan atomik (FR-008) | `database/migrations/20260930120000_*.sql`, `import_service.py` | `tests/test_import_service.py` | Test RPC rollback PASS |
| Pencarian dan paginasi master (FR-009) | `backend/app/services/master_query_service.py`, `frontend/components/master-data-page.tsx` | `tests/test_sync_api.py` | Typecheck dan build PASS |
| Validasi berkas wisuda (FR-010) | `backend/app/services/wisuda_validation_service.py`, `frontend/app/(dashboard)/sinkronisasi/page.tsx` | `tests/test_wisuda_validation.py` | 8 test PASS |
| Pencocokan NIM dan attempt (FR-011/012) | `backend/app/services/matching_service.py` | `tests/test_matching_service.py` | 21 test PASS |
| Pencocokan Certiport dan saran (FR-013/014) | `backend/app/services/matching_service.py` | `tests/test_certiport_matching.py` | 24 test PASS |
| Penentuan status dan kode aturan (FR-015) | `backend/app/services/matching_service.py` | `tests/test_validation_engine.py` | 22 test PASS |
| Antrean review dan jejak audit (FR-016) | `backend/app/services/sync_service.py`, `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx` | `tests/test_review.py` | 12 test PASS |
| Pratinjau dan filter hasil (FR-017) | `frontend/app/(dashboard)/sinkronisasi/[id]/page.tsx` | `tests/test_sync_api.py` | 8 test PASS |
| Ekspor draf dan proteksi final (FR-018) | `backend/app/services/sync_service.py`, `endpoints/sync.py` | `tests/test_export_gate.py` | 6 test PASS (status 403 terkunci) |
| Riwayat sesi sinkronisasi (FR-019/020) | `sync_service.py`, `frontend/app/(dashboard)/riwayat/page.tsx` | `tests/test_sync_service.py` | 7 test PASS |
| Ringkasan operasional dashboard | `frontend/app/(dashboard)/dashboard/page.tsx` | Build dan typecheck | PASS kompilasi Next.js |
| Penyimpanan sesi dan bukti | `database/migrations/20261003120000_*.sql`, `sync_service.py` | `tests/test_sync_service.py` | 15 test PASS |

---

## Lampiran B: Status akhir tahap pengembangan

| Aspek capaian | Status pencapaian | Bukti validasi |
|---|---|---|
| Layanan backend | Terimplementasi penuh dan teruji otomatis | 134 test PASS pada `docs/21_TEST_RESULTS.md` |
| Antarmuka frontend | Terimplementasi penuh dan terkompilasi sukses | `npm run typecheck` dan `build` PASS |
| Migrasi skema SQL | Berkas migrasi siap di folder repository | Direktori `database/migrations/` |
| Runtime live Supabase | Belum diverifikasi pada database aktif | Membutuhkan kredensial server berizin |
| Pengujian penerimaan staf | Belum dilaksanakan | Formulir pengujian di `docs/22_UAT_FORM.md` |
| Ekspor berkas final | Terkunci secara sengaja (HTTP 403) | Menunggu lembar persetujuan `docs/20` |
| Pengukuran performa | Belum diukur secara empiris | Memerlukan data skala nyata |
| Kebijakan retensi data | Belum disahkan unit kerja | Terdaftar pada keputusan ADR-007 |
| Kesiapan lingkungan produksi | BELUM SIAP PRODUCTION | Menunggu integrasi pangkalan data dan UAT |

---

## Lampiran C: Keputusan institusi yang belum final

| Kode keputusan | Topik kebijakan | Kebutuhan konfirmasi institusi |
|---|---|---|
| ADR-003 | Format kolom Sertifikasi MOS dan MCF | Pemilihan aturan penulisan pada draf ekspor final |
| ADR-005 | Standarisasi ekuivalensi sub-ujian | Daftar alias sertifikasi yang diakui resmi |
| ADR-006 | Kriteria pengisian kolom Title Microsoft | Contoh pemetaan keluaran untuk tiap variasi nilai |
| ADR-007 | Prosedur retensi dan backup berkas | Masa penyimpanan data dan kewenangan penghapusan |
| ADR-009 | Hak akses staf peninjau review | Penetapan daftar akun petugas verifikator resmi |
| ADR-010 | Penanganan sel wisuda terisi | Kebijakan penimpaan data yang sudah memiliki nilai |
| ADR-011 | Standar kelulusan per program studi | Penentuan kewajiban sertifikasi per prodi |
| Keamanan | Rotasi service-role key P0 | Verifikasi langsung bersama pemilik proyek |
| Infrastruktur | Akses Supabase development berizin | Penyediaan basis data uji terisolasi |

---

## Pernyataan kejujuran data

1. Seluruh data pengujian yang digunakan bersifat sintetis dan anonim tanpa menampilkan data asli mahasiswa.
2. Capaian kelulusan pengujian otomatis (134 test PASS, typecheck, dan build) merupakan hasil eksekusi lokal pada lingkungan pengembangan, bukan hasil pengujian basis data langsung.
3. Pengujian runtime basis data dan uji peramban UAT secara jujur dinyatakan belum dilaksanakan dan tidak diklaim telah lulus.
4. Nilai kesamaan string tidak dijadikan persentase kebenaran mutlak identitas mahasiswa tanpa adanya data ground truth terverifikasi.
5. Sebelum seluruh pengujian pangkalan data dan sesi UAT selesai dilaksanakan, status akhir sistem secara tegas dinyatakan: BELUM SIAP PRODUCTION.
