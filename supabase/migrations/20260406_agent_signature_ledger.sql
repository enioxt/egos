-- EGOS Agent Signature Ledger Migration
-- Created: 2026-04-06 (post-INC-001)
-- Purpose: cryptographically signed, append-only ledger of agent actions
--          + 3-tier approval levels (L0 autonomous / L1 notify / L2 approval)
--
-- Lineage: extends the non-repudiation provenance pattern from br-acc/
-- etl/src/bracc_etl/provenance.py (canonical_row_json + sha256 + source
-- fingerprinting). br-acc uses it for ETL audit trails ("this row came
-- from this exact public source at this exact time"). We reuse the same
-- field names (raw_line_hash, source_url, source_method, verified_at,
-- source_fingerprint) so EGOS provenance and br-acc provenance are
-- interchangeable / verifiable across the ecosystem.
--
-- Why: INC-001 (force-push by parallel scheduled agent) showed that
-- agent actions need cryptographic provenance + rollback safety.

-- ─── agent_keys ───────────────────────────────────────────────────────
-- Each agent has one Ed25519 keypair. Public key lives here, private key
-- in Supabase Vault (NOT this table). Rotation supported via revoked_at.

CREATE TABLE IF NOT EXISTS agent_keys (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  agent_id text NOT NULL,
  public_key text NOT NULL, -- base64url-encoded Ed25519 32-byte public key
  algorithm text NOT NULL DEFAULT 'ed25519',
  created_at timestamptz DEFAULT now(),
  revoked_at timestamptz,
  notes text,
  CONSTRAINT agent_keys_agent_active_unique UNIQUE NULLS NOT DISTINCT (agent_id, revoked_at)
);
CREATE INDEX IF NOT EXISTS agent_keys_agent_id_idx ON agent_keys(agent_id) WHERE revoked_at IS NULL;
ALTER TABLE agent_keys ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_all" ON agent_keys USING (true) WITH CHECK (true);

-- ─── agent_actions_ledger ────────────────────────────────────────────
-- Append-only Merkle-chained ledger of every meaningful agent action.
-- Combines:
--   - br-acc provenance fields (raw_line_hash, source_*, verified_at)
--   - hash chain (prev_hash -> hash) for tamper detection
--   - Ed25519 signature for non-repudiation
--   - 3-tier approval level (L0/L1/L2)

CREATE TABLE IF NOT EXISTS agent_actions_ledger (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  ts timestamptz NOT NULL DEFAULT now(),

  agent_id text NOT NULL,

  action_type text NOT NULL CHECK (action_type IN (
    'commit', 'push', 'merge', 'release', 'deploy', 'config_change',
    'message_send', 'task_create', 'task_update', 'file_write', 'file_delete',
    'api_call', 'tool_use', 'merge_pr', 'merge_branch', 'rebase',
    'schedule_run', 'governance_check', 'audit_run',
    -- br-acc style data ingestion actions:
    'fetch_source', 'parse_response', 'enrich_node', 'graph_write',
    'other'
  )),

  approval_level text NOT NULL CHECK (approval_level IN ('L0', 'L1', 'L2')),
  -- L0: autonomous — agent did this on its own, just logged
  -- L1: notify — agent did this and notified a human, no approval gate
  -- L2: approval — agent proposed and a human approved before execution

  -- ── br-acc provenance fields (consistent naming with provenance.py) ──
  raw_line_hash text NOT NULL,
  -- sha256 of canonical JSON of the action payload (== br-acc's raw_row_hash)

  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  -- structured details: file paths, commit sha, branch, message, etc.

  source_url text,
  -- where the action originated (URL form): file://, https://, ccr://, gha://

  source_method text,
  -- how it ran: 'http_get', 'git_commit', 'ccr_scheduled', 'gha_workflow', etc.

  source_fingerprint text NOT NULL,
  -- sha256(source_url || '|' || source_method || '|' || verified_at)

  verified_at timestamptz NOT NULL DEFAULT now(),
  -- when the action was verified to have happened

  audit_status text NOT NULL DEFAULT 'verified' CHECK (audit_status IN (
    'verified', 'pending', 'rejected', 'tampered'
  )),

  -- ── hash chain (Merkle) ──
  prev_hash text,
  -- the `hash` of the previous row in this agent's chain. NULL = genesis.

  hash text NOT NULL,
  -- sha256(prev_hash || ts || agent_id || action_type || raw_line_hash || source_fingerprint)
  -- This is the cryptographic chain link.

  -- ── digital signature (Ed25519) ──
  signature text NOT NULL,
  -- base64url Ed25519 signature of `hash` by the agent's private key

  signing_key_id uuid REFERENCES agent_keys(id),

  -- ── approval audit ──
  approved_by text,
  -- if approval_level == L2, who approved (human handle or session id)

  approval_evidence jsonb,
  -- arbitrary proof of approval (slack message id, telegram id, click trace)

  -- ── correlation ──
  correlation_id text,
  -- group related actions (e.g. all commits in one session)

  created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS aal_ts_idx ON agent_actions_ledger(ts DESC);
CREATE INDEX IF NOT EXISTS aal_agent_id_idx ON agent_actions_ledger(agent_id);
CREATE INDEX IF NOT EXISTS aal_action_type_idx ON agent_actions_ledger(action_type);
CREATE INDEX IF NOT EXISTS aal_approval_level_idx ON agent_actions_ledger(approval_level);
CREATE INDEX IF NOT EXISTS aal_correlation_idx ON agent_actions_ledger(correlation_id);
CREATE INDEX IF NOT EXISTS aal_source_fingerprint_idx ON agent_actions_ledger(source_fingerprint);
CREATE UNIQUE INDEX IF NOT EXISTS aal_hash_unique ON agent_actions_ledger(hash);

ALTER TABLE agent_actions_ledger ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_all" ON agent_actions_ledger USING (true) WITH CHECK (true);

-- ─── chain integrity helper ───────────────────────────────────────────
-- Detects breaks in the hash chain. Returns rows where prev_hash doesn't
-- match the actual previous row's hash. A non-empty result = tampering
-- or a recovery break point.

CREATE OR REPLACE VIEW agent_ledger_integrity AS
WITH ordered AS (
  SELECT
    id, ts, agent_id, action_type, hash, prev_hash,
    LAG(hash) OVER (PARTITION BY agent_id ORDER BY ts) AS expected_prev_hash
  FROM agent_actions_ledger
)
SELECT id, ts, agent_id, action_type, hash, prev_hash, expected_prev_hash
FROM ordered
WHERE prev_hash IS DISTINCT FROM expected_prev_hash
  AND NOT (prev_hash IS NULL AND expected_prev_hash IS NULL);

-- ─── pending_approvals view ───────────────────────────────────────────
CREATE OR REPLACE VIEW pending_approvals AS
SELECT id, ts, agent_id, action_type, payload, source_url, source_method, correlation_id
FROM agent_actions_ledger
WHERE approval_level = 'L2' AND approved_by IS NULL
ORDER BY ts ASC;

COMMENT ON TABLE agent_keys IS 'Ed25519 public keys per agent. Private keys live in Supabase Vault. Lineage: br-acc provenance pattern + signature.';
COMMENT ON TABLE agent_actions_ledger IS 'Append-only Merkle chain of cryptographically signed agent actions. INC-001 mitigation. Field names align with br-acc/provenance.py.';
COMMENT ON VIEW agent_ledger_integrity IS 'Returns rows where the hash chain is broken. Empty = healthy.';
COMMENT ON VIEW pending_approvals IS 'L2 actions awaiting human approval.';
