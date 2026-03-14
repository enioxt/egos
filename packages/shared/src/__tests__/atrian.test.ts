/**
 * REAL tests for atrian.ts — adversarial prompt validation.
 * Tests verify that ATRiAN actually CATCHES violations, not just that it exists.
 *
 * Run: bun test packages/shared/src/__tests__/atrian.test.ts
 */
import { describe, it, expect } from 'bun:test';
import { createAtrianValidator } from '../atrian';

const atrian = createAtrianValidator({
  knownAcronyms: ['CPF', 'CNPJ', 'LGPD', 'ERP', 'RG', 'MASP', 'REDS', 'PCMG', 'SEDS', 'MG'],
  blockedEntities: ['Fulano de Tal', 'Juiz Secreto'],
});

// ═══════════════════════════════════════════════════════════
// Absolute claims — must be flagged
// ═══════════════════════════════════════════════════════════
describe('ATRiAN — Absolute claims', () => {
  it('flags "com certeza" as absolute claim', () => {
    const result = atrian.validateResponse('Com certeza o suspeito é culpado.');
    expect(result.violations.some(v => v.category === 'absolute_claim')).toBe(true);
    expect(result.score).toBeLessThan(100);
  });

  it('flags "nunca" as absolute claim', () => {
    const result = atrian.validateResponse('Ele nunca esteve no local do crime.');
    expect(result.violations.some(v => v.category === 'absolute_claim')).toBe(true);
  });

  it('flags "100%" as absolute claim', () => {
    const result = atrian.validateResponse('Tenho 100% de certeza sobre isso.');
    expect(result.violations.some(v => v.category === 'absolute_claim')).toBe(true);
  });

  it('passes clean text without absolute claims', () => {
    const result = atrian.validateResponse('De acordo com os dados disponíveis, há indícios de irregularidade.');
    const absolutes = result.violations.filter(v => v.category === 'absolute_claim');
    expect(absolutes.length).toBe(0);
  });
});

// ═══════════════════════════════════════════════════════════
// Fabricated data references — must be flagged
// ═══════════════════════════════════════════════════════════
describe('ATRiAN — Fabricated data', () => {
  it('flags "segundo dados da" as fabricated reference', () => {
    const result = atrian.validateResponse('Segundo dados da pesquisa nacional, o índice subiu 40%.');
    expect(result.violations.some(v => v.category === 'fabricated_data')).toBe(true);
    expect(result.passed).toBe(false);
  });

  it('flags "de acordo com relatórios da" as fabricated', () => {
    const result = atrian.validateResponse('De acordo com relatórios da assessoria, os números melhoraram.');
    expect(result.violations.some(v => v.category === 'fabricated_data')).toBe(true);
  });

  it('does NOT flag factual hedged statements', () => {
    const result = atrian.validateResponse('Os dados públicos do Portal da Transparência mostram gastos de R$ 1.2M.');
    const fabricated = result.violations.filter(v => v.category === 'fabricated_data');
    expect(fabricated.length).toBe(0);
  });
});

// ═══════════════════════════════════════════════════════════
// False promises — must be flagged
// ═══════════════════════════════════════════════════════════
describe('ATRiAN — False promises', () => {
  it('flags "vamos resolver" as false promise', () => {
    const result = atrian.validateResponse('Vamos resolver essa situação imediatamente.');
    expect(result.violations.some(v => v.category === 'false_promise')).toBe(true);
    expect(result.passed).toBe(false);
  });

  it('flags "providências serão tomadas" as false promise', () => {
    const result = atrian.validateResponse('Providências serão tomadas pela equipe responsável.');
    expect(result.violations.some(v => v.category === 'false_promise')).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════
// Blocked entities — critical level
// ═══════════════════════════════════════════════════════════
describe('ATRiAN — Blocked entities', () => {
  it('blocks mention of configured entity', () => {
    const result = atrian.validateResponse('O Fulano de Tal foi visto no local.');
    expect(result.violations.some(v => v.level === 'critical')).toBe(true);
    expect(result.passed).toBe(false);
    expect(result.score).toBeLessThanOrEqual(70);
  });

  it('filterChunk replaces blocked entity with ***', () => {
    const filtered = atrian.filterChunk('O Juiz Secreto decidiu o caso.');
    expect(filtered).not.toContain('Juiz Secreto');
    expect(filtered).toContain('***');
  });
});

// ═══════════════════════════════════════════════════════════
// Invented acronyms — must warn
// ═══════════════════════════════════════════════════════════
describe('ATRiAN — Invented acronyms', () => {
  it('flags unknown acronym XYZW as invented', () => {
    const result = atrian.validateResponse('O sistema XYZW detectou anomalias.');
    expect(result.violations.some(v => v.category === 'invented_acronym')).toBe(true);
  });

  it('does NOT flag known acronyms like CPF, LGPD', () => {
    const result = atrian.validateResponse('O CPF está protegido pela LGPD.');
    const invented = result.violations.filter(v => v.category === 'invented_acronym');
    expect(invented.length).toBe(0);
  });
});

// ═══════════════════════════════════════════════════════════
// Score calculation — must be deterministic
// ═══════════════════════════════════════════════════════════
describe('ATRiAN — Score', () => {
  it('clean text scores 100', () => {
    const result = atrian.validateResponse('Os dados públicos indicam uma tendência de crescimento moderado.');
    expect(result.score).toBe(100);
    expect(result.passed).toBe(true);
  });

  it('multiple violations compound score reduction', () => {
    const result = atrian.validateResponse('Com certeza vamos resolver isso. Segundo dados da ONG, 100% dos casos melhoraram. Providências serão tomadas.');
    expect(result.score).toBeLessThan(60);
    expect(result.passed).toBe(false);
  });

  it('score never goes below 0', () => {
    const badText = 'Com certeza sem dúvida sempre nunca 100% vamos resolver vamos garantir vamos providenciar segundo dados da segundo pesquisas da Fulano de Tal';
    const result = atrian.validateResponse(badText);
    expect(result.score).toBeGreaterThanOrEqual(0);
  });
});
