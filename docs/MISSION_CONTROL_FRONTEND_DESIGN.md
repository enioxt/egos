# Mission Control Frontend — Design & Architecture (EGOS-117)

> **Version:** 1.0.0 DRAFT | **Date:** 2026-03-26 | **Status:** Architecture Phase
> **Owner:** Frontend Architect | **Target:** kernel.egos.ia.br (Vercel)
> **Ticket:** EGOS-117 — Build operator-facing narrative kit

---

## Executive Summary

**Mission Control Frontend** is a real-time observability dashboard for the EGOS ecosystem. It provides:

- **Governance Health Dashboard** — Real-time SSOT compliance, test pass rates, deployment frequency
- **PR/Workflow Status Board** — Cross-repo PR timeline, approval gates, merge blockers
- **Agent Activity Monitor** — Execution timelines, task logs, performance metrics
- **Governance Drift Alerting** — Policy violations, anomalies, auto-triage recommendations

This document defines the complete tech stack, page architecture, data model, and API requirements for phase 1 (MVP).

---

## Part 1: Tech Stack Recommendation

### Decision: React 19 + TypeScript + Vite

**Rationale:**
1. **Alignment with existing EGOS ecosystem** — `apps/commons` and `apps/agent-028-template` already use React 19 + Vite
2. **Low cognitive load** — Team familiar with this stack; no relearning needed
3. **Performance** — Vite dev server (50ms HMR), optimized prod builds
4. **Ecosystem maturity** — Proven patterns for state management, routing, real-time data
5. **Cost efficiency** — Vercel auto-deploy + serverless functions (no runtime cost)

### Alternatives Considered & Rejected

| Framework | Pros | Cons | Decision |
|-----------|------|------|----------|
| **React 19** | Alignment, mature, known patterns | Larger bundle than Svelte | ✅ **CHOSEN** |
| **Svelte 5** | Lightweight, smaller bundle (10-15KB less) | New to team, fewer UI libraries | ❌ Rejected — overkill optimization |
| **Qwik** | Resumability, instant interactivity | Immature, small ecosystem, hard to onboard | ❌ Rejected — too experimental |
| **Vue 3** | Lightweight, simpler template syntax | Non-standard in EGOS ecosystem | ❌ Rejected — ecosystem alignment |
| **Web Components** | Framework-agnostic | Poor DX, verbose boilerplate | ❌ Rejected — not suitable for dashboards |

### Core Dependencies

```json
{
  "dependencies": {
    "react": "^19.2.4",
    "react-dom": "^19.2.4",
    "react-router-dom": "^7.13.2",
    "zustand": "^4.5.0",
    "recharts": "^3.8.0",
    "lucide-react": "^0.577.0",
    "@supabase/supabase-js": "^2.99.3"
  },
  "devDependencies": {
    "vite": "^8.0.1",
    "@vitejs/plugin-react": "^6.0.1",
    "typescript": "~5.9.3",
    "tailwindcss": "^4.2.2",
    "@tailwindcss/vite": "^4.2.2",
    "eslint": "^9.39.4"
  }
}
```

### State Management: Zustand (NOT Redux/Redux Toolkit)

**Why Zustand?**
- Minimal boilerplate (1/10th of Redux)
- Excellent for dashboard real-time updates
- Built-in middleware (subscribe, persist, devtools)
- Perfect match for Mission Control use case: fetch→store→notify→update

**Example Store Shape:**

```typescript
interface MissionControlStore {
  // Repos & Commits
  repos: Repository[];
  commits: CommitEvent[];

  // Governance
  governanceChecks: GovernanceCheck[];
  driftAlerts: DriftAlert[];

  // Agents
  agentExecutions: AgentExecution[];
  agentLogs: AgentLog[];

  // Real-time subscriptions
  isConnected: boolean;

  // Actions
  addCommit: (commit: CommitEvent) => void;
  updateGovernanceCheck: (check: GovernanceCheck) => void;
  setDriftAlert: (alert: DriftAlert) => void;
  setConnected: (connected: boolean) => void;
}
```

### Real-time Data: Supabase Realtime (WebSocket)

**Why NOT GraphQL subscriptions?**
- Supabase Realtime is already in the backend (KERNEL_MISSION_CONTROL.md)
- Native broadcast channels for different topics
- RLS policy-aware (no extra auth layer needed)
- Cost: included in Supabase plan (no extra fees)

**Subscription Pattern:**

```typescript
// Listen to all new commits
supabase
  .channel('commits')
  .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'provenance_events' }, (payload) => {
    store.addCommit(payload.new);
  })
  .subscribe();

// Listen to governance check updates
supabase
  .channel('governance')
  .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'governance_checks' }, (payload) => {
    store.updateGovernanceCheck(payload.new);
  })
  .subscribe();
```

### Charts & Visualizations: Recharts (NOT Plotly/Chart.js)

