#!/usr/bin/env bun
/**
 * egos-guard — EGOS Guard Brasil CLI
 *
 * Usage:
 *   bun scripts/guard.ts validate <file>       # Validate file for ATRiAN + PII
 *   bun scripts/guard.ts validate --text "..." # Validate inline text
 *   bun scripts/guard.ts mask <file>           # Mask PII from file, output to stdout
 *   bun scripts/guard.ts mask --text "..."     # Mask inline text
 *   bun scripts/guard.ts check <file>          # Full compliance check (all guards)
 *   bun scripts/guard.ts demo                  # Run a demo with sample text
 */

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import {
  createAtrianValidator,
  maskPublicOutput,
  buildLGPDDisclosure,
  isPublicSafe,
} from '../packages/shared/src/index.js';

const args = process.argv.slice(2);
const command = args[0];

// ─── Helpers ────────────────────────────────────────────────────────────────

function readInput(args: string[]): string {
  const textFlag = args.indexOf('--text');
  if (textFlag !== -1 && args[textFlag + 1]) {
    return args[textFlag + 1];
  }
  const filePath = args.find(a => !a.startsWith('--'));
  if (filePath) {
    return readFileSync(resolve(process.cwd(), filePath), 'utf-8');
  }
  console.error('❌ Provide a file path or --text "..."');
  process.exit(1);
}

function colorize(color: 'red' | 'green' | 'yellow' | 'cyan' | 'reset', text: string): string {
  const codes = { red: '\x1b[31m', green: '\x1b[32m', yellow: '\x1b[33m', cyan: '\x1b[36m', reset: '\x1b[0m' };
  return `${codes[color]}${text}${codes.reset}`;
}

// ─── Commands ───────────────────────────────────────────────────────────────

function cmdValidate(args: string[]) {
  const text = readInput(args);
  const atrian = createAtrianValidator();
  const ethicsResult = atrian.validateResponse(text);
  const guardResult = maskPublicOutput(text);

  console.log('\n' + colorize('cyan', '╔══════════════════════════════════════╗'));
  console.log(colorize('cyan', '║   EGOS Guard Brasil — Validation     ║'));
  console.log(colorize('cyan', '╚══════════════════════════════════════╝') + '\n');

  // ATRiAN result
  const ethicsIcon = ethicsResult.passed ? colorize('green', '✅') : colorize('red', '❌');
  console.log(`${ethicsIcon} ATRiAN Ethics Score: ${ethicsResult.score}/100`);
  if (ethicsResult.violations.length > 0) {
    for (const v of ethicsResult.violations) {
      const icon = v.level === 'critical' ? '🚨' : v.level === 'error' ? '❌' : '⚠️';
      console.log(`   ${icon} [${v.category}] ${v.message}`);
    }
  }

  // PII result
  const piiIcon = guardResult.safe ? colorize('green', '✅') : colorize('red', '❌');
  console.log(`\n${piiIcon} PII Safety: ${guardResult.safe ? 'CLEAN' : `${guardResult.findings.length} findings (${guardResult.sensitivityLevel})`}`);
  if (!guardResult.safe) {
    const disclosure = buildLGPDDisclosure(guardResult);
    console.log(colorize('yellow', `   ${disclosure}`));
    for (const finding of guardResult.findings.slice(0, 5)) {
      console.log(`   → [${finding.category}] "${finding.matched}" at pos ${finding.start}`);
    }
    if (guardResult.findings.length > 5) {
      console.log(`   ... and ${guardResult.findings.length - 5} more findings`);
    }
  }

  // Summary
  const allClear = ethicsResult.passed && guardResult.safe;
  console.log('\n' + (allClear
    ? colorize('green', '✅ PASSED — Safe for public output')
    : colorize('red', '❌ FAILED — Review violations before publishing')));
  console.log();

  process.exit(allClear ? 0 : 1);
}

function cmdMask(args: string[]) {
  const text = readInput(args);
  const result = maskPublicOutput(text);

  if (result.safe) {
    console.log(colorize('green', '✅ No PII found — text is already clean\n'));
    console.log(text);
    return;
  }

  console.log(colorize('yellow', `⚠️  Masked ${result.findings.length} PII findings (${result.sensitivityLevel} sensitivity)\n`));
  console.log(result.masked);
  console.log('\n' + colorize('cyan', buildLGPDDisclosure(result)));
}

