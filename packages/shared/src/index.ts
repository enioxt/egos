/**
 * @egos/shared — Core EGOS framework utilities
 *
 * Exports only framework-level infrastructure.
 * Domain-specific utilities (OSINT, social, etc.) live in leaf repos.
 */

// ═══════════════════════════════════════════════════════════
// @public — LLM Provider (Alibaba + fallback)
// ═══════════════════════════════════════════════════════════
export { chatWithLLM, ALIBABA_TEST_MODELS } from './llm-provider';
export type { SharedLLMProvider } from './llm-provider';

// ═══════════════════════════════════════════════════════════
// @public — Model Router (task-based selection across 8 models)
// ═══════════════════════════════════════════════════════════
export { resolveModel, routeForChat, listAvailableModels, MODEL_CATALOG } from './model-router';
export type { TaskType, CostPreference, RouteOptions, ResolvedRoute, ModelProfile } from './model-router';

// ═══════════════════════════════════════════════════════════
// @public — ATRiAN (Ethical validation, 7 axioms)
// ═══════════════════════════════════════════════════════════
export { createAtrianValidator } from './atrian';
export type { AtrianConfig, AtrianResult, AtrianViolation, ViolationLevel } from './atrian';

// ═══════════════════════════════════════════════════════════
// @public — PII Scanner (Brazilian PII detection)
// ═══════════════════════════════════════════════════════════
export { scanForPII, sanitizeText, getPIISummary } from './pii-scanner';
export type { PIICategory, PIIFinding, PIIPatternDefinition } from './pii-scanner';

// ═══════════════════════════════════════════════════════════
// @public — Conversation Memory (session memory + summarization)
// ═══════════════════════════════════════════════════════════
export { shouldSummarizeConversation, buildConversationTranscript, normalizeConversationSummary, buildConversationMemoryBlock } from './conversation-memory';
export type { ConversationMemoryOptions, ConversationMessage } from './conversation-memory';

// ═══════════════════════════════════════════════════════════
// @public — Rate Limiter (token bucket)
// ═══════════════════════════════════════════════════════════
export { RateLimiter } from './rate-limiter';

// ═══════════════════════════════════════════════════════════
// @public — Core Types (analysis results, agent metadata)
// ═══════════════════════════════════════════════════════════
export type { AIAnalysisResult, AgentMetadata } from './types';

// ═══════════════════════════════════════════════════════════
// @public — Mycelium Reference Graph (27 nodes, 32 edges, DAG)
// ═══════════════════════════════════════════════════════════
export { createGraph, findNode, findEdgesFrom, findEdgesTo, nodesByType, nodesByStatus, graphHealth, getKernelSeedGraph } from './mycelium/reference-graph';
export type { ReferenceEntityType, ReferenceRelation, ReferenceEvidence, NodeStatus, ReferenceNode, ReferenceEdge, ReferenceGraph } from './mycelium/reference-graph';

// ═══════════════════════════════════════════════════════════
// @public — Repo Role (repo classification heuristics)
// ═══════════════════════════════════════════════════════════
export { detectRepoRole, hasSurface, roleDescription } from './repo-role';
export type { RepoRole, EgosConfig } from './repo-role';

// ═══════════════════════════════════════════════════════════
// @public — Telemetry (dual output: Supabase + JSON logs)
// ═══════════════════════════════════════════════════════════
export { createTelemetryRecorder } from './telemetry.js';
export type { TelemetryRecorder, TelemetryEvent } from './telemetry.js';

// ═══════════════════════════════════════════════════════════
// @public — Cross-Session Memory (Supabase-based)
// ═══════════════════════════════════════════════════════════
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

// ═══════════════════════════════════════════════════════════
// @public — Metrics Tracker (session, tool, task metrics)
// ═══════════════════════════════════════════════════════════
export { MetricsTracker, initMetricsTracker, getMetricsTracker, trackToolUsage, trackTask } from './metrics-tracker.js';
export type { ToolUsageMetric, TaskMetric, SessionMetric } from './metrics-tracker.js';

// ═══════════════════════════════════════════════════════════
// EGOS Guard Brasil — Brazilian AI Safety Layer
// ═══════════════════════════════════════════════════════════

// @public — Public Guard (LGPD-compliant PII masking)
export { maskPublicOutput, isPublicSafe, buildLGPDDisclosure } from './public-guard.js';
export type { PublicGuardConfig, MaskingResult, MaskingAction, GuardAction, SensitivityLevel } from './public-guard.js';

// @public — Evidence Chain (traceable response discipline)
export { createEvidenceChain, EvidenceChainBuilder, formatEvidenceBlock, validateChain } from './evidence-chain.js';
export type { EvidenceChain, EvidenceItem, ClaimWithEvidence, EvidenceType, ConfidenceLevel, EvidenceChainOptions } from './evidence-chain.js';