**Why Recharts?**
- Used in `agent-028-template` already (consistency)
- Composable React components (not wrapper over canvas library)
- Excellent TypeScript support
- Built-in responsive containers
- Perfect for real-time updates (pure React re-render)

**Examples:**

```typescript
// Commit timeline sparkline
<LineChart data={commits}>
  <Line type="monotone" dataKey="count" stroke="#8b5cf6" />
</LineChart>

// Test pass rate trend
<AreaChart data={testMetrics}>
  <Area type="monotone" dataKey="passRate" fill="#10b981" />
</AreaChart>

// Drift detection heatmap (custom Recharts layer)
<ScatterChart data={driftPoints}>
  <Scatter dataKey="severity" fill="#ef4444" />
</ScatterChart>
```

### Styling: Tailwind CSS v4 (NOT CSS-in-JS)

**Why Tailwind?**
- Already in use across `commons` and `agent-028-template`
- @tailwindcss/vite plugin for zero runtime cost
- Dark mode built-in (`dark:` prefix)
- Perfect for rapid dashboard iteration
- Team expertise already exists

---

## Part 2: Page Architecture & Data Flow

### Page Hierarchy

```
/mission-control/
├── / (root redirect to /dashboard)
├── /dashboard (Overview)
│   ├── Health Cards
│   ├── Sparkline Charts
│   ├── Quick Stats
│   └── Recent Activity
├── /commits (Commit Timeline / Firehose)
│   ├── Filters (repo, date range, author, severity)
│   ├── Commit Cards (expandable)
│   ├── Diff Viewer
│   └── Search
├── /anomalies (Anomaly Feed)
│   ├── Severity Filter (critical, warning, info)
│   ├── Anomaly Cards
│   ├── AI Triage Details
│   ├── Action Buttons (escalate, dismiss)
│   └── Trend Analysis
├── /governance (Governance Gate)
│   ├── PR Queue (blocked by checks)
│   ├── Check Status
│   ├── Remediation Links
│   ├── Override Request UI
│   └── Audit Log
├── /agents (Agent Activity)
│   ├── Agent Registry
│   ├── Execution Timeline
│   ├── Agent Logs
│   ├── Performance Metrics
│   └── Status Indicators
└── /insights (AI Insights & Reports)
    ├── Weekly Report (Qwen-Plus)
    ├── Semantic Search
    ├── Trend Charts
    ├── Recommendations
    └── Export (PDF/CSV)
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 19)                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Pages:                                                      │  │
│  │  - Dashboard / Commits / Anomalies / Governance /            │  │
│  │  - Agents / Insights                                         │  │
│  └─────────────────────────────────────────────────────────────┘   │
│                          ↓ (subscriptions)                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Zustand Store (Real-time State)                             │  │
│  │  - repos[] / commits[] / governanceChecks[] / agents[]       │  │
│  │  - Middleware: subscribe, persist, devtools                 │  │
│  └─────────────────────────────────────────────────────────────┘   │
│                          ↓ (REST + WebSocket)                      │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────────┐
        │     Supabase Realtime (WebSocket)   │
        │  (provenance_events, governance_*) │
        └─────────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────────┐
        │      FastAPI Gateway (Python)       │
        │  /api/webhooks/* / /api/governance/ │
        │  /api/openClaw/*                    │
        └─────────────────────────────────────┘
                          ↓
        ┌──────────────────────────────────────────┐
        │      Supabase PostgreSQL Backend         │
        │  Tables:                                 │
        │  - provenance_events (commits/PRs)       │
        │  - semantic_embeddings (pgvector)        │
        │  - governance_checks (SSOT drift)        │
        │  - anomalies (detected issues)           │
        │  - agent_executions (agent logs)         │
        │  - team_overrides (audit trail)          │
        └──────────────────────────────────────────┘
                          ↓
        ┌──────────────────────────────────────────┐
        │     AI/ML Layer (Alibaba Dashscope)      │
        │  - Qwen-Plus (anomaly analysis)          │
        │  - Embeddings (semantic search)          │
        │  - K-means clustering (grouping)         │
        └──────────────────────────────────────────┘
```

### Component Tree

