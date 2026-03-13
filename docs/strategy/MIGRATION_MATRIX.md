# Kernel-to-Leaf Migration Matrix

> **Version:** 1.0.0 | **Updated:** 2026-03-13
> **Task:** EGOS-052

## Purpose

This document defines the criteria for what belongs in the **kernel** (`egos`)
versus **leaf repos** (`egos-lab`, `carteira-livre`, `br-acc`, etc.).
It prevents scope creep in the kernel and ensures leaf repos stay autonomous.

## Role Definitions

| Role | Description | Examples |
|------|-------------|----------|
| **kernel** | Governance DNA, agent runtime, shared packages, orchestration protocol | `egos` |
| **lab** | Full monorepo with apps, workers, dashboards, and production surfaces | `egos-lab` |
| **leaf** | Independent project that consumes kernel governance via `~/.egos/` | `carteira-livre`, `br-acc`, `forja`, `852` |

## Migration Criteria

### Belongs in Kernel

| Criterion | Example |
|-----------|---------|
| Used by 2+ repos | `llm-provider.ts`, `atrian.ts`, `pii-scanner.ts` |
| Governance/orchestration | `.guarani/`, `PIPELINE.md`, `GATES.md` |
| Agent runtime infrastructure | `runner.ts`, `event-bus.ts`, `cli.ts` |
| Shared type definitions | `types.ts`, `reference-graph.ts` |
| Cross-repo sync scripts | `governance-sync.sh` |
| Meta-prompts (universal) | `universal-strategist.md`, `ecosystem-audit.md` |
| Model routing | `model-router.ts` |
| Repo-role detection | `repo-role.ts`, `egos.config.json` schema |

### Belongs in Lab (egos-lab)

| Criterion | Example |
|-----------|---------|
| Production web apps | `egos-web`, `intelink` |
| Production bots | `telegram-bot`, `agent-commander` |
| Worker infrastructure | Railway worker, Redis queue |
| App-specific agents | `gem-hunter`, `report-generator` |
| Deploy configs | `vercel.json`, Dockerfiles |
| Production databases | Supabase project-specific schemas |
| Nexus Market | Marketplace-specific code |

### Belongs in Leaf Repos

| Criterion | Example |
|-----------|---------|
| Domain-specific business logic | `carteira-livre` portability engine |
| Project-specific APIs | `br-acc` Neo4j queries, OSINT tools |
| Custom chatbot implementations | Each leaf's `/api/chat` endpoint |
| Project-specific CI/CD | Docker compose, deploy scripts |
| Local workflow overrides | Repo-specific `/start` or `/end` extensions |

## Migration Checklist

When moving code from leaf → kernel:

1. **Evidence**: Is it used by 2+ repos? (required)
2. **Zero deps**: Does it use only Node/Bun stdlib? (required)
3. **Generic**: Is it domain-agnostic? (required)
4. **Types**: Are shared types exported from `packages/shared/`?
5. **Tests**: Does it have at least a dry-run validation?
6. **Registry**: If it's an agent, is it in `agents.json`?
7. **Docs**: Is `CAPABILITY_REGISTRY.md` updated?

## Current Migration State

| Module | Origin | Kernel? | Evidence |
|--------|--------|---------|----------|
| ATRiAN validator | 852 | ✅ | `packages/shared/src/atrian.ts` |
| PII scanner | 852 | ✅ | `packages/shared/src/pii-scanner.ts` |
| Conversation memory | 852 | ✅ | `packages/shared/src/conversation-memory.ts` |
| LLM provider | egos-lab | ✅ | `packages/shared/src/llm-provider.ts` |
| Model router | new | ✅ | `packages/shared/src/model-router.ts` |
| Reference graph | new | ✅ | `packages/shared/src/mycelium/reference-graph.ts` |
| Repo-role detection | new | ✅ | `packages/shared/src/repo-role.ts` |
| Rate limiter | egos-lab | ✅ | `packages/shared/src/rate-limiter.ts` |
| Gem Hunter agent | egos-lab | ❌ | Lab-specific, uses Gemini image gen |
| Report Generator | egos-lab | ❌ | Lab-specific, produces HTML reports |
| Session Guard | egos-lab | ❌ | Lab-specific, checks lab-only surfaces |
| SSOT Auditor | egos-lab | 🔄 | Candidate — needs generalization |
| Contract Tester | egos-lab | 🔄 | Candidate — needs API registry abstraction |

## Anti-Patterns

- **Don't**: Move app-specific code to kernel just because it's "useful"
- **Don't**: Create kernel agents that depend on lab infrastructure
- **Don't**: Put deploy configs (Vercel, Railway, Docker) in kernel
- **Don't**: Add Supabase project-specific schemas to kernel
- **Do**: Extract the generic pattern, leave the specific implementation in the leaf
