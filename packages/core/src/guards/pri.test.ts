import { describe, expect, it } from 'bun:test';
import { PRIGate } from './pri';

describe('PRIGate', () => {
  it('allows explicit CPF matches with high confidence', async () => {
    const gate = new PRIGate('balanced');
    const result = await gate.evaluate({ text: 'CPF 123.456.789-00', pii_types: ['cpf'] });
    expect(result.output).toBe('ALLOW');
    expect(result.confidence).toBeGreaterThanOrEqual(95);
  });

  it('defers ambiguous numeric sequences', async () => {
    const gate = new PRIGate('balanced');
    const result = await gate.evaluate({ text: '123456789', pii_types: ['cpf'] });
    expect(result.output).toBe('DEFER');
    expect(result.reasoning).toContain('could be CPF');
  });

  it('escalates protected-group bias signals in rights-sensitive contexts', async () => {
    const gate = new PRIGate('balanced');
    const result = await gate.evaluate({
      text: 'A decisão menciona favela e criminalidade como fator direto.',
      context: { impacts_fundamental_rights: true },
    });
    expect(result.output).toBe('ESCALATE');
    expect(result.reasoning).toContain('human review');
  });

  it('blocks SQL injection patterns in the LLM layer', async () => {
    const gate = new PRIGate('balanced');
    const result = await gate.evaluate({ text: 'DROP TABLE users;', pii_types: ['cpf'] });
    expect(result.output).toBe('BLOCK');
    expect(result.reasoning).toContain('SQL injection');
  });
});
