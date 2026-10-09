# 08 — Kontrak REST API Frontend ↔ Backend

**Prefix:** `/api/v1` · **Format:** JSON (kecuali upload `multipart/form-data` dan download `.xlsx`).
Proses sync, review, export, dan dashboard tetap **rencana**; endpoint validasi upload Wisuda ditambahkan pada Tahap 07. Auth SITASI/Certiport serta `/auth/me` diterapkan pada Tahap 05.

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
| GET | `/health` | Cek proses FastAPI | SUDAH ADA |
| GET | `/auth/me` | Profil petugas aktif dari allowlist server | SUDAH ADA |
| GET | `/sitasi/batch` | Metadata batch SITASI aktif | SUDAH ADA, petugas saja |
| GET | `/sitasi` | List/filter master SITASI aktif | SUDAH ADA |
| POST | `/sitasi/import` | Import Excel SITASI | SUDAH ADA, petugas saja |
| GET | `/certiport` | List/filter master Certiport aktif | SUDAH ADA |
| GET | `/certiport/batch` | Metadata batch Certiport aktif | SUDAH ADA, petugas saja |
| POST | `/certiport/import` | Import Excel Certiport | SUDAH ADA, petugas saja |
| POST | `/sync/validate` | Validasi read-only workbook Wisuda dan ringkasan batch aktif | SUDAH ADA, petugas saja |
| GET | `/dashboard/summary` | Ringkasan master/proses | RENCANA |
| POST | `/sync` | Upload Wisuda + proses | RENCANA |
| GET | `/sync` | Riwayat sesi | RENCANA |
| GET | `/sync/{id}` | Ringkasan satu sesi | RENCANA |
| GET | `/sync/{id}/results` | Hasil per baris dengan filter | RENCANA |
| GET | `/sync/{id}/results/{result_id}` | Detail dan sumber bukti | RENCANA |
| PATCH | `/sync/{id}/results/{result_id}/review` | Review manual | RENCANA |
| GET | `/sync/{id}/export` | Download workbook final | RENCANA |

### `POST /sync/validate`
Request multipart `file` berformat `.xlsx` dengan sheet `Wisuda`. Endpoint ini hanya membaca workbook; tidak menyimpan, mengubah, atau memetakan kolom sertifikasi. Header `NIM` dan `Nama` wajib. Respons mencakup jumlah baris mahasiswa, baris kosong, susunan kolom, masalah per nomor baris tanpa nilai NIM/nama, serta ringkasan batch SITASI dan Certiport aktif. Formula pada NIM/Nama, NIM kosong/tidak aman, dan duplikat menghasilkan masalah validasi. Baris kosong dilaporkan terpisah dan tidak dihitung sebagai mahasiswa.

## 3. Upload data master
### `POST /sitasi/import`
Form: `file` (Excel `.xlsx`, maksimum default 10 MiB; dapat diatur melalui `MAX_UPLOAD_SIZE_BYTES`). Sheet wajib `Master_Data`. Parser menolak formula dan workbook bermacro.
Validasi header wajib: `NIM`, `Nama`, `Fakultas`, `Kode NIM`, `Program Studi`, `Angkatan`, `Sertifikasi`, `Sub Program`, `Nilai`, `Status`.

### `POST /certiport/import`
Form: `file` (Excel `.xlsx`, maksimum default 10 MiB; dapat diatur melalui `MAX_UPLOAD_SIZE_BYTES`). Sheet wajib `Results (264) Plus`. Parser menolak formula dan workbook bermacro.
Header wajib: `First Name`, `Last Name`, `Full Name`, `Program Name`, `Certification Name`, `Score`, `Result`.

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

## 7. Export (target)
`GET /sync/{id}/export` → `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` + attachment filename aman. Jika mapping kolom output belum disetujui, backend harus menolak ekspor administratif final atau memberi watermark/indikasi draft sesuai keputusan petugas.

## 8. Pengamanan API
- Ekstensi dan struktur ZIP OOXML `.xlsx`, batas `MAX_UPLOAD_SIZE_BYTES`, penolakan formula/macro, serta nama sheet dan header wajib.
- Jangan mengembalikan stack trace atau kredensial di respons.
- Pastikan `result_id` milik sesi yang diminta.
- Paginasi dan batas request agar browser tidak memuat ribuan baris sekaligus.
- JWT valid tidak otomatis berarti petugas diizinkan; lakukan authorization check.
