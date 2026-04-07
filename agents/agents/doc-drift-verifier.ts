#!/usr/bin/env bun
/**
 * doc-drift-verifier.ts — Layer 2 of the EGOS Doc-Drift Shield
 *
 * Reads a `.egos-manifest.yaml`, runs each claim command, compares results
 * against declared tolerances, and outputs a verification report.
 *
 * Usage:
 *   bun agents/agents/doc-drift-verifier.ts --manifest ./.egos-manifest.yaml
 *   bun agents/agents/doc-drift-verifier.ts --repo /home/enio/carteira-livre
 *   bun agents/agents/doc-drift-verifier.ts --all          # scan all known repos
 *   bun agents/agents/doc-drift-verifier.ts --fail-on-drift # exit 1 if any drift
 *   bun agents/agents/doc-drift-verifier.ts --json          # JSON output
 *   bun agents/agents/doc-drift-verifier.ts --markdown      # markdown table
 *
 * Exit codes:
 *   0 — all claims passed
 *   1 — drift detected (only when --fail-on-drift)
 *   2 — command error / manifest not found
 *
 * Part of: docs/DOC_DRIFT_SHIELD.md
 * Schema version: 1.0.0
 */

import { existsSync, mkdirSync, writeFileSync } from "fs";
import { join, dirname } from "path";
import { parse as parseYamlLib } from "yaml";

// ─── Types ────────────────────────────────────────────────────────────────────

interface ManifestClaim {
  id: string;
  description: string;
  readme_location?: string;
  command: string;
  tolerance: string; // "exact" | "±N" | "±N%" | "min:N" | "max:N"
  last_value: string;
  last_verified_at?: string;
  category?: string;
}

interface ManifestDomain {
  url: string;
  expected_status: string;
  checked_at?: string;
  note?: string;
}

interface ManifestEndpoint {
  url: string;
  expected_status: string;
  expected_contains?: string;
  checked_at?: string;
  note?: string;
}

interface Manifest {
  schema_version: string;
  repo: string;
  updated_at?: string;
  updated_by?: string;
  manifest_doc?: string;
  claims: ManifestClaim[];
  domains?: ManifestDomain[];
  endpoints?: ManifestEndpoint[];
}

type ClaimStatus = "ok" | "warn" | "drifted" | "error" | "skipped";

interface ClaimResult {
  id: string;
  description?: string;
  status: ClaimStatus;
  last_value: string;
  current_value: string;
  tolerance: string;
  drift_pct?: number;
  drift_abs?: number;
  command: string;
  error?: string;
  severity: "ok" | "warn" | "drift" | "error";
}

interface DomainResult {
  url: string;
  status: "ok" | "drifted" | "error";
  expected_status: string;
  actual_status: string;
  contains_check?: boolean;
  error?: string;
}

interface VerificationReport {
  manifest: string;
  repo: string;
  verified_at: string;
  summary: {
    total_claims: number;
    passed: number;
    warned: number;
    drifted: number;
    errors: number;
    total_domains: number;
    domains_ok: number;
    domains_drifted: number;
  };
  results: ClaimResult[];
  domains: DomainResult[];
  exit_code: number;
}

// ─── Known repos ─────────────────────────────────────────────────────────────

const KNOWN_REPOS = [
  "/home/enio/egos",
  "/home/enio/carteira-livre",
  "/home/enio/br-acc",
  "/home/enio/egos-lab",
  "/home/enio/852",
];

// ─── YAML parser ─────────────────────────────────────────────────────────────

function parseYaml(content: string): unknown {
  return parseYamlLib(content);
}

