-- Trigger otomatis: Saat ada akun dibuat di auth.users, otomatis catat di public.profiles
-- Role default: staff, is_active: true

create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, display_name, role, is_active)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1)),
    'staff',
    true
  )
  on conflict (id) do update
  set display_name = coalesce(excluded.display_name, public.profiles.display_name);
  return new;
end;
$$ language plpgsql security definer;

-- Pasang trigger pada auth.users
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
