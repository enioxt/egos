#!/usr/bin/env bun
/**
 * scripts/disseminate-verifier.ts — EGOS Kernel Propagation Verifier (DISS-003)
 *
 * Re-reads each repo after propagation, verifies the EGOS-KERNEL-PROPAGATED
 * marker exists and is up-to-date with the last manifest date.
 *
 * Usage:
 *   bun scripts/disseminate-verifier.ts [--dry] [--tg]
 *
 * Exit codes:
 *   0 — all repos verified
 *   1 — one or more repos missing/stale marker
 */

import { existsSync, readFileSync } from "node:fs";
import { join, resolve, dirname } from "node:path";

// ── Config ──────────────────────────────────────────────────────────────────

const HOME = process.env.HOME ?? "/home/enio";
const REPO_ROOT = resolve(dirname(import.meta.path), "..");
const MANIFEST_PATH = join(REPO_ROOT, ".egos-disseminate-manifest.json");
const MARKER_PREFIX = "# EGOS-KERNEL-PROPAGATED:";
const TARGET_FILES = ["CLAUDE.md", ".windsurfrules"];

const DRY = process.argv.includes("--dry");
const SEND_TG = process.argv.includes("--tg");

// ── Types ────────────────────────────────────────────────────────────────────

interface DisseminateManifest {
  date: string;
  commit: string;
  existing_repos: string[];
  propagation_needed: boolean;
}

interface RepoVerification {
  repo: string;
  path: string;
  status: "pass" | "fail" | "skip";
  marker_found: boolean;
  marker_date: string | null;
  expected_date: string;
  date_match: boolean;
  checked_files: string[];
  missing_rules: string[];
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function loadManifest(): DisseminateManifest | null {
  if (!existsSync(MANIFEST_PATH)) {
    console.error(`[verifier] Manifest not found: ${MANIFEST_PATH}`);
    console.error(`[verifier] Run: bun scripts/disseminate-scanner.ts first`);
    return null;
  }
  try {
    return JSON.parse(readFileSync(MANIFEST_PATH, "utf-8")) as DisseminateManifest;
  } catch (e) {
    console.error(`[verifier] Failed to parse manifest: ${e}`);
    return null;
  }
}

function extractMarkerDate(content: string): string | null {
  const lines = content.split("\n");
  for (const line of lines) {
    if (line.startsWith(MARKER_PREFIX)) {
      const date = line.replace(MARKER_PREFIX, "").trim();
      return date || null;
    }
  }
  return null;
}

function verifyRepo(repoPath: string, expectedDate: string): RepoVerification {
  const repoName = repoPath.split("/").pop() ?? repoPath;
  const result: RepoVerification = {
    repo: repoName,
    path: repoPath,
    status: "fail",
    marker_found: false,
    marker_date: null,
    expected_date: expectedDate,
    date_match: false,
    checked_files: [],
    missing_rules: [],
  };

  if (!existsSync(repoPath)) {
    result.status = "skip";
    result.missing_rules.push("repo path does not exist");
    return result;
  }

  for (const fileName of TARGET_FILES) {
    const filePath = join(repoPath, fileName);
    if (!existsSync(filePath)) continue;

    result.checked_files.push(fileName);
    const content = readFileSync(filePath, "utf-8");
    const markerDate = extractMarkerDate(content);

    if (markerDate) {
      result.marker_found = true;
      result.marker_date = markerDate;
      result.date_match = markerDate === expectedDate;

      if (!result.date_match) {
        result.missing_rules.push(`${fileName}: marker date ${markerDate} ≠ expected ${expectedDate}`);
      } else {
        result.status = "pass";
        break; // found and valid in at least one file
      }
    } else {
      result.missing_rules.push(`${fileName}: EGOS-KERNEL-PROPAGATED marker not found`);
    }
  }

  if (result.checked_files.length === 0) {
    result.status = "skip";
    result.missing_rules.push("no CLAUDE.md or .windsurfrules found");
  }

  return result;
}

// ── Report ───────────────────────────────────────────────────────────────────

function formatReport(results: RepoVerification[]): string {
  const passed = results.filter(r => r.status === "pass");
  const failed = results.filter(r => r.status === "fail");
  const skipped = results.filter(r => r.status === "skip");

  const lines = [
    `[verifier] Results: ${passed.length} pass / ${failed.length} fail / ${skipped.length} skip`,
    "",
  ];

  for (const r of results) {
    const icon = r.status === "pass" ? "✅" : r.status === "skip" ? "⏭️ " : "❌";
    lines.push(`  ${icon} ${r.repo}`);
    if (r.status !== "pass" && r.missing_rules.length > 0) {
      for (const rule of r.missing_rules) {
        lines.push(`      → ${rule}`);
      }
    }
  }

  return lines.join("\n");
}

// ── Telegram ─────────────────────────────────────────────────────────────────

async function sendTelegram(results: RepoVerification[]): Promise<void> {
  const TG_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  const TG_CHAT_ID = process.env.TELEGRAM_CHAT_ID;
  if (!TG_BOT_TOKEN || !TG_CHAT_ID) return;

  const passed = results.filter(r => r.status === "pass").length;
  const failed = results.filter(r => r.status === "fail");

  const statusIcon = failed.length === 0 ? "✅" : "⚠️";
  const failList = failed.map(r => `• ${r.repo}: ${r.missing_rules[0] ?? "unknown"}`).join("\n");

  const msg = `${statusIcon} *Disseminate Verifier*\n\n✅ ${passed} repos synced\n${failed.length > 0 ? `❌ ${failed.length} repos need propagation:\n${failList}` : "All repos up-to-date"}`;

  await fetch(`https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage`, {
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
  const manifest = loadManifest();
  if (!manifest) {
    // No manifest = nothing to verify (scanner hasn't run yet — not an error)
    console.log("[verifier] No manifest found. Run disseminate-scanner.ts first.");
    process.exit(0);
  }

  if (!manifest.propagation_needed) {
    console.log("[verifier] Manifest says no propagation needed. Skipping.");
    process.exit(0);
  }

  const { date: expectedDate, existing_repos } = manifest;
  console.log(`[verifier] Verifying ${existing_repos.length} repos against date ${expectedDate}...`);

  const results: RepoVerification[] = [];
  for (const repoPath of existing_repos) {
    const result = verifyRepo(repoPath, expectedDate);
    results.push(result);
  }

  // Always print report
  console.log(formatReport(results));

  if (SEND_TG) {
    await sendTelegram(results);
  }

  const failCount = results.filter(r => r.status === "fail").length;
  if (failCount > 0) {
    console.log(`\n[verifier] ${failCount} repos need propagation. Run:`);
    console.log(`  bun scripts/disseminate-propagator.ts --all`);
    process.exit(DRY ? 0 : 1);
  }

  console.log("[verifier] ✅ All repos verified.");
}

main().catch(err => {
  console.error("[verifier] Fatal:", err);
  process.exit(1);
});
