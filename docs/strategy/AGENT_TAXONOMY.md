# EGOS Agent Reality Audit — Verificação Cruzada Completa

> **Gerado por:** Claude Code (Opus 4.6) — cruzando diagnóstico do outro agente com verificação independente
> **Data:** 2026-03-30 | **Status:** SSOT canônico para decisões sobre agentes
> **Decisão do operador:** Opção A (rebrand honesto) → gradualmente Opção B (agentic platform)

---

## 1. Diagnóstico Original vs Verificação

### Claims confirmados

| Claim | Status | Evidência |
|-------|--------|-----------|
| 43 entradas totais | **CONFIRMADO** | 13 kernel + 24 lab + 6 tools |
| 4 true agents (loop contínuo) | **PARCIALMENTE** | Os 4 existem mas 0 deles rodam no kernel — estão todos no egos-lab |
| AGENTS.md diz "6 agents" | **CONFIRMADO** | Linha 135 — desatualizado, deveria dizer 13 (kernel) |
| ssot-auditor duplicado kernel/lab | **CONFIRMADO** | Byte-for-byte idênticos |
| ssot-fixer duplicado | **CONFIRMADO** | Byte-for-byte idênticos |
| drift-sentinel duplicado | **CONFIRMADO** | Byte-for-byte idênticos |
| uptime-monitor menciona Railway | **CONFIRMADO** | Linha 10 |
| mcp-router e spec-router não registrados | **CONFIRMADO** | 531 e 447 linhas, sem entrada no agents.json |
| event-bus é stub | **INCORRETO** | 327 linhas, MyceliumBus funcional com emit/subscribe/persist |
| e2e-smoke dormant | **CONFIRMADO** | Stub de 19 linhas, throws Error("dormant") |
| social-media broken | **CONFIRMADO** | Import de módulo inexistente |
| carteira-x-engine mockado | **CONFIRMADO** | Dados hardcoded, Supabase comentado |

### Correção importante do diagnóstico original

O outro agente disse que o event-bus é "stub". **Está errado.** O `agents/runtime/event-bus.ts` tem 327 linhas com implementação real:
- `MyceliumBus` class com `emit()`, `subscribe()`, `persistEvent()`, `queryEvents()`
- Persistência JSONL com correlation IDs
- Pattern matching com wildcards
- Singleton via `getGlobalBus()`

O que é verdade: **nenhum agente do kernel usa o event-bus ativamente**. Ele está implementado mas sem consumers. Isso é diferente de ser stub.

---

## 2. Inventário Completo com Classificação Real

### Kernel (egos/) — 15 arquivos, 13 registrados

| Nome | Linhas | Tipo Real | Loop | Side-Effects | Registrado | Decisão |
|------|--------|-----------|------|--------------|------------|---------|
| ssot-auditor | 3075 | **CLI Tool** (enterprise-grade) | while | FS read/write | Sim | **Manter como tool, promover a produto** |
| spec-router | 447 | **CLI Tool** (routing) | Não | Nenhum | **NÃO** | Registrar |
| mcp-router | 531 | **CLI Tool** (MCP routing) | Não | Nenhum | **NÃO** | Registrar |
| archaeology-digger | 417 | **CLI Tool** (análise) | Não | FS write | Sim | Manter |
| drift-sentinel | 358 | **CLI Tool** (diagnóstico) | Não | FS read/write | Sim | Manter |
| dep-auditor | 247 | **CLI Tool** (dependências) | Não | FS write | Sim | Manter |
| dead-code-detector | 237 | **CLI Tool** (linting) | Não | FS read | Sim | Manter |
| ssot-fixer | 227 | **CLI Tool** (auto-fix) | for | FS write | Sim | Manter |
| capability-drift-checker | 205 | **CLI Tool** (compliance) | Não | FS read | Sim | Manter |
| aiox-gem-hunter | 197 | **CLI Tool** (research) | Não | fetch, FS write | Sim | Manter |
| context-tracker | 156 | **CLI Tool** (ctx management) | Não | Nenhum | Sim | Manter |
| gtm-harvester | 143 | **CLI Tool** (GTM research) | Não | fetch | Sim | Manter |
| framework-benchmarker | 116 | **CLI Tool** (benchmark) | Não | Nenhum | Sim | Manter |
| mastra-gem-hunter | 101 | **CLI Tool** (research) | Não | fetch | Sim | Manter |
| chatbot-compliance-checker | 54 | **CLI Tool** (verificação) | Não | Nenhum | Sim | Manter |

