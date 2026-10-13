# 24 — Panduan Operator: Import, Backup, Recovery & Referensi Teknis

Panduan untuk operator/teknis yang menjalankan ITCC Wisuda Sync di lingkungan **development berizin**. Melengkapi `docs/17_OPERATIONS.md` (setup) dan `docs/23_USER_MANUAL.md` (alur petugas).

> **Prinsip:** jangan jalankan pada data asli atau produksi sebelum UAT selesai, retensi/backup disetujui, dan izin institusi diperoleh.

---

## 1. Ringkasan sistem

```
Browser (Next.js)  →  FastAPI (Python)  →  Supabase (PostgreSQL + Auth)
      |                     |                        |
  Supabase Auth        validasi & matching      data master, sesi,
  (token)              Excel (Pandas/OpenPyXL)   hasil, evidence, audit
```
Browser **tidak pernah** memegang service-role key. Semua akses data lewat FastAPI yang memverifikasi token Supabase dan profil petugas.

Komponen kode utama:
- Backend: `backend/app/main.py`, `api/v1/endpoints/*`, `services/*`, `core/*`.
- Frontend: `frontend/app/*`, `frontend/components/*`, `frontend/lib/api.ts`.
- Database: `database/migrations/*`, `database/checks/*`, `database/rollbacks/*`.

---

## 2. Import data master

### 2.1 Format yang diterima

| Sumber | Sheet wajib | Header wajib |
|---|---|---|
| SITASI | `Master_Data` | `NIM`, `Nama`, `Fakultas`, `Kode NIM`, `Program Studi`, `Angkatan`, `Sertifikasi`, `Sub Program`, `Nilai`, `Status` |
| Certiport | `Results (264) Plus` | `First Name`, `Last Name`, `Full Name`, `Program Name`, `Certification Name`, `Score`, `Result` |

Aturan aman: file `.xlsx` saja (bukan `.xlsm`), maksimum 10 MiB (default, dapat diatur `MAX_UPLOAD_SIZE_BYTES`), header dicari pada 10 baris awal, baris berformula pada kolom wajib ditolak, header ganda ditolak. Pengecualian: kolom `Full Name` Certiport boleh berformula CONCATENATE; nilainya diambil dari cache atau diturunkan dari `First Name` + `Last Name`.

### 2.2 Langkah import

1. Login sebagai petugas berhak.
2. Buka **Data SITASI** atau **Data Certiport**.
3. Unggah berkas `.xlsx`. Sistem:
   - memvalidasi sheet & header;
   - membuat baris `data_imports` berstatus `PROCESSING`;
   - menyisipkan baris ke `sitasi_data`/`certiport_data` per potongan (500 baris);
   - mengaktifkan batch lewat RPC `complete_data_import` (atomik): menonaktifkan batch lama, menandai batch baru `COMPLETED` + `is_active = true`.
4. Batch aktif terbaru tampil di UI; filter/pencarian hanya menyentuh batch aktif.

### 2.3 Satu batch aktif per jenis

Index unik parsial `data_imports_one_active_per_type_idx` (pada `data_type` where `is_active`) menjamin maksimal satu batch aktif. RPC mengambil `pg_advisory_xact_lock` per jenis data sehingga dua import nyaris bersamaan tidak menghasilkan keadaan tak konsisten.

### 2.4 Recovery saat import gagal

- Kegagalan sebelum aktivasi → batch staging diberi status `FAILED`, baris staging dihapus, **batch aktif lama tetap utuh**.
- Kegagalan di RPC/aktivasi → batch tidak diaktifkan; periksa `error_message`.
- Jika jumlah baris tak sesuai (`total_rows <> imported_rows`), RPC menolak aktivasi.
- Untuk mengulang: cukup unggah ulang berkas yang sudah diperbaiki; ini membuat batch/sesi baru tanpa merusak riwayat lama.

### 2.5 Pemeriksaan database (read-only)

Jalankan `database/checks/phase4_foundation_check.sql` untuk memverifikasi tabel, kolom, constraint, index, status RLS (harus tanpa policy browser), grants (hanya `service_role`), dan duplikasi batch aktif. Skrip ini **tidak** mengubah data.

---

## 3. Prosedur backup

> Semua di bawah mengikuti **kebijakan resmi ITCC** (ADR-007 masih terbuka). Angka frekuensi/lokasi belum ditetapkan; jangan mengarang.

### 3.1 Yang perlu dicadangkan
- Skema & data tabel: `profiles`, `data_imports`, `sitasi_data`, `certiport_data`, `sync_sessions`, `sync_results`, `sync_evidence`, `review_audit`.
- File pengaturan (tanpa rahasia): `.env.example`, lockfile.
- **Bukan** untuk dicadangkan ke repo: `.env` berisi service-role key dan berkas Excel asli.

### 3.2 Cara (development)
1. Gunakan fitur backup/dump Supabase development sesuai kebijakan.
2. Simpan salinan di lokasi **privat** yang disetujui, bukan direktori yang diekspos web.
3. Catat waktu, cakupan, dan penanggung jawab backup.
4. Uji pemulihan pada database development terpisah minimal sekali.

### 3.3 Larangan
- Jangan menyimpan dump berisi data pribadi di Git/hosting publik.
- Jangan menaruh backup di dalam folder yang diserve web.

---

