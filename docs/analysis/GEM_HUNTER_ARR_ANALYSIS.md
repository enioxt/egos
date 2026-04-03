# EGOS Discovery Systems — Gem Hunter + ARR Analysis

> **Analysis Date:** 2026-04-03  
> **Analyst:** cascade-agent  
> **Purpose:** Verificar estado atual de sistemas de descoberta e identificar gaps para monitoramento de forks/contribuições

---

## Executive Summary

**Status:** Sistemas operacionais, mas **GAP CRÍTICO** identificado para monitoramento de forks/contribuições GitHub.

| Sistema | Status | Cobertura | Gaps |
|---------|--------|-----------|------|
| **Gem Hunter** | ✅ Ativo v6.1 | Descoberta de novos repos/papers | ❌ Não monitora forks do EGOS |
| **ARR (Search Engine)** | ✅ Implementado | Busca atômica em conteúdo | ❌ Não indexa forks externos |
| **Signal Mesh** | ✅ Ativo | Roteamento de sinais | ❌ Sem sinais de contribuição |
| **Fork/Contrib Monitor** | ❌ **INEXISTENTE** | — | Necessário criar |

**Conclusão:** Temos excelente sistema para descobrir gems NOVAS, mas NÃO temos sistema para rastrear melhorias em forks/contribs do EGOS.

---

## 1. Gem Hunter — Estado Atual

### 1.1 O que é

Engine de descoberta automatizada que encontra, escora e extrai padrões transplantáveis de repositórios open-source.

**Local:** `agents/agents/gem-hunter.ts` (v6.1, 2250 linhas)

### 1.2 Fontes Monitoradas (14+)

| Fonte | API | Status | Dados Coletados |
|-------|-----|--------|-----------------|
| GitHub Search | ✅ | Ativo | stars, forks, descrição, linguagem |
| GitHub Code Search | ✅ | Ativo | arquivos específicos, código |
| HuggingFace Hub | ✅ | Ativo | models, spaces, downloads, likes |
| arXiv | ✅ | Ativo | papers, abstracts, autores |
| Papers With Code | ✅ | Ativo | papers + implementações |
| X API | ✅ | Ativo | tweets, trends, KOL signals |
| Reddit | ✅ | Ativo | posts, scores |
| StackOverflow | ✅ | Ativo | Q&A, tags |
| HackerNews | ✅ | Ativo | pontos, comentários |
| Exa Search | ✅ | Ativo | web discovery |
| GitLab | ✅ | Ativo | repos alternativos |
| CoinGecko | ✅ | Ativo | dados crypto |
| DeFiLlama | ✅ | Ativo | dados DeFi |
| Telegram channels | ✅ | Ativo | mensagens |

### 1.3 Pipeline v6.0 — Papers Without Code

```
S1 Discovery (free APIs) → S2 Abstract Triage (free LLM) → S3 Deep Reading (Gemini)
  → S4 Scaffold Generation (.ts + .md) → S5 Scoring → S6 Trend Evolution
```

### 1.4 Scoring 9-Fatores

```
egos_relevance(0.24) + transplantability(0.18) + complementarity(0.14) + novelty(0.12)
+ maintenance(0.10) + doc_quality(0.08) + license(0.06) + op_fit(0.04) + obs_maturity(0.04)
```

### 1.5 Execução

**GitHub Actions:** `.github/workflows/gem-hunter-adaptive.yml`
- **Schedule:** Seg + Qui 2h37 BRT (5h37 UTC)
- **Triggers:** `x-signals-public`, `early-warning`, `governance-plugplay`

**Comandos:**
```bash
bun agent:run gem-hunter --exec                    # Full run
bun agent:run gem-hunter --exec --quick            # Top 3 per keyword
bun agent:run gem-hunter --exec --analyze          # AI synthesis
bun agent:run gem-hunter --history                 # SQLite trends
```

---

## 2. ARR (Adaptive Atomic Retrieval)

### 2.1 O que é

Sistema de busca em memória com atomização semântica de conteúdo.

