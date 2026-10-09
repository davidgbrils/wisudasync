# 01 — Project Charter

## Identitas
- **Nama:** Sistem Sinkronisasi dan Validasi Data Sertifikasi Mahasiswa pada Data Wisuda Menggunakan SITASI dan Certiport Berbasis Web.
- **Jenis:** Proyek magang/penerapan sistem informasi.
- **Pengguna:** Petugas ITCC yang diberi akses oleh penanggung jawab data.
- **Sponsor/pihak validasi:** Pembimbing lapangan dan penanggung jawab data ITCC/BAA (nama tidak ditetapkan).
- **Status:** Prototipe pengembangan; bukan pengganti verifikasi institusi sampai hasil diuji dan disetujui.

## Latar belakang masalah
Data wisuda, data sertifikasi di SITASI, dan hasil ujian Certiport berada pada sumber Excel berbeda. Staf perlu mencocokkan identitas serta sertifikasi agar kolom output pada daftar wisuda terisi. Masalah utamanya: jumlah baris cukup banyak, data SITASI menyimpan beberapa attempt per mahasiswa, nama tidak selalu ditulis sama, dan data Certiport tidak mempunyai NIM. Pencocokan manual berpotensi menyita waktu dan membuat hasil tidak konsisten.

## Tujuan SMART (target rancangan; perlu diuji)
1. Petugas dapat mengunggah file Excel dengan header sesuai sumber dan menerima validasi format sebelum proses.
2. Sistem menghasilkan hasil pencocokan per baris wisuda disertai status dan alasan pengecualian.
3. Data ambigu/konflik tidak ditetapkan valid tanpa intervensi petugas.
4. Hasil ekspor mempertahankan kolom, urutan, dan isi non-target Excel asli.
5. Semua hasil dapat ditelusuri ke sesi dan batch sumber yang dipakai.

Tidak ada janji pengurangan waktu tertentu tanpa baseline manual dan pengukuran pengujian.

## Lingkup MVP
**Masuk:** login petugas; impor SITASI/Certiport `.xlsx`; daftar dan pencarian master data; upload wisuda; pencocokan NIM/nama/program/status; preview; review manual; ekspor Excel; riwayat proses.  
**Di luar:** API langsung ke sistem eksternal, scraping website, OCR PDF, LLM untuk menentukan kelulusan, integrasi SIAKAD produksi, aplikasi Android, administrasi multi-unit rumit.

## Pemangku kepentingan
| Pihak | Peran |
|---|---|
| Petugas ITCC | Upload master, proses, review, ekspor |
| Staf BAA | Penyedia/pengguna daftar wisuda sesuai prosedur |
| Pembimbing lapangan | Verifikasi kelayakan alur dan output |
| Mahasiswa pengembang | Analisis, desain, implementasi, dokumentasi, testing |

## Keberhasilan proyek
Dianggap memenuhi MVP jika: file valid dapat diproses; kasus NIM yang sama dan multiple attempt ditangani; konflik lintas sumber masuk antrean review; hasil bisa diekspor tanpa kehilangan data asli; bukti uji black-box tersedia; pengguna terkait menerima format hasilnya.

## Batasan dan risiko
- Akses sumber hanya dari ekspor Excel; kesegaran data bergantung pada kapan petugas mengunggah.
- Format output sertifikasi belum disepakati sepenuhnya.
- Pencocokan berdasarkan nama tanpa NIM memiliki risiko salah orang.
- Data mahasiswa sensitif secara operasional dan harus dibatasi aksesnya.

## Produk akhir
Aplikasi internal, basis data, dokumentasi teknis, petunjuk penggunaan, matriks pengujian, dan laporan magang berdasarkan aktivitas yang terbukti.
