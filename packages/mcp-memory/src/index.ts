#!/usr/bin/env bun
/**
 * @egos/mcp-memory — EGOS-088
 * MCP server (stdio) for persistent conversation memory.
 *
 * Tools:
 *   memory_store   — write a memory entry to ~/.egos/memory/mcp-store/{key}.md
 *   memory_recall  — keyword search across ~/.claude/projects/…/memory/*.md
 *   memory_list    — list all stored memories with key + first line
 *   memory_delete  — delete a stored memory by key
 *
 * Connect via Claude Code .claude/settings.json:
 *   {
 *     "mcpServers": {
 *       "egos-memory": {
 *         "command": "bun",
 *         "args": ["/home/enio/egos/packages/mcp-memory/src/index.ts"]
 *       }
 *     }
 *   }
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import {
  readFileSync,
  writeFileSync,
  existsSync,
  mkdirSync,
  readdirSync,
  unlinkSync,
  statSync,
} from "fs";
import { join, basename } from "path";
import { homedir } from "os";

// ── Paths ──────────────────────────────────────────────────────────────────

const HOME = homedir();

/** Where new memories are written */
const STORE_DIR = join(HOME, ".egos", "memory", "mcp-store");

/** Where Claude Code auto-memory files live (for memory_recall) */
const CLAUDE_MEMORY_DIR = join(
  HOME,
  ".claude",
  "projects",
  "-home-enio-egos",
  "memory"
);

// Ensure store dir exists at startup
if (!existsSync(STORE_DIR)) {
  mkdirSync(STORE_DIR, { recursive: true });
}

// ── Helpers ────────────────────────────────────────────────────────────────

function sanitizeKey(key: string): string {
  // Allow alphanumeric, hyphens, underscores, dots — strip everything else
  return key.replace(/[^a-zA-Z0-9_\-\.]/g, "_").slice(0, 120);
}

function filePath(key: string): string {
  return join(STORE_DIR, `${sanitizeKey(key)}.md`);
}

function buildFrontmatter(tags: string[]): string {
  const date = new Date().toISOString();
  const tagLine = tags.length > 0 ? `tags: [${tags.join(", ")}]` : "tags: []";
  return `---\ndate: ${date}\n${tagLine}\n---\n\n`;
}

function parseFrontmatter(raw: string): {
  date: string | null;
  tags: string[];
  body: string;
} {
  const fmMatch = raw.match(/^---\n([\s\S]*?)\n---\n\n?([\s\S]*)$/);
  if (!fmMatch) return { date: null, tags: [], body: raw };
  const fm = fmMatch[1];
  const body = fmMatch[2];
  const dateMatch = fm.match(/^date:\s*(.+)$/m);
  const tagsMatch = fm.match(/^tags:\s*\[(.+?)\]$/m);
  return {
    date: dateMatch ? dateMatch[1].trim() : null,
    tags: tagsMatch
      ? tagsMatch[1].split(",").map((t) => t.trim()).filter(Boolean)
      : [],
    body,
  };
}

/** Read all .md files from a directory safely */
function readAllMd(dir: string): Array<{ key: string; path: string; raw: string }> {
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith(".md"))
    .map((f) => {
      const p = join(dir, f);
      try {
        return { key: f.replace(/\.md$/, ""), path: p, raw: readFileSync(p, "utf8") };
      } catch {
        return null;
      }
    })
    .filter((x): x is { key: string; path: string; raw: string } => x !== null);
}

/** Simple keyword match — returns true if ALL terms appear in text (case-insensitive) */
function matchesQuery(text: string, query: string): boolean {
  const lower = text.toLowerCase();
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  return terms.every((t) => lower.includes(t));
}

function snippet(body: string, maxLen = 200): string {
  const trimmed = body.trim();
  return trimmed.length <= maxLen ? trimmed : trimmed.slice(0, maxLen) + "…";
}

// ── MCP Server ─────────────────────────────────────────────────────────────

