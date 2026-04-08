# LLM Model Monitor — OpenRouter Intelligence System

> **SSOT:** Este documento | **Versão:** 1.0.0 | **Atualizado:** 2026-04-08

## Visão Geral

Sistema automatizado para monitorar novos modelos LLM no OpenRouter, testar performance, comparar com fallbacks existentes e adaptar dinamicamente a cadeia de fallback do EGOS.

## Contexto

Pesquisa aprofundada (CostGoat, Digital Applied, TeamDay AI, Reddit r/LocalLLaMA) revelou:
- **28+ modelos free** no OpenRouter (Qwen3 Coder, Nemotron 3 Super, MiniMax M2.5, Step 3.5 Flash)
- **Dezenas de modelos pagos** com excelente custo-benefício (Kimi K2.5, DeepSeek V3.2, MiMo-V2-Pro)
- **Rate limits free:** 20 req/min, 200 req/dia
- **Modelos chineses dominam** custo-benefício em 2026

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Model Monitor                        │
│                   (VPS - a cada 6h)                         │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  1. FETCH: OpenRouter API /models                           │
│     - Detecta novos modelos (free/paid)                     │
│     - Compara com baseline local                            │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  2. RESEARCH: MCP Exa                                       │
│     - Reddit reviews                                        │
│     - X.com mentions                                        │
│     - Blogs técnicos                                        │
│     - Benchmarks públicos                                 │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  3. STORE: Supabase llm_models                              │
│     - Metadata do modelo                                    │
│     - Sentiment analysis                                      │
│     - Benchmark scores                                      │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  4. TEST: Auto-Test Runner (se S-tier)                    │
│     - Coding challenges                                     │
│     - Reasoning problems                                    │
│     - Long-context retrieval                                │
│     - Agentic/tool calling                                  │
│     - Creative/copywriting                                  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  5. COMPARE: Benchmark Report                               │
│     - vs Current fallback chain                             │
│     - Quality/cost trade-off                                │
│     - Recommendation EGOS                                   │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  6. ACT: Auto-Update ou Alert                               │
│     - PR automático se supera current                       │
│     - Telegram/WhatsApp alert                               │
│     - Dashboard update                                      │
└─────────────────────────────────────────────────────────────┘
```

## OpenRouter Free Models — Tier S (Prioridade Máxima)

| Modelo | ID | Contexto | Uso Recomendado | Rate Limit | Estimativa Custo/Mês* |
|--------|-----|----------|-----------------|------------|----------------------|
| Qwen3 Coder 480B | `qwen/qwen3-coder:free` | 262K | Coding SOTA free | 20/min, 200/dia | $0 (free tier) |
| NVIDIA Nemotron 3 Super | `nvidia/nemotron-3-super-120b-a12b:free` | 262K | Documentos longos | 20/min, 200/dia | $0 (free tier) |
| MiniMax M2.5 | `minimax/minimax-m2.5:free` | 197K | Coding, office | 20/min, 200/dia | $0 (free tier) |
| Step 3.5 Flash | `stepfun/step-3.5-flash:free` | 256K | SEO, programação | 20/min, 200/dia | $0 (free tier) |
| Qwen3.6 Plus | `qwen/qwen3.6-plus:free` | 1M | Raciocínio, long context | 20/min, 200/dia | $0 (free tier) |

*Cálculo: 200 req/dia × 30 dias = 6,000 requests/mês no free tier

## OpenRouter Paid — Best Value (Custo-Benefício)

| Modelo | ID | Input/1M | Output/1M | Uso | Inteligência/$ |
|--------|-----|----------|-----------|-----|----------------|
| Kimi K2.5 | `moonshotai/kimi-k2.5` | $0.38-0.57 | $1.72-1.91 | Agentic coding, planning | ★★★★★ |
| MiniMax M2.5 | `minimax/minimax-m2.5` | $0.12-0.30 | $0.95-1.20 | Coding, iterações | ★★★★☆ |
| DeepSeek V3.2 | `deepseek/deepseek-v3.2` | $0.27 | $1.10 | Value king | ★★★★★ |
| MiMo-V2-Pro | `xiaomi/mimo-v2-pro` | Variável | Variável | SWE-Bench #1 | ★★★★★ |

## Schema Supabase

```sql
CREATE TABLE llm_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider TEXT NOT NULL,
    model_id TEXT NOT NULL UNIQUE, -- ex: qwen/qwen3-coder:free
    name TEXT NOT NULL,
    is_free BOOLEAN DEFAULT false,
    
    -- Pricing (for paid models)
    price_input_per_1m DECIMAL(10,6),
    price_output_per_1m DECIMAL(10,6),
    
    -- Technical specs
    context_length INTEGER,
    capabilities TEXT[], -- ['vision', 'tools', 'json']
    
    -- Discovery
    discovery_date TIMESTAMPTZ DEFAULT now(),
    discovered_by TEXT DEFAULT 'llm-monitor',
    
    -- Research (MCP Exa)
    review_sentiment DECIMAL(3,2), -- -1.0 to 1.0
    review_sources INTEGER, -- number of sources found
    community_mentions INTEGER, -- X.com, Reddit mentions
    
    -- Benchmark scores (from our test suite)
    coding_score DECIMAL(3,1),
    reasoning_score DECIMAL(3,1),
    context_score DECIMAL(3,1),
    agentic_score DECIMAL(3,1),
    creative_score DECIMAL(3,1),
    overall_score DECIMAL(3,1),
    
    -- Performance metrics
    avg_latency_ms INTEGER,
    reliability_rate DECIMAL(3,2), -- 0.0 to 1.0
    
    -- EGOS classification
    egos_tier TEXT CHECK (egos_tier IN ('S', 'A', 'B', 'C', 'pending')),
    egos_recommendation TEXT, -- 'primary', 'fallback', 'experimental', 'reject'
    recommended_tasks TEXT[], -- ['coding', 'reasoning', 'summary']
    
    -- Comparison
    vs_current_fallback TEXT, -- 'superior', 'equivalent', 'inferior'
    cost_savings_percent INTEGER, -- if cheaper with same quality
    
    -- Status
    test_status TEXT DEFAULT 'pending' CHECK (test_status IN ('pending', 'testing', 'completed', 'failed')),
    last_tested_at TIMESTAMPTZ,
    
    -- Metadata
    raw_data JSONB, -- full OpenRouter API response
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_llm_models_tier ON llm_models(egos_tier);
CREATE INDEX idx_llm_models_free ON llm_models(is_free) WHERE is_free = true;
CREATE INDEX idx_llm_models_score ON llm_models(overall_score DESC);
CREATE INDEX idx_llm_models_recommendation ON llm_models(egos_recommendation);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_llm_models_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_llm_models
    BEFORE UPDATE ON llm_models
    FOR EACH ROW
    EXECUTE FUNCTION update_llm_models_updated_at();
