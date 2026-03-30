# X.com Social Automation — Plano Completo Guard Brasil

> **Data:** 2026-03-30 | **Fontes:** X API docs, Postproxy, tendX, ppc.land
> **Objetivo:** Sistema completo de geração, publicação, monitoramento e engajamento no X.com

---

## 1. CAPACIDADES DO X.COM EM 2026 (pesquisa atualizada)

### O que podemos postar via API:

| Tipo | Disponível via API? | Limites | Notas |
|------|-------------------|---------|-------|
| **Tweet texto** | Sim | 280 chars (free), 25k chars (Premium) | Core feature |
| **Thread** | Sim | Encadeia múltiplos tweets | Ótimo para tutorials |
| **Imagens** | Sim | 4 por post, JPG/PNG/GIF, max 5MB | Upload via media endpoint |
| **Vídeos** | Sim | 1 por post, max 512MB, 2:20 min | Upload assíncrono |
| **GIFs** | Sim | Via media upload | Animações |
| **Polls** | Sim | 2-4 opções, 5min-7dias | Engajamento alto |
| **Articles** | **NÃO via API** | Premium only, web UI | Lançado Jan 2026 para todos Premium |
| **Spaces** | Parcial | Criar/gerenciar | Audio live |
| **Cards** | Automático | Link preview | URL no tweet gera card |

### X API Pricing (2026):

| Tier | Preço | Post writes/mês | Post reads/mês |
|------|-------|-----------------|----------------|
| **Free** | $0 | ~500 | ~50 |
| **Basic** | $200/mo | ~50.000 | ~10.000-15.000 |
| **Pro** | $5.000/mo | ~300.000 | 1.000.000 |
| **Pay-per-use** | Créditos | $0.01/post | $0.005/read |

### Nosso cenário:
- 1 post/dia = 30 posts/mês
- **Free tier basta** (500 writes/mês > 30)
- Se precisarmos ler (monitorar mentions): Free lê ~50/mês — pode ser curto
- **Solução:** Começar no Free, migrar para Pay-per-use se precisar monitorar

### Articles (posts longos):
- Lançado Jan 2026 para **todos os Premium** (antes era Premium+ exclusivo)
- Suporta markdown, imagens inline, formatação rica
- **NÃO disponível via API** — precisa postar manualmente ou via automação de browser
- **Estratégia:** Postar tweet curto (API) + link para article (manual 1x/semana)

### Limites importantes:
- 2.400 posts/dia (inclui replies, reposts, quotes)
- ~50 posts por janela de 30 minutos
- Follow: 400/dia (free), 1.000/dia (Premium)
- DM: 500/dia
- **Para nós: 1 post/dia está muito abaixo de qualquer limite**

---

## 2. SISTEMA COMPLETO DE SOCIAL AUTOMATION

### Arquitetura do Sistema:

```
┌─────────────────────────────────────────────────────────┐
│                GUARD BRASIL SOCIAL ENGINE               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Content  │  │ Visual   │  │ Schedule │              │
│  │ Generator│  │ Generator│  │ Manager  │              │
│  │ (Qwen)   │  │(Qwen/API)│  │ (Cron)   │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │              │             │                     │
│  ┌────▼──────────────▼─────────────▼─────┐              │
│  │           Post Composer                │              │
│  │  tweet + image + hashtags + CTA        │              │
│  └────────────────┬──────────────────────┘              │
│                   │                                      │
│  ┌────────────────▼──────────────────────┐              │
│  │           Review Queue                 │              │
│  │  (human approval before posting)       │              │
│  └────────────────┬──────────────────────┘              │
│                   │                                      │
│  ┌────────────────▼──────────────────────┐              │
│  │           X.com API Publisher          │              │
│  │  OAuth 1.0a + media upload             │              │
│  └────────────────┬──────────────────────┘              │
│                   │                                      │
│  ┌────────────────▼──────────────────────┐              │
│  │           Analytics Tracker            │              │
│  │  impressions, likes, retweets, clicks  │              │
│  └────────────────┬──────────────────────┘              │
│                   │                                      │
│  ┌────────────────▼──────────────────────┐              │
│  │           Engagement Bot               │              │
│  │  reply to mentions, thank followers    │              │
│  └───────────────────────────────────────┘              │
│                                                         │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│               DASHBOARD INTEGRATION                      │
│  Social tab: posts scheduled, analytics, engagement     │
│  Semrush-style: mentions, sentiment, competitor watch   │
└─────────────────────────────────────────────────────────┘
```

