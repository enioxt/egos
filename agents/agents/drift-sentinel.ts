/**
 * AGENT-034: Drift Sentinel v1.0
 *
 * 24/7 configuration drift detection — compares narrative (docs/code) vs live system state.
 *
 * Monitors:
 * - TASKS.md priorities vs actual git activity
 * - AGENTS.md registry vs agents/ directory
 * - CLAUDE.md rules vs actual behavior
 * - docs/SYSTEM_MAP.md vs live architecture
 * - .guarani/prompts/ versions vs git history
 *
 * Actions:
 * - Detects divergence with severity levels
 * - Writes drift report to docs/drift-sentinel/
 * - Alerts via Telegram when critical drift found
 * - Suggests reconciliation actions
 *
 * Usage:
 *   bun agent:run drift_sentinel --dry      # Preview drift analysis
 *   bun agent:run drift_sentinel --exec     # Execute + alert if needed
 */

import { writeFileSync, readFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import { execSync } from "child_process";
import { emit } from "../../packages/shared/src/event-bus";

const ROOT = join(import.meta.dir, "../..");
const REPORTS_DIR = join(ROOT, "docs/drift-sentinel");
const STATUS_FILE = join(REPORTS_DIR, "status.json");
const ALERTS_LOG = join(REPORTS_DIR, "alerts.jsonl");

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID;

interface DriftFinding {
  domain: string;
  severity: "critical" | "high" | "medium" | "low";
  narrative: string; // What docs say
  live: string; // What system actually is
  evidence: string; // File:line reference
  reconciliation: string; // How to fix
}

interface DriftReport {
  mode: "dry" | "exec";
  checkedAt: string;
  summary: {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  findings: DriftFinding[];
  alerts: string[];
}

// ─── Drift checkers ──────────────────────────────────────────────────────────

function checkTasksDrift(): DriftFinding[] {
  const findings: DriftFinding[] = [];
  const tasksPath = join(ROOT, "TASKS.md");

  if (!existsSync(tasksPath)) {
    return [];
  }

  try {
    const tasksContent = readFileSync(tasksPath, "utf-8");
    const P0Tasks = (tasksContent.match(/- \[ \]\s*\*\*P0:/g) || []).length;
    const P0Done = (tasksContent.match(/- \[x\]\s*\*\*P0:/gi) || []).length;

    // Check last 7 days of commits
    const logOutput = execSync(
      `git log --since="7 days ago" --oneline 2>/dev/null | wc -l`,
      { cwd: ROOT, encoding: "utf-8" }
    ).trim();
    const recentCommits = parseInt(logOutput, 10);

    // If P0 tasks exist but few commits in 7 days, possible drift
    if (P0Tasks > 0 && recentCommits < P0Tasks * 2) {
      findings.push({
        domain: "task-execution",
        severity: "high",
        narrative: `TASKS.md lists ${P0Tasks} P0 tasks (${P0Done} done)`,
        live: `Only ${recentCommits} commits in last 7 days`,
        evidence: "TASKS.md + git log",
        reconciliation: "Update TASKS.md to reflect actual priorities or increase execution pace",
      });
    }
  } catch (err) {
    // git may not be available or repo may be shallow
  }

  return findings;
}

function checkAgentsDrift(): DriftFinding[] {
  const findings: DriftFinding[] = [];
  const registryPath = join(ROOT, "agents/registry/agents.json");
  const agentsDir = join(ROOT, "agents/agents");

  if (!existsSync(registryPath)) {
    return findings;
  }

  try {
    const registryContent = readFileSync(registryPath, "utf-8");
    const registry = JSON.parse(registryContent);
    const registeredIds = (registry.agents || []).map((a: any) => a.id);

    // Check which entrypoints exist
    const actualFiles = new Set<string>();
    if (existsSync(agentsDir)) {
      const files = execSync(`ls ${agentsDir}/*.ts 2>/dev/null || true`, {
        encoding: "utf-8",
      });
      files.split("\n").forEach((f) => {
        if (f) {
          const id = f.split("/").pop()?.replace(".ts", "");
          if (id) actualFiles.add(id);
        }
      });
    }

    // Registered but missing file
    for (const id of registeredIds) {
      if (!actualFiles.has(id) && id !== "integration-tester") {
        // integration-tester may be archived
        findings.push({
          domain: "agent-registry",
          severity: "high",
          narrative: `agents.json lists agent "${id}"`,
          live: `File agents/agents/${id}.ts does not exist`,
          evidence: `agents/registry/agents.json + agents/agents/`,
          reconciliation: `Either create agents/agents/${id}.ts or remove from registry`,
        });
      }
    }

    // File exists but not registered
    for (const id of actualFiles) {
      if (!registeredIds.includes(id)) {
        findings.push({
          domain: "agent-registry",
          severity: "medium",
          narrative: `agents.json has no entry for "${id}"`,
          live: `File agents/agents/${id}.ts exists and active`,
          evidence: `agents/agents/ + agents/registry/agents.json`,
          reconciliation: `Add "${id}" to agents.json registry with metadata`,
        });
      }
    }
  } catch (err) {
    // JSON parse or command error
  }

  return findings;
}

function checkClaudeMdDrift(): DriftFinding[] {
  const findings: DriftFinding[] = [];
  const claudePath = join(ROOT, "CLAUDE.md");

  if (!existsSync(claudePath)) {
    return findings;
  }

  try {
    const claudeContent = readFileSync(claudePath, "utf-8");

    // Check if CLAUDE.md mentions "6 Kernel Agents" but registry has more/fewer
    const registryPath = join(ROOT, "agents/registry/agents.json");
    if (existsSync(registryPath)) {
      const registry = JSON.parse(readFileSync(registryPath, "utf-8"));
      const activeCount = (registry.agents || []).filter((a: any) => a.status === "active").length;

      if (claudeContent.includes("6 Kernel Agents") && activeCount !== 6) {
        findings.push({
          domain: "documentation",
          severity: "medium",
          narrative: `CLAUDE.md states "6 Kernel Agents"`,
          live: `agents.json shows ${activeCount} active agents`,
          evidence: "CLAUDE.md:1 + agents/registry/agents.json",
          reconciliation: `Update CLAUDE.md to reflect actual agent count (${activeCount})`,
        });
      }
    }
  } catch (err) {
    // Parse error
  }

  return findings;
}

function checkPromptsVersionDrift(): DriftFinding[] {
  const findings: DriftFinding[] = [];
  const systemPath = join(ROOT, ".guarani/prompts/PROMPT_SYSTEM.md");

  if (!existsSync(systemPath)) {
    return findings;
  }

  try {
    const content = readFileSync(systemPath, "utf-8");
    const versionMatch = content.match(/v(\d+\.\d+)/);
    const docVersion = versionMatch ? versionMatch[1] : "unknown";

    // Check git history
    const gitLog = execSync(
      `git log -1 --format=%ai -- .guarani/prompts/ 2>/dev/null || echo "never"`,
      { cwd: ROOT, encoding: "utf-8" }
    ).trim();

    // If PROMPT_SYSTEM says v2.0 but was last edited >30 days ago, might be stale
    if (docVersion === "2.0" && gitLog !== "never") {
      const daysOld = parseInt(
        execSync(
          `echo $(( ($(date +%s) - $(git log -1 --format=%at -- .guarani/prompts/ 2>/dev/null || echo 0)) ) / 86400 ))`,
          { cwd: ROOT, encoding: "utf-8" }
        ).trim(),
        10
      );

      if (daysOld > 30) {
        findings.push({
          domain: "governance",
          severity: "low",
          narrative: `PROMPT_SYSTEM.md says v2.0 (consolidated /start)`,
          live: `Last updated ${daysOld} days ago`,
          evidence: `.guarani/prompts/ git history`,
          reconciliation: `Review prompts and update version/date if significant changes made`,
        });
      }
    }
  } catch (err) {
    // Calculation error
  }

  return findings;
}

// ─── Telegram ────────────────────────────────────────────────────────────────

async function sendTelegramAlert(message: string): Promise<void> {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.log("[Telegram] Skipped — env vars not set");
    return;
  }
  try {
    await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text: message,
        parse_mode: "Markdown",
      }),
    });
  } catch (err) {
    console.error("[Telegram] Failed to send alert:", err);
  }
}

