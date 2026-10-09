# 15 — Checklist Penerimaan MVP (Definition of Done)

Centang hanya setelah benar-benar dibuktikan. Belum ada klaim bahwa semua pekerjaan di bawah selesai.

## A. Data master
- [ ] Import SITASI valid dari Excel `.xlsx` contoh (di lingkungan berizin) atau dummy.
- [ ] Import Certiport valid dari Excel `.xlsx` contoh/dummy.
- [ ] Header salah ditolak dengan pesan jelas.
- [ ] Semua baris dan `source_row` sesuai.
- [ ] Normalisasi NIM tidak menghilangkan digit/nol awal.
- [ ] Banyak attempt SITASI tidak dihapus.
- [ ] Batch gagal tidak mengganti master aktif.
- [ ] Pergantian batch aktif aman ketika upload gagal/paralel.

## B. Keamanan dan identitas
- [ ] Login Supabase Auth bekerja.
- [ ] Endpoint data/informasi mahasiswa menolak tanpa token.
- [ ] Akun non-petugas tidak dapat membaca atau mengubah data.
- [ ] Secret/service key hanya di backend.
- [ ] File sebenarnya tidak tersedia publik dan tidak ikut Git.

## C. Matching dan validasi
- [ ] Exact NIM memproses seluruh attempt mahasiswa.
- [ ] Pencocokan dijalankan per jenis dan ujian, bukan kategori besar saja.
- [ ] Kasus nama berbeda tercatat.
- [ ] Nama yang sama untuk kandidat berbeda tidak menghasilkan auto VALID.
- [ ] Fuzzy hanya membuat kandidat untuk review.
- [ ] SITASI LULUS + Certiport PASS yang sesuai dan unik memberi bukti VALID pada ujian tersebut.
- [ ] SITASI gagal + Certiport PASS yang cocok menghasilkan konflik/review.
- [ ] NIM yang tak ditemukan mengembalikan `DATA_TIDAK_DITEMUKAN`.
- [ ] Setiap status memiliki alasan/bukti terperiksa.

## D. Review dan ekspor
- [ ] Petugas dapat mengonfirmasi/menolak/menunda dengan catatan.
- [ ] Keputusan tersimpan dengan reviewer dan waktu.
- [ ] Format tiga kolom keluaran wisuda sudah disetujui.
- [ ] Workbook hasil mempertahankan jumlah, urutan, kolom dan nilai non-target.
- [ ] Sel yang sudah berisi data ditangani sesuai kebijakan overwrite.
- [ ] Hasil review belum selesai tidak diekspor sebagai klaim lulus final.
- [ ] Berkas hasil dapat dibuka di Microsoft Excel.

## E. Kesiapan laporan magang
- [ ] Flowchart sesuai implementasi terakhir.
- [ ] ERD sesuai tabel yang benar-benar dibuat.
- [ ] Daftar library/versi aktual tercatat.
- [ ] Screenshot nyata tersimpan dan data pribadi disensor.
- [ ] Tabel uji berisi hasil aktual, bukan hasil contoh.
- [ ] Kesimpulan hanya berdasarkan fungsi yang benar-benar telah diuji.

## Ringkasan penerimaan
| Kategori | Status | Bukti/tautan |
|---|---|---|
| A. Master data | BELUM DIVERIFIKASI END-TO-END | — |
| B. Keamanan | BELUM SELESAI DI STARTER | — |
| C. Matching | BELUM DIBANGUN | — |
| D. Review & Export | BELUM DIBANGUN | — |
| E. Laporan | DALAM PERSIAPAN | — |

Tanggal pengesahan dan pihak pemeriksa diisi setelah UAT.
