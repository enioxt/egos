#!/usr/bin/env bun
/**
 * scripts/paperclip-register-agents.ts — DASH-004
 *
 * Registers EGOS agents as Paperclip "employees" via the Paperclip API.
 * Reads agents.json registry and POSTs each agent to Paperclip.
 *
 * Usage:
 *   bun scripts/paperclip-register-agents.ts [--dry] [--url http://localhost:3100]
 *
 * Prerequisites:
 *   - Paperclip running (DASH-002 ✅)
 *   - PAPERCLIP_API_TOKEN env var set (get from Paperclip UI → Settings → API)
 *   - feat/external-adapter-phase1 merged into Paperclip main
 *
 * Status: BLOCKED on feat/external-adapter-phase1 — adapter registration API
 *         not yet available in Paperclip main. See docs/PAPERCLIP_ORG.md.
 */

import { existsSync, readFileSync } from "node:fs";
import { join, dirname } from "node:path";

const REPO_ROOT = join(dirname(import.meta.path), "..");
const AGENTS_JSON = join(REPO_ROOT, "agents/registry/agents.json");
const ORG_DOC = join(REPO_ROOT, "docs/PAPERCLIP_ORG.md");

const DRY = process.argv.includes("--dry");
const PAPERCLIP_URL = process.argv.find(a => a.startsWith("--url="))?.replace("--url=", "")
  ?? process.env.PAPERCLIP_URL
  ?? "http://localhost:3100";
const API_TOKEN = process.env.PAPERCLIP_API_TOKEN ?? "";

// EGOS org chart (from PAPERCLIP_ORG.md canonical)
const ORG_CHART = [
  { id: "egos-kernel", title: "EGOS Kernel", role: "CEO", reports_to: null },
  { id: "guard-brasil", title: "Guard Brasil API", role: "Director", reports_to: "egos-kernel" },
  { id: "gem-hunter", title: "Gem Hunter", role: "Director", reports_to: "egos-kernel" },
  { id: "codebase-miner", title: "Codebase Archaeologist", role: "IC", reports_to: "egos-kernel" },
  { id: "doc-drift-sentinel", title: "Doc Drift Sentinel", role: "IC", reports_to: "egos-kernel" },
  { id: "disseminate-propagator", title: "Disseminate Propagator", role: "IC", reports_to: "egos-kernel" },
] as const;

interface AgentRegistration {
  id: string;
  name: string;
  title: string;
  role: string;
  adapter_type: string;
  reports_to: string | null;
  description: string;
}

async function checkPaperclipHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${PAPERCLIP_URL}/health`, { signal: AbortSignal.timeout(5000) });
    return res.ok;
  } catch {
    return false;
  }
}

async function registerAgent(agent: AgentRegistration): Promise<void> {
  if (DRY) {
    console.log(`  [DRY] Would register: ${agent.id} (${agent.role}) → reports to: ${agent.reports_to ?? "human"}`);
    return;
  }

  // NOTE: This endpoint path is speculative — depends on feat/external-adapter-phase1 API.
  // Update when the PR merges and API contract is published.
  const res = await fetch(`${PAPERCLIP_URL}/api/agents`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${API_TOKEN}`,
    },
    body: JSON.stringify({
      externalId: agent.id,
      name: agent.name,
      jobTitle: agent.title,
      adapterType: agent.adapter_type,
      reportsTo: agent.reports_to,
      description: agent.description,
    }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Failed to register ${agent.id}: ${res.status} ${body}`);
  }

  console.log(`  ✅ Registered: ${agent.id}`);
}

async function main() {
  console.log("[paperclip-register] DASH-004 — EGOS agents → Paperclip employees");
  console.log(`  URL: ${PAPERCLIP_URL}`);
  console.log(`  Mode: ${DRY ? "DRY RUN" : "LIVE"}`);
  console.log("");

  // Check Paperclip is running
  const healthy = await checkPaperclipHealth();
  if (!healthy) {
    console.error(`[paperclip-register] ❌ Paperclip not reachable at ${PAPERCLIP_URL}`);
    console.error("  Start it: docker compose -f infra/docker-compose.paperclip.yml up -d");
    process.exit(1);
  }

  if (!DRY && !API_TOKEN) {
    console.error("[paperclip-register] ❌ PAPERCLIP_API_TOKEN not set");
    console.error("  Get it from: Paperclip UI → Settings → API Keys");
    process.exit(1);
  }

  // Load agents.json for descriptions
  let agentsJson: Record<string, unknown> = {};
  if (existsSync(AGENTS_JSON)) {
    agentsJson = JSON.parse(readFileSync(AGENTS_JSON, "utf-8"));
  }

  console.log(`[paperclip-register] Registering ${ORG_CHART.length} EGOS agents...`);
  let success = 0;
  let failed = 0;

  for (const entry of ORG_CHART) {
    const registration: AgentRegistration = {
      id: entry.id,
      name: entry.id,
      title: entry.title,
      role: entry.role,
      adapter_type: "custom/egos",
      reports_to: entry.reports_to,
      description: `EGOS ${entry.role} — managed by Guard Brasil compliance layer`,
    };

    try {
      await registerAgent(registration);
      success++;
    } catch (err) {
      console.error(`  ❌ ${entry.id}: ${err}`);
      failed++;
    }
  }

  console.log(`\n[paperclip-register] Done: ${success} registered / ${failed} failed`);

  if (!DRY) {
    console.log("\nNext steps:");
    console.log("  1. Open Paperclip UI → verify agents appear in org chart");
    console.log("  2. Assign job descriptions and heartbeat schedules");
    console.log("  3. Run DASH-006 to add Guard Brasil compliance plugin");
  }
}

main().catch(err => {
  console.error("[paperclip-register] Fatal:", err);
  process.exit(1);
});
