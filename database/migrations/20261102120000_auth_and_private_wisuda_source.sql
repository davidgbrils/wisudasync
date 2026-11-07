-- Jalankan hanya pada lingkungan development berizin setelah meninjau profil petugas.
-- Akun Auth baru tidak boleh otomatis mendapatkan profil staff/admin aktif.
begin;

drop trigger if exists on_auth_user_created on auth.users;
drop function if exists public.handle_new_user();

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'wisuda-source',
  'wisuda-source',
  false,
  10485760,
  array['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
)
on conflict (id) do update set
  public = false,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

commit;
