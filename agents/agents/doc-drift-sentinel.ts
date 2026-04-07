#!/usr/bin/env bun
/**
 * doc-drift-sentinel.ts — Layer 3 of the EGOS Doc-Drift Shield
 *
 * Autonomous daily scanner that:
 *   1. Discovers all repos with .egos-manifest.yaml
 *   2. Runs doc-drift-verifier for each repo
 *   3. On drift: creates a branch, auto-patches last_value, commits, pushes, opens GitHub issue
 *   4. Sends Telegram alerts for drift and domain failures
 *   5. Rate-limits GitHub issue creation (max 1 per claim per 7 days)
 *
 * Usage:
 *   bun agents/agents/doc-drift-sentinel.ts --dry          # detect-only, no writes
 *   bun agents/agents/doc-drift-sentinel.ts --exec         # full run
 *   bun agents/agents/doc-drift-sentinel.ts --exec --repo /home/enio/carteira-livre
 *
 * Safety rules (CLAUDE.md §25):
 *   - Never force-push
 *   - Never push to main/master
 *   - Never modify files when repo has uncommitted changes
 *   - Always exit 0 (never blocks other jobs)
 *
 * Part of: docs/DOC_DRIFT_SHIELD.md
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "fs";
import { join, dirname } from "path";
import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

// ─── Constants ────────────────────────────────────────────────────────────────

const VERIFIER = join(dirname(Bun.main), "doc-drift-verifier.ts");
const ISSUE_LOG = "/var/lib/egos/doc-drift-sentinel/issue-log.json";
const ISSUE_COOLDOWN_DAYS = 7;
const REPOS_ROOT = "/home/enio";
const REPO_GITHUB_MAP: Record<string, string> = {
  "egos": "enioxt/egos",
  "carteira-livre": "enioxt/carteira-livre",
  "br-acc": "enioxt/EGOS-Inteligencia",
  "egos-lab": "enioxt/egos-lab",
  "852": "enioxt/852",
};

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? "";
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID ?? "-4685671293";

// ─── Types ────────────────────────────────────────────────────────────────────

interface ClaimResult {
  id: string;
  status: "ok" | "warn" | "drifted" | "error" | "skipped";
  last_value: string;
  current_value: string;
  tolerance: string;
  drift_pct?: number;
  drift_abs?: number;
  error?: string;
}

interface DomainResult {
  url: string;
  status: "ok" | "drifted" | "error";
  expected_status: string;
  actual_status: string;
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

interface IssueLogEntry {
  repo: string;
  claim_id: string;
  issue_number: number;
  opened_at: string;
}

interface IssueLog {
  issues: IssueLogEntry[];
}

interface SentinelRun {
  mode: "dry" | "exec";
  started_at: string;
  repos_scanned: number;
  total_drift: number;
  total_domain_failures: number;
  actions: string[];
  errors: string[];
}

// ─── Shell runner ─────────────────────────────────────────────────────────────

async function run(
  cmd: string,
  cwd?: string,
  timeoutMs = 60_000
): Promise<{ stdout: string; stderr: string; exitCode: number }> {
  try {
    const proc = Bun.spawn(["bash", "-c", cmd], {
      cwd: cwd ?? process.cwd(),
      stdout: "pipe",
      stderr: "pipe",
    });

    const t = setTimeout(() => proc.kill(), timeoutMs);
    const [stdout, stderr] = await Promise.all([
      new Response(proc.stdout).text(),
      new Response(proc.stderr).text(),
    ]);
    await proc.exited;
    clearTimeout(t);

    return { stdout: stdout.trim(), stderr: stderr.trim(), exitCode: proc.exitCode ?? 0 };
  } catch (err) {
    return { stdout: "", stderr: String(err), exitCode: 127 };
  }
}

// ─── Telegram ─────────────────────────────────────────────────────────────────

async function sendTelegram(message: string): Promise<void> {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.log("[sentinel] Telegram: skipped — env vars not set");
    return;
  }
  try {
    await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text: message,
        parse_mode: "Markdown",
      }),
    });
  } catch (err) {
    console.error("[sentinel] Telegram error:", err);
  }
}

// ─── Issue rate-limiter ───────────────────────────────────────────────────────

function loadIssueLog(): IssueLog {
  try {
    if (existsSync(ISSUE_LOG)) {
      return JSON.parse(readFileSync(ISSUE_LOG, "utf-8")) as IssueLog;
    }
  } catch { /* ignore */ }
  return { issues: [] };
}

function saveIssueLog(log: IssueLog, mode: "dry" | "exec"): void {
  if (mode !== "exec") return;
  try {
    mkdirSync(dirname(ISSUE_LOG), { recursive: true });
    writeFileSync(ISSUE_LOG, JSON.stringify(log, null, 2));
  } catch (err) {
    console.error("[sentinel] Could not save issue log:", err);
  }
}

