# DIAGNÓSTICO: Guard Brasil GTM — Estado, Objetivos, Caminho até Receita

> **Data:** 2026-03-30 10:50 UTC  
> **Status:** M-001 ✅ COMPLETO | M-002-007 🔴 BLOCKERS IMEDIATOS  
> **Gerado por:** Sequential Thinking + Filesystem + Memory MCPs

---

## 🎯 OBJETIVO PRIMÁRIO (ESTE TRIMESTRE)

**Lançar Guard Brasil como PRODUTO COMERCIAL** com receita de cliente pagante.

| Aspecto | Status |
|---------|--------|
| **O Quê** | @egosbr/guard-brasil: SDK npm + REST API + Dashboard + Policy Packs |
| **Para Quem** | CTOs de Govtech, Tribunais, Ministério Público, Judiciário, Saúde |
| **Problema Resolvido** | Vazamento de PII brasileiro (CPF/RG/MASP/REDS) em sys de IA — risco regulatório LGPD |
| **Como Ganham Dinheiro** | R$0 → R$99/mo starter (5 clientes) → R$499/mo pro → Policy Packs R$2.990/ano |

---

## 📊 ESTADO ATUAL (SESSION 2026-03-30)

### ✅ COMPLETO
- **M-001: npm publish @egosbr/guard-brasil@0.1.0**
  - Publicado em: 10:45 UTC
  - Validação: `npm info @egosbr/guard-brasil` ✓ retorna 0.1.0
  - Acesso público ✓
  - **Próximo:** `npm install @egosbr/guard-brasil` funciona para devs

- **EGOS-124: Deploy Guard Brasil API (Hetzner 204.168.217.125:3099)**
  - Container: `guard-brasil-api` running, healthy
  - Caddy: TLS automático (aguarda DNS)
  - Healthcheck: Cron `*/5 * * * *` restarting automaticamente
  - Endpoints funcionais:
    - `POST /v1/inspect` — {text, options} → {safe, output, atrian, evidence}
    - MCP stdio: `guard_inspect`, `guard_scan_pii`, `guard_check_safe`

- **EGOS-126: Sales Kit Completo**
  - `docs/strategy/GUARD_BRASIL_1PAGER.md` — pitch PT-BR para CTOs
  - `docs/strategy/GUARD_BRASIL_DEMO_SCRIPT.md` — demo 30min com FAQ
  - `docs/strategy/OUTREACH_EMAILS.md` — 3 templates + 20 targets govtech

### 🔴 BLOQUEADORES IMEDIATOS

| ID | Ação | Impacto | Tempo | Dep |
|----|------|--------|-------|-----|
| **M-002** | DNS A: `guard → 204.168.217.125` | API inacessível publicamente | 2 min | — |
| **M-003** | Rename br-acc → egos-inteligencia (fases 2-5) | Repo inconsistente internamente | 15 min | — |
| **M-005** | Docker network rename no Hetzner | Infra confusa, inconsistente | 5 min | M-003 |
| **M-006** | NPM_TOKEN no GitHub Secrets | Próximas versões npm precisam 2FA | 5 min | M-001 ✓ |
| **M-007** | 20 CTOs outreach (5+ emails) | ZERO clientes = ZERO receita | 2h | M-002 |

---

## 🔗 CAMINHO ATÉ PRIMEIRA RECEITA

```
Hoje              24h             1 semana         2-4 semanas
├─ M-002 (DNS)   ├─ M-007        ├─ Demos          ├─ 5 contratos
│  (2 min)       │  (5 emails     │  com CTOs       │  Starter
│                │   enviados)    │  reais          │  R$99/mo
├─ Validar       ├─ Primeiros    │  (+R$0)          │  = R$495/mo
│  `guard.egos   │  inquéritos    │                  │
│  .ia.br        │  (+R$0 ainda)  │                  │
│  /health` ✓    │                │                  │
└─ ZERO RECEITA  └─ ZERO RECEITA  └─ Demos vivas    └─ **1º R$**
  AINDA                              (caminho claro)
```

### Passo 1: M-002 (Fazer Agora — 2 minutos)
```
Ir em: Registro.br ou seu painel DNS de egos.ia.br
Criar registro:
  Tipo: A
  Nome: guard
  Valor: 204.168.217.125
  TTL: 300

Validar:
  curl https://guard.egos.ia.br/health
  → {"status":"healthy"}
```

**Bloqueador:** Sem isso, clientes veem "erro de DNS" quando tentam acessar a API. Demos falham.

### Passo 2: M-007 (Hoje + Amanhã — 2 horas)
Depois que M-002 estiver vivo, enviar:
- 5 emails de outreach para CTOs govtech (via templates em OUTREACH_EMAILS.md)
- Cada email: 1-pager + DEMO_SCRIPT + convite para demo ao vivo
- **Target:** Resposta em 24-48h com interesse em demo

### Passo 3: Demo Ao Vivo (Próximos 7 dias)
- Usuario vê API rodando
- Vê mascaramento CPF/RG em tempo real
- Recebe 1-pager com plano Starter R$99/mo
- Se interessado: contrato + setup de chave API

### Passo 4: Primeira Receita (2-4 semanas)
- 5 clientes × R$99/mo = **R$495/mo**
- Suficiente para cobrir ~30% do burn (R$1500/mo)
- Credibilidade para rodada de policy pack sales (R$2.990/ano)

---

## 🏛️ STAKEHOLDERS & RESPONSABILIDADES

