/**
 * SSOT Fixer Agent v1.0.0
 *
 * Consumes the JSON output from ssot-auditor (ssot-audit.json) and applies
 * safe codemod plans automatically. Only LOW-risk, collision-free plans
 * with EXACT or RELAXED drift are applied.
 *
 * Modes:
 * - dry_run: Report what would be fixed (no file changes)
 * - execute: Apply fixes, write summary report
 *
 * Safety:
 * - NEVER applies HIGH / BLOCKED_ARCHITECTURE / REQUIRES_EXTRACTION plans
 * - Skips plans with lexical collisions
 * - Validates file existence before modifying
 * - Logs every action for auditability
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, relative, dirname } from 'path';
import { runAgent, printResult, log, type RunContext, type Finding } from '../runtime/runner';

// ─── Types (mirror ssot-auditor output) ──────────────────────

interface CodemodAction {
  type: 'DELETE_DEFINITION' | 'ADD_IMPORT' | 'REPLACE_IMPORT';
  file: string;
  line: number;
  description: string;
}

interface CodemodPlan {
  symbol: string;
  kind: string;
  drift: string;
  canonical: { file: string; line: number; layer: string };
  actions: CodemodAction[];
  risk: string;
  reason: string;
  blastRadius?: number;
  blockReason?: string;
  collisions?: string[];
}

interface AuditReport {
  meta: { generatedAt: string; correlationId: string };
  codemod_plans?: CodemodPlan[];
}

// ─── Helpers ─────────────────────────────────────────────────

function isSafePlan(plan: CodemodPlan): boolean {
  if (plan.risk !== 'LOW') return false;
  if (plan.collisions && plan.collisions.length > 0) return false;
  if (!['EXACT', 'RELAXED'].includes(plan.drift)) return false;
  if (plan.actions.length === 0) return false;
  return true;
}

function deleteDefinitionLines(content: string, line: number, symbol: string): string {
  const lines = content.split('\n');
  const targetIdx = line - 1; // 1-indexed to 0-indexed
  if (targetIdx < 0 || targetIdx >= lines.length) return content;

  // Find the start of the definition (look for export keyword)
  let startIdx = targetIdx;
  while (startIdx > 0 && !lines[startIdx].match(/^export\s/)) {
    startIdx--;
  }

  // Find the end: matching braces or semicolon
  let endIdx = startIdx;
  let braceDepth = 0;
  let foundOpen = false;
  for (let i = startIdx; i < lines.length; i++) {
    const l = lines[i];
    for (const ch of l) {
      if (ch === '{') { braceDepth++; foundOpen = true; }
      if (ch === '}') braceDepth--;
    }
    endIdx = i;
    if (foundOpen && braceDepth <= 0) break;
    if (!foundOpen && l.trimEnd().endsWith(';')) break;
  }

  // Remove the lines
  lines.splice(startIdx, endIdx - startIdx + 1);
  return lines.join('\n');
}

function addImportStatement(content: string, symbol: string, fromPath: string): string {
  const lines = content.split('\n');
  // Find last import line
  let lastImportIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].match(/^import\s/)) lastImportIdx = i;
  }
  const importLine = `import type { ${symbol} } from '${fromPath}';`;
  // Check if already imported
  if (content.includes(importLine)) return content;
  if (lastImportIdx >= 0) {
    lines.splice(lastImportIdx + 1, 0, importLine);
  } else {
    lines.unshift(importLine);
  }
  return lines.join('\n');
}

function computeRelativeImport(fromFile: string, toFile: string): string {
  const fromDir = dirname(fromFile);
  let rel = relative(fromDir, toFile).replace(/\\/g, '/');
  // Remove .ts/.tsx extension
  rel = rel.replace(/\.(ts|tsx)$/, '');
  if (!rel.startsWith('.')) rel = './' + rel;
  return rel;
}

// ─── Main Handler ────────────────────────────────────────────

async function handler(ctx: RunContext): Promise<Finding[]> {
  const findings: Finding[] = [];
  const repoRoot = ctx.repoRoot;
  const reportPath = join(repoRoot, 'docs', 'agentic', 'reports', 'ssot-audit.json');

  if (!existsSync(reportPath)) {
    findings.push({
      severity: 'error',
      category: 'ssot-fixer',
      message: 'ssot-audit.json not found. Run ssot-auditor first: bun agent:ssot:exec',
    });
    return findings;
  }

  const report: AuditReport = JSON.parse(readFileSync(reportPath, 'utf-8'));
  const plans = report.codemod_plans || [];
  log(ctx, 'info', `Loaded ${plans.length} codemod plans from ssot-audit.json`);

  const safePlans = plans.filter(isSafePlan);
  const skipped = plans.length - safePlans.length;
  log(ctx, 'info', `Safe plans: ${safePlans.length} | Skipped (unsafe): ${skipped}`);

  if (safePlans.length === 0) {
    findings.push({
      severity: 'info',
      category: 'ssot-fixer',
      message: `No safe plans to apply (${plans.length} total, all filtered by safety rails)`,
    });
    return findings;
  }

  let applied = 0;
  let errors = 0;

  for (const plan of safePlans) {
    const label = `${plan.symbol} (${plan.drift}, blast=${plan.blastRadius ?? '?'})`;

    if (ctx.mode === 'dry_run') {
      findings.push({
        severity: 'info',
        category: 'ssot-fixer',
        message: `[DRY] Would fix: ${label} — ${plan.actions.length} action(s)`,
        suggestion: plan.actions.map(a => `${a.type} @ ${a.file}:${a.line}`).join('; '),
      });
      continue;
    }

    for (const action of plan.actions) {
      const absFile = join(repoRoot, action.file);
      if (!existsSync(absFile)) {
        findings.push({
          severity: 'warning',
          category: 'ssot-fixer',
          message: `File not found: ${action.file} — skipping`,
          file: action.file,
        });
        errors++;
        continue;
      }

      try {
        let content = readFileSync(absFile, 'utf-8');
        const canonicalAbs = join(repoRoot, plan.canonical.file);
        const relImport = computeRelativeImport(absFile, canonicalAbs);

        if (action.type === 'DELETE_DEFINITION') {
          content = deleteDefinitionLines(content, action.line, plan.symbol);
          content = addImportStatement(content, plan.symbol, relImport);
        } else if (action.type === 'REPLACE_IMPORT') {
          const re = new RegExp(
            `(import\\s+(?:type\\s+)?{[^}]*\\b${plan.symbol}\\b[^}]*}\\s+from\\s+)['"][^'"]+['"]`,
          );
          content = content.replace(re, `$1'${relImport}'`);
        } else if (action.type === 'ADD_IMPORT') {
          content = addImportStatement(content, plan.symbol, relImport);
        }

        writeFileSync(absFile, content);
        log(ctx, 'info', `✅ ${action.type} @ ${action.file}:${action.line}`);
        applied++;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        findings.push({
          severity: 'error',
          category: 'ssot-fixer',
          message: `Failed ${action.type} on ${action.file}: ${msg}`,
          file: action.file, line: action.line,
        });
        errors++;
      }
    }
  }

  findings.push({
    severity: errors > 0 ? 'warning' : 'info',
    category: 'ssot-fixer',
    message: ctx.mode === 'dry_run'
      ? `Dry run: ${safePlans.length} plans would be applied`
      : `Applied ${applied} actions, ${errors} errors, ${skipped} skipped (unsafe)`,
  });

  return findings;
}

// ─── CLI ─────────────────────────────────────────────────────

const mode = process.argv.includes('--exec') ? 'execute' : 'dry_run';
runAgent('ssot_fixer', mode, handler).then(printResult);
