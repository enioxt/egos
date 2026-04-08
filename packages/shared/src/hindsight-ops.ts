/**
 * Hindsight Operations — Biomimetic Memory Lifecycle
 *
 * Port of Hindsight's Retain/Recall/Reflect operations.
 * Implements human-memory-inspired lifecycle for AI agent memories.
 *
 * Principles from vectorize-io/hindsight:
 * - Retain: Encode experiences into storable form
 * - Recall: Retrieve relevant memories with context
 * - Reflect: Consolidate and strengthen frequently accessed memories
 *
 * @module HindsightOps
 * @see https://github.com/vectorize-io/hindsight
 */

import { randomUUID } from 'crypto';

// ═════════════════════════════════════════════════════════════════════════════
// Types
// ═════════════════════════════════════════════════════════════════════════════

export type MemoryState = 'encoding' | 'consolidating' | 'retrievable' | 'fading';

export interface HindsightMemory {
  id: string;
  content: string;
  state: MemoryState;
  createdAt: string;
  lastAccessedAt: string | null;
  accessCount: number;
  relevanceScore: number;
  associations: string[]; // IDs of related memories
  context: Record<string, unknown>; // Session, agent, task context
}

export interface RetainOptions {
  sessionId?: string;
  agentId?: string;
  taskId?: string;
  associations?: string[];
  importance?: 'low' | 'medium' | 'high' | 'critical';
}

export interface RecallOptions {
  limit?: number;
  recencyWeight?: number; // 0-1, how much to weight recent memories
  relevanceWeight?: number; // 0-1, how much to weight relevance matching
  includeFading?: boolean;
}

export interface ReflectOptions {
  consolidationThreshold?: number; // Access count to trigger consolidation
  fadingThreshold?: number; // Days of inactivity to mark as fading
}

// ═════════════════════════════════════════════════════════════════════════════
// Core Operations
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Retain a new memory into the system
 * Mimics human memory encoding (short-term → working → long-term)
 *
 * @param content Memory content to store
 * @param options Retention context and metadata
 * @returns Encoded memory ready for storage
 */
export function retain(
  content: string,
  options: RetainOptions = {}
): HindsightMemory {
  const { sessionId, agentId, taskId, associations = [], importance = 'medium' } = options;

  // Calculate initial relevance based on importance
  const relevanceScore = importanceToScore(importance);

  const memory: HindsightMemory = {
    id: randomUUID(),
    content: encodeContent(content),
    state: 'encoding',
    createdAt: new Date().toISOString(),
    lastAccessedAt: null,
    accessCount: 0,
    relevanceScore,
    associations,
    context: {
      sessionId,
      agentId,
      taskId,
      importance,
    },
  };

  // Immediately transition to consolidating (analogous to working memory)
  memory.state = 'consolidating';

  return memory;
}

/**
 * Recall relevant memories based on query and context
 * Mimics human memory retrieval (cue-driven associative recall)
 *
 * @param query Search query or context
 * @param memories All stored memories
 * @param options Recall parameters
 * @returns Ranked list of relevant memories
 */
export function recall(
  query: string,
  memories: HindsightMemory[],
  options: RecallOptions = {}
): HindsightMemory[] {
  const {
    limit = 5,
    recencyWeight = 0.3,
    relevanceWeight = 0.7,
    includeFading = false,
  } = options;

  // Filter out fading memories unless explicitly included
  const activeMemories = includeFading
    ? memories
    : memories.filter(m => m.state !== 'fading');

  if (activeMemories.length === 0) return [];

  // Score each memory
  const scored = activeMemories.map(memory => {
    const recencyScore = calculateRecency(memory);
    const relevanceMatch = calculateRelevanceMatch(query, memory);
    const associationBoost = calculateAssociationBoost(query, memory, activeMemories);

    const totalScore =
      recencyScore * recencyWeight +
      relevanceMatch * relevanceWeight +
      associationBoost * 0.1; // Small boost for associations

    return { memory, score: totalScore };
  });

  // Sort by score descending
  scored.sort((a, b) => b.score - a.score);

  // Update access metrics for retrieved memories
  const retrieved = scored.slice(0, limit).map(({ memory }) => {
    memory.accessCount++;
    memory.lastAccessedAt = new Date().toISOString();

    // Transition to retrievable if was consolidating
    if (memory.state === 'consolidating' && memory.accessCount >= 2) {
      memory.state = 'retrievable';
    }

    return memory;
  });

  return retrieved;
}

/**
 * Reflect on and consolidate the memory system
 * Mimics human memory consolidation during sleep/rest
 *
 * Strengthens frequently accessed memories (consolidation)
 * Marks rarely accessed memories as fading (forgetting curve)
 *
 * @param memories All stored memories
 * @param options Reflection parameters
 * @returns Consolidated memory set
 */
