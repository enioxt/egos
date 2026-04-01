#!/usr/bin/env bun
/**
 * AI Coverage Scanner — EGOS Ecosystem
 *
 * Scans all repos for AI/LLM calls and checks against docs/AI_COVERAGE_MAP.md.
 * Used in pre-commit hook to detect unregistered AI usage.
 *
 * Usage:
 *   bun scripts/ai-coverage-scan.ts           # check mode (exits 1 if stale)
 *   bun scripts/ai-coverage-scan.ts --check   # same as above
 *   bun scripts/ai-coverage-scan.ts --update  # update AI_COVERAGE_MAP.md summary table
 *   bun scripts/ai-coverage-scan.ts --dry-run # show findings without writing
 */

import { execSync } from "child_process";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { join } from "path";

const ROOT = "/home/enio";
const EGOS = join(ROOT, "egos");
const COVERAGE_FILE = join(EGOS, "docs/AI_COVERAGE_MAP.md");
const DRY_RUN = process.argv.includes("--dry-run");
const UPDATE = process.argv.includes("--update");

// ── AI call patterns to search for ───────────────────────────────────────────

const AI_PATTERNS = [
  "chatWithLLM",
  "openai\\.chat",
  "anthropic\\.messages",
  "gemini\\.generateContent",
  "fetch.*openrouter",
  "fetch.*dashscope",
  "fetch.*openai",
  "createMessage",
  "chat\\.completions\\.create",
  "openrouter\\.ai/api",
  "dashscope-intl\\.aliyuncs\\.com",
  "googleapis.*generativelanguage",
];

// ── Repos to scan ─────────────────────────────────────────────────────────────

const REPOS: { name: string; path: string; glob: string }[] = [
  { name: "egos/packages/shared", path: join(EGOS, "packages/shared/src"), glob: "**/*.ts" },
  { name: "egos-lab/eagle-eye", path: join(ROOT, "egos-lab/apps/eagle-eye/src"), glob: "**/*.ts" },
  { name: "egos-lab/agents", path: join(ROOT, "egos-lab/agents/agents"), glob: "**/*.ts" },
  { name: "852", path: join(ROOT, "852"), glob: "**/*.ts" },
  { name: "forja", path: join(ROOT, "forja"), glob: "**/*.ts" },
  { name: "br-acc", path: join(ROOT, "br-acc"), glob: "**/*.{ts,py}" },
  { name: "carteira-livre", path: join(ROOT, "carteira-livre"), glob: "**/*.ts" },
  { name: "smartbuscas", path: join(ROOT, "smartbuscas"), glob: "**/*.{ts,py}" },
];

// ── Scanner ───────────────────────────────────────────────────────────────────

interface RepoResult {
  name: string;
  files: string[];
  callCount: number;
  models: Set<string>;
}

function scanRepo(repo: { name: string; path: string; glob: string }): RepoResult {
  const result: RepoResult = { name: repo.name, files: [], callCount: 0, models: new Set() };

  if (!existsSync(repo.path)) return result;

  const pattern = AI_PATTERNS.join("|");
  try {
    const output = execSync(
      `rg -l "${pattern}" "${repo.path}" --glob "${repo.glob}" 2>/dev/null || true`,
      { encoding: "utf8" }
    ).trim();

    if (output) {
      result.files = output.split("\n").filter(Boolean);

      // Count individual calls
      const countOutput = execSync(
        `rg -c "${pattern}" "${repo.path}" --glob "${repo.glob}" 2>/dev/null | awk -F: '{sum+=$2} END{print sum}' || echo 0`,
        { encoding: "utf8" }
      ).trim();
      result.callCount = parseInt(countOutput || "0", 10);

      // Extract model names
      const modelOutput = execSync(
        `rg -o "(gemini-[\\w.\\-]+|gpt-[\\w.\\-]+|claude-[\\w.\\-]+|qwen[-_][\\w.\\-]+|llama[-_\\d.]+|qwq[-_\\w.]+)" "${repo.path}" --glob "${repo.glob}" 2>/dev/null | sort -u || true`,
        { encoding: "utf8" }
      ).trim();
      if (modelOutput) {
        for (const m of modelOutput.split("\n").filter(Boolean)) {
          result.models.add(m.trim());
        }
      }
    }
  } catch (_e) {
    // repo might not exist or rg not available
  }

  return result;
}

