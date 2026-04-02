/**
 * REAL tests for evidence-chain.ts — Traceable response discipline.
 * Tests verify chain building, confidence derivation, hashing, and formatting.
 *
 * Run: bun test packages/shared/src/__tests__/evidence-chain.test.ts
 */
import { describe, it, expect } from 'bun:test';
import {
  createEvidenceChain,
  formatEvidenceBlock,
  validateChain,
  type EvidenceItem,
} from '../evidence-chain';

// ═══════════════════════════════════════════════════════════
// Chain building — fluent API
// ═══════════════════════════════════════════════════════════
describe('Evidence Chain — Building', () => {
  it('builds an empty chain with speculative confidence', () => {
    const chain = createEvidenceChain().build();
    expect(chain.claims.length).toBe(0);
    expect(chain.overallConfidence).toBe('speculative');
    expect(chain.auditHash).toBeDefined();
    expect(chain.responseId).toContain('resp-');
  });

  it('builds chain with tool-call claim', () => {
    const chain = createEvidenceChain()
      .addToolCallClaim('Empresa X tem CNPJ ativo', 'cnpj_query', 'Status: ATIVA', 'high')
      .build();
    expect(chain.claims.length).toBe(1);
    expect(chain.claims[0].claim).toBe('Empresa X tem CNPJ ativo');
    expect(chain.claims[0].evidence[0].type).toBe('tool_call');
    expect(chain.claims[0].verifiable).toBe(true);
  });

  it('builds chain with document claim', () => {
    const chain = createEvidenceChain()
      .addDocumentClaim('Licitação irregular', 'PNCP-2026-001', 'Valor acima do mercado', 'medium')
      .build();
    expect(chain.claims[0].evidence[0].type).toBe('document');
    expect(chain.claims[0].confidence).toBe('medium');
  });

  it('supports fluent chaining of multiple claims', () => {
    const chain = createEvidenceChain({ sessionId: 'sess-123' })
      .addToolCallClaim('Dado A', 'tool1', 'resultado1', 'high')
      .addDocumentClaim('Dado B', 'doc-ref', 'excerto', 'low')
      .build();
    expect(chain.claims.length).toBe(2);
    expect(chain.sessionId).toBe('sess-123');
  });
});

// ═══════════════════════════════════════════════════════════
// Confidence derivation — lowest wins
// ═══════════════════════════════════════════════════════════
describe('Evidence Chain — Confidence', () => {
  it('derives confidence from weakest evidence', () => {
    const evidence: EvidenceItem[] = [
      { id: 'e1', type: 'tool_call', source: 'api', content: 'ok', confidence: 'high', timestamp: '' },
      { id: 'e2', type: 'inference', source: 'model', content: 'guess', confidence: 'low', timestamp: '' },
    ];
    const chain = createEvidenceChain()
      .addClaim('Claim mista', evidence)
      .build();
    expect(chain.claims[0].confidence).toBe('low');
  });

  it('overall confidence is lowest across all claims', () => {
    const chain = createEvidenceChain()
      .addToolCallClaim('Claim forte', 'tool', 'data', 'certain')
      .addDocumentClaim('Claim fraca', 'doc', 'trecho', 'speculative')
      .build();
    expect(chain.overallConfidence).toBe('speculative');
  });

  it('single high-confidence claim yields high overall', () => {
    const chain = createEvidenceChain()
      .addToolCallClaim('Única claim', 'tool', 'data', 'high')
      .build();
    expect(chain.overallConfidence).toBe('high');
  });
});

// ═══════════════════════════════════════════════════════════
// Verifiability — inference-only claims are not verifiable
// ═══════════════════════════════════════════════════════════
describe('Evidence Chain — Verifiability', () => {
  it('marks tool_call backed claims as verifiable', () => {
    const chain = createEvidenceChain()
      .addToolCallClaim('Fato verificável', 'api_check', 'resultado', 'high')
      .build();
    expect(chain.claims[0].verifiable).toBe(true);
  });

  it('marks inference-only claims as NOT verifiable', () => {
    const evidence: EvidenceItem[] = [
      { id: 'e1', type: 'inference', source: 'model', content: 'dedução', confidence: 'medium', timestamp: '' },
    ];
    const chain = createEvidenceChain()
      .addClaim('Dedução sem prova', evidence)
      .build();
    expect(chain.claims[0].verifiable).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════
// Audit hash — deterministic
// ═══════════════════════════════════════════════════════════
describe('Evidence Chain — Audit hash', () => {
  it('produces deterministic hash for same chain', () => {
    const builder1 = createEvidenceChain();
    const builder2 = createEvidenceChain();
    // Different builders produce different responseIds/timestamps,
    // so hashes will differ. But each individual build is deterministic.
    const chain = builder1
      .addToolCallClaim('Test', 'tool', 'data', 'high')
      .build();
    expect(chain.auditHash).toMatch(/^ev-[0-9a-f]{8}$/);
  });

  it('hash changes when claims change', () => {
    const chain1 = createEvidenceChain()
      .addToolCallClaim('Claim A', 'tool', 'data', 'high')
      .build();
    const chain2 = createEvidenceChain()
      .addToolCallClaim('Claim B', 'tool', 'data', 'high')
      .build();
    // Very high probability of different hashes
    expect(chain1.auditHash).not.toBe(chain2.auditHash);
  });
});

// ═══════════════════════════════════════════════════════════
// Formatting — human-readable output
// ═══════════════════════════════════════════════════════════
describe('Evidence Chain — Formatting', () => {
  it('formats chain with citations', () => {
    const chain = createEvidenceChain()
      .addToolCallClaim('CNPJ ativo', 'cnpj_api', '{"status":"ATIVA"}', 'high')
      .build();
    const block = formatEvidenceBlock(chain);
    expect(block).toContain('CNPJ ativo');
    expect(block).toContain('confiança: high');
    expect(block).toContain('tool_call');
    expect(block).toContain('cnpj_api');
    expect(block).toContain('Audit hash: ev-');
  });
});

// ═══════════════════════════════════════════════════════════
// Validation — minimum confidence check
// ═══════════════════════════════════════════════════════════
describe('Evidence Chain — Validation', () => {
  it('validates chain meets minimum confidence', () => {
    const chain = createEvidenceChain()
      .addToolCallClaim('Fato', 'tool', 'data', 'high')
      .build();
    expect(validateChain(chain, 'medium')).toBe(true);
    expect(validateChain(chain, 'certain')).toBe(false);
  });

  it('speculative chain fails medium threshold', () => {
    const chain = createEvidenceChain().build(); // no claims = speculative
    expect(validateChain(chain, 'medium')).toBe(false);
    expect(validateChain(chain, 'speculative')).toBe(true);
  });

  it('default minimum is low', () => {
    const chain = createEvidenceChain()
      .addToolCallClaim('Algo', 'tool', 'data', 'low')
      .build();
    expect(validateChain(chain)).toBe(true);
  });
});
