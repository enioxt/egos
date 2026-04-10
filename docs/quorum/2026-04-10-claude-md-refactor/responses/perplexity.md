<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## Correção Crítica Urgente

**Enio, preciso corrigir um erro grave na análise anterior.**

A análise consolidada que entreguei estava **contaminada por alucinação propagada**. Eu assumi que você estava construindo um "marketplace de instrutores autônomos de trânsito" baseado nas conversas com ChatGPT/Gemini/Grok - mas isso foi uma **alucinação cruzada entre LLMs**.[^1][^2]

**A realidade (verificada nos arquivos que você acabou de enviar):**

- **EGOS** = ecossistema open-source brasileiro de agentes de IA com governança embutida
- **Forja** = ERP industrial para metalúrgicas (não marketplace de instrutores)
- **7 repos ativos**: egos kernel, 852, forja, egos-inteligencia, br-acc, policia, arch
- **19 agentes registrados**, VPS Hetzner com 19 containers Docker
- **R\$ 0 MRR** (0 clientes pagantes) - gap a fechar
- **Guard Brasil API**: 16 padrões PII, 4ms response, live
- **852**: chatbot público (852.egos.ia.br)
- **br-acc**: Neo4j com 83.7M nós de dados públicos brasileiros[^2][^1]

**O que aconteceu:**
Perplexity e Kimi alucinaram "marketplace de instrutores autônomos" e cada LLM subsequente confiou na análise anterior sem verificar. Isso é exatamente o que seu **§33 Evidence-First Principle** existe para prevenir.[^2]

***

## Auditoria Crítica do CLAUDE.md

Vou executar agora a auditoria que você solicitou no meta-prompt. Serei brutal e direto conforme instruções.[^1]

### 1. Tabela de Classificação (§0 a §33)

| Seção | Título | Classificação | Justificativa |
| :-- | :-- | :-- | :-- |
| §0 | Identity \& Posture | **B** | Conceito essencial, mas inchado. "Investigative, proactive, questioning" é o core - resto é prolixo |
| §1 | Mandatory Verification Gates | **A** | Essencial. Previne exatamente o tipo de alucinação que contaminou minha análise anterior |
| §2 | Context Management | **A** | Critical para evitar autocompact e perda de contexto em sessões longas |
| §3 | Edit Safety Protocol | **A** | Previne INC-002 (perda de commits). Core safety |
| §3.1 | Pre-Work Rule | **C** | Redundante com §3. Fundir |
| §4 | Sub-Agent Swarm Rules | **B** | Útil mas pode comprimir 40%. Parallel/sequential pattern é o essencial |
| §5 | EGOS-Specific Rules | **A** | Frozen zones + SSOT hierarchy. Impossível operar sem isso |
| §6 | Response Quality Rules | **C** | Senso comum. LLMs modernos já fazem isso. Eliminar ou fundir com §0 |
| §7 | Security Non-Negotiables | **A** | 4 linhas. Perfeito. MANTER |
| §8 | Integration Awareness | **B** | Útil mas desatualizado rápido. Mover para `egos-rules/integrations.md` |
| §9 | Forced Verification | **A** | Override crítico. Employee-grade behavior |
| §10 | Useful Repos \& References | **C** | Lista externa. Não pertence ao rulebook. Mover para HARVEST.md |
| §11 | Codebase-Memory-MCP | **A** | Game changer. Reduz Grep/Read em 70% |
| §12 | Scheduled Jobs | **C** | Redundante com `egos-rules/jobs-monitoring.md`. Apenas link |
| §13 | Model Selection Guide | **C** | Redundante com `egos-rules/llm-routing.md`. Apenas link |
| §14 | Swarm Execution Rules | **A** | Read-Parallel / Write-Sequential. Previne merge conflicts. Core |
| §15 | Maximum Autonomy Mode | **B** | Conceito correto mas tom motivacional. Comprimir 50% |
| §16 | Challenge Mode | **D** | Aspirational. "Seja chato comigo" não é enforced. Eliminar ou mover para posture |
| §17 | Snapshot Versioning | **C** | Procedimento específico. Mover para `scripts/snapshot.sh` |
| §18 | Disseminate Everywhere | **B** | Core concept, mas lista de locais fica stale. Gerar dinamicamente |
| §19 | Meta-Prompt Activation | **B** | Importante mas pode comprimir. Essência: "Load full context before meta-prompts" |
| §20 | Investigation Protocol | **C** | Redundante com §0 (posture) + §33 (evidence-first). Fundir |
| §21 | Enio's Vocabulary Map | **A** | Crítico. Previne confusão Mycelium/ARR/etc. MANTER |
| §22 | Chatbot Everywhere | **D** | Aspirational. Não há enforcement. Mover para product roadmap |
| §23 | Product-First Mindset | **B** | Filosofia importante mas 60% é narrativo. Core: "showcase-first, no revenue anxiety" |
| §24 | Enio Rocha Profile | **B** | Útil para contexto mas meio motivacional. Comprimir 50% |
| §24.1 | No Jobs Rule | **A** | Hard constraint. Previne waste. MANTER |
| §25 | Git Push Protocol | **A** | Previne INC-001. Não negociável. MANTER |
| §26 | SSOT-First Rule | **A** | Anti-dispersão. Core architecture principle |
| §27 | Doc-Drift Shield | **A** | Evidence-first enforcement layer. Critical |
| §28 | Auto-Disseminate Pipeline | **C** | Redundante com `egos-rules/jobs-monitoring.md` |
| §29 | Auto-Research | **C** | Redundante com §12 |
| §30 | Incidental Findings Protocol | **A** | Decision tree claro. Previne scope creep |
| §31 | TASKS.md Anti-Hallucination | **A** | Previne INC-003. Verification before task creation |
| §32 | Repo Map | **B** | Útil mas desatualizado rápido. Gerar de `ECOSYSTEM_REGISTRY.md` |
| §33 | Evidence-First Principle | **A** | Regra canônica. Toda a auditoria valida sua necessidade |

