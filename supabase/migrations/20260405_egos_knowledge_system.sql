-- ============================================================
-- EGOS Knowledge System — Wiki Pages + Learnings
-- Pattern: Karpathy LLM Wiki (3-layer: raw → wiki → schema)
-- Applied via Supabase MCP on 2026-04-05
-- ============================================================

-- Wiki pages: compiled knowledge from raw sources
CREATE TABLE IF NOT EXISTS egos_wiki_pages (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug         text UNIQUE NOT NULL,
  title        text NOT NULL,
  content      text NOT NULL,
  category     text NOT NULL DEFAULT 'concept'
               CHECK (category IN ('concept', 'entity', 'decision', 'pattern', 'synthesis', 'how-to')),
  tags         text[] DEFAULT '{}',
  cross_refs   text[] DEFAULT '{}',
  source_files text[] DEFAULT '{}',
  compiled_by  text NOT NULL DEFAULT 'wiki-compiler',
  quality_score int DEFAULT 0 CHECK (quality_score BETWEEN 0 AND 100),
  version      int NOT NULL DEFAULT 1,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_wiki_pages_category ON egos_wiki_pages (category);
CREATE INDEX idx_wiki_pages_updated ON egos_wiki_pages (updated_at DESC);
CREATE INDEX idx_wiki_pages_tags ON egos_wiki_pages USING gin (tags);

-- Learnings: explicit what-worked / what-failed records
CREATE TABLE IF NOT EXISTS egos_learnings (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id   text,
  domain       text NOT NULL DEFAULT 'general'
               CHECK (domain IN ('general', 'architecture', 'deployment', 'monetization', 'governance', 'agents', 'security', 'dx')),
  outcome      text NOT NULL CHECK (outcome IN ('success', 'failure', 'insight')),
  summary      text NOT NULL,
  detail       text,
  pattern      text,
  evidence     text[],
  impact       text DEFAULT 'low' CHECK (impact IN ('low', 'medium', 'high', 'critical')),
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_learnings_domain ON egos_learnings (domain);
CREATE INDEX idx_learnings_outcome ON egos_learnings (outcome);
CREATE INDEX idx_learnings_created ON egos_learnings (created_at DESC);

-- Wiki changelog
CREATE TABLE IF NOT EXISTS egos_wiki_changelog (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  page_id      uuid NOT NULL REFERENCES egos_wiki_pages(id) ON DELETE CASCADE,
  action       text NOT NULL CHECK (action IN ('created', 'updated', 'lint_pass', 'lint_fail')),
  diff_summary text,
  compiled_by  text NOT NULL DEFAULT 'wiki-compiler',
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_wiki_changelog_page ON egos_wiki_changelog (page_id, created_at DESC);

-- RLS
ALTER TABLE egos_wiki_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE egos_learnings ENABLE ROW LEVEL SECURITY;
ALTER TABLE egos_wiki_changelog ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_wiki" ON egos_wiki_pages FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_learnings" ON egos_learnings FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_changelog" ON egos_wiki_changelog FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_read_wiki" ON egos_wiki_pages FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_learnings" ON egos_learnings FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_changelog" ON egos_wiki_changelog FOR SELECT TO authenticated USING (true);
