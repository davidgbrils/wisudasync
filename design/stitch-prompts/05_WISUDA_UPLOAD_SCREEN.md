# Prompt Desain Google Stitch — Screen 05: Halaman Upload & Validasi Wisuda

> **Instruksi penggunaan:** Salin seluruh isi file ini dan tempel ke kolom prompt Google Stitch. File ini hanya untuk satu screen. Jangan menggabungkannya dengan prompt lain.

---

## Konteks Produk

**ITCC Wisuda Sync** adalah aplikasi web internal. Halaman Upload & Validasi Wisuda (`/sinkronisasi`) adalah titik awal proses utama sistem. Petugas mengunggah file Excel data wisuda, sistem memvalidasinya, dan setelah siap, petugas memulai proses sinkronisasi.

Alur kerja halaman ini:
1. Petugas memilih atau menyeret file `.xlsx` ke area dropzone.
2. Klik "Validasi File" → server memeriksa header, NIM, dan kesiapan batch master.
3. Hasil validasi ditampilkan: ringkasan kolom, jumlah baris, status batch SITASI dan Certiport.
4. Jika semua siap → tombol "Mulai Sinkronisasi" aktif.
5. Klik "Mulai Sinkronisasi" → proses dimulai → setelah selesai, diarahkan ke halaman hasil.

---

## Instruksi untuk Google Stitch

Buat **hanya satu screen**: halaman Upload & Validasi Wisuda. Jangan mendesain halaman hasil sinkronisasi atau halaman lain dalam desain ini.

---

## Pengguna dan Tugas Utama

**Pengguna:** Petugas ITCC yang sudah login.
**Tugas utama:** Mengunggah file Excel wisuda dan memulai proses sinkronisasi data.

---

## Shell Layout

```
┌──────────────────────────────────────────────────────────┐
│ HEADER: [W] ITCC Wisuda Sync                    [Keluar] │
├────────────┬─────────────────────────────────────────────┤
│  SIDEBAR   │  KONTEN UTAMA                               │
│  Ringkasan │                                             │
│ ○ Validasi │                                             │
│  Riwayat   │                                             │
│  SITASI    │                                             │
│  Certiport │                                             │
└────────────┴─────────────────────────────────────────────┘
```

- Item "Validasi" (Validasi Wisuda) disorot aktif di sidebar.

---

## Konten Halaman Upload & Validasi Wisuda

### 1. Header Halaman

- Label kecil atas: "SINKRONISASI", uppercase, IBM Plex Sans 11 px, warna `#0F766E`.
- Judul H1: **"Validasi & Sinkronisasi Wisuda"**, IBM Plex Sans Semibold 24 px, warna `#172321`.
- Deskripsi: "Unggah workbook Excel wisuda, periksa validasi, lalu jalankan proses pencocokan data.", 13 px, warna `#66736F`.

### 2. Kartu Upload File (Dropzone)

Kartu besar dengan area drag-and-drop:
- Background: `#FFFFFF`. Border: `2px dashed #DDE4E1`. Border radius: 12 px.
- Area tengah dropzone (padding besar, min-height 180 px):
  - Ikon upload (panah ke atas dalam lingkaran), outline, 40×40 px, warna `#0F766E`.
  - Teks utama: "Seret dan lepas file Excel wisuda ke sini", IBM Plex Sans Medium 15 px, warna `#172321`.
  - Teks kecil: "atau gunakan tombol di bawah", 13 px, warna `#66736F`.
  - Format yang didukung: ".xlsx · Batas ukuran: 10 MiB", 12 px, warna `#66736F`.
  - Tombol "Pilih File Excel" di bawah teks (sekunder, border, `border-radius: 8 px`).
- State dragging (saat file diseret ke atas area): border menjadi `2px dashed #0F766E`, `bg: #ECFAF8`, warna ikon lebih gelap.
- State file dipilih: area dropzone berubah menjadi ringkasan file:
  - Ikon file Excel.
  - Nama file: "data_wisuda.xlsx", IBM Plex Sans Medium 14 px.
  - Ukuran file: "2,3 MiB", warna `#66736F`.
  - Tombol ×/ganti file di pojok kanan.

### 3. Pesan Error File

Tampil di bawah kartu dropzone jika file tidak valid:
- Background `#FFF1F2`, border `1px #FECDD3`, teks `#9F1239`.
- Contoh: "Pilih file dengan format .xlsx." atau "Ukuran file melebihi batas 10 MiB."
- Border radius: 8 px.

### 4. Tombol Validasi File

- Tombol "Validasi File" (primer, `bg: #0F766E`), lebar penuh atau min 180 px.
- Disabled jika belum ada file terpilih.
- State loading: "Memvalidasi…" + spinner kecil.

### 5. Panel Hasil Validasi (Muncul Setelah Validasi)

Kartu hasil validasi dengan beberapa sub-bagian:

**Sub-bagian A: Ringkasan File**
- Judul H2: "Hasil Validasi File".
- Grid 2 kolom:
  - "Baris Mahasiswa": **424** (angka dummy)
  - "Baris Kosong": **0**
  - "Status Header": ✓ "Kolom lengkap" atau ✗ "Kolom hilang: [nama]"
  - "Format": "Excel .xlsx"

