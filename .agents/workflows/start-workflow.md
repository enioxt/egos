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

4. **GATE**
   - Rodar `bun run governance:check` antes de mudanças estruturais.
   - Nunca editar frozen zones sem pedido explícito.

5. **EXECUTE**
   - Aplicar mudanças de documentação/planejamento em SSOT.
   - Se houver integração do BLUEPRINT, iniciar por contrato/interface e só depois migração física de módulos.

6. **VERIFY**
   - Rodar validações mínimas:
     - `bun run agent:lint`
     - `bun run typecheck` (quando houver mudança de código TS)

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
