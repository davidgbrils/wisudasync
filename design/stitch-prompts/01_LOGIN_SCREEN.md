# Prompt Desain Google Stitch — Screen 01: Halaman Login

> **Instruksi penggunaan:** Salin seluruh isi file ini dan tempel ke kolom prompt Google Stitch. File ini hanya untuk satu screen. Jangan menggabungkannya dengan prompt lain.

---

## Konteks Produk

Ini adalah halaman login untuk aplikasi web internal bernama **ITCC Wisuda Sync** — sistem yang digunakan oleh petugas ITCC untuk melakukan sinkronisasi dan validasi data sertifikasi mahasiswa wisuda. Sistem ini tidak dapat diakses publik. Tidak ada pendaftaran mandiri oleh pengguna biasa; akun petugas dibuat oleh administrator.

Halaman login adalah satu-satunya titik masuk ke aplikasi. Setelah login berhasil, pengguna diarahkan ke halaman Ringkasan (Dashboard).

---

## Instruksi untuk Google Stitch

Buat **hanya satu screen**: halaman login. Jangan membuat halaman lain seperti dashboard, halaman daftar, atau halaman lupa kata sandi dalam desain ini.

---

## Pengguna dan Tugas Utama

**Pengguna:** Petugas ITCC yang sudah memiliki akun.
**Tugas:** Memasukkan email dan kata sandi untuk masuk ke sistem.

---

## Layout dan Komposisi

Halaman terdiri dari dua kolom pada layar laptop/desktop:

### Kolom Kiri (≤ 45% lebar)
- Background: `#F5F7F6` (abu hijau sangat muda).
- Konten tengah secara vertikal.
- Berisi:
  - Logo aplikasi: kotak 48×48 px, background `#0F4B46`, huruf "W" berwarna putih, font IBM Plex Sans Semibold, border radius 10 px.
  - Di bawah logo: teks nama aplikasi **"ITCC Wisuda Sync"**, font IBM Plex Sans, ukuran 20 px, warna `#172321`, Semibold.
  - Di bawah nama: teks kecil "Sistem sinkronisasi data sertifikasi mahasiswa wisuda", ukuran 13 px, warna `#66736F`.
  - Jarak vertikal antar elemen: 12 px.

### Kolom Kanan (≥ 55% lebar)
- Background: `#FFFFFF`.
- Berisi kartu formulir login di tengah secara vertikal dan horizontal.
- Kartu formulir:
  - Padding: 40 px.
  - Tidak ada bayangan atau border yang mencolok — cukup sedikit separasi visual.
  - Lebar maksimal kartu: 400 px.

---

## Komponen Formulir Login

### Judul
- Teks: **"Masuk ke Sistem"**
- Font: IBM Plex Sans Semibold, 22 px, warna `#172321`.
- Sub-judul/deskripsi: "Masukkan akun petugas ITCC Anda untuk mengakses sistem.", ukuran 13 px, warna `#66736F`.
- Jarak ke formulir: 24 px.

### Field Email
- Label terlihat (bukan placeholder): **"Email"**, font IBM Plex Sans Medium 13 px, warna `#172321`.
- Input tipe email, placeholder: "contoh@itcc.ac.id".
- Tinggi input: 44 px. Border: `1px solid #DDE4E1`. Border radius: 8 px.
- Focus ring: `2px solid #0F766E`.

### Field Kata Sandi
- Label terlihat: **"Kata Sandi"**.
- Input tipe password.
- Di sebelah kanan label kata sandi: teks kecil "Lupa kata sandi?" — ini adalah placeholder statis, **tidak perlu aktif atau mengarah ke halaman lain** pada desain ini.
- Tampilan tombol "lihat/sembunyikan" kata sandi (ikon mata) di sisi kanan input.

### Tombol Masuk
- Teks: **"Masuk"**.
- Lebar penuh (100% lebar kartu).
- Tinggi: 44 px. Background: `#0F766E`. Teks putih. Border radius: 8 px.
- Versi loading: teks berubah menjadi "Sedang masuk…" dengan spinner kecil di kiri teks.
- Versi disabled: opacity 50%.

