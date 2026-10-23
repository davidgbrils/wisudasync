-- ============================================================================
-- ITCC WISUDA SYNC - SETUP SEMUA TABEL, RLS, TRIGGER & AKUN AWAL
-- Jalankan skrip ini sekali di Supabase Dashboard -> SQL Editor
-- Proyek: ocdyjdsvekewbicfskxg.supabase.co
-- ============================================================================

create extension if not exists pgcrypto;

-- 1. TABEL PROFILES (Akun Administrator)
create table if not exists public.profiles (
    id uuid primary key default gen_random_uuid(),
    display_name text,
    role text not null default 'admin'
        constraint profiles_role_allowed check (role in ('admin')),
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- 2. TABEL DATA_IMPORTS (Batch Unggahan SITASI & Certiport)
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
    created_by uuid,
    created_at timestamptz not null default now(),
    completed_at timestamptz,
    constraint data_imports_rows_nonnegative check (total_rows >= 0 and imported_rows >= 0),
    constraint data_imports_active_completed check (not is_active or status = 'COMPLETED')
);

-- 3. TABEL SITASI_DATA
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

-- 4. TABEL CERTIPORT_DATA
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

-- 5. TABEL SYNC_SESSIONS
create table if not exists public.sync_sessions (
    id uuid primary key default gen_random_uuid(),
    created_by uuid,
    file_name text not null,
    original_file_path text,
    output_file_path text,
    sitasi_import_id uuid not null references public.data_imports(id) on delete restrict,
    certiport_import_id uuid not null references public.data_imports(id) on delete restrict,
    total_rows integer not null default 0,
    total_valid integer not null default 0,
    total_review integer not null default 0,
    total_not_found integer not null default 0,
    status text not null default 'UPLOADED'
        constraint sync_sessions_status_allowed check (status in ('UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED')),
    error_message text,
    created_at timestamptz not null default now(),
    completed_at timestamptz,
    constraint sync_sessions_totals_nonnegative check (
        total_rows >= 0 and total_valid >= 0 and total_review >= 0 and total_not_found >= 0
    )
);

-- 6. TABEL SYNC_RESULTS
create table if not exists public.sync_results (
    id uuid primary key default gen_random_uuid(),
    sync_session_id uuid not null references public.sync_sessions(id) on delete cascade,
    source_row integer not null constraint sync_results_source_row_valid check (source_row >= 2),
    nim text not null,
    nama_wisuda text not null,
    kode_prodi text,
    program_studi text,
    nama_sitasi text,
    name_match_type text,
    mos_status text,
    mcf_status text,
    mos_programs jsonb,
    mcf_programs jsonb,
    validation_status text not null,
    needs_review boolean not null default false,
    review_note text,
    created_at timestamptz not null default now(),
    constraint sync_results_session_source_unique unique (sync_session_id, source_row)
);

-- 7. TABEL SYNC_EVIDENCE
create table if not exists public.sync_evidence (
    id uuid primary key default gen_random_uuid(),
    result_id uuid not null references public.sync_results(id) on delete cascade,
    category text,
    exam text,
    sitasi_row_id bigint references public.sitasi_data(id) on delete set null,
    certiport_row_id bigint references public.certiport_data(id) on delete set null,
    match_method text,
    match_score numeric,
    evidence_status text,
    reason text,
    created_at timestamptz not null default now()
);

-- 8. TABEL REVIEW_AUDIT
create table if not exists public.review_audit (
    id uuid primary key default gen_random_uuid(),
    result_id uuid not null references public.sync_results(id) on delete cascade,
    reviewed_by uuid,
    reviewer_name text,
    decision text not null
        constraint review_audit_decision_allowed check (
            decision in ('KONFIRMASI_COCOK', 'TIDAK_COCOK', 'TUNDA_VERIFIKASI', 'PENDING_APPROVAL')
        ),
    note text not null,
    previous_status text not null,
    new_status text not null,
    created_at timestamptz not null default now()
);

-- INDEKS
create index if not exists profiles_active_role_idx on public.profiles (role) where is_active = true;
create index if not exists data_imports_created_by_idx on public.data_imports (created_by);
create index if not exists data_imports_type_created_idx on public.data_imports (data_type, created_at desc);
create unique index if not exists data_imports_one_active_per_type_idx on public.data_imports (data_type) where is_active = true;
create index if not exists sitasi_data_import_nim_idx on public.sitasi_data (import_id, nim);
create index if not exists sitasi_data_import_name_idx on public.sitasi_data (import_id, nama_normalized);
create index if not exists sitasi_data_import_cert_status_idx on public.sitasi_data (import_id, sertifikasi, status);
create index if not exists certiport_data_import_name_idx on public.certiport_data (import_id, full_name_normalized);
create index if not exists certiport_data_import_program_result_idx on public.certiport_data (import_id, program_name, result);
create index if not exists sync_sessions_created_at_idx on public.sync_sessions (created_at desc);
create index if not exists sync_sessions_status_idx on public.sync_sessions (status);
create index if not exists sync_results_session_validation_idx on public.sync_results (sync_session_id, validation_status);
create index if not exists sync_results_session_nim_idx on public.sync_results (sync_session_id, nim);
create index if not exists sync_evidence_result_id_idx on public.sync_evidence (result_id);
create index if not exists review_audit_result_id_idx on public.review_audit (result_id, created_at desc);

-- FUNGSI AKTIVASI BATCH ATOMIK
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

-- RLS & HAK AKSES SERVICE_ROLE
alter table public.profiles enable row level security;
alter table public.data_imports enable row level security;
alter table public.sitasi_data enable row level security;
alter table public.certiport_data enable row level security;
alter table public.sync_sessions enable row level security;
alter table public.sync_results enable row level security;
alter table public.sync_evidence enable row level security;
alter table public.review_audit enable row level security;

revoke all on table public.profiles from public, anon, authenticated;
revoke all on table public.data_imports from public, anon, authenticated;
revoke all on table public.sitasi_data from public, anon, authenticated;
revoke all on table public.certiport_data from public, anon, authenticated;
revoke all on table public.sync_sessions from public, anon, authenticated;
revoke all on table public.sync_results from public, anon, authenticated;
revoke all on table public.sync_evidence from public, anon, authenticated;
revoke all on table public.review_audit from public, anon, authenticated;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.profiles to service_role;
grant select, insert, update, delete on table public.data_imports to service_role;
grant select, insert, update, delete on table public.sitasi_data to service_role;
grant select, insert, update, delete on table public.certiport_data to service_role;
grant select, insert, update, delete on table public.sync_sessions to service_role;
grant select, insert, update, delete on table public.sync_results to service_role;
grant select, insert, update, delete on table public.sync_evidence to service_role;
grant select, insert, update, delete on table public.review_audit to service_role;
grant usage, select on all sequences in schema public to service_role;
grant execute on function public.complete_data_import(uuid, integer) to service_role;

-- PROFIL ADMINISTRATOR DEFAULT (Sistem Admin-Only tanpa batasan registrasi)
insert into public.profiles (id, display_name, role, is_active)
values ('00000000-0000-0000-0000-000000000001', 'Administrator ITCC', 'admin', true)
on conflict (id) do update set role = 'admin', is_active = true;

-- REFRESH SCHEMA CACHE SUPABASE POSTGREST
notify pgrst, 'reload schema';
