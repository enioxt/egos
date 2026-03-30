# EGOS — Kernel de Orquestração para Agentes de IA Governados

> **"Saímos de casa para nos doar."**
> Rules govern agents. Agents enforce rules. Community evolves rules.

EGOS é o kernel open-source que fornece governança, orquestração e infraestrutura de runtime para sistemas de IA. É a camada invisível que faz agentes pensarem como sistemas governados — com rastreabilidade, conformidade LGPD e prova de trabalho em cada decisão.

---

## Produto Principal: Guard Brasil

**Guard Brasil** (`@egos/guard-brasil`) é o produto comercial construído sobre o kernel EGOS.
Protege sistemas de IA contra vazamento de dados pessoais brasileiros em tempo real.

```bash
# SDK (open source, MIT)
npm install @egos/guard-brasil

# REST API (hosted, R$99/mês)
curl -X POST https://guard.egos.ia.br/v1/inspect \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "CPF do suspeito: 123.456.789-00"}'
# → {"safe":false,"output":"CPF do suspeito: [CPF REMOVIDO]","meta":{"durationMs":4}}
```

**Detecta e mascara:** CPF, RG, MASP, REDS, número de processo, placa, telefone, e-mail e mais 8 categorias de PII brasileiro.

**Documentação comercial:**
- [1-pager PT-BR](docs/strategy/GUARD_BRASIL_1PAGER.md)
- [Demo script 30min](docs/strategy/GUARD_BRASIL_DEMO_SCRIPT.md)
- [Tiers e preços](docs/strategy/FREE_VS_PAID_SURFACE.md)

---

## O que o Kernel Provê

| Módulo | Descrição |
|--------|-----------|
| **Governance DNA** (`.guarani/`) | Identidade, protocolo de orquestração, quality gates, meta-prompts |
| **Agent Runtime** | Registry-based discovery, dry-run/execute, correlation IDs, event bus |
| **Guard Brasil Stack** | ATRiAN ético + PII Scanner BR + LGPD masking + Evidence Chain |
| **Multi-LLM Routing** | Alibaba Qwen (primário), OpenRouter/Gemini (fallback), cost tracking |
| **Frozen Zones** | Arquivos protegidos com pré-commit enforcement |
| **SSOT Enforcement** | Limites de arquivo, drift checks, gitleaks |
| **MANUAL_ACTIONS** | Rastreio de bloqueios manuais, lido obrigatoriamente no `/start` |

---

## Quick Start

```bash
git clone https://github.com/enioxt/egos.git
cd egos
bun install
bun run doctor              # valida ambiente (23 checks)
bun run governance:check    # verifica drift
bun run agent:list          # lista agentes registrados
```

**Testar Guard Brasil localmente:**
```bash
bun run packages/guard-brasil/src/demo.ts
bun test packages/guard-brasil/src/guard.test.ts   # 15/15 pass
```

---

## Workflows Operacionais

Workflows canônicos em `.agents/workflows/`:

| Comando | Arquivo | Descrição |
|---------|---------|-----------|
| `/start` | `.agents/workflows/start-workflow.md` | Ativação + MANUAL_ACTIONS check |
| `/end` | `/disseminate` | Handoff + docs + commit |
| `/diag` | `.windsurf/workflows/diag.md` | Diagnóstico completo do ecossistema |
| `/pr` | `.agents/workflows/pr-prep.md` | Preparação de PR com evidence |

```bash
bun run pr:pack --title "[AREA] summary" --out /tmp/pr-pack.md
bun run pr:gate --file /tmp/pr-pack.md
```

---

## Arquitetura

