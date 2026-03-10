create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text,
  avatar_url text,
  provider text,
  raw_user_meta_data jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  last_sign_in_at timestamptz
);

create table if not exists public.marketing_events (
  id uuid primary key default extensions.gen_random_uuid(),
  created_at timestamptz not null default timezone('utc', now()),
  user_id uuid references auth.users(id) on delete set null,
  session_id text not null,
  event_name text not null,
  page_path text not null,
  page_key text,
  landing_variant text,
  referrer text,
  utm_source text,
  utm_medium text,
  utm_campaign text,
  utm_term text,
  utm_content text,
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists marketing_events_created_at_idx
  on public.marketing_events (created_at desc);

create index if not exists marketing_events_event_name_idx
  on public.marketing_events (event_name);

create index if not exists marketing_events_session_id_idx
  on public.marketing_events (session_id);

create index if not exists marketing_events_user_id_idx
  on public.marketing_events (user_id);

create index if not exists marketing_events_utm_campaign_idx
  on public.marketing_events (utm_campaign);

create or replace function public.set_profile_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

drop trigger if exists set_profiles_updated_at on public.profiles;
create trigger set_profiles_updated_at
before update on public.profiles
for each row
execute function public.set_profile_updated_at();

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (
    id,
    email,
    display_name,
    avatar_url,
    provider,
    raw_user_meta_data,
    created_at,
    updated_at,
    last_sign_in_at
  )
  values (
    new.id,
    new.email,
    coalesce(
      new.raw_user_meta_data ->> 'name',
      new.raw_user_meta_data ->> 'full_name',
      new.raw_user_meta_data ->> 'user_name',
      split_part(coalesce(new.email, ''), '@', 1)
    ),
    new.raw_user_meta_data ->> 'avatar_url',
    new.raw_app_meta_data ->> 'provider',
    coalesce(new.raw_user_meta_data, '{}'::jsonb),
    coalesce(new.created_at, timezone('utc', now())),
    timezone('utc', now()),
    new.last_sign_in_at
  )
  on conflict (id) do update
  set
    email = excluded.email,
    display_name = excluded.display_name,
    avatar_url = excluded.avatar_url,
    provider = excluded.provider,
    raw_user_meta_data = excluded.raw_user_meta_data,
    updated_at = timezone('utc', now()),
    last_sign_in_at = excluded.last_sign_in_at;

  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row
execute function public.handle_new_user();

drop trigger if exists on_auth_user_updated on auth.users;
create trigger on_auth_user_updated
after update of email, raw_user_meta_data, raw_app_meta_data, last_sign_in_at on auth.users
for each row
execute function public.handle_new_user();

alter table public.profiles enable row level security;
alter table public.marketing_events enable row level security;

drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own"
on public.profiles
for select
to authenticated
using ((select auth.uid()) = id);

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own"
on public.profiles
for update
to authenticated
using ((select auth.uid()) = id)
with check ((select auth.uid()) = id);

drop policy if exists "profiles_insert_own" on public.profiles;
create policy "profiles_insert_own"
on public.profiles
for insert
to authenticated
with check ((select auth.uid()) = id);

drop policy if exists "marketing_events_insert" on public.marketing_events;
create policy "marketing_events_insert"
on public.marketing_events
for insert
to anon, authenticated
with check (user_id is null or user_id = (select auth.uid()));

insert into public.profiles (
  id,
  email,
  display_name,
  avatar_url,
  provider,
  raw_user_meta_data,
  created_at,
  updated_at,
  last_sign_in_at
)
select
  users.id,
  users.email,
  coalesce(
    users.raw_user_meta_data ->> 'name',
    users.raw_user_meta_data ->> 'full_name',
    users.raw_user_meta_data ->> 'user_name',
    split_part(coalesce(users.email, ''), '@', 1)
  ),
  users.raw_user_meta_data ->> 'avatar_url',
  users.raw_app_meta_data ->> 'provider',
  coalesce(users.raw_user_meta_data, '{}'::jsonb),
  coalesce(users.created_at, timezone('utc', now())),
  timezone('utc', now()),
  users.last_sign_in_at
from auth.users as users
on conflict (id) do update
set
  email = excluded.email,
  display_name = excluded.display_name,
  avatar_url = excluded.avatar_url,
  provider = excluded.provider,
  raw_user_meta_data = excluded.raw_user_meta_data,
  updated_at = timezone('utc', now()),
  last_sign_in_at = excluded.last_sign_in_at;
