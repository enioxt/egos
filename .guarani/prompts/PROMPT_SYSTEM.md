# EGOS Meta-Prompt System v2.0

> **Centralizado em:** `.guarani/prompts/`
> **Filosofia:** Um único ponto de ativação. Zero duplicação. Zero confusão.
> **Atualizado:** 2026-03-27

---

## Regra Fundamental

**Use apenas `/start`.** Não existe `/activation`, `/strategy`, `/brainstorm`, `/mycelium` ou `/audit` separados.

O `/start` detecta o contexto e ativa o modo correto automaticamente.

---

## Arquitetura

```text
.guarani/prompts/
├── PROMPT_SYSTEM.md             # Este arquivo
├── triggers.json                # Mapeamento: keyword → meta-prompt
└── meta/
    ├── egos-activation-governance.md  # ← ÚNICO META-PROMPT ATIVO (/start)
    ├── universal-strategist.md        # LEGADO (absorvido pelo /start)
    ├── brainet-collective.md          # LEGADO (absorvido pelo /start)
    ├── mycelium-orchestrator.md       # LEGADO (absorvido pelo /start)
    └── ecosystem-audit.md             # LEGADO (absorvido pelo /start)
```

---

## Como Usar

| Situação | Comando |
|----------|---------|
| Novo ambiente, health check | `/start` |
| Decisão estratégica | `/start` → MODO: ESTRATÉGIA |
| Brainstorm / multi-perspectiva | `/start` → MODO: RACIOCÍNIO COLETIVO |
| Sync de governance | `/start` → MODO: SYNC |
| Auditoria de repo | `/start` → MODO: AUDITORIA |
| Validação lógica / debate | Tsun-Cha Protocol |
| Extração de documentos policiais | Intelink meta-prompts |

---

## Modos do /start

O `/start` detecta automaticamente pelo contexto:

- **ATIVAÇÃO** — diagnóstico do sistema, pipeline 7-phase
- **ESTRATÉGIA** — decisão, negociação, game theory
- **RACIOCÍNIO COLETIVO** — brainstorm, multi-perspectiva (4 personas)
- **SYNC** — mycelium, mesh, reality table vs narrative
- **AUDITORIA** — análise de repo, code review, onboarding

---

## Prompts Especializados (não substituídos)

| ID | Arquivo | Quando usar |
|----|---------|-------------|
| `debate.tsun-cha` | `../philosophy/TSUN_CHA_PROTOCOL.md` | Validar hipótese, lógica, contradição |
| `extraction.police` | `apps/intelink/lib/intelink/meta-prompts.ts` | Extrair BO, depoimento, doc policial |

---

*"Menos prompts. Mais inteligência. Zero caixa preta."*
