# Metrics Dashboard — EGOS Ecosystem

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** metrics dashboard specification and tracking model
- **Summary:** Defines unified EGOS metrics for tooling usage, costs, performance, and orchestration quality.
- **Read next:**
  - `docs/TELEMETRY_SSOT.md` — telemetry contract
  - `docs/KERNEL_MISSION_CONTROL.md` — observability control-plane vision
  - `TASKS.md` — telemetry/observability open tasks
<!-- llmrefs:end -->

> **Version:** 1.0.0 | **Date:** 2026-03-20
> **Purpose:** Unified metrics tracking for all AI tools, APIs, and orchestration patterns

---

## Overview

Sistema completo de métricas para rastrear uso de ferramentas, custos, performance e divisão de tarefas no ecossistema EGOS.

## Ferramentas Rastreadas

### 1. Codex CLI

**Uso:** Code review, diff application, mechanical refactoring

**Métricas:**
- Número de reviews executados
- Número de diffs aplicados
- Tempo médio por operação
- Taxa de sucesso/falha
- Arquivos modificados por operação

**Comandos:**
```bash
codex review --uncommitted
codex cloud list
codex cloud apply <id>
```

**Custo:** Incluído no plano OpenAI

### 2. Alibaba DashScope (Qwen)

**Uso:** Primary LLM para chat, summarization, conversation memory

**Modelos:**
- `qwen-plus` — Chat, reasoning, tool-calling
- `qwen-max` — Intelligence reports, deep analysis
- `qwen-turbo` — Fast responses, simple tasks

**Métricas:**
- Tokens in/out por modelo
- Custo por request (¥0.004/1K tokens qwen-plus)
- Latência média
- Taxa de erro
- Uso por tipo de task (chat/summary/intelligence)

**API:** DashScope REST API

### 3. Claude Code

**Uso:** Parallel code generation, architecture design, complex refactoring

**Métricas:**
- Número de sessões
- Arquivos gerados
- Tokens consumidos
- Custo estimado
- Integração com MCP servers

**Configuração:** `~/.claude/` (user scope)

### 4. OpenRouter

**Uso:** Fallback LLM, model routing, multi-provider access

**Modelos Ativos:**
- `google/gemini-2.0-flash-exp:free` — Fast, free tier
- `google/gemini-2.0-flash-001` — Production
- `anthropic/claude-3.5-sonnet` — Complex reasoning
- `openai/gpt-4o-mini` — Tool-calling

**Métricas:**
- Tokens in/out por modelo
- Custo por provider
- Latência por modelo
- Fallback triggers
- Success rate por modelo

**API:** OpenRouter REST API

### 5. Cascade (Windsurf IDE Agent)

**Uso:** Primary orchestrator, autonomous task execution

**Métricas:**
- Sessões ativas
- Tasks completadas
- Commits criados
- Arquivos modificados
- Tool calls executados
- Context usage (CTX score 0-280)

---

## Estrutura de Métricas

### Tool Usage Metric

```typescript
interface ToolUsageMetric {
  tool: 'codex' | 'alibaba' | 'claude_code' | 'openrouter' | 'gemini' | 'cascade';
  operation: string;
  timestamp: string;
  durationMs?: number;
  tokensIn?: number;
  tokensOut?: number;
  costUsd?: number;
  model?: string;
  success: boolean;
  errorMessage?: string;
  metadata?: Record<string, unknown>;
}
```

### Task Metric

```typescript
interface TaskMetric {
  taskId: string;
  taskType: 'feature' | 'bug' | 'docs' | 'refactor' | 'test' | 'deploy';
  priority: 'P0' | 'P1' | 'P2';
  repo: string;
  startTime: string;
  endTime?: string;
  durationMs?: number;
  toolsUsed: string[];
  filesChanged: number;
  linesAdded: number;
  linesRemoved: number;
  commitsCreated: number;
  status: 'pending' | 'in_progress' | 'completed' | 'blocked' | 'failed';
}
```

### Session Metric

```typescript
interface SessionMetric {
  sessionId: string;
  startTime: string;
  endTime?: string;
  durationMs?: number;
  tasksCompleted: number;
  toolUsage: Record<string, number>;
  totalTokensIn: number;
  totalTokensOut: number;
  totalCostUsd: number;
  reposModified: string[];
  totalCommits: number;
  totalFilesChanged: number;
}
```

---

## Uso do Metrics Tracker

### Inicialização

```typescript
import { initMetricsTracker, trackToolUsage, trackTask } from '@egos/shared';

const tracker = initMetricsTracker('session-2026-03-20');
```

