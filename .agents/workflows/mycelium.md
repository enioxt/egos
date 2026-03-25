---
description: Mycelium cross-repo synchronization and PR status mesh audit
---

# Workflow: /mycelium (Cross-Repo Mesh Audit)

## Objetivo
Criar visão integrada dos repositórios públicos e PRs ativos/inativos para orientar decisões de sincronização em lote.

## Passos
1. Rodar auditoria de PRs no ecossistema:
```bash
bun run pr:audit --owner enioxt --days 15
```
2. Classificar ação por grupo:
   - Open ativo (últimos 15 dias): acompanhar/revisar
   - Open inativo: decidir merge/close/revive
   - Closed unmerged recente: revisar motivo
3. Rodar disseminação do kernel:
```bash
EGOS_KERNEL=/workspace/egos bun run governance:sync:exec
EGOS_KERNEL=/workspace/egos bun run governance:check
```
4. Publicar resumo com:
   - estado da malha
   - bloqueios
   - próximas 3 ações

## Regra ética
Aplicar ATRiAN: não recomendar merge automático sem evidência técnica + risco aceitável.
