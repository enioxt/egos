# Timeline + AI Publishing System — Architecture

> **Date:** 2026-04-08
> **Status:** Design (DRAFT — pending approval)
> **Owner:** Enio
> **Builds on:** Timeline System v1 (2026-03-27, transparency_reports), X_POSTS_SSOT.md, x-reply-bot, x-opportunity-alert

---

## 1. The Idea (in plain words)

Enio é pesquisador. Posta pouco, escreve menos, mas commita muito. Cada commit relevante e cada doc novo no GitHub deveriam virar **automaticamente**:

1. Um artigo completo no **egos.ia.br/timeline** (formato longo, links, contexto)
2. Um snippet no **X.com** respeitando o limite de caracteres, linkando o artigo
3. Notificação no **Telegram/WhatsApp/HQ** pedindo aprovação **antes** de publicar

A timeline pública é uma "feed transparente" do que o ecossistema está construindo, alimentada por agentes de IA que leem o repositório e produzem conteúdo legível para humanos.

**Princípio canônico:** *"Não seremos uma caixa preta. Iremos mostrando tudo que vamos fazendo."*
(Já documentado em egos-lab/docs/TIMELINE_DEPLOYMENT_STATUS.md como TRANSPARENCY_RADICAL.)

---

## 2. Relação com o que já existe

| Já existe | O que adiciona |
|-----------|----------------|
| `transparency_reports` table (Supabase) | Vira a fonte primária da timeline pública |
| `TransparencyTimeline.tsx` (forja) | Vira o componente base do `/timeline` em egos.ia.br |
| `x-reply-bot.ts` + `x-opportunity-alert.ts` | Reusa OAuth1+Bearer, adiciona "publish article" |
| `X_POSTS_SSOT.md` | Continua canônico para DMs e templates manuais |
| `auto-disseminate.sh` (post-commit) | Já lê commits e atualiza TASKS/HARVEST — vira o trigger |
| `session-aggregator.sh` (cron 02:30 UTC) | Já produz handoff diário — vira o "weekly digest article" |

**Nada do que já existe é reescrito.** O sistema é uma camada sobre o que está vivo.

---

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       TRIGGERS (in)                              │
├─────────────────────────────────────────────────────────────────┤
│ T1. post-commit hook (auto-disseminate.sh) detecta "PUBLISH:"   │
│ T2. cron diário 03:00 UTC: scan commits últimos 24h            │
│ T3. cron semanal domingo 12:00 UTC: digest agregando 7 dias    │
│ T4. manual: bash scripts/publish.sh "tema do artigo"           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AGENT: article-writer                           │
├─────────────────────────────────────────────────────────────────┤
│ Input:   commit hash, files changed, diff, related docs         │
│ LLM:     DashScope qwen-plus → OpenRouter free fallback         │
│          (mesma chain do hermes, $0 ou ~$0.001/artigo)          │
│ Reads:   docs/CAPABILITY_REGISTRY.md, GTM_SSOT.md, README do    │
│          repo afetado, X_POSTS_SSOT.md (tom), docs/HERMES_SSOT  │
│ Writes:  draft em docs/timeline/drafts/YYYY-MM-DD-{slug}.md     │
│          com frontmatter (title, summary, tags, link_x, status) │
│ Bound:   max 1000 palavras, max 3 código blocks, sempre cita    │
│          sources (commits, files, urls reais)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 GUARD: pii + drift check                        │
├─────────────────────────────────────────────────────────────────┤
│ • POST guard.egos.ia.br/v1/inspect (drop CPF/email/keys)        │
│ • doc-drift-verifier roda no draft (números devem casar com    │
│   .egos-manifest.yaml — bloqueia publicação se drift)           │
│ • LGPD compliance trail logado em transparency_logs             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│            APPROVAL: human-in-the-loop (HITL)                   │
├─────────────────────────────────────────────────────────────────┤
│ Notifica em paralelo:                                           │
│ • Telegram bot @egos_updates (botões: ✅ Approve / ✏️ Edit / ❌)│
│ • WhatsApp via Evolution API (mesma fila)                       │
│ • HQ dashboard /timeline/pending (UI rica, edit inline)         │
│                                                                 │
│ Estado: pending → approved | rejected | needs_edit              │
│ Persistido em Supabase: timeline_drafts table                   │
│ Timeout: 48h sem resposta = auto-rejected (volta pra drafts)    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (apenas se approved)
┌─────────────────────────────────────────────────────────────────┐
│                  PUBLISH: dual destination                       │
├─────────────────────────────────────────────────────────────────┤
│ A) egos.ia.br/timeline/{slug}                                   │
│    - Markdown → MDX render (Vite + remark)                      │
│    - URL canônica, OG image gerada (apps/og-gen)                │
│    - Insere row em transparency_reports + timeline_articles     │
│                                                                 │
│ B) X.com (via x-reply-bot OAuth1)                               │
│    - Snippet ≤ 270 chars (margem 10) gerado pelo writer         │
│    - Inclui link canônico https://egos.ia.br/timeline/{slug}    │
│    - Thread opcional (max 4 tweets) se article > 800 palavras   │
│    - Logged em x_posts table com tweet_id                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OBSERVABILITY                               │
├─────────────────────────────────────────────────────────────────┤
│ • HQ /timeline tab: view/edit/republish, metrics                │
│ • Telegram alerts: published, errors, low engagement (24h)      │
│ • Supabase: timeline_articles, timeline_drafts, x_posts         │
│ • CCR daily report: artigos publicados + engajamento            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Data Model (Supabase additions)

