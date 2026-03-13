/**
 * @egos/shared — Core EGOS framework utilities
 * 
 * Exports only framework-level infrastructure.
 * Domain-specific utilities (OSINT, social, etc.) live in leaf repos.
 */

export { chatWithLLM, ALIBABA_TEST_MODELS } from './llm-provider';
export type { SharedLLMProvider } from './llm-provider';
export { createAtrianValidator } from './atrian';
export { scanForPII, sanitizeText, getPIISummary } from './pii-scanner';
export { shouldSummarizeConversation, buildConversationTranscript, normalizeConversationSummary, buildConversationMemoryBlock } from './conversation-memory';
export { RateLimiter } from './rate-limiter';
export type { AtrianConfig, AtrianResult, AtrianViolation, ViolationLevel } from './atrian';
export type { ConversationMemoryOptions, ConversationMessage } from './conversation-memory';
export type { PIICategory, PIIFinding, PIIPatternDefinition } from './pii-scanner';
export type { AIAnalysisResult, AgentMetadata } from './types';
