# X_POSTS_SSOT.md — X.com Posts Canonical Source
# Account: @anoineim | SSOT version: 1.0.0 | 2026-04-07
# Rule: ALL X.com post content lives here. No other post files should exist.
# Deprecated: X_POST_PROFILE_PARTNERSHIP.md, X_COM_CONTENT_KIT.md (content merged below)

---

## STATUS BOARD

| Thread | Status | Audience | Tweets | Scheduled |
|--------|--------|----------|--------|-----------|
| Version 6 — Investigador→Builder (PT) | ✅ READY | BR dev/compliance/govtech | 7 | 9h–11h BRT |
| English Native — Neo4j/OSINT (EN) | ✅ READY | Global Neo4j/agents/govtech | 7 | 9h–11h EST |
| Partnership Thread (PT) | ✅ READY | BR GTM operators | 11 | Semana 2 |
| Themed Kit v1 — 77M Entities (EN) | ⚠️ OUTDATED | BR/EN open-source | 5 | Atualizar antes de usar |
| Themed Kit v2 — 17 Agents (EN) | ⚠️ OUTDATED | EN devs | 5 | Atualizar antes de usar |
| Themed Kit v3 — Architecture (EN) | ⚠️ OUTDATED | EN infra | 5 | Atualizar antes de usar |
| Kernel Sprint Post (2026-03-30) | 🗄️ HISTORICAL | — | 1 | Não postar |

**Rule:** Post PT first, EN 2–3 dias depois. Nunca dois threads no mesmo dia.

---

## BLOCO 1 — VERSÃO 6: O INVESTIGADOR QUE VIROU BUILDER (PT) ← POSTAR PRIMEIRO

> **Tom:** Pessoal + técnico. Narrativa única. Use esta primeiro.
> **Recomendada para:** lançamento inicial, foco em parceiros BR

### Tweet 1/7 — O Gancho
```
15 anos investigando crimes em Minas Gerais.

Em 2024, larguei o Excel e passei a construir código.

18 meses depois: 13 produtos, 83,7 milhões de entidades em grafo, zero vendas.

Essa é minha história e o que estou buscando 👇
```

### Tweet 2/7 — A Transferência de Skills
```
Como investigador, aprendi a conectar pontos em bases de dados dispersas.

Apliquei isso direto no código:

Neo4j com 83,7M nós. 32 tipos: empresas, PEPs, contratos, sanções, licitações, viagens corporativas.

26,8M relacionamentos. Tudo público. Tudo rastreável.

Isso é OSINT de dados públicos brasileiros em escala.
```

### Tweet 3/7 — Guard Brasil (Produto Principal)
```
Meu primeiro produto monetizável: Guard Brasil.

API de detecção de PII/LGPD com 15 padrões brasileiros.
4ms de latência. F1 85.3%.

Rodando em produção em guard.egos.ia.br.

DPO de uma empresa de 500 pessoas precisa disso. Ele só não sabe que existe.
```

### Tweet 4/7 — O Problema Honesto
```
Sou pesquisador e builder.

Não sou vendedor. Nunca fui. Não vou fingir que vou virar.

Código: excelente.
Venda: zero.

Busco parceiro de GTM que complete o que falta.
Equity real. Produto real. Sem pitch deck.
```

### Tweet 5/7 — O Que Ofereço
```
3 produtos procurando GTM partner:

🔐 Guard Brasil — compliance LGPD, ICP: DPOs, advogados, fintechs
🧠 EGOS Inteligência — 83,7M nós, ICP: govtech, investigações, compliance
🦅 Eagle Eye — licitações 84+ territórios, ICP: software houses, integradores B2G

Equity 20-35%. Código pronto. VPS rodando há 9+ dias sem falha.
```

### Tweet 6/7 — Verificação Pública
```
Não é vaporware. Hoje às 0h verifiquei:

✅ guard.egos.ia.br — responde em 4ms
✅ 852.egos.ia.br — up 9 dias
✅ Neo4j: 83.773.683 nós (query executada agora)
✅ 19 containers Docker em produção
✅ Gateway v0.3.0 — 4 canais ativos

github.com/enioxt — MIT license, auditável.
```

