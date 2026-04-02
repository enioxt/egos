/**
 * REAL tests for public-guard.ts — LGPD-compliant output masking.
 * Tests verify BEHAVIOR: masking, sensitivity levels, blocking, disclosure.
 *
 * Run: bun test packages/shared/src/__tests__/public-guard.test.ts
 */
import { describe, it, expect } from 'bun:test';
import { maskPublicOutput, isPublicSafe, buildLGPDDisclosure } from '../public-guard';

// ═══════════════════════════════════════════════════════════
// Basic masking — PII is removed from output
// ═══════════════════════════════════════════════════════════
describe('Public Guard — Basic masking', () => {
  it('masks CPF from output text', () => {
    const result = maskPublicOutput('O titular é João, CPF 123.456.789-00.');
    expect(result.masked).not.toContain('123.456.789-00');
    expect(result.safe).toBe(false);
    expect(result.findings.length).toBeGreaterThan(0);
  });

  it('marks clean text as safe', () => {
    const result = maskPublicOutput('Este texto não contém dados pessoais.');
    expect(result.safe).toBe(true);
    expect(result.findings.length).toBe(0);
    expect(result.masked).toBe(result.original);
  });

  it('masks email addresses', () => {
    const result = maskPublicOutput('Contato: maria@empresa.com.br para informações.');
    expect(result.masked).not.toContain('maria@empresa.com.br');
    expect(result.safe).toBe(false);
  });

  it('masks phone numbers', () => {
    const result = maskPublicOutput('Ligar para (11) 98765-4321 urgente.');
    expect(result.masked).not.toContain('98765-4321');
    expect(result.safe).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════
// Sensitivity levels — critical vs low
// ═══════════════════════════════════════════════════════════
describe('Public Guard — Sensitivity levels', () => {
  it('assigns critical for CPF (CRITICAL_CATEGORIES)', () => {
    const result = maskPublicOutput('CPF: 123.456.789-00');
    expect(result.sensitivityLevel).toBe('critical');
  });

  it('assigns low for email only (not in critical/high categories)', () => {
    const result = maskPublicOutput('Email: joao@test.com');
    expect(result.sensitivityLevel).toBe('low');
  });

  it('assigns low for clean text', () => {
    const result = maskPublicOutput('Texto limpo sem dados sensíveis.');
    expect(result.sensitivityLevel).toBe('low');
  });
});

// ═══════════════════════════════════════════════════════════
// Blocking — critical PII with block action
// ═══════════════════════════════════════════════════════════
describe('Public Guard — Blocking mode', () => {
  it('blocks entire output when criticalPiiAction is block and critical PII found', () => {
    const result = maskPublicOutput('O CPF 123.456.789-00 está no relatório.', {
      criticalPiiAction: 'block',
    });
    expect(result.masked).toContain('BLOQUEADO');
    expect(result.masked).not.toContain('123.456.789-00');
  });

  it('does NOT block when no critical PII even with block config', () => {
    const result = maskPublicOutput('Email: a@b.com apenas.', {
      criticalPiiAction: 'block',
    });
    expect(result.masked).not.toContain('BLOQUEADO');
    expect(result.masked).not.toContain('a@b.com');
  });
});

// ═══════════════════════════════════════════════════════════
// Actions audit trail
// ═══════════════════════════════════════════════════════════
describe('Public Guard — Actions audit', () => {
  it('tracks masking actions with counts and positions', () => {
    const result = maskPublicOutput('CPF 123.456.789-00 e CPF 987.654.321-00.');
    const cpfAction = result.actionsApplied.find(a => a.category === 'cpf');
    expect(cpfAction).toBeDefined();
    expect(cpfAction!.count).toBe(2);
    expect(cpfAction!.positions.length).toBe(2);
  });

  it('tracks multiple PII categories separately', () => {
    const result = maskPublicOutput('CPF 123.456.789-00, email x@y.com');
    const categories = result.actionsApplied.map(a => a.category);
    expect(categories).toContain('cpf');
    expect(categories).toContain('email');
  });
});

// ═══════════════════════════════════════════════════════════
// isPublicSafe — quick check
// ═══════════════════════════════════════════════════════════
describe('Public Guard — isPublicSafe', () => {
  it('returns true for clean text', () => {
    expect(isPublicSafe('Texto sem dados pessoais.')).toBe(true);
  });

  it('returns false when CPF present', () => {
    expect(isPublicSafe('CPF: 12345678900')).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════
// LGPD disclosure
// ═══════════════════════════════════════════════════════════
describe('Public Guard — LGPD disclosure', () => {
  it('generates disclosure when PII was masked', () => {
    const result = maskPublicOutput('CPF 123.456.789-00 no sistema.');
    const disclosure = buildLGPDDisclosure(result);
    expect(disclosure).toContain('LGPD');
    expect(disclosure).toContain('13.709/2018');
  });

  it('returns empty string when no PII found', () => {
    const result = maskPublicOutput('Nenhum dado pessoal aqui.');
    const disclosure = buildLGPDDisclosure(result);
    expect(disclosure).toBe('');
  });
});
