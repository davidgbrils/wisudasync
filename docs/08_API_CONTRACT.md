# 08 — Kontrak REST API Frontend ↔ Backend

**Prefix:** `/api/v1` · **Format:** JSON (kecuali upload `multipart/form-data` dan download `.xlsx`).
Seluruh endpoint SITASI/Certiport/Sync beserta `/auth/me` **sudah diimplementasikan** dan diuji dengan fixture lokal (134 test backend PASS). Runtime terhadap Supabase development berizin **belum dijalankan**.

## 1. Prinsip umum
- Semua route SITASI/Certiport mewajibkan `Authorization: Bearer <access_token>`. Backend memvalidasi token melalui Supabase Auth dan cek `profiles.id`, `is_active`, serta `role` tepercaya (`staff`/`admin`).
- `GET /health` satu-satunya endpoint publik saat ini. Login saja atau role `authenticated` tidak memberi akses data.
- Pagination: `page` dimulai 1; `limit` default 50 dan mempunyai maksimum yang dibatasi server.
- Kesalahan file/validasi → 400/422, file terlalu besar → 413, token invalid → 401, tidak berhak → 403, konflik → 409, error internal → 500.

### Respons sukses (target)
```json
{ "success": true, "message": "Berhasil", "data": { "items": [], "total": 0 } }
```

### Respons kesalahan (target)
```json
{ "success": false, "message": "Kolom wajib tidak ditemukan", "errors": [{ "field": "NIM", "reason": "Header wajib" }] }
```

Catatan: Bentuk respons yang sudah ada pada starter dapat berbeda dari contoh target ini. Saat fase integrasi, pilih satu struktur konsisten dan perbarui implementasi/test serta dokumentasi bersamaan.

## 2. Daftar endpoint
| Metode | Path | Keterangan | Status |
|---|---|---|---|
| GET | `/health` | Cek proses FastAPI (publik) | SUDAH ADA |
| GET | `/auth/me` | Profil petugas aktif dari allowlist server | SUDAH ADA, petugas saja |
| GET | `/sitasi/batch` | Metadata batch SITASI aktif | SUDAH ADA, petugas saja |
| GET | `/sitasi` | List/filter master SITASI aktif | SUDAH ADA, petugas saja |
| POST | `/sitasi/import` | Import Excel SITASI | SUDAH ADA, petugas saja |
| GET | `/certiport/batch` | Metadata batch Certiport aktif | SUDAH ADA, petugas saja |
| GET | `/certiport` | List/filter master Certiport aktif | SUDAH ADA, petugas saja |
| POST | `/certiport/import` | Import Excel Certiport | SUDAH ADA, petugas saja |
| POST | `/sync/validate` | Validasi read-only workbook Wisuda dan ringkasan batch aktif | SUDAH ADA, petugas saja |
| POST | `/sync` | Upload Wisuda + jalankan sinkronisasi (HTTP 201) | SUDAH ADA, petugas saja |
| GET | `/sync` | Riwayat sesi (paginasi) | SUDAH ADA, petugas saja |
| GET | `/sync/{session_id}` | Ringkasan satu sesi (404 bila tak ada) | SUDAH ADA, petugas saja |
| GET | `/sync/{session_id}/results` | Hasil per baris dengan filter status/search/needs_review | SUDAH ADA, petugas saja |
| GET | `/sync/{session_id}/results/{result_id}` | Detail dan sumber bukti + riwayat review | SUDAH ADA, petugas saja |
| PATCH | `/sync/{session_id}/results/{result_id}/review` | Review manual (jejak audit append-only) | SUDAH ADA, petugas saja |
| GET | `/sync/{session_id}/export` | Download workbook; `mode=final` (default, isi LULUS) / `mode=draft` (berlabel) | SUDAH ADA, petugas saja |
| GET | `/dashboard/summary` | Ringkasan master/proses | RENCANA (tidak dipakai; UI memakai endpoint batch langsung) |

### `POST /sync/validate`
Request multipart `file` berformat `.xlsx` dengan sheet `Wisuda`. Endpoint ini hanya membaca workbook; tidak menyimpan, mengubah, atau memetakan kolom sertifikasi. Header `NIM` dan `Nama` wajib. Respons mencakup jumlah baris mahasiswa, baris kosong, susunan kolom, masalah per nomor baris tanpa nilai NIM/nama, serta ringkasan batch SITASI dan Certiport aktif. Formula pada NIM/Nama, NIM kosong/tidak aman, dan duplikat menghasilkan masalah validasi. Baris kosong dilaporkan terpisah dan tidak dihitung sebagai mahasiswa.

## 3. Upload data master
### `POST /sitasi/import`
Form: `file` (Excel `.xlsx`, maksimum default 10 MiB; dapat diatur melalui `MAX_UPLOAD_SIZE_BYTES`). Sheet wajib `Master_Data`. Parser menolak formula pada kolom wajib dan workbook bermacro.
Header wajib (skema ringkas): `NIM`, `Nama`, `Sertifikasi`, `Nilai`, `Status`. Header opsional: `Kode NIM`, `Program Studi`, `Fakultas`, `Angkatan`, `Sub Program`.

