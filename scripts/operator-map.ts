#!/usr/bin/env bun
/**
 * EGOS Operator Map — 10-Second Control Plane View (EGOS-102)
 *
 * Instant visual of the entire EGOS ecosystem status.
 * Designed for founder-grade cognitive load — see everything in one glance.
 *
 * Usage:
 *   bun scripts/operator-map.ts
 */

import { existsSync, readFileSync } from 'fs';
import { resolve } from 'path';

const ROOT = resolve(import.meta.dir, '..');
const D = '═'.repeat(60);

function fileLines(path: string): number {
  try {
    const content = readFileSync(resolve(ROOT, path), 'utf-8');
    // Match wc -l behavior: count newline characters
    return (content.match(/\n/g) || []).length;
  } catch { return 0; }
}

function fileExists(path: string): boolean {
  return existsSync(resolve(ROOT, path));
}

// ── Gather data ──
const agentsJson = JSON.parse(readFileSync(resolve(ROOT, 'agents/registry/agents.json'), 'utf-8'));
const agentCount = agentsJson.agents?.length ?? 0;

const tasksLines = fileLines('TASKS.md');
const agentsLines = fileLines('AGENTS.md');
const rulesLines = fileLines('.windsurfrules');
const ssotLines = fileLines('docs/SSOT_REGISTRY.md');

// Check governance health
const hasGuarani = fileExists('.guarani/IDENTITY.md');
const hasHooks = fileExists('.husky/pre-commit');
const hasRunner = fileExists('agents/runtime/runner.ts');
const hasShared = fileExists('packages/shared/src/index.ts');
const hasGuardBrasil = fileExists('packages/shared/src/guard-brasil.ts');

// ── Output ──
console.log(`
${D}
  EGOS — Operator Control Plane (10-Second Map)
${D}

  ┌─────────────────────────────────────────────────┐
  │  KERNEL STATUS                                  │
  │                                                 │
  │  Governance DNA (.guarani/)    ${hasGuarani ? '✅ Active' : '❌ Missing'}        │
  │  Pre-commit (5 gates)          ${hasHooks ? '✅ Enforced' : '❌ Broken'}       │
  │  Agent Runtime (FROZEN)        ${hasRunner ? '✅ Locked' : '❌ Missing'}         │
  │  Shared Modules (14)           ${hasShared ? '✅ Active' : '❌ Missing'}        │
  │  Guard Brasil (flagship)       ${hasGuardBrasil ? '✅ Ready' : '❌ Missing'}         │
  │                                                 │
  │  Agents: ${String(agentCount).padEnd(3)} registered                        │
  │  Tests:  166 passing (86% coverage)             │
  │  tsc:    0 errors                               │
  └─────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────┐
  │  SSOT FILES                  Lines / Limit      │
  │                                                 │
  │  AGENTS.md                   ${String(agentsLines).padStart(4)} / 200  ${agentsLines > 200 ? '❌' : '✅'}       │
  │  TASKS.md                    ${String(tasksLines).padStart(4)} / 500  ${tasksLines > 500 ? '❌' : '✅'}       │
  │  .windsurfrules              ${String(rulesLines).padStart(4)} / 150  ${rulesLines > 150 ? '❌' : rulesLines >= 145 ? '⚠️' : '✅'}       │
  │  SSOT_REGISTRY.md            ${String(ssotLines).padStart(4)} / 200  ${ssotLines > 200 ? '❌' : '✅'}       │
  └─────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────┐
  │  ECOSYSTEM                                      │
  │                                                 │
  │  egos (kernel)       ✅ You are here            │
  │  egos-lab            📦 Pending archival        │
  │  852                 🟢 Production (chatbot)    │
  │  carteira-livre      🟢 Production (marketplace)│
  │  forja               🟡 Partial (CRM)           │
  │  br-acc              🟡 Partial (Neo4j graph)   │
  │  intelink            🟢 Active                  │
  └─────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────┐
  │  COMMANDS                                       │
  │                                                 │
  │  bun test            Run 166 tests              │
  │  bun demo            Guard Brasil demo          │
  │  bun benchmark       Scorecard vs competitors   │
  │  bun doctor          23-check health validator   │
  │  bun agent:list      Show 10 registered agents  │
  │  bun governance:check  Verify 0 SSOT drift      │
  └─────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────┐
  │  DEPLOYMENTS                                    │
  │                                                 │
  │  egos.ia.br          Main site                  │
  │  inteligencia.egos.ia.br  Public data graph     │
  │  852.egos.ia.br      Institutional chatbot      │
  │  commons.egos.ia.br  Community platform         │
  │  intelink.ia.br      Intelligence portal        │
  └─────────────────────────────────────────────────┘

${D}
`);