### Componentes detalhados:

#### 2.1 Content Generator (Qwen-powered)

```typescript
// agents/social/content-generator.ts

interface PostDraft {
  text: string;        // Tweet text (max 280 chars para free, 25k Premium)
  hashtags: string[];  // Max 3-5 (mais que isso reduz engagement)
  cta: string;         // Call to action
  image_prompt?: string; // Para gerar imagem
  thread?: string[];   // Se for thread
  category: 'educational' | 'case_study' | 'product' | 'engagement' | 'news';
  tone: 'professional' | 'casual' | 'technical' | 'provocative';
}

// Template de geração diária
const WEEKLY_CALENDAR = {
  monday:    { category: 'educational', topic: 'LGPD concept' },
  tuesday:   { category: 'case_study', topic: 'CPF masking demo' },
  wednesday: { category: 'product', topic: 'Guard Brasil feature' },
  thursday:  { category: 'engagement', topic: 'Poll or question' },
  friday:    { category: 'news', topic: 'AI safety news' },
  saturday:  { category: 'educational', topic: 'ATRiAN ethical AI' },
  sunday:    { category: 'case_study', topic: 'Govtech use case' },
};
```

#### 2.2 Visual Generator

```typescript
// agents/social/visual-generator.ts

// Opções de geração visual:
// 1. Screenshot da API em ação (terminal-style)
// 2. Diagrama (mermaid → PNG)
// 3. Infográfico (HTML → screenshot)
// 4. Code snippet (syntax highlighted)

async function generateVisual(post: PostDraft): Promise<Buffer> {
  switch (post.category) {
    case 'case_study':
      // Terminal screenshot mostrando API call + response
      return renderTerminalScreenshot({
        command: 'curl guard.egos.ia.br/v1/inspect -d \'{"text":"CPF: 123.456.789-00"}\'',
        response: '{"safe":true,"masked":"CPF: ***.***.***-00","atrian_score":95}',
      });
    case 'educational':
      // Infográfico com stats
      return renderInfoGraphic({
        title: post.text.slice(0, 50),
        stats: ['96% margem', '4ms latência', '<$0.01/chamada'],
      });
    case 'product':
      // Screenshot do dashboard
      return renderDashboardPreview();
    default:
      return null; // Text-only post
  }
}
```

#### 2.3 Schedule Manager + Review Queue

```typescript
// agents/social/scheduler.ts

interface ScheduledPost {
  id: string;
  draft: PostDraft;
  visual?: Buffer;
  scheduled_at: Date;     // Horário ideal (pesquisa: 9-10 AM BRT ou 18-19 PM BRT)
  status: 'draft' | 'pending_review' | 'approved' | 'posted' | 'failed';
  approved_by?: string;   // Enio approves before posting
  posted_at?: Date;
  x_post_id?: string;     // ID do post no X
  analytics?: PostAnalytics;
}

// Fluxo:
// 1. Content Generator cria draft (6 AM diário)
// 2. Review Queue notifica Enio via Telegram
// 3. Enio aprova/edita via Telegram ou Dashboard
// 4. Publisher posta no horário agendado (9 AM BRT)
// 5. Analytics Tracker coleta dados (a cada 6h)
```

#### 2.4 Analytics Tracker

```typescript
// agents/social/analytics.ts

interface PostAnalytics {
  post_id: string;
  impressions: number;
  likes: number;
  retweets: number;
  replies: number;
  url_clicks: number;    // Clicks no link guard.egos.ia.br
  profile_visits: number;
  engagement_rate: number; // (likes+retweets+replies) / impressions

  // Nosso tracking adicional
  landing_page_visits: number;   // Via UTM params
  api_tests_from_post: number;   // Via referrer tracking
  signups_from_post: number;     // Via attribution
}

// KPIs semanais:
// - Engagement rate > 2% (bom para tech/B2B)
// - URL clicks > 10% do impressions
// - API tests > 5 por post
// - Signups > 1 por semana
```

#### 2.5 Engagement Bot

