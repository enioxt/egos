#!/usr/bin/env bun
/**
 * scripts/codebase-miner.ts — EGOS Codebase Archaeology Agent (ARCH-001)
 *
 * Phase 1: Scan all EGOS repos for TODO/FIXME/HACK/XXX/WIP markers in .ts/.py/.md files.
 *          Generates report docs/jobs/codebase-mining-YYYY-MM-DD.md
 *          Sends Telegram summary if markers found.
 *
 * Phase 2: Detect stale .md files (updated: > 90 days, referenced in code).
 *
 * Phase 3 (--concepts): Detect concept mentions without implementation.
 *
 * Usage:
 *   bun scripts/codebase-miner.ts              # Phase 1 (default)
 *   bun scripts/codebase-miner.ts --phase2     # Phase 1 + stale docs
 *   bun scripts/codebase-miner.ts --all        # All phases
 *   bun scripts/codebase-miner.ts --dry        # Print to stdout, no file write
 *   bun scripts/codebase-miner.ts --tg         # Send Telegram notification
 */

import { execSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync, readdirSync, statSync } from "node:fs";
import { join, extname, relative, basename } from "node:path";

// ── Config ──────────────────────────────────────────────────────────────────

const HOME = process.env.HOME ?? "/home/enio";
const EGOS_ROOT = join(HOME, "egos");
const DOCS_JOBS = join(EGOS_ROOT, "docs/jobs");

const REPOS = [
  join(HOME, "egos"),
  join(HOME, "egos-lab"),
  join(HOME, "852"),
  join(HOME, "forja"),
  join(HOME, "br-acc"),
  join(HOME, "carteira-livre"),
];

const EXTENSIONS = new Set([".ts", ".py", ".md"]);

const SKIP_DIRS = new Set([
  "node_modules", ".git", "dist", "build", ".next", "__pycache__",
  ".turbo", "coverage", ".cache", "tmp", "temp", "bun.lock",
  "venv", "venv_test", ".venv", "env",
  "site-packages", "lib", "Lib", // Python library dirs
  "vendor", "third_party", "extern", "deps",
  "migrations",
  ".archive", "archive", "archived", // archived workflows/docs
  "TASKS_ARCHIVE_2026.md", // not a dir but excluded from file walk
]);

const SKIP_FILE_PATTERNS = [
  /TASKS_ARCHIVE/,
  /_ARCHIVE/,
  /handoff_.*\.md$/, // session handoffs often have TODO in examples
];

const MARKERS = [
  { pattern: /\bTODO\b/, label: "TODO" },
  { pattern: /\bFIXME\b/, label: "FIXME" },
  { pattern: /\bHACK\b/, label: "HACK" },
  // XXX: require it to appear as a comment marker, not in placeholder IDs like "EGOS-XXX"
  { pattern: /(?:\/\/|#|<!--|\/\*)\s*XXX\b/, label: "XXX" },
  { pattern: /\bWIP\b/, label: "WIP" },
];

// Stale docs threshold: 90 days
const STALE_DAYS = 90;
const STALE_MS = STALE_DAYS * 24 * 60 * 60 * 1000;

const DRY = process.argv.includes("--dry");
const DO_PHASE2 = process.argv.includes("--phase2") || process.argv.includes("--all");
const DO_PHASE3 = process.argv.includes("--concepts") || process.argv.includes("--all");
const SEND_TG = process.argv.includes("--tg");

// ── Types ────────────────────────────────────────────────────────────────────

interface Finding {
  repo: string;
  file: string;
  line: number;
  marker: string;
  text: string;
}

interface StaleDoc {
  repo: string;
  file: string;
  daysSinceUpdate: number;
  referencedIn: string[];
}

// ── File scanner ─────────────────────────────────────────────────────────────

function scanFile(filePath: string, repoName: string): Finding[] {
  const findings: Finding[] = [];
  let content: string;
  try {
    content = readFileSync(filePath, "utf-8");
  } catch {
    return findings;
  }

  const lines = content.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const { pattern, label } of MARKERS) {
      if (pattern.test(line)) {
        findings.push({
          repo: repoName,
          file: filePath,
          line: i + 1,
          marker: label,
          text: line.trim().slice(0, 120),
        });
        break; // one finding per line
      }
    }
  }
  return findings;
}

