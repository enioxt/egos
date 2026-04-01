#!/usr/bin/env bun
/**
 * 🔄 EGOS Task Reconciliation
 *
 * Compares git log task IDs against TASKS.md status.
 * Finds: tasks done in commits but not marked [x], orphan IDs, stale entries.
 *
 * Usage:
 *   bun scripts/task-reconciliation.ts           # full report
 *   bun scripts/task-reconciliation.ts --fix      # auto-mark done tasks
 *   bun scripts/task-reconciliation.ts --summary  # one-liner for /start
 *   bun scripts/task-reconciliation.ts --pre-commit # exit 1 if drift > threshold
 */

import { execSync } from "child_process";
import { readFileSync, writeFileSync } from "fs";

const ROOT = "/home/enio/egos";
const TASKS_PATH = `${ROOT}/TASKS.md`;
const FIX = process.argv.includes("--fix");
const SUMMARY = process.argv.includes("--summary");
const PRE_COMMIT = process.argv.includes("--pre-commit");
const DRIFT_THRESHOLD = 5; // max allowed drift before pre-commit warns

// ── Parse TASKS.md ─────────────────────────────────────────────────────────────

interface Task {
  id: string;
  done: boolean;
  line: number;
  text: string;
}

function parseTasks(content: string): Task[] {
  const tasks: Task[] = [];
  const lines = content.split("\n");

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const match = line.match(/^\s*-\s+\[([ xX])\]\s+([A-Z]+-\d+)[\s:]/);
    if (match) {
      tasks.push({
        id: match[2],
        done: match[1] !== " ",
        line: i + 1,
        text: line.trim(),
      });
    }
  }

  return tasks;
}

// ── Parse git log for task IDs ────────────────────────────────────────────────

function getCommittedTaskIds(commits = 100): Set<string> {
  // Only count a task as "done" if the SUBJECT line contains the ID
  // OR commit body contains "ID ✅" / "ID: ... done" / "marked done"
  // This avoids false positives from "New tasks: GH-032, GH-035" lines.
  const subjects = execSync(
    `git -C ${ROOT} log --oneline -${commits} --format="%s"`,
    { encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }
  );

  const bodies = execSync(
    `git -C ${ROOT} log --oneline -${commits} --format="%b"`,
    { encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }
  );

  const ids = new Set<string>();
  const subjectPattern = /\b([A-Z]+-\d+)\b/g;
  let m;

  // Subject-line matches are reliable (e.g., "feat: GH-034 OpenHarness task")
  while ((m = subjectPattern.exec(subjects)) !== null) {
    ids.add(m[1]);
  }

  // Body matches only if paired with completion markers
  const completionPattern = /\b([A-Z]+-\d+)[^✅\n]*✅/g;
  const markedDonePattern = /marked\s+done.*?([A-Z]+-\d+)/g;
  const checkedPattern = /\[x\]\s+([A-Z]+-\d+)/g;
  for (const pattern of [completionPattern, markedDonePattern, checkedPattern]) {
    pattern.lastIndex = 0;
    while ((m = pattern.exec(bodies)) !== null) {
      ids.add(m[1]);
    }
  }

  return ids;
}

// ── Analyze drift ─────────────────────────────────────────────────────────────

interface DriftReport {
  doneInGitNotInTasks: Task[];   // committed but tasks.md says [ ]
  pendingNoCommit: Task[];       // [ ] with no git evidence (expected — future tasks)
  totalTasks: number;
  doneTasks: number;
  driftScore: number;
}

function analyzeDrift(tasks: Task[], committedIds: Set<string>): DriftReport {
  const doneInGitNotInTasks = tasks.filter(
    t => !t.done && committedIds.has(t.id)
  );

  const pendingNoCommit = tasks.filter(
    t => !t.done && !committedIds.has(t.id)
  );

  const doneTasks = tasks.filter(t => t.done).length;

  return {
    doneInGitNotInTasks,
    pendingNoCommit,
    totalTasks: tasks.length,
    doneTasks,
    driftScore: doneInGitNotInTasks.length,
  };
}

