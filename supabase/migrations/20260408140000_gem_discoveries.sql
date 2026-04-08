-- Migration: Create gem_discoveries table for CORAL knowledge reuse pattern
-- Date: 2026-04-08
-- Author: EGOS Memory Integration v2
-- SSOT: TASKS.md §CORAL Pattern

-- ═════════════════════════════════════════════════════════════════════════════
-- Table: gem_discoveries
-- Purpose: Shared agent discovery store for knowledge reuse across runs
-- Pattern from: CORAL (MIT, arXiv 2604.01658)
-- ═════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS gem_discoveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Discovery metadata
    repo_url TEXT NOT NULL,
    gem_name TEXT NOT NULL,
    category TEXT NOT NULL,
    score DECIMAL(3,1) NOT NULL CHECK (score >= 0 AND score <= 10),

    -- Discovery source
    discovered_by TEXT NOT NULL, -- Agent ID that found this
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Content
    summary TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',

    -- Reuse metadata (for CORAL pattern)
    novelty_score DECIMAL(3,2) DEFAULT 0.5, -- How unique is this discovery
    applicability_score DECIMAL(3,2) DEFAULT 0.5, -- How applicable to other tasks
    reuse_count INTEGER DEFAULT 0, -- How many times this was reused
    last_reused_at TIMESTAMPTZ,

    -- Status
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'stale', 'archived')),

    -- Full-text search vector
    search_vector tsvector
);

-- ═════════════════════════════════════════════════════════════════════════════
-- Indexes
-- ═════════════════════════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_gem_discoveries_repo_url ON gem_discoveries(repo_url);
CREATE INDEX IF NOT EXISTS idx_gem_discoveries_category ON gem_discoveries(category);
CREATE INDEX IF NOT EXISTS idx_gem_discoveries_score ON gem_discoveries(score DESC);
CREATE INDEX IF NOT EXISTS idx_gem_discoveries_discovered_at ON gem_discoveries(discovered_at DESC);
CREATE INDEX IF NOT EXISTS idx_gem_discoveries_status ON gem_discoveries(status) WHERE status = 'active';

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_gem_discoveries_search ON gem_discoveries USING GIN(search_vector);

-- Composite index for reuse queries
CREATE INDEX IF NOT EXISTS idx_gem_discoveries_reuse ON gem_discoveries(
    novelty_score DESC,
    applicability_score DESC,
    reuse_count ASC
) WHERE status = 'active';

-- ═════════════════════════════════════════════════════════════════════════════
-- Full-text search trigger
-- ═════════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_gem_discoveries_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.gem_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.tags, ' '), '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS gem_discoveries_search_update ON gem_discoveries;

CREATE TRIGGER gem_discoveries_search_update
    BEFORE INSERT OR UPDATE ON gem_discoveries
    FOR EACH ROW
    EXECUTE FUNCTION update_gem_discoveries_search_vector();

-- ═════════════════════════════════════════════════════════════════════════════
-- Row Level Security (RLS)
-- ═════════════════════════════════════════════════════════════════════════════

ALTER TABLE gem_discoveries ENABLE ROW LEVEL SECURITY;

-- Policy: Allow read for all authenticated users
CREATE POLICY gem_discoveries_read ON gem_discoveries
    FOR SELECT
    TO authenticated
    USING (true);

-- Policy: Allow insert/update for service role
CREATE POLICY gem_discoveries_write ON gem_discoveries
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ═════════════════════════════════════════════════════════════════════════════
-- Utility Functions
-- ═════════════════════════════════════════════════════════════════════════════

-- Find relevant discoveries for a task (CORAL knowledge reuse)
CREATE OR REPLACE FUNCTION find_relevant_discoveries(
    task_query TEXT,
    context_tags TEXT[],
    min_score DECIMAL DEFAULT 7.0,
    max_age_days INTEGER DEFAULT 14
)
RETURNS TABLE (
    id UUID,
    repo_url TEXT,
    gem_name TEXT,
    category TEXT,
    score DECIMAL,
    summary TEXT,
    tags TEXT[],
    novelty_score DECIMAL,
    applicability_score DECIMAL,
    relevance_rank DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        gd.id,
        gd.repo_url,
        gd.gem_name,
        gd.category,
        gd.score,
        gd.summary,
        gd.tags,
        gd.novelty_score,
        gd.applicability_score,
        (
            -- Relevance ranking: novelty × applicability / (reuse_count + 1)
            (gd.novelty_score * gd.applicability_score) /
            (gd.reuse_count + 1.0) *
            -- Boost for matching tags
            (1.0 + COALESCE(
                (SELECT COUNT(*) FROM unnest(gd.tags) t WHERE t = ANY(context_tags)),
                0
            ) * 0.1)
        )::DECIMAL(10,4) as relevance_rank
    FROM gem_discoveries gd
    WHERE gd.status = 'active'
        AND gd.score >= min_score
        AND gd.discovered_at > (now() - (max_age_days || ' days')::interval)
        AND (
            gd.search_vector @@ plainto_tsquery('english', task_query)
            OR gd.tags && context_tags
        )
    ORDER BY relevance_rank DESC, gd.score DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Record reuse of a discovery
CREATE OR REPLACE FUNCTION record_discovery_reuse(discovery_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE gem_discoveries
    SET
        reuse_count = reuse_count + 1,
        last_reused_at = now()
    WHERE id = discovery_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Mark old discoveries as stale
CREATE OR REPLACE FUNCTION mark_stale_discoveries(age_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE gem_discoveries
    SET status = 'stale'
    WHERE status = 'active'
        AND discovered_at < (now() - (age_days || ' days')::interval)
        AND last_seen_at < (now() - (age_days || ' days')::interval);

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ═════════════════════════════════════════════════════════════════════════════
-- Comments
-- ═════════════════════════════════════════════════════════════════════════════

COMMENT ON TABLE gem_discoveries IS 'Shared agent discovery store for CORAL knowledge reuse pattern';
COMMENT ON COLUMN gem_discoveries.novelty_score IS 'How unique this discovery is (0-1)';
COMMENT ON COLUMN gem_discoveries.applicability_score IS 'How applicable to other tasks (0-1)';
COMMENT ON COLUMN gem_discoveries.reuse_count IS 'Number of times this discovery was reused by other agents';
COMMENT ON FUNCTION find_relevant_discoveries IS 'CORAL knowledge reuse: find relevant past discoveries for current task';