function walkDir(dir: string, repoName: string): Finding[] {
  const findings: Finding[] = [];
  if (!existsSync(dir)) return findings;

  const entries = readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (SKIP_DIRS.has(entry.name)) continue;

    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      findings.push(...walkDir(fullPath, repoName));
    } else if (entry.isFile() && EXTENSIONS.has(extname(entry.name))) {
      if (SKIP_FILE_PATTERNS.some(p => p.test(entry.name) || p.test(fullPath))) continue;
      findings.push(...scanFile(fullPath, repoName));
    }
  }
  return findings;
}

// ── Phase 2: Stale docs ──────────────────────────────────────────────────────

function findStaleDocs(): StaleDoc[] {
  const staleDocs: StaleDoc[] = [];
  const now = Date.now();

  for (const repoPath of REPOS) {
    if (!existsSync(repoPath)) continue;
    const repoName = basename(repoPath);

    const docsDirs = [
      join(repoPath, "docs"),
      repoPath, // root .md files
    ];

    for (const dir of docsDirs) {
      if (!existsSync(dir)) continue;
      const entries = readdirSync(dir, { withFileTypes: true });

      for (const entry of entries) {
        if (!entry.isFile() || extname(entry.name) !== ".md") continue;
        const filePath = join(dir, entry.name);
        const stat = statSync(filePath);
        const ageMs = now - stat.mtimeMs;

        if (ageMs > STALE_MS) {
          const daysSinceUpdate = Math.floor(ageMs / (24 * 60 * 60 * 1000));
          // Check if this doc is referenced in .ts or .py files
          const docName = entry.name;
          const refsFound: string[] = [];
          try {
            const grepResult = execSync(
              `grep -rl "${docName}" "${repoPath}" --include="*.ts" --include="*.py" 2>/dev/null | head -3`,
              { encoding: "utf-8", timeout: 5000 }
            ).trim();
            if (grepResult) refsFound.push(...grepResult.split("\n").filter(Boolean));
          } catch {}

          if (refsFound.length > 0) {
            staleDocs.push({
              repo: repoName,
              file: relative(repoPath, filePath),
              daysSinceUpdate,
              referencedIn: refsFound.map(f => relative(repoPath, f)),
            });
          }
        }
      }
    }
  }

  return staleDocs.sort((a, b) => b.daysSinceUpdate - a.daysSinceUpdate);
}

// ── Report generator ─────────────────────────────────────────────────────────

function generateReport(findings: Finding[], staleDocs: StaleDoc[]): string {
  const date = new Date().toISOString().slice(0, 10);
  const now = new Date().toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" });

  // Group findings by repo
  const byRepo = new Map<string, Finding[]>();
  for (const f of findings) {
    const repoName = basename(f.repo);
    const existing = byRepo.get(repoName) ?? [];
    existing.push(f);
    byRepo.set(repoName, existing);
  }

  // Count by marker type
  const byMarker = new Map<string, number>();
  for (const f of findings) {
    byMarker.set(f.marker, (byMarker.get(f.marker) ?? 0) + 1);
  }

  const lines: string[] = [
    `# Codebase Mining Report — ${date}`,
    `> Generated: ${now} BRT | Repos: ${REPOS.length} | Phase 1: TODO/FIXME/HACK scan`,
    ``,
    `## Summary`,
    ``,
    `| Metric | Value |`,
    `|--------|-------|`,
    `| Total markers found | ${findings.length} |`,
    `| Repos scanned | ${REPOS.filter(r => existsSync(r)).length} |`,
    ...Array.from(byMarker.entries()).map(([m, c]) => `| ${m} | ${c} |`),
  ];

  if (DO_PHASE2 && staleDocs.length > 0) {
    lines.push(`| Stale docs referenced in code | ${staleDocs.length} |`);
  }

  // Findings by repo
  lines.push("", "## Findings by Repository", "");

  if (findings.length === 0) {
    lines.push("✅ No TODO/FIXME/HACK markers found across all repos.");
  } else {
    for (const [repoName, repoFindings] of Array.from(byRepo.entries()).sort()) {
      lines.push(`### ${repoName} (${repoFindings.length} markers)`, "");

      // Group by file
      const byFile = new Map<string, Finding[]>();
      for (const f of repoFindings) {
        const key = relative(f.repo, f.file);
        const existing = byFile.get(key) ?? [];
        existing.push(f);
        byFile.set(key, existing);
      }

      for (const [filePath, fileFindings] of Array.from(byFile.entries()).sort()) {
        lines.push(`**\`${filePath}\`** (${fileFindings.length})`);
        lines.push("```");
        for (const f of fileFindings) {
          lines.push(`  L${f.line} [${f.marker}] ${f.text}`);
        }
        lines.push("```", "");
      }
    }
  }

  // Stale docs section
  if (DO_PHASE2) {
    lines.push("## Phase 2: Stale Docs Referenced in Code", "");
    if (staleDocs.length === 0) {
      lines.push("✅ No stale referenced docs found.");
    } else {
      lines.push(`> Docs older than ${STALE_DAYS} days that are still imported/referenced in code.`, "");
      lines.push("| Repo | File | Days old | Referenced in |");
      lines.push("|------|------|----------|---------------|");
      for (const d of staleDocs.slice(0, 30)) {
        lines.push(`| ${d.repo} | \`${d.file}\` | ${d.daysSinceUpdate}d | \`${d.referencedIn.join(", ")}\` |`);
      }
    }
  }

  lines.push(
    "",
    "---",
    "",
    `*ARCH-001 | codebase-miner.ts | Next run: weekly CCR (ARCH-004)*`
  );

  return lines.join("\n");
}

