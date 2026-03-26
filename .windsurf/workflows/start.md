---
description: start workflow (compatibility wrapper)
---

# /start (Compatibility Wrapper)

Este arquivo mantém compatibilidade com superfícies legadas do Windsurf.

## Fonte canônica
- Workflow canônico operacional: `.agents/workflows/start-workflow.md`

## Comportamento
1. Carregar e executar `.agents/workflows/start-workflow.md` como SSOT.
2. Tratar regras específicas do cliente Windsurf apenas como camada de compatibilidade.
3. Em caso de conflito, prevalece o conteúdo de `.agents/workflows/start-workflow.md`.

## Doctor Command Integration
O workflow /start executa a validação de ambiente via `bun run doctor --json` na fase GATE:
- **Report Location**: `docs/_generated/doctor-report.json` (timestamped)
- **Health Categories**: env, file, provider, hooks, workspace, governance
- **Exit Codes**: 0 (ok), 1 (warnings), 2 (failures)
- **Flags**: `--doctor-skip` para contorno, `--fix` para auto-fixes

## Saída obrigatória
- `✅ /start concluído — Kernel ativo`
- Resumo com fatos verificados, inferências e propostas
- Doctor health score e recommendations (se houver alertas)
