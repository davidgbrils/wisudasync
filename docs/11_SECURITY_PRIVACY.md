# 11 — Keamanan, Akses dan Privasi Data

## 1. Sensitivitas data
NIM, nama, program studi, status sertifikasi dan hasil ujian adalah data pribadi/akademik. Gunakan hanya untuk keperluan resmi yang diizinkan; kebijakan retensi, akses institusional, dan penggunaan platform cloud harus disetujui penanggung jawab data.

## 2. Model akses MVP
- **Petugas ITCC yang diizinkan:** akses login, data master, sinkronisasi, review dan export sesuai persetujuan organisasi.
- **Pengunjung anonim:** tidak dapat membaca/unggah/mengunduh data mahasiswa.
- **Backend FastAPI:** memproses perintah atas nama user yang telah terverifikasi dan terotorisasi.
- **Admin teknis cloud:** akses infrastruktur dibatasi, credential tidak disebar.

Satu aktor aplikasi tetap dapat dibatasi melalui allowlist email/ID user resmi atau tabel profiles yang dikontrol server. Status `authenticated` saja **tidak cukup** untuk menyatakan user merupakan petugas ITCC.

## 3. Implementasi kontrol pada Tahap 05
- FastAPI meminta bearer token, memvalidasinya melalui Supabase Auth, lalu membaca profil aktif/role dari `public.profiles` memakai server client. `user_metadata` tidak digunakan.
- `/sitasi`, `/certiport`, dan `/auth/me` dibatasi untuk `staff`/`admin`; `/health` tetap publik. Supabase Auth memvalidasi access token dengan konfigurasi project (signature, issuer, audience).
- Tabel publik memiliki RLS aktif, tanpa grant/policy untuk browser `anon`/`authenticated`; akses tabel diberikan ke service role server saja.
- Frontend memuat sesi Supabase cookie, melindungi navigasi, dan menambah access token ke request FastAPI. Guard frontend bukan pengganti pemeriksaan backend.
- Uji ini berbasis fixture sintetis; belum membuktikan konfigurasi Auth/RLS pada project Supabase development.

## 4. Kontrol wajib sebelum memakai data asli pada cloud
1. Konfirmasi izin pengelolaan/unggah data dari ITCC/BAA.
2. Lindungi endpoint dengan JWT yang tervalidasi + cek daftar petugas berhak.
3. Kunci secret key di `.env` server, jangan pernah beri prefix `NEXT_PUBLIC_`.
4. Aktifkan RLS pada tabel schema publik dan atur grants sesuai kebutuhan; tidak membuat policy `USING (true)` untuk data mahasiswa.
5. Gunakan HTTPS untuk frontend/backend pada deployment.
6. Beri batas ukuran file, ekstensi `.xlsx`, dan validasi isi workbook; tangani parsing error.
7. Jika memakai Supabase Storage, bucket **private**, bukan public, dengan aturan akses server-side yang jelas.
8. Jangan log seluruh row NIM/nama atau menampilkan stack trace berisi data ke client.
9. Jangan menaruh file Excel asli, service keys atau hasil output di repository/GitHub.
10. Siapkan mekanisme penghapusan/retensi setelah jangka waktu yang disetujui institusi.

## 5. Keamanan Excel
- Jangan memperlakukan teks hasil input sebagai formula Excel jika karakter awal `=`, `+`, `-`, `@` pada data eksternal memunculkan risiko formula injection; tulis sebagai string literal jika perlu.
- Batasi/matikan pengolahan macro; `.xlsx` bukan `.xlsm` dalam MVP.
- Pertahankan formula non-target asli tanpa mengevaluasi formula yang tidak dikenal pada server.
- Jangan membuka URL tertanam atau mengaktifkan konten eksternal dari workbook.

## 6. Keamanan session dan audit
- Token tidak dicetak ke log.
- Tidak memutuskan izin menggunakan field `user_metadata` yang mudah diedit pengguna.
- `review_audit` append-only mencatat siapa mengubah keputusan dan kapan.
- Daftar data dan file ekspor hanya dapat dibaca petugas sesuai wewenang.
- Lindungi hasil download dengan otorisasi `session_id` dan validasi relasi kepemilikan/akses, bukan sekadar URL UUID.

## 7. Prinsip minimisasi dan penyimpanan
Simpan data yang diperlukan untuk matching, review dan penelusuran. Pisahkan backup/temp file dari direktori yang diekspos web. Tanggal retensi **belum diputuskan**; hindari mengarang 30/90 hari sebagai kewajiban. Perlu keputusan pembimbing untuk retensi, backup, dan siapa yang dapat menghapus batch.

## 8. Checklist audit sebelum demo
- [ ] Endpoint tanpa token mengembalikan 401.
- [ ] Akun tidak berizin mendapatkan 403.
- [ ] Bucket hasil Excel tidak public.
- [ ] `.env`/secret tidak ada dalam Git history.
- [ ] Data tes di presentasi telah dianonimkan.
- [ ] Tidak ada endpoint debug yang menampilkan seluruh master bebas akses.
- [ ] Perubahan keputusan review tercatat di audit.

## 9. Referensi teknis
- https://supabase.com/docs/guides/database/postgres/row-level-security
- https://supabase.com/docs/guides/auth
- https://supabase.com/docs/guides/storage/security/access-control

Dokumen ini merupakan arahan desain keamanan sistem, bukan opini hukum tentang seluruh kewajiban kepatuhan institusi.