// ─── (internal stub, kept for reference — not used) ──────────────────────────
// Replaced by `yaml` npm package for correctness with escaped quotes.
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function _minimalYamlParse_UNUSED(content: string): unknown {
  // Remove BOM if present
  content = content.replace(/^\uFEFF/, "");

  const lines = content.split("\n");
  let pos = 0;

  function peek(): string | undefined {
    return lines[pos];
  }

  function isComment(line: string): boolean {
    return line.trimStart().startsWith("#");
  }

  function indentOf(line: string): number {
    return line.length - line.trimStart().length;
  }

  function parseValue(raw: string): unknown {
    const s = raw.trim();
    if (s === "null" || s === "~" || s === "") return null;
    if (s === "true") return true;
    if (s === "false") return false;
    if (/^-?\d+(\.\d+)?$/.test(s)) return Number(s);
    // Quoted string
    if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
      return s.slice(1, -1);
    }
    return s;
  }

  function parseBlock(baseIndent: number): unknown {
    // Determine if it's a sequence or mapping
    while (pos < lines.length && (lines[pos].trim() === "" || isComment(lines[pos]))) pos++;

    if (pos >= lines.length) return null;

    const firstLine = lines[pos];
    const firstIndent = indentOf(firstLine);
    if (firstIndent < baseIndent) return null;

    const trimmed = firstLine.trimStart();

    if (trimmed.startsWith("- ") || trimmed === "-") {
      // Sequence
      const arr: unknown[] = [];
      while (pos < lines.length) {
        const line = lines[pos];
        if (line.trim() === "" || isComment(line)) { pos++; continue; }
        const ind = indentOf(line);
        if (ind < baseIndent) break;
        if (!line.trimStart().startsWith("- ") && line.trimStart() !== "-") break;

        const afterDash = line.trimStart().slice(2);
        pos++;

        if (afterDash.trim() === "" || afterDash.trim() === "") {
          // Block mapping inside sequence
          arr.push(parseBlock(ind + 2));
        } else if (afterDash.includes(": ")) {
          // Inline mapping: `- key: value`
          const obj: Record<string, unknown> = {};
          const [k, ...vParts] = afterDash.split(": ");
          const v = vParts.join(": ");
          obj[k.trim()] = parseValue(v);
          // Continue reading sibling keys at same indent level
          while (pos < lines.length) {
            const next = lines[pos];
            if (next.trim() === "" || isComment(next)) { pos++; continue; }
            if (indentOf(next) <= ind) break;
            const nextTrimmed = next.trimStart();
            if (nextTrimmed.startsWith("- ")) break;
            if (nextTrimmed.endsWith(": |") || nextTrimmed.endsWith(": >")) {
              const [nk] = nextTrimmed.split(": ");
              const blockChar = nextTrimmed.slice(nextTrimmed.lastIndexOf(": ") + 2).trim();
              pos++;
              const blockLines: string[] = [];
              const blockBaseIndent = indentOf(next) + 2;
              while (pos < lines.length) {
                const bl = lines[pos];
                if (bl.trim() === "" && pos + 1 < lines.length && indentOf(lines[pos + 1]) >= blockBaseIndent) {
                  blockLines.push(""); pos++; continue;
                }
                if (bl.trim() === "") { pos++; break; }
                if (indentOf(bl) < blockBaseIndent && bl.trim() !== "") break;
                blockLines.push(bl.slice(blockBaseIndent));
                pos++;
              }
              let blockStr = blockLines.join("\n");
              if (blockChar === "|") {
                // Literal block: keep trailing newline
                blockStr = blockStr.trimEnd() + "\n";
              } else {
                // Folded block: replace newlines with spaces
                blockStr = blockStr.replace(/\n/g, " ").trim();
              }
              obj[nk.trim()] = blockStr;
            } else if (nextTrimmed.includes(": ")) {
              const [nk, ...nv] = nextTrimmed.split(": ");
              obj[nk.trim()] = parseValue(nv.join(": "));
              pos++;
            } else {
              break;
            }
          }
          arr.push(obj);
        } else {
          arr.push(parseValue(afterDash));
        }
      }
      return arr;
    } else {
      // Mapping
      const obj: Record<string, unknown> = {};
      while (pos < lines.length) {
        const line = lines[pos];
        if (line.trim() === "" || isComment(line)) { pos++; continue; }
        const ind = indentOf(line);
        if (ind < baseIndent) break;

        const trimmedLine = line.trimStart();
        if (trimmedLine.startsWith("- ")) break;

        if (!trimmedLine.includes(":")) { pos++; continue; }

        const colonIdx = trimmedLine.indexOf(":");
        const key = trimmedLine.slice(0, colonIdx).trim();
        const rest = trimmedLine.slice(colonIdx + 1).trim();

        pos++;

        if (rest === "|" || rest === ">") {
          // Block scalar
          const blockLines: string[] = [];
          const blockBaseIndent = ind + 2;
          while (pos < lines.length) {
            const bl = lines[pos];
            if (bl.trim() === "" && pos + 1 < lines.length && indentOf(lines[pos + 1]) >= blockBaseIndent) {
              blockLines.push(""); pos++; continue;
            }
            if (bl.trim() === "") { pos++; break; }
            if (indentOf(bl) < blockBaseIndent && bl.trim() !== "") break;
            blockLines.push(bl.slice(blockBaseIndent));
            pos++;
          }
          let blockStr = blockLines.join("\n");
          if (rest === "|") {
            blockStr = blockStr.trimEnd() + "\n";
          } else {
            blockStr = blockStr.replace(/\n/g, " ").trim();
          }
          obj[key] = blockStr;
        } else if (rest === "" || rest === null) {
          // Nested block
          const nested = parseBlock(ind + 2);
          obj[key] = nested;
        } else {
          obj[key] = parseValue(rest);
        }
      }
      return obj;
    }
  }

  return parseBlock(0);
}

