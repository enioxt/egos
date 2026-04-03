/**
 * REAL tests for guard-brasil.ts — Unified Brazilian AI Safety Layer.
 * Tests verify the combined ATRiAN + PII + LGPD pipeline.
 *
 * Run: bun test packages/shared/src/__tests__/guard-brasil.test.ts
 */
import { describe, it, expect } from 'bun:test';
import { createGuardBrasil } from '../guard-brasil';
import { getGuardBrasilUsageTier, priceGuardBrasilCalls } from '../billing/pricing';

const guard = createGuardBrasil({
  atrian: {
    knownAcronyms: ['CPF', 'CNPJ', 'LGPD', 'RG'],
    blockedEntities: ['Fulano de Tal'],
  },
});

// ═══════════════════════════════════════════════════════════
// Clean text — passes all checks
// ═══════════════════════════════════════════════════════════
describe('Guard Brasil — Clean text', () => {
  it('marks clean text as safe', () => {
    const result = guard.validate('Os dados públicos indicam crescimento moderado no setor.');
    expect(result.safe).toBe(true);
    expect(result.atrianScore).toBe(100);
    expect(result.atrianPassed).toBe(true);
    expect(result.piiCount).toBe(0);
    expect(result.lgpdDisclosure).toBe('');
  });
});

// ═══════════════════════════════════════════════════════════
// PII detected — not safe
// ═══════════════════════════════════════════════════════════
describe('Guard Brasil — PII detection', () => {
  it('flags text with CPF as unsafe', () => {
    const result = guard.validate('O titular João, CPF 123.456.789-00, está ativo.');
    expect(result.safe).toBe(false);
    expect(result.piiCount).toBeGreaterThan(0);
    expect(result.maskedText).not.toContain('123.456.789-00');
    expect(result.sensitivityLevel).toBe('critical');
  });

  it('generates LGPD disclosure for PII', () => {
    const result = guard.validate('Email: joao@empresa.com.br');
    expect(result.lgpdDisclosure).toContain('LGPD');
    expect(result.lgpdDisclosure).toContain('13.709/2018');
  });
});

// ═══════════════════════════════════════════════════════════
// ATRiAN violations — ethical issues
// ═══════════════════════════════════════════════════════════
describe('Guard Brasil — ATRiAN violations', () => {
  it('flags absolute claims and reduces score', () => {
    const result = guard.validate('Com certeza o suspeito é culpado.');
    expect(result.atrian.violations.some(v => v.category === 'absolute_claim')).toBe(true);
    expect(result.atrianScore).toBeLessThan(100);
  });

  it('flags fabricated data references', () => {
    const result = guard.validate('Segundo dados da pesquisa nacional, o índice subiu 40%.');
    expect(result.atrianPassed).toBe(false);
    expect(result.safe).toBe(false);
  });

  it('flags blocked entities at critical level', () => {
    const result = guard.validate('O Fulano de Tal foi visto no local.');
    expect(result.atrianScore).toBeLessThanOrEqual(70);
    expect(result.safe).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════
// Combined violations — PII + ATRiAN
// ═══════════════════════════════════════════════════════════
describe('Guard Brasil — Combined violations', () => {
  it('catches both PII and ethical violations in one pass', () => {
    const result = guard.validate(
      'Com certeza o CPF 123.456.789-00 pertence ao Fulano de Tal. Segundo dados da pesquisa, vamos resolver isso.'
    );
    expect(result.safe).toBe(false);
    expect(result.piiCount).toBeGreaterThan(0);
    expect(result.atrianScore).toBeLessThan(60);
    expect(result.maskedText).not.toContain('123.456.789-00');
  });
});

// ═══════════════════════════════════════════════════════════
// Custom configuration
// ═══════════════════════════════════════════════════════════
describe('Guard Brasil — Configuration', () => {
  it('supports custom minAtrianScore threshold', () => {
    const strict = createGuardBrasil({ minAtrianScore: 99 });
    // "Com certeza" deducts 5 points → score 95, below 99 threshold → unsafe
    const result = strict.validate('Com certeza isso é verdade. Segundo dados da pesquisa, sempre funciona.');
    expect(result.atrianScore).toBeLessThan(99);
    expect(result.safe).toBe(false);
  });

  it('works with empty config', () => {
    const defaultGuard = createGuardBrasil();
    const result = defaultGuard.validate('Texto simples e seguro.');
    expect(result.safe).toBe(true);
  });
});

describe('Guard Brasil — Usage pricing', () => {
  it('keeps the free tier for 150 monthly calls', () => {
    const tier = getGuardBrasilUsageTier(150);
    const estimate = priceGuardBrasilCalls(150);

    expect(tier.id).toBe('free');
    expect(estimate.totalBrl).toBe(0);
  });

  it('uses pro tier pricing at 10k monthly calls', () => {
    const tier = getGuardBrasilUsageTier(10_000);
    const estimate = priceGuardBrasilCalls(10_000);

    expect(tier.id).toBe('pro'); // 10k is within pro tier (≤50k)
    expect(estimate.totalBrl).toBe(70); // 10k × R$0.007 = R$70
  });

  it('uses enterprise pricing above 500k monthly calls', () => {
    const tier = getGuardBrasilUsageTier(750_000);
    const estimate = priceGuardBrasilCalls(750_000);

    expect(tier.id).toBe('enterprise');
    expect(estimate.totalBrl).toBe(1500); // 750k × R$0.002 = R$1.500
  });
});