### Tweet 7/7 — CTA
```
Se você:
→ Já vendeu SaaS B2B
→ Tem acesso a DPOs, govtech, compliance, licitações
→ Prefere equity em produto real a equity em PowerPoint

Me chama. DM aberto.
enioxt@gmail.com

Não tenho pressa. Só quero o parceiro certo.
```

---

## BLOCO 2 — ENGLISH NATIVE: NEO4J/OSINT/AGENTS (EN) ← POSTAR SEGUNDO

> **Tom:** Technical confidence, no hype. Show the work.
> **Target:** Neo4j engineers, agent builders, compliance devs, govtech, Web3/ethics crowd
> **Hashtags (tweet 1):** `#Neo4j #GraphDatabase #AI #Agents #OSINT #OpenSource`
> **Best time:** 9–11am EST

### Tweet 1/7 — The Hook
```
I spent 4 months building a graph database of Brazil's entire public sector.

83,773,683 nodes.
26,808,540 relationships.
32 entity types: politicians, contractors, sanctions, elections, judiciary.

All interconnected. All queryable. Here's what I found. 🧵
```

### Tweet 2/7 — The Architecture
```
The stack:

→ Neo4j on Hetzner VPS (12 vCPU, 24GB RAM)
→ 45+ ETL pipelines: procurement, elections, IBAMA, STF, PEPs
→ FastAPI + React explorer
→ 19 AI agents orchestrated by EGOS Framework
→ LGPD-compliant: CPF/RG masked at ingest

19 Docker containers. 9+ days uptime. No k8s. Just discipline.
```

### Tweet 3/7 — The Agent Layer
```
On top of the graph: a multi-LLM agent system.

- Multi-provider routing: Alibaba Qwen (primary), OpenRouter, DashScope
- 26 OSINT tools: procurement, judiciary, corporate registry, PEPs, sanctions
- Telegram + Discord chatbots (24/7)
- Doc-Drift Shield: sentinel validates all claims daily via .egos-manifest.yaml

The system self-monitors. No manual number-checking.
```

### Tweet 4/7 — What It Actually Found
```
Real patterns from the graph (examples, not allegations):

→ Company A won 3 municipal contracts worth R$4.2M
→ Same company appears in 7 sanction records (CEIS)
→ Partner of Company A is a declared asset of Politician B (TSE filings)

These are public records. The graph just removes the 40 browser tabs.
```

### Tweet 5/7 — The Builder Story
```
Built in 4 months. Solo. Bootstrapped.

Dec 2025 → Carteira Livre (marketplace) MVP: 1 day to prod
Feb 2026 → br-acc foundation: 5 commits in 9 minutes (pre-planned)
Mar 2026 → EGOS Framework v1.0 + Guard Brasil API: 7 days to production
Apr 2026 → 19 agents, 3 CCR scheduled jobs, 8 public domains live

Total: ~3,000 commits. Revenue: R$0. Working on that last part.
```

### Tweet 6/7 — The Honest Ask
```
I'm a researcher-builder. Excellent at: architecture, agents, infrastructure.
Not excellent at: selling, outreach, closing deals.

Looking for:
→ GTM partner (B2G/govtech or compliance/LGPD focus)
→ Co-founder who likes selling what already works
→ Or just: interesting conversations with graph/agent/OSINT people

Equity: real. Code: MIT. Pipeline: live.
```

### Tweet 7/7 — CTA + Links
```
Open source. Verifiable.

→ github.com/enioxt/EGOS-Inteligencia (128⭐)
→ inteligencia.egos.ia.br (live chatbot)
→ guard.egos.ia.br/health (4ms response time)

Want to see how the graph works? Ask me anything.
DM open. No pitch deck.

Built in Brazil 🇧🇷 for the world.
```

---

## BLOCO 3 — PARTNERSHIP THREAD: GTM OPERATOR SEARCH (PT) ← SEMANA 2

