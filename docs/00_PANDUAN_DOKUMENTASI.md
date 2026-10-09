# 00 — Panduan Menggunakan Dokumen

**Pemilik dokumen:** Mahasiswa pengembang; ditinjau pembimbing magang/petugas ITCC.  
**Versi:** 1.0-draft · **Pembaruan:** 30 September 2026.

## Tujuan
Paket dokumen ini mengubah pembahasan Phase 1–4 menjadi persyaratan yang dapat ditelusuri ke desain, kode, pengujian, serta laporan magang. Format Markdown (`.md`) dipilih karena mudah dipakai di VS Code, GitHub, dan AI coding tools.

## Hubungan dokumen

| Dokumen | Menjawab pertanyaan | Dipakai pada |
|---|---|---|
| Project Charter | Masalah apa dan mengapa dibuat? | Proposal, BAB I |
| PRD | Fitur apa yang dibutuhkan pengguna? | Persetujuan scope |
| SRS | Kondisi teknis apa yang harus dipenuhi? | Koding, pengujian |
| Architecture | Komponen apa berkomunikasi bagaimana? | BAB III |
| Data Dictionary | Kolom input/output bagaimana dipetakan? | Importer, export |
| Business Rules | Apa keputusan matching yang sah? | Matching engine |
| Database Design | Di mana data/riwayat disimpan? | Supabase, ERD |
| API Contract | Endpoint dan bentuk pesan apa? | Integrasi Next.js–FastAPI |
| UI/UX Spec | Alur dan layar pengguna? | Frontend, BAB III |
| Test Plan | Bagaimana membuktikan fitur benar? | BAB IV |
| Security | Bagaimana data mahasiswa dilindungi? | Pengembangan/penerapan |
| Roadmap | Urutan eksekusi dan milestone? | Monitoring pengerjaan |
| Laporan Magang | Apa yang perlu dicatat untuk BAB I–V? | Penulisan laporan |

## Alur perubahan kebutuhan
1. Usulan perubahan → cek kesesuaian PRD dan status keputusan `docs/14_DECISIONS.md`.
2. Jika diterima → ubah SRS, aturan bisnis dan model data/API terkait.
3. Baru modifikasi kode dan test.
4. Simpan alasan, tanggal, dan dampaknya di changelog.

## Cara memakai untuk presentasi
Gunakan Project Charter untuk latar belakang; flowchart & arsitektur untuk desain; API/database untuk penjelasan teknis; hasil pengujian riil untuk evaluasi. Jangan mencantumkan ilustrasi dummy sebagai hasil pengujian sebenarnya.

## Klasifikasi persetujuan
`DISAHKAN`: telah disetujui pembimbing/petugas. `USULAN`: rancangan pengembang. `PERLU KONFIRMASI`: berdampak langsung ke output dan tidak boleh diam-diam diputuskan oleh sistem.

> Saat paket ini dibuat, aturan pemetaan beberapa kolom output, standar kelulusan per program, dan mekanisme verifikasi kasus ambigu masih `PERLU KONFIRMASI`.
