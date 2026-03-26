---
description: Ativação canônica do kernel + plano de execução EGOS/BLUEPRINT para Claude Code/Codex
---

# Workflow: /start (Kernel Activation + Placement Plan)

## Objetivo
Ativar o kernel EGOS com checagem de governança, carregar contexto SSOT e preparar um plano executável por fases (curto, médio e longo prazo) sem criar drift entre `egos` e `BLUEPRINT-EGOS`.

## Ordem obrigatória (7 fases)

1. **INTAKE**
   - Ler: `AGENTS.md`, `TASKS.md`, `.windsurfrules`, `docs/SYSTEM_MAP.md`.
   - Confirmar data da sessão e registrar no resumo.

2. **CHALLENGE**
   - Verificar contradições entre pedido e frozen zones.
   - Se houver ambiguidade sobre escopo, assumir postura conservadora: atualizar SSOT primeiro, código depois.

3. **PLAN**
   - Definir onde cada artefato deve viver:
     - **Comandos `/` e operação**: `.agents/workflows/`
     - **Prioridades e fases**: `TASKS.md`
     - **Mapa e encaixe arquitetural**: `docs/SYSTEM_MAP.md`
     - **Capacidades reutilizáveis**: `docs/CAPABILITY_REGISTRY.md`

4. **GATE** (Quality & Environment Checks) - BLOCKING GATE
   - **Doctor Validation**: Executar `bun run doctor --json` para capturar estado de saúde do ambiente (exit code governa fluxo):
     - Exit 0 (✅): Todos checks ok — prosseguir
     - Exit 1 (⚠️): Apenas warnings — log recommendations no session report, permitir continuar
     - Exit 2 (❌): Failures bloqueantes — oferecer `--doctor-skip` ou `bun run doctor:fix` para contorno
     - Report JSON salvo em `docs/_generated/doctor-report.json` com timestamp
   - **Rodar `bun run governance:check`** antes de mudanças estruturais.
   - **Worktree Orchestration Check (EGOS-110)**: Executar `bun scripts/worktree-validator.ts --status` para validar concorrência, ownership locks, e lifecycle state.
     - Falha crítica se concurrency > 5/5 (bloqueia nova branch)
     - Warning se há branches stale (7-30 dias) ou abandoned (> 30 dias)
     - Sempre reportar ownership metadata para evitar conflicts
   - Nunca editar frozen zones sem pedido explícito.

5. **EXECUTE**
   - Aplicar mudanças de documentação/planejamento em SSOT.
   - Se houver integração do BLUEPRINT, iniciar por contrato/interface e só depois migração física de módulos.

6. **VERIFY**
   - Rodar validações mínimas:
     - `bun run doctor` (verificação de integridade do ambiente — report em `docs/_generated/doctor-report.json` com timestamp, health score, e recommendations)
     - `bun run agent:lint`
     - `bun run typecheck` (quando houver mudança de código TS)
     - `bun run governance:check`
   - Incluir doctor-report.json (lido de `docs/_generated/`) no bloco de saída final do /start

7. **LEARN**
   - Registrar no retorno final:
     - o que foi alterado,
     - onde foi alterado,
     - próximos passos priorizados (P0/P1/P2).

## Plano de fases para executar após /start

### Fase 1 (0-7 dias)
- Consolidar `/start` como workflow oficial e eliminar variantes conflitantes.
- Criar backlog de integração BLUEPRINT orientado a contratos (sem big bang).
- Definir checklist de prova para qualquer claim de "agent online".

### Fase 2 (1-4 semanas)
- Implementar "bridge" de capacidades do BLUEPRINT em `packages/shared` por adapters.
- Adicionar testes reais de recuperação/contexto antes de afirmar ganhos de AAR.
- Preparar piloto com 1 fluxo de receita validado (split + compliance).

### Fase 3 (1-3 meses)
- Evoluir para arquitetura estável de marketplace governado com gates de risco.
- Automatizar auditoria de drift cross-repo no ciclo de PR.
- Medir adoção por métricas: tempo de ativação, taxa de sucesso de workflows, custo por task.

## Regras de resposta do comando /start
- Não afirmar leitura de "todos os repositórios" sem evidência.
- Sempre separar: **fatos verificados**, **inferências**, **propostas**.
- Final obrigatório:
  - `✅ /start concluído — Kernel ativo`
  - bloco "Próximas 3 ações" com dono e ordem.

## Contrato Evidence-First (/start)

Toda saída de `/start` deve seguir este formato mínimo:

1. **Fatos verificados (com prova observável)**
   - arquivos/comandos realmente lidos/executados
   - estado atual confirmado
2. **Inferências**
   - hipóteses derivadas dos fatos, marcadas como inferência
3. **Propostas**
   - próximos passos priorizados, com dependências e risco

Checklist de bloqueio:
- Se um item não tiver evidência, ele NÃO entra em "Fatos verificados".
- Se houver limitação de ambiente, explicitar imediatamente.

## Doctor Command Reference

O comando `doctor` valida a saúde completa do ambiente EGOS antes de operações críticas:

### Uso

```bash
bun run doctor              # Validação completa (modo dry-run, relatório apenas)
bun run doctor:codex       # Doctor para ambiente Codex (shell script legacy)
bun run doctor:fix         # Tenta auto-fixes comuns (env vars, hooks, stale docs)
bun run doctor --json      # Saída em JSON (programática)
bun run doctor --fix       # Executa fixes automáticos quando possível
bun run doctor --no-network # Modo offline (pula checks de API)
bun run doctor --doctor-skip # Pula doctor, permite execução mesmo com falhas
```

### Categorias de Validação

1. **Environment** — API keys (Alibaba, OpenRouter) e vars opcionais
2. **Files** — Freshness de AGENTS.md, TASKS.md, .windsurfrules, SYSTEM_MAP.md (< 7 dias)
3. **Providers** — Reachability de LLM APIs (Alibaba DashScope, OpenRouter, OpenAI)
4. **Hooks** — Instalação de pre-commit hooks (Husky)
5. **Workspace** — Git status (clean/dirty), upstream sync, branch state
6. **Governance** — Drift detection via `governance:check`

### Exit Codes

- `0` — Todos os checks passaram (✅ ready)
- `1` — Apenas warnings (⚠️  proceder com cautela)
- `2` — Failures detectadas (❌ bloqueia até fix)

### Report Location

`docs/_generated/doctor-report.json` — timestamped, contém:
- Summary (health score, contagem de ok/warn/fail)
- Results detalhados por categoria
- Recommendations automáticas para cada problema
