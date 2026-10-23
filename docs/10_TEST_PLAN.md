# 10 — Rencana Pengujian (Test Plan)

**Tujuan:** Membuktikan bahwa aplikasi memenuhi kebutuhan tanpa menebak kelulusan mahasiswa. Ini **rencana tes**, bukan laporan semua tes lulus.

## 1. Metode
- **Unit test:** normalisasi NIM/nama, agregasi riwayat, mapping kategori/ujian, status.
- **Integration test:** importer→database→matching→review→export.
- **Black-box/UAT:** petugas menjalankan skenario di browser dengan Excel uji.
- **Regresi:** sesudah aturan alias atau exporter diubah.
- **Pengukuran:** catat jumlah baris, waktu proses, jumlah konflik dan pesan error.

## 2. Dataset pengujian
Gunakan **data sintetis tanpa NIM/nama mahasiswa nyata** untuk unit dan CI. File asli dari petugas hanya diproses pada lingkungan internal berizin dan tidak dipublikasikan. Sertakan contoh: NIM numerik, nol awal, nama dengan titik awal, beda kapitalisasi, nama disingkat, attempt ganda, hasil tidak konsisten, program berbeda, dua Certiport bernama sama, baris kosong, file rusak.

## 3. Matriks test case
| Test ID | Kebutuhan | Input/situasi | Ekspektasi |
|---|---|---|---|
| TC-AUTH-01 | FR-001 | Tidak ada Bearer token | 401; tidak memaparkan data |
| TC-AUTH-02 | FR-002 | User login tetapi tidak terdaftar sebagai petugas | 403 |
| TC-IMP-01 | FR-003 | XLSX SITASI semua header | Batch selesai, jumlah sesuai, source_row benar |
| TC-IMP-02 | FR-004 | XLSX Certiport semua header | Batch selesai, nama/result dinormalisasi |
| TC-IMP-03 | FR-005 | Header wajib `Nilai` hilang | Ditolak sebelum menjadi aktif |
| TC-IMP-04 | FR-005 | Nama/Sertifikasi kosong pada baris data | Ditolak dengan nomor baris yang jelas |
| TC-NORM-01 | FR-006 | `". NAMA CONTOH "` | Nama asli tetap; normalized `NAMA CONTOH` |
| TC-NORM-02 | FR-006 | NIM string `001234` | Nol awal tetap |
| TC-TRACE-01 | FR-007 | Source row ke-2 | `source_row=2` dalam import |
| TC-BATCH-01 | FR-008 | Import baru gagal | Batch sebelumnya tetap aktif |
| TC-BATCH-02 | FR-008 | Dua import sukses hampir bersamaan | Maksimal satu batch aktif, tidak ada keadaan tak konsisten |
| TC-MASTER-01 | FR-009 | Filter `MOS`, page 2 | Hanya hasil batch aktif; pagination benar |
| TC-WIS-01 | FR-010 | Upload wisuda dengan NIM/Nama | Jumlah baris sesuai tanpa duplikasi |
| TC-WIS-02 | FR-010 | NIM kosong di satu baris | Ditandai untuk review atau invalid sesuai kebijakan, tidak dikarang |
| TC-MAT-01 | FR-011 | Exact NIM SITASI ditemukan | Semua baris SITASI NIM terambil |
| TC-MAT-02 | FR-012 | Fail, Fail, Lulus untuk ujian sama | Bukti pernah lulus, semua attempt tetap terlacak |
| TC-MAT-03 | FR-013 | Nama singkatan, fuzzy tinggi | **PERLU_VERIFIKASI**, bukan VALID |
| TC-MAT-04 | FR-014 | SITASI MOS lulus; Certiport MCF pass | MOS valid; MCF tidak dihitung sebagai MOS |
| TC-MAT-05 | FR-014 | Nama persis + kandidat nama mirip di Certiport | Nama persis dipakai; kandidat mirip tidak mengisi |
| TC-MAT-06 | FR-014 | Nama parsial (2 dari 3 token) + Certiport PASS | `PERLU_VERIFIKASI`; kandidat bukan evidence/skor; skor < 100 |
| TC-MAT-07 | FR-014 | Nama sama tetapi NIM Certiport berbeda | `PERLU_VERIFIKASI` (`R16_NIM_CONFLICT`); tidak mengisi |
| TC-MAT-08 | FR-014 | Urutan nama/gelar berbeda, seluruh token sama | Identitas exact; bukan fuzzy |
| TC-VAL-01 | FR-015 | SITASI LULUS, Certiport FAIL ujian cocok | Konflik → review |
| TC-VAL-02 | FR-015 | NIM tidak ada di SITASI | `DATA_TIDAK_DITEMUKAN` |
| TC-VAL-03 | FR-015 | Certiport `INCO` | Tidak otomatis VALID |
| TC-REVIEW-01 | FR-016 | Petugas konfirmasi cocok + alasan | Audit petugas, waktu, alasan dan status tersimpan |
| TC-REVIEW-02 | FR-016 | Reviewer memaksa FAIL menjadi PASS | Ditolak; bukti sumber tidak dimanipulasi |
| TC-RES-01 | FR-017 | Filter status review | Jumlah dan isi konsisten |
| TC-EXP-01 | FR-018 | Ekspor setelah review | Baris/urutan/kolom non-target tetap |
| TC-EXP-02 | FR-018 | Ekspor final dengan campuran status | Hanya LULUS terisi; status lain kosong |
| TC-TRACE-02 | FR-019 | Master aktif berubah sesudah sync | Detail sesi tetap menunjukkan ID batch yang digunakan |
| TC-HIST-01 | FR-020 | Dua sesi berbeda | Riwayat terpisah dan dapat dibuka |

## 4. Kriteria penerimaan pengujian
- Seluruh test P0 harus diuji dan lulus sebelum demo dengan data institusi yang sesungguhnya.
- Kegagalan yang masih ada dicatat dengan severity, langkah reproduksi, dampak, dan bukti.
- Test tidak boleh diberi status PASS hanya karena fungsinya direncanakan/dokumen telah dibuat.

## 5. Format bukti black-box
| ID Test | Tanggal | Input (anonim) | Langkah | Hasil diharapkan | Hasil sebenarnya | Status | Screenshot/log |
|---|---|---|---|---|---|---|---|
| TC-IMP-01 | isi saat uji | `sitasi_dummy.xlsx` | Upload melalui UI | Batch COMPLETED | **Belum diuji** | NOT RUN | — |

## 6. Metrik evaluasi
Hitung `accuracy` hanya terhadap dataset dengan ground truth yang telah diverifikasi oleh petugas. Selain itu laporkan `jumlah data cocok by NIM`, `kasus perlu review`, `kasus tidak ditemukan`, `waktu proses`, tanpa menyebutnya akurasi. Nilai kemiripan fuzzy juga **bukan persentase kepastian kebenaran identitas**.

## 7. Instruksi praktis
Jalankan test unit di backend memakai `pytest`, gunakan FastAPI TestClient untuk API, dan lakukan UAT dengan browser. Catat versi kode/commit, dataset dummy, hasil aktual, dan tanggal untuk BAB IV.
