# 02 — Product Requirements Document (PRD)

**Produk:** ITCC Wisuda Sync · **Versi:** 1.0-draft · **Tanggal:** 30 September 2026  
**Status persetujuan:** Usulan; butuh validasi petugas ITCC untuk output akhir.

## 1. Ringkasan produk
Aplikasi web internal yang menerima ekspor Excel SITASI, Certiport, dan daftar wisuda. Petugas mengelola data master, mengunggah daftar wisuda, kemudian sistem mencocokkan NIM ke SITASI dan memverifikasi hasil sertifikasi menggunakan data Certiport. Setiap baris memperoleh hasil dan alasan, kasus ambigu ditinjau manual, lalu petugas mengunduh Excel mengikuti template wisuda.

## 2. Pernyataan masalah
Proses manual memerlukan pengecekan antar-file, termasuk riwayat attempt ganda, perbedaan penulisan nama, serta label program ujian yang tidak sepenuhnya sama. Jika hanya mengambil baris SITASI pertama atau hanya membandingkan nama, hasil berisiko keliru. Dibutuhkan proses yang **terulang, tercatat, dan memberi ruang keputusan manual**.

## 3. Pengguna dan kebutuhan
| Pengguna | Kegiatan | Kebutuhan utama |
|---|---|---|
| Petugas ITCC | Kelola data sertifikasi | File mudah diimpor, riwayat batch terlihat |
| Petugas ITCC/BAA berwenang | Lengkapi daftar wisuda | Hasil sesuai kolom Excel dan bisa diperiksa |
| Pembimbing/penanggung jawab | Evaluasi hasil | Jejak sumber, kasus konflik, bukti uji |

MVP menerapkan **satu tipe aktor aplikasi: petugas berwenang**. Perbedaan tanggung jawab institusional tidak harus diwujudkan sebagai banyak role dalam versi pertama.

## 4. Alur pengguna utama
1. Petugas login.
2. Petugas mengunggah ekspor SITASI dan Certiport; masing-masing divalidasi lalu disimpan sebagai batch aktif.
3. Petugas memilih menu Sinkronisasi dan mengunggah data wisuda `.xlsx`.
4. Sistem mengecek header, nomor NIM, baris kosong, serta ketergantungan pada master data aktif.
5. Sistem memproses tiap wisudawan: pencarian SITASI berdasarkan NIM, agregasi attempt per jenis/ujian, lalu pencarian kandidat Certiport berdasarkan nama serta jenis ujian.
6. Sistem menampilkan tabel status dengan penjelasan alasan dan kandidat pencocokan.
7. Petugas meninjau hasil yang memerlukan verifikasi dan membuat keputusan disertai catatan.
8. Petugas mengekspor Excel; data asli pada kolom lain tetap dipertahankan.

## 5. Prioritas fitur
P0 = wajib agar sistem menghasilkan output yang aman dan dapat dipertanggungjawabkan; P1 = penting untuk operasional yang nyaman; P2 = pengembangan lanjutan.

| ID | Fitur | Prioritas | Status kode saat dokumen dibuat |
|---|---|---|---|
| PRD-01 | Login dan kontrol akses petugas | P0 | RENCANA — **belum ada di starter** |
| PRD-02 | Validasi header & impor SITASI `.xlsx` | P0 | SUDAH ADA dalam starter Phase 4 |
| PRD-03 | Validasi header & impor Certiport `.xlsx` | P0 | SUDAH ADA dalam starter Phase 4 |
| PRD-04 | Riwayat batch import + satu batch aktif per sumber | P0 | SUDAH ADA sebagai rancangan kode/schema |
| PRD-05 | Cari, filter, paginasi data master | P1 | SUDAH ADA dasar |
| PRD-06 | Upload & validasi Excel wisuda | P0 | RENCANA |
| PRD-07 | Matching Wisuda→SITASI berdasarkan NIM | P0 | RENCANA |
| PRD-08 | Agregasi multiple attempt per ujian | P0 | RENCANA |
| PRD-09 | Validasi SITASI↔Certiport berdasar identitas+ujian | P0 | RENCANA |
| PRD-10 | Status + alasan + penanda ketidakpastian | P0 | RENCANA |
| PRD-11 | Pemeriksaan/keputusan manual + audit | P0 | RENCANA |
| PRD-12 | Preview, pencarian, filter hasil | P0 | RENCANA |
| PRD-13 | Ekspor `.xlsx` sesuai kolom asli | P0 | RENCANA; mapping target **PERLU KONFIRMASI** |
| PRD-14 | Riwayat sesi & referensi batch sumber | P1 | RENCANA |
| PRD-15 | Fuzzy matching sebagai **saran kandidat** | P1 | RENCANA |
| PRD-16 | Dashboard ringkasan aktivitas | P1 | RENCANA |
| PRD-17 | Integrasi API langsung SITASI/Certiport | P2 | Di luar MVP |

