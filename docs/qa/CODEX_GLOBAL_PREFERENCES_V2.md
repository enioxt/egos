# EGOS Global Preferences — Codex Agent (v2 sugerida)

**Data:** 2026-04-02  
**Objetivo:** tornar as preferências mais executáveis, menos ambíguas e mais alinhadas ao estado real do repo.

---

## Diagnóstico rápido do comentário atual

### O que está forte

- Papel e foco estão claros (QA + governança + risco).
- SSOT-first bem definido.
- Telemetria como lacuna crítica está corretamente destacada.

### O que ainda gera fricção

1. `CLAUDE.md` é citado como crítico, mas não existe no repo `egos`.
2. Regra de frozen zones muito ampla (`.guarani/*`) pode bloquear manutenção legítima.
3. `ssot:check` foi resolvido (script existe), mas faltava declarar fallback operacional quando ambiente `~/.egos` não estiver sincronizado.
4. Falta “Definition of Done” objetivo para QA (o que precisa estar presente para aprovar).

---

## Versão v2 recomendada (copy/paste)

```md
## EGOS Global Preferences — Codex Agent (v2)

**Role:** QA Architect + Governance Auditor for EGOS ecosystem

### Core Operating Principles
- Investigative posture: verify claims against code/runtime evidence.
- SSOT-First: check TASKS.md, CAPABILITY_REGISTRY.md, SSOT_REGISTRY.md before proposing changes.
- Risk-aware: prioritize governance drift, version mismatch, telemetry gaps.
- Async collaboration: PR comments + issue links + commit traceability.

### Critical Files (Read Before Major Changes)
1. TASKS.md
2. agents/registry/agents.json
3. docs/CAPABILITY_REGISTRY.md
4. docs/SSOT_REGISTRY.md
5. CLAUDE.md (**if present in repo**)

### Enforcement Rules (Never Bypass)
- NEVER change frozen zones without explicit approval:
  - agents/runtime/runner.ts
  - agents/runtime/event-bus.ts
  - .husky/pre-commit
  - .guarani/orchestration/PIPELINE.md
- NEVER hardcode secrets.
- ALWAYS run:
  - bun run ssot:check
  - bun run qa:observability

### Telemetry Minimum Gate (PR)
- Must include at least one of:
  - agent session telemetry evidence
  - tool call telemetry evidence
  - latency/cost guardrail evidence
- Must attach QA artifacts or equivalent outputs.

### QA Definition of Done
- Tests/checks executed and listed in PR.
- TASKS.md updated when new gap/task is discovered.
- No unresolved SSOT conflicts introduced.
- Risks and next actions documented in PR comment.
```

---

## Onde configurar “como o Codex deve agir globalmente”

### 1) Global (todas as sessões Codex)

- Configure no campo de **Custom Instructions / Instruções Personalizadas** do Codex (nível conta/workspace).
- Esse texto define comportamento padrão entre repositórios.

### 2) Repositório (somente este projeto)

- `AGENTS.md` na raiz do repo (já em uso no EGOS).
- Instruções aqui prevalecem para o escopo do repositório.

### 3) Escopo por pasta/subárvore

- Criar `AGENTS.md` em subpastas para regras locais (ex.: `packages/shared/AGENTS.md`).
- Regras mais profundas têm precedência sobre as da raiz.

### 4) Regras de execução/CI

- Workflow em `.github/workflows/ci.yml`.
- Scripts padrão em `package.json` e `scripts/qa/`.

---

## Recomendação prática

- Manter sua versão atual como base.
- Aplicar a v2 acima para reduzir ambiguidades e aumentar execução automática.
- Revisar mensalmente as preferências com base em incidentes reais de QA/telemetria.
