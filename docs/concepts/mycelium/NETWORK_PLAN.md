# 🍄 Mycelium Network — Complete Integration Plan

> **Version:** 2.1.0 | **Updated:** 2026-03-08
> **Status:** Phase 1 (Local Event Bus) LIVE · Phase 2 (Distributed Bridge) PARTIAL/UNVERIFIED
> **Concept:** The "Fungal Root System" — invisible infrastructure connecting all EGOS agents, apps, and services.

---

## 1. Current State (What Exists)

Before reading this plan, keep the canonical separation from `docs/knowledge/MYCELIUM_OVERVIEW.md`:

- **Runtime Bus** = `agents/runtime/event-bus.ts`
- **Bridge / PoC** = `packages/shared/src/mycelium/node.ts` + `scripts/mycelium/test-poc.ts`
- **Snapshot / Dashboard** = `apps/egos-web/src/lib/mycelium.ts` + `/api/mycelium-stats`
- **Reference Graph** = `packages/shared/src/mycelium/reference-graph.ts`

| Layer | Implementation | Status |
|-------|---------------|--------|
| **Event Bus** | `agents/runtime/event-bus.ts` — In-memory, sync, TypeScript-native | ✅ LIVE |
| **Worker** | `agents/worker/index.ts` — Railway + Redis queue | ✅ LIVE (24/7) |
| **Dashboard UI** | `MyceliumDashboard.tsx` — Snapshot projection, ZKP planned state, Inspector | ✅ LIVE (snapshot-based, not live mesh) |
| **Stats API** | `apps/egos-web/api/mycelium-stats.ts` — Evidence-based topology snapshot | ✅ LIVE |
| **Reference Graph** | `packages/shared/src/mycelium/reference-graph.ts` — Canonical topology/reporting map | ✅ LIVE |
| **Harvester** | `scripts/disseminate.ts` — Knowledge extraction | ✅ LIVE |
| **Registered Agents** | `agents/registry/agents.json` | ✅ LIVE (count changes with registry) |

### Current Event Flow
```
Agent → MyceliumBus.emit() → In-memory dispatch → JSONL audit trail
                                ↓
                    Orchestrator aggregates results
                                ↓
                    Worker (Railway) processes tasks via Redis
```

### Limitation: No cross-process communication
The Event Bus is in-memory only. Vercel serverless functions, Railway workers, and the frontend dashboard do not yet share verified real-time Mycelium events in production.

### Limitation: Reference Graph Is Not the Event Stream
The reference graph is already canonical for topology/reporting, but it does not mean the distributed event mesh is live. It maps what exists and what is planned; it does not replace runtime evidence.

---

## 2. Target Architecture (Phase 2)

### 2.1. Redis Pub/Sub as Distributed Backbone

**Why Redis over NATS?** We already run Redis on Railway for the worker queue. Adding Pub/Sub to the same Redis instance = zero new infrastructure cost.

```
┌─────────────┐     ┌─────────────────────┐     ┌──────────────┐
│  Vercel API  │────▶│   Redis Pub/Sub      │◀────│ Railway      │
│  (egos-web)  │     │   (Message Broker)   │     │ Worker       │
└─────────────┘     │                     │     └──────────────┘
       │            │  Channels:           │            │
       │            │  mycelium:events     │            │
       │            │  mycelium:agents     │            │
       │            │  mycelium:zkp        │            │
       │            └──────────┬──────────┘            │
       │                       │                        │
       ▼                       ▼                        ▼
┌─────────────┐     ┌─────────────────────┐     ┌──────────────┐
│  Supabase    │     │  Dashboard (SSE)     │     │ Shadow Nodes │
│  (Persist)   │     │  Real-time events    │     │ (ZKP Verify) │
└─────────────┘     └─────────────────────┘     └──────────────┘
```

### 2.2. Event Schema (Zod-validated)

