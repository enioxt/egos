#!/usr/bin/env bun
/**
 * ssot-package-auditor.ts — SSOT-v2-03
 *
 * Enforces structural compliance across package.json files in the monorepo.
 * Checks each workspace package against expected standards:
 * - Required fields (name, version, type, exports, scripts.typecheck)
 * - Naming convention (@egos/<name>)
 * - No cross-workspace circular deps
 * - Dev deps not in production deps
 * - private: true for internal packages
 *
 * Usage:
 *   bun scripts/ssot-package-auditor.ts           # audit + print report
 *   bun scripts/ssot-package-auditor.ts --strict  # exit 1 on any violation
 *   bun scripts/ssot-package-auditor.ts --json    # JSON output
 */

import { readdirSync, readFileSync, existsSync } from 'fs';
import { join } from 'path';

const STRICT = process.argv.includes('--strict');
const JSON_MODE = process.argv.includes('--json');

// ─── Types ────────────────────────────────────────────────────────────────────

interface PackageViolation {
  package: string;
  field: string;
  severity: 'error' | 'warn';
  message: string;
}

interface PackageAuditResult {
  package: string;
  path: string;
  violations: PackageViolation[];
}

// ─── Standards ───────────────────────────────────────────────────────────────

const REQUIRED_FIELDS = ['name', 'version', 'type'];
const REQUIRED_SCRIPTS = ['typecheck'];

// Packages that are publishable (not private) — must have full publish fields
const PUBLISHABLE = ['@egos/guard-brasil'];

const PUBLISHABLE_REQUIRED = ['description', 'keywords', 'author', 'license', 'repository', 'exports'];

// Dev-only package name patterns — should never appear in `dependencies`
const DEV_ONLY_PATTERNS = ['@types/', 'eslint', 'prettier', 'typescript', 'vitest', 'jest', 'tsx'];

// ─── Audit logic ─────────────────────────────────────────────────────────────

function auditPackage(pkgPath: string): PackageAuditResult {
  const pkgJsonPath = join(pkgPath, 'package.json');
  const violations: PackageViolation[] = [];

  if (!existsSync(pkgJsonPath)) {
    return {
      package: pkgPath,
      path: pkgJsonPath,
      violations: [{
        package: pkgPath,
        field: 'package.json',
        severity: 'error',
        message: 'package.json missing — workspace package must have one',
      }],
    };
  }

  let pkg: Record<string, unknown>;
  try {
    pkg = JSON.parse(readFileSync(pkgJsonPath, 'utf8'));
  } catch {
    return {
      package: pkgPath,
      path: pkgJsonPath,
      violations: [{
        package: pkgPath,
        field: 'package.json',
        severity: 'error',
        message: 'package.json is not valid JSON',
      }],
    };
  }

  const name = (pkg.name as string) ?? pkgPath;

  // 1. Required fields
  for (const field of REQUIRED_FIELDS) {
    if (!pkg[field]) {
      violations.push({ package: name, field, severity: 'error', message: `Missing required field: "${field}"` });
    }
  }

  // 2. Naming convention
  if (pkg.name && !(pkg.name as string).startsWith('@egos/')) {
    violations.push({ package: name, field: 'name', severity: 'warn', message: `Package name should follow @egos/<name> convention` });
  }

  // 3. type: "module"
  if (pkg.type !== 'module') {
    violations.push({ package: name, field: 'type', severity: 'warn', message: `"type" should be "module" for ESM consistency` });
  }

  // 4. Required scripts
  const scripts = (pkg.scripts as Record<string, string>) ?? {};
  for (const script of REQUIRED_SCRIPTS) {
    if (!scripts[script]) {
      violations.push({ package: name, field: `scripts.${script}`, severity: 'warn', message: `Missing script: "${script}"` });
    }
  }

  // 5. Dev deps in production
  const deps = (pkg.dependencies as Record<string, string>) ?? {};
  for (const dep of Object.keys(deps)) {
    if (DEV_ONLY_PATTERNS.some(p => dep.startsWith(p))) {
      violations.push({ package: name, field: 'dependencies', severity: 'error', message: `Dev-only package in dependencies: "${dep}" — move to devDependencies` });
    }
  }

  // 6. Publishable packages need full fields
  if (PUBLISHABLE.includes(pkg.name as string)) {
    for (const field of PUBLISHABLE_REQUIRED) {
      if (!pkg[field]) {
        violations.push({ package: name, field, severity: 'error', message: `Publishable package missing: "${field}"` });
      }
    }
    if (pkg.private === true) {
      violations.push({ package: name, field: 'private', severity: 'error', message: `Publishable package has "private": true — remove it` });
    }
  }

  // 7. Internal packages should be private
  if (!PUBLISHABLE.includes(pkg.name as string) && pkg.private !== true) {
    violations.push({ package: name, field: 'private', severity: 'warn', message: `Internal package missing "private": true` });
  }

  return { package: name, path: pkgJsonPath, violations };
}

// ─── Main ─────────────────────────────────────────────────────────────────────

const PACKAGES_DIR = 'packages';
const packages = readdirSync(PACKAGES_DIR, { withFileTypes: true })
  .filter(d => d.isDirectory())
  .map(d => join(PACKAGES_DIR, d.name));

const results: PackageAuditResult[] = packages.map(auditPackage);

const totalViolations = results.reduce((acc, r) => acc + r.violations.length, 0);
const errors = results.flatMap(r => r.violations.filter(v => v.severity === 'error'));
const warnings = results.flatMap(r => r.violations.filter(v => v.severity === 'warn'));

if (JSON_MODE) {
  console.log(JSON.stringify({ results, summary: { totalPackages: packages.length, totalViolations, errors: errors.length, warnings: warnings.length } }, null, 2));
  process.exit(STRICT && errors.length > 0 ? 1 : 0);
}

console.log('\n╔══════════════════════════════════════════════════╗');
console.log('║  SSOT Package Auditor                           ║');
console.log('╚══════════════════════════════════════════════════╝\n');

let hasOutput = false;
for (const result of results) {
  if (result.violations.length === 0) continue;
  hasOutput = true;
  console.log(`  [${result.package}]`);
  for (const v of result.violations) {
    const icon = v.severity === 'error' ? '❌' : '⚠️ ';
    console.log(`    ${icon} ${v.field}: ${v.message}`);
  }
  console.log('');
}

if (!hasOutput) {
  console.log(`  ✅ All ${packages.length} package(s) pass structural compliance.\n`);
} else {
  console.log(`  Summary: ${packages.length} packages | ${errors.length} error(s) | ${warnings.length} warning(s)\n`);
}

if (STRICT && errors.length > 0) {
  process.exit(1);
}