**Arquitetura:**
- **Atomizer:** `packages/atomizer/src/default-atomizer.ts`
- **Search Engine:** `packages/search-engine/src/in-memory-search.ts`

### 2.2 Componentes

```typescript
// Atom — unidade mínima de conteúdo
interface Atom {
  id: string;
  kind: 'text';
  content: string;           // Sentença original
  normalizedContent: string; // Para matching
  sourceId: string;          // Origem (arquivo, repo)
  sourceType: string;
  confidence: number;        // 0-1
  metadata: Record<string, unknown>;
  createdAt: string;
}

// Search Result
interface SearchResult {
  atom: Atom;
  score: number;            // Ranking
  reasons: string[];        // Por que matchou
}
```

### 2.3 Capacidades

| Feature | Status |
|---------|--------|
| Atomização por sentença | ✅ |
| Normalização (NFKD) | ✅ |
| Busca substring exata | ✅ |
| Token overlap scoring | ✅ |
| Sugestões (autocomplete) | ✅ |
| Indexação incremental | ✅ |

### 2.4 Limitações

| Limitação | Impacto |
|-----------|---------|
| Apenas texto, não código AST | Não entende estrutura de código |
| Busca local (in-memory) | Não escala para big data |
| Sem embeddings vetoriais | Matching superficial |
| Sem histórico de versões | Não rastreia mudanças |

---

## 3. Signal Mesh

### 3.1 O que é

Meta-SSOT que define fontes de sinais, capacidades, e roteamento.

**Local:** `docs/SIGNAL_MESH.md`

### 3.2 Hierarquia

```
TASKS.md (priority)
  → agents.json (registry)
    → SIGNAL_MESH.md (collection plan)
      → signals.json, kol-list.json (outputs)
```

### 3.3 Fontes Mapeadas (15+)

| Fonte | Tipo | Agent | Output |
|-------|------|-------|--------|
| X API | Social | gem-hunter, kol-discovery | signals.json |
| arXiv | Academic | gem-hunter | papers.json |
| GitHub Trending | Dev | gem-hunter | signals.json |
| GitHub API | Dev | gem-hunter | signals.json |
| HackerNews | News | world-model | signals.json |
| Reddit | Social | gem-hunter | signals.json |
| Exa | Web | kol-discovery, world-model | next-queries.json |

### 3.4 Regras de Roteamento

- Score ≥ 4 na matriz topic×source = PRIMARY
- Score < 3 = skip unless PRIMARY unavailable
- Score ≥ 80 (any category) → Telegram admin alert

---

## 4. GAP CRÍTICO: Monitoramento de Forks/Contribuições

### 4.1 O que NÃO temos

❌ **Nenhum sistema que monitore:**
- Forks do repositório `enioxt/egos`
- Pull requests de contribuidores externos
- Issues criadas por usuários
- Commits em forks que poderiam ser upstreamed
- Releases/tags em forks
- Discussions com melhorias propostas

### 4.2 Por que isso importa

**Cenário perdido hoje:**
1. Usuário fork `egos` → implementa feature X
2. Usuário não abre PR (ou PR fica stale)
3. Nós nunca sabemos que feature X existe
4. Perdemos melhoria potencial

**Valor:**
- Detectar inovações na comunidade
- Identificar contribuidores potenciais
- Melhorias upstream automáticas
- Feedback de uso real

### 4.3 O que precisamos

| Componente | Descrição |
|------------|-----------|
| **Fork Scanner** | Listar todos os forks de `enioxt/egos` |
| **Commit Monitor** | Detectar commits em forks não presentes no upstream |
| **PR Tracker** | Monitorar PRs abertos (incluindo stale) |
| **Issue Scanner** | Capturar issues com feature requests |
| **Release Watcher** | Notificar quando forks fazem releases |
| **Diff Analyzer** | Comparar forks com upstream, identificar diff relevante |
| **ARR Indexer** | Indexar código de forks para busca |

---

## 5. Proposta: Fork Hunter System

### 5.1 Arquitetura Proposta

