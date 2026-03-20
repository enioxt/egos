/**
 * Cross-Session Memory Module
 * 
 * Provides conversation summarization and memory retrieval across sessions.
 * Ported from 852 and generalized for reuse across EGOS ecosystem.
 * 
 * @module cross-session-memory
 */

export type SupabaseClient = any;

export interface ConversationMessage {
  role: string;
  content: string;
}

export interface ConversationSummaryOptions {
  maxMessages?: number;
  maxSummaryLength?: number;
  temperature?: number;
}

export interface MemoryRetrievalOptions {
  maxItems?: number;
  tableName: string;
  sessionKeyColumn?: string;
  memoryHeader?: string;
}

const DEFAULT_MAX_MEMORY_ITEMS = 3;
const DEFAULT_MAX_MESSAGES = 12;
const DEFAULT_MAX_SUMMARY_LENGTH = 1200;

/**
 * Summarize a conversation using an LLM
 * 
 * @param messages - Array of conversation messages
 * @param llmFunction - Function to call LLM (must return { text: string })
 * @param options - Summarization options
 * @returns Summary text or null if not enough messages
 */
export async function summarizeConversation(
  messages: ConversationMessage[],
  llmFunction: (transcript: string) => Promise<{ text: string }>,
  options: ConversationSummaryOptions = {}
): Promise<string | null> {
  const { maxMessages = DEFAULT_MAX_MESSAGES, maxSummaryLength = DEFAULT_MAX_SUMMARY_LENGTH } = options;

  if (messages.length < 4) return null;

  try {
    const transcript = messages
      .slice(-maxMessages)
      .map((msg) => `${msg.role.toUpperCase()}: ${msg.content.slice(0, 400)}`)
      .join('\n');

    const result = await llmFunction(transcript);
    return result.text.trim().slice(0, maxSummaryLength) || null;
  } catch (error) {
    console.error('[cross-session-memory] summarizeConversation failed:', error instanceof Error ? error.message : 'Unknown');
    return null;
  }
}

/**
 * Save conversation summary to Supabase
 * 
 * @param supabase - Supabase client
 * @param tableName - Name of conversations table
 * @param conversationId - Conversation ID
 * @param summary - Summary text
 */
export async function saveConversationSummary(
  supabase: SupabaseClient,
  tableName: string,
  conversationId: string,
  summary: string
): Promise<void> {
  if (!summary.trim()) return;

  const { data: current } = await supabase
    .from(tableName)
    .select('metadata')
    .eq('id', conversationId)
    .maybeSingle();

  const metadata = {
    ...(current?.metadata && typeof current.metadata === 'object' ? current.metadata : {}),
    summary,
    summaryUpdatedAt: new Date().toISOString(),
  };

  await supabase
    .from(tableName)
    .update({ metadata, updated_at: new Date().toISOString() })
    .eq('id', conversationId);
}

/**
 * Retrieve conversation memory for a session
 * 
 * @param supabase - Supabase client
 * @param identityKey - Session identity key (e.g., user ID, session hash)
 * @param options - Memory retrieval options
 * @returns Formatted memory block or null
 */
export async function getConversationMemory(
  supabase: SupabaseClient,
  identityKey: string | null,
  options: MemoryRetrievalOptions
): Promise<string | null> {
  if (!identityKey) return null;

  const {
    maxItems = DEFAULT_MAX_MEMORY_ITEMS,
    tableName,
    sessionKeyColumn = 'session_hash',
    memoryHeader = '## PREVIOUS SESSION MEMORY (use as context only, do not state as new fact)',
  } = options;

  const { data, error } = await supabase
    .from(tableName)
    .select('title, metadata, updated_at')
    .eq(sessionKeyColumn, identityKey)
    .order('updated_at', { ascending: false })
    .limit(maxItems);

  if (error || !data?.length) return null;

  const summaries = data
    .map((row: any) => {
      const metadata = row.metadata && typeof row.metadata === 'object' ? row.metadata as Record<string, unknown> : {};
      const summary = typeof metadata.summary === 'string' ? metadata.summary.trim() : '';
      if (!summary) return null;
      const title = typeof row.title === 'string' && row.title.trim() ? row.title.trim() : 'Previous conversation';
      return `- ${title}: ${summary}`;
    })
    .filter(Boolean)
    .join('\n');

  if (!summaries) return null;

  return [
    memoryHeader,
    summaries,
    'If something seems outdated, confirm with the user before assuming continuity.',
  ].join('\n');
}

/**
 * Check if conversation should be summarized
 * 
 * @param messageCount - Current message count
 * @param threshold - Minimum messages before summarization (default: 5)
 * @returns True if should summarize
 */
export function shouldSummarizeConversation(messageCount: number, threshold = 5): boolean {
  return messageCount >= threshold && messageCount % 5 === 0;
}
