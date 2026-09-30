-- Phase 4: Data Master SITASI & Certiport
-- Jalankan di Supabase SQL Editor atau simpan sebagai migration.

create extension if not exists pgcrypto;

create table if not exists public.data_imports (
    id uuid primary key default gen_random_uuid(),
    data_type text not null check (data_type in ('SITASI', 'CERTIPORT')),
    file_name text not null,
    sheet_name text,
    total_rows integer not null default 0,
    imported_rows integer not null default 0,
    status text not null default 'PROCESSING'
        check (status in ('PROCESSING', 'COMPLETED', 'FAILED')),
    is_active boolean not null default false,
    error_message text,
    created_by uuid references auth.users(id) on delete set null,
    created_at timestamptz not null default now(),
    completed_at timestamptz
);

create table if not exists public.sitasi_data (
    id bigint generated always as identity primary key,
    import_id uuid not null references public.data_imports(id) on delete cascade,
    source_row integer not null,
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
    unique(import_id, source_row)
);

create table if not exists public.certiport_data (
    id bigint generated always as identity primary key,
    import_id uuid not null references public.data_imports(id) on delete cascade,
    source_row integer not null,
    first_name text,
    last_name text,
    full_name text,
    full_name_normalized text,
    program_name text,
    certification_name text,
    score numeric,
    result text,
    created_at timestamptz not null default now(),
    unique(import_id, source_row)
);

-- Index yang dibutuhkan nanti oleh matching engine.
create index if not exists idx_data_imports_active
    on public.data_imports(data_type, is_active, created_at desc);

-- Hanya satu batch aktif untuk setiap jenis data master.
create unique index if not exists uq_data_imports_one_active_per_type
    on public.data_imports(data_type)
    where is_active = true;

create index if not exists idx_sitasi_import
    on public.sitasi_data(import_id);
create index if not exists idx_sitasi_nim
    on public.sitasi_data(nim);
create index if not exists idx_sitasi_name_normalized
    on public.sitasi_data(nama_normalized);
create index if not exists idx_sitasi_cert_status
    on public.sitasi_data(sertifikasi, status);

create index if not exists idx_certiport_import
    on public.certiport_data(import_id);
create index if not exists idx_certiport_name_normalized
    on public.certiport_data(full_name_normalized);
create index if not exists idx_certiport_program_result
    on public.certiport_data(program_name, result);

-- Data master hanya diakses melalui FastAPI dengan server secret/service key.
-- Browser tidak diberi akses langsung ke tabel ini.
alter table public.data_imports enable row level security;
alter table public.sitasi_data enable row level security;
alter table public.certiport_data enable row level security;

revoke all on table public.data_imports from anon, authenticated;
revoke all on table public.sitasi_data from anon, authenticated;
revoke all on table public.certiport_data from anon, authenticated;

-- Pastikan backend server tetap dapat mengakses tabel melalui service_role.
grant select, insert, update, delete on table public.data_imports to service_role;
grant select, insert, update, delete on table public.sitasi_data to service_role;
grant select, insert, update, delete on table public.certiport_data to service_role;
grant usage, select on all sequences in schema public to service_role;