function isOnCooldown(log: IssueLog, repo: string, claimId: string): boolean {
  const cutoff = new Date(Date.now() - ISSUE_COOLDOWN_DAYS * 86_400_000).toISOString();
  return log.issues.some(
    (e) => e.repo === repo && e.claim_id === claimId && e.opened_at >= cutoff
  );
}

// ─── Repo discovery ───────────────────────────────────────────────────────────

async function discoverRepos(singleRepo?: string): Promise<string[]> {
  if (singleRepo) {
    const manifestPath = join(singleRepo, ".egos-manifest.yaml");
    return existsSync(manifestPath) ? [singleRepo] : [];
  }

  const { stdout } = await run(
    `find ${REPOS_ROOT} -maxdepth 2 -name '.egos-manifest.yaml' -not -path '*/node_modules/*' 2>/dev/null`
  );
  return stdout
    .split("\n")
    .filter(Boolean)
    .map((p) => dirname(p));
}

// ─── Manifest patcher ─────────────────────────────────────────────────────────

async function patchManifest(
  repoDir: string,
  driftedClaims: ClaimResult[],
  mode: "dry" | "exec"
): Promise<boolean> {
  const manifestPath = join(repoDir, ".egos-manifest.yaml");
  const today = new Date().toISOString().slice(0, 10);

  if (mode === "dry") {
    console.log(`  [dry] would patch ${driftedClaims.length} claim(s) in ${manifestPath}`);
    return true;
  }

  // Safety: check for uncommitted changes first
  const { stdout: status } = await run("git status --porcelain", repoDir);
  if (status.length > 0) {
    console.log(`  [sentinel] SKIP patch: ${repoDir} has uncommitted changes`);
    return false;
  }

  // Read and patch manifest
  let content: string;
  try {
    content = readFileSync(manifestPath, "utf-8");
  } catch {
    return false;
  }

  const manifest = parseYaml(content) as { claims?: Array<{ id: string; last_value: string; last_verified_at: string }> };
  if (!manifest?.claims) return false;

  for (const drifted of driftedClaims) {
    const claim = manifest.claims.find((c) => c.id === drifted.id);
    if (claim && drifted.current_value) {
      claim.last_value = drifted.current_value;
      claim.last_verified_at = today;
    }
  }

  // Update manifest updated_at
  (manifest as Record<string, unknown>)["updated_at"] = today;

  writeFileSync(manifestPath, stringifyYaml(manifest, { lineWidth: 120 }));
  return true;
}

// ─── Git branch + commit ──────────────────────────────────────────────────────

async function commitAndPush(
  repoDir: string,
  driftedClaims: ClaimResult[],
  mode: "dry" | "exec"
): Promise<{ branchName: string; pushed: boolean }> {
  const today = new Date().toISOString().slice(0, 10);
  const branchName = `drift-${today}`;

  if (mode === "dry") {
    console.log(`  [dry] would create branch ${branchName} and commit in ${repoDir}`);
    return { branchName, pushed: false };
  }

  // Create branch if not exists
  const { exitCode: branchExists } = await run(
    `git show-ref --verify --quiet refs/heads/${branchName}`,
    repoDir
  );
  if (branchExists !== 0) {
    await run(`git checkout -b ${branchName}`, repoDir);
  } else {
    await run(`git checkout ${branchName}`, repoDir);
  }

  // Stage manifest
  await run("git add .egos-manifest.yaml", repoDir);

  // Build commit message
  const claimSummary = driftedClaims
    .map((c) => `${c.id} ${c.last_value}→${c.current_value}`)
    .join(", ");
  const msg = `auto(drift): update manifest claims [${claimSummary}] [skip ci]`;

  const { exitCode } = await run(`git commit -m "${msg}"`, repoDir);
  if (exitCode !== 0) {
    console.log(`  [sentinel] Nothing to commit in ${repoDir}`);
    await run("git checkout -", repoDir); // return to previous branch
    return { branchName, pushed: false };
  }

  // Push branch (never force, never to main)
  const { exitCode: pushCode, stderr } = await run(
    `git push origin ${branchName}`,
    repoDir
  );
  if (pushCode !== 0) {
    console.error(`  [sentinel] Push failed: ${stderr}`);
    await run("git checkout -", repoDir);
    return { branchName, pushed: false };
  }

  await run("git checkout -", repoDir); // return to main
  return { branchName, pushed: true };
}

// ─── GitHub issue ─────────────────────────────────────────────────────────────

