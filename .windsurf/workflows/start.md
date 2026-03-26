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

## Saída obrigatória
- `✅ /start concluído — Kernel ativo`
- Resumo com fatos verificados, inferências e propostas.
