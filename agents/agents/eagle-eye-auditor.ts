/**
 * Eagle Eye Auditor Agent — EGOS-125
 *
 * Audits an Eagle Eye deployment (egos-lab/apps/eagle-eye) for:
 * - LGPD compliance gaps (citizen data, PII handling, consent flows)
 * - Module health (required files present, exports valid)
 * - Guard Brasil integration status (is @egos/guard-brasil wired in?)
 * - Kernel consumption status (is @egos/shared used instead of local copies?)
 * - Test coverage presence
 *
 * Modes:
 * - dry_run: Audit and report findings only
 * - execute: Write audit report to docs/intake/eagle-eye-audit-<timestamp>.json
 *
 * Usage:
 *   EAGLE_EYE_PATH=/path/to/egos-lab/apps/eagle-eye bun agents/cli.ts run eagle_eye_auditor dry_run
 */

import { existsSync, readdirSync, readFileSync, mkdirSync, writeFileSync } from 'fs';
import { join, basename } from 'path';
import { runAgent, printResult, log, type Finding } from '../runtime/runner';

// ─── Required module inventory ────────────────────────────────────────────────

const REQUIRED_CORE_FILES = [
  'src/fetch_gazettes.ts',
  'src/analyze_viability.ts',
  'src/analyze_gazette.ts',
  'src/enrich_opportunity.ts',
  'src/index.ts',
  'package.json',
  'README.md',
];

const REQUIRED_TOURISM_FILES = [
  'src/modules/tourism/index.ts',
  'src/modules/tourism/types.ts',
  'src/modules/tourism/citizen-logger.ts',
  'src/modules/tourism/gamification.ts',
];

const LGPD_SENSITIVE_PATTERNS = [
  /cpf/i, /rg\b/i, /cnpj/i, /nome completo/i, /endere[çc]o/i,
  /telefone/i, /celular/i, /email/i, /nascimento/i,
];

// ─── Helpers ──────────────────────────────────────────────────────────────────

function checkFileExists(root: string, rel: string): boolean {
  return existsSync(join(root, rel));
}

function readFileSafe(path: string): string {
  try { return readFileSync(path, 'utf8'); } catch { return ''; }
}

function detectPIIInFile(content: string): string[] {
  return LGPD_SENSITIVE_PATTERNS
    .filter(p => p.test(content))
    .map(p => p.source);
}

// ─── Audit checks ─────────────────────────────────────────────────────────────

function auditCoreFiles(root: string, findings: Finding[]): void {
  let missing = 0;
  for (const f of REQUIRED_CORE_FILES) {
    if (!checkFileExists(root, f)) {
      findings.push({ severity: 'warning', category: 'module_health', message: `Missing required file: ${f}`, file: f });
      missing++;
    }
  }
  if (missing === 0) {
    findings.push({ severity: 'info', category: 'module_health', message: `All ${REQUIRED_CORE_FILES.length} core files present` });
  }
}

function auditTourismModule(root: string, findings: Finding[]): void {
  const tourismRoot = join(root, 'src/modules/tourism');
  if (!existsSync(tourismRoot)) {
    findings.push({ severity: 'warning', category: 'module_health', message: 'Tourism module directory not found — expected src/modules/tourism/' });
    return;
  }
  let missing = 0;
  for (const f of REQUIRED_TOURISM_FILES) {
    if (!checkFileExists(root, f)) {
      findings.push({ severity: 'warning', category: 'module_health', message: `Tourism: missing ${f}`, file: f });
      missing++;
    }
  }
  if (missing === 0) {
    findings.push({ severity: 'info', category: 'module_health', message: `Tourism module: all ${REQUIRED_TOURISM_FILES.length} required files present` });
  }
}

function auditGuardBrasilIntegration(root: string, findings: Finding[]): void {
  const pkgPath = join(root, 'package.json');
  const pkg = readFileSafe(pkgPath);
  if (pkg.includes('@egos/guard-brasil')) {
    findings.push({ severity: 'info', category: 'compliance', message: '@egos/guard-brasil dependency found in package.json' });
  } else {
    findings.push({
      severity: 'warning',
      category: 'compliance',
      message: '@egos/guard-brasil not in dependencies — LGPD masking and ATRiAN scoring not guaranteed',
      suggestion: 'Add @egos/guard-brasil to dependencies and wire GuardBrasil into citizen-logger.ts',
    });
  }
}

function auditSharedConsumption(root: string, findings: Finding[]): void {
  const pkgPath = join(root, 'package.json');
  const pkg = readFileSafe(pkgPath);
  if (pkg.includes('@egos/shared')) {
    findings.push({ severity: 'info', category: 'kernel_adoption', message: '@egos/shared consumed — model-router and PII scanner available' });
  } else {
    findings.push({
      severity: 'warning',
      category: 'kernel_adoption',
      message: '@egos/shared not in dependencies — may have local copies of model-router, PII scanner',
      suggestion: 'Add @egos/shared and import from there instead of local duplicates',
    });
  }
}

