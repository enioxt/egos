# EGOS Operator Map

> **VERSION:** 1.0.0 | **UPDATED:** 2026-03-29
> **Purpose:** 10-second founder-grade control plane view — what runs, where, how to check it

---

## What We Are Building

```
@egos/guard-brasil  ←  Brazilian AI safety layer (flagship)
npm install @egos/guard-brasil

guard.inspect(llmOutput) → { safe, output, atrian, masking, evidenceChain }
```

**Revenue model:** Free SDK (npm) → Paid API (R$199/mo) → Enterprise (custom)

---

## Live Surfaces

| Surface | Status | Check |
|---------|--------|-------|
| `@egos/guard-brasil` npm package | PENDING PUBLISH | `cd packages/guard-brasil && npm publish --access public` |
| `egos` kernel (this repo) | ACTIVE | `bun run typecheck && bun run agent:lint` |
| EGOS-Inteligência (br-acc) | PROOF CASE | runs on VPS |

---

## Control Plane Commands

```bash
# Health
bun run typecheck              # TypeScript — 0 errors required
bun run agent:lint             # Agent registry contract — all pass
bun run governance:check       # SSOT drift — kernel vs ~/.egos

# Tests
bun test packages/guard-brasil/src/guard.test.ts   # 15/15 must pass
bun test packages/shared/src/__tests__/

# Agents
bun run agent:list             # list all registered agents
bun run agent:run <id> dry_run # run any agent in safe mode

# Sync
bun run governance:sync:exec   # push kernel governance to ~/.egos
```

---

## Architecture (one view)

```
egos/ (kernel)
├── packages/
│   ├── guard-brasil/     ← FLAGSHIP — @egos/guard-brasil
│   │   ├── ATRiAN        ← ethical validation (PT-BR)
│   │   ├── PII Scanner   ← CPF, RG, MASP, REDS, processo
│   │   ├── Public Guard  ← LGPD masking + disclosure
│   │   └── Evidence Chain← audit hash + claim traceability
│   └── shared/           ← reusable modules (consumed by leaf repos)
├── agents/               ← 13 governance agents (all manual/T0)
└── docs/governance/      ← contracts (this map, new-project gate, etc.)

leaf repos (consumers)
├── egos-lab/             ← apps, demos, distribution
├── EGOS-Inteligência/    ← proof case (br-acc, police/judicial)
├── carteira-livre/       ← WhatsApp bot
└── forja/                ← ERP/chat API
```

---

## Decision Log (last 5 significant decisions)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-29 | Guard Brasil stays in monorepo | npm-standalone already; repo extraction adds overhead before users |
| 2026-03-29 | Agent Claim Gate enforced | `bun run agent:lint` — all 13 agents pass contract |
| 2026-03-29 | No new flagship until Guard Brasil on npm | Gate documented in NEW_PROJECT_GATE.md |
| 2026-03-23 | Guard Brasil = primary product | ECOSYSTEM_PRODUCT_VERDICT_2026-03.md |
| 2026-03-23 | Free SDK + paid API model | FREE_VS_PAID_SURFACE.md |

---

## What's Blocked (requires action)

| Item | Blocker | Who |
|------|---------|-----|
| Guard Brasil on npm | `npm login` + `npm publish` | Enio |
| egos-lab consolidation (EGOS-074) | Requires egos-lab repo access | Enio |
| santiago onboarding (EGOS-069) | Requires santiago repo access | Enio |
| Pre-commit agent:lint integration (EGOS-079) | Frozen zone — needs explicit approval | Enio |

---

## What's Ready to Ship

| Item | Command | Status |
|------|---------|--------|
| `@egos/guard-brasil` | `npm publish --access public` from `packages/guard-brasil/` | READY |
| Agent lint gate | `bun run agent:lint` | ACTIVE |
| Governance contracts | `docs/governance/` | COMPLETE |
| 13 agents | `bun run agent:list` | REGISTERED + CONTRACT-COMPLIANT |

---

## Governance Docs Index

| Doc | What it governs |
|-----|----------------|
| `docs/governance/AGENT_CLAIM_CONTRACT.md` | What can be called an agent, proof fields |
| `docs/governance/LLM_ORCHESTRATION_MATRIX.md` | Which AI tool for which task |
| `docs/governance/NEW_PROJECT_GATE.md` | Gate before creating any new product |
| `docs/governance/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` → `docs/strategy/` | Surface classification |
| `docs/governance/WORKTREE_CONTRACT.md` | Branch naming, lifecycle, merge gates |
| `docs/governance/LINEAR_SYNC_CONTRACT.md` | TASKS.md ↔ GitHub Issues sync |
| `docs/governance/QA_LOOP_CONTRACT.md` | How to verify a change is done |
| `docs/governance/SYSTEM_MAP_CONTROL_PLANE.md` | System map freshness rules |

---

*Single source: `egos/docs/OPERATOR_MAP.md`*
*Update: after any significant architectural decision or new surface*
