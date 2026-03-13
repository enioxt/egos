/**
 * Shared Types — Core EGOS framework types
 * Domain-specific types (gazette, OSINT, etc.) live in leaf repos.
 */

// ═══════════════════════════════════════════════════════════
// AI Client Types
// ═══════════════════════════════════════════════════════════

export interface AIAnalysisResult {
    content: string;
    model: string;
    usage: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
    };
    cost_usd: number;
}

// ═══════════════════════════════════════════════════════════
// Agent Types (re-exported from runner for convenience)
// ═══════════════════════════════════════════════════════════

export interface AgentMetadata {
    id: string;
    name: string;
    area: string;
    description: string;
    status: 'active' | 'placeholder' | 'pending' | 'disabled';
}
