/**
 * Knowledge Reuse — CORAL Pattern Implementation
 *
 * Algorithm for finding and reusing relevant past discoveries.
 * Based on CORAL (MIT): 50%+ of breakthroughs come from knowledge reuse.
 *
 * Core principle: Agents should check "what's already known" before exploring.
 *
 * @module KnowledgeReuse
 * @see https://github.com/Human-Agent-Society/CORAL
 */

// ═════════════════════════════════════════════════════════════════════════════
// Types
// ═════════════════════════════════════════════════════════════════════════════

export interface Discovery {
  id: string;
  repoUrl: string;
  gemName: string;
  category: string;
  score: number; // 0-10
  summary: string;
  tags: string[];
  noveltyScore: number; // 0-1
  applicabilityScore: number; // 0-1
  reuseCount: number;
  discoveredAt: string;
  lastReusedAt?: string;
}

export interface TaskContext {
  task?: string;
  category?: string;
  tags?: string[];
  minScore?: number;
  maxAgeDays?: number;
}

export interface RelevanceScore {
  discovery: Discovery;
  relevance: number; // 0-1, higher = more relevant
  matchReasons: string[];
}

export interface PrioritizationResult {
  discoveries: Discovery[];
  totalAvailable: number;
  skippedCount: number;
  potentialSavings: number; // Estimated API call reduction
}

// ═════════════════════════════════════════════════════════════════════════════
// Knowledge Reuse Algorithm
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Find relevant discoveries for current task
 * Implements CORAL knowledge reuse pattern
 *
 * @param task Current task description/query
 * @param discoveries All past discoveries
 * @param context Task context for filtering
 * @returns Ranked list of relevant discoveries
 */
export function findRelevantDiscoveries(
  task: string,
  discoveries: Discovery[],
  context: TaskContext = {}
): RelevanceScore[] {
  const {
    category,
    tags = [],
    minScore = 7.0,
    maxAgeDays = 14,
  } = context;

  // Filter by basic criteria
  const candidates = discoveries.filter(d => {
    // Score threshold
    if (d.score < minScore) return false;

    // Age filter
    const age = daysSince(d.discoveredAt);
    if (age > maxAgeDays) return false;

    // Category match (if specified)
    if (category && d.category !== category) return false;

    return true;
  });

  if (candidates.length === 0) return [];

  // Score each candidate by relevance
  const scored = candidates.map(d => scoreRelevance(d, task, tags));

  // Sort by relevance descending
  scored.sort((a, b) => b.relevance - a.relevance);

  return scored;
}

/**
 * Prioritize discoveries for exploration
 * CORAL: Score = novelty × applicability / cost
 *
 * @param discoveries Available discoveries
 * @param budget Exploration budget (max API calls)
 * @returns Prioritized list with skip recommendations
 */
export function prioritizeDiscoveries(
  discoveries: Discovery[],
  budget: number = 10
): PrioritizationResult {
  // Calculate priority score for each discovery
  const scored = discoveries.map(d => {
    // CORAL formula: novelty × applicability / (reuse_penalty)
    // reuse_penalty increases as reuseCount grows (diminishing returns)
    const novelty = d.noveltyScore;
    const applicability = d.applicabilityScore;
    const reusePenalty = 1 + (d.reuseCount * 0.1); // 10% penalty per reuse

    const priorityScore = (novelty * applicability) / reusePenalty;

    return { discovery: d, priorityScore };
  });

  // Sort by priority
  scored.sort((a, b) => b.priorityScore - a.priorityScore);

  // Select top N based on budget
  const selected = scored.slice(0, budget).map(s => s.discovery);
  const skipped = scored.slice(budget);

  // Estimate savings
  const potentialSavings = skipped.length * 0.3; // Assume 30% API call reduction per skipped item

  return {
    discoveries: selected,
    totalAvailable: discoveries.length,
    skippedCount: skipped.length,
    potentialSavings,
  };
}

/**
 * Check if a specific repo/task should be skipped (already discovered)
 *
 * @param repoUrl Target repository URL
 * @param discoveries Past discoveries
 * @param recencyDays How recent to consider "already done"
 * @returns Skip recommendation
 */
