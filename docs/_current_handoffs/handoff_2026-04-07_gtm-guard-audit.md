# Handoff — 2026-04-07 (GTM + Guard Brasil Audit + Chatbot Sprint)

**Session commits:** 17 | **TASKS.md:** 506 lines | **Branch:** main | **Wiki:** 72 páginas

---

## Accomplished

### GTM / M-007
- **3/5 emails enviados** — Nubank, Memed, RD Station (assuntos como perguntas, CTA baixa fricção, 100% PT-BR, `enioxt@gmail.com`, `Fundador`)
- **2 falharam** — `contact@lgpd-brasil.com.br` (domínio inexistente), `contato@rocketseat.com.br` (não aceita). Task M-007-FIX criada.

### Guard Brasil Sandbox Audit
- Testados 6 demos do frontend contra API real → 2 ✅, 2 ❌, 2 ⚠️
- **GUARD-BUG-001**: RG não detectado (regex inativa)
- **GUARD-BUG-002**: ATRiAN bias completamente inativo (texto racista → score 100)
- **GUARD-SEC-001**: `/dashboard-v1` público sem auth (placeholders visíveis externamente)
- Tasks criadas: GUARD-BUG-001..006 + GUARD-SEC-001

### RATIO Infrastructure
- **RATIO-VPS-001/002/003 ✅** — LanceDB synced, Neo4j healthy, Caddy routes live

### Chatbot Sprint (commits desta sessão)
- `atrian-stream.ts` — filtro ATRiAN stream-time (CHAT-001)
- `circuit-breaker` em model-router (CHAT-006)
- `prompt-assembler.ts` — schema-driven (CHAT-003)
- `eval harness` — GoldenCase runner com scoring (CHAT-009)
- Guard Brasil partial masking mode (`***.456.789-**`)

### Hermes (sessão anterior, finalizado)
- HERMES-001..004 ✅ — v0.7.0 local + VPS, Claude OAuth, cron refresh, Haiku default

### HQ Integration
- 8/9 serviços live. HQI-001..007 done.

---

## In Progress

- **HERMES-005 trial** (80%) — monitor até 2026-04-15, gate go/no-go
- **M-007** (60%) — 3/5 enviados, aguardar respostas (follow-up em 7d)
- **CHAT-001..031** — P0s parcialmente feitos (CHAT-001/003/006/009), restam CHAT-002/004/005/007/008/010

---

## Blocked

- **M-007-FIX**: emails Rocketseat + LGPD Brasil inválidos — buscar na página `/contato` dos sites ou LinkedIn
- **GUARD-BUG-001/002**: sandbox não pode ser mostrado a prospects antes de corrigir RG + ATRiAN
- **GUARD-SEC-001**: `/dashboard-v1` deve ser protegido com auth ANTES de qualquer demo para prospect

---

## Next Steps (prioridade)

1. **GUARD-SEC-001** — proteger `/dashboard-v1` com middleware Next.js (30min)
2. **GUARD-BUG-001** — corrigir regex RG (`12.345.678-9` não detectado)
3. **GUARD-BUG-002** — ativar ATRiAN bias detection (motor desligado ou não configurado)
4. **M-007-FIX** — encontrar emails corretos Rocketseat (Diego Fernandes LinkedIn) + LGPD Brasil
5. **GTM-002** — X.com thread (4 tweets, rascunhos prontos)
6. **CHAT-002/004/005/007/008/010** — continuar sprint chatbot

---

## Environment State

| Serviço | Status |
|---------|--------|
| Guard Brasil API | ✅ v0.2.2 healthy |
| RATIO VPS | ✅ ratio.egos.ia.br + ratio-api.egos.ia.br live |
| Hermes local | ✅ v0.7.0, cron ativo |
| Hermes VPS | ✅ credenciais sincronizadas |
| VPS RAM | 5.4GB / 15GB usado |
| Wiki KB | ✅ 72 páginas (avg quality 80/100) |
| `/dashboard-v1` | ⚠️ **PÚBLICO SEM AUTH** — corrigir urgente |
| Sandbox (RG + ATRiAN) | ❌ bugs críticos — não mostrar a prospects |

---

## Notas de Segurança

**GUARD-SEC-001 é P0:** o dashboard em `/dashboard-v1` está acessível sem autenticação. Embora mostre apenas placeholders, a estrutura do produto e os menus internos ficam expostos. Qualquer prospect ou concorrente com a URL pode ver.
