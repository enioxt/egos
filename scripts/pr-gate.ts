#!/usr/bin/env bun
/**
 * pr:gate — validate PR markdown contains mandatory sign-off + IDE evidence
 * required by EGOS workflow before merge.
 *
 * Usage:
 *   bun scripts/pr-gate.ts --file /tmp/pr-pack.md
 */

import { existsSync, readFileSync } from 'fs';
import { resolve } from 'path';

function argValue(flag: string): string | undefined {
  const idx = process.argv.indexOf(flag);
  if (idx === -1) return undefined;
  return process.argv[idx + 1];
}

function fail(message: string): never {
  console.error(`❌ ${message}`);
  process.exit(1);
}

function hasCheckedLine(content: string, text: string): boolean {
  const escaped = text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`- \\[x\\]\\s+${escaped}`, 'i');
  return regex.test(content);
}

function main(): void {
  const fileArg = argValue('--file');
  if (!fileArg) fail('Missing required --file argument');

  const file = resolve(fileArg);
  if (!existsSync(file)) fail(`File not found: ${file}`);

  const content = readFileSync(file, 'utf-8');

  const failures: string[] = [];

  if (!content.includes('Signed-off-by:')) {
    failures.push('Signed-off-by footer missing');
  }

  const requiredChecks = [
    'Windsurf: validate locally end-to-end',
    'Antigravity: validate locally end-to-end',
    'Re-run tests after IDE adjustments',
  ];

  for (const check of requiredChecks) {
    if (!hasCheckedLine(content, check)) {
      failures.push(`Unchecked required IDE validation item: ${check}`);
    }
  }

  if (failures.length > 0) {
    console.error('⛔ PR gate failed:');
    failures.forEach((entry) => console.error(`  - ${entry}`));
    process.exit(1);
  }

  console.log('✅ PR gate passed: sign-off + IDE validation evidence found.');
}

main();