function cmdCheck(args: string[]) {
  const text = readInput(args);
  const atrian = createAtrianValidator();
  const ethicsResult = atrian.validateResponse(text);
  const guardResult = maskPublicOutput(text);

  const overallPassed = ethicsResult.passed && guardResult.safe;

  console.log('\n' + colorize('cyan', '╔══════════════════════════════════════════╗'));
  console.log(colorize('cyan', '║   EGOS Guard Brasil — Full Compliance    ║'));
  console.log(colorize('cyan', '╚══════════════════════════════════════════╝') + '\n');

  console.log('Module Results:');
  console.log(`  ATRiAN Ethics    : ${ethicsResult.passed ? colorize('green', 'PASS') : colorize('red', 'FAIL')} (score: ${ethicsResult.score}/100, violations: ${ethicsResult.violations.length})`);
  console.log(`  PII Scanner      : ${guardResult.safe ? colorize('green', 'PASS') : colorize('red', 'FAIL')} (findings: ${guardResult.findings.length}, level: ${guardResult.sensitivityLevel})`);
  console.log(`  Public Safe      : ${isPublicSafe(text) ? colorize('green', 'YES') : colorize('red', 'NO')}`);

  console.log('\n' + colorize('cyan', '─'.repeat(45)));
  console.log('Overall: ' + (overallPassed
    ? colorize('green', 'COMPLIANT ✅')
    : colorize('red', 'NON-COMPLIANT ❌')));

  if (!overallPassed) {
    console.log('\nRequired actions:');
    if (!ethicsResult.passed) {
      console.log('  1. Fix ATRiAN violations (absolute claims, false promises, fabricated data)');
    }
    if (!guardResult.safe) {
      console.log('  2. Remove or mask PII before publishing');
      console.log(`     Run: bun scripts/guard.ts mask --text "${text.slice(0, 40)}..."`);
    }
  }
  console.log();
  process.exit(overallPassed ? 0 : 1);
}

function cmdDemo() {
  const sampleTexts = [
    {
      label: 'Clean text',
      text: 'O sistema de IA analisou o documento e identificou possíveis irregularidades para revisão.',
    },
    {
      label: 'Text with CPF + false promise',
      text: 'O CPF 123.456.789-00 do servidor foi encontrado. Vamos resolver esse caso com certeza.',
    },
    {
      label: 'Text with process number + absolute claim',
      text: 'O processo 1234567-89.2024.6.26.0100 foi encerrado. Todos os casos são resolvidos em 30 dias.',
    },
  ];

  console.log('\n' + colorize('cyan', '╔══════════════════════════════════════════╗'));
  console.log(colorize('cyan', '║   EGOS Guard Brasil — Demo               ║'));
  console.log(colorize('cyan', '╚══════════════════════════════════════════╝') + '\n');

  const atrian = createAtrianValidator();

  for (const { label, text } of sampleTexts) {
    console.log(colorize('cyan', `── ${label} ──`));
    console.log(`Input: "${text}"`);

    const ethics = atrian.validateResponse(text);
    const guard = maskPublicOutput(text);

    console.log(`ATRiAN: score=${ethics.score}, passed=${ethics.passed}, violations=${ethics.violations.length}`);
    console.log(`PII: safe=${guard.safe}, level=${guard.sensitivityLevel}, findings=${guard.findings.length}`);
    if (!guard.safe) console.log(`Masked: "${guard.masked}"`);
    console.log();
  }
}

// ─── Router ─────────────────────────────────────────────────────────────────

switch (command) {
  case 'validate':
    cmdValidate(args.slice(1));
    break;
  case 'mask':
    cmdMask(args.slice(1));
    break;
  case 'check':
    cmdCheck(args.slice(1));
    break;
  case 'demo':
    cmdDemo();
    break;
  default:
    console.log(`
${colorize('cyan', 'EGOS Guard Brasil — Brazilian AI Safety CLI')}

Usage:
  bun scripts/guard.ts validate <file>        Validate file for ethics + PII
  bun scripts/guard.ts validate --text "..."  Validate inline text
  bun scripts/guard.ts mask <file>            Mask PII from file
  bun scripts/guard.ts mask --text "..."      Mask inline text
  bun scripts/guard.ts check <file>           Full compliance check
  bun scripts/guard.ts demo                   Run demo with sample texts

Modules:
  ATRiAN         Brazilian ethical validation (absolute claims, false promises)
  PII Scanner    CPF, RG, MASP, REDS, process numbers, phones, emails
  Public Guard   LGPD-compliant masking with sensitivity scoring
  Evidence Chain Traceable response discipline (via SDK)
`);
    process.exit(0);
}
