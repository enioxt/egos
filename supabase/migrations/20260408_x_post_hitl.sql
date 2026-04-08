-- ═══════════════════════════════════════════════════════════════════
-- X Post HITL — 3-Option Approval System
-- ═══════════════════════════════════════════════════════════════════
-- Tables:
--   x_post_options   — 3 LLM-generated alternatives per queued post
--   x_post_choices   — user's choice history + edit diffs for LLM learning

-- ── Alter x_post_queue: add pending status + final_text ──────────────
alter table x_post_queue
  add column if not exists final_text text,          -- chosen + edited text
  add column if not exists approved_at timestamptz,  -- when user approved
  add column if not exists options_id uuid;          -- FK to x_post_options (set after generation)

-- Update default status to 'pending' for new rows (requires human approval)
alter table x_post_queue alter column status set default 'pending';

-- ── x_post_options ────────────────────────────────────────────────────
create table x_post_options (
  id          uuid primary key default gen_random_uuid(),
  post_id     uuid not null references x_post_queue(id) on delete cascade,
  created_at  timestamptz default now(),

  -- Three alternatives
  option_a    text not null,   -- tone: bold/hook
  option_b    text not null,   -- tone: conversational/accessible
  option_c    text not null,   -- tone: technical/precise

  tone_a      text default 'bold',
  tone_b      text default 'conversational',
  tone_c      text default 'technical',

  -- Generation metadata
  model_used  text default 'qwen-plus',
  prompt_hash text,            -- SHA256 of the prompt (for dedup)
  context     jsonb            -- article_title, article_url, key_claims, article_id
);

alter table x_post_options enable row level security;
create policy "service_role_all_x_post_options"
  on x_post_options for all
  using (auth.role() = 'service_role');

-- ── x_post_choices ────────────────────────────────────────────────────
create table x_post_choices (
  id           uuid primary key default gen_random_uuid(),
  post_id      uuid not null references x_post_queue(id) on delete cascade,
  options_id   uuid references x_post_options(id),
  chosen_at    timestamptz default now(),

  -- What the user chose
  chosen_option  text not null check (chosen_option in ('a','b','c','custom')),
  chosen_text    text not null,    -- final text after any edits
  original_text  text not null,    -- the option text before editing

  -- Edit analysis (populated by bot after diff)
  was_edited     boolean default false,
  edit_distance  int,              -- Levenshtein distance
  edit_summary   text,             -- e.g. "shortened by 40 chars", "added emoji"
  added_chars    text,             -- new chars/phrases not in original
  removed_chars  text,             -- removed phrases

  -- Learning signal
  preferred_tone    text,          -- from x_post_options.tone_X
  preferred_length  int,           -- char count of final text
  article_category  text,          -- article type: govtech/guard/gem-hunter/general

  -- Context snapshot
  telegram_msg_id   bigint,        -- for traceability
  model_used        text
);

alter table x_post_choices enable row level security;
create policy "service_role_all_x_post_choices"
  on x_post_choices for all
  using (auth.role() = 'service_role');

-- ── x_post_preferences (aggregated learning) ─────────────────────────
create table x_post_preferences (
  id                uuid primary key default gen_random_uuid(),
  last_updated      timestamptz default now(),
  sample_count      int default 0,

  -- Tone preferences (percentage of choices)
  pct_bold          float default 0,
  pct_conversational float default 0,
  pct_technical     float default 0,

  -- Format preferences
  avg_preferred_length int,
  pct_edited        float default 0,          -- how often user edits before posting
  avg_edit_distance float default 0,

  -- Common additions (e.g. always adds "🧵" or "→")
  common_additions  text[],
  common_removals   text[],

  -- System prompt context for LLM
  preference_summary text              -- human-readable summary for LLM system prompt
);

-- Seed with defaults
insert into x_post_preferences (sample_count, preference_summary) values
(0, 'No preference data yet. Generate diverse options. User is Enio Rocha, Brazilian developer, builder-researcher. Authentic tone, no hype, no sales-speak. Portuguese preferred unless topic naturally suits English.');

alter table x_post_preferences enable row level security;
create policy "service_role_all_x_post_preferences"
  on x_post_preferences for all
  using (auth.role() = 'service_role');

-- ── Update FK on x_post_queue ─────────────────────────────────────────
alter table x_post_queue
  add constraint x_post_queue_options_fk
  foreign key (options_id) references x_post_options(id) on delete set null;