```typescript
// agents/social/engagement.ts

// Ações automáticas (com aprovação):
// 1. Like em mentions de Guard Brasil
// 2. Reply agradecer quem testa
// 3. Quote retweet de posts sobre LGPD/PII com comentário relevante
// 4. Follow back contas govtech/devs BR

// Ações manuais (Enio):
// 1. Responder perguntas técnicas
// 2. Compartilhar resultados de demos
// 3. Postar articles longos (1x/semana)
```

---

## 3. PRIMEIRO POST — DRAFT PARA APROVAÇÃO

### Post #1 (Segunda-feira, educational):

```
🛡️ Guard Brasil — LGPD compliance para IA em 4ms

"CPF: 123.456.789-00"
     ↓ Guard Brasil API
"CPF: ***.***.***-00" ✅

Open source. Free tier. Made for govtech BR.

Teste grátis: guard.egos.ia.br

#LGPD #IA #Govtech #OpenSource #DataPrivacy
```

**Análise:**
- 198 caracteres (bem dentro do limite de 280)
- 5 hashtags (no limite ideal — mais reduz engagement)
- CTA direto (link)
- Demonstra valor em 1 exemplo
- Tom: técnico + acessível
- Imagem: terminal screenshot mostrando curl command + response

### Post #2 (Terça-feira, case study):

```
Masking de placa veicular em tempo real:

"Carro ABC-1234 visto no local"
     ↓
"Carro ***-**** visto no local"

4ms. R$ 0,005/chamada. 150 testes grátis.

guard.egos.ia.br

#LGPD #Segurança #Policia #Govtech
```

### Post #3 (Quarta-feira, product):

```
Guard Brasil agora tem ATRiAN — validação ética de IA 🧠

Score 0-100 para detectar bias em textos:
• Discriminação racial? Score baixo ⚠️
• Dados sem consentimento? Bloqueado 🚫
• LGPD compliant? Score alto ✅

API + npm SDK gratuito.

guard.egos.ia.br
```

### Post #4 (Quinta-feira, engagement):

```
Qual o maior risco de compliance com IA no Brasil hoje?

🔴 Vazamento de CPF/dados pessoais
🟡 Bias algorítmico (racial, gênero)
🟢 Falta de auditoria/trilha
🔵 Nenhum, IA é segura
```
*(Poll — 7 dias)*

### Post #5 (Sexta-feira, news):

```
LGPD completa 8 anos em 2026.

Quantas empresas brasileiras têm masking automático de PII?

Quase zero.

Guard Brasil resolve isso com 3 linhas de código:

npm install @egosbr/guard-brasil

guard.egos.ia.br — 150 testes grátis
```

---

## 4. TOM, HASHTAGS, TAMANHO — REGRAS

### Tom:
- **Profissional mas acessível** — não acadêmico, não casual demais
- **Show, don't tell** — sempre com exemplo real (input → output)
- **Brasileiro** — português (exceto termos técnicos)
- **Provocativo quando apropriado** — perguntas, polls, dados surpreendentes
- **Nunca vendedor** — informar/educar primeiro, CTA sutil

### Hashtags:
- **3-5 por post** (pesquisas mostram que >5 reduz engagement)
- **Core fixas:** #LGPD #Govtech
- **Rotativas:** #IA #DataPrivacy #OpenSource #Segurança #Compliance #AIEthics #PII
- **Nichos:** #Policia #TribunalDeContas #MinistérioPúblico (quando relevante)

### Tamanho:
- **Tweet:** 150-250 chars (ideal para engagement)
- **Thread:** 3-5 tweets (1x/semana para deep dives)
- **Article:** 500-2000 palavras (1x/semana, manual via web Premium)

### Horários ideais (BR):
- **9-10 AM BRT** — profissionais começando o dia
- **12-13 PM BRT** — hora do almoço (scroll time)
- **18-19 PM BRT** — fim do expediente

### Frequência:
- **1 post/dia** (M-F)
- **1 thread/semana** (deep dive)
- **1 article/semana** (se Premium ativo)
- **Weekend:** descanso ou repost do melhor da semana

---

## 5. AUTOMAÇÃO COMPLETA — GERA, POSTA, MONITORA, INTERAGE

### Pipeline diário:

```
06:00 BRT — Content Generator (Qwen) cria draft do dia
  ├─ Texto do tweet
  ├─ Hashtags
  ├─ Imagem (se aplicável)
  └─ CTA

07:00 BRT — Notificação para Enio (Telegram)
  ├─ Preview do post
  ├─ Botões: ✅ Aprovar | ✏️ Editar | ❌ Rejeitar
  └─ Sugestões alternativas

09:00 BRT — Publisher posta (se aprovado)
  ├─ Upload de mídia (se imagem/vídeo)
  ├─ Post do tweet
  └─ Log em telemetria

15:00 BRT — Analytics snapshot #1
  ├─ Impressions, likes, retweets
  └─ URL clicks (UTM tracking)

21:00 BRT — Analytics snapshot #2 + engagement
  ├─ Responder mentions
  ├─ Like em replies relevantes
  └─ Report do dia via Telegram
```

### Geração de vídeo (futuro — fase 2):

```
Opções:
1. Screen recording do terminal (API demo)
2. Animação de dados sendo mascarados (CSS/canvas)
3. Slideshow com stats (3-5 slides, 15s cada)
4. Talking head com legendas (IA-generated)

Ferramentas:
- Remotion (React → vídeo programático)
- FFmpeg (composição)
- Qwen Vision (para gerar storyboard)
```

### Geração de imagens:

```
Tipos:
1. Terminal screenshots (puppeteer → screenshot)
2. Infográficos (HTML template → screenshot)
3. Code snippets (Shiki syntax highlighting → image)
4. Diagramas (Mermaid → PNG)
5. Stats cards (React component → PNG)

Todas geradas programaticamente, sem depender de IA de imagem.
```

---

## 6. INTEGRAÇÃO COM DASHBOARD (estilo Semrush/Canva)

### Tab "Social" no Dashboard:

```
┌─────────────────────────────────────────────────────────┐
│  GUARD BRASIL DASHBOARD — Social                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─── Posts This Week ──────────────────────────────┐   │
│  │ Mon: 🟢 "CPF masking demo" — 342 imp, 12 likes  │   │
│  │ Tue: 🟢 "Placa detection" — 198 imp, 8 likes    │   │
│  │ Wed: 🟡 "ATRiAN feature" — pending approval     │   │
│  │ Thu: ⚪ Scheduled (poll)                         │   │
│  │ Fri: ⚪ Draft ready                              │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─── Weekly Stats ─────────────────────────────────┐   │
│  │ Impressions: 1,240    Engagement: 3.2%           │   │
│  │ URL Clicks: 87        API Tests: 23              │   │
│  │ New Followers: 14     Signups: 2                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─── Content Calendar ─────────────────────────────┐   │
│  │ [Apr 1] CPF masking → Terminal screenshot         │   │
│  │ [Apr 2] RG detection → Infographic                │   │
│  │ [Apr 3] ATRiAN ethics → Diagram                   │   │
│  │ [Apr 4] Poll: biggest compliance risk?            │   │
│  │ [Apr 5] LGPD birthday post → Stats card           │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─── Engagement Queue ─────────────────────────────┐   │
│  │ @cto_govtech mentioned Guard Brasil → Reply?      │   │
│  │ @dev_lgpd asked about pricing → Reply?            │   │
│  │ @tribunal_mg retweeted → Thank?                   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─── Competitor Watch ─────────────────────────────┐   │
│  │ Grepture: 2 posts this week (EU privacy focus)    │   │
│  │ Protecto: 1 post (enterprise healthcare)          │   │
│  │ Strac: 3 posts (DLP general)                      │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 7. CRONOGRAMA DE IMPLEMENTAÇÃO

| Fase | Dias | Entrega |
|------|------|---------|
| 1 | 1-2 | Content generator (Qwen) + 7 drafts iniciais |
| 2 | 2-3 | X.com API client (OAuth + post + media upload) |
| 3 | 3-4 | Review queue (Telegram bot notification) |
| 4 | 4-5 | Analytics tracker básico |
| 5 | 6-7 | Visual generator (terminal screenshots) |
| 6 | 8-10 | Dashboard Social tab |
| 7 | 11-14 | Engagement bot + competitor watch |
| 8 | 15+ | Vídeo automation (Remotion) |

**Primeira versão funcional: 5 dias.**
**Sistema completo: 2 semanas.**
