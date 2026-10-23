# Dokumentasi Proyek — Sistem Sinkronisasi Data Wisuda ITCC

**Versi dokumen:** 1.0-draft · **Tanggal:** 30 September 2026  
**Jenis proyek:** Project magang mahasiswa · **Bahasa:** Indonesia  
**Status implementasi:** backend & frontend terimplementasi dan lulus 165 test otomatis (fixture) + typecheck + build. **Belum siap production** — migrasi SQL/RLS belum dieksekusi pada Supabase dan UAT browser belum dijalankan. Ekspor final aktif dan hanya mengisi status LULUS.

## Ringkasan
Sistem web internal untuk membantu petugas ITCC memproses Excel data wisuda, mencocokkannya menggunakan **NIM** ke riwayat SITASI, memvalidasi hasil sertifikasi terhadap ekspor Certiport yang **tidak memiliki NIM**, meninjau kasus ambigu, dan mengekspor Excel dengan kolom sertifikasi. Tidak ada koneksi langsung atau scraping ke website SITASI maupun Certiport dalam MVP; kedua sumber diimpor dari file Excel resmi yang disediakan petugas.

## Urutan membaca dokumen

1. [00 Panduan Dokumentasi](00_PANDUAN_DOKUMENTASI.md)
2. [01 Project Charter](01_PROJECT_CHARTER.md)
3. [02 PRD](02_PRD.md)
4. [03 SRS](03_SRS.md)
5. [04 Arsitektur](04_ARCHITECTURE.md)
6. [05 Kamus Data & Mapping Excel](05_DATA_DICTIONARY.md)
7. [06 Aturan Pencocokan & Validasi](06_BUSINESS_RULES.md)
8. [07 Rancangan Database](07_DATABASE_DESIGN.md)
9. [08 Kontrak API](08_API_CONTRACT.md)
10. [09 Spesifikasi UI/UX](09_UI_UX_SPEC.md)
11. [10 Test Plan](10_TEST_PLAN.md)
12. [11 Keamanan & Privasi](11_SECURITY_PRIVACY.md)
13. [12 Roadmap & Task Breakdown](12_ROADMAP.md)
14. [13 Panduan Laporan Magang](13_REPORT_MAGANG.md)
15. [14 Keputusan Teknis & Isu Terbuka](14_DECISIONS.md)
16. [15 Checklist Penerimaan](15_ACCEPTANCE.md)
17. [16 Glosarium](16_GLOSSARY.md)
18. [17 Panduan Operasional](17_OPERATIONS.md)
19. [18 Catatan Perubahan](18_CHANGELOG.md)
20. [19 Progres AI](19_AI_PROGRESS.md)
21. [20 Gate Output Mapping](20_OUTPUT_MAPPING_APPROVAL.md)
22. [21 Laporan Hasil Pengujian](21_TEST_RESULTS.md)
23. [22 Formulir UAT](22_UAT_FORM.md)
24. [23 User Manual Petugas](23_USER_MANUAL.md)
25. [24 Panduan Operator](24_OPERATOR_GUIDE.md)
26. [25 Laporan Magang](25_LAPORAN_MAGANG.md)

Untuk pengembangan memakai AI coding agent, baca [`AGENTS.md`](../AGENTS.md) **sebelum meminta AI mengubah kode**.

## Sumber acuan
- Hasil Phase 1–3: analisis, aturan pencocokan, use case, ERD, wireframe, arsitektur.
- Starter Phase 4: `sitasi-wisuda-sync-phase4.zip` (kode import data master saat dokumentasi ini disusun).
- Tiga file contoh yang digunakan untuk memverifikasi header: `data_wisuda.xlsx`, `data_sitasi.xlsx`, `data_certiport.xlsx`.

> **Privasi:** File Excel asli berisi data mahasiswa. File tersebut **tidak dimasukkan** ke dalam paket dokumentasi maupun contoh kode publik. Seluruh contoh identitas pada dokumen adalah fiktif.

## Konvensi status
- **SUDAH ADA:** dapat ditelusuri dalam kode starter Phase 4, namun belum berarti telah berhasil dijalankan pada project Supabase milik pengguna.
- **RENCANA:** desain/kontrak yang perlu diimplementasikan.
- **BUTUH KONFIRMASI:** keputusan bisnis yang harus dipastikan petugas/pembimbing sebelum hasil final digunakan.

Dokumentasi ini adalah acuan implementasi dan laporan magang, bukan klaim sistem sudah beroperasi di lingkungan produksi.
