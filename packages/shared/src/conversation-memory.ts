export interface ConversationMessage { role: string; content: string; }
export interface ConversationMemoryOptions {
  maxTranscriptMessages?: number;
  maxSummaryLength?: number;
  minimumMessagesForSummary?: number;
  heading?: string;
  footer?: string;
  speakerLabels?: Record<string, string>;
}

const DEFAULT_OPTIONS: Required<ConversationMemoryOptions> = {
  maxTranscriptMessages: 12,
  maxSummaryLength: 1200,
  minimumMessagesForSummary: 4,
  heading: '## MEMÓRIA DE SESSÕES ANTERIORES (use apenas como contexto, sem afirmar como fato novo)',
  footer: 'Se algo parecer desatualizado, confirme com o usuário antes de assumir continuidade.',
  speakerLabels: { user: 'USUÁRIO', assistant: 'AGENTE' },
};

export function shouldSummarizeConversation(messages: ConversationMessage[], options?: ConversationMemoryOptions): boolean {
  const config = { ...DEFAULT_OPTIONS, ...options };
  return messages.length >= config.minimumMessagesForSummary;
}

export function buildConversationTranscript(messages: ConversationMessage[], options?: ConversationMemoryOptions): string {
  const config = { ...DEFAULT_OPTIONS, ...options };
  return messages.slice(-config.maxTranscriptMessages).map((message) => `${config.speakerLabels[message.role] ?? message.role.toUpperCase()}: ${message.content.slice(0, 400)}`).join('\n');
}

export function normalizeConversationSummary(summary: string | null | undefined, options?: ConversationMemoryOptions): string | null {
  if (!summary) return null;
  const config = { ...DEFAULT_OPTIONS, ...options };
  const normalized = summary.trim().slice(0, config.maxSummaryLength);
  return normalized || null;
}

export function buildConversationMemoryBlock(items: Array<{ title?: string | null; summary?: string | null }>, options?: ConversationMemoryOptions): string | null {
  const config = { ...DEFAULT_OPTIONS, ...options };
  const summaries = items.map((item) => {
    const summary = normalizeConversationSummary(item.summary, config);
    if (!summary) return null;
    const title = item.title?.trim() ? item.title.trim() : 'Conversa anterior';
    return `- ${title}: ${summary}`;
  }).filter(Boolean);
  if (summaries.length === 0) return null;
  return [config.heading, ...summaries, config.footer].join('\n');
}
