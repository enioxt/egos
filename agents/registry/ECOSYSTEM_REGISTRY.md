# EGOS Agent Ecosystem Registry — SSOT Master
<!-- version: 1.0.0 | updated: 2026-03-31 | maintainer: egos kernel -->

> **SSOT único.** Este arquivo é a fonte de verdade de todo ecossistema EGOS.  
> Kernel tools em `agents.json`. Agentes de leaf repos declarados aqui com referência canônica.  
> **Regra:** nenhum agente existe oficialmente sem entrada aqui.

---

## Resumo Executivo

| Categoria | Count | Repos |
|-----------|-------|-------|
| 🤖 **True Agents** (loop 24/7) | **5** | egos-lab |
| 🔧 **CLI Tools** (one-shot, manual) | **15** | egos (kernel) |
| 🛠️  **Lab Tools** (scripts/orchestrators) | **22** | egos-lab |
| 🔬 **Research Loop** | **1** | egos-lab |
| 💀 **Dormant / Broken** | **3** | egos-lab |
| **TOTAL** | **46** | |

---

## 🤖 TRUE AGENTS — Loop Contínuo com Side-Effects

> Critério: roda em background, persiste estado, tem side-effects reais (Telegram, DB, FS).

| ID | Repo | Intervalo | Trigger | Side-Effects | Telemetria | Linhas | Status |
|----|------|-----------|---------|--------------|------------|--------|--------|
| `uptime-monitor` | egos-lab | 5 min | cron | Telegram alerts, `status.json`, `alerts.jsonl` | stdout JSONL | 303 | ✅ active |
| `quota-guardian` | egos-lab | 15 min | cron | Telegram alerts, `status.json`, `alerts.jsonl` | stdout JSONL | 491 | ✅ active |
| `drift-sentinel` (lab) | egos-lab | 6 h | cron | `drift-report.json`, Telegram | stdout JSONL | 358 | ✅ active |
| `etl-orchestrator` | egos-lab | 1 h | cron | Pipeline br-acc, `etl-status.json` | stdout JSONL | 330 | ✅ active |
| `autoresearch` | egos-lab | manual loop | CLI `--max-iterations N` | commits código, `results.tsv`, `program.md` | stdout TSV | 414 | ✅ active |

### Observabilidade dos True Agents

