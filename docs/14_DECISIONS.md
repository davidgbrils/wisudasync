# 14 — Architecture Decision Records (ADR) dan Keputusan Terbuka

Dokumen ini menghindari keputusan penting diambil diam-diam oleh kode/AI. `DIPUTUSKAN` berarti keputusan desain internal dari Phase 1–4, bukan otomatis persetujuan administratif ITCC. `TERBUKA` memerlukan penetapan penanggung jawab.

## Ringkasan
| ADR | Topik | Status | Dampak |
|---|---|---|---|
| ADR-001 | Frontend Next.js, backend FastAPI | DIPUTUSKAN | Pemisahan UI dan proses Excel |
| ADR-002 | Wisuda→SITASI menggunakan exact NIM | DIPUTUSKAN | NIM adalah identitas; nama hanya peringatan |
| ADR-003 | Isi dan kolom target ekspor Wisuda | **DISETUJUI (2026-10-23)** | Isi hanya LULUS, format `MOS (Lulus)` |
| ADR-004 | Certiport tanpa NIM; fuzzy hanya kandidat | DIPUTUSKAN | Exact name mengisi; fuzzy tidak |
| ADR-005 | Aturan ekuivalensi jenis ujian/versi | **DIPUTUSKAN (DISETUJUI)** | Relevan untuk berkas legacy bersub-program |
| ADR-006 | Definisi output `Title Microsoft` | **DISETUJUI (2026-10-23)** | `MOS`, `MCF`, atau `MOS, MCF` |
| ADR-007 | Penyimpanan dan retensi data | TERBUKA | Keamanan/privasi |
| ADR-008 | Satu batch aktif per jenis data master | DIPUTUSKAN | Konsistensi import |
| ADR-009 | Siapa dapat melakukan review | TERBUKA | Otorisasi dan akuntabilitas |
| ADR-010 | Perlakuan sel sertifikasi yang sudah terisi | **DISETUJUI (2026-10-23)** | Berkas baru; sel non-LULUS dikosongkan |
| ADR-011 | Kriteria wajib MOS/MCF per program/prodi | **DISETUJUI (2026-10-23)** | Sistem hanya mengisi bukti LULUS, bukan syarat wisuda |

## ADR-001 — Arsitektur client–backend–database
**Keputusan:** Next.js UI, FastAPI mengelola API/pemrosesan, Supabase PostgreSQL penyimpanan/Auth.  
**Alasan:** Cukup sederhana untuk project mahasiswa dan sesuai penggunaan Python dalam pengolahan Excel.  
**Konsekuensi:** Perlu menjaga kesesuaian kontrak API dan token autentikasi.

## ADR-002 — Primary matching NIM
**Keputusan:** Normalized exact NIM untuk Wisuda↔SITASI; nama menjadi pemeriksaan sekunder.  
**Alasan:** NIM tersedia pada keduanya sementara nama bisa berbeda.

## ADR-003 — Mapping output Wisuda [DISETUJUI 2026-10-23]
**Keputusan pemilik project:** Isi hanya sertifikasi berstatus LULUS. Format sel: `MOS (Lulus)` dan `MCF (Lulus)`. Sel yang tidak lulus/tidak ditemukan/perlu verifikasi dibiarkan kosong. Karena sumber ringkas tidak lagi memuat sub-program, nama produk (Word/Excel) tidak dicantumkan. Ekspor final diaktifkan kembali.

## ADR-004 — Matching Certiport
**Keputusan:** Identitas hanya dikonfirmasi bila seluruh token nama sama (urutan/gelar boleh berbeda). Kandidat parsial/fuzzy hanya saran review; record-nya tidak dipakai sebagai bukti atau skor. Jika NIM tersedia di kedua sumber dan berbeda, identitas dianggap konflik.

**Alternatif ditolak:** `full_name` parsial atau fuzzy langsung menjadi VALID; risiko salah orang. **Regresi 2026-10-23:** kandidat fuzzy sempat dipakai sebagai evidence dan exam; sudah diperbaiki.

## ADR-005 — Mapping ekuivalensi ujian [DISETUJUI]
**Pertanyaan:** Apakah `Word` SITASI boleh setara `Word 2019` Certiport? Apakah `Azure AI-900` setara `Microsoft Azure AI Fundamentals`? Bagaimana perbedaan versi tahun produk?  
**Keputusan (2026-10-19):** Ekuivalensi alias disetujui resmi bersama pihak ITCC. Ujian `Word` SITASI setara `Word 2019` / `Microsoft Word 2019`; `Excel` setara `Excel 2019` / `Microsoft Excel 2019`; `PowerPoint` setara `PowerPoint 2019`; serta `Azure AI-900` setara `Microsoft Azure AI Fundamentals`. Bila kedua sumber konsisten LULUS/PASS, mahasiswa otomatis berstatus `VALID`.

## ADR-006 — Title Microsoft [DISETUJUI 2026-10-23]
`Title Microsoft` berisi label kategori: `MOS` bila hanya MOS lulus, `MCF` bila hanya MCF lulus (prodi 31/32), `MOS, MCF` bila keduanya, dan kosong bila tidak ada yang lulus.

## ADR-007 — Retensi [TERBUKA]
Tentukan lokasi file asli, lama retensi per jenis, backup, dan aturan penghapusan berdasarkan kebijakan ITCC. Sampai jelas, hindari upload asli ke repo/hosting publik; gunakan file dummy lokal.

## ADR-008 — Aktif per tipe master
Satu batch SITASI aktif dan satu Certiport aktif. ID batch disimpan per sesi. **Perbaikan Phase 4:** operasi pergantian aktif perlu atomik (saat ini kode starter menggunakan dua update terpisah).

## ADR-009 — Reviewer [TERBUKA]
Tentukan apakah semua petugas ITCC boleh konfirmasi atau memerlukan satu penanggung jawab yang ditunjuk. Gunakan role/allowlist yang disetujui dan audit keputusan.

## ADR-010 — Overwrite sel lama [DISETUJUI 2026-10-23]
Berkas hasil dibuat sebagai **berkas baru** (mis. `hasil_wisuda_terisi.xlsx`); `data_wisuda.xlsx` asli tidak ditimpa. Pada berkas baru, sel target diisi hanya untuk LULUS dan dikosongkan untuk status lain sesuai permintaan pemilik project.

## ADR-011 — Kewajiban sertifikasi [DISETUJUI 2026-10-23]
Sistem hanya mengisi bukti sertifikasi yang LULUS. Sistem **tidak** menyimpulkan bahwa mahasiswa memenuhi syarat wisuda, dan tidak menandai tidak memenuhi syarat karena MOS/MCF kosong.

## Proses pengesahan
Setelah diskusi dengan pembimbing, catat: `Tanggal | ADR | Pilihan disetujui | Pihak pemberi persetujuan | Bukti | Dampak ke kode/test`. Perbarui Business Rules, Data Dictionary, API, lalu implementasi.
