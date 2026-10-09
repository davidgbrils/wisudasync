# 14 — Architecture Decision Records (ADR) dan Keputusan Terbuka

Dokumen ini menghindari keputusan penting diambil diam-diam oleh kode/AI. `DIPUTUSKAN` berarti keputusan desain internal dari Phase 1–4, bukan otomatis persetujuan administratif ITCC. `TERBUKA` memerlukan penetapan penanggung jawab.

## Ringkasan
| ADR | Topik | Status | Dampak |
|---|---|---|---|
| ADR-001 | Frontend Next.js, backend FastAPI | DIPUTUSKAN | Pemisahan UI dan proses Excel |
| ADR-002 | Wisuda→SITASI menggunakan exact NIM | DIPUTUSKAN | Hindari join nama utama |
| ADR-003 | Isi dan kolom target ekspor Wisuda | **TERBUKA — PRIORITAS TERTINGGI** | Export final tidak boleh ditentukan sembarang |
| ADR-004 | Certiport tanpa NIM; fuzzy hanya kandidat | DIPUTUSKAN | Kasus ambigu wajib review |
| ADR-005 | Aturan ekuivalensi jenis ujian/versi | TERBUKA | Berpengaruh pada `VALID` |
| ADR-006 | Definisi output `Title Microsoft` | TERBUKA | Risiko salah isi kolom |
| ADR-007 | Penyimpanan dan retensi data | TERBUKA | Keamanan/privasi |
| ADR-008 | Satu batch aktif per jenis data master | DIPUTUSKAN | Konsistensi import |
| ADR-009 | Siapa dapat melakukan review | TERBUKA | Otorisasi dan akuntabilitas |
| ADR-010 | Perlakuan sel sertifikasi yang sudah terisi | TERBUKA | Menghindari overwrite data sah |
| ADR-011 | Kriteria wajib MOS/MCF per program/prodi | TERBUKA | Tidak boleh menyimpulkan syarat wisuda |

## ADR-001 — Arsitektur client–backend–database
**Keputusan:** Next.js UI, FastAPI mengelola API/pemrosesan, Supabase PostgreSQL penyimpanan/Auth.  
**Alasan:** Cukup sederhana untuk project mahasiswa dan sesuai penggunaan Python dalam pengolahan Excel.  
**Konsekuensi:** Perlu menjaga kesesuaian kontrak API dan token autentikasi.

## ADR-002 — Primary matching NIM
**Keputusan:** Normalized exact NIM untuk Wisuda↔SITASI; nama menjadi pemeriksaan sekunder.  
**Alasan:** NIM tersedia pada keduanya sementara nama bisa berbeda.

## ADR-003 — Mapping output Wisuda [TERBUKA]
**Bukti input:** Kolom `Sertifikasi MOS`, `Sertifikasi MCF`, `Title Microsoft` ada di sheet `Wisuda`; sebagian sel pada kolom MCF berisi teks yang mengacu pada MOS.  
**Pertanyaan ke petugas:** (1) Apakah salah tempat pada contoh atau praktik yang disengaja? (2) Format pasti per kolom, mis. `MOS (Word 2019 - Lulus)`? (3) Boleh lebih dari satu sertifikasi per sel? (4) Jika belum lulus/perlu review, sel kosong atau ada keterangan? (5) Apakah `Title Microsoft` hanya label MOS/MCF atau nama gelar lengkap?  
**Keputusan sementara:** Hanya buat pratinjau internal dan catat rincian; jangan aktifkan isi otomatis final.

## ADR-004 — Matching Certiport
**Keputusan:** Normalisasi nama + pencarian kandidat + kategori & ujian; nama ambigu/fuzzy perlu tinjauan manusia.  
**Alternatif ditolak:** `full_name` saja langsung menjadi VALID; risiko salah orang.

## ADR-005 — Mapping ekuivalensi ujian [TERBUKA]
**Pertanyaan:** Apakah `Word` SITASI boleh setara `Word 2019` Certiport? Apakah `Azure AI-900` setara `Microsoft Azure AI Fundamentals`? Bagaimana perbedaan versi tahun produk?  
**Keputusan sementara:** mapping kandidat saja; harus ada daftar alias disetujui dan pengujian.

## ADR-006 — Title Microsoft [TERBUKA]
`Title Microsoft` tidak didefinisikan hanya dari nama kolom. Petugas harus memberikan contoh output benar untuk MOS saja, MCF saja, keduanya, dan tidak lulus.

## ADR-007 — Retensi [TERBUKA]
Tentukan lokasi file asli, lama retensi per jenis, backup, dan aturan penghapusan berdasarkan kebijakan ITCC. Sampai jelas, hindari upload asli ke repo/hosting publik; gunakan file dummy lokal.

## ADR-008 — Aktif per tipe master
Satu batch SITASI aktif dan satu Certiport aktif. ID batch disimpan per sesi. **Perbaikan Phase 4:** operasi pergantian aktif perlu atomik (saat ini kode starter menggunakan dua update terpisah).

## ADR-009 — Reviewer [TERBUKA]
Tentukan apakah semua petugas ITCC boleh konfirmasi atau memerlukan satu penanggung jawab yang ditunjuk. Gunakan role/allowlist yang disetujui dan audit keputusan.

## ADR-010 — Overwrite sel lama [TERBUKA]
Tentukan ketika sel target wisuda telah terisi: pertahankan, isi hanya yang kosong, atau tampilkan pilihan perbedaan sebelum overwrite. Default paling aman: **jangan overwrite tanpa persetujuan dan jejak perubahan**.

## ADR-011 — Kewajiban sertifikasi [TERBUKA]
Jangan menilai kelayakan wisuda dari `MOS/MCF` sebelum institusi menentukan apakah masing-masing sertifikasi wajib/opsional menurut prodi atau angkatan.

## Proses pengesahan
Setelah diskusi dengan pembimbing, catat: `Tanggal | ADR | Pilihan disetujui | Pihak pemberi persetujuan | Bukti | Dampak ke kode/test`. Perbarui Business Rules, Data Dictionary, API, lalu implementasi.
