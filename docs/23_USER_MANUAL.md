# 23 — User Manual Petugas: Upload, Review, Export

Panduan ini untuk **petugas ITCC** yang memakai aplikasi ITCC Wisuda Sync melalui browser. Bahasa dibuat sederhana. Semua contoh identitas bersifat fiktif.

> **Penting:** Sejak 2026-10-23 ekspor **final** aktif. Kolom `Sertifikasi MOS`, `Sertifikasi MCF`, dan `Title Microsoft` hanya diisi untuk status **LULUS**; status lain dikosongkan. Pratinjau DRAFT tetap tersedia. Selama lingkungan Supabase **development berizin** belum tersedia, aplikasi belum boleh dipakai dengan data asli.

---

## 1. Sebelum mulai

Pastikan:
1. Anda sudah punya akun petugas yang terdaftar dengan role `staff` atau `admin` (dibuat oleh admin, lihat `docs/17_OPERATIONS.md`).
2. Backend FastAPI dan frontend Next.js sudah berjalan di lingkungan yang berizin.
3. Data master SITASI dan Certiport sudah diimpor (lihat `docs/24_OPERATOR_GUIDE.md`) — tanpa keduanya, sinkronisasi ditolak.

Alur singkat petugas:

```
Login  →  (Data Master sudah diimpor)  →  Sinkronisasi (Upload Wisuda)
       →  Validasi file  →  Proses Sinkronisasi  →  Review hasil
       →  Unduh Excel Final (LULUS saja)
```

---

## 2. Login

1. Buka alamat aplikasi, Anda diarahkan ke halaman **Masuk**.
2. Isi email dan kata sandi akun petugas, lalu klik **Masuk**.
3. Jika berhasil, Anda masuk ke halaman **Ringkasan** (`/dashboard`).
4. Jika akun tidak berhak sebagai petugas, Anda melihat halaman **Akses ditolak** (`/unauthorized`).
5. Untuk keluar, klik tombol **Keluar** di sudut kanan atas.

> Tips: lupa keluar? Tutup browser tetap **tidak** mencabut sesi. Selalu gunakan tombol **Keluar**.

---

## 3. Menyiapkan data master (ringkas)

Data master dikelola di menu **Data SITASI** dan **Data Certiport**. Setiap impor membuat **batch baru**; hanya batch terakhir yang sukses menjadi **aktif**. Bila belum ada batch aktif, halaman menampilkan "Belum ada batch aktif".

Detail langkah, format file, dan pemulihan kegagalan ada di `docs/24_OPERATOR_GUIDE.md`.

---

## 4. Upload data Wisuda dan validasi

1. Buka menu **Sinkronisasi** (`/sinkronisasi`).
2. Seret berkas Excel Wisuda (`.xlsx`, sheet `Wisuda`) ke area unggah, atau klik **Pilih file**.
3. Klik **Validasi file** untuk pemeriksaan cepat **tanpa mengubah database**. Sistem menampilkan:
   - jumlah baris mahasiswa dan baris kosong;
   - kesesuaian urutan kolom;
   - daftar masalah per baris (mis. NIM kosong/ganda) tanpa menampilkan NIM/nama;
   - ringkasan batch SITASI dan Certiport yang aktif.
4. Perbaiki berkas bila ada masalah, lalu unggah ulang.

Berkas `.xlsx` wajib. Berkas `.xlsm`/bermakro, berkas berformula pada kolom wajib, dan berkas melebihi batas ukuran (default 10 MiB) akan ditolak dengan pesan kesalahan.

Header SITASI: `NIM`, `Nama`, `Sertifikasi`, `Nilai`, `Status` (opsional: `Kode NIM`, `Program Studi`, `Fakultas`, `Angkatan`, `Sub Program`). Header Certiport: `Nama`, `Sertifikasi`, `Nilai`, `Status`. Skema lama Certiport masih dibaca sebagai fallback.

---

## 5. Menjalankan sinkronisasi

1. Pada halaman yang sama, klik **Proses Sinkronisasi**.
2. Sistem membuat **sesi** baru, mencocokkan tiap baris Wisuda:
   - mencari SITASI memakai **NIM** (semua attempt diambil, tidak hanya baris pertama);
   - mencari kandidat Certiport memakai **nama** (Certiport tidak punya NIM);
   - menentukan status per ujian dan status keseluruhan.
3. Setelah selesai, Anda otomatis diarahkan ke halaman hasil **`/sinkronisasi/[id]`**.
4. Bila salah satu batch master belum ada, proses **ditolak** dengan pesan bahwa batch aktif belum lengkap.

Status yang mungkin muncul (`docs/02_PRD.md` §7):

