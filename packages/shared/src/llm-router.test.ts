import { describe, expect, it } from 'bun:test';
import { routeTask, routeGuardBrasil, reportUsage, resetQuotas, DEFAULT_MODELS } from './llm-router';

describe('LLM Router — U(m,t)', () => {
  it('selects cheap model for classification tasks', () => {
    const result = routeTask('classification', { preferLane: 'cheap' });
    expect(result.selectedModel.lane).toBe('cheap');
    expect(result.selectedModel.costPer1kTokens).toBeLessThan(0.001);
    expect(result.score).toBeGreaterThan(0);
  });

  it('selects planner model for complex reasoning', () => {
    const result = routeTask('complex_reasoning', { preferLane: 'planner' });
    expect(result.selectedModel.lane).toBe('planner');
    expect(result.selectedModel.capabilities.complex_reasoning).toBeGreaterThan(90);
  });

  it('respects max cost constraint', () => {
    const result = routeTask('code_generation', { maxCostPer1k: 0.001 });
    expect(result.selectedModel.costPer1kTokens).toBeLessThanOrEqual(0.001);
  });

  it('provides fallback chain with different providers', () => {
    const result = routeTask('text_generation');
    expect(result.fallbackChain.length).toBeGreaterThanOrEqual(2);
  });

  it('returns alternatives sorted by score', () => {
    const result = routeTask('pii_detection');
    for (let i = 0; i < result.alternatives.length - 1; i++) {
      expect(result.alternatives[i].score).toBeGreaterThanOrEqual(result.alternatives[i + 1].score);
    }
  });

  it('degrades score when quota is near limit', () => {
    const models = structuredClone(DEFAULT_MODELS);
    const cheap = models.find((m) => m.id === 'qwen-turbo')!;
    const scoreBeforeQuota = routeTask('classification', { preferLane: 'cheap', models }).score;
    cheap.quotaUsed = cheap.quotaLimit - 1; // near limit
    const scoreNearQuota = routeTask('classification', { preferLane: 'cheap', models }).score;
    expect(scoreNearQuota).toBeLessThan(scoreBeforeQuota);
  });
});

describe('Guard Brasil routing', () => {
  it('routes pii_detection to cheap lane', () => {
    const result = routeGuardBrasil('pii_detection');
    expect(result.selectedModel.lane).toBe('cheap');
  });

  it('routes bias_analysis to sovereign lane', () => {
    const result = routeGuardBrasil('bias_analysis');
    expect(result.selectedModel.lane).toBe('sovereign');
  });

  it('routes classification to cheap lane', () => {
    const result = routeGuardBrasil('classification');
    expect(result.selectedModel.lane).toBe('cheap');
  });
});

describe('Quota management', () => {
  it('increments quota usage', () => {
    const models = structuredClone(DEFAULT_MODELS);
    const model = models.find((m) => m.id === 'qwen-plus')!;
    expect(model.quotaUsed).toBe(0);
    reportUsage('qwen-plus', models);
    expect(model.quotaUsed).toBe(1);
  });

  it('resets all quotas', () => {
    const models = structuredClone(DEFAULT_MODELS);
    models.forEach((m) => { m.quotaUsed = 50; });
    resetQuotas(models);
    models.forEach((m) => expect(m.quotaUsed).toBe(0));
  });
});