```

## Test Suite Standard

### Categoria 1: Coding
- Function generation (TypeScript/Python)
- Debug challenges
- Refactoring
- Algorithm design

**Meta-prompt:** `.guarani/prompts/meta/llm-test-coding.md`

### Categoria 2: Reasoning
- Logical deduction
- Mathematical word problems
- Multi-step planning
- Abductive reasoning

**Meta-prompt:** `.guarani/prompts/meta/llm-test-reasoning.md`

### Categoria 3: Contexto Longo
- Needle in haystack (128K, 256K, 1M)
- Multi-needle retrieval
- Long-context summarization
- Context-aware code generation

**Meta-prompt:** `.guarani/prompts/meta/llm-test-context.md`

### Categoria 4: Agentic
- Tool selection accuracy
- State management across turns
- Error recovery
- Multi-tool coordination

**Meta-prompt:** `.guarani/prompts/meta/llm-test-agentic.md`

### Categoria 5: Creative
- Brand voice adaptation
- Multi-format content
- Headline generation
- Email sequences

**Meta-prompt:** `.guarani/prompts/meta/llm-test-creative.md`

## Scoring Thresholds

| Tier | Overall Score | Use Case |
|------|---------------|----------|
| **S** | 9.0+ | Primary model for category |
| **A** | 8.0-8.9 | Secondary fallback |
| **B** | 7.0-7.9 | Tertiary/general tasks |
| **C** | <7.0 | Not recommended |

## Fallback Chain Atual (EGOS)

```typescript
// packages/shared/src/llm-provider.ts

