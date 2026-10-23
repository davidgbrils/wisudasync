# 05 — Kamus Data & Pemetaan Excel

**Sumber:** Header workbook contoh yang dilampirkan dalam percakapan dan diverifikasi pada 30 September 2026. Kolom di bawah adalah **header nyata**, bukan tebakan. Data asli mahasiswa tidak direproduksi.

## 1. Excel Wisuda — sumber utama output
Nama contoh: `data_wisuda.xlsx` · Sheet: `Wisuda`.

| Posisi | Header Excel | Penggunaan | Perlakuan |
|---|---|---|---|
| A | `No` | Nomor urut | Pertahankan |
| B | `Kode Prodi` | Identitas prodi | String, pertahankan |
| C | `Program Studi` | Keterangan prodi | Pertahankan |
| D | `NIM` | **Kunci matching SITASI** | String; jangan hapus nol awal |
| E | `Nama` | Pemeriksaan identitas | Simpan asli + normalisasi saat proses |
| F | `Sertifikasi MOS` | Target output terencana | **BUTUH KONFIRMASI** format & aturan isi |
| G | `Sertifikasi MCF` | Target output terencana | **BUTUH KONFIRMASI**; contoh menemukan data MOS di sini |
| H | `Title Microsoft` | Target output terencana | **BUTUH KONFIRMASI** cara pengisian |

Jangan menghitung kolom A sebagai indeks database. Satu hasil internal harus tetap memetakan ke **baris input** (row number/source_row). Pertahankan kolom tambahan jika file baru memiliki kolom lain; validasi kebutuhan minimal per versi template.

## 2. Excel SITASI (skema ringkas 2026-10-23)
Nama contoh: `data_sitasi.xlsx` · Sheet: `Master_Data`.

| Header Excel | Kolom database Phase 4 | Kegunaan |
|---|---|---|
| `NIM` | `nim` | Join utama dengan wisuda (exact string) |
| `Nama` | `nama`, `nama_normalized` | Pemeriksaan nama; **bukan** syarat pembatalan bila NIM sama |
| `Kode NIM` | `kode_nim` | Metadata program studi |
| `Program Studi` | `program_studi` | Metadata program studi |
| `Sertifikasi` | `sertifikasi` | Kategori `MOS`, `MCF`; `MTCNA` disimpan tetapi tidak mengisi kolom Wisuda |
| `Nilai` | `nilai` | Informasi pendukung, bukan dasar kelulusan |
| `Status` | `status` | `LULUS`, `TIDAK LULUS`, `PENDING`, `GAGAL`, kosong/lainnya |

Kolom `Fakultas`, `Angkatan`, dan `Sub Program` tidak lagi wajib. Bila tidak ada, nilainya `null` di database. Satu NIM dapat muncul **berulang** (banyak sertifikasi/attempt). **Tidak boleh ada unique constraint pada `nim` di `sitasi_data`**; keunikan memakai `import_id + source_row`.

## 3. Excel Certiport (skema ringkas 2026-10-23)
Nama contoh: `data_certiport.xlsx` · Sheet: `Results (264) Plus`.

| Header Excel | Kolom database Phase 4 | Kegunaan |
|---|---|---|
| `Nama` | `full_name`, `full_name_normalized` | Identitas kandidat; satu-satunya kunci pencocokan |
| `Sertifikasi` | `certification_name`, `program_name` | Kategori `MOS`/`MCF`; `program_name` diturunkan ke label lengkap |
| `Nilai` | `score` | Bukti tambahan, **bukan** putusan |
| `Status` | `result` | `LULUS`/`PASS` → `PASS`; `TIDAK LULUS`/`GAGAL`/`FAIL` → `FAIL` |

**Tidak ada NIM di file Certiport.** Identitas hanya dikonfirmasi bila **seluruh token nama sama** setelah normalisasi (urutan kata dan gelar akademik boleh berbeda). Kecocokan sebagian/fuzzy hanya menjadi kandidat saran: record-nya tidak dipakai sebagai bukti, tidak menghasilkan exam, dan tidak memberi skor kepada mahasiswa. Skema lama (`First Name`, `Last Name`, `Full Name`, `Program Name`, `Certification Name`, `Score`, `Result`) masih dapat dibaca sebagai fallback; jika record lama menyediakan NIM, NIM yang berbeda dari wisuda dianggap konflik identitas.

