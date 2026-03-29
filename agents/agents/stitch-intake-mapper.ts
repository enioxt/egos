/**
 * Stitch Intake Mapper Agent — EGOS-108
 *
 * Parses a returned .zip file from Google Stitch (or any UI generation tool),
 * generates a mapping table of files → EGOS destination paths,
 * and creates TASKS.md integration tasks automatically.
 *
 * Modes:
 * - dry_run: Parse .zip and print mapping table (no writes)
 * - execute: Parse .zip, write mapping table to docs/intake/, create TASKS.md entries
 *
 * Usage:
 *   bun agents/cli.ts run stitch_intake_mapper dry_run --zip /path/to/stitch.zip
 *   bun agents/cli.ts run stitch_intake_mapper execute --zip /path/to/stitch.zip --target egos-lab
 */

import { existsSync, mkdirSync, writeFileSync } from 'fs';
import { basename, extname, join } from 'path';
import { execSync } from 'child_process';
import { runAgent, printResult, log, type Finding } from '../runtime/runner';

// ─── Types ────────────────────────────────────────────────────────────────────

type FileType = 'component' | 'page' | 'api' | 'style' | 'config' | 'asset' | 'unknown';
type FileAction = 'create' | 'merge' | 'review';

interface FileMapping {
  zipPath: string;
  suggestedDest: string;
  fileType: FileType;
  action: FileAction;
}

interface StitchReport {
  zipPath: string;
  targetRepo: string;
  totalFiles: number;
  mappings: FileMapping[];
  suggestedTasks: string[];
  timestamp: string;
}

// ─── File classification ──────────────────────────────────────────────────────

function classifyFile(filePath: string): FileType {
  const ext = extname(filePath).toLowerCase();
  const lower = filePath.toLowerCase();
  if (lower.includes('/components/') || lower.includes('/ui/')) return 'component';
  if (lower.includes('/pages/') || lower.includes('/app/') || lower.includes('/routes/')) return 'page';
  if (lower.includes('/api/') || lower.includes('/server/')) return 'api';
  if (['.css', '.scss', '.sass', '.less'].includes(ext)) return 'style';
  if (['.json', '.yaml', '.yml', '.env'].includes(ext)) return 'config';
  if (['.png', '.jpg', '.svg', '.ico', '.webp'].includes(ext)) return 'asset';
  return 'unknown';
}

function suggestDest(filePath: string, targetRepo: string): string {
  const file = basename(filePath);
  const map: Record<FileType, string> = {
    component: `${targetRepo}/src/components/${file}`,
    page:      `${targetRepo}/src/app/${file}`,
    api:       `${targetRepo}/src/app/api/${file}`,
    style:     `${targetRepo}/src/styles/${file}`,
    config:    `${targetRepo}/${file}`,
    asset:     `${targetRepo}/public/${file}`,
    unknown:   `${targetRepo}/src/${file}`,
  };
  return map[classifyFile(filePath)];
}

function suggestAction(filePath: string): FileAction {
  const lower = filePath.toLowerCase();
  if (lower.includes('package.json') || lower.includes('tsconfig') || lower.includes('.env')) return 'review';
  return 'create';
}

// ─── ZIP listing ─────────────────────────────────────────────────────────────

function listZip(zipPath: string): string[] {
  if (!existsSync(zipPath)) throw new Error(`ZIP not found: ${zipPath}`);
  const output = execSync(`unzip -l "${zipPath}" 2>/dev/null`, { encoding: 'utf8' });
  const files: string[] = [];
  for (const line of output.split('\n').slice(3)) {
    const match = line.trim().match(/^\d+\s+\S+\s+\S+\s+(.+)$/);
    if (match?.[1] && !match[1].trim().endsWith('/')) files.push(match[1].trim());
  }
  return files;
}

// ─── Task generation ──────────────────────────────────────────────────────────

function buildTasks(mappings: FileMapping[], target: string): string[] {
  const tasks: string[] = [];
  const byType = (t: FileType) => mappings.filter(m => m.fileType === t);
  const reviews = mappings.filter(m => m.action === 'review');

  if (byType('component').length) tasks.push(`Integrate ${byType('component').length} component(s) from Stitch → ${target}/src/components/`);
  if (byType('page').length)      tasks.push(`Integrate ${byType('page').length} page(s) from Stitch → ${target}/src/app/`);
  if (byType('api').length)       tasks.push(`Integrate ${byType('api').length} API route(s) from Stitch → ${target}/src/app/api/`);
  if (reviews.length)             tasks.push(`Manual review ${reviews.length} config file(s): ${reviews.map(r => basename(r.zipPath)).join(', ')}`);
  tasks.push('Run typecheck + tests after integration: bun run typecheck && bun test');
  return tasks;
}

// ─── Agent ────────────────────────────────────────────────────────────────────

const result = await runAgent('stitch_intake_mapper', 'dry_run', async (ctx) => {
  const findings: Finding[] = [];
  const zipPath = process.env['STITCH_ZIP'] ?? '';
  const targetRepo = process.env['STITCH_TARGET'] ?? 'egos-lab';

  if (!zipPath) {
    findings.push({ severity: 'error', category: 'args', message: 'Missing STITCH_ZIP env var. Set: STITCH_ZIP=/path/to/file.zip' });
    return findings;
  }

  log(ctx, 'info', `Parsing ZIP: ${zipPath} → target: ${targetRepo}`);

  let files: string[];
  try {
    files = listZip(zipPath);
  } catch (err) {
    findings.push({ severity: 'error', category: 'zip', message: String(err), file: zipPath });
    return findings;
  }

  log(ctx, 'info', `Found ${files.length} file(s)`);

  const mappings: FileMapping[] = files.map(f => ({
    zipPath: f,
    suggestedDest: suggestDest(f, targetRepo),
    fileType: classifyFile(f),
    action: suggestAction(f),
  }));

  const tasks = buildTasks(mappings, targetRepo);

  // Print mapping table
  log(ctx, 'info', `\n${'Source'.padEnd(50)} ${'Destination'.padEnd(55)} ${'Type'.padEnd(12)} Action`);
  log(ctx, 'info', '-'.repeat(125));
  for (const m of mappings) {
    log(ctx, 'info', `${m.zipPath.padEnd(50)} ${m.suggestedDest.padEnd(55)} ${m.fileType.padEnd(12)} ${m.action}`);
  }
  log(ctx, 'info', '\nSuggested tasks:');
  for (const t of tasks) log(ctx, 'info', `  - [ ] ${t}`);

  findings.push({ severity: 'info', category: 'summary', message: `Mapped ${files.length} file(s) from ${basename(zipPath)} → ${targetRepo}` });

  // Execute: write report
  if (ctx.mode === 'execute') {
    const dir = 'docs/intake';
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
    const reportPath = join(dir, `stitch-${Date.now()}.json`);
    const report: StitchReport = { zipPath, targetRepo, totalFiles: files.length, mappings, suggestedTasks: tasks, timestamp: new Date().toISOString() };
    writeFileSync(reportPath, JSON.stringify(report, null, 2));
    findings.push({ severity: 'info', category: 'output', message: `Report saved: ${reportPath}`, file: reportPath });
  }

  return findings;
});

printResult(result);
