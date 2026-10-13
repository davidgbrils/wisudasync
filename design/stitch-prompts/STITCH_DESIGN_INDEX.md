# STITCH Design Index — ITCC Wisuda Sync

Dokumen ini menjelaskan urutan penggunaan prompt desain di Google Stitch. Setiap file `.md` berisi **satu prompt lengkap untuk satu screen**.

---

## Cara Menggunakan Prompt di Google Stitch

1. Buka [Google Stitch](https://stitch.withgoogle.com).
2. Buat project baru atau buka project yang sudah ada.
3. Pilih opsi **"Buat layar dari teks"** atau **"Design from prompt"**.
4. Buka salah satu file `*_SCREEN.md` di bawah.
5. Salin **seluruh isi file** (Ctrl+A, Ctrl+C).
6. Tempel ke kolom prompt di Google Stitch.
7. Klik **Generate** / **Buat desain**.

> **Penting:** Setiap file hanya untuk satu screen. Jangan menyalin dua file sekaligus ke satu prompt.

---

## Urutan Screen dan File

| Urutan | File | Screen | Route Implementasi | Status Kode |
|--------|------|--------|--------------------|-------------|
| 0 | `00_DESIGN_SYSTEM.md` | Design system & tokens | — | Referensi |
| 1 | `01_LOGIN_SCREEN.md` | Login petugas | `/login` | Sudah ada |
| 2 | `02_DASHBOARD_SCREEN.md` | Ringkasan data master | `/dashboard` | Sudah ada |
| 3 | `03_SITASI_MASTER_SCREEN.md` | Data master SITASI | `/sitasi` | Sudah ada |
| 4 | `04_CERTIPORT_MASTER_SCREEN.md` | Data master Certiport | `/certiport` | Sudah ada |
| 5 | `05_WISUDA_UPLOAD_SCREEN.md` | Upload & validasi wisuda | `/sinkronisasi` | Sudah ada |
| 6 | `06_SYNC_RESULTS_SCREEN.md` | Hasil sinkronisasi | `/sinkronisasi/{id}` | Sudah ada |
| 7 | `07_RESULT_REVIEW_SCREEN.md` | Detail & verifikasi baris | Dialog pada hasil | Sudah ada |
| 8 | `08_SYNC_HISTORY_SCREEN.md` | Riwayat sesi sinkronisasi | `/riwayat` | Sudah ada |

---

## Urutan Penggunaan yang Disarankan

Mulai dari screen yang paling sering digunakan atau yang menjadi dasar alur produk:

1. **`01_LOGIN_SCREEN.md`** — Gerbang masuk aplikasi. Desain paling sederhana, baik sebagai titik awal.
2. **`02_DASHBOARD_SCREEN.md`** — Halaman utama yang memuat ringkasan batch aktif.
3. **`03_SITASI_MASTER_SCREEN.md`** dan **`04_CERTIPORT_MASTER_SCREEN.md`** — Manajemen data master. Keduanya berbagi pola komponen yang sama.
4. **`05_WISUDA_UPLOAD_SCREEN.md`** — Proses inti: upload dan validasi workbook wisuda.
5. **`06_SYNC_RESULTS_SCREEN.md`** — Tabel hasil sinkronisasi dengan filter dan status.
6. **`07_RESULT_REVIEW_SCREEN.md`** — Panel/dialog verifikasi manual baris yang ambigu.
7. **`08_SYNC_HISTORY_SCREEN.md`** — Tabel riwayat semua sesi yang pernah dijalankan.

---

## Catatan Konsistensi

- Semua screen menggunakan **design tokens yang sama** dari `00_DESIGN_SYSTEM.md`.
- Semua label UI dalam **bahasa Indonesia**.
- Setiap prompt screen menyertakan ringkasan token warna dan tipografi agar dapat digunakan secara mandiri.
- Jangan menggabungkan dua file prompt sekaligus ke satu sesi Stitch.

---

## Status Implementasi Codebase

Berdasarkan audit codebase pada Oktober 2026:

- Seluruh route sudah ada di `frontend/app/(dashboard)/`.
- Komponen sidebar, login form, master data page, upload wisuda, dan tabel hasil sudah diimplementasikan.
- Koneksi ke Supabase runtime belum selesai (menunggu eksekusi `SETUP_ALL_TABLES.sql`).
- Mapping kolom ekspor (`Sertifikasi MOS`, `Sertifikasi MCF`, `Title Microsoft`) belum disahkan (ADR-003 terbuka).
- Tombol ekspor final menampilkan `403` dan harus didesain dalam keadaan nonaktif beserta penjelasan alasan.

---

## Keputusan yang Masih Terbuka (Perlu Dikonfirmasi)

| ADR | Topik | Dampak pada Desain |
|-----|-------|-------------------|
| ADR-003 | Mapping kolom ekspor final | Tombol ekspor tetap nonaktif |
| ADR-005 | Ekuivalensi ujian MOS/MCF antar sumber | Label ujian pada screen verifikasi |
| ADR-006 | Definisi `Title Microsoft` | Kolom tabel ekspor |
| ADR-009 | Siapa yang boleh melakukan review | Tampilan tombol keputusan |
| ADR-011 | Kewajiban MOS/MCF per prodi | Label ringkasan hasil |
