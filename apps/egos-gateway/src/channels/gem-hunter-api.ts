/**
 * EGOS Gateway — Gem Hunter API Channel
 *
 * Exposes Gem Hunter discovery engine results as a REST API.
 * Backed by pre-computed reports (latest-run.json, SQLite history).
 *
 * Endpoints:
 *   GET  /gem-hunter/topics        — list all search topic categories
 *   GET  /gem-hunter/latest        — latest run: top gems by score
 *   GET  /gem-hunter/reports       — list available report files
 *   GET  /gem-hunter/sector/:name  — filter latest results by sector keyword
 *   GET  /gem-hunter/trending      — trending from SQLite history (multi-run)
 *   GET  /gem-hunter/health        — API health + last run info
 *
 * Product: Gem Hunter API (revenue stream)
 *   Free tier  : 5 req/day, top 5 results
 *   Starter    : R$99/mo, 50 req/day, top 20 results
 *   Pro        : R$499/mo, unlimited, all sectors, AI synthesis
 */

import { Hono } from "hono";
import { join } from "path";
import { existsSync, readdirSync, readFileSync, statSync } from "fs";
import Database from "bun:sqlite";

const ROOT = join(import.meta.dir, "../../../..");
const REPORTS_DIR = join(ROOT, "docs/gem-hunter");
const LATEST_RUN_PATH = join(REPORTS_DIR, "latest-run.json");
const HISTORY_DB_PATH = join(REPORTS_DIR, "history.db");

export const gemHunter = new Hono();

// ── Types ──────────────────────────────────────────────────────────────────────

interface GemResult {
  name: string;
  description: string;
  url: string;
  source: string;
  stars?: number;
  score?: number;
  topic?: string;
  category?: string;
  tags?: string[];
}

