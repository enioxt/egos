-- GH-077: Gem Hunter Community Voting Tables
-- gem_hunter_gems PK is url (text)
-- Applied: 2026-04-08

alter table gem_hunter_gems add column if not exists vote_count int not null default 0;

create table if not exists gem_lists (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text unique not null,
  description text,
  owner_id uuid references auth.users(id) on delete cascade,
  is_public boolean not null default true,
  gem_count int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists gem_list_items (
  id uuid primary key default gen_random_uuid(),
  list_id uuid not null references gem_lists(id) on delete cascade,
  gem_url text not null references gem_hunter_gems(url) on delete cascade,
  note text,
  added_at timestamptz not null default now(),
  unique(list_id, gem_url)
);

create table if not exists gem_votes (
  id uuid primary key default gen_random_uuid(),
  gem_url text not null references gem_hunter_gems(url) on delete cascade,
  user_id uuid references auth.users(id) on delete set null,
  fingerprint text,
  voted_at timestamptz not null default now(),
  unique(gem_url, user_id),
  constraint voter_required check (user_id is not null or fingerprint is not null)
);

-- Indexes, triggers, RLS — see migration applied via MCP 2026-04-08
