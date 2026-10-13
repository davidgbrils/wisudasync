# 00 — Design System: ITCC Wisuda Sync

Dokumen ini adalah panduan desain bersama yang **harus disertakan atau dirujuk** dalam setiap prompt screen Google Stitch. Tujuannya agar seluruh screen memiliki tampilan yang konsisten meskipun dibuat secara terpisah.

---

## Filosofi Desain

**Swiss Minimalism + Enterprise Utility UI**

- Minimalis, profesional, dan berorientasi pada pengolahan data.
- Grid konsisten, hierarki tipografi jelas, whitespace terukur.
- Satu sidebar vertikal di kiri, tidak ada navigasi ganda.
- Tabel, filter, status, dan formulir harus mudah dibaca.
- Hindari: gradien dekoratif, glassmorphism, neumorphism, neon, claymorphism, neo-brutalism, atau gaya dashboard SaaS generik.

---

## Design Tokens

### Warna Dasar

| Token          | Nilai       | Penggunaan                            |
|----------------|-------------|---------------------------------------|
| Background     | `#F5F7F6`   | Latar halaman (body/html)            |
| Surface        | `#FFFFFF`   | Kartu, tabel, form, sidebar          |
| Teks utama     | `#172321`   | Judul, label, isi tabel              |
| Teks sekunder  | `#66736F`   | Deskripsi, helper text, placeholder  |
| Aksen utama    | `#0F766E`   | Tombol primer, link aktif, focus ring |
| Aksen hover    | `#0C5F58`   | Hover tombol primer                  |
| Border         | `#DDE4E1`   | Garis kartu, tabel, input            |
| Sidebar aktif bg | `#ECFAF8` | Background item navigasi aktif       |
| Sidebar aktif teks | `#0F4B46` | Teks item navigasi aktif            |

### Warna Status (WAJIB ada label teks, bukan hanya warna)

| Status                 | Background  | Teks        | Border      | Label Tampil          |
|------------------------|-------------|-------------|-------------|----------------------|
| VALID                  | `#ECFDF5`   | `#065F46`   | `#A7F3D0`   | Teks: "Valid"        |
| PERLU_VERIFIKASI       | `#FFFBEB`   | `#92400E`   | `#FCD34D`   | Teks: "Perlu Verifikasi" |
| TIDAK_LULUS            | `#FFF1F2`   | `#9F1239`   | `#FECDD3`   | Teks: "Tidak Lulus"  |
| PENDING                | `#EFF6FF`   | `#1E40AF`   | `#BFDBFE`   | Teks: "Pending"      |
| DATA_TIDAK_DITEMUKAN   | `#F8FAFC`   | `#475569`   | `#E2E8F0`   | Teks: "Tidak Ditemukan" |

### Warna Bahaya / Informasi

| Konteks       | Nilai bg    | Nilai teks  |
|---------------|-------------|-------------|
| Error/danger  | `#FFF1F2`   | `#9F1239`   |
| Peringatan    | `#FFFBEB`   | `#92400E`   |
| Informasi     | `#EFF6FF`   | `#1E40AF`   |
| Sukses/berhasil | `#ECFDF5` | `#065F46`   |

---

## Tipografi

| Hierarki         | Font            | Ukuran | Berat       | Contoh Penggunaan              |
|------------------|-----------------|--------|-------------|--------------------------------|
| Judul halaman H1 | IBM Plex Sans   | 24 px  | Semibold 600| Nama halaman (mis. Data SITASI) |
| Judul seksi H2   | IBM Plex Sans   | 16 px  | Semibold 600| Judul kartu atau seksi         |
| Label           | IBM Plex Sans   | 13 px  | Medium 500  | Label kolom, filter            |
| Isi tabel / data | IBM Plex Sans  | 13 px  | Regular 400 | Isi baris tabel                |
| Data teknis (ID, batch) | IBM Plex Mono | 11 px | Regular 400 | UUID, ID batch, nomor sumber |
| Helper text / caption | IBM Plex Sans | 12 px | Regular 400 | Deskripsi di bawah input |
| Tombol          | IBM Plex Sans   | 13 px  | Semibold 600| Teks tombol aksi               |

---

## Komponen Dasar

### Layout Shell Aplikasi

```
┌──────────────────────────────────────────────────────────┐
│ HEADER STICKY: [Logo W] ITCC Wisuda Sync         [Keluar]│
├────────────┬─────────────────────────────────────────────┤
│  SIDEBAR   │                                             │
│  (240 px)  │  KONTEN UTAMA (max-width 1400 px)          │
│            │                                             │
│  Ringkasan │                                             │
│  Validasi  │                                             │
│  Riwayat   │                                             │
│  SITASI    │                                             │
│  Certiport │                                             │
│            │                                             │
└────────────┴─────────────────────────────────────────────┘
```

- Header: tinggi 64 px, `bg: #FFFFFF`, `border-bottom: 1px #DDE4E1`.
- Logo: kotak 36×36 px, `bg: #0F4B46`, huruf "W" putih, radius 8 px.
- Sidebar: lebar 240 px, `bg: #FFFFFF`, `border-right: 1px #DDE4E1`. Tersembunyi di layar < 768 px (mobile: nav horizontal scrollable di bawah header).
- Konten: `bg: #F5F7F6`, padding 24–32 px.

