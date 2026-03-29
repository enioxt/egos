/**
 * @deprecated Use `model-router.ts` instead — it has the canonical MODEL_CATALOG
 * with 8 models, 10 task types, and 3 cost tiers. This file is kept for
 * backward compatibility but should not be used for new code.
 *
 * SSOT Merge Rule applied 2026-03-29: model-router.ts is the canonical
 * LLM routing SSOT. See docs/SSOT_REGISTRY.md.
 *
 * LLM Orchestrator — Multi-Model Economic Routing (DEPRECATED)
 */

export type TaskComplexity = 'simple' | 'moderate' | 'complex';
export type LLMProvider = 'alibaba' | 'openrouter' | 'openai';

export interface ModelConfig {
  provider: LLMProvider;
  model: string;
  costPer1kTokens: number;
  maxTokens: number;
  bestFor: TaskComplexity[];
}

export const MODEL_REGISTRY: Record<string, ModelConfig> = {
  // Alibaba DashScope
  'qwen-turbo': {
    provider: 'alibaba',
    model: 'qwen-turbo',
    costPer1kTokens: 0.002, // ~$0.002/1k tokens (estimado)
    maxTokens: 8000,
    bestFor: ['simple'],
  },
  'qwen-plus': {
    provider: 'alibaba',
    model: 'qwen-plus',
    costPer1kTokens: 0.008, // ~$0.008/1k tokens (estimado)
    maxTokens: 32000,
    bestFor: ['moderate', 'complex'],
  },
  
  // OpenRouter (via Gemini)
  'gemini-flash': {
    provider: 'openrouter',
    model: 'google/gemini-2.0-flash-exp:free',
    costPer1kTokens: 0.0, // Free tier
    maxTokens: 8000,
    bestFor: ['simple', 'moderate'],
  },
  'gemini-flash-paid': {
    provider: 'openrouter',
    model: 'google/gemini-2.0-flash-001',
    costPer1kTokens: 0.0001, // Very cheap
    maxTokens: 8000,
    bestFor: ['simple', 'moderate'],
  },
};

export interface OrchestratorConfig {
  preferFree: boolean;
  maxCostPerCall: number; // USD
  fallbackChain: string[];
}

export class LLMOrchestrator {
  private config: OrchestratorConfig;
  
  constructor(config: Partial<OrchestratorConfig> = {}) {
    this.config = {
      preferFree: config.preferFree ?? true,
      maxCostPerCall: config.maxCostPerCall ?? 0.05,
      fallbackChain: config.fallbackChain ?? ['gemini-flash', 'gemini-flash-paid', 'qwen-turbo', 'qwen-plus'],
    };
  }
  
  /**
   * Seleciona o melhor modelo para a task baseado em complexidade e custo
   */
  selectModel(complexity: TaskComplexity, estimatedTokens: number = 1000): ModelConfig {
    const candidates = this.config.fallbackChain
      .map(key => MODEL_REGISTRY[key])
      .filter(model => model.bestFor.includes(complexity));
    
    if (this.config.preferFree) {
      const freeModel = candidates.find(m => m.costPer1kTokens === 0);
      if (freeModel) return freeModel;
    }
    
    // Ordena por custo (menor primeiro)
    const sorted = candidates.sort((a, b) => a.costPer1kTokens - b.costPer1kTokens);
    
    // Retorna o mais barato que cabe no orçamento
    const estimatedCost = (estimatedTokens / 1000) * (sorted[0]?.costPer1kTokens || 0);
    if (estimatedCost <= this.config.maxCostPerCall) {
      return sorted[0];
    }
    
    // Fallback: retorna o primeiro disponível
    return sorted[0] || MODEL_REGISTRY['gemini-flash'];
  }
  
  /**
   * Estima complexidade baseado no prompt
   */
  estimateComplexity(prompt: string): TaskComplexity {
    const length = prompt.length;
    const hasCode = /```|function|class|import/.test(prompt);
    const hasMultiStep = /step|first|then|finally|\d\./gi.test(prompt);
    
    if (length > 2000 || (hasCode && hasMultiStep)) return 'complex';
    if (length > 500 || hasCode || hasMultiStep) return 'moderate';
    return 'simple';
  }
  
  /**
   * Orquestra chamada LLM com seleção automática de modelo
   */
  async orchestrate(params: {
    prompt: string;
    complexity?: TaskComplexity;
    maxTokens?: number;
    forceModel?: string;
  }): Promise<{ model: ModelConfig; estimatedCost: number }> {
    const complexity = params.complexity || this.estimateComplexity(params.prompt);
    const estimatedTokens = params.maxTokens || Math.min(params.prompt.length * 2, 4000);
    
    const model = params.forceModel 
      ? MODEL_REGISTRY[params.forceModel] 
      : this.selectModel(complexity, estimatedTokens);
    
    const estimatedCost = (estimatedTokens / 1000) * model.costPer1kTokens;
    
    return { model, estimatedCost };
  }
}

// Singleton instance
export const llmOrchestrator = new LLMOrchestrator();