**Resumo:**

- **A (Essencial):** 14 seções
- **B (Útil mas inchado):** 9 seções
- **C (Redundante):** 8 seções
- **D (Aspirational):** 2 seções
- **E (Contra-produtivo):** 0 seções


### 2. Top 5 Seções para Eliminar

1. **§6 (Response Quality)** — Senso comum de LLM moderno. Eliminar.
2. **§10 (Useful Repos)** — Lista externa. Mover para HARVEST.md.
3. **§16 (Challenge Mode)** — Não é enforced. Eliminar ou fundir com §0.
4. **§22 (Chatbot Everywhere)** — Product roadmap, não rulebook. Eliminar.
5. **§29 (Auto-Research)** — Duplica §12. Eliminar.

### 3. Top 5 Seções para Comprimir

1. **§0 (Identity \& Posture)** — Cortar para 4 linhas: "Investigative. Question assumptions. Propose alternatives. Label facts/inferences/proposals."
2. **§15 (Maximum Autonomy)** — Cortar lista. Core: "ACT FIRST. Only stop for: human login, >R\$50 spend, irreversible data loss."
3. **§23 (Product-First)** — Cortar narrativa. Core: "Every feature → who uses + how found. No revenue anxiety. Showcase-first."
4. **§24 (Enio Profile)** — Cortar para 6 linhas: commits/mês, produtos live, R\$0 MRR gap, quer pesquisar/construir/colaborar, NOT apply jobs.
5. **§19 (Meta-Prompt)** — Cortar para 2 linhas: "If first prompt = meta, load TASKS/agents/HARVEST/jobs first."

### 4. Top 3 Regras que Faltam

#### **Regra Faltante 1: Conflitos entre Sessões Paralelas**

**Problema:** §14 tem read-parallel/write-sequential mas não há protocolo para quando 2 humanos + N agents trabalham no mesmo repo simultaneamente.

**Proposta:**

```markdown
## §34. PARALLEL HUMAN PROTOCOL

Quando múltiplas janelas/agentes trabalham no mesmo repo:
1. **Antes de começar:** `git fetch && git status` — se há uncommitted changes de outra sessão, pergunte ao humano
2. **TASKS.md lock:** Primeira ação em qualquer sessão = commit TASKS.md se modificado. Outras sessões só veem estado committed
3. **Collision detection:** Se git pull traz conflito em arquivo que você acabou de ler, STOP e re-read antes de edit
4. **Handoff rule:** Ao terminar sessão longa (>30min), commit + push. Não deixe working tree dirty
```


#### **Regra Faltante 2: Quando Escalar (1 pessoa → 2-5)**

**Problema:** Regras fazem sentido para 1 dev + agents. O que muda quando Enio encontrar primeiro co-builder?

**Proposta:**

