#!/usr/bin/env bun
/**
 * readme-syncer.ts — Layer 2.5 of the EGOS Doc-Drift Shield
 *
 * Reads `.egos-manifest.yaml`, then patches annotated README sections
 * with the current `last_value` from each claim.
 *
 * Annotation format (invisible in rendered Markdown):
 *
 *   Plain value in table/prose:
 *     <!-- metric:CLAIM_ID -->1690<!-- /metric:CLAIM_ID -->
 *
 *   Badge line (full replacement):
 *     <!-- badge:CLAIM_ID:TEMPLATE -->
 *     [![Label](https://img.shields.io/badge/label-1690-green)]()
 *     <!-- /badge:CLAIM_ID -->
 *
 *   Where TEMPLATE is a shields.io badge spec:
 *     label-{VALUE}-color  (e.g. "commits-{VALUE}-brightgreen")
 *
 * Usage:
 *   bun agents/agents/readme-syncer.ts --repo /home/enio/carteira-livre
 *   bun agents/agents/readme-syncer.ts --all          # all known repos
 *   bun agents/agents/readme-syncer.ts --dry          # show diff, no writes
 *
 * Part of: docs/DOC_DRIFT_SHIELD.md
 */

import { existsSync, readFileSync, writeFileSync } from "fs";
import { join, dirname } from "path";
import { parse as parseYaml } from "yaml";

// ─── Types ────────────────────────────────────────────────────────────────────

interface ManifestClaim {
  id: string;
  last_value: string;
}

interface Manifest {
  repo: string;
  claims: ManifestClaim[];
}

// ─── Known repos ─────────────────────────────────────────────────────────────

const KNOWN_REPOS = [
  "/home/enio/egos",
  "/home/enio/carteira-livre",
  "/home/enio/br-acc",
];

// ─── Patterns ────────────────────────────────────────────────────────────────

// <!-- metric:CLAIM_ID -->VALUE<!-- /metric:CLAIM_ID -->
const METRIC_RE = (id: string) =>
  new RegExp(`(<!-- metric:${id} -->)[^<]*(<!-- /metric:${id} -->)`, "g");

// <!-- badge:CLAIM_ID -->
// [![Label](https://img.shields.io/badge/label-OLD_VALUE-color)]()
// <!-- /badge:CLAIM_ID -->
//
// The syncer keeps the existing badge line intact, replacing only the
// numeric value segment in the shields.io URL (penultimate dash-segment).

function patchBadgeValue(badgeLine: string, newValue: string): string {
  return badgeLine.replace(
    /(https:\/\/img\.shields\.io\/badge\/[^)]+)/,
    (url) => {
      const segments = url.split("-");
      if (segments.length < 3) return url;
      segments[segments.length - 2] = newValue;
      return segments.join("-");
    }
  );
}

// ─── Syncer ───────────────────────────────────────────────────────────────────

interface SyncResult {
  repo: string;
  file: string;
  patches: number;
  changed: boolean;
}

function syncFile(
  filePath: string,
  claims: ManifestClaim[],
  dry: boolean
): SyncResult {
  let content = readFileSync(filePath, "utf-8");
  const original = content;
  let patches = 0;

  for (const claim of claims) {
    const { id, last_value: value } = claim;
    if (!value) continue;

    // 1. Patch plain metric annotations
    const metricRe = METRIC_RE(id);
    const metricReplacement = `$1${value}$2`;
    const afterMetric = content.replace(metricRe, metricReplacement);
    if (afterMetric !== content) {
      patches += (content.match(METRIC_RE(id)) ?? []).length;
      content = afterMetric;
    }

    // 2. Patch badge block annotations (simple block replacement)
    const badgeOpenTag = `<!-- badge:${id} -->`;
    const badgeCloseTag = `<!-- /badge:${id} -->`;
    let searchFrom = 0;
    while (true) {
      const start = content.indexOf(badgeOpenTag, searchFrom);
      if (start === -1) break;
      const end = content.indexOf(badgeCloseTag, start);
      if (end === -1) break;

      const block = content.slice(start, end + badgeCloseTag.length);
      const patched = patchBadgeValue(block, value);
      if (patched !== block) {
        patches++;
        content = content.slice(0, start) + patched + content.slice(start + block.length);
        searchFrom = start + patched.length;
      } else {
        searchFrom = end + badgeCloseTag.length;
      }
    }
  }

  const changed = content !== original;

  if (changed) {
    if (dry) {
      // Show diff summary
      const oldLines = original.split("\n");
      const newLines = content.split("\n");
      for (let i = 0; i < Math.max(oldLines.length, newLines.length); i++) {
        if (oldLines[i] !== newLines[i]) {
          console.log(`  - ${oldLines[i] ?? ""}`);
          console.log(`  + ${newLines[i] ?? ""}`);
        }
      }
    } else {
      writeFileSync(filePath, content);
    }
  }

  return {
    repo: dirname(filePath),
    file: filePath,
    patches,
    changed,
  };
}

function syncRepo(repoDir: string, dry: boolean): SyncResult[] {
  const manifestPath = join(repoDir, ".egos-manifest.yaml");
  if (!existsSync(manifestPath)) return [];

  const manifest = parseYaml(readFileSync(manifestPath, "utf-8")) as Manifest;
  if (!manifest?.claims) return [];

  const claims = manifest.claims;
  const results: SyncResult[] = [];

  // Sync README.md (primary target)
  const readmePath = join(repoDir, "README.md");
  if (existsSync(readmePath)) {
    const result = syncFile(readmePath, claims, dry);
    if (result.patches > 0 || result.changed) {
      console.log(
        `  ${result.changed ? "✏️ " : "✅"} README.md — ${result.patches} metric(s) ${dry ? "(dry)" : "patched"}`
      );
    } else {
      console.log(`  ✅ README.md — no annotations found (add <!-- metric:CLAIM_ID --> tags)`);
    }
    results.push(result);
  }

  return results;
}

// ─── CLI ─────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const dry = args.includes("--dry");
const all = args.includes("--all");
const repoIdx = args.indexOf("--repo");
const singleRepo = repoIdx !== -1 ? args[repoIdx + 1] : undefined;

const repos = all
  ? KNOWN_REPOS.filter((r) => existsSync(join(r, ".egos-manifest.yaml")))
  : singleRepo
  ? [singleRepo]
  : [process.cwd()];

console.log(`\n📝 README Syncer${dry ? " (dry run)" : ""} — ${repos.length} repo(s)\n`);

let totalPatches = 0;
let totalChanged = 0;

for (const repo of repos) {
  console.log(`── ${repo}`);
  const results = syncRepo(repo, dry);
  const patches = results.reduce((s, r) => s + r.patches, 0);
  const changed = results.filter((r) => r.changed).length;
  totalPatches += patches;
  totalChanged += changed;
}

console.log(`\n${totalChanged > 0 ? "✏️" : "✅"} Total: ${totalPatches} patch(es) in ${totalChanged} file(s)`);
