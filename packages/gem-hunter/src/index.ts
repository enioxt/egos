/**
 * @egosbr/gem-hunter — Public API
 * Programmatic interface to the EGOS Gem Hunter discovery engine.
 *
 * Usage:
 *   import { GemHunter, type GemResult, type HuntOptions } from '@egosbr/gem-hunter';
 *   const hunter = new GemHunter({ apiUrl: 'http://localhost:3097' });
 *   const results = await hunter.hunt({ quick: true });
 */

export interface GemResult {
  name: string;
  source: string;
  url: string;
  description: string;
  stars?: number;
  downloads?: number;
  relevance: "high" | "medium" | "low";
  category: string;
  lastUpdated?: string;
  language?: string;
  license?: string;
  structureBonus?: number;
  abstractScore?: number;
}

export interface HuntOptions {
  quick?: boolean;
  track?: string;
  topic?: string;
}

export interface FindingsResult {
  latest: {
    generatedAt: string;
    totalGems: number;
    byCategory: Record<string, number>;
    bySource: Record<string, number>;
  };
  topSignals: Array<{
    name: string;
    url: string;
    score: number;
    category: string;
    date: string;
    headline: string;
  }>;
}

export interface HuntJob {
  jobId: string;
  status: "running" | "done" | "error";
  startedAt: string;
}

/** Client for the Gem Hunter standalone API (GH-058) */
export class GemHunter {
  private apiUrl: string;
  private apiKey?: string;

  constructor(opts: { apiUrl?: string; apiKey?: string } = {}) {
    this.apiUrl = opts.apiUrl ?? "http://localhost:3097";
    this.apiKey = opts.apiKey ?? process.env.GEM_HUNTER_API_KEY;
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (this.apiKey) h["Authorization"] = `Bearer ${this.apiKey}`;
    return h;
  }

  /** Trigger an async gem hunt run. Returns a job ID to poll. */
  async hunt(opts: HuntOptions = {}): Promise<HuntJob> {
    const res = await fetch(`${this.apiUrl}/v1/hunt`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(opts),
    });
    if (!res.ok) throw new Error(`Hunt failed: ${res.status} ${await res.text()}`);
    return res.json() as Promise<HuntJob>;
  }

  /** Get job status by ID. */
  async jobStatus(jobId: string): Promise<HuntJob> {
    const res = await fetch(`${this.apiUrl}/v1/jobs/${jobId}`, { headers: this.headers() });
    if (!res.ok) throw new Error(`Job fetch failed: ${res.status}`);
    return res.json() as Promise<HuntJob>;
  }

  /** Get the latest run findings + top signals. */
  async findings(): Promise<FindingsResult> {
    const res = await fetch(`${this.apiUrl}/v1/findings`, { headers: this.headers() });
    if (!res.ok) throw new Error(`Findings fetch failed: ${res.status}`);
    return res.json() as Promise<FindingsResult>;
  }

  /** Get scaffolded papers from the paper pipeline. */
  async papers(): Promise<{ count: number; papers: Array<{ file: string; title: string; score: number | null }> }> {
    const res = await fetch(`${this.apiUrl}/v1/papers`, { headers: this.headers() });
    if (!res.ok) throw new Error(`Papers fetch failed: ${res.status}`);
    return res.json();
  }

  /** Get world-model signals feed. */
  async signals(): Promise<{ version: string; signals: FindingsResult["topSignals"] }> {
    const res = await fetch(`${this.apiUrl}/v1/signals`, { headers: this.headers() });
    if (!res.ok) throw new Error(`Signals fetch failed: ${res.status}`);
    return res.json();
  }

  /** Poll job until done or timeout (default 10min). */
  async waitForJob(jobId: string, timeoutMs = 600_000): Promise<HuntJob> {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      await new Promise(r => setTimeout(r, 5000));
      const job = await this.jobStatus(jobId);
      if (job.status !== "running") return job;
    }
    throw new Error(`Job ${jobId} timed out after ${timeoutMs}ms`);
  }
}