export function reflect(
  memories: HindsightMemory[],
  options: ReflectOptions = {}
): HindsightMemory[] {
  const {
    consolidationThreshold = 3,
    fadingThreshold = 30, // days
  } = options;

  const now = new Date();

  return memories.map(memory => {
    // Consolidate frequently accessed memories
    if (memory.accessCount >= consolidationThreshold && memory.state === 'consolidating') {
      memory.state = 'retrievable';
      memory.relevanceScore = Math.min(memory.relevanceScore * 1.2, 1.0); // Cap at 1.0
    }

    // Mark as fading if inactive
    if (memory.lastAccessedAt) {
      const daysInactive = (now.getTime() - new Date(memory.lastAccessedAt).getTime()) / (1000 * 60 * 60 * 24);

      if (daysInactive > fadingThreshold && memory.state === 'retrievable') {
        memory.state = 'fading';
      }
    }

    return memory;
  });
}

// ═════════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Encode content for storage (lightweight compression)
 * @param content Raw content
 * @returns Encoded content
 */
function encodeContent(content: string): string {
  // Simple encoding: trim and normalize whitespace
  return content
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 10000); // Cap at 10k chars
}

/**
 * Convert importance level to numeric score
 */
function importanceToScore(importance: string): number {
  const scores: Record<string, number> = {
    low: 0.3,
    medium: 0.5,
    high: 0.8,
    critical: 1.0,
  };
  return scores[importance] ?? 0.5;
}

/**
 * Calculate recency score (0-1, higher = more recent)
 */
function calculateRecency(memory: HindsightMemory): number {
  const now = new Date().getTime();
  const created = new Date(memory.createdAt).getTime();
  const age = now - created;

  // Exponential decay: newer = higher score
  // Half-life of 7 days
  const halfLife = 7 * 24 * 60 * 60 * 1000;
  return Math.exp(-age / halfLife);
}

/**
 * Calculate relevance match between query and memory
 */
function calculateRelevanceMatch(query: string, memory: HindsightMemory): number {
  const queryLower = query.toLowerCase();
  const contentLower = memory.content.toLowerCase();

  // Simple keyword matching (can be enhanced with embeddings)
  const queryWords = queryLower.split(/\s+/).filter(w => w.length > 3);

  if (queryWords.length === 0) return 0.5;

  let matches = 0;
  for (const word of queryWords) {
    if (contentLower.includes(word)) matches++;
  }

  // Jaccard-like similarity
  return matches / queryWords.length;
}

/**
 * Calculate association boost (memories connected to recalled ones)
 */
function calculateAssociationBoost(
  query: string,
  memory: HindsightMemory,
  allMemories: HindsightMemory[]
): number {
  // Find memories that match query
  const queryMatches = allMemories.filter(m => {
    const score = calculateRelevanceMatch(query, m);
    return score > 0.5;
  });

  // Check if current memory is associated with any query-matching memory
  const matchingIds = new Set(queryMatches.map(m => m.id));

  for (const assocId of memory.associations) {
    if (matchingIds.has(assocId)) {
      return 0.5; // Boost for being associated with relevant memory
    }
  }

  return 0;
}

// ═════════════════════════════════════════════════════════════════════════════
// Batch Operations
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Retain multiple memories at once
 */
export function batchRetain(
  contents: string[],
  options: RetainOptions = {}
): HindsightMemory[] {
  return contents.map(content => retain(content, options));
}

/**
 * Get memory statistics
 */
export function getMemoryStats(memories: HindsightMemory[]): {
  total: number;
  byState: Record<MemoryState, number>;
  avgAccessCount: number;
  highRelevanceCount: number;
} {
  const byState: Record<MemoryState, number> = {
    encoding: 0,
    consolidating: 0,
    retrievable: 0,
    fading: 0,
  };

  let totalAccess = 0;
  let highRelevance = 0;

  for (const memory of memories) {
    byState[memory.state]++;
    totalAccess += memory.accessCount;
    if (memory.relevanceScore > 0.7) highRelevance++;
  }

  return {
    total: memories.length,
    byState,
    avgAccessCount: memories.length > 0 ? totalAccess / memories.length : 0,
    highRelevanceCount: highRelevance,
  };
}

/**
 * Prune fading memories (optional cleanup)
 */
export function pruneFadingMemories(
  memories: HindsightMemory[],
  minDaysFading: number = 60
): { kept: HindsightMemory[]; pruned: HindsightMemory[] } {
  const now = new Date();

  const kept: HindsightMemory[] = [];
  const pruned: HindsightMemory[] = [];

  for (const memory of memories) {
    if (memory.state === 'fading' && memory.lastAccessedAt) {
      const daysFading = (now.getTime() - new Date(memory.lastAccessedAt).getTime()) / (1000 * 60 * 60 * 24);

      if (daysFading > minDaysFading) {
        pruned.push(memory);
        continue;
      }
    }
    kept.push(memory);
  }

  return { kept, pruned };
}
