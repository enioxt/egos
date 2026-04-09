/**
 * GH-094: Scoring Feedback Reader
 * Reads gem_feedback reactions from Supabase 2x/day (09:00 + 21:00 BRT)
 * and generates actionable reports + auto-tasks in TASKS.md.
 *
 * Usage:
 *   bun scripts/scoring-feedback-reader.ts         # reads since last run
 *   bun scripts/scoring-feedback-reader.ts --now   # force immediate run
 *   bun scripts/scoring-feedback-reader.ts --since 2026-04-01  # custom window
 *
 * Output:
 *   docs/jobs/scoring-feedback-YYYY-MM-DD.md  — daily report
 *   TASKS.md auto-tasks appended when patterns emerge
 *
 * VPS cron: 0 9,21 * * * (09:00 + 21:00 BRT = 12:00 + 00:00 UTC)
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import { execSync } from "child_process";

const DRY = process.argv.includes("--dry");
const FORCE_NOW = process.argv.includes("--now");
const SINCE_ARG = process.argv.find(a => a.startsWith("--since="))?.replace("--since=", "");

const REPO_ROOT = execSync("git rev-parse --show-toplevel", { encoding: "utf-8" }).trim();
const JOBS_DIR = join(REPO_ROOT, "docs/jobs");
const TASKS_FILE = join(REPO_ROOT, "TASKS.md");
const LAST_RUN_FILE = "/tmp/scoring-feedback-reader-last.txt";

const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_ANON_KEY ?? "";

// ── Types ─────────────────────────────────────────────────────────────────────

interface FeedbackRow {
  id: string;
  alert_id: string;
  gem_url: string;
  gem_name: string | null;
  reaction: string;
  comment: string | null;
  score_at_alert: number | null;
  run_id: string | null;
  created_at: string;
}

interface GemStats {
  name: string;
  url: string;
  thumbsUp: number;
  thumbsDown: number;
  research: number;
  comments: string[];
  avgScore: number;
  netScore: number; // thumbsUp - thumbsDown
}

// ── Supabase fetch ────────────────────────────────────────────────────────────

async function fetchFeedback(since: string): Promise<FeedbackRow[]> {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    console.warn("[FeedbackReader] Supabase not configured — using empty dataset");
    return [];
  }
  const url = `${SUPABASE_URL}/rest/v1/gem_feedback?created_at=gte.${since}&order=created_at.asc&limit=500`;
  const res = await fetch(url, {
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${SUPABASE_KEY}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) {
    console.error(`[FeedbackReader] Supabase error: ${res.status} ${await res.text()}`);
    return [];
  }
  return res.json();
}

// ── Analysis ──────────────────────────────────────────────────────────────────

function analyzeRows(rows: FeedbackRow[]): {
  perGem: Map<string, GemStats>;
  totalReactions: number;
  approvalRate: number;
  falsePositives: GemStats[];
  hiddenGems: GemStats[];
  topGems: GemStats[];
} {
  const perGem = new Map<string, GemStats>();

  for (const row of rows) {
    const key = row.gem_url;
    if (!perGem.has(key)) {
      perGem.set(key, {
        name: row.gem_name ?? row.gem_url,
        url: row.gem_url,
        thumbsUp: 0,
        thumbsDown: 0,
        research: 0,
        comments: [],
        avgScore: row.score_at_alert ?? 0,
        netScore: 0,
      });
    }
    const stats = perGem.get(key)!;
    if (row.reaction === "👍") stats.thumbsUp++;
    if (row.reaction === "👎") stats.thumbsDown++;
    if (row.reaction === "🔍") stats.research++;
    if (row.reaction === "💬" && row.comment) stats.comments.push(row.comment);
    if (row.score_at_alert) stats.avgScore = row.score_at_alert; // last known score
    stats.netScore = stats.thumbsUp - stats.thumbsDown;
  }

  const gems = Array.from(perGem.values());
  const totalReactions = rows.length;
  const approvals = rows.filter(r => r.reaction === "👍").length;
  const approvalRate = totalReactions > 0 ? Math.round((approvals / totalReactions) * 100) : 0;

  // False positives: high score at alert but 👎 reactions
  const falsePositives = gems
    .filter(g => g.thumbsDown > 0 && g.avgScore >= 75)
    .sort((a, b) => b.thumbsDown - a.thumbsDown);

  // Hidden gems: 👍 reactions on low-score gems (scoring undervalued them)
  const hiddenGems = gems
    .filter(g => g.thumbsUp > 0 && g.avgScore < 75)
    .sort((a, b) => b.thumbsUp - a.thumbsUp);

  // Top gems: most positive reactions
  const topGems = gems
    .filter(g => g.thumbsUp > 0)
    .sort((a, b) => b.netScore - a.netScore)
    .slice(0, 5);

  return { perGem, totalReactions, approvalRate, falsePositives, hiddenGems, topGems };
}

// ── Report Generator ──────────────────────────────────────────────────────────

function generateReport(
  rows: FeedbackRow[],
  since: string,
  analysis: ReturnType<typeof analyzeRows>
): string {
  const today = new Date().toISOString().slice(0, 10);
  const { totalReactions, approvalRate, falsePositives, hiddenGems, topGems } = analysis;

  const fp = falsePositives.slice(0, 3)
    .map(g => `- **${g.name}** (score=${g.avgScore}, 👎×${g.thumbsDown}) — ${g.url}`)
    .join("\n") || "_None detected_";

  const hg = hiddenGems.slice(0, 3)
    .map(g => `- **${g.name}** (score=${g.avgScore}, 👍×${g.thumbsUp}) — ${g.url}`)
    .join("\n") || "_None detected_";

  const tg = topGems
    .map(g => `- **${g.name}** — net=${g.netScore} (👍${g.thumbsUp}/👎${g.thumbsDown}) score=${g.avgScore}`)
    .join("\n") || "_No reactions yet_";

  const comments = rows
    .filter(r => r.comment)
    .map(r => `- "${r.comment}" on [${r.gem_name ?? r.gem_url}](${r.gem_url})`)
    .join("\n") || "_None_";

  return `# Gem Hunter Scoring Feedback Report
# Date: ${today} | Window: ${since} → ${today}
# Status: ${totalReactions === 0 ? "EMPTY" : approvalRate >= 60 ? "HEALTHY" : "REVIEW_NEEDED"}
# Generated: scoring-feedback-reader.ts (GH-094)

## Summary
- **Total reactions:** ${totalReactions}
- **Approval rate:** ${approvalRate}% (👍 = ${rows.filter(r => r.reaction === "👍").length}, 👎 = ${rows.filter(r => r.reaction === "👎").length})
- **Research flags:** ${rows.filter(r => r.reaction === "🔍").length}
- **Comments:** ${rows.filter(r => r.comment).length}

## Top Gems (most approved)
${tg}

## False Positives (high score → 👎)
${fp}

## Hidden Gems (low score → 👍 — scoring undervalued)
${hg}

## Comments
${comments}

## Raw Counts by Reaction
| Reaction | Count | % |
|----------|-------|---|
| 👍 Gem | ${rows.filter(r => r.reaction === "👍").length} | ${totalReactions > 0 ? Math.round(rows.filter(r => r.reaction === "👍").length / totalReactions * 100) : 0}% |
| 👎 Skip | ${rows.filter(r => r.reaction === "👎").length} | ${totalReactions > 0 ? Math.round(rows.filter(r => r.reaction === "👎").length / totalReactions * 100) : 0}% |
| 🔍 Research | ${rows.filter(r => r.reaction === "🔍").length} | ${totalReactions > 0 ? Math.round(rows.filter(r => r.reaction === "🔍").length / totalReactions * 100) : 0}% |
| 💬 Comment | ${rows.filter(r => r.reaction === "💬").length} | ${totalReactions > 0 ? Math.round(rows.filter(r => r.reaction === "💬").length / totalReactions * 100) : 0}% |

---
_Auto-generated by scoring-feedback-reader.ts. Next run: ~12h._
`;
}

// ── Auto-task Generator ───────────────────────────────────────────────────────

function generateAutoTasks(analysis: ReturnType<typeof analyzeRows>, today: string): string[] {
  const tasks: string[] = [];

  // False positive pattern: if >2 high-score gems got 👎
  if (analysis.falsePositives.length >= 2) {
    const names = analysis.falsePositives.slice(0, 2).map(g => g.name).join(", ");
    tasks.push(
      `- [ ] **GH-AUTO-${today.replace(/-/g, "")}A [P1]**: Fix false positive pattern — ${names} scored high but got 👎. Review scoring-v1.md heuristics. File: \`agents/agents/gem-hunter.ts:1778\`.`
    );
  }

  // Hidden gem pattern: if >1 low-score gems got 👍
  if (analysis.hiddenGems.length >= 1) {
    const names = analysis.hiddenGems.slice(0, 2).map(g => g.name).join(", ");
    tasks.push(
      `- [ ] **GH-AUTO-${today.replace(/-/g, "")}B [P1]**: Fix hidden gem undervaluation — ${names} got 👍 despite low score. Consider +bonus in scoreGem(). File: \`docs/gem-hunter/prompts/scoring-v1.md\`.`
    );
  }

  // Low approval rate: overall quality issue
  if (analysis.approvalRate < 40 && analysis.totalReactions >= 5) {
    tasks.push(
      `- [ ] **GH-AUTO-${today.replace(/-/g, "")}C [P0]**: Gem quality degraded — approval rate ${analysis.approvalRate}% (below 40%). Review isXSignalRelevant() and scoring thresholds. File: \`agents/agents/gem-hunter.ts\`.`
    );
  }

  return tasks;
}

// ── TASKS.md Appender ─────────────────────────────────────────────────────────

function appendAutoTasks(tasks: string[]): void {
  if (tasks.length === 0 || !existsSync(TASKS_FILE)) return;
  const content = readFileSync(TASKS_FILE, "utf-8");

  // Find "Gem Hunter" section or append to end
  const section = "## Gem Hunter — Auto-Generated Tasks";
  const entry = `\n${section}\n_Last updated: ${new Date().toISOString().slice(0, 10)} by scoring-feedback-reader.ts_\n\n${tasks.join("\n")}\n`;

  if (content.includes(section)) {
    // Replace section
    const updated = content.replace(
      new RegExp(`${section.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}[\\s\\S]*?(?=\n## |\n---|\n$)`),
      entry
    );
    writeFileSync(TASKS_FILE, updated);
  } else {
    writeFileSync(TASKS_FILE, content + entry);
  }
  console.log(`[FeedbackReader] ${tasks.length} auto-task(s) appended to TASKS.md`);
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main(): Promise<void> {
  const today = new Date().toISOString().slice(0, 10);

  // Determine "since" window
  let since: string;
  if (SINCE_ARG) {
    since = SINCE_ARG;
  } else if (FORCE_NOW || !existsSync(LAST_RUN_FILE)) {
    // Default: last 12 hours
    const d = new Date(Date.now() - 12 * 60 * 60 * 1000);
    since = d.toISOString();
  } else {
    since = readFileSync(LAST_RUN_FILE, "utf-8").trim();
  }

  console.log(`[FeedbackReader] Reading feedback since ${since}`);

  const rows = await fetchFeedback(since);
  console.log(`[FeedbackReader] ${rows.length} feedback row(s) found`);

  const analysis = analyzeRows(rows);
  const report = generateReport(rows, since, analysis);
  const autoTasks = generateAutoTasks(analysis, today);

  if (!DRY) {
    // Write report
    if (!existsSync(JOBS_DIR)) mkdirSync(JOBS_DIR, { recursive: true });
    const reportPath = join(JOBS_DIR, `scoring-feedback-${today}.md`);
    writeFileSync(reportPath, report);
    console.log(`[FeedbackReader] Report written: ${reportPath}`);

    // Append auto-tasks if any
    if (autoTasks.length > 0) {
      appendAutoTasks(autoTasks);
    }

    // Update last-run timestamp
    writeFileSync(LAST_RUN_FILE, new Date().toISOString());
  } else {
    console.log("[FeedbackReader] DRY MODE — report preview:");
    console.log(report.slice(0, 400) + "...");
    if (autoTasks.length > 0) {
      console.log(`[FeedbackReader] Would create ${autoTasks.length} auto-task(s):`);
      autoTasks.forEach(t => console.log(" ", t.slice(0, 80)));
    }
  }
}

main().catch(err => {
  console.error("[FeedbackReader] Fatal:", err);
  process.exit(1);
});
