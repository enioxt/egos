# Guard Brasil — TRANSPARÊNCIA RADICAL (Pricing + Observabilidade)

> **Versão:** 1.0.0 | **Data:** 2026-03-30 | **Modelo:** Tiers mensais + visibilidade operacional + relatórios IA
> **Baseado em:** telemetry.ts, egos-repo-health.sh, code-health-monitor.ts, doctor.ts

---

## 🎯 CONCEITO: TRANSPARÊNCIA RADICAL

**Não é opacidade operacional.** Cada cliente vê o que está acontecendo no uso contratado, sem precisar expor detalhes sensíveis de infraestrutura:

```
Cliente entra no Dashboard
  ↓
Vê cada chamada API registrada (timestamp, categoria, custo, decisão)
  ↓
Vê breakdown de custos e eventos (masking, ATRiAN, evidence, policy)
  ↓
Vê relatórios automáticos gerados por IA (correlações, trends, recomendações)
  ↓
Entende claramente o que está pagando e o que está sendo protegido
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

## 💰 ESTRUTURA DE PREÇOS

### Tier 1: Free (npm SDK)
- `npm install @egosbr/guard-brasil`
- Uso local, sem telemetria hospedada
- PII Scanner BR + ATRiAN core + masking + evidence chain
- Sem limite local de chamadas
- **Preço:** R$0

### Tier 2: Starter API
- `POST guard.egos.ia.br/v1/inspect`
- Autenticação via Bearer Token
- Telemetria automática
- Dashboard básico
- **Preço:** R$49/mês até 10k inspeções

### Tier 3: Pro
- Tudo de Starter +
- Dashboard avançado
- Relatórios automáticos com IA
- Alertas customizados
- **Preço:** R$199/mês até 100k inspeções

### Tier 4: Business
- Tudo de Pro +
- SLA ampliado
- Operação multi-time
- Suporte dedicado
- **Preço:** R$499/mês até 500k inspeções

### Tier 5: Enterprise
- Tudo de Business +
- On-premise ou deployment dedicado
- Modelo de cobrança customizado
- Relatórios forenses
- **Preço:** Sob consulta

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

const guard = GuardBrasil.create();
const result = guard.inspect('CPF do usuário: 123.456.789-00');

console.log(result.output);
console.log(result.summary);
```

### MCP Tool
```bash
mcp call guard_inspect \
  --text "Paciente: João Silva, CPF 123.456.789-00" \
  --options '{"verbose": true, "audit": true}'
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
  3 clientes Starter = R$147
  1 cliente Pro = R$199
  Total: R$346

Mês 2:
  6 clientes Starter = R$294
  2 clientes Pro = R$398
  Total: R$692

Mês 3:
  10 clientes Starter = R$490
  3 clientes Pro = R$597
  1 cliente Business = R$499
  Total: R$1.586

Trimestral: R$2.624
Annual run-rate após M3: R$19.032
```

### Break-Even Analysis
- **Burn Rate:** R$1.500/mês (VPS + SaaS + APIs)
- **Mês 1 Revenue:** R$346
- **Mês 2 Revenue:** R$692
- **Mês 3 Revenue:** R$1.586 (cobre o burn)
- **Break-even:** Mês 3

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
