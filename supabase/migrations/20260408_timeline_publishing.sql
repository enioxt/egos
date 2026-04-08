-- Timeline + AI Publishing Migration
-- Created: 2026-04-08
-- Task: TL-001
-- Tables: timeline_drafts, timeline_articles, x_post_queue

create table timeline_drafts (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  title text not null,
  summary text not null,                  -- <= 280 chars (used as X snippet)
  body_md text not null,                  -- full article markdown
  source_commits text[] not null,         -- ['ae7b9ad', '13c12ae']
  source_files text[],
  tags text[],
  status text not null default 'pending', -- pending|approved|rejected|published
  llm_provider text,                      -- 'qwen-plus' | 'qwen3-free'
  llm_cost_usd numeric(8,5) default 0,
  pii_check_passed bool default false,
  drift_check_passed bool default false,
  created_at timestamptz default now(),
  approved_at timestamptz,
  approved_by text,                       -- 'enio' | 'auto'
  rejected_reason text
);

create table timeline_articles (
  id uuid primary key default gen_random_uuid(),
  draft_id uuid references timeline_drafts(id),
  slug text unique not null,
  title text not null,
  body_html text not null,                -- rendered MDX
  url text not null,                      -- https://egos.ia.br/timeline/{slug}
  published_at timestamptz default now(),
  x_post_id text,                         -- tweet id se publicado
  x_post_url text,
  views int default 0,
  engagement_json jsonb                   -- {likes, retweets, replies, click_through}
);

create table x_post_queue (
  id uuid primary key default gen_random_uuid(),
  article_id uuid references timeline_articles(id),
  text text not null,                     -- <= 270 chars
  thread_position int default 0,
  scheduled_for timestamptz default now(),
  posted_at timestamptz,
  tweet_id text,
  status text default 'queued'            -- queued|posted|failed
);

alter table timeline_drafts enable row level security;
alter table timeline_articles enable row level security;
alter table x_post_queue enable row level security;

create policy "service_role_all_timeline_drafts" on timeline_drafts for all using (auth.role() = 'service_role');
create policy "service_role_all_timeline_articles" on timeline_articles for all using (auth.role() = 'service_role');
create policy "service_role_all_x_post_queue" on x_post_queue for all using (auth.role() = 'service_role');