// ─── Tolerance evaluation ─────────────────────────────────────────────────────

interface ToleranceResult {
  status: ClaimStatus;
  drift_abs?: number;
  drift_pct?: number;
}

function evaluateTolerance(lastVal: string, currentVal: string, tolerance: string): ToleranceResult {
  const last = parseFloat(lastVal);
  const current = parseFloat(currentVal);

  if (tolerance === "exact") {
    if (lastVal.trim() === currentVal.trim()) return { status: "ok" };
    return { status: "drifted", drift_abs: Math.abs(current - last) };
  }

  if (tolerance.startsWith("min:")) {
    const min = parseFloat(tolerance.slice(4));
    if (current >= min) return { status: "ok" };
    return { status: "drifted", drift_abs: min - current };
  }

  if (tolerance.startsWith("max:")) {
    const max = parseFloat(tolerance.slice(4));
    if (current <= max) return { status: "ok" };
    return { status: "drifted", drift_abs: current - max };
  }

  if (tolerance.endsWith("%")) {
    const pct = parseFloat(tolerance.replace("±", "").replace("%", ""));
    if (isNaN(last) || isNaN(current)) return { status: "error" };
    const diff = Math.abs(current - last);
    const diffPct = last !== 0 ? (diff / last) * 100 : diff > 0 ? 100 : 0;
    if (diffPct <= pct) return { status: "ok", drift_pct: diffPct };
    return { status: "drifted", drift_pct: diffPct };
  }

  if (tolerance.startsWith("±")) {
    const allowedAbs = parseFloat(tolerance.slice(1));
    if (isNaN(last) || isNaN(current)) return { status: "error" };
    const diff = Math.abs(current - last);
    if (diff <= allowedAbs) return { status: "ok", drift_abs: diff };
    return { status: "drifted", drift_abs: diff };
  }

  // Unknown tolerance format
  return { status: "warn" };
}

// ─── Command executor ─────────────────────────────────────────────────────────

async function runCommand(command: string, cwd: string, timeoutMs = 30_000): Promise<{ output: string; error: string; exitCode: number }> {
  try {
    const proc = Bun.spawn(["bash", "-c", command], {
      cwd,
      stdout: "pipe",
      stderr: "pipe",
    });

    const timeout = setTimeout(() => proc.kill(), timeoutMs);

    const [stdout, stderr] = await Promise.all([
      new Response(proc.stdout).text(),
      new Response(proc.stderr).text(),
    ]);

    await proc.exited;
    clearTimeout(timeout);

    return {
      output: stdout.trim(),
      error: stderr.trim(),
      exitCode: proc.exitCode ?? 0,
    };
  } catch (err) {
    return {
      output: "",
      error: String(err),
      exitCode: 127,
    };
  }
}

