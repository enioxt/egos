# EGOS Ecosystem Classification Registry

> **VERSION:** 1.1.0 | **CREATED:** 2026-03-23 | **UPDATED:** 2026-03-29 | **STATUS:** Active
> **TASK:** EGOS-076
> **SSOT STATUS:** This file IS the canonical product/module classification map

---

## Classification Schema

| Class | Definition | Examples |
|-------|-----------|---------|
| `product` | Actively sold or marketed, has clear ICP and pricing | Guard Brasil, egos.ia.br |
| `standalone_candidate` | Could be its own package/repo — strong enough standalone | `@egos/guard-brasil`, `egos-guard` CLI |
| `candidate` | Good idea, needs PRD + ICP before becoming product | Agent-028 as SaaS, Commons courses |
| `lab` | Active experiment or acquisition surface — not a product yet | egos-lab, gem-hunter |
| `internal_infra` | Dev tooling, CI, governance — powers other things | governance-sync, metrics-tracker |
| `archive` | No longer active — preserved for reference | Old chatbot experiments |
| `discard` | Dead code — no users, no plans | Abandoned scaffolds |

---

## Products

| Name | Class | ICP | Pricing | Repo | Status |
|------|-------|-----|---------|------|--------|
| **EGOS Guard Brasil** | `product` | AI/chatbot developers in Brazil needing LGPD compliance | Free SDK / Paid API+Dashboard | `egos/packages/shared` | ✅ SDK ready, API planned |
| **egos.ia.br** | `product` | Brazilian dev community + early customers | Free (acquisition) | `egos-lab/apps/egos-web` | ✅ Live |
| **EGOS-Inteligencia (br-acc)** | `product` | Law enforcement + public sector investigators | Custom contract | `br-acc` | ✅ Production |

---

## Standalone Candidates

| Name | Class | Rationale | Next Step |
|------|-------|-----------|-----------|
| `@egos/guard-brasil` | `standalone_candidate` | ATRiAN + PII + Public Guard + Evidence Chain bundled — high reuse potential | Publish to npm |
| `egos-guard` CLI | `standalone_candidate` | Terminal tool for Guard Brasil — devtools adoption surface | Add to README install instructions |
| `@egos/shared` | `standalone_candidate` | Core framework utilities — used by 3+ repos already | Already published in workspace; add to npm |
| Cross-session memory | `standalone_candidate` | Supabase-based cross-session AI memory — generic enough | Extract as `@egos/memory` |
| Mycelium reference graph | `standalone_candidate` | Knowledge graph for repo relationships — open-source tool | Extract as `@egos/mycelium` |

---

## Candidates (need PRD before promotion)

| Name | Class | Current State | Gate Required |
|------|-------|--------------|--------------|
| Agent-028 dashboard | `candidate` | UI + data pipeline done, Vercel deploy needed | PRD: ICP (who pays?), pricing model |
| EGOS Commons courses | `candidate` | Marketplace + 2 courses live | PRD: LMS vs hosted video, pricing tiers |
| EGOS Forja | `candidate` | CRM chat backend, multi-tenant | PRD: mobile-first B2B CRM vs AI API |
| 852 (law enforcement chatbot) | `candidate` | Production chatbot with 27 tools | PRD: SaaS licensing model for public sector |
| carteira-livre | `candidate` | Portability engine + AI flows | PRD: monetization beyond custom builds |

---

## Lab (Active Experiments)

| Name | Class | Purpose | Owner |
|------|-------|---------|-------|
| egos-lab | `lab` | App incubator, acquisition platform, agent playground | EGOS team |
| gem-hunter | `lab` | Code discovery agent — lab internal | egos-lab agents |
| report_generator | `lab` | Agent-028 data pipeline — generates dashboard JSON | egos-lab agents |
| archaeology_digger | `lab` | Historical EGOS timeline reconstruction | egos kernel agents |
| Mycelium graph seed | `lab` | Reference graph experiments | egos kernel |

---

## Internal Infrastructure

| Name | Class | Purpose | Repo |
|------|-------|---------|------|
| governance-sync.sh | `internal_infra` | Syncs governance docs across repos | egos/scripts |
| activation-check.ts | `internal_infra` | 42-check kernel health validation | egos/scripts |
| guard.ts CLI | `internal_infra` + `standalone_candidate` | Guard Brasil CLI (dual use) | egos/scripts |
| metrics-tracker.ts | `internal_infra` | AI tool usage and cost tracking | egos/packages/shared |
| telemetry.ts | `internal_infra` | Dual output telemetry (JSON + Supabase) | egos/packages/shared |
| pre-commit hooks | `internal_infra` | gitleaks + tsc + frozen-zones | egos/.husky |
| GitHub Actions CI | `internal_infra` | lint + typecheck + registry lint | egos/.github/workflows |
| governance-sync propagation | `internal_infra` | Cross-repo SSOT sync | egos/scripts |

---

## Archive

| Name | Class | Reason | Last Active |
|------|-------|--------|------------|
| Old egos-lab system map (pre-2026-03) | `archive` | Superseded by kernel SYSTEM_MAP | 2026-02 |
| Early chatbot experiments | `archive` | Superseded by 852 + forja | 2025-Q4 |
| egos-lab capability docs (duplicates) | `archive` | Kernel owns CAPABILITY_REGISTRY | 2026-03 |

---

## Wiring Status

| Surface | TASKS.md | SYSTEM_MAP.md | CAPABILITY_REGISTRY.md |
|---------|----------|---------------|----------------------|
| Guard Brasil | ✅ EGOS-062..064 | ✅ v3.0.0 | ✅ v1.4.0 |
| Ecosystem Classification Registry (this file) | ✅ EGOS-076 | ✅ v3.0.0 | — |
| egos-lab Consolidation Diagnostic | ✅ EGOS-073 | ✅ | — |
| SSOT Registry | ✅ | ✅ v3.0.0 | ✅ v2.0.0 |

---

## Update Protocol

1. Any new product/module proposal → add as `candidate` here first
2. `candidate` → `product` requires: PRD, ICP, pricing, success metric, multi-model review
3. `lab` → `standalone_candidate` requires: evidence of reuse by 2+ repos
4. `standalone_candidate` → `product` requires: first paying customer
5. `archive` items are never deleted — preserved for reference

---

*Maintained by: EGOS Kernel*
*Wired into: TASKS.md, SYSTEM_MAP.md (pending), CAPABILITY_REGISTRY.md (pending)*
*Related: EGOS-076, EGOS-077, EGOS-078*
