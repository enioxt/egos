#!/usr/bin/env bun
/**
 * @egos/knowledge-mcp — KB-018
 * MCP server (stdio) for EGOS Knowledge Base access.
 * Tools: search_wiki, get_page, record_learning, get_stats
 *
 * Connect via Claude Code settings.json:
 *   { "mcpServers": { "egos-knowledge": { "command": "bun", "args": ["/home/enio/egos/packages/knowledge-mcp/src/index.ts"] } } }
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// ── Config ─────────────────────────────────────────────────────────────────
const GW = process.env.EGOS_GATEWAY_URL ?? "https://gateway.egos.ia.br";
const TIMEOUT = 8000;

// ── Helpers ────────────────────────────────────────────────────────────────
async function gwFetch(path: string, init?: RequestInit): Promise<unknown> {
  try {
    const res = await fetch(`${GW}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      signal: AbortSignal.timeout(TIMEOUT),
    });
    if (!res.ok) return { error: `HTTP ${res.status}`, path };
    return res.json();
  } catch (e) {
    return { error: (e as Error).message, path };
  }
}

function fmt(data: unknown): string {
  return JSON.stringify(data, null, 2);
}

// ── MCP Server ─────────────────────────────────────────────────────────────
const server = new McpServer({
  name: "egos-knowledge",
  version: "1.0.0",
});

// Tool: search_wiki
server.tool(
  "search_wiki",
  "Search the EGOS Knowledge Base wiki pages by keyword. Returns matching pages with title, category, quality score, and summary.",
  { query: z.string().describe("Search term (e.g. 'guard brasil', 'orchestration', 'agent')") },
  async ({ query }) => {
    const data = await gwFetch(`/knowledge/search?q=${encodeURIComponent(query)}`);
    const d = data as { results?: Array<{ title: string; category: string; quality_score: number; summary?: string; slug: string }> };
    if (!d.results?.length) return { content: [{ type: "text" as const, text: `No results found for "${query}"` }] };
    const lines = d.results.slice(0, 10).map((p) =>
      `• [${p.category}] **${p.title}** (quality: ${p.quality_score}/100)\n  ${p.summary ?? "No summary"}\n  slug: ${p.slug}`
    );
    return { content: [{ type: "text" as const, text: `Search results for "${query}":\n\n${lines.join("\n\n")}` }] };
  }
);

// Tool: get_page
server.tool(
  "get_page",
  "Get a specific Knowledge Base wiki page by slug. Returns full content, tags, and metadata.",
  { slug: z.string().describe("Page slug (e.g. 'guard-brasil-api', 'egos-orchestration')") },
  async ({ slug }) => {
    const data = await gwFetch(`/knowledge/pages/${slug}`);
    const d = data as { title?: string; content?: string; category?: string; tags?: string[]; quality_score?: number; error?: string };
    if (d.error || !d.title) return { content: [{ type: "text" as const, text: `Page "${slug}" not found` }] };
    const text = [
      `# ${d.title}`,
      `Category: ${d.category} | Quality: ${d.quality_score}/100`,
      `Tags: ${(d.tags ?? []).join(", ")}`,
      "",
      d.content ?? "(no content)",
    ].join("\n");
    return { content: [{ type: "text" as const, text }] };
  }
);

// Tool: get_stats
server.tool(
  "get_stats",
  "Get Knowledge Base statistics: total pages, average quality, breakdown by category, and learnings count.",
  {},
  async () => {
    const data = await gwFetch("/knowledge/stats");
    const d = data as {
      pages?: { total: number; avg_quality: number; by_category: Record<string, number> };
      learnings?: { total: number };
    };
    if (!d.pages) return { content: [{ type: "text" as const, text: `Stats unavailable: ${fmt(data)}` }] };
    const cats = Object.entries(d.pages.by_category ?? {})
      .map(([k, v]) => `  ${k}: ${v}`)
      .join("\n");
    const text = [
      `Knowledge Base Stats:`,
      `  Total pages: ${d.pages.total}`,
      `  Average quality: ${d.pages.avg_quality}/100`,
      `  By category:\n${cats}`,
      `  Total learnings: ${d.learnings?.total ?? 0}`,
    ].join("\n");
    return { content: [{ type: "text" as const, text }] };
  }
);

// Tool: record_learning
server.tool(
  "record_learning",
  "Record a learning or insight from the current session into the EGOS Knowledge Base.",
  {
    domain: z.enum(["general", "architecture", "deployment", "monetization", "governance", "agents", "security", "dx"])
      .describe("Domain of the learning"),
    outcome: z.enum(["success", "failure", "insight"])
      .describe("Type of learning"),
    description: z.string().describe("What was learned (1-3 sentences)"),
    tags: z.array(z.string()).optional().describe("Optional tags for categorization"),
  },
  async ({ domain, outcome, description, tags }) => {
    const data = await gwFetch("/knowledge/learnings", {
      method: "POST",
      body: JSON.stringify({ domain, outcome, description, tags: tags ?? [], session_id: new Date().toISOString().slice(0, 10) }),
    });
    const d = data as { id?: string; error?: string };
    if (d.error) return { content: [{ type: "text" as const, text: `Failed to record: ${d.error}` }] };
    return { content: [{ type: "text" as const, text: `✅ Learning recorded (id: ${d.id ?? "ok"})\n[${domain}/${outcome}] ${description}` }] };
  }
);

// Tool: list_learnings
server.tool(
  "list_learnings",
  "List recent learnings from the EGOS Knowledge Base.",
  {
    domain: z.string().optional().describe("Filter by domain (optional)"),
    limit: z.number().optional().describe("Max results (default 10)"),
  },
  async ({ domain, limit = 10 }) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (domain) params.set("domain", domain);
    const data = await gwFetch(`/knowledge/learnings?${params}`);
    const d = data as { learnings?: Array<{ domain: string; outcome: string; description: string; created_at: string }> };
    if (!d.learnings?.length) return { content: [{ type: "text" as const, text: "No learnings found" }] };
    const lines = d.learnings.map((l) =>
      `• [${l.domain}/${l.outcome}] ${l.description} (${new Date(l.created_at).toLocaleDateString("pt-BR")})`
    );
    return { content: [{ type: "text" as const, text: `Recent Learnings:\n\n${lines.join("\n")}` }] };
  }
);

// Tool: ingest_file
server.tool(
  "ingest_file",
  "Ingest a local PDF, DOCX, or Markdown file into the EGOS Knowledge Base. Runs Guard Brasil PII scan automatically.",
  {
    file_path: z.string().describe("Absolute path to the file (PDF, DOCX, or Markdown)"),
    category: z.string().optional().describe("Category (e.g. 'metalurgia', 'juridico', 'saude'). Default: 'geral'"),
    dry: z.boolean().optional().describe("If true, preview without writing to database"),
  },
  async ({ file_path, category = "geral", dry = false }) => {
    try {
      const { execSync } = await import("child_process");
      const bunPath = process.execPath;
      const scriptPath = new URL("../../scripts/kb-ingest.ts", import.meta.url).pathname;
      const args = ["--file", file_path, "--category", category, ...(dry ? ["--dry"] : [])];
      const output = execSync(`${bunPath} ${scriptPath} ${args.map((a) => JSON.stringify(a)).join(" ")}`, {
        env: process.env,
        encoding: "utf-8",
        timeout: 30000,
      });
      return { content: [{ type: "text" as const, text: output }] };
    } catch (e) {
      const err = e as { stdout?: string; stderr?: string; message?: string };
      const detail = err.stdout ?? err.stderr ?? err.message ?? "unknown error";
      return { content: [{ type: "text" as const, text: "❌ Ingest failed: " + detail }] };
    }
  }
);

// ── Start ──────────────────────────────────────────────────────────────────
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  process.stderr.write("[knowledge-mcp] Started — gateway: " + GW + "\n");
}

main().catch((e) => {
  process.stderr.write("[knowledge-mcp] Fatal: " + e.message + "\n");
  process.exit(1);
});