### Pesan Error
- Tampil di antara field terakhir dan tombol, atau di atas tombol.
- Background `#FFF1F2`, border `1px solid #FECDD3`, teks `#9F1239`.
- Contoh teks: "Email atau kata sandi tidak sesuai. Silakan coba lagi."
- Border radius: 8 px. Padding: 12 px.

### Pesan Sukses (opsional, untuk registrasi yang berhasil)
- Background `#ECFDF5`, border `1px solid #A7F3D0`, teks `#065F46`.
- Contoh teks: "Akun berhasil dibuat. Silakan masuk menggunakan akun Anda."

---

## State yang Harus Ditampilkan

Tampilkan dalam satu kanvas tiga variasi state (susun vertikal atau gunakan frame terpisah):

1. **State default/kosong**: Formulir kosong, semua field bersih, tombol aktif.
2. **State error**: Field terisi (atau kosong), pesan error muncul, tombol tetap aktif.
3. **State loading**: Tombol dalam kondisi loading ("Sedang masuk…" + spinner), field dinonaktifkan.

---

## Interaksi Penting

- Tombol "Masuk" nonaktif saat sedang proses loading.
- Pesan error muncul di bawah field kata sandi, di atas tombol.
- Fokus otomatis ke field email saat halaman pertama dimuat.
- Tekan Enter pada field mana pun akan submit formulir.

---

## Catatan Desain Penting

- **Jangan** tambahkan tombol "Daftar akun baru" atau tautan ke pendaftaran publik. Sistem ini tidak mendukung registrasi mandiri oleh pengguna umum.
- **Jangan** tambahkan opsi login sosial (Google, Microsoft, dll.).
- **Jangan** tampilkan kolom nama atau field lain selain email dan kata sandi.
- **Jangan** tambahkan ilustrasi besar atau gambar latar dekoratif.
- Desain harus terasa profesional, bersih, dan enterprise — bukan aplikasi SaaS publik.

---

## Design Tokens (Ringkasan untuk Prompt Ini)

```
Background halaman  : #F5F7F6
Surface/kartu       : #FFFFFF
Teks utama          : #172321
Teks sekunder       : #66736F
Aksen utama         : #0F766E
Border              : #DDE4E1
Error bg            : #FFF1F2  |  Error border : #FECDD3  |  Error teks : #9F1239
Sukses bg           : #ECFDF5  |  Sukses border: #A7F3D0  |  Sukses teks: #065F46
Font                : IBM Plex Sans
Border radius       : 8–12 px
```

---

## Responsif

| Layar          | Perilaku                                                       |
|----------------|----------------------------------------------------------------|
| ≥ 1024 px (laptop) | Dua kolom: kiri (branding), kanan (formulir)              |
| 768–1023 px (tablet) | Satu kolom, branding di atas, formulir di bawah          |
| < 768 px (ponsel) | Satu kolom, hanya formulir (branding disederhanakan ke logo + nama saja di atas) |

---

## Aksesibilitas

- Setiap `<input>` dihubungkan ke `<label>` yang terlihat.
- Tombol masuk mempunyai teks deskriptif (bukan hanya ikon).
- Pesan error menggunakan `role="alert"` agar dibaca screen reader.
- Urutan tab: logo → field email → field kata sandi → tombol masuk.

---

## Instruksi Final untuk Google Stitch

Buat tepat **satu screen halaman login** dengan elemen berikut:
1. Kartu formulir di kanan (atau tengah pada mobile) berisi field email, field kata sandi, dan tombol "Masuk".
2. Area branding di kiri berisi logo "W" + nama aplikasi + deskripsi singkat.
3. Tampilkan tiga frame/state: default kosong, error aktif, dan tombol loading.
4. Gunakan design tokens yang tercantum di atas.
5. Semua teks dalam bahasa Indonesia.
6. Gaya desain: Swiss Minimalism, bersih, tidak ada dekorasi berlebihan.
