# 20 — Gate Keputusan Bisnis: Lembar Pengesahan Output Mapping (ADR-003, 005, 006, 010, 011)

Dokumen ini adalah **gerbang keputusan bisnis resmi** sebelum ekspor administratif wisuda dapat difinalisasi. Berdasarkan prinsip kehati-hatian, sistem ITCC Wisuda Sync **tidak boleh menulis hasil akhir resmi atau menimpa berkas akademik** sebelum tabel pertanyaan dan opsi di bawah ini disahkan oleh pihak berwenang ITCC dan pimpinan program studi.

---

## 1. Status Gerbang Keputusan

| Topik | ADR Terkait | Status Saat Ini | Dampak Implementasi |
|---|---|---|---|
| Format Isi Kolom `Sertifikasi MOS`, `MCF` | ADR-003 | **TERBUKA (BLOCKED)** | Ekspor final diblokir; hanya pratinjau DRAFT berlabel |
| Ekuivalensi Alias & Versi Ujian | ADR-005 | **TERBUKA (DRAFT)** | Semua alias menghasilkan status `PERLU_VERIFIKASI` |
| Format & Definisi `Title Microsoft` | ADR-006 | **TERBUKA (BLOCKED)** | Kolom tidak diisi otomatis pada ekspor final |
| Perlakuan Sel yang Sudah Terisi | ADR-010 | **TERBUKA (BLOCKED)** | Dilarang menimpa (overwrite) data pra-ekspor |
| Syarat Sertifikasi per Prodi / Wisuda | ADR-011 | **TERBUKA (BLOCKED)** | Sistem tidak menyimpulkan kelulusan syarat wisuda |

---

## 2. Tabel Pertanyaan Keputusan, Opsi Kebijakan, dan Contoh Anonim

### Pertanyaan 1: Format Teks pada Kolom `Sertifikasi MOS` dan `Sertifikasi MCF` (ADR-003)
*Temuan data contoh:* Kolom F berisi teks seperti `MOS (Word 2019 - Lulus)`, `MOS (Excel 2019 - Lulus)`, `MOS (Word 2019 - Tidak lulus)`. Kolom G (`Sertifikasi MCF`) kosong pada data contoh.

| Opsi | Deskripsi Opsi | Contoh Keluaran Anonim (Lulus) | Contoh Keluaran Anonim (Gagal) | Rekomendasi Teknis |
|---|---|---|---|---|
| **Opsi 1A (Format Eksisting)** | Sertakan kategori, nama produk, tahun, dan status kelulusan | `MOS (Word 2019 - Lulus)` | `MOS (Word 2019 - Tidak lulus)` | **Direkomendasikan**: Sesuai pola file wisuda eksisting |
| **Opsi 1B (Hanya Nama Ujian)** | Nama ujian singkat tanpa tanda kurung status | `Word 2019` | Kosong (tidak diisi jika gagal) | Perlu kejelasan jika gagal |
| **Opsi 1C (Hanya Jika Lulus)** | Sel diisi hanya jika mahasiswa lulus; jika gagal/belum ujian, sel dikosongkan | `MOS (Word 2019 - Lulus)` | `[KOSONG]` | Menghindari label negatif di berkas wisuda |

---

### Pertanyaan 2: Mahasiswa dengan Lebih dari Satu Ujian dalam Satu Kategori (ADR-003)
*Contoh kasus:* Mahasiswa lulus `MOS Word` DAN `MOS Excel`.

| Opsi | Deskripsi Opsi | Contoh Kolom `Sertifikasi MOS` | Catatan Risiko |
|---|---|---|---|
| **Opsi 2A (Gabung Koma/Pemisah)** | Seluruh sertifikasi yang lulus digabungkan dalam satu sel dengan pemisah koma | `MOS (Word 2019 - Lulus), MOS (Excel 2019 - Lulus)` | Panjang teks bertambah; kompatibel Excel |
| **Opsi 2B (Ambil Salah Satu / Prioritas)** | Hanya satu sertifikasi tertinggi atau pertama yang diisikan | `MOS (Word 2019 - Lulus)` | Menghilangkan bukti pencapaian ujian kedua |
| **Opsi 2C (Baris Baru dalam Sel)** | Menggunakan pemisah baris (`Alt+Enter` / `\n`) | `MOS (Word 2019 - Lulus)`<br>`MOS (Excel 2019 - Lulus)` | Memerlukan auto-row height pada template Excel |

---

### Pertanyaan 3: Perlakuan Status Belum Lulus, Pending, atau Perlu Review (ADR-003, ADR-004)
*Kasus:* Mahasiswa hanya memiliki riwayat gagal, masih pending, atau status review belum disetujui.

| Opsi | Deskripsi Opsi | Nilai Kolom MOS / MCF | Nilai Kolom Catatan / Status |
|---|---|---|---|
| **Opsi 3A (Teks Eksplisit)** | Tulis status lengkap di sel target | `MOS (Word 2019 - Tidak lulus)` atau `[PERLU VERIFIKASI]` | Transparan, tetapi berkas wisuda memuat label kegagalan |
| **Opsi 3B (Kosongkan Sel Target, Beri Lembar Review)** | Sel sertifikasi wisuda dikosongkan; daftar verifikasi dicetak di sheet audit terpisah | `[KOSONG]` | **Direkomendasikan**: Menjaga kebersihan lembar utama wisuda |
| **Opsi 3C (Tanda Khusus)** | Diberi penanda asterisk `*` atau tanda strip `-` | `-` | Ambigu tanpa keterangan tambahan |

---

