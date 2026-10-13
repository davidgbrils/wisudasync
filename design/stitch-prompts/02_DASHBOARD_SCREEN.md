# Prompt Desain Google Stitch — Screen 02: Halaman Dashboard (Ringkasan)

> **Instruksi penggunaan:** Salin seluruh isi file ini dan tempel ke kolom prompt Google Stitch. File ini hanya untuk satu screen. Jangan menggabungkannya dengan prompt lain.

---

## Konteks Produk

**ITCC Wisuda Sync** adalah aplikasi web internal. Halaman Dashboard adalah halaman pertama setelah petugas login. Fungsinya adalah memberikan ringkasan status sistem dan akses cepat ke fitur utama.

Dashboard tidak membuat angka statistik — data yang ditampilkan berasal dari API batch aktif. Jika tidak ada batch aktif, tampilkan empty state yang jelas. Jangan mengarang angka.

---

## Instruksi untuk Google Stitch

Buat **hanya satu screen**: halaman Dashboard/Ringkasan. Jangan membuat halaman SITASI, Certiport, atau sinkronisasi dalam desain ini.

---

## Pengguna dan Tugas Utama

**Pengguna:** Petugas ITCC yang sudah login.
**Tugas:** Melihat status batch aktif (SITASI dan Certiport), mengakses menu utama, dan membuka proses sinkronisasi atau riwayat.

---

## Shell Layout (Wajib Ada di Semua Screen Dashboard)

```
┌──────────────────────────────────────────────────────────┐
│ HEADER: [W] ITCC Wisuda Sync     Pusat data sertifikasi  │  [Keluar]
├────────────┬─────────────────────────────────────────────┤
│  SIDEBAR   │  KONTEN UTAMA                               │
│            │                                             │
│ ○ Ringkasan│                                             │
│   Validasi │                                             │
│   Riwayat  │                                             │
│   SITASI   │                                             │
│   Certiport│                                             │
└────────────┴─────────────────────────────────────────────┘
```

- Header: tinggi 64 px, `bg: #FFFFFF`, border bawah `1px #DDE4E1`.
- Logo kotak: 36×36 px, `bg: #0F4B46`, huruf "W" putih, radius 8 px.
- Tombol "Keluar" di kanan header: teks kecil, border ringan.
- Sidebar kiri: 240 px, `bg: #FFFFFF`, border kanan `1px #DDE4E1`.
- Item aktif sidebar: "Ringkasan" disorot dengan `bg: #ECFAF8`, teks `#0F4B46`, bar indikator kiri `3px solid #0F766E`.
- Konten: `bg: #F5F7F6`, padding 32 px.

---

## Konten Halaman Dashboard

### 1. Banner Selamat Datang (Hero Section)

- Background: `#172321` (gelap, hampir hitam).
- Konten:
  - Label kecil di atas: "RUANG KERJA PETUGAS", uppercase, font IBM Plex Sans 11 px, letter-spacing lebar, warna `#4AEADC` (teal muda).
  - Judul H1: **"Ringkasan Data Master"**, font IBM Plex Sans Semibold 26 px, warna `#FFFFFF`.
  - Deskripsi: "Periksa batch aktif dan buka data SITASI atau Certiport yang perlu dikelola.", ukuran 13 px, warna `rgba(255,255,255,0.7)`.
- Border radius: 12 px.
- Padding: 32 px.

### 2. Dua Kartu Aksi Cepat

Dua kartu sejajar (grid 2 kolom), di bawah banner hero.

**Kartu A — Validasi & Sinkronisasi Wisuda** (aksi utama/prioritas):
- Background `#ECFAF8`, border `1px solid #A7F3D0`.
- Konten kiri: judul "Validasi & Sinkronisasi Wisuda" (teks bold), deskripsi kecil "Unggah workbook wisuda dan jalankan pencocokan dengan data master."
- Teks kanan: "Buka →" warna `#0F766E`.
- Border radius: 12 px. Padding: 16 px.
- Hover: background sedikit lebih gelap.

**Kartu B — Riwayat Sinkronisasi**:
- Background `#FFFFFF`, border `1px solid #DDE4E1`.
- Konten kiri: judul "Riwayat Sinkronisasi", deskripsi "Periksa hasil pencocokan dan detail bukti sesi sebelumnya."
- Teks kanan: "Lihat →" warna `#66736F`.
- Border radius: 12 px. Padding: 16 px.

### 3. Seksi Batch Aktif

Judul H2: **"Status Batch Aktif"**, font IBM Plex Sans Semibold 16 px, warna `#172321`.
Sub-judul: "Informasi dimuat dari server. Data nyata dari batch yang tersimpan di database." Ukuran 13 px, warna `#66736F`.

Dua kartu sejajar (grid 2 kolom pada layar besar, 1 kolom pada tablet):

