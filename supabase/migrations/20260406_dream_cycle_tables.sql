-- Dream Cycle tables for overnight intelligence

-- Nightly log harvest results
CREATE TABLE IF NOT EXISTS egos_nightly_logs (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  date date NOT NULL,
  summary jsonb NOT NULL DEFAULT '{}',
  containers jsonb NOT NULL DEFAULT '[]',
  critical_count integer NOT NULL DEFAULT 0,
  guard_calls_24h integer NOT NULL DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

-- Nightly intelligence reports
CREATE TABLE IF NOT EXISTS egos_nightly_reports (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  date date NOT NULL,
  report_md text NOT NULL,
  tasks_created integer NOT NULL DEFAULT 0,
  insights jsonb NOT NULL DEFAULT '[]',
  action_taken text[] DEFAULT ARRAY[]::text[],
  created_at timestamptz DEFAULT now()
);

-- RLS
ALTER TABLE egos_nightly_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE egos_nightly_reports ENABLE ROW LEVEL SECURITY;

-- Service role has full access (used by Dream Cycle agents)
CREATE POLICY "service_all_nightly_logs" ON egos_nightly_logs
  FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_all_nightly_reports" ON egos_nightly_reports
  FOR ALL USING (auth.role() = 'service_role');