> **Tom:** Direto, honesto sobre o gap de vendas. Para operadores BR.
> **Checklist pré-postagem:**
> - [ ] og-image.jpg deployada (GTM-015)
> - [ ] 2h bloqueadas para replies/DMs
> - [ ] X DMs abertos para não-seguidores

### Tweet 1/11 — Hook
```
Construí 13 produtos em 18 meses.

Solo. Bootstrapped. Zero VC.

Código pronto. Infra rodando.

Resultado: ZERO clientes pagantes.

Por que? 👇
```

### Tweet 2/11 — A Verdade
```
Sou pesquisador/builder. Não sou vendedor.

LGPD se vende com confiança, não com feature list.
Compliance se vende com credibilidade, não código.

Preciso de quem converta construção em receita.
```

### Tweet 3/11 — O Que Construí
```
Guard Brasil: API de PII detection, 15 padrões BR, 4ms latência, F1 85.3%.

EGOS Inteligência: 83,7M nós Neo4j (verificado), 32 tipos de entidade, OSINT brasileiro.

Eagle Eye: Monitor de licitações, 84+ territórios.

Tudo no GitHub. MIT license. Auditável.
```

### Tweet 4/11 — Prova de Capacidade
```
83,7M entidades em grafo Neo4j (verificado, rodando hoje).
19 containers Docker no VPS.
23 agentes autônomos orquestrados.
13+ fontes de dados para Gem Hunter.

Não é promessa. É código rodando.
https://github.com/enioxt/egos
```

### Tweet 5/11 — O Que Eu Não Faço Bem
```
❌ Sales enterprise e follow-up
❌ DevRel e comunidade
❌ Networking e pitch events
❌ Contratos e burocracia comercial

Isso não é modéstia. É honestidade.
Busco parceiros que compensem minhas falhas.
```

### Tweet 6/11 — História Crypto
```
Desde 2017 no crypto.

Não como influencer. Como gem hunter.
Avaliei 1000+ projetos, estudei tokenomics, vi rug pulls de perto.

Aprendi: open source + transparência > hype.
Esse é o DNA do EGOS.
```

### Tweet 7/11 — O Que Busco
```
Parceiro de GTM que:
• Já vendeu SaaS B2B
• Tem acesso ao meu ICP (DPOs, govtech, indústria)
• Topa equity generosa (15-35%) em vez de salário
• Faz 10-20h/semana no início

Sem bullshit. Split justo.
```

### Tweet 8/11 — Modelos de Parceria
```
1. Co-fundador equity (20-35%)
2. Revenue share (20-30% MRR)
3. White-label (sua marca, minha tech)
4. Pilot pago (validar antes de equity)

Nota de compromisso simples. Vesting 1 ano.
```

### Tweet 9/11 — Produtos Prioritários
```
🔐 Guard Brasil — equity 20-30%
🧠 EGOS Inteligência — equity 25-35%
🦅 Eagle Eye — equity 25-35%
🏭 Forja — equity 20-30%

Todos: código pronto, infra rodando, ICP definido.
Falta só quem venda.
```

### Tweet 10/11 — CTA
```
Se você é DPO, consultor LGPD, govtech operator, ou ERP seller...

E quer equity em produto pronto em vez de equity em slide deck...

Me chama. Vamos conversar.

enioxt@gmail.com
DM aberto.
```

### Tweet 11/11 — Links
```
🛡️ Guard Brasil: https://guard.egos.ia.br
📁 GitHub: https://github.com/enioxt
📧 Email: enioxt@gmail.com

Sacred Code: 000.111.369.963.1618
```

**O QUE NÃO DIZER:**
- ❌ "Production-ready, enterprise-grade" (ainda não)
- ❌ "Trusted by leading fintechs" (zero clientes enterprise)
- ❌ "$10M ARR potential" (especulação)
- ❌ "AI-powered" (é arquitetura + dados, não hype)

---

## BLOCO 5 — ALTERNATIVE FORMATS (PT) — single-tweet variants

