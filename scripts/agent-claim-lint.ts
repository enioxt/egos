#!/usr/bin/env bun
/**
 * agent-claim-lint.ts — EGOS-079: Agent Claim Gate
 *
 * Validates agents/registry/agents.json against the Agent Claim Contract
 * (EGOS-078). Enforces proof requirements per `kind`.
 *
 * Exit codes:
 *   0 — all checks pass (warnings may be emitted)
 *   1 — one or more verified_agent / online_agent entries fail required proofs
 *
 * Usage:
 *   bun scripts/agent-claim-lint.ts
 *   bun scripts/agent-claim-lint.ts --strict   # treat warnings as errors
 */

import { existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type Kind =
  | "verified_agent"
  | "online_agent"
  | "agent_candidate"
  | "workflow"
  | "tool"
  | "dormant";

interface AgentEntry {
  id: string;
  name: string;
  kind: Kind;
  entrypoint?: string;
  runtime_proof?: string;
  loop_mechanism?: string;
  eval_suite?: string[];
  last_duration_ms?: number;
  telemetry_source?: string;
  owner?: string;
  triggers?: string[];
  [key: string]: unknown;
}

interface Registry {
  version: string;
  agents: AgentEntry[];
}

interface LintResult {
  id: string;
  kind: Kind;
  errors: string[];
  warnings: string[];
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const args = process.argv.slice(2);
const STRICT = args.includes("--strict");

// Resolve registry path relative to this script's location
const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(SCRIPT_DIR, "..");
const REGISTRY_PATH = resolve(REPO_ROOT, "agents/registry/agents.json");

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function entrypointExists(entry: AgentEntry): boolean {
  if (!entry.entrypoint) return false;
  return existsSync(resolve(REPO_ROOT, entry.entrypoint));
}

function hasRuntimeProof(entry: AgentEntry): boolean {
  return typeof entry.runtime_proof === "string" && entry.runtime_proof.trim().length > 0;
}

function hasLoop(entry: AgentEntry): boolean {
  return (
    typeof entry.loop_mechanism === "string" &&
    entry.loop_mechanism !== "none" &&
    entry.loop_mechanism.trim().length > 0
  );
}

function hasEvals(entry: AgentEntry): boolean {
  return Array.isArray(entry.eval_suite) && entry.eval_suite.length > 0;
}

function hasDuration(entry: AgentEntry): boolean {
  return typeof entry.last_duration_ms === "number" && entry.last_duration_ms >= 0;
}

function hasTelemetry(entry: AgentEntry): boolean {
  return typeof entry.telemetry_source === "string" && entry.telemetry_source.trim().length > 0;
}

function hasOwner(entry: AgentEntry): boolean {
  return typeof entry.owner === "string" && entry.owner.trim().length > 0;
}

// ---------------------------------------------------------------------------
// Lint rules per kind
// ---------------------------------------------------------------------------

function lintEntry(entry: AgentEntry): LintResult {
  const result: LintResult = { id: entry.id, kind: entry.kind, errors: [], warnings: [] };
  const err = (msg: string) => result.errors.push(msg);
  const warn = (msg: string) => result.warnings.push(msg);

  // Owner is required for all kinds
  if (!hasOwner(entry)) err("missing `owner` field");

  // Entrypoint must exist on disk for all kinds (except dormant — warn only)
  if (entry.kind === "dormant") {
    if (entry.entrypoint && !entrypointExists(entry)) {
      warn(`entrypoint not found on disk: ${entry.entrypoint}`);
    }
    return result; // dormant: no further checks
  }

  if (!entry.entrypoint) {
    err("missing `entrypoint` field");
  } else if (!entrypointExists(entry)) {
    err(`entrypoint not found on disk: ${entry.entrypoint}`);
  }

  switch (entry.kind) {
    // -----------------------------------------------------------------------
    case "tool":
    case "workflow": {
      if (!hasRuntimeProof(entry)) warn("missing `runtime_proof` — recommended for tools/workflows");
      break;
    }

    // -----------------------------------------------------------------------
    case "agent_candidate": {
      if (!hasRuntimeProof(entry)) warn("missing `runtime_proof` — agent_candidate should have proof");
      if (!hasLoop(entry)) {
        err("`loop_mechanism` must be non-`none` for agent_candidate — if no loop exists, downgrade to `tool`");
      }
      if (!hasTelemetry(entry)) warn("missing `telemetry_source` — observability required before promotion");
      break;
    }

    // -----------------------------------------------------------------------
    case "verified_agent": {
      if (!hasRuntimeProof(entry)) err("missing `runtime_proof` — required for verified_agent");
      if (!hasLoop(entry)) err("`loop_mechanism` must be non-`none` for verified_agent");
      if (!hasEvals(entry)) err("`eval_suite` must be non-empty for verified_agent");
      if (!hasDuration(entry)) err("`last_duration_ms` must be ≥ 0 (real measurement) for verified_agent");
      if (!hasTelemetry(entry)) warn("`telemetry_source` should be a persistent sink (not just stdout) for verified_agent");
      break;
    }

    // -----------------------------------------------------------------------
    case "online_agent": {
      if (!hasRuntimeProof(entry)) err("missing `runtime_proof` (health endpoint or live log) — required for online_agent");
      if (!hasLoop(entry)) err("`loop_mechanism` must be non-`none` for online_agent");
      if (!hasEvals(entry)) err("`eval_suite` must be non-empty for online_agent");
      if (!hasDuration(entry)) err("`last_duration_ms` must be ≥ 0 for online_agent");
      if (!hasTelemetry(entry)) err("`telemetry_source` must point to a persistent sink for online_agent");
      // For online_agent, loop_mechanism must be one of the active kinds
      if (
        entry.loop_mechanism &&
        !["cron", "event_driven", "while_loop"].includes(entry.loop_mechanism)
      ) {
        err(
          `\`loop_mechanism\` for online_agent must be cron | event_driven | while_loop, got: ${entry.loop_mechanism}`
        );
      }
      break;
    }
  }

  return result;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  if (!existsSync(REGISTRY_PATH)) {
    console.error(`[agent-claim-lint] ERROR: registry not found at ${REGISTRY_PATH}`);
    process.exit(1);
  }

  const registry: Registry = JSON.parse(require("fs").readFileSync(REGISTRY_PATH, "utf-8"));
  const entries: AgentEntry[] = registry.agents ?? [];

  if (entries.length === 0) {
    console.log("[agent-claim-lint] WARNING: registry has 0 entries");
    process.exit(0);
  }

  const results: LintResult[] = entries.map(lintEntry);

  // Tally
  let totalErrors = 0;
  let totalWarnings = 0;
  const byKind: Record<string, number> = {};

  for (const r of results) {
    byKind[r.kind] = (byKind[r.kind] ?? 0) + 1;
    totalErrors += r.errors.length;
    totalWarnings += r.warnings.length;
  }

  // Print summary header
  console.log(`\n[agent-claim-lint] EGOS Agent Claim Gate — registry v${registry.version}`);
  console.log(`  Entries: ${entries.length}`);
  for (const [kind, count] of Object.entries(byKind)) {
    console.log(`    ${kind}: ${count}`);
  }
  console.log("");

  // Print results
  for (const r of results) {
    const hasIssues = r.errors.length > 0 || r.warnings.length > 0;
    if (!hasIssues) {
      console.log(`  [OK]   ${r.id} (${r.kind})`);
      continue;
    }
    for (const e of r.errors) {
      console.log(`  [ERR]  ${r.id} (${r.kind}): ${e}`);
    }
    for (const w of r.warnings) {
      console.log(`  [WARN] ${r.id} (${r.kind}): ${w}`);
    }
  }

  // Final verdict
  const effectiveErrors = STRICT ? totalErrors + totalWarnings : totalErrors;
  console.log("");
  if (effectiveErrors === 0) {
    console.log(
      `[agent-claim-lint] PASS — ${entries.length} entries checked, ${totalWarnings} warning(s)${STRICT ? " (strict mode)" : ""}`
    );
    process.exit(0);
  } else {
    console.log(
      `[agent-claim-lint] FAIL — ${totalErrors} error(s), ${totalWarnings} warning(s)${STRICT ? " (strict mode)" : ""}`
    );
    console.log(
      "  Fix: verified_agent and online_agent require runtime_proof, loop_mechanism, eval_suite, and last_duration_ms."
    );
    console.log(
      "  Downgrade kind to agent_candidate or tool if proof is unavailable."
    );
    process.exit(1);
  }
}

main();