| Status | Arti singkat |
|---|---|
| `VALID` | Bukti SITASI & Certiport sesuai dan unik untuk ujian itu |
| `PERLU_VERIFIKASI` | Ambiguitas/konflik; butuh keputusan petugas |
| `TIDAK_LULUS` | Semua bukti menunjukkan belum lulus (bukan keputusan akademik final) |
| `PENDING` | Belum cukup bukti selesai |
| `DATA_TIDAK_DITEMUKAN` | NIM tidak ada di batch SITASI aktif |

> Catatan: status `VALID` berarti **bukti sertifikasi untuk ujian tersebut lengkap**, bukan pernyataan bahwa mahasiswa memenuhi syarat wisuda. Sistem tidak menyimpulkan syarat kelulusan (ADR-011).

---

## 6. Meninjau hasil (review)

1. Di halaman hasil, gunakan **filter status** dan **filter "Hanya Perlu Review"**, atau **pencarian NIM/Nama**.
2. Klik baris untuk membuka **modal rincian bukti**: perbandingan nama Wisuda vs SITASI, serta bukti per ujian (kategori, nama ujian, baris SITASI/Certiport, skor, alasan).
3. Pilih keputusan:
   - `TUNDA_VERIFIKASI` — tunda dulu;
   - `TIDAK_COCOK` — bukti tidak sesuai;
   - `KONFIRMASI_COCOK` — konfirmasi identitas cocok.
4. Tulis **catatan** (wajib) lalu simpan.
5. Keputusan tersimpan sebagai jejak audit (petugas, waktu, keputusan, catatan) dan **tidak** mengubah bukti sumber.

**Pembatasan hak (ADR-009, belum disahkan):** selama kebijakan reviewer belum ditetapkan, petugas `staff` biasa hanya boleh memilih `TUNDA_VERIFIKASI` atau `TIDAK_COCOK`. `KONFIRMASI_COCOK` dibatasi untuk `admin`. Konfirmasi identitas **tidak** mengubah nilai `FAIL` menjadi `PASS`.

---

## 7. Ekspor

1. Di halaman hasil, gunakan bilah **Ekspor**.
2. Klik **Unduh Excel Final** untuk mengunduh workbook delapan kolom Wisuda. Kolom `Sertifikasi MOS` berisi `MOS (Lulus)`, `Sertifikasi MCF` berisi `MCF (Lulus)` (prodi 31/32), dan `Title Microsoft` berisi `MOS`, `MCF`, atau `MOS, MCF`. Sel yang tidak LULUS kosong.
3. Klik **Unduh Pratinjau (DRAFT)** bila ingin berkas berlabel `[DRAFT]` untuk pemeriksaan internal.
4. Untuk pemrosesan lokal tanpa aplikasi web, jalankan `backend/scripts/generate_validation_workbook.py`. Hasilnya `hasil_wisuda_terisi.xlsx`; `data_wisuda.xlsx` asli tidak diubah.

---

## 8. Riwayat sesi lama

Buka menu **Riwayat** (`/riwayat`) untuk melihat daftar sesi (waktu, nama file, snapshot batch SITASI/Certiport, total baris, ringkasan status). Sesi lama tetap merujuk batch master yang dipakai saat itu, walaupun batch baru diaktifkan kemudian.

---

## 9. Masalah umum

| Gejala | Kemungkinan penyebab | Tindakan |
|---|---|---|
| Diarahkan ke login terus | Sesi habis atau belum login | Login ulang |
| Halaman "Akses ditolak" | Akun bukan petugas aktif | Hubungi admin |
| Tombol proses menolak | Batch SITASI/Certiport belum aktif | Impor data master lebih dulu |
| Berkas ditolak | Bukan `.xlsx`, sheet/header salah, bermakro, atau >10 MiB | Perbaiki sesuai pesan |
| Kolom sertifikasi kosong | Status bukan LULUS atau data tidak ditemukan | Periksa sumber SITASI/Certiport; jangan mengisi manual tanpa bukti |
| Status banyak `PERLU_VERIFIKASI` | Nama ambigu/ujian tak ekuivalen | Tinjau manual; jangan paksa VALID |

---

## 10. Yang belum ada (jangan diasumsikan)

- **Ekspor final resmi** — aktif, tetapi hanya mengisi bukti LULUS (bukan syarat wisuda).
- **Integrasi langsung API SITASI/Certiport** — di luar MVP; sumber tetap diimpor dari Excel.
- **Akurasi terukur** — belum ada ground truth yang diverifikasi; skor fuzzy bukan persentase kebenaran.
- **UAT & verifikasi runtime Supabase** — belum dijalankan (lihat `docs/22_UAT_FORM.md`).
