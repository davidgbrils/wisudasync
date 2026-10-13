# Prompt Desain Google Stitch — Screen 07: Panel Verifikasi Detail Baris

> **Instruksi penggunaan:** Salin seluruh isi file ini dan tempel ke kolom prompt Google Stitch. File ini hanya untuk satu screen. Jangan menggabungkannya dengan prompt lain.

---

## Konteks Produk

**ITCC Wisuda Sync** adalah aplikasi web internal. Panel/Dialog Verifikasi Detail Baris dibuka saat petugas mengklik tombol "Periksa" pada salah satu baris di halaman Hasil Sinkronisasi. Panel ini menampilkan semua bukti sumber dan memungkinkan petugas membuat keputusan manual.

Panel ini ditampilkan sebagai **drawer/panel samping yang muncul dari kanan**, atau **dialog modal besar** — mempertahankan tabel hasil di latar. Panel ini bukan halaman baru tersendiri.

---

## Instruksi untuk Google Stitch

Buat **hanya satu screen** yang menampilkan halaman Hasil Sinkronisasi dengan **panel verifikasi terbuka di sebelah kanan**. Tabel hasil tetap terlihat di latar (sedikit gelap/blur). Jangan membuat halaman baru yang terpisah.

---

## Pengguna dan Tugas Utama

**Pengguna:** Petugas ITCC yang sudah login.
**Tugas utama:** Membandingkan data dari tiga sumber (Wisuda, SITASI, Certiport), memahami alasan review, dan membuat keputusan beserta catatan.

---

## Layout Halaman + Panel

```
┌─────────────────────────────────────┬──────────────────────────┐
│ Latar: Tabel Hasil (sedikit gelap)  │  PANEL VERIFIKASI        │
│                                     │  (lebar 480–560 px)      │
│  [baris-baris tabel terlihat samar] │                          │
│                                     │  Budi Santoso            │
│                                     │  NIM: 2021001003         │
│                                     │  Status: PERLU_VERIFIKASI│
│                                     │  ...                     │
└─────────────────────────────────────┴──────────────────────────┘
```

Panel muncul dari kanan, memiliki:
- Background `#FFFFFF`.
- Shadow kiri: `box-shadow: -4px 0 20px rgba(0,0,0,0.1)`.
- Tombol × / tutup di pojok kanan atas panel.
- Konten dapat di-scroll secara vertikal.

---

## Konten Panel Verifikasi

### 1. Header Panel

- Judul: Nama mahasiswa wisuda, mis. **"Ahmad Fauzi"**, IBM Plex Sans Semibold 18 px.
- NIM: **"2021001003"**, IBM Plex Mono 13 px, warna `#66736F`.
- Badge status: "Perlu Verifikasi", `bg: #FFFBEB`, teks `#92400E`, border `#FCD34D`, pill.
- Divider `1px #DDE4E1` di bawah header.

### 2. Seksi Data Sumber (Tiga Kolom atau Kartu Berdampingan)

Tampilkan tiga blok bukti secara berdampingan (jika cukup lebar) atau vertikal:

**Blok A — Data Wisuda** (sumber awal):
- Judul kecil: "DATA WISUDA", uppercase 11 px, `#66736F`.
- Isi:
  - NIM: `2021001003`
  - Nama: `Ahmad Fauzi`
  - Program Studi: `Teknik Informatika`
  - Baris sumber: `4`
- Background: `#F8FAFC`, border `1px #DDE4E1`, radius 8 px, padding 12 px.

**Blok B — Data SITASI** (hasil pencocokan NIM):
- Judul kecil: "DATA SITASI", uppercase 11 px, `#66736F`.
- Isi (bisa lebih dari satu baris attempt):
  - NIM: `2021001003` ✓ (cocok)
  - Nama SITASI: `Ahmad Fauzi` (sama) atau `Ahmad F.` (berbeda — tandai)
  - Sertifikasi: `MOS`, Sub Program: `Word 2019`
  - Status attempt 1: `TIDAK LULUS`
  - Status attempt 2: `LULUS`
  - Baris sumber SITASI: `1247` (IBM Plex Mono)
