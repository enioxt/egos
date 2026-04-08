# Telegram Alerts Audit — @EGOSin_bot

> **Versão:** 1.0.0 | **Data:** 2026-04-08 | **Auditor:** Cascade
> **Propósito:** Inventário completo de alertas, identificação de sistemas ativos/inativos, e proposta de consolidação

---

## 📊 Resumo Executivo

| Métrica | Valor |
|---------|-------|
| **Total de fontes de alerta** | 8 |
| **Ativos** | 5 |
| **Inativos/Suspeitos** | 2 |
| **Para desativar** | 1 |
| **Botões de ação** | 0 (nenhum) |
| **Comandos interativos** | 10+ |

---

## 🔍 Inventário de Fontes de Alerta

### 1. EGOS Gateway — Bot Interativo Principal

**Arquivo:** `apps/egos-gateway/src/channels/telegram.ts`

**Status:** ✅ **ATIVO** — Gateway online, bot @EGOSin_bot

**Comandos disponíveis:**
| Comando | Função | Status |
|---------|--------|--------|
| `/start` | Inicialização | ✅ Funcionando |
| `/help` | Ajuda | ✅ Funcionando |
| `/status` | Status do sistema | ✅ Funcionando |
| `/gems` | Listar gems recentes | ✅ Funcionando |
| `/wiki` | Consultar wiki | ✅ Funcionando |
| `/agents` | Listar agentes | ✅ Funcionando |
| `/costs` | Custos LLM | ✅ Funcionando |
| `/hunt` | Executar gem-hunter | ✅ Funcionando |
| `/trending` | Tópicos em alta | ✅ Funcionando |
| `/sector <nome>` | Gems por setor | ✅ Funcionando |

**Recursos:**
- Texto → AI Orchestrator
- Áudio → Whisper transcription
- Fotos → Qwen-VL vision
- Documentos → Análise

**Limitação crítica:** Botões de ação NÃO implementados (só comandos de texto)

---

### 2. X Opportunity Alert — Alertas de Negócio

**Arquivo:** `scripts/x-opportunity-alert.ts`

**Status:** ✅ **ATIVO** — Cron a cada 2h

**Alertas enviados:**
- Oportunidades X.com (OSINT, GovTech, LGPD)
- Scoring de relevância (60-100)
- Análise por IA (DashScope + OpenRouter)

**Canais:**
- Telegram (HTML formatado)
- WhatsApp (Evolution API)

**Proposta de melhoria:** Adicionar botões: ✅ Aprovar, ❌ Rejeitar, 🔍 Ver

---

### 3. X Approval Bot — Aprovação de DMs

**Arquivo:** `scripts/x-approval-bot.ts`

**Status:** ⚠️ **PARCIAL** — Rodando mas sem interface de botões

**Comandos:**
- `/start` — Início
- `/status` — Pendentes
- `/approve <id>` — Aprovar DM
- `/reject <id>` — Rejeitar
- `/preview <id>` — Preview

**Problema:** Requer digitar comando + ID manualmente

**Solução proposta:** Inline keyboards com callback buttons

---

### 4. VPS RAM Monitor — Monitoramento Infra

**Arquivo:** `scripts/vps-ram-monitor.sh` (deploy: `/opt/egos/bin/`)

**Status:** ✅ **ATIVO** — Cron every 5 min

**Alertas:**
| Nível | Threshold | Emoji | Ação |
|-------|-----------|-------|------|
| Info | < 1GB | ℹ️ | Log apenas |
| Warning | < 500MB | ⚠️ | Telegram alert |
| Critical | < 100MB | 🚨 | Telegram + ações sugeridas |

**Qualidade:** ⚠️ **RUÍDO ALTO** — Alerta de 1GB é muito sensível para VPS com 2GB

**Recomendação:** Desativar alerta "info" (<1GB), manter only warning/critical

---

### 5. Gem Hunter — Gems Hot

**Arquivo:** `agents/agents/gem-hunter.ts`

**Status:** ✅ **ATIVO** — Envia gems de alta relevância

