# PART-003: X.com Launch Thread — Guard Brasil + Partner Search

> **Purpose:** Open the doors for partnerships, find a GTM co-founder, attract first customers — all in one honest thread. No exaggeration, no fake metrics.
> **Tone:** Direct, technical, vulnerable, looking-for-partners. Reads like a human, not a marketer.
> **Drafted:** 2026-04-06
> **Status:** Pending Enio approval before posting

---

## Strategy

This thread does FOUR things at once:
1. **Demos the product** (with a real curl call + real numbers)
2. **Admits the gap** (0 customers, looking for partner) — counterintuitively this builds trust
3. **Opens 3 doors** at the end: try the API, become an early customer, become a co-founder
4. **Anchors a brand voice** — Brazilian, builder, honest, technical

The "looking for a GTM co-founder" angle is **the differentiator**. Most launch threads pretend everything is fine. Yours says "I built this, I need help selling it" — that's catnip for the right kind of person and signal-to-noise filter for everyone else.

---

## The Thread (5 tweets)

### Tweet 1 (HOOK — must stop the scroll)

```
Construí uma API de detecção de PII brasileiro:
CPF, CNPJ, RG, MASP, CNH e mais 11 padrões.

4ms de resposta. 500 chamadas grátis/mês.
Open source no npm.

Mas tem um problema honesto que vou contar no fim 👇

(thread)
```

**Why it works:**
- Concrete numbers in line 1 (anchors trust)
- Free tier in line 2 (removes friction)
- "honest problem" hook in line 4 (curiosity gap)
- "thread" signal — readers know to expand

**280 chars: ✅** (243 chars)

---

### Tweet 2 (PROOF — demo the API live)

```
Roda agora no terminal:

curl -X POST https://guard.egos.ia.br/v1/inspect \
  -d '{"content":"CPF 123.456.789-00, e-mail joao@x.com"}'

Resposta em ~4ms:
{
  "patterns": ["CPF","EMAIL"],
  "lgpd_risk": "HIGH",
  "verified": true
}

Sem cadastro, sem cartão.
```

**Why it works:**
- Anyone reading can copy-paste right now
- Real endpoint, real response shape
- Shows it's a real product, not vaporware

**280 chars: ✅** (266 chars)

---

### Tweet 3 (DIFFERENTIATION — what's different from regex copy-paste)

```
Por que não é só regex:

→ 15 padrões BR validados com dígito verificador real
→ Detecta CPF mascarado (123.***.789-00) e CPF cru
→ Classifica risco LGPD por contexto (HIGH/MEDIUM/LOW)
→ Open source — auditável: github.com/enioxt/egos
→ SDK TypeScript: @egosbr/guard-brasil

E roda no VPS Hetzner, não em "cloud mágica".
```

**Why it works:**
- Lists real differentiators (check digits, masking detection, risk classification)
- Open source link transfers trust
- "VPS Hetzner não cloud mágica" = builder honesty, separates from corporate vendors

**280 chars: ⚠️ check** (343 chars — too long, needs trim)

**Trimmed version:**
```
Por que não é só regex:

→ 15 padrões BR validados com dígito verificador real
→ Detecta CPF mascarado e CPF cru
→ Classifica risco LGPD por contexto
→ Open source: github.com/enioxt/egos
→ SDK npm: @egosbr/guard-brasil

Roda no VPS Hetzner, sem cloud mágica.
```
**280 chars: ✅** (276 chars)

---

### Tweet 4 (THE HONEST PROBLEM — vulnerability + opportunity)

```
Agora a parte honesta:

Tenho ZERO clientes pagantes hoje.

Construí o produto, a infra, os SDKs, os docs.
Mas eu sou developer, não vendedor.

E LGPD/compliance se vende com confiança, não com tweet.

Estou procurando um sócio de GTM (DPO, compliance, vendas B2B BR).
```

**Why it works:**
- "ZERO clientes" — radical honesty disarms skepticism
- "developer, não vendedor" — explains the gap without making excuses
- "se vende com confiança" — names the real moat (Moat 1 from defensibility doc)
- Specific ask: GTM co-founder

