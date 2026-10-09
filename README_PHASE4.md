# Phase 4 — Implementasi Data Master SITASI & Certiport

Phase ini mengikuti keputusan Phase 1–3:

- Wisuda ↔ SITASI memakai **NIM sebagai key utama**.
- SITASI boleh memiliki banyak baris untuk satu NIM karena merupakan riwayat attempt/program.
- Certiport tidak memiliki NIM, sehingga nama yang sudah dinormalisasi disiapkan untuk Phase Matching berikutnya.
- Data master tidak dibaca langsung dari browser. Frontend memanggil FastAPI, FastAPI memanggil Supabase memakai server secret/service key.
- Import baru dibuat sebagai batch baru dan baru dijadikan `is_active = true` setelah semua baris berhasil masuk.

## Struktur Excel yang sudah diverifikasi

### Wisuda
Sheet: `Wisuda`

Kolom:
`No`, `Kode Prodi`, `Program Studi`, `NIM`, `Nama`, `Sertifikasi MOS`, `Sertifikasi MCF`, `Title Microsoft`

### SITASI
Sheet: `Master_Data`

Kolom:
`NIM`, `Nama`, `Fakultas`, `Kode NIM`, `Program Studi`, `Angkatan`, `Sertifikasi`, `Sub Program`, `Nilai`, `Status`

### Certiport
Sheet: `Results (264) Plus`

Kolom:
`First Name`, `Last Name`, `Full Name`, `Program Name`, `Certification Name`, `Score`, `Result`

## 1. Buat tabel Supabase

Buka SQL Editor Supabase lalu jalankan:

`database/migrations/20260930120000_phase4_foundation.sql`

Setelah itu jalankan query read-only `database/checks/phase4_foundation_check.sql`. Tabel data master tidak diberi akses langsung ke `anon` dan `authenticated`; FastAPI memakai server key.

## 2. Backend di PowerShell Windows

```powershell
py -3.12 -m venv backend\venv
backend\venv\Scripts\python.exe -m pip install -r backend\requirements.lock.txt
if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
Set-Location backend
.\venv\Scripts\Activate.ps1
```

Template environment hanya berisi nilai dummy yang cukup untuk health check. Endpoint import membutuhkan Supabase development yang berizin.

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Buka:

- API: `http://localhost:8000/api/v1/health`
- Swagger: `http://localhost:8000/docs`

## 3. Test importer melalui Swagger

### SITASI

`POST /api/v1/sitasi/import`

Upload file `data_sitasi.xlsx`.

### Certiport

`POST /api/v1/certiport/import`

Upload file `data_certiport.xlsx`.

Setelah berhasil:

- `GET /api/v1/sitasi?page=1&limit=50`
- `GET /api/v1/certiport?page=1&limit=50`

## 4. Frontend

Folder `frontend/` sudah memiliki manifest Next.js dan lockfile. Jalankan dari root repository:

```powershell
Set-Location frontend
npm ci
if (-not (Test-Path .env.local)) { Copy-Item .env.local.example .env.local }
npm run dev
```

`NEXT_PUBLIC_API_URL` pada `.env.local.example` mengarah ke `http://localhost:8000/api/v1`.

Halaman:

- `/sitasi`
- `/certiport`

## 5. Catatan penting output Wisuda

Pada file wisuda contoh, ditemukan data MOS berada pada kolom `Sertifikasi MCF` pada beberapa baris. Karena itu Phase 4 **belum mengisi kolom output wisuda**. Mapping output akhir harus dikunci pada fase matching/export agar tidak menulis data ke kolom yang salah.

## Definition of Done Phase 4

- Schema data master tersedia.
- Import SITASI `.xlsx` tervalidasi berdasarkan header.
- Import Certiport `.xlsx` tervalidasi berdasarkan header.
- NIM dan nama dinormalisasi.
- Import memakai batch dan hanya batch sukses yang aktif.
- Data SITASI dapat dipaginasi/filter.
- Data Certiport dapat dipaginasi/filter.
- Halaman Data SITASI dan Data Certiport memiliki upload dan tabel preview.

Phase berikutnya: **Phase 5 — Upload Wisuda + Matching Engine Wisuda ↔ SITASI ↔ Certiport + status agregat MOS/MCF.**