**Condição de alerta:** `relevance === "high" && score >= 80`

**Formato atual:** Markdown simples

**Proposta:** Rich format com botões: 📖 Wiki, 🔗 GitHub, ⭐️ Favoritar

---

### 6. Doc Drift Sentinel — Drift Documentação

**Arquivo:** `agents/agents/doc-drift-sentinel.ts`

**Status:** ⚠️ **ATIVO MAS VERIFICAR** — Pode estar enviando muitos alertas

**Alertas:**
- Divergência manifesto vs. realidade
- Arquivos órfãos
- Links quebrados

**Problema:** Se drift é alto, gera spam

**Recomendação:** Consolidar em 1 alerta diário com sumário, não individual

---

### 7. Drift Sentinel — Agente Fantasma

**Arquivo:** `agents/agents/drift-sentinel.ts`

**Status:** ⚠️ **VERIFICAR** — Após fix de 2026-04-03, deve estar OK

**Última ação:** Removido falsos positivos (kol-discovery, gem-hunter-api)

---

### 8. Gemini Quota Tracker — Uso de API

**Arquivo:** `scripts/gemini-quota-tracker.ts`

**Status:** ❓ **DESCONHECIDO** — Script existe mas não confirmado se está no cron

**Função:** Log diário de uso Gemini → Supabase

**Verificação necessária:** `crontab -l | grep gemini`

---

## 🚫 Sistemas para Desativar

### 1. OpenClaw — LEGADO

**Status:** ❌ **LEGADO / DESATIVAR**

**Histórico:** Gateway antigo na porta 18789, substituído por EGOS Gateway

**Ação:** Desativar serviço no VPS, manter documentação

**Comando:**
```bash
ssh root@egos.ia.br "systemctl stop openclaw && systemctl disable openclaw"
```

---

## 📱 WhatsApp Integration (Evolution API)

**Arquivo:** `apps/egos-gateway/src/channels/whatsapp.ts`

**Status:** ✅ **ATIVO** — Instância "forja-notifications"

**Número:** 553492374363

**Recursos:**
- Texto
- Áudio (transcrição Whisper)
- Imagem (Qwen-VL)
- Vídeo, documento, sticker

**Uso atual:**
- X Opportunity Alert (duplicado com Telegram)
- Gateway bidirecional limitado

**Proposta:** Consolidar — usar WhatsApp para alertas urgentes apenas, Telegram para interação rica

---

## 🎯 Proposta de Consolidação

### Princípios

1. **Um canal por propósito**
   - Telegram: Interação rica, comandos, botões
   - WhatsApp: Alertas críticos apenas

2. **Menos é mais**
   - Consolidar alertas similares
   - Sumários diários > alertas individuais

3. **Ação imediata**
   - Toda notificação deve ter botão de ação
   - Nada que requer digitação manual

### Nova Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    EGOS Unified Bot                     │
│                    (@EGOSin_bot)                        │
├─────────────────────────────────────────────────────────┤
│  Canais:                                                │
│  • Commands (texto) — para queries                      │
│  • Inline Buttons — para ações rápidas                │
│  • Menu Principal — navegação estruturada             │
├─────────────────────────────────────────────────────────┤
│  Módulos:                                               │
│  • 🎯 Tasks — criar, listar, concluir                  │
│  • 📊 Monitor — saúde sistema, recursos                │
│  • 🔍 X-Ops — oportunidades, aprovações                │
│  • 💎 Gems — descobertas, curadoria                    │
│  • ⚙️ Config — ambientes, variáveis                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Novos Comandos Propostos

### Gestão de Tasks

| Comando | Descrição | Ação no Sistema |
|---------|-----------|-----------------|
| `/task nova <título>` | Criar task | Adiciona ao TASKS.md |
| `/task lista` | Listar abertas | Query TASKS.md |
| `/task feita <id>` | Marcar concluída | Update TASKS.md + commit |
| `/task prioridade <id> <P0/P1/P2>` | Alterar prioridade | Update TASKS.md |