// ─── Domain checker ───────────────────────────────────────────────────────────

async function checkDomain(domain: ManifestDomain | ManifestEndpoint): Promise<DomainResult> {
  try {
    const response = await fetch(domain.url, {
      method: "GET",
      redirect: "manual",
      signal: AbortSignal.timeout(10_000),
    });

    const actualStatus = String(response.status);
    const expectedStatus = String(domain.expected_status);
    const statusOk = actualStatus === expectedStatus;

    let containsCheck: boolean | undefined;
    if ("expected_contains" in domain && domain.expected_contains) {
      const body = await response.text().catch(() => "");
      containsCheck = body.includes(domain.expected_contains);
    }

    const ok = statusOk && (containsCheck === undefined || containsCheck);

    return {
      url: domain.url,
      status: ok ? "ok" : "drifted",
      expected_status: expectedStatus,
      actual_status: actualStatus,
      contains_check: containsCheck,
    };
  } catch (err) {
    return {
      url: domain.url,
      status: "error",
      expected_status: String(domain.expected_status),
      actual_status: "connection_error",
      error: String(err),
    };
  }
}

// ─── Manifest verifier ────────────────────────────────────────────────────────

async function verifyManifest(manifestPath: string, opts: { failOnDrift: boolean }): Promise<VerificationReport> {
  const repoDir = dirname(manifestPath);

  let content: string;
  try {
    content = await Bun.file(manifestPath).text();
  } catch {
    console.error(`[doc-drift] ERROR: Cannot read manifest: ${manifestPath}`);
    process.exit(2);
  }

  const manifest = parseYaml(content) as Manifest;

  if (!manifest || typeof manifest !== "object") {
    console.error(`[doc-drift] ERROR: Invalid manifest YAML: ${manifestPath}`);
    process.exit(2);
  }

  const claims: ManifestClaim[] = manifest.claims ?? [];
  const domains: (ManifestDomain | ManifestEndpoint)[] = [
    ...(manifest.domains ?? []),
    ...(manifest.endpoints ?? []),
  ];

  const results: ClaimResult[] = [];
  const domainResults: DomainResult[] = [];

  // ── Run claim commands ──
  console.error(`\n[doc-drift] Verifying ${claims.length} claims in ${manifest.repo ?? "?"} ...`);

  for (const claim of claims) {
    const { output, error, exitCode } = await runCommand(claim.command, repoDir);

    if (exitCode !== 0 || output === "") {
      results.push({
        id: claim.id,
        description: claim.description,
        status: "error",
        last_value: claim.last_value,
        current_value: "",
        tolerance: claim.tolerance,
        command: claim.command,
        error: error || `exit code ${exitCode}`,
        severity: "error",
      });
      console.error(`  [error] ${claim.id}: command failed — ${error.slice(0, 80)}`);
      continue;
    }

    const currentValue = output.trim();
    const tolResult = evaluateTolerance(claim.last_value, currentValue, claim.tolerance);

    const severity =
      tolResult.status === "ok" ? "ok"
      : tolResult.status === "warn" ? "warn"
      : tolResult.status === "drifted" ? "drift"
      : "error";

    const icon =
      tolResult.status === "ok" ? "✅"
      : tolResult.status === "warn" ? "⚠️"
      : tolResult.status === "drifted" ? "❌"
      : "💥";

    console.error(
      `  ${icon} ${claim.id}: ${claim.last_value} → ${currentValue}` +
      (tolResult.drift_abs !== undefined ? ` (Δ${tolResult.drift_abs})` : "") +
      (tolResult.drift_pct !== undefined ? ` (${tolResult.drift_pct.toFixed(1)}%)` : "")
    );

    results.push({
      id: claim.id,
      description: claim.description,
      status: tolResult.status,
      last_value: claim.last_value,
      current_value: currentValue,
      tolerance: claim.tolerance,
      drift_abs: tolResult.drift_abs,
      drift_pct: tolResult.drift_pct !== undefined ? parseFloat(tolResult.drift_pct.toFixed(2)) : undefined,
      command: claim.command,
      severity,
    });
  }

  // ── Check domains ──
  if (domains.length > 0) {
    console.error(`\n[doc-drift] Checking ${domains.length} domain(s) ...`);
    for (const domain of domains) {
      const result = await checkDomain(domain);
      const icon = result.status === "ok" ? "✅" : result.status === "drifted" ? "❌" : "💥";
      console.error(`  ${icon} ${domain.url} → ${result.actual_status} (expected ${result.expected_status})`);
      domainResults.push(result);
    }
  }

  // ── Summarize ──
  const passed = results.filter((r) => r.status === "ok").length;
  const warned = results.filter((r) => r.status === "warn").length;
  const drifted = results.filter((r) => r.status === "drifted").length;
  const errors = results.filter((r) => r.status === "error").length;
  const domainsOk = domainResults.filter((d) => d.status === "ok").length;
  const domainsDrifted = domainResults.filter((d) => d.status !== "ok").length;

  const exitCode = drifted > 0 && opts.failOnDrift ? 1 : errors > 0 ? 2 : 0;

  return {
    manifest: manifestPath,
    repo: manifest.repo ?? "unknown",
    verified_at: new Date().toISOString(),
    summary: {
      total_claims: claims.length,
      passed,
      warned,
      drifted,
      errors,
      total_domains: domainResults.length,
      domains_ok: domainsOk,
      domains_drifted: domainsDrifted,
    },
    results,
    domains: domainResults,
    exit_code: exitCode,
  };
}

