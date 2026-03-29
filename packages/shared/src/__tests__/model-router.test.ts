/**
 * REAL tests for model-router.ts — Task-aware LLM selection.
 * Tests verify routing logic, cost awareness, and availability checks.
 *
 * Run: bun test packages/shared/src/__tests__/model-router.test.ts
 */
import { describe, it, expect, beforeEach, afterEach } from 'bun:test';
import { resolveModel, routeForChat, listAvailableModels, MODEL_CATALOG } from '../model-router';

// Save and restore env
const savedEnv: Record<string, string | undefined> = {};

beforeEach(() => {
  // Save current env
  savedEnv.ALIBABA_DASHSCOPE_API_KEY = process.env.ALIBABA_DASHSCOPE_API_KEY;
  savedEnv.OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
});

afterEach(() => {
  // Restore env
  if (savedEnv.ALIBABA_DASHSCOPE_API_KEY !== undefined) {
    process.env.ALIBABA_DASHSCOPE_API_KEY = savedEnv.ALIBABA_DASHSCOPE_API_KEY;
  } else {
    delete process.env.ALIBABA_DASHSCOPE_API_KEY;
  }
  if (savedEnv.OPENROUTER_API_KEY !== undefined) {
    process.env.OPENROUTER_API_KEY = savedEnv.OPENROUTER_API_KEY;
  } else {
    delete process.env.OPENROUTER_API_KEY;
  }
});

// ═══════════════════════════════════════════════════════════
// Catalog integrity
// ═══════════════════════════════════════════════════════════
describe('Model Router — Catalog', () => {
  it('has at least 5 models in catalog', () => {
    expect(MODEL_CATALOG.length).toBeGreaterThanOrEqual(5);
  });

  it('every model has required fields', () => {
    for (const m of MODEL_CATALOG) {
      expect(m.id).toBeTruthy();
      expect(m.provider).toBeTruthy();
      expect(m.strengths.length).toBeGreaterThan(0);
      expect(m.tier).toBeTruthy();
      expect(m.envKey).toBeTruthy();
      expect(m.costPer1MInput).toBeGreaterThanOrEqual(0);
      expect(m.costPer1MOutput).toBeGreaterThanOrEqual(0);
    }
  });

  it('has at least one economy model', () => {
    const economy = MODEL_CATALOG.filter(m => m.tier === 'economy');
    expect(economy.length).toBeGreaterThan(0);
  });

  it('has at least one premium model', () => {
    const premium = MODEL_CATALOG.filter(m => m.tier === 'premium');
    expect(premium.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════
// Routing logic — task matching
// ═══════════════════════════════════════════════════════════
describe('Model Router — Routing', () => {
  it('routes fast_check to economy model', () => {
    process.env.ALIBABA_DASHSCOPE_API_KEY = 'test-key';
    const route = resolveModel({ task: 'fast_check', cost: 'economy' });
    expect(route.profile.tier).toBe('economy');
  });

  it('routes orchestration with premium preference to premium model', () => {
    process.env.ALIBABA_DASHSCOPE_API_KEY = 'test-key';
    process.env.OPENROUTER_API_KEY = 'test-key';
    const route = resolveModel({ task: 'orchestration', cost: 'premium' });
    expect(route.profile.tier).toBe('premium');
  });

  it('prefers alibaba provider when specified', () => {
    process.env.ALIBABA_DASHSCOPE_API_KEY = 'test-key';
    process.env.OPENROUTER_API_KEY = 'test-key';
    const route = resolveModel({ task: 'chat', preferProvider: 'alibaba' });
    expect(route.provider).toBe('alibaba');
  });

  it('throws when no provider available', () => {
    delete process.env.ALIBABA_DASHSCOPE_API_KEY;
    delete process.env.OPENROUTER_API_KEY;
    expect(() => resolveModel('chat')).toThrow('No LLM provider available');
  });

  it('accepts string shorthand for task', () => {
    process.env.ALIBABA_DASHSCOPE_API_KEY = 'test-key';
    const route = resolveModel('summarization');
    expect(route.model).toBeTruthy();
    expect(route.provider).toBeTruthy();
  });
});

// ═══════════════════════════════════════════════════════════
// Context filtering
// ═══════════════════════════════════════════════════════════
describe('Model Router — Context filtering', () => {
  it('filters by minContext requirement', () => {
    process.env.ALIBABA_DASHSCOPE_API_KEY = 'test-key';
    process.env.OPENROUTER_API_KEY = 'test-key';
    const route = resolveModel({ task: 'analysis', minContext: 200000 });
    expect(route.profile.maxContext).toBeGreaterThanOrEqual(200000);
  });
});

// ═══════════════════════════════════════════════════════════
// routeForChat — convenience wrapper
// ═══════════════════════════════════════════════════════════
describe('Model Router — routeForChat', () => {
  it('returns model and provider only', () => {
    process.env.ALIBABA_DASHSCOPE_API_KEY = 'test-key';
    const result = routeForChat('chat');
    expect(result).toHaveProperty('model');
    expect(result).toHaveProperty('provider');
    expect(Object.keys(result).length).toBe(2);
  });
});

// ═══════════════════════════════════════════════════════════
// Cheap-first policy (EGOS-071)
// ═══════════════════════════════════════════════════════════
describe('Model Router — Cheap-first policy', () => {
  it('defaults to economy tier (cheap-first)', () => {
    process.env.ALIBABA_DASHSCOPE_API_KEY = 'test-key';
    // Default cost preference should be 'economy'
    const route = resolveModel('chat');
    expect(route.profile.tier).toBe('economy');
  });

  it('routes fast_check to free qwen-flash by default', () => {
    process.env.ALIBABA_DASHSCOPE_API_KEY = 'test-key';
    const route = resolveModel('fast_check');
    expect(route.model).toBe('qwen-flash');
    expect(route.profile.costPer1MInput).toBe(0);
  });

  it('breaks ties by lower cost', () => {
    process.env.ALIBABA_DASHSCOPE_API_KEY = 'test-key';
    process.env.OPENROUTER_API_KEY = 'test-key';
    // summarization has multiple economy options - should pick cheapest
    const route = resolveModel('summarization');
    expect(route.profile.costPer1MInput).toBeLessThanOrEqual(0.1);
  });

  it('can override to premium when needed', () => {
    process.env.ALIBABA_DASHSCOPE_API_KEY = 'test-key';
    process.env.OPENROUTER_API_KEY = 'test-key';
    const route = resolveModel({ task: 'orchestration', cost: 'premium' });
    expect(route.profile.tier).toBe('premium');
  });
});

// ═══════════════════════════════════════════════════════════
// listAvailableModels
// ═══════════════════════════════════════════════════════════
describe('Model Router — listAvailableModels', () => {
  it('marks models as available when env key is set', () => {
    process.env.ALIBABA_DASHSCOPE_API_KEY = 'test-key';
    delete process.env.OPENROUTER_API_KEY;
    const models = listAvailableModels();
    const alibaba = models.filter(m => m.provider === 'alibaba');
    const openrouter = models.filter(m => m.provider === 'openrouter');
    for (const m of alibaba) expect(m.available).toBe(true);
    for (const m of openrouter) expect(m.available).toBe(false);
  });
});