**Veredicto kernel:** 0 true agents, 15 CLI tools de alta qualidade. `ssot-auditor` é o standout.

### Lab (egos-lab/) — 24 registrados, 4 true agents

| Nome | Tipo Real | Loop | Status |
|------|-----------|------|--------|
| **uptime-monitor** | **True Agent** | setInterval 5min | Funciona — migrar para kernel |
| **quota-guardian** | **True Agent** | setInterval 15min | Funciona — migrar para kernel |
| **drift-sentinel** | **True Agent** (lab version) | setInterval 6h | DUPLICADO com kernel |
| **etl-orchestrator** | **True Agent** | cron hourly | Específico do EGOS-Inteligencia |
| e2e-smoke | Dormant | N/A | Stub, limpar |
| social-media | Broken | N/A | Import quebrado |
| carteira-x-engine | Mockado | N/A | Dados hardcoded |
| orchestrator | CLI Tool | N/A | Manter |
| ...20 outros... | CLI Tools | N/A | Avaliar caso a caso |

---

## 3. O que o EGOS faz que ninguém faz (Diferencial Real)

Antes de decidir sobre frameworks, vamos ser claros sobre o que é **genuinamente único**:

### Diferenciais reais (proteger)

| Feature | Por que é único | Quem mais tem |
|---------|-----------------|---------------|
| **Governance as Code** (`.guarani/`) | Identidade, preferências, regras de orquestração versionadas no repo | Ninguém |
| **SSOT Enforcement** (pre-commit, drift check) | Previne drift automaticamente em 12 repos | Ninguém |
| **Frozen Zones** | Arquivos protegidos por pre-commit hook | Parcial no Backstage/IDP |
| **Guard Brasil** (PII + ATRiAN + Evidence Chain) | Compliance LGPD nativo para IA | Ninguém (AWS Comprehend não faz ATRiAN) |
| **CRCDM** (Cross-Repo Commit DAG) | Trilha de auditoria cross-repo com hash por commit | Ninguém |
| **Dry-run universal** | Todo agente/tool tem dry-run mode | Mastra não tem |
| **ssot-auditor** (3075 linhas, AST parsing) | Dev tool de enterprise para drift detection | Possível produto standalone |

### O que NÃO é diferencial (não reinventar)

| Feature | Quem já faz melhor | Usar ao invés de build |
|---------|--------------------|-----------------------|
| Agent orchestration (loops, state) | Mastra, Temporal, Inngest | Adotar Mastra como substrate |
| LLM routing | Mastra (40+ providers), OpenRouter | Já usamos OpenRouter |
| Agent memory | Mastra (working + semantic memory) | Adotar quando necessário |
| Observability (traces, metrics) | Mastra, OpenTelemetry | Adotar quando tiver volume |
| Human-in-the-loop | Mastra (suspend/resume nativo) | Adotar quando necessário |

---

## 4. Mastra como Substrate — Análise Detalhada

### Por que Mastra e não Temporal/Inngest/CrewAI

