# SSOT Rules — Anti-Dispersão de Conteúdo
> Version: 1.0.0 | Created: 2026-04-06

## Princípio

Um domínio = um arquivo SSOT. Qualquer conteúdo sobre aquele domínio VAI para o SSOT, nunca para arquivo novo.

## Mapa canônico

| Domínio | SSOT |
|---------|------|
| GTM, social, outreach, equity, parceiros | `docs/GTM_SSOT.md` |
| OpenClaw config | `docs/OPENCLAW_SSOT.md` |
| Tasks e prioridades | `TASKS.md` |
| Capabilities e agentes | `docs/CAPABILITY_REGISTRY.md` |
| Credenciais e infra | `~/.openclaw/workspace/TOOLS.md` |
| Learnings técnicos | `docs/knowledge/HARVEST.md` |
| Handoffs entre sessões | `docs/_current_handoffs/handoff_YYYY-MM-DD.md` |

## Diretórios proibidos para conteúdo operacional

- `docs/business/` → use GTM_SSOT.md
- `docs/sales/` → use GTM_SSOT.md
- `docs/notes/`, `docs/tmp/` → não criar

## Checklist antes de criar arquivo de doc

1. Existe SSOT para este domínio? → adicione ao SSOT
2. Não existe SSOT? → crie `docs/DOMINIO_SSOT.md` e registre aqui

## Incidente motivador

P28 (2026-04-06): GTM content disperso em 7 arquivos. Encontrar termos de equity exigiu busca em 4 arquivos. Consolidado em GTM_SSOT.md.
