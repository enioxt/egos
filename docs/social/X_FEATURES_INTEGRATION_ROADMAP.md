# X.com Automation — Feature Integration Roadmap

> **Date:** 2026-04-07  
> **Source:** Research AutoTweet, TweetHunter, Hypefury, Typefully, Brand24  
> **Goal:** Integrar melhores features em nossa solução customizada (self-hosted, sem custos mensais)

---

## 🎯 Features Identificadas — Prioridade de Implementação

### P0 — CRÍTICO (Implementar Primeiro)

#### 1. Smart Scheduling com AI
**Fonte:** AutoTweet, PostEverywhere  
**Descrição:** Análise do comportamento da audiência para determinar melhores horários de postagem (não dados genéricos da indústria)  
**Implementação:**
- Analisar histórico de engajamento (likes, RTs, replies por hora)
- Machine learning simples (regressão ou clustering) para previsão
- Sugerir horários ótimos para cada tipo de conteúdo
**Custo:** $0 (processamento no VPS)  
**Arquivo:** `scripts/x-smart-scheduler.ts`

#### 2. Evergreen Recycling Inteligente
**Fonte:** AutoTweet, Hypefury  
**Descrição:** Recompartilhar automaticamente posts de melhor performance para novos seguidores  
**Implementação:**
- Identificar top 20% posts por engajamento
- Fila de repost com espaçamento inteligente (evitar spam)
- Variantes de texto (paraphrasing leve) para não parecer repetido
- Regras: mínimo 7 dias entre reposts do mesmo conteúdo
**Custo:** $0  
**Arquivo:** `scripts/x-evergreen-recycler.ts`

#### 3. Thread Composer Visual
**Fonte:** AutoTweet, Typefully  
**Descrição:** Builder visual de threads com drag-and-drop, preview, character count  
**Implementação:**
- Interface web simples (Next.js page no HQ)
- Drag-and-drop para reordenar tweets
- Preview em tempo real do thread
- Auto-split de texto longo em múltiplos tweets
- Salvamento de drafts no Supabase
**Custo:** $0  
**Arquivo:** `apps/egos-hq/app/x-composer/page.tsx`

---

### P1 — ALTA PRIORIDADE

#### 4. Viral Content Library (Inspiração)
**Fonte:** TweetHunter  
**Descrição:** Biblioteca de posts virais para inspiração e análise de padrões  
**Implementação:**
- Buscar tweets virais por nicho (LGPD, govtech, etc.)
- Categorização automática (thread, hot take, educational, etc.)
- Análise de padrões: hooks, estrutura, CTAs
- Database local (SQLite/JSON) — não precisa ser complexo
**Custo:** $0 (usa X API gratuita para buscar)  
**Arquivo:** `scripts/x-viral-library.ts`

#### 5. Lead Tracking CRM (DMs)
**Fonte:** TweetHunter  
**Descrição:** Track leads que responderam ou engajaram para follow-up  
**Implementação:**
- Database no Supabase: leads table
- Campos: username, first_contact_date, last_interaction, status, notes
- Reminders para follow-up após X dias
- Integração com x-approval-bot.ts existente
**Custo:** $0  
**Arquivo:** `scripts/x-lead-crm.ts` (extensão do x-approval-bot)

#### 6. Auto-DM Sequences (Aprovadas)
**Fonte:** TweetHunter, PhantomBuster  
**Descrição:** Sequências de DM automatizadas (após aprovação manual)  
**Implementação:**
- Workflow: Day 0 (intro) → Day 3 (follow-up) → Day 7 (value-add)
- Templates customizáveis por nicho
- Tracking de abertura/resposta (via X API polling)
- Parar sequência se usuário responder
**Custo:** $0  
**Arquivo:** Integrado em `x-approval-bot.ts`

---

### P2 — MÉDIA PRIORIDADE

#### 7. Social Listening Avançado (Brand24-style)
**Fonte:** Brand24, Mention  
**Descrição:** Monitorar menções de keywords, concorrentes, oportunidades  
**Implementação:**
- Queries: "LGPD", "licitação software", "preciso de chatbot", etc.
- Alertas em tempo real (webhook → Telegram/WhatsApp)
- Sentiment analysis básica (positivo/negativo/neutro)
- Dashboard no HQ mostrando menções recentes
**Custo:** $0 (usa X API search gratuita)  
**Arquivo:** Extensão de `x-opportunity-alert.ts`

#### 8. Analytics Dashboard Detalhado
**Fonte:** AutoTweet, Hypefury  
**Descrição:** Métricas de crescimento, engajamento, análise de conteúdo  
**Implementação:**
- Gráficos: follower growth, engagement rate por dia/semana
- Top performing content (identificar padrões)
- Best times to post (heatmap visual)
- Export PDF/CSV para relatórios
**Custo:** $0  
**Arquivo:** `apps/egos-hq/app/x-analytics/page.tsx`

