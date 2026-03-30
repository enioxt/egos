/**
 * ai-engine.ts — Shim for gem-hunter and other discord-style agents.
 * Bridges the callAI(discord-params) signature → chatWithLLM.
 */

import { chatWithLLM } from '../llm-provider';

export interface CallAIParams {
  userMessage: string;
  channelId?: string;
  userId?: string;
  userName?: string;
  platform?: string;
  openrouterApiKey?: string;
  model?: string;
  systemPrompt?: string;
}

export interface CallAIResult {
  reply: string;
}

export async function callAI(params: CallAIParams): Promise<CallAIResult> {
  const result = await chatWithLLM({
    systemPrompt: params.systemPrompt ?? 'You are a helpful AI assistant in the EGOS ecosystem.',
    userPrompt: params.userMessage,
    model: params.model,
  });
  return { reply: typeof result === 'string' ? result : (result as { content?: string; text?: string }).content ?? (result as { content?: string; text?: string }).text ?? JSON.stringify(result) };
}
