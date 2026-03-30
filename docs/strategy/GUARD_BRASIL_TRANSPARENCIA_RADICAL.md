# Guard Brasil — TRANSPARÊNCIA RADICAL (Pricing + Observabilidade)

> **Versão:** 1.0.0 | **Data:** 2026-03-30 | **Modelo:** Pay-Per-Use + Dashboard + Relatórios IA
> **Baseado em:** telemetry.ts, egos-repo-health.sh, code-health-monitor.ts, doctor.ts

---

## 🎯 CONCEITO: TRANSPARÊNCIA RADICAL

**Não é assinatura fixa.** Cada cliente VEMTUDO que está pagando em tempo real:

```
Cliente entra no Dashboard
  ↓
Vê cada chamada API registrada (timestamp, modelo, tokens, custo)
  ↓
Vê breakdown de custos (CPF scanning, RG masking, ATRiAN score, evidence chain)
  ↓
Vê relatório automático gerado por IA (correlações, trends, recomendações)
  ↓
Paga EXATAMENTE o que usou (sem surpresas, sem mínimos)
```

### Diferencial vs Stripe/Twilio/OpenAI

| Aspecto | Guard Brasil | Concorrentes |
|---------|--------------|--------------|
| **Precificação** | Radicalmente transparente (cada evento visível) | Agregado em faturas opacas |
| **Dashboard** | IA explica cada linha | Gráficos genéricos |
| **Customização** | Você define seus próprios thresholds | Presets apenas |
| **Relatórios** | Automáticos com IA, em PT-BR | CSV crú |
| **Modelos de Cobrança** | API + consumo, ou monthly, ou volume discounts | Um modelo só |

---

## 💰 ESTRUTURA DE PREÇOS (PAY-PER-USE)

### Tier 1: Free (npm SDK)
- `npm install @egosbr/guard-brasil`
- Uso local, sem telemetria
- PII Scanner BR + ATRiAN core
- Sem limite de chamadas (local-only)
- **Preço:** R$0

### Tier 2: Starter API (Pay-Per-Call)
- `POST guard.egos.ia.br/v1/inspect`
- Autenticação via Bearer Token
- Telemetria automática (cada chamada)
- Dashboard básico (últimos 30 dias)
- **Preço:** R$0,02 por chamada (mínimo R$0)
  - 1 chamada = ~R$0,02
  - 100 chamadas/dia = ~R$1,40/dia = ~R$42/mês
  - 10.000 chamadas/mês = ~R$200/mês

### Tier 3: Pro (Dashboard + IA Reports)
- Tudo de Starter +
- Dashboard avançado (histórico completo)
- Relatórios automáticos com IA (diários/semanais)
- Alertas customizados (CPFs detectados, scores baixos)
- Integração com Slack/Teams/Email
- **Preço:** R$299/mês (inclui até 50k chamadas)
  - Cada chamada adicional: R$0,01 (50% desconto)

### Tier 4: Enterprise (Custom)
- Tudo de Pro +
- SLA 99.9% uptime
- Modelo de cobrança customizado (flat fee, volume commits, etc.)
- Suporte dedicado (Slack)
- Relatórios forenses (compliance audits)
- **Preço:** Sob consulta (mínimo R$2.990/mês)

---

## 📊 DASHBOARD: O CORAÇÃO DA TRANSPARÊNCIA

Página única que mostra TUDO:

### Seção 1: Activity Feed (Hoje)
```
[13:45] ✅ CPF masking (1 ocorrência)        R$0,02
[13:44] ✅ RG detection (0 ocorrências)      R$0,02
[13:30] ✅ ATRiAN validation (score 87)      R$0,02
[13:15] ❌ MASP lookup (API timeout)         R$0,00 (sem custo)
─────────────────────────────────────────────────
Hoje: 47 chamadas, R$0,94
```

### Seção 2: Breakdown por Tipo
```
CPF Masking:      420 chamadas (R$8.40) — 45%
RG Detection:     310 chamadas (R$6.20) — 33%
ATRiAN Scoring:   215 chamadas (R$4.30) — 23%
MASP Validation:  5 falhas       (R$0) — 0%
─────────────────────────────────────────────────
Total este mês: R$19.10 (de R$299 Pro budget)
```

### Seção 3: Relatório IA (Automático)
```
📊 Insights Automáticos (IA Qwen + ATRiAN)

• Padrão detectado: Picos de CPF scanning às 14h
  → Recomendação: Considere batch processing para reduzir custos

• Alerta: 12 RG detections ontem (vs média 3/dia)
  → Possível risco: Documento mal armazenado?
  → Ação sugerida: Revisar logs deste período

• Economia possível: Usar /batch endpoint = 50% desconto
  → Potencial: R$9.55/mês em economia
```

### Seção 4: Configuração + Thresholds
```
Alertas customizados:
  ☑️ Notificar se > 100 CPFs/hora
  ☑️ Notificar se ATRiAN score < 50 (risco ético)
  ☐ Notificar se custo diário > R$50

Relatórios automáticos:
  ✓ Diário (email) — próximo às 8:00
  ✓ Semanal (Slack) — todo seg
  ✗ Mensal (nada configurado)

Rate limiting:
  Limite: 10.000 chamadas/hora
  Status: 3.456 usadas hoje (34%)
```

