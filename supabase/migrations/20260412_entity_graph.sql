-- KBS-028 — Entity Graph Layer v2
-- Creates egos_entities + egos_relationships tables for structured KB
-- Multi-tenant (tenant_id) with RLS mirroring egos_wiki_pages pattern
-- Designed for: delegacia, advocacia, agronegócio, EGOS self-demo

-- ── 1. egos_entities ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS egos_entities (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       TEXT        NOT NULL DEFAULT 'egos',
  type            TEXT        NOT NULL,   -- agent|task|capability|incident|decision|pattern|integration|pessoa|veiculo|caso|...
  name            TEXT        NOT NULL,
  slug            TEXT        NOT NULL,   -- url-safe identifier (unique per tenant+type)
  attributes      JSONB       NOT NULL DEFAULT '{}',
  source_file     TEXT,                   -- original doc/file this was extracted from
  source_slug     TEXT,                   -- if from egos_wiki_pages: the page slug
  extracted_by    TEXT        DEFAULT 'manual',  -- manual|kb-ingest|extractor-agent
  has_pii         BOOLEAN     NOT NULL DEFAULT false,
  confidence      FLOAT4      DEFAULT 1.0,       -- 0.0-1.0 (NER confidence)
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Unique per tenant + type + slug (prevents duplicate entities)
CREATE UNIQUE INDEX IF NOT EXISTS idx_entities_tenant_type_slug
  ON egos_entities (tenant_id, type, slug);

-- Fast lookup by tenant
CREATE INDEX IF NOT EXISTS idx_entities_tenant
  ON egos_entities (tenant_id, type, updated_at DESC);

-- Full-text search on name + attributes
CREATE INDEX IF NOT EXISTS idx_entities_fts
  ON egos_entities
  USING GIN (to_tsvector('portuguese', name || ' ' || coalesce(attributes::text, '')));

COMMENT ON TABLE egos_entities IS
  'Structured entities extracted from KB documents. One row per real-world entity (pessoa, caso, agent, task...).';
COMMENT ON COLUMN egos_entities.type IS
  'Entity type: EGOS=(agent|task|capability|incident|decision|pattern|integration), Delegacia=(pessoa|veiculo|caso|local|evento|organizacao|arma), Advocacia=(cliente|processo|audiencia|jurisprudencia|contrato|prazo), Agro=(talhao|cultura|insumo|equipamento|atividade)';
COMMENT ON COLUMN egos_entities.attributes IS
  'Flexible attributes as JSONB. Schema varies by entity type. See KBS_ENTITY_SCHEMA_EGOS.md.';
COMMENT ON COLUMN egos_entities.confidence IS
  'NER extraction confidence score (0.0-1.0). Manual entries = 1.0.';


-- ── 2. egos_relationships ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS egos_relationships (
  id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           TEXT        NOT NULL DEFAULT 'egos',
  source_entity_id    UUID        NOT NULL REFERENCES egos_entities(id) ON DELETE CASCADE,
  target_entity_id    UUID        NOT NULL REFERENCES egos_entities(id) ON DELETE CASCADE,
  relation_type       TEXT        NOT NULL,   -- TRIGGERS|IMPLEMENTS|BLOCKS|CAUSED_BY|APPLIED_IN|DEPENDS_ON|...
  context             TEXT,                   -- free-form description of this specific relationship
  doc_source          TEXT,                   -- which document established this relationship
  confidence          FLOAT4      DEFAULT 1.0,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Prevent duplicate relationships
CREATE UNIQUE INDEX IF NOT EXISTS idx_relationships_unique
  ON egos_relationships (tenant_id, source_entity_id, target_entity_id, relation_type);

-- Fast traversal queries
CREATE INDEX IF NOT EXISTS idx_relationships_source
  ON egos_relationships (tenant_id, source_entity_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_relationships_target
  ON egos_relationships (tenant_id, target_entity_id, relation_type);

COMMENT ON TABLE egos_relationships IS
  'Directed edges between entities. Source --[relation_type]--> Target.';
COMMENT ON COLUMN egos_relationships.relation_type IS
  'Relationship type in UPPER_SNAKE_CASE: TRIGGERS, IMPLEMENTS, BLOCKS, CAUSED_BY, FIXED_BY, APPLIED_IN, DEPENDS_ON, RELATED_TO, WORKS_WITH, INVESTIGATED_BY, OWNS, LOCATED_AT, OCCURRED_AT, PART_OF...';


-- ── 3. RLS Policies ─────────────────────────────────────────────────────────

ALTER TABLE egos_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE egos_relationships ENABLE ROW LEVEL SECURITY;

-- service_role: full access (used by agents + kb-ingest)
CREATE POLICY "service_role_all_entities" ON egos_entities
  FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_relationships" ON egos_relationships
  FOR ALL TO service_role USING (true) WITH CHECK (true);

-- authenticated: read own tenant only
CREATE POLICY "authenticated_read_own_entities" ON egos_entities
  FOR SELECT TO authenticated
  USING (tenant_id = current_setting('app.tenant_id', true));
CREATE POLICY "authenticated_read_own_relationships" ON egos_relationships
  FOR SELECT TO authenticated
  USING (tenant_id = current_setting('app.tenant_id', true));

-- anon: no access (entities may contain sensitive data)
-- (no anon policy = blocked by default)


-- ── 4. updated_at trigger ───────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER entities_updated_at
  BEFORE UPDATE ON egos_entities
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER relationships_updated_at
  BEFORE UPDATE ON egos_relationships
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ── 5. Helper views ─────────────────────────────────────────────────────────

-- Entity summary by tenant + type (for client dashboard)
CREATE OR REPLACE VIEW egos_entity_summary AS
SELECT
  tenant_id,
  type,
  COUNT(*)                                          AS total,
  COUNT(*) FILTER (WHERE has_pii)                   AS with_pii,
  AVG(confidence)::FLOAT4                           AS avg_confidence,
  MAX(updated_at)                                   AS last_updated
FROM egos_entities
GROUP BY tenant_id, type;

COMMENT ON VIEW egos_entity_summary IS
  'Aggregated entity counts per tenant+type. Used by client dashboard (KBS-039).';

-- Relationship stats per tenant
CREATE OR REPLACE VIEW egos_relationship_summary AS
SELECT
  r.tenant_id,
  r.relation_type,
  COUNT(*) AS total,
  COUNT(DISTINCT r.source_entity_id) AS unique_sources,
  COUNT(DISTINCT r.target_entity_id) AS unique_targets
FROM egos_relationships r
GROUP BY r.tenant_id, r.relation_type;

COMMENT ON VIEW egos_relationship_summary IS
  'Aggregated relationship counts per tenant+type. Used for graph density metrics.';


-- ── Done ────────────────────────────────────────────────────────────────────
-- Apply: supabase db push (local) or via Supabase MCP apply_migration
-- Next: KBS-029 entity extractor adapter, KBS-031 intelligence report generator
