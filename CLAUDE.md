# EGOS — Claude Code Context

> **Projeto:** EGOS Framework Core — Kernel de agentes, governance, orchestration
> **Stack:** TypeScript + Bun + 6 kernel agents + governance tooling
> **Repo:** /home/enio/egos/

---

## Regra: Próxima Task

Quando iniciado neste repositório e perguntado **"qual a próxima task?"** ou **"what's next?"**:

1. Leia este CLAUDE.md para contexto
2. Leia `TASKS.md` e identifique a task P0/P1 de maior prioridade incompleta
3. Leia PRs abertos: `gh pr list`
4. Responda com: task ID, descrição, arquivos envolvidos, e próximo passo concreto

**Sem fricção. Direto ao ponto.**

---

## Contexto do Projeto

EGOS é o kernel de AI orchestration — governa todos os outros repositórios do ecossistema.

### 6 Kernel Agents (testados e validados em 2026-03-27)

| Agent | Função |
|-------|--------|
| `dep_auditor` | Audita dependências (CVEs, versões) |
| `archaeology_digger` | Encontra código morto/legacy |
| `chatbot_compliance_checker` | Valida compliance de chatbots |
| `dead_code_detector` | Detecta código não utilizado |
| `capability_drift_checker` | Identifica drift de capacidades |
| `context_tracker` | Rastreia contexto cross-agent |

### Estrutura de Diretórios

```
agents/agents/       — 6 kernel agents
agents/runtime/      — runner.ts + event-bus.ts
agents/registry/     — agents.json
packages/shared/     — mycelium reference-graph
docs/                — research, tests, strategic plans
scripts/             — agent-chain-runner.ts
```

---

## Comandos Comuns

```bash
bun run build              # Build TypeScript
bun run test               # 43 testes
bun agent:run dep_auditor  # Rodar agente individual
bun governance:sync:exec   # Disseminate governance
```

---

## Estado Atual (2026-03-27)

- Todos 6 agentes testados em --dry mode ✅
- Chain runner criado (`scripts/agent-chain-runner.ts`) ✅
- Meta-prompts documentados em `docs/PHASE_1_RESEARCH_METAPROMPTS_CONSTELLATION.md` ✅
- Plano estratégico 2026-Q1 em `docs/STRATEGIC_PLAN_2026Q1.md` ✅

## Prioridades P0

1. **Integrar reference-graph.ts** — exports mortos, não consumidos
2. **Mycelium Orchestrator** — conectar kernel agents ao graph
3. **Hetzner VPS** — subir agents no servidor após migração br-acc

---

## Convenção de Arquivos

- `TASKS.md` — tarefas priorizadas (P0/P1/P2)
- `AGENTS.md` — registry de agentes
- `CLAUDE.md` — este arquivo
- `docs/knowledge/HARVEST.md` — knowledge acumulado de sessões