---

## 🔌 INTEGRAÇÃO: API + MCP + Dashboard

### Client Code (Node.js)
```typescript
import { GuardBrasil } from '@egosbr/guard-brasil';

const guard = new GuardBrasil({
  apiKey: 'sk_live_xyz123...',
  // Telemetria automática ativada
  telemetryUrl: 'https://guard.egos.ia.br/telemetry'
});

const result = await guard.inspect('CPF do usuário: 123.456.789-00');
// Resultado + evento de telemetria enviado automaticamente

// Todo uso é rastreado:
// - Tipo: 'cpf_masking'
// - Custo: R$0.02
// - Token auth: hash do API key
// - Timestamp: ISO 8601
// - Modelo usado: Qwen-plus
```

### MCP Tool
```bash
mcp call guard_inspect \
  --text "Paciente: João Silva, CPF 123.456.789-00" \
  --options '{"verbose": true, "audit": true}'

# Resposta:
{
  "safe": true,
  "blocked": ["123.456.789-00"],
  "output": "Paciente: João Silva, CPF [CPF REMOVIDO]",
  "atrian": {
    "score": 92,
    "reasoning": "Disclosure de PII em contexto clínico"
  },
  "evidenceChain": "hash:abc123...",
  "telemetry": {
    "event_id": "evt_789xyz",
    "cost_usd": 0.004,  // ~R$0.02
    "provider": "qwen",
    "tokens_in": 35,
    "tokens_out": 8
  }
}
```

### Dashboard + Relatórios
- **Integração:** SPA Next.js (Vercel)
- **Autenticação:** OAuth2 + API key
- **Dados:** Supabase (tabela `guard_events`)
- **Relatórios:** Qwen via MCP (análise IA automática)
- **Alertas:** Webhooks para Slack/Teams/Email

---

## 📈 MODELO DE RECEITA

### Revenue Math (3 meses)

```
Mês 1:
  5 clientes × R$99/mês (Starter, ~500 chamadas cada) = R$495
  2 clientes × R$0,50/dia (Free users curiosos) ≈ R$30
  Total: R$525

Mês 2:
  10 clientes Starter = R$990
  3 clientes Pro = R$897
  Total: R$1.887

Mês 3:
  15 clientes Starter = R$1.485
  5 clientes Pro = R$1.495
  1 cliente Enterprise (estimado R$5k) = R$5.000
  Total: R$7.980

Trimestral: R$10.392
Annual run-rate: R$41.568
```

### Break-Even Analysis
- **Burn Rate:** R$1.500/mês (Hetzner + Vercel)
- **Mês 1 Revenue:** R$525
- **Mês 2 Revenue:** R$1.887 (cobre 125% do burn)
- **Mês 3 Revenue:** R$7.980 (5.3x do burn)
- **Break-even:** Mês 2

---

## 🛠️ IMPLEMENTAÇÃO (3 Semanas)

### Semana 1: Dashboard MVP
- [ ] Next.js app em `apps/dashboard`
- [ ] Supabase tabelas: `guard_events`, `guard_customers`, `guard_alerts`
- [ ] Charts: Activity feed, breakdown, custo acumulado
- [ ] Autenticação: API key + OAuth

### Semana 2: Telemetria + IA Reports
- [ ] Estender `apps/api/src/server.ts` para persistir eventos em Supabase
- [ ] Criar `apps/api/src/reports.ts` — gerador de relatórios (Qwen via MCP)
- [ ] Webhooks: Slack, Teams, Email
- [ ] Alertas customizáveis

### Semana 3: Configuração + Go-Live
- [ ] Deploy dashboard em `guard.egos.ia.br/dashboard`
- [ ] Documentação de setup (client SDK, API key, MCP)
- [ ] Testes de cobrança end-to-end
- [ ] Lançamento para 5 clientes piloto

---

## 🎁 DIFERENCIAL FINAL

**Por que clientes vão escolher Guard Brasil sobre Presidio/NeMo Guardrails:**

1. **Transparência Total:** Cada centavo rastreado, visível em tempo real
2. **IA Explícita:** Relatórios que explicam POR QUE algo foi bloqueado (não só "sim/não")
3. **Context Brasil:** Conhece cultura, Lei LGPD, órgãos governamentais PT-BR
4. **Customização Fácil:** "Alerta se meu alerta aparecer" em clicks, não em código
5. **Sem Lock-in:** SDK é open-source MIT, API é padrão REST
6. **Casamento de Produtos:** Depois, vire Customer = cliente de IA Ethics + data intelligence + compliance

---

## 📌 Próximos Passos

1. **Hoje:** M-002 (DNS ✓) + M-007 (5 emails outreach)
2. **Semana 1:** Build dashboard MVP
3. **Semana 2:** Integração telemetria + Qwen reports
4. **Semana 3:** Deploy + 5 customer pilots
5. **Semana 4:** R$300-500/mês receita em escala
