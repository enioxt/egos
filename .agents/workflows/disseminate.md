---
description: Disseminação de governança/workflows do kernel para ~/.egos e leaf repos
---

# Workflow: /disseminate (Kernel -> Workspace)

## Objetivo
Propagar todas as mudanças canônicas de governança/workflows do `egos` para `~/.egos` e repositórios mapeados, com prova de drift zero.

## Comandos obrigatórios
```bash
EGOS_KERNEL=/workspace/egos bun run governance:sync:exec
EGOS_KERNEL=/workspace/egos bun run governance:check
```

> Fora do container, substitua `EGOS_KERNEL` para o caminho real do kernel (normalmente `$HOME/egos`).

## Critérios de sucesso
1. Sync executa sem erro.
2. `governance:check` retorna 0 drift.
3. Relatório final lista:
   - arquivos/superfícies propagadas,
   - limitações de ambiente,
   - próximos passos.

## Regras
- Nunca alterar frozen zones sem autorização explícita.
- Sempre registrar se houve limitação de ambiente (path/home/credenciais).
- Se houver drift residual, não encerrar sem plano de correção.