### Rastreando Uso de Ferramentas

```typescript
// Codex
trackToolUsage({
  tool: 'codex',
  operation: 'review',
  durationMs: 5400,
  success: true,
  metadata: { filesReviewed: 12 }
});

// Alibaba
trackToolUsage({
  tool: 'alibaba',
  operation: 'chat',
  model: 'qwen-plus',
  tokensIn: 1200,
  tokensOut: 800,
  costUsd: 0.008,
  durationMs: 2300,
  success: true
});

// OpenRouter
trackToolUsage({
  tool: 'openrouter',
  operation: 'chat',
  model: 'google/gemini-2.0-flash-001',
  tokensIn: 800,
  tokensOut: 600,
  costUsd: 0.0014,
  durationMs: 1800,
  success: true
});
```

### Rastreando Tasks

```typescript
trackTask({
  taskId: 'FORJA-001',
  taskType: 'feature',
  priority: 'P0',
  repo: 'forja',
  startTime: '2026-03-19T20:00:00Z',
  endTime: '2026-03-19T22:30:00Z',
  durationMs: 9000000,
  toolsUsed: ['cascade', 'alibaba', 'codex'],
  filesChanged: 15,
  linesAdded: 450,
  linesRemoved: 120,
  commitsCreated: 12,
  status: 'completed'
});
```

### Exportando Métricas

```typescript
const tracker = getMetricsTracker();

// Print summary
console.log(tracker.printSummary());

// Export to JSON
tracker.saveToFile('/home/enio/egos/metrics/session-2026-03-20.json');

// Get detailed report
const metrics = tracker.exportMetrics();
```

---

## Divisão de Tarefas por Ferramenta

### Cascade (Windsurf IDE Agent)

**Responsabilidades:**
- Orchestração geral de tasks
- Edição de código (write_to_file, edit, multi_edit)
- Execução de comandos shell
- Navegação de arquivos
- Commits e push para GitHub
- Integração com MCPs

**Quando usar:** Tasks que requerem múltiplas operações coordenadas, edição de código, e orchestração de ferramentas.

### Codex CLI

**Responsabilidades:**
- Code review de uncommitted changes
- Aplicação de diffs complexos
- Refactoring mecânico multi-arquivo
- Análise de código estático

**Quando usar:** Quando há muitos arquivos para revisar ou aplicar mudanças mecânicas em batch.

### Alibaba (Qwen)

**Responsabilidades:**
- Chat conversacional
- Summarization de conversas
- Intelligence reports
- Reasoning complexo
- Tool-calling

**Quando usar:** Primary LLM para todas as operações de chat e reasoning.

### Claude Code

**Responsabilidades:**
- Geração de código complexo
- Design de arquitetura
- Refactoring profundo
- Trabalho paralelo com Cascade

**Quando usar:** Tasks que se beneficiam de múltiplos agentes trabalhando em paralelo.

### OpenRouter (Gemini/GPT)

**Responsabilidades:**
- Fallback quando Alibaba falha
- Tasks específicas que funcionam melhor com Gemini/GPT
- Model routing baseado em task type

**Quando usar:** Fallback automático ou tasks específicas (ex: name validation, ethical checks).

---

## Custos Estimados

### Session 3 (2026-03-19/20)

| Tool | Calls | Tokens | Cost (USD) |
|------|-------|--------|------------|
| Cascade | ~150 | ~100K | Incluído |
| Alibaba | ~30 | ~50K | ~$0.20 |
| Codex | 0 | 0 | $0 |
| OpenRouter | ~5 | ~8K | ~$0.01 |
| **Total** | **~185** | **~158K** | **~$0.21** |

### Projeção Mensal (30 sessões)

| Tool | Calls | Tokens | Cost (USD) |
|------|-------|--------|------------|
| Cascade | ~4,500 | ~3M | Incluído |
| Alibaba | ~900 | ~1.5M | ~$6.00 |
| Codex | ~100 | ~500K | Incluído |
| OpenRouter | ~150 | ~240K | ~$0.30 |
| **Total** | **~5,650** | **~5.24M** | **~$6.30** |

---

## Próximos Passos

1. ✅ Criar módulo `metrics-tracker.ts` no @egos/shared
2. ⬜ Integrar tracking em todos os repos (forja, 852, carteira-livre)
3. ⬜ Criar dashboard visual (React + Recharts)
4. ⬜ Exportar métricas para Supabase
5. ⬜ Criar alertas de custo (threshold: $10/mês)
6. ⬜ Integrar com telemetry existente
7. ⬜ Criar relatórios semanais automáticos
