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

`database/001_phase4_data_master.sql`

Untuk project ini tabel data master sengaja tidak diberi akses langsung ke `anon` dan `authenticated`. FastAPI memakai service/server key.

## 2. Backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Copy environment:

```bash
copy .env.example .env
```

Isi URL dan server secret/service role key milik project Supabase.

Run:

```bash
uvicorn app.main:app --reload
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

File dalam folder `frontend/` adalah file Phase 4 yang ditempelkan ke project Next.js hasil `create-next-app` dari Phase 3.

Pastikan alias `@/*` aktif (default create-next-app TypeScript), lalu buat `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

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
