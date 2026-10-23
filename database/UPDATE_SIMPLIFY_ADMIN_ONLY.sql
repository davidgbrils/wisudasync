-- ============================================================================
-- ITCC WISUDA SYNC: PEMBARUAN PENYEDERHANAAN (ADMIN ONLY & TANPA LOGIN/REGISTER)
-- Salin dan tempel (copy-paste) seluruh isi skrip ini ke:
-- Supabase Dashboard -> SQL Editor -> Klik "Run"
-- Proyek: ocdyjdsvekewbicfskxg.supabase.co
-- ============================================================================

-- 1. Lepaskan foreign key ke auth.users agar operasi data tidak wajib memiliki akun Supabase Auth
alter table if exists public.profiles drop constraint if exists profiles_id_fkey;
alter table if exists public.data_imports drop constraint if exists data_imports_created_by_fkey;
alter table if exists public.sync_sessions drop constraint if exists sync_sessions_created_by_fkey;
alter table if exists public.review_audit drop constraint if exists review_audit_reviewed_by_fkey;

-- 2. Perbarui seluruh profil pengguna menjadi role 'admin'
update public.profiles set role = 'admin' where role <> 'admin';

-- 3. Batasi role profiles hanya untuk 'admin' (role lain seperti staff ditiadakan)
alter table public.profiles drop constraint if exists profiles_role_allowed;
alter table public.profiles add constraint profiles_role_allowed check (role in ('admin'));
alter table public.profiles alter column role set default 'admin';

-- 4. Pastikan kolom program studi tersedia di tabel sync_results (jika belum ada)
alter table public.sync_results add column if not exists kode_prodi text;
alter table public.sync_results add column if not exists program_studi text;

-- 5. Hapus trigger dan fungsi registrasi otomatis dari auth.users (fitur registrasi dihapus)
drop trigger if exists on_auth_user_created on auth.users;
drop function if exists public.handle_new_user();

-- 6. Tambahkan profil Administrator ITCC default jika belum ada
insert into public.profiles (id, display_name, role, is_active)
values ('00000000-0000-0000-0000-000000000001', 'Administrator ITCC', 'admin', true)
on conflict (id) do update set role = 'admin', is_active = true;

-- 7. Pastikan hak akses service_role tetap lengkap untuk seluruh tabel
grant usage on schema public to service_role;
grant select, insert, update, delete on all tables in schema public to service_role;
grant usage, select on all sequences in schema public to service_role;

-- 8. Refresh schema cache Supabase PostgREST
notify pgrst, 'reload schema';

-- Pesan konfirmasi
select 'Pembaruan schema Supabase selesai. Sistem kini Admin-Only tanpa batasan login/register.' as status;
