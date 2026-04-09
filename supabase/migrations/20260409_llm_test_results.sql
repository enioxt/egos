-- LLM-MON-005 — llm_test_results table
-- Stores results from llm-test-suite.ts for each model tested

CREATE TABLE IF NOT EXISTS llm_test_results (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  model_id        TEXT NOT NULL,
  total_score     INTEGER NOT NULL DEFAULT 0,
  tests_passed    INTEGER NOT NULL DEFAULT 0,
  tests_total     INTEGER NOT NULL DEFAULT 0,
  results_json    JSONB,
  tested_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_llm_test_results_model ON llm_test_results (model_id, tested_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_test_results_score ON llm_test_results (total_score DESC);

ALTER TABLE llm_test_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all" ON llm_test_results
  FOR ALL USING (auth.role() = 'service_role');
