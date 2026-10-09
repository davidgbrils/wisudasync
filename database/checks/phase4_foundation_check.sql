-- Read-only checks for the Phase 4 foundation migration.

select
    required.object_name,
    to_regclass(required.object_name) is not null as exists
from (
    values
        ('public.profiles'),
        ('public.data_imports'),
        ('public.sitasi_data'),
        ('public.certiport_data')
) as required(object_name)
order by required.object_name;

select
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
from information_schema.columns
where table_schema = 'public'
  and table_name in ('profiles', 'data_imports', 'sitasi_data', 'certiport_data')
order by table_name, ordinal_position;

select
    conrelid::regclass as table_name,
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as definition
from pg_constraint
where conrelid in (
    'public.profiles'::regclass,
    'public.data_imports'::regclass,
    'public.sitasi_data'::regclass,
    'public.certiport_data'::regclass
)
order by table_name, constraint_name;

select
    schemaname,
    tablename,
    indexname,
    indexdef
from pg_indexes
where schemaname = 'public'
  and tablename in ('profiles', 'data_imports', 'sitasi_data', 'certiport_data')
order by tablename, indexname;

select
    n.nspname as schema_name,
    c.relname as table_name,
    c.relrowsecurity as rls_enabled,
    c.relforcerowsecurity as rls_forced
from pg_class as c
join pg_namespace as n on n.oid = c.relnamespace
where n.nspname = 'public'
  and c.relname in ('profiles', 'data_imports', 'sitasi_data', 'certiport_data')
order by c.relname;

select
    required.table_name,
    count(p.policyname) as policy_count
from (
    values
        ('profiles'),
        ('data_imports'),
        ('sitasi_data'),
        ('certiport_data')
) as required(table_name)
left join pg_policies as p
    on p.schemaname = 'public'
   and p.tablename = required.table_name
group by required.table_name
order by required.table_name;

select
    table_name,
    grantee,
    string_agg(privilege_type, ', ' order by privilege_type) as privileges
from information_schema.role_table_grants
where table_schema = 'public'
  and table_name in ('profiles', 'data_imports', 'sitasi_data', 'certiport_data')
  and grantee in ('PUBLIC', 'anon', 'authenticated', 'service_role')
group by table_name, grantee
order by table_name, grantee;

select
    to_regprocedure('public.complete_data_import(uuid,integer)') is not null
        as activation_function_exists,
    has_function_privilege(
        'anon',
        to_regprocedure('public.complete_data_import(uuid,integer)'),
        'EXECUTE'
    )
        as anon_can_execute,
    has_function_privilege(
        'authenticated',
        to_regprocedure('public.complete_data_import(uuid,integer)'),
        'EXECUTE'
    )
        as authenticated_can_execute,
    has_function_privilege(
        'service_role',
        to_regprocedure('public.complete_data_import(uuid,integer)'),
        'EXECUTE'
    )
        as service_role_can_execute;

select data_type, count(*) as active_batches
from public.data_imports
where is_active = true
group by data_type
having count(*) > 1;

select import_id, source_row, count(*) as duplicate_rows
from public.sitasi_data
group by import_id, source_row
having count(*) > 1;

select import_id, source_row, count(*) as duplicate_rows
from public.certiport_data
group by import_id, source_row
having count(*) > 1;