## 4. Pemetaan nama/status program awal
| SITASI `Sertifikasi` | Certiport `Program Name` | Status mapping |
|---|---|---|
| `MOS` | `Microsoft Office Specialist` | Kandidat mapping kategori |
| `MCF` | `Microsoft Certified Fundamentals` | Kandidat mapping kategori |
| `MTCNA` | Tidak ditentukan pada file contoh | Di luar output MVP; tetap simpan di SITASI |

**Catatan penting:** Kesamaan kategori saja tidak menjamin kesamaan ujian. Contoh `Excel` vs `Excel 2019` mungkin ekuivalen sesuai aturan petugas; `Word` tidak boleh divalidasi menggunakan kelulusan `Excel` hanya karena sama-sama MOS. Daftar alias detail harus dikonfirmasi sebelum diaktifkan.

## 5. Aturan normalisasi
### NIM
- Konversi string tanpa memotong digit; trim whitespace.
- Excel numerik yang setara bilangan bulat boleh dikonversi menjadi digit string tanpa `.0`, dengan pengecekan keutuhan nilainya.
- Jangan mengubah NIM panjang ke floating-point yang kehilangan presisi; jika ambigu/kosong beri flag.
- Jangan menyimpulkan identitas dari awalan atau tahun NIM.

### Nama
- Simpan nama asli.
- Untuk perbandingan: `strip`, `uppercase`, rapikan whitespace, normalisasi tanda baca pinggir, Unicode sewajarnya.
- Jangan menghapus seluruh bagian nama, mengembangkan singkatan (`NST` menjadi `NASUTION`), atau menghapus kata umum otomatis tanpa persetujuan.

### Sertifikasi dan status
- Simpan label sumber aslinya jika membutuhkan audit, dan buat nilai normalisasi untuk matching/status.
- `Pass` → `PASS`; `Lulus` → `LULUS`; kosong tetap kosong/unknown.
- Ambang nilai kelulusan tidak ditebak dari `Score/Nilai` jika status resmi sudah tersedia.

## 6. Kasus data yang wajib ditangani
| Kasus | Perlakuan |
|---|---|
| NIM hanya ada di wisuda | `DATA_TIDAK_DITEMUKAN` pada hasil keseluruhan; boleh munculkan saran review kandidat, tetapi tidak auto VALID |
| Satu NIM ada pada 4 baris SITASI | Simpan semua; kelompokkan per program + ujian + attempt |
| Nama wisuda berbeda dari SITASI dengan NIM sama | Catat perbedaan; tidak menolak NIM, tetapi flag review jika bermakna |
| Nama Certiport sama pada lebih dari satu record | Bedakan record ujian vs orang berbeda; cek kombinasi program dan hasil; jika ambigu review |
| Sertifikasi SITASI `MOS Word`, Certiport `MOS Excel` | **Bukan** validasi ujian yang sama |
| `Result=INCO` | Status tidak cukup untuk `VALID` |
| Sel hasil wisuda sebelumnya terisi | Pilihan overwrite/pertahankan harus disetujui staf, dan perubahan tampil dalam pratinjau |
| Formula pada template asli | Pertahankan formula non-target; jangan memindahkan data teks sebagai formula aktif |

## 7. Aturan output `.xlsx`
1. Buka salinan workbook asli menggunakan OpenPyXL.
2. Kenali sheet/kolom target berdasarkan **header**, tidak cuma koordinat hard-coded.
3. Pastikan tiap baris yang diproses memiliki referensi `source_row`.
4. Isi hanya kolom target berdasarkan mapping yang telah disetujui.
5. Kolom non-target, urutan row, styling penting, dan sheet lain harus tetap ada.
6. Jika review belum selesai, jangan membuat keluaran menyesatkan. Opsi disetujui: sel kosong/label review, atau lembar terpisah, sesuai keputusan institusi.
7. Sediakan perbandingan output vs input pada test otomatis.

## 8. Contoh fiktif
Wisuda: `NIM=209900001`, `Nama=MAHASISWA CONTOH`.  
SITASI: `209900001 | MAHASISWA CONTOH | MOS | Word | LULUS`.  
Certiport: `MAHASISWA CONTOH | Microsoft Office Specialist | Word 2019 | Pass`.  
**Keputusan:** Kandidat cocok; `VALID` hanya bila alias jenis ujian Word↔Word 2019 disahkan dan kandidat Certiport tidak ambigu. Contoh bukan data riil.

## 9. Aturan yang belum dipastikan
Khusus `Sertifikasi MOS`, `Sertifikasi MCF`, dan `Title Microsoft`, **JANGAN** mengklaim mapping final. Lihat ADR-003 di `14_DECISIONS.md`.
