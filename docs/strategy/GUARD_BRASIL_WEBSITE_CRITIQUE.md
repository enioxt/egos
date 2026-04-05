# Guard Brasil Website — Crítica Completa & Plano de Melhoria

> **Data:** 2026-04-05 | **URL:** guard.egos.ia.br | **Stack:** Next.js 15 + Tailwind CSS 4 + Vercel

---

## O que está BOM

1. **Playground interativo** — 6 exemplos com teste ao vivo. Isso é raro em APIs de segurança — diferencial competitivo.
2. **Geração de API key sem cartão** — zero fricção para começar. Ótimo para conversão.
3. **Pricing transparente** — tiers claros, sem surpresas.
4. **Latência de 4ms** — é fast. Vale destacar mais.
5. **Audit trail com hash SHA-256** — diferencial de compliance. Precisa estar mais visível.

---

## O que precisa MELHORAR (por prioridade)

### P0 — Impede conversão

| # | Problema | Impacto | Fix |
|---|----------|---------|-----|
| 1 | **Sem OG image** — compartilhar no LinkedIn/X mostra quadrado cinza | Alto | Criar og-image.png 1200x630 |
| 2 | **Sem vídeo demo** — visitor não entende em 10s o que faz | Alto | Gravar/gerar vídeo de 30s |
| 3 | **CTA "Assinar Startup" aponta para URL raw** | Alto | Abrir Stripe Checkout em nova aba |
| 4 | **Sem social proof** — zero logos, testimonials, números | Alto | Adicionar seção "Usado por" |
| 5 | **Hero não tem visual impact** — só texto + emoji | Médio | Adicionar animação ou ilustração |

### P1 — Reduz profissionalismo

| # | Problema | Impacto | Fix |
|---|----------|---------|-----|
| 6 | **DashboardV1Giant não é responsivo** — quebra no mobile | Médio | Sidebar hamburger menu |
| 7 | **Sem favicon personalizado** — usa default Next.js | Baixo | Criar favicon Guard Brasil |
| 8 | **Sem loading states elegantes** — skeleton/shimmer | Baixo | Adicionar Suspense boundaries |
| 9 | **Código de exemplo no landing** — poderia ter syntax highlighting | Baixo | Usar prism/shiki |
| 10 | **Sem footer completo** — falta links, empresa, termos | Médio | Adicionar footer profissional |

### P2 — Diferenciação

| # | Problema | Impacto | Fix |
|---|----------|---------|-----|
| 11 | **Sem page de /about** — quem está por trás? | Médio | Criar página institucional |
| 12 | **Sem blog/changelog** — parecer produto vivo | Médio | Adicionar /blog com MDX |
| 13 | **Sem comparação com concorrentes** — Presidio, AWS Macie | Médio | Tabela comparativa na landing |
| 14 | **Sem caso de uso real** — "como a empresa X usa" | Alto | Case study (mesmo fictício) |

---

## Assets Visuais Necessários

### 1. OG Image (1200x630)
**Prompt para Google Imagen/Gemini:**
```
Create a professional dark-themed banner (1200x630px) for a Brazilian AI security API called "Guard Brasil". 
Show a shield icon with the Brazilian flag colors (green, yellow, blue). 
Include text "Guard Brasil" in bold white sans-serif font. 
Subtitle: "Segurança de IA para dados brasileiros". 
Dark navy background (#0f172a) with subtle gradient to emerald green.
Modern, clean, tech SaaS aesthetic. No photos of people.
```

### 2. Hero Illustration
**Prompt para Google Imagen:**
```
Isometric 3D illustration of a digital shield protecting Brazilian data. 
Show flowing text being scanned and masked (CPF numbers turning into asterisks). 
Color palette: dark navy (#0f172a), emerald green (#10b981), white.
Clean vector style, no gradients, suitable for dark background.
Transparent or dark navy background. 1200x800px.
```

### 3. Favicon (32x32 + 192x192)
**Prompt:**
```
Minimalist icon of a shield with "GB" letters inside. 
Emerald green (#10b981) shield on transparent background.
Simple, recognizable at 16x16px. Vector/SVG style.
```

### 4. Demo Video (30s)
**Storyboard:**
```
0-5s:  Tela com texto contendo CPF e dados sensíveis
5-10s: Cursor clica "Testar" no playground
10-15s: Animação mostrando dados sendo mascarados em tempo real
15-20s: Receipt com hash SHA-256 aparece
20-25s: Score ATRiAN 95/100 "Seguro"
25-30s: CTA "500 chamadas grátis — guard.egos.ia.br"
```
**Para gravar:** Use o próprio playground do site + screen recording (OBS ou loom.com)