### `POST /certiport/import`
Form: `file` (Excel `.xlsx`, maksimum default 10 MiB; dapat diatur melalui `MAX_UPLOAD_SIZE_BYTES`). Sheet wajib `Results (264) Plus`. Parser menolak formula pada kolom wajib dan workbook bermacro.
Header wajib (skema ringkas): `Nama`, `Sertifikasi`, `Nilai`, `Status`. Skema lama (`First Name`, `Last Name`, `Full Name`, `Program Name`, `Certification Name`, `Score`, `Result`) masih dibaca sebagai fallback. Status sumber `LULUS`/`PASS` dipetakan menjadi `PASS`; `TIDAK LULUS`/`GAGAL`/`FAIL` menjadi `FAIL`.

Respons contoh rancangan:
```json
{
  "success": true,
  "message": "Impor berhasil",
  "data": {
    "import_id": "uuid-dari-server",
    "file_name": "contoh.xlsx",
    "total_rows": 100,
    "imported_rows": 100,
    "status": "COMPLETED"
  }
}
```
Jumlah pada contoh adalah dummy.

`GET /sitasi/batch` dan `GET /certiport/batch` mengembalikan metadata batch aktif saja (`id`, jumlah baris, status, waktu selesai), atau `data: null` jika belum ada batch. Endpoint ini memerlukan petugas dan tidak mengembalikan nama file.

## 4. Filter master
- `GET /sitasi?page=1&limit=50&nim=209900001&sertifikasi=MOS&status=LULUS`
- `GET /certiport?page=1&limit=50&nama=CONTOH&result=PASS`

Semua filter harus diterapkan hanya pada `import_id` **aktif**, tidak menampilkan batch lama secara tidak sengaja.

## 5. Sinkronisasi wisuda (target)
### `POST /sync`
Request: multipart form `file`. Respons 200/201 untuk proses langsung, atau 202 jika proses asynchronous diimplementasikan kemudian.

```json
{
  "success": true,
  "data": {
    "session_id": "uuid-dari-server",
    "status": "COMPLETED",
    "total_rows": 3,
    "sitasi_import_id": "uuid-batch-sitasi",
    "certiport_import_id": "uuid-batch-certiport"
  }
}
```

### `GET /sync/{id}/results?status=PERLU_VERIFIKASI&page=1`
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid-result",
        "source_row": 2,
        "nim": "209900001",
        "nama_wisuda": "MAHASISWA CONTOH",
        "mos_status": "LULUS",
        "mcf_status": null,
        "validation_status": "PERLU_VERIFIKASI",
        "needs_review": true,
        "review_reasons": ["Nama Certiport tidak unik"]
      }
    ],
    "page": 1,
    "limit": 50,
    "total": 1
  }
}
```

### `GET /sync/{id}/results/{result_id}`
Mengembalikan detail baris wisuda, seluruh bukti yang diperlukan dari SITASI dan Certiport (minimal source_row, kategori, ujian, status), dan catatan kandidat tanpa mengeluarkan data yang tidak dibutuhkan browser.

## 6. Review manual (target)
`PATCH /sync/{id}/results/{result_id}/review`
```json
{ "decision": "KONFIRMASI_COCOK", "note": "Nama singkatan diverifikasi menggunakan data resmi" }
```
Nilai decision yang direncanakan: `KONFIRMASI_COCOK`, `TIDAK_COCOK`, `TUNDA_VERIFIKASI`. Backend memeriksa hak petugas dan mencatat audit. `KONFIRMASI_COCOK` memverifikasi **identitas**, bukan mengganti status ujian dari gagal menjadi lulus.

## 7. Export
`GET /sync/{id}/export?mode=final` (default) → workbook delapan kolom Wisuda. Kolom `Sertifikasi MOS`, `Sertifikasi MCF`, dan `Title Microsoft` hanya diisi untuk status `VALID` (LULUS); status lain kosong. `mode=draft` mengembalikan data yang sama dengan awalan `[DRAFT] `.

Format isi yang disetujui 2026-10-23:
- `Sertifikasi MOS`: `MOS (Lulus)` atau kosong.
- `Sertifikasi MCF`: `MCF (Lulus)` untuk prodi 31/32 atau kosong.
- `Title Microsoft`: `MOS`, `MCF`, `MOS, MCF`, atau kosong.

`Content-Disposition` memakai nama berkas aman `wisuda_<mode>_<session-prefix>.xlsx`.

## 8. Pengamanan API
- Ekstensi dan struktur ZIP OOXML `.xlsx`, batas `MAX_UPLOAD_SIZE_BYTES`, penolakan formula/macro, serta nama sheet dan header wajib.
- Jangan mengembalikan stack trace atau kredensial di respons.
- Pastikan `result_id` milik sesi yang diminta.
- Paginasi dan batas request agar browser tidak memuat ribuan baris sekaligus.
- JWT valid tidak otomatis berarti petugas diizinkan; lakukan authorization check.