// ─── Output formatters ────────────────────────────────────────────────────────

function formatMarkdown(report: VerificationReport): string {
  const { summary } = report;
  const lines: string[] = [
    `# Doc-Drift Report — ${report.repo}`,
    ``,
    `**Verified at:** ${report.verified_at}  `,
    `**Manifest:** \`${report.manifest}\``,
    ``,
    `## Summary`,
    ``,
    `| Metric | Value |`,
    `|--------|-------|`,
    `| Total claims | ${summary.total_claims} |`,
    `| Passed | ${summary.passed} |`,
    `| Warned | ${summary.warned} |`,
    `| Drifted | ${summary.drifted} |`,
    `| Errors | ${summary.errors} |`,
    `| Domains OK | ${summary.domains_ok}/${summary.total_domains} |`,
    ``,
    `## Claims`,
    ``,
    `| ID | Status | Last | Current | Tolerance | Drift |`,
    `|----|--------|------|---------|-----------|-------|`,
    ...report.results.map((r) => {
      const icon = r.status === "ok" ? "✅" : r.status === "warn" ? "⚠️" : r.status === "drifted" ? "❌" : "💥";
      const drift =
        r.drift_pct !== undefined ? `${r.drift_pct}%`
        : r.drift_abs !== undefined ? `${r.drift_abs}`
        : "-";
      return `| \`${r.id}\` | ${icon} ${r.status} | ${r.last_value} | ${r.current_value || "-"} | \`${r.tolerance}\` | ${drift} |`;
    }),
  ];

  if (report.domains.length > 0) {
    lines.push(
      ``,
      `## Domains`,
      ``,
      `| URL | Expected | Actual | Status |`,
      `|-----|----------|--------|--------|`,
      ...report.domains.map((d) => {
        const icon = d.status === "ok" ? "✅" : "❌";
        return `| ${d.url} | ${d.expected_status} | ${d.actual_status} | ${icon} |`;
      }),
    );
  }

  return lines.join("\n");
}

