/**
 * @egos/shared — Core EGOS framework utilities
 * 
 * Exports only framework-level infrastructure.
 * Domain-specific utilities (OSINT, social, etc.) live in leaf repos.
 */

export { chatWithLLM, ALIBABA_TEST_MODELS } from './llm-provider';
export type { SharedLLMProvider } from './llm-provider';
export { resolveModel, routeForChat, listAvailableModels, MODEL_CATALOG } from './model-router';
export type { TaskType, CostPreference, RouteOptions, ResolvedRoute, ModelProfile } from './model-router';
export { createAtrianValidator } from './atrian';
export { scanForPII, sanitizeText, getPIISummary } from './pii-scanner';
export { shouldSummarizeConversation, buildConversationTranscript, normalizeConversationSummary, buildConversationMemoryBlock } from './conversation-memory';
export { RateLimiter } from './rate-limiter';
export type { AtrianConfig, AtrianResult, AtrianViolation, ViolationLevel } from './atrian';
export type { ConversationMemoryOptions, ConversationMessage } from './conversation-memory';
export type { PIICategory, PIIFinding, PIIPatternDefinition } from './pii-scanner';
export type { AIAnalysisResult, AgentMetadata } from './types';
export { createGraph, findNode, findEdgesFrom, findEdgesTo, nodesByType, nodesByStatus, graphHealth, getKernelSeedGraph } from './mycelium/reference-graph';
export type { ReferenceEntityType, ReferenceRelation, ReferenceEvidence, NodeStatus, ReferenceNode, ReferenceEdge, ReferenceGraph } from './mycelium/reference-graph';
export { detectRepoRole, hasSurface, roleDescription } from './repo-role';
export type { RepoRole, EgosConfig } from './repo-role';
export { createTelemetryRecorder } from './telemetry.js';
export type { TelemetryRecorder, TelemetryEvent } from './telemetry.js';

// Cross-Session Memory (Supabase-based)
export {
  summarizeConversation as summarizeConversationCrossSession,
  saveConversationSummary as saveConversationSummaryCrossSession,
  getConversationMemory as getConversationMemoryCrossSession,
  shouldSummarizeConversation as shouldSummarizeConversationCrossSession,
} from './cross-session-memory.js';
export type {
  ConversationSummaryOptions,
  MemoryRetrievalOptions,
} from './cross-session-memory.js';
