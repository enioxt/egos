# KERNEL MISSION CONTROL — kernel.egos.ia.br

> **Version:** 1.0.0 | **Absorbed from:** Google AI Studio Handoff (BLUEPRINT-EGOS) | **Status:** Architecture Phase | **Date:** 2026-03-25

---

## Vision

**EGOS Mission Control** is a centralized observability and governance dashboard for the entire EGOS ecosystem. It monitors commits across all leaf repositories, detects anomalies (breaking changes, test failures, security issues), provides AI-driven insights via Qwen-Plus, and orchestrates automated governance actions (PRs, task creation, notifications).

Think of it as:
- **GitHub Dashboard on steroids** — cross-repo view with real-time event streaming
- **Incident Response Center** — detects and auto-triages anomalies
- **Code Provenance Tracker** — every commit is a signed event with source attribution (GitHub/Codex/Claude Code/Alibaba)
- **Automated Governance Engine** — enforces SSOT policies, blocks non-compliant PRs, kicks off remediation workflows

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    KERNEL MISSION CONTROL                        │
│                  (kernel.egos.ia.br — Vercel)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Frontend (React + Vite)                                        │
│  ├─ Dashboard (repos, commits, anomalies, insights)            │
│  ├─ Real-time feeds (WebSocket via Supabase)                   │
│  └─ PDF export + email alerts                                  │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Gateway (Contabo VPS)                                  │
│  ├─ /api/webhooks/github — GitHub webhook receiver            │
│  ├─ /api/webhooks/codex — Codex events                        │
│  ├─ /api/webhooks/claude-code — Claude Code integration       │
│  ├─ /api/governance/gate — pre-merge policy enforcement      │
│  └─ /api/openClaw/* — Git automation endpoints               │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Event Processing Pipeline                                      │
│  ├─ Webhook → Event validation (GPG signatures)               │
│  ├─ Event enrichment (code analysis, semantic embeddings)     │
│  ├─ Supabase provenance_events table (multi-tenant RLS)       │
│  └─ Mycelium event bus (Redis Pub/Sub for agent triggers)    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Supabase Backend                                               │
│  ├─ provenance_events (commits, PRs, deploys, test runs)     │
│  ├─ semantic_embeddings (pgvector column, 1536-dim)          │
│  ├─ governance_checks (SSOT drift, security scans)           │
│  └─ RLS policies (by tenant_id and repo_id)                  │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  AI/ML Layer                                                    │
│  ├─ Qwen-Plus insights (anomaly analysis, root causes)        │
│  ├─ Alibaba Dashscope embeddings (semantic commit similarity) │
│  ├─ K-means clustering (group related commits)               │
│  └─ Drift detection (SSOT vs actual)                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. **Frontend — Mission Control Dashboard** (React + Vite)

**Deploy Target:** `kernel.egos.ia.br` (Vercel)

#### Screens:

1. **Overview Dashboard**
   - Real-time status cards: repos online, last 10 commits, anomalies count
   - Sparkline charts: commits/day, test pass rate, SSOT compliance %
   - Quick stats: total repos, active developers, pending governance gates

2. **Commit Timeline** (Firehose)
   - All commits across repos in reverse chronological order
   - Color-coded by repo + severity (breaking/normal/style-fix)
   - Expandable details: message, diffs, author, source tool (GitHub/Codex/etc)
   - Filters: repo, time range, author, event type

3. **Anomalies Feed**
   - Cards grouped by severity: critical, warning, info
   - Examples: test failures, breaking API changes, security vulnerabilities, SSOT drift
   - Auto-triage via Qwen-Plus: root cause hypothesis, suggested action
   - Click-to-escalate: create GitHub issue, create EGOS task, notify oncall

4. **Governance Gate** (Enforcement)
   - PRs blocked by governance checks: SSOT drift, security scan fails, test coverage drop
   - Show: which check failed, remediation link, PR author contact
   - Override capability (for approved users)

5. **Insights & Trends**
   - AI-generated weekly report (Qwen-Plus): top anomalies, patterns, recommendations
   - Semantic search: "find commits similar to this PRD"
   - Trend analysis: velocity, test stability, deployment frequency

#### Tech Stack:
- **Framework:** React 19 + TypeScript
- **Build:** Vite (fast dev server)
- **Styling:** Tailwind CSS v4 + dark mode
- **Realtime:** Supabase Realtime (WebSocket subscriptions)
- **Charts:** Recharts (D3-based) for trends
- **PDF Export:** jsPDF + html2canvas
- **Deployment:** Vercel (auto-deploy from GitHub)

### 2. **FastAPI Gateway** (Python)

**Deploy Target:** Hetzner VPS (204.168.217.125) — migrado de Contabo em 2026-03-28

#### Endpoints:

```
POST /api/webhooks/github
  Receives: GitHub push, PR, release events
  Validates: HMAC-SHA256 signature
  Maps: github event → provenance_event record
  Publish: Mycelium event bus

POST /api/webhooks/codex
  Receives: Codex execution events (session start, model calls, outputs)
  Tags: codex_model, task_class, cost_estimate

POST /api/webhooks/claude-code
  Receives: Claude Code tool calls, file writes, git commits
  Tags: tool_name, operation_type, affected_files

GET /api/governance/gate?pr_id=123
  Pre-merge check: SSOT drift? Security scan OK? Tests pass?
  Returns: pass/fail + metadata for Mission Control

POST /api/governance/gate/override
  Admin-only: temporarily waive governance check with justification

POST /api/openClaw/clone
  Trigger: Git clone + move files to destination repo

POST /api/openClaw/pr
  Trigger: Create PR with template, assign reviewers, auto-label
```

#### Implementation Details:
- **Event Validation:** GPG signature check (if using signed webhooks)
- **Idempotency:** Track event IDs to prevent duplicate processing
- **Retry Logic:** Exponential backoff (3 retries, max 30s)
- **Logging:** Structured JSON logs to Supabase `gateway_logs` table
- **Rate Limiting:** 1000 req/min per source

### 3. **Supabase Schema**

#### Table: `provenance_events`

```sql
CREATE TABLE provenance_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  repo_id UUID NOT NULL REFERENCES repositories(id),

  -- Event metadata
  source TEXT NOT NULL CHECK (source IN ('github', 'codex', 'claude-code', 'alibaba')),
  event_type TEXT NOT NULL CHECK (event_type IN ('push', 'pr', 'release', 'test_run', 'deploy', 'scan')),

  -- Git info
  commit_sha VARCHAR(40),
  commit_message TEXT,
  author_email TEXT,
  author_name TEXT,

  -- Timestamps
  event_timestamp TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),

  -- Enrichment
  embedding vector(1536),  -- pgvector column
  severity TEXT CHECK (severity IN ('critical', 'warning', 'info')),
  anomaly_detected BOOLEAN DEFAULT FALSE,

  -- Extra metadata (JSON)
  metadata JSONB DEFAULT '{}',

  CONSTRAINT valid_embedding CHECK (embedding IS NULL OR array_length(embedding::float8[], 1) = 1536)
);

CREATE INDEX idx_provenance_repo_ts ON provenance_events(repo_id, event_timestamp DESC);
CREATE INDEX idx_provenance_author_ts ON provenance_events(author_email, event_timestamp DESC);
CREATE INDEX idx_provenance_type_ts ON provenance_events(event_type, event_timestamp DESC);
CREATE INDEX idx_provenance_anomaly ON provenance_events(anomaly_detected) WHERE anomaly_detected = TRUE;

-- RLS policy: users see events from their tenant only
ALTER TABLE provenance_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY provenance_tenant_isolation ON provenance_events
  FOR SELECT USING (tenant_id = auth.jwt_claims() ->> 'tenant_id'::uuid);
```

#### Table: `governance_checks`

```sql
CREATE TABLE governance_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  pr_id VARCHAR(20),  -- GitHub PR number

  -- Check results
  ssot_drift BOOLEAN,
  ssot_drift_details TEXT,

  security_scan_passed BOOLEAN,
  security_scan_findings JSONB,

  tests_passed BOOLEAN,
  test_coverage_percent FLOAT,

  typescript_compile BOOLEAN,
  compile_errors TEXT,

  created_at TIMESTAMP DEFAULT NOW(),
  passed BOOLEAN GENERATED ALWAYS AS (ssot_drift = FALSE AND security_scan_passed = TRUE AND tests_passed = TRUE AND typescript_compile = TRUE) STORED
);

CREATE INDEX idx_governance_pr ON governance_checks(pr_id, tenant_id);
```

#### Table: `anomaly_alerts`

```sql
CREATE TABLE anomaly_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  event_id UUID REFERENCES provenance_events(id),

  -- Alert info
  severity TEXT CHECK (severity IN ('critical', 'warning', 'info')),
  title TEXT NOT NULL,
  description TEXT,
  root_cause_hypothesis TEXT,  -- from Qwen-Plus
  suggested_action TEXT,

  -- Status
  status TEXT DEFAULT 'new' CHECK (status IN ('new', 'acknowledged', 'resolved', 'false_positive')),
  created_at TIMESTAMP DEFAULT NOW(),
  resolved_at TIMESTAMP,

  -- Escalation
  escalated_to_github_issue BOOLEAN DEFAULT FALSE,
  escalated_to_egos_task BOOLEAN DEFAULT FALSE,
  oncall_notified BOOLEAN DEFAULT FALSE
);
```

---

## Data Flow

### GitHub Push Event → Dashboard Update

```
1. Developer pushes to main branch
   ↓
2. GitHub webhook hits /api/webhooks/github
   ↓
3. FastAPI validates HMAC signature
   ↓
4. Extract: commit_sha, message, author, timestamp
   ↓
5. Enrichment:
   - Generate embedding via Alibaba Dashscope API
   - Code analysis: breaking changes? (AST diff)
   - Security scan: gitleaks + snyk
   ↓
6. Supabase insert: provenance_events + governance_checks
   ↓
7. Realtime broadcast to frontend subscribers
   ↓
8. Dashboard shows new commit in timeline (within 500ms)
   ↓
9. If anomaly detected:
   - Qwen-Plus generates analysis
   - Create anomaly_alerts record
   - Publish to Mycelium event bus → OpenClaw or manual escalation
```

---

## Integration with Ecosystem

### Mycelium Event Bus (Redis Pub/Sub)

Mission Control publishes events to Mycelium for downstream processing:

```
Channel: "mission_control:anomaly"
Message: { anomaly_id, severity, type, pr_url, suggested_action }

Subscribers:
- Oncall service → sends PagerDuty alert
- GitHub automation → creates issue or assigns label
- EGOS task creator → creates task for engineering team
```

### OpenClaw Executor

When governance gate is breached or code needs to be moved:

```
Trigger: "code_move_required" event
Action: Clone source repo → apply transformation → create PR in dest repo
Example: "Move new feature from egos-lab to egos kernel"
```

### EGOS Task Creation

Critical anomalies auto-create tasks:

```
Severity: CRITICAL
→ Create EGOS-XXX task with:
  - Title: "Fix breaking change in API"
  - Description: Link to commit, root cause analysis, suggested action
  - Label: "urgent"
  - Assign: on-call engineer
  - Link: Mission Control dashboard anomaly card
```

---

## Governance Gate Details

**When:** Every PR is created or updated

**Checks:**

1. **SSOT Drift** — Does this PR change SSOT files without updating governance?
   - Scan: `docs/`, `packages/shared/`, `.guarani/`
   - Tool: `governance:check` (lint on expected vs actual)

2. **Security Scan** — Does code contain secrets, PII, or vulnerabilities?
   - Tools: gitleaks, Snyk
   - Block: HIGH/CRITICAL findings

3. **Tests Pass** — Do all tests pass?
   - Tool: GitHub Actions CI
   - Coverage: minimum 80% for new code

4. **TypeScript Compile** — Does code compile?
   - Tool: tsc --noEmit
   - Prevent: type errors in prod

5. **PR Template** — Is description complete?
   - Require: objective, test plan, rollback plan
   - Tool: GitHub Actions (regex check)

**Remediation:**
- Show all failing checks to PR author
- Link to documentation
- Auto-suggest fixes where possible
- Allow override by maintainers (with justification)

---

## Cost Estimate (Monthly)

| Component | Provider | Tier | Cost |
|-----------|----------|------|------|
| Frontend (Vercel) | Vercel | Pro | ~$20 |
| Database (Supabase) | Supabase | Pro | ~$25 |
| Gateway (VPS) | Hetzner | 24GB | ~$24 |
| Embeddings API (Alibaba) | Alibaba Dashscope | 10M tokens | ~$50 |
| Qwen-Plus API | Alibaba Dashscope | On-demand | ~$30 |
| Redis (Mycelium) | Upstash | Starter | ~$0 (free tier) |
| **TOTAL** | | | **~$150/month** |

---

## Roadmap (Phases)

### Phase 1: Foundation (Sprint 2 — 2-3 weeks)
- [x] Supabase schema + RLS policies
- [ ] FastAPI gateway (basic webhooks)
- [ ] React dashboard (static mockup)
- [ ] GitHub webhook integration (push events only)
- [ ] Deploy to kernel.egos.ia.br (Vercel frontend)

### Phase 2: Realtime + Enrichment (Sprint 3 — 2-3 weeks)
- [ ] Supabase Realtime subscriptions in frontend
- [ ] Code analysis (breaking changes detection)
- [ ] Semantic embeddings (pgvector + Alibaba)
- [ ] Anomaly detection (hardcoded rules → ML-based)
- [ ] Qwen-Plus insights generation

### Phase 3: Governance Enforcement (Sprint 4 — 2-3 weeks)
- [ ] Governance gate implementation
- [ ] PR blocking (fail checks → block merge)
- [ ] SSOT drift detection
- [ ] Security scanning integration (gitleaks + Snyk)

### Phase 4: Automation + Escalation (Sprint 5 — 2-3 weeks)
- [ ] Mycelium integration (event publishing)
- [ ] OpenClaw executor (Git automation)
- [ ] Auto-task creation (EGOS task generator)
- [ ] Oncall notifications (PagerDuty webhook)

### Phase 5: Polish + Analytics (Sprint 6 → Ongoing)
- [ ] Performance optimization (query caching, index tuning)
- [ ] PDF export + email reports
- [ ] Advanced search (semantic + keyword)
- [ ] Team dashboards (per-repo, per-author)
- [ ] SLA tracking + trend analysis

---

## Security Considerations

- **Webhook Signature Validation:** HMAC-SHA256 for all incoming webhooks
- **RLS Policies:** Multi-tenant isolation (tenant_id in every table)
- **Secret Management:** API keys in `.env` (not committed)
- **Audit Trail:** All governance actions logged with actor + timestamp
- **Rate Limiting:** Per-IP, per-source, per-action (prevent abuse)
- **PII Masking:** Commit messages may contain sensitive data (auto-mask)

---

## References

- **BLUEPRINT-EGOS Handoff:** `/home/enio/blueprint-egos/HANDOFF.md`
- **EGOS Tasks:** `/home/enio/egos/TASKS.md` (EGOS-116 through EGOS-123)
- **Mycelium Architecture:** `/home/enio/egos/docs/MYCELIUM_NETWORK.md`
- **Supabase RLS Guide:** https://supabase.com/docs/guides/auth/row-level-security
- **FastAPI Webhooks:** https://fastapi.tiangolo.com/advanced/security/

---

**Status:** ✅ Architecture documented | ⏳ Implementation pending (Phase 1 Spring 2)
