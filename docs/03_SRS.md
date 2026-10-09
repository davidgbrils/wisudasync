# 03 — Software Requirements Specification (SRS)

**Acuan:** `02_PRD.md`; semua persyaratan memiliki ID untuk referensi test.

## 1. Lingkungan operasi
- Browser desktop modern untuk staf; UI responsif minimal agar dapat dilihat laptop.
- Frontend: Next.js, TypeScript, Tailwind CSS.
- Backend: Python/FastAPI; Excel: Pandas dan OpenPyXL; kandidat nama: RapidFuzz.
- Database: PostgreSQL/Supabase; Auth: Supabase Auth.
- Ekspor utama: `.xlsx` menggunakan template input wisuda.

## 2. Kebutuhan fungsional
| ID | Persyaratan "sistem harus" | Prioritas | Verifikasi |
|---|---|---|---|
| FR-001 | Mengautentikasi akun staf dan menolak API tanpa token yang valid | P0 | TC-AUTH-01 |
| FR-002 | Memeriksa otorisasi per endpoint import, lihat data, review, ekspor | P0 | TC-AUTH-02 |
| FR-003 | Mengunggah SITASI `.xlsx` dengan header lengkap | P0 | TC-IMP-01 |
| FR-004 | Mengunggah Certiport `.xlsx` dengan header lengkap | P0 | TC-IMP-02 |
| FR-005 | Menolak file salah format, terlalu besar, header hilang, sheet tidak tepat | P0 | TC-IMP-03 |
| FR-006 | Mempertahankan isi sumber asli dan menyimpan hasil normalisasi terpisah | P0 | TC-NORM-01 |
| FR-007 | Mencatat nomor baris Excel dan ID batch import | P0 | TC-TRACE-01 |
| FR-008 | Mengaktifkan tepat satu batch SITASI dan Certiport untuk pemrosesan baru | P0 | TC-BATCH-01 |
| FR-009 | Menampilkan daftar data master dengan paginasi/search/filter | P1 | TC-MASTER-01 |
| FR-010 | Mengunggah Excel wisuda dengan NIM, Nama dan kolom output relevan | P0 | TC-WIS-01 |
| FR-011 | Menentukan kandidat SITASI dengan exact NIM terlebih dahulu | P0 | TC-MAT-01 |
| FR-012 | Mengagregasi multiple attempt tanpa kehilangan riwayat tiap program/ujian | P0 | TC-MAT-02 |
| FR-013 | Menormalkan dan menilai nama tanpa menganggap fuzzy match final | P0 | TC-MAT-03 |
| FR-014 | Memverifikasi kandidat Certiport dengan identitas, jenis dan nama ujian | P0 | TC-MAT-04 |
| FR-015 | Menandai konflik/ambigu dan memberikan alasan review | P0 | TC-VAL-01 |
| FR-016 | Menyimpan review manual beserta waktu, petugas, alasan | P0 | TC-REVIEW-01 |
| FR-017 | Menampilkan hasil berdasarkan status dan pencarian | P0 | TC-RES-01 |
| FR-018 | Mengekspor Excel dengan baris, urutan, kolom non-target dan format penting terjaga | P0 | TC-EXP-01 |
| FR-019 | Menyimpan hasil per sesi dan ID batch master sumber | P0 | TC-TRACE-02 |
| FR-020 | Menampilkan riwayat proses dan ringkasan data | P1 | TC-HIST-01 |

## 3. Kebutuhan nonfungsional
| ID | Aspek | Kriteria yang dapat diuji |
|---|---|---|
| NFR-001 | Keamanan | Endpoint berisi data mahasiswa menolak request tanpa hak akses; key server tidak muncul pada bundle client/repository |
| NFR-002 | Integritas | Jumlah row input valid vs output sama; nilai non-target identik |
| NFR-003 | Akurasi | Kasus ambigu tidak otomatis `VALID`; setiap `VALID` menyimpan bukti sumber terkait |
| NFR-004 | Keandalan | Import gagal tidak menonaktifkan master yang sebelumnya valid |
| NFR-005 | Kemudahan | Pesan error menjelaskan kesalahan file/kolom dan langkah perbaikan |
| NFR-006 | Auditabilitas | Review mencatat `reviewed_by`, `reviewed_at`, alasan, nilai lama/baru |
| NFR-007 | Kinerja | Uji dengan skala data contoh: ratusan wisuda, ribuan baris master; rekam waktu dan RAM, bukan mengklaim ambang tanpa benchmark |
| NFR-008 | Pemeliharaan | Parser, normalisasi, matching, validasi dan ekspor terpisah, dengan unit test |
| NFR-009 | Privasi | File asli dan hasil berada pada penyimpanan privat/akses terbatas; log tidak memuat semua data mahasiswa |

## 4. Batas input/output
**Input valid:** Excel `.xlsx`; sheet/header dikenali; NIM dapat diubah menjadi string tanpa kehilangan digit; batas ukuran file dikonfigurasi dan diuji.  
**Output utama:** Excel daftar wisuda mengikuti format sumber; lampiran lembar `Review` opsional setelah disetujui staf.  
**Error:** HTTP 400/422 untuk input salah; 401/403 autentikasi/otorisasi; 409 untuk konflik batch/keputusan; 500 untuk kesalahan internal tak terduga.

## 5. Aturan akuntansi data
- Satu baris input wisuda memunculkan satu hasil utama, disertai banyak rincian attempt apabila ada.
- Multiple attempt dihitung **per kategori dan subprogram/ujian**, bukan merata semua ujian MOS/MCF.
- `LULUS` di SITASI sendiri belum cukup untuk klaim `VALID` lintas sumber.
- Hasil dari Certiport tanpa keunikan identitas yang meyakinkan tidak bisa otomatis menetapkan lulus.
- Master versi lama tetap terarsip sesuai kebijakan; setiap sesi mereferensikan batch sumber tertentu.

## 6. Asumsi, risiko dan pengecualian
Tabel data master dari Phase 4 merupakan implementasi awal; belum ada login dan sinkronisasi wisuda dalam source starter. Kriteria di dokumen ini adalah **target implementasi**, bukan pernyataan semuanya selesai.

## 7. Traceability
`PRD-02 → FR-003 → Import SITASI → TC-IMP-01`.  
`PRD-07 → FR-011 → Matching Service → TC-MAT-01`.  
`PRD-11 → FR-016 → Review Endpoint + Audit → TC-REVIEW-01`.  
`PRD-13 → FR-018 → Export Service → TC-EXP-01`.