> **Origem:** consolidado de `personal/X_POST_5_VERCOES_LOW_PROFILE.md` (Versões 2-5)
> **Uso:** quando não há tempo/energia para postar thread completa (BLOCO 1), ou para reposts subsequentes
> **Tom:** low profile, sem hype, "faz muito fala pouco"

### V5.1 — Post Único Conciso (1 tweet, ~280 chars)
```
Construí 13+ produtos solo em 18 meses. Código pronto, infra rodando, 83,7M nós em grafo Neo4j (verificado hoje).

Resultado: 0 vendas. Porque sou builder, não vendedor.

Busco parceiro GTM com equity generosa (15-35%). DPOs, govtech, compliance — meu ICP é seu network?

guard.egos.ia.br | github.com/enioxt
```

### V5.2 — Storytelling Pessoal (1 post longo)
```
Em 2017 descobri crypto. Não como trader. Como curioso.

Passei 8 anos avaliando projetos, estudando tokenomics, aprendendo a detectar padrões. 1000+ projetos analisados.

Em 2024 apliquei isso em código. Construí o EGOS: 13 produtos, open source, governança transparente.

Agora preciso de quem complete o que falta: distribuição.

Se você vende B2B e quer equity em produto real — vamos conversar.
```

### V5.3 — Técnico Sem Arrogância (1 post)
```
Stack atual:
• 83,7M nós Neo4j (CNPJ, PEPs, sanções, contratos — 32 tipos)
• 26,8M relacionamentos entre entidades
• 15 padrões PII brasileiros detectados em 4ms
• 23 agentes autônomos com governança
• 19 containers Docker em produção (Hetzner VPS)

Tudo documentado, testado, open source.

Só falta quem leve isso pra quem precisa.

DM aberto pra parceiros de GTM.
```

### V5.4 — Convite Direto (1 post — para quem já conhece)
```
Você já viu meu código no GitHub.
Já viu o Guard Brasil funcionando em produção.
Já viu o grafo de 83,7M nós rodando no VPS hoje.

Sabe que não é vaporware.

Agora: quer equity pra distribuir isso?

Busco 3 parceiros de GTM:
• Guard Brasil (LGPD/compliance)
• EGOS Inteligência (govtech/OSINT)
• Eagle Eye (licitações/B2G)

Equity 20-35%. Nota simples. Split justo.

enioxt@gmail.com
```

---

## BLOCO 4 — THEMED KIT: DADOS/AGENTES/INFRA (EN) ← ATUALIZAR ANTES DE USAR

> **Status:** ⚠️ OUTDATED — números precisam atualização para 83.7M, 19 containers, Hetzner
> **Origin:** X_COM_CONTENT_KIT.md (egos-lab/docs/plans/, 2026-03-06, agora depreciado)
> **Uso:** base de inspiração para futuras threads, não postar sem revisão

### Thread A: "83M Entities" (escala de dados)
Hook: `I spent 4 months building a graph database of Brazil's entire public sector. 83,773,683 nodes...`
(Usar Bloco 2 Tweet 1 como base atualizada — os números do content kit original estavam desatualizados)

### Thread B: "19 Agents" (plataforma agentic)
> Atualizar: 17→19 agents, zero-deps ainda válido, ~50KB total ainda válido

### Thread C: "~$50/month Architecture" (infraestrutura)
> Atualizar: Contabo→Hetzner (12 vCPU, 24GB RAM, 204.168.217.125), Redis: verificar se ainda em uso

### Thread D: "Governance Story" (qualidade de código)
> Conteúdo ainda válido — GOV-006/007 story, .guarani/, 19 agents enforcing rules

### Video Script: "EGOS in 60 Seconds"
> Atualizar números antes de gravar. Usar asciinema para terminal, Neo4j Bloom para grafo.
> Vertical 1080x1920 para X/TikTok ou 1920x1080 horizontal.

---

## DIRETRIZES GERAIS DE POSTAGEM

