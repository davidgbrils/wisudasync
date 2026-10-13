# Prompt Desain Google Stitch — Screen 03: Halaman Data SITASI

> **Instruksi penggunaan:** Salin seluruh isi file ini dan tempel ke kolom prompt Google Stitch. File ini hanya untuk satu screen. Jangan menggabungkannya dengan prompt lain.

---

## Konteks Produk

**ITCC Wisuda Sync** adalah aplikasi web internal. Halaman Data SITASI (`/sitasi`) adalah halaman manajemen data master sertifikasi dari sistem SITASI. Data SITASI diimpor dari file Excel `.xlsx` dengan sheet `Master_Data` dan menjadi sumber utama pencocokan NIM mahasiswa wisuda.

Halaman ini memungkinkan petugas untuk:
- Mengimpor (mengunggah) file Excel SITASI baru sebagai batch aktif baru.
- Melihat informasi batch yang sedang aktif.
- Mencari dan memfilter data mahasiswa dalam batch aktif.
- Melihat isi tabel data SITASI.

---

## Instruksi untuk Google Stitch

Buat **hanya satu screen**: halaman Data SITASI. Jangan mendesain halaman Certiport, Dashboard, atau sinkronisasi dalam desain ini.

---

## Pengguna dan Tugas Utama

**Pengguna:** Petugas ITCC yang sudah login.
**Tugas utama:** Memperbarui data master SITASI dengan file baru dan memeriksa data yang sudah tersimpan.

---

## Shell Layout

```
┌──────────────────────────────────────────────────────────┐
│ HEADER: [W] ITCC Wisuda Sync                    [Keluar] │
├────────────┬─────────────────────────────────────────────┤
│  SIDEBAR   │  KONTEN UTAMA                               │
│            │                                             │
│  Ringkasan │                                             │
│  Validasi  │                                             │
│  Riwayat   │                                             │
│ ○ SITASI   │                                             │
│  Certiport │                                             │
└────────────┴─────────────────────────────────────────────┘
```

- Item "SITASI" disorot aktif di sidebar dengan `bg: #ECFAF8`, teks `#0F4B46`, bar indikator kiri.

---

## Konten Halaman Data SITASI

### 1. Header Halaman

- Label kecil atas: "DATA MASTER", uppercase, IBM Plex Sans 11 px, warna `#0F766E`.
- Judul H1: **"Data SITASI"**, IBM Plex Sans Semibold 24 px, warna `#172321`.
- Deskripsi: "Cari, periksa, atau perbarui batch sumber SITASI.", 13 px, warna `#66736F`.
- Di pojok kanan atas header: badge count total, mis. **"7.449 hasil"**, `bg: #F5F7F6`, teks `#475569`, border ringan, radius 999 px.

### 2. Seksi Perbarui Data Sumber (Kartu Import)

Dua kartu sejajar: **Kartu Import File** (kiri, lebih lebar) dan **Kartu Batch Aktif** (kanan).

**Kartu Import File:**
- Judul H2: "Perbarui Data Sumber".
- Deskripsi kecil: "Pilih workbook `.xlsx` sesuai template Master_Data. Batas unggah 10 MiB."
- Konten:
  - Tombol "Pilih File Excel" (sekunder, dengan border): berfungsi sebagai trigger file picker tersembunyi.
  - Teks indikator file: "Belum ada file" (atau "1 file dipilih" jika sudah memilih) — di samping tombol.
  - Tombol "Import Batch" (primer, `bg: #0F766E`): disabled jika belum ada file.
  - Helper text di bawah: "Batch aktif lama tetap digunakan jika import gagal.", ukuran 12 px, warna `#66736F`.
- State uploading: teks tombol berubah "Mengunggah…", ada teks status "Mengunggah dan memvalidasi workbook…" di bawah tombol.
- State sukses: pesan hijau "Import selesai. X baris tersimpan dan batch baru aktif.", `bg: #ECFDF5`, teks `#065F46`.
- Border radius: 12 px. `bg: #FFFFFF`. Border: `1px #DDE4E1`.

**Kartu Batch Aktif:**
- Judul H2: "Batch Aktif".
- Badge di pojok kanan atas judul: "Aktif", `bg: #ECFDF5`, teks `#065F46`, pill.
- Isi (jika ada batch):
  - "Baris Sumber" → **"7.449"** (angka besar, tabular-nums)
  - "Status" → **"Selesai"**
  - "Diperbarui" → **"12 Okt 2026, 18:30"**
  - "ID Batch" → `fee8b2bb-18e7-4f48-9dff...` (IBM Plex Mono, 11 px, warna `#66736F`)
- Isi (jika belum ada batch): teks "Belum ada batch aktif. Import workbook untuk memulai."
- Border radius: 12 px. `bg: #FFFFFF`. Border: `1px #DDE4E1`.

### 3. Seksi Filter dan Pencarian

Kartu filter dengan grid 4 kolom (pada layar besar):
- Judul H2: "Cari dan Filter Data".
- Deskripsi kecil: "Pencarian diterapkan di server pada batch aktif.", 13 px, warna `#66736F`.
- Field input filter SITASI:
  1. **NIM** — input teks, placeholder "Cari NIM…"
  2. **Nama** — input teks, placeholder "Cari nama…"
  3. **Sertifikasi** — input teks, placeholder "Contoh: MOS"
  4. **Status sumber** — input teks, placeholder "Contoh: LULUS"
