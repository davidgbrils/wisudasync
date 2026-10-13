# ITCC Wisuda Sync

Aplikasi web internal untuk mengimpor data master SITASI & Certiport, mengunggah Excel wisuda, mencocokkan berdasarkan NIM, memverifikasi dengan Certiport, meninjau kasus ambigu, dan mengekspor Excel. Alur: **Next.js → FastAPI → Supabase**.

**Status terkini:** backend (auth, impor, matching, sinkronisasi, review, export-gate) dan frontend terimplementasi serta lulus **134 test otomatis + typecheck + build** dengan fixture sintetis. **Belum siap production**: migrasi SQL/RLS belum dieksekusi pada Supabase, UAT browser belum dijalankan, dan ekspor final masih terkunci. Lihat `docs/22_UAT_FORM.md` dan `docs/25_LAPORAN_MAGANG.md`.

Dokumentasi lengkap ada di [`docs/README.md`](docs/README.md).

## Prasyarat Windows

- Python 3.12
- Node.js 22 dan npm 10
- PowerShell
- Supabase lokal/development hanya diperlukan untuk mencoba endpoint import; health check dapat memakai konfigurasi dummy.

## 1. Siapkan backend

Jalankan dari root repository:

```powershell
py -3.12 -m venv backend\venv
backend\venv\Scripts\python.exe -m pip install -r backend\requirements.lock.txt
if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
```

`backend/.env.example` hanya berisi nilai dummy. Untuk mencoba import, ubah `backend/.env` memakai URL dan server key dari Supabase development yang berizin. Jangan commit file tersebut.

Jalankan API pada terminal pertama:

```powershell
Set-Location backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Periksa health dari terminal lain:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
```

## 2. Siapkan frontend

Jalankan dari root repository:

```powershell
Set-Location frontend
npm ci
if (-not (Test-Path .env.local)) { Copy-Item .env.local.example .env.local }
npm run dev
```

Buka `http://localhost:3000/sitasi` atau `http://localhost:3000/certiport`. Frontend memakai `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1` untuk memanggil FastAPI.

## 3. Pemeriksaan lokal

Backend:

```powershell
Set-Location backend
.\venv\Scripts\python.exe -m pytest -q
```

Frontend:

```powershell
Set-Location frontend
npm run typecheck
npm run build
npm audit --audit-level=moderate
```

## Batas dan catatan

- Gunakan hanya fixture anonim atau data dummy untuk pengujian lokal.
- Endpoint data (SITASI/Certiport/Sync) memerlukan Bearer token petugas aktif; `/health` publik.
- Konfigurasi dummy hanya mendukung health check, bukan operasi Supabase.
- Mapping `Sertifikasi MOS`, `Sertifikasi MCF`, dan `Title Microsoft` belum disetujui dan tidak diisi otomatis; ekspor final terkunci (`403`).
- Jangan jalankan deployment sebelum UAT selesai dan pengesahan output ditandatangani.

Detail implementasi tersedia di [`README_PHASE4.md`](README_PHASE4.md). Aturan agent tersedia di [`AGENTS.md`](AGENTS.md), sedangkan dokumentasi produk berada di [`docs/README.md`](docs/README.md).
