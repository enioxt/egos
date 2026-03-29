/**
 * Agent CLI — Entry point for all agent operations
 * 
 * Usage:
 *   bun agents/cli.ts list
 *   bun agents/cli.ts run <agent_id> --dry
 *   bun agents/cli.ts run <agent_id> --exec
 *   bun agents/cli.ts lint-registry
 */

import { resolve } from 'node:path';
import { listAgents } from './runtime/runner';

const args = process.argv.slice(2);
const command = args[0];
const repoRoot = resolve(import.meta.dir, '..');

switch (command) {
  case 'list': {
    const agents = listAgents();
    console.log('\n📋 Registered Agents:\n');
    console.log('  ID                     | Area           | Status      | Modes');
    console.log('  ' + '─'.repeat(80));
    for (const a of agents) {
      const id = a.id.padEnd(23);
      const area = a.area.padEnd(15);
      const status = a.status.padEnd(12);
      const modes = a.run_modes.join(', ');
      console.log(`  ${id}| ${area}| ${status}| ${modes}`);
    }
    console.log(`\n  Total: ${agents.length} agents\n`);
    break;
  }

  case 'run': {
    const agentId = args[1];
    if (!agentId) {
      console.error('Usage: bun agents/cli.ts run <agent_id> [--dry|--exec]');
      process.exit(1);
    }
    const forwardedArgs = args.slice(2);
    if (!forwardedArgs.includes('--exec') && !forwardedArgs.includes('--dry')) {
      forwardedArgs.unshift('--dry');
    }
    // Delegate to the agent's own entrypoint
    const agent = listAgents().find(a => a.id === agentId);
    if (!agent) {
      console.error(`Agent "${agentId}" not found. Run "bun agents/cli.ts list" to see available agents.`);
      process.exit(1);
    }
    const entrypoint = resolve(repoRoot, agent.entrypoint);
    console.log(`\n🚀 Delegating to: bun ${entrypoint} ${forwardedArgs.join(' ')}\n`);
    const { spawnSync } = await import('child_process');
    const result = spawnSync('bun', [entrypoint, ...forwardedArgs], {
      cwd: process.cwd(),
      stdio: 'inherit',
    });
    process.exit(result.status ?? 1);
  }

  case 'lint-registry': {
    const agents = listAgents();
    let errors = 0;
    let warnings = 0;
    console.log('\n🔍 Linting agent registry (with Agent Claim Contract)...\n');

    const seenIds = new Set<string>();

    for (const a of agents) {
      // === L2 Required Fields (Agent Claim Contract) ===
      if (!a.id || !a.name || !a.area || !a.entrypoint) {
        console.error(`  ❌ [L2] Agent missing required fields: ${JSON.stringify(a)}`);
        errors++;
      }
      if (!['T0', 'T1', 'T2', 'T3'].includes(a.risk_level)) {
        console.error(`  ❌ [L2] Agent "${a.id}" has invalid risk_level: ${a.risk_level}`);
        errors++;
      }
      if (!a.run_modes || a.run_modes.length === 0) {
        console.error(`  ❌ [L2] Agent "${a.id}" has no run_modes defined`);
        errors++;
      }
      if (!a.status || !['active', 'placeholder', 'pending', 'disabled'].includes(a.status)) {
        console.error(`  ❌ [L2] Agent "${a.id}" has invalid status: ${a.status}`);
        errors++;
      }

      // Duplicate ID check
      if (seenIds.has(a.id)) {
        console.error(`  ❌ Duplicate agent ID: "${a.id}"`);
        errors++;
      }
      seenIds.add(a.id);

      // === L3 Checks (Verified Agent — advisory) ===
      if (a.eval_suite && a.eval_suite.length > 0) {
        // If claiming L3, verify eval files exist
        for (const evalPath of a.eval_suite) {
          const { existsSync } = await import('fs');
          if (!existsSync(resolve(repoRoot, evalPath))) {
            console.error(`  ❌ [L3] Agent "${a.id}" declares eval_suite "${evalPath}" but file not found`);
            errors++;
          }
        }
      } else if (a.run_modes?.includes('execute')) {
        console.warn(`  ⚠️  [L3] Agent "${a.id}" supports execute mode but has no eval_suite — consider adding for L3 promotion`);
        warnings++;
      }

      // === Entrypoint existence check ===
      const { existsSync } = await import('fs');
      if (a.entrypoint && !existsSync(resolve(repoRoot, a.entrypoint))) {
        console.error(`  ❌ Agent "${a.id}" entrypoint not found: ${a.entrypoint}`);
        errors++;
      }
    }

    console.log('');
    if (errors === 0) {
      console.log(`  ✅ Registry valid. ${agents.length} agents, 0 errors, ${warnings} warnings.\n`);
    } else {
      console.error(`  ❌ ${errors} error(s), ${warnings} warning(s) found.\n`);
      process.exit(1);
    }
    break;
  }

  default:
    console.log(`
EGOS Agent Platform CLI

Commands:
  list              List all registered agents
  run <id> --dry    Run agent in dry-run mode (report only)
  run <id> --exec   Run agent in execute mode (apply changes)
  lint-registry     Validate the agent registry
`);
}
