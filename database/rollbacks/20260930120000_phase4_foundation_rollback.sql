-- Development-only rollback. It aborts before dropping anything when data exists.

begin;

do $$
begin
    if exists (select 1 from public.sitasi_data limit 1)
       or exists (select 1 from public.certiport_data limit 1)
       or exists (select 1 from public.data_imports limit 1)
       or exists (select 1 from public.profiles limit 1) then
        raise exception using
            message = 'Rollback dibatalkan: tabel Phase 4 masih berisi data.',
            hint = 'Gunakan backup dan prosedur migrasi data yang disetujui; jangan memakai rollback development ini.';
    end if;
end
$$;

drop function if exists public.complete_data_import(uuid, integer);
drop table if exists public.certiport_data;
drop table if exists public.sitasi_data;
drop table if exists public.data_imports;
drop table if exists public.profiles;

commit;
