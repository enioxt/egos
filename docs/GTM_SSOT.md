# GTM_SSOT.md — Guard Brasil Go-To-Market (SSOT)
> Version: 1.0.0 | Updated: 2026-04-06
> SINGLE SOURCE OF TRUTH for: tasks, social content, outreach, partners, equity offer
> All GTM content lives HERE. Never create docs/business/*, docs/sales/* for GTM topics.
> Supersedes: PART002_SOCIAL_POSTS.md, PART003_LAUNCH_THREAD.md, OUTREACH_EMAIL_TEMPLATES.md, M007_OUTREACH_STRATEGY_EMAILS.md, PARTNERSHIP_STRATEGY.md, DISTRIBUTION_PARTNERS_BR.md

---

## 1. STATUS (atualizar a cada sessão)

| Métrica | Hoje | Meta 30 dias | Meta 90 dias |
|---------|------|--------------|--------------|
| MRR | R$0 | R$500 | R$5.000 |
| Clientes pagantes | 0 | 5 | 50 |
| npm downloads/semana | ~10 | 100 | 500 |
| Parceiros ativos | 0 | 1 (Stripe) | 3 |
| GitHub stars | ? | 50 | 200 |
| M-007 emails enviados | 0 | 5 | 20 |
| M-007 dias em atraso | **7+** | — | — |

**Bloqueadores ativos:**
- M-007: STALE 7+ dias — emails de outreach ainda não enviados (P0#2)
- GTM-002: thread X.com bloqueada por og-image.png não deployada
- GTM-009: LinkedIn post aguarda postagem manual
- GTM-015: og-image.jpg não gerado ainda (bloqueador de GTM-002)

**Última atualização:** 2026-04-06

---

## 2. EQUITY & CO-FOUNDER OFFER

> Esta seção é estratégica. Manter proeminente — foi enterrada em PART003 antes.

### O que Enio traz

- Produto live: Guard Brasil API v0.2.2 — 15 padrões PII, 4ms p95, free tier
- Infraestrutura: VPS Hetzner, Supabase, Stripe metered billing ativo
- SDK TypeScript publicado no npm (`@egosbr/guard-brasil`, MIT)
- Open source core auditável: github.com/enioxt/egos
- F1 score 85.3% (melhor que Microsoft Presidio para dados BR)
- Manutenção, evolução técnica, novos padrões, roadmap API

### O que o parceiro/sócio traz

- Background em DPO, compliance LGPD, ou vendas B2B BR
- Idealmente: certificação CDPO/BR (ANPPD ou IAPP)
- Já vendeu SaaS B2B antes (mesmo que pequeno)
- Rede de DPOs, compliance consultants, fintechs/healthtechs
- Presença pública no espaço de privacidade de dados BR
- **NOT um developer** (essa parte está coberta)
- Open a equity-based comp (não salário fixo)

### Termos

- **Split:** equity justo, conversamos. Nenhuma fórmula pre-definida.
- **Estrutura:** Co-fundador, não funcionário — full upside, sem salário fixo inicial
- **Rationale:** LGPD/compliance se vende com confiança, não com feature. O moat real é a rede de DPOs e a credibilidade no mercado BR — não o regex.

### Script de abordagem (co-founder outreach)

> Hey [nome], sou Enio Rocha. Construí uma API open source de detecção de PII para BR (https://guard.egos.ia.br) — mais rápida que Presidio, 15 padrões BR nativos, 4ms p95.
> Está live, free tier, números reais. Sou developer, não vendedor — procuro um sócio de GTM que conheça o mercado BR de compliance e possa tocar vendas/parcerias enquanto eu continuo construindo.
> Equity, full upside, sem salário fixo no início. Quer 30 minutos de call?

### Onde encontrar o sócio ideal

1. **ANPPD member directory** (associação BR de DPOs — vale pagar a associação)
2. **LinkedIn search:** `(DPO OR "Data Protection Officer") AND Brazil AND "open to opportunities"`
3. **DPO meetup speakers** — quem apresenta em eventos IAPP ou ANPPD
4. **YC BR / Latitud / Atlantico Ventures** — compliance heads de portfólio
5. **Nossos próprios usuários** (quando tivermos) — DPOs entusiastas que se auto-selecionam

---

## 3. TASKS PENDENTES (P0 → P2)

### P0 — Crítico (bloqueia receita)

- [ ] **M-007**: Enviar 5 emails de outreach para DPOs/compliance teams (templates: §5). STALE 7+ dias. **Ação imediata.**
- [ ] **GTM-002**: Publicar thread de 4 tweets no X.com @anoineim — demo Guard Brasil (CPF/RG/MASP, 4ms, free tier). Drafts: §4.1. Bloqueador: og-image.png não deployada + scripts/x-post.ts ausente.
- [ ] **GTM-015**: Gerar og-image.jpg para Guard Brasil (1200×630, template HTML pronto). Automação via Playwright screenshot. Plano: `/home/enio/.claude/plans/precious-doodling-clover.md`.
- [ ] **GTM-009**: Publicar post LinkedIn targeting compliance managers + DPOs BR. Draft: §4.3. Bloqueador: sem LINKEDIN_* credentials. **Ação: postar manualmente** (copy/paste — caminho mais rápido).
- [ ] **GTM-014**: Construir `scripts/x-post.ts` — thread poster standalone (reusar OAuth1.0a do x-reply-bot linhas 169-225). Features: lê markdown → posta thread → retorna URL. Necessário para GTM-002/011 autônomos.

### P1 — Alta prioridade

- [x] **PART-002**: Posts X.com + LinkedIn preparados ✅ 2026-04-06 — conteúdo migrado para §4 deste arquivo
- [ ] **PART-001**: Publicar Guard Brasil no ProductHunt (fazer M-007 emails primeiro)
- [ ] **PART-003**: Contatar 3 DPOs/compliance SaaS BR (templates: §5)
- [ ] **PART-004**: Submeter ao Stripe App Marketplace (já somos clientes Stripe — baixo atrito)
- [ ] **GTM-001**: Atualizar queries do x-reply-bot para focar em LGPD/compliance/DPO/ANPD (atualmente muito genérico — adicionar: lgpd, anpd, dpo, "proteção de dados", "vazamento de dados", "conformidade")
- [ ] **GTM-003**: Adicionar card de métricas GTM na home do HQ — exibe: MRR (R$0), clientes (0), M-007 status (STALE), outreach enviado/respondido, demos pendentes
- [ ] **GTM-004**: Adicionar track de descoberta de parceiros no Gem Hunter — queries: "lgpd api", "data privacy compliance brazil", "dpo tools brasil", "pii detection api". Output alimenta pipeline PART-001..015.
- [ ] **GTM-005**: Vídeo demo Guard Brasil (90 segundos) — gravar tela: chamada API → PII detectado → relatório LGPD. Subir no thread X.com.
- [ ] **GTM-011**: Tweet solo no X.com "ANPD está acelerando fiscalização em 2026. Aqui está uma API gratuita para verificar se seu app vaza PII brasileiro." + link free tier. Postar após thread GTM-002 aterrissar.
- [ ] **GTM-012**: Contatar Privacy Tools BR (Frederico Boldori) para parceria/integração — eles têm DPOs que precisam da nossa camada de API.
- [ ] **PART-005**: Nuvemshop / VTEX app store — guia de integração + submissão (e-commerce PII protection)
- [ ] **PART-006**: Totvs / SAP BR partner program (ERP + LGPD = fit natural)
- [ ] **PART-007**: AWS Marketplace listing (SaaS contract, pay-as-you-go)
- [ ] **PART-008**: Contatar DPOnet / OneTrust BR para white-label ou API partnership
- [ ] **PART-013**: LangChain Guard Brasil tool (npm @egosbr/guard-brasil-langchain)
- [ ] **GTM-016**: Construir `guard-brasil-mcp` — wraps guard.egos.ia.br como Claude tool, publicar como `@egosbr/guard-brasil-mcp` (GTM play: devs instalam na sessão Claude deles)

### P2 — Médio prazo

- [ ] **GTM-006**: Deploy Guard Brasil docs em guard.egos.ia.br/docs com playground interativo de API (Scalar ou Swagger UI)
- [ ] **GTM-007**: Submeter Guard Brasil ao registro público de ferramentas DPO da ANPD (quando abrir — constrói legitimidade)
- [ ] **GTM-008**: ProductHunt launch — preparar assets, agendar para terça ou quarta (dias de pico)
- [ ] **GTM-010**: Post no dev.to "Como detectar CPF, RG e MASP na sua API Node.js em 5 minutos" — com exemplo live Guard Brasil. Target: devs backend BR.
- [ ] **GTM-013**: Nuvemshop / VTEX app store — guia de integração + submissão
- [ ] **PART-009**: Documentação SLA v1.0 (99.9% uptime, <5ms P95, incident response) — necessário antes de abordar Totvs/Deloitte
- [ ] **PART-010**: SOC2 readiness assessment (com Vanta ou Secureframe)
- [ ] **PART-011**: Página de preços enterprise (contratos custom, volume, suporte dedicado)
- [ ] **PART-012**: Template de security questionnaire (pronto para procurement enterprise)
- [ ] **PART-014**: Zapier / Make.com connector
- [ ] **PART-015**: Bubble.io plugin (mercado no-code)

---

## 4. SOCIAL CONTENT

### 4.1 X.com — Thread Principal (4 tweets, PART-002)

> Status: RASCUNHO PRONTO — aguarda og-image.png deployada e postagem manual/GTM-014

**Tweet 1 (hook):**
```
🔍 Validamos CPF, RG, MASP e 11 outros padrões de dados pessoais brasileiros em 4ms.

@guard_brasil — API de detecção de PII para conformidade com a LGPD.

Free tier: 500 chamadas/mês. Sem cartão.

🧵 (1/4)
```

**Tweet 2 (prova técnica):**
```
Testamos ao vivo:

POST https://guard.egos.ia.br/v1/inspect
{
  "content": "CPF: 123.456.789-00, cartão 4111 1111..."
}

→ Resposta: 4ms
→ Detectado: CPF, CREDIT_CARD, LGPD_RISK: HIGH

Código aberto. Deploy em 5 min.

(2/4)
```

**Tweet 3 (diferencial):**
```
O que nos diferencia:
• 15 padrões BR nativos (CPF, RG, MASP, CNPJ, título eleitor...)
• Conformidade LGPD automática
• 0 dados enviados a terceiros (self-hostable)
• SDK TypeScript/Python no npm

Não é só regex — usa validação de dígitos verificadores reais.

(3/4)
```

**Tweet 4 (CTA):**
```
Integre em 3 linhas:

import { guard } from "@egosbr/guard-brasil"
const result = await guard.inspect(text)
if (result.lgpd_risk === "HIGH") redactPII(text)

Docs + demo: guard.egos.ia.br
npm: @egosbr/guard-brasil

Quem aqui lida com dados de usuários BR? 👇

(4/4)
```

---

### 4.2 X.com — Thread Co-founder/Equity (5 tweets, PART-003)

> Status: RASCUNHO PRONTO — pendente aprovação de Enio antes de postar
> Estratégia: faz 4 coisas de uma vez — demo do produto, admite o gap (0 clientes), abre 3 portas, ancora a voz da marca

**Tweet 1 (HOOK — deve parar o scroll):**
```
Construí uma API de detecção de PII brasileiro:
CPF, CNPJ, RG, MASP, CNH e mais 11 padrões.

4ms de resposta. 500 chamadas grátis/mês.
Open source no npm.

Mas tem um problema honesto que vou contar no fim 👇

(thread)
```
*243 chars — dentro do limite*

**Tweet 2 (PROVA — demo a API ao vivo):**
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
*266 chars — dentro do limite*

**Tweet 3 (DIFERENCIAÇÃO — versão trimmed, 276 chars):**
```
Por que não é só regex:

→ 15 padrões BR validados com dígito verificador real
→ Detecta CPF mascarado e CPF cru
→ Classifica risco LGPD por contexto
→ Open source: github.com/enioxt/egos
→ SDK npm: @egosbr/guard-brasil

Roda no VPS Hetzner, sem cloud mágica.
```

**Tweet 4 (O PROBLEMA HONESTO):**
```
Agora a parte honesta:

Tenho ZERO clientes pagantes hoje.

Construí o produto, a infra, os SDKs, os docs.
Mas eu sou developer, não vendedor.

E LGPD/compliance se vende com confiança, não com tweet.

Estou procurando um sócio de GTM (DPO, compliance, vendas B2B BR).
```
*263 chars — dentro do limite*

**Tweet 5 (AS 3 PORTAS — call to action):**
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
*270 chars — dentro do limite*

**Primeiro reply (postar 2 minutos após a thread):**
```
Para quem quiser ver o código antes de testar:
github.com/enioxt/egos/tree/main/packages/guard-brasil

Tudo MIT. Inclusive os 15 padrões e os testes.
```

---

### 4.3 LinkedIn Posts

#### Post Principal (PART-002 — produto)

**Headline:** Construímos a API de detecção de dados pessoais mais rápida do Brasil — open source

```
Nos últimos 3 meses construímos o Guard Brasil: uma API que detecta e classifica dados pessoais brasileiros (CPF, RG, CNPJ, cartão de crédito e mais 11 padrões) em menos de 5 milissegundos.

Por que isso importa:
A LGPD exige que empresas identifiquem, classifiquem e protejam dados pessoais antes de armazenar ou processar. Hoje, a maioria usa soluções genéricas que não conhecem o formato brasileiro.

O que fizemos diferente:
→ 15 padrões validados com dígito verificador real (não só regex)
→ Classificação automática de risco LGPD (BAIXO / MÉDIO / ALTO)
→ Resposta em 4ms (média em produção)
→ Free tier de 500 chamadas/mês sem cartão
→ SDK open source no npm (@egosbr/guard-brasil)

Casos de uso:
• Sanitização antes de armazenar em banco de dados
• Validação em pipelines de CI/CD
• Auditoria de logs e arquivos
• Conformidade em LLMs que processam dados BR

Está no ar: guard.egos.ia.br

Se sua empresa lida com dados de usuários brasileiros e não tem uma solução de PII detection, seria ótimo conversar.

#LGPD #PrivacidadeDeDados #OpenSource #API #Brasil #Compliance
```

#### Post Co-founder/Parceiro (PART-003 companion — LinkedIn long-form)

> Postar no mesmo dia da thread X.com, 2 horas depois. Audiência diferente — formato longo funciona melhor no LinkedIn.

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

---

### 4.4 Posting Mechanics + Pre-flight Checklist + FAQ

#### Quando postar

- **Melhor dia/hora:** Terça ou Quarta, 09:00 BRT (= 12:00 UTC)
- Audiência BR no pico antes do almoço
- Evitar: fins de semana (engajamento baixo), noite (se perde no ruído)
- LinkedIn: mesmo dia, 2 horas depois da thread X.com

#### Pre-flight checklist (obrigatório antes de postar)

- [ ] og-image.png deployada em guard.egos.ia.br/og-image.png (GTM-015 feito)
- [ ] guard.egos.ia.br/v1/inspect responde em <10ms (testar 5x)
- [ ] github.com/enioxt/egos é público e README menciona Guard Brasil prominentemente
- [ ] enioxt@gmail.com monitorado (notificações ativas)
- [ ] X DMs abertos para não-seguidores
- [ ] Perfil LinkedIn atualizado com headline "Founder, Guard Brasil"
- [ ] Primeiro reply da thread agendado (você responde primeiro → semeia engajamento)
- [ ] 2h bloqueadas no calendário do dia de postagem para replies + DMs
- [ ] enioxt@gmail.com inbox ≤10 unread

#### DO NOT POST até que (condições PART-003)

1. Enio leu a thread completa e aprovou cada tweet
2. og-image.png deployada em guard.egos.ia.br/og-image.png
3. Página de preços (guard.egos.ia.br/pricing) mostra tiers OU thread não menciona pricing
4. Calendar bloqueado com 2h para respostas no dia de postagem

#### O que fazer nas primeiras horas após postagem

**Hora 0-1 (janela crítica):**
- Ficar na frente da thread
- Responder cada reply em até 5 minutos
- Like + RT cada resposta significativa
- NÃO auto-responder — cada reply é uma pessoa

**Hora 1-24:**
- 1 quote-tweet da thread com um insight de follow-up
- Reply para quem compartilhou a thread com agradecimento

**Dias 2-7:**
- Checar métricas de engajamento (impressões, cliques de perfil, DMs, signups)
- Trackear em `docs/business/launch_thread_metrics.md`
- Para cada DM sobre co-fundador: agendar call de 30min em 48h

#### Métricas de sucesso realistas

- Tweet 1 impressões: 5k–15k (bom para founder sem clientes)
- Replies: 10–30
- Free tier signups (se mensuráveis): 5–20
- Co-founder DMs: 1–5 (1 sério conta como sucesso)
- LinkedIn post engajamentos: 50–200

#### FAQ — respostas preparadas (ter no Notes antes de postar)

| Pergunta provável | Resposta pronta |
|---|---|
| "Como vocês comparam com Presidio?" | Presidio é Microsoft, foco global, 0 padrões BR. A gente: 15 patterns BR, dígitos verificadores reais, free tier sem cadastro. Trade-off: Presidio tem mais maturidade global, a gente tem foco brasileiro. |
| "Onde fica hospedado?" | VPS Hetzner Falkenstein, 100% BR-aware. Latência média 4ms BR-EU, vamos colocar réplica BR em Q3. |
| "Fonte do código?" | github.com/enioxt/egos — monorepo, packages/guard-brasil. |
| "Como funciona o free tier?" | 500 chamadas/mês sem cadastro, depois R$ X/mês para 10k+. Sem credit card upfront. |
| "É só regex?" | Não. Validação de dígito verificador (CPF/CNPJ algo), classificação de risco contextual, detecção de máscaras (123.***.789-00). Mas sim, regex é parte. O valor está mais no contexto e responsabilidade legal do que no regex puro. |
| "ANPD aprovou?" | ANPD não aprova ferramentas, só regula uso. Vamos submeter ao registro público quando abrir. |
| "Quanto custa?" | Free tier: 500 chamadas/mês. Outros tiers em design (Starter ~R$99/mês, Pro ~R$497/mês, Enterprise custom) — não estão no ar. Quem quiser contratar agora vira parceiro piloto com pricing custom. |
| "Preciso de DPO certificado pra usar?" | Não. Mas recomendamos. Posso indicar DPOs parceiros se precisar. |
| "Vocês têm SLA?" | Hoje, NÃO. Open source em desenvolvimento ativo, sem contrato formal. Meta para Enterprise (quando lançar) é 99.9% uptime + 24h response — ainda é rascunho. Free tier é best-effort. Quem precisa de SLA hoje, melhor esperar 2-3 meses ou conversar sobre parceria piloto. |
| "Como ser sócio?" | Manda DM ou email enioxt@gmail.com com 3 linhas: quem você é, o que faz hoje, por que essa oportunidade. Marco call de 30min na semana seguinte. |

#### Modo de falha

- 0 DMs em 48h → thread não aterrizou
- Recuperação: postar thread de follow-up na próxima semana com ângulo diferente (ex: "Como eu construí isso" — deep dive técnico)

---

## 5. OUTREACH — M-007 (Email)

> **STALE: 7+ dias.** Ação imediata necessária. Estes templates estão prontos para envio — só personalizar [Nome] e [Empresa].

### 5.1 Lista de targets + status

| Segmento | Empresas alvo | Template | Status |
|----------|--------------|----------|--------|
| SaaS com IA | Nuvemshop, RD Station, Pipefy | #2 Pain Point | [ ] não enviado |
| Fintechs | Nubank, PicPay, Stone | #1 Cold Intro | [ ] não enviado |
| Healthtech | Dr. Consulta, Memed, iClinic | #3 Regulatório | [ ] não enviado |
| Devtools | Rocketseat, Alura, Cubos | #4 Developer | [ ] não enviado |
| Compliance SaaS | OneTrust BR, DPOnet, LGPD Brasil | #5 Parceria | [ ] não enviado |
| Govtech CTOs | Pref. BH, TCE-MG, MP-MG, PCMG | #1 Pain Point (M-007 strategy) | [ ] não enviado |

**Métricas de sucesso para M-007:**
- Enviados: 5 emails
- Abertura: >40% (govtech avg: 25%)
- Taxa de resposta: >20% (govtech avg: 5-10%)
- Conversões para demo: 4+ demos agendados
- Ciclo de negócio: 7-14 dias para LOI

**Impacto financeiro:**
- 1 cliente × R$49/mês = R$49/mês
- 5 clientes × R$199/mês = R$995/mês (meta: R$500+/mês)

---

### 5.2 Email Templates

#### Template 1: Cold Intro — Compliance Officer / DPO

**Para:** Responsável LGPD de empresas SaaS BR
**Subject:** Proteção de dados brasileiros em 4 linhas de código

```
Olá [Nome],

Vi que a [Empresa] processa dados de clientes brasileiros. Uma pergunta rápida: como vocês mascaram CPFs e CNPJs antes de enviar para seus modelos de IA?

Criamos o Guard Brasil — uma API que detecta e mascara 15 tipos de PII brasileiro (CPF, CNPJ, RG, CNH, etc.) em tempo real. Uma chamada REST, 4ms de latência, compliance LGPD automático.

Funciona assim:
curl -X POST guard.egos.ia.br/v1/inspect \
  -H "Authorization: Bearer SUA_CHAVE" \
  -d '{"text": "O CPF 123.456.789-00 do João..."}'

Resposta: texto mascarado + relatório de compliance + receipt hash.

500 chamadas/mês grátis. Posso gerar uma chave de teste para vocês agora?

— Enio Rocha | EGOS | guard.egos.ia.br
```

---

#### Template 2: Pain Point — Startup que usa IA

**Para:** CTO/tech lead de startups que integram LLMs
**Subject:** Seus prompts vazam CPFs para a OpenAI?

```
[Nome],

Se vocês mandam texto de usuários brasileiros para qualquer LLM (ChatGPT, Claude, Gemini), provavelmente estão enviando CPFs, RGs e telefones sem saber.

O Guard Brasil resolve isso em uma chamada de API:
- Detecta 15 tipos de PII brasileiro automaticamente
- Mascara antes de enviar ao LLM
- Devolve o texto limpo + receipt de compliance
- R$0.007/chamada (500 grátis/mês)

Já estamos live em produção: guard.egos.ia.br/v1/meta

Quer testar com dados reais do seu produto? Gero uma key em 10 segundos.

— Enio Rocha | guard.egos.ia.br
```

---

#### Template 3: Regulatório — Empresa grande

**Para:** Head of Legal / Compliance de empresas enterprise
**Subject:** LGPD + IA: como garantir compliance automático nas APIs

```
Prezado(a) [Nome],

Com a ANPD intensificando fiscalizações em 2026, empresas que processam dados pessoais via IA precisam comprovar que mascaramento ocorre ANTES do processamento.

O Guard Brasil é uma camada de segurança que se integra entre seu sistema e qualquer API de IA:

- 15 padrões PII brasileiros detectados (CPF, CNPJ, RG, CNH, SUS, NIS, CEP, placas...)
- Receipt com hash SHA-256 — prova auditável de compliance por chamada
- Validação ética ATRiAN — scoring de conteúdo sensível (0-100)
- SLA enterprise: <5ms latência, 99.9% uptime

Preços sob demanda: R$0.002/chamada no volume enterprise.
Documentação completa: guard.egos.ia.br/openapi.json

Podemos agendar 15 min para demonstração?

— Enio Rocha | EGOS | guard.egos.ia.br
```

---

#### Template 4: Developer Evangelist — Comunidade dev

**Para:** Devs influentes, tech bloggers, community leads
**Subject:** Open source: detecção de PII brasileiro em tempo real

```
Ei [Nome],

Lancei o @egosbr/guard-brasil no npm — detecção de PII brasileiro com 85.3% F1 score (melhor que Presidio para dados BR).

npm install @egosbr/guard-brasil

15 padrões: CPF, CNPJ, RG, CNH, SUS, NIS, CEP, placas, processos judiciais...

API REST grátis (500/mês): guard.egos.ia.br
OpenAPI spec: guard.egos.ia.br/openapi.json
npm: npmjs.com/package/@egosbr/guard-brasil

Se você escrever/publicar sobre proteção de dados em IA, posso dar acesso Pro ilimitado em troca de um review honesto.

— Enio | @anoineim
```

---

#### Template 5: Integração — Parceiro SaaS

**Para:** Founders de SaaS BR que já vendem compliance/security
**Subject:** Parceria: Guard Brasil como módulo white-label

```
Olá [Nome],

Percebi que a [Empresa] já atende clientes brasileiros com [solução de compliance/security]. Temos uma API de detecção de PII brasileiro que pode complementar o produto de vocês:

Proposta: Integrar o Guard Brasil como módulo dentro do [Produto]:
- Vocês ganham feature de mascaramento LGPD sem build interno
- Nós ganhamos distribuição via sua base de clientes
- Revenue share: 30% da receita gerada por clientes indicados

Stack técnica: REST API, <5ms, 15 padrões BR, receipt com hash.
API doc: guard.egos.ia.br/openapi.json

Vale uma call de 15 min esta semana?

— Enio Rocha | EGOS | guard.egos.ia.br
```

---

#### Templates M-007 Strategy (foco govtech)

#### M-007/Template-A: Govtech — LGPD Compliance Pain Point

**Para:** CTOs de govtech (municípios, TCEs, MPs, agências federais)
**Subject:** [GUARDBRASIL] LGPD compliance check-up for [ORGAO_NAME] — real case inside

```
Oi [CTO_NAME],

Quick context: many Brazilian AI workflows still let citizen PII reach logs, reports and model prompts without a dedicated masking layer.

LGPD raises the bar for accountability when personal data is processed in these systems.

We built Guard Brasil specifically for this. It:
- Detects Brazilian PII in real time (CPF, RG, MASP, placa, processo, REDS, email, phone)
- Masks sensitive identifiers before output leaves the app
- Adds ethical review signals through ATRiAN for high-stakes text
- Preserves an auditable trail for inspection and compliance review

Fast validation path:
1. Share a sample text flow you already process
2. We run a guided inspection live or send a curl example
3. You validate output, latency and masking policy with your team

Free local SDK for evaluation. Hosted API plans start at R$49/mês.

Next step: 15-min demo call where we test on a real sample from your environment.

Available for a quick call this week?

[Your name]
Founder, Guard Brasil
[your-email]
[link: calendly.com/guardbrasil/demo]
```

---

#### M-007/Template-B: Govtech — Ethical AI / Bias Detection

**Para:** Juízes, MPs, tomadores de decisão sobre AI pública
**Subject:** Guard Brasil + ATRiAN: Stop algorithmic bias before it harms citizens

```
Oi [DECISION_MAKER_NAME],

Your institution recently made [automated decision type]. Did you validate that the reasoning and output are reviewable before they reach citizens or operators?

Common risk factors in AI-assisted decisions include:
- Proxy variables hidden in names, addresses, geography or socioeconomic markers
- Outputs that sound certain without sufficient evidence
- No audit trail showing what was masked, flagged or escalated

Guard Brasil + ATRiAN helps review this before production. Every output can be scored, flagged and routed for human review.

For [ORGAO], this means:
✅ Defensible decisions (audit trail + ATRiAN review signals)
✅ Better review posture for high-risk automated flows
✅ Clearer documentation for compliance and governance teams

The test: Send us anonymized sample outputs or rules. We'll run ATRiAN analysis and show where review gates should exist.

Want a free bias and governance review of your flow?

[Your name]
Founder, Guard Brasil
[your-email]
[link: calendly.com/guardbrasil/audit]
```

---

#### M-007/Template-C: Govtech — Custo / Eficiência

**Para:** CFOs / Tech leads com orçamento restrito
**Subject:** LGPD compliance tool — costs R$ 0 to start

```
Oi [CFO/TECH_LEAD_NAME],

Compliance tools are expensive. Most LGPD solutions:
- AWS CloudDLP: R$ 2-5k/month setup + overages
- Protecto: EUR 3k+/year minimum
- Open source: Free but requires 2-3 engineers for 6 months (cost: R$ 300k+)

Guard Brasil flips the model:
- Free SDK: R$ 0/month for local evaluation
- Starter: R$ 49/month (10k calls)
- Pro: R$ 199/month (100k calls)
- Business: R$ 499/month (500k calls, expanded support)

For [ORGAO]:
- Pilot cost: local evaluation or a small hosted pilot
- Prod cost: probably R$49-199/mês depending on scale
- Savings vs enterprise-only vendors: significant for early rollout

Want to run a pilot this week?

[Your name]
Founder, Guard Brasil
[your-email]
[link: calendly.com/guardbrasil/pilot]
```

---

#### M-007/Template-D: DevOps/SRE — CI/CD Integration

**Para:** Times DevOps/SRE
**Subject:** 4ms PII detection for your CI/CD pipeline — no latency hit

```
Oi [DEVOPS/SRE_NAME],

You're probably scanning secrets in CI/CD (good!). But you're NOT catching PII leaks in logs, configs, or API responses.

Common case: Developer logs a citizen's CPF for debugging → log aggregator stores it → LGPD audit finds it → R$ 100k+ fine.

Guard Brasil integrates 2 ways:

1. Inline (low latency): Add 1 line to your code
   const result = guard.inspect(userData);
   Latency hit: low enough for interactive flows

2. Hosted inspection API: Send text to a managed endpoint when you want auth, rate limits and shared usage

For [ORGAO]:
- Drop-in npm package: npm install @egosbr/guard-brasil
- REST API: POST to https://guard.egos.ia.br/v1/inspect
- Reference server: Bun/TypeScript, self-hostable
- MCP surface: guard_inspect, guard_scan_pii, guard_check_safe

Want a 30-min integration walkthrough?

[Your name]
Founder, Guard Brasil
[your-email]
[link: calendly.com/guardbrasil/integration]
```

---

#### M-007/Template-E: Vision + Partnership

**Para:** Líderes institucionais / Strategic leaders
**Subject:** Let's build Brazilian data protection infrastructure together

```
Oi [INSTITUTIONAL_LEADER_NAME],

LGPD created a compliance market in Brazil. But the tooling is still North American (AWS, Google, Cloak).

Brazil deserves a Brazilian solution.

Guard Brasil is:
- Built by Brazilians, for Brazilian data (CPF/RG/MASP)
- Open-source core (transparency)
- Pay-what-you-use (no vendor lock-in)
- Ethical by design (ATRiAN ethical validation)

Our ask: Partner with us to validate that Guard Brasil fits your compliance needs. We'll:
1. Run a free audit of your current PII exposure
2. Design a custom deployment (API/package/webhook)
3. Create a case study (you're the first [SECTOR] deployment in Brazil)

What we need from you: 2 hours of your team's time + access to 1 non-production environment.

This is a chance to:
✅ Solve your compliance problem
✅ Help shape Brazilian data protection standards
✅ Be the reference deployment for your sector

Interested in exploring this?

[Your name]
Founder, Guard Brasil
[your-email]
[link: calendly.com/guardbrasil/partnership]
```

---

### 5.3 Guia de Deployment para Prospects

**Caminho mais rápido para testar o Guard Brasil:**

**Opção A: Local SDK evaluation (5 minutos)**
1. Instalar `@egosbr/guard-brasil`
2. Rodar inspeção local contra texto de amostra
3. Revisar output mascarado e ATRiAN score

**Opção B: API Testing (30 minutos)**
1. Obter uma test key
2. Chamar endpoint:
```bash
curl -X POST https://guard.egos.ia.br/v1/inspect \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "CPF 123.456.789-00 foi aprovado"}'
```
3. Resposta esperada:
```json
{
  "safe": false,
  "blocked": false,
  "output": "[CONTEÚDO PROTEGIDO]",
  "atrian": { "passed": true, "score": 100, "violationCount": 0 },
  "masking": { "sensitivityLevel": "critical", "findingCount": 1 },
  "meta": { "durationMs": 4 }
}
```

**Opção C: Production Deployment (2-4 dias)**
1. SDK local ou hosted API
2. Policy review pelo time
3. Definição de logging / retenção de evidências
4. Policy packs setoriais opcionais

---

## 6. PARTNER TARGETS

### 6.1 Marketplaces / App Stores (Tipo A — baixo atrito, alto alcance)

**Ordem recomendada de execução:**
1. Stripe Verified Partners (grátis, rápido, sinal de confiança) — HOJE
2. Nuvemshop (BR-específico, barreira baixa) — semana 1
3. VTEX (BR enterprise) — mês 2
4. Stripe Apps (após construir extensão de UI) — mês 2-3

| Parceiro | O que distribuem | Audiência | Como entrar | Prioridade |
|---|---|---|---|---|
| **Stripe Verified Partners** | Compliance/security service providers | 100k+ devs/founders globais, forte presença BR | Free application, caminho mais rápido | **P0** |
| **Stripe Apps Marketplace** | Dashboard widgets Stripe | Mesma audiência | Build extensão UI + submissão (listing em inglês; sem "Stripe"/"app"/"free"/"paid" no nome — "Guard Brasil" passa) | P0 |
| **AWS Marketplace** | Enterprise BR usa AWS | Enterprise com SaaS contract | aws.amazon.com/marketplace/sell | P0 |
| **DPOnet** | Líder BR em software LGPD | 2.500+ clientes | Email DPO/partnership | P1 |
| **Nuvemshop App Store** | E-commerce add-ons BR-native | 110k+ lojas BR | Partner portal + listing PT-BR OK | P1 |
| **VTEX App Store** | Enterprise e-commerce extensions | Grandes varejistas BR (Decathlon, Walmart BR) | Barra mais alta (review + tech); revenue share | P2 |
| **RD Station Marketplace** | Marketing automation + data integrations | 30k+ SMBs BR | App listing no diretório de integrações | P2 |
| **GitHub Marketplace** | Developer tools / actions | Devs globais | Free listing para projetos OSS | P2 |
| **ProductHunt** | Tech launches | International reach | Launch terça ou quarta (pico de tráfego) | P2 |
| **OneTrust BR** | Global compliance SaaS | Enterprise | LinkedIn + partnership form | P1 |
| **LGPD Brasil** | Consultoria + software | Base SMB | Cold email + parceria API | P1 |

---

### 6.2 Channel Partners — Fintechs que vendem para fintechs (Tipo B)

> Empresas com times de vendas que já falam com nosso ICP diariamente. Parceria = revenue share + acesso.

| Empresa | Produtos | Por que parceria | Contato |
|---|---|---|---|
| **Privacy Tools BR** | DPO management software | **#1 prioridade.** Eles têm os DPOs. Falta API de runtime PII detection. Parceria complementar perfeita. | https://www.privacytools.com.br — sales@privacytools.com.br; founder Frederico Boldori no LinkedIn |
| **OneTrust BR** | Enterprise compliance suite | Time BR precisa de ferramentas SMB para indicar — somos esse referral | https://www.onetrust.com/pt/ |
| **iManage BR** | Document compliance legal/financial | Vende para law firms e compliance teams; PII detection complementa | https://imanage.com/ |
| **Bitwise / Compliance Online** | Compliance training + audit consultancy | Vendem treinamento; podemos ser "a ferramenta que recomendamos no treinamento" | https://www.complianceonline.com.br |
| **LGPD Brasil** | Certificação + consultoria LGPD | Aliado natural — foco puro em LGPD | https://www.lgpdbrasil.com.br |

**Ação:** Cold email cada um com "construímos X, vocês têm Y, vamos explorar referral ou integração".

---

### 6.3 Enterprise Integrators (Tipo B premium)

> Revendem ou implementam compliance tooling para enterprises. Marcam up nossa API e embalam com serviços de implementação.

| Integrador | Especialidade | Interesse provável | Prioridade |
|---|---|---|---|
| **Totvs** | ERP líder BR, 40k+ clientes, LGPD mandatório | Totvs Partner Program + pitch técnico | P1 |
| **SENIOR Sistemas** | RH/DP/Fiscal BR, dados pessoais em volume | Contato via Ecosystem Senior | P1 |
| **Stefanini** | Enterprise IT services BR | LinkedIn + RFP submission | P1 |
| **CI&T** | Dev shop BR, constrói apps com dados pessoais | LinkedIn → partnerships | P2 |
| **TIVIT** | Cloud + compliance | LinkedIn → partnerships | P2 |
| **Squadra** | Healthtech-focused integrator | Healthtech LGPD é espaço quente | P2 |
| **Indra** | Government/finance integrator | Alto risco LGPD em contratos gov | P2 |
| **Accenture BR (LGPD practice)** | Prática de privacidade | LinkedIn → LGPD lead | P2 |
| **Deloitte BR (Risk Advisory)** | Audita compliance LGPD enterprise | Contato via Risk Advisory | P2 |

**Ação:** LinkedIn outreach para especialistas em "data privacy" ou "LGPD" em cada uma. Pitch: "economizamos 200h de código de compliance por projeto."

---

### 6.4 Technical Integrations (Tipo C — ecossistema)

| Plataforma | Usuários | Como integrar | Prioridade |
|---|---|---|---|
| **LangChain** | 100k+ devs AI | npm @egosbr/guard-brasil-langchain + PR | P1 |
| **Bubble.io** | 3M+ usuários no-code | Plugin marketplace submission | P1 |
| **Make.com** | 500k+ automações | App submission (REST-based) | P1 |
| **Zapier** | 6M+ usuários | Zapier Partner Program | P2 |
| **n8n** | Self-hosted, popular devs BR | Node community submission | P2 |
| **Dify.ai** | AI app builder crescendo | Plugin submission | P2 |
| **Stack AI** | AI workflows no-code | API integration | P3 |

---

### 6.5 Comunidades + Influenciadores (Tipo D — distribuição orgânica)

| Canal / Pessoa | Tipo | Alcance | Ação |
|---|---|---|---|
| **ANPPD** | Associação profissional de DPOs BR | ~3000 membros | https://www.anppd.org.br — candidatar para falar em eventos |
| **IAPP — BR chapter** | Certificação DPO global | 50k+ DPOs, ~2000 BR | KnowledgeNet meetups, ANPD speakers |
| **DPO Brasil meetups** | Meetups mensais/trimestrais SP/RJ/BH | 100-300 por evento | LinkedIn search "DPO meetup brasil", aplicar para sponsor ou palestra |
| **Patricia Peck Pinheiro** | A LGPD lawyer mais conhecida BR | Books, cursos, keynotes | Free Pro em troca de review honesto |
| **Renato Opice Blum** | Membro fundador grupos enforcement LGPD | Fala em todo evento | Free Pro em troca de review |
| **Akita** | Tech YouTuber BR, cobre LGPD prática | 200k+ subs | Free Pro em troca de review |
| **Filipe Deschamps** | Dev YouTuber BR, cobre compliance | 1.4M subs | Free Pro em troca de review |
| **Lucas Persona** | Indie hacker BR, builds in public | Engineer-founder demographic | Free Pro em troca de review |
| **Codecasts (Diego Fernandes)** | BR dev course creator (Rocketseat) | Todo junior backend dev BR | Parceria de conteúdo |
| **Tabnews / dev.to BR / Reddit r/brdev** | Dev communities | 200k+ | Tutoriais LGPD com exemplos Guard Brasil |
| **Telegram: "DPO Brasil" group** | DPO chat group | ~500 DPOs ativos | Participar, contribuir, mencionar ocasionalmente |

**Script de outreach para influenciadores:**
> "Construímos uma ferramenta open source de LGPD. Estamos dando Pro grátis para criadores de conteúdo de DPO em troca de um review honesto. Sem compromisso. Quer uma demo?"

---

### 6.6 Canais Governamentais / Regulatórios

| Org | O que fazem | Como entrar |
|---|---|---|
| **ANPD** | Autoridade de enforcement LGPD | Submeter Guard Brasil nas consultas públicas + registro de ferramentas quando abrir |
| **CGI.br** | Governança da internet BR | Working groups sobre proteção de dados |
| **SERPRO** | Serviço federal de processamento de dados | Procurement para LGPD tooling governamental |
| **TCU** | Tribunal de Contas da União | Padrões de auditoria de compliance |

---

### 6.7 Modelos de Parceria

**White-label API:**
```
Parceiro vende "LGPD Shield powered by GuardTech" (ou nome deles)
Nós: infraestrutura + manutenção
Eles: vendas + suporte cliente
Revenue split: 70% nós / 30% parceiro (ou negociável por volume)
SLA: <5ms P95, 99.9% uptime, ANPD-ready receipts
```

**Revenue Share — Referral:**
```
Parceiro indica clientes → link rastreável
Nós pagamos: 20% MRR por 12 meses por cliente indicado
Mínimo: R$0 para começar, sem contrato de exclusividade
```

**OEM / Embed:**
```
Parceiro incorpora Guard Brasil no produto (ex: Totvs, Senior)
Pricing: volume por chamada com desconto (R$0.001–0.003/call)
Contrato mínimo: 100k chamadas/mês
Suporte: SLA enterprise + canal dedicado
```

**Co-desenvolvimento (Tipo B premium):**
```
Parceiro financia feature específica (ex: validação de Passaporte, integração SAP)
Nós desenvolvemos + damos exclusividade por 6 meses
Preço: custo de desenvolvimento + 30% sobre receita gerada pela feature
```

---

### 6.8 O que falta para enterprise-grade

**Gaps técnicos** (resolver antes de abordar Totvs/Deloitte):
- [ ] SLA formal — documento com uptime guarantee, RTO/RPO, incident response (PART-009)
- [ ] SOC2 readiness — checklist Vanta/Secureframe (PART-010)
- [ ] Security questionnaire — template padrão procurement enterprise (PART-012)
- [ ] Enterprise pricing page — contratos custom, volume, suporte dedicado (PART-011)
- [ ] Status page — status.guard.egos.ia.br (Instatus ou Betteruptime, grátis)
- [ ] DPA template — Data Processing Agreement para LGPD/GDPR

**Gaps de presença** (resolver antes de abordar distribuidores):
- [ ] ProductHunt launch — precisa de 30-50 upvotes nas primeiras horas
- [ ] LinkedIn empresa — EGOS / Guard Brasil page com 100+ seguidores
- [ ] Case study — 1 cliente real usando Guard Brasil em produção
- [ ] Benchmark público — blog post com metodologia F1 score vs Presidio vs re:patterns

---

## 7. CONTENT CALENDAR

> Ordenado por prioridade, dependências anotadas.

| Dia | Ação | Canal | Esforço | Dependência |
|-----|------|-------|---------|-------------|
| **Imediato** | Enviar 5 emails M-007 | Email | 1h | Nenhuma — templates prontos |
| **Hoje** | Stripe Verified Partner application | Form | 30min | Nenhuma |
| **Hoje/amanhã** | Gerar og-image.png (GTM-015) | Playwright/script | 1h | Nenhuma |
| **Dia 1 (após og-image)** | Postar X.com thread principal (§4.1) | X.com | 30min + 2h replies | og-image.png deployada |
| **Dia 1 +2h** | Postar LinkedIn post principal (§4.3) | LinkedIn | 15min | Nenhuma (postar manualmente) |
| **Dia 2** | LinkedIn DM para Privacy Tools BR (Frederico Boldori) | LinkedIn | 15min | Nenhuma |
| **Dia 2** | Construir scripts/x-post.ts (GTM-014) | Código | 2h | Nenhuma |
| **Dia 3** | Cold email para 3 consultores DPO (programa de endorsement) | Email | 1h | Nenhuma |
| **Dia 4** | Postar X.com thread co-fundador/equity (§4.2) | X.com | 30min + 2h replies | og-image.png deployada |
| **Dia 4** | Postar LinkedIn long-form co-fundador (§4.3) | LinkedIn | 15min | Nenhuma |
| **Dia 5** | Aplicar ao ANPPD individual membership | Form | 15min | Nenhuma |
| **Semana 1** | Submit Nuvemshop app | Form | 1h | Nenhuma |
| **Semana 2** | ProductHunt — preparar assets, agendar launch | PH | 2h | Case study ou user |
| **Semana 2** | AWS Marketplace — iniciar cadastro de seller | AWS | 1h | Nenhuma |
| **Semana 3** | Cold email 5 integradores (CI&T, Stefanini, etc.) | Email | 2h | Nenhuma |
| **Semana 4** | Falar em DPO meetup (aplicar na semana 2) | In-person/online | 4h prep | ANPPD membership |
| **Mês 2** | Contato LangChain via GitHub PR | GitHub | 1h | npm package atualizado |
| **Mês 2** | VTEX e Stripe Apps submissions | Forms | 3h | UI extension construída |

**Regra:** não tente fazer as 30 coisas. Faça **5 bem feitas nos primeiros 7 dias** e deixe as respostas guiar os próximos 23.

---

## 8. SUCCESS METRICS

### Pitch de 30 segundos

> "Toda empresa brasileira que usa IA processa CPFs, CNPJs e dados pessoais de clientes. O Guard Brasil é uma API que detecta e mascara 15 tipos de PII brasileiro em tempo real — antes que esses dados cheguem ao ChatGPT, Claude ou qualquer LLM. Uma linha de código, 4ms de latência, receipt SHA-256 para cada inspeção. Compliance LGPD automático. 500 chamadas grátis para testar agora."

**Para enterprise:** "Cada inspeção gera um receipt imutável com hash SHA-256 — prova auditável que o mascaramento ocorreu. Isso é o que a ANPD pede em fiscalizações."

**Para parceiros técnicos:** "npm install @egosbr/guard-brasil — open source core, API enterprise, 85.3% F1 score, melhor que Microsoft Presidio para dados brasileiros."

### O que NÃO dizer (evitar — soam falso)

- ❌ "Production-ready, enterprise-grade" (ainda não)
- ❌ "Trusted by leading fintechs" (zero clientes)
- ❌ "$10M ARR potential" (não especular)
- ❌ "AI-powered" (é regex + check digits, majoritariamente)
- ❌ "Solves all your LGPD needs" (resolve runtime PII detection — uma peça)

### O que DIZER (credível)

- ✅ "15 padrões BR, validados com check digits, 4ms p95 — verificável: testa agora"
- ✅ "Free tier, sem cartão — seu time de dev prova que funciona em 5 minutos"
- ✅ "Open source — seu time de segurança pode auditar o código hoje"
- ✅ "Construído por um dev ativo no BR que responde em 24h"
- ✅ "Fazemos tech, procuramos quem faça mercado — split justo"

### KPIs por canal (30 dias)

| Canal | Baseline | Meta 30d | Tracking |
|-------|---------|----------|----------|
| MRR | R$0 | R$500 | Supabase billing |
| Clientes pagantes | 0 | 5 | Stripe |
| M-007 emails enviados | 0 | 5 | Manual |
| M-007 taxa de resposta | — | >20% | Manual |
| npm downloads/semana | ~10 | 100 | npmjs.com |
| GitHub stars | ? | 50 | GitHub |
| X.com thread impressões | 0 | 5k–15k | X Analytics |
| LinkedIn engajamentos | 0 | 50–200 | LinkedIn Analytics |
| Co-founder DMs | 0 | 1 (sério) | Inbox |
| Free tier signups | 0 | 5–20 | Supabase |
| Parceiros ativos | 0 | 1 (Stripe) | Manual |
| Demos agendadas | 0 | 4 | Calendly |

---

## Referências internas

- `apps/guard-brasil-web/app/landing/page.tsx` — landing pública guard.egos.ia.br/landing
- `apps/guard-brasil-web/` — web app completa
- `packages/guard-brasil/` — SDK npm core (open source)
- `agents/x-reply-bot/` — OAuth1.0a reutilizável para scripts/x-post.ts
- TASKS.md — tasks GTM-*, PART-*, M-007 com checkboxes
- `docs/strategy/GUARD_BRASIL_WEBSITE_CRITIQUE.md` — 14 melhorias identificadas
- `docs/strategy/GUARD_BRASIL_1PAGER.md` — 1-pager para parceiros

---

*Gerado em: 2026-04-06 | EGOS P28 | Consolida: PART002, PART003, OUTREACH_EMAIL_TEMPLATES, M007_OUTREACH_STRATEGY_EMAILS, PARTNERSHIP_STRATEGY, DISTRIBUTION_PARTNERS_BR*
