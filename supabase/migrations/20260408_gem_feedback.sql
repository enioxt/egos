-- Migration: gem_feedback table
-- Task: GH-090 (Gem Hunter Feedback Loop v8)
-- Created: 2026-04-08
-- Purpose: Store user reactions to Telegram gem alerts for scoring self-improvement

CREATE TABLE IF NOT EXISTS gem_feedback (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id     TEXT NOT NULL,         -- Telegram message_id or run_id+gem_url hash
  gem_url      TEXT NOT NULL,         -- URL of the gem that was alerted
  gem_name     TEXT,                  -- Name at time of alert
  run_id       TEXT,                  -- gem-hunter run that produced this alert
  reaction     TEXT NOT NULL          -- '👍' | '👎' | '🔍' | '💬'
                CHECK (reaction IN ('👍', '👎', '🔍', '💬')),
  comment      TEXT,                  -- Optional inline comment from user
  score_at_alert INTEGER,             -- Score when alert was sent (for drift tracking)
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for feedback reader (reads by created_at for 2x/day cron)
CREATE INDEX IF NOT EXISTS gem_feedback_created_idx ON gem_feedback(created_at DESC);

-- Index for per-gem analysis
CREATE INDEX IF NOT EXISTS gem_feedback_gem_url_idx ON gem_feedback(gem_url);

-- RLS: only service role can read/write (no public access to scoring feedback)
ALTER TABLE gem_feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only" ON gem_feedback
  FOR ALL USING (auth.role() = 'service_role');

-- Also create gem_seen_cache for GH-094 repetition detector
CREATE TABLE IF NOT EXISTS gem_seen_cache (
  url_hash     TEXT PRIMARY KEY,      -- sha256(gem.url + gem.author)
  gem_url      TEXT NOT NULL,
  gem_name     TEXT,
  first_seen   TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen    TIMESTAMPTZ NOT NULL DEFAULT now(),
  seen_count   INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS gem_seen_cache_last_seen_idx ON gem_seen_cache(last_seen DESC);

ALTER TABLE gem_seen_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only" ON gem_seen_cache
  FOR ALL USING (auth.role() = 'service_role');