**280 chars: ✅** (263 chars)

---

### Tweet 5 (THE 3 DOORS — call to action, choose-your-own-adventure)

```
Se você é:

🛠️ Dev/CTO de fintech ou healthtech:
   testa free tier — 500 calls/mês — guard.egos.ia.br

🎯 DPO ou consultor LGPD:
   me chama — quero feedback honesto + parceria

🤝 Quer ser sócio de GTM:
   responde aqui ou DM

Sou @anoineim. Abrindo as portas.
```

**Why it works:**
- 3 clear personas, 3 clear actions
- DM open (unusual on X — signals approachability)
- Last line has handle + "abrindo as portas" — reframes as invitation, not begging

**280 chars: ✅** (270 chars)

---

## Posting Mechanics

### When to post
- **Best time:** Tuesday or Wednesday, 09:00 BRT (=12:00 UTC)
- Why: BR audience peak engagement, before lunch
- Avoid: weekends (low engagement), evenings (lost in noise)

### Visual to attach to Tweet 1
- The new `og-image.png` we built (1200×630, dark navy + green shield + "Detecção de PII brasileira em 4ms")
- This gives the thread a strong visual anchor in the timeline

### Replies to prepare
Have these answers ready in Notes app for fast response (first 60 min after posting matters most for reach):

| Likely question | Answer |
|---|---|
| "Como vocês comparam com Presidio?" | Presidio é Microsoft, foco global, 0 padrões BR. A gente: 15 patterns BR, dígitos verificadores reais, free tier sem cadastro. Trade-off: Presidio tem mais maturidade global, a gente tem foco brasileiro. |
| "Onde fica hospedado?" | VPS Hetzner Falkenstein, 100% BR-aware. Latência média 4ms BR-EU, vamos colocar replica BR em Q3. |
| "Fonte do código?" | github.com/enioxt/egos — monorepo, packages/guard-brasil. |
| "Como funciona o free tier?" | 500 chamadas/mês sem cadastro, depois R$ X/mês para 10k+. Sem credit card upfront. |
| "É só regex?" | Não. Validação de dígito verificador (CPF/CNPJ algo), classificação de risco contextual, detecção de máscaras (123.***.789-00). Mas sim, regex é parte. Honesto: o valor está mais no contexto e responsabilidade legal do que no regex puro. |
| "ANPD aprovou?" | Não — ANPD não aprova ferramentas, só regula uso. Vamos submeter ao registro público de tools quando abrir. |
| "Quanto custa?" | Free tier: 500 chamadas/mês — único tier oficial hoje. Os outros tiers estão sendo desenhados (Starter ~R$ 99/mês, Pro ~R$ 497/mês, Enterprise custom) mas ainda não estão no ar. Quem quiser contratar agora vira parceiro piloto com pricing custom. |
| "Preciso de DPO certificado pra usar?" | Não. Mas a gente RECOMENDA. Posso indicar DPOs parceiros se você precisar. |
| "Vocês têm SLA?" | Hoje, NÃO. É open source em desenvolvimento ativo, sem contrato formal. A meta para o tier Enterprise (quando lançar) é 99.9% uptime + 24h response, mas isso ainda é rascunho — não uma garantia. Free tier é best-effort. Quem precisa de SLA hoje, melhor esperar 2-3 meses ou conversar com a gente sobre uma parceria piloto. |
| "Como ser sócio?" | Manda DM ou email enioxt@gmail.com com 3 linhas: quem você é, o que faz hoje, por que essa oportunidade. Marco call de 30min na semana seguinte. |

---

## LinkedIn Long-form Companion Post

Posted **same day, 2 hours after** the X thread, on LinkedIn (different audience):