```markdown
## §35. SCALING TRIGGERS

**Enquanto solo (atual):**
- TASKS.md pode ter 500 linhas
- Commits direto na main OK (hooks são safety net)
- CLAUDE.md versão única global

**Quando 2º humano regular aparece:**
- TASKS.md split em `TASKS_KERNEL.md` + `TASKS_PRODUCT.md`
- Branch strategy: `feat/*` obrigatório, PR review antes de main
- CLAUDE.md versionado: `CLAUDE_KERNEL.md` + `CLAUDE_PRODUCT.md`

**Trigger explícito:** 3+ commits/semana de outro dev por 2 semanas = activate scaling mode
```


#### **Regra Faltante 3: Quando NÃO Usar IA**

**Problema:** O rulebook assume IA everywhere. Falta lista de "quando desligar o autopilot".

**Proposta:**

```markdown
## §36. AUTOPILOT OFF ZONES

**NEVER delegate to agents:**
1. Final decision on architecture pivot (agent propõe, humano decide)
2. Security credential rotation (generate with agent, apply manually)
3. Customer-facing communication (draft with agent, human sends)
4. Deletion of production data (agent can warn, human executes)
5. Money decisions >R$50 (research with agent, human approves)
6. Conflict resolution when 2+ agents disagree (human tiebreak)

**Pattern:** Agent = research + draft. Human = decide + execute critical path.
```


### 5. Contradições Encontradas

**Contradição 1: §15 (Maximum Autonomy) vs §3 (Edit Safety)**

- §15 diz "ACT FIRST, REPORT AFTER"
- §3 diz "Read → Confirm → Edit → Re-read"
- **Resolução:** §3 é safety protocol, não é "stop and ask". §15 ok, mas clarificar que autonomy ≠ skip verification.

**Contradição 2: §24.1 (No Jobs) vs §23 (Product-First)**

- §24.1 é hard rule "NEVER apply to jobs"
- §23 diz "Every feature → who uses, how found" (market validation)
- **Não é contradição real**, mas pode confundir: §24.1 = não aplicar para emprego formal; §23 = validar product-market fit. Clarificar.

**Contradição 3: §26 (SSOT-First) vs proliferação de `egos-rules/*.md`**

- §26 diz "cada domínio tem UM arquivo SSOT"
- Mas existem 5+ arquivos em `~/.claude/egos-rules/` (ssot-map, doc-drift, jobs-monitoring, llm-routing, product-gtm)
- **Resolução:** `egos-rules/` é OK (modular domain rules). Contradição é quando cria `docs/business/PART002.md` + `docs/sales/STRATEGY.md` para MESMO domínio. Clarificar.


### 6. Veredicto Geral

**O CLAUDE.md é funcionalmente sólido mas sofre de 3 problemas clássicos de sistema que cresceu organicamente:**

1. **30% de gordura** — Seções redundantes (§12/28/29), aspiracionais (§16/22), ou senso comum (§6/10). Pode cortar para ~550 linhas sem perda.
2. **Hierarquia de prioridade invisível** — As 5 CRITICAL NON-NEGOTIABLES no topo são perfeitas. Mas depois disso, não há marcação clara de "tier 1 core rules" vs "tier 2 guidelines". Um agent novo lê linearmente e trata §6 (response quality) como tão importante quanto §25 (never force-push). **Solução:** Adicionar badges `[CORE]`, `[SAFETY]`, `[STYLE]` ao lado de cada seção.
3. **Falta de self-enforcement** — §27 (doc-drift) e §33 (evidence-first) são geniais porque TÊM enforcement (pre-commit hooks, CI gates). Mas §16 (challenge mode), §22 (chatbot everywhere), §23 (product-first mindset) são aspiracionais — não há código forçando. **Recomendação:** Ou adicionar enforcement (ex: pre-commit warning se commit não tem `EVIDENCE:` em docs/products/) ou mover para `docs/PHILOSOPHY.md` separado.

**Se fosse publicar como artigo "How I govern a multi-agent AI ecosystem solo":**

- **Showcase:** §1 (verification gates), §11 (codebase-memory), §14 (swarm execution), §25 (git safety), §27 (doc-drift shield), §31 (anti-hallucination), §33 (evidence-first)
- **Skip:** §6 (trivial), §10 (externa), §16/22 (aspirational), §23/24 (narrativo demais)

***

## O Que Fazer Agora

Enio, você tem 3 opções:

1. **Implementar a auditoria** — Cortar as 5 seções redundantes, comprimir as 5 inchadas, adicionar as 3 regras faltantes. Resultado: CLAUDE.md 2.0 com ~550 linhas, mais denso, sem gordura.
2. **Consolidar o meta-prompt e rodar em outros LLMs** — Enviar o meta-prompt + CLAUDE.md completo para Gemini/Grok/Claude Sonnet e coletar 3-4 auditorias. Consolidar diferenças.
3. **Priorizar o Evidence-First (§33)** — Esquecer auditoria do CLAUDE.md por enquanto e focar em ativar o `scripts/evidence-gate.ts` conforme o plano gradual (warning-only semana 1). Isso previne futuras alucinações como a que contaminou minha análise.

**Minha recomendação:** Opção 3 primeiro (evidence-gate warning-only live em 48h), depois opção 1 (cortar gordura do CLAUDE.md). A auditoria é útil mas o evidence-first é mais urgente — você está prestes a começar showcase público (Caminho B) e não pode ter claims sem prova.[^2]

Qual caminho você quer seguir?

<div align="center">⁂</div>

[^1]: META_PROMPT_CLAUDE_MD_REVIEW-2.md

[^2]: CLAUDE_MD_GLOBAL_2026-04-09.md