```typescript
// packages/shared/mycelium/schema.ts
import { z } from 'zod';

export const MyceliumEventSchema = z.object({
  id: z.string().uuid(),
  topic: z.string().regex(/^egos\.\w+\.\w+(\.\w+)?$/),
  source: z.string(),           // "worker", "vercel", "agent:ssot-auditor"
  correlationId: z.string(),
  timestamp: z.string().datetime(),
  payload: z.unknown(),
  zkpProof: z.string().optional(),  // ZKP signature when applicable
  metadata: z.record(z.unknown()).optional(),
});

// Well-known topics
export const TOPICS = {
  // Agent lifecycle
  'egos.agent.started':      'Agent execution began',
  'egos.agent.completed':    'Agent execution finished',
  'egos.agent.failed':       'Agent execution failed',
  
  // Security
  'egos.security.finding':   'Security vulnerability detected',
  'egos.security.secret':    'Secret/credential leak detected',
  'egos.security.jailbreak': 'Prompt injection attempt blocked',
  
  // Audit
  'egos.audit.queued':       'Audit task added to queue',
  'egos.audit.completed':    'Audit analysis finished',
  'egos.audit.report':       'Audit report generated',
  
  // Consciousness Tools
  'egos.consciousness.report': 'User report generated',
  'egos.consciousness.shared': 'Report shared externally',
  
  // ETHIK Token
  'egos.ethik.mint':         'ETHIK tokens minted',
  'egos.ethik.transfer':     'ETHIK tokens transferred',
  'egos.ethik.reward':       'Contribution reward issued',
  
  // Knowledge
  'egos.knowledge.harvested': 'New knowledge extracted',
  'egos.knowledge.pattern':   'Pattern detected in codebase',
  
  // Network Health
  'egos.network.heartbeat':  'Node health check',
  'egos.network.zkp.verify': 'ZKP proof verification',
  'egos.network.node.join':  'New node joined network',
} as const;
```

---

## 3. Zero-Knowledge Proofs (ZKP) — The Shadow Node Protocol

### 3.1. Why ZKP Matters for EGOS

| Use Case | Without ZKP | With ZKP |
|----------|-------------|----------|
| **Audit Reports** | Anyone can fake a report | Cryptographic proof the report was generated by a real agent |
| **User Contributions** | Trust-based attribution | Verified contribution without revealing identity |
| **ETHIK Rewards** | Admin can manipulate scores | Mathematically verifiable fair distribution |
| **Data Validation** | Central authority validates | Any node can verify without seeing raw data |
| **Agent Identity** | Simple API keys | Agents prove they're authorized without exposing credentials |

### 3.2. ZKP Implementation Strategy

**Library:** `snarkjs` (Groth16) + `circom` circuits

#### Circuit 1: Report Authenticity Proof
```
// Proves: "This report was generated by an authorized EGOS agent"
// Without revealing: Which agent, which model, which API key

Input (private): agent_id, api_key_hash, model_used, timestamp
Input (public):  report_hash, system_version
Output:          proof (valid/invalid)
```

#### Circuit 2: Contribution Verification
```
// Proves: "This user made N contributions to EGOS"
// Without revealing: Which commits, which files, user identity

Input (private): commit_shas[], user_id, contribution_details
Input (public):  contribution_count, repo_hash
Output:          proof (valid/invalid)
```

#### Circuit 3: ETHIK Token Distribution Fairness
```
// Proves: "The ETHIK distribution follows the Sacred Math formula"
// Without revealing: Individual allocations

Input (private): allocations[], formula_params
Input (public):  total_distributed, gini_coefficient
Output:          proof (fair/unfair)
```

### 3.3. Shadow Node Architecture

Shadow Nodes are lightweight verification nodes that:
1. **Subscribe** to `egos.network.zkp.verify` events
2. **Validate** ZKP proofs without seeing raw data
3. **Publish** verification results to the network
4. **Earn** ETHIK tokens for valid verifications

