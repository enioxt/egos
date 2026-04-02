#!/usr/bin/env bun
/**
 * 🌐 EGOS World Model
 *
 * Inspired by Block/Jack Dorsey "company as intelligence":
 * A persistent, queryable snapshot of EGOS state — tasks, agents,
 * capabilities, recent signals, constraints.
 *
 * The world model is the foundation for the Intelligence Layer:
 * it gives any agent or LLM a complete, up-to-date view of the system
 * before making decisions. No more "blind" execution.
 *
 * Usage:
 *   bun packages/shared/src/world-model.ts            # generate + print summary
 *   bun packages/shared/src/world-model.ts --save     # save to docs/world-model/current.json
 *   bun packages/shared/src/world-model.ts --mermaid  # print Mermaid graph
 *   bun packages/shared/src/world-model.ts --blockers # print P0 blockers only
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { execSync } from "child_process";
import { join } from "path";

const ROOT = "/home/enio/egos";
const OUTPUT_DIR = `${ROOT}/docs/world-model`;
const OUTPUT_FILE = `${OUTPUT_DIR}/current.json`;

// ── Types ─────────────────────────────────────────────────────────────────────

interface TaskSnapshot {
  id: string;
  priority: "P0" | "P1" | "P2" | "unknown";
  done: boolean;
  text: string;
  section: string;
}

interface AgentSnapshot {
  id: string;
  role: "IC" | "DRI" | "coach" | "killed";
  description: string;
}

interface SignalSnapshot {
  source: "gem-hunter" | "governance-drift" | "security-audit";
  date: string;
  headline: string;
  severity: "CRITICAL" | "WARNING" | "CLEAN" | "UNKNOWN";
}

interface CapabilitySnapshot {
  domain: string;
  count: number;
}

interface WorldModel {
  generated_at: string;
  git_sha: string;
  git_branch: string;
  last_commit: string;

  tasks: {
    total: number;
    done: number;
    p0_blockers: TaskSnapshot[];
    p1_sprint: TaskSnapshot[];
    p2_backlog: TaskSnapshot[];
  };

  agents: {
    total: number;
    active: AgentSnapshot[];
    killed: string[];
  };

  capabilities: {
    total: number;
    domains: CapabilitySnapshot[];
  };

  signals: SignalSnapshot[];

  blockers: string[];    // human-readable P0 blockers
  health_pct: number;    // done/total * 100
}

// ── Parsers ───────────────────────────────────────────────────────────────────

function parseTasks(content: string): TaskSnapshot[] {
  const tasks: TaskSnapshot[] = [];
  const lines = content.split("\n");
  let currentSection = "unknown";

  for (const line of lines) {
    // Detect section headers: ### headings and **P0/P1/P2** bold lines
    if (line.startsWith("###")) {
      currentSection = line.replace(/^###\s*/, "").trim();
      continue;
    }
    // Any **bold** line is a subsection header — update context
    if (line.match(/^\*\*.+\*\*[:\s]*$/)) {
      currentSection = line.replace(/\*\*/g, "").replace(/:$/, "").trim();
      continue;
    }

    const match = line.match(/^\s*-\s+\[([ xX])\]\s+([A-Z]+-\d+)[:\s]/);
    if (!match) continue;

    const done = match[1] !== " ";
    const id = match[2];
    const text = line.trim();

    // Infer priority from section or explicit markers
    let priority: TaskSnapshot["priority"] = "unknown";
    if (currentSection.includes("P0") || text.includes("P0-URGENT") || currentSection.includes("Revenue blocking") || currentSection.includes("URGENTE")) {
      priority = "P0";
    } else if (currentSection.includes("P1") || currentSection.includes("Competitive") || currentSection.includes("Sprint")) {
      priority = "P1";
    } else if (currentSection.includes("P2") || currentSection.includes("Growth") || currentSection.includes("Backlog")) {
      priority = "P2";
    } else if (!done) {
      priority = "P1"; // default pending to P1
    }

    tasks.push({ id, done, text: text.slice(0, 120), section: currentSection, priority });
  }

  return tasks;
}

function parseAgents(registryPath: string): AgentSnapshot[] {
  try {
    const data = JSON.parse(readFileSync(registryPath, "utf8"));
    const agents = data.agents ?? [];
    return agents.map((a: any): AgentSnapshot => ({
      id: a.id,
      role: a.description?.includes("[KILLED") ? "killed"
           : a.id.includes("coach") || a.id.includes("hermes") ? "coach"
           : a.id.includes("auditor") || a.id.includes("sentinel") || a.id.includes("checker") ? "DRI"
           : "IC",
      description: (a.description ?? "").slice(0, 80),
    }));
  } catch {
    return [];
  }
}

