# Guard Brasil GTM — 3-Week Roadmap (TRANSPARÊNCIA RADICAL)

> **Período:** Semana de 2026-03-30 até 2026-04-20  
> **Objetivo:** R$500/mês receita + Dashboard MVP + 5 customer pilots  
> **Status Atual:** M-001 ✅ | M-002 ✅ | Arquitetura ✅ | Prontos para build

---

## SEMANA 1 (Março 30 — Abril 5): OUTREACH + Dashboard Foundation

### Bloqueios de Receita (Manual)
- [ ] **M-007:** Enviar 5 emails outreach para CTOs govtech (HOJE)
  - Use templates em `docs/strategy/OUTREACH_EMAILS.md`
  - Cada email: 1-pager + DEMO_SCRIPT + link para demo
  - Esperado: 3-5 respostas com interesse em demo

### Desenvolvimento (Claude Code)
- [ ] Dashboard MVP estrutura
  - [ ] `apps/dashboard/` criada com Next.js 15
  - [ ] Supabase tables: `guard_events`, `guard_customers`, `guard_alerts`
  - [ ] Autenticação: API key + OAuth (GitHub)
  
- [ ] Activity Feed (sem dados reais ainda)
  - [ ] Component: `pages/dashboard/activity.tsx`
  - [ ] Mock data para layout
  - [ ] Real-time Supabase Realtime wired (mas sem eventos ainda)

- [ ] Telemetria: Estender API Server
  - [ ] Modificar `apps/api/src/server.ts`
  - [ ] Cada POST /v1/inspect → salva em `guard_events` Supabase
  - [ ] Estrutura: event_type, cost_usd, tokens_in/out, model_id, duration_ms

### Infraestrutura
- [ ] M-006: NPM_TOKEN criado + adicionado GitHub Secrets
  - Precisa de: npm granular token (publish-only para @egosbr/guard-brasil)

### Métricas de Sucesso (Semana 1)
- ✓ 5+ emails enviados
- ✓ 2-3 CTOs responderam com interesse
- ✓ Dashboard skeleton vivo (guard.egos.ia.br/dashboard)
- ✓ Telemetria fluindo para Supabase

---

## SEMANA 2 (Abril 6 — Abril 12): IA Reports + Webhooks

### Demo & Sales (Manual)
- [ ] Agendar 2-3 demo calls com CTOs interessados
  - [ ] Usar GUARD_BRASIL_DEMO_SCRIPT.md
  - [ ] Mostrar: API ao vivo + cost transparency
  - [ ] Resultado esperado: 1-2 LOIs (Letters of Intent)

### Desenvolvimento (Claude Code)
- [ ] Cost Breakdown Charts
  - [ ] Component: `pages/dashboard/costs.tsx`
  - [ ] Pie chart (% por event type)
  - [ ] Line chart (trend diário)
  - [ ] conectar a Supabase real-time

- [ ] IA Reports (Qwen Integration)
  - [ ] Criar `apps/api/src/reports.ts`
  - [ ] Async job: agregra events últimas 24h
  - [ ] Query Supabase: SUM(cost), COUNT(*), GROUP BY(event_type)
  - [ ] Prompt para Qwen: "Analisa essas stats..."
  - [ ] Store resultado em `guard_reports` table

- [ ] Webhook Dispatcher
  - [ ] Setup: Slack integration (OAuth)
  - [ ] Trigger: Daily report @ 8am
  - [ ] Output: Markdown com insights + link para dashboard

### Integração MCP
- [ ] Verificar que MCP stdio serve ainda funciona
  - [ ] Test: `guard_inspect`, `guard_scan_pii`, `guard_check_safe`

### Métricas de Sucesso (Semana 2)
- ✓ 2-3 demos feitas com sucesso
- ✓ Dashboard mostra cost breakdown em tempo real
- ✓ Primeiro relatório IA gerado + enviado para Slack
- ✓ 1+ cliente assinou contrato Starter

---

## SEMANA 3 (Abril 13 — Abril 20): Go-Live + Customer Pilots

### Production Setup
- [ ] Guard Brasil API → produção estável (já está em Hetzner)
- [ ] Dashboard → deployment em `guard.egos.ia.br/dashboard`
- [ ] Supabase → backup automático, SLA 99.9%
- [ ] Monitoring: healthcheck, alerts em Slack #ops

