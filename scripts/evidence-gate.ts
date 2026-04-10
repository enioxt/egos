#!/usr/bin/env bun
/**
 * Evidence Gate (§33 CLAUDE.md) — Warning-only on week 1, blocking on week 2+
 *
 * Purpose:
 *   Enforce "claim without proof = invalid claim" rule across EGOS kernel docs.
 *   Extends Doc-Drift Shield (§27) to cover capability claims in docs/products/,
 *   docs/agents/, and CAPABILITY_REGISTRY.md — not just .egos-manifest.yaml.
 *
 * Modes:
 *   warning  — default until 2026-04-16. Logs violations but exits 0.
 *   blocking — after 2026-04-16 for kernel docs. Exits 1 on violation.
 *
 * Usage:
 *   bun scripts/evidence-gate.ts [--mode warning|blocking] [--staged-only] [--file <path>]
 *
 * Integration:
 *   Called by .husky/pre-commit after existing doc-drift-verifier.
 *   Output log: docs/jobs/evidence-gate-YYYY-MM-DD.log
 *
 * SSOT: docs/strategy/EGOS_PATH_B_C_PLAN.md §1.1 Evidence-First Principle
 * Rule:  ~/.claude/CLAUDE.md §33
 */

import { execSync } from "child_process";
import { readFileSync, existsSync, appendFileSync, mkdirSync } from "fs";
import { join, dirname } from "path";

// ============================================================
// CONFIG — ACTIVATION SCHEDULE (from §33)
// ============================================================
const WEEK1_START = new Date("2026-04-09");
const WEEK2_START = new Date("2026-04-16"); // Blocking activates in kernel
const WEEK3_START = new Date("2026-04-23"); // Full blocking in kernel

const KERNEL_WATCHED_PATHS = [
  "docs/products/",
  "docs/agents/",
  "CAPABILITY_REGISTRY.md",
  "docs/CAPABILITY_REGISTRY.md",
];

const CLAIM_PATTERNS: Array<{ name: string; regex: RegExp }> = [
  { name: "numeric-metric", regex: /\b\d+(?:[.,]\d+)?\s*(ms|µs|us|s|%|req\/s|nós|nodes|commits|agents?|capabilities|padrões|patterns|tests?)\b/gi },
  { name: "ratio", regex: /\b\d+\/\d+\b/g },
  { name: "currency", regex: /R\$\s*\d+/g },
  { name: "version", regex: /\bv?\d+\.\d+\.\d+\b/g },
];

const EVIDENCE_MARKERS = [
  /<!--\s*evidence:\s*[\w-]+\s*-->/i,
  /\bEVIDENCE:\s*\n/,
  /\bproof:\s*/,
  /\.egos-manifest\.yaml/,
];

// ============================================================
// MODE RESOLUTION
// ============================================================
function resolveMode(cliMode: string | undefined): "warning" | "blocking" {
  if (cliMode === "warning" || cliMode === "blocking") return cliMode;
  const now = new Date();
  if (now < WEEK2_START) return "warning";
  return "blocking";
}

// ============================================================
// STAGED FILES
// ============================================================
function getStagedFiles(): string[] {
  try {
    const out = execSync("git diff --cached --name-only --diff-filter=ACM", { encoding: "utf-8" });
    return out.split("\n").filter(Boolean);
  } catch {
    return [];
  }
}

function isWatchedPath(path: string): boolean {
  return KERNEL_WATCHED_PATHS.some((p) => path === p || path.startsWith(p));
}

// ============================================================
// CLAIM DETECTION
// ============================================================
interface Violation {
  file: string;
  line: number;
  claim: string;
  claimType: string;
  reason: string;
}

