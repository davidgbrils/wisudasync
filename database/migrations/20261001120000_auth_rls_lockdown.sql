-- Tegaskan akses data hanya melalui FastAPI dengan service_role.
-- Terapkan dahulu pada Supabase development berizin; jangan jalankan langsung di production.

begin;

alter table public.profiles enable row level security;
alter table public.data_imports enable row level security;
alter table public.sitasi_data enable row level security;
alter table public.certiport_data enable row level security;

revoke all on table public.profiles from public, anon, authenticated;
revoke all on table public.data_imports from public, anon, authenticated;
revoke all on table public.sitasi_data from public, anon, authenticated;
revoke all on table public.certiport_data from public, anon, authenticated;
revoke all on sequence public.sitasi_data_id_seq from public, anon, authenticated;
revoke all on sequence public.certiport_data_id_seq from public, anon, authenticated;
revoke execute on function public.complete_data_import(uuid, integer)
    from public, anon, authenticated;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.profiles to service_role;
grant select, insert, update, delete on table public.data_imports to service_role;
grant select, insert, update, delete on table public.sitasi_data to service_role;
grant select, insert, update, delete on table public.certiport_data to service_role;
grant usage, select on sequence public.sitasi_data_id_seq to service_role;
grant usage, select on sequence public.certiport_data_id_seq to service_role;
grant execute on function public.complete_data_import(uuid, integer) to service_role;

commit;