| Critério | Mastra | Temporal | Inngest | CrewAI |
|----------|--------|----------|---------|--------|
| Linguagem | TypeScript (nosso stack) | Polyglot | TS/Python | Python only |
| AI-nativo | Sim (agents, RAG, evals) | Não | Não | Sim |
| Usa como library | Sim (`npm install`) | Complexo (server) | Sim | Sim |
| MCP support | Sim, nativo | Não | Não | Não |
| Governance | **Não tem** (nosso gap) | Não | Não | Não |
| Licença | Apache 2.0 (core) | MIT | MIT | Apache 2.0 |
| Stars | 22.5k | 12k+ | 5k+ | 25k+ |
| Maturidade | 1 ano (v1.16) | 5 anos | 3 anos | 2 anos |

**Mastra ganha porque:**
1. TypeScript-first (nosso stack)
2. AI-nativo (agents, workflows, tools)
3. MCP support nativo (já temos guard-brasil MCP)
4. **Não tem governance** — exatamente o gap que EGOS preenche
5. Usa como library, não como plataforma

### Arquitetura proposta: EGOS governance ON TOP of Mastra

```
┌─────────────────────────────────────────────────┐
│  EGOS Governance Layer (diferencial nosso)      │
│  .guarani/ │ frozen zones │ SSOT │ CRCDM │ audit│
├─────────────────────────────────────────────────┤
│  EGOS Products (Guard Brasil, ssot-auditor...)  │
├─────────────────────────────────────────────────┤
│  Mastra Orchestration (quando necessário)       │
│  agents │ workflows │ tools │ memory │ evals    │
├─────────────────────────────────────────────────┤
│  Execution Engine (Default → Inngest/Temporal)  │
├─────────────────────────────────────────────────┤
│  LLM Providers (via OpenRouter / Mastra router) │
└─────────────────────────────────────────────────┘
```

### Plano de adoção gradual (não reinventar, migrar quando maduro)

| Fase | Quando | O que |
|------|--------|-------|
| **0 (agora)** | 2026-03-30 | Rebrand honesto: 15 CLI tools + 4 monitors + governance framework |
| **1 (1 mês)** | Quando tiver 1 cliente Guard Brasil | `npm install @mastra/core` como dep no kernel |
| **2 (2 meses)** | Após validar Mastra internamente | Migrar uptime-monitor e quota-guardian para Mastra agents |
| **3 (3 meses)** | Após Mastra estável | Publicar `@egos/governance-mastra` — plugin Mastra com EGOS governance |
| **4 (6 meses)** | Após validação de mercado | EGOS como "Mastra + governance" — posicionamento claro |

---

## 5. Plano de Execução P0 — O Que Fazer Agora

### 5.1 Corrigir AGENTS.md
- Atualizar "6 agents" → "15 tools + 4 monitors"
- Ser honesto sobre o que cada coisa é

### 5.2 Registry cleanup
- Registrar `mcp-router` e `spec-router` no agents.json
- Marcar `e2e-smoke` como `"status": "dormant"`
- Marcar `social-media` como `"status": "broken"`
- Marcar `carteira-x-engine` como `"status": "mockado"`

### 5.3 Resolver duplicação
**Decisão do operador: kernel é o SSOT.**
- `ssot-auditor.ts`: kernel é canônico, lab é cópia
- `ssot-fixer.ts`: kernel é canônico, lab é cópia
- `drift-sentinel.ts`: kernel é canônico, lab é cópia
- Ação: lab aponta para kernel via symlink ou remove e documenta

### 5.4 Limpar referências Railway
- `uptime-monitor.ts` linha 10: remover menção Railway

### 5.5 Migrar true agents para kernel
Os 4 true agents estão no egos-lab mas deveriam estar no kernel (SSOT):
- `uptime-monitor` → kernel
- `quota-guardian` → kernel
- `drift-sentinel` → já está (duplicado, remover do lab)
- `etl-orchestrator` → fica no EGOS-Inteligencia (específico do ETL)

---

## 6. Taxonomia Canônica (Opção A implementada)

A partir de agora, EGOS usa esta taxonomia:

| Categoria | Definição | Critério |
|-----------|-----------|----------|
| **Monitor** | Roda em loop contínuo, detecta e alerta | `setInterval` ou cron + Telegram/webhook |
| **Tool** | CLI one-shot executável sob demanda | `bun run agents/agents/X.ts` |
| **Router** | Recebe input e decide para onde encaminhar | Request → routing logic → handler |
| **Stub** | Existe mas não funciona | Throws error ou imports quebrados |

### Resultado:
- **4 Monitors**: uptime-monitor, quota-guardian, drift-sentinel, etl-orchestrator
- **11 Tools**: ssot-auditor, ssot-fixer, dep-auditor, dead-code-detector, capability-drift-checker, context-tracker, archaeology-digger, aiox-gem-hunter, gtm-harvester, framework-benchmarker, mastra-gem-hunter, chatbot-compliance-checker
- **2 Routers**: mcp-router, spec-router
- **3 Stubs**: e2e-smoke, social-media, carteira-x-engine

---

## 7. Perguntas para o Operador

Preciso de decisões suas para avançar:

### 7.1 Domínio DNS
**Onde está registrado o domínio `egos.ia.br`?** (Cloudflare, Registro.br, outro?)
- Preciso disso para M-002 (DNS guard.egos.ia.br)
- Sem isso, a API está live no Hetzner mas não acessível publicamente

### 7.2 Conta npm
**Você tem conta no npmjs.com?** Se não, precisa criar em https://www.npmjs.com/signup
- Username escolhido?
- Preciso de um scope: publicar como `@egos/guard-brasil` requer ter a org `egos` no npm
- Se `egos` já estiver tomado, alternativa: `@egosai/guard-brasil`

### 7.3 Mastra — confirmação
**Confirma que quer adotar Mastra como substrate de orquestração (Fase 1 apenas)?**
- Fase 1 = `npm install @mastra/core` + um POC com uptime-monitor
- Não muda nada existente, apenas adiciona
- Risco: Mastra tem 1 ano de idade, API pode mudar

### 7.4 egos-lab — escopo do arquivo
**O que fica no egos-lab?**
- Opção: Lab vira "playground/experimentação" — agentes experimentais, POCs
- Tudo canônico (governance, SSOT, tools de produção) fica no kernel
- Os 4 true agents migram para o kernel
- Confirma?

### 7.5 etl-orchestrator
**O etl-orchestrator é específico do EGOS-Inteligencia (ex-br-acc). Ele migra para o kernel ou fica no EGOS-Inteligencia?**
- Argumento kernel: centralizar todos os monitors
- Argumento egos-inteligencia: é específico do pipeline de dados
- Minha recomendação: fica no EGOS-Inteligencia

### 7.6 Guard Brasil como TP para Mastra
**Quando maduro, quer publicar Guard Brasil como Mastra Tool?**
- Seria um `@egos/mastra-guard-brasil` que registra `guard_inspect` como tool no Mastra
- Daria visibilidade no ecossistema Mastra (22.5k stars)
- Pode ser feito sem mudar nada no Guard Brasil atual

### 7.7 ssot-auditor como produto
**O ssot-auditor tem 3075 linhas, AST parsing, codemod generation. Quer considerar como segundo produto?**
- Possível: `@egos/ssot-auditor` no npm como dev tool
- Target: equipes TypeScript que querem drift detection enterprise
- Precisa: README, testes, documentação

---

## 8. Decisões Já Tomadas (pelo operador)

| Decisão | Valor |
|---------|-------|
| Kernel (egos) é SSOT para tudo | **Sim** |
| egos-lab sendo arquivado | **Sim** (lentamente) |
| Opção A (rebrand honesto) | **Sim** |
| Opção B (agentic platform) depois | **Sim** (quando maduro) |
| Não reinventar, focar na diferença | **Sim** |
| FORJA e Santiago congelados | **Sim** |

---

*Documento canônico. Próxima revisão: quando operador responder seções 7.1-7.7*