**Sub-bagian B: Status Kesiapan Master Data**
- Judul kecil: "Kesiapan Batch Master".
- Dua baris (atau kartu kecil):
  - **Batch SITASI:** Badge "Aktif" hijau + "7.449 baris" (atau badge "Belum tersedia" abu + "Belum ada batch aktif").
  - **Batch Certiport:** Badge "Aktif" hijau + "264 baris" (atau badge "Belum tersedia" abu).
- Jika salah satu batch belum tersedia: tampilkan teks peringatan amber, mis. "Batch Certiport belum tersedia. Sinkronisasi mungkin tidak lengkap. Impor data Certiport terlebih dahulu.", dengan tautan ke halaman Certiport.

**Sub-bagian C: Masalah Validasi** (opsional, tampil jika ada)
- Daftar masalah per baris:
  - "Baris 5: NIM kosong"
  - "Baris 12: Format NIM tidak aman (mengandung formula)"
- Jika tidak ada masalah: tampilkan tanda centang hijau dan teks "Tidak ada masalah validasi ditemukan."

**Sub-bagian D: Tombol Aksi**
- Tombol "Mulai Sinkronisasi" (primer, `bg: #0F766E`), aktif hanya jika:
  - Header lengkap.
  - Tidak ada masalah kritis.
  - Minimal batch SITASI aktif.
- State loading sinkronisasi: "Memproses…" + spinner. Tombol disabled.
- Di bawah tombol, teks kecil: "Proses sinkronisasi tidak dapat dibatalkan setelah dimulai.", warna `#66736F`.

---

## State yang Harus Ditampilkan

Buat beberapa frame/state berbeda:

1. **State awal (kosong)**: Dropzone kosong, tidak ada panel validasi. Tombol validasi disabled.
2. **State file terpilih**: File nama tampil di dropzone. Tombol validasi aktif.
3. **State sedang memvalidasi**: Tombol "Memvalidasi…" + spinner, panel validasi belum muncul.
4. **State validasi berhasil + batch siap**: Panel validasi tampil dengan semua indikator hijau, tombol "Mulai Sinkronisasi" aktif.
5. **State validasi berhasil + batch belum siap**: Peringatan amber untuk batch yang belum ada. Tombol sinkronisasi tetap ada tetapi bisa dengan peringatan.
6. **State error file**: Pesan error merah di bawah dropzone. Panel validasi tidak muncul.
7. **State sedang sinkronisasi**: Tombol "Memproses…", loading, semua aksi dinonaktifkan.

---

## Catatan Desain Penting

- **Jangan** menampilkan progress bar dengan persentase (mis. "67% selesai") — sistem tidak menyediakan data ini.
- **Jangan** menampilkan estimasi waktu proses.
- **Jangan** menampilkan spinner yang tidak jujur seolah ada kemajuan terukur.
- Teks deskripsi format ditulis apa adanya: ".xlsx" — bukan "Excel, CSV, PDF".
- Jika ada masalah validasi, tampilkan nomor baris spesifik, bukan pesan generik.

---

## Design Tokens (Ringkasan untuk Prompt Ini)

```
Background halaman  : #F5F7F6
Surface/kartu       : #FFFFFF
Teks utama          : #172321
Teks sekunder       : #66736F
Aksen utama         : #0F766E
Border              : #DDE4E1
Dropzone border     : 2px dashed #DDE4E1
Dropzone drag bg    : #ECFAF8  |  Dropzone drag border: 2px dashed #0F766E
Badge Aktif bg      : #ECFDF5  |  Badge Aktif teks   : #065F46
Peringatan bg       : #FFFBEB  |  Peringatan teks    : #92400E  |  Peringatan border: #FCD34D
Error bg            : #FFF1F2  |  Error teks         : #9F1239  |  Error border     : #FECDD3
Font UI             : IBM Plex Sans
Border radius       : 8–12 px
```

---

## Responsif

| Layar | Perilaku |
|-------|----------|
| ≥ 1024 px | Konten terpusat, max-width sekitar 800 px, sidebar vertikal |
| 768–1023 px | Konten penuh lebar, sidebar tersembunyi → nav horizontal |
| < 768 px | Konten 1 kolom, panel validasi full lebar |

---

## Aksesibilitas

- Area dropzone dapat diakses via keyboard (tombol "Pilih File Excel" sebagai alternatif).
- Semua state mempunyai teks yang jelas (bukan hanya perubahan warna).
- Tombol disabled menggunakan `aria-disabled` dan cursor: not-allowed.
- Pesan error menggunakan `role="alert"`.
- Pesan status menggunakan `role="status"`.

---

## Instruksi Final untuk Google Stitch

Buat tepat **satu screen halaman Upload & Validasi Wisuda** yang menampilkan:
1. Shell layout: header + sidebar (Validasi Wisuda disorot) + konten.
2. Header halaman dengan judul dan deskripsi.
3. Kartu dropzone besar dengan area drag-and-drop, teks panduan, dan tombol "Pilih File Excel".
4. Tampilkan frame state utama: "validasi berhasil dengan semua siap" — panel validasi tampil dengan ringkasan file, status batch SITASI aktif dan Certiport belum tersedia (dengan peringatan amber), dan tombol "Mulai Sinkronisasi" aktif.
5. Tampilkan frame alternatif: "state awal kosong" dan "file terpilih belum divalidasi".
6. Gunakan design tokens, gaya Swiss Minimalism, semua teks bahasa Indonesia. Tidak ada progress bar palsu.