```
┌────────────────────────────────────────────────────────────────┐
│                    FORK HUNTER SYSTEM                           │
├────────────────────────────────────────────────────────────────┤
│  L1: DISCOVERY                                                  │
│    ├── GitHub API: GET /repos/enioxt/egos/forks                │
│    ├── Paginate all forks (max 100/page)                        │
│    └── Store: fork-owner, created_at, updated_at, stars        │
├────────────────────────────────────────────────────────────────┤
│  L2: MONITORING                                                │
│    ├── Per fork: GET /repos/{fork}/commits                     │
│    ├── Diff: compare/{base}...{fork}:main                      │
│    └── Detect: commits ahead of upstream                        │
├────────────────────────────────────────────────────────────────┤
│  L3: ANALYSIS                                                  │
│    ├── ARR: atomizar commits (mensagens, diff)                  │
│    ├── LLM: classify intent (bugfix, feature, refactor)        │
│    └── Score: EGOS_relevance × upstream_value                   │
├────────────────────────────────────────────────────────────────┤
│  L4: ALERTS                                                    │
│    ├── High score → Telegram + TASKS.md entry                  │
│    ├── Weekly digest → all forks activity                       │
│    └── Exceptional → manual review suggestion                   │
└────────────────────────────────────────────────────────────────┘
```

### 5.2 Dados a Coletar

**Por Fork:**
```typescript
interface ForkInfo {
  owner: string;              // Quem forkou
  createdAt: string;          // Quando
  updatedAt: string;          // Última atividade
  stars: number;              // Popularidade do fork
  aheadBy: number;            // Commits à frente do upstream
  behindBy: number;           // Commits atrás do upstream
  defaultBranch: string;      // Branch principal
  openIssues: number;         // Issues no fork
  language: string;           // Linguagem principal
  
  // Diff analysis
  commits: CommitDiff[];       // Commits não no upstream
  filesChanged: string[];      // Arquivos modificados
  linesAdded: number;         // Stats de código
  linesRemoved: number;
  
  // LLM analysis
  intent: 'bugfix' | 'feature' | 'refactor' | 'experimental' | 'unknown';
  relevanceScore: number;     // 0-100 para EGOS
  summary: string;            // Descrição do que foi feito
  suggestedAction: 'review' | 'upstream' | 'ignore' | 'contact';
}
```

### 5.3 Triggers de Alerta

| Condição | Ação | Prioridade |
|----------|------|------------|
| Fork tem > 50 stars | Notificar admin | P1 |
| Fork > 10 commits ahead com intent=feature | TASKS.md entry | P1 |
| Fork implementa capability nossa (ARR detecta) | Review suggestion | P0 |
| Fork faz release com tag | Alert Telegram | P2 |
| PR aberto > 30 dias sem review | Stale PR alert | P2 |
| Issue com "feature request" + upvotes | Product feedback | P2 |

### 5.4 Integração com Sistemas Existentes

| Sistema | Integração |
|---------|------------|
| **Gem Hunter** | Fork Hunter é módulo novo do gem-hunter.ts ou agent separado |
| **ARR** | Indexar commits de forks como atoms (sourceType: 'github-fork') |
| **Signal Mesh** | Nova fonte: `github-forks` → roteamento para world-model |
| **World Model** | Sinais de forks entram em `signals.json` |
| **TASKS.md** | High-value forks geram tasks automáticas |
| **Telegram** | Alerts para forks excepcionais |

---

## 6. Tasks Propostas

### P0 — Foundation (1-2 semanas)

**FH-001:** Implementar Fork Discovery
- API GitHub: listar todos forks de `enioxt/egos`
- Paginação (máx 100/page)
- Persistir: `docs/gem-hunter/forks.json`

**FH-002:** Commit Diff Detection
- Para cada fork ativo, comparar com upstream
- Detectar: ahead_by, behind_by
- Persistir: `docs/gem-hunter/fork-diffs/{owner}.json`

**FH-003:** Basic Intent Classification
- LLM (Qwen free) classifica commits: bugfix/feature/refactor
- Output: intenção + summary

### P1 — Analysis (2-4 semanas)

**FH-004:** ARR Indexing de Forks
- Atomizar commits de forks
- Indexar mensagens de commit, diff snippets
- Busca: "qual fork implementou X?"

