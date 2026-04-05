-- EGOS HQ Tables Migration
-- Created: 2026-04-06
-- Tables: x_reply_runs, egos_agent_events

-- x_reply_runs: persists hourly bot results (replaces ephemeral /tmp/ state)
CREATE TABLE IF NOT EXISTS x_reply_runs (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  run_at timestamptz DEFAULT now(),
  topic text,
  tweet_id text UNIQUE,
  tweet_text text,
  tweet_author text,
  tweet_likes int DEFAULT 0,
  generated_reply text,
  status text CHECK (status IN ('pending','approved','rejected','sent','dry_run')) DEFAULT 'pending',
  sent_at timestamptz,
  error text,
  created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS x_reply_runs_status_idx ON x_reply_runs(status);
CREATE INDEX IF NOT EXISTS x_reply_runs_run_at_idx ON x_reply_runs(run_at DESC);
ALTER TABLE x_reply_runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_all" ON x_reply_runs USING (true) WITH CHECK (true);

-- egos_agent_events: live event stream from agent runner and services
CREATE TABLE IF NOT EXISTS egos_agent_events (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamptz DEFAULT now(),
  source text NOT NULL,
  event_type text NOT NULL,
  severity text CHECK (severity IN ('info','warning','error','critical')) DEFAULT 'info',
  payload jsonb DEFAULT '{}',
  correlation_id text
);
CREATE INDEX IF NOT EXISTS egos_agent_events_created_idx ON egos_agent_events(created_at DESC);
CREATE INDEX IF NOT EXISTS egos_agent_events_source_idx ON egos_agent_events(source);
CREATE INDEX IF NOT EXISTS egos_agent_events_severity_idx ON egos_agent_events(severity);
ALTER TABLE egos_agent_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_all" ON egos_agent_events USING (true) WITH CHECK (true);

-- Enable Realtime on egos_agent_events
-- NOTE: Also enable in Supabase Dashboard → Database → Replication → egos_agent_events
