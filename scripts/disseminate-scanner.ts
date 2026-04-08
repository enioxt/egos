#!/usr/bin/env bun
/**
 * scripts/disseminate-scanner.ts — EGOS Kernel Change Scanner (DISS-001)
 *
 * Reads git diff on kernel governance files, extracts which sections changed,
 * and generates a propagation manifest for disseminate-propagator.ts.
 *
 * Usage:
 *   bun scripts/disseminate-scanner.ts [--dry] [--since <commit>]
 *
 * Output:
 *   .egos-disseminate-manifest.json  (or stdout if --stdout)
 *   Exit 0: no changes needed
 *   Exit 1: changes found (manifest written)
 */

import { execSync } from "node:child_process";
import { existsSync, writeFileSync, readFileSync } from "node:fs";
import { join, resolve, dirname } from "node:path";

// ── Config ──────────────────────────────────────────────────────────────────

const HOME = process.env.HOME ?? "/home/enio";
const REPO_ROOT = resolve(dirname(import.meta.path), "..");

const KERNEL_FILES: KernelFile[] = [
  {
    path: join(HOME, ".claude/CLAUDE.md"),
    label: "global-claude-md",
    description: "Global user CLAUDE.md (all projects)",
    // Note: this file lives outside the git repo — we track it separately
    tracked_in_repo: false,
  },
  {
    path: join(REPO_ROOT, ".windsurfrules"),
    label: "windsurfrules",
    description: "Project governance rules (.windsurfrules)",
    tracked_in_repo: true,
  },
  {
    path: join(REPO_ROOT, "CLAUDE.md"),
    label: "project-claude-md",
    description: "Project CLAUDE.md adapter",
    tracked_in_repo: true,
  },
  {
    path: join(REPO_ROOT, "docs/CAPABILITY_REGISTRY.md"),
    label: "capability-registry",
    description: "Capability registry",
    tracked_in_repo: true,
  },
];

const AFFECTED_REPOS: string[] = [
  join(HOME, "852"),
  join(HOME, "br-acc"),
  join(HOME, "carteira-livre"),
  join(HOME, "egos-inteligencia"),
  join(HOME, "egos-lab"),
  join(HOME, "forja"),
  join(HOME, "smartbuscas"),
  join(HOME, "santiago"),
  join(HOME, "commons"),
  join(HOME, "arch"),
  join(HOME, "egos-self"),
  join(HOME, "INPI"),
];

const MANIFEST_PATH = join(REPO_ROOT, ".egos-disseminate-manifest.json");

// ── Types ────────────────────────────────────────────────────────────────────

interface KernelFile {
  path: string;
  label: string;
  description: string;
  tracked_in_repo: boolean;
}

interface ChangedRule {
  file: string;
  label: string;
  section: string;
  change_type: "added" | "modified" | "removed";
  diff_lines: number;
}