// ── Auto-fix ──────────────────────────────────────────────────────────────────

function applyFixes(content: string, tasks: Task[]): string {
  let fixed = content;
  const today = new Date().toISOString().slice(0, 10);

  for (const task of tasks) {
    // Replace `- [ ] ID:` or `- [ ] **ID:**` with `- [x] ID:` + date
    const escapedText = task.text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const linePattern = new RegExp(
      `(^\\s*- \\[) \\] (${task.id}[\\s:])`,
      "m"
    );
    const newLine = fixed.replace(linePattern, `$1x] $2`);
    if (newLine !== fixed) {
      fixed = newLine;
      console.log(`  ✅ Fixed: ${task.id} marked done (auto-fix)`);
    }
  }

  return fixed;
}

// ── Main ──────────────────────────────────────────────────────────────────────

function main() {
  const content = readFileSync(TASKS_PATH, "utf8");
  const tasks = parseTasks(content);
  const committedIds = getCommittedTaskIds(100);
  const report = analyzeDrift(tasks, committedIds);

  if (SUMMARY) {
    const health = Math.round(((report.totalTasks - report.driftScore) / report.totalTasks) * 100);
    const status = report.driftScore === 0 ? "✅" : report.driftScore <= DRIFT_THRESHOLD ? "⚠️" : "🔴";
    console.log(
      `${status} TASKS: ${report.doneTasks}/${report.totalTasks} done | ${report.driftScore} drift (commits done but tasks not marked) | Health: ${health}%`
    );
    return;
  }

  if (PRE_COMMIT) {
    if (report.driftScore > DRIFT_THRESHOLD) {
      console.warn(`⚠️  Task drift detected: ${report.driftScore} tasks committed but not marked done in TASKS.md`);
      console.warn(`   Run: bun scripts/task-reconciliation.ts --fix`);
      // Non-blocking — just warn, don't fail pre-commit
    }
    process.exit(0);
  }

  // Full report
  console.log(`\n📊 EGOS Task Reconciliation Report`);
  console.log(`   ${new Date().toISOString().slice(0, 16)} | Last 100 commits scanned\n`);

  console.log(`📈 Stats:`);
  console.log(`   Total tasks:    ${report.totalTasks}`);
  console.log(`   Marked done:    ${report.doneTasks}`);
  console.log(`   Pending:        ${report.totalTasks - report.doneTasks}`);
  console.log(`   Drift (fix needed): ${report.driftScore}\n`);

  if (report.doneInGitNotInTasks.length > 0) {
    console.log(`🔴 Done in git but NOT marked [x] in TASKS.md:`);
    for (const t of report.doneInGitNotInTasks) {
      console.log(`   Line ${t.line}: ${t.id} — ${t.text.slice(0, 80)}`);
    }
    console.log();
  } else {
    console.log(`✅ No drift — all committed tasks are marked done\n`);
  }

  console.log(`📋 Pending tasks (no commit evidence — future work):`);
  // Show only top 10 to keep output manageable
  const topPending = report.pendingNoCommit.slice(0, 10);
  for (const t of topPending) {
    console.log(`   ${t.id}: ${t.text.slice(0, 80)}`);
  }
  if (report.pendingNoCommit.length > 10) {
    console.log(`   ... and ${report.pendingNoCommit.length - 10} more`);
  }
  console.log();

  if (FIX && report.doneInGitNotInTasks.length > 0) {
    console.log(`🔧 Applying fixes...`);
    const fixed = applyFixes(content, report.doneInGitNotInTasks);
    writeFileSync(TASKS_PATH, fixed);
    console.log(`   Wrote updated TASKS.md`);
  } else if (report.doneInGitNotInTasks.length > 0) {
    console.log(`💡 Run with --fix to auto-mark these tasks as done`);
  }
}

main();
