/**
 * @egos/guard-brasil — Tests
 *
 * Tests the GuardBrasil facade end-to-end with realistic inputs.
 */

import { GuardBrasil } from './guard.js';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function makeGuard(blockOnCriticalPII = false) {
  return GuardBrasil.create({ blockOnCriticalPII, lgpdDisclosure: true });
}

// ─── Clean output ─────────────────────────────────────────────────────────────

describe('GuardBrasil — clean output', () => {
  it('marks a clean response as safe', () => {
    const guard = makeGuard();
    const result = guard.inspect('O processo está em andamento. Aguarde contato.');
    expect(result.safe).toBe(true);
    expect(result.blocked).toBe(false);
    expect(result.masking.findings).toHaveLength(0);
    expect(result.atrian.passed).toBe(true);
    expect(result.lgpdDisclosure).toBe('');
  });
});

// ─── PII detection ────────────────────────────────────────────────────────────

describe('GuardBrasil — PII detection', () => {
  it('detects and masks CPF', () => {
    const guard = makeGuard();
    const result = guard.inspect('O CPF do solicitante é 123.456.789-09.');
    expect(result.masking.findings.some(f => f.category === 'cpf')).toBe(true);
    expect(result.output).not.toContain('123.456.789-09');
    expect(result.output).toContain('[CPF REMOVIDO]');
    expect(result.safe).toBe(false);
  });

  it('detects MASP', () => {
    const guard = makeGuard();
    const result = guard.inspect('Delegado MASP: 1234567 presente.');
    expect(result.masking.findings.some(f => f.category === 'masp')).toBe(true);
    expect(result.output).not.toContain('1234567');
  });

  it('detects REDS', () => {
    const guard = makeGuard();
    const result = guard.inspect('REDS 2024/0098765 foi registrado.');
    expect(result.masking.findings.some(f => f.category === 'reds')).toBe(true);
  });

  it('adds LGPD disclosure when PII found', () => {
    const guard = makeGuard();
    const result = guard.inspect('CPF: 111.222.333-44');
    expect(result.lgpdDisclosure).toContain('LGPD');
    expect(result.lgpdDisclosure).toContain('13.709/2018');
  });

  it('does NOT add LGPD disclosure for clean output', () => {
    const guard = makeGuard();
    const result = guard.inspect('Sem dados pessoais aqui.');
    expect(result.lgpdDisclosure).toBe('');
  });
});

// ─── ATRiAN validation ────────────────────────────────────────────────────────

describe('GuardBrasil — ATRiAN ethical validation', () => {
  it('flags absolute claim "com certeza"', () => {
    const guard = makeGuard();
    const result = guard.inspect('Com certeza o problema será resolvido.');
    expect(result.atrian.violations.some(v => v.category === 'absolute_claim')).toBe(true);
    // absolute claims are warnings, not errors — passes validation
    expect(result.atrian.score).toBeLessThan(100);
  });

  it('flags false promise', () => {
    const guard = makeGuard();
    const result = guard.inspect('Vamos resolver o caso imediatamente.');
    const hasFalsePromise = result.atrian.violations.some(v => v.category === 'false_promise');
    expect(hasFalsePromise).toBe(true);
    expect(result.atrian.passed).toBe(false);
  });

  it('flags fabricated data reference', () => {
    const guard = makeGuard();
    const result = guard.inspect('Segundo dados do Ministério da Justiça, 98% dos casos são resolvidos.');
    expect(result.atrian.violations.some(v => v.category === 'fabricated_data')).toBe(true);
    expect(result.atrian.passed).toBe(false);
  });

  it('blocks entity in blocklist', () => {
    const guard = GuardBrasil.create({ atrian: { blockedEntities: ['PROIBIDO'] } });
    const result = guard.inspect('Este sistema usa o módulo PROIBIDO para isso.');
    expect(result.atrian.violations.some(v => v.category === 'blocked_entity')).toBe(true);
    expect(result.atrian.passed).toBe(false);
    expect(result.output).toContain('***');
  });
});

// ─── blockOnCriticalPII ───────────────────────────────────────────────────────

describe('GuardBrasil — blockOnCriticalPII', () => {
  it('blocks output entirely when critical PII found and blockOnCriticalPII=true', () => {
    const guard = makeGuard(true);
    const result = guard.inspect('O CPF do agente é 999.888.777-66.');
    expect(result.blocked).toBe(true);
    expect(result.output).toContain('[CONTEÚDO BLOQUEADO');
  });

  it('masks (not blocks) critical PII by default', () => {
    const guard = makeGuard(false);
    const result = guard.inspect('CPF: 999.888.777-66');
    expect(result.blocked).toBe(false);
    expect(result.output).toContain('[CPF REMOVIDO]');
  });
});

// ─── Evidence chain ───────────────────────────────────────────────────────────

describe('GuardBrasil — evidence chain', () => {
  it('builds evidence chain when claims provided', () => {
    const guard = makeGuard();
    const result = guard.inspect('O suspeito foi identificado.', {
      sessionId: 'test-session',
      claims: [
        {
          claim: 'Suspeito identificado via sistema',
          source: 'boletim-interno',
          excerpt: 'registro #42',
          confidence: 'high',
        },
      ],
    });
    expect(result.evidenceChain).toBeDefined();
    expect(result.evidenceChain?.claims).toHaveLength(1);
    expect(result.evidenceChain?.auditHash).toMatch(/^ev-[0-9a-f]{8}$/);
    expect(result.evidenceBlock).toContain('[Evidências');
  });

  it('does not build evidence chain without claims', () => {
    const guard = makeGuard();
    const result = guard.inspect('Texto simples.');
    expect(result.evidenceChain).toBeUndefined();
    expect(result.evidenceBlock).toBeUndefined();
  });
});

// ─── Combined scenario ────────────────────────────────────────────────────────

describe('GuardBrasil — combined scenario', () => {
  it('handles text with PII + ATRiAN violations simultaneously', () => {
    const guard = makeGuard();
    const text = 'Com certeza o investigador de CPF 123.456.789-09 resolverá o caso. Vamos encaminhar isso agora.';
    const result = guard.inspect(text);

    expect(result.safe).toBe(false);
    expect(result.output).not.toContain('123.456.789-09');
    expect(result.atrian.violations.length).toBeGreaterThan(0);
    expect(result.summary).toContain('ATRiAN');
    expect(result.summary).toContain('PII');
    expect(result.lgpdDisclosure).toContain('LGPD');
  });
});