async function openGitHubIssue(
  repoSlug: string,
  repoDir: string,
  claim: ClaimResult,
  mode: "dry" | "exec",
  issueLog: IssueLog
): Promise<number | null> {
  if (isOnCooldown(issueLog, repoSlug, claim.id)) {
    console.log(`  [sentinel] Issue for ${repoSlug}/${claim.id} on cooldown — skipping`);
    return null;
  }

  const drift =
    claim.drift_pct !== undefined
      ? `${claim.drift_pct}% drift`
      : claim.drift_abs !== undefined
      ? `Δ${claim.drift_abs}`
      : "exceeds tolerance";

  const title = `[doc-drift] ${claim.id}: ${claim.last_value} → ${claim.current_value} (${drift})`;
  const body = [
    `## Doc-Drift Detected`,
    ``,
    `**Claim:** \`${claim.id}\``,
    `**Repo:** ${repoDir}`,
    `**Drift:** ${claim.last_value} → ${claim.current_value} (tolerance: ${claim.tolerance})`,
    `**Deviation:** ${drift}`,
    ``,
    `### Reproduction`,
    `\`\`\`bash`,
    `bun agents/agents/doc-drift-verifier.ts --repo ${repoDir}`,
    `\`\`\``,
    ``,
    `### Resolution`,
    `1. Run verifier to confirm current value`,
    `2. Update README/docs with new value`,
    `3. Update \`.egos-manifest.yaml\` \`last_value\` field`,
    `4. Close this issue with commit reference`,
    ``,
    `*Auto-generated by doc-drift-sentinel — Layer 3 of the EGOS Doc-Drift Shield*`,
  ].join("\n");

  if (mode === "dry") {
    console.log(`  [dry] would open GitHub issue: "${title}"`);
    return -1;
  }

  const { stdout, exitCode } = await run(
    `gh issue create --repo "${repoSlug}" --title "${title.replace(/"/g, "'")}" --body "${body.replace(/"/g, "'")}"`
  );

  if (exitCode !== 0) {
    console.error(`  [sentinel] Failed to open issue for ${repoSlug}/${claim.id}`);
    return null;
  }

  // Extract issue number from URL (gh returns URL like https://github.com/repo/issues/42)
  const match = stdout.match(/\/issues\/(\d+)/);
  const issueNumber = match ? parseInt(match[1]) : -1;

  issueLog.issues.push({
    repo: repoSlug,
    claim_id: claim.id,
    issue_number: issueNumber,
    opened_at: new Date().toISOString(),
  });

  return issueNumber;
}

// ─── Main sentinel runner ─────────────────────────────────────────────────────