### Kartu (Card)

- `bg: #FFFFFF`, `border: 1px solid #DDE4E1`, `border-radius: 12 px`, `box-shadow: 0 1px 3px rgba(0,0,0,0.06)`.

### Input Field

- Tinggi min 40 px, `border: 1px solid #DDE4E1`, `border-radius: 8 px`.
- Focus: `outline: 2px solid #0F766E`, `outline-offset: 2px`.
- Placeholder: warna `#66736F`.

### Tombol Primer

- `bg: #0F766E`, teks `#FFFFFF`, `border-radius: 8 px`, tinggi min 40 px, padding 0 16 px.
- Hover: `bg: #0C5F58`.
- Disabled: opacity 50%, cursor not-allowed.

### Tombol Sekunder

- `bg: #FFFFFF`, `border: 1px solid #DDE4E1`, teks `#172321`, `border-radius: 8 px`.
- Hover: `bg: #F5F7F6`.

### Tombol Destruktif / Bahaya

- `bg: #FFFFFF`, `border: 1px solid #FECDD3`, teks `#9F1239`.
- Hover: `bg: #FFF1F2`.

### Tabel Data

- Header: `bg: #F5F7F6`, teks `#66736F`, ukuran 11 px, uppercase, semibold.
- Baris ganjil/genap: alternatif subtle atau hover `bg: #F8FAFC`.
- Sel: padding 12 px horizontal, 10 px vertikal.
- Kolom data teknis (NIM, ID): `font-family: IBM Plex Mono`.

### Badge Status

- Tampilan inline, `border-radius: 999 px` (pill), `border: 1px solid`, ukuran teks 12 px.
- **Selalu ada teks status** — jangan hanya mengandalkan warna.

### Pagination

- Tombol "Sebelumnya" dan "Berikutnya", teks halaman "Halaman X dari Y".
- Disabled: opacity 45%.

---

## Spasi

- Unit dasar: 4 px.
- Jarak antar elemen dalam kartu: 16–24 px.
- Jarak antar kartu/seksi: 24–32 px.
- Padding konten halaman: 24 px (mobile) → 32 px (tablet) → 32 px (desktop).

---

## Radius Border

- Komponen besar (kartu, tabel): 12 px.
- Komponen kecil (tombol, input, badge): 8 px.
- Badge/pill: 999 px (full rounded).

---

## Ikon

Gunakan ikon garis bersih (outline style). Ukuran 16–20 px. Warna mengikuti konteks teks. Hindari ikon dekoratif tanpa makna fungsi. Contoh ikon yang umum digunakan:

- Upload/Import: ikon panah ke atas.
- Download/Ekspor: ikon panah ke bawah.
- Cari: ikon kaca pembesar.
- Filter: ikon corong/funnel.
- Detail/buka: ikon panah diagonal atau chevron kanan.
- Centang / Konfirmasi: ikon centang.
- Silang / Tolak: ikon X.
- Peringatan: ikon segitiga seru.
- Info: ikon lingkaran-i.

---

## Perilaku Responsive

| Breakpoint | Perilaku                                                     |
|------------|--------------------------------------------------------------|
| ≥ 1024 px  | Sidebar vertikal tampil, konten mengambil sisa lebar         |
| 768–1023 px | Sidebar tersembunyi, navigasi horizontal scrollable di bawah header |
| < 768 px   | Navigasi horizontal, konten full lebar, tabel dapat digeser  |

---

## State UI yang Selalu Ada

Setiap screen atau komponen wajib memiliki state:

- **Loading**: Spinner atau teks "Memuat…", `role="status"`.
- **Empty state**: Teks informatif tentang kondisi (mis. "Belum ada batch aktif").
- **Error state**: Banner pesan merah dengan tombol "Coba lagi" jika relevan.
- **Disabled**: Tombol dengan opacity 50% dan `cursor: not-allowed`, dengan label atau tooltip alasan.
- **Success**: Pesan konfirmasi hijau setelah aksi berhasil.

---

## Akses dan Aksesibilitas

- Tombol "Lewati navigasi" tersembunyi, muncul saat Tab pertama.
- Semua input mempunyai `<label>` yang terlihat.
- Semua gambar/ikon bermakna punya `alt` atau `aria-label`.
- Validasi error tidak hanya dari warna — harus ada pesan teks.
- Tabel punya `<caption>` atau `aria-label`.
- Ukuran target klik minimum 40×40 px.
- Focus ring: `2px solid #0F766E`.

---

## Catatan Data Dummy

Semua contoh data dalam prompt adalah **data dummy fiktif** untuk keperluan ilustrasi desain. Jangan menggunakan data pribadi mahasiswa asli. Format NIM, nama, dan nilai bersifat ilustratif.

Contoh data dummy yang aman digunakan:
- NIM: `2021001001`, `2020999001`
- Nama: `Budi Santoso`, `Dewi Rahayu`, `Ahmad Fauzi`
- Program: `Microsoft Office Specialist`, `Microsoft Certified Fundamentals`
- Sertifikasi: `MOS Word 2019`, `MCF Azure AI-900`
