/**
 * AGENT-035: Agent Registry Validator v1.0
 *
 * Lightweight validation agent — updates agents/registry/validation.json cache.
 * Does NOT run automatically every time — only on explicit request or agents.json changes.
 *
 * Ground Truth Hierarchy:
 *   1. agents.json — SSOT of definitions (what SHOULD exist)
 *   2. validation.json — SSOT of verification (what WAS confirmed to exist)
 *   3. drift-sentinel — Drift detector (may have false positives)
 *
 * Usage:
 *   bun agents/agents/agent-validator.ts --dry      # Preview, don't write
 *   bun agents/agents/agent-validator.ts --exec     # Validate + update validation.json
 *   bun agents/agents/agent-validator.ts --check    # Check if validation is fresh (< 24h)
 */

import { writeFileSync, readFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import { createHash } from "crypto";

const ROOT = "/home/enio/egos";
const REGISTRY_PATH = join(ROOT, "agents/registry/agents.json");
const VALIDATION_PATH = join(ROOT, "agents/registry/validation.json");

interface AgentValidation {
  id: string;
  entrypoint: string;
  status: string;
  exists: boolean;
  verifiedAt: string;
  validationHash: string;
}

interface ValidationCache {
  $schema?: string;
  version: string;
  description: string;
  lastValidated: string;
  validator: string;
  validationSource: string;
  validationMethod: string;
  agents: AgentValidation[];
  stats: {
    total: number;
    verified: number;
    ghosts: number;
    dead: number;
    orphanFiles: number;
  };
  globalHash: string;
}

function sha256(content: string): string {
  return createHash("sha256").update(content).digest("hex").slice(0, 16);
}

function log(level: "info" | "warn" | "error", msg: string) {
  const icon = level === "info" ? "ℹ️" : level === "warn" ? "⚠️" : "❌";
  console.log(`${icon} ${msg}`);
}

function validateAgent(agent: any): AgentValidation {
  const entrypoint = agent.entrypoint || "";
  const fullPath = join(ROOT, entrypoint);
  const exists = existsSync(fullPath);
  const content = exists ? readFileSync(fullPath, "utf-8").slice(0, 100) : "";
  const validationHash = sha256(`${agent.id}:${entrypoint}:${exists}:${content}`);

  return {
    id: agent.id,
    entrypoint,
    status: agent.status || "unknown",
    exists,
    verifiedAt: new Date().toISOString(),
    validationHash: `sha256:${validationHash}`,
  };
}

function runValidation(mode: "dry" | "exec" | "check"): void {
  log("info", `Agent Registry Validator — mode: ${mode}`);

  // Check if validation is fresh (for --check mode)
  if (mode === "check") {
    if (!existsSync(VALIDATION_PATH)) {
      log("warn", "No validation cache found. Run with --exec to create.");
      process.exit(1);
    }
    const cache: ValidationCache = JSON.parse(readFileSync(VALIDATION_PATH, "utf-8"));
    const lastValidated = new Date(cache.lastValidated).getTime();
    const now = Date.now();
    const hoursSince = (now - lastValidated) / (1000 * 60 * 60);

    if (hoursSince < 24) {
      log("info", `Validation cache is fresh (${hoursSince.toFixed(1)}h old).`);
      log("info", `Stats: ${cache.stats.verified}/${cache.stats.total} verified, ${cache.stats.ghosts} ghosts`);
      process.exit(0);
    } else {
      log("warn", `Validation cache is stale (${hoursSince.toFixed(1)}h old). Run --exec to update.`);
      process.exit(1);
    }
  }

  // Load registry
  if (!existsSync(REGISTRY_PATH)) {
    log("error", `Registry not found: ${REGISTRY_PATH}`);
    process.exit(2);
  }

  const registry = JSON.parse(readFileSync(REGISTRY_PATH, "utf-8"));
  const agents = registry.agents || [];

  log("info", `Validating ${agents.length} agents from registry...`);

  // Validate each agent
  const validations: AgentValidation[] = [];
  let ghosts = 0;
  let dead = 0;

  for (const agent of agents) {
    const validation = validateAgent(agent);
    validations.push(validation);

    if (agent.status === "dead") {
      dead++;
      log("info", `  ⚠️ ${agent.id}: status=dead (intentionally removed)`);
    } else if (!validation.exists) {
      ghosts++;
      log("warn", `  ❌ ${agent.id}: MISSING at ${validation.entrypoint}`);
    } else {
      log("info", `  ✅ ${agent.id}: exists at ${validation.entrypoint}`);
    }
  }

  // Build cache
  const cache: ValidationCache = {
    version: "1.0.0",
    description: "EGOS Agent Registry Validation Cache — Lightweight provenance for agent existence checks",
    lastValidated: new Date().toISOString(),
    validator: "agent-validator",
    validationSource: REGISTRY_PATH,
    validationMethod: "4-point-check",
    agents: validations,
    stats: {
      total: agents.length,
      verified: validations.filter(v => v.exists).length,
      ghosts,
      dead,
      orphanFiles: 0, // TODO: Check for files in agents/agents/ not in registry
    },
    globalHash: `sha256:${sha256(JSON.stringify(validations))}`,
  };

  // Output summary
  console.log("\n📊 Validation Summary:");
  console.log(`  Total agents: ${cache.stats.total}`);
  console.log(`  Verified alive: ${cache.stats.verified}`);
  console.log(`  Dead (intentional): ${cache.stats.dead}`);
  console.log(`  Ghosts (missing): ${cache.stats.ghosts}`);

  if (mode === "exec") {
    writeFileSync(VALIDATION_PATH, JSON.stringify(cache, null, 2));
    log("info", `\n✅ Validation cache written to: ${VALIDATION_PATH}`);
  } else {
    log("info", `\n💡 Dry run — use --exec to write cache`);
  }

  // Exit with error if ghosts found (unless all are dead)
  const realGhosts = ghosts;
  if (realGhosts > 0) {
    log("error", `\nFound ${realGhosts} ghost agent(s)!`);
    process.exit(1);
  }
}

// Entry point
const args = process.argv.slice(2);
const mode: "dry" | "exec" | "check" = args.includes("--exec") ? "exec" : args.includes("--check") ? "check" : "dry";

runValidation(mode);