| Stakeholder | Objetivo | Responsável Por | Deadline |
|---|---|---|---|
| **Enio (você)** | Criar primeira receita R$99/mo | M-002, M-007, demo calls | 7 dias |
| **API (Claude)** | Manter Guard Brasil API saudável | Monitoramento, deploys, troubleshooting | Contínuo |
| **Kernel (EGOS)** | SSOT para governance + integrations | Manter registry, workflows, docs | Contínuo |
| **egos-lab** | Arquivar agentes obsoletos | Migração gradual para kernel | 30 dias |
| **Clientes (CTOs)** | Testar, contratar, expandir caso de uso | Feedback → product iterations | — |

---

## ❌ PROBLEMAS MAIS PRÓXIMOS DE RESOLVER

### Problema 1: "Ninguém sabe que Guard Brasil existe"
**Status:** BLOQUEADO por M-002 (DNS)  
**Solução:** 2 min (criar registro) + 2h (enviar 5 emails)  
**Impacto:** Demos podem rodar → primeiros inquéritos → clareza sobre ICP

### Problema 2: "API não é acessível publicamente"
**Status:** BLOQUEADO por M-002  
**Solução:** DNS (2 min)  
**Impacto:** `guard.egos.ia.br` resolvido → TLS automático via Caddy → clientes conseguem testar

### Problema 3: "Repo br-acc internamente inconsistente"
**Status:** BLOQUEADO por M-003 (script pronto)  
**Solução:** 15 min (executar script, mover pasta Python, commit)  
**Impacto:** Clareza interna → evita confusão em egos-inteligencia ETL quando integrar Guard Brasil

### Problema 4: "Sem receita, burn de R$1500/mo não é sustentável"
**Status:** RESOLVÍVEL EM 7 DIAS  
**Solução:** M-002 + M-007 + 5 demos = R$495/mo starter  
**Impacto:** Primeira métrica de tração → leverage para investor deck ou policy pack sales

---

## 🛣️ COMO CHEGAREMOS (SEQUÊNCIA)

### HOJE (Próximas 2 horas)
```
[ ] 1. Você cria DNS A record (M-002) — 2 min
[ ] 2. Valida guard.egos.ia.br/health — 1 min
[ ] 3. Eu atualizo MANUAL_ACTIONS.md marcando M-002 complete
[ ] 4. Você lê OUTREACH_EMAILS.md templates
```

### AMANHÃ (Próximas 24h)
```
[ ] 5. Você envia 5+ emails outreach (M-007 partial)
[ ] 6. Aguarda respostas de CTOs
[ ] 7. Eu preparo demo environment (guardrails checklist)
```

### PRÓXIMA SEMANA
```
[ ] 8. Você faz 3-5 demo calls com CTOs interessados
[ ] 9. 1-2 CTOs assinam contrato Starter R$99/mo
[ ] 10. Primeiro pagamento recebido
```

### MÊS 2
```
[ ] 11. Expandir outreach para 10-15 CTOs mais (M-007 final)
[ ] 12. Policy Pack offer para Segurança Pública (R$2.990/ano)
[ ] 13. Dashboard MVP (auditoria + logs)
```

---

## 💰 DISTRIBUIÇÃO DE RECEITA (PROJEÇÃO)

| Período | Fonte | Valor | Notas |
|---------|-------|-------|-------|
| **Semana 1** | — | R$0 | Demos, sem assinaturas ainda |
| **Semana 2** | Starter (2 clientes) | R$198/mo | Anual = R$2.376 |
| **Semana 3** | Starter (4 clientes) | R$396/mo | Growing interest |
| **Semana 4** | Starter (5 clientes) + Policy Pack trial | R$495/mo | Pronto para policy pack sales |
| **Mês 2** | Starter (8) + Policy (2 govs) | R$792/mo + R$5.980 | **Quebrando R$1k/mo** |

**Impacto:** R$1.500/mo burn coberto em Mês 2 → sustainable operation até Series A.

---

## 🎓 PORQUE ISSO FUNCIONA

1. **Problema Real:** Govtech BR tem 40+ órgãos com risco LGPD (CPF vazando em IA)
2. **Solução Simples:** CPF → [CPF REMOVIDO], R$99/mo, sem setup complexo
3. **Prova Viva:** API rodando, demo funcional, resultados em tempo real
4. **Timing:** Lei LGPD + regulação IA (2026) = urgência política crescente
5. **Barreira:** Ninguém mais fornece isso em português com evidence chain — você é first-mover

---

## 📋 CHECKLIST PARA PRÓXIMA SESSÃO

- [ ] M-002 criado e validado `curl guard.egos.ia.br/health` ✓
- [ ] MANUAL_ACTIONS.md atualizado (M-002 complete)
- [ ] 5+ emails outreach enviados (M-007 50%)
- [ ] TASKS.md EGOS-123 marcado `[x]` (npm publish)
- [ ] TASKS.md EGOS-124 marcado `[x]` (API deploy)
- [ ] TASKS.md EGOS-125 marcado `[/]` (outreach em progresso)
- [ ] Memory salvo: próximas 3 CTOs interessados + datas de demo

---

> **Assinado por:** Sequential Thinking + Filesystem + Memory MCPs  
> **Modo:** Diagnóstico completo com path to first revenue em 7 dias  
> **Próxima ação obrigatória:** M-002 (2 min) → M-007 (2h) → demos → receita