```
App.tsx
├── <Layout>
│   ├── <Header> (nav, user menu, status lights)
│   ├── <Sidebar> (repo filter, date range, quick links)
│   └── <Routes>
│       ├── <DashboardPage>
│       │   ├── <HealthCardsSection>
│       │   │   ├── <ReposHealthCard>
│       │   │   ├── <SSoTComplianceCard>
│       │   │   ├── <TestPassRateCard>
│       │   │   └── <DeploymentFrequencyCard>
│       │   ├── <SparklineChartsSection>
│       │   │   ├── <CommitsPerDayChart>
│       │   │   ├── <TestTrendChart>
│       │   │   └── <ComplianceTrendChart>
│       │   └── <RecentActivityFeed>
│       ├── <CommitsPage>
│       │   ├── <FilterBar>
│       │   │   ├── <RepoFilter>
│       │   │   ├── <DateRangeFilter>
│       │   │   ├── <AuthorFilter>
│       │   │   └── <SeverityFilter>
│       │   ├── <CommitTimeline>
│       │   │   └── <CommitCard> (repeating)
│       │   │       ├── <CommitHeader>
│       │   │       ├── <CommitDiff>
│       │   │       └── <CommitActions>
│       │   └── <SearchBox>
│       ├── <AnomaliesPage>
│       │   ├── <AnomalyFeed>
│       │   │   ├── <AnomalyCard> (critical)
│       │   │   ├── <AnomalyCard> (warning)
│       │   │   └── <AnomalyCard> (info)
│       │   ├── <AnomalyDetails>
│       │   │   ├── <TriageResults> (Qwen-Plus AI)
│       │   │   ├── <RecommendedActions>
│       │   │   └── <EscalationButtons>
│       │   └── <TrendAnalysis>
│       ├── <GovernancePage>
│       │   ├── <PRQueue>
│       │   │   └── <PRCard> (repeating)
│       │   │       ├── <CheckResults>
│       │   │       ├── <RemediationLink>
│       │   │       └── <OverrideUI>
│       │   └── <AuditLog>
│       ├── <AgentsPage>
│       │   ├── <AgentRegistry>
│       │   │   └── <AgentRow> (repeating)
│       │   ├── <ExecutionTimeline>
│       │   │   └── <ExecutionCard> (repeating)
│       │   ├── <AgentLogs>
│       │   │   └── <LogEntry> (repeating)
│       │   └── <PerformanceMetrics>
│       └── <InsightsPage>
│           ├── <WeeklyReportSection> (Qwen-Plus)
│           ├── <SemanticSearch>
│           ├── <TrendCharts>
│           ├── <RecommendationsList>
│           └── <ExportButtons>
└── <RealTimeSubscriber> (background WebSocket)
```

---

## Part 3: Data Model & Schema

### Core Tables (Supabase)

#### `provenance_events` (Commits, PRs, Deploys)

```sql
CREATE TABLE provenance_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id TEXT NOT NULL, -- governance boundary
  repo_id TEXT NOT NULL,
  repo_name TEXT NOT NULL, -- human-readable
  event_type VARCHAR(50), -- 'push', 'pr', 'release'
  event_source VARCHAR(50), -- 'github', 'codex', 'claude-code'

  -- Commit details
  commit_sha TEXT,
  commit_message TEXT,
  author_name TEXT,
  author_email TEXT,
  timestamp TIMESTAMP,

  -- Code analysis
  files_changed INTEGER,
  additions INTEGER,
  deletions INTEGER,
  is_breaking_change BOOLEAN,
  severity VARCHAR(50), -- 'critical', 'warning', 'normal'

  -- Semantic enrichment
  embedding_id UUID REFERENCES semantic_embeddings(id),

  -- Governance
  ssot_compliant BOOLEAN,
  test_pass_rate NUMERIC,

  created_at TIMESTAMP DEFAULT now(),

  CONSTRAINT fk_tenant FOREIGN KEY(tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX idx_provenance_repo_time ON provenance_events(repo_id, timestamp DESC);
CREATE INDEX idx_provenance_severity ON provenance_events(severity);
CREATE POLICY "rls_provenance" ON provenance_events
  USING (tenant_id = current_user_tenant());
```

#### `governance_checks` (Policy Enforcement)

```sql
CREATE TABLE governance_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id TEXT NOT NULL,

  -- PR/Event reference
  event_id UUID REFERENCES provenance_events(id),
  pr_number INTEGER,
  pr_branch TEXT,

  -- Check results
  check_name VARCHAR(100), -- 'ssot_drift', 'test_coverage', 'security_scan'
  check_type VARCHAR(50), -- 'blocking', 'advisory'
  status VARCHAR(50), -- 'pass', 'fail', 'warning'
  details JSONB, -- { errors: [...], remediation: "..." }

  -- Actions
  is_blocked BOOLEAN DEFAULT FALSE,
  override_requested BOOLEAN DEFAULT FALSE,
  override_justification TEXT,
  override_actor TEXT,

  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_governance_status ON governance_checks(status, check_name);
CREATE POLICY "rls_governance" ON governance_checks
  USING (tenant_id = current_user_tenant());
```

#### `anomalies` (Drift & Failures)

```sql
CREATE TABLE anomalies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id TEXT NOT NULL,

  -- Detection
  event_id UUID REFERENCES provenance_events(id),
  anomaly_type VARCHAR(100), -- 'test_failure', 'breaking_change', 'drift'
  severity VARCHAR(50), -- 'critical', 'warning', 'info'
  description TEXT,

  -- AI triage (Qwen-Plus)
  root_cause_hypothesis TEXT,
  suggested_action TEXT,
  confidence_score NUMERIC,

  -- Resolution
  is_resolved BOOLEAN DEFAULT FALSE,
  resolution_notes TEXT,

  created_at TIMESTAMP DEFAULT now(),
  resolved_at TIMESTAMP
);

CREATE INDEX idx_anomalies_unresolved ON anomalies(is_resolved, severity);
CREATE POLICY "rls_anomalies" ON anomalies
  USING (tenant_id = current_user_tenant());
```