async function runSentinel(mode: "dry" | "exec", singleRepo?: string): Promise<SentinelRun> {
  const sentinelRun: SentinelRun = {
    mode,
    started_at: new Date().toISOString(),
    repos_scanned: 0,
    total_drift: 0,
    total_domain_failures: 0,
    actions: [],
    errors: [],
  };

  const issueLog = loadIssueLog();
  const repos = await discoverRepos(singleRepo);

  console.log(`\n🛡️  EGOS Doc-Drift Sentinel — mode: ${mode}`);
  console.log(`📍 Repos found: ${repos.join(", ") || "(none)"}\n`);

  if (repos.length === 0) {
    console.log("[sentinel] No repos with .egos-manifest.yaml found.");
    return sentinelRun;
  }

  for (const repoDir of repos) {
    sentinelRun.repos_scanned++;
    console.log(`\n─── ${repoDir} ───`);

    if (!existsSync(VERIFIER)) {
      sentinelRun.errors.push(`Verifier not found: ${VERIFIER}`);
      continue;
    }

    // Run verifier
    const { stdout, exitCode } = await run(
      `bun "${VERIFIER}" --repo "${repoDir}" --fail-on-drift --json`,
      repoDir,
      120_000
    );

    let report: VerificationReport | null = null;
    try {
      report = JSON.parse(stdout) as VerificationReport;
    } catch {
      sentinelRun.errors.push(`${repoDir}: failed to parse verifier output`);
      console.error(`  [sentinel] ERROR: Could not parse verifier output for ${repoDir}`);
      continue;
    }

    const drifted = report.results.filter((r) => r.status === "drifted");
    const domainFails = report.domains.filter((d) => d.status !== "ok");

    sentinelRun.total_drift += drifted.length;
    sentinelRun.total_domain_failures += domainFails.length;

    if (drifted.length === 0 && domainFails.length === 0) {
      console.log(`  ✅ No drift — all claims and domains clean.`);
      continue;
    }

    // ── Handle drifted claims ──
    if (drifted.length > 0) {
      console.log(`  ⚠️  ${drifted.length} drifted claim(s):`);
      for (const c of drifted) {
        console.log(`     - ${c.id}: ${c.last_value} → ${c.current_value} (${c.tolerance})`);
      }

      const patched = await patchManifest(repoDir, drifted, mode);

      if (patched) {
        const { branchName, pushed } = await commitAndPush(repoDir, drifted, mode);

        if (pushed || mode === "dry") {
          sentinelRun.actions.push(`${repoDir}: patched ${drifted.length} claim(s) → branch ${branchName}`);

          const repoSlug = REPO_GITHUB_MAP[report.repo] ?? `enioxt/${report.repo}`;

          // Open issues for each drifted claim
          for (const claim of drifted) {
            const issueNumber = await openGitHubIssue(
              repoSlug,
              repoDir,
              claim,
              mode,
              issueLog
            );

            // Send Telegram alert
            const drift =
              claim.drift_pct !== undefined ? `${claim.drift_pct}% drift`
              : claim.drift_abs !== undefined ? `Δ${claim.drift_abs}`
              : "exceeded tolerance";

            const telegramMsg = [
              `⚠️ *Doc-Drift Sentinel*`,
              `Repo: \`${report.repo}\``,
              `Claim: \`${claim.id}\``,
              `Drift: ${claim.last_value} → ${claim.current_value} (${drift})`,
              `Branch: \`${branchName}\``,
              issueNumber && issueNumber > 0
                ? `Issue: https://github.com/${repoSlug}/issues/${issueNumber}`
                : "",
            ]
              .filter(Boolean)
              .join("\n");

            await sendTelegram(telegramMsg);
          }
        }
      }
    }

    // ── Handle domain failures ──
    if (domainFails.length > 0) {
      console.log(`  🌐 ${domainFails.length} domain failure(s):`);
      for (const d of domainFails) {
        console.log(`     - ${d.url}: expected ${d.expected_status} got ${d.actual_status}`);
      }

      const telegramMsg = [
        `🔴 *Doc-Drift Sentinel — Domain Failure*`,
        `Repo: \`${report.repo}\``,
        ...domainFails.map((d) => `URL: \`${d.url}\` — expected ${d.expected_status}, got ${d.actual_status}`),
      ].join("\n");

      await sendTelegram(telegramMsg);
      sentinelRun.actions.push(`${repoDir}: alerted on ${domainFails.length} domain failure(s)`);
    }
  }

  saveIssueLog(issueLog, mode);
  return sentinelRun;
}

// ─── Report writer ────────────────────────────────────────────────────────────

function writeReport(run: SentinelRun): void {
  const date = new Date().toISOString().slice(0, 10);
  const reportDir = "/home/enio/egos/docs/jobs";
  const reportPath = join(reportDir, `${date}-doc-drift-sentinel.md`);

  const lines = [
    `# Doc-Drift Sentinel — ${date}`,
    ``,
    `**Mode:** ${run.mode}  `,
    `**Started:** ${run.started_at}  `,
    `**Repos scanned:** ${run.repos_scanned}  `,
    `**Total drift:** ${run.total_drift}  `,
    `**Domain failures:** ${run.total_domain_failures}  `,
    ``,
    `## Actions`,
    run.actions.length > 0
      ? run.actions.map((a) => `- ${a}`).join("\n")
      : "- None (all repos clean)",
    ``,
    `## Errors`,
    run.errors.length > 0
      ? run.errors.map((e) => `- ${e}`).join("\n")
      : "- None",
    ``,
    `---`,
    `*Generated by doc-drift-sentinel.ts — Layer 3 of the EGOS Doc-Drift Shield*`,
  ].join("\n");

  try {
    mkdirSync(reportDir, { recursive: true });
    writeFileSync(reportPath, lines);
    console.log(`\n📄 Report: ${reportPath}`);
  } catch (err) {
    console.error("[sentinel] Failed to write report:", err);
  }
}

// ─── CLI ─────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const mode = args.includes("--exec") ? "exec" : "dry";
const repoIdx = args.indexOf("--repo");
const singleRepo = repoIdx !== -1 ? args[repoIdx + 1] : undefined;

if (mode === "dry") {
  console.log("[sentinel] Running in DRY mode — no writes, no pushes, no alerts");
}

const result = await runSentinel(mode, singleRepo);

console.log(`\n─── Summary ───`);
console.log(`  Repos scanned: ${result.repos_scanned}`);
console.log(`  Claims drifted: ${result.total_drift}`);
console.log(`  Domain failures: ${result.total_domain_failures}`);
console.log(`  Actions: ${result.actions.length}`);
console.log(`  Errors: ${result.errors.length}`);

writeReport(result);

// Always exit 0 — sentinel is non-blocking
process.exit(0);