**FH-005:** Relevance Scoring
- Score EGOS_relevance × upstream_value
- Train classifier com histórico de forks úteis

**FH-006:** Alert System
- Telegram alerts para forks P0/P1
- Weekly digest email/json

### P2 — Automation (1-2 meses)

**FH-007:** Auto TASKS.md Generation
- Forks high-relevance → automatic task creation
- Template: "Review fork/{owner} — implementa {feature}"

**FH-008:** Upstream Suggestion
- Detectar quando fork tem melhoria "fácil" de upstream
- Auto-suggest: "Considerar merge de {commit}"

**FH-009:** Contributor Network
- Identificar contribuidores recorrentes
- Mapa de colaboração EGOS

### P3 — Intelligence (2-3 meses)

**FH-010:** Predictive Fork Value
- ML: prever se fork terá valor antes de analisar
- Base: owner history, star velocity, code churn

**FH-011:** Semantic Diff Understanding
- AST diff (não só textual)
- Entender refatorações, não só linhas

**FH-012:** Auto-PR Generation
- Para forks com melhorias claras, gerar PR description
- Sugerir upstream ao owner do fork

---

## 7. Custos Estimados

### API GitHub

| Endpoint | Calls/Dia | Rate Limit | Status |
|----------|-----------|------------|--------|
| List forks | 1 | 5K/hr | ✅ Free |
| Compare commits | ~50 forks × 1/day | 5K/hr | ✅ Free |
| Get commit details | ~100 commits | 5K/hr | ✅ Free |

**Total:** $0 (dentro de limites gratuitos)

### LLM (classificação)

| Volume | Model | Cost/Dia |
|--------|-------|----------|
| ~50 forks × 5 commits = 250 commits | Qwen-plus (free) | $0 |
| Exceptional cases needing deep | Gemini Flash | ~$0.01 |

**Total:** ~$0.30/mês

---

## 8. Alternativas Consideradas

### Opção A: Integrar no Gem Hunter existente
**Pros:** Reusa infra, scheduling, alerts  
**Cons:** Código já complexo (2250 linhas)  
**Veredito:** ❌ Não — manter separado para clareza

### Opção B: Novo agent `fork-hunter.ts`
**Pros:** Responsabilidade única, pode ter scheduling diferente  
**Cons:** Duplicação de infra GitHub API  
**Veredito:** ✅ Sim — agent separado, scheduling diário

### Opção C: GitHub Apps (webhook-based)
**Pros:** Real-time, eficiente  
**Cons:** Requer infra webhooks, mais complexo  
**Veredito:** ❌ Não agora — polling diário é suficiente

---

## 9. Conclusão

### O que temos ✅

1. **Gem Hunter v6.1** — Excelente descoberta de gems NOVAS
2. **ARR** — Busca atômica funcional
3. **Signal Mesh** — Roteamento de sinais definido
4. **Scheduled execution** — GitHub Actions funcionando
5. **Cost-effective** — ~$15/mês para Gem Hunter

### O que falta ❌

1. **Fork monitoring** — Não rastreamos forks de `enioxt/egos`
2. **Contrib tracking** — Não monitoramos PRs/issues de externos
3. **Diff analysis** — Não comparamos forks com upstream
4. **Community intelligence** — Perdendo inovações da comunidade

### Recomendação

**Criar `fork-hunter.ts` como novo agent P0.**

Justificativa:
- Baixo custo ($0-0.30/mês)
- Alto valor (descoberta de melhorias comunitárias)
- Simples de implementar (GitHub API bem documentada)
- Integra bem com ARR + Signal Mesh existentes

---

## Referências

- `agents/agents/gem-hunter.ts` — v6.1 source
- `docs/gem-hunter/SSOT.md` — Gem Hunter canonical
- `docs/gem-hunter/GEM_HUNTER_v6_MASTER_PLAN.md` — Master plan
- `packages/search-engine/` — ARR implementation
- `packages/atomizer/` — Atomizer implementation
- `docs/SIGNAL_MESH.md` — Signal routing

---

*Análise completa — 2026-04-03*