// ── Main ──────────────────────────────────────────────────────────────────────

function main() {
  console.log("🔍 AI Coverage Scanner — EGOS Ecosystem");
  console.log("═".repeat(60));

  const results: RepoResult[] = [];
  let totalFiles = 0;
  let totalCalls = 0;

  for (const repo of REPOS) {
    const r = scanRepo(repo);
    results.push(r);
    totalFiles += r.files.length;
    totalCalls += r.callCount;

    const status = r.files.length > 0 ? "✅" : "⬜";
    const modelList = r.models.size > 0 ? `[${[...r.models].slice(0, 3).join(", ")}${r.models.size > 3 ? "…" : ""}]` : "none";
    console.log(`  ${status} ${repo.name.padEnd(30)} ${r.files.length} files  ${r.callCount} calls  ${modelList}`);
  }

  console.log("─".repeat(60));
  console.log(`  Total: ${totalFiles} AI files, ${totalCalls} call sites`);

  // ── Check mode: verify coverage map is not stale ──────────────────────────
  if (!UPDATE && !DRY_RUN) {
    if (!existsSync(COVERAGE_FILE)) {
      console.error("\n❌ AI_COVERAGE_MAP.md not found! Run --update to create it.");
      process.exit(1);
    }
    const coverage = readFileSync(COVERAGE_FILE, "utf8");
    const mapDate = coverage.match(/Updated:\s*(\d{4}-\d{2}-\d{2})/)?.[1] ?? "unknown";
    const today = new Date().toISOString().slice(0, 10);

    // Check if any repo has MORE files than documented
    let stale = false;
    for (const r of results) {
      if (r.files.length === 0) continue;
      const escaped = r.name.replace(/\//g, "\\/");
      const mapMatch = coverage.match(new RegExp(`\\|.*${escaped}.*\\|\\s*(\\d+)\\s*\\|`));
      const mappedCount = mapMatch ? parseInt(mapMatch[1], 10) : 0;
      if (r.files.length > mappedCount + 2) {
        console.warn(`\n⚠️  ${r.name}: ${r.files.length} AI files found, but map shows ${mappedCount}. Run --update.`);
        stale = true;
      }
    }

    if (stale) {
      console.error("\n❌ AI_COVERAGE_MAP.md is stale. Run: bun scripts/ai-coverage-scan.ts --update");
      process.exit(1);
    }

    console.log(`\n✅ AI_COVERAGE_MAP.md is current (last updated: ${mapDate})`);
    return;
  }

  // ── Update mode: rewrite summary table ───────────────────────────────────
  if (UPDATE || DRY_RUN) {
    const today = new Date().toISOString().slice(0, 10);

    // Build new summary table
    const tableRows = results.map(r => {
      const models = r.models.size > 0 ? [...r.models].slice(0, 3).join(", ") : "—";
      const cost = r.files.length === 0 ? "$0" : "~TBD";
      const status = r.files.length > 0 ? "✅ Active" : "⬜ None";
      return `| \`${r.name}\` | ${r.files.length} | ${models} | ${cost} | ${status} |`;
    }).join("\n");

    const newTable = `| Repo | AI Files | Models Used | Est. Cost/mo | Status |
|------|----------|-------------|--------------|--------|
${tableRows}

**Total ecosystem AI files:** ~${totalFiles} | **Est. total cost/mo:** ~$20–40 USD`;

    if (!existsSync(COVERAGE_FILE)) {
      console.error("❌ AI_COVERAGE_MAP.md not found. Cannot update.");
      process.exit(1);
    }

    const content = readFileSync(COVERAGE_FILE, "utf8");

    // Update version line
    const updated = content
      .replace(/Updated:\s*[\d-]+/, `Updated: ${today}`)
      .replace(
        /\| Repo \| AI Files.*?\n\*\*Total ecosystem.*?\*\*/s,
        newTable
      );

    if (DRY_RUN) {
      console.log("\n📋 Dry run — would write:");
      console.log(newTable);
    } else {
      writeFileSync(COVERAGE_FILE, updated, "utf8");
      console.log(`\n✅ AI_COVERAGE_MAP.md updated (${today})`);
    }
  }
}

main();
