/**
 * REAL tests for conversation-memory.ts — behavior verification.
 *
 * Run: bun test packages/shared/src/__tests__/conversation-memory.test.ts
 */
import { describe, it, expect } from 'bun:test';
import {
  shouldSummarizeConversation,
  buildConversationTranscript,
  normalizeConversationSummary,
  buildConversationMemoryBlock,
} from '../conversation-memory';

// ═══════════════════════════════════════════════════════════
// shouldSummarizeConversation
// ═══════════════════════════════════════════════════════════
describe('shouldSummarizeConversation', () => {
  it('returns false for fewer than 4 messages', () => {
    const msgs = [
      { role: 'user', content: 'Olá' },
      { role: 'assistant', content: 'Oi!' },
    ];
    expect(shouldSummarizeConversation(msgs)).toBe(false);
  });

  it('returns true for 4+ messages', () => {
    const msgs = Array.from({ length: 5 }, (_, i) => ({
      role: i % 2 === 0 ? 'user' : 'assistant',
      content: `Mensagem ${i}`,
    }));
    expect(shouldSummarizeConversation(msgs)).toBe(true);
  });

  it('respects custom minimumMessagesForSummary', () => {
    const msgs = [{ role: 'user', content: 'a' }, { role: 'assistant', content: 'b' }];
    expect(shouldSummarizeConversation(msgs, { minimumMessagesForSummary: 2 })).toBe(true);
    expect(shouldSummarizeConversation(msgs, { minimumMessagesForSummary: 3 })).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════
// buildConversationTranscript
// ═══════════════════════════════════════════════════════════
describe('buildConversationTranscript', () => {
  it('truncates to last 12 messages by default', () => {
    const msgs = Array.from({ length: 20 }, (_, i) => ({
      role: 'user',
      content: `msg-${i}`,
    }));
    const transcript = buildConversationTranscript(msgs);
    expect(transcript).not.toContain('msg-0');
    expect(transcript).toContain('msg-19');
    expect(transcript).toContain('msg-8');
  });

  it('truncates message content at 400 chars', () => {
    const longContent = 'A'.repeat(500);
    const msgs = [{ role: 'user', content: longContent }];
    const transcript = buildConversationTranscript(msgs);
    expect(transcript.length).toBeLessThan(500);
  });

  it('uses correct speaker labels', () => {
    const msgs = [
      { role: 'user', content: 'pergunta' },
      { role: 'assistant', content: 'resposta' },
    ];
    const transcript = buildConversationTranscript(msgs);
    expect(transcript).toContain('USUÁRIO: pergunta');
    expect(transcript).toContain('AGENTE: resposta');
  });
});

// ═══════════════════════════════════════════════════════════
// normalizeConversationSummary
// ═══════════════════════════════════════════════════════════
describe('normalizeConversationSummary', () => {
  it('returns null for empty/null input', () => {
    expect(normalizeConversationSummary(null)).toBeNull();
    expect(normalizeConversationSummary(undefined)).toBeNull();
    expect(normalizeConversationSummary('')).toBeNull();
    expect(normalizeConversationSummary('   ')).toBeNull();
  });

  it('trims whitespace', () => {
    expect(normalizeConversationSummary('  hello  ')).toBe('hello');
  });

  it('truncates at maxSummaryLength', () => {
    const long = 'X'.repeat(2000);
    const result = normalizeConversationSummary(long, { maxSummaryLength: 100 });
    expect(result!.length).toBe(100);
  });
});

// ═══════════════════════════════════════════════════════════
// buildConversationMemoryBlock
// ═══════════════════════════════════════════════════════════
describe('buildConversationMemoryBlock', () => {
  it('returns null when no valid summaries', () => {
    const result = buildConversationMemoryBlock([
      { title: 'Test', summary: null },
      { title: 'Test2', summary: '' },
    ]);
    expect(result).toBeNull();
  });

  it('builds block with heading and footer', () => {
    const result = buildConversationMemoryBlock([
      { title: 'Sessão 1', summary: 'Discutimos o plano de ação.' },
      { title: 'Sessão 2', summary: 'Revisamos os agentes.' },
    ]);
    expect(result).not.toBeNull();
    expect(result).toContain('MEMÓRIA DE SESSÕES ANTERIORES');
    expect(result).toContain('Sessão 1: Discutimos');
    expect(result).toContain('Sessão 2: Revisamos');
    expect(result).toContain('desatualizado');
  });

  it('uses default title when none provided', () => {
    const result = buildConversationMemoryBlock([
      { summary: 'Algo importante aconteceu.' },
    ]);
    expect(result).toContain('Conversa anterior');
  });

  it('filters out items with no summary', () => {
    const result = buildConversationMemoryBlock([
      { title: 'A', summary: 'Real summary' },
      { title: 'B', summary: null },
      { title: 'C', summary: 'Another real one' },
    ]);
    expect(result).toContain('A: Real summary');
    expect(result).not.toContain('B:');
    expect(result).toContain('C: Another real one');
  });
});
