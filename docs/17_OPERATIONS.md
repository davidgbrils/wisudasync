# 17 — Panduan Operasional dan Setup Lokal

Dokumen ini dipakai sesudah kode Phase 4 starter digabungkan dengan project Next.js lengkap. **Paket dokumen tidak otomatis membuat aplikasi yang sudah selesai.**

## 1. Prasyarat
- Python versi kompatibel dengan dependencies yang dipilih serta Node.js versi yang didukung Next.js terpasang.
- Proyek Supabase development sendiri dengan kredensial server yang dirahasiakan.
- Data Excel dummy; izin institusi jika menggunakan file asli.
- Aplikasi terminal/VS Code.

## 2. Persiapan backend
Pada source code Phase 4:
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Isi `.env` dengan `SUPABASE_URL`, server secret/service-role key, dan origin frontend. Jangan commit `.env`.

Jalankan:
```powershell
uvicorn app.main:app --reload
```
Akses `http://localhost:8000/docs` atau `http://localhost:8000/api/v1/health`.

### Autentikasi dan pembuatan petugas pertama
1. Di Supabase development yang disetujui, matikan public signups pada pengaturan Auth. Buat/invite akun petugas melalui Dashboard Auth; jangan membuat endpoint signup publik.
2. Salin UUID akun dari Dashboard. Dengan akun database administrator melalui SQL Editor development yang berizin, masukkan UUID itu ke `public.profiles` dengan role minimum `staff` dan `is_active = true`:

   ```sql
   insert into public.profiles (id, display_name, role, is_active)
   values ('<UUID_AUTH_USER>'::uuid, 'Petugas ITCC', 'staff', true);
   ```

3. Tetapkan `admin` hanya kepada pemilik/petugas yang secara resmi disetujui. Jangan memakai `user_metadata` sebagai sumber hak akses dan jangan membuat bootstrap endpoint.
4. Simpan `NEXT_PUBLIC_SUPABASE_URL` dan publishable key di `frontend/.env.local`; nilainya memang publik. `SUPABASE_SERVICE_ROLE_KEY` hanya di `backend/.env`, tidak dikirim ke browser atau log.

Endpoint SITASI/Certiport kini memerlukan bearer token valid dan profil petugas aktif. `GET /api/v1/health` tetap publik. RLS/grants membatasi akses langsung dari role browser; pribadi hanya diambil FastAPI. Tetap gunakan development dan data dummy sampai izin cloud/retensi/UAT disetujui.

## 3. Database
Pada lingkungan development, review dan jalankan `database/migrations/20260930120000_phase4_foundation.sql`, lalu jalankan `database/checks/phase4_foundation_check.sql`. Verifikasi `profiles`, `data_imports`, `sitasi_data`, `certiport_data`, indeks, RLS, grants, dan fungsi aktivasi batch. Gunakan migration baru untuk `sync_sessions` dan tabel terkait saat Phase 5.

## 4. Frontend
Salin `frontend/.env.example` menjadi `frontend/.env.local` dan isi URL FastAPI serta URL/publishable key Supabase. Jalankan `npm ci` lalu `npm run dev` dari `frontend`. Publishable key boleh berada di client; service-role key dan secret lain tidak.

## 5. Alur operator setelah fitur selesai
1. Login sebagai petugas resmi.
2. Periksa batch SITASI/Certiport aktif dan waktu pengunggahannya.
3. Impor sumber baru bila memang lebih mutakhir dan sudah benar.
4. Unggah daftar wisuda, baca hasil validasi input.
5. Jalankan matching.
6. Tinjau **PERLU_VERIFIKASI** dan konflik; buat catatan.
7. Setelah mapping output disetujui, unduh hasil Excel dan cek beberapa baris sampel.
8. Catat nomor sesi, tanggal, dan nama file sesuai prosedur institusi.

## 6. Masalah umum
| Masalah | Pemeriksaan |
|---|---|
| API tidak dapat diakses | Backend running? port 8000? nilai frontend URL? |
| CORS | Origin Next.js cocok konfigurasi backend? CORS bukan pengganti auth |
| 401/403 | Access token valid? user mendapat izin petugas? |
| Header tidak ditemukan | Sheet/header file sesuai data dictionary? |
| Angka NIM jadi `...0` | Periksa tipe sel dan normalisasi; jangan langsung cast ke float |
| Hasil kosong | Ada batch master aktif? query memakai `import_id` sesuai? |
| Kandidat tidak cocok | Cek nama normalisasi, kategori dan alias ujian, jangan mengubah langsung menjadi VALID |
| Import gagal saat aktivasi | Periksa transaksi batch dan unique index partial |
| Export berubah format | Pastikan OpenPyXL mengubah salinan input, bukan DataFrame baru |

## 7. Perawatan dan pengamanan
- Backup data sesuai kebijakan resmi, bukan berdasarkan asumsi.
- Uji migrasi pada dev sebelum production.
- Putar kredensial bila bocor; jangan pernah memublikasikan service-role key.
- Ukur performa dengan dataset dummy dan jumlah row riil tanpa mengekspos identitas.
- Perbarui dokumentasi dan hasil uji setiap ada perubahan aturan bisnis.