function scanFile(path: string): Violation[] {
  if (!existsSync(path)) return [];
  const content = readFileSync(path, "utf-8");
  const lines = content.split("\n");
  const violations: Violation[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // Skip lines already marked as unverified or planned
    if (/unverified:|<!--\s*vocab-guard:\s*planned\s*-->/i.test(line)) continue;

    for (const { name, regex } of CLAIM_PATTERNS) {
      const matches = line.matchAll(regex);
      for (const match of matches) {
        // Check if evidence marker is present in the same line OR within 3 lines below
        const contextWindow = lines.slice(i, Math.min(i + 4, lines.length)).join("\n");
        const hasEvidence = EVIDENCE_MARKERS.some((m) => m.test(contextWindow));
        if (!hasEvidence) {
          violations.push({
            file: path,
            line: i + 1,
            claim: match[0],
            claimType: name,
            reason: "no evidence marker within 3 lines",
          });
        }
      }
    }
  }
  return violations;
}

// ============================================================
// LOGGING
// ============================================================
function logViolations(violations: Violation[], mode: string) {
  const logDir = "docs/jobs";
  if (!existsSync(logDir)) mkdirSync(logDir, { recursive: true });
  const date = new Date().toISOString().slice(0, 10);
  const logFile = join(logDir, `evidence-gate-${date}.log`);
  const timestamp = new Date().toISOString();
  const entry = {
    timestamp,
    mode,
    violation_count: violations.length,
    violations: violations.slice(0, 50), // cap to avoid log bloat
  };
  appendFileSync(logFile, JSON.stringify(entry) + "\n");
}

// ============================================================
// MAIN
// ============================================================
function main() {
  const args = process.argv.slice(2);
  const modeArg = args.find((a) => a.startsWith("--mode="))?.split("=")[1];
  const mode = resolveMode(modeArg);
  const fileArg = args.find((a) => a.startsWith("--file="))?.split("=")[1]
    ?? (args.indexOf("--file") !== -1 ? args[args.indexOf("--file") + 1] : null);
  const stagedOnly = !fileArg && (args.includes("--staged-only") || !args.includes("--file")); // default to staged

  let files: string[];
  if (fileArg) {
    files = [fileArg];
  } else if (stagedOnly) {
    files = getStagedFiles();
  } else {
    files = [];
  }
  const watched = files.filter(isWatchedPath);

  if (watched.length === 0) {
    // Nothing in scope — silent pass
    process.exit(0);
  }

  console.log(`[evidence-gate] mode=${mode} scanning ${watched.length} file(s)...`);

  const allViolations: Violation[] = [];
  for (const f of watched) {
    allViolations.push(...scanFile(f));
  }

  if (allViolations.length === 0) {
    console.log("[evidence-gate] ✅ all claims in scope have evidence markers");
    process.exit(0);
  }

  // Log regardless of mode
  logViolations(allViolations, mode);

  // Report
  console.log(`[evidence-gate] found ${allViolations.length} unbacked claim(s):`);
  for (const v of allViolations.slice(0, 10)) {
    console.log(`  - ${v.file}:${v.line} [${v.claimType}] "${v.claim}" — ${v.reason}`);
  }
  if (allViolations.length > 10) {
    console.log(`  ... and ${allViolations.length - 10} more (see docs/jobs/evidence-gate-*.log)`);
  }

  console.log("");
  console.log("  Fix options:");
  console.log("  1. Add <!-- evidence: <claim-id> --> pointing to a claim in .egos-manifest.yaml");
  console.log("  2. Add EVIDENCE: block in commit body with proof command + verified_at");
  console.log("  3. Mark the line with 'unverified:' prefix if genuinely aspirational");
  console.log("  4. Remove the claim if it cannot be backed by proof");

  if (mode === "blocking") {
    console.log("");
    console.log("❌ BLOCKED: Evidence-First mode is blocking. See §33 of ~/.claude/CLAUDE.md");
    process.exit(1);
  } else {
    console.log("");
    console.log("⚠️  WARNING mode — commit allowed but violations logged. Blocking activates 2026-04-16.");
    process.exit(0);
  }
}

main();
