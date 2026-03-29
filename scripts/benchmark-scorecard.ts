#!/usr/bin/env bun
/**
 * EGOS Benchmark Scorecard — EGOS-119
 *
 * Compares EGOS governance capabilities against competing frameworks.
 * Based on documented features (not benchmarker agent fetch — this is static/deterministic).
 *
 * Usage:
 *   bun scripts/benchmark-scorecard.ts
 *   bun scripts/benchmark-scorecard.ts --json
 */

interface FrameworkScore {
  name: string;
  governance: number;      // 0-10
  multiRepo: number;       // 0-10
  compliance: number;      // 0-10
  costControl: number;     // 0-10
  testInfra: number;       // 0-10
  agentRuntime: number;    // 0-10
  total: number;           // sum
  notes: string;
}

const CATEGORIES = [
  'governance', 'multiRepo', 'compliance', 'costControl', 'testInfra', 'agentRuntime',
] as const;

const CATEGORY_LABELS: Record<string, string> = {
  governance: 'Governance-as-Code',
  multiRepo: 'Multi-Repo Sync',
  compliance: 'Compliance (LGPD/PII)',
  costControl: 'Cost Control',
  testInfra: 'Test Infrastructure',
  agentRuntime: 'Agent Runtime',
};

// Scores based on documented features (not subjective — each point has evidence)
const FRAMEWORKS: FrameworkScore[] = [
  {
    name: 'EGOS',
    governance: 9,      // Pre-commit 5 gates, frozen zones, SSOT registry, governance sync
    multiRepo: 9,       // Symlink propagation, governance-sync.sh, 7+ repos consuming
    compliance: 9,       // ATRiAN 7 axioms, PII scanner, Public Guard, LGPD masking
    costControl: 8,      // Cheap-first routing, MODEL_COSTS map, metrics tracker, telemetry
    testInfra: 8,        // 166 tests, behavioral, E2E spec-pipeline
    agentRuntime: 7,     // 10 agents, registry, runner, event-bus, dry-run
    total: 0,
    notes: 'Governance-first. Brazilian compliance leader. Pre-commit enforcement unique.',
  },
  {
    name: 'LangChain/LangGraph',
    governance: 2,       // No pre-commit, no governance layer, no SSOT
    multiRepo: 1,        // Single-repo focused
    compliance: 2,       // Basic output parsers, no PII/LGPD native
    costControl: 5,      // Token counting, callbacks, but no routing policy
    testInfra: 7,        // Good test ecosystem, pytest integration
    agentRuntime: 9,     // Excellent agent communication, graph execution
    total: 0,
    notes: 'Best agent communication. No governance layer.',
  },
  {
    name: 'CrewAI',
    governance: 3,       // Role-based but loose, no enforcement gates
    multiRepo: 1,        // Single-repo
    compliance: 1,       // No native compliance
    costControl: 4,      // Basic cost tracking
    testInfra: 5,        // Standard Python testing
    agentRuntime: 8,     // Role-based agents, task delegation
    total: 0,
    notes: 'Fun and fast. Weak governance and compliance.',
  },
  {
    name: 'AutoGen (Microsoft)',
    governance: 4,       // Some conversation policies, no pre-commit
    multiRepo: 2,        // Single-repo with workspace concept
    compliance: 2,       // No native compliance
    costControl: 5,      // Budget tracking per agent
    testInfra: 6,        // Good testing support
    agentRuntime: 8,     // Multi-agent conversation, code execution
    total: 0,
    notes: 'Strong multi-agent. Growing governance features.',
  },
  {
    name: 'Cursor/Windsurf',
    governance: 3,       // .cursorrules / .windsurfrules (rules files only)
    multiRepo: 1,        // IDE-scoped, single workspace
    compliance: 1,       // No compliance layer
    costControl: 2,      // IDE subscription model, no per-call tracking
    testInfra: 3,        // IDE-assisted but no framework
    agentRuntime: 6,     // IDE-embedded agents, edit-time only
    total: 0,
    notes: 'Edit-time governance only. No runtime enforcement.',
  },
];

// Calculate totals
for (const f of FRAMEWORKS) {
  f.total = CATEGORIES.reduce((sum, cat) => sum + f[cat], 0);
}

// Sort by total
FRAMEWORKS.sort((a, b) => b.total - a.total);

// Output
const jsonMode = process.argv.includes('--json');

if (jsonMode) {
  console.log(JSON.stringify({ frameworks: FRAMEWORKS, categories: CATEGORY_LABELS }, null, 2));
} else {
  console.log('\n📊 EGOS Benchmark Scorecard (EGOS-119)\n');
  console.log('  Scores: 0-10 per category. Based on documented features.\n');

  // Header
  const nameWidth = 22;
  const colWidth = 6;
  const header = '  ' + 'Framework'.padEnd(nameWidth) +
    CATEGORIES.map(c => CATEGORY_LABELS[c].slice(0, 5).padStart(colWidth)).join('') +
    '  TOTAL';
  console.log(header);
  console.log('  ' + '─'.repeat(header.length));

  // Rows
  for (const f of FRAMEWORKS) {
    const isEgos = f.name === 'EGOS';
    const prefix = isEgos ? '▸ ' : '  ';
    const scores = CATEGORIES.map(c => String(f[c]).padStart(colWidth)).join('');
    const total = `  ${f.total}/60`;
    console.log(`${prefix}${f.name.padEnd(nameWidth)}${scores}${total}${isEgos ? ' ★' : ''}`);
  }

  console.log('\n  Categories: Gover=Governance, Multi=Multi-Repo, Compl=Compliance,');
  console.log('              CostC=CostControl, TestI=TestInfra, Agent=AgentRuntime\n');

  // EGOS advantages
  console.log('  🏆 EGOS Unique Advantages:');
  console.log('     • Only framework with pre-commit rule enforcement');
  console.log('     • Only framework with multi-repo symlink governance propagation');
  console.log('     • Only framework with native Brazilian LGPD/PII compliance');
  console.log('     • Only framework with ATRiAN post-response ethical validation');
  console.log('     • Only framework with frozen zone protection for core runtime\n');
}
