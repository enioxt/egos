# Handoff — 2026-04-07 (Sessão Final)
# Chatbot P0 Complete + Guard Brasil Partial Masking + Credentials + X.com v2.0

## Accomplished

### Guard Brasil Partial Masking
- [pii-patterns.ts](packages/guard-brasil/src/pii-patterns.ts) — `MaskMode`, `partialMaskFn` (CPF/CNPJ/telefone/email)
- [public-guard.ts](packages/guard-brasil/src/lib/public-guard.ts) — `maskMode` em `PublicGuardConfig`
- [guard.ts](packages/guard-brasil/src/guard.ts) — `maskMode` em `InspectOptions`
- [server.ts](apps/api/src/server.ts) — `mask_mode` em `POST /v1/inspect`
- API: `{ "mask_mode": "partial" }` → CPF vira `***.456.789-**`

### Chatbot SSOT v2.0 — P0 completos (CHAT-001..010)
- CHAT-003: [prompt-assembler.ts](packages/shared/src/prompt-assembler.ts) — PromptSection schema + createAssembler
- CHAT-005: [memory-store.ts](packages/shared/src/memory-store.ts) — MemoryStore (Supabase/InMemory/Null)
- CHAT-008: [rate-limit.ts](../852/src/lib/rate-limit.ts) — per-identity budget (auth 50/anon 20/unknown 12)
- CHAT-009: [eval/runner.ts](packages/shared/src/eval/runner.ts) + [852.ts](../852/src/eval/golden/852.ts) — 20 golden cases
- CHAT-010: [egos-web api/_chat-guard.ts](../egos-lab/apps/egos-web/api/_chat-guard.ts) — input PII scan + session budget

### Credential Audit + Rotation
- Auditados 15 keys. 5 mortas encontradas.
- Rotacionadas: GITHUB_TOKEN, HUGGINGFACE_TOKEN, BRAVE_API, X.com (5 tokens)
- ANTHROPIC_API_KEY: ainda morta (baixa prioridade — Claude Code usa key própria)
- SSOT: [infra_credentials_ssot.md](~/.claude/projects/-home-enio-egos/memory/infra_credentials_ssot.md)

### X_POSTS_SSOT v2.0
- [X_POSTS_SSOT.md](docs/social/X_POSTS_SSOT.md) — reescrito de 610→379 linhas
- Nova estratégia: DMs pessoais → encontrar builders alinhados
- 6 templates DM + 5 posts públicos + regras de automação + targeting guide
- XMCP-001 ✅ (X credentials válidas agora)

### Disseminate
- HARVEST.md: KB-022..027 (6 novos padrões)
- CAPABILITY_REGISTRY.md: §19-§22 (partial masking, prompt-assembler, MemoryStore, eval)
- TASKS.md: XMCP-001 done, SOCIAL-003..006 adicionados

## In Progress (~0%)

- **XMCP-002**: Atualizar /opt/xmcp/.env no VPS com X keys rotados (desbloqueado)
- **RATIO-001**: PR #2 Guard Brasil para Carlos Victor Rodrigues
- **CHAT-011..022**: P1 chatbot tasks (structured output, multimodal, semantic memory...)

## Blocked

- **ANTHROPIC_API_KEY**: Dead. Qualquer código que leia `process.env.ANTHROPIC_API_KEY` vai falhar. Regenerar em console.anthropic.com quando necessário.
- **SOCIAL-004**: Fila de DMs depende de XMCP-002 (VPS xmcp rodando)

## Next Steps (por prioridade)

1. **XMCP-002** — atualizar /opt/xmcp/.env no VPS: `ssh hetzner; cd /opt/xmcp; vim .env; bash start.sh`
2. **Enviar 5 DMs manuais** usando os templates do X_POSTS_SSOT v2.0 (§4)
3. **RATIO-001** — PR #2 Guard Brasil no repo carlosvictorodrigues/ratio
4. **CHAT-011** — structured outputs (próximo P1 chatbot)
5. **GOV-TECH-005** — Brief "Ouvidoria Municipal + LGPD SaaS" (R$30k-80k/ano)

## Environment State

| Repo | Last commit | Tests | Build |
|------|-------------|-------|-------|
| egos | 8b03f06 | `bun test` — ok | `bun typecheck` — 0 errors |
| 852 | e0fe326 | `npx tsc --noEmit` — 0 errors | ok |
| egos-lab | f9d8bd6 | `npx tsc --noEmit` — 0 errors | ok |

**VPS:** 19 containers, guard.egos.ia.br live, ratio.egos.ia.br live.
**X.com:** todos 5 tokens válidos em ~/.egos/secrets.env.
**Uncommitted egos:** 13 files (playwright ymls, govtech docs, settings) — não críticos.
