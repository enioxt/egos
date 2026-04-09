-- KBS-016 — Multi-tenant support for egos_wiki_pages
-- Adds tenant_id to isolate knowledge bases per client
-- Safe: nullable with default 'egos' so existing rows keep working

-- 1. Add tenant_id column (defaults to 'egos' = internal EGOS knowledge base)
ALTER TABLE egos_wiki_pages
  ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'egos';

-- 2. Index for fast per-tenant queries
CREATE INDEX IF NOT EXISTS idx_wiki_pages_tenant
  ON egos_wiki_pages (tenant_id, updated_at DESC);

-- 3. Composite unique constraint: slug must be unique per tenant
ALTER TABLE egos_wiki_pages
  DROP CONSTRAINT IF EXISTS egos_wiki_pages_slug_key;

ALTER TABLE egos_wiki_pages
  ADD CONSTRAINT egos_wiki_pages_tenant_slug_unique
  UNIQUE (tenant_id, slug);

-- 4. Update RLS: service_role sees all, authenticated sees own tenant
DROP POLICY IF EXISTS "authenticated_read_wiki" ON egos_wiki_pages;
CREATE POLICY "authenticated_read_own_tenant" ON egos_wiki_pages
  FOR SELECT TO authenticated
  USING (tenant_id = current_setting('app.tenant_id', true));

-- Note: service_role_all_wiki policy already covers writes (unchanged)

-- 5. Function to set tenant context (used by app layer)
CREATE OR REPLACE FUNCTION set_tenant(t_id TEXT)
RETURNS VOID AS $$
BEGIN
  PERFORM set_config('app.tenant_id', t_id, true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON COLUMN egos_wiki_pages.tenant_id IS
  'Client tenant identifier (e.g. egos, forja, rocha-adv). Default: egos (internal EGOS KB)';
