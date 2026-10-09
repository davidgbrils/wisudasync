# Database Phase 4

Folder ini memakai migration SQL imperatif. Jangan jalankan migration atau rollback ke production tanpa izin, backup, dan review ITCC.

## File

- `migrations/20260930120000_phase4_foundation.sql`: schema fondasi Phase 4.
- `checks/phase4_foundation_check.sql`: query pemeriksaan read-only.
- `rollbacks/20260930120000_phase4_foundation_rollback.sql`: rollback development yang berhenti bila tabel berisi data.

Migration hanya membuat `profiles`, `data_imports`, `sitasi_data`, dan `certiport_data`. Tabel sesi, hasil sinkronisasi, bukti, review, dan export belum dibuat.

## Menjalankan pada database development berizin

Simpan connection string pada environment variable PowerShell. Jangan menulis credential di command history atau repository.

```powershell
$env:DATABASE_URL = '<connection-string-development>'
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f database/migrations/20260930120000_phase4_foundation.sql
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f database/checks/phase4_foundation_check.sql
```

Hasil pemeriksaan yang diharapkan:

- Empat tabel tersedia dan RLS aktif.
- Tidak ada policy browser; `anon` dan `authenticated` tidak mempunyai grant tabel.
- `service_role` mempunyai akses tabel dan fungsi aktivasi batch.
- Query duplikat batch aktif serta `(import_id, source_row)` mengembalikan nol baris.

## Rollback development

Rollback hanya untuk database development kosong. Script memeriksa seluruh tabel lebih dahulu dan membatalkan transaksi jika satu baris pun ditemukan. Script tidak memakai `CASCADE`, sehingga dependency lain juga akan menghentikan penghapusan.

```powershell
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f database/rollbacks/20260930120000_phase4_foundation_rollback.sql
```