**Kartu SITASI:**
- Label atas kecil: "SITASI", warna `#66736F`, 12 px.
- Angka besar (baris batch aktif): misal **"7.449"**, font IBM Plex Sans Semibold 28 px, tabular-nums, warna `#172321`.
- Sub-teks: "baris pada batch aktif".
- Badge pojok kanan atas: "Aktif", `bg: #ECFDF5`, teks `#065F46`, border `#A7F3D0`, radius 999 px.
- Di bawah: teks mono kecil ID batch, mis. "Batch fee8b2bb-18e7...", `font-family: IBM Plex Mono`, ukuran 11 px, warna `#66736F`.
- Tombol "Buka data" di bawah, sekunder, penuh lebar kartu.
- Border: `1px solid #DDE4E1`, radius 12 px, `bg: #FFFFFF`.

**Kartu Certiport** (dalam keadaan belum ada batch aktif):
- Angka: "—" (tanda hubung panjang), warna `#66736F`.
- Sub-teks: "belum ada batch aktif".
- Badge: "Belum Tersedia", `bg: #F8FAFC`, teks `#475569`, border `#E2E8F0`.
- Tombol "Buka data" aktif, tapi tabel akan kosong.

---

## State yang Harus Ditampilkan

Tampilkan dua frame state:

1. **State normal/ada data**: Kartu SITASI menampilkan angka baris nyata, badge "Aktif". Kartu Certiport menampilkan "belum ada batch aktif" (empty state jujur).
2. **State loading**: Seluruh area seksi "Status Batch Aktif" diganti dengan teks "Memeriksa batch…" dalam satu kotak dengan border ringan. Kartu aksi cepat tetap tampil.

---

## Interaksi Penting

- Klik kartu "Validasi & Sinkronisasi Wisuda" → mengarah ke `/sinkronisasi`.
- Klik kartu "Riwayat Sinkronisasi" → mengarah ke `/riwayat`.
- Klik tombol "Buka data" di kartu SITASI → mengarah ke `/sitasi`.
- Klik tombol "Buka data" di kartu Certiport → mengarah ke `/certiport`.
- Klik item navigasi sidebar → pindah halaman.

---

## Catatan Desain Penting

- **Jangan** membuat statistik angka (jumlah "valid", "tidak lulus") yang tidak berasal dari data nyata.
- **Jangan** menambahkan grafik atau chart — dashboard ini bukan analytics dashboard.
- **Jangan** menampilkan nama petugas yang sedang login di hero (tidak ada endpoint yang mengembalikannya ke dashboard).
- Badge status harus selalu disertai **teks label**, bukan hanya warna.

---

## Design Tokens (Ringkasan untuk Prompt Ini)

```
Background halaman   : #F5F7F6
Surface/kartu        : #FFFFFF
Teks utama           : #172321
Teks sekunder        : #66736F
Aksen utama          : #0F766E
Border               : #DDE4E1
Hero bg              : #172321
Sidebar aktif bg     : #ECFAF8  |  Sidebar aktif teks: #0F4B46
Badge Aktif bg       : #ECFDF5  |  Badge Aktif teks : #065F46  |  Badge border: #A7F3D0
Badge Kosong bg      : #F8FAFC  |  Badge Kosong teks: #475569
Font                 : IBM Plex Sans
Font data teknis     : IBM Plex Mono (untuk ID batch)
Border radius        : 8–12 px
```

---

## Responsif

| Layar | Perilaku |
|-------|----------|
| ≥ 1024 px (laptop) | Sidebar vertikal 240 px + konten utama. Grid 2 kolom untuk kartu aksi dan batch. |
| 768–1023 px (tablet) | Sidebar tersembunyi → nav horizontal scrollable di bawah header. Kartu 2 kolom tetap. |
| < 768 px (ponsel) | Nav horizontal, semua kartu menjadi 1 kolom penuh. |

---

## Aksesibilitas

- Judul H1 dan H2 menggunakan tag heading yang benar.
- Kartu yang bisa diklik mempunyai `role="link"` atau dibungkus elemen `<a>`.
- Angka batch menggunakan `tabular-nums` agar tidak bergeser.
- State loading menggunakan `role="status"`.

---

## Instruksi Final untuk Google Stitch

Buat tepat **satu screen halaman Dashboard** yang menampilkan:
1. Shell layout lengkap: header, sidebar kiri dengan item navigasi (Ringkasan disorot), dan area konten.
2. Banner hero gelap di atas konten dengan judul dan deskripsi singkat.
3. Dua kartu aksi cepat di bawah hero.
4. Dua kartu batch aktif SITASI dan Certiport dengan data dummy (satu aktif, satu belum ada).
5. Tampilkan juga satu frame state loading pada area batch.
6. Gunakan design tokens yang tercantum, gaya Swiss Minimalism, semua teks bahasa Indonesia.
