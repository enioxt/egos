#!/usr/bin/env bun
/**
 * doc-drift-analyzer.ts — Layer 3.5 of the EGOS Doc-Drift Shield
 *
 * Weekly pattern analysis of drift history stored in docs/jobs/.
 * Reads past drift reports, detects trends, and produces a summary
 * suitable for the CCR Governance Drift Sentinel job.
 *
 * Unlike doc-drift-sentinel.ts (runs locally across all repos),
 * this analyzer works with the committed history in one repo and
 * is designed to run inside GitHub Actions.
 *
 * Usage:
 *   bun agents/agents/doc-drift-analyzer.ts                  # analyze + console
 *   bun agents/agents/doc-drift-analyzer.ts --output-file    # write to docs/jobs/
 *   bun agents/agents/doc-drift-analyzer.ts --json           # JSON output
 *
 * Part of: docs/DOC_DRIFT_SHIELD.md
 */

import { existsSync, readdirSync, readFileSync, writeFileSync } from "fs";
import { join } from "path";

// ─── Types ────────────────────────────────────────────────────────────────────

interface DriftEvent {
  date: string;
  claimId: string;
  repo: string;
  drift: string;
}

interface ClaimFrequency {
  claimId: string;
  driftCount: number;
  lastDrift: string;
  repos: string[];
}

interface AnalysisResult {
  period: { from: string; to: string };
  totalReports: number;
  totalDriftEvents: number;
  topDriftingClaims: ClaimFrequency[];
  stableClaimsCount: number;
  healthScore: number; // 0-100
  trend: "improving" | "stable" | "worsening";
  recommendations: string[];
}

// ─── Parse a single drift report markdown ─────────────────────────────────────

function parseDriftReport(content: string, filename: string): DriftEvent[] {
  const events: DriftEvent[] = [];
  const dateMatch = filename.match(/(\d{4}-\d{2}-\d{2})/);
  const date = dateMatch?.[1] ?? "unknown";

  // Look for lines like: "❌ claim_id: 100 → 200 (drift X%)"
  // or "🔴 DRIFT claim_id" patterns
  const claimPattern = /(?:❌|🔴|DRIFT)\s+([a-z_]+).*?(\d+\s*→\s*\d+|\+\d+%|-\d+%)/gi;
  const repoPattern = /repo[:\s]+([a-zA-Z_-]+)/i;

  const repoMatch = content.match(repoPattern);
  const repo = repoMatch?.[1] ?? "egos";

  let match;
  while ((match = claimPattern.exec(content)) !== null) {
    events.push({
      date,
      claimId: match[1],
      repo,
      drift: match[2],
    });
  }

  // Also look for table rows with ❌
  const tablePattern = /\|\s*❌[^|]*\|\s*([a-z_]+)\s*\|/gi;
  while ((match = tablePattern.exec(content)) !== null) {
    events.push({
      date,
      claimId: match[1],
      repo,
      drift: "table-row",
    });
  }

  return events;
}

// ─── Analyzer ─────────────────────────────────────────────────────────────────