```
egos/
├── .guarani/               # Governance DNA (identity, orchestration, prompts)
├── agents/
│   ├── runtime/            # Runner + Event Bus (FROZEN)
│   ├── registry/           # Agent definitions SSOT (13 agents)
│   └── agents/             # Implementations (ssot-auditor, drift-sentinel...)
├── packages/
│   ├── guard-brasil/       # @egos/guard-brasil v0.1.0 — produto comercial
│   └── shared/             # ATRiAN, PII Scanner, Evidence Chain, LLM router
├── apps/
│   └── api/                # Guard Brasil REST API (Bun, porta 3099)
│       ├── src/server.ts   # POST /v1/inspect, Bearer auth, rate limiting
│       ├── src/mcp-server.ts # MCP stdio (guard_inspect, guard_scan_pii...)
│       └── deploy.sh       # Deploy 1-comando para Hetzner
├── scripts/                # doctor.ts, governance-sync.sh, egos-repo-health.sh
├── MANUAL_ACTIONS.md       # ⚠️ Bloqueios que só o humano resolve — ler primeiro
├── TASKS.md                # Roadmap vivo (EGOS-001 → EGOS-130)
└── AGENTS.md               # Mapa do sistema
```

---

## Ecossistema (Repos Folha)

| Repo | Propósito | Status |
|------|-----------|--------|
| [egos-lab](https://github.com/enioxt/egos-lab) | Lab + incubadora (29 agentes) | Ativo |
| [852](https://github.com/enioxt/852) | Chatbot institucional segurança pública | Produção |
| [EGOS-Inteligencia](https://github.com/enioxt/EGOS-Inteligencia) | Grafo de inteligência de dados públicos BR | Renomeando |
| [carteira-livre](https://github.com/enioxt/carteira-livre) | Marketplace SaaS | Produção |
| [FORJA](https://github.com/enioxt/forja) | ERP Chat-First para pequenos negócios | MVP |

---

## Infraestrutura de Produção

**VPS:** Hetzner 204.168.217.125 — 12 containers Docker ativos

| Serviço | Endpoint | Status |
|---------|----------|--------|
| guard-brasil-api | guard.egos.ia.br/v1/inspect *(DNS pendente)* | ✅ Healthy |
| 852-app | 852.egos.ia.br | ✅ Healthy |
| bracc-neo4j | 127.0.0.1:7474 | ✅ Healthy |
| infra-caddy | TLS automático | ✅ Up |

**Deploy Guard Brasil API:**
```bash
bash apps/api/deploy.sh          # deploy completo
bash apps/api/deploy.sh --logs   # deploy + tail logs
```

---

## Monetização Guard Brasil

| Tier | Preço | Limite |
|------|-------|--------|
| Open Source SDK | Gratuito | `npm install @egos/guard-brasil` |
| Starter API | R$99/mês | 100 req/min |
| Pro + Dashboard | R$499/mês | Sem limite + auditoria |
| Enterprise | Sob consulta | SLA 99.9%, on-premise |
| Policy Packs | R$2.990/ano | Segurança Pública, Judiciário, Saúde, Financeiro |

---

## Bloqueios Manuais Ativos

Arquivo: [`MANUAL_ACTIONS.md`](MANUAL_ACTIONS.md) — atualizado automaticamente.

| ID | Ação | Tempo | Prioridade |
|----|------|-------|-----------|
| M-001 | `npm login` + `npm publish` em `packages/guard-brasil/` | 5 min | 🔴 |
| M-002 | DNS A `guard → 204.168.217.125` em `egos.ia.br` | 2 min | 🔴 |
| M-003 | `bash scripts/rename-to-egos-inteligencia.sh --execute` | 15 min | 🟡 |
| M-005 | `docker network rename infra_bracc infra_egos_inteligencia` | 5 min | 🟡 |
| M-006 | `NPM_TOKEN` no GitHub Secrets | 5 min | 🟢 |
| M-007 | 20 emails outreach CTOs govtech BR | 2h | 🟢 |

---

## Contribuindo

Ver [CONTRIBUTING.md](CONTRIBUTING.md). Todos os commits passam por:
- `gitleaks` — detecção de segredos
- `tsc --noEmit` — typecheck estrito
- frozen zones check — proteção de arquivos canônicos
- governance drift check — `~/.egos/` sync

## Licença

MIT — [`@egos/guard-brasil`](packages/guard-brasil/) também MIT.