#### `agent_executions` (Agent Activity)

```sql
CREATE TABLE agent_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id TEXT NOT NULL,

  -- Agent details
  agent_id TEXT NOT NULL,
  agent_name TEXT NOT NULL,

  -- Execution lifecycle
  status VARCHAR(50), -- 'pending', 'running', 'success', 'failed'
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  duration_ms INTEGER,

  -- Input/Output
  input_task TEXT,
  output_result TEXT,
  error_message TEXT,

  -- Performance
  tokens_used INTEGER,
  cost_estimate NUMERIC,

  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_agent_status_time ON agent_executions(status, started_at DESC);
CREATE POLICY "rls_agents" ON agent_executions
  USING (tenant_id = current_user_tenant());
```

#### `semantic_embeddings` (Search Index)

```sql
CREATE TABLE semantic_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id TEXT NOT NULL,

  -- Source reference
  event_id UUID REFERENCES provenance_events(id),

  -- Vector (pgvector extension required)
  embedding vector(1536), -- Alibaba DashScope embeddings

  -- Metadata
  source_text TEXT,

  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_embeddings_cosine ON semantic_embeddings USING ivfflat (embedding vector_cosine_ops);
CREATE POLICY "rls_embeddings" ON semantic_embeddings
  USING (tenant_id = current_user_tenant());
```

### TypeScript Types

```typescript
// events.ts
export interface CommitEvent {
  id: string;
  repo_id: string;
  repo_name: string;
  commit_sha: string;
  commit_message: string;
  author_name: string;
  timestamp: string;
  files_changed: number;
  severity: 'critical' | 'warning' | 'normal';
  is_breaking_change: boolean;
  test_pass_rate?: number;
  ssot_compliant: boolean;
}

// governance.ts
export interface GovernanceCheck {
  id: string;
  event_id: string;
  pr_number: number;
  check_name: string;
  status: 'pass' | 'fail' | 'warning';
  details: {
    errors: string[];
    remediation?: string;
  };
  is_blocked: boolean;
}

// anomalies.ts
export interface Anomaly {
  id: string;
  event_id: string;
  anomaly_type: string;
  severity: 'critical' | 'warning' | 'info';
  description: string;
  root_cause_hypothesis?: string;
  suggested_action?: string;
  confidence_score?: number;
  is_resolved: boolean;
}

// agents.ts
export interface AgentExecution {
  id: string;
  agent_id: string;
  agent_name: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  started_at: string;
  ended_at?: string;
  duration_ms?: number;
  input_task: string;
  output_result?: string;
  error_message?: string;
  tokens_used: number;
  cost_estimate: number;
}
```

---

## Part 4: API Requirements (FastAPI Gateway)

### Endpoints Needed for Frontend

#### 1. **Commit Timeline**

```http
GET /api/commits?repo_id=egos&limit=50&offset=0&sort=timestamp&order=desc
Authorization: Bearer {jwt_token}

Response:
{
  "data": [CommitEvent, ...],
  "total": 342,
  "hasMore": true
}
```

#### 2. **Governance Status**

```http
GET /api/governance/checks?pr_number=123&status=fail
Authorization: Bearer {jwt_token}

Response:
{
  "pr_number": 123,
  "checks": [GovernanceCheck, ...],
  "is_blocked": true,
  "remediation_url": "https://..."
}
```

#### 3. **Anomalies Feed**

```http
GET /api/anomalies?severity=critical&is_resolved=false
Authorization: Bearer {jwt_token}

Response:
{
  "data": [Anomaly, ...],
  "total": 12,
  "unresolved_count": 8
}
```

#### 4. **Agent Activity**

```http
GET /api/agents?status=running&limit=20
Authorization: Bearer {jwt_token}

Response:
{
  "data": [AgentExecution, ...],
  "total": 156
}

GET /api/agents/{agent_id}/logs?limit=100
Authorization: Bearer {jwt_token}

Response:
{
  "logs": [
    { timestamp: "...", level: "info", message: "..." },
    ...
  ]
}
```

#### 5. **Dashboard Summary**

```http
GET /api/dashboard/summary
Authorization: Bearer {jwt_token}

Response:
{
  "repos_count": 12,
  "commits_24h": 42,
  "anomalies_unresolved": 8,
  "test_pass_rate": 0.94,
  "ssot_compliance": 0.98,
  "deployment_frequency": 24.5,
  "last_deployment": "2026-03-26T15:30:00Z"
}
```

#### 6. **AI Insights (Qwen-Plus)**

```http
POST /api/insights/generate-report
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "period": "week",
  "include_anomalies": true,
  "include_trends": true
}

Response:
{
  "report_id": "uuid",
  "status": "processing",
  "eta_seconds": 30,
  "report_url": "/api/insights/reports/{report_id}"
}
```

