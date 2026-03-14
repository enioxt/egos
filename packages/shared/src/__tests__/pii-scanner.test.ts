/**
 * REAL tests for pii-scanner.ts — using actual Brazilian PII formats.
 * These tests verify BEHAVIOR, not string presence.
 *
 * Run: bun test packages/shared/src/__tests__/pii-scanner.test.ts
 */
import { describe, it, expect } from 'bun:test';
import { scanForPII, sanitizeText, getPIISummary } from '../pii-scanner';

// ═══════════════════════════════════════════════════════════
// Real CPF patterns (formatted and unformatted)
// ═══════════════════════════════════════════════════════════
describe('PII Scanner — CPF detection', () => {
  it('detects formatted CPF: 123.456.789-00', () => {
    const text = 'O CPF do contribuinte é 123.456.789-00 conforme registro.';
    const findings = scanForPII(text);
    const cpf = findings.find(f => f.category === 'cpf');
    expect(cpf).toBeDefined();
    expect(cpf!.matched).toBe('123.456.789-00');
  });

  it('detects unformatted CPF: 12345678900', () => {
    const text = 'CPF: 12345678900';
    const findings = scanForPII(text);
    const cpf = findings.find(f => f.category === 'cpf');
    expect(cpf).toBeDefined();
    expect(cpf!.matched).toBe('12345678900');
  });

  it('detects CPF with spaces: 123 456 789 00', () => {
    const text = 'Documento 123 456 789 00 verificado';
    const findings = scanForPII(text);
    const cpf = findings.find(f => f.category === 'cpf');
    expect(cpf).toBeDefined();
  });

  it('sanitizes CPF in output text', () => {
    const text = 'Titular: João, CPF 123.456.789-00, ativo.';
    const findings = scanForPII(text);
    const clean = sanitizeText(text, findings);
    expect(clean).not.toContain('123.456.789-00');
    expect(clean).toContain('[CPF REMOVIDO]');
  });
});

// ═══════════════════════════════════════════════════════════
// Real email patterns
// ═══════════════════════════════════════════════════════════
describe('PII Scanner — Email detection', () => {
  it('detects standard email', () => {
    const text = 'Contato: joao.silva@empresa.com.br para dúvidas.';
    const findings = scanForPII(text);
    const email = findings.find(f => f.category === 'email');
    expect(email).toBeDefined();
    expect(email!.matched).toBe('joao.silva@empresa.com.br');
  });

  it('does NOT false-positive on non-email @mentions', () => {
    const text = 'Siga @egos no Twitter';
    const findings = scanForPII(text);
    const email = findings.find(f => f.category === 'email');
    expect(email).toBeUndefined();
  });
});

// ═══════════════════════════════════════════════════════════
// Real phone patterns (Brazilian)
// ═══════════════════════════════════════════════════════════
describe('PII Scanner — Phone detection', () => {
  it('detects formatted phone: (31) 99876-5432', () => {
    const text = 'Ligue para (31) 99876-5432 para mais info.';
    const findings = scanForPII(text);
    const phone = findings.find(f => f.category === 'phone');
    expect(phone).toBeDefined();
  });

  it('detects phone with +55: +55 31 99876-5432', () => {
    const text = 'WhatsApp: +55 31 99876-5432';
    const findings = scanForPII(text);
    const phone = findings.find(f => f.category === 'phone');
    expect(phone).toBeDefined();
  });
});

// ═══════════════════════════════════════════════════════════
// Real vehicle plate patterns (BR)
// ═══════════════════════════════════════════════════════════
describe('PII Scanner — Vehicle plate detection', () => {
  it('detects old format plate: ABC-1234', () => {
    const text = 'Veículo com placa ABC-1234 registrado.';
    const findings = scanForPII(text);
    const plate = findings.find(f => f.category === 'plate');
    expect(plate).toBeDefined();
  });

  it('detects Mercosul plate: ABC1D23', () => {
    const text = 'Nova placa Mercosul: ABC1D23';
    const findings = scanForPII(text);
    const plate = findings.find(f => f.category === 'plate');
    expect(plate).toBeDefined();
  });
});

// ═══════════════════════════════════════════════════════════
// Combined: multiple PII in one text
// ═══════════════════════════════════════════════════════════
describe('PII Scanner — Combined detection + sanitization', () => {
  it('detects multiple PII types in one paragraph', () => {
    const text = `
      Relatório: O delegado João Silva, CPF 123.456.789-00,
      email joao@policia.mg.gov.br, telefone (31) 3333-4444,
      conduziu a operação com viatura placa HGT-5J67.
    `;
    const findings = scanForPII(text);
    const categories = new Set(findings.map(f => f.category));
    expect(categories.has('cpf')).toBe(true);
    expect(categories.has('email')).toBe(true);
    expect(categories.has('phone')).toBe(true);
    expect(categories.has('plate')).toBe(true);
  });

  it('sanitizeText replaces ALL PII findings', () => {
    const text = 'CPF: 123.456.789-00, Email: a@b.com';
    const findings = scanForPII(text);
    const clean = sanitizeText(text, findings);
    expect(clean).not.toContain('123.456.789-00');
    expect(clean).not.toContain('a@b.com');
    expect(clean).toContain('[CPF REMOVIDO]');
    expect(clean).toContain('[EMAIL REMOVIDO]');
  });

  it('getPIISummary reports correct count', () => {
    const findings = scanForPII('CPF 11122233344 email x@y.com');
    const summary = getPIISummary(findings);
    expect(summary).toContain('2');
    expect(summary).toContain('CPF');
    expect(summary).toContain('Email');
  });

  it('returns empty summary when no PII found', () => {
    const findings = scanForPII('Este texto não contém dados sensíveis.');
    expect(findings.length).toBe(0);
    expect(getPIISummary(findings)).toContain('Nenhum');
  });
});
