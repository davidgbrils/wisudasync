# Prompt Desain Google Stitch — Screen 08: Halaman Riwayat Sinkronisasi

> **Instruksi penggunaan:** Salin seluruh isi file ini dan tempel ke kolom prompt Google Stitch. File ini hanya untuk satu screen. Jangan menggabungkannya dengan prompt lain.

---

## Konteks Produk

**ITCC Wisuda Sync** adalah aplikasi web internal. Halaman Riwayat Sinkronisasi (`/riwayat`) menampilkan daftar semua sesi pencocokan data wisuda yang pernah dijalankan. Setiap sesi mencatat nama file, waktu proses, status sesi, referensi batch master yang digunakan, jumlah baris, dan ringkasan hasil.

Halaman ini bersifat **read-only** — tidak ada aksi edit atau hapus. Petugas dapat membuka detail setiap sesi.

---

## Instruksi untuk Google Stitch

Buat **hanya satu screen**: halaman Riwayat Sinkronisasi. Jangan mendesain halaman hasil detail, upload, atau halaman lain dalam desain ini.

---

## Pengguna dan Tugas Utama

**Pengguna:** Petugas ITCC yang sudah login.
**Tugas utama:** Melihat daftar sesi sinkronisasi yang pernah dijalankan dan membuka kembali hasilnya.

---

## Shell Layout

```
┌──────────────────────────────────────────────────────────┐
│ HEADER: [W] ITCC Wisuda Sync                    [Keluar] │
├────────────┬─────────────────────────────────────────────┤
│  SIDEBAR   │  KONTEN UTAMA                               │
│  Ringkasan │                                             │
│  Validasi  │                                             │
│ ○ Riwayat  │                                             │
│  SITASI    │                                             │
│  Certiport │                                             │
└────────────┴─────────────────────────────────────────────┘
```

- Item "Riwayat" disorot aktif di sidebar.

---

## Konten Halaman Riwayat Sinkronisasi

### 1. Header Halaman

- Label kecil atas: "RIWAYAT SESI", uppercase, IBM Plex Sans 11 px, warna `#0F766E`.
- Judul H1: **"Riwayat Sinkronisasi"**, IBM Plex Sans Semibold 24 px, warna `#172321`.
- Deskripsi: "Daftar seluruh proses pencocokan data wisuda yang pernah dijalankan beserta versi snapshot batch masternya.", 13 px, warna `#66736F`, max-width 700 px.

### 2. Tabel Riwayat Sesi

Kartu tabel besar dengan overflow horizontal scrollable.

**Header tabel** (background `#F8FAFC`, uppercase, 11 px, semibold, warna `#66736F`):
| Waktu | Nama File | Status | Batch Master | Total Baris | Ringkasan Hasil | Aksi |

**Baris data dummy** (empat baris contoh):

**Baris 1 — Sesi Selesai Sempurna:**
| 12 Okt 2026, 20:15 | data_wisuda_oktober.xlsx | SELESAI | SITASI: fee8b2bb · Certiport: a1b2c3d4 | 424 | 318 Valid, 52 Perlu Verifikasi, 31 Tidak Lulus, 23 Tidak Ditemukan | [Buka Hasil] |

**Baris 2 — Sesi Selesai dengan Review Tertunda:**
| 5 Okt 2026, 14:30 | data_wisuda_sept.xlsx | SELESAI | SITASI: abc12345 · Certiport: — | 380 | 290 Valid, 60 Perlu Verifikasi, 30 Tidak Lulus | [Buka Hasil] |

**Baris 3 — Sesi Gagal:**
| 1 Okt 2026, 09:00 | wisuda_test.xlsx | GAGAL | SITASI: abc12345 · Certiport: — | 0 | Proses gagal: header tidak lengkap | [Lihat Error] |

**Baris 4 — Sesi Sedang Diproses:**
| 12 Okt 2026, 21:00 | data_baru.xlsx | DIPROSES | SITASI: xyz99999 · Certiport: def56789 | — | Sedang berjalan… | — |

---

#### Kolom Detail:

**Kolom "Waktu":**
- Format: "12 Okt 2026, 20:15"
- IBM Plex Sans Regular 13 px.

**Kolom "Nama File":**
- Nama file dengan font IBM Plex Sans Medium.
- Teks singkat, maks. 24 karakter sebelum truncate dengan "...".

**Kolom "Status":**
- Badge pill sesuai status:
  - "Selesai" → `bg: #ECFDF5`, teks `#065F46`.
  - "Gagal" → `bg: #FFF1F2`, teks `#9F1239`.
  - "Diproses" → `bg: #EFF6FF`, teks `#1E40AF`.
- Selalu tampilkan **teks label**, bukan hanya warna.