#### 7. **Semantic Search**

```http
GET /api/search/semantic?query=database%20performance&limit=10
Authorization: Bearer {jwt_token}

Response:
{
  "results": [
    { event_id: "...", score: 0.92, snippet: "..." },
    ...
  ]
}
```

#### 8. **Governance Override**

```http
POST /api/governance/override
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "pr_number": 123,
  "check_id": "uuid",
  "justification": "Emergency hotfix — security patch",
  "duration_minutes": 60
}

Response:
{
  "override_id": "uuid",
  "expires_at": "2026-03-26T16:30:00Z",
  "approver": "user@example.com"
}
```

### Implementation Notes

- **Auth:** All endpoints require valid JWT from GitHub OAuth (handled by Supabase)
- **Rate Limiting:** 1000 req/min per user, 5000 req/min per tenant
- **Caching:** GET endpoints should support `ETag` + `304 Not Modified`
- **WebSocket:** Supabase Realtime handles subscriptions (no additional REST endpoint needed)
- **Error Handling:** Standard HTTP status codes + JSON error body with `error` and `details` fields

---

## Part 5: Component Architecture Diagram

### High-Level Component Flow

```
User (Operator)
  ↓
[Browser]
  ├─ Zustand Store (local state + subscriptions)
  │  ├─ commits[] → CommitEvent[]
  │  ├─ governanceChecks[] → GovernanceCheck[]
  │  ├─ anomalies[] → Anomaly[]
  │  ├─ agentExecutions[] → AgentExecution[]
  │  └─ setters: addCommit(), updateCheck(), etc.
  │
  ├─ Supabase Client (real-time)
  │  ├─ channel('commits').on('INSERT', ...)
  │  ├─ channel('governance').on('UPDATE', ...)
  │  └─ channel('anomalies').on('INSERT', ...)
  │
  ├─ REST API Client
  │  ├─ GET /api/dashboard/summary
  │  ├─ GET /api/commits?...
  │  ├─ GET /api/governance/checks?...
  │  └─ POST /api/insights/generate-report
  │
  └─ Pages
     ├─ DashboardPage (health overview)
     ├─ CommitsPage (timeline)
     ├─ AnomaliesPage (triage)
     ├─ GovernancePage (gates)
     ├─ AgentsPage (activity)
     └─ InsightsPage (reports)
```

### Example: Anomaly Detection Flow

```
FastAPI Gateway
  ↓ (webhook)
GitHub event (test failure)
  ↓ (process)
Anomaly detection: "test_failure"
  ↓ (store)
INSERT INTO anomalies (event_id, anomaly_type, ...)
  ↓ (realtime broadcast)
Supabase Realtime
  ↓ (WebSocket)
Frontend Zustand store
  ↓ (update)
AnomaliesPage re-renders
  ↓ (user sees)
Anomaly card appears + AI triage badge
  ↓ (user clicks)
POST /api/insights/analyze-anomaly
  ↓ (AI processes)
Qwen-Plus generates root cause + suggestions
  ↓ (store update)
Anomaly details populate
  ↓ (user action)
Click "Escalate to oncall" or "Auto-remediate"
```

---

## Part 6: Feature Breakdown (MVP)

### Phase 1 (Weeks 1-2): Foundation

- [x] Supabase schema + RLS policies (already defined in KERNEL_MISSION_CONTROL.md)
- [ ] React app scaffolding (Vite + Zustand + TypeScript)
- [ ] Layout + header + sidebar components
- [ ] Dashboard page (static mockup)
- [ ] Supabase client + auth integration
- [ ] First real-time subscription (commits channel)

**Deliverables:**
- Working React app deployed to Vercel
- Real-time commit feed from Supabase
- Dashboard showing last 10 commits

### Phase 2 (Weeks 3-4): Core Pages

- [ ] Commits page (full timeline + filters)
- [ ] Governance page (PR queue)
- [ ] Agents page (execution timeline)
- [ ] Anomalies page (basic feed)
- [ ] Chart integration (Recharts)
- [ ] Real-time subscriptions for all tables

**Deliverables:**
- All 5 core pages functional
- Filtering + search working
- Real-time updates across all pages

### Phase 3 (Weeks 5-6): AI Integration

- [ ] Qwen-Plus API calls (insights generation)
- [ ] Anomaly triage (root cause + suggestions)
- [ ] Semantic search (Alibaba embeddings)
- [ ] Weekly report generator
- [ ] AI-driven recommendations

**Deliverables:**
- Insights page with weekly report
- Anomaly details with AI triage
- Semantic search functional

### Phase 4 (Weeks 7-8): Polish + Governance

- [ ] Governance override UI (with audit trail)
- [ ] PDF export (jsPDF + html2canvas)
- [ ] Performance optimization (query caching, lazy loading)
- [ ] Dark mode + accessibility
- [ ] E2E tests (Cypress/Playwright)

**Deliverables:**
- Production-ready dashboard
- Full governance enforcement UI
- Test coverage >80%

