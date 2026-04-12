# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.61.0 | **Updated:** 2026-04-09 23:45 UTC-3 | **NEW:** ENCAPSULATION track (Path B/C) — Evidence-First §33, 7 camadas inside-out, EGOS Lab community, artigo âncora showcase
> **Philosophy:** Build what needs to be built, in the right order, without urgency.
> **Active Principle:** §33 Evidence-First — nothing advances without proof. No new features until kernel is encapsulated.

---

### 🔭 ENCAPSULATION TRACK (Path B + C) [P0 — fechado 2026-04-09]
**SSOT:** `docs/strategy/EGOS_PATH_B_C_PLAN.md` v0.3.0 | **Principle:** §33 Evidence-First (`~/.claude/CLAUDE.md`)
**Context:** Decisão estratégica de 2026-04-09 após análise ChatGPT+Gemini+Grok+Perplexity+Kimi. Caminho B = artigo showcase + Caminho C = EGOS Lab (R$ 20/mês). Inside-out, sem pressa, sem features novas. Encapsular, testar, provar, publicar.
**Rule:** Nenhuma feature nova até Camada 7 publicada. Tarefas paralelas em outros repos (Eagle Eye, Forja, 852) continuam fora desta track.

#### EVIDENCE-GATE [P0 — ativar warning agora, blocking 2026-04-16]
- [x] **EVG-001**: §33 Evidence-First adicionado ao `~/.claude/CLAUDE.md` global ✅ 2026-04-09
- [x] **EVG-002**: `scripts/evidence-gate.ts` placeholder criado (warning mode até 2026-04-16) ✅ 2026-04-09
- [x] **EVG-003 [P0]**: Integrar `evidence-gate.ts` ao `.husky/pre-commit` do kernel (warning-only) | 1h ✅ 2026-04-09
- [x] **EVG-004 [P0]**: Primeiro dry-run em `CAPABILITY_REGISTRY.md` — contar violations reais sem bloquear | 30min ✅ 2026-04-10 — 33 unbacked claims found (versions + capability counts)
- [ ] **EVG-005 [P1]**: Expandir `.egos-manifest.yaml` para cobrir capability claims (não só README metrics) | 3h
- [ ] **EVG-006 [P1]**: Ativar blocking mode no kernel a partir de 2026-04-16 | 15min
- [ ] **EVG-007 [P2]**: Disseminar evidence-gate para repos de produto conforme Camadas 4+ avançam | on-going

#### CAMADA 0 — Kernel do Kernel (semana 1)
**Escopo:** `~/.claude/CLAUDE.md` (33 seções) + `egos/CLAUDE.md` + `.guarani/RULES_INDEX.md` + `.guarani/PREFERENCES.md`
- [x] **ENC-L0-001 [P0]**: Auditoria completa do CLAUDE.md v4 — 4 PROVEN / 6 PARTIAL / 6 ASPIRATIONAL ✅ 2026-04-10
- [x] **ENC-L0-002 [P0]**: `docs/audit/KERNEL_AUDIT.md` — auditoria com gaps priorizados (top 5) ✅ 2026-04-10
- [ ] **ENC-L0-003 [P0]**: Compressão do CLAUDE.md global — remover aspirational, consolidar duplicadas, alvo ≤ 2000 linhas (está em ~1500+) | 3h
- [ ] **ENC-L0-004 [P0]**: Compressão do `egos/CLAUDE.md` — remover duplicações com global (DRY) | 2h
- [ ] **ENC-L0-005 [P1]**: Dissemination pipeline valida blocks injetados nos repos de leaf após compressão | 1h

#### CAMADA 1 — Agents Registry (semana 2)
**Escopo:** `agents/registry/agents.json` + `agents/agents/*.ts` + prove-or-kill
- [x] **ENC-L1-001 [P0]**: Inventário de cada agent: 20 registered (18 active, 2 dead) + 4 unregistered found ✅ 2026-04-10
- [x] **ENC-L1-002 [P1]**: Registrar 4 agents não-registrados (article-writer, doc-drift-verifier, doc-drift-analyzer, readme-syncer) no agents.json ✅ done 2026-04-10 — agents.json v2.4.0 (24 agents)
- [x] **ENC-L1-003 [P0]**: `docs/agents/<name>.md` — 24 stubs criados com seção "Prova de vida" ✅ 2026-04-10
- [x] **ENC-L1-004 [P0]**: `docs/agents/INDEX.md` — índice mestre com 24 agents, status, LOC, proof command ✅ 2026-04-10
- [ ] **ENC-L1-005 [P0]**: Smoke test suite — cada agent roda em `--dry` com output determinístico | 4h
- [ ] **ENC-L1-006 [P1]**: Screenshot/export de `agent_events` Supabase mostrando execuções reais dos últimos 7 dias | 1h

#### CAMADA 2 — Governance Pipeline (semana 3)
**Escopo:** Pre-commit hooks + CCR jobs + Doc-Drift Shield + vocab guard + file-intelligence + auto-disseminate
- [ ] **ENC-L2-001 [P0]**: `docs/governance/PIPELINE_SPEC.md` — documentar cada hook linha a linha com exemplo de falha real | 6h
- [ ] **ENC-L2-002 [P0]**: Diagrama Mermaid do pipeline completo (commit → hooks → CCR → reports → dashboards) | 2h
- [ ] **ENC-L2-003 [P0]**: `bun test:governance` — suite unificada que injeta violations e verifica bloqueios | 4h
- [ ] **ENC-L2-004 [P1]**: Índice de incidentes (INC-001 force push, INC-002 git add -A, INC-003 TASKS hallucination) com link para fix | 2h

#### CAMADA 3 — Stack & Alternatives Matrix (semana 4)
**Escopo:** Multi-provider routing + MCP stack + runtimes
- [ ] **ENC-L3-001 [P0]**: `docs/stack/PROVIDER_ROUTING.md` — Qwen → Gemini → OpenRouter fallback com justificativa e trade-offs | 3h
- [ ] **ENC-L3-002 [P0]**: `docs/stack/MCP_SERVERS.md` — 3 MCPs próprios (egos-governance, codebase-memory, egos-memory) + externos (Notion, Supabase, Vercel) | 3h
- [ ] **ENC-L3-003 [P0]**: `docs/stack/ALTERNATIVES_MATRIX.md` — para cada escolha, 2-3 alternativas com quando cada uma serve melhor (requisito Enio) | 6h
- [ ] **ENC-L3-004 [P0]**: `scripts/bench-providers.ts` — roda llm-test-suite contra cada provider, publica resultado em `docs/benchmarks/YYYY-MM-DD.md` | 4h
- [ ] **ENC-L3-005 [P1]**: Comparação de custo mensal real vs alternativas (self-hosted vs OpenAI vs Groq) — tabela com números reais | 2h

#### CAMADA 4 — Produtos Core (semanas 5-6)
**Escopo:** Guard Brasil, 852, Forja, Gem Hunter, KB/Knowledge MCP, Gateway
- [ ] **ENC-L4-001 [P0]**: Template único `docs/products/_TEMPLATE.md` — arquitetura, stack, alternativas, métricas, como testar, como acessar produção, roadmap | 2h
- [ ] **ENC-L4-002 [P0]**: `docs/products/guard-brasil.md` — completo com evidence + benchmark 4ms reproduzível | 4h
- [ ] **ENC-L4-003 [P0]**: `docs/products/852.md` — completo com ATRiAN layer + 68 capabilities provadas | 4h
- [ ] **ENC-L4-004 [P0]**: `docs/products/forja.md` — completo com case Rocha Implementos (dados quantitativos sanitizados) | 4h
- [ ] **ENC-L4-005 [P0]**: `docs/products/gem-hunter.md` — completo, padrão standalone | 3h
- [ ] **ENC-L4-006 [P0]**: `docs/products/knowledge-mcp.md` — completo com ingest + lint + export + x402 | 3h
- [ ] **ENC-L4-007 [P0]**: `docs/products/egos-gateway.md` — completo com OAS 3.1 + routing | 3h
- [ ] **ENC-L4-008 [P0]**: `docs/products/INDEX.md` — índice mestre visual | 1h
- [ ] **ENC-L4-009 [P0]**: Cada produto tem health endpoint + dashboard tile + link de último deploy + test suite | 6h

#### CAMADA 5 — Data & Observability (semana 7)
**Escopo:** br-acc Neo4j + Supabase tables + CCR reports + heartbeat + obs-central
- [ ] **ENC-L5-001 [P0]**: `docs/data/INVENTORY.md` — inventário completo de dados (br-acc schema público sanitizado + Supabase tables + finalidade) | 6h
- [ ] **ENC-L5-002 [P0]**: `docs/data/LGPD_COMPLIANCE.md` — auditoria Guard Brasil sobre os próprios dados EGOS | 4h
- [ ] **ENC-L5-003 [P0]**: `scripts/obs-central.ts` — script (NÃO agent) que coleta métricas e gera report em `docs/jobs/` | 6h
- [ ] **ENC-L5-004 [P0]**: Cron VPS 09:00 + 21:00 BRT rodando obs-central | 1h
- [ ] **ENC-L5-005 [P1]**: Políticas de retenção documentadas (o que fica quanto tempo, por quê) | 2h

#### CAMADA 6 — Dashboards Públicos & status.egos.ia.br (semanas 8-9)
**Escopo:** status.egos.ia.br + versão pública do egos-hq + tiles de prova
- [ ] **ENC-L6-001 [P0]**: `apps/status-site/` — novo app Bun + Hono, read-only, consome `snapshot.json` | 6h
- [ ] **ENC-L6-002 [P0]**: `scripts/status-snapshot.ts` — pull-based 5min snapshot com Guard Brasil audit antes de servir | 6h
- [ ] **ENC-L6-003 [P0]**: 3 tiers (public/community/enio-only) com OTP gate para community via Evolution API WhatsApp | 6h
- [ ] **ENC-L6-004 [P0]**: Caddyfile routing `status.egos.ia.br` + deploy container VPS | 2h
- [x] **ENC-L6-005 [P0]**: Botão "verify" em cada tile mostrando comando shell + timestamp + SHA-256 do snapshot | 4h ✅ 2026-04-12
- [ ] **ENC-L6-006 [P1]**: `docs/public/STATUS_PAGE.md` — explicando cada métrica para público externo | 2h

#### CAMADA 7 — Artigo Âncora Showcase (semanas 10-12)
**Escopo:** "EGOS: plataforma multi-agente brasileira open source — mapa visual completo"
- [ ] **ENC-L7-001 [P0]**: `apps/egos-site/src/content/posts/egos-showcase.md` — draft outline com 7 seções (1 por camada) | 3h
- [ ] **ENC-L7-002 [P0]**: Seção 1: Kernel audit + filosofia (link para docs/audit) | 3h
- [ ] **ENC-L7-003 [P0]**: Seção 2: Agents registry (screenshots + links para docs/agents) | 3h
- [ ] **ENC-L7-004 [P0]**: Seção 3: Governance pipeline (diagrama Mermaid + exemplos reais) | 3h
- [ ] **ENC-L7-005 [P0]**: Seção 4: Stack + alternativas (tabelas) | 3h
- [ ] **ENC-L7-006 [P0]**: Seção 5: 6 produtos core com screenshots dashboard vivo | 4h
- [ ] **ENC-L7-007 [P0]**: Seção 6: Dados + observability (snapshot status.egos.ia.br) | 2h
- [ ] **ENC-L7-008 [P0]**: Seção 7: EGOS Lab (convite + como participar) | 2h
- [ ] **ENC-L7-009 [P0]**: Cada claim do artigo linka para: comando reproduzível OU entry no manifest OU tile do dashboard | 6h
- [ ] **ENC-L7-010 [P0]**: Review final via Guard Brasil + ATRiAN Truth/Accuracy antes de publicar | 2h
- [ ] **ENC-L7-011 [P0]**: Publicar em egos.ia.br (canonical) | 1h
- [ ] **ENC-L7-012 [P0]**: Repost manual no Substack (copy-paste, link canonical para egos.ia.br) | 1h
- [ ] **ENC-L7-013 [P0]**: Crosspost tabnews + thread X.com + post LinkedIn | 2h

#### EGOS LAB — Comunidade (paralelo, bootstrapping a partir da semana 4)
**Estrutura:** R$ 20/mês via Stripe, tier único, tudo incluso. Conteúdo público gratuito. Pagamento = acesso à comunidade + encontros ao vivo.
- [ ] **LAB-001 [P1]**: Stripe recorrente R$ 20/mês produto "EGOS Lab" — reusar infra Guard Brasil | 2h
- [ ] **LAB-002 [P1]**: Notion workspace template da comunidade (rulebook, canais, welcome page) | 3h
- [ ] **LAB-003 [P1]**: `scripts/egos-lab-onboard.ts` — webhook Stripe → Evolution API WhatsApp OTP → add ao grupo + Notion invite | 6h
- [ ] **LAB-004 [P1]**: Formulário Notion de descoberta (nome, cidade, stack, por quê, o que quer construir) | 1h
- [ ] **LAB-005 [P1]**: Grupo WhatsApp EGOS Lab criado (Evolution API gerenciado) | 30min
- [ ] **LAB-006 [P1]**: Email fallback via Resend (se WhatsApp falhar no OTP) | 2h
- [ ] **LAB-007 [P1]**: Bot Claude com contexto EGOS respondendo no grupo fora do horário humano (via paperclip) | 4h
- [ ] **LAB-008 [P1]**: Convidar 2-3 primeiros co-stewards/testers (Enio já tem em mente) antes do launch público | 30min
- [ ] **LAB-009 [P1]**: Gravar primeiro encontro ao vivo interno (testers + Enio) para ter material inicial | 2h
- [ ] **LAB-010 [P2]**: Landing page EGOS Lab em egos.ia.br com CTA Stripe | 3h
- [ ] **LAB-011 [P2]**: Documentação do onboarding flow como **showcase público** — "como automatizamos o próprio onboarding com agentes" vira post técnico | 3h
- [ ] **LAB-012 [P2]**: Certificação leve "EGOS Practitioner" automática após 90 dias ativos | 4h

#### EGOS-SITE — Blog/Showcase (semanas 1-10 paralelo às camadas)
- [x] **SITE-001 [P1]**: egos-site reativado — Hono server, /lab + /showcase routes, live em egos.ia.br ✅ 2026-04-10 (commit 6a28b1f)
- [x] **SITE-002 [P1]**: Rotas: index, /timeline, /lab, /showcase, nav atualizada. Query corrigida para schema real timeline_articles. ✅ 2026-04-10 (commit 2c43c35)
- [ ] **SITE-003 [P1]**: Markdown-based posts em `src/content/posts/*.md` — sem CMS | 2h
- [ ] **SITE-004 [P1]**: [BLOCKER] DNS A record egos.ia.br → 204.168.217.125 (atualmente aponta para Vercel 216.150.1.1). Caddy já configurado. Container já rodando Hono. Só falta mudar o DNS. | 5min
- [ ] **SITE-005 [P1]**: Theme dark/light simples, tipografia técnica (Inter + JetBrains Mono) | 3h
- [ ] **SITE-006 [P2]**: RSS feed para distribuição | 1h
- [ ] **SITE-007 [P2]**: llms.txt já existe, garantir que egos-site serve | 30min

---

### 🗺️ REPO MAP & PAPERCLIP STRUCTURE [P0 — Opus session 2026-04-09]
**Context:** Enio quer integrar todos os repos no Paperclip para observabilidade, agrupando por estágio (produção/plataforma/R&D). Sessão Opus produziu o mapeamento canônico.
**SSOT:** `docs/REPO_MAP.md` (a criar) + `~/.claude/CLAUDE.md §32` + memory `repo_classification_2026-04-09.md`

#### Classificação canônica (use isto, ignore listas antigas)

| Grupo | Repos | Status | Path local |
|-------|-------|--------|-----------|
| **PRODUCTION** | guard-brasil, forja, 852, gem-hunter, egos-gateway | Live com usuários ou pilot | `/home/enio/{forja,852}` + `/home/enio/egos/{apps/egos-gateway,packages/gem-hunter}` |
| **PLATFORM** | egos (kernel), egos-hq, paperclip | Infra interna | `/home/enio/egos`, `/opt/apps/{egos-hq,paperclip}` |
| **ACTIVE-DEV** | egos-inteligencia | Em construção, busca parceiros | `/home/enio/egos-inteligencia` |
| **CONTRIBUTIONS** | ratio | Read-only (PRs externos a Carlos Victor) | `/home/enio/contributions/ratio` |
| **ABSORBING** | policia → egos-inteligencia, br-acc → egos-inteligencia (selective port) | Migrando peças úteis | `/home/enio/{policia,br-acc}` |
| **PARKED** | arch | Aguarda parceiro de arte | `/home/enio/arch` |
| **ARCHIVING** | egos-lab | Sinalizado para arquivamento | `/home/enio/egos-lab` |

#### Esclarecimentos críticos (anti-confusão para futuros agentes IA)
1. **ratio NÃO é um produto conjunto.** É repo do Carlos Victor (carlosvictorodrigues/ratio). VPS hospeda só pra testar 3 PRs futuros (Claude fallback / Guard Brasil PII / Neo4j entity extraction). Não tocar no código, só observar.
2. **852 e policia são DIFERENTES**. 852 = chatbot público Next.js (live em 852.egos.ia.br). policia = CLI Python privado (DHPP, automação documentos). Ambos eventualmente absorvidos por egos-inteligencia, mas em camadas diferentes.
3. **egos-inteligencia = fusão**: intelink + br-acc (Neo4j data layer) + 852 (chat UI logic) + policia (case templates) + ideias do ratio. Em PHASE-1, FastAPI + Next.js 15 + Neo4j 5.x + 30 commits últimos 30d.
4. **gem-hunter está dentro do egos kernel** mas precisa virar standalone (P0, ver GH-STANDALONE-* abaixo). Enio identifica-se como gem hunter — produto-âncora.
5. **br-acc continua canonical para Neo4j** (83.7M nodes); egos-inteligencia consume via shim `api/src/bracc/__init__.py`.

#### REPO-MAP tasks
- [x] **REPO-MAP-001 [P0]**: Criar `docs/REPO_MAP.md` com a tabela acima + diagrama Mermaid de dependências ✅ 2026-04-09
- [x] **REPO-MAP-002 [P0]**: Adicionar seção `§32 REPO MAP` em `~/.claude/CLAUDE.md` (feito nesta sessão Opus)
- [x] **REPO-MAP-003 [P0]**: Memory file `repo_classification_2026-04-09.md` (feito nesta sessão Opus)
- [ ] **REPO-MAP-004 [P1]**: Atualizar `docs/EGOS_STATE_OF_THE_ECOSYSTEM.md` com nova classificação
- [ ] **REPO-MAP-005 [P1]**: Atualizar `docs/CAPABILITY_REGISTRY.md` agrupando capabilities por grupo de repo
- [ ] **REPO-MAP-006 [P2]**: Marcar `COMPLETE_REPO_INVENTORY_2026-04-03.md` como deprecated apontando para REPO_MAP.md