```typescript
// Shadow Node lifecycle
interface ShadowNode {
  id: string;              // Deterministic hash (not wallet address)
  publicKey: string;       // For ZKP verification
  status: 'online' | 'verifying' | 'flagged';
  uptime: number;          // Percentage
  proofsVerified: number;  // Total proofs validated
  ethikEarned: number;     // Tokens earned through verification
  lastProof: string;       // ISO timestamp of last proof
  stakingAmount: number;   // ETHIK staked (skin in the game)
}
```

---

## 4. Agent Integration Map

### 4.1. All 15 Agents → Mycelium Events

| Agent | Emits | Subscribes To |
|-------|-------|---------------|
| **orchestrator** | `egos.agent.*` | — (root controller) |
| **ssot-auditor** | `egos.audit.completed`, `architecture.ssot_violation` | `egos.audit.queued` |
| **security-scanner** | `egos.security.finding`, `security.secret` | `egos.audit.queued` |
| **contract-tester** | `qa.contract_fail` | `egos.audit.queued` |
| **integration-tester** | `qa.integration_result` | `egos.audit.queued` |
| **regression-watcher** | `qa.regression` | `egos.agent.completed` |
| **dead-code-detector** | `qa.dead_code` | `egos.audit.queued` |
| **dep-auditor** | `architecture.dep_conflict` | `egos.audit.queued` |
| **auth-roles-checker** | `security.auth_issue` | `egos.audit.queued` |
| **ai-verifier** | `egos.security.jailbreak` | `egos.audit.queued` |
| **showcase-writer** | `egos.knowledge.harvested` | `egos.audit.completed` |
| **ui-designer** | `egos.ui.mockup_generated` | `egos.audit.queued` |
| **domain-explorer** | `egos.knowledge.pattern` | `egos.audit.queued` |
| **social-media** | `egos.social.post_created` | `egos.audit.completed` |
| **living-laboratory** | `egos.experiment.result` | `egos.knowledge.pattern` |

### 4.2. Cross-App Event Flow

```
Vercel (egos-web)                    Railway (Worker)
├─ POST /api/run-audit ──────────▶ Redis Queue ──▶ Agent Execution
│                                                        │
│  POST /api/consciousness ─────▶ Redis Pub/Sub          │
│        │                          │                     │
│        ▼                          ▼                     ▼
│  Supabase (persist report)    Dashboard (SSE)    Mycelium Events
│                                                        │
│  GET /api/mycelium/events ◀── Redis Subscribe ◀────────┘
│        │
│        ▼
│  MyceliumDashboard.tsx (real-time updates)
```

---

## 5. Implementation Phases

### Phase 1: Foundation ✅ DONE
- [x] MyceliumBus class with typed events
- [x] JSONL audit trail
- [x] Topic matching with wildcards
- [x] Agent registry wired as the authoritative count source
- [x] Worker on Railway with Redis queue
- [x] Dashboard UI using evidence-based snapshot instead of simulated live mesh
- [x] Canonical reference graph seed in `packages/shared/src/mycelium/reference-graph.ts`

### Phase 2: Real-Time Bridge (CURRENT)
- [ ] **API endpoint** `/api/mycelium/events` — SSE stream from Redis
- [x] **API endpoint** `/api/mycelium-stats` — Honest snapshot of declared topology and observed signals
- [ ] **Worker integration** — Worker publishes events to Redis Pub/Sub
- [x] **Dashboard wiring** — MyceliumDashboard fetches snapshot data
- [ ] **Dashboard wiring** — real-time events stream beyond local JSONL snapshots
- [ ] **Supabase table** `mycelium_events` — Persistent event storage

### Phase 3: ZKP Integration
- [ ] Install `snarkjs` + compile circom circuits
- [ ] Report Authenticity circuit (Circuit 1)
- [ ] Shadow Node registration API
- [ ] Proof verification in worker pipeline
- [ ] Dashboard: real ZKP node status