### 5. Comparação Visual (tabela)
```
|                | Guard Brasil | Presidio | AWS Macie | Google DLP |
|----------------|-------------|----------|-----------|------------|
| PII Brasileiro | 15 padrões  | 3-5      | ~8        | ~10        |
| Latência       | 4ms         | 50-200ms | 200-500ms | 100-300ms  |
| ATRiAN Ético   | ✅          | ❌       | ❌        | ❌         |
| Audit Trail    | ✅ SHA-256  | ❌       | Parcial   | Parcial    |
| Setup          | 1 curl      | Docker   | Console   | Console    |
| Grátis         | 500/mês     | OSS      | Não       | Não        |
| Foco Brasil    | Nativo      | Genérico | Genérico  | Genérico   |
```

---

## Layout Melhorias (com Google Stitch se necessário)

### Hero Section Redesign
```
Current: Emoji + texto + botão
Proposed: 
  [Left] Headline + subtitle + 2 CTAs (Testar Grátis | Ver Documentação)
  [Right] Animated terminal showing live PII masking
  [Below] 3 stat cards: "4ms latência" | "15 padrões PII" | "500 grátis/mês"
```

### Social Proof Section (novo)
```
"Protegendo dados brasileiros em produção"
[Logo 1] [Logo 2] [Logo 3] [Logo 4]
"Mais de X chamadas processadas"
```

### How It Works Section (novo)
```
3 passos com ícones:
1. Gere sua chave (POST /v1/keys) — ícone de chave
2. Envie texto (POST /v1/inspect) — ícone de scanner
3. Receba resultado mascarado + receipt — ícone de escudo ✓
```

---

## Prompts para Google Stitch (se usar)

**Prompt 1 — Hero redesign:**
```
Redesign the hero section of a dark-themed SaaS landing page. 
Left side: headline "Proteja dados brasileiros com IA" in white bold, 
subtitle "15 padrões PII detectados em 4ms", 
two buttons: green "Testar Grátis" and outline "Ver Documentação".
Right side: dark terminal window showing JSON API response with masked CPF.
Background: dark navy #0f172a with subtle emerald glow.
```

**Prompt 2 — Pricing section:**
```
Three pricing cards on dark background (#0f172a). 
Card 1: "Gratuito" R$0, 500 chamadas, green outline.
Card 2: "Startup" R$0.007/chamada, highlighted with emerald border and "Mais Popular" badge.
Card 3: "Business" R$0.004/chamada, subtle border.
Modern SaaS pricing card design, Tailwind CSS compatible.
```

**Prompt 3 — Comparação:**
```
Dark-themed comparison table showing Guard Brasil vs 4 competitors.
Columns: Feature, Guard Brasil (green checkmarks), Presidio, AWS Macie, Google DLP.
Guard Brasil column highlighted in emerald green.
Clean, easy to read, professional tech aesthetic.
```

---

## HttpOnly Cookies no Privy

No dashboard Privy (Settings → Security):
1. Encontre "HttpOnly cookies" toggle
2. **ATIVE** — quando ativado, o token de autenticação é armazenado como cookie HttpOnly
3. Isso significa que JavaScript do lado do cliente **não pode** acessar o token via `document.cookie`
4. Protege contra ataques XSS (scripts maliciosos não conseguem roubar o token)
5. O Privy SDK continua funcionando normalmente — ele usa o cookie automaticamente nos requests

**Trade-off:** Com HttpOnly ativado, se você precisar do token no client-side para algo custom, não terá acesso. Mas para Guard Brasil isso é irrelevante — o SDK gerencia tudo.

---

## Plano de Execução (Ordem)

1. **Hoje:** Testar Guard Brasil com dados reais (agente rodando)
2. **Hoje:** Gerar OG image + favicon (prompts acima)
3. **Amanhã:** Gravar vídeo demo (30s, screen recording do playground)
4. **Amanhã:** Adicionar seção "Como Funciona" + comparação
5. **Esta semana:** Post no X.com + LinkedIn com vídeo
6. **Esta semana:** Enviar 5 emails (M-007)
7. **Próxima semana:** Integrar NOWPayments + x402

---

*Guard Brasil Website Critique v1.0 — Claude Opus 4.6 — 2026-04-05*
