---
description: Preparação de PRs (mensagem, contexto de ambiente, assinatura e checklist de validação)
---

# Workflow: /pr (PR Preparation Pack)

## Objetivo
Gerar PRs consistentes, auditáveis e prontos para revisão humana, com contexto explícito de ambiente e assinatura do agente.

## Entradas mínimas
- Branch atual
- Escopo da mudança
- Evidências de teste/check
- Limitações de ambiente (se houver)

## Execução recomendada
```bash
bun run pr:pack --title "[AREA] resumo da mudança" --out /tmp/pr-pack.md
bun run pr:gate --file /tmp/pr-pack.md
```

## Saída obrigatória (PR pack)
1. **Title**
   - Formato: `[AREA] ação principal + impacto`
2. **Motivation**
   - Problema real e risco de não fazer.
3. **What changed**
   - Lista objetiva por arquivo/superfície.
4. **Environment notes**
   - Exemplo: path esperado por scripts, ausência de credenciais, limitações de rede.
5. **Validation**
   - Comandos executados + status (pass/warn/fail) + motivo.
6. **Risk & rollback**
   - Risco operacional e como reverter rapidamente.
7. **Sign-off**
   - `Signed-off-by: EGOS Codex Agent <codex@egos.local>`
8. **Next Tasks**
   - Listar próximos itens abertos do `TASKS.md` (checklist real).
9. **Validação manual em IDE**
   - Declarar validação obrigatória pós-PR no Windsurf e Antigravity.

## Regras
- Nunca esconder falha de validação: registrar claramente warning/fail.
- Não afirmar deploy/integração externa sem prova observável.
- Referenciar frozen zones explicitamente quando não tocadas.
- Se for mudança só de docs/governança, dizer isso em texto direto.
