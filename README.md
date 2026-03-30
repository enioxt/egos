# EGOS — Governance Kernel for Auditable AI Systems

> Governance-first runtime, policy enforcement, and reusable safety modules for production AI systems.

EGOS é o kernel open-source que fornece governança, orquestração, validação e superfícies reutilizáveis para sistemas de IA que precisam de rastreabilidade, conformidade e disciplina operacional.

---

## Produto Principal: Guard Brasil

**Guard Brasil** (`@egosbr/guard-brasil`) é o primeiro produto público construído sobre o kernel EGOS.
Ele adiciona proteção LGPD, validação ética, trilha de evidências e políticas de saída para assistentes e fluxos de IA operando no contexto brasileiro.

```bash
# SDK (open source, MIT)
npm install @egosbr/guard-brasil

# REST API hospedada
curl -X POST https://guard.egos.ia.br/v1/inspect \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "CPF do cliente: 123.456.789-00"}'
```

**Detecta e trata:** CPF, RG, MASP, REDS, número de processo, placa, telefone, e-mail, nomes e outros identificadores relevantes para cenários brasileiros.

**Nota de naming público:** o kernel continua sendo `EGOS`; os pacotes npm públicos usam o escopo `@egosbr/*`.

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
| **Guard Brasil Stack** | ATRiAN + PII Scanner BR + LGPD masking + PRI + Evidence Chain |
| **Multi-LLM Routing** | Alibaba Qwen (primário), OpenRouter/Gemini (fallback), cost tracking |
| **Protected Surfaces** | Arquivos protegidos com enforcement via pre-commit e governança |
| **SSOT Enforcement** | Limites de arquivo, drift checks, gitleaks |

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
│   ├── runtime/            # Runner + Event Bus (protected surfaces)
│   ├── registry/           # Agent definitions SSOT
│   └── agents/             # Implementations
├── packages/
│   ├── guard-brasil/       # @egosbr/guard-brasil v0.1.0 — public package
│   └── shared/             # ATRiAN, PII Scanner, Evidence Chain, LLM router
├── apps/
│   ├── api/                # Guard Brasil REST + MCP reference server
│   └── guard-brasil-web/   # Public landing + dashboard explorations
├── scripts/                # doctor.ts, governance-sync.sh, kernel utilities
├── TASKS.md                # Roadmap vivo
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

## Superfície Pública e Postura de Segurança

Este README público mostra apenas o que um prospect, operador ou contribuidor precisa para avaliar o produto.

**Público e verificável:**
- pacote npm `@egosbr/guard-brasil`
- endpoint `https://guard.egos.ia.br/v1/inspect`
- health check `https://guard.egos.ia.br/health`
- documentação técnica e comercial em `docs/strategy/`

**Intencionalmente omitido daqui:**
- IPs de VPS, SSH e topologia detalhada de runtime
- localizações de segredos, tokens e rotinas de rotação
- comandos operacionais manuais e checklists internos
- chaves de demonstração e credenciais temporárias

---

## Superfície Comercial Atual

| Oferta | Preço | Uso típico |
|------|-------|--------|
| Open Source SDK | Gratuito | uso local, PoC, ferramentas internas |
| Starter API | a partir de R$ 49/mês | pilotos e integrações leves |
| Pro | R$ 199/mês | times com volume recorrente |
| Business | R$ 499/mês | ambientes com auditoria, dashboards e SLA ampliado |
| Enterprise | Sob consulta | on-premise, policy packs e suporte dedicado |

**Pricing SSOT:** `docs/strategy/GUARD_BRASIL_PRICING_RESEARCH.md`

---

## Contribuindo

Ver [CONTRIBUTING.md](CONTRIBUTING.md). Todos os commits passam por:
- `gitleaks` — detecção de segredos
- `tsc --noEmit` — typecheck estrito
- frozen zones check — proteção de arquivos canônicos
- governance drift check — `~/.egos/` sync

## Licença

MIT — [`@egosbr/guard-brasil`](packages/guard-brasil/) também MIT.