#### 9. Auto-Plug (Promoção Inteligente)
**Fonte:** Hypefury  
**Descrição:** Auto-promover produto/serviço em replies de tweets virais próprios  
**Implementação:**
- Detectar quando tweet próprio atinge X likes (ex: 50+)
- Adicionar reply automático com link/link de produto
- Regra: máx 1 auto-plug por dia para não ser spam
**Custo:** $0  
**Arquivo:** `scripts/x-auto-plug.ts`

#### 10. Content Variations Generator
**Fonte:** PostEverywhere, TweetHunter  
**Descrição:** Gerar variações do mesmo conteúdo para A/B testing  
**Implementação:**
- Input: texto original
- Output: 3 variações com diferentes angles/tone
- Usar LLM local (Gemma 4 31B via Google AI Studio — gratuito)
- Track performance de cada variação
**Custo:** $0 (Google AI Studio free tier: 1500 req/dia)  
**Arquivo:** `scripts/x-variations-generator.ts`

---

## 📊 Implementação por Fases

### FASE 1 — Core (Semana 1)
- [X-COM-010] Smart Scheduling: análise de audiência
- [X-COM-011] Evergreen Recycling: recompartilhamento inteligente
- [X-COM-012] Thread Composer: interface web básica

### FASE 2 — Growth (Semana 2-3)
- [X-COM-013] Viral Library: busca e categorização
- [X-COM-014] Lead CRM: tracking no Supabase
- [X-COM-015] Auto-DM Sequences: workflow aprovado

### FASE 3 — Scale (Semana 4-6)
- [X-COM-016] Social Listening: monitoramento avançado
- [X-COM-017] Analytics Dashboard: visualizações
- [X-COM-018] Auto-Plug: promoção inteligente
- [X-COM-019] Variations Generator: A/B testing

---

## 💰 Economia vs Ferramentas Pagas

| Ferramenta | Preço Mensal | Nossa Alternativa | Economia |
|--------------|--------------|-------------------|----------|
| AutoTweet Pro | $29/mo | x-smart-scheduler.ts | $348/ano |
| TweetHunter | $99/mo | x-viral-library.ts + x-lead-crm.ts | $1188/ano |
| Hypefury | $49/mo | x-evergreen-recycler.ts + x-auto-plug.ts | $588/ano |
| Brand24 | $79/mo | x-opportunity-alert.ts (social listening) | $948/ano |
| Typefully Pro | $19/mo | x-composer (thread builder) | $228/ano |
| **TOTAL** | **$275/mo** | **Self-hosted VPS** | **$3300/ano** |

**Custo real:** Apenas VPS (já pago) + X API (gratuita até 500 posts/mês)

---

## 🔧 Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────┐
│                    EGOS VPS (Hetzner)                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  /opt/xmcp (existente) — MCP Server X              │    │
│  │  → X API credentials, OAuth, low-level API calls      │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  /opt/x-automation (novo) — Nossas ferramentas      │    │
│  │                                                     │    │
│  │  • x-opportunity-alert.ts     (P0 - done)          │    │
│  │  • x-approval-bot.ts          (P0 - done)        │    │
│  │  • x-smart-scheduler.ts       (P1 - semana 1)      │    │
│  │  • x-evergreen-recycler.ts    (P1 - semana 1)      │    │
│  │  • x-viral-library.ts         (P2 - semana 2)      │    │
│  │  • x-lead-crm.ts              (P2 - semana 2)      │    │
│  │  • x-auto-plug.ts             (P3 - semana 4)     │    │
│  │  • x-variations-generator.ts  (P3 - semana 4)     │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                              │
│  Cron: a cada 2h ────────────┤                              │
│  Cron: daily 9h ──────────────┤                              │
│                              ▼                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Supabase (PostgreSQL)                               │    │
│  │  • leads table                                       │    │
│  │  • posts history                                     │    │
│  │  • analytics cache                                   │    │
│  │  • evergreen queue                                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  EGOS HQ Dashboard (Next.js)                                │
│  • /x-composer — Thread builder                            │
│  • /x-analytics — Analytics dashboard                       │
│  • /x-leads — CRM leads view                               │
│  • /x-viral — Viral content library                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Próximos Passos Imediatos

1. **Hoje:** Adaptar `setup-x-monitoring.sh` para instalar em `/opt/x-automation/` (não conflitar com `/opt/xmcp`)
2. **Amanhã:** Deploy do sistema básico (x-opportunity-alert + x-approval-bot)
3. **Semana 1:** Implementar x-smart-scheduler e x-evergreen-recycler
4. **Semana 2:** Thread composer web interface

---

*Integrar features de $275/mo em solução própria — economia de $3300/ano*