```
🇧🇷 Procurando sócio de GTM para uma API de compliance LGPD

Nos últimos 3 meses construí o Guard Brasil: uma API de detecção
de PII brasileiro (CPF, CNPJ, RG, MASP, CNH e mais 11 padrões) com
4ms de resposta e free tier de 500 chamadas/mês.

A parte técnica está pronta:
✅ API live em guard.egos.ia.br
✅ SDK TypeScript publicado no npm (@egosbr/guard-brasil)
✅ 15 padrões validados com dígito verificador real
✅ Open source no GitHub (auditável)
✅ Infraestrutura no VPS Hetzner

A parte comercial está em ZERO:
❌ 0 clientes pagantes
❌ 0 contratos SLA assinados
❌ 0 parcerias formais
❌ 0 listagens em marketplaces

E aqui vem a parte honesta: eu sou developer.
Construo bem, vendo mal.

LGPD/compliance se vende com CONFIANÇA, não com regex.
DPO de fintech não compra porque o produto é bom — compra porque
sabe quem é responsável quando der ruim.

Por isso, estou procurando um sócio de GTM:

→ Background em DPO, compliance LGPD, ou vendas B2B BR
→ Idealmente com certificação CDPO/BR (ANPPD ou IAPP)
→ Já vendeu SaaS B2B antes (mesmo que pequeno)
→ Quer trabalhar com equity, não salário fixo
→ Acredita que open source + transparência = vantagem competitiva

Eu trago: produto, infra, manutenção, evolução técnica.
Você traz: rede de DPOs, vendas, parcerias, presença pública.
Split: justo, conversamos.

Se você é, ou conhece alguém que seja, manda mensagem aqui ou
email: enioxt@gmail.com

Próximas 48h vou responder cada mensagem pessoalmente.

Compartilha se conhece alguém que poderia se interessar 🙏

#LGPD #Compliance #PrivacyTech #Brasil #SaaS #B2B #Founder
```

**Why this works on LinkedIn:**
- LinkedIn audience expects long-form
- "Construo bem, vendo mal" — universally relatable founder pain
- Specific role profile (CDPO/BR cert) — filters serious from curious
- "Equity, não salário" — sets expectation upfront
- Hashtags are LinkedIn-optimized for BR compliance audience

---

## What happens after posting

### Hour 0-1 (critical window)
- Stay in front of the thread
- Respond to every reply within 5 minutes
- Like + RT every meaningful response
- DO NOT auto-respond — every reply is a person

### Hour 1-24
- 1 quote-tweet of the thread with a follow-up insight
- Reply to anyone who shared the thread with a thank-you

### Day 2-7
- Engagement metrics check (impressions, profile clicks, DMs, signups)
- Track in `docs/business/launch_thread_metrics.md`
- For every DM about co-founder: schedule 30min call within 48h

### Success metrics (realistic)
- Tweet 1 impressions: 5k-15k (good for a 0-customer founder)
- Replies: 10-30
- Free tier signups (if measurable): 5-20
- Co-founder DMs: 1-5 (1 serious counts as success)
- LinkedIn post engagements: 50-200

### Failure mode
- 0 DMs in 48h → thread didn't land
- Recovery: post a follow-up thread next week with a different angle (e.g., "How I built it" technical deep dive)

---

## Pre-flight checklist before posting

- [ ] og-image.png is live on guard.egos.ia.br/ (deploy first!)
- [ ] guard.egos.ia.br/v1/inspect actually responds in <10ms (test 5x)
- [ ] github.com/enioxt/egos is public and the README mentions Guard Brasil prominently
- [ ] enioxt@gmail.com is monitored (notifications on)
- [ ] X DMs open to non-followers
- [ ] LinkedIn profile updated with "Founder, Guard Brasil" headline
- [ ] First reply to your own thread is scheduled (you reply first → seeds engagement)
```
First reply (post 2 minutes after the thread):
"Para quem quiser ver o código antes de testar:
github.com/enioxt/egos/tree/main/packages/guard-brasil

Tudo MIT. Inclusive os 15 padrões e os testes."
```

---

## DO NOT POST until

1. Enio reads the full thread and approves each tweet
2. og-image.png is deployed to guard.egos.ia.br/og-image.png (currently only in dev server)
3. The pricing page (guard.egos.ia.br/pricing or similar) actually shows tiers (or the thread doesn't mention pricing)
4. enioxt@gmail.com inbox is at ≤10 unread (so you can respond fast)
5. Calendar has 2h blocked the day of posting for replies + DMs
