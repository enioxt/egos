# Partner Brief — Guard Brasil

> **Produto:** Guard Brasil — API de Detecção de PII Brasileiro  
> **Status:** API Live, Stripe ativo  
> **Equity Oferecido:** 20-30%  
> **Parceiro Ideal:** DPO/Consultor LGPD com rede em fintechs/healthtechs  
> **Data:** 2026-04-06  
> **SSOT:** docs/business/MONETIZATION_SSOT.md

---

## 🎯 O Problema que Resolvemos

**LGPD é lei desde 2020, mas 90% das empresas brasileiras ainda não têm compliance técnico.**

- ANPD está acelerando fiscalizações em 2026
- Vazamentos de CPF/RG geram multas de até 2% do faturamento
- DPOs precisam de ferramentas que falem "brasileiro" (CPF, RG, MASP, CNH, etc.)
- Soluções internacionais (Presidio, OneTrust) têm 0 padrões brasileiros

---

## 🛠️ O Que Construímos

### API de PII Detection — 15 padrões BR nativos

| Padrão | Precisão | Latência |
|--------|----------|----------|
| CPF | 99.5% | <4ms |
| RG | 97.2% | <4ms |
| CNPJ | 99.1% | <4ms |
| MASP (servidor público) | 95.8% | <4ms |
| CNH | 96.5% | <4ms |
| +10 padrões | F1 85.3% médio | P95 <5ms |

### Features Enterprise
- **Evidence chain:** Cada detecção gera log auditável para ANPD
- **Masking reversível:** Oculta PII sem perder dados (para testes/dev)
- **SDK npm:** `@egosbr/guard-brasil` — instalação em 30 segundos
- **Batch processing:** Até 10MB por request
- **Webhook:** Notificações em tempo real de vazamentos detectados

### Infraestrutura
- Deploy: VPS Hetzner (204.168.217.125)
- SSL: Let's Encrypt auto-renew
- Billing: Stripe (BRL via Asaas)
- Uptime: 99.9% target (monitorado)

---

## 📊 Prova de Capacidade

### Benchmark vs Concorrência

| Ferramenta | Padrões BR | Latência | Custo/Mês |
|------------|-----------|----------|-----------|
| **Guard Brasil** | 15 | 4ms | $50 infra |
| Microsoft Presidio | 0 | 50ms | $500+ Azure |
| OneTrust | 0 | N/A | $50K+ enterprise |
| Solução caseira | ? | ? | 3 eng × 6 meses |

### Teste ao Vivo
```bash
# Free tier — 100 requests/dia
curl -X POST https://guard.egos.ia.br/api/v1/detect \
  -H "Authorization: Bearer $GUARD_API_KEY" \
  -d '{"text": "Meu CPF é 529.982.247-25"}'

# Retorno:
# {"entities": [{"type": "CPF", "value": "529.982.247-25", "position": [12, 28], "confidence": 0.995}]}
```

---

## 🎯 ICP (Ideal Customer Profile)

### Primário
- **CTOs/backend devs** em fintechs/healthtechs 50-500 funcionários
- **Handle CPF/RG diariamente** (empréstimos, cadastros, KYC)
- **Pressão da ANPD** — precisam demonstrar compliance técnico
- **Buy em dias** — não meses

### Secundário
- **DPOs (Data Protection Officers)** — precisam de evidência de proteção
- **Consultorias LGPD** — querem ferramenta para múltiplos clientes
- **Legal tech** — integrar em workflows de due diligence

---

## 💰 Modelos de Parceria

### Opção A — Co-fundador Equity (recomendado)
- **Equity:** 20-30% do produto
- **Vesting:** 12 meses, cliff 3 meses
- **Sua contribuição:** Pipeline, demos, closes, follow-up
- **Nossa contribuição:** Tech, infra, evolução, suporte

### Opção B — Revenue Share
- **Split:** 25% do MRR por cliente que você traz
- **Duração:** 12 meses por cliente
- **Tracking:** Stripe customer attribution
- **Ideal para:** Consultorias com múltiplos clientes LGPD

### Opção C — White-label
- **Modelo:** Você vende com sua marca, mantemos infra
- **Split:** 70/30 (infra/evolução vs distribuição)
- **Ideal para:** Consultorias LGPD com marca estabelecida

---

## 🚀 Próximos Passos Imediatos

### Se você é DPO/Consultor LGPD:
1. **Teste:** Use o free tier em um cliente (100 requests/dia)
2. **Valide:** Mostre para seu cliente que detectamos os PII deles
3. **Converse:** Agende 30 min comigo (enioxt@gmail.com)
4. **Feche:** Assine nota de compromisso, comece a vender

### Se você é CTO de fintech/healthtech:
1. **SDK:** `npm install @egosbr/guard-brasil`
2. **Teste:** Rode em sua base de dados em 5 minutos
3. **Resultado:** Veja quantos CPFs/RGs estão expostos
4. **Decisão:** Compre API key ou converse sobre parceria

---

## 📞 Contato

**Enio Rocha**
- Email: enioxt@gmail.com
- X.com: @anoineim
- Demo: https://guard.egos.ia.br
- Código: github.com/enioxt/egos

---

**Sacred Code:** 000.111.369.963.1618  
**Nota de Compromisso:** docs/legal/NOTA_COMPROMISSO_EQUITY_GTM_TEMPLATE.md