---

### 🤖 PAP-AGENTS — Paperclip Agent Structure [P0 — Opus session 2026-04-09]
**Context:** Já existem 5 agentes no Paperclip (CEO, Gem Hunter, Guard Brasil, KB, Gateway) criados sessão Sonnet anterior. Falta organizar em Projects + adicionar agentes faltantes (Observability é o GAP MAIS CRÍTICO).
**SSOT:** `docs/PAPERCLIP_STRUCTURE.md` (a criar)

#### Final agent roster (10 agentes em 3 Projects)

**Project: PRODUCTION** (live com usuários)
1. **Guard Brasil Agent** ✅ (existing) — guard-brasil API health, false positives, billing
2. **Gem Hunter Agent** ✅ (existing, expandir scope) — gem-hunter + tracking standalone migration
3. **FORJA Agent** (NEW) — forja repo + Rocha Implementos pilot, multi-tenant ERP
4. **852 Agent** (NEW) — 852 chatbot health + tracking eventual absorção em egos-inteligencia

**Project: PLATFORM** (infra interna)
5. **CEO Agent** ✅ (existing default Paperclip) — coordenação geral, kernel oversight
6. **Knowledge Base Agent** ✅ (existing) — KB cross-repo, ingestor, lint, citations
7. **Observability Agent** (NEW — P0 CRITICAL) — fecha o gap de observabilidade do VPS
8. **Gateway Agent** ✅ (existing) — egos-gateway routing, OpenAPI, channels

**Project: R&D** (em desenvolvimento ou colaboração externa)
9. **EGOS-Inteligencia Agent** (NEW) — fusão project + tracking absorção br-acc/852/policia
10. **Ratio Liaison Agent** (NEW, lightweight) — só tracking dos 3 PRs ao Carlos Victor

#### PAP-AGENTS tasks
- [ ] **PAP-AGENTS-001 [P0]**: Criar 3 Projects no Paperclip (Production / Platform / R&D)
- [ ] **PAP-AGENTS-002 [P0]**: Mover os 5 agentes existentes para os Projects corretos
- [ ] **PAP-AGENTS-003 [P0]**: Criar **Observability Agent** com cwd=`/opt/apps/egos-agents`, instructions: ler `/var/log/egos/`, `docker logs`, cron outcomes, produzir `docs/jobs/obs-YYYY-MM-DD.md` 2x/dia
- [ ] **PAP-AGENTS-004 [P0]**: Criar **FORJA Agent** com cwd=`/opt/apps/forja-clone` (provisionar via PAP-AGENTS-010), instructions baseadas em `forja/CLAUDE.md`
- [ ] **PAP-AGENTS-005 [P0]**: Criar **EGOS-Inteligencia Agent** com cwd=`/opt/apps/egos-inteligencia-clone`, instructions baseadas em `egos-inteligencia/README.md`
- [ ] **PAP-AGENTS-006 [P1]**: Criar **852 Agent** com cwd=`/opt/apps/852` (já no VPS), instructions sobre chat health + plan absorção
- [ ] **PAP-AGENTS-007 [P2]**: Criar **Ratio Liaison Agent** lightweight (read-only mode, só tracking dos 3 PRs)
- [ ] **PAP-AGENTS-008 [P0]**: Criar board API key no Paperclip via UI → salvar em `/root/.paperclip/board-api-key` no VPS (necessário para agentes consumirem API)
- [x] **PAP-AGENTS-009 [P0]**: Default model dos agentes EGOS = Haiku 4.5 (feito para 4 agentes; CEO continua Sonnet pra decisões estratégicas)
- [ ] **PAP-AGENTS-010 [P1]**: Provisionar `/opt/apps/forja-clone` e `/opt/apps/egos-inteligencia-clone` no VPS (read-only git clones para os agentes lerem)
- [ ] **PAP-AGENTS-011 [P1]**: Documentar fluxo: como atribuir task ao agente certo via Paperclip UI (`docs/PAPERCLIP_STRUCTURE.md`)
- [ ] **PAP-AGENTS-012 [P2]**: Validar OpenRouter como fallback no Paperclip (Gemini 2.0 flash, Qwen3) caso queira economizar Claude Code subscription
- [ ] **PAP-AGENTS-013 [P1]**: Verificar que CEO agent retry no run `8cf173ec` funciona após Claude CLI install + HOME=/paperclip

---

### 👁️ OBS-CENTRAL — Observabilidade Centralizada [P0 — Opus session 2026-04-09]
**Context:** GAP crítico identificado no diagnóstico. VPS tem 22 containers + 16 crons mas logs em 8 lugares, sem dashboard, sem trending, sem alerts estruturados. Hermes ficou quebrado dias sem ninguém saber (qwen-plus model ID errado, fix em 2026-04-09 nesta sessão).
**SSOT:** `scripts/obs-central.ts` (a criar) + `docs/jobs/obs-YYYY-MM-DD.md` (output diário)

#### Princípios
- **Estruturado** — JSON output, não texto livre
- **Local first** — não depender de Loki/Grafana inicialmente, usar SQLite + scripts
- **Telegram só pra urgente** — relatório completo vai pro `docs/jobs/`
- **Cobertura total** — todos containers, todos crons, todos serviços HTTP, custos LLM, último commit→deploy

#### OBS-CENTRAL tasks
- [ ] **OBS-CENTRAL-001 [P0]**: Criar `scripts/obs-central.ts` que coleta:
  - Docker stats de todos containers (CPU/RAM/restart count)
  - Tail dos últimos 100 lines de cada cron job log em `/var/log/egos/` e `/var/log/`
  - HTTP status de todos endpoints internos (3050, 3060, 3099, 3100, etc)
  - Disk + RAM headroom
  - Hermes session log (tail)
  - Sai como JSON estruturado
- [ ] **OBS-CENTRAL-002 [P0]**: `obs-central.ts --report` produz markdown daily report em `docs/jobs/obs-YYYY-MM-DD.md`
- [ ] **OBS-CENTRAL-003 [P0]**: Cron VPS 2x/dia (09:00 + 21:00 BRT) rodando obs-central + Telegram alert se anomalia
- [ ] **OBS-CENTRAL-004 [P1]**: SQLite local em `/var/lib/egos/obs.db` com histórico (para trending)
- [ ] **OBS-CENTRAL-005 [P1]**: HQ dashboard pull data de `obs.db` → mostra uptime/latency/erros por serviço
- [ ] **OBS-CENTRAL-006 [P1]**: Tracking commit→deploy: cada commit no main do egos kernel registrado com SHA + timestamp + health snapshot 5min depois
- [ ] **OBS-CENTRAL-007 [P1]**: Cost-per-agent: ler `cost_events` table do paperclip-db + Claude Code session logs → relatório semanal de gasto por agente
- [ ] **OBS-CENTRAL-008 [P2]**: Anomaly detection (volume agent_events, erro rate, latência > p95)
- [ ] **OBS-CENTRAL-009 [P2]**: Avaliar Loki/Grafana stack (só depois de OBS-CENTRAL-001..005 estarem funcionando — não over-engineer cedo)
- [x] **OBS-CENTRAL-010 [P0]**: Fix Hermes qwen-plus model ID (`openai/qwen-plus` → `qwen-plus` em `/root/.hermes/config.yaml`) — feito nesta sessão Opus

---

### 💎 GH-STANDALONE — Gem Hunter Standalone Migration [P0 — Opus session 2026-04-09]
**Context:** Enio identifica-se como gem hunter (8 anos investindo em web3, agora construindo a ferramenta). Produto-âncora dele mas vive "esquecido" porque está embedded no egos kernel. Análise mostrou que dá pra extrair em 8-12h. 80% das peças já existem isoladas.
**SSOT:** `docs/gem-hunter/STANDALONE_MIGRATION_PLAN.md` (a criar)

#### Estado atual (FACT do Explore agent)
- Core: `agents/agents/gem-hunter.ts` (2537 LOC, depende de `packages/shared/src/social/ai-engine.ts`)
- API: `agents/api/gem-hunter-server.ts` (428 LOC, **já isolado**, sem kernel imports)
- npm package: `packages/gem-hunter/` v6.0.0 publicado, fully portable
- Landing: `apps/gem-hunter-landing/` Bun/Hono
- Docs: `docs/gem-hunter/{GEM_HUNTER_v6_MASTER_PLAN.md,GEM_HUNTER_PRODUCT.md,SSOT.md}`
- BLOCKER P0: GH-067 (deploy gem-hunter-server to VPS) — sem isso não monetiza

#### GH-STANDALONE tasks
- [ ] **GH-STANDALONE-001 [P0]**: Documentar plano em `docs/gem-hunter/STANDALONE_MIGRATION_PLAN.md`
- [ ] **GH-STANDALONE-002 [P0]**: Extrair `ai-engine.ts` de `packages/shared/src/social/` → copiar 200 LOC para `packages/gem-hunter/src/llm/multi-router.ts` (mantém também no shared, não quebra outros)
- [ ] **GH-STANDALONE-003 [P0]**: Verificar `gem-hunter-server.ts` roda standalone — `bun agents/api/gem-hunter-server.ts` sem precisar do agent runner
- [ ] **GH-STANDALONE-004 [P0]**: GH-067 (existing) — deploy `gem-hunter-server` para VPS porta 3097 + Caddy gemhunter.egos.ia.br
- [ ] **GH-STANDALONE-005 [P0]**: Atualizar `docs/gem-hunter/SSOT.md` apontando para o novo standalone path
- [ ] **GH-STANDALONE-006 [P1]**: Criar repo separado `gem-hunter-standalone` (ou pasta `/home/enio/gem-hunter` clone) — fica fora do egos kernel mas ainda usa egos-bun para tooling
- [ ] **GH-STANDALONE-007 [P1]**: Migrar `awesome-gems` repo (GH-080) referência no novo standalone
- [ ] **GH-STANDALONE-008 [P1]**: Publicar `@egosbr/gem-hunter-core` na npm
- [ ] **GH-STANDALONE-009 [P2]**: GH-086 — MCP server `@egosbr/gem-hunter-mcp` (fica trivial após standalone)
- [ ] **GH-STANDALONE-010 [P2]**: GH-070 — Chatbot orchestrator (intent → tool calls → gem-hunter API) via WhatsApp/Telegram

---

### 🧬 EI-ABSORB — EGOS-Inteligencia Absorption Plan [P1 — Opus session 2026-04-09]
**Context:** egos-inteligencia é fusão de intelink + br-acc (selective) + 852 (chat UI) + policia (case templates) + ideias ratio. Atualmente em PHASE-1 (FastAPI + Neo4j + Next.js 15). Falta plano explícito do que migra, do que fica separado, do que copia.
**SSOT:** `/home/enio/egos-inteligencia/docs/ABSORPTION_PLAN.md` (a criar lá, não no kernel)

#### Princípios
- **Não merge tudo de uma vez** — perigo de quebrar o que funciona (852 está live, policia está em uso)
- **Extract shared library** — `@egos/intelligence-core` com ATRiAN + PII scanner + AI router + correlation engine
- **Mantém deploys separados** até PHASE-2 estar provada

#### EI-ABSORB tasks (executadas dentro do repo egos-inteligencia, NÃO no kernel)
- [ ] **EI-ABSORB-001 [P1]**: Criar `egos-inteligencia/docs/ABSORPTION_PLAN.md` com matriz: o que migra, o que copia, o que fica separado
- [ ] **EI-ABSORB-002 [P1]**: Decidir 852: (A) absorver chat UI inteiro, (B) extrair shared lib, (C) deixar separado e linkar via API. Documentar trade-offs.
- [ ] **EI-ABSORB-003 [P1]**: Decidir policia: idem
- [ ] **EI-ABSORB-004 [P1]**: Documentar shim atual `api/src/bracc/__init__.py` — quando remove? Quando br-acc fica obsoleto?
- [ ] **EI-ABSORB-005 [P1]**: Identificar peças do `ratio` que podem inspirar (não copiar) — sacred math? jurisprudência search?
- [ ] **EI-ABSORB-006 [P2]**: Criar `@egos/intelligence-core` package (ATRiAN + PII + AI router) consumível por 852, policia, egos-inteligencia
- [ ] **EI-ABSORB-007 [P2]**: Migration tracker — relatório semanal: "X% absorvido, Y peças pendentes, Z dependências quebradas"

---

### 🔴 SESSÃO 2026-04-09 — ETL + REPORT_SSOT + MYCELIUM + 852 [P0 ATIVO]
**Contexto:** Validação BR-ACC ETL, disseminação REPORT_SSOT v2.0, decisão EGOS-118 (Mycelium → Repository Mesh), configuração testes 852.  
**Artefatos Criados:** `REPORT_SSOT_DISSEMINATION_PLAN.md`, `MYCELIUM_RESEARCH_REPORT_2026-04-09.md`, `EXECUTIVE_SUMMARY_2026-04-09.md`, `health-monitor.ts`

#### P0 — BR-ACC ETL Validation & Execution
**SSOT:** `/opt/bracc/etl/` no VPS (204.168.217.125) | **Serviço:** `bracc-etl.service` | **Log:** `/var/log/bracc-etl.log`
- [x] **ETL-001**: Debug ETL Fase 3 — SSH com saída truncada, script fix criado ✅ 2026-04-09
  - `.env` criado no VPS
  - Script `scripts/fix-bracc-etl.sh` criado para correção manual
- [ ] **ETL-002**: Corrigir erro systemd — executar `scripts/fix-bracc-etl.sh` no VPS
- [ ] **ETL-003**: Executar ETL completo Fase 3 (17.4M/24.6M Partner = ~70% completo)
- [ ] **ETL-004**: Validar Neo4j linking final — verificar relacionamentos criados
- [ ] **ETL-005**: Documentar ganhos reais: 40+ fontes, 83M+ entidades cruzadas

#### P0 — REPORT_SSOT Dissemination (Convergir 3 implementações paralelas)
**SSOT:** `egos/docs/REPORT_SSOT.md` v2.0.0 | **Plano:** `docs/monitoring/REPORT_SSOT_DISSEMINATION_PLAN.md`

**Fase 1 — Kernel Hardening (24h):**
- [x] **REPORT-001**: Criar `@egos/report-standard` package skeleton ✅ 2026-04-09
  - `package.json`, `tsconfig.json`, `src/schema.ts`, `src/validator.ts`, `src/index.ts`
  - `schemas/report-v2.json` — JSON Schema completo
  - `README.md` com documentação de uso
- [ ] **REPORT-002**: Extrair JSON Schema de `REPORT_SSOT.md` → `schemas/report-v2.json`
- [ ] **REPORT-003**: Implementar validator TypeScript (`validateReportSchema()`)
- [ ] **REPORT-004**: Exportar types canônicos (`ReportSchema`, `ReportType`, `ReportSection`)

**Fase 2 — Leaf Repo Migration (48h):**
- [ ] **REPORT-005** [852]: Criar `src/lib/report-adapter.ts` (legacy → canonical)
- [ ] **REPORT-006** [852]: Adicionar referência REPORT_SSOT em `AGENTS.md`
- [ ] **REPORT-007** [br-acc]: Atualizar `api/src/bracc/report_schema.py` para v2.0 (Pydantic)
- [ ] **REPORT-008** [br-acc]: Adicionar `$ref` ao kernel REPORT_SSOT
- [ ] **REPORT-009** [egos-inteligencia]: Criar `api/src/models/report.py` com Intelink extensions
- [ ] **REPORT-010** [egos-inteligencia]: Implementar endpoint `/reports/generate` com RBAC

**Fase 3 — Auto-Dissemination (72h):**
- [ ] **REPORT-011**: Criar `scripts/report-ssot-propagator.ts` (detecta mudanças → propaga)
- [ ] **REPORT-012**: Workflow `.windsurf/workflows/report-ssot-sync.md`
- [ ] **REPORT-013**: Testes cross-repo: validar export PDF/JSON/DOCX interoperáveis

#### P1 — Mycelium / EGOS-118 Decision & Implementation
**SSOT:** `docs/concepts/mycelium/SSOT.md` | **Pesquisa:** `docs/monitoring/MYCELIUM_RESEARCH_REPORT_2026-04-09.md`
**Contexto:** Decisão EGOS-118 (2026-03-24) propõe rename "Mycelium" → "Repository Mesh" em docs técnicos

- [x] **MYCELIUM-001**: Decisão **GO** — usar "Repository Mesh" em docs técnicos, manter "Mycelium" para reconhecimento de voz ✅ 2026-04-09
- [x] **MYCELIUM-002**: Atualizar `docs/concepts/mycelium/SSOT.md` → v1.1.0 ✅ 2026-04-09
- [x] **MYCELIUM-003**: Atualizar `MYCELIUM_OVERVIEW.md` → v1.1.0 ✅ 2026-04-09
  - Tabela de nomenclatura: RepositoryMesh/MeshBus/MeshNode (docs) ↔ Mycelium/MyceliumBus/MyceliumNode (voz)
- [ ] **MYCELIUM-004**: Liminar docs obsoletos em `egos-lab` que referenciam arquivos inexistentes (`node.ts`, `schema.ts`, `test-poc.ts`)
- [ ] **MYCELIUM-005**: Validar Redis Bridge — testar se `redis-bridge.ts` está efetivamente conectado
- [ ] **MYCELIUM-006**: Expandir Reference Graph de 27 nodes/32 edges para refletir sistema real
- [ ] **MYCELIUM-007**: Decisão ZKP/Shadow Nodes — implementar ou remover do roadmap? <!-- vocab-guard: planned -->

#### P1 — 852 Test Suite Configuration
**SSOT:** `/home/enio/852/` | **Goal:** `npm test` funcional, reduzir 32 fails para <10

- [ ] **852-TEST-001**: Configurar Jest/Vitest em `package.json`
- [ ] **852-TEST-002**: Criar testes para `pii-scanner.ts` (migrar para `@egosbr/guard-brasil`)
- [ ] **852-TEST-003**: Criar testes para `atrian.ts` (validation rules)
- [ ] **852-TEST-004**: Criar testes para `ai-provider.ts` (multi-provider fallback)
- [ ] **852-TEST-005**: Reduzir fails de 32 para <10

#### P2 — Health Monitor & Automation
**SSOT:** `scripts/health-monitor.ts` | **Relatório:** `logs/health-report.json`

- [ ] **MONITOR-001**: Agendar `health-monitor.ts` no cron (1x por hora)
- [ ] **MONITOR-002**: Configurar alertas Telegram quando VPS services down
- [ ] **MONITOR-003**: Dashboard HQ integrar health data do ETL e Neo4j

---

### 🔴 SECURITY — Dependabot Vulnerabilities (2026-04-09) [P0 BLOCKER]
**SSOT:** `docs/jobs/2026-04-09-code-security.md` | `SECURITY.md` | `.github/dependabot.yml` | `.github/workflows/security.yml`

