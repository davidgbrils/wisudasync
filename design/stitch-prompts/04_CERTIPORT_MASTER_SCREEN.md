# Prompt Desain Google Stitch — Screen 04: Halaman Data Certiport

> **Instruksi penggunaan:** Salin seluruh isi file ini dan tempel ke kolom prompt Google Stitch. File ini hanya untuk satu screen. Jangan menggabungkannya dengan prompt lain.

---

## Konteks Produk

**ITCC Wisuda Sync** adalah aplikasi web internal. Halaman Data Certiport (`/certiport`) adalah halaman manajemen data master hasil ujian dari sistem Certiport. Data Certiport diimpor dari file Excel `.xlsx` dengan sheet `Results (264) Plus`.

**Perbedaan penting dibanding SITASI:** Data Certiport **tidak memiliki kolom NIM**. Pencocokan ke mahasiswa wisuda dilakukan berdasarkan nama (normalisasi) dan program ujian, bukan NIM. Oleh karena itu, tabel Certiport **tidak memiliki kolom NIM** — ini bukan kekeliruan desain.

Halaman ini memungkinkan petugas untuk:
- Mengimpor file Excel Certiport baru sebagai batch aktif.
- Melihat informasi batch yang sedang aktif.
- Mencari dan memfilter data berdasarkan nama, program, dan hasil ujian.
- Melihat tabel data Certiport.

---

## Instruksi untuk Google Stitch

Buat **hanya satu screen**: halaman Data Certiport. Jangan mendesain halaman SITASI, Dashboard, atau sinkronisasi dalam desain ini.

---

## Pengguna dan Tugas Utama

**Pengguna:** Petugas ITCC yang sudah login.
**Tugas utama:** Memperbarui data master Certiport dan memeriksa data ujian yang tersimpan.

---

## Shell Layout

```
┌──────────────────────────────────────────────────────────┐
│ HEADER: [W] ITCC Wisuda Sync                    [Keluar] │
├────────────┬─────────────────────────────────────────────┤
│  SIDEBAR   │  KONTEN UTAMA                               │
│  Ringkasan │                                             │
│  Validasi  │                                             │
│  Riwayat   │                                             │
│  SITASI    │                                             │
│ ○ Certiport│                                             │
└────────────┴─────────────────────────────────────────────┘
```

- Item "Certiport" disorot aktif di sidebar.

---

## Konten Halaman Data Certiport

### 1. Header Halaman

- Label kecil atas: "DATA MASTER", uppercase, IBM Plex Sans 11 px, warna `#0F766E`.
- Judul H1: **"Data Certiport"**, IBM Plex Sans Semibold 24 px, warna `#172321`.
- Deskripsi: "Cari, periksa, atau perbarui batch sumber Certiport.", 13 px, warna `#66736F`.
- Badge count total di pojok kanan: mis. **"264 hasil"**, atau "Memuat…" saat loading.

### 2. Seksi Perbarui Data Sumber

Dua kartu sejajar: **Kartu Import File** (kiri) dan **Kartu Batch Aktif** (kanan).

**Kartu Import File:**
- Judul H2: "Perbarui Data Sumber".
- Deskripsi kecil: "Pilih workbook `.xlsx` sesuai template Results (264) Plus. Batas unggah 10 MiB."
- Konten:
  - Tombol "Pilih File Excel" (sekunder, border).
  - Teks indikator file di samping: "Belum ada file".
  - Tombol "Import Batch" (primer), disabled jika tidak ada file.
  - Helper text: "Batch aktif lama tetap digunakan jika import gagal."
- State sukses: pesan hijau "Import selesai. X baris tersimpan dan batch baru aktif."
- Border radius: 12 px. `bg: #FFFFFF`. Border: `1px #DDE4E1`.

**Kartu Batch Aktif** (state: belum ada batch):
- Judul H2: "Batch Aktif".
- Teks: "Belum ada batch aktif. Import workbook untuk memulai."
- Tidak ada badge "Aktif" karena belum ada data.

**Kartu Batch Aktif** (state: ada batch — tampilkan versi alternatif):
- Badge "Aktif" di pojok kanan judul, hijau.
- Detail: "Baris Sumber", "Status", "Diperbarui", "ID Batch" (mono).

### 3. Seksi Filter dan Pencarian

Kartu filter dengan grid 3 kolom (berbeda dengan SITASI yang 4 kolom, karena filter berbeda):
- Judul H2: "Cari dan Filter Data".
- Deskripsi kecil: "Pencarian diterapkan di server pada batch aktif."
- Field input filter Certiport (berbeda dari SITASI — tidak ada NIM):
  1. **Nama** — input teks, placeholder "Cari nama peserta…"
  2. **Program** — input teks, placeholder "Contoh: Microsoft Office Specialist"
  3. **Hasil** — input teks, placeholder "Contoh: PASS"
