-- KBS-009 — Relax egos_wiki_pages category constraint for kb-ingest
-- Allow free-form categories beyond the original 6 built-in values

ALTER TABLE egos_wiki_pages
  DROP CONSTRAINT IF EXISTS egos_wiki_pages_category_check;

-- Add a non-restrictive constraint: just non-empty
ALTER TABLE egos_wiki_pages
  ADD CONSTRAINT egos_wiki_pages_category_nonempty
  CHECK (category IS NOT NULL AND length(category) > 0);

-- Common categories (not enforced, documentation only):
-- concept, entity, decision, pattern, synthesis, how-to
-- governanca, learnings, arquitetura, geral, metalurgia, juridico, saude
