-- Migration: sync_sessions, sync_results, and sync_evidence for Tahap 11.
-- Sesuai docs/07_DATABASE_DESIGN.md.
-- Terapkan pada Supabase development berizin.

begin;

create table if not exists public.sync_sessions (
    id uuid primary key default gen_random_uuid(),
    created_by uuid references auth.users(id) on delete set null,
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

create table if not exists public.sync_results (
    id uuid primary key default gen_random_uuid(),
    sync_session_id uuid not null references public.sync_sessions(id) on delete cascade,
    source_row integer not null constraint sync_results_source_row_valid check (source_row >= 2),
    nim text not null,
    nama_wisuda text not null,
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

-- Indeks performa pencarian dan filter
create index if not exists sync_sessions_created_at_idx
    on public.sync_sessions (created_at desc);

create index if not exists sync_sessions_status_idx
    on public.sync_sessions (status);

create index if not exists sync_results_session_validation_idx
    on public.sync_results (sync_session_id, validation_status);

create index if not exists sync_results_session_nim_idx
    on public.sync_results (sync_session_id, nim);

create index if not exists sync_evidence_result_id_idx
    on public.sync_evidence (result_id);

-- RLS deny-by-default, akses hanya melalui service_role backend
alter table public.sync_sessions enable row level security;
alter table public.sync_results enable row level security;
alter table public.sync_evidence enable row level security;

revoke all on table public.sync_sessions from public, anon, authenticated;
revoke all on table public.sync_results from public, anon, authenticated;
revoke all on table public.sync_evidence from public, anon, authenticated;

grant select, insert, update, delete on table public.sync_sessions to service_role;
grant select, insert, update, delete on table public.sync_results to service_role;
grant select, insert, update, delete on table public.sync_evidence to service_role;

commit;