### Pertanyaan 4: Definisi dan Pengisian Kolom `Title Microsoft` (ADR-006)
*Temuan data contoh:* Kolom H memuat teks `'MOS'` pada sebagian baris.

| Opsi | Kondisi Mahasiswa | Nilai Kolom `Title Microsoft` | Keterangan |
|---|---|---|---|
| **Opsi 4A (Label Kategori)** | Lulus MOS saja<br>Lulus MCF saja<br>Lulus MOS & MCF<br>Tidak Lulus | `MOS`<br>`MCF`<br>`MOS, MCF`<br>`[KOSONG]` | **Direkomendasikan**: Sesuai temuan pola sampel |
| **Opsi 4B (Sebutan Gelar Lengkap)** | Lulus MOS<br>Lulus MCF | `Microsoft Office Specialist`<br>`Microsoft Certified Fundamentals` | Lebih panjang, berisiko terpotong tampilan cetak |
| **Opsi 4C (Hanya Ditentukan Manual)** | Semua kondisi | Ditentukan manual oleh petugas | Mencegah salah asumsikan sertifikasi |

---

### Pertanyaan 5: Perlakuan Sel Target yang Sudah Terisi Sebelumnya (ADR-010)
*Kasus:* File Excel wisuda yang diunggah sudah memiliki teks lama pada kolom F, G, atau H.

| Opsi | Tindakan Sistem | Jejak Audit | Rekomendasi |
|---|---|---|---|
| **Opsi 5A (Jangan Overwrite)** | Pertahankan nilai lama; laporkan selisih pada pratinjau | Sel lama dicatat, tidak diubah | **Sangat Direkomendasikan**: Perlindungan data sah |
| **Opsi 5B (Isi Hanya yang Kosong)** | Sel terisi dibiarkan; hanya sel kosong yang diisi dari hasil sinkronisasi | Nilai baru diisi ke sel kosong | Aman bila data lama adalah input manual sah |
| **Opsi 5C (Timpa dengan Konfirmasi)** | Nilai ditimpa hanya jika petugas memberikan konfirmasi tertulis | Nilai lama dan baru dicatat di `review_audit` | Memerlukan intervensi manual |

---

### Pertanyaan 6: Ekuivalensi Alias dan Versi Tahun Produk (ADR-005)
*Kasus:* Perbedaan label penamaan antara SITASI dan Certiport.

| Produk SITASI | Label Certiport | Usulan Status Ekuivalensi | Catatan / Risiko |
|---|---|---|---|
| `Word` | `Word 2019` | Setara (Ekuivalen) | Apakah berlaku untuk Word 2016? Butuh kepastian batas tahun |
| `Word` | `Microsoft Word 2019` | Setara (Ekuivalen) | Variasi penamaan vendor |
| `Excel` | `Excel 2019` | Setara (Ekuivalen) | Sama dengan Word |
| `Azure AI-900` | `Microsoft Azure AI Fundamentals` | Setara (Ekuivalen) | Kode ujian vs nama resmi sertifikasi |
| `Azure AZ-900` | `Microsoft Azure Fundamentals` | Setara (Ekuivalen) | Kode ujian vs nama resmi sertifikasi |

---

### Pertanyaan 7: Kewajiban Sertifikasi per Program Studi (ADR-011)
*Pertanyaan:* Apakah seluruh program studi wajib memiliki sertifikasi MOS dan MCF sebagai syarat kelulusan?

| Program Studi | Kewajiban MOS | Kewajiban MCF | Dasar SK / Keputusan |
|---|---|---|---|
| Teknik Informatika | Wajib / Pilihan / Belum disahkan | Wajib / Pilihan / Belum disahkan | Menunggu penetapan Dekanat/Kaprodi |
| Sistem Informasi | Wajib / Pilihan / Belum disahkan | Wajib / Pilihan / Belum disahkan | Menunggu penetapan Dekanat/Kaprodi |
| Prodi Lainnya | Wajib / Pilihan / Belum disahkan | Wajib / Pilihan / Belum disahkan | Menunggu penetapan Dekanat/Kaprodi |

*Prinsip sistem:* Sebelum ada penetapan tertulis, sistem **tidak berhak** menandai mahasiswa "Tidak Memenuhi Syarat Wisuda" hanya karena sertifikasi belum lengkap.

---

## 3. Ketetapan Implementasi Teknis Sebelum Pengesahan

1. **Ekspor Final Resmi DIBLOKIR**: Endpoint `GET /api/v1/sync/{id}/export?mode=final` mengembalikan respons `403 Forbidden` disertai pesan penolakan yang merujuk pada dokumen ini.
2. **Ekspor Pratinjau DRAFT Diizinkan**: Endpoint `GET /api/v1/sync/{id}/export?mode=draft` menghasilkan berkas Excel dengan watermark/label `[DRAFT - PRATINJAU BELUM DISAHKAN]` pada kolom target atau nama file, mempertahankan seluruh susunan sheet dan formula non-target.
3. **Tombol UI Final Nonaktif**: Pada antarmuka pengguna, tombol "Unduh Excel Final" ditampilkan dalam keadaan dinonaktifkan (disabled) dengan tooltip penjelasan.

---

## 4. Lembar Tanda Tangan Pengesahan (Template)

| Pihak | Nama Pejabat | NIP / Identitas | Tanda Tangan | Tanggal |
|---|---|---|---|---|
| Kepala ITCC | ______________________ | _________________ | [                ] | ____/____/2026 |
| Pembimbing Project | ______________________ | _________________ | [                ] | ____/____/2026 |
| Perwakilan Akademik / Wisuda | ______________________ | _________________ | [                ] | ____/____/2026 |