const FALLBACK_CHAIN = {
  coding: [
    { model: 'qwen/qwen3-coder:free', provider: 'openrouter', tier: 'S' },
    { model: 'qwen-plus', provider: 'dashscope', tier: 'S' },
    { model: 'minimax/minimax-m2.5', provider: 'openrouter', tier: 'A' },
  ],
  reasoning: [
    { model: 'qwen/qwen3.6-plus:free', provider: 'openrouter', tier: 'S' },
    { model: 'nvidia/nemotron-3-super-120b-a12b:free', provider: 'openrouter', tier: 'S' },
  ],
  long_context: [
    { model: 'nvidia/nemotron-3-super-120b-a12b:free', provider: 'openrouter', tier: 'S' },
    { model: 'qwen/qwen3.6-plus:free', provider: 'openrouter', tier: 'S' },
  ],
  agentic: [
    { model: 'qwen-plus', provider: 'dashscope', tier: 'S' },
    { model: 'gemini-2.0-flash', provider: 'openrouter', tier: 'A' },
  ],
  creative: [
    { model: 'qwen/qwen3.6-plus:free', provider: 'openrouter', tier: 'A' },
    { model: 'gemini-2.0-flash', provider: 'openrouter', tier: 'A' },
  ],
};
```

## Scripts

### llm-model-monitor.ts
Localização: `scripts/llm-model-monitor.ts`
Frequência: Cada 6h (cron)
Função: Detectar novos modelos, research, store, trigger tests

### llm-model-tester.ts
Localização: `scripts/llm-model-tester.ts`
Trigger: Após detecção de modelo S-tier
Função: Rodar test suite, calcular scores, update database

### llm-comparison-report.ts
Localização: `scripts/llm-comparison-report.ts`
Trigger: Após test completion
Função: Gerar report markdown, comparar com baseline

## Dashboard HQ

Métricas visuais:
- Modelos monitorados (total, S-tier, A-tier)
- Fallback chain atual
- Scores por categoria (radar chart)
- Economia gerada (comparação cost/mês)
- Latency trends
- Test status (pending/testing/completed)

## Integrações

### MCP Exa
- Research de novos modelos
- Sentiment analysis de reviews
- Benchmark discovery

### CORAL
- Modelos validados como S-tier são salvos em `gem_discoveries`
- Reuso por outros agentes do EGOS

### Event Bus
- `llm.model.discovered`
- `llm.model.test.completed`
- `llm.fallback.updated`

### Notificações
- Telegram: Alertas de modelo S-tier detectado
- WhatsApp: Resumo semanal de economia

## Referências

- **CostGoat:** https://costgoat.com/pricing/openrouter-free-models
- **Digital Applied Rankings:** https://www.digitalapplied.com/blog/openrouter-rankings-april-2026
- **OpenRouter Docs:** https://openrouter.ai/docs
- **Reddit r/LocalLLaMA:** User benchmarks and reviews

## Tasks Relacionadas

- LLM-MON-001..012 (TASKS.md §LLM Model Monitor)

---

**Nota:** Este sistema garante que o EGOS sempre use os melhores modelos disponíveis no OpenRouter, maximizando qualidade e minimizando custos através de testes contínuos e adaptação automática.
