-- PLAT-MON-002 — platform_updates table
-- Tracks detected version changes for Claude Code, Notion, Anthropic SDK, Bun, MCP SDK

CREATE TABLE IF NOT EXISTS platform_updates (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  platform    TEXT NOT NULL,
  current_version TEXT NOT NULL,
  previous_version TEXT,
  summary     TEXT,
  changelog_url TEXT,
  egos_impact TEXT NOT NULL DEFAULT 'low' CHECK (egos_impact IN ('low','medium','high','critical')),
  egos_notes  TEXT,
  alerted     BOOLEAN DEFAULT FALSE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_platform_updates_platform ON platform_updates (platform, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_platform_updates_impact ON platform_updates (egos_impact) WHERE alerted = FALSE;

-- RLS: service role only (internal monitoring)
ALTER TABLE platform_updates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all" ON platform_updates
  FOR ALL USING (auth.role() = 'service_role');