### O Que Fazer ✅
- Postar entre 9h–11h BRT (audience BR) ou 9h–11h EST (audience EN)
- Responder comentários em até 2h após postagem
- Fixar no perfil por 1 semana
- Repostar a cada 3–4 dias com variação de texto
- Primeiro reply own-thread: "Bookmark this 🔖" para boostar saves

### O Que Evitar ❌
- Não usar emojis excessivos (máx 2 por tweet)
- Não fazer "threadstorm" (máx 11 tweets por thread)
- Não responder haters defensivamente
- Não prometer datas ou milestones
- Não postar dois threads no mesmo dia
- Não postar EN e PT no mesmo dia (2–3 dias de intervalo)

### Hashtags por audiência
- **BR tech/compliance:** `#LGPD #OpenSource #BuildInPublic #FintechBrasil`
- **EN global:** `#Neo4j #GraphDatabase #AI #Agents #OSINT #OpenSource`
- Usar 2–3 por thread máximo, somente no primeiro tweet

### Métricas de Sucesso
- 50+ bookmarks = interesse real
- 10+ DMs qualificados = sucesso
- 3+ calls agendadas = ótimo
- 1 parceria fechada = meta atingida

---

## AUTOMAÇÃO X.COM & STRATEGY

> **Origem:** consolidado de `egos/docs/strategy/XCOM_SOCIAL_AUTOMATION_PLAN.md` (482 linhas, 2026-03-30) + `gtm15_x_thread_imagen_plan_2026_04_06.md`

### A) X API Capabilities (2026)

| Tipo | Via API? | Limites | Notas |
|------|----------|---------|-------|
| Tweet texto | ✅ | 280 chars (free), 25k chars (Premium) | Core |
| Thread | ✅ | Encadeamento múltiplo | Tutorials |
| Imagens | ✅ | 4 por post, JPG/PNG/GIF, max 5MB | media endpoint |
| Vídeos | ✅ | 1 por post, 512MB, 2:20 min | upload async |
| GIFs | ✅ | media upload | — |
| Polls | ✅ | 2-4 opções, 5min-7d | engajamento alto |
| Articles | ❌ | Premium only, web UI | postar manual ou via browser auto |
| Spaces | ⚠️ parcial | criar/gerenciar | audio live |
| Cards | auto | link preview | URL gera card |

### B) X API Pricing (2026)

| Tier | Preço | Writes/mês | Reads/mês |
|------|-------|------------|-----------|
| Free | $0 | ~500 | ~50 |
| Basic | $200/mo | ~50.000 | ~10-15k |
| Pro | $5.000/mo | ~300.000 | 1.000.000 |
| Pay-per-use | créditos | $0.01/post | $0.005/read |

**Nosso cenário:** 1 post/dia = 30/mês → **Free tier basta**. Migrar para Pay-per-use só se precisar monitorar mentions.

**Limites duros:** 2400 posts/dia, ~50 posts/30min, follow 400/dia free, DM 500/dia.

### C) Architecture: GUARD BRASIL SOCIAL ENGINE (planejado)

```
┌─────────────────────────────────────────────────────────┐
│                GUARD BRASIL SOCIAL ENGINE               │
├─────────────────────────────────────────────────────────┤
│  Content Gen (Qwen) → Visual Gen → Schedule Manager     │
│         ↓                                                │
│  Post Composer (text + image + hashtags + CTA)          │
│         ↓                                                │
│  Review Queue (Telegram approval before posting)        │
│         ↓                                                │
│  X.com API Publisher (OAuth 1.0a + media upload)        │
│         ↓                                                │
│  Analytics Tracker (impressions, likes, RT, clicks)     │
│         ↓                                                │
│  Engagement Bot (reply mentions, thank followers)       │
└─────────────────────────────────────────────────────────┘
         ↓
   HQ Dashboard: social tab + Semrush-style monitoring
```

### D) Weekly content calendar (auto-generated)

| Dia | Categoria | Tópico |
|-----|-----------|--------|
| Mon | educational | LGPD concept |
| Tue | case_study | CPF masking demo |
| Wed | product | Guard Brasil feature |
| Thu | engagement | poll or question |
| Fri | news | AI safety news |
| Sat | educational | ATRiAN ethical AI |
| Sun | case_study | govtech use case |