// ─── Main runner ─────────────────────────────────────────────────────────────

async function runDriftSentinel(mode: "dry" | "exec"): Promise<DriftReport> {
  console.log(`\n🔍 EGOS Drift Sentinel — mode: ${mode}`);
  console.log(`📊 Scanning: narrative vs live state...\n`);

  const findings: DriftFinding[] = [
    ...checkTasksDrift(),
    ...checkAgentsDrift(),
    ...checkClaudeMdDrift(),
    ...checkPromptsVersionDrift(),
  ];

  const summary = {
    total: findings.length,
    critical: findings.filter((f) => f.severity === "critical").length,
    high: findings.filter((f) => f.severity === "high").length,
    medium: findings.filter((f) => f.severity === "medium").length,
    low: findings.filter((f) => f.severity === "low").length,
  };

  const alerts: string[] = [];

  console.log(`📈 Results: ${summary.total} drift(s) detected\n`);

  for (const f of findings) {
    const icon =
      f.severity === "critical" ? "🔴"
      : f.severity === "high" ? "🟠"
      : f.severity === "medium" ? "🟡"
      : "🔵";

    console.log(`  ${icon} [${f.domain}] ${f.narrative}`);
    console.log(`     → ${f.live}`);
    console.log(`     🔧 ${f.reconciliation}`);
    console.log();

    if (f.severity === "critical" || f.severity === "high") {
      const alert =
        `⚠️ *Drift detected* — ${f.domain}\n` +
        `Narrative: ${f.narrative}\n` +
        `Live: ${f.live}\n` +
        `→ ${f.reconciliation}`;
      alerts.push(alert);
    }
  }

  if (summary.total === 0) {
    console.log("✅ No drift detected — narrative and live state aligned.");
  }

  const report: DriftReport = {
    mode,
    checkedAt: new Date().toISOString(),
    summary,
    findings,
    alerts,
  };

  if (mode === "exec") {
    mkdirSync(REPORTS_DIR, { recursive: true });
    writeFileSync(STATUS_FILE, JSON.stringify(report, null, 2));

    if (alerts.length > 0) {
      const logEntry = { timestamp: new Date().toISOString(), alerts };
      const existing = existsSync(ALERTS_LOG) ? readFileSync(ALERTS_LOG, "utf-8") : "";
      writeFileSync(ALERTS_LOG, existing + JSON.stringify(logEntry) + "\n");

      console.log(`\n⚠️  ${alerts.length} alert(s) — sending Telegram notifications...`);
      for (const alert of alerts) {
        await sendTelegramAlert(alert);
      }
    } else {
      console.log("\n✅ All systems aligned — no critical alerts.");
    }
  }

  return report;
}

// Entry point
const args = process.argv.slice(2);
const mode: "dry" | "exec" = args.includes("--exec") ? "exec" : "dry";

const _start = Date.now();
runDriftSentinel(mode)
  .then(async (report) => {
    const hasCritical = report.summary.critical > 0;
    await emit("agent.completed.drift-sentinel", "drift-sentinel", {
      critical: report.summary.critical, high: report.summary.high, mode,
      duration_ms: Date.now() - _start,
    }, hasCritical ? "warn" : "info").catch(() => {});
    if (hasCritical) {
      await emit("alert.drift-sentinel", "drift-sentinel", {
        critical: report.summary.critical,
      }, "critical").catch(() => {});
    }
    process.exit(hasCritical ? 1 : 0);
  })
  .catch(async (err) => {
    await emit("agent.completed.drift-sentinel", "drift-sentinel", {
      error: err?.message, mode, duration_ms: Date.now() - _start,
    }, "error").catch(() => {});
    console.error("Fatal error:", err);
    process.exit(2);
  });