```sql
-- Reuses existing transparency_reports as the unified event log

create table timeline_drafts (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  title text not null,
  summary text not null,                  -- ≤ 280 chars (used as X snippet)
  body_md text not null,                  -- full article markdown
  source_commits text[] not null,         -- ['ae7b9ad', '13c12ae']
  source_files text[],
  tags text[],
  status text not null default 'pending', -- pending|approved|rejected|published
  llm_provider text,                      -- 'qwen-plus' | 'qwen3-free'
  llm_cost_usd numeric(8,5) default 0,
  pii_check_passed bool default false,
  drift_check_passed bool default false,
  created_at timestamptz default now(),
  approved_at timestamptz,
  approved_by text,                       -- 'enio' | 'auto'
  rejected_reason text
);

create table timeline_articles (
  id uuid primary key default gen_random_uuid(),
  draft_id uuid references timeline_drafts(id),
  slug text unique not null,
  title text not null,
  body_html text not null,                -- rendered MDX
  url text not null,                      -- https://egos.ia.br/timeline/{slug}
  published_at timestamptz default now(),
  x_post_id text,                         -- tweet id se publicado
  x_post_url text,
  views int default 0,
  engagement_json jsonb                   -- {likes, retweets, replies, click_through}
);

create table x_post_queue (
  id uuid primary key default gen_random_uuid(),
  article_id uuid references timeline_articles(id),
  text text not null,                     -- ≤ 270 chars
  thread_position int default 0,
  scheduled_for timestamptz default now(),
  posted_at timestamptz,
  tweet_id text,
  status text default 'queued'            -- queued|posted|failed
);
```

---

## 5. File / Code Layout

```
egos/
├── agents/agents/
│   └── article-writer.ts          (NEW — main writer agent, ~400 LOC)
├── apps/
│   ├── egos-site/                 (NEW — Vite+React site for egos.ia.br)
│   │   ├── src/pages/timeline/    (route /timeline + /timeline/[slug])
│   │   ├── src/components/Timeline*.tsx  (reuse forja components)
│   │   └── public/og/             (auto-generated OG images)
│   └── og-gen/                    (NEW — small service to render OG png)
├── scripts/
│   ├── publish.sh                 (NEW — manual trigger)
│   ├── timeline-cron-daily.sh     (NEW — cron 03:00 UTC)
│   └── timeline-cron-weekly.sh    (NEW — cron 12:00 UTC sun)
├── docs/
│   ├── timeline/
│   │   ├── drafts/                (writer output, gitignored)
│   │   └── published/              (after approve, mirrored from Supabase)
│   └── TIMELINE_AI_PUBLISHING_ARCHITECTURE.md  (THIS FILE)
└── supabase/migrations/
    └── 20260408_timeline_publishing.sql
```

**Reused (no edits):**
- `scripts/x-reply-bot.ts` — adds new method `postArticle(snippet, url)`
- `scripts/auto-disseminate.sh` — detects `PUBLISH: <slug>` lines (mirror of `LEARNING:`)
- `apps/api/` — already has guard.egos.ia.br PII inspect endpoint

---

## 6. Approval UX (Telegram bot example)

```
┌───────────────────────────────────────┐
│ 📝 New article ready for review       │
│                                       │
│ Title: "Codex está fora. Hermes      │
│         live com chain DashScope+    │
│         OpenRouter."                  │
│                                       │
│ Summary (X snippet, 248 chars):       │
│ "Decommissionei o Codex. Hermes     │
│  agora roda com qwen-plus na       │
│  DashScope, fallback OpenRouter.    │
│  Custo: $0/mês até 1M tokens.       │
│  Audit completo em..."               │
│                                       │
│ Source: ae7b9ad + HERMES_SSOT.md     │
│ Length: 720 words, 2 code blocks     │
│ PII check: ✅  Drift check: ✅      │
│                                       │
│ [✅ Approve & Publish]                │
│ [✏️ Edit in HQ]                       │
│ [❌ Reject]                           │
│ [⏰ Snooze 24h]                       │
└───────────────────────────────────────┘
```

