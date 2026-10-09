# 09 — Spesifikasi UI/UX dan Wireframe

## 1. Prinsip antarmuka
Sederhana untuk petugas administrasi; urut dari unggah master → unggah wisuda → proses → review → unduh. Tampilan bersih, label bahasa Indonesia, pesan error jelas, dan hasil yang belum pasti **tidak diberi warna/label seolah-olah valid**.

## 2. Navigasi
```text
ITCC Wisuda Sync
├── Login
└── Dashboard
    ├── Data Master
    │   ├── SITASI
    │   └── Certiport
    ├── Sinkronisasi
    ├── Hasil & Verifikasi
    └── Riwayat
```

## 3. Daftar halaman
| Halaman | Route usulan | Komponen utama |
|---|---|---|
| Login | `/login` | Email, password, feedback login |
| Dashboard | `/` atau `/dashboard` | Jumlah master aktif, proses terakhir, shortcut |
| SITASI | `/sitasi` | Upload, info batch aktif, filter NIM/nama/status/sertifikasi |
| Certiport | `/certiport` | Upload, batch aktif, filter nama/program/result |
| Sinkronisasi | `/sinkronisasi` | Dropzone XLSX, validasi header, proses |
| Hasil | `/sinkronisasi/{id}` | Summary, filter status, tabel hasil, rincian |
| Verifikasi | Dialog pada hasil | Data pembanding, kandidat, keputusan, catatan |
| Riwayat | `/riwayat` | Tanggal, filename, ID batch, jumlah hasil, detail |

## 4. Wireframe halaman utama
```text
+----------------+--------------------------------------------------+
| ITCC Sync      | Sinkronisasi Data Wisuda                        |
| Dashboard      |                                                  |
| Sinkronisasi * | [ Drag & Drop data_wisuda.xlsx ] [Pilih File]    |
| SITASI         | Format: .xlsx                                   |
| Certiport      |                                                  |
| Riwayat        | Nama file: data_wisuda.xlsx                     |
|                | Baris terbaca: 424 [contoh dataset]             |
|                | Batch SITASI: aktif / belum tersedia            |
|                | Batch Certiport: aktif / belum tersedia         |
|                |                                                  |
|                | [Validasi File]  [Proses Sinkronisasi]           |
+----------------+--------------------------------------------------+
```

## 5. Wireframe hasil
```text
+--------------------------------------------------------------+
| Hasil Sinkronisasi — wisuda.xlsx                             |
| [Total] [Valid] [Perlu Verifikasi] [Tidak Lulus] [Tidak Ada]  |
| Filter status [▼]   Cari NIM/Nama [________________]         |
|--------------------------------------------------------------|
| NIM | Nama | MOS | MCF | Status | Alasan | Aksi              |
| ... | .... | ... | ... | REVIEW | Nama ganda | [Periksa]    |
|--------------------------------------------------------------|
| [Unduh Excel] (nonaktif jika aturan output belum disahkan)   |
+--------------------------------------------------------------+
```

Angka contoh pada wireframe hanya ilustrasi, **bukan hasil sinkronisasi yang sudah diuji**.

## 6. Dialog verifikasi
Perlihatkan **sumber berdampingan**, tidak hanya skor fuzzy:
- Wisuda: NIM, nama, program studi.
- SITASI: nama, kategori, semua attempt relevan, status, source_row.
- Certiport: nama, kategori, certification name, result, source_row, kandidat ganda jika ada.
- Alasan review, siapa/kapannya, input catatan, pilihan `Konfirmasi cocok`, `Tidak cocok`, `Tunda`.
- Konfirmasi identitas tidak otomatis menyulap `FAIL` menjadi `PASS`.

## 7. State UI
| State | Tampilan |
|---|---|
| Belum upload | Instruksi memilih file |
| File salah | Pesan kolom hilang/format salah |
| Master belum aktif | Peringatan + tombol ke halaman import |
| Loading | Spinner/progress yang jujur; jangan tampil persen palsu |
| Proses selesai | Ringkasan real hasil server |
| Gagal | Kode/penjelasan tanpa stack trace |
| Review tersimpan | Update status + indikator jejak audit |
| Export belum diizinkan | Tombol nonaktif dengan penjelasan |

## 8. Aksesibilitas sederhana
Input/dropzone juga dapat digunakan lewat tombol pilih file; label form terlihat; validasi bukan semata warna; tabel bisa digulir; tombol punya keadaan disabled/loading; ukuran teks dapat dibaca pada laptop.

## 9. Design tokens sederhana (usulan)
Gunakan palet netral dan satu warna aksen. Status: `VALID` hijau, `PERLU_VERIFIKASI` amber, `TIDAK_LULUS` merah, `PENDING` abu/biru, `DATA_TIDAK_DITEMUKAN` abu; selalu tampilkan teks status karena warna tidak cukup.

## 10. Bukti untuk laporan
Ambil screenshot halaman sesudah benar-benar berjalan (login, import, preview, kasus review, export). Pada BAB IV jangan menggunakan wireframe sebagai bukti fitur sudah diimplementasikan.