Todos escrevem estado em `docs/<agent-id>/status.json` e alertas em `alerts.jsonl`.  
Formato de telemetria: JSONL com campos `timestamp`, `agent_id`, `status`, `latency_ms`.  
Não há dashboard centralizado — ver [P1 abaixo](#roadmap).

---

## 🔧 KERNEL TOOLS — CLI One-Shot (egos repo)

> Source: `/home/enio/egos/agents/registry/agents.json` v2.0.0  
> Entrypoints: `agents/agents/*.ts` — invocados via `bun agents/cli.ts run <id> --dry`

| ID | Área | Função | Linhas | Runtime Proof | Status |
|----|------|--------|--------|---------------|--------|
| `ssot_auditor` | architecture | AST scan TypeScript+Python, type drift detection, codemod plans | 3075 | `bun agents/agents/ssot-auditor.ts --dry-run --target .` | ✅ active |
| `ssot_fixer` | architecture | Aplica codemods safe do ssot_auditor (EXACT/RELAXED drift) | 227 | `bun agents/agents/ssot-fixer.ts --dry-run` | ✅ active |
| `drift_sentinel` | governance | Docs vs live system state, TASKS.md vs git, registry vs filesystem | 358 | `bun agents/agents/drift-sentinel.ts --dry-run` | ✅ active |
| `dep_auditor` | architecture | Conflitos de versão, dev deps erradas, deps não usadas | 247 | `bun agents/agents/dep-auditor.ts --dry-run --target .` | ✅ active |
| `archaeology_digger` | knowledge | Reconstrói lineage completo do EGOS via git+registries+handoffs | 417 | `bun agents/agents/archaeology-digger.ts --dry-run` | ✅ active |
| `chatbot_compliance_checker` | qa | Checa módulos obrigatórios definidos em CHATBOT_SSOT | 54 | `bun agents/agents/chatbot-compliance-checker.ts --target ../852` | ✅ active |
| `dead_code_detector` | qa | Dead exports, orphan files, empty stubs em TypeScript | 237 | `bun agents/agents/dead-code-detector.ts --dry-run --target .` | ✅ active |
| `capability_drift_checker` | governance | Repo vs kernel capabilities, governance files, workflows, security | 205 | `bun agents/agents/capability-drift-checker.ts --target ../852` | ✅ active |
| `context_tracker` | observability | CTX score 0–280, zone emoji, recomenda `/end` quando CTX>180 | 156 | `bun agents/agents/context-tracker.ts` | ✅ active |
| `gtm_harvester` | knowledge | Scan GitHub públicos para GTM/market strategy artifacts | 143 | `bun agents/agents/gtm-harvester.ts --dry-run` | ✅ active |
| `aiox_gem_hunter` | knowledge | Scan SynkraAI/aiox-core para orchestration gems | 197 | `bun agents/agents/aiox-gem-hunter.ts --dry-run` | ✅ active |
| `framework_benchmarker` | knowledge | Benchmark MASA + competitors, produz keep/drop guidance | 116 | `bun agents/agents/framework-benchmarker.ts --dry-run` | ✅ active |
| `mastra_gem_hunter` | knowledge | Scan mastra-ai/mastra para workflow/eval/MCP patterns | 101 | `bun agents/agents/mastra-gem-hunter.ts --dry-run` | ✅ active |
| `mcp_router` | infrastructure | Routing inteligente para MCP servers (Supabase, EXA, Git, etc.) | 205 | `bun agents/agents/mcp-router.ts --dry-run` | ✅ active |
| `spec_router` | governance | Orchestração spec-pipeline review: analyst→pm→architect→sm | 150 | `bun agents/agents/spec-router.ts --dry-run` | ✅ active |

**Comandos:**
```bash
cd /home/enio/egos
bun agent:list                              # lista todos
bun agent:run <id> --dry                    # dry run
bun agent:run context_tracker --dry         # CTX score (sempre rodar antes de tasks longas)
bun agent:lint                              # valida registry
```

---

## 🛠️ LAB TOOLS & AGENTS — egos-lab repo

> Source: `/home/enio/egos-lab/agents/registry/agents.json` v2.0.0  
> Entrypoints: `agents/agents/*.ts` + `scripts/*.ts`

### One-Shot Analysis Tools (kind: tool)

| ID | Área | Função | Linhas | Status |
|----|------|--------|--------|--------|
| `ssot-auditor` (lab) | architecture | Versão lab do ssot_auditor kernel — detecta SSOT violations | 3075 | ✅ active (⚠️ duplicata kernel) |
| `ssot-fixer` (lab) | architecture | Versão lab do ssot_fixer — aplica codemods safe | 227 | ✅ active (⚠️ duplicata kernel) |
| `ui-designer` | design | Gera UI mockups via Gemini/OpenRouter (Stitch prompts) | 118 | ✅ active |
| `auth-roles-checker` | auth | Valida RBAC: middleware, UI conditionals, API route guards | 213 | ✅ active |
| `contract-tester` | qa | Layer 2: API routes — status codes, response shapes, error handling | 239 | ✅ active |
| `integration-tester` | qa | Layer 3: Supabase RLS, full flows, data integrity | 323 | ✅ active |
| `regression-watcher` | qa | Layer 4: Compara runs, detecta regressões e flaky tests | 322 | ✅ active |
| `ai-verifier` | qa | Layer 5: Testa respostas de IA — adversarial, factual, safety | 263 | ✅ active |
| `domain-explorer` | architecture | Descript Pattern: decompõe domínio em SSOT+primitivos+tools+MVP | 300 | ✅ active |
| `living-laboratory` | architecture | Rule evolution: analisa git patterns, propõe updates em .windsurfrules | 425 | ✅ active |
| `showcase-writer` | qa | OSS readiness: README quality, LICENSE, Good First Issues | 550 | ✅ active |
| `open-source-readiness` | orchestration | Combina security-scanner + ssot-auditor + showcase-writer em score único | 276 | ✅ active |
| `gem-hunter` | knowledge | GitHub/HuggingFace/EXA/X — busca tools, models, papers e sinais diários | 1047 | ✅ active |
| `orchestrator` | infrastructure | Roda TODOS os agentes lab registrados e gera combined report | 338 | ✅ active |
| `report-generator` | analytics | Sintetiza dados de pesquisa em HTML/JSON dashboards | 384 | ✅ active |
| `prompt` | infrastructure | Exporta prompts reutilizáveis (AIXBT schemas, report templates) | 47 | ✅ active |
| `security-scanner` | security | Vulnerabilities + secrets scan em repositórios | 626 | ✅ active |

### Lab Scripts (kind: script)

| ID | Área | Função | Linhas | Trigger | Status |
|----|------|--------|--------|---------|--------|
| `security_scanner` | security | Pre-commit secret scanner (entropy + heuristic) | 128 | pre-commit, manual | ✅ active |
| `idea_scanner` | knowledge | Scan compiladochats — classifica e ingere novas ideias de negócio | 255 | pre-commit, manual | ✅ active |
| `rho_calculator` | observability | Project health metrics: authority, diversity, bus factor via git log | 233 | manual, weekly | ✅ active |
| `code_reviewer` | qa | AI-powered code review via Gemini/OpenRouter (git diff + LLM) | 121 | pre-commit, manual | ✅ active |
| `disseminator` | knowledge | Harvest @disseminate comments, propaga knowledge pelo repo | 79 | manual | ✅ active |
| `ambient_disseminator` | knowledge | Auto-patch .windsurfrules e PREFERENCES.md via git diffs + AI | 107 | session-end, manual | ✅ active |

**Comandos:**
```bash
cd /home/enio/egos-lab
bun agent:list                              # lista todos
bun agent:run <id> --dry                    # dry run
bun agent:run uptime-monitor --dry          # testa true agent
bun agent:run security-scanner --dry        # security scan
```

---

## 💀 DORMANT / BROKEN (Lab)

| ID | Tipo | Problema | Dead Reason | Ação Recomendada |
|----|------|----------|-------------|-----------------|
| `e2e-smoke` | dormant | Stub de 18 linhas, joga `Error("dormant")` | Nunca implementado | Implementar com Playwright ou deletar |
| `carteira-x-engine` | mockado | Mock hardcoded, Supabase comentado, tiltDetected=true forçado | Protótipo abandonado | Reconectar Supabase quando carteira-livre tiver DB real |
| `social-media` | broken | `Cannot find module '../../packages/shared/src/social/x-client'` | Módulo `x-client.ts` não existe em shared | Criar módulo ou marcar pending |

---

## 🔬 AUTORESEARCH — Loop de Pesquisa Autônomo

> Baseado no padrão Karpathy/autoresearch. Lê `program.md`, propõe mudanças via LLM,  
> roda evaluator, commita se melhorou métrica, reverte se não.

| Campo | Valor |
|-------|-------|
| **Entrypoint** | `/home/enio/egos-lab/egos-autoresearch/autoresearch.ts` |
| **Linhas** | 414 |
| **Loop** | `--max-iterations N` (default 10) |
| **LLM** | Alibaba Qwen-plus (fallback: Gemini via OpenRouter) |
| **Side-Effects** | git commits, `results.tsv`, `program.md` |
| **Trigger** | manual |
| **Status** | ✅ active |

```bash
cd /home/enio/egos-lab
bun egos-autoresearch/autoresearch.ts --dry --max-iterations 3
```

---

## 📊 Telemetria & Observabilidade

### Estado Atual

| Componente | Status | Localização |
|-----------|--------|-------------|
| JSONL logs (per-agent) | ✅ ativo | `agents/.logs/<id>.jsonl` |
| Status JSON (true agents) | ✅ ativo | `docs/<agent-id>/status.json` |
| Alerts log | ✅ ativo | `docs/<agent-id>/alerts.jsonl` |
| Telegram alerting | ✅ ativo | uptime-monitor, quota-guardian |
| Distributed tracing | ❌ não existe | — |
| Cost tracking | ❌ apenas teórico | — |
| Central dashboard | ❌ não existe | — |
| OpenTelemetry | ❌ não existe | — |

### Formato de Log (JSONL)

```json
{
  "timestamp": "2026-03-31T10:00:00Z",
  "correlation_id": "abc-123",
  "agent_id": "uptime-monitor",
  "mode": "execute",
  "level": "info",
  "message": "br-acc API DOWN — alerting Telegram",
  "latency_ms": 5003
}
```

### Formato de Status (True Agents)

```json
{
  "checkedAt": "2026-03-31T10:00:00Z",
  "mode": "execute",
  "summary": { "total": 6, "up": 3, "down": 3, "avgLatencyMs": 2007 },
  "services": [...],
  "alerts": ["br-acc API DOWN", "forja.egos.ia.br DOWN"]
}
```

---

## 🏗️ Infraestrutura de Execução

| Infraestrutura | Status | Uso |
|---------------|--------|-----|
| VPS Hetzner (204.168.217.125) | ✅ ativo | True agents via cron + Docker |
| Supabase (4 projetos) | ✅ ativo | egos-lab, carteira-livre, 852, forja |
| Vercel (2 deploys) | ✅ ativo | egos.ia.br, carteira-livre |
| Railway | ❌ cancelado | Remover referências |
| GitHub Actions | ⚠️ parcial | security-scanner no pre-commit |

### Cron Schedule (VPS Hetzner)

```cron
*/5  * * * *  bun /home/enio/egos-lab/agents/agents/uptime-monitor.ts --exec
*/15 * * * *  bun /home/enio/egos-lab/agents/agents/quota-guardian.ts --exec
0    */6 * * * bun /home/enio/egos-lab/agents/agents/drift-sentinel.ts --exec
0    * * * *   bun /home/enio/egos-lab/agents/agents/etl-orchestrator.ts --exec
```

> ⚠️ Verificar se esses crons estão realmente ativos no VPS: `ssh hetzner "crontab -l"`

---

## 📋 Roadmap de Melhorias

### P0 — Crítico (esta semana)

- [ ] Corrigir `status` de 3 agents no lab registry (`e2e-smoke`, `carteira-x-engine`, `social-media`)
- [ ] Registrar `autoresearch` no lab `agents.json`
- [ ] Remover referências ao Railway do `uptime-monitor.ts`
- [ ] Atualizar lab registry para v2.0.0 (adicionar `kind`, `loop_mechanism`, `side_effects`)
- [ ] Verificar crons no VPS estão ativos: `ssh hetzner "crontab -l"`

### P1 — Alta prioridade (esta sprint)

- [ ] Resolver duplicação `ssot-auditor`/`ssot-fixer` kernel vs lab (symlink ou deletar)
- [ ] Criar `packages/shared/src/social/x-client.ts` ou remover social-media do registry
- [ ] Implementar dashboard de status em tempo real (Supabase + Vercel)
- [ ] Adicionar `kind`, `loop_mechanism`, `side_effects` no lab registry

### P2 — Médio prazo

- [ ] Migrar true agents para framework de orquestração (Temporal ou Inngest)
- [ ] Implementar cost tracking real (tokens por run, budget alerts)
- [ ] Implementar human-in-loop gates (Telegram approval para T2+)
- [ ] OpenTelemetry integration para distributed tracing

---

## 🔒 Segurança

- **Risk Levels:** T0 (read-only) → T1 (low write) → T2 (high write, PII, secrets)
- **T2 agents** precisam de aprovação humana antes de `--exec`: `open-source-readiness`, `integration-tester`, `domain-explorer`, `living-laboratory`
- **Secrets:** todos via `.env` (nunca commitados), verificados pelo `security_scanner` pre-commit

---

*Gerado por: Claude Code + EGOS kernel audit — 2026-03-31*  
*Próxima revisão: quando qualquer registry mudar*
