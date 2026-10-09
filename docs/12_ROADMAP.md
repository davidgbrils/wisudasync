# 12 — Roadmap Pengembangan, Urutan Implementasi dan Task Breakdown

**Prinsip:** lanjutkan Phase 4 starter, selesaikan satu fitur kemudian uji; jangan menambah fitur di luar lingkup ketika fitur inti belum stabil.

## Rekap fase
| Fase | Fokus | Status dokumentasi/kode |
|---|---|---|
| 1 | Analisis data 3 Excel, kebutuhan dan risiko | Analisis awal dilakukan pada percakapan |
| 2 | Use case, flowchart, activity, ERD, wireframe | Desain awal disusun pada percakapan |
| 3 | Arsitektur, folder, kontrak API | Disepakati pada percakapan |
| 4 | Starter import master SITASI & Certiport | **Kode starter tersedia**, belum diverifikasi pada Supabase milik pengguna |
| 4.1 | **Pengamanan endpoint sebelum data nyata** | WAJIB berikutnya |
| 5 | Upload Wisuda & matching deterministik | BELUM DIBANGUN |
| 6 | Validasi Certiport, review dan bukti | BELUM DIBANGUN |
| 7 | Export Excel dengan mapping disahkan | BELUM DIBANGUN |
| 8 | UAT, perbaikan, demo, laporan | BELUM SELESAI |

## Fase 4.1 — Hardening starter
**Tugas:** Bootstrap frontend Next.js lengkap (starter saat ini hanya potongan halaman), isi `.env` aman, verifikasi migration SQL di dev, autentikasi Supabase, pengecekan role/allowlist FastAPI, pembatasan file, tes akses 401/403, pastikan aktivasi batch atomik.

**Selesai jika:** tes import dummy berfungsi; unauthorized ditolak; impor gagal tidak merusak batch aktif; daftar master hanya dapat diakses petugas yang berhak.

## Fase 5 — Upload dan matching Wisuda
- Tambah model `sync_sessions`, `sync_results` dan referensi snapshot batch.
- Parser header `Wisuda`, validasi dan penanganan row kosong.
- Simpan baris asli/NIM sebagai string dan `source_row`.
- Lookup `NIM` ke seluruh SITASI dalam batch aktif.
- Kelompokkan attempt menurut jenis dan ujian; simpan bukti.
- Tambah unit test exact NIM, NIM kosong, duplicate NIM/attempt, jenis ujian berbeda.

**Selesai jika:** setiap baris Wisuda mendapat hasil internal yang dapat dijelaskan dan jumlah row tidak berubah.

## Fase 6 — Certiport + review
- Normalisasi nama, pencarian exact, saran fuzzy (tidak otomatis valid).
- Review keunikan kandidat, mapping program/ujian dan konflik status.
- Penetapan status per ujian; simpan `sync_evidence`/reason.
- Dialog verifikasi serta `review_audit` (petugas/waktu/catatan).
- Tes semua cabang konflik.

**Selesai jika:** bukti lengkap menghasilkan hasil deterministik dan seluruh kasus ambigu masuk antrean review.

## Fase 7 — Excel export
- Minta persetujuan pemetaan kolom `Sertifikasi MOS`, `Sertifikasi MCF`, `Title Microsoft` sebelum mengaktifkan eksport final.
- Pertahankan workbook template asli dan isi hanya kolom target.
- Tambahkan indikator review yang disepakati, simpan/unduh file.
- Bandingkan workbook input/output otomatis dan secara visual.

**Selesai jika:** petugas setuju output, file terbuka di Excel, baris/kolom tidak rusak dan nilai non-target terjaga.

## Fase 8 — Pengujian dan pelaporan
- Unit/integrasi/black-box sesuai `10_TEST_PLAN.md`.
- UAT bersama petugas untuk baris konflik.
- Dokumentasikan perbaikan, screenshot dan hasil sebenarnya.
- Susun BAB I–V mengikuti `13_REPORT_MAGANG.md`.
- Deployment hanya jika ada izin lingkungan dan data.

## Urutan task minimal yang disarankan
1. Siapkan repositori dan environment dummy.
2. Jalankan starter Phase 4 di dev dan konfirmasi tabel Supabase.
3. Implementasikan auth guard (P0).
4. Bereskan transaksi batch aktif.
5. Buat parser wisuda + test.
6. Buat matching NIM + agregasi attempt.
7. Buat matching Certiport per ujian.
8. Buat review UI, keputusan dan audit.
9. Putuskan mapping output bersama pembimbing.
10. Implementasikan export, UAT dan laporan.

## Pelacakan tugas
Gunakan format tabel berikut pada README atau issue tracker:
| Task ID | Deskripsi | Dokumen acuan | Status | Bukti |
|---|---|---|---|---|
| T-401 | Auth guard API | SRS FR-001/002 | TODO | — |
| T-501 | Parser Wisuda | Data Dictionary | TODO | — |
| T-502 | Matching NIM | Business Rules | TODO | — |
| T-601 | Review + audit | PRD-11 | TODO | — |
| T-701 | Excel output | PRD-13 | BLOCKED: mapping | — |

> Jangan menetapkan tanggal selesai atau status DONE tanpa bukti pengerjaan.
