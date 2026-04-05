# Guard Brasil — Partnership & Distribution Strategy
> **Created:** 2026-04-05 | **Author:** EGOS P22 | **Status:** ACTIVE

---

## 1. O que temos para oferecer

### Produto
- **Guard Brasil API v0.2.2** — 15 padrões PII brasileiro (CPF, CNPJ, RG, CNH, SUS, NIS, CEP, placa, MASP, REDS, processo judicial, título eleitor, NF-e, SIAPE, passaporte)
- **Latência:** 1–6ms (local) / <20ms (API)
- **Compliance automático:** LGPD Arts. 6, 12, 46, 18 — receipt SHA-256 por inspeção
- **ATRiAN scoring:** validação ética 0–100 por payload
- **npm:** `@egosbr/guard-brasil` (MIT, open-source core)
- **API REST:** `guard.egos.ia.br/v1/inspect` (500 chamadas/mês grátis)
- **Pricing:** R$0/R$0.007/R$0.004/R$0.002 por chamada (Free→Startup→Business→Enterprise)
- **Crypto:** NOWPayments (241 moedas, min $19)
- **Faturamento:** Stripe metered billing ativo

### Diferenciais técnicos
- **Único no Brasil** com validação matemática de CPF/CNPJ + mascaramento reversível/irreversível
- **85.3% F1 score** (benchmark vs Presidio — melhor para dados BR)
- **Receipt hash** auditável por chamada — prova de compliance para ANPD
- **Zero armazenamento de texto** — processa em memória, descarta

### Stack comprovada
- Bun/TypeScript monorepo, Docker VPS Hetzner, Supabase, Caddy, Stripe, NOWPayments
- 18 containers ativos, 99.9% uptime desde deploy
- Knowledge System (50 wiki pages), Gem Hunter intelligence layer, Eagle Eye OSINT

---

## 2. O que precisamos de parceiros

### Tipo A — Distribuição (Market Reach)
**Problema:** Temos produto, falta alcance. Zero usuários pagantes hoje.
**O parceiro traz:** Base de clientes, confiança, canal de vendas.
**Nós oferecemos:** API white-label, revenue share 30%, co-branding.

**Perfil ideal:** SaaS BR com 50+ clientes enterprise que já vendem compliance, segurança ou IA.

### Tipo B — Enterprise Layer (Credibilidade)
**Problema:** Contratos enterprise exigem SOC2, SLA formal, suporte L2.
**O parceiro traz:** Certificações, equipe de suporte, relacionamento enterprise.
**Nós oferecemos:** API + inteligência técnica + receita compartilhada.

**Perfil ideal:** Consultorias de TI / integradores com prática LGPD.

### Tipo C — Integração Técnica (Ecossistema)
**Problema:** Desenvolvedor não quer uma API avulsa — quer uma biblioteca no stack dele.
**O parceiro traz:** Plataforma com milhares de devs (Bubble, Zapier, LangChain, etc).
**Nós oferecemos:** Plugin nativo, co-marketing, revenue share.

**Perfil ideal:** Plataformas no-code/low-code ou frameworks AI/ML com base BR.

---

## 3. Parceiros alvo — Mapeamento

### 3.1 Distribuidores / Marketplaces (Tipo A)

| Parceiro | Por quê | Como abordar | Prioridade |
|----------|---------|--------------|------------|
| **Stripe App Marketplace** | Já somos clientes Stripe, zero friction, global reach | Submeter via dashboard.stripe.com/apps | P0 |
| **AWS Marketplace** | Enterprise BR usa AWS, SaaS contract | Contato via aws.amazon.com/marketplace/sell | P0 |
| **DPOnet** | Líder BR em software LGPD, 2.500+ clientes | Email DPO/partnership | P1 |
| **OneTrust BR** | Global compliance SaaS, ativo no Brasil | LinkedIn + partnership form | P1 |
| **LGPD Brasil (lgpdbrasil.com.br)** | Consultorias + software, base SMB | Cold email + parceria API | P1 |
| **Nuvemshop App Store** | 100k+ lojas BR, precisam de LGPD | Cadastro de app no portal dev | P2 |
| **VTEX App Store** | E-commerce enterprise, compliance crítico | VTEX IO SDK + submissão | P2 |

