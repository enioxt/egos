#!/usr/bin/env bun
/**
 * EGOS Demo Lane — Reproducible demonstration script (EGOS-118)
 *
 * Runs a self-contained demo showing Guard Brasil + agent runtime capabilities.
 * Designed for meetings and presentations — offline-capable, deterministic output.
 *
 * Usage:
 *   bun scripts/demo.ts              # Full demo
 *   bun scripts/demo.ts --guard      # Guard Brasil only
 *   bun scripts/demo.ts --agents     # Agent system only
 *   bun scripts/demo.ts --routing    # LLM routing only
 */

import { createGuardBrasil } from '../packages/shared/src/guard-brasil';
import { createAtrianValidator } from '../packages/shared/src/atrian';
import { scanForPII, sanitizeText, getPIISummary } from '../packages/shared/src/pii-scanner';
import { resolveModel, listAvailableModels } from '../packages/shared/src/model-router';
import { createEvidenceChain, formatEvidenceBlock } from '../packages/shared/src/evidence-chain';
import { detectRepoRole, roleDescription } from '../packages/shared/src/repo-role';
import { resolve } from 'path';

const DIVIDER = '═'.repeat(60);
const args = process.argv.slice(2);
const showAll = args.length === 0;
const showGuard = showAll || args.includes('--guard');
const showAgents = showAll || args.includes('--agents');
const showRouting = showAll || args.includes('--routing');

console.log(`
${DIVIDER}
  EGOS — Governance-First AI Agent Orchestration
  Demo Lane v1.0.0
${DIVIDER}
`);

// ── 1. Guard Brasil Demo ──
if (showGuard) {
  console.log('▶ GUARD BRASIL — Brazilian AI Safety Layer\n');

  const guard = createGuardBrasil({
    atrian: {
      knownAcronyms: ['CPF', 'CNPJ', 'LGPD', 'RG', 'PNCP', 'TSE'],
      blockedEntities: ['Teste Bloqueado'],
    },
    minAtrianScore: 60,
  });

  // Test 1: Clean text
  const clean = guard.validate('De acordo com os dados públicos, a empresa está ativa desde 2020.');
  console.log(`  ✅ Clean text → safe: ${clean.safe}, score: ${clean.atrianScore}/100`);

  // Test 2: PII detected
  const pii = guard.validate('O titular João, CPF 123.456.789-00, telefone (31) 99876-5432.');
  console.log(`  🔒 PII detected → safe: ${pii.safe}, PII count: ${pii.piiCount}, sensitivity: ${pii.sensitivityLevel}`);
  console.log(`     Masked: "${pii.maskedText.slice(0, 80)}..."`);
  console.log(`     LGPD: ${pii.lgpdDisclosure.slice(0, 80)}...`);

  // Test 3: Ethical violation
  const ethical = guard.validate('Com certeza vamos resolver. Segundo dados da pesquisa, 100% melhoraram.');
  console.log(`  ⚠️  Ethical violation → safe: ${ethical.safe}, score: ${ethical.atrianScore}/100`);

  // Test 4: Evidence Chain
  const chain = createEvidenceChain({ sessionId: 'demo-001' })
    .addToolCallClaim('Empresa XYZ tem CNPJ ativo', 'cnpj_query', '{"status":"ATIVA","since":"2020"}', 'high')
    .addDocumentClaim('Licitação PNCP-2026-001 acima do valor de mercado', 'PNCP', 'R$ 2.5M vs média R$ 800K', 'medium')
    .build();
  console.log(`  📋 Evidence Chain → ${chain.claims.length} claims, confidence: ${chain.overallConfidence}, hash: ${chain.auditHash}`);

  console.log('');
}

// ── 2. Agent System Demo ──
if (showAgents) {
  console.log('▶ AGENT RUNTIME — Registry-Based Execution\n');

  const repoRoot = resolve(import.meta.dir, '..');
  const role = detectRepoRole(repoRoot);
  console.log(`  📍 Repo: ${role.role} (${role.version})`);

  // Read agent registry
  const registryPath = resolve(repoRoot, 'agents/registry/agents.json');
  const registry = JSON.parse(await Bun.file(registryPath).text());
  console.log(`  🤖 Agents: ${registry.agents.length} registered`);

  for (const agent of registry.agents.slice(0, 5)) {
    const modes = agent.run_modes.join('/');
    console.log(`     ${agent.id.padEnd(28)} [${agent.area}] ${modes}`);
  }
  console.log(`     ... and ${registry.agents.length - 5} more`);

  console.log('');
}

// ── 3. LLM Routing Demo ──
if (showRouting) {
  console.log('▶ LLM ROUTING — Cheap-First Cost-Aware Selection\n');

  const tasks = ['fast_check', 'chat', 'code_generation', 'orchestration'] as const;
  const hasAlibaba = !!process.env.ALIBABA_DASHSCOPE_API_KEY;
  const hasOpenRouter = !!process.env.OPENROUTER_API_KEY;

  console.log(`  Providers: Alibaba ${hasAlibaba ? '✅' : '❌'} | OpenRouter ${hasOpenRouter ? '✅' : '❌'}`);

  if (hasAlibaba || hasOpenRouter) {
    for (const task of tasks) {
      try {
        const route = resolveModel(task);
        const cost = ((route.profile.costPer1MInput + route.profile.costPer1MOutput) / 2).toFixed(2);
        console.log(`  ${task.padEnd(20)} → ${route.profile.displayName.padEnd(20)} [${route.profile.tier}] $${cost}/1M`);
      } catch {
        console.log(`  ${task.padEnd(20)} → No provider available`);
      }
    }
  } else {
    console.log('  ⚠️  Set ALIBABA_DASHSCOPE_API_KEY or OPENROUTER_API_KEY for live routing demo');
    console.log('  Showing catalog instead:');
    const models = listAvailableModels();
    for (const m of models.slice(0, 4)) {
      console.log(`     ${m.displayName.padEnd(20)} [${m.tier}] ${m.available ? '✅' : '❌'}`);
    }
  }

  console.log('');
}

// ── Summary ──
console.log(`${DIVIDER}`);
console.log('  ✅ Demo complete. All operations run locally — no API calls made.');
console.log(`  📊 162 tests | 14 modules | 10 agents | MIT license`);
console.log(`  🌐 egos.ia.br | github.com/enioxt/egos`);
console.log(`${DIVIDER}`);
