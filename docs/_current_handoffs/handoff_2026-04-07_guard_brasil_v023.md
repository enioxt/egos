# Session Handoff — Guard Brasil v0.2.3 + Bug Fixes (2026-04-07)

**Branch:** main | **Commits esta sessão:** 2 | **Tests:** 20/20

---

## ✅ DELIVERABLES

### Guard Brasil v0.2.3 — 3 bugs corrigidos

| Bug | Arquivo | Fix | Commit |
|-----|---------|-----|--------|
| BUG-003 (nome) | `packages/guard-brasil/src/lib/pii-scanner.ts` | DEFAULT_NAME_PATTERN expandido para 12 labels civis | 8b45fde |
| BUG-004 (saúde) | `packages/guard-brasil/src/pii-patterns.ts` | HEALTH_CONDITION_PATTERN + PIICategory health_data | 8b45fde |
| BUG-006 (version) | `packages/guard-brasil/src/guard.ts` | GUARD_VERSION '0.2.1' → '0.2.2' | 8b45fde |

### Testes verificados (node --input-type=module):
```
nome label:   "Nome: João da Silva mora..."  → [{cat:"name", matched:"João da Silva"}] ✅
paciente:     "Paciente: Maria Santos..."    → [{cat:"name", matched:"Maria Santos"}] ✅  
HIV portador: "portador de HIV positivo..."  → [{cat:"health_data", ...}] ✅
diagnóstico:  "diagnosticado com diabetes..." → [{cat:"health_data", ...}] ✅
RG standalone: "12.345.678-9"               → [{cat:"rg", ...}] ✅
false positive MG: "delegacia de MG"        → [] ✅ (not flagged)
```

### TASKS.md atualizado (482 linhas)
- GUARD-BUG-003 ✅ | GUARD-BUG-004 ✅ | GUARD-BUG-006 ✅
- CAPABILITY_REGISTRY §5 Guard Brasil: v0.2.0 → v0.2.3, 15 → 16 patterns
- HARVEST.md: KB-021 adicionado

---

## 🚨 AÇÕES MANUAIS (ENIO faz — não delegável)

1. **DASHBOARD_SECRET no Vercel** — bloqueante (dashboard retorna 503 sem isso):
   ```bash
   openssl rand -hex 32   # gera o secret
   # Vercel → guard-brasil-web → Settings → Environment Variables
   # DASHBOARD_SECRET=<o valor gerado>
   # Redeploy
   ```

2. **M-007-FIX** — 2 emails pendentes (rascunhos prontos):
   - Rocketseat: `oi@rocketseat.com.br`
   - LBCA Advogados: `lgpd@lbca.com.br`

3. **XMCP-001** — X credentials 401 (manual no developer.twitter.com):
   - Regenerar: Apps → Keys and Tokens → Regenerate
   - Atualizar `.env` e VPS `/opt/xmcp/.env`

---

## 📋 PRIORITY QUEUE (próxima sessão)

### P0 — Publish npm (agente pode fazer)
```bash
cd /home/enio/egos/packages/guard-brasil
npm publish --access public
# Then update guard-brasil-web:
# "dependencies": { "@egosbr/guard-brasil": "^0.2.3" }
# bun install && git commit
```

### P1 — Guard Brasil demos (4/6 → 6/6)
- Sandbox agora cobre: RG, CPF, nome, condição médica ✅
- Verificar que sandbox usa a v0.2.3 (guard-brasil-web ainda tem `^0.1.0` no package.json!)

### P1 — GTM (bloqueado por XMCP-001 manual)
- **GTM-002**: Thread X.com (4 tweets em GTM_SSOT.md §4.1) — UNBLOCKED após XMCP-001
- **GTM-X-001**: Thread MemPalace+CORAL (trending) — idem

### P1 — Chatbot (CHAT-011..022)
Ver TASKS.md §Chatbot — próximo sprint: structured output, runAgentLoop, semantic memory, OTel

### P1 — MEM-001: MemPalace benchmark
```bash
pip install mempalace
mempalace mine --mode convos
# Compare R@5 vs file-based memory (gate: ≥80%)
```

### P1 — CORAL-001: gem_discoveries Supabase table
- Schema: `{id, repo_url, gem_name, category, score, discovered_by, discovered_at, summary, tags[], last_seen_at}`
- Migration em `supabase/migrations/`

---

## 📊 Estado do Guard Brasil (todos os bugs)

| Bug | Status | Commit |
|-----|--------|--------|
| BUG-001: RG standalone | ✅ v0.2.2 | 185b0f7 |
| BUG-002: ATRiAN bias | ⚠️ Feature nunca existiu — demo corrigido | N/A |
| BUG-003: Nome pessoa | ✅ v0.2.3 | 8b45fde |
| BUG-004: Condição médica | ✅ v0.2.3 | 8b45fde |
| BUG-005: Whitelist falsos positivos | ✅ v0.2.2 | 185b0f7 |
| BUG-006: Version inconsistente | ✅ v0.2.3 | 8b45fde |
| SEC-001: Dashboard público | ✅ middleware.ts | 185b0f7 |

**Sandbox cobertura:** 6/6 demos funcionam após publicar v0.2.3 e atualizar guard-brasil-web.

---

## ⚠️ Contexto crítico para próxima sessão

- **ATRiAN** não detecta viés racial — nunca foi implementado. Motor detecta: absolute_claim, fabricated_data, false_promise, invented_acronym. Feature futura (não P1).
- **HERMES-005** trial roda até 2026-04-15 — só monitorar logs, não interromper.
- **guard-brasil-web** ainda usa `@egosbr/guard-brasil@^0.1.0` — publicar 0.2.3 no npm e atualizar.
- **19 LLMRefs stale** em docs (não-bloqueante): `python3 scripts/qa/llmrefs_staleness.py --root .`

---

**Disseminação:** CAPABILITY_REGISTRY ✅ | HARVEST.md ✅ | TASKS.md ✅ | memory ✅ | git push ✅