export function shouldSkipExploration(
  repoUrl: string,
  discoveries: Discovery[],
  recencyDays: number = 14
): { skip: boolean; reason?: string; existingDiscovery?: Discovery } {
  const existing = discoveries.find(d => {
    if (d.repoUrl !== repoUrl) return false;

    const age = daysSince(d.discoveredAt);
    return age <= recencyDays;
  });

  if (existing) {
    return {
      skip: true,
      reason: `Already discovered ${daysSince(existing.discoveredAt).toFixed(0)} days ago with score ${existing.score}`,
      existingDiscovery: existing,
    };
  }

  return { skip: false };
}

/**
 * Mark a discovery as reused
 * Updates reuse metrics for future prioritization
 *
 * @param discovery Discovery being reused
 * @returns Updated discovery
 */
export function markReused(discovery: Discovery): Discovery {
  return {
    ...discovery,
    reuseCount: discovery.reuseCount + 1,
    lastReusedAt: new Date().toISOString(),
  };
}

// ═════════════════════════════════════════════════════════════════════════════
// Internal Functions
// ═════════════════════════════════════════════════════════════════════════════

function scoreRelevance(
  discovery: Discovery,
  task: string,
  contextTags: string[]
): RelevanceScore {
  const matchReasons: string[] = [];
  const taskLower = task.toLowerCase();

  // 1. Keyword overlap (semantic similarity proxy)
  const discoveryWords = discovery.summary.toLowerCase().split(/\s+/);
  const taskWords = taskLower.split(/\s+/).filter(w => w.length > 3);

  let keywordMatches = 0;
  for (const word of taskWords) {
    if (discoveryWords.some(dw => dw.includes(word) || word.includes(dw))) {
      keywordMatches++;
    }
  }
  const keywordScore = taskWords.length > 0 ? keywordMatches / taskWords.length : 0;

  if (keywordScore > 0.5) matchReasons.push('keyword match');

  // 2. Tag overlap
  const tagMatches = discovery.tags.filter(t =>
    contextTags.some(ct => ct.toLowerCase() === t.toLowerCase())
  ).length;
  const tagScore = contextTags.length > 0 ? tagMatches / contextTags.length : 0;

  if (tagMatches > 0) matchReasons.push(`${tagMatches} tag matches`);

  // 3. Applicability boost
  const applicabilityBoost = discovery.applicabilityScore;

  // 4. Novelty boost (prefer less-reused discoveries)
  const noveltyBoost = discovery.noveltyScore * (1 / (1 + discovery.reuseCount * 0.1));

  // Combined relevance score
  const relevance = (
    keywordScore * 0.4 +
    tagScore * 0.3 +
    applicabilityBoost * 0.2 +
    noveltyBoost * 0.1
  );

  return {
    discovery,
    relevance: Math.min(relevance, 1.0), // Cap at 1.0
    matchReasons,
  };
}

function daysSince(dateString: string): number {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  return diffMs / (1000 * 60 * 60 * 24);
}

// ═════════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Calculate knowledge reuse statistics
 */
export function getReuseStats(discoveries: Discovery[]): {
  totalDiscoveries: number;
  totalReuses: number;
  avgReusesPerDiscovery: number;
  topReused: Discovery[];
  neverReused: number;
} {
  const totalDiscoveries = discoveries.length;
  const totalReuses = discoveries.reduce((sum, d) => sum + d.reuseCount, 0);
  const avgReuses = totalDiscoveries > 0 ? totalReuses / totalDiscoveries : 0;

  const sortedByReuse = [...discoveries].sort((a, b) => b.reuseCount - a.reuseCount);
  const topReused = sortedByReuse.slice(0, 5);

  const neverReused = discoveries.filter(d => d.reuseCount === 0).length;

  return {
    totalDiscoveries,
    totalReuses,
    avgReusesPerDiscovery: avgReuses,
    topReused,
    neverReused,
  };
}

/**
 * Batch mark discoveries as reused
 */
export function batchMarkReused(discoveries: Discovery[]): Discovery[] {
  return discoveries.map(markReused);
}

/**
 * Filter discoveries by age
 */
export function filterByAge(
  discoveries: Discovery[],
  maxAgeDays: number
): Discovery[] {
  return discoveries.filter(d => daysSince(d.discoveredAt) <= maxAgeDays);
}

/**
 * Filter discoveries by score
 */
export function filterByScore(
  discoveries: Discovery[],
  minScore: number
): Discovery[] {
  return discoveries.filter(d => d.score >= minScore);
}