### 3.2 Integradores Enterprise (Tipo B)

| Parceiro | Fit | Abordagem | Prioridade |
|----------|-----|-----------|------------|
| **Totvs** | ERP líder BR, 40k+ clientes, LGPD mandatório para todos | Totvs Partner Program + pitch técnico | P1 |
| **SENIOR Sistemas** | RH/DP/Fiscal BR, dados pessoais em volume | Contato via Ecosystem Senior | P1 |
| **Stefanini** | Integradora IT BR com prática de dados/IA | LinkedIn + RFP submission | P1 |
| **Accenture BR (LGPD practice)** | Tem prática de privacidade, precisa de ferramenta técnica | LinkedIn → LGPD lead | P2 |
| **CI&T** | Dev shop BR, constrói apps com dados pessoais | LinkedIn → partnerships | P2 |
| **Deloitte BR (Risk Advisory)** | Audita compliance LGPD para enterprise | Contato via Risk Advisory | P2 |

### 3.3 Integrações Técnicas (Tipo C)

| Plataforma | Usuários | Como integrar | Prioridade |
|-----------|----------|---------------|------------|
| **LangChain** | 100k+ devs AI | npm @egosbr/guard-brasil-langchain + PR | P1 |
| **Bubble.io** | 3M+ usuários no-code | Plugin marketplace submission | P1 |
| **Make.com (Integromat)** | 500k+ automações | App submission (REST-based) | P1 |
| **Zapier** | 6M+ usuários | Zapier Partner Program | P2 |
| **n8n** | Self-hosted, popular BR devs | Node community submission | P2 |
| **Dify.ai** | AI app builder em crescimento | Plugin submission | P2 |
| **Stack AI** | AI workflows no-code | API integration | P3 |

### 3.4 Comunidade / Influência (Tipo D — distribuição orgânica)

| Canal | Ação | Output |
|-------|------|--------|
| **npmjs.com** | @egosbr/guard-brasil já publicado | Weekly downloads tracking |
| **GitHub** | README, CONTRIBUTING, good-first-issues | Stars → credibilidade |
| **Dev.to / Hashnode** | "Como mascaro PII brasileiro com 4 linhas" | SEO + backlinks |
| **Rocketseat / Alura / Full Cycle** | Parceria conteúdo / tutorial | Base de 500k+ devs BR |
| **ProductHunt** | Launch Guard Brasil API | International reach |
| **LinkedIn BR** | Posts semanais com casos de uso reais | B2B pipeline |

---

## 4. Modelos de parceria

### White-label API
```
Parceiro vende "LGPD Shield powered by GuardTech" (ou nome deles)
Nós: infraestrutura + manutenção
Eles: vendas + suporte cliente
Revenue split: 70% nós / 30% parceiro (ou negociável por volume)
SLA: <5ms P95, 99.9% uptime, ANPD-ready receipts
```

### Revenue Share — Referral
```
Parceiro indica clientes → link rastreável
Nós pagamos: 20% MRR por 12 meses por cliente indicado
Mínimo: R$0 para começar, sem contrato de exclusividade
```

### OEM / Embed
```
Parceiro incorpora Guard Brasil no produto deles (ex: Totvs, Senior)
Pricing: volume por chamada com desconto (R$0.001–0.003/call)
Contrato mínimo: 100k chamadas/mês
Suporte: SLA enterprise + canal dedicado
```

### Co-desenvolvimento (Tipo B premium)
```
Parceiro financia feature específica (ex: validação de Passaporte, integração SAP)
Nós desenvolvemos + damos exclusividade por 6 meses
Preço: custo de desenvolvimento + 30% sobre receita gerada pela feature
```