function printHuman(report: VerificationReport): void {
  const { summary } = report;
  const statusIcon = summary.drifted === 0 && summary.errors === 0 ? "✅" : "❌";

  console.log(`\n${statusIcon} Doc-Drift Verification — ${report.repo}`);
  console.log(`   Claims: ${summary.passed}/${summary.total_claims} passed | ${summary.drifted} drifted | ${summary.errors} errors`);

  if (summary.total_domains > 0) {
    console.log(`   Domains: ${summary.domains_ok}/${summary.total_domains} reachable`);
  }

  if (summary.drifted > 0) {
    console.log(`\n   Drifted claims:`);
    for (const r of report.results.filter((r) => r.status === "drifted")) {
      const drift =
        r.drift_pct !== undefined ? `(${r.drift_pct}% drift)`
        : r.drift_abs !== undefined ? `(Δ${r.drift_abs})`
        : "";
      console.log(`     ❌ ${r.id}: ${r.last_value} → ${r.current_value} ${drift} [tolerance: ${r.tolerance}]`);
    }
  }

  if (summary.errors > 0) {
    console.log(`\n   Errors:`);
    for (const r of report.results.filter((r) => r.status === "error")) {
      console.log(`     💥 ${r.id}: ${r.error}`);
    }
  }
}

// ─── CLI ─────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const opts = {
  manifest: "",
  repo: "",
  all: args.includes("--all"),
  failOnDrift: args.includes("--fail-on-drift"),
  json: args.includes("--json"),
  markdown: args.includes("--markdown"),
};

const manifestIdx = args.indexOf("--manifest");
if (manifestIdx !== -1) opts.manifest = args[manifestIdx + 1] ?? "";

const repoIdx = args.indexOf("--repo");
if (repoIdx !== -1) opts.repo = args[repoIdx + 1] ?? "";

// Collect manifest paths to verify
const manifestPaths: string[] = [];

if (opts.all) {
  for (const repo of KNOWN_REPOS) {
    const p = join(repo, ".egos-manifest.yaml");
    if (existsSync(p)) manifestPaths.push(p);
  }
  if (manifestPaths.length === 0) {
    console.error("[doc-drift] No manifests found in known repos.");
    process.exit(0);
  }
} else if (opts.repo) {
  const p = join(opts.repo, ".egos-manifest.yaml");
  if (!existsSync(p)) {
    console.error(`[doc-drift] ERROR: No manifest at ${p}`);
    process.exit(2);
  }
  manifestPaths.push(p);
} else if (opts.manifest) {
  if (!existsSync(opts.manifest)) {
    console.error(`[doc-drift] ERROR: Manifest not found: ${opts.manifest}`);
    process.exit(2);
  }
  manifestPaths.push(opts.manifest);
} else {
  // Auto-detect in CWD
  const cwd = process.cwd();
  const p = join(cwd, ".egos-manifest.yaml");
  if (!existsSync(p)) {
    console.error(`[doc-drift] No manifest found in ${cwd}. Use --manifest, --repo, or --all.`);
    process.exit(0);
  }
  manifestPaths.push(p);
}

// Run verifications
const reports: VerificationReport[] = [];
for (const manifestPath of manifestPaths) {
  const report = await verifyManifest(manifestPath, { failOnDrift: opts.failOnDrift });
  reports.push(report);
}

// Output
if (opts.json) {
  const output = reports.length === 1 ? reports[0] : reports;
  process.stdout.write(JSON.stringify(output, null, 2) + "\n");
} else if (opts.markdown) {
  for (const r of reports) {
    process.stdout.write(formatMarkdown(r) + "\n\n---\n\n");
  }
} else {
  for (const r of reports) {
    printHuman(r);
  }
}

// Save report to docs/jobs/
const EGOS_ROOT = "/home/enio/egos";
try {
  const jobsDir = join(EGOS_ROOT, "docs/jobs");
  mkdirSync(jobsDir, { recursive: true });
  const date = new Date().toISOString().slice(0, 10);
  const reportPath = join(jobsDir, `${date}-doc-drift-verifier.json`);
  writeFileSync(reportPath, JSON.stringify(reports.length === 1 ? reports[0] : reports, null, 2));
} catch {
  // Non-fatal: may not have write access to egos root from other repos
}

// Exit with appropriate code
const worstExit = Math.max(...reports.map((r) => r.exit_code));
process.exit(worstExit);