### Configuração de Ambientes

| Comando | Descrição | Ação no Sistema |
|---------|-----------|-----------------|
| `/env listar` | Listar ambientes | Scan VPS containers |
| `/env status <nome>` | Status de env | Health check |
| `/env restart <nome>` | Reiniciar serviço | Docker/docker-compose |
| `/env logs <nome>` | Ver logs | Tail remoto |
| `/env var <nome> <var>` | Ver variável | Read .env remoto |

### Monitoramento Consolidado

| Comando | Descrição |
|---------|-----------|
| `/status` | Dashboard geral (saúde, recursos, tasks abertas) |
| `/alertas` | Configurar quais alertas receber |
| `/silenciar <tipo>` | Pausar alertas por tipo |

---

## 📋 Plano de Implementação

### Fase 1: Limpeza (Hoje)

- [ ] Desativar OpenClaw no VPS
- [ ] Ajustar threshold RAM monitor (warning < 500MB, critical < 100MB, remover info)
- [ ] Consolidar Doc Drift em 1 alerta diário (manhã)
- [ ] Verificar Gemini Quota Tracker — ativar se não estiver

### Fase 2: Botões Básicos (Semana 1)

- [ ] Adicionar inline keyboard ao X Approval Bot
- [ ] Adicionar botões ao X Opportunity Alert
- [ ] Criar menu principal `/menu`

### Fase 3: Gestão de Tasks via Bot (Semana 2)

- [ ] Implementar `/task nova` — parser simples
- [ ] Implementar `/task lista` — query TASKS.md
- [ ] Implementar `/task feita` — update + auto-commit

### Fase 4: Configuração de Ambientes (Semana 3)

- [ ] Mapear todos os containers/serviços no VPS
- [ ] Criar API bridge para comandos Docker
- [ ] Implementar comandos `/env *`

### Fase 5: Consolidação Final (Semana 4)

- [ ] Unificar todos os bots em EGOS Gateway
- [ ] Criar sistema de plugin para novos comandos
- [ ] Documentar API interna

---

## 🔧 Tasks Criadas

**NOTIFY-001..010** adicionadas ao TASKS.md:

| ID | Task | Prioridade |
|----|------|------------|
| NOTIFY-001 | Desativar OpenClaw no VPS | P0 |
| NOTIFY-002 | Ajustar thresholds RAM monitor | P0 |
| NOTIFY-003 | Consolidar Doc Drift alerts diários | P0 |
| NOTIFY-004 | Adicionar botões ao X Approval Bot | P1 |
| NOTIFY-005 | Adicionar botões ao X Opportunity Alert | P1 |
| NOTIFY-006 | Criar comando `/task nova` | P1 |
| NOTIFY-007 | Criar comando `/task lista` | P1 |
| NOTIFY-008 | Criar comando `/task feita` | P1 |
| NOTIFY-009 | Mapear serviços VPS para `/env` | P1 |
| NOTIFY-010 | Criar menu principal `/menu` | P2 |

---

## 📊 Métricas de Sucesso

| Métrica | Antes | Depois (meta) |
|---------|-------|---------------|
| Fontes de alerta | 8 | 4 consolidadas |
| Alertas/dia (média) | ~20-30 | < 10 relevantes |
| Tempo para aprovar X oportunidade | 30s (digitação) | 3s (botão) |
| Capacidade de criar task via bot | ❌ Não | ✅ Sim |
| Capacidade de reiniciar serviço | ❌ SSH manual | ✅ /env restart |

---

## 📚 Referências

- SSOT: Este documento
- Gateway: `apps/egos-gateway/src/channels/telegram.ts`
- X-Ops: `scripts/x-opportunity-alert.ts`, `scripts/x-approval-bot.ts`
- WhatsApp: `apps/egos-gateway/src/channels/whatsapp.ts`
- VPS Monitor: `scripts/vps-ram-monitor.sh`

---

*Documento de auditoria criado em 2026-04-08. Próxima revisão: após implementação Fase 1.*