### E) Visual generation strategies

- **case_study** → terminal screenshot (curl → response, dark theme)
- **educational** → infographic HTML → Playwright screenshot
- **product** → dashboard preview screenshot
- **news** → text-only or quote-card
- **engagement** → poll image or simple stat card

### F) Scheduler workflow

1. Content generator runs 6 AM BRT daily → drafts in queue
2. Telegram bot notifies Enio with preview
3. Enio approves/edits via Telegram inline buttons OR HQ dashboard
4. Publisher posts at 9 AM BRT (peak engagement window for BR tech)
5. Analytics tracker pulls metrics every 6h, persists to Supabase

### G) KPIs semanais

- Engagement rate > 2% (bom para tech/B2B)
- URL clicks > 10% das impressions
- API tests > 5 por post
- Signups > 1 por semana

### H) Tasks pendentes (GTM/automation)

- **XMCP-001:** regenerar credenciais X em developer.twitter.com (atual: 401 Unauthorized) → bloqueador #1
- **GTM-015:** OG image — screenshot `scripts/assets/guard-og.html` → `og-image.jpg` via Playwright
- **GTM-015b:** `x-post-thread.ts` — script que posta thread em sequência com imagem no tweet 1
- **GTM-015c:** Imagen 3 — `generate-social-image.ts` para cards e banners LGPD
- **SOCIAL-001:** Telegram approval bot wired to Supabase queue
- **SOCIAL-002:** HQ dashboard social tab (analytics + queue + scheduler)

### I) Engagement bot rules (auto + manual)

**Auto (with approval):**
- Like mentions of Guard Brasil
- Reply thank-you to anyone who tests guard.egos.ia.br
- Quote retweet posts about LGPD/PII with relevant comment
- Follow back govtech/devs BR

**Manual (Enio):**
- Answer technical questions
- Share demo results
- Post articles longos (1x/semana via web UI)

---

## HISTÓRICO (NÃO POSTAR)

### Sprint Update — 2026-03-30
> Kernel sprint notification — publicado internamente apenas
```
EGOS Kernel Sprint: 16 tasks shipped, Agent Claim taxonomy live, SSOT Visit Protocol
now constitutional law. Guard Brasil API 4ms. Eagle Eye 15→50 territories next sprint.
Neo4j claim (77M entities) corrected to br-acc. Control plane ready. egos.ia.br/#mission
```

---

## ARQUIVOS DELETADOS (consolidação 2026-04-07)

| Arquivo | Status | Conteúdo migrado para |
|---------|--------|------------------------|
| `personal/X_POST_5_VERCOES_LOW_PROFILE.md` | 🗑️ DELETED 2026-04-07 | Blocos 1, 3 + novo BLOCO 5 (V5.1-V5.4) |
| `egos/docs/social/X_POST_PROFILE_PARTNERSHIP.md` | 🗑️ DELETED 2026-04-07 | BLOCO 3 (partnership thread completo) |
| `egos-lab/docs/plans/X_COM_CONTENT_KIT.md` | 🗑️ DELETED 2026-04-07 | BLOCO 4 (themed kit, marcado outdated) |
| `egos/docs/strategy/XCOM_SOCIAL_AUTOMATION_PLAN.md` | 🗑️ DELETED 2026-04-07 | §AUTOMAÇÃO X.COM & STRATEGY (seções A-I) |
| `egos/docs/_archived_handoffs/SOCIAL_POSTS_2026-03-30.md` | 📚 archived | §Histórico |
| `.egos/memory/mcp-store/gtm15_x_thread_imagen_plan_2026_04_06.md` | 📚 keep (memory) | §Automação H |

---

*Version: 1.0.0 — 2026-04-07*
*SSOT criado para cumprir §26 (SSOT-First Rule) — conteúdo de 5 arquivos dispersos consolidado*
*Próxima atualização: após execução do GTM-015 (OG image + x-post-thread.ts)*