**Kolom "Batch Master":**
- ID batch yang digunakan saat sesi:
  - Format: "SITASI: fee8b2bb · Certiport: a1b2c3d4"
  - Font IBM Plex Mono 11 px, warna `#66736F`.
  - Teks "—" jika tidak ada batch.

**Kolom "Total Baris":**
- Angka jumlah baris mahasiswa yang diproses.
- Tabular-nums. "—" jika gagal sebelum mulai.

**Kolom "Ringkasan Hasil":**
- Teks singkat satu baris:
  - "318 Valid, 52 Perlu Verifikasi, 31 Tidak Lulus, 23 Tidak Ditemukan"
  - Atau "Proses gagal: header tidak lengkap" (teks merah kecil jika gagal).
  - Atau "Sedang berjalan…" dengan dots animasi jika diproses.

**Kolom "Aksi":**
- Tombol "Buka Hasil" (sekunder, border) untuk sesi selesai → link ke `/sinkronisasi/{id}`.
- Tombol "Lihat Error" (sekunder, border merah) untuk sesi gagal.
- "—" untuk sesi yang masih berjalan.

---

### 3. Footer Pagination

- "Halaman 1 dari 3"
- Tombol "Sebelumnya" (disabled pada halaman pertama) dan "Berikutnya".

---

## State yang Harus Ditampilkan

1. **State utama**: Tabel berisi 4 baris dengan status berbeda (selesai, selesai parsial, gagal, diproses).
2. **State loading**: Satu baris penuh di tabel dengan teks "Memuat riwayat sinkronisasi…" di tengah.
3. **State kosong (belum ada sesi)**: Teks "Belum ada sesi sinkronisasi yang dijalankan." + tautan "Mulai sinkronisasi pertama" ke `/sinkronisasi`.
4. **State error API**: Banner merah di atas tabel, "Gagal memuat riwayat. Coba lagi."

---

## Catatan Desain Penting

- **Jangan** menampilkan nama petugas yang menjalankan sesi jika data tidak tersedia di API.
- Kolom "Batch Master" menampilkan ID batch snapshot yang dipakai sesi — bukan batch aktif saat ini.
- Halaman ini **read-only** — tidak ada tombol edit, hapus, atau jalankan ulang.
- Jangan menampilkan detail baris hasil di halaman ini — itu ada di halaman hasil detail.
- Angka ringkasan adalah ilustrasi dummy — jangan gunakan sebagai data nyata.

---

## Design Tokens (Ringkasan untuk Prompt Ini)

```
Background halaman  : #F5F7F6
Surface/kartu       : #FFFFFF
Teks utama          : #172321
Teks sekunder       : #66736F
Aksen utama         : #0F766E
Border              : #DDE4E1
Tabel header bg     : #F8FAFC
Tabel hover         : #F8FAFC

Badge Selesai bg/teks  : #ECFDF5 / #065F46
Badge Gagal bg/teks    : #FFF1F2 / #9F1239
Badge Diproses bg/teks : #EFF6FF / #1E40AF

Font UI             : IBM Plex Sans
Font data teknis    : IBM Plex Mono (ID batch, ID sesi)
Border radius       : 8–12 px
```

---

## Responsif

| Layar | Perilaku |
|-------|----------|
| ≥ 1024 px | Tabel penuh dengan semua kolom |
| 768–1023 px | Tabel horizontal scrollable, sidebar tersembunyi |
| < 768 px | Tabel horizontal scroll, tampilkan hanya kolom penting (Waktu, Nama File, Status, Aksi) |

---

## Aksesibilitas

- Tabel mempunyai `<caption>` atau `aria-label` "Riwayat sesi sinkronisasi".
- Tombol "Buka Hasil" mempunyai `aria-label` dengan nama file: "Buka hasil sesi data_wisuda_oktober.xlsx".
- Badge status mempunyai teks label yang dapat dibaca screen reader.
- State loading menggunakan `role="status"`.
- State empty menyertakan link ke halaman sinkronisasi.

---

## Instruksi Final untuk Google Stitch

Buat tepat **satu screen halaman Riwayat Sinkronisasi** yang menampilkan:
1. Shell layout: header + sidebar (Riwayat disorot) + konten.
2. Header halaman dengan judul dan deskripsi.
3. Tabel riwayat dengan 4 baris data dummy berbeda status: selesai, selesai, gagal, sedang diproses.
4. Setiap baris berisi: Waktu, Nama File, Badge Status, ID Batch Master (mono), Total Baris, Ringkasan Hasil, Tombol Aksi.
5. Pagination di bawah tabel.
6. Tampilkan frame state "empty state" (belum ada sesi) sebagai frame alternatif.
7. Tampilkan frame state "loading" sebagai frame alternatif.
8. Gunakan design tokens, gaya Swiss Minimalism, semua teks bahasa Indonesia.