interface DisseminateManifest {
  date: string;
  commit: string;
  since_commit: string;
  changed_rules: ChangedRule[];
  affected_repos: string[];
  existing_repos: string[];
  propagation_needed: boolean;
  generated_at: string;
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function run(cmd: string, cwd?: string): string {
  try {
    return execSync(cmd, {
      cwd: cwd ?? REPO_ROOT,
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();
  } catch {
    return "";
  }
}

function extractChangedSections(diff: string, filePath: string): ChangedRule[] {
  const rules: ChangedRule[] = [];
  if (!diff) return rules;

  const lines = diff.split("\n");
  let currentSection = "(preamble)";
  let addedLines = 0;
  let removedLines = 0;

  for (const line of lines) {
    // Detect markdown headings in diff context
    if (line.match(/^[+ ]#+\s+/)) {
      // Save previous section if it had changes
      if (addedLines > 0 || removedLines > 0) {
        rules.push({
          file: filePath,
          label: filePath.split("/").pop() ?? filePath,
          section: currentSection,
          change_type: addedLines > 0 && removedLines > 0 ? "modified" : addedLines > 0 ? "added" : "removed",
          diff_lines: addedLines + removedLines,
        });
        addedLines = 0;
        removedLines = 0;
      }
      // Extract the heading text
      currentSection = line.replace(/^[+ ]/, "").trim();
    } else if (line.startsWith("+") && !line.startsWith("+++")) {
      addedLines++;
    } else if (line.startsWith("-") && !line.startsWith("---")) {
      removedLines++;
    }
  }

  // Flush last section
  if (addedLines > 0 || removedLines > 0) {
    rules.push({
      file: filePath,
      label: filePath.split("/").pop() ?? filePath,
      section: currentSection,
      change_type: addedLines > 0 && removedLines > 0 ? "modified" : addedLines > 0 ? "added" : "removed",
      diff_lines: addedLines + removedLines,
    });
  }

  return rules;
}

function getFileDiff(filePath: string, sinceCommit: string, isTrackedInRepo: boolean): string {
  if (!existsSync(filePath)) return "";

  if (isTrackedInRepo) {
    // Standard git diff for tracked files
    return run(`git diff ${sinceCommit} -- "${filePath}"`);
  } else {
    // For global CLAUDE.md outside the repo: compare to git-stashed version
    // Check if we have a cached version to compare against
    const cacheFile = join(REPO_ROOT, ".egos-kernel-cache", "global-claude-md.md");
    if (!existsSync(cacheFile)) {
      // First run: no cache exists, treat as "added"
      return `+++ (new baseline — no previous cache)`;
    }
    const cached = readFileSync(cacheFile, "utf-8");
    const current = readFileSync(filePath, "utf-8");
    if (cached === current) return "";
    // Simple line-diff approximation
    const cachedLines = new Set(cached.split("\n"));
    const currentLines = current.split("\n");
    const added = currentLines.filter((l) => !cachedLines.has(l)).length;
    return added > 0 ? `+++ (${added} lines changed vs cache)` : "";
  }
}

function updateGlobalClaudeCache(filePath: string): void {
  const cacheDir = join(REPO_ROOT, ".egos-kernel-cache");
  const cacheFile = join(cacheDir, "global-claude-md.md");
  run(`mkdir -p "${cacheDir}"`);
  try {
    const content = readFileSync(filePath, "utf-8");
    writeFileSync(cacheFile, content);
  } catch {
    // Non-fatal
  }
}

// ── Main ─────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const isDry = args.includes("--dry");
const toStdout = args.includes("--stdout");
const sinceIdx = args.indexOf("--since");
const sinceCommit = sinceIdx >= 0 ? (args[sinceIdx + 1] ?? "HEAD~1") : "HEAD~1";

const currentCommit = run("git rev-parse --short HEAD");
const date = new Date().toISOString().split("T")[0];

console.log(`[disseminate-scanner] commit=${currentCommit} since=${sinceCommit} date=${date}`);

// Collect changed rules across all kernel files
const allChangedRules: ChangedRule[] = [];

for (const kf of KERNEL_FILES) {
  if (!existsSync(kf.path)) {
    console.warn(`  ⚠️  Kernel file not found: ${kf.path}`);
    continue;
  }

  const diff = getFileDiff(kf.path, sinceCommit, kf.tracked_in_repo);
  if (!diff) {
    console.log(`  ✅ ${kf.label}: no changes`);
    continue;
  }

  const rules = extractChangedSections(diff, kf.path);
  if (rules.length === 0) {
    console.log(`  ✅ ${kf.label}: diff exists but no section headers detected`);
    continue;
  }

  console.log(`  🔄 ${kf.label}: ${rules.length} section(s) changed`);
  for (const r of rules) {
    console.log(`     - ${r.section} (${r.change_type}, +${r.diff_lines} lines)`);
  }
  allChangedRules.push(...rules);
}

// Filter affected repos (only existing ones)
const existingRepos = AFFECTED_REPOS.filter((r) => existsSync(r));
const missingRepos = AFFECTED_REPOS.filter((r) => !existsSync(r));

if (missingRepos.length > 0) {
  console.log(`  ℹ️  Missing repos (skipped): ${missingRepos.map((r) => r.split("/").pop()).join(", ")}`);
}

const propagationNeeded = allChangedRules.length > 0;

const manifest: DisseminateManifest = {
  date,
  commit: currentCommit,
  since_commit: sinceCommit,
  changed_rules: allChangedRules,
  affected_repos: AFFECTED_REPOS,
  existing_repos: existingRepos,
  propagation_needed: propagationNeeded,
  generated_at: new Date().toISOString(),
};

if (propagationNeeded) {
  console.log(`\n🔴 Propagation needed: ${allChangedRules.length} rule section(s) changed across ${existingRepos.length} repos`);
} else {
  console.log(`\n✅ No propagation needed — kernel files unchanged since ${sinceCommit}`);
}

if (isDry) {
  console.log("\n[DRY-RUN] Manifest (not written):");
  console.log(JSON.stringify(manifest, null, 2));
  process.exit(propagationNeeded ? 1 : 0);
}

if (toStdout) {
  console.log(JSON.stringify(manifest, null, 2));
} else {
  writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2));
  console.log(`\n📄 Manifest written: ${MANIFEST_PATH}`);

  // Update cache for global CLAUDE.md (untracked file)
  const globalClaude = KERNEL_FILES.find((f) => f.label === "global-claude-md");
  if (globalClaude && existsSync(globalClaude.path)) {
    updateGlobalClaudeCache(globalClaude.path);
  }
}

process.exit(propagationNeeded ? 1 : 0);
