#!/usr/bin/env bun
/**
 * @egos/mcp-governance — EGOS-087
 * MCP server (stdio) for SSOT drift check, task listing, agent status, repo health.
 *
 * Connect via Claude Code settings.json:
 *   { "mcpServers": { "egos-governance": { "command": "bun", "args": ["/path/to/packages/mcp-governance/src/index.ts"] } } }
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync, existsSync } from "fs";
import { execSync } from "child_process";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

// ── Paths ──────────────────────────────────────────────────────────────────
const __dir = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dir, "../../..");
const AGENTS_JSON = join(REPO_ROOT, "agents/registry/agents.json");
const TASKS_MD = join(REPO_ROOT, "TASKS.md");

// ── Helpers ────────────────────────────────────────────────────────────────
function readFileSafe(path: string): string {
  if (!existsSync(path)) return "";
  return readFileSync(path, "utf8");
}

function execSafe(cmd: string, cwd: string = REPO_ROOT): string {
  try {
    return execSync(cmd, { cwd, encoding: "utf8", timeout: 10_000 }).trim();
  } catch {
    return "";
  }
}

function parseTasks(content: string): Array<{ id: string; status: string; text: string }> {
  const tasks: Array<{ id: string; status: string; text: string }> = [];
  const lines = content.split("\n");
  const taskRe = /^- \[([ xX])\] (EGOS-\d+[^:]*)?:?\s*(.+)/;
  for (const line of lines) {
    const m = line.match(taskRe);
    if (!m) continue;
    const checked = m[1].trim().toLowerCase() === "x";
    const id = m[2]?.trim() ?? "";
    const text = m[3]?.trim() ?? "";
    tasks.push({ id, status: checked ? "done" : "pending", text });
  }
  return tasks;
}

// ── MCP Server ─────────────────────────────────────────────────────────────
const server = new McpServer(
  { name: "egos-governance", version: "0.1.0" },
  { capabilities: { tools: {} } }
);

// Tool 1: ssot_drift_check
server.registerTool(
  "ssot_drift_check",
  {
    description:
      "Check SSOT drift: compares agents.json registry with tasks in TASKS.md. Returns list of agents with no corresponding task, tasks with no agent owner, and pending high-priority items.",
    inputSchema: z.object({}),
  },
  async () => {
    const agentsRaw = readFileSafe(AGENTS_JSON);
    const tasksContent = readFileSafe(TASKS_MD);
    const agents: Array<{ id: string; status: string; owner?: string }> =
      agentsRaw ? JSON.parse(agentsRaw).agents ?? [] : [];
    const tasks = parseTasks(tasksContent);

    const taskIds = new Set(tasks.map((t) => t.id).filter(Boolean));
    const agentIds = new Set(agents.map((a) => a.id));

    // Agents with no task reference
    const untracked = agents
      .filter((a) => !taskIds.has(a.id))
      .map((a) => ({ id: a.id, status: a.status }));

    // Pending tasks (EGOS-xxx form)
    const pending = tasks.filter((t) => t.status === "pending" && t.id);

    // Tasks referencing no agent
    const orphaned = tasks.filter(
      (t) => t.id && !agentIds.has(t.id.toLowerCase().replace(/-/g, "_"))
    );

    const result = {
      checked_at: new Date().toISOString(),
      total_agents: agents.length,
      total_tasks: tasks.length,
      pending_tasks: pending.length,
      untracked_agents: untracked,
      orphaned_tasks: orphaned.slice(0, 20),
      drift_score: untracked.length + orphaned.length,
    };
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// Tool 2: list_tasks
server.registerTool(
  "list_tasks",
  {
    description:
      "List tasks from TASKS.md filtered by status. Returns task id, status, and description.",
    inputSchema: z.object({
      status: z
        .enum(["pending", "done", "all"])
        .optional()
        .describe("Filter by status (default: pending)"),
      limit: z
        .number()
        .int()
        .min(1)
        .max(200)
        .optional()
        .describe("Max tasks to return (default: 50)"),
    }),
  },
  async ({ status = "pending", limit = 50 }) => {
    const content = readFileSafe(TASKS_MD);
    const all = parseTasks(content);
    const filtered =
      status === "all" ? all : all.filter((t) => t.status === status);
    const result = {
      filter: status,
      total_matching: filtered.length,
      tasks: filtered.slice(0, limit),
    };
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// Tool 3: agent_status
server.registerTool(
  "agent_status",
  {
    description:
      "Returns EGOS agent registry health: total agents, by kind, by status, risk levels, and active entrypoints.",
    inputSchema: z.object({
      filter_kind: z
        .string()
        .optional()
        .describe("Filter agents by kind (tool | monitor | router | daemon)"),
    }),
  },
  async ({ filter_kind }) => {
    const raw = readFileSafe(AGENTS_JSON);
    if (!raw) {
      return {
        content: [{ type: "text", text: JSON.stringify({ error: "agents.json not found" }) }],
      };
    }
    const registry = JSON.parse(raw);
    let agents: Array<Record<string, unknown>> = registry.agents ?? [];
    if (filter_kind) {
      agents = agents.filter((a) => a["kind"] === filter_kind);
    }

    const byKind: Record<string, number> = {};
    const byStatus: Record<string, number> = {};
    const byRisk: Record<string, number> = {};
    for (const a of agents) {
      const k = String(a["kind"] ?? "unknown");
      const s = String(a["status"] ?? "unknown");
      const r = String(a["risk_level"] ?? "unknown");
      byKind[k] = (byKind[k] ?? 0) + 1;
      byStatus[s] = (byStatus[s] ?? 0) + 1;
      byRisk[r] = (byRisk[r] ?? 0) + 1;
    }

    const result = {
      registry_version: registry.version,
      updated: registry.updated,
      total: agents.length,
      by_kind: byKind,
      by_status: byStatus,
      by_risk: byRisk,
      agents: agents.map((a) => ({
        id: a["id"],
        kind: a["kind"],
        status: a["status"],
        risk_level: a["risk_level"],
        entrypoint: a["entrypoint"],
      })),
    };
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// Tool 4: repo_health
server.registerTool(
  "repo_health",
  {
    description:
      "Returns EGOS repo health score: TASKS.md line count, last commit age, git status, and governance sync state.",
    inputSchema: z.object({}),
  },
  async () => {
    const tasksContent = readFileSafe(TASKS_MD);
    const lineCount = tasksContent.split("\n").length;
    const tasks = parseTasks(tasksContent);
    const pendingCount = tasks.filter((t) => t.status === "pending").length;
    const doneCount = tasks.filter((t) => t.status === "done").length;

    const lastCommitAge = execSafe(
      'git log -1 --format="%ar" HEAD'
    );
    const lastCommitHash = execSafe("git log -1 --format=%h HEAD");
    const lastCommitMsg = execSafe("git log -1 --format=%s HEAD");
    const branch = execSafe("git rev-parse --abbrev-ref HEAD");
    const uncommitted = execSafe("git status --porcelain").split("\n").filter(Boolean).length;

    // Governance files existence check
    const governanceFiles = [
      "AGENTS.md",
      "TASKS.md",
      ".guarani/mcp-config.json",
      "agents/registry/agents.json",
      "docs/SYSTEM_MAP.md",
    ];
    const govSync = governanceFiles.map((f) => ({
      file: f,
      exists: existsSync(join(REPO_ROOT, f)),
    }));
    const missingGov = govSync.filter((g) => !g.exists).map((g) => g.file);

    // Scoring: 100 - penalties
    let score = 100;
    if (pendingCount > 20) score -= 10;
    if (uncommitted > 10) score -= 10;
    if (missingGov.length > 0) score -= missingGov.length * 5;

    const result = {
      checked_at: new Date().toISOString(),
      repo_root: REPO_ROOT,
      branch,
      last_commit: { hash: lastCommitHash, message: lastCommitMsg, age: lastCommitAge },
      tasks_md: { line_count: lineCount, pending: pendingCount, done: doneCount },
      uncommitted_files: uncommitted,
      governance_sync: { all_present: missingGov.length === 0, missing: missingGov },
      health_score: Math.max(0, score),
    };
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// ── Bootstrap ──────────────────────────────────────────────────────────────
const transport = new StdioServerTransport();
await server.connect(transport);
