/**
 * REAL tests for cross-session-memory.ts — Cross-session conversation persistence.
 * Tests verify summarization, saving, retrieval, and threshold logic.
 * Uses mock Supabase client and mock LLM function.
 *
 * Run: bun test packages/shared/src/__tests__/cross-session-memory.test.ts
 */
import { describe, it, expect } from 'bun:test';
import {
  summarizeConversation,
  saveConversationSummary,
  getConversationMemory,
  shouldSummarizeConversation,
  type ConversationMessage,
} from '../cross-session-memory';

// Mock LLM function
const mockLLM = async (transcript: string) => ({
  text: `Resumo: ${transcript.slice(0, 50)}...`,
});

// Mock Supabase
function createMockSupabase() {
  const store = new Map<string, Record<string, unknown>>();

  return {
    store,
    from: (table: string) => ({
      insert: async (data: Record<string, unknown>) => {
        store.set(`${table}:${data.id}`, data);
        return { error: undefined };
      },
      select: (columns: string) => ({
        eq: (col: string, val: string) => ({
          maybeSingle: async () => {
            const key = `${table}:${val}`;
            return { data: store.get(key) || null, error: undefined };
          },
          order: (orderCol: string, opts: { ascending: boolean }) => ({
            limit: (n: number) => {
              const items = Array.from(store.values())
                .filter((item) => item[col] === val)
                .slice(0, n);
              return Promise.resolve({ data: items.length > 0 ? items : null, error: undefined });
            },
          }),
        }),
      }),
      update: (data: Record<string, unknown>) => ({
        eq: async (col: string, val: string) => {
          const key = `${table}:${val}`;
          const existing = store.get(key) || {};
          store.set(key, { ...existing, ...data });
          return { error: undefined };
        },
      }),
    }),
  };
}

// ═══════════════════════════════════════════════════════════
// Summarization
// ═══════════════════════════════════════════════════════════
describe('Cross-Session Memory — Summarization', () => {
  it('returns null for less than 4 messages', async () => {
    const messages: ConversationMessage[] = [
      { role: 'user', content: 'Olá' },
      { role: 'assistant', content: 'Oi!' },
      { role: 'user', content: 'Como vai?' },
    ];
    const result = await summarizeConversation(messages, mockLLM);
    expect(result).toBeNull();
  });

  it('summarizes conversations with 4+ messages', async () => {
    const messages: ConversationMessage[] = [
      { role: 'user', content: 'Preciso verificar um CNPJ' },
      { role: 'assistant', content: 'Claro, qual o CNPJ?' },
      { role: 'user', content: '12.345.678/0001-00' },
      { role: 'assistant', content: 'Empresa ativa desde 2020' },
    ];
    const result = await summarizeConversation(messages, mockLLM);
    expect(result).not.toBeNull();
    expect(result).toContain('Resumo');
  });

  it('truncates summary to maxSummaryLength', async () => {
    const longLLM = async () => ({ text: 'A'.repeat(2000) });
    const messages: ConversationMessage[] = Array(5).fill({ role: 'user', content: 'msg' });
    const result = await summarizeConversation(messages, longLLM, { maxSummaryLength: 100 });
    expect(result!.length).toBeLessThanOrEqual(100);
  });

  it('handles LLM errors gracefully', async () => {
    const failLLM = async () => { throw new Error('LLM timeout'); };
    const messages: ConversationMessage[] = Array(5).fill({ role: 'user', content: 'msg' });
    const result = await summarizeConversation(messages, failLLM);
    expect(result).toBeNull();
  });

  it('respects maxMessages limit', async () => {
    let receivedTranscript = '';
    const captureLLM = async (transcript: string) => {
      receivedTranscript = transcript;
      return { text: 'ok' };
    };
    const messages: ConversationMessage[] = Array(20).fill(null).map((_, i) => ({
      role: i % 2 === 0 ? 'user' : 'assistant',
      content: `Message ${i}`,
    }));
    await summarizeConversation(messages, captureLLM, { maxMessages: 5 });
    // Should only contain last 5 messages
    expect(receivedTranscript).toContain('Message 19');
    expect(receivedTranscript).toContain('Message 15');
    expect(receivedTranscript).not.toContain('Message 0');
  });
});

// ═══════════════════════════════════════════════════════════
// Saving summaries
// ═══════════════════════════════════════════════════════════
describe('Cross-Session Memory — Save', () => {
  it('saves summary to Supabase', async () => {
    const mock = createMockSupabase();
    // Pre-populate existing conversation
    mock.store.set('conversations:conv-1', { id: 'conv-1', metadata: {} });

    await saveConversationSummary(mock, 'conversations', 'conv-1', 'Resumo da conversa sobre CNPJ');
    const saved = mock.store.get('conversations:conv-1');
    expect(saved).toBeDefined();
    expect((saved!.metadata as any).summary).toBe('Resumo da conversa sobre CNPJ');
    expect((saved!.metadata as any).summaryUpdatedAt).toBeTruthy();
  });

  it('skips empty summaries', async () => {
    const mock = createMockSupabase();
    mock.store.set('conversations:conv-2', { id: 'conv-2', metadata: {} });
    await saveConversationSummary(mock, 'conversations', 'conv-2', '   ');
    // Metadata should not have been updated
    const saved = mock.store.get('conversations:conv-2');
    expect((saved!.metadata as any)?.summary).toBeUndefined();
  });
});

// ═══════════════════════════════════════════════════════════
// Memory retrieval
// ═══════════════════════════════════════════════════════════
describe('Cross-Session Memory — Retrieval', () => {
  it('returns null for null identityKey', async () => {
    const mock = createMockSupabase();
    const result = await getConversationMemory(mock, null, { tableName: 'conversations' });
    expect(result).toBeNull();
  });

  it('returns null when no data found', async () => {
    const mock = createMockSupabase();
    const result = await getConversationMemory(mock, 'user-123', { tableName: 'conversations' });
    expect(result).toBeNull();
  });

  it('returns formatted memory block when summaries exist', async () => {
    const mock = createMockSupabase();
    mock.store.set('conversations:row1', {
      session_hash: 'user-abc',
      title: 'Consulta CNPJ',
      metadata: { summary: 'Usuário verificou CNPJ 12.345' },
      updated_at: new Date().toISOString(),
    });

    const result = await getConversationMemory(mock, 'user-abc', { tableName: 'conversations' });
    expect(result).not.toBeNull();
    expect(result).toContain('PREVIOUS SESSION MEMORY');
    expect(result).toContain('Consulta CNPJ');
    expect(result).toContain('Usuário verificou CNPJ 12.345');
    expect(result).toContain('confirm with the user');
  });
});

// ═══════════════════════════════════════════════════════════
// shouldSummarizeConversation threshold
// ═══════════════════════════════════════════════════════════
describe('Cross-Session Memory — Threshold', () => {
  it('returns false for less than threshold', () => {
    expect(shouldSummarizeConversation(3)).toBe(false);
    expect(shouldSummarizeConversation(4)).toBe(false);
  });

  it('returns true at threshold when divisible by 5', () => {
    expect(shouldSummarizeConversation(5)).toBe(true);
    expect(shouldSummarizeConversation(10)).toBe(true);
    expect(shouldSummarizeConversation(15)).toBe(true);
  });

  it('returns false when not divisible by 5', () => {
    expect(shouldSummarizeConversation(6)).toBe(false);
    expect(shouldSummarizeConversation(11)).toBe(false);
  });

  it('supports custom threshold', () => {
    expect(shouldSummarizeConversation(10, 10)).toBe(true);
    expect(shouldSummarizeConversation(5, 10)).toBe(false);
  });
});
