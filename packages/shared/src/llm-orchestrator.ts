/**
 * LLM Orchestrator — Multi-Model Economic Routing
 *
 * Type definitions for model routing.
 * Implementation delegated to model-router.ts
 */

// @public - Used for model complexity classification
export type TaskComplexity = 'simple' | 'moderate' | 'complex';

// @public - Used for provider definitions
export type LLMProvider = 'alibaba' | 'openrouter' | 'openai';

// @public - Used for model configuration
export interface ModelConfig {
  provider: LLMProvider;
  model: string;
  costPer1kTokens: number;
  maxTokens: number;
  bestFor: TaskComplexity[];
}

// @public - Used for orchestrator configuration
export interface OrchestratorConfig {
  preferFree: boolean;
  maxCostPerCall: number; // USD
  fallbackChain: string[];
}
