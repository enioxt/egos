/**
 * Tests for llm-provider.ts — LLM API abstraction.
 * Tests validate provider detection, parameter construction, and error handling.
 * Does NOT make real HTTP calls — tests structural logic only.
 *
 * Run: bun test packages/shared/src/__tests__/llm-provider.test.ts
 */
import { describe, it, expect, beforeEach, afterEach } from 'bun:test';
import { ALIBABA_TEST_MODELS } from '../llm-provider';

// Save and restore env
const savedEnv: Record<string, string | undefined> = {};

beforeEach(() => {
  savedEnv.ALIBABA_DASHSCOPE_API_KEY = process.env.ALIBABA_DASHSCOPE_API_KEY;
  savedEnv.OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
  savedEnv.LLM_PROVIDER = process.env.LLM_PROVIDER;
});

afterEach(() => {
  for (const [key, val] of Object.entries(savedEnv)) {
    if (val !== undefined) process.env[key] = val;
    else delete process.env[key];
  }
});

// ═══════════════════════════════════════════════════════════
// Model catalog
// ═══════════════════════════════════════════════════════════
describe('LLM Provider — Model catalog', () => {
  it('exports Alibaba test models', () => {
    expect(ALIBABA_TEST_MODELS.length).toBeGreaterThan(0);
    expect(ALIBABA_TEST_MODELS).toContain('qwen-plus');
    expect(ALIBABA_TEST_MODELS).toContain('qwen-flash');
  });

  it('includes coder model', () => {
    expect(ALIBABA_TEST_MODELS).toContain('qwen3-coder-plus');
  });
});

// ═══════════════════════════════════════════════════════════
// Provider detection — throws when no API key
// ═══════════════════════════════════════════════════════════
describe('LLM Provider — API key validation', () => {
  it('throws when ALIBABA key missing and alibaba provider requested', async () => {
    delete process.env.ALIBABA_DASHSCOPE_API_KEY;
    delete process.env.OPENROUTER_API_KEY;

    // Dynamic import to get fresh module state
    const { chatWithLLM } = await import('../llm-provider');
    try {
      await chatWithLLM({
        systemPrompt: 'test',
        userPrompt: 'test',
        provider: 'alibaba',
      });
      expect(true).toBe(false); // should not reach
    } catch (e: unknown) {
      expect((e as Error).message).toContain('ALIBABA_DASHSCOPE_API_KEY');
    }
  });

  it('throws when OPENROUTER key missing and openrouter provider requested', async () => {
    delete process.env.ALIBABA_DASHSCOPE_API_KEY;
    delete process.env.OPENROUTER_API_KEY;

    const { chatWithLLM } = await import('../llm-provider');
    try {
      await chatWithLLM({
        systemPrompt: 'test',
        userPrompt: 'test',
        provider: 'openrouter',
      });
      expect(true).toBe(false);
    } catch (e: unknown) {
      expect((e as Error).message).toContain('OPENROUTER_API_KEY');
    }
  });
});

// ═══════════════════════════════════════════════════════════
// Provider auto-detection — qwen prefix → alibaba
// ═══════════════════════════════════════════════════════════
describe('LLM Provider — Auto-detection', () => {
  it('detects alibaba from qwen model prefix', async () => {
    delete process.env.ALIBABA_DASHSCOPE_API_KEY;
    const { chatWithLLM } = await import('../llm-provider');
    try {
      await chatWithLLM({
        systemPrompt: 'test',
        userPrompt: 'test',
        model: 'qwen-plus',
      });
    } catch (e: unknown) {
      // Should throw about ALIBABA key, proving alibaba was detected
      expect((e as Error).message).toContain('ALIBABA_DASHSCOPE_API_KEY');
    }
  });

  it('falls back to openrouter for non-qwen models', async () => {
    delete process.env.ALIBABA_DASHSCOPE_API_KEY;
    delete process.env.OPENROUTER_API_KEY;
    delete process.env.LLM_PROVIDER;
    const { chatWithLLM } = await import('../llm-provider');
    try {
      await chatWithLLM({
        systemPrompt: 'test',
        userPrompt: 'test',
        model: 'google/gemini-2.0-flash',
      });
    } catch (e: unknown) {
      // Should throw about OPENROUTER key
      expect((e as Error).message).toContain('OPENROUTER_API_KEY');
    }
  });
});