### Customer Onboarding (Manual)
- [ ] 5 customer pilots começam
  - [ ] Setup de API keys (random, per customer)
  - [ ] Dashboard access criado
  - [ ] Slack channel privado #guard-brasil-<customer>
  - [ ] Kickoff call: "Seu cost aparece aqui em tempo real"

### Documentation
- [ ] API reference: `/docs/GUARD_BRASIL_API.md`
- [ ] SDK guide: `@egosbr/guard-brasil` + exemplos
- [ ] MCP usage: como usar as 3 tools
- [ ] Dashboard walkthrough: vídeo ou screenshot tour
- [ ] Pricing explainer: por que cada custo

### Desenvolvimento Final (Claude Code)
- [ ] Configuration Panel (se tempo permitir)
  - [ ] Alert thresholds (CPF/hour, score < X)
  - [ ] Integrations (Teams, Email)
  - [ ] Report scheduling
  - [ ] API key rotation UI

- [ ] Bug fixes + performance
  - [ ] Profile dashboard queries (Supabase)
  - [ ] Otimizar Activity Feed pagination (1000+ events)

### Métricas de Sucesso (Semana 3)
- ✓ 5 customer pilots com dados reais
- ✓ R$300-500/mês receita estimada (5 × R$99/mo Starter)
- ✓ 0 P0 bugs em produção
- ✓ Dashboard responde em < 1s
- ✓ Primeiros relatórios IA gerados + clientes leem

---

## PARA ALÉM (Semana 4+)

### Expansão (Next Iteration)
- [ ] M-003+M-005: Rename br-acc completo (já parcialmente feito)
  - [ ] Wire Guard Brasil em egos-inteligencia Python ETL
  - [ ] `etl/src/egos_inteligencia_etl/guard.py`

- [ ] Policy Packs (R$2.990/ano)
  - [ ] Segurança Pública: customização para PRF/PF
  - [ ] Judiciário: customização para Tribunais
  - [ ] Saúde: customização para HIPAA-BR equivalente

- [ ] Dashboard Avançado (Pro tier)
  - [ ] Histórico completo (não apenas 30 dias)
  - [ ] Custom reports (user-generated)
  - [ ] Team management (múltiplos users)

### Receita Projeção
```
Semana 3:       R$500/mês (break-even)
Semana 4:       R$1.200/mês (2 Pro, 10 Starter)
Mês 2:          R$2.500+/mês (escala)
Mês 3:          R$5.000+/mês (com policy packs)
```

---

## CHECKLIST: "GO-LIVE READY"

### Pre-Deployment
- [ ] API healthcheck: `curl -s guard.egos.ia.br/health | jq`
- [ ] DNS: `nslookup guard.egos.ia.br` → 204.168.217.125 ✓
- [ ] TLS: `curl -I https://guard.egos.ia.br | grep "200 OK"`
- [ ] Telemetria: 1 test call → Supabase registrada
- [ ] Dashboard: abre em < 2s
- [ ] Relatório: Qwen retorna em < 30s

### Contato
- [ ] Email setup: support@egos.ia.br (monitored)
- [ ] Slack: #guard-brasil-support
- [ ] SLA doc: uptime, response times, limits

### Compliance
- [ ] LGPD: Privacy policy em `docs/strategy/LGPD_COMPLIANCE.md`
- [ ] Data deletion: 30-day retention default (customizable)
- [ ] Audit logs: Quem acessou seu dashboard, quando

---

## Comando Master (Run Anytime to Check Status)

```bash
# Validate everything is ready for week N
bun run scripts/doctor.ts --json | jq '.guard_brasil'

# Expected:
# {
#   "api_health": "healthy",
#   "dns_resolves": true,
#   "telemetry_working": true,
#   "dashboard_deployed": "https://guard.egos.ia.br/dashboard",
#   "supabase_connected": true,
#   "qwen_available": true,
#   "customers_onboarded": 5,
#   "revenue_this_month": "R$500"
# }
```

---

**Signed by:** Sequential Thinking + telemetry.ts + egos-repo-health.sh + code-health-monitor.ts  
**Data:** 2026-03-30  
**Próxima ação:** **M-007 HOJE** (5 emails outreach)