## 4. Prosedur recovery

| Situasi | Langkah |
|---|---|
| Import salah/gagal | Batch staging dibersihkan otomatis; unggah ulang berkas benar. Batch aktif lama tidak berubah. |
| Batch aktif tidak sengaja berubah | Aktifkan kembali batch yang benar dengan mengimpornya ulang, atau pulihkan dari backup. |
| Sesi sinkronisasi `FAILED` | Buka detail sesi (`error_message` aman), perbaiki penyebab, jalankan ulang (membuat sesi baru). Sesi lama tidak dihapus. |
| Data hilang karena kesalahan manual | Pulihkan dari backup terakhir; verifikasi jumlah baris & index unik batch aktif. |
| Migrasi gagal | Jangan pakai `CASCADE`. Gunakan `database/rollbacks/20260930120000_phase4_foundation_rollback.sql` (menolak bila tabel berisi data). |
| Service-role key bocor | Rotasi kunci di dashboard Supabase; ganti `backend/.env`; audit log akses. |

**Aturan recovery:** jangan hapus `sync_sessions`/`sync_evidence`/`review_audit` secara manual tanpa kebijakan retensi; catat setiap tindakan.

---

## 5. Kontrol akses & audit (ringkas)

- Endpoint data (SITASI/Certiport/Sync) wajib Bearer token **dan** profil `is_active` + role `staff`/`admin`. `/health` publik.
- RLS deny-by-default; tidak ada policy `anon`/`authenticated`; akses hanya `service_role` (backend).
- `review_audit` append-only: siapa, kapan, keputusan, catatan, status lama→baru.
- Ekspor final terkunci (`403`) sampai `docs/20_OUTPUT_MAPPING_APPROVAL.md` disahkan.

---

## 6. Daftar library & versi aktual

### Backend (`backend/requirements.txt`, Python 3.12)
| Library | Versi |
|---|---|
| fastapi | 0.142.2 |
| uvicorn[standard] | 0.54.0 |
| pandas | 3.0.6 |
| openpyxl | 3.1.5 |
| supabase | 2.31.0 |
| python-dotenv | 1.2.3 |
| python-multipart | 0.0.32 |
| pydantic-settings | 2.15.0 |
| rapidfuzz | 3.13.0 |
| pytest (dev, `requirements-dev.txt`) | 9.1.1 |

Versi transitif lengkap ada di `backend/requirements.lock.txt`.

### Frontend (`frontend/package.json`, Node.js 22 / npm 10)
| Paket | Versi |
|---|---|
| next | 16.3.7 |
| react / react-dom | 19.3.0 |
| @supabase/ssr | 0.12.7 |
| @supabase/supabase-js | 2.117.2 |
| typescript (dev) | 5.9.3 |
| tailwindcss (dev) | 3.4.19 |
| postcss (dev) | 8.5.28 |
| autoprefixer (dev) | 10.6.1 |
| @types/node (dev) | ^22 |
| @types/react, @types/react-dom (dev) | ^19 |

### Infrastruktur
Supabase (PostgreSQL + Auth) — versi mengikuti project development yang disetujui.

---

## 7. Limitasi terbuka

| # | Limitasi | Status | Dampak |
|---|---|---|---|
| L1 | Migrasi SQL belum pernah dieksekusi di PostgreSQL/Supabase | Blocker | Perilaku DB hanya terverifikasi statis/unit |
| L2 | Tidak ada lingkungan Supabase development berizin | Blocker | Login/runtime, UAT browser, RLS belum diuji |
| L3 | Service-role key lama terekspos; rotasi belum dikonfirmasi | P0 | Risiko keamanan sampai dirotasi |
| L4 | Pemetaan output (`Sertifikasi MOS/MCF`, `Title Microsoft`) belum disetujui | ADR-003/006 | Ekspor final diblokir |
| L5 | Alias ujian masih `DRAFT` | ADR-005 | Semua alias → `PERLU_VERIFIKASI` |
| L6 | Kebijakan retensi/backup belum ditetapkan | ADR-007 | Larangan data asli di cloud |
| L7 | Kebijakan reviewer belum disahkan | ADR-009 | `KONFIRMASI_COCOK` staf dibatasi |
| L8 | Penanganan sel wisuda yang sudah terisi belum disahkan | ADR-010 | Larangan overwrite |
| L9 | Kriteria wajib sertifikasi per prodi belum ditetapkan | ADR-011 | Sistem tidak menyimpulkan kelulusan |
| L10 | Performa runtime (waktu proses, batas jumlah baris) belum diukur | Belum diukur | Angka performa tidak diklaim |
| L11 | Tabel `certification_aliases` belum dibuat | Rencana | Alias disimpan sebagai konstanta kode |
| L12 | Integrasi langsung API SITASI/Certiport | Di luar MVP | Sumber tetap via Excel |
| L13 | UAT & tanda tangan pengesahan belum ada | Belum | **BELUM SIAP PRODUCTION** |

---

## 8. Perintah pemeriksaan lokal

```powershell
# Backend
cd backend
.\venv\Scripts\python.exe -m pytest -q          # 134 test
# Frontend
cd frontend
npm run typecheck
npm run build
```
Catat versi commit, tanggal, dan hasil aktual setiap kali menjalankan — jangan menyalin hasil lama sebagai hasil baru.