function analyze(repoRoot: string): AnalysisResult {
  const jobsDir = join(repoRoot, "docs", "jobs");
  if (!existsSync(jobsDir)) {
    return emptyResult();
  }

  const reportFiles = readdirSync(jobsDir)
    .filter((f) => f.includes("drift") || f.includes("governance"))
    .filter((f) => f.endsWith(".md"))
    .sort();

  const allEvents: DriftEvent[] = [];

  for (const file of reportFiles) {
    const content = readFileSync(join(jobsDir, file), "utf-8");
    const events = parseDriftReport(content, file);
    allEvents.push(...events);
  }

  // Aggregate by claimId
  const frequency = new Map<string, ClaimFrequency>();
  for (const event of allEvents) {
    const existing = frequency.get(event.claimId) ?? {
      claimId: event.claimId,
      driftCount: 0,
      lastDrift: event.date,
      repos: [],
    };
    existing.driftCount++;
    if (event.date > existing.lastDrift) existing.lastDrift = event.date;
    if (!existing.repos.includes(event.repo)) existing.repos.push(event.repo);
    frequency.set(event.claimId, existing);
  }

  const topDriftingClaims = Array.from(frequency.values())
    .sort((a, b) => b.driftCount - a.driftCount)
    .slice(0, 10);

  // Health score: 100 - (driftEvents / expectedClaims * 100), capped 0-100
  const expectedClaims = 20; // rough estimate
  const healthScore = Math.max(
    0,
    Math.min(100, 100 - Math.floor((allEvents.length / expectedClaims) * 10))
  );

  // Trend: compare first half vs second half of reports
  const half = Math.floor(reportFiles.length / 2);
  const firstHalfEvents = allEvents.filter((e) =>
    reportFiles.slice(0, half).some((f) => f.includes(e.date))
  ).length;
  const secondHalfEvents = allEvents.filter((e) =>
    reportFiles.slice(half).some((f) => f.includes(e.date))
  ).length;

  let trend: "improving" | "stable" | "worsening" = "stable";
  if (reportFiles.length >= 4) {
    if (secondHalfEvents < firstHalfEvents * 0.7) trend = "improving";
    else if (secondHalfEvents > firstHalfEvents * 1.3) trend = "worsening";
  }

  // Recommendations
  const recommendations: string[] = [];
  if (topDriftingClaims.length > 0) {
    recommendations.push(
      `High-drift claim: \`${topDriftingClaims[0].claimId}\` drifted ${topDriftingClaims[0].driftCount}x — consider loosening tolerance`
    );
  }
  if (trend === "worsening") {
    recommendations.push(
      "Drift frequency increasing — review recently added claims for correctness of commands"
    );
  }
  if (allEvents.length === 0 && reportFiles.length > 0) {
    recommendations.push(
      "No drift events found in reports — either all clean or report format not parsed. Verify doc-drift-sentinel output format."
    );
  }
  if (reportFiles.length === 0) {
    recommendations.push(
      "No drift reports found in docs/jobs/. Run doc-drift-sentinel.ts --exec to generate first report."
    );
  }

  const dates = reportFiles
    .map((f) => f.match(/(\d{4}-\d{2}-\d{2})/)?.[1])
    .filter(Boolean) as string[];

  return {
    period: {
      from: dates[0] ?? "N/A",
      to: dates[dates.length - 1] ?? "N/A",
    },
    totalReports: reportFiles.length,
    totalDriftEvents: allEvents.length,
    topDriftingClaims,
    stableClaimsCount: Math.max(0, expectedClaims - frequency.size),
    healthScore,
    trend,
    recommendations,
  };
}

function emptyResult(): AnalysisResult {
  return {
    period: { from: "N/A", to: "N/A" },
    totalReports: 0,
    totalDriftEvents: 0,
    topDriftingClaims: [],
    stableClaimsCount: 0,
    healthScore: 100,
    trend: "stable",
    recommendations: ["No docs/jobs/ directory found — run doc-drift-sentinel first"],
  };
}

// ─── Renderers ────────────────────────────────────────────────────────────────

function renderMarkdown(result: AnalysisResult, repoRoot: string): string {
  const now = new Date().toISOString().slice(0, 10);
  const trendIcon =
    result.trend === "improving" ? "📉" : result.trend === "worsening" ? "📈" : "➡️";
  const healthIcon = result.healthScore >= 80 ? "✅" : result.healthScore >= 50 ? "⚠️" : "🔴";

  const rows =
    result.topDriftingClaims.length > 0
      ? result.topDriftingClaims
          .map(
            (c) =>
              `| \`${c.claimId}\` | ${c.driftCount} | ${c.repos.join(", ")} | ${c.lastDrift} |`
          )
          .join("\n")
      : "| — | 0 | — | — |";

  return `# Doc-Drift Pattern Analysis — ${now}

**Period:** ${result.period.from} → ${result.period.to}
**Reports analyzed:** ${result.totalReports}
**Total drift events:** ${result.totalDriftEvents}
**Health score:** ${healthIcon} ${result.healthScore}/100
**Trend:** ${trendIcon} ${result.trend}

## Top Drifting Claims

| Claim ID | Drift Count | Repos | Last Drift |
|----------|-------------|-------|------------|
${rows}

## Recommendations

${result.recommendations.map((r) => `- ${r}`).join("\n")}

---
*Generated by doc-drift-analyzer.ts | EGOS Doc-Drift Shield Layer 3.5*
*Repo: ${repoRoot}*
`;
}

// ─── CLI ─────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const outputFile = args.includes("--output-file");
const jsonMode = args.includes("--json");
const repoRoot = process.cwd();

const result = analyze(repoRoot);

if (jsonMode) {
  console.log(JSON.stringify(result, null, 2));
} else {
  const md = renderMarkdown(result, repoRoot);

  if (outputFile) {
    const now = new Date().toISOString().slice(0, 10);
    const outPath = join(repoRoot, "docs", "jobs", `${now}-doc-drift-analysis.md`);
    writeFileSync(outPath, md);
    console.log(`✅ Analysis written to ${outPath}`);
  } else {
    console.log(md);
  }
}