function parseCapabilities(registryPath: string): CapabilitySnapshot[] {
  try {
    const content = readFileSync(registryPath, "utf8");
    const domains: CapabilitySnapshot[] = [];
    const sectionPattern = /^## (\d+\. .+)/gm;
    const rowPattern = /^\|[^|]+\|/gm;
    let m;
    let currentDomain = "";
    let rowCount = 0;

    const lines = content.split("\n");
    for (const line of lines) {
      if (line.match(/^## \d+\./)) {
        if (currentDomain && rowCount > 0) {
          domains.push({ domain: currentDomain, count: rowCount - 1 }); // -1 for header row
        }
        currentDomain = line.replace(/^## \d+\.\s*/, "").trim();
        rowCount = 0;
      } else if (line.startsWith("|") && currentDomain && !line.includes("---")) {
        rowCount++;
      }
    }
    if (currentDomain && rowCount > 0) {
      domains.push({ domain: currentDomain, count: rowCount - 1 });
    }
    return domains.filter(d => d.count > 0);
  } catch {
    return [];
  }
}

function parseSignals(): SignalSnapshot[] {
  const signals: SignalSnapshot[] = [];

  // Governance drift reports
  try {
    const files = execSync(`ls -t ${ROOT}/docs/jobs/*.md 2>/dev/null | head -3`, { encoding: "utf8" })
      .trim().split("\n").filter(Boolean);

    for (const f of files) {
      const content = readFileSync(f, "utf8");
      const dateMatch = f.match(/(\d{4}-\d{2}-\d{2})/);
      const statusMatch = content.match(/[Ss]tatus:\s*(\w+)/);
      const severityRaw = statusMatch?.[1]?.toUpperCase() ?? "UNKNOWN";
      const severity = (["CRITICAL", "WARNING", "CLEAN"].includes(severityRaw) ? severityRaw : "UNKNOWN") as SignalSnapshot["severity"];
      const firstLine = content.split("\n").find(l => l.trim() && !l.startsWith("#")) ?? "";

      signals.push({
        source: f.includes("governance") ? "governance-drift" : f.includes("security") ? "security-audit" : "gem-hunter",
        date: dateMatch?.[1] ?? "unknown",
        headline: firstLine.slice(0, 100),
        severity,
      });
    }
  } catch {}

  // Gem Hunter latest markdown report
  try {
    const gemFile = execSync(`ls -t ${ROOT}/docs/gem-hunter/*.md 2>/dev/null | grep -v SSOT | head -1`, { encoding: "utf8" }).trim();
    if (gemFile && existsSync(gemFile)) {
      const content = readFileSync(gemFile, "utf8");
      const dateMatch = gemFile.match(/(\d{4}-\d{2}-\d{2})/);
      const topGem = content.match(/score[:\s]+(\d+)/i)?.[0] ?? "latest discovery";
      signals.push({
        source: "gem-hunter",
        date: dateMatch?.[1] ?? "unknown",
        headline: `Latest gem scan: ${topGem}`,
        severity: "CLEAN",
      });
    }
  } catch {}

  // Gem Hunter high-value signals from signals.json (GH-050)
  try {
    const signalsPath = join(ROOT, 'docs/gem-hunter/signals.json');
    if (existsSync(signalsPath)) {
      const data = JSON.parse(readFileSync(signalsPath, 'utf-8'));
      for (const sig of (data.signals ?? [])) {
        signals.push({
          source: 'gem-hunter',
          date: sig.date ?? 'unknown',
          headline: (sig.headline ?? `${sig.name} (score: ${sig.score})`).slice(0, 100),
          severity: sig.score > 90 ? 'CRITICAL' : 'CLEAN',
        });
      }
    }
  } catch {}

  return signals;
}

// ── Mermaid Generator ─────────────────────────────────────────────────────────

function toMermaid(model: WorldModel): string {
  const lines = [
    "graph TD",
    `  WM[🌐 EGOS World Model<br/>${model.generated_at.slice(0, 10)}]`,
    "",
    `  HEALTH[Health: ${model.health_pct}%<br/>${model.tasks.done}/${model.tasks.total} done]`,
    `  WM --> HEALTH`,
  ];

  // P0 blockers
  if (model.tasks.p0_blockers.length > 0) {
    lines.push(`  P0[🔴 P0 Blockers: ${model.tasks.p0_blockers.length}]`);
    lines.push(`  WM --> P0`);
    for (const t of model.tasks.p0_blockers.slice(0, 3)) {
      const safe = t.id.replace(/[^A-Za-z0-9]/g, "_");
      lines.push(`  ${safe}[${t.id}]`);
      lines.push(`  P0 --> ${safe}`);
    }
  }

  // Active agents
  const activeAgents = model.agents.active.slice(0, 5);
  if (activeAgents.length > 0) {
    lines.push(`  AGENTS[⚙️ Agents: ${model.agents.total} active]`);
    lines.push(`  WM --> AGENTS`);
    for (const a of activeAgents) {
      const safe = a.id.replace(/[^A-Za-z0-9]/g, "_");
      const icon = a.role === "DRI" ? "🎯" : a.role === "coach" ? "🧑‍🏫" : "⚡";
      lines.push(`  ${safe}[${icon} ${a.id}<br/>${a.role}]`);
      lines.push(`  AGENTS --> ${safe}`);
    }
  }

  // Signals
  const criticals = model.signals.filter(s => s.severity === "CRITICAL");
  if (criticals.length > 0) {
    lines.push(`  SIGNALS[⚠️ Critical Signals: ${criticals.length}]`);
    lines.push(`  WM --> SIGNALS`);
  }

  return lines.join("\n");
}

// ── Main ──────────────────────────────────────────────────────────────────────

function buildWorldModel(): WorldModel {
  const tasksContent = readFileSync(`${ROOT}/TASKS.md`, "utf8");
  const allTasks = parseTasks(tasksContent);
  const pendingTasks = allTasks.filter(t => !t.done);

  const p0 = pendingTasks.filter(t => t.priority === "P0");
  const p1 = pendingTasks.filter(t => t.priority === "P1");
  const p2 = pendingTasks.filter(t => t.priority === "P2" || t.priority === "unknown");

  const agents = parseAgents(`${ROOT}/agents/registry/agents.json`);
  const activeAgents = agents.filter(a => a.role !== "killed");
  const killedAgents = agents.filter(a => a.role === "killed").map(a => a.id);

  const capDomains = parseCapabilities(`${ROOT}/docs/CAPABILITY_REGISTRY.md`);
  const totalCaps = capDomains.reduce((s, d) => s + d.count, 0);

  const signals = parseSignals();

  const gitSha = execSync(`git -C ${ROOT} rev-parse --short HEAD 2>/dev/null || echo unknown`, { encoding: "utf8" }).trim();
  const gitBranch = execSync(`git -C ${ROOT} branch --show-current 2>/dev/null || echo main`, { encoding: "utf8" }).trim();
  const lastCommit = execSync(`git -C ${ROOT} log --oneline -1 2>/dev/null || echo none`, { encoding: "utf8" }).trim();

  const done = allTasks.filter(t => t.done).length;
  const total = allTasks.length;

  return {
    generated_at: new Date().toISOString(),
    git_sha: gitSha,
    git_branch: gitBranch,
    last_commit: lastCommit,
    tasks: {
      total,
      done,
      p0_blockers: p0,
      p1_sprint: p1,
      p2_backlog: p2,
    },
    agents: {
      total: activeAgents.length,
      active: activeAgents,
      killed: killedAgents,
    },
    capabilities: {
      total: totalCaps,
      domains: capDomains,
    },
    signals,
    blockers: p0.map(t => `${t.id}: ${t.text.slice(0, 80)}`),
    health_pct: Math.round((done / total) * 100),
  };
}

function printSummary(model: WorldModel) {
  console.log(`\n🌐 EGOS World Model — ${model.generated_at.slice(0, 16)}`);
  console.log(`   SHA: ${model.git_sha} | Branch: ${model.git_branch}`);
  console.log(`   Last: ${model.last_commit}`);
  console.log();
  console.log(`📊 Health: ${model.health_pct}% (${model.tasks.done}/${model.tasks.total} tasks done)`);
  console.log(`⚙️  Agents: ${model.agents.total} active (${model.agents.killed.length} killed)`);
  console.log(`🔧 Capabilities: ${model.capabilities.total} across ${model.capabilities.domains.length} domains`);
  console.log();

  if (model.blockers.length > 0) {
    console.log(`🔴 P0 Blockers (${model.blockers.length}):`);
    for (const b of model.blockers) {
      console.log(`   • ${b}`);
    }
    console.log();
  }

  if (model.tasks.p1_sprint.length > 0) {
    console.log(`🟡 P1 Sprint (top 5 of ${model.tasks.p1_sprint.length}):`);
    for (const t of model.tasks.p1_sprint.slice(0, 5)) {
      console.log(`   • ${t.id}: ${t.text.slice(0, 70)}`);
    }
    console.log();
  }

  const critical = model.signals.filter(s => s.severity === "CRITICAL");
  if (critical.length > 0) {
    console.log(`⚠️  Critical Signals:`);
    for (const s of critical) {
      console.log(`   • [${s.source}] ${s.headline}`);
    }
  }
}

// ── CLI ───────────────────────────────────────────────────────────────────────

const SAVE = process.argv.includes("--save");
const MERMAID = process.argv.includes("--mermaid");
const BLOCKERS_ONLY = process.argv.includes("--blockers");
const JSON_OUT = process.argv.includes("--json");

const model = buildWorldModel();

if (BLOCKERS_ONLY) {
  if (model.blockers.length === 0) {
    console.log("✅ No P0 blockers");
  } else {
    console.log(`🔴 ${model.blockers.length} P0 blockers:`);
    model.blockers.forEach(b => console.log(`  • ${b}`));
  }
} else if (MERMAID) {
  console.log(toMermaid(model));
} else if (JSON_OUT) {
  console.log(JSON.stringify(model, null, 2));
} else {
  printSummary(model);
}

if (SAVE) {
  if (!existsSync(OUTPUT_DIR)) mkdirSync(OUTPUT_DIR, { recursive: true });
  writeFileSync(OUTPUT_FILE, JSON.stringify(model, null, 2));
  console.log(`\n💾 Saved: ${OUTPUT_FILE}`);
}

export type { WorldModel, TaskSnapshot, AgentSnapshot, SignalSnapshot };
export { buildWorldModel, toMermaid };