---

## Part 7: Technology Decisions & Alternatives

### Decision 1: Zustand over Redux

**Problem:** Need lightweight, composable state management for real-time dashboard

**Options:**
1. **Redux + Redux Toolkit** — Industry standard, but verbose (300+ LOC for store setup)
2. **MobX** — Reactive, good for dashboards, but less popular in team
3. **Zustand** — Minimal, hooks-based, perfect for real-time
4. **Jotai** — Similar to Zustand, slightly more complex API

**Decision:** ✅ **Zustand**

**Rationale:**
- 1/10th boilerplate of Redux
- Excellent WebSocket integration (can subscribe store to realtime)
- Perfect for dashboard: `store.subscribe(() => updateUI())`
- No opinionated folder structure (no decision fatigue)

**Example:**

```typescript
// store.ts (entire store in <50 LOC)
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

interface Store {
  commits: CommitEvent[];
  addCommit: (commit: CommitEvent) => void;
}

export const useStore = create<Store>(
  subscribeWithSelector((set) => ({
    commits: [],
    addCommit: (commit) => set((state) => ({
      commits: [commit, ...state.commits],
    })),
  }))
);

// Listen to all updates
useStore.subscribe(
  (state) => state.commits,
  (commits) => console.log('Commits updated:', commits)
);
```

### Decision 2: Recharts over Plotly/Chart.js

**Problem:** Need composable, React-native charting library for real-time updates

**Options:**
1. **Recharts** — React components, perfect for real-time, used in EGOS already
2. **Plotly.js** — Powerful, but not React-native (wrapper library)
3. **Chart.js** — Popular, good features, but canvas-based (harder to update)
4. **D3.js** — Full power, but steep learning curve, overkill for dashboards
5. **Victory** — Good alternative, but less known in team

**Decision:** ✅ **Recharts**

**Rationale:**
- Already used in `agent-028-template` (no new dependency learning)
- Pure React components (not canvas wrappers)
- Excellent real-time performance (just re-render on data change)
- Built-in responsive containers

### Decision 3: Supabase Realtime over GraphQL Subscriptions

**Problem:** Need real-time data updates for dashboard without polling

**Options:**
1. **Supabase Realtime** — WebSocket, already in architecture, free
2. **GraphQL subscriptions** — Powerful, but adds Apollo complexity
3. **Socket.io** — Good for custom events, but extra infrastructure
4. **SSE (Server-Sent Events)** — Simpler than WebSocket, but unidirectional
5. **Polling** — Simple, but wastes bandwidth

**Decision:** ✅ **Supabase Realtime**

**Rationale:**
- Already used in KERNEL_MISSION_CONTROL.md architecture
- No extra dependencies (included in Supabase plan)
- RLS-aware (security policy enforcement at database level)
- Broadcast channels for topic-based subscriptions
- Cost: included (no extra fees)

### Decision 4: Tailwind CSS v4 over CSS-in-JS

**Problem:** Need consistent, maintainable styling for dashboard

**Options:**
1. **Tailwind CSS** — Utility-first, already in use, great DX
2. **CSS-in-JS (styled-components)** — Dynamic styles, but runtime overhead
3. **Emotion** — Similar to styled-components, smaller bundle
4. **PostCSS** — Lower level, more control, but verbose
5. **Vanilla CSS/SCSS** — Full control, but no reuse

**Decision:** ✅ **Tailwind CSS v4**

**Rationale:**
- Already used in `commons` and `agent-028-template`
- @tailwindcss/vite plugin = zero runtime overhead
- Dark mode support built-in
- Team expertise already exists
- Faster iteration (no build step for style changes)

---

## Part 8: Deployment & DevOps

### Frontend Deployment (Vercel)

```yaml
# vercel.json
{
  "buildCommand": "vite build",
  "outputDirectory": "dist",
  "env": {
    "VITE_SUPABASE_URL": "https://[project].supabase.co",
    "VITE_SUPABASE_KEY": "@SUPABASE_ANON_KEY"
  }
}
```

**CI/CD:**
- Push to `main` → Vercel auto-deploys
- Preview deployments for all PRs
- Environment promotion: staging → production

**Monitoring:**
- Vercel built-in analytics (Core Web Vitals)
- Sentry for error tracking
- LogRocket for session replay (optional)

### Local Development

```bash
cd apps/commons-mission-control
npm run dev  # Start Vite dev server (localhost:5173)
npm run build  # Build for production
npm run lint  # ESLint check
npm run typecheck  # TypeScript check
```

### Environment Variables

```bash
# .env.local
VITE_SUPABASE_URL=https://[project].supabase.co
VITE_SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...
VITE_API_BASE_URL=https://api.egos.ia.br
VITE_ENABLE_INSIGHTS=true
VITE_QWEN_ENABLED=true
```

---

## Part 9: Performance Targets

### Core Web Vitals (Lighthouse)