### Phase 4: Full Mesh
- [ ] Cross-app event routing (Intelink ↔ EGOS ↔ Eagle Eye)
- [ ] ETHIK reward system connected to verified events
- [ ] Shadow Node staking mechanism
- [ ] P2P node discovery (optional, post-MVP)

---

## 6. API Design

### GET /api/mycelium/events (SSE)
```
Returns: Server-Sent Events stream
Query: ?topic=egos.agent.*&since=2026-02-26T00:00:00Z

data: {"id":"...","topic":"egos.agent.completed","source":"worker","payload":{...}}
data: {"id":"...","topic":"egos.security.finding","source":"security-scanner","payload":{...}}
```

### GET /api/mycelium/stats
```json
{
  "network": {
    "nodesOnline": 4,
    "totalEvents24h": 1247,
    "avgLatencyMs": 12,
    "uptime": 99.9
  },
  "agents": {
    "active": 15,
    "lastRun": "2026-02-26T10:42:15Z",
    "totalRuns24h": 48
  },
  "zkp": {
    "proofsVerified": 8492,
    "validityRate": 99.5,
    "shadowNodes": 14,
    "networkIntegrity": 100
  }
}
```

### POST /api/mycelium/verify (ZKP)
```json
{
  "proof": "0x7f...a9c2",
  "publicInputs": ["report_hash", "system_version"],
  "circuitId": "report_authenticity_v1"
}
// Response: { valid: true, verifiedBy: "shadow_node_alpha" }
```

---

## 7. Database Schema

```sql
-- Persistent event storage for the Mycelium Network
CREATE TABLE mycelium_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic TEXT NOT NULL,
  source TEXT NOT NULL,
  correlation_id TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}',
  zkp_proof TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_mycelium_topic ON mycelium_events(topic);
CREATE INDEX idx_mycelium_created ON mycelium_events(created_at DESC);

-- Shadow Node registry
CREATE TABLE mycelium_shadow_nodes (
  id TEXT PRIMARY KEY,
  public_key TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'online',
  uptime_pct NUMERIC(5,2) DEFAULT 0,
  proofs_verified INTEGER DEFAULT 0,
  ethik_earned NUMERIC(18,8) DEFAULT 0,
  staking_amount NUMERIC(18,8) DEFAULT 0,
  last_proof_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE mycelium_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE mycelium_shadow_nodes ENABLE ROW LEVEL SECURITY;

-- Public read for transparency
CREATE POLICY "Public read mycelium_events"
  ON mycelium_events FOR SELECT USING (true);
CREATE POLICY "Public read shadow_nodes"
  ON mycelium_shadow_nodes FOR SELECT USING (true);
```

---

## 8. Why This Matters

The Mycelium Network transforms EGOS from a **collection of tools** into a **living organism**:

1. **Transparency:** Every agent action is an auditable event
2. **Trustlessness:** ZKP proves data validity without central authority
3. **Composability:** New agents plug in by subscribing to topics
4. **Resilience:** Distributed events survive serverless cold starts
5. **Incentive Alignment:** Shadow Nodes earn ETHIK for verification work

> *"Just as fungal networks make forests resilient by connecting trees, the Mycelium Network makes EGOS resilient by connecting agents."*

---

## 9. Files Reference

| File | Purpose |
|------|---------|
| `agents/runtime/event-bus.ts` | Core MyceliumBus class |
| `agents/worker/index.ts` | Railway worker (Redis queue) |
| `apps/egos-web/src/components/MyceliumDashboard.tsx` | Network dashboard UI |
| `apps/egos-web/src/components/MyceliumDashboard.css` | Dashboard styles |
| `docs/plans/tech/MYCELIUM_NETWORK.md` | This plan |
| `docs/knowledge/MYCELIUM_OVERVIEW.md` | Consolidated overview |
| `docs/agentic/HANDOFF_MYCELIUM.md` | Agent-to-agent handoff prompt |