- Jika nama SITASI berbeda dengan nama wisuda: tampilkan badge kecil "Nama berbeda" berwarna amber.
- Background: `#F8FAFC`, border `1px #DDE4E1`, radius 8 px.

**Blok C — Kandidat Certiport** (pencocokan berbasis nama):
- Judul kecil: "KANDIDAT CERTIPORT", uppercase 11 px, `#66736F`.
- Isi (satu atau lebih kandidat):
  - Nama Certiport: `Ahmad F.`
  - Program: `Microsoft Office Specialist`
  - Sertifikasi: `Word 2019`
  - Hasil: `PASS`
  - Baris sumber: `89` (IBM Plex Mono)
  - Metode cocok: "Nama normalisasi" (bukan fuzzy)
  - Jika kandidat lebih dari satu: tampilkan keduanya dalam daftar dengan label "Kandidat Ganda — risiko salah orang" berwarna amber.
  - Skor kemiripan (jika ada fuzzy): tampilkan sebagai info tambahan saja: "Kemiripan: 93%" — **bukan bukti identitas.**
- Background: `#F8FAFC`, border `1px #DDE4E1`, radius 8 px.

### 3. Seksi Alasan Review

- Judul H2: "Alasan Perlu Verifikasi".
- Teks alasan dari sistem (kuning/amber): mis. "Nama Certiport berbeda dengan nama SITASI. Ditemukan lebih dari satu kandidat dengan nama serupa."
- Background: `#FFFBEB`, border `1px #FCD34D`, teks `#92400E`, radius 8 px, padding 12 px.

### 4. Riwayat Keputusan Sebelumnya (Jika Ada)

- Judul kecil: "Riwayat Tinjauan", 12 px.
- Daftar keputusan sebelumnya (jika ada):
  - "12 Okt 2026, 20:30 — Tunda Verifikasi" oleh "Petugas A" — Catatan: "Perlu konfirmasi dari SITASI"
  - Tampil sebagai timeline sederhana.
- Jika belum ada riwayat: "Belum ada riwayat tinjauan untuk baris ini."

### 5. Formulir Keputusan

- Judul H2: "Keputusan Verifikasi".
- **Pilihan keputusan** (radio button atau tiga tombol pilihan):
  1. "Konfirmasi Cocok" — warna hijau saat dipilih.
  2. "Tidak Cocok" — warna merah saat dipilih.
  3. "Tunda Verifikasi" — warna abu saat dipilih (default).
- **Catatan/alasan wajib** (textarea):
  - Label: "Catatan Verifikasi (wajib diisi)".
  - Placeholder: "Tuliskan alasan atau dasar keputusan Anda…"
  - Min-height: 80 px.
- **Peringatan penting** (sebelum tombol):
  - Teks kecil italic amber: "Konfirmasi identitas tidak otomatis mengubah hasil ujian FAIL menjadi PASS."
- Tombol "Simpan Keputusan" (primer, `bg: #0F766E`):
  - Disabled jika catatan kosong.
  - State loading: "Menyimpan…".
- Tombol "Batal" (sekunder, di samping tombol simpan).

### 6. Pesan Sukses / Error Simpan

- Sukses: "Keputusan berhasil disimpan.", `bg: #ECFDF5`, teks `#065F46`.
- Error: "Keputusan gagal disimpan. Coba lagi.", `bg: #FFF1F2`, teks `#9F1239`.

---

## State yang Harus Ditampilkan

1. **State utama**: Panel terbuka dengan semua data terisi, keputusan "Tunda Verifikasi" dipilih, catatan kosong, tombol simpan disabled.
2. **State keputusan dipilih + catatan diisi**: Tombol simpan aktif.
3. **State loading simpan**: Tombol "Menyimpan…" + spinner.
4. **State sukses simpan**: Pesan hijau, tombol kembali ke tabel.

---

## Aturan Bisnis yang Harus Dicerminkan Dalam Desain