| Metric | Target | Current | Tool |
|--------|--------|---------|------|
| LCP (Largest Contentful Paint) | < 2.5s | TBD | Vercel Analytics |
| FID (First Input Delay) | < 100ms | TBD | Vercel Analytics |
| CLS (Cumulative Layout Shift) | < 0.1 | TBD | Vercel Analytics |
| TTFB (Time to First Byte) | < 600ms | TBD | Vercel |

### Bundle Size Targets

| Asset | Target | Notes |
|-------|--------|-------|
| JavaScript | < 200KB | After gzip, including React |
| CSS | < 50KB | After gzip, Tailwind |
| Images | < 500KB total | Lazy-loaded charts |
| Total | < 750KB | Initial load budget |

### Real-time Subscription Latency

| Event | Target Latency | Notes |
|-------|----------------|-------|
| Commit push → Dashboard update | < 1s | Supabase Realtime |
| Governance check result → UI | < 500ms | Realtime broadcast |
| Anomaly detection → Alert | < 2s | AI triage may be slower |
| Search query → Results | < 500ms | Cached + indexed |

### Database Query Performance

| Query | Target | Index |
|-------|--------|-------|
| Last 50 commits | < 100ms | idx_provenance_repo_time |
| Governance checks by status | < 100ms | idx_governance_status |
| Unresolved anomalies | < 100ms | idx_anomalies_unresolved |
| Agent executions by status | < 100ms | idx_agent_status_time |

---

## Part 10: Security Considerations

### Authentication & Authorization

- **OAuth:** GitHub OAuth via Supabase Auth (existing)
- **JWT:** All API calls require `Authorization: Bearer {jwt_token}`
- **RLS:** Row-level security by `tenant_id` (multi-tenant isolation)
- **Scopes:** Fine-grained permissions (viewer, commenter, admin)

### Data Privacy

- **PII Masking:** Commit messages may contain sensitive data → auto-mask emails
- **Audit Trail:** All governance overrides logged with actor + timestamp
- **Secret Management:** API keys in `.env.local` (never committed)
- **Rate Limiting:** Prevent abuse (1000 req/min per user)

### WebSocket Security

- **Signature Validation:** All webhook payloads must have valid HMAC-SHA256
- **Channel Authorization:** Supabase Realtime enforces RLS on subscriptions
- **Message Validation:** Reject invalid data structures (schema validation)

### SSRF Prevention

- **URL Validation:** All external links must be whitelisted
- **Diff Viewer:** Sanitize code diffs (prevent XSS)
- **PDF Export:** Use jsPDF library (safe DOM → PDF conversion)

---

## Part 11: Success Metrics (OKRs)

### Objective 1: Real-time Observability

**Key Results:**
- [ ] Dashboard loads in < 2 seconds
- [ ] Commit timeline updates < 1 second after push
- [ ] Anomaly detection latency < 5 seconds
- [ ] 99.9% uptime for Supabase Realtime

### Objective 2: Governance Enforcement

**Key Results:**
- [ ] 100% of PRs validated by governance gate
- [ ] False positive rate < 5% for drift detection
- [ ] Triage time for anomalies < 2 minutes (AI-assisted)
- [ ] Override requests logged + audited (100%)

### Objective 3: Developer Productivity

**Key Results:**
- [ ] Operators can find anomalies in < 30 seconds
- [ ] Root cause analysis (AI triage) accuracy > 80%
- [ ] Semantic search finds relevant commits > 90% precision
- [ ] No manual context-switching needed (all info in dashboard)

### Objective 4: Cost Efficiency

**Key Results:**
- [ ] Keep total monthly cost < $200 (target: $150)
- [ ] Query cost < 10% of Supabase budget
- [ ] Vercel cost < $50/month (within free tier + Pro features)
- [ ] AI inference cost < $50/month (Qwen-Plus on-demand)

---

## Part 12: Open Questions & Dependencies

### Blockers

1. **FastAPI Gateway Implementation** — EGOS-117 depends on `/api/commits`, `/api/governance`, `/api/anomalies` endpoints (KERNEL_MISSION_CONTROL.md Phase 1)
2. **Supabase Schema** — Tables must be created + RLS policies configured before frontend development
3. **GitHub OAuth Setup** — Supabase Auth must be configured with GitHub as OAuth provider
4. **Qwen-Plus API Access** — Alibaba DashScope embeddings + Qwen-Plus must be available

### Questions

1. **Multi-tenancy Model** — Should each EGOS leaf repo be a separate tenant or all under one?
   - _Current assumption:_ One tenant per GitHub organization (EGOS org = 1 tenant)

2. **Audit Trail Retention** — How long to keep override logs + anomaly history?
   - _Proposed:_ 90 days in Supabase, older data archived to S3

3. **Real-time Scaling** — How many concurrent WebSocket connections can Supabase Realtime handle?
   - _Supabase answer:_ Millions of concurrent connections (tested at scale)

4. **Semantic Search Accuracy** — Acceptable precision/recall for finding related commits?
   - _Proposed:_ > 85% precision, > 75% recall (F1 score > 0.8)