function auditLGPDRisk(root: string, findings: Finding[]): void {
  const citizenLoggerPath = join(root, 'src/modules/tourism/citizen-logger.ts');
  if (!existsSync(citizenLoggerPath)) return;

  const content = readFileSafe(citizenLoggerPath);
  const piiPatterns = detectPIIInFile(content);
  if (piiPatterns.length > 0) {
    findings.push({
      severity: 'warning',
      category: 'lgpd',
      message: `citizen-logger.ts contains PII-related patterns: ${piiPatterns.join(', ')}`,
      file: 'src/modules/tourism/citizen-logger.ts',
      suggestion: 'Ensure all PII fields are masked via @egos/guard-brasil maskPublicOutput() before logging/storage',
    });
  }

  const hasConsentCheck = /consentimento|consent|lgpd|lei 13\.709/i.test(content);
  if (!hasConsentCheck) {
    findings.push({
      severity: 'warning',
      category: 'lgpd',
      message: 'citizen-logger.ts: no LGPD consent check detected',
      file: 'src/modules/tourism/citizen-logger.ts',
      suggestion: 'Add explicit LGPD consent validation before recording any citizen data',
    });
  } else {
    findings.push({ severity: 'info', category: 'lgpd', message: 'citizen-logger.ts: LGPD consent reference found' });
  }
}

function auditTestCoverage(root: string, findings: Finding[]): void {
  const hasTestFiles = existsSync(join(root, 'src/scripts')) &&
    readdirSync(join(root, 'src/scripts')).some(f => f.startsWith('test_'));
  const hasBunTest = existsSync(join(root, 'src')) &&
    readdirSync(join(root, 'src')).some(f => f.includes('test'));

  if (hasTestFiles || hasBunTest) {
    findings.push({ severity: 'info', category: 'quality', message: 'Test scripts found in src/scripts/' });
  } else {
    findings.push({
      severity: 'warning',
      category: 'quality',
      message: 'No test files detected',
      suggestion: 'Add bun test suite for core analysis functions (analyze_viability, analyze_gazette)',
    });
  }
}

function auditEnvFile(root: string, findings: Finding[]): void {
  if (checkFileExists(root, '.env.example')) {
    findings.push({ severity: 'info', category: 'infra', message: '.env.example present' });
  } else {
    findings.push({
      severity: 'warning', category: 'infra',
      message: '.env.example missing',
      suggestion: 'Add .env.example with all required environment variables documented',
    });
  }
  if (checkFileExists(root, 'Dockerfile')) {
    findings.push({ severity: 'info', category: 'infra', message: 'Dockerfile present — containerized deployment ready' });
  }
}

// ─── Agent ────────────────────────────────────────────────────────────────────

const result = await runAgent('eagle_eye_auditor', 'dry_run', async (ctx) => {
  const findings: Finding[] = [];
  const eagleEyePath = process.env['EAGLE_EYE_PATH'] ?? '';

  if (!eagleEyePath) {
    findings.push({
      severity: 'error',
      category: 'args',
      message: 'Missing EAGLE_EYE_PATH env var. Set: EAGLE_EYE_PATH=/path/to/egos-lab/apps/eagle-eye',
    });
    return findings;
  }

  if (!existsSync(eagleEyePath)) {
    findings.push({ severity: 'error', category: 'args', message: `Path not found: ${eagleEyePath}` });
    return findings;
  }

  log(ctx, 'info', `Auditing Eagle Eye at: ${eagleEyePath}`);

  auditCoreFiles(eagleEyePath, findings);
  auditTourismModule(eagleEyePath, findings);
  auditGuardBrasilIntegration(eagleEyePath, findings);
  auditSharedConsumption(eagleEyePath, findings);
  auditLGPDRisk(eagleEyePath, findings);
  auditTestCoverage(eagleEyePath, findings);
  auditEnvFile(eagleEyePath, findings);

  const errors = findings.filter(f => f.severity === 'error').length;
  const warnings = findings.filter(f => f.severity === 'warning').length;
  const infos = findings.filter(f => f.severity === 'info').length;

  log(ctx, 'info', `\nAudit complete: ${errors} errors | ${warnings} warnings | ${infos} passed`);

  findings.push({
    severity: errors > 0 ? 'error' : warnings > 5 ? 'warning' : 'info',
    category: 'summary',
    message: `Eagle Eye audit: ${errors} errors, ${warnings} warnings, ${infos} checks passed`,
  });

  if (ctx.mode === 'execute') {
    const dir = 'docs/intake';
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
    const reportPath = join(dir, `eagle-eye-audit-${Date.now()}.json`);
    writeFileSync(reportPath, JSON.stringify({ path: eagleEyePath, findings, auditedAt: new Date().toISOString() }, null, 2));
    findings.push({ severity: 'info', category: 'output', message: `Audit report saved: ${reportPath}`, file: reportPath });
  }

  return findings;
});

printResult(result);