- **Fuzzy score BUKAN bukti identitas**: Tampilkan sebagai "Kemiripan: 93%" dengan teks kecil "hanya sebagai petunjuk, bukan konfirmasi".
- **Kandidat ganda TIDAK boleh auto-VALID**: Tampilkan peringatan "Kandidat Ganda" yang jelas.
- **Konfirmasi Cocok TIDAK mengubah hasil ujian**: Tampilkan peringatan kuning yang jelas sebelum tombol simpan.
- **Setiap keputusan harus menyertakan catatan**: Tombol simpan disabled tanpa catatan.
- Status baru setelah konfirmasi: `KONFIRMASI_COCOK`, `TIDAK_COCOK`, atau `TUNDA_VERIFIKASI` — bukan otomatis menjadi VALID.

---

## Catatan Desain Penting

- Semua tiga blok sumber harus terlihat sekaligus (atau dapat digeser/ditab) untuk memudahkan perbandingan.
- Jangan gunakan warna sebagai satu-satunya penanda perbedaan — tambahkan label teks "Nama berbeda", "Kandidat Ganda".
- Jangan membuat tampilan yang mengimplikasikan keputusan sudah diambil sebelum petugas menekan tombol.

---

## Design Tokens (Ringkasan untuk Prompt Ini)

```
Background panel    : #FFFFFF
Shadow panel        : -4px 0 20px rgba(0,0,0,0.1)
Teks utama          : #172321
Teks sekunder       : #66736F
Aksen utama         : #0F766E
Border              : #DDE4E1
Blok bukti bg       : #F8FAFC

PERLU_VERIFIKASI bg/teks/border : #FFFBEB / #92400E / #FCD34D
Peringatan bg/teks/border       : #FFFBEB / #92400E / #FCD34D
VALID bg/teks/border            : #ECFDF5 / #065F46 / #A7F3D0
Error bg/teks/border            : #FFF1F2 / #9F1239 / #FECDD3

Font UI             : IBM Plex Sans
Font data teknis    : IBM Plex Mono (NIM, baris sumber, ID)
Border radius       : 8–12 px
```

---

## Responsif

| Layar | Perilaku |
|-------|----------|
| ≥ 1024 px | Panel drawer kanan 480–560 px, tabel terlihat di latar |
| 768–1023 px | Panel drawer kanan lebar penuh atau 420 px |
| < 768 px | Panel modal full-screen, tabel tersembunyi |

---

## Aksesibilitas

- Panel mempunyai `role="dialog"` dan `aria-modal="true"`.
- Fokus otomatis pindah ke dalam panel saat dibuka.
- Tombol × mempunyai `aria-label="Tutup panel verifikasi"`.
- Radio button keputusan mempunyai label yang jelas.
- Textarea mempunyai label yang terlihat, bukan hanya placeholder.
- Pesan sukses/error menggunakan `role="alert"`.

---

## Instruksi Final untuk Google Stitch

Buat tepat **satu screen** yang menampilkan:
1. Latar: Halaman Hasil Sinkronisasi yang sedikit gelap/blur (overlay ringan).
2. Panel verifikasi dari kanan (lebar ~480 px) yang terbuka penuh dengan scroll vertikal.
3. Header panel: nama mahasiswa, NIM mono, badge "Perlu Verifikasi".
4. Tiga blok bukti berdampingan: Data Wisuda, Data SITASI (dengan informasi attempt), Kandidat Certiport (dengan info kemiripan dan peringatan kandidat ganda).
5. Blok alasan review berwarna amber.
6. Formulir keputusan: tiga pilihan radio + textarea catatan + peringatan "konfirmasi ≠ ubah hasil" + tombol simpan.
7. Tampilkan state utama: keputusan "Tunda Verifikasi" terpilih, catatan belum diisi, tombol simpan disabled.
8. Tampilkan frame alternatif: semua diisi, tombol simpan aktif.
9. Gunakan design tokens, gaya Swiss Minimalism, semua teks bahasa Indonesia.