- Tombol "Terapkan Filter" (primer).
- Tombol "Reset" (sekunder).
- Border radius: 12 px. `bg: #FFFFFF`. Border: `1px #DDE4E1`.

### 4. Tabel Data Certiport

**Penting: Tidak ada kolom NIM di tabel Certiport.**

**Header tabel** (background `#F5F7F6`, uppercase, 11 px, semibold, warna `#66736F`):
| Nama | Program | Sertifikasi | Nilai | Hasil |

**Baris data dummy** (tiga baris contoh):
| Budi Santoso | Microsoft Office Specialist | Word 2019 | 851 | PASS |
| Dewi Rahayu Putri | Microsoft Office Specialist | Excel 2019 | 780 | PASS |
| Ahmad F | Microsoft Certified Fundamentals | Azure AI-900 | 540 | FAIL |

Catatan pada data dummy:
- Kolom "Nama" adalah nama Certiport yang mungkin berbeda dengan nama di data wisuda atau SITASI.
- Kolom "Nilai" adalah score numerik dari ujian.
- Kolom "Hasil" adalah "PASS" atau "FAIL" — tanpa NIM atau program studi.

- Hover baris: `bg: #F8FAFC`.
- Garis pemisah baris: `1px solid #F0F4F3`.

**Footer (Pagination):**
- Teks: "Halaman 1 dari 11"
- Tombol "Sebelumnya" (disabled) dan "Berikutnya" (aktif).

---

## State yang Harus Ditampilkan

Satu frame utama + dua frame alternatif:

1. **State normal**: Tabel terisi 3–5 baris data dummy, batch belum ada (empty state di kartu batch).
2. **State batch ada**: Kartu batch menampilkan detail data batch aktif.
3. **State loading**: Tabel menampilkan "Memuat data…" di tengah.
4. **State empty state (filter)**: "Tidak ada data yang cocok. Ubah kata kunci atau reset filter."

---

## Perbedaan Utama dari Halaman SITASI

| Aspek | SITASI | Certiport |
|-------|--------|-----------|
| Kolom NIM | Ada | **Tidak ada** |
| Filter NIM | Ada | **Tidak ada** |
| Filter Sertifikasi/Status | Ada (sertifikasi + status sumber) | Program + Hasil (PASS/FAIL) |
| Kolom tabel | NIM, Nama, Program Studi, Sertifikasi, Sub Program, Nilai, Status | Nama, Program, Sertifikasi, Nilai, Hasil |
| Sheet Excel sumber | `Master_Data` | `Results (264) Plus` |

---

## Catatan Desain Penting

- **Jangan** menambahkan kolom NIM pada tabel Certiport. Data Certiport memang tidak mempunyai NIM.
- **Jangan** menampilkan status VALID/PERLU_VERIFIKASI pada tabel ini — itu bukan status ujian Certiport. Hanya PASS/FAIL.
- Nama di Certiport mungkin berbeda dengan nama di SITASI atau data wisuda. Ini adalah kondisi yang diketahui dan bukan error.
- Nilai "Score" ditampilkan apa adanya sebagai angka — bukan dikonversi atau dinilai ulang.

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
Font data (ID)      : IBM Plex Mono
Border radius       : 8–12 px
```

---

## Responsif

| Layar | Perilaku |
|-------|----------|
| ≥ 1024 px | Sidebar vertikal + dua kartu atas sejajar + filter 3 kolom |
| 768–1023 px | Kartu atas 1 kolom, filter 2 kolom, tabel horizontal scroll |
| < 768 px | Semua 1 kolom, filter 1 kolom, tabel horizontal scroll |

---

## Aksesibilitas

- Label setiap input filter terlihat.
- Tombol disabled menggunakan `aria-disabled` dan `cursor: not-allowed`.
- Tabel mempunyai `aria-label` yang menyebutkan "Data Certiport dari batch aktif".

---

## Instruksi Final untuk Google Stitch

Buat tepat **satu screen halaman Data Certiport** yang menampilkan:
1. Shell layout: header + sidebar (Certiport disorot) + konten.
2. Header halaman dengan judul dan badge count total.
3. Dua kartu sejajar: form import file dan informasi batch aktif (tampilkan state "belum ada batch").
4. Kartu filter dengan tiga field input: Nama, Program, Hasil — **tanpa field NIM**.
5. Tabel data **tanpa kolom NIM**, berisi: Nama, Program, Sertifikasi, Nilai, Hasil — dengan 3–5 baris data dummy.
6. Pagination di bawah tabel.
7. Tampilkan satu frame state "tabel loading" sebagai alternatif.
8. Gunakan design tokens, gaya Swiss Minimalism, semua teks bahasa Indonesia.
