# 13 — Panduan Menyusun Laporan Magang dari Proyek

**Gaya bahasa:** Mahasiswa S1 yang profesional, jelas, tidak terlalu teknis. Ikuti **pedoman resmi kampus** jika format/judul BAB berbeda; ini hanya kerangka awal.

## Rekomendasi judul
**“Perancangan dan Implementasi Sistem Sinkronisasi Data Sertifikasi Mahasiswa pada Data Wisuda Menggunakan SITASI dan Certiport Berbasis Web”**.

Gunakan kata **Perancangan** saja bila yang diselesaikan baru desain. Tambahkan **Implementasi** setelah fitur utama telah benar-benar berjalan.

## BAB I — Pendahuluan
### 1.1 Latar Belakang
Uraikan pengolahan Excel wisuda dan sertifikasi, tiga sumber data, kebutuhan mengurangi pencocokan manual, masalah NIM ganda sebagai riwayat, Certiport tidak punya NIM, serta risiko beda penulisan nama. Jangan menulis klaim kuantitatif efisiensi jika belum ada pengukuran.

### 1.2 Rumusan Masalah
1. Bagaimana membangun aplikasi yang mengolah Excel wisuda dan data sertifikasi SITASI/Certiport?
2. Bagaimana mencocokkan mahasiswa berdasarkan NIM serta memverifikasi data ujian yang hanya memiliki nama?
3. Bagaimana menyajikan hasil dan kasus yang memerlukan pemeriksaan manual dalam format Excel?

### 1.3 Batasan Masalah
`.xlsx`, MOS/MCF, impor offline dari file ekspor, satu aktor petugas, tidak mencakup sistem produksi langsung atau LLM.

### 1.4 Tujuan dan Manfaat
Tujuan pembuatan aplikasi sesuai PRD. Manfaat: membantu pengecekan, menyediakan status, jejak proses dan keluaran format yang dapat dipakai staf (manfaat potensial, bukan hasil terukur sampai diuji).

## BAB II — Gambaran Umum Tempat Magang & Dasar Teori
- Profil instansi/unit sesuai informasi resmi pembimbing, bukan hasil karangan.
- Tugas dan alur kerja magang sesuai catatan kegiatan sebenarnya.
- Dasar teori: sistem informasi, Python, FastAPI, Next.js, database relasional, pengolahan Excel, data matching, validasi data, fuzzy matching sebagai bantuan, black-box testing.
- Kutip sumber teknis resmi secukupnya; hindari paragraf salinan dokumentasi.

## BAB III — Analisis & Perancangan
Gunakan dokumen yang sudah dibuat:
- Analisis proses berjalan dan usulan proses (Project Charter/PRD).
- Kebutuhan fungsional dan nonfungsional (SRS).
- Use case (1 petugas), Activity Diagram, flowchart matching, ERD (Design Phase 2 dan Architecture).
- Desain database (tabel data master dan tabel sesi/result; bedakan yang sudah dibuat dengan rencana).
- Wireframe dashboard, impor, sinkronisasi, hasil dan review.
- Tabel data input/output dari `05_DATA_DICTIONARY.md`.

## BAB IV — Implementasi dan Pengujian
**Jangan menulis seolah fitur selesai sebelum demonstrasi berhasil.** Dokumentasikan sesuai urutan sebenarnya:
1. Lingkungan pengembangan dan tool versi aktual.
2. Tampilan backend/frontend yang berfungsi, beserta screenshot.
3. Import SITASI & Certiport: file uji, validasi header, hasil baris, contoh error.
4. Normalisasi/matching: contoh **data dummy**, penjelasan algoritma, perbedaan status sumber.
5. Review: screenshot rincian konflik dan catatan keputusan bila sudah diterapkan.
6. Export: perbandingan workbook asli vs output bila mapping disetujui.
7. Tabel black-box dari Test Plan lengkap tanggal, hasil aktual, PASS/FAIL, bug dan revisi.

## BAB V — Penutup
Kesimpulan hanya menyebut capaian yang terbukti dari hasil BAB IV, keterbatasan data dan kasus ambigu, serta saran pengembangan seperti integrasi sumber resmi jika tersedia dan diizinkan.

## Template paragraf akademik (contoh)
> Sistem yang dirancang bertujuan membantu petugas melakukan pencocokan data mahasiswa pada file wisuda dengan data sertifikasi. Proses pencocokan utama dilakukan menggunakan NIM yang tersedia pada data wisuda dan SITASI. Data Certiport digunakan sebagai sumber pembanding tambahan melalui kesesuaian nama dan jenis ujian. Untuk mengurangi risiko ketidaksesuaian data, hasil yang belum dapat dipastikan ditandai agar dapat diperiksa oleh petugas.

Teks tersebut adalah pernyataan **rancangan**, bukan klaim hasil sukses.

## Berkas pendukung yang sebaiknya disiapkan
- Log kegiatan mingguan, tanggal, nama aktivitas dan bukti.
- Screenshots halaman aplikasi yang benar-benar berjalan.
- Diagram final yang sesuai implementasi terakhir.
- Test case dengan data dummy dan catatan hasil nyata.
- Daftar sumber/referensi dengan gaya sitasi yang diminta kampus.
- Persetujuan untuk menampilkan data dan identitas institusi di laporan; sensor nama/NIM jika perlu.

## Batas etika akademik
Jangan menampilkan data mahasiswa tanpa izin, mengaku mengembangkan fitur yang belum dibuat, menuliskan persentase akurasi tanpa ground truth, atau menampilkan benchmark yang belum dilakukan. Narasi dibuat setara mahasiswa yang memahami sistemnya sendiri.
