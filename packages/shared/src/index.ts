/**
 * @egos/shared — Core EGOS framework utilities
 * 
 * Exports only framework-level infrastructure.
 * Domain-specific utilities (OSINT, social, etc.) live in leaf repos.
 */

export { chatWithLLM, chatWithLLM as analyzeWithAI, ALIBABA_MODELS } from './llm-provider';
export type { SharedLLMProvider } from './llm-provider';
export { resolveModel, routeForChat, listAvailableModels, MODEL_CATALOG } from './model-router';
export type { TaskType, CostPreference, RouteOptions, ResolvedRoute, ModelProfile } from './model-router';
export { createAtrianValidator } from './atrian';
export { scanForPII, sanitizeText, getPIISummary } from './pii-scanner';
export { shouldSummarizeConversation, buildConversationTranscript, normalizeConversationSummary, buildConversationMemoryBlock } from './conversation-memory';
export { RateLimiter } from './rate-limiter';
export { CircuitBreaker, CircuitOpenError } from './circuit-breaker';
export type { CircuitState, CircuitBreakerOptions, CircuitBreakerStatus } from './circuit-breaker';
export type { AtrianConfig, AtrianResult, AtrianViolation, ViolationLevel } from './atrian';
export type { ConversationMemoryOptions, ConversationMessage } from './conversation-memory';
export type { PIICategory, PIIFinding, PIIPatternDefinition } from './pii-scanner';
export type { AIAnalysisResult, AgentMetadata } from './types';
export { createGraph, findNode, findEdgesFrom, findEdgesTo, nodesByType, nodesByStatus, graphHealth, getKernelSeedGraph } from './mycelium/reference-graph';
export type { ReferenceEntityType, ReferenceRelation, ReferenceEvidence, NodeStatus, ReferenceNode, ReferenceEdge, ReferenceGraph } from './mycelium/reference-graph';
export { createRedisBridge, publishEvent, subscribeToEvents, buildEvent } from './mycelium/redis-bridge';
export type { RedisBridgeConfig, MyceliumEvent, RedisBridge } from './mycelium/redis-bridge';
export { detectRepoRole, hasSurface, roleDescription } from './repo-role';
export type { RepoRole, EgosConfig } from './repo-role';
export { createTelemetryRecorder, getStats as getTelemetryStats, getLatencyHeatmap } from './telemetry.js';
export type { TelemetryRecorder, TelemetryEvent, TelemetryStats, LatencyBucket } from './telemetry.js';

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

// Metrics Tracker
export { MetricsTracker, initMetricsTracker, getMetricsTracker, trackToolUsage, trackTask } from './metrics-tracker.js';
export type { ToolUsageMetric, TaskMetric, SessionMetric } from './metrics-tracker.js';

// ═══════════════════════════════════════════════════════════
// EGOS Guard Brasil — Brazilian AI Safety Layer
// ═══════════════════════════════════════════════════════════

// Public Guard — LGPD-compliant PII masking
export { maskPublicOutput, isPublicSafe, buildLGPDDisclosure } from './public-guard.js';
export type { PublicGuardConfig, MaskingResult, MaskingAction, GuardAction, SensitivityLevel } from './public-guard.js';

// Event Bus — agent coordination via Supabase Realtime
export { emit, subscribe, subscribeOnce, getRecentEvents, cleanup } from './event-bus.js';
export type { AgentEvent, Severity } from './event-bus.js';

// Evidence Chain — traceable response discipline
export { createEvidenceChain, EvidenceChainBuilder, formatEvidenceBlock, validateChain } from './evidence-chain.js';
export type { EvidenceChain, EvidenceItem, ClaimWithEvidence, EvidenceType, ConfidenceLevel, EvidenceChainOptions } from './evidence-chain.js';

// Intelligence Layer — Architecture Selector (GH-046/047, arXiv 2512.08296)
export { selectArchitecture, classifyFromDescription, formatForBraid } from './intelligence/architecture-selector.js';
export type { ArchitectureType, ArchitectureProfile, SelectionInput, SelectionResult } from './intelligence/architecture-selector.js';

export { assemblePrompt, createAssembler } from './prompt-assembler';
export type { PromptSection, AssembledPrompt } from './prompt-assembler';
export { SupabaseMemoryStore, InMemoryStore, NullMemoryStore } from './memory-store';
export type { MemoryEntry, MemoryStore, SupabaseClientLike, SupabaseMemoryStoreOptions } from './memory-store';
export { runEval } from './eval/runner';
export type { GoldenCase, EvalResult, EvalReport, ChatFn, EvalMessage } from './eval/runner';