// ── Telegram notification ─────────────────────────────────────────────────────

async function sendTelegram(findings: Finding[]): Promise<void> {
  const TG_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  const TG_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

  if (!TG_BOT_TOKEN || !TG_CHAT_ID) {
    console.warn("[codebase-miner] TG creds not set — skipping notification");
    return;
  }

  const byMarker = new Map<string, number>();
  for (const f of findings) {
    byMarker.set(f.marker, (byMarker.get(f.marker) ?? 0) + 1);
  }

  const markerSummary = Array.from(byMarker.entries())
    .map(([m, c]) => `• ${m}: ${c}`)
    .join("\n");

  const topItems = findings
    .slice(0, 5)
    .map(f => `  ${basename(f.repo)}/${relative(f.repo, f.file)}:${f.line} [${f.marker}]`)
    .join("\n");

  const msg = `🔍 *Codebase Mining Report*\n\n*${findings.length} markers found:*\n${markerSummary}\n\n*Top findings:*\n${topItems}\n\n📄 Full report: docs/jobs/`;

  const url = `https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage`;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: TG_CHAT_ID,
      text: msg,
      parse_mode: "Markdown",
    }),
  });
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  console.log("[codebase-miner] ARCH-001 — Phase 1: Scanning for TODO/FIXME/HACK/XXX/WIP...");

  const findings: Finding[] = [];
  for (const repoPath of REPOS) {
    if (!existsSync(repoPath)) {
      console.log(`  ⚠️  Repo not found: ${repoPath}`);
      continue;
    }
    const repoName = basename(repoPath);
    console.log(`  📂 Scanning ${repoName}...`);
    const found = walkDir(repoPath, repoPath);
    findings.push(...found);
    console.log(`     → ${found.length} markers`);
  }

  let staleDocs: StaleDoc[] = [];
  if (DO_PHASE2) {
    console.log("[codebase-miner] Phase 2: Scanning for stale referenced docs...");
    staleDocs = findStaleDocs();
    console.log(`  → ${staleDocs.length} stale docs found`);
  }

  const report = generateReport(findings, staleDocs);

  if (DRY) {
    console.log("\n" + report);
    return;
  }

  const date = new Date().toISOString().slice(0, 10);
  const outPath = join(DOCS_JOBS, `codebase-mining-${date}.md`);
  writeFileSync(outPath, report, "utf-8");
  console.log(`\n[codebase-miner] ✅ Report written: ${outPath}`);
  console.log(`  Total markers: ${findings.length}`);
  if (DO_PHASE2) console.log(`  Stale docs: ${staleDocs.length}`);

  if (SEND_TG && findings.length > 0) {
    await sendTelegram(findings);
    console.log("[codebase-miner] Telegram notification sent");
  }
}

main().catch(err => {
  console.error("[codebase-miner] Fatal:", err);
  process.exit(1);
});
