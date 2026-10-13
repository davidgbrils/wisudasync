# Prompt Desain Google Stitch — Screen 06: Halaman Hasil Sinkronisasi

> **Instruksi penggunaan:** Salin seluruh isi file ini dan tempel ke kolom prompt Google Stitch. File ini hanya untuk satu screen. Jangan menggabungkannya dengan prompt lain.

---

## Konteks Produk

**ITCC Wisuda Sync** adalah aplikasi web internal. Halaman Hasil Sinkronisasi (`/sinkronisasi/{id}`) menampilkan hasil dari satu sesi proses pencocokan. Setiap baris wisuda mendapatkan status dan alasan. Petugas dapat mencari, memfilter, dan membuka detail verifikasi per baris.

Halaman ini juga menjadi titik ekspor Excel. Tombol ekspor **final** saat ini selalu nonaktif karena pemetaan kolom output belum disetujui ITCC (ADR-003 masih terbuka). Hanya ekspor **draft** yang tersedia.

---

## Instruksi untuk Google Stitch

Buat **hanya satu screen**: halaman Hasil Sinkronisasi. Jangan mendesain dialog detail verifikasi, halaman upload, atau halaman lain dalam desain ini. Dialog verifikasi ada di file terpisah (`07_RESULT_REVIEW_SCREEN.md`).

---

## Pengguna dan Tugas Utama

**Pengguna:** Petugas ITCC yang sudah login.
**Tugas utama:** Melihat hasil sinkronisasi per baris, memfilter berdasarkan status, mencari NIM atau nama, dan memulai verifikasi manual untuk baris yang perlu ditinjau.

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

- Item "Validasi" disorot aktif.
- Link navigasi di atas konten: "← Riwayat Sinkronisasi" untuk kembali.

---

## Konten Halaman Hasil Sinkronisasi

### 1. Header Sesi

- Breadcrumb/link kembali: "← Riwayat Sinkronisasi", 13 px, warna `#0F766E`.
- Label kecil: "HASIL SINKRONISASI", uppercase.
- Judul H1: **"data_wisuda_oktober_2026.xlsx"** (nama file yang diproses), Semibold 22 px.
- Meta sesi (baris kecil di bawah judul):
  - "Diproses: 12 Okt 2026, 20:15"
  - "ID Sesi: abc12345-..." (IBM Plex Mono 11 px)
  - Status sesi: badge "SELESAI", `bg: #ECFDF5`, teks `#065F46`.

### 2. Kartu Ringkasan Hasil

Baris kartu horizontal berisi 5 metrik (atau grid 5 kolom):

| Metrik | Nilai | Warna badge |
|--------|-------|-------------|
| Total Baris | 424 | Netral (`#F5F7F6`, teks `#172321`) |
| Valid | 318 | Hijau (`#ECFDF5`, teks `#065F46`) |
| Perlu Verifikasi | 52 | Amber (`#FFFBEB`, teks `#92400E`) |
| Tidak Lulus | 31 | Merah (`#FFF1F2`, teks `#9F1239`) |
| Tidak Ditemukan | 23 | Abu (`#F8FAFC`, teks `#475569`) |

Semua angka adalah **data dummy untuk ilustrasi desain**, bukan angka nyata.

Setiap kartu metrik:
- Label di atas (kecil, abu).
- Angka besar di bawah label (IBM Plex Sans Semibold, 26 px, tabular-nums).
- Border, background sesuai warna status, radius 12 px.
- Dapat diklik untuk langsung memfilter tabel ke status tersebut.

### 3. Filter dan Pencarian

Baris filter horizontal di atas tabel:
- **Filter status**: Dropdown atau tombol pill (All / Valid / Perlu Verifikasi / Tidak Lulus / Pending / Tidak Ditemukan). Tombol aktif mendapat `bg: #0F766E`, teks putih.
- **Pencarian NIM/Nama**: Input teks, placeholder "Cari NIM atau nama…", lebar fleksibel, di sebelah kanan filter.
- **Toggle "Hanya Perlu Review"**: Checkbox atau toggle, teks "Tampilkan hanya yang perlu verifikasi".
- Tombol "Terapkan" (jika pencarian tidak otomatis) atau live search.

### 4. Tabel Hasil Sinkronisasi

Kartu tabel dengan overflow horizontal scrollable.

**Header tabel** (background `#F5F7F6`, uppercase, 11 px, semibold, warna `#66736F`):
| No. Baris | NIM | Nama Wisuda | MOS | MCF | Status | Alasan | Aksi |

**Baris data dummy** (lima baris berbeda status):

| 2 | 2021001001 | Budi Santoso | MOS Word 2019 | — | VALID | Cocok semua sumber | [Periksa] |
| 3 | 2021001002 | Dewi Rahayu | MOS Excel 2019 | MCF AI-900 | VALID | Cocok semua sumber | [Periksa] |
| 4 | 2021001003 | Ahmad Fauzi | — | — | PERLU_VERIFIKASI | Nama Certiport ganda | [Periksa] |
| 5 | 2021001004 | Siti Nurhaliza | MOS Word 2019 | — | TIDAK_LULUS | Tidak ada bukti lulus | [Periksa] |
| 6 | 2099999001 | Reza Ardian | — | — | DATA_TIDAK_DITEMUKAN | NIM tidak ada di SITASI | [Periksa] |

