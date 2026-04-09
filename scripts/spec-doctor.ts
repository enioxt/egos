#!/usr/bin/env bun
/**
 * spec-doctor.ts — SDD-005
 * Checks every feat/* git branch for a corresponding SPEC doc.
 *
 * Usage:
 *   bun scripts/spec-doctor.ts         # exits 1 if any MISSING
 *   bun scripts/spec-doctor.ts --dry   # just list, exit 0 always
 */

import { execSync } from "child_process";
import { existsSync } from "fs";
import { resolve } from "path";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const REPO_ROOT = resolve(import.meta.dir, "..");
const SPECS_DIR = "docs/specs";
const DRY = process.argv.includes("--dry");

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Convert a feat/* branch name to the expected SPEC filename.
 *  feat/guard-brasil-pii  →  docs/specs/SPEC-GUARD-BRASIL-PII.md
 */
function branchToSpecPath(branch: string): string {
  // strip remote prefix (origin/feat/...) and leading "feat/"
  const bare = branch
    .replace(/^[^/]+\//, "")   // strip "origin/"
    .replace(/^feat\//, "");    // strip "feat/"

  const slug = bare.toUpperCase().replace(/[^A-Z0-9]+/g, "-");
  return `${SPECS_DIR}/SPEC-${slug}.md`;
}

/** Run a shell command and return trimmed stdout. */
function run(cmd: string): string {
  return execSync(cmd, { cwd: REPO_ROOT, encoding: "utf8" }).trim();
}

/** Left-pad a string to a fixed width. */
function pad(s: string, width: number): string {
  return s.length >= width ? s : s + " ".repeat(width - s.length);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main(): void {
  // 1. List remote feat/* branches
  let rawBranches: string;
  try {
    rawBranches = run("git branch -r");
  } catch {
    console.error("ERROR: git branch -r failed. Are you in a git repo?");
    process.exit(1);
  }

  const featBranches = rawBranches
    .split("\n")
    .map((b) => b.trim())
    .filter((b) => /^(origin\/)?feat\//i.test(b))
    .filter((b) => !b.includes("->"));   // skip HEAD -> pointers

  if (featBranches.length === 0) {
    console.log("No feat/* branches found in remotes.");
    process.exit(0);
  }

  // 2. Build result rows
  type Row = { branch: string; specPath: string; exists: boolean };
  const rows: Row[] = featBranches.map((branch) => {
    const specPath = branchToSpecPath(branch);
    const absPath = resolve(REPO_ROOT, specPath);
    return { branch, specPath, exists: existsSync(absPath) };
  });

  // 3. Print table
  const COL1 = Math.max(30, ...rows.map((r) => r.branch.length)) + 2;
  const COL2 = Math.max(40, ...rows.map((r) => r.specPath.length)) + 2;

  const header = `${pad("BRANCH", COL1)}${pad("SPEC", COL2)}STATUS`;
  const separator = "-".repeat(header.length);

  console.log(header);
  console.log(separator);

  let missingCount = 0;
  for (const { branch, specPath, exists } of rows) {
    const status = exists ? "✅ exists" : "❌ MISSING";
    if (!exists) missingCount++;
    console.log(`${pad(branch, COL1)}${pad(specPath, COL2)}${status}`);
  }

  console.log(separator);
  console.log(
    `${rows.length} branch(es) checked — ${missingCount} MISSING spec(s).`
  );

  // 4. Exit code
  if (missingCount > 0 && !DRY) {
    process.exit(1);
  }
  process.exit(0);
}

main();