- Tombol "Terapkan Filter" (primer, `bg: #0F766E`).
- Tombol "Reset" (sekunder, border `#DDE4E1`).
- Border radius: 12 px. `bg: #FFFFFF`. Border: `1px #DDE4E1`.

### 4. Tabel Data SITASI

Kartu tabel dengan overflow horizontal scrollable.

**Header tabel** (background `#F5F7F6`, uppercase, 11 px, semibold, warna `#66736F`):
| NIM | Nama | Program Studi | Sertifikasi | Sub Program | Nilai | Status |

**Baris data dummy** (tiga baris contoh):
| 2021001001 | Budi Santoso | Teknik Informatika | MOS | Word 2019 | 851 | LULUS |
| 2021001002 | Dewi Rahayu | Sistem Informasi | MOS | Excel 2019 | 780 | LULUS |
| 2021001003 | Ahmad Fauzi | Teknik Informatika | MCF | Azure AI-900 | 720 | TIDAK LULUS |

- Kolom NIM menggunakan `font-family: IBM Plex Mono`.
- Hover baris: `bg: #F8FAFC`.
- Lebar kolom: proporsional berdasarkan konten.
- Garis pemisah baris: `1px solid #F0F4F3`.

**Footer Tabel (Pagination):**
- Teks: "Halaman 1 dari 298"
- Tombol "Sebelumnya" (disabled pada halaman 1) dan "Berikutnya" (aktif).
- Border atas: `1px #DDE4E1`.

---

## State yang Harus Ditampilkan

Tampilkan dalam frame/artboard terpisah atau anotasi:

1. **State normal**: Tabel terisi data dummy, batch aktif terlihat, form import kosong.
2. **State loading tabel**: Pengganti isi tabel: teks "Memuat data…" di tengah kartu tabel.
3. **State tabel kosong (filter tidak menemukan data)**: Teks "Tidak ada data yang cocok. Ubah kata kunci atau reset filter." di tengah kartu tabel.
4. **State belum ada batch aktif**: Kartu batch menampilkan pesan empty, tabel menampilkan "Data belum tersedia. Belum ada batch aktif untuk sumber ini."
5. **State error tabel**: Banner merah dengan pesan error dan tombol "Coba lagi".

---

## Catatan Desain Penting

- **Jangan** menampilkan kolom NIM untuk data Certiport — ini adalah halaman SITASI yang memang mempunyai NIM.
- Nilai numerik (Score) ditampilkan apa adanya, bukan dikonversi ke grade.
- Status SITASI berasal dari sumber (mis. "LULUS", "TIDAK LULUS") — bukan status sinkronisasi.
- Jangan menambahkan tombol edit atau hapus baris data — data master hanya dibaca.

---

## Design Tokens (Ringkasan untuk Prompt Ini)

```
Background halaman  : #F5F7F6
Surface/kartu       : #FFFFFF
Teks utama          : #172321
Teks sekunder       : #66736F
Aksen utama         : #0F766E
Border              : #DDE4E1
Tabel header bg     : #F5F7F6
Tabel hover         : #F8FAFC
Badge Aktif bg      : #ECFDF5  |  Badge Aktif teks: #065F46
Sukses bg           : #ECFDF5  |  Sukses teks    : #065F46
Error bg            : #FFF1F2  |  Error teks     : #9F1239
Font UI             : IBM Plex Sans
Font data (NIM, ID) : IBM Plex Mono
Border radius       : 8–12 px
```

---

## Responsif

| Layar | Perilaku |
|-------|----------|
| ≥ 1024 px | Sidebar vertikal + dua kartu atas sejajar (import + batch) + filter 4 kolom |
| 768–1023 px | Kartu atas 1 kolom penuh, filter 2 kolom, tabel horizontal scroll |
| < 768 px | Semua 1 kolom, filter 1 kolom, tabel horizontal scroll |

---

## Aksesibilitas

- Label setiap input filter terlihat dan dihubungkan ke input.
- Tombol "Import Batch" menggunakan `aria-disabled` dan `cursor: not-allowed` saat disabled.
- Tabel mempunyai `<caption>` tersembunyi atau `aria-label`.
- State loading dan error menggunakan `role="status"` dan `role="alert"`.

---

## Instruksi Final untuk Google Stitch

Buat tepat **satu screen halaman Data SITASI** yang menampilkan:
1. Shell layout: header + sidebar (item SITASI disorot) + konten.
2. Header halaman dengan judul dan badge count total.
3. Dua kartu sejajar: form import file dan informasi batch aktif.
4. Kartu filter dengan empat field input dan dua tombol.
5. Tabel data dengan kolom NIM, Nama, Program Studi, Sertifikasi, Sub Program, Nilai, Status — diisi 3–5 baris data dummy.
6. Pagination di bawah tabel.
7. Tampilkan satu frame state "tabel loading" dan satu frame "empty state" sebagai alternatif.
8. Gunakan design tokens, gaya Swiss Minimalism, semua teks bahasa Indonesia.
