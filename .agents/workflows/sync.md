---
description: Sincronização Global de Governança EGOS (Kernel -> Leaf Repos)
---
# Workflow: Sincronização de Governança (/sync)

Este workflow descreve o procedimento exato para disseminar regras, metaprompts, identidades e workflows do Kernel EGOS para todos os repositórios filhos do ecossistema. Sempre que houver uma mudança de regra mestra, este procedimento **DEVE** ser executado.

## O que este workflow faz?
Ele pega a SSOT (Single Source of Truth) definida nas pastas `.guarani` e `.agents` do repositório raiz `/home/enio/egos/` e espalha via symlinks ou cópia hard para os repositórios conectados (ex: `852`, `carteira-livre`, `br-acc`).

## Execução Passo a Passo

### Passo 1: Dry-Run (Teste de Deriva / Drift)
O agente deve sempre checar se a sincronização destruirá algum arquivo divergente antes de rodar o modo de execução.
```bash
cd /home/enio/egos
bun run governance:sync
```

### Passo 2: Sincronização Local (Apenas ~/.egos)
Se a intenção for apenas atualizar as regras globais da máquina sem tocar nos repositórios:
```bash
cd /home/enio/egos
bun run governance:sync:local
```

### Passo 3: Execução Total (Disseminação Completa)
Para espalhar forçosamente por todo o ecossistema (O equivalente real ao antigo `/disseminate` profundo):
```bash
cd /home/enio/egos
bun run governance:sync:exec
```

> **Aviso de Segurança:** Após a execução, o agente deve relatar quais repositórios sofreram atualização.