interface LatestRun {
  date: string;
  gems: GemResult[];
  totalFound?: number;
  topKeywords?: string[];
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function readLatestRun(): LatestRun | null {
  if (!existsSync(LATEST_RUN_PATH)) return null;
  try {
    return JSON.parse(readFileSync(LATEST_RUN_PATH, "utf-8")) as LatestRun;
  } catch {
    return null;
  }
}

function getLastModified(path: string): string | null {
  try {
    return statSync(path).mtime.toISOString();
  } catch {
    return null;
  }
}

/** Map user-facing sector names to internal topic keywords */
const SECTOR_MAP: Record<string, string[]> = {
  ai: ["agents", "AI", "LLM", "GPT", "language model", "autonomous", "MCP", "orchestration"],
  crypto: ["blockchain", "crypto", "web3", "DeFi", "x402", "on-chain", "CoinGecko"],
  systems: ["systems dev", "runtime", "compiler", "bun", "typescript", "rust", "go"],
  agents: ["agent", "multi-agent", "tool use", "A2A", "MCP", "orchestration", "swarm"],
  governance: ["governance", "rules", "compliance", "SSOT", "audit", "policy"],
  research: ["arxiv", "paper", "academic", "research", "benchmark"],
};

/** Sector aliases for API query normalization */
const SECTOR_ALIASES: Record<string, string> = {
  "ia": "ai",
  "inteligencia-artificial": "ai",
  "agentes": "agents",
  "orquestracao": "agents",
  "cripto": "crypto",
  "blockchain": "crypto",
  "governanca": "governance",
  "pesquisa": "research",
};

function filterBySector(gems: GemResult[], sector: string): GemResult[] {
  const normalizedSector = SECTOR_ALIASES[sector.toLowerCase()] || sector.toLowerCase();
  const keywords = SECTOR_MAP[normalizedSector];
  if (!keywords) return gems;

  return gems.filter((g) => {
    const text = `${g.name} ${g.description} ${g.topic || ""} ${g.category || ""}`.toLowerCase();
    return keywords.some((kw) => text.includes(kw.toLowerCase()));
  });
}

// ── Static topic definitions (mirrors gem-hunter.ts DEFAULT_QUERIES categories) ──

const TOPICS = [
  { sector: "ai", name: "AI Agents / MCP / Tool Use", description: "LLM agents, tool calling, MCP servers" },
  { sector: "ai", name: "Agent Orchestration / Control Plane", description: "Multi-agent coordination, swarms, control planes" },
  { sector: "ai", name: "Autonomous Agents (Social + Ops)", description: "Social and operational autonomous agents" },
  { sector: "ai", name: "AI Report & Dashboard Generators", description: "AI-powered reporting and visualization" },
  { sector: "ai", name: "Multi-Agent Coordination / Chat Rooms", description: "Agent-to-agent communication protocols" },
  { sector: "ai", name: "Declarative Sub-Agents / Chains", description: "Declarative agent chaining patterns" },
  { sector: "ai", name: "AutoResearch / Autonomous Experiment Loops", description: "Self-directed research loops" },
  { sector: "ai", name: "Agent Safety / Red-Teaming", description: "Safety evaluation and adversarial testing" },
  { sector: "ai", name: "Agent Adapter / Polyglot Wrappers", description: "Cross-language agent adapters" },
  { sector: "ai", name: "Agent Marketplaces / Registries / Tool Routers", description: "Discovery and routing for AI tools" },
  { sector: "ai", name: "HuggingFace Trending Models & Spaces", description: "Hot models and spaces on HuggingFace" },
  { sector: "research", name: "Academic Research / arXiv", description: "Latest papers from arXiv" },
  { sector: "research", name: "Early Warning — Researcher Launches (Day 0)", description: "New repos from researchers" },
  { sector: "crypto", name: "Blockchain / x402 / On-Chain Payments", description: "Web3, DeFi, and payment protocols" },
  { sector: "governance", name: "Strategic MCP Servers / Governance", description: "MCP servers for governance and compliance" },
  { sector: "governance", name: "A2A Agent Cards / Interoperability", description: "Agent interoperability standards" },
  { sector: "governance", name: "Strategic Signals / MCP + A2A + OpenClaw", description: "Strategic positioning signals" },
  { sector: "systems", name: "Local Research / Self-Hosted Search", description: "Self-hosted search and RAG tools" },
  { sector: "systems", name: "Web Extraction / Rendered Capture", description: "Scraping, crawling, content extraction" },
  { sector: "ai", name: "ProductHunt AI Developer Tools", description: "Latest AI tools on ProductHunt" },
  { sector: "ai", name: "Community Signals / Reddit Discussions", description: "Reddit discussions on AI/dev" },
];

// ── Routes ────────────────────────────────────────────────────────────────────

// Health
gemHunter.get("/health", (c) => {
  const run = readLatestRun();
  return c.json({
    service: "gem-hunter-api",
    version: "1.0.0",
    status: run ? "operational" : "no_data",
    last_run: run?.date || null,
    last_modified: getLastModified(LATEST_RUN_PATH),
    total_gems: run?.gems?.length || 0,
    sectors: Object.keys(SECTOR_MAP),
    docs: "/gem-hunter/topics",
  });
});

// List all topic categories
gemHunter.get("/topics", (c) => {
  const sectorFilter = c.req.query("sector");
  const topics = sectorFilter
    ? TOPICS.filter((t) => t.sector === sectorFilter.toLowerCase())
    : TOPICS;

  const bySector: Record<string, typeof TOPICS> = {};
  for (const t of topics) {
    if (!bySector[t.sector]) bySector[t.sector] = [];
    bySector[t.sector].push(t);
  }

  return c.json({
    total: topics.length,
    sectors: Object.keys(SECTOR_MAP),
    by_sector: bySector,
  });
});

// Latest run — top gems
gemHunter.get("/latest", (c) => {
  const run = readLatestRun();
  if (!run) return c.json({ error: "No latest run found. Run: bun agent:run gem-hunter --exec" }, 404);

  const limit = Math.min(Number(c.req.query("limit") || 20), 100);
  const sector = c.req.query("sector");

  let gems = run.gems || [];
  if (sector) gems = filterBySector(gems, sector);

  // Sort by score descending
  gems = gems.sort((a, b) => (b.score || 0) - (a.score || 0)).slice(0, limit);

  return c.json({
    date: run.date,
    total: gems.length,
    sector: sector || "all",
    gems,
  });
});

// Filter by sector
gemHunter.get("/sector/:name", (c) => {
  const sector = c.req.param("name").toLowerCase();
  const run = readLatestRun();
  if (!run) return c.json({ error: "No data available" }, 404);

  const normalizedSector = SECTOR_ALIASES[sector] || sector;
  if (!SECTOR_MAP[normalizedSector]) {
    return c.json({ error: `Unknown sector: ${sector}`, available: Object.keys(SECTOR_MAP) }, 400);
  }

  const gems = filterBySector(run.gems || [], normalizedSector)
    .sort((a, b) => (b.score || 0) - (a.score || 0))
    .slice(0, 20);

  return c.json({
    sector: normalizedSector,
    date: run.date,
    count: gems.length,
    gems,
  });
});

// List reports
gemHunter.get("/reports", (c) => {
  if (!existsSync(REPORTS_DIR)) return c.json({ reports: [] });

  const files = readdirSync(REPORTS_DIR)
    .filter((f) => f.endsWith(".md") && f !== "SSOT.md")
    .sort()
    .reverse()
    .slice(0, 20);

  const reports = files.map((f) => {
    const fullPath = join(REPORTS_DIR, f);
    const stat = statSync(fullPath);
    return {
      filename: f,
      size_bytes: stat.size,
      modified: stat.mtime.toISOString(),
    };
  });

  return c.json({ count: reports.length, reports });
});

// Trending from SQLite history
gemHunter.get("/trending", (c) => {
  if (!existsSync(HISTORY_DB_PATH)) {
    return c.json({ message: "No history database yet — run gem-hunter a few times to build trends", trending: [] });
  }

  try {
    const db = new Database(HISTORY_DB_PATH, { readonly: true });
    const rows = db.query<
      { url: string; name: string; run_count: number; max_score: number },
      []
    >(
      `SELECT url, name, COUNT(*) as run_count, MAX(score) as max_score
       FROM gems GROUP BY url HAVING run_count >= 2
       ORDER BY run_count DESC, max_score DESC LIMIT 20`
    ).all();
    db.close();
    return c.json({ count: rows.length, trending: rows });
  } catch (e) {
    return c.json({ error: "Failed to query history", detail: String(e) }, 500);
  }
});

// Product pricing info
gemHunter.get("/product", (c) => {
  return c.json({
    product: "Gem Hunter API",
    description: "Discovery engine for the best open-source tools, models, papers, and frameworks across 20+ sources",
    sectors: Object.keys(SECTOR_MAP),
    sources: ["GitHub", "HuggingFace", "arXiv", "Exa", "Reddit", "StackOverflow", "ProductHunt", "X/Twitter", "npm", "GitLab", "CoinGecko", "DeFiLlama"],
    tiers: [
      {
        name: "Free",
        price: "R$0/mo",
        limits: { requests_per_day: 5, results_per_query: 5, sectors: ["ai"], sources: 2 },
      },
      {
        name: "Starter",
        price: "R$99/mo",
        limits: { requests_per_day: 50, results_per_query: 20, sectors: ["ai", "crypto", "systems"], sources: 6 },
        extras: ["email delivery", "trending alerts"],
      },
      {
        name: "Pro",
        price: "R$499/mo",
        limits: { requests_per_day: "unlimited", results_per_query: 100, sectors: "all", sources: "all" },
        extras: ["AI synthesis (Qwen)", "webhook delivery", "SQLite history export", "custom sectors", "priority support"],
      },
      {
        name: "Pay-per-use",
        price: "R$0.15/search",
        limits: { min_purchase: "R$15", results_per_query: 20, sectors: "all" },
      },
    ],
    endpoints: {
      topics: "GET /gem-hunter/topics",
      latest: "GET /gem-hunter/latest?sector=ai&limit=20",
      sector: "GET /gem-hunter/sector/{ai|crypto|systems|agents|governance|research}",
      trending: "GET /gem-hunter/trending",
      reports: "GET /gem-hunter/reports",
    },
    chatbot: {
      whatsapp: "WhatsApp chatbot for natural language gem search (coming soon)",
      example: "\"Find me the best agent orchestration tools released this month\"",
    },
  });
});