5. **AI Triage Confidence Threshold** — When should Qwen-Plus suggestion be marked as "high confidence"?
   - _Proposed:_ confidence_score > 0.8 = high, 0.5-0.8 = medium, < 0.5 = low

### Dependencies

- EGOS-116: Presentation System (provides identity/visual guidelines for dashboard)
- EGOS-118: Reproducible demo lane (needs Mission Control frontend as live demo)
- EGOS-119: Benchmark scorecard (needs metrics dashboard from Mission Control)

---

## Part 13: Next Steps

### Immediate (This Week)

1. [ ] **Approve this design document** — Confirm tech stack, data model, API contracts
2. [ ] **Create Supabase schema** — Tables + RLS policies (copy from KERNEL_MISSION_CONTROL.md)
3. [ ] **Set up repository** — `apps/commons-mission-control/` with Vite + React scaffolding
4. [ ] **GitHub OAuth setup** — Configure Supabase Auth with GitHub provider

### Short Term (Sprint 1 — Weeks 1-2)

1. [ ] **Phase 1 implementation** — Supabase integration + auth + Zustand store
2. [ ] **First page** — Dashboard with static mockup + real-time commit feed
3. [ ] **Layout components** — Header, sidebar, main content area
4. [ ] **Vercel deployment** — Auto-deploy from GitHub main branch

### Medium Term (Sprint 2-3 — Weeks 3-6)

1. [ ] **Core pages** — Commits, Governance, Agents, Anomalies
2. [ ] **Real-time subscriptions** — All tables connected via Supabase Realtime
3. [ ] **Charting** — Recharts integration for trends + metrics
4. [ ] **API integration** — /api/dashboard, /api/commits, /api/governance endpoints

### Long Term (Sprint 4-5+ — Weeks 7+)

1. [ ] **AI integration** — Qwen-Plus insights + semantic search
2. [ ] **Governance enforcement** — Override UI + audit trail
3. [ ] **Performance optimization** — Query caching, lazy loading, bundle optimization
4. [ ] **Polish + Testing** — Dark mode, accessibility, E2E tests, production readiness

---

## Conclusion

Mission Control Frontend provides **operator-facing real-time observability** for the EGOS ecosystem. By combining **React 19 + Zustand + Supabase Realtime + Recharts**, we get a lightweight, maintainable dashboard that aligns with existing EGOS tech choices and scales to millions of events.

The architecture is **phased**, **cost-efficient** (~$150/month), and **operator-first** — designed for quick anomaly detection, root cause analysis, and governance enforcement without cognitive overload.

---

## Appendix A: File Structure

```
apps/commons-mission-control/
├── src/
│   ├── components/
│   │   ├── Dashboard/
│   │   │   ├── HealthCards.tsx
│   │   │   ├── SparklineCharts.tsx
│   │   │   └── RecentActivity.tsx
│   │   ├── Commits/
│   │   │   ├── CommitTimeline.tsx
│   │   │   ├── FilterBar.tsx
│   │   │   └── CommitCard.tsx
│   │   ├── Anomalies/
│   │   │   ├── AnomalyFeed.tsx
│   │   │   ├── AnomalyCard.tsx
│   │   │   └── TriageDetails.tsx
│   │   ├── Governance/
│   │   │   ├── PRQueue.tsx
│   │   │   ├── CheckResults.tsx
│   │   │   └── OverrideUI.tsx
│   │   ├── Agents/
│   │   │   ├── AgentRegistry.tsx
│   │   │   ├── ExecutionTimeline.tsx
│   │   │   └── PerformanceMetrics.tsx
│   │   ├── Insights/
│   │   │   ├── WeeklyReport.tsx
│   │   │   ├── SemanticSearch.tsx
│   │   │   └── TrendCharts.tsx
│   │   ├── Layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   └── Common/
│   │       ├── Loading.tsx
│   │       ├── ErrorBoundary.tsx
│   │       └── Modal.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Commits.tsx
│   │   ├── Anomalies.tsx
│   │   ├── Governance.tsx
│   │   ├── Agents.tsx
│   │   └── Insights.tsx
│   ├── lib/
│   │   ├── store.ts (Zustand)
│   │   ├── supabase.ts (client)
│   │   ├── api.ts (REST client)
│   │   ├── types.ts (TypeScript interfaces)
│   │   ├── utils/
│   │   │   ├── formatting.ts
│   │   │   ├── filters.ts
│   │   │   └── validators.ts
│   │   └── hooks/
│   │       ├── useCommits.ts
│   │       ├── useGovernance.ts
│   │       ├── useAnomalies.ts
│   │       └── useAgent.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
├── .env.example
└── README.md
```

---

**Document Version:** 1.0.0 DRAFT
**Author:** Frontend Architect
**Date:** 2026-03-26
**Status:** Ready for review & approval
**Next Gate:** Tech lead sign-off + Supabase schema creation
