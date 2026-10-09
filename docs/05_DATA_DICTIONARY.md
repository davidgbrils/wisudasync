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

## 2. Excel SITASI
Nama contoh: `data_sitasi.xlsx` · Sheet: `Master_Data`.

| Header Excel | Kolom database Phase 4 | Kegunaan |
|---|---|---|
| `NIM` | `nim` | Join utama dengan wisuda |
| `Nama` | `nama`, `nama_normalized` | Pemeriksaan nama dan jembatan ke Certiport |
| `Fakultas` | `fakultas` | Metadata sumber |
| `Kode NIM` | `kode_nim` | Metadata, tidak menggantikan NIM |
| `Program Studi` | `program_studi` | Metadata |
| `Angkatan` | `angkatan` | Informasi akademik tambahan |
| `Sertifikasi` | `sertifikasi` | Kategori `MOS`, `MCF`, termasuk `MTCNA` di data master |
| `Sub Program` | `sub_program` | Jenis ujian; gunakan mapping ke Certiport |
| `Nilai` | `nilai` | Informasi pendukung; bukan satu-satunya dasar kelulusan |
| `Status` | `status` | `LULUS`, `TIDAK LULUS`, `PENDING`, `GAGAL`, kosong/lainnya |

Satu NIM dapat muncul **berulang**, karena banyak attempt/jenis ujian. **Tidak boleh ada unique constraint pada `nim` di `sitasi_data`**. Keunikan rekaman sumber lebih tepat menggunakan `import_id + source_row`.

## 3. Excel Certiport
Nama contoh: `data_certiport.xlsx` · Sheet: `Results (264) Plus`.

| Header Excel | Kolom database Phase 4 | Kegunaan |
|---|---|---|
| `First Name` | `first_name` | Nama depan |
| `Last Name` | `last_name` | Nama belakang |
| `Full Name` | `full_name`, `full_name_normalized` | Pencocokan identitas kandidat |
| `Program Name` | `program_name` | Kategori MOS/MCF dengan label berbeda |
| `Certification Name` | `certification_name` | Produk/ujian aktual |
| `Score` | `score` | Bukti tambahan, **bukan** putusan menggantikan `Result` |
| `Result` | `result` | `PASS`, `FAIL`, `INCO` atau nilai lain yang harus ditangani |

**Tidak ada NIM di file Certiport contoh.** Exact match nama belum tentu mengidentifikasi orang secara unik; gunakan pengecekan duplikat kandidat dan program ujian.

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