---

## 5. Pitch de 30 segundos

> "Toda empresa brasileira que usa IA processa CPFs, CNPJs e dados pessoais de clientes. O Guard Brasil é uma API que detecta e mascara 15 tipos de PII brasileiro em tempo real — antes que esses dados cheguem ao ChatGPT, Claude ou qualquer LLM. Uma linha de código, 4ms de latência, receipt SHA-256 para cada inspeção. Compliance LGPD automático. 500 chamadas grátis para testar agora."

**Para enterprise:** "Cada inspeção gera um receipt imutável com hash SHA-256 — prova auditável que o mascaramento ocorreu. Isso é o que a ANPD pede em fiscalizações."

**Para parceiros técnicos:** "npm install @egosbr/guard-brasil — open source core, API enterprise, 85.3% F1 score, melhor que Microsoft Presidio para dados brasileiros."

---

## 6. O que falta para enterprise-grade

### Gaps técnicos (resolver antes de abordar Totvs/Deloitte)
- [ ] **SLA formal** — documento com uptime guarantee, RTO/RPO, incident response (PART-009)
- [ ] **SOC2 readiness** — checklist Vanta/Secureframe (PART-010)
- [ ] **Security questionnaire** — template padrão procurement enterprise (PART-012)
- [ ] **Enterprise pricing page** — contratos custom, volume, suporte dedicado (PART-011)
- [ ] **Status page** — status.guard.egos.ia.br (Instatus ou Betteruptime, grátis)
- [ ] **DPA template** — Data Processing Agreement para LGPD/GDPR

### Gaps de presença (resolver antes de abordar distribuidores)
- [ ] **ProductHunt launch** — precisa de 30-50 upvotes nas primeiras horas
- [ ] **LinkedIn empresa** — EGOS / Guard Brasil page com 100+ seguidores
- [ ] **Case study** — 1 cliente real usando Guard Brasil em produção
- [ ] **Benchmark público** — blog post com metodologia F1 score vs Presidio vs re:patterns

---

## 7. Execução semana 1 (Enio)

| Dia | Ação | Tempo |
|-----|------|-------|
| **Segunda** | Postar X.com + LinkedIn com og-image.jpg | 30min |
| **Segunda** | Submeter Stripe App Marketplace | 2h |
| **Terça** | Enviar 3 emails cold (DPOnet, LGPD Brasil, Rocketseat) | 1h |
| **Quarta** | ProductHunt — preparar assets, agendar launch | 2h |
| **Quinta** | AWS Marketplace — iniciar cadastro de seller | 1h |
| **Sexta** | Contato LangChain via GitHub PR (npm package integration) | 1h |

**Total:** ~8h de esforço comercial + técnico.

---

## 8. Métricas de sucesso

| Métrica | Baseline (hoje) | Meta 30 dias | Meta 90 dias |
|---------|----------------|--------------|--------------|
| Usuários API | 0 pagantes | 5 pagantes | 50 pagantes |
| MRR | R$0 | R$500 | R$5.000 |
| npm downloads/semana | ~10 | 100 | 500 |
| Parceiros ativos | 0 | 1 (Stripe Marketplace) | 3 |
| GitHub stars | ? | 50 | 200 |

---

## 9. Referências e próximos docs

- `docs/business/OUTREACH_EMAIL_TEMPLATES.md` — 5 templates prontos (DPO, CTO, Legal, Dev, SaaS)
- `docs/strategy/GUARD_BRASIL_WEBSITE_CRITIQUE.md` — 14 melhorias identificadas
- `docs/strategy/GUARD_BRASIL_1PAGER.md` — 1-pager para parceiros
- `apps/guard-brasil-web/app/landing/page.tsx` — landing pública guard.egos.ia.br/landing
- TASKS.md PART-001..015 — todas as tasks de parceria

---

*Gerado automaticamente em 2026-04-05 via P22 dissemination run.*