---

## 7. Phasing (concrete, executable)

### PHASE 1 — Foundation (4-6h, this week)
- [ ] **TL-001** Migration `timeline_drafts` + `timeline_articles` + `x_post_queue`
- [ ] **TL-002** `agents/agents/article-writer.ts` — reads commit, calls qwen-plus, writes draft
- [ ] **TL-003** `scripts/publish.sh "topic"` manual trigger funcionando local
- [ ] **TL-004** Telegram bot approve flow (botões inline) → grava aprovação no Supabase

### PHASE 2 — Site público (6-8h)
- [ ] **TL-005** `apps/egos-site` Vite+React inicial em egos.ia.br
- [ ] **TL-006** Rota `/timeline` listando timeline_articles (paginado)
- [ ] **TL-007** Rota `/timeline/[slug]` renderizando MDX
- [ ] **TL-008** Caddy: egos.ia.br/timeline/* roteado para egos-site (porta 3070)

### PHASE 3 — Automação completa (4h)
- [ ] **TL-009** `scripts/timeline-cron-daily.sh` — escaneia commits 24h, gera drafts
- [ ] **TL-010** Crontab: `0 3 * * * timeline-cron-daily.sh`
- [ ] **TL-011** auto-disseminate.sh: detecta `PUBLISH:` no commit body
- [ ] **TL-012** x-reply-bot integração: `postArticle(snippet, url)` após approve

### PHASE 4 — Multi-canal (3h)
- [ ] **TL-013** WhatsApp via Evolution API (mesma fila do Telegram)
- [ ] **TL-014** HQ tab `/timeline/pending` com edit inline
- [ ] **TL-015** OG image generation (apps/og-gen)

### PHASE 5 — Inteligência (opcional, 6h)
- [ ] **TL-016** Weekly digest agente (agrega 7 dias em 1 artigo "what shipped this week")
- [ ] **TL-017** Engagement feedback loop: posts com baixo engajamento → tweak tom
- [ ] **TL-018** Multi-language: PT canônico, EN auto-traduzido para alcance global

**Total Phase 1-3:** ~14h (1 semana de evening work)
**Custo recorrente:** ~$1/mês LLM (90% qwen-free) + Vercel/VPS já existentes

---

## 8. Guard rails (non-negotiable)

1. **Nunca publicar sem aprovação humana.** Default deny. Timeout = reject.
2. **Nunca publicar conteúdo que falha PII check** (Guard Brasil bloqueia).
3. **Nunca publicar números que falham drift check** (.egos-manifest.yaml é fonte).
4. **Sempre logar provider LLM usado e custo** em timeline_drafts.llm_cost_usd.
5. **Nunca apagar drafts rejeitados** — auditoria histórica + treino futuro do tom.
6. **Rate limit X.com:** max 3 posts/dia, max 1 thread/dia (evita spam, respeita followers).

---

## 9. Por que isso resolve o problema do Enio

| Problema atual | Como o sistema resolve |
|----------------|------------------------|
| "Construo muito, posto pouco" | Auto-extract de cada commit relevante vira draft |
| "Não tenho paciência pra escrever" | Agente escreve, Enio só aprova/edita |
| "Não tenho tempo de pensar em copy" | qwen-plus + tom de X_POSTS_SSOT.md como referência |
| "Quero transparência radical" | Timeline pública = artefato da transparência |
| "Quero atrair builders parecidos" | Artigos longos com substância → self-selection |
| "Não confio em automação cega" | HITL via 3 canais paralelos, sempre approval humano |

---

## 10. Decisões abertas (precisam input do Enio)

1. **Site:** novo `apps/egos-site` ou estender o atual da Mission Control? (Recomendo novo — separação de concerns público/privado)
2. **OG images:** prioridade alta ou pode esperar Phase 4?
3. **Multi-language:** PT-only ou PT+EN desde o início? (Recomendo PT-only Phase 1, EN em Phase 5)
4. **Approval timeout:** 48h ou 7 dias? (Recomendo 48h para forçar cadência)
5. **Frequência max:** 1 artigo/dia ou 1 artigo/semana? (Recomendo até 3/semana para Phase 1)

---

*Architecture v0.1 — pendente revisão e aprovação.*
*Próximo passo: Enio aprova, criar TASKS TL-001..018 em TASKS.md, começar Phase 1.*