const server = new McpServer(
  { name: "egos-memory", version: "0.1.0" },
  { capabilities: { tools: {} } }
);

// ── Tool 1: memory_store ──────────────────────────────────────────────────

server.registerTool(
  "memory_store",
  {
    description:
      "Store a memory entry as a Markdown file in ~/.egos/memory/mcp-store/{key}.md. " +
      "Overwrites if key already exists.",
    inputSchema: z.object({
      key: z.string().min(1).describe("Unique identifier for this memory (filename-safe)"),
      content: z.string().min(1).describe("Markdown content to store"),
      tags: z
        .array(z.string())
        .optional()
        .describe("Optional list of tags for filtering"),
    }),
  },
  async ({ key, content, tags = [] }) => {
    const p = filePath(key);
    const fm = buildFrontmatter(tags);
    writeFileSync(p, fm + content, "utf8");
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ stored: true, path: p, key: sanitizeKey(key) }, null, 2),
        },
      ],
    };
  }
);

// ── Tool 2: memory_recall ─────────────────────────────────────────────────

server.registerTool(
  "memory_recall",
  {
    description:
      "Search stored memories (both ~/.egos/memory/mcp-store/ and Claude auto-memory) " +
      "using simple keyword matching. Returns matching entries with key, snippet, path, and tags.",
    inputSchema: z.object({
      query: z.string().min(1).describe("Keywords to search for (space-separated, all must match)"),
      limit: z
        .number()
        .int()
        .min(1)
        .max(50)
        .optional()
        .describe("Max results to return (default: 10)"),
    }),
  },
  async ({ query, limit = 10 }) => {
    const storeFiles = readAllMd(STORE_DIR);
    const claudeFiles = readAllMd(CLAUDE_MEMORY_DIR);
    const all = [...storeFiles, ...claudeFiles];

    const results = all
      .filter(({ raw }) => matchesQuery(raw, query))
      .slice(0, limit)
      .map(({ key, path, raw }) => {
        const { date, tags, body } = parseFrontmatter(raw);
        return { key, snippet: snippet(body), path, tags, date };
      });

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { query, total_searched: all.length, results },
            null,
            2
          ),
        },
      ],
    };
  }
);

// ── Tool 3: memory_list ───────────────────────────────────────────────────

server.registerTool(
  "memory_list",
  {
    description:
      "List all memories stored in ~/.egos/memory/mcp-store/ with key, title (first non-empty line), date, and tags.",
    inputSchema: z.object({}),
  },
  async () => {
    const files = readAllMd(STORE_DIR);
    const memories = files.map(({ key, path, raw }) => {
      const { date, tags, body } = parseFrontmatter(raw);
      const title = body.split("\n").find((l) => l.trim().length > 0)?.trim() ?? "";
      const stat = statSync(path);
      return { key, title, date, tags, size_bytes: stat.size };
    });

    // Sort newest first (by date field if present, else mtime)
    memories.sort((a, b) => {
      const da = a.date ? new Date(a.date).getTime() : 0;
      const db = b.date ? new Date(b.date).getTime() : 0;
      return db - da;
    });

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ total: memories.length, memories }, null, 2),
        },
      ],
    };
  }
);

// ── Tool 4: memory_delete ─────────────────────────────────────────────────

server.registerTool(
  "memory_delete",
  {
    description: "Delete a stored memory from ~/.egos/memory/mcp-store/{key}.md.",
    inputSchema: z.object({
      key: z.string().min(1).describe("Key of the memory to delete"),
    }),
  },
  async ({ key }) => {
    const p = filePath(key);
    if (!existsSync(p)) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              { deleted: false, error: `Key "${sanitizeKey(key)}" not found`, path: p },
              null,
              2
            ),
          },
        ],
      };
    }
    unlinkSync(p);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ deleted: true, path: p, key: sanitizeKey(key) }, null, 2),
        },
      ],
    };
  }
);

// ── Bootstrap ──────────────────────────────────────────────────────────────

const transport = new StdioServerTransport();
await server.connect(transport);
