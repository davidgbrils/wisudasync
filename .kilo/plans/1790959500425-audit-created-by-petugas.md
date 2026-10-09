# Tahap 08 — Isi jejak petugas pada batch import (`created_by`)

## Konteks

`data_imports.created_by uuid references auth.users(id) on delete set null`
sudah ada di `database/migrations/20260930120000_phase4_foundation.sql:30` dan sudah
diindeks, tetapi tidak pernah diisi. `import_master_data()` sudah menerima parameter
`created_by` (`backend/app/services/import_service.py:357`), namun
`backend/app/api/v1/endpoints/sitasi.py:33` dan `certiport.py:33` memanggilnya tanpa
principal sehingga kolom selalu `NULL`. Akibatnya tidak ada jejak siapa yang mengimpor
batch, padahal `docs/07_DATABASE_DESIGN.md:108` menetapkan `created_by` sebagai pemilik
kegiatan dan ADR-009 menuntut jejak keputusan yang accountable.

Fakta yang sudah diverifikasi, tidak perlu diuji ulang:
- FastAPI men-cache dependency per request, sehingga `Depends(require_staff)` di level
  router dan level route **dipanggil sekali**, bukan dua kali.
- `StaffPrincipal.user_id` berasal dari `supabase.auth.get_user().id`, yaitu UUID
  `auth.users`, sehingga FK `created_by` selalu valid.
- Hanya dua endpoint yang memanggil `import_master_data`; `sync.py` tidak membuat batch.

## Keputusan yang sudah ditetapkan

- `created_by` **tetap internal**; tidak masuk respons API dan tidak tampil di UI.
- Tidak ada migration baru, tidak ada perubahan schema, tidak ada perubahan kontrak
  bentuk respons.
- Tidak mengisi kolom output wisuda; tidak menyentuh parser, logika import, atau
  `core/auth.py`.

## Langkah implementasi

1. **`backend/app/api/v1/endpoints/sitasi.py`**
   - Ubah `import_sitasi` menjadi
     `def import_sitasi(file: UploadFile = File(...), principal: StaffPrincipal = Depends(require_staff))`.
   - Tambahkan import `StaffPrincipal` dari `app.core.auth`.
   - Teruskan `created_by=principal.user_id` ke `import_master_data`.
   - Dependency level router pada `sitasi.py:14` tetap ada untuk endpoint `/batch` dan
     `GET /sitasi`. Jangan dihapus.

2. **`backend/app/api/v1/endpoints/certiport.py`** — perubahan identik pada
   `import_certiport`.

3. **`backend/app/api/v1/endpoints/sync.py` — tidak berubah.** Endpoint `/sync/validate`
   hanya membaca workbook dan tidak membuat batch. Jangan tambahkan parameter principal.
   Perhatikan `backend/tests/test_wisuda_validation.py:104` meng-override
   `require_staff` dengan `lambda: object()`; itu aman selama `/sync/validate` tidak
   menyentuh `.user_id`.

4. **`backend/tests/test_import_service.py`**
   - Perbarui dua pemanggilan fungsi langsung yang tanda tangannya berubah:
     `test_sitasi_endpoint_returns_413_for_oversized_file` (sekitar baris 293) dan
     `test_sitasi_endpoint_hides_internal_storage_error` (sekitar baris 315).
     Tambahkan argumen `principal=SimpleNamespace(user_id="synthetic-user-id")`.
     Tanpa ini keduanya gagal `TypeError`.
   - Tambah `test_import_endpoint_records_staff_as_batch_owner`: patch
     `sitasi_endpoint.get_supabase` ke `FakeSupabase` yang sudah ada, panggil
     `import_sitasi(upload, principal=...)` dengan fixture anonim, lalu assert
     `supabase.imports[-1]["created_by"] == "synthetic-user-id"`.
   - Tambah test kompatibilitas: `import_master_data(..., created_by=None)` tetap
     menghasilkan `"created_by": None`, karena signature publik tidak berubah.

5. **Dokumentasi**
   - `docs/18_CHANGELOG.md`: entri baru "Tahap 08 jejak petugas pada batch import"
     di bawah blok Tahap 07.
   - `docs/19_AI_PROGRESS.md`: blok Tahap 08 berisi status, perubahan, hasil tes
     aktual, blocker (Supabase development belum berizin; rotasi service-role key
     menunggu pemilik), dan langkah "Berikutnya".
   - `docs/08_API_CONTRACT.md`: satu kalimat pada `/sitasi/import` dan
     `/certiport/import` bahwa batch menyimpan petugas pemroses secara internal dan
     kolom itu tidak dikembalikan ke browser.
   - `README.md`: frasa "Endpoint import belum memiliki auth" sudah usang karena guard
     `require_staff` sudah ada sejak Tahap 05. Koreksi satu baris tersebut menjadi
     acuan auth, tanpa mengubah kode aplikasi.

## Failure mode yang perlu diperhatikan

- Dua test lama memanggil `import_sitasi(upload)` tanpa principal. Signature berubah,
  keduanya harus diperbarui dalam commit yang sama.
- Jangan sampai `created_by` masuk respons. Bentuk respons import tetap
  `{success, message, data:{import_id, sheet_name, total_rows, imported_rows}}`.
- Jika migration `20260930120000` belum pernah dijalankan pada database target, kolom
  `created_by` belum ada dan insert akan gagal. Perilaku gagal-tertutup sudah ada:
  `_mark_failed` membersihkan batch staging dan batch aktif lama tetap utuh. Tidak perlu
  kode tambahan.
- Jangan ubah pemetaan error di `core/auth.py` atau `sync.py`; di luar scope.

## Validasi

Dari folder `backend`:

```powershell
.\venv\Scripts\python.exe -m pytest tests -q
git diff --check
```

Ekspektasi: seluruh test PASS (baseline tercatat 34, ditambah 2 test baru = 36),
tanpa kegagalan baru dan tanpa regression. Tidak ada perubahan frontend, sehingga
`npm run typecheck` dan `npm run build` tidak perlu dijalankan ulang kecuali
terjadi perubahan file frontend di luar rencana.

Test memakai `FakeSupabase`, sama seperti test importer yang sudah ada. Jangan menulis
klaim bahwa integrasi runtime Supabase sudah terverifikasi.

## Risiko dan di luar scope

- `created_by` berisi UUID petugas, bukan data mahasiswa, dan tidak pernah dikirim ke
  browser.
- Di luar scope dan tidak boleh disentuh: siapa yang berwenang mengesahkan review
  (ADR-009 masih TERBUKA), overwrite sel lama (ADR-010), alias ujian (ADR-005),
  kewajiban MOS/MCF (ADR-011), dan isi tiga kolom output wisuda (ADR-003). Mengisi
  `created_by` bukan persetujuan atas keputusan bisnis mana pun.
- Markdown non-ASCII pada plan ini perlu dibaca ulang bila implementing agent
  menemukan karakter aneh pada plan; jangan menyalin teks itu apa adanya ke komentar
  kode.