-- Phase 4 foundation: profiles, master import batches, source rows, indexes, and RLS.
-- Apply only to an authorized development database before production review.

begin;

create extension if not exists pgcrypto;

create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    display_name text,
    role text not null default 'staff'
        constraint profiles_role_allowed check (role in ('staff', 'admin')),
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.data_imports (
    id uuid primary key default gen_random_uuid(),
    data_type text not null
        constraint data_imports_data_type_allowed check (data_type in ('SITASI', 'CERTIPORT')),
    file_name text not null,
    sheet_name text,
    total_rows integer not null default 0,
    imported_rows integer not null default 0,
    status text not null default 'PROCESSING'
        constraint data_imports_status_allowed check (status in ('PROCESSING', 'COMPLETED', 'FAILED')),
    is_active boolean not null default false,
    error_message text,
    created_by uuid references auth.users(id) on delete set null,
    created_at timestamptz not null default now(),
    completed_at timestamptz,
    constraint data_imports_rows_nonnegative check (total_rows >= 0 and imported_rows >= 0),
    constraint data_imports_active_completed check (not is_active or status = 'COMPLETED')
);

create table if not exists public.sitasi_data (
    id bigint generated always as identity primary key,
    import_id uuid not null references public.data_imports(id) on delete cascade,
    source_row integer not null constraint sitasi_data_source_row_valid check (source_row >= 2),
    nim text,
    nama text,
    nama_normalized text,
    fakultas text,
    kode_nim text,
    program_studi text,
    angkatan text,
    sertifikasi text,
    sub_program text,
    nilai numeric,
    status text,
    created_at timestamptz not null default now(),
    constraint sitasi_data_import_source_unique unique (import_id, source_row)
);

create table if not exists public.certiport_data (
    id bigint generated always as identity primary key,
    import_id uuid not null references public.data_imports(id) on delete cascade,
    source_row integer not null constraint certiport_data_source_row_valid check (source_row >= 2),
    first_name text,
    last_name text,
    full_name text,
    full_name_normalized text,
    program_name text,
    certification_name text,
    score numeric,
    result text,
    created_at timestamptz not null default now(),
    constraint certiport_data_import_source_unique unique (import_id, source_row)
);

-- Tambahkan constraint baru saat migration diterapkan di atas schema starter lama.
do $$
begin
    if not exists (
        select 1 from pg_constraint
        where conname = 'data_imports_rows_nonnegative'
          and conrelid = 'public.data_imports'::regclass
    ) then
        alter table public.data_imports
            add constraint data_imports_rows_nonnegative
            check (total_rows >= 0 and imported_rows >= 0);
    end if;

    if not exists (
        select 1 from pg_constraint
        where conname = 'data_imports_active_completed'
          and conrelid = 'public.data_imports'::regclass
    ) then
        alter table public.data_imports
            add constraint data_imports_active_completed
            check (not is_active or status = 'COMPLETED');
    end if;

    if not exists (
        select 1 from pg_constraint
        where conname = 'sitasi_data_source_row_valid'
          and conrelid = 'public.sitasi_data'::regclass
    ) then
        alter table public.sitasi_data
            add constraint sitasi_data_source_row_valid check (source_row >= 2);
    end if;

    if not exists (
        select 1 from pg_constraint
        where conname = 'certiport_data_source_row_valid'
          and conrelid = 'public.certiport_data'::regclass
    ) then
        alter table public.certiport_data
            add constraint certiport_data_source_row_valid check (source_row >= 2);
    end if;
end
$$;

create index if not exists profiles_active_role_idx
    on public.profiles (role)
    where is_active = true;

create index if not exists data_imports_created_by_idx
    on public.data_imports (created_by);

create index if not exists data_imports_type_created_idx
    on public.data_imports (data_type, created_at desc);

create unique index if not exists data_imports_one_active_per_type_idx
    on public.data_imports (data_type)
    where is_active = true;

create index if not exists sitasi_data_import_nim_idx
    on public.sitasi_data (import_id, nim);

create index if not exists sitasi_data_import_name_idx
    on public.sitasi_data (import_id, nama_normalized);

create index if not exists sitasi_data_import_cert_status_idx
    on public.sitasi_data (import_id, sertifikasi, status);

create index if not exists certiport_data_import_name_idx
    on public.certiport_data (import_id, full_name_normalized);

create index if not exists certiport_data_import_program_result_idx
    on public.certiport_data (import_id, program_name, result);

-- Satu transaksi database menyelesaikan batch baru dan menonaktifkan batch lama.
create or replace function public.complete_data_import(
    p_import_id uuid,
    p_imported_rows integer
)
returns public.data_imports
language plpgsql
security invoker
set search_path = ''
as $$
declare
    target_import public.data_imports;
begin
    if p_imported_rows < 0 then
        raise exception 'imported_rows tidak boleh negatif';
    end if;

    select di.*
      into target_import
      from public.data_imports as di
     where di.id = p_import_id
     for update;

    if not found then
        raise exception 'Import batch tidak ditemukan';
    end if;

    if target_import.status = 'FAILED' then
        raise exception 'Import batch FAILED tidak dapat diaktifkan';
    end if;

    if target_import.total_rows <> p_imported_rows then
        raise exception 'Jumlah baris import tidak sesuai: expected %, received %',
            target_import.total_rows,
            p_imported_rows;
    end if;

    perform pg_advisory_xact_lock(hashtextextended(target_import.data_type, 0));

    update public.data_imports
       set is_active = false
     where data_type = target_import.data_type
       and is_active = true
       and id <> p_import_id;

    update public.data_imports
       set imported_rows = p_imported_rows,
           status = 'COMPLETED',
           is_active = true,
           error_message = null,
           completed_at = coalesce(completed_at, now())
     where id = p_import_id
     returning * into target_import;

    return target_import;
end;
$$;

alter table public.profiles enable row level security;
alter table public.data_imports enable row level security;
alter table public.sitasi_data enable row level security;
alter table public.certiport_data enable row level security;

revoke all on table public.profiles from public, anon, authenticated;
revoke all on table public.data_imports from public, anon, authenticated;
revoke all on table public.sitasi_data from public, anon, authenticated;
revoke all on table public.certiport_data from public, anon, authenticated;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.profiles to service_role;
grant select, insert, update, delete on table public.data_imports to service_role;
grant select, insert, update, delete on table public.sitasi_data to service_role;
grant select, insert, update, delete on table public.certiport_data to service_role;
grant usage, select on sequence public.sitasi_data_id_seq to service_role;
grant usage, select on sequence public.certiport_data_id_seq to service_role;

revoke execute on function public.complete_data_import(uuid, integer)
    from public, anon, authenticated;
grant execute on function public.complete_data_import(uuid, integer)
    to service_role;

commit;