**Kolom Status:**
- Tampilkan badge pill per status:
  - "Valid" → `bg: #ECFDF5`, teks `#065F46`, border `#A7F3D0`.
  - "Perlu Verifikasi" → `bg: #FFFBEB`, teks `#92400E`, border `#FCD34D`.
  - "Tidak Lulus" → `bg: #FFF1F2`, teks `#9F1239`, border `#FECDD3`.
  - "Pending" → `bg: #EFF6FF`, teks `#1E40AF`, border `#BFDBFE`.
  - "Tidak Ditemukan" → `bg: #F8FAFC`, teks `#475569`, border `#E2E8F0`.
- Selalu tampilkan **teks label** di dalam badge — jangan hanya warna.

**Kolom Aksi:**
- Tombol "Periksa" kecil (sekunder, border, tinggi 32 px) untuk membuka detail/verifikasi.
- Untuk baris yang sudah direview: tampilkan teks kecil "(Ditinjau)" di bawah tombol.

**Footer (Pagination):**
- "Halaman 1 dari 17" + tombol Sebelumnya/Berikutnya.

### 5. Tombol Ekspor

Di bawah atau di atas tabel:

**Tombol Unduh Draft [.xlsx]** (selalu aktif, tombol sekunder):
- Teks: "Unduh Draft Excel".
- Keterangan kecil: "Pratinjau internal, diberi label [DRAFT]."

**Tombol Unduh Final [.xlsx]** (selalu nonaktif / disabled):
- Teks: "Unduh Excel Final" (abu-abu, cursor not-allowed).
- Keterangan kecil di bawah: "Ekspor final diblokir. Pemetaan kolom output belum disahkan oleh ITCC. Lihat ADR-003.", warna `#66736F`.
- Tidak ada tooltip — cukup teks keterangan yang jelas.

---

## State yang Harus Ditampilkan

1. **State utama (ada data, filter All)**: Tabel 5 baris dengan berbagai status, kartu metrik terisi, tombol ekspor tampil.
2. **State filter "Perlu Verifikasi"**: Hanya baris PERLU_VERIFIKASI tampil, tombol filter Perlu Verifikasi aktif.
3. **State loading**: Tabel menampilkan "Memuat hasil…" di tengah. Kartu metrik belum terisi (atau dalam state loading).
4. **State error**: Banner merah "Gagal memuat hasil. Coba lagi." + tombol retry.

---

## Catatan Desain Penting

- **Jangan** menampilkan nilai persentase atau chart pie — tidak ada data ini di sistem.
- **Jangan** membuat tombol ekspor final aktif — harus nonaktif dengan penjelasan tertulis.
- Status VALID hanya berlaku untuk baris dengan bukti lengkap dari kedua sumber — jangan tambahkan baris VALID hanya karena nama mirip.
- Kolom MOS dan MCF menampilkan nama sertifikasi, atau "—" jika tidak ada data.
- Kolom "Alasan" menampilkan ringkasan singkat alasan status.

---

## Design Tokens (Ringkasan untuk Prompt Ini)

```
Background halaman       : #F5F7F6
Surface/kartu            : #FFFFFF
Teks utama               : #172321
Teks sekunder            : #66736F
Aksen utama              : #0F766E
Border                   : #DDE4E1
Tabel header bg          : #F5F7F6

VALID bg/teks/border     : #ECFDF5 / #065F46 / #A7F3D0
PERLU_VERIFIKASI         : #FFFBEB / #92400E / #FCD34D
TIDAK_LULUS              : #FFF1F2 / #9F1239 / #FECDD3
PENDING                  : #EFF6FF / #1E40AF / #BFDBFE
DATA_TIDAK_DITEMUKAN     : #F8FAFC / #475569 / #E2E8F0

Font UI                  : IBM Plex Sans
Font NIM/ID              : IBM Plex Mono
Border radius            : 8–12 px
```

---

## Responsif

| Layar | Perilaku |
|-------|----------|
| ≥ 1024 px | Kartu metrik 5 kolom, tabel penuh |
| 768–1023 px | Kartu metrik wrap 3+2, tabel horizontal scroll |
| < 768 px | Kartu metrik 2 kolom, tabel horizontal scroll, filter vertikal |

---

## Aksesibilitas

- Badge status selalu disertai teks label.
- Tombol "Periksa" mempunyai `aria-label` yang menyebutkan nama/NIM: "Periksa baris Budi Santoso".
- Tombol ekspor final menggunakan `aria-disabled` dan `title` berisi penjelasan.
- Filter aktif memiliki `aria-pressed` untuk tombol pill.

---

## Instruksi Final untuk Google Stitch

Buat tepat **satu screen halaman Hasil Sinkronisasi** yang menampilkan:
1. Shell layout: header + sidebar (Validasi disorot) + konten.
2. Header sesi dengan nama file, meta sesi, dan badge status "Selesai".
3. Baris kartu metrik 5 kolom: Total, Valid, Perlu Verifikasi, Tidak Lulus, Tidak Ditemukan.
4. Baris filter: tombol pill status + input pencarian NIM/nama.
5. Tabel hasil dengan 5 baris berbeda status, badge status berwarna + teks, tombol "Periksa".
6. Tombol ekspor: "Unduh Draft Excel" (aktif) dan "Unduh Excel Final" (nonaktif, dengan teks alasan).
7. Tampilkan frame state loading dan frame filter "Perlu Verifikasi".
8. Gunakan design tokens, gaya Swiss Minimalism, semua teks bahasa Indonesia.