## 6. User stories dan kriteria penerimaan
### US-01 — Impor master
*Sebagai petugas, saya ingin mengunggah Excel SITASI/Certiport agar data pemeriksaan tersedia tanpa ketik manual.*
- File `.xlsx` tidak sesuai header ditolak dengan daftar nama kolom yang kurang.
- Upload sukses memiliki ID batch, jumlah baris, waktu, nama sumber, dan status.
- Upload gagal tidak menjadi batch aktif; sumber sebelumnya tetap tersedia atau dipulihkan dengan jelas (pergantian aktif dibuat atomik saat disempurnakan).

### US-02 — Sinkronisasi wisuda
*Sebagai petugas, saya ingin menyeret Excel wisuda ke web agar proses pencocokan otomatis.*
- Kolom NIM dan Nama wajib ada; NIM dibaca sebagai string agar tidak kehilangan nol awal.
- Satu NIM di SITASI dapat memiliki beberapa baris ujian tanpa menyebabkan output wisuda berulang tak terkontrol.
- Sistem tidak menyatakan sukses bila belum ada master aktif yang dibutuhkan.

### US-03 — Peninjauan konflik
*Sebagai petugas, saya ingin mengetahui alasan perbedaan agar dapat memutuskan kasus dengan tepat.*
- Jika NIM cocok namun nama berbeda mencolok, flag review tampil.
- Dua orang dengan nama sama di Certiport tidak menghasilkan auto-VALID.
- Setiap keputusan manual menyimpan petugas, tanggal, keputusan, dan catatan.

### US-04 — Ekspor sesuai template
*Sebagai petugas, saya ingin mengunduh file dengan susunan awal agar bisa dipakai untuk proses administrasi.*
- Urutan dan kolom non-target tidak berubah.
- Kolom target diisi hanya berdasarkan aturan yang sudah disetujui.
- Baris perlu review tidak dibuat seolah sudah lulus; dapat diekspor dengan penanda/lembar review yang disepakati.

## 7. Status bisnis yang ditampilkan
`VALID`, `PERLU_VERIFIKASI`, `TIDAK_LULUS`, `PENDING`, `DATA_TIDAK_DITEMUKAN`.

Status keseluruhan tidak boleh menghapus detail MOS dan MCF. Karena satu orang bisa punya hasil berbeda untuk dua program, tampilkan juga **status per jenis sertifikasi** dan rincian ujian/attempt.

## 8. Batasan dan asumsi
- Input file Excel berasal dari sumber resmi yang diberikan petugas.
- SITASI mempunyai NIM dan riwayat ujian; Certiport tidak mempunyai NIM.
- Nama mungkin singkatan, kapitalisasi berbeda, atau memiliki tanda baca.
- Satu orang dapat mempunyai lebih dari satu jenis sertifikasi dan banyak attempt.
- Fuzzy score **bukan** bukti identitas maupun kelulusan.
- Sistem tidak mengambil keputusan administratif akhir atas nama institusi.

## 9. Target kualitas awal (belum diuji)
- Proses ratusan baris wisuda dan ribuan baris master tanpa terhenti dalam pengujian lokal.
- Hasil deterministik untuk batch sumber dan parameter yang sama (kecuali keputusan review manual).
- Error memberikan pesan yang mudah dipahami tanpa membocorkan token/file/path rahasia.
- Seluruh kasus ambiguitas tertahan untuk review; tidak ada penetapan kelulusan dari nama saja.

## 10. Ukuran keberhasilan yang dikumpulkan saat uji
- Jumlah baris wisuda masuk dan keluar (harus sama bila input baris valid).
- Total per status dan per sertifikasi.
- Jumlah kasus duplikat NIM, nama tidak cocok, kandidat Certiport ganda.
- Waktu proses aktual vs waktu pengecekan manual berdasarkan skenario sama (jika baseline tersedia).
- Persentase test case lulus dan catatan perbaikan.

## 11. Ketergantungan & keputusan yang menghambat rilis
1. Makna dan format isi `Sertifikasi MOS`, `Sertifikasi MCF`, dan `Title Microsoft` pada wisuda; data contoh memiliki isi MOS pada kolom MCF.
2. Apakah validasi Certiport dilakukan menurut nama+program saja atau juga nama sertifikasi/versi ujian wajib identik/ekuivalen.
3. Format resmi catatan pada baris `PENDING`, gagal, tidak ditemukan, atau review.
4. Petugas berwenang untuk mengesahkan review dan kebijakan penyimpanan file.

Lihat [catatan keputusan](14_DECISIONS.md). Sampai keputusan output disetujui, ekspor final dibatasi pada pratinjau/internal, bukan dokumen administrasi yang dianggap final.