**Status:** 12 vulnerabilidades detectadas (4 HIGH, 8 MODERATE) — [github.com/enioxt/egos/security/dependabot](https://github.com/enioxt/egos/security/dependabot)

**Vulnerabilidades Conhecidas:**
| Pacote | Versão Atual | CVE/Problema | Severidade | Fix |
|--------|--------------|--------------|------------|-----|
| axios | 1.15.0 | CVE-2024-39353 (XSS), CVE-2023-45857 (CSRF) | HIGH | `bun update axios@^1.17.0` |
| ajv | 6.14.0 | CVE-2020-15366 (prototype pollution) | MODERATE | `bun update ajv@^8.17.1` |
| cross-spawn | 7.0.5 | CVE-2024-21538 (prototype pollution) | HIGH | `bun update cross-spawn@^7.0.6` |
| semver | range | ReDoS em <7.5.2 | MODERATE | `bun update semver@latest` |
| ws | ^8.18.2 | DoS vulnerability (verificar) | MODERATE | `bun update ws@latest` |

**✅ DONE 2026-04-09:**
- `SECURITY.md` criado — política de segurança + incident response
- `.github/dependabot.yml` v6.0 — security-first config, daily scans, auto-grouping
- `.github/workflows/security.yml` — CI security scan + gitleaks + dependabot check

**P0 — Resolver Vulnerabilidades (24h SLA):**
- [x] **SEC-001**: Atualizar axios 1.15.0 → 1.17.0+ (CVE-2024-39353, CVE-2023-45857) ✅ 2026-04-09
- [x] **SEC-002**: Atualizar cross-spawn 7.0.5 → 7.0.6+ (CVE-2024-21538) ✅ 2026-04-09
- [ ] **SEC-003**: Verificar e atualizar semver se necessário
- [ ] **SEC-004**: Verificar e atualizar ws (Supabase realtime) se necessário

**P1 — Security Hardening:**
- [ ] **SEC-005**: Aplicar security patches do Dependabot via GitHub UI
- [x] **SEC-006**: Criar script `scripts/security-audit.ts` para scan local automatizado ✅ 2026-04-09

---

### X.com Monitoring System (2026-04-07)
**SSOT:** `docs/social/X_POSTS_SSOT.md` | **Features Roadmap:** `docs/social/X_FEATURES_INTEGRATION_ROADMAP.md` | **Scripts:** `scripts/x-opportunity-alert.ts`, `scripts/x-approval-bot.ts`, `scripts/setup-x-monitoring.sh`
**Context:** Sistema completo de monitoramento de oportunidades X.com. Busca automática a cada 2h, alertas WhatsApp/Telegram, aprovação manual via bot. Integrando melhores features de ferramentas pagas (AutoTweet, TweetHunter, Hypefury) em solução própria self-hosted.

**✅ DONE 2026-04-07/08:** X-COM-001..005 (alert+approval bots, setup, SSOT templates, roadmap) | X-COM-018..024 (LLM analysis layer DashScope+OpenRouter, recordFeedback, HTML format, diagnostic — all in `scripts/x-opportunity-alert.ts`)

**P0 — Deploy + Core (Esta semana):**
- [x] **X-COM-008**: x-smart-scheduler.ts — análise de audiência para melhores horários
- [x] **X-COM-009**: x-evergreen-recycler.ts — recompartilhamento inteligente de top posts

**P1 — Growth (Próximas 2 semanas):**
- [ ] **X-COM-010**: Thread composer web — interface no HQ para criar threads
- [ ] **X-COM-011**: x-viral-library.ts — biblioteca de conteúdo viral por nicho
- [ ] **X-COM-012**: x-lead-crm.ts — tracking de leads no Supabase
- [ ] **X-COM-013**: Auto-DM sequences — workflow day 0/3/7 pós-aprovação

**P2 — Scale (Mês 2):**
- [ ] **X-COM-014**: Social listening avançado — Brand24-style monitoring
- [ ] **X-COM-015**: Analytics dashboard no HQ — heatmaps, métricas de crescimento
- [ ] **X-COM-016**: Auto-plug — promoção inteligente em tweets virais
- [ ] **X-COM-017**: Variations generator — A/B testing com LLM local (Gemma)

**P0 — Refinement (2026-04-08):**
- [ ] **X-COM-023**: Hermes integration — Agent para análise semanal e refinement automático de keywords
- [ ] **X-COM-024**: Templates DM específicos — OSINT/Investigação, AI/Framework, GovTech separados

---

### GovTech — Documentação de Oportunidades (2026-04-07)
**SSOT:** `docs/knowledge/GOVTECH_LICITACOES_ABERTAS_2026-04-07.md` | 7 licitações documentadas.
- [ ] **GOV-TECH-005**: Monitoramento diário PNCP
- [ ] **GOV-TECH-006**: One-pager "Eagle Eye para Parceiros"
- [ ] **GOV-TECH-007**: 5 software houses habilitadas para abordar
<!-- GOV-TECH-001..004/008..010 + full context in TASKS_ARCHIVE_2026.md -->

### OSINT Brasil — Toolkit & Matriz Operacional (2026-04-08)
**SSOT:** `docs/knowledge/OSINT_BRASIL_TOOLKIT.md` | 8 categorias + 8 tipos de investigação.
- [ ] **OSINT-006**: Mapear integração Brasil.IO + Escavador + Jusbrasil na 852
- [ ] **OSINT-007**: Templates DM para delegacias (PCMG/PMMG/PF)
- [ ] **OSINT-008**: Alertas de vazamentos HIBP API no Guard Brasil
<!-- OSINT-009..016 + full context moved to TASKS_ARCHIVE_2026.md -->

### API Marketplaces — Estratégia Multi-Plataforma EGOS (2026-04-08) [EXPANDED]
**SSOT:** `~/.codeium/windsurf-next/API_MARKETPLACES_MASTER_ANALYSIS.md` | 20+ plataformas, 5 camadas (x402/Stripe MPP, AgentCash/APINow.fun, MCP eco, Web3, Traditional). Mercado $52B/2030.
- **Proxies.sx** — 0%, 4G/5G proxies, bounties, ~95% take rate
- **ToolOracle** — 73 MCP servers, 708 tools, $0.01-0.08/call, AgentGuard security

**Camada 3 — MCP Ecosystem:**
- **Smithery** — 5,000+ servers, one-click install, gateway 6500
- **Glama** — 20,771 servers, SEO discovery (80% inbound)
- **MCP Hive, MCP Market, mcpservers.org** — Directories
- **TrueFoundry** — Enterprise gateway, RBAC, audit

**Camada 4 — Web3/On-chain:**
- **Virtuals Protocol** — Agent tokenization on Base, $VIRTUAL liquidity
- **ai16z / ELIZAOS** — AI-led VC DAO, Eliza framework
- **Sahara AI** — 40+ enterprise clients, AI marketplace
- **Heurist Mesh** — 25 providers, 100 tools, 40 agents, Web3 skills
- **Talus** — Sui blockchain, autonomous AI agents
- **Nevermined** — Visa + Coinbase integration, card rails

**Camada 5 — Traditional + Hybrid:**
- **RapidAPI** — 4M devs, 40k APIs, 20% commission
- **Replicate** — ML models, per-compute billing
- **DigitalAPI, API Layer, APYHub, Zyla** — Curated marketplaces

**P0 — Payment Protocols & x402 Onboarding (Esta semana):**
- [x] **API-001**: AgentCash onboard + testar consumer ✅ 2026-04-08
- [ ] **API-002**: APINow.fun — criar conta, explorar tokenization
- [ ] **API-003**: Proxies.sx — avaliar match OSINT scraping
- [x] **API-004**: Análise x402 vs Stripe MPP — escolher primary protocol ✅ 2026-04-08
- [x] **API-005**: Criar wallet Base chain única para pagamentos ✅ 2026-04-08

**P1 — MCP Ecosystem (Próximas 2 semanas):**
- [x] **API-006**: x402 channel para Guard Brasil ✅ — `apps/egos-gateway/src/channels/guard-brasil.ts` live. Vercel wrapper deferred (gateway serve propósito). ✅ 2026-04-09
- [/] **API-007 [ENIO]**: Submit Guard Brasil em Smithery — `smithery.yaml` ✅, npm ✅ (`@egosbr/guard-brasil-mcp@0.1.0`). **Precisa API key:** smithery.ai/account/api-keys → `SMITHERY_API_KEY` → `npx @smithery/cli@latest publish --name egosbr/guard-brasil`. | 15min MANUAL
- [/] **API-008 [ENIO]**: Listar em Glama (20,771 servers, SEO) — `glama.json` ✅ pronto em `packages/guard-brasil-mcp/`. Tutorial: (1) glama.ai/mcp/servers → "Add Server" → cole: `https://github.com/enioxt/egos/tree/main/packages/guard-brasil-mcp` → Glama auto-indexa do GitHub (não precisa npm). Metadata exibida: nome, descrição, security grade, license, last updated. | 15min MANUAL (Glama não precisa npm publish)
- [x] **MCP-PUB-001 [P1]**: Publish `@egosbr/guard-brasil-mcp` to npm — bundled with `bun build --bundle`, 30KB single file, smoke-tested. ✅ 2026-04-09
- [x] **API-009**: Criar llms.txt para AI discovery ✅ 2026-04-09
- [ ] **API-010**: Documentar X402_INTEGRATION.md

**P2 — Web3/On-chain (Mês 2):**
- [ ] **API-011**: Avaliar Virtuals tokenization para 852 Intelligence
- [ ] **API-012**: Submit skills ao Heurist Mesh (Web3 audience)
- [ ] **API-013**: Explorar Nevermined (Visa integration)
- [ ] **API-014**: Publicar OSINT Brasil wrappers (Brasil.IO, Escavador)
- [ ] **API-015**: ATRiAN Validator como compliance-as-a-service

**P3 — Traditional Scale (Mês 2-3):**
- [ ] **API-016**: RapidAPI provider account + freemium tiers
- [ ] **API-017**: Replicate — avaliar Gem Hunter como "model"
- [ ] **API-018**: DigitalAPI curated listing

**P4 — Otimização & Scale (Mês 3+):**
- [ ] **API-019**: A/B test pricing cross-platform
- [ ] **API-020**: Consolidar métricas revenue/usage/discovery (all platforms)
- [ ] **API-021**: Case study: "Guard Brasil: from local API to global agent marketplace"
- [ ] **API-022**: Avaliar criação API coins/tokens (APINow model)
- [ ] **API-023**: Stripe MPP integration (enterprise clients)

**Insights da Pesquisa (Atualizado 2026-04-08):**
- **30+ plataformas** identificadas em 5 camadas (Payment, Agent-Native, MCP, Web3, Traditional)
- 11,000+ MCP servers listados, **<5% monetizados** (oportunidade enorme)
- **xpay MCP**: Proxy wrapper para monetizar MCP servers sem code changes
- **ToolOracle**: 73 servers, 708 tools, 15% conversion free→paid via health_check discovery
- **Stripe MPP**: session batching para high-frequency (vs 1 TX/call x402)
- **Nevermined + Visa**: partnership abril 2026 — card rails tradicionais para agents
- **Hyperbolic**: GPU marketplace para AI agents (descentralized compute)
- **PinAI**: Personal AI Network — smartphone AI agents

**Diferenciais EGOS para Monetização:**
1. **Guard Brasil** — Único PII BR + LGPD art.11 (dados de saúde), zero competidores
2. **Gem Hunter** — Discovery engine 14 fontes (competidores têm 1-3)
3. **852 Inteligência** — Chatbot policial anônimo + ATRiAN (52 capabilities)
4. **ATRiAN** — Validação ética 90+ acrônimos policiais
5. **OSINT Brasil** — 12 ferramentas curadas + LGPD compliant
6. **X Opportunity** — Monitoramento X.com policial (23 queries)

**Documentos Consolidados:**
- `/home/enio/.codeium/windsurf-next/EGOS_API_MONETIZATION_COMPLETE.md` — Documento único 30+ plataformas
- `/home/enio/.codeium/windsurf-next/EGOS_DIFERENCIAIS_UNICOS.md` — Análise dos 6 diferenciais EGOS
- `/home/enio/.codeium/windsurf-next/ATRIAN_VS_GUARD_ANALYSIS.md` — ATRiAN vs Guard Brasil comparativo
- `/home/enio/.codeium/windsurf-next/API_MARKETPLACES_EXTENDED_RESEARCH.md` — Pesquisa ampla

**Recursos:**
- Awesome x402: https://github.com/xpaysh/awesome-x402
- x402 vs MPP (WorkOS): https://workos.com/blog/x402-vs-stripe-mpp
- MCP State 2026: https://settlegrid.ai/learn/state-of-mcp-2026
- xpay MCP: https://docs.xpay.sh/en/products/mcp-monetization
- ToolOracle: https://tooloracle.io/blog/how-to-monetize-mcp-servers-x402-usdc-micropayments

---

### Doc-Drift Shield Implementation (2026-04-07)
**SSOT:** `docs/DOC_DRIFT_SHIELD.md` | **Handoff:** `docs/_current_handoffs/handoff_2026-04-07_doc-drift-shield-plan.md`
**Context:** P33 discovered severe drift (Carteira Livre 54→134 pages +148%, BR-ACC 77M→83.7M Neo4j). 4-layer shield: L1 manifest + L4 CLAUDE.md §27 + L2 pre-commit + L3 VPS sentinel + L4 CCR module — ALL DONE (P33-P35).
**Done P33-P35 (2026-04-07):** doc-drift-verifier.ts, doc-drift-sentinel.ts, readme-syncer.ts, doc-drift-check.sh, agents.json (19 agents), manifests (br-acc/carteira-livre/852/forja/egos-lab/egos-inteligencia), MASTER_INDEX v1.3.0, governance-drift.yml CCR, manifest-generator.ts, .ssot-map.yaml (21 domains), ssot-router.ts (pre-commit step 5.7), X_POSTS_SSOT consolidation (5→1), doc-drift-analyzer.ts (L3.5)

**P1 — Pending:**
- [ ] **DRIFT-012**: Drift dashboard in hq.egos.ia.br showing status across all repos
- [ ] **DRIFT-013**: Integrate with Gem Hunter for third-party claim verification
- [ ] **SSOT-MCP**: Create `docs/MCP_SSOT.md` — consolidate 7 MCP_*.md files (MCP_DEPLOYMENT_CHECKLIST, MCP_ENV_VARS_REFERENCE, MCP_INTEGRATION_GUIDE, MCP_INTEGRATION_MAP, MCP_ORCHESTRATION_STRATEGY, MCP_SCOPE_POLICY, MCP_IMPLEMENTATION_SUMMARY)
- [ ] **SSOT-OUTREACH**: Migrate docs/outreach/ (8 files) → GTM_SSOT.md §partnerships
- [ ] **ARR-001**: Wire AAR (`@egos/search-engine`) into Gem Hunter content indexing (first activation use case)
- [ ] **ARR-002**: Wire AAR into KB wiki search (replaces raw grep in wiki-compiler)
- [ ] **ARR-003**: Hybrid retrieval pattern — AAR (precision/exact) + pg_trgm FTS (recall) for Guard Brasil + EGOS Inteligência. Validated by 2025 research (Meilisearch/Redis/Glean): full-text superior to vectors for identifier-heavy domains (CPF/CNPJ/PEPs/contracts). NOT a vector DB replacement.

### HQ Integration Masterplan (2026-04-07)
**Goal:** HQ shows live data for ALL 19 VPS containers — no service invisible, no number hardcoded.
**Diagnostic:** 2026-04-07 — hq.egos.ia.br covers 5/19 services. 14 containers invisible. Placeholder cards shipped (page.tsx + health/route.ts extended). Integration in 4 phases.
**SSOT:** `apps/egos-hq/app/page.tsx` + `apps/egos-hq/app/api/hq/health/route.ts`

**Phase 1 — Wiring internal services (health/route.ts already extended):**
- [ ] **HQI-001**: Eagle Eye → add counts from Supabase (territories, opportunities) via `/api/hq/eagle-eye` route
- [ ] **HQI-002**: 852 Police Bot → expose messages_today from 852-app internal API (find correct health endpoint)
- [ ] **HQI-003**: SINAPI → verify internal Docker URL + expose entry_count from DB
- [ ] **HQI-004**: br-acc/Neo4j → live node count via bolt (find creds in VPS docker-compose)
- [ ] **HQI-008**: OpenClaw real config → read actual fallback_chain from openclaw-sandbox (not hardcoded)

**Phase 2 — Volume mounts + data routes:**
- [x] **HQV2-000**: VPS docker-compose: volume mounts → /opt/data/egos:/data:ro + daily GitHub sync cron. ✅ 2026-04-09
- [x] **HQV2-001**: `/api/hq/tasks` — parse /data/TASKS.md → `{total, pending, p0, p1, stale_p0}` ✅ 2026-04-09
- [ ] **HQV2-003**: `/api/hq/gems` — gem-hunter API → top gems, last run, sector breakdown
- [x] **HQV2-004**: `/api/hq/drift` — read /data/jobs/doc-drift-sentinel.md → structured drift per repo (DRIFT-012) ✅ 2026-04-09

**Phase 3 — New dashboard pages:**
- [x] **HQV2-006**: `/tasks` page — Kanban P0/P1/P2, done/pending counts (dep: HQV2-001) ✅ 2026-04-09
- [ ] **HQV2-007**: `/world-model` page — health% gauge, P0 blockers, agent inventory
- [ ] **HQV2-008**: `/gems` page — filterable cards (score, source, category)
- [ ] **HQV2-009**: `/system-map` page — D3 graph from agents.json + CAPABILITY_REGISTRY
- [ ] **HQV2-010**: Nav update — add tasks, world-model, gems, system-map, drift links

**Phase 4 — Intelligence + Dream Cycle:**
- [ ] **DC-007**: HQ "Last Night" card — Dream Cycle results from egos_nightly_logs
- [ ] **HQC-012**: Intelligence engine — `intelligence-engine.ts` + Gemma 4 31B free → auto-task creation
- [ ] **GRF-002**: Knowledge Graph panel — vis.js embed from codebase-memory-mcp
- [ ] **ORB-004**: Orchestration Status widget — MCP server health (brave, github, filesystem, etc.)
- [ ] **HQC-011**: Remove all remaining hardcoded data — drive from canonical registries

---

### P2 — SSOT Limpeza / Misc
- [ ] **CLEAN-001..004 [P2]**: XCOM→GTM_SSOT, X_POST_PROFILE→delete, outreach/→GTM_SSOT §partnerships, sales/→MONETIZATION_SSOT
- [ ] **EGOS-132 [P2]**: Resolve brand conflict: BRAND_CANONICAL.md (kernel) vs egos-lab/branding/BRAND_GUIDE.md
- [ ] **DOC-005 [P2]**: Remove `Sacred Code`/`Frozen Zones` from legacy governance docs

---

**Archive (P1-P26):** EGOS-151..176, MONETIZE-001..015, KB-001..018, GH-001..071, X-001..008, THEATER, WA, EAGLE, GOV, BRACC, PART — all ✅. Products: Guard Brasil v0.2.2 API+web+npm, Gateway v0.3.0, Gem Hunter dashboard, HQ, Eagle Eye, KB. Codex/OpenClaw/billing proxy decommissioned 2026-04-08 → DashScope+Hermes.

### Guard Brasil Monetization Roadmap

**Completed:** EGOS-151..161, MONETIZE-001..015, EGOS-162/164 — all DONE ✅ (see archive)

**P1 — Remaining:**
- [ ] EGOS-163: Pix billing integration

**P2 — Growth:**
- [ ] EGOS-165: White-label outreach
- [ ] EGOS-166: REST API gateway mode

---

### HQ Completion Program (2026-04-06)
**SSOT:** `docs/MASTER_INDEX.md` + `docs/SSOT_REGISTRY.md` + `docs/SYSTEM_MAP.md`
**Goal:** HQ becomes the non-hardcoded control plane for verified ecosystem reality.

**P0 — Truth normalization + /start evidence:**
- [ ] **HQC-004**: Add kernel SSOT pointers to `852`, `br-acc`, `carteira-livre`, `forja`, `egos-lab`; audit `policia`, `INPI`, `commons`

**P1 — Wiring + contracts:**
- [ ] **HQC-008**: Complete MCP setup gaps (obsidian, stripe, telegram) and make HQ consume installation truth
- [x] **HQC-009**: DUPLICATE of GTM-016 — guard-brasil-mcp package already exists
- [ ] **HQC-010**: Configure OpenClaw Gateway / WhatsApp / Telegram path without duplicated orchestration
- [ ] **HQC-011**: Remove hardcoded HQ data dependencies and drive HQ from canonical registries (`TASKS.md`, `agents.json`, `validation.json`, `CAPABILITY_REGISTRY.md`, `MASTER_INDEX.md`)
- [ ] **HQC-012**: Build `intelligence-engine.ts` and connect Dream Cycle outputs to HQ

**P2 — Ecosystem consolidation:**
- [ ] **HQC-013**: Fix HARVEST/KB dedup and freshness so HQ can trust knowledge surfaces
- [ ] **HQC-014**: Archive 11 dormant repos and close Santiago fix-or-kill
- [ ] **HQC-015**: Execute egos-lab kernel consolidation wave (`LAB-ARCHIVE-001..006`)

---

**Infra+Init DONE:** Neural Mesh telemetry ✅, codebase-memory-mcp 51K nodes ✅, KB wiki-compiler 50 pages ✅, CCR 3 jobs ✅
- [ ] **KB-017 [P2]**: Auto-learning from git commits | EGOS-169: @aiready/pattern-detect | EGOS-173: CRCDM auto-heal rename

---

### Eagle Eye — OSINT Licitações LIVE
**eagleeye.egos.ia.br** | 84 territories | 121 opportunities | daily cron 9am BRT
**Done (EAGLE-000..023):** standalone Docker, Supabase 6 tables, 26 detection patterns, Telegram alerts, PNCP enrichment, 80 territories seeded, integrador 70/30 channel doc, daily cron, real pipeline (36 opps R$10.5M).
- [ ] EAGLE-009: Stripe/Pix for Pro tier (R$497/mo)
- [ ] EAGLE-019: Integrador partnership outreach
- [ ] EAGLE-020: R$250k proposal — deadline 2026-04-29
- [ ] EAGLE-GH-003..010: Classification + extraction + profile + API v2 + MCP + Pix
- [ ] SANT-001: Santiago partner onboarding (MVP ready, waiting partner)

---

### Gem Hunter v6 — Research Discovery Engine LIVE
**CCR:** seg+qui 2h37 BRT | **Standalone API:** port 3097 | **npm:** @egosbr/gem-hunter v6.0.0
**Done (GH-001..066):** /study+/study-end skills, pair studies (Continue 71/100, Aider 74/100, Cline 72.8/100), PWC pipeline, Papers Without Code, KOL discovery, Telegram+Discord alerts, BRAID GRD, X-reply-bot (VPS hourly cron), ArchitectureSelector, cost-tracker, world-model signals, gem-hunter-server API, pricing.ts, Gateway /gem-hunter channel.

**Active — Pair Studies Queue:**
- [ ] GH-013: EGOS OpenHands | GH-014: EGOS LangGraph | GH-015: EGOS OpenAI Agents SDK | GH-016: EGOS LiteLLM | GH-017: EGOS Langfuse
- [ ] GH-020: EGOS Mem0 | GH-021: EGOS Temporal | GH-022: EGOS Haystack | GH-023: EGOS DSPy | GH-036: OpenHarness adapter

**Active — Product:**
- [ ] GH-025: `/pr` workflow + GitHub App (pre-merge gate)
- [ ] GH-026: Upgrade codebase-memory-mcp to HTTP/SSE transport
- [ ] GH-027: `.guarani/checks/` layer
**Gem Hunter product (revenue):**
- [ ] GH-073: Weekly email digest

**Gem Hunter CCR:**

**P1 — Reference Repo Study Queue (priority order):**
- [ ] GH-013: EGOS OpenHands (`OpenHands/OpenHands`) — full software agent SDK/CLI/GUI
- [ ] GH-014: EGOS LangGraph (`langchain-ai/langgraph`) — stateful long-running agents, durable execution
- [ ] GH-015: EGOS OpenAI Agents SDK (`openai/openai-agents-python`) — handoffs, guardrails, tracing
- [ ] GH-016: EGOS LiteLLM (`BerriAI/litellm`) — multi-model proxy, cost tracking, routing
- [ ] GH-017: EGOS Langfuse (`langfuse/langfuse`) — observability, prompt versioning, evals

**Aider study done (GH-031..039):** pre-edit-safety hook, CLAUDE.md §13 model guide, OpenHarness early-warning, Telegram gem alerts, BRAID Mode GRD, x-reply-bot VPS cron. Details: git log.
- [ ] GH-032: EGOS edit benchmark (SWE-Bench inspired, 20 tasks)
- [ ] GH-036: OpenHarness adapter in packages/shared/harness/

**Gem Hunter v5.1+v6.0 DONE (GH-043..065):** PWC pipeline, low-star scoring, ArchitectureSelector adapter, structural validation, auto-queue, signals ingestion, Papers Without Code, KOL discovery, evolution engine, multi-LLM fallback, Telegram alerts, multi-stage paper pipeline, cost budgeting, standalone API, MONETIZATION_SSOT, pricing.ts, gem-hunter npm v6.0.0. Details: git log.

*Month 2-3 — Product Scale:*
- [ ] GH-063: x402 pay-per-call — M2M agent payments via x402 protocol
- [ ] GH-067: Deploy gem-hunter-server to VPS (gemhunter.egos.ia.br) + Caddy routing → P0 revenue
- [ ] GH-070: Chatbot orchestrator — WhatsApp channel NLP intent → tool calls → gem-hunter → curated reply
- [ ] GH-072: Chatbot tier enforcement (200 queries/mo for R$149/mo chatbot plan)
- [ ] GH-073: Email digest — weekly top 10 gems to subscribers
- SSOT: docs/gem-hunter/GEM_HUNTER_PRODUCT.md

**P2:** GH-020..024 (Mem0, Temporal, Haystack, DSPy, Lego Assembler) — post PMF.

---

<!-- Claude Code Hardening (archived) — LEAK/AI/OBS 001..013 done. P2: LEAK-010..012, AI-008..010, OBS-010..013. Ref: awesome-claude-code. -->

<!-- X.com Presence (2026-04-01) — X-009/X-012 pending (blocked: XMCP-001 credentials). See TASKS_ARCHIVE_2026.md. -->

<!-- Block Intelligence + Eagle Eye (compressed) — MONETIZE-011/012 ENIO action required (Stripe meter + NOWPayments). See TASKS_ARCHIVE_2026.md. -->

### Partnership & Distribution Strategy (2026-04-05)
**Compressed:** See `docs/GTM_SSOT.md` + `docs/MONETIZATION_SSOT.md` for full roadmap.
- [ ] **PART-001**: Publish npm + ProductHunt (M-007 emails first)
- [ ] **PART-016**: Decide PARTNER-D1 co-founder model

---

### GTM & Incidents (P25-P35)
**SSOT:** `docs/GTM_SSOT.md` | INC-001 resolved. Guard Brasil bugs BUG-001/005/SEC-001 ✅.
- [ ] **GTM-001**: x-reply-bot search tuning (lgpd/anpd/dpo keywords)
- [/] **GUARD-BUG-002**: ATRiAN bias não existe. Demo corrigido. Feature futura.
<!-- GTM-006..013 and full context in TASKS_ARCHIVE_2026.md -->

### HQ Dashboard v2 (2026-04-06)
**Goal:** Mission Control shows full system state. **Prereq:** Volume mounts on VPS (data → /data/).
- [x] **HQV2-000 [P0]**: Docker volume mounts — /opt/data/egos → /data:ro, env vars AGENTS_REGISTRY_PATH/TASKS_MD_PATH/CAPABILITY_REGISTRY_PATH/JOBS_DIR, daily GitHub sync cron 09:00 UTC. ✅ 2026-04-09
- [x] **HQV2-001 [P1]**: `/api/hq/tasks` — parses /data/TASKS.md → total/pending/p0/p1/stale_p0/completion_pct. ✅ 2026-04-09
- [x] **HQV2-003 [P1]**: `/api/hq/gems` — proxies gateway gem-hunter/product endpoint. ✅ 2026-04-09
- [x] **HQV2-002 [P1]**: `/api/hq/world-model` — read /data/world-model/current.json → health%, blockers
- [x] **HQV2-004 [P1]**: `/api/hq/drift` — read /data/jobs/doc-drift-sentinel.md → structured drift per repo
- [x] **HQV2-005 [P1]**: `/api/hq/system-map` — agents.json + CAPABILITY_REGISTRY → graph data
- [ ] **HQV2-006..010 [P2]**: Dashboard pages — /tasks Kanban, /world-model gauge, /gems cards, /system-map D3, nav update

---

### P26 — MCPs + Focus v2.0 (2026-04-06)

**Completed:**

**Pending:**
- [ ] MCP-005: Obsidian MCP — needs vault path from Enio (`setup-obsidian-mcp.sh` ready, smithery CLI)
- [ ] MCP-006: Stripe MCP (`@stripe/mcp`) — needs Stripe secret key (on VPS only)
- [ ] MCP-007: Telegram MCP (`mcp-telegram`) — needs bot token
- [ ] MCP-008: Move `egos-knowledge` MCP from `egos/.claude/settings.json` → `~/.claude/settings.json` (make global)
- [/] GTM-016: `guard-brasil-mcp` package EXISTS at packages/guard-brasil-mcp/ — needs npm publish + Claude tool registration — wraps guard.egos.ia.br as Claude tool, publish as `@egosbr/guard-brasil-mcp` (GTM play: devs install it in their Claude session)
- [x] KB-019: `bun wiki:dedup` ✅ command exists in package.json — fix HARVEST.md 1944-line triplication caused by wiki:compile running without dedup

---

### Dream Cycle — Overnight Intelligence (2026-04-06)
**SSOT:** `docs/strategy/DREAM_CYCLE_SSOT.md` | Phase 1 ✅ (log-harvester running)
- [ ] **DC-004**: intelligence-engine.ts — reads nightly logs, writes egos_nightly_reports
- [ ] **DC-006**: Auto-Healer script — restart containers on known patterns
- [ ] **DC-009**: Morning Briefing 06h30 BRT — Telegram + WhatsApp
<!-- DC-005/007/008/011 moved to TASKS_ARCHIVE_2026.md -->

### Skills + Hooks Backlog (2026-04-06)
- [ ] **SKILL-001**: `/gate` command → `~/.claude/commands/gate.md`
- [ ] **SKILL-002**: `/mycelium-think` → `~/.claude/commands/mycelium-think.md`
- [x] **HOOK-001 [CANCELED]**: UserPromptSubmit hook — keyword→meta-prompt injection from triggers.json. **CANCELED 2026-04-11:** Skills já auto-roteiam via description: YAML. Hook adicionaria complexidade sem benefício. triggers.json atualizado v2.0.0 para apontar para skills corretos (6/11 targets estavam inexistentes).
- [ ] **HOOK-002**: RefineGate hook — vague prompt (<50 chars) → clarification guidance
<!-- SKILL-003 and context moved to TASKS_ARCHIVE_2026.md -->

<!-- ~~OpenClaw~~ DECOMMISSIONED 2026-04-08. Replaced by DashScope+OpenRouter+Hermes. SD-001..019 Self-Discovery deferred post-PMF. See TASKS_ARCHIVE_2026.md. -->

### VPS Infrastructure (P34-P35)
- [ ] **VPS-CAPACITY-001**: Capacity planning model (19 containers, Neo4j 4.8GB) [2h]
- [ ] **VPS-SWAP-001**: 4GB swap if RAM insufficient [P1, deferred]
<!-- Full context in TASKS_ARCHIVE_2026.md -->

### Hermes MVP (P35) — HERMES-001..004 ✅ DONE 2026-04-07/08
**Status:** systemd running 142MB RAM, DashScope qwen-plus + OpenRouter fallback. Trial period: 2026-04-07 → 2026-04-15.
- [ ] **HERMES-005-P1**: 7-day production trial (uptime/RAM/tokens/errors) [Owner: infra]
- [ ] **HERMES-005-P4**: Go/no-go gate 2026-04-15 → scale to 6 profiles [Owner: Enio]
<!-- HERMES-006..009 and details in TASKS_ARCHIVE_2026.md -->

### VPS Orchestration — DashScope + Hermes + Gemini CLI (P35)

**2026-04-08:** Codex + OpenClaw + Billing proxy DECOMMISSIONED. Engine: DashScope qwen-plus (primary) + OpenRouter free (fallback). Hermes systemd running.

- [ ] **ORB-003**: Cost attribution per task → Supabase [dev, 3h]
- [ ] **ORB-004**: HQ widget "Orchestration Status" [UI, 2h]

---

### Gem Research — P31 (2026-04-06): Graphify + A-Evolve + XMCP
**Source:** Grok analysis. Decisions: Graphify=adopt patterns only (codebase-memory-mcp overlap 80%); A-Evolve=bookmark pós PMF; XMCP=install now.

**XMCP — X MCP Server oficial (xdevplatform/xmcp):**
- [x] **XMCP-002**: Keys regeneradas e .env atualizado ✅ 2026-04-07. Serviço iniciado ✅ 2026-04-08 — PID 802844, port 8200, VPS 204.168.217.125. Dois patches em server.py: (1) usar tokens existentes ao invés de OAuth flow, (2) load_env() antes de ler MCP_PORT.
- [x] **SOCIAL-003 [P1]**: x-reply-bot — busca por "LGPD", "licitação", "split payment", "análise de vínculos" ✅ 2026-04-09
- [x] **SOCIAL-004 [P1]**: X Post HITL bot live ✅ 2026-04-08 — 3 alternatives + Telegram inline keyboard + choice learning (x_post_options, x_post_choices, x_post_preferences tables). VPS daemon running.
- [ ] **SOCIAL-005 [P2]**: Reply automático a @mentions com link produto relevante (aprovação manual)
- [ ] **SOCIAL-006 [P2]**: HQ dashboard tab social — candidatos DM, DMs enviadas, respostas
- [x] **XMCP-003** (dep: XMCP-002): UFW rules adicionadas (172.19.0.0/16 + 172.17.0.0/16 → port 8200). ✅ 2026-04-08
- [x] **XMCP-004** (dep: XMCP-002): Criar skill `egos-x-researcher` — usa XMCP searchPostsRecent para monitorar: lgpd, anpd, dpo, "proteção de dados". Saída → Supabase + HQ. ✅ 2026-04-08

**Graphify patterns (adotar sem instalar a lib):**
- [ ] **GRF-001 (P2)**: Criar CCR job `graph-report` — usa codebase-memory-mcp query_graph para gerar GRAPH_REPORT.md semanal (god nodes, surprising connections, clusters). Output em `docs/jobs/`.
- [ ] **GRF-002 (P2)**: Embutir graph.html (vis.js) no HQ como painel "Knowledge Graph" — feed de codebase-memory-mcp export. Parte de HQV2-009.
- [ ] **GRF-003 (P2)**: Adicionar ingestão multimodal ao wiki-compiler: PDFs + papers → Supabase `egos_wiki_pages`. Usa Graphify padrão (PDF→AST→nodes).

**A-Evolve patterns (bookmark pós PMF):** AEV-001..002 (P3) — manifest.yaml per skill + evolution loop. See git log for design.

### Governance Mesh Cleanup (2026-04-06 audit)
- [ ] **GOV-001**: CLAUDE.md → thin adapter to `.guarani` kernel [constitution drift]
- [ ] **GOV-002**: Unify workflow catalog (.windsurf/workflows + ~/.egos/workflows + workflow-sync-check.sh)
- [ ] **GOV-003**: Canonical skill distribution ~/.egos/skills vs ~/.claude/skills
- [ ] **GOV-004**: manifest.json SSOT hierarchy → kernel-first `.guarani`
- [ ] **GOV-005**: settings.local.json allowlist audit — hardcoded tokens, unsafe legacy permissions
- [ ] **GOV-006**: Sanitize stale ~/.egos artifacts (.windsurfrules, SSOT_STATUS_20260328.txt)
- [ ] **GOV-007**: Unify repo mesh registry (sync.sh + sync-all-leaf-repos.sh + manifest.json)

### Ratio Collaboration (2026-04-07) — PR #1 open, Guard Brasil wired
**Context:** Fork `enioxt/ratio` — Carlos Victor Rodrigues, Brazilian legal RAG + LangGraph drafting. Goal: PRs that demonstrate EGOS assets and open organic partnership. Branch: `feat/escritorio-multi-provider-llm`, PR #12 (103 tests passing).

**Done:** llm_provider 4 providers ✅ | pii_guard Guard Brasil ✅ | planning id-coercion ✅ | bot review issues ✅ | live pipeline 4/4 ✅ | frontend local ✅

- [ ] **RATIO-001 [P1]**: Submit PR #2 (Guard Brasil) as separate branch after PR #1 merged. Branch: `feat/escritorio-pii-guard`. LGPD compliance, fail-open, 8 tests.
- [ ] **RATIO-002 [P1]**: Open Issue on Carlos's repo re: LGPD gap (fatos_brutos with CPF → Gemini unmasked). Offer Guard Brasil free tier. Frame constructively. Metric: Carlos responds.
- [ ] **RATIO-003 [P2]**: br-acc entity resolution adapter — `entity_resolver.py` + `resolve_parties()` in intake. Maps party names → CPF/CNPJ/OAB/process history via br-acc API. PR #3.
- [ ] **RATIO-004 [P2]**: `.ratio-manifest.yaml` Doc-Drift Shield adoption PR. Claims: `total_documents: 471366`, `lancedb_store_gb: 8.5`. Verified via LanceDB count.
- [ ] **RATIO-005 [P2]**: Full end-to-end test via API with Caso 1 (STJ PDF real) → intake → planning → redaction → adversarial → formatter → download DOCX.
- [ ] **RATIO-006 [P3]**: Draft br-acc API pricing model for Carlos (free 100 lookups/mês + paid). Monetization path proposal.

### Chatbot SSOT v2.0 — World-Class Upgrade (2026-04-07) [DEFERRED — not in 90-day focus]
**SSOT:** `docs/modules/CHATBOT_SSOT.md` | **Done:** CHAT-001..010 ✅ | **Pending:** CHAT-011..031 (P1-P2, deferred)
<!-- Full task list moved to TASKS_ARCHIVE_2026.md -->

### Memory Intelligence — MemPalace + ARR Activation (2026-04-07) [DEFERRED]
**SSOT:** `packages/shared/src/cross-session-memory.ts` | **Pending:** MEM-001..004, GTM-X-001 (P1-P2, deferred)
<!-- Full task list moved to TASKS_ARCHIVE_2026.md -->

<!-- CORAL Pattern ✅ DONE — CORAL-001..003 all done 2026-04-08. gem_discoveries table live, Gem Hunter skip logic active. -->

### GovTech — Licitações de Software (2026-04-07) [P2 — post-PMF]
**SSOT:** `docs/GTM_SSOT.md` §govtech | **Pending:** GOV-TECH-001..010 (P1-P2, deferred)
<!-- Full task list moved to TASKS_ARCHIVE_2026.md -->

### Intelink v3 — Segurança + Multi-Device (2026-04-09) [P0 — standalone repo]
**SSOT:** `docs/knowledge/INTELINK_V3_SECURITY_ARCHITECTURE.md` | Repo: `/home/enio/egos-inteligencia/`
**Pending:** INTELINK-SEC-001..005, INTELINK-SYNC-001..004, INTELINK-DEVICE-001..004, INTELINK-TIER-001..004, INTELINK-HARD-001..004 — managed in egos-inteligencia/TASKS.md
<!-- Full task list moved to TASKS_ARCHIVE_2026.md -->

### Telegram Alerts Consolidation (2026-04-08)
**SSOT:** `docs/knowledge/TELEGRAM_ALERTS_AUDIT_2026-04-08.md`
**Context:** Audit de 8 fontes de alerta @EGOSin_bot. 5 ativos, 2 para verificar, 1 legado (OpenClaw). Meta: <10 alertas relevantes/dia.

**P0 — Limpeza:**
- [x] **NOTIFY-001**: OpenClaw already stopped on VPS — no systemctl service found (`systemctl stop/disable`)
- [x] **NOTIFY-002**: RAM monitor already configured correctly — warning <500MB, critical <100MB (vps-ram-monitor.sh:91/74)
- [ ] **NOTIFY-003**: Consolidar Doc Drift alerts em 1 sumário diário

**P1 — Botões e Interatividade:**
- [ ] **NOTIFY-004**: Inline keyboard no X Approval Bot
- [ ] **NOTIFY-005**: Botões no X Opportunity Alert
- [ ] **NOTIFY-006**: Comando `/task nova` no Telegram
- [ ] **NOTIFY-007**: Comando `/task lista`
- [ ] **NOTIFY-008**: Comando `/task feita` com auto-commit

**P2 — Config via Bot:**
- [ ] **NOTIFY-009**: Mapear serviços VPS para `/env` commands
- [ ] **NOTIFY-010**: Menu principal `/menu`

---

### Timeline + AI Publishing System (2026-04-08)
**SSOT:** `docs/TIMELINE_AI_PUBLISHING_ARCHITECTURE.md` | **Status:** TL-001 ✅ schema live.
**Context:** Auto-generate articles from commits → Supabase drafts → Human approval (Telegram/WhatsApp/HQ) → Publish to egos.ia.br/timeline + X.com. Principles: transparência radical, HITL (never blind publish), PII guard.

| Phase | Task | Description | Status |
|-------|------|-------------|--------|
| **1: Foundation** | TL-001 | Supabase: timeline_drafts + timeline_articles + x_post_queue | ✅ Done |
| | TL-002 | Agent: article-writer.ts — reads commit/diff, calls qwen-plus, writes draft | [x] |
| | TL-003 | Script: publish.sh manual trigger | [x] |
| | TL-004 | Telegram bot: approve flow (✅/✏️/❌) with 48h timeout | [x] |
| **2: Site público** | TL-005 | Bun/Hono: apps/egos-site — /timeline + /timeline/[slug] | [x] |
| | TL-006 | Route: GET /timeline — list articles paginated | [x] |
| | TL-007 | Route: GET /timeline/[slug] — render article + metrics | [x] |
| | TL-008 | Caddy: egos.ia.br → egos-site:3071 — live | [x] |
| **3: Automação** | TL-009 | timeline-cron-daily.sh — scan commits 24h (cron 03:00 UTC) | [x] |
| | TL-010 | Crontab: add timeline-cron-daily.sh | [x] |
| | TL-011 | auto-disseminate.sh: detect PUBLISH: → article-writer background | [x] |
| | TL-012 | x-reply-bot: postArticle(snippet, url) method | [ ] |
| **4: Multi-canal** | TL-013 | WhatsApp via Evolution API (same approval flow) | [ ] |
| | TL-014 | HQ tab: /timeline/pending with inline edit | [ ] |
| | TL-015 | OG image generation: apps/og-gen | [ ] |
| **5: Intelligence** | TL-016 | Weekly digest agent: 7 days → "What shipped this week" | [ ] |
| | TL-017 | Engagement feedback: low-engagement → flag for tone adjustment | [ ] |
| | TL-018 | PT→EN auto-translation via Deepl API | [ ] |

---

### Gem Hunter — Product Roadmap (2026-04-08)
**SSOT:** `docs/GEM_HUNTER_MARKET_DOMINATION_ROADMAP.md` | **Status:** GH-074 ✅ digest live.
**Context:** Build well, distribute honestly, let the right people find it. Multi-source + autonomous + quality-scored = genuine value for developers.

| Phase | Task | Description | Status |
|-------|------|-------------|--------|
| **A: Distribution** | GH-074 | gem-hunter-digest.ts — top 3-5 repos/week, markdown+Telegram (cron Thu 02:00 UTC) | ✅ Done |
| | GH-075 | Landing page: gemhunter.egos.ia.br (Bun/Hono, dark mode) — live | [x] |
| | GH-076 | Substack: Telegram HITL draft Thu 08:00 UTC — cron live | [x] |
| **B: Community** | GH-077 | Supabase: gem_lists + gem_votes + vote_count — RLS live | [x] |
| | GH-078 | API: /gems/:url/upvote + /trending + /lists/* — live port 3070 | [x] |
| | GH-079 | Dashboard: 👍 voting button + Top voted tab + dynamic API load | [x] |
| | GH-080 | github.com/enioxt/awesome-gems — created, README + 2026-04-08 gems | [x] |
| **C: Distribution** | GH-081 | Slack bot: /gem-hunter trending [lang] | [ ] |
| | GH-082 | Discord bot: !gems [lang] embed + buttons | [ ] |
| | GH-083 | Telegram @gem_hunter_bot: /trending /random /subscribe | [ ] |
| **D: Optional tiers** | GH-084 | Stripe: Free/Pro/Team tiers when community validates demand | [ ] |
| | GH-085 | Supply-chain risk endpoint: /gems/{id}/supply-chain-risk | [ ] |
| **E: MCP + Multi-Domain** | GH-086 | `@egosbr/gem-hunter-mcp` — MCP server (tools: search/trending/by_domain) for Claude Code/Windsurf/Cursor/Copilot, install by repo URL | [ ] |
| | GH-087 | Multi-domain sources: medical (PubMed/arXiv-bio), engineering (IEEE/papers-with-code), veterinary, finance/traders (QuantConnect/QuantStack), web3 (Awesome lists, Etherscan dev tools) — adapter pattern in `agents/gem-hunter/sources/` | [ ] |
| | GH-088 | Persona-aware scoring: same gem ranks differently for `--persona=doctor` vs `trader` vs `web3-dev` | [ ] |
| **Fixes 2026-04-08** | GH-FIX-1 | Caddyfile: gemhunter upstream `egos-site:3070` → `gem-hunter-landing:3070` (was 502) | [x] |
| | GH-FIX-2 | server.ts + index.html: query column `language` → `category` (404 in trending API) | [x] |

---

### X.com Public Posts — Transparency & Partnerships (2026-04-08)
**SSOT:** `docs/social/X_POSTS_SSOT.md` §8.5 | **Schedule:** N1 Mon 2026-04-14 → N8 Wed 2026-04-23 (2/week)
**Context:** 8 posts approved. Transparency strategy: show what's being built, attract aligned builders naturally.

| ID | Post | CTA | Schedule | Status |
|----|------|-----|----------|--------|
| **SOCIAL-001** | Open partnerships (equity flexible) | "DM aberta" | 2026-04-14 | ✅ Queued Supabase |
| **SOCIAL-002** | Gem Hunter spotlight | "DM para parceria" | 2026-04-15 | ✅ Queued Supabase |
| **SOCIAL-003** | Guard Brasil LGPD | "parceria compliance" | 2026-04-16 | ✅ Queued Supabase |
| **SOCIAL-004** | Researcher mindset | "DM aberta" | 2026-04-17 | ✅ Queued Supabase |
| **SOCIAL-005** | Transparência radical | "building in public" | 2026-04-18 | ✅ Queued Supabase |
| **SOCIAL-006** | Hermes decommission (Codex → qwen-plus chain) | "Vale ler pra agentic builders" | 2026-04-15 | ⏳ Queue |
| **SOCIAL-007** | Governance (26 SSOTs, 4-layer doc-drift) | "Vale ver se tá nesse pico" | 2026-04-17 | ⏳ Queue |
| **SOCIAL-008** | Call for builders | "DM aberta" | 2026-04-23 | ⏳ Queue |


---

### Supabase Cleanup (2026-04-08)
<!-- 4 task(s) archived 2026-04-08 — see TASKS_ARCHIVE_2026.md -->
**SSOT:** `docs/SUPABASE_AUDIT.md` | **Project:** `lhscgsqhiooyatkebose` | **State:** 173 tables, ~37 dead, 4 unrelated domains

- [ ] **SUPA-005 [P2]**: CCR weekly job — alert if any non-core table > 50 MB
- [ ] **SUPA-006 [P2]**: Naming convention rule — every new table prefixed with active domain (`egos_`, `gem_`, `guard_`, `intelink_`, `eagle_`, `x_post_`, `timeline_`, `852_`)

---

### CLAUDE.md Modular Refactor (2026-04-08)
<!-- 6 task(s) archived 2026-04-08 — see TASKS_ARCHIVE_2026.md -->
**SSOT:** `~/.claude/CLAUDE.md` | **Evidence:** arXiv "Curse of Instructions" + Lost in Middle + HumanLayer analysis
**Context:** 639 linhas, 30 seções = above reliable compliance threshold. §10-§20 systematically 30%+ lower compliance (middle blind spot). Solution: modular architecture — core file <120 lines + domain files loaded on demand.

**P0 — Reorder critical rules (30 min, immediate impact):**

**P1 — Modular split (2-3h, correct fix):**
- [ ] **RULES-004 [P1]**: Compress core ~/.claude/CLAUDE.md to <120 lines — only MUST/MUST NOT rules

**P2 — Skills for on-demand loading:**
- [ ] **RULES-006 [P2]**: Convert §12 (Scheduled Jobs) to a /start skill that loads on session open
- [ ] **RULES-007 [P2]**: Convert §28 (Auto-Disseminate) to a /disseminate skill

**Target after refactor:** ~100 lines core file, 7 domain files, compliance for critical rules at primacy position.
---
## Git Workflow — Branch Protection (INC-001 follow-up)
**Decision (2026-04-08):** Manter branch protection. GIT-001..003 RESOLVIDOS (já em main, divergência resolvida via rebase). Branch protection funcionando como esperado.
- [ ] **GIT-004 [P1]**: Documentar workflow PR-first em `CLAUDE.md` para mudanças >5 arquivos ou >100 linhas
- [x] **GIT-005 [P1]**: `scripts/create-pr.sh` ✅ 2026-04-09 — automatiza branch+push+gh CLI
- [x] **GIT-006 [P1]**: Comando `egos pr "título"` em `agents.json` ✅ 2026-04-09

---

### LLM Model Monitor — OpenRouter Intelligence System (2026-04-08)
**Context:** Pesquisa aprofundada revela 28+ modelos free no OpenRouter (Qwen3 Coder, Nemotron 3 Super, MiniMax M2.5, Step 3.5 Flash) e dezenas de modelos pagos com excelente custo-benefício (Kimi K2.5, DeepSeek V3.2, MiMo-V2-Pro). Necessário sistema automatizado para monitorar novos modelos, testar, comparar e adaptar fallbacks dinamicamente.
**SSOT:** `docs/knowledge/LLM_MODEL_MONITOR.md` (a criar) | **Fontes:** CostGoat, OpenRouter Rankings April 2026, TeamDay AI, Reddit r/LocalLLaMA, Digital Applied

**Models catalogued:** Qwen3 Coder 480B, Nemotron 3 Super, MiniMax M2.5, Step 3.5 Flash, Qwen3.6 Plus (free S-tier); Kimi K2.5, DeepSeek V3.2, MiMo-V2-Pro (paid best-value). Full tables: `docs/knowledge/LLM_MODEL_MONITOR.md`.

**P0 — Foundation (Agente Monitor):**
- [x] **LLM-MON-001 [P1]**: Criar `scripts/llm-model-monitor.ts` ✅ 2026-04-09 — agente que roda no VPS a cada 6h, consulta OpenRouter API `/models`, detecta novos modelos (free ou paid)
- [x] **LLM-MON-002 [P1]**: Integração MCP Exa ✅ 2026-04-09 — para cada novo modelo detectado, pesquisar reviews no Reddit, X.com, blogs técnicos (qualidade, benchmarks, casos de uso)
- [x] **LLM-MON-003 [P1]**: Supabase schema `llm_models` ✅ 2026-04-09 — armazenar: id, provider, name, pricing, context_length, capabilities, is_free, discovery_date, review_sentiment, benchmark_scores, egos_recommendation
- [x] **LLM-MON-004 [P1]**: Notificações ✅ 2026-04-09 — alertar no Telegram/WhatsApp quando modelo promissor (S-tier) é detectado, com summary do research Exa

**P1 — Test & Comparison Engine:**
- [x] **LLM-MON-005 [P1]**: `scripts/llm-test-suite.ts` — 9 testes em 5 categorias: coding(2), reasoning(2), long_ctx(1), agentic(2), ptbr(2). Scoring 0-100 + Supabase storage. `--model`, `--category`, `--dry`. ✅ 2026-04-09
- [x] **LLM-MON-006 [P1]**: `scripts/llm-auto-test.ts` — queries llm_models S-tier, skips already-tested (7d window), runs llm-test-suite.ts, Telegram summary. `--dry`, `--force <model>`. ✅ 2026-04-09
- [ ] **LLM-MON-007 [P2]**: Benchmark Comparison — comparar resultados do novo modelo vs current fallback chain, gerar report `docs/knowledge/LLM_MODEL_COMPARISON_YYYY-MM-DD.md`
- [ ] **LLM-MON-008 [P2]**: Fallback Chain Auto-Update — se novo modelo supera current fallback em quality/cost, propor atualização de `packages/shared/src/llm-provider.ts` via PR automático

**P2 — Intelligence & Adaptation:**
- [ ] **LLM-MON-009 [P2]**: Task-Based Routing — mapear cada categoria de teste para tipo de task EGOS (chat, review, summary, intelligence, coding) e sugerir modelos específicos por tarefa
- [ ] **LLM-MON-010 [P2]**: Cost Optimization Engine — monitorar gasto real do OpenRouter (via API key usage), alertar quando alternativa free/cheaper atinge paridade de qualidade
- [ ] **LLM-MON-011 [P2]**: Dashboard no HQ — visualizar: modelos monitorados, scores de testes, fallback chain atual, economia gerada por otimizações
- [ ] **LLM-MON-012 [P2]**: Integration com CORAL — quando modelo é validado como S-tier, salvar discovery no `gem_discoveries` para reuso por outros agentes

---

### Content Orchestrator v2 — OpenMontage + OpenScreen (2026-04-08) [P2 — deferred]
**SSOT:** `docs/knowledge/CONTENT_ORCHESTRATOR_V2.md` | **Pending:** CONTENT-001..014 (P1-P2, deferred)
<!-- Full task list moved to TASKS_ARCHIVE_2026.md -->

### Test & Validation Orchestrator v2 — Multi-Agent Review (2026-04-08) [P2 — deferred]
**SSOT:** `docs/knowledge/TEST_ORCHESTRATOR_V2.md` | **Pending:** TEST-001..013 (P1-P2, deferred)
<!-- Full task list moved to TASKS_ARCHIVE_2026.md -->

### Auto-Disseminate Agent Pipeline (2026-04-08)
**SSOT:** `docs/CAPABILITY_REGISTRY.md` §25 | **Context:** `/disseminate` hoje é manual e custoso em tokens. Goal: 3-agent pipeline post-commit → propagação automática → Enio aprova via Telegram.

- [x] **DISS-001 [P1]**: `scripts/disseminate-scanner.ts` — lê `git diff HEAD~1` nos kernel files, identifica seções que mudaram, gera manifest `{changed_rules: [], affected_repos: []}` | 2h ✅ 2026-04-08
- [x] **DISS-002 [P1]**: `scripts/disseminate-propagator.ts` — recebe manifest, para cada repo: atualiza bloco kernel no marker `# EGOS-KERNEL-PROPAGATED`, cria commit `chore(kernel): propagate YYYY-MM-DD` | 3h ✅ 2026-04-08
- [x] **DISS-003 [P1]**: `scripts/disseminate-verifier.ts` ✅ — verifica marker EGOS-KERNEL-PROPAGATED em todos repos, output pass/fail/skip. 12/12 pass. | 2h ✅ 2026-04-09
- [x] **DISS-004 [P1]**: post-commit hook trigger — quando CLAUDE.md | .windsurfrules | CAPABILITY_REGISTRY.md muda, auto-chama scanner | 1h ✅ 2026-04-08
- [x] **DISS-005 [P1]**: Telegram approval gate — PUBLISH: commits queue + Telegram notify, approve via /approve-pub. ✅ 2026-04-09
- [ ] **DISS-006 [P2]**: VPS propagation — após aprovação local, SSH push kernel block para os 4 repos no VPS (`/opt/852`, `/opt/bracc`, `/opt/egos`, `/opt/egos-lab`) | 2h ✅ 2026-04-08

---

### Paperclip Integration Patterns (2026-04-08)
**SSOT:** `docs/knowledge/HARVEST.md` KB-028 | **Source:** github.com/paperclipai/paperclip (49.9K⭐, MIT) | **Strategy:** EGOS = safety/compliance kernel inside Paperclip, not competing.

**Adoptable NOW (sem Paperclip dependency):**
- [x] **PAP-001 [P1]**: Heartbeat loop nativo — `agents/runtime/heartbeat.ts` (wrapper, runner.ts FROZEN): ciclo wake(30min) → checkWorkQueue() → runAgent() → emit(bus) → sleep. Configurable per-agent. ✅ 2026-04-08
- [x] **PAP-002 [P1]**: Per-agent budget enforcement ✅ 2026-04-09 — estender Guard Brasil token counter: campo `monthly_cap` per agent_id, auto-pause signal quando 100%, warning Telegram 80%. | 3h
- [ ] **PAP-003 [P2]**: Goal ancestry em TASKS.md — adicionar coluna `WHY` em tasks (link para parent goal). Template: `[PAP-003] Fix X → goal: Y → mission: Z`. | 1h

**Integration (com Paperclip):**
- [ ] **PAP-004 [P2]**: EGOS↔Paperclip adapter — registra agents EGOS como "employees" do Paperclip. Guard Brasil valida outputs antes de retornar ao Paperclip. Repositório: `@egosbr/paperclip-adapter`. | 8h
- [ ] **PAP-005 [P3]**: Pitch adapter para @dotta (criador Paperclip) — "EGOS adds LGPD/PII compliance layer for Brazilian Paperclip users." DM via GitHub Issues ou X.com. | 1h

---

### Live School — The Observatory (reativação EGOSv2)
**SSOT:** `egos-archive/v2/EGOSv2/live_school_redesign/` + `modules/egos_learning_orbit/` | **Status:** EGOSv2 completo, precisa rewrite Bun/TS
**Conceito:** Tela inteira cosmos 3D (React Three Fiber) + 3 agentes AI (EVA/GUARANI/MAIÊUTICA). "Ensinar é recordar o que já se é" — método maiêutico socrático (do grego μαιευτική: arte de parir ideias).

- [x] **LS-001 [P2]**: Análise assets EGOSv2 — ObservatoryLanding.tsx (React Three Fiber), 3 agentes Python, design_concept.md → gerar spec moderna Bun/TS. Decisão: standalone app ou integrar em egos-site? | 2h ✅ 2026-04-08
- [ ] **LS-002 [P2]**: Port EVA+GUARANI+MAIÊUTICA para TypeScript — usar EGOS agent-runner como base. Guard Brasil wrapping dados de alunos (LGPD). | 6h
- [ ] **LS-003 [P3]**: Observatory UI — Bun/Hono + React Three Fiber — tela cósmica full-screen. Stars, órbitas gravitacionais, portal de entrada. Base: `live_school_redesign/src/components/ObservatoryLanding.tsx` | 8h

---

### KB-as-a-Service — "EGOS Knowledge" (2026-04-08)
**SSOT:** `docs/strategy/KB_AS_A_SERVICE_PLAN.md` | **Parent:** Track A+B+C+D
**Contexto:** Produtizar wiki-compiler + atomizer + ARR + Guard Brasil + Notion MCP nativo como serviço de "Cérebro Externo Governado" para profissionais brasileiros. FORJA = beta. Notion = frontend (curva baixa). Claude Code $20/mês = motor no cliente. EGOS kernel = governance.
**Unlock 2026-04-08:** Notion MCP nativo descoberto (`mcp__claude_ai_Notion__*`) — eliminou blocker de integração custom.

**P0 — Dogfooding + template + FORJA (próximas 2 semanas):**
- [x] **KBS-001 [P0]**: Criar template Notion "Inteligência da Empresa" via MCP — DB Documentos, DB Q&A, DB Decisões, página "Como usar" PT-BR. Duplicável. | 4h ✅ 2026-04-08 (done in prev session — 10 sector templates + FORJA demo live in Notion)
- [x] **KBS-002 [P0]**: Escrever `CLAUDE.md` cliente (≤100 linhas, PT-BR, placeholders por setor — metal/jurídico/saúde). Salvar em `packages/knowledge-mcp/templates/CLAUDE.md.tpl`. | 2h ✅ 2026-04-08
- [x] **KBS-003 [P0]**: Guia setup PT-BR — `docs/guides/KBS_ONBOARDING_PT_BR.md` — install Claude Code → OAuth Notion MCP → primeiro `/ingest` + `/ask`. Com screenshots. | 3h ✅ 2026-04-09
- [x] **KBS-004 [P0]**: FORJA namespace beta — `clients/forja/` ou branch no FORJA repo, `.guarani/forja-rules.md`, ingestar 10 docs piloto (orçamento antigo, ficha produção, ABNT referenciada). | 6h ✅ 2026-04-08
- [x] **KBS-005 [P0]**: Loom demo 3–5min PT-BR — "Sua Inteligência da Empresa em 5 minutos". Gravar usando dogfooding interno (TASKS.md + HARVEST.md como exemplo). ✅ 2026-04-08
- [x] **KBS-006 [P0]**: PDF/Docx ingestor — `scripts/kb-ingest.ts` via `unpdf` + `mammoth` + Guard Brasil PII scan. `ingest_file` tool adicionado ao knowledge-mcp. ✅ 2026-04-09
- [x] **KBS-007 [P0]**: KB-lint — `scripts/kb-lint.ts` — orphans, stale >90d, low_quality <40, broken_refs, duplicates, empty <100chars. Auto-fix broken_refs com --fix. Exit 1 em erros (CI-ready). ✅ 2026-04-09
- [x] **KBS-008 [P0]**: `packages/knowledge-mcp/` completo — tools: ingest_file, kb_lint, kb_export (+ search_wiki, get_page, get_stats, record_learning). Publicado `@egosbr/knowledge-mcp@1.1.0` npm. ✅ 2026-04-09
- [x] **KBS-009 [P0]**: Dogfooding interno — apontar knowledge-mcp para TASKS.md + HARVEST.md + handoffs. Usar 2 semanas antes de qualquer venda. Gate: 10 queries/dia por 14 dias. ✅ 2026-04-09 — 50 docs indexados (TASKS/HARVEST/CAPABILITY_REGISTRY/handoffs/ecosystem state)

**P1 — Produto público + pricing (semanas 3-6):**
- [ ] **KBS-010 [P1]**: Landing page "EGOS Knowledge" no `egos-site/` — 1 página, hero + 3 tiers + demo embed + CTA WhatsApp. PT-BR. | 6h
- [ ] **KBS-011 [P1]**: Pricing page detalhada — Starter R$1.5k / Pro R$5k / Enterprise R$15k+. Comparação com consultoria tradicional. | 3h
- [ ] **KBS-012 [P1]**: Contract template — serviço de implementação + manutenção. Revisado por advogado (network Enio). | 4h
- [x] **KBS-013 [P1]**: Onboarding checklist — `docs/guides/KBS_DELIVERY_CHECKLIST.md` — passo-a-passo replicável (discovery → contrato → setup → treinamento → handoff). ✅ 2026-04-09
- [ ] **KBS-014 [P1]**: Primeiros 3 leads aligned (não vaga, não cold sales) — advogado brasileiro, PME metal além de FORJA, clínica. Research via exa/firecrawl em grupos WhatsApp/Telegram e Twitter. | 4h
- [x] **KBS-015 [P1]**: Template Notion público no GitHub (`egosbr/knowledge-template`) — MIT, com instruções de duplicação. ✅ 2026-04-08
- [x] **KBS-016 [P1]**: Multi-tenant Supabase — RLS por `tenant_id`, migration `egos_wiki_pages_tenanted`. Antes do 2º cliente Pro. ✅ 2026-04-09
- [ ] **KBS-017 [P1]**: Stripe billing tiers (Starter/Pro/Enterprise) — reusar infra Guard Brasil. Cartão BRL aceito. | 4h
- [x] **KBS-018 [P1]**: Citation export — comando `/export` produz Markdown + PDF com fontes numeradas. ✅ 2026-04-09 — `scripts/kb-export-citations.ts` + `kb_export_citations` tool no knowledge-mcp
- [x] **KBS-019 [P1]**: Guard Brasil hook no ingest — todo `/ingest` roda via `guard_scan_pii` primeiro, redação automática, alerta no Telegram se PII detectada. ✅ 2026-04-09

**P2 — Scale + evolução (mês 2+):**
- [ ] **KBS-020 [P2]**: Multi-idioma PT+EN no mesmo vault — tag `lang` no schema, query filter. Para clientes bilíngues. | 6h
- [ ] **KBS-021 [P2]**: Dream Cycle integration — KB linting automático noturno (batch `kb:lint` em todos tenants ativos). | 4h
- [ ] **KBS-022 [P2]**: Agente "KB-Librarian" — agente EGOS dedicado que mantém KB do cliente (dedup, sugere cross-refs, flagga staleness). Roda via hermes-gateway. | 8h
- [ ] **KBS-023 [P2]**: `/ingest` via web clipper — Chrome extension que envia URL para o KB do cliente. | 6h
- [ ] **KBS-024 [P2]**: Health dashboard por tenant — página Notion auto-atualizada com stats (total docs, staleness, queries/semana, linting score). | 4h
- [ ] **KBS-025 [P2]**: Vídeos de caso de uso por setor — jurídico, metal, saúde, consultoria. 2–3 min cada, PT-BR. | 8h
- [ ] **KBS-026 [P2]**: Certificação "EGOS Knowledge Implementer" — programa leve para parceiros que queiram revender serviço. | on-going

#### P0 — Entity Graph Layer (KBS v2 — "EGOS como caso-demo") [2026-04-12]

> **Visão:** KB-as-a-Service não é só RAG (chunk + busca). É extração de entidades + mapeamento de relacionamentos + relatórios de inteligência por setor. EGOS é o primeiro caso real — construir aqui = template replicável para qualquer cliente.

- [ ] **KBS-027 [P0]**: Schema de entidades para EGOS demo — definir tipos: Agent, Task, Capability, Incident, Decision, Pattern, Integration. Criar `docs/strategy/KBS_ENTITY_SCHEMA_EGOS.md` com atributos, exemplos e relacionamentos para cada tipo. | 3h
- [ ] **KBS-028 [P0]**: Migração Supabase — tabelas `egos_entities` (id, tenant_id, type, name, attributes jsonb) e `egos_relationships` (id, source_entity_id, target_entity_id, relation_type, context, doc_source). RLS por tenant. | 4h
- [ ] **KBS-029 [P0]**: Agente entity-extractor — dado um wiki_page já ingerido, usar LLM para extrair entidades tipadas e inserir em `egos_entities`. Dry-run first. Agent: `agents/agents/kb-entity-extractor.ts`. | 6h
- [ ] **KBS-030 [P0]**: Relationship mapper — após extração, cruzar entidades entre docs e criar `egos_relationships`. Algoritmo: mesmo nome + tipo → tentar linkar; LLM confirma. | 6h
- [ ] **KBS-031 [P0]**: EGOS Intelligence Report — relatório semanal gerado do grafo de entidades: capabilities ativas, incidentes abertos, decisões recentes, agents por status. Output: Notion page + Markdown. | 6h
- [ ] **KBS-032 [P0]**: EGOS como showcase completo — ingerir 100% dos docs SSOT (TASKS, HARVEST, CAPABILITY_REGISTRY, handoffs, agents.json, incidents), extrair entidades, gerar relatório, criar Notion dashboard. Este IS o portfólio. | 8h

#### P1 — Sector Templates (replicar EGOS para clientes)

- [ ] **KBS-033 [P1]**: Schema entidades — Delegacia (policial) — tipos: Pessoa, Veículo, Caso, Local, Evento, Organização, Arma. Relacionamentos: Pessoa→envolvida→Caso, Veículo→placa→Pessoa, Caso→ocorreu_em→Local. | 4h
- [ ] **KBS-034 [P1]**: Schema entidades — Advocacia — tipos: Cliente, Processo, Audiência, Jurisprudência, Contrato, Prazo, Vara. Relacionamentos: Cliente→parte→Processo, Processo→cita→Jurisprudência. | 4h
- [ ] **KBS-035 [P1]**: Schema entidades — Agronomia — tipos: Propriedade, Cultura, Análise, ART, Defensivo, Norma, Produtor. Relacionamentos: Análise→recomenda→Defensivo, ART→cobertura→Propriedade. | 3h
- [ ] **KBS-036 [P1]**: Validação delegacia própria (DHPP/Inteligência) — usar template KBS-033 no contexto policial de Enio. Ingerir docs internos (sem dados reais de investigação). Validar ROI, gerar relatório. Portfolio item #1. | 8h
- [ ] **KBS-037 [P1]**: Delivery checklist v2 — atualizar `docs/guides/KBS_DELIVERY_CHECKLIST.md` com fase de entity extraction + relationship mapping. Adicionar estimativas de tempo com layer de entidades. | 2h

#### P0 — ICP + Client Dashboard (pré-requisito de vendas)

- [x] **KBS-038 [P0]**: ICP (Ideal Customer Profile) — documentar persona exata em `docs/strategy/KBS_ICP.md`. Critérios obrigatórios: (1) já usa IA ativamente, (2) já assina ou disposto a assinar Claude Pro $20/mês ou equivalente, (3) tem base de dados digital própria (documentos, clientes, casos, propriedades), (4) sente dor de "não acho o que preciso" ou "perco tempo buscando informação". Setor é secundário — comportamento é primário. Incluir: como qualificar em 5 min numa conversa, red flags, green flags. | 3h ✅ 2026-04-12
- [ ] **KBS-039 [P0]**: Client dashboard v1 (Notion) — página central por cliente com: (a) Visão geral das entidades extraídas (counts por tipo), (b) Relatório semanal de inteligência mais recente, (c) Saúde dos documentos (staleness, orphans, linting score), (d) Últimas queries feitas, (e) Link rápido para "/perguntar". Template duplicável em 10 min. | 6h

#### P3 — KBS Dissemination para produtos EGOS (baixa prioridade, não bloqueia foco)

> **Arquitetura:** `@egosbr/knowledge-mcp@1.1.0` já no npm. Multi-tenant Supabase com RLS por `tenant_id`. Disseminar = MCP no `.claude/settings.json` do repo + namespace + ingest de docs do domínio. Zero código novo. Cada produto ganha `/ask /ingest /lint` no próprio contexto.

> **Ordem:** EGOS (feito) → 852 → Eagle Eye → Carteira Livre → DHPP → outros.

- [ ] **KBS-DISS-001 [P3]**: Guia leaf repos — `docs/guides/KBS_LEAF_REPO_SETUP.md`: adicionar knowledge-mcp ao settings.json, definir tenant_id, ingerir docs, testar /ask. Replicável em <30min. | 2h
- [ ] **KBS-DISS-002 [P3]**: **852** KB — chatbot público. Domínio: FAQs, docs públicas, knowledge de Enio. Tenant: `852`. 852 responde baseado em conteúdo real, sem alucinação. | 3h
- [ ] **KBS-DISS-003 [P3]**: **Eagle Eye** KB — licitações OSINT. Domínio: normas PNCP, limites de dispensa, jurisprudência TCU/CGU. Tenant: `eagle-eye`. Agente cita norma ao responder dúvidas regulatórias. | 4h
- [ ] **KBS-DISS-004 [P3]**: **Carteira Livre** KB — DeFi + tributação cripto. Domínio: regulações CVM/BACEN, limites IR cripto, protocolos DeFi. Tenant: `carteira-livre`. | 4h
- [ ] **KBS-DISS-005 [P3]**: **FORJA** KB — promoção KBS-004 beta → produção. Tenant: `forja`. Namespace existe — validar + ingerir docs reais. | 2h
- [ ] **KBS-DISS-006 [P3]**: **DHPP/Inteligência** KB — contexto profissional de Enio. Domínio: procedimentos (sem dados reais), normas perícia, jurisprudência penal. Tenant: `dhpp`. Portfolio item #1. | 6h
- [ ] **KBS-DISS-007 [P3]**: Cron VPS — `/lint` semanal em todos tenants + relatório consolidado no HQ. | 3h

---

### API Monetization — x402 Marketplaces (carry-over 2026-04-07)
**SSOT:** `docs/strategy/KB_AS_A_SERVICE_PLAN.md` §4.2 + `~/.codeium/windsurf-next/API_MARKETPLACES_MASTER_ANALYSIS.md` | **Parent:** Camada B monetização
**Context:** Publicar Guard Brasil + (futuramente) knowledge-mcp + OSINT Brasil em marketplaces agent-native para receber USDC global via protocolo x402. AGENTCASH-001..012 foram consolidados em API-001..019.

**P0 — Tier 1 x402 native (0% comissão):**
- [x] **API-001 [P0]**: AgentCash onboard — wallet Base: 0x8C26958753cdfc6434455021F330BF95FD260b2f, Solana: HkwMoWsUMEpFRVJLLW4sALgFg35jdU1VFFmFgVJL8Jpe (balance $0, invite redeemed). ✅ 2026-04-09
- [ ] **API-002 [P0]**: APINow.fun provider signup — criar conta em `https://www.apinow.fun/providers`, instalar `apinow-sdk`. | 1h
- [ ] **API-003 [P0]**: Proxies.sx marketplace avaliação — verificar fit com OSINT Brasil scraping em `https://proxies.sx/marketplace`. | 1h
- [x] **API-004 [P0]**: Wallet Base chain — criar wallet dedicada para receber USDC (não usar wallet pessoal). Documentar em `memory/infra_credentials_ssot.md`. | 1h ✅ 2026-04-08
- [x] **API-005 [P0]**: x402 middleware no Guard Brasil — branch `feat/x402-marketplaces`, middleware HTTP 402 que aceita USDC on-demand. | 6h ✅ 2026-04-08
- [x] **API-006 [P0]**: Publicar Guard Brasil v0.2.3 no AgentCash — primeiro deploy, pricing $0.001-0.005/call. | 3h ✅ 2026-04-08

**P1 — Tier 1 expansão:**
- [x] **API-007 [P1]**: Publicar Guard Brasil no APINow.fun — avaliar tokenization do endpoint popular. | 2h ✅ 2026-04-08 ✅ 2026-04-08
- [ ] **API-008 [P1]**: Publicar OSINT Brasil scraping no Proxies.sx — match perfeito com 0% comissão. | 4h
- [x] **API-009 [P1]**: OpenAPI spec universal — `openapi.yaml` que serve todos os marketplaces. ✅ 2026-04-09 — `apps/egos-gateway/openapi.yaml` (OAS 3.1, Guard Brasil + KB + Gem Hunter), served at `/openapi.yaml`
- [ ] **API-010 [P1]**: Dashboard monetização no HQ — mostra receita x402 por plataforma, calls/dia, top consumers. | 4h

**P2 — Tier 2 tradicionais:**
- [ ] **API-011 [P2]**: RapidAPI freemium listing do Guard Brasil (4M+ devs, 20% comissão). | 4h
- [ ] **API-012 [P2]**: Replicate — avaliar fit (foco ML models, pode não servir). | 2h ✅ 2026-04-08
- [ ] **API-013 [P2]**: DigitalAPI — curated enterprise listing. | 3h
- [ ] **API-014 [P2]**: APILayer listing. | 2h ✅ 2026-04-08
- [ ] **API-015 [P2]**: APYHub credits system. | 2h ✅ 2026-04-08
- [ ] **API-016 [P2]**: Zyla Labs listing. | 2h ✅ 2026-04-08
- [ ] **API-017 [P2]**: Mintlify docs sync para API portal. | 3h
- [x] **API-018 [P2]**: Knowledge MCP publicado como API x402 — `@egosbr/knowledge-mcp` exposto via AgentCash após KBS-008 pronto. | 4h ✅ 2026-04-09
- [ ] **API-019 [P2]**: x402 + Stripe hybrid billing — cliente escolhe crypto ou cartão na checkout. | 6h

---

### Session Carry-over — DISS + PAP + LS (2026-04-08 → próximas sessões)
**SSOT:** `docs/_current_handoffs/handoff_2026-04-08_end.md` | **Parent:** Track E manutenção
**Context:** Tasks pendentes do session end 2026-04-08. Não perder de vista enquanto KBS-* toma espaço.

**P0 — Desbloqueio GTM:**
- [x] **XMCP-002 [P0]**: xmcp started on VPS :8200 ✅ 2026-04-09
- [x] **DISS-002 [P0]**: `scripts/disseminate-propagator.ts` — propaga kernel blocks pós-scanner (DISS-001 ✅). Target: blocks de rules via `scripts/auto-disseminate.sh`. | 3h ✅ 2026-04-08
- [x] **DISS-003 [P0]**: `scripts/disseminate-verifier.ts` ✅ — 12/12 repos verified. | 2h ✅ 2026-04-09
- [x] **DISS-005 [P0]**: Telegram approval gate para propagação — /approve antes de push. | 2h ✅ 2026-04-09
- [x] **PAP-002 [P0]**: Per-agent monthly token budget — estender Guard Brasil token counter com `monthly_cap` por agent_id, auto-pause + alerta 80%. | 3h ✅ 2026-04-09

**P1 — GH-086 + LS-002 (Sprint 1 continuação):**
- [ ] **GH-086 [P1]**: `@egosbr/gem-hunter-mcp` — MCP server (3 tools: `gh_search`, `gh_trending`, `gh_score`) para Claude Code/Windsurf/Cursor. Blocked by §26 completion. | 6h
- [ ] **LS-002 [P2]**: Port EVA+GUARANI+MAIÊUTICA para TypeScript — ver seção Live School acima. | 6h

---

### KB-as-a-Service — Patos de Minas (KBS-PM-*) (2026-04-08)
<!-- 11 task(s) archived 2026-04-08 — see TASKS_ARCHIVE_2026.md -->
**SSOT:** `docs/strategy/KBS_PATOS_DE_MINAS_PERSONAS.md` | **Notion workspace:** https://www.notion.so/33ce6358f08081ac8d41c001a87a7445
**Contexto:** 10 perfis profissionais de Patos de Minas criados no Notion via MCP. Templates com databases reais e dados demo. ERP replacement narrative: EGOS não substitui ERP — vira camada de inteligência em cima. Ingestão de DOC/DOCX/PDF/áudio/vídeo.
**Notion pages criadas:**
- 🧠 Root: https://www.notion.so/33ce6358f08081ac8d41c001a87a7445
- 🌾 Agrônomo: https://www.notion.so/33ce6358f08081159239f78684c78794
- ⚖️ Advocacia: https://www.notion.so/33ce6358f08081afa23de233c4e2639d
- 💰 Contador: https://www.notion.so/33ce6358f08081afbce2d227d3639f79
- 🏭 FORJA Demo: https://www.notion.so/33ce6358f08081a4baccd88685b62f29

**P0 — Dados demo + dogfooding (próximas 48h):**
- [x] **KBS-PM-006 [P0]**: Gravar Loom demo 5min PT-BR usando FORJA como exemplo — "Do orçamento em 2h para resposta em 10s". Usar dados demo populados. ✅ 2026-04-08

**P1 — Completar perfis P1 com databases (próximas 2 semanas):**
- [ ] **KBS-PM-012 [P1]**: PDF/áudio ingestor — plugar `unpdf` + `mammoth` + `whisper-api` no wiki-compiler. Input: pasta com arquivos mistos, output: atoms em egos_wiki_pages. | 8h
- [ ] **KBS-PM-013 [P1]**: Testar pipeline completo: ingestar 5 documentos reais de cada perfil P0 → query com citações → verificar accuracy. | 4h

**P1 — Narrativa ERP Replacement (posicionamento):**
- [ ] **KBS-PM-015 [P1]**: Post X.com thread sobre ERP replacement + demo FORJA (3 tweets). Usar narrativa do 1-pager. Agendar via sistema de aprovação. | 1h
- [ ] **KBS-PM-016 [P1]**: Abordagem direta de 3 metalúrgicas em Patos de Minas via LinkedIn/WhatsApp — oferecer demo gratuita com dados deles. | 2h ✅ 2026-04-08

**P2 — Completar perfis P2 + escala:**
- [ ] **KBS-PM-017 [P2]**: Criar databases para Cooperativa (perfil 08) — Cooperados, Preços, Insumos, CONAB, Safra. | 2h ✅ 2026-04-08
- [ ] **KBS-PM-018 [P2]**: Criar databases para Imobiliária Rural (perfil 09) — Propriedades, CAR/CCIR, Histórico transações, Situação ambiental. | 2h ✅ 2026-04-08
- [ ] **KBS-PM-019 [P2]**: Criar databases para SENAR/Escola (perfil 10) — Cursos, Competências, Experimentos, Turmas. | 2h ✅ 2026-04-08
- [ ] **KBS-PM-020 [P2]**: Guia de replicação — documento PT-BR "Como duplicar e configurar em 15 minutos" para qualquer um dos 10 perfis. | 3h
- [ ] **KBS-PM-021 [P2]**: Gravar 2 vídeos demo adicionais: Advocacia (prazo processual em segundos) + Agrônomo (defensivo por carência). | 4h

---

### Gem Hunter — Feedback Loop v8 (2026-04-08)
<!-- 7 task(s) archived 2026-04-08 — see TASKS_ARCHIVE_2026.md -->
**Status 2026-04-09:** GH-090 ✅ scoring-v1.md | GH-091 ✅ low-visibility gem +25 | GH-092 ✅ gem_feedback table | GH-093 ✅ inline keyboard | GH-094 ✅ feedback-reader.ts | GH-095 ✅ repetition detector (gem_seen_cache + -30 penalty). P2 remaining: GH-096/097.

**P1 — Fundações (fazer primeiro, desbloqueiam todo o resto):**

**P2 — Self-improvement loop:**
- [ ] **GH-096 [P2]**: HQ aba "Feedback Loop" — score drift chart, approve/reject rate, top false positives. | 8h
- [ ] **GH-097 [P2]**: `scripts/scoring-prompt-evolver.ts` — agrega feedback mensal, propõe rewrite de `scoring-v1.md` → Enio aprova via HQ → vira `scoring-v2.md`. | 6h

---

### FORJA Chatbot Pilot — Referência (repo standalone)
**FORJA é repo standalone em `/home/enio/forja/`. Tasks FORJA adicionadas lá.**
- [/] **FORJA-003**: RLS migrations ✅ + RBAC roles ✅ + isolation test ✅ (`scripts/test-rls-isolation.ts`). **ENIO:** run `bun scripts/test-rls-isolation.ts` to verify + enable Google OAuth in Supabase dashboard.
- Tasks P0 em `/home/enio/forja/TASKS.md`: FORJA-004B (Design Oficina), FORJA-019B (Email Pipeline), FORJA-020 (WhatsApp bidirecional), FORJA-TOOLS-001 (budget_tool/cost_history/ata_extractor), FORJA-TOOLS-002 (Whisper), FORJA-KBS-001 (namespace EGOS Knowledge)
- KBS-003..007 já existem em egos/TASKS.md (seção KB-as-a-Service)
- Para trabalhar no FORJA: `cd /home/enio/forja && claude`

---

### Safety & Testing — Guard Brasil + ATRiAN (2026-04-08)
**Context:** Windsurf session identificou gap: faltam 50 amostras reais + k6 load test + fuzzing. ATRiAN ⊆ Guard (componente do resultado + uso standalone em 852).
- [ ] **SAFETY-001 [P1]**: Coletar 50 amostras de texto real da internet (notícias, tweets, docs públicos) contendo PII brasileiro para validar Guard Brasil + ATRiAN. Salvar em `packages/guard-brasil/test/fixtures/real-world-samples/`. | 1 dia
- [ ] **SAFETY-002 [P2]**: Prompt injection detection module — Guard Brasil extension: detecta tentativas de override ("ignore previous instructions", "você é um assistente diferente"). | 3 dias

---

### API Monetization — Carry-over + Novos (2026-04-08)
**Nota:** API-001..023 já existem em seção anterior. Abaixo apenas IDs novos.
- [ ] **API-024 [P2]**: Churn tracker — cliente sem chamadas à API por 14 dias → Telegram alert. Implementar como cron diário em `scripts/churn-tracker.ts` lendo `gem_hunter_usage` + billing events. | 3h

---

### SYNC — Kernel Sync Harmonization

- [x] **SYNC-001 [P0]**: Auto-propagate kernel changes post-commit — `.husky/post-commit` atualizado: ao detectar mudança em CLAUDE.md/.windsurfrules/CAPABILITY_REGISTRY, roda disseminate-scanner + propagator (background). ✅ 2026-04-09
- [x] **SYNC-002 [P1]**: VPS cron diário (03:15 BRT) — `governance-sync --exec --propagate` garante que nenhum repo leaf fica > 24h sem sync de kernel. Adicionar ao crontab do VPS. ✅ 2026-04-09 — `/etc/cron.d/governance-sync` + `/opt/egos/governance-sync-vps.sh` (pulls CLAUDE.md from GitHub → 5 app dirs)
- [x] **SYNC-003 [P1]**: `br-acc/.husky/pre-commit` ✅ — 5 checks (ruff lint, secrets, PII guard, SSOT size, kernel marker). | 1h ✅ 2026-04-09
- [ ] **SYNC-004 [P2]**: Leaf→kernel feedback loop — sentinel que detecta se um leaf repo tem regra nova valiosa (padrão: marcada `CANDIDATE-GLOBAL:`) e cria issue no kernel para revisão. | 4h
- [x] **SYNC-005 [P1]**: Harmonizar pre-commit de `egos-lab` (4 checks custom) para incluir checks críticos do kernel: frozen zones, vocab guard, gitleaks. ✅ 2026-04-09

### VPS — Auto-Deploy Pipelines

- [x] **VPS-001 [P0]**: `.github/workflows/vps-deploy-guard-brasil.yml` criado — dispara em push para paths `packages/guard-brasil/**`, `apps/api/**`. Rollback automático se healthcheck falha. ✅ 2026-04-09
- [ ] **VPS-002 [P1] [ENIO]**: Configurar 3 GitHub Secrets para o workflow `vps-deploy-guard-brasil.yml`. Passos: (1) github.com/enioxt/egos/settings/secrets/actions → "New repository secret" → `VPS_SSH_KEY` = conteúdo de `~/.ssh/hetzner_ed25519` (chave privada completa com BEGIN/END). (2) `VPS_HOST` = `204.168.217.125`. (3) `GH_DEPLOY_TOKEN` = PAT com escopo `contents:read` (Settings→Developer settings→PAT). (4) Testar: Actions → "VPS Deploy Guard Brasil" → "Run workflow". Claude não tem acesso ao GitHub Settings via gh CLI (requer browser auth). | 15min MANUAL
- [ ] **VPS-003 [P2]**: Workflow análogo para `egos-gateway` — paths: `apps/egos-gateway/**`. Deploy via rsync + docker compose no VPS. | 2h
- [ ] **VPS-004 [P2]**: Workflow para `egos-hq` — paths: `apps/egos-hq/**`. | 1h
- [x] **VPS-005 [P1]**: VPS health check 2x/dia (09:00 + 21:00 BRT) — script que verifica todos os containers Docker ativos, versões vs. main branch, reporta discrepâncias via Telegram. ✅ 2026-04-09 — `scripts/vps-health-check.ts` (disk/RAM/docker/HTTP/certs), cron `/etc/cron.d/vps-health-check`

### KB — Wiki Quality 79→90 (genuíno, sem hardcode)

- [x] **KB-020 [P1]**: Rodar `wiki-compiler --enrich` em páginas com quality < 80 (estimativa: ~40 páginas). Usa LLM Qwen para enriquecer com cross-refs, exemplos, estrutura. `--dry` primeiro, depois `--exec`. | 2h ✅ 2026-04-08
- [x] **KB-021 [P1]**: `docs/CAPABILITY_REGISTRY.md` como fonte de wiki ✅ — já em `RAW_SOURCES` (wiki-compiler.ts:59, category=pattern). | 2h ✅ 2026-04-09
- [ ] **KB-022 [P2]**: Melhorar extração de cross-refs em wiki-compiler — hoje é 0 refs para muitas páginas. Implementar parser que lê frontmatter `# Cross-refs:` e links `[text](./slug)` de cada doc. | 3h
- [ ] **KB-023 [P1]**: Integrar docs FORJA tenant na compilação periódica — adicionar entrada no `gem-hunter-adaptive.yml` (ou workflow separado) para rodar `wiki-compiler --compile --tenant=forja` semanalmente. | 1h
- [ ] **KB-024 [P2]**: Quality score mais inteligente — penalizar páginas com apenas título (q<40), bonificar páginas com tabelas estruturadas, código, cross-refs reais. Atualizar `computeQualityScore()` em wiki-compiler. | 3h

### ARCH — Codebase Archaeology Agent

> **Objetivo:** Escanear todos os repos (`.md`, `.py`, `.ts`) buscando conceitos valiosos esquecidos, TODOs abandonados, padrões obsoletos, docs desatualizadas. Reportar via docs/jobs/ + Telegram.

- [x] **ARCH-001 [P1]**: `scripts/codebase-miner.ts` — agente de arqueologia. Fase 1 ✅: 127 markers em 6 repos. Report `docs/jobs/codebase-mining-2026-04-09.md`. | 4h ✅ 2026-04-09
- [ ] **ARCH-002 [P1]**: `codebase-miner.ts` Fase 2 — detecção de docs obsoletas: `.md` com `updated:` > 90 dias + referenciada em código. Usa LLM para avaliar "ainda relevante?" (sim/talvez/arquivar). | 6h
- [ ] **ARCH-003 [P2]**: `codebase-miner.ts` Fase 3 — "gem concepts": lê títulos H2/H3 de todos `.md`, detecta conceitos sem implementação correspondente (ex: "ARR" mencionado mas `/packages/search-engine` inativo). Lista conceitos candidate. | 4h
- [x] **ARCH-004 [P1]**: CCR job weekly (sexta 06h00 UTC) — `.github/workflows/codebase-miner-weekly.yml`. Report commitado automaticamente. | 1h ✅ 2026-04-09
- [ ] **ARCH-005 [P2]**: Multi-repo GitHub scan — `codebase-miner.ts --github` usa GitHub API para escanear repos públicos do Enio que não estão clonados localmente (enioxt/*). Detecta repos abandonados vs. ativos. | 3h

### PRICE — Pricing como Referência (não como gate de revenue)

- [x] **PRICE-001 [P0]**: x402 pricing externalizado para env (`X402_PRICE_USDC_ATOMIC`, `X402_NETWORK`, `X402_FACILITATOR_URL`). Wallet Base wired. Pricing = referência de mercado, não objetivo de lucro. ✅ 2026-04-09
- [ ] **PRICE-002 [P1]**: Guard Brasil pricing tiers — atualizar `apps/api/src/server.ts` e `/v1/meta` para refletir tiers éticos (Free 150 calls, Starter R$49/10k, Pro R$199/100k, Business R$499/500k). Como referência para demos/parceiros. Nenhum tier bloqueia desenvolvimento. | 2h
- [ ] **PRICE-003 [P2]**: Remover referências a MRR/R$ específicos de comentários no código. Mover para `docs/GTM_SSOT.md` como "projeções de referência" apenas. | 1h

### ACASH — AgentCash

- [x] **ACASH-001 [P0]**: Skill AgentCash instalado em `~/.claude/commands/agentcash.md`. Invite AC-LZR4-C5AX-F5DH-EAB2 resgatado. ✅ 2026-04-09
- [x] **ACASH-002 [P0]**: Wallet criada via `npx agentcash@latest onboard` (invite já resgatado — OK). Wallet Base/Tempo: `0x8C26958753cdfc6434455021F330BF95FD260b2f` | Solana: `HkwMoWsUMEpFRVJLLW4sALgFg35jdU1VFFmFgVJL8Jpe` | Saldo: 0 USDC. Depositar em `agentcash.dev/deposit/0x8C26...` ✅ 2026-04-09
- [ ] **ACASH-003 [P1]**: Listar Guard Brasil `/guard-brasil/inspect` no AgentCash como provider x402. Usar `npx agentcash discover` para entender o processo. Guard Brasil já tem x402 implementado (API-005 ✅). | 2h
- [ ] **ACASH-004 [P2]**: Testar chamada Guard Brasil via AgentCash: `npx agentcash fetch https://gateway.egos.ia.br/guard-brasil/inspect` com payload PII. Documentar fluxo completo. | 1h

### HYPER — Hyperspace Network

- [ ] **HYPER-001 [P2]**: Instalar Hyperspace na máquina LOCAL (não no VPS): `curl -fsSL https://agents.hyper.space/api/install | bash`. Testar API OpenAI-compatible em `localhost:8080/v1`. Avaliar como LLM fallback local no EGOS chain. | 2h
- [ ] **HYPER-002 [P3]**: Avaliar pontos Hyperspace após 7 dias de uptime. Se pontos tiverem valor real → configurar VPS separado (não o Hetzner atual) para mining. | 1 semana avaliação
- [ ] **HYPER-003 [P3]**: Integrar `localhost:8080/v1` como nó 4 da cadeia de LLMs do EGOS (após Qwen → Claude → OpenRouter → Hyperspace local). Apenas para inferência não-crítica. | 2h

---

## Paperclip Visual Dashboard + Grok 5-Topic Complement (2026-04-09)

> **Context (investigação):** Grok analisou 5 tópicos estratégicos para EGOS: (1) Spec-Driven Dev, (2) Paperclip visual dashboard, (3) Claude Code + No-Code, (4) Obsidian knowledge layer, (5) Cost monitoring + Distribution. Tasks complementam o que já existe.

### DASH — Paperclip Visual Dashboard

> **Estratégia HYBRID:** EGOS não compete com Paperclip — é o compliance kernel dentro dele. EGOS agents se registram como Paperclip "employees", Guard Brasil valida outputs.
>
> **Dificuldades de integração (documentadas):**
> 1. **Hierarquia vs flat:** Paperclip requer CEO→Director→IC reporting. EGOS agents são flat. Precisa org-chart wrapper.
> 2. **Ticket vs event bus:** Paperclip usa Prisma tickets imutáveis. EGOS usa Supabase agent_events. Mapper necessário.
> 3. **Budget enforcement:** Paperclip tem monthly_cap nativo. EGOS só monitora (PAP-002 bloqueia DASH-008).
> 4. **Deploy divergente:** Paperclip espera Node.js local :3100. EGOS = VPS Docker. Compose separado necessário.
> 5. **"Bring-your-own-ticket-system" ainda no Roadmap** — adapter externo depende de feature não lançada.
> 6. **"Multiple Human Users" não suportado** — bloqueia cenário multi-tenant FORJA.
> 7. **"CEO Chat" não implementado** — sem interface natural language para diretivas top-level.

- [x] **DASH-001 [P2]**: Pesquisa técnica Paperclip adapter-plugin + schema Prisma — antes de implementar, mapear exatamente como registrar agent externo (adapter-plugin.md + `/packages`). | 2h ✅ 2026-04-09
- [x] **DASH-002 [P2]**: Docker compose Paperclip self-hosted no VPS — `infra/docker-compose.paperclip.yml` com server:3100 + UI + Postgres isolado. | 3h ✅ 2026-04-09
- [x] **DASH-003 [P2]**: Bridge EGOS→Paperclip — `scripts/egos-to-paperclip-bridge.ts`: converte `agent_events` Supabase para ticket format Prisma. | 4h ✅ 2026-04-09
- [ ] **DASH-004 [P2]**: EGOS agents como Paperclip employees — script lê `agents.json` e POST /agents no Paperclip com hierarchy (runner.ts=CEO, domain=Director, task=IC). | 4h
- [x] **DASH-005 [P3]**: Org chart EGOS canônico — `docs/PAPERCLIP_ORG.md` ✅ 2026-04-09
- [ ] **DASH-006 [P3]**: Guard Brasil compliance plugin Paperclip — intercepta outputs de ICs antes de subir, valida PII via Guard Brasil. | 6h
- [ ] **DASH-007 [P3]**: Heartbeat EGOS visível no Paperclip UI — mapear pulso 30min (heartbeat.ts) para Paperclip scheduled task format. | 3h (dep: PAP-001 ✅)
- [x] **DASH-008 [P3]**: Budget EGOS→Paperclip — mapear `monthly_cap` (PAP-002) para budget enforcement nativo do Paperclip. | 2h (dep: PAP-002) ✅ 2026-04-09
- [x] **DASH-009 [P3]**: Publicar `@egosbr/paperclip-adapter` — npm package com adapter + docs + exemplo de uso. | 4h (dep: DASH-003/004) ✅ 2026-04-09
- [x] **DASH-010 [P3]**: Demo screenshot "EGOS inside Paperclip org chart" → draft X.com thread. | 1h (dep: DASH-002/004) ✅ 2026-04-09

### SDD — Spec-Driven Development

> **Contexto:** 80-90% do que SDD precisa já existe em EGOS (`.guarani/`, doctor, pr:gate). Falta formalizar como skills + template SSOT.

- [x] **SDD-001 [P2]**: Skill `/spec:init` ✅ 2026-04-09
- [x] **SDD-002 [P2]**: Skill `/spec:plan` ✅ 2026-04-09
- [x] **SDD-003 [P2]**: Skill `/spec:implement` ✅ 2026-04-09
- [x] **SDD-004 [P2]**: Skill `/spec:review` ✅ 2026-04-09
- [x] **SDD-005 [P2]**: spec-doctor.ts ✅ 2026-04-09
- [x] **SDD-006 [P3]**: spec-gate-check.sh ✅ 2026-04-09
- [x] **SDD-007 [P3]**: `docs/specs/SPEC-TEMPLATE.md` ✅ 2026-04-09
- [ ] **SDD-008 [P3]**: Specs retroativas Guard Brasil — 4 SPECs para endpoints existentes: inspect, meta, webhook, admin. | 4h
- [x] **SDD-009 [P3]**: HARVEST entry SDD ✅ 2026-04-09

### OBS — Obsidian + Knowledge Layer

> **Contexto:** Complementa KBS (Knowledge Base Service). KBS = service público para clientes. OBS = ferramenta interna Enio + agents. 3-layer memory: CLAUDE.md+MEMORY.md (session), vault+wikilinks+MCP (knowledge graph), brain-ingest (audio/PDF→notas).

- [x] **OBS-010 [P2]**: Vault Obsidian template EGOS — ~/.egos/vault/ criado ✅ 2026-04-09
- [ ] **OBS-011 [P2]**: MCP Obsidian Server — instalar e configurar MCP para Claude ler/escrever notas do vault diretamente. | 2h
- [x] **OBS-012 [P2]**: Skill `/kb:init` — ~/.egos/.claude/commands/kb-init.md ✅ 2026-04-09
- [ ] **OBS-013 [P3]**: Brain-ingest pipeline FORJA — Whisper transcreve átas → nota Obsidian formatada → indexada no wiki-compiler. | 8h (dep: FORJA-TOOLS-002)
- [ ] **OBS-014 [P3]**: Wikilinks → codebase-memory-mcp sync — script que lê [[wikilinks]] do vault e cria relacionamentos no grafo EGOS. | 4h
- [x] **OBS-015 [P3]**: Skill `/daily` — ~/.egos/.claude/commands/daily.md ✅ 2026-04-09

### COST — Monitoramento de Uso + Custos

- [x] **COST-001 [P1]**: `scripts/claude-cost.ts` — lê JSONL de `~/.claude/projects/*/`, agrega por projeto/sessão/model, calcula custo (Haiku/Sonnet/Opus pricing), top 5 sessions mais caras. `--days`, `--project`, `--json` flags. ✅ 2026-04-09
- [ ] **COST-002 [P1]**: EGOS logs → custo estimado — `agent_events` Supabase + custo por model (Haiku:$0.25/Sonnet:$3/Opus:$15 por 1M tokens). Tabela `usage_costs` no Supabase. | 4h
- [x] **COST-003 [P1]**: Skill `/usage-report` criado em `~/.egos/.claude/commands/usage-report.md`. ✅ 2026-04-09
- [x] **COST-004 [P1]**: `scripts/claude-cost-alert.sh` — alerta Telegram sexta 18h BRT, top project + total semanal. Cron a instalar no VPS. ✅ 2026-04-09
- [x] **COST-005 [P3]**: Budget guard session — ~/.claude/hooks/budget-guard.sh ✅ 2026-04-09

### GTM — Distribuição (complement GTM-001)

- [ ] **GTM-002 [P2]**: Newsletter mensal industria/FORJA — "IA para indústria metalúrgica" template + Notion integration + lista opt-in. | 3h
- [ ] **GTM-003 [P2]**: Infinite loop de conteúdo — cron semanal que pega gem mais votado (semana) + gera draft X.com thread via Qwen. | 3h (dep: GH-094 feedback loop)
- [ ] **GTM-004 [P3]**: EGOS Media Kit automático — `scripts/media-kit-generator.ts` gera PDF com stats reais do Guard Brasil (calls/uptime/PII patterns). | 4h
- [x] **GTM-005 [P3]**: llms.txt Guard Brasil /llms.txt endpoint ✅ 2026-04-09

---

## ARCH — Arqueologia e Drift (2026-04-09)

> **Contexto:** Protocolo Rho detectado em estado de drift crítico. Agente existe no registry (2026-02-16) mas artefatos canônicos sumiram do filesystem.

**Rationale:** Rho = possível "Runtime Health Observer" ou "Recursive Health Orchestration". Criado no mesmo dia do agent kernel (Wave 0), citado na filosofia do Mycelium Orchestrator. Para orquestração de 50+ agents, métricas de saúde unificadas seriam valiosas.

**Decisão:** Hibernar (dormant) — não recuperar agora, não deletar do registry. Registrar para ressurreição futura quando escala demandar.

- [x] **ARCH-006 [P0]**: Drift Rho documentado em HARVEST.md §P40 (Windsurf) — ghost reference, ECOSYSTEM_REGISTRY.md entry, decisão: DORMANT. ✅ 2026-04-09
- [ ] **ARCH-007 [P2]**: Git history archaeology — `git log --all --full-history -- scripts/rho.ts` e `docs/protocols/rho-calibration.md` para recuperar última versão. | 1h
- [ ] **ARCH-008 [P2]**: Decisão formal — ressuscitar (recuperar artefatos) vs deprecar (remover do registry). Depende de: ter 50+ agents ativos? Sim → ressuscitar. Não → manter dormant. | 15min

---

## NOTION-AGENTS — Notion Claude Agents Integration (2026-04-09)

> **Contexto:** Notion anunciou Claude AI Agents nativos (2026-04-08). "Your task board is Claude's to-do list." Anthropic = motor + agent harness. Notion = orchestration layer (contexto, UI, task boards compartilhados). Isso valida exatamente a estratégia EGOS: Notion = frontend, EGOS kernel = governança backend. Oportunidade: entrar na waitlist + preparar template EGOS-nativo para quando liberar.

- [ ] **NOTION-AGENTS-001 [P0]**: Entrar na waitlist Notion Claude Agents — notion.so/agents (ação humana: acessar e registrar email). | 5min
- [ ] **NOTION-AGENTS-002 [P1]**: Atualizar CAPABILITY_REGISTRY §27 KBS — documentar estratégia "Notion = orchestration layer official + EGOS = governance kernel". Diferencial: .guarani/ rules, audit trail, LGPD compliance, frozen zones. | 1h
- [x] **NOTION-AGENTS-003 [P1]**: docs/strategy/NOTION_AGENTS_FORJA_SPEC.md criado. ✅ 2026-04-09
- [ ] **NOTION-AGENTS-004 [P1]**: Template Notion "EGOS-Governed Task Board" — pronto para receber Claude Agents nativos quando waitlist abrir. Boards: Backlog / In Progress / Review / Done + propriedades EGOS (priority, agent, spec_link, audit_id). | 3h
- [ ] **NOTION-AGENTS-005 [P2]**: Video PT-BR "Notion + Claude Agents + EGOS para orçamentos 10x mais rápidos na metalúrgica" — quando feature sair da waitlist. | 2h

## PLAT-MON — Platform Monitor (Notion/Claude Code diário) (2026-04-09)

> **Contexto:** Estamos usando Notion MCP + Claude Code diariamente. Mudanças nas plataformas (novos MCPs, novos features, breaking changes) devem ser detectadas e adaptadas. Já temos llm-model-monitor.ts rodando 4x/dia para modelos. Criar padrão similar para plataformas.

- [x] **PLAT-MON-001 [P1]**: `scripts/platform-monitor.ts` — monitora 5 plataformas (claude-code, anthropic-sdk, notion-client, mcp-sdk, bun) via npm registry + GitHub releases. Impact assessment (low/medium/high/critical). Telegram alert para high+. ✅ 2026-04-09
- [x] **PLAT-MON-002 [P1]**: Supabase migration `20260409_platform_updates.sql` — tabela `platform_updates` com RLS service_role. ✅ 2026-04-09
- [x] **PLAT-MON-003 [P2]**: Auto-task em TASKS.md quando impacto HIGH detectado — `platform_updates.egos_impact = "high"` → cria task `ADAPT-NNN` automaticamente. ✅ 2026-04-09 — `appendTasksEntry()` em platform-monitor.ts

---

## OBS — OBSIDIAN + CLAUDE CODE KNOWLEDGE STACK (2026-04-10)

> **Context:** Grok + analysis identified Obsidian + Claude Code as optimal knowledge layer for EGOS. Stack provides persistent external brain, wikilink graph, /start + /end integration, and compounding knowledge. Minimal setup, maximum velocity.
> **Decision:** Research + task creation first (this session). Implementation in next session(s).
> **SSOT:** docs/knowledge/OBSIDIAN_STACK_SSOT.md (to be created)

### Setup & Foundation (P0-P1)

- [x] **OBS-001 [P1]**: Create Obsidian vault directory structure. Vault: `~/Obsidian Vault/EGOS/` (00-07 + 99 folders). ✅ 2026-04-10
- [x] **OBS-002 [P1]**: Symlink 12+ repos into vault by REPO_MAP group (PRODUCTION/PLATFORM/ACTIVE-DEV/etc). `bun obsidian:sync` v2.0 (symlinks, not copies). ✅ 2026-04-10
- [x] **OBS-003 [P1]**: Vault-specific CLAUDE.md with meta-prompt, /start + /end instructions, frozen zones. File: `~/Obsidian Vault/EGOS/CLAUDE.md`. ✅ 2026-04-10
- [x] **OBS-004 [P1]**: Vault folder structure (00-Inbox, 01-RawSources, 02-Wiki, 03-Sessions, 04-Outputs, 05-Decisions, 06-FORJA, 07-Handoffs, 99-Archive). ✅ 2026-04-10
- [x] **OBS-005 [P1]**: MEMORY.md template for vault (Session Index, Active Projects, Decision Trail, HARVEST entries). File: `~/Obsidian Vault/EGOS/MEMORY.md`. ✅ 2026-04-10

### MCP & Search Integration (P1-P2)

- [ ] **OBS-006 [P1]**: Install MCP for Obsidian (codebase-memory-mcp or equivalent). Test graph queries: search_graph(name_pattern="*"), trace_call_path("wiki-compiler"). Validate symlinked repos are indexed. | 2h
- [ ] **OBS-007 [P1]**: Create MCP wrapper script (scripts/vault-search.ts). Allows Claude Code to query vault via: `bun vault-search "pattern"` or `bun vault-search:trace "function"`. Returns wikilink suggestions. | 2h
- [ ] **OBS-008 [P2]**: Implement wikilink auto-suggestion in CLAUDE.md hooks. When Claude creates a note, automatically suggest links to existing notes based on keywords. File: `~/.claude/hooks/wikilink-suggester.ts`. | 3h

### /start + /end Integration (P1-P2)

- [x] **OBS-009 [P1]**: /start workflow updated — INTAKE reads vault MEMORY.md, runs `bun obsidian:sync`. File: `.agents/workflows/start-workflow.md`. ✅ 2026-04-10
- [x] **OBS-010 [P1]**: /end workflow updated — Phase 5 writes handoff to vault, updates MEMORY.md, runs `bun obsidian:sync`. File: `.windsurf/workflows/end.md`. ✅ 2026-04-10
- [ ] **OBS-011 [P2]**: Create /vault-sync script (scripts/vault-sync.ts). Triggered by /end or manual trigger. Syncs HARVEST.md ← → vault/Learnings/, CAPABILITY_REGISTRY.md ← → vault/Capabilities/, etc. Bi-directional link maintenance. | 3h

### Governance & Auditing (P2-P3)

- [ ] **OBS-012 [P2]**: Create vault doctor command (scripts/vault-doctor.ts). Checks: orphaned notes (no backlinks), dead wikilinks (link targets not found), stale notes (>30 days no edit), graph connectivity score. Output: JSON report. | 3h
- [ ] **OBS-013 [P2]**: Implement frozen zones for vault. Files like CLAUDE.md, MEMORY.md, Handoffs/current/ should have edit-locks. Any .guarani/ rules or philosophy should be read-only except via /disseminate. File: vault-frozen-zones.yaml. | 2h
- [ ] **OBS-014 [P2]**: Create vault manifest (.egos-vault-manifest.yaml). Declares: vault purpose, canonical SSOT links, symlinked repos, MCP status, /start + /end integration status, last doctor run. | 1h
- [ ] **OBS-015 [P3]**: Audit trail for vault. Log all note creates/deletes/edits to Supabase or local JSONL (vault_audit.jsonl). Include: timestamp, user, action, note_id, change_hash. Queryable via doctor or /end report. | 3h

### FORJA-Specific Knowledge Layer (P2)

- [ ] **OBS-016 [P2]**: Create FORJA knowledge subvault (EGOS-Knowledge/FORJA-Specific/). Sections: Cliente Profiles, Normas ABNT, Orçamentos Template, Reuniões, Insights, ROI Estimates. | 1h
- [ ] **OBS-017 [P2]**: Ingest FORJA artifacts into vault. CLI tool (scripts/forja-ingest.ts): reads FORJA repo docs, PDFs (via Guard extractors), creates vault notes with auto-tags (#metalurgia, #orçamento, #cliente). | 3h
- [ ] **OBS-018 [P2]**: FORJA client profile template. Template: EGOS-Knowledge/FORJA-Specific/Clients/[CLIENT_NAME].md with: contact, last order, preferences, special requirements, linked to orders & norms. Auto-populated from CRM if available. | 1h

### Dashboard & Visualization (P3)

- [ ] **OBS-019 [P3]**: Create vault dashboard (scripts/vault-dashboard.ts or Obsidian plugin). Shows: note count, graph health score, decision count, learning count, last /end sync, stale note warnings. Outputs to HQ or TUI. | 4h
- [ ] **OBS-020 [P3]**: Obsidian vault graph export for HQ (optional). Periodically export graph as JSON (nodes + edges) → display in HQ dashboard as interactive network (D3.js or similar). | 4h

### Documentation

- [x] **OBS-DOC-001 [P1]**: `docs/knowledge/OBSIDIAN_STACK_SSOT.md` criado. SSOT do vault: arquitetura, governança, task breakdown, acceptance criteria. ✅ 2026-04-10
- [x] **OBS-DOC-002 [P1]**: `docs/knowledge/OBSIDIAN_SETUP_GUIDE.md` criado. Step-by-step: Phase 1-5, comandos exatos. ✅ 2026-04-10

### External Tools Evaluation (P3 — backlog, revisitar quando estabilizar)
**Context:** Avaliacao de 2026-04-11 (Karpathy skills, Skill Graph, 35 MCPs, Engraph, NotebookLM, Claude Skills best practices). Conclusao: ja temos 90%+ do que propoe. Itens abaixo sao os unicos gaps reais.
- [ ] **EVAL-001 [P3]**: Avaliar Engraph (devwhodevs/engraph) quando atingir 500+ stars. Hybrid search 5-lane + section-level edit + vault health. Hoje: 76 stars, v1.6, risco alto. Ja temos codebase-memory-mcp + Obsidian MCP cobrindo 80% do use case. | Revisitar 2026-Q3
- [ ] **EVAL-002 [P3]**: Avaliar Neo4j MCP server para br-acc (83.7M nodes). Atualmente acessamos via shim Python. MCP daria acesso direto via Claude Code. Nao urgente — br-acc esta estavel. | 2h
- [ ] **EVAL-003 [P3]**: Avaliar Docker MCP para gerenciar containers VPS via prompt. Hoje temos egos-watchdog.sh (cron 5min) + manual `docker ps`. MCP seria mais interativo mas nao critico. | 1h
- [ ] **EVAL-004 [P3]**: Skills testing protocol — adicionar exemplos + edge cases nos 25 skills existentes em `~/.egos/.claude/commands/`. Seguir padrao: happy path, minimal input, edge case, negative test, repeatability. Fazer gradualmente, 2-3 skills por sessao. | ongoing

---

