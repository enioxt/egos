/**
 * cost-tracker.ts — GH-059
 * LLM cost budgeting module for the EGOS gem-hunter pipeline.
 * No external dependencies.
 */

export interface CostEntry {
  input: number;  // USD per 1M input tokens
  output: number; // USD per 1M output tokens
}

export const COST_TABLE: Record<string, CostEntry> = {
  "qwen-plus":          { input: 0.0,   output: 0.0  },
  "qwen-2.5-7b":        { input: 0.0,   output: 0.0  },
  "gemini-1.5-flash":   { input: 0.075, output: 0.30 },
  "gemini-2.0-flash":   { input: 0.10,  output: 0.40 },
  "claude-haiku-4-5":   { input: 0.80,  output: 4.0  },
  "claude-sonnet-4-6":  { input: 3.0,   output: 15.0 },
  "openai-gpt-4o-mini": { input: 0.15,  output: 0.60 },
  "default":            { input: 1.0,   output: 3.0  },
};

export interface CostUsage {
  model: string;
  inputTokens: number;
  outputTokens: number;
  costUsd: number;
  timestamp: string;
  context?: string;
}

export interface CostSession {
  usages: CostUsage[];
  track(usage: CostUsage): void;
  total(): number;
  report(): string;
}

/** Rough token estimate: ~4 chars per token */
export function estimateTokens(text: string): number {
  return Math.ceil(text.length / 4);
}

/** Returns cost in USD for a given model and token counts */
export function estimateCost(
  model: string,
  inputTokens: number,
  outputTokens: number = 0,
): number {
  const entry = COST_TABLE[model] ?? COST_TABLE["default"];
  const inputCost  = (inputTokens  / 1_000_000) * entry.input;
  const outputCost = (outputTokens / 1_000_000) * entry.output;
  return inputCost + outputCost;
}

/** Returns whether the call is within budget, the estimated cost, and remaining budget */
export function checkBudget(
  model: string,
  inputTokens: number,
  budget: number,
): { allowed: boolean; estimatedCost: number; remainingBudget: number } {
  const estimatedCost = estimateCost(model, inputTokens);
  const allowed = estimatedCost <= budget;
  const remainingBudget = budget - estimatedCost;
  return { allowed, estimatedCost, remainingBudget };
}

/** Returns a human-readable cost table */
export function formatCostReport(usages: CostUsage[]): string {
  if (usages.length === 0) return "No usages recorded.";

  const header = "Model                    | In Tokens | Out Tokens |   Cost USD | Timestamp            | Context";
  const sep    = "-".repeat(header.length);
  const rows = usages.map((u) => {
    const model   = u.model.padEnd(24);
    const inTok   = String(u.inputTokens).padStart(9);
    const outTok  = String(u.outputTokens).padStart(10);
    const cost    = `$${u.costUsd.toFixed(6)}`.padStart(10);
    const ts      = u.timestamp.slice(0, 20).padEnd(20);
    const ctx     = u.context ?? "";
    return `${model} | ${inTok} | ${outTok} | ${cost} | ${ts} | ${ctx}`;
  });

  const totalCost = usages.reduce((s, u) => s + u.costUsd, 0);
  const totalLine = `${"TOTAL".padEnd(24)} | ${" ".repeat(9)} | ${" ".repeat(10)} | $${totalCost.toFixed(6).padStart(9)} |`;

  return [header, sep, ...rows, sep, totalLine].join("\n");
}

/** Creates an in-memory cost session for tracking multiple LLM calls */
export function createCostSession(): CostSession {
  const usages: CostUsage[] = [];

  return {
    usages,
    track(usage: CostUsage): void {
      usages.push(usage);
    },
    total(): number {
      return usages.reduce((s, u) => s + u.costUsd, 0);
    },
    report(): string {
      return formatCostReport(usages);
    },
  };
}
