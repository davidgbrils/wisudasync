-- Migration: review_audit table for Tahap 12.
-- Sesuai docs/07_DATABASE_DESIGN.md dan ADR-009.
-- Terapkan pada Supabase development berizin.

begin;

create table if not exists public.review_audit (
    id uuid primary key default gen_random_uuid(),
    result_id uuid not null references public.sync_results(id) on delete cascade,
    reviewed_by uuid references auth.users(id) on delete set null,
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

create index if not exists review_audit_result_id_idx
    on public.review_audit (result_id, created_at desc);

-- RLS deny-by-default, akses hanya melalui service_role backend
alter table public.review_audit enable row level security;

revoke all on table public.review_audit from public, anon, authenticated;

grant select, insert, update, delete on table public.review_audit to service_role;

commit;
