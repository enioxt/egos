#!/usr/bin/env bun
/**
 * worktree-validator.ts — EGOS-110 Worktree Orchestration Contract Enforcer
 *
 * Validates worktree naming, ownership, lifecycle, and concurrency limits.
 * Enforces gates defined in .guarani/orchestration/WORKTREE_CONTRACT.md
 *
 * Usage:
 *   bun scripts/worktree-validator.ts --pre-commit
 *   bun scripts/worktree-validator.ts --ci --pr-number 42
 *   bun scripts/worktree-validator.ts --status
 *   bun scripts/worktree-validator.ts --cleanup [--exec]
 *   bun scripts/worktree-validator.ts --count-active
 */

import { execSync } from 'child_process';
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';

// ─────────────────────────────────────────────────────────────────────────────
// Configuration & Types
// ─────────────────────────────────────────────────────────────────────────────

const CONCURRENCY_LIMIT = 5;
const ACTIVE_TTL_DAYS = 7;
const STALE_TTL_DAYS = 30;
const ABANDONED_TTL_DAYS = 30;

// Semantic branch naming regex (matching WORKTREE_CONTRACT.md section 2.1)
const BRANCH_NAMING_REGEX =
  /^(feature|fix|docs|chore|refactor|perf|test|ci|security)\/[a-z0-9]+(-[a-z0-9]+)*$/;

interface WorktreeMetadata {
  branch: string;
  owner: string;
  created_at: string;
  last_commit: string;
  status: 'active' | 'stale' | 'abandoned' | 'merged' | 'deleted';
  files_touched: string[];
  issue_link?: string;
}

interface ValidationReport {
  schema_version: string;
  timestamp: string;
  repository: string;
  context: string;
  summary: {
    total_worktrees: number;
    active_worktrees: number;
    stale_worktrees: number;
    abandoned_worktrees: number;
    concurrency_limit: number;
    concurrency_used: number;
    concurrency_status: 'healthy' | 'warning' | 'critical';
  };
  checks: {
    branch_naming: { status: string; message: string };
    ownership: { status: string; owner?: string; verified_at?: string };
    single_ownership: { status: string; unique_authors?: number };
    frozen_zone: { status: string; files_touched: string[]; frozen_files_touched: number };
    lifecycle: { status: string; age_days: number; ttl_remaining_days: number; lifecycle_state: string };
  };
  gates: Array<{ name: string; status: string; weight: number }>;
  warnings: string[];
  errors: string[];
  exit_code: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// Utility Functions
// ─────────────────────────────────────────────────────────────────────────────

function getArg(flag: string): string | undefined {
  const idx = process.argv.indexOf(flag);
  return idx !== -1 && idx + 1 < process.argv.length ? process.argv[idx + 1] : undefined;
}

function hasFlag(flag: string): boolean {
  return process.argv.includes(flag);
}

function run(cmd: string, safe = true): string {
  try {
    return execSync(cmd, { encoding: 'utf-8', stdio: safe ? 'pipe' : 'inherit' }).trim();
  } catch (e) {
    if (!safe) throw e;
    return '';
  }
}

function getCurrentBranch(): string {
  try {
    return run('git rev-parse --abbrev-ref HEAD').trim();
  } catch {
    return '';
  }
}

function getAllBranches(): string[] {
  try {
    const output = run('git branch -a --format="%(refname:short)"');
    return output.split('\n').filter(b => b && !b.startsWith('origin/'));
  } catch {
    return [];
  }
}

function getBranchOwner(branch: string): string {
  const metadata = loadWorkTreeMetadata();
  const entry = metadata.worktrees.find(w => w.branch === branch);
  return entry?.owner || '';
}

function getLastCommitDate(branch: string): Date {
  try {
    const timestamp = run(`git log -1 --format=%aI ${branch}`);
    return new Date(timestamp);
  } catch {
    return new Date();
  }
}

function getCommitAuthors(branch: string, baseBranch = 'main'): string[] {
  try {
    const output = run(`git log ${baseBranch}..${branch} --format=%an`);
    const authors = new Set(output.split('\n').filter(a => a.trim()));
    return Array.from(authors);
  } catch {
    return [];
  }
}

function getFilesTouched(branch: string, baseBranch = 'main'): string[] {
  try {
    const output = run(`git diff --name-only ${baseBranch}...${branch}`);
    return output.split('\n').filter(f => f.trim());
  } catch {
    return [];
  }
}

function isFrozenZoneFile(filePath: string): boolean {
  const frozenZones = [
    'agents/runtime/runner.ts',
    'agents/runtime/event-bus.ts',
    '.husky/pre-commit',
    '.guarani/orchestration/PIPELINE.md',
  ];
  return frozenZones.some(zone => filePath.includes(zone));
}

function getWorkTreeMetadataPath(): string {
  return resolve(process.cwd(), '.guarani', 'worktrees.json');
}

function loadWorkTreeMetadata(): { worktrees: WorktreeMetadata[] } {
  const path = getWorkTreeMetadataPath();
  if (existsSync(path)) {
    return JSON.parse(readFileSync(path, 'utf-8'));
  }
  return { worktrees: [] };
}

function saveWorkTreeMetadata(data: { worktrees: WorktreeMetadata[] }): void {
  const path = getWorkTreeMetadataPath();
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(data, null, 2), 'utf-8');
}

function recordWorktreeMetadata(branch: string, owner: string, issueLink?: string): void {
  const metadata = loadWorkTreeMetadata();
  const existing = metadata.worktrees.findIndex(w => w.branch === branch);
  const entry: WorktreeMetadata = {
    branch,
    owner,
    created_at: new Date().toISOString(),
    last_commit: new Date().toISOString(),
    status: 'active',
    files_touched: getFilesTouched(branch),
    issue_link: issueLink,
  };

  if (existing !== -1) {
    metadata.worktrees[existing] = { ...metadata.worktrees[existing], ...entry };
  } else {
    metadata.worktrees.push(entry);
  }

  saveWorkTreeMetadata(metadata);
}

function getAgeInDays(date: Date): number {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  return Math.floor(diffMs / (1000 * 60 * 60 * 24));
}

function getLifecycleState(ageInDays: number): string {
  if (ageInDays < ACTIVE_TTL_DAYS) return 'ACTIVE';
  if (ageInDays < ABANDONED_TTL_DAYS) return 'STALE';
  return 'ABANDONED';
}

function countActiveWorktrees(): { active: number; stale: number; abandoned: number } {
  const branches = getAllBranches();
  let active = 0,
    stale = 0,
    abandoned = 0;

  for (const branch of branches) {
    if (branch === 'main' || branch === 'master') continue;
    const lastCommit = getLastCommitDate(branch);
    const age = getAgeInDays(lastCommit);

    if (age < ACTIVE_TTL_DAYS) active++;
    else if (age < ABANDONED_TTL_DAYS) stale++;
    else abandoned++;
  }

  return { active, stale, abandoned };
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Validators
// ─────────────────────────────────────────────────────────────────────────────

function validateBranchNaming(branch: string): { valid: boolean; message: string } {
  if (!BRANCH_NAMING_REGEX.test(branch)) {
    return {
      valid: false,
      message: `Branch "${branch}" does not match semantic naming rule. Must match: (feature|fix|docs|chore|refactor|perf|test|ci|security)/[a-z0-9]+(-[a-z0-9]+)*`,
    };
  }
  return { valid: true, message: 'Branch matches semantic naming rule' };
}

function validateOwnership(branch: string): { valid: boolean; owner: string; verified: boolean } {
  try {
    const ownerEmail = run('git config user.email').trim();
    const recordedOwner = getBranchOwner(branch) || ownerEmail;
    const verified = ownerEmail === recordedOwner;

    return {
      valid: true,
      owner: recordedOwner,
      verified,
    };
  } catch {
    return {
      valid: false,
      owner: 'unknown',
      verified: false,
    };
  }
}

function validateSingleOwnership(branch: string): { valid: boolean; authors: number } {
  const authors = getCommitAuthors(branch);
  return {
    valid: authors.length === 1,
    authors: authors.length,
  };
}

function validateFrozenZones(branch: string): { valid: boolean; frozenCount: number; files: string[] } {
  const files = getFilesTouched(branch);
  const frozenFiles = files.filter(isFrozenZoneFile);
  return {
    valid: frozenFiles.length === 0,
    frozenCount: frozenFiles.length,
    files: frozenFiles,
  };
}

function validateLifecycle(branch: string): { valid: boolean; ageInDays: number; state: string; ttlRemaining: number } {
  const lastCommit = getLastCommitDate(branch);
  const ageInDays = getAgeInDays(lastCommit);
  const state = getLifecycleState(ageInDays);
  const ttlRemaining = Math.max(0, ABANDONED_TTL_DAYS - ageInDays);

  return {
    valid: state !== 'ABANDONED',
    ageInDays,
    state,
    ttlRemaining,
  };
}

function validateConcurrency(): { valid: boolean; active: number; limit: number } {
  const { active } = countActiveWorktrees();
  return {
    valid: active < CONCURRENCY_LIMIT,
    active,
    limit: CONCURRENCY_LIMIT,
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Context Modes
// ─────────────────────────────────────────────────────────────────────────────

function modePreCommit(): void {
  const branch = getCurrentBranch();

  if (!branch || branch === 'HEAD') {
    console.error('❌ Not on a branch');
    process.exit(1);
  }

  // Check naming
  const naming = validateBranchNaming(branch);
  if (!naming.valid) {
    console.error(`❌ ${naming.message}`);
    process.exit(1);
  }

  // Check ownership
  const ownership = validateOwnership(branch);
  if (!ownership.verified) {
    console.warn(`⚠️  Ownership not yet recorded. Recording: ${ownership.owner}`);
    recordWorktreeMetadata(branch, ownership.owner);
  }

  // Check frozen zones
  const frozen = validateFrozenZones(branch);
  if (!frozen.valid) {
    console.error(`❌ Frozen zone violation: ${frozen.files.join(', ')}`);
    process.exit(1);
  }

  // Check concurrency
  const concurrency = validateConcurrency();
  if (!concurrency.valid) {
    const { active, stale } = countActiveWorktrees();
    console.error(`❌ Concurrency limit reached (${active}/${CONCURRENCY_LIMIT})`);
    if (stale > 0) {
      console.error(`   (${stale} stale branches available for cleanup)`);
    }
    process.exit(1);
  }

  console.log('✅ Pre-commit validation passed');
  process.exit(0);
}

function modeCI(): void {
  const branch = getCurrentBranch();
  const prNumber = getArg('--pr-number');

  if (!branch) {
    console.error('❌ Unable to determine current branch');
    process.exit(1);
  }

  const report: ValidationReport = {
    schema_version: '1.0.0',
    timestamp: new Date().toISOString(),
    repository: run('git config --get remote.origin.url').split('/').pop()?.replace('.git', '') || 'unknown',
    context: 'ci',
    summary: {
      total_worktrees: getAllBranches().length - 1, // Exclude main
      active_worktrees: 0,
      stale_worktrees: 0,
      abandoned_worktrees: 0,
      concurrency_limit: CONCURRENCY_LIMIT,
      concurrency_used: 0,
      concurrency_status: 'healthy',
    },
    checks: {
      branch_naming: { status: 'pending', message: '' },
      ownership: { status: 'pending' },
      single_ownership: { status: 'pending' },
      frozen_zone: { status: 'pending', files_touched: [], frozen_files_touched: 0 },
      lifecycle: { status: 'pending', age_days: 0, ttl_remaining_days: 0, lifecycle_state: '' },
    },
    gates: [],
    warnings: [],
    errors: [],
    exit_code: 0,
  };

  // Branch naming
  const naming = validateBranchNaming(branch);
  report.checks.branch_naming.status = naming.valid ? 'pass' : 'fail';
  report.checks.branch_naming.message = naming.message;
  if (!naming.valid) report.errors.push(naming.message);

  // Ownership
  const ownership = validateOwnership(branch);
  report.checks.ownership.status = ownership.verified ? 'pass' : 'warn';
  report.checks.ownership.owner = ownership.owner;
  report.checks.ownership.verified_at = new Date().toISOString();
  if (!ownership.verified) report.warnings.push(`Ownership not verified: ${ownership.owner}`);

  // Single ownership
  const singleOwn = validateSingleOwnership(branch);
  report.checks.single_ownership.status = singleOwn.valid ? 'pass' : 'warn';
  report.checks.single_ownership.unique_authors = singleOwn.authors;
  if (!singleOwn.valid) {
    report.warnings.push(`Multiple authors detected (${singleOwn.authors}); requires coordination`);
  }

  // Frozen zones
  const frozen = validateFrozenZones(branch);
  const filesTouched = getFilesTouched(branch);
  report.checks.frozen_zone.status = frozen.valid ? 'pass' : 'fail';
  report.checks.frozen_zone.files_touched = filesTouched;
  report.checks.frozen_zone.frozen_files_touched = frozen.frozenCount;
  if (!frozen.valid) {
    report.errors.push(`Frozen zone violation: ${frozen.files.join(', ')}`);
  }

  // Lifecycle
  const lifecycle = validateLifecycle(branch);
  report.checks.lifecycle.status = lifecycle.valid ? 'pass' : 'warn';
  report.checks.lifecycle.age_days = lifecycle.ageInDays;
  report.checks.lifecycle.ttl_remaining_days = lifecycle.ttlRemaining;
  report.checks.lifecycle.lifecycle_state = lifecycle.state;
  if (!lifecycle.valid) {
    report.warnings.push(`Worktree abandoned (${lifecycle.ageInDays} days); schedule for cleanup`);
  }

  // Concurrency
  const concurrency = validateConcurrency();
  const counts = countActiveWorktrees();
  report.summary.active_worktrees = counts.active;
  report.summary.stale_worktrees = counts.stale;
  report.summary.abandoned_worktrees = counts.abandoned;
  report.summary.concurrency_used = counts.active;
  report.summary.concurrency_status = concurrency.valid ? 'healthy' : 'critical';

  // Build gates array
  report.gates.push(
    { name: 'branch_naming', status: report.checks.branch_naming.status, weight: 1 },
    { name: 'ownership_verified', status: report.checks.ownership.status, weight: 1 },
    { name: 'single_ownership', status: report.checks.single_ownership.status, weight: 1 },
    { name: 'frozen_zone', status: report.checks.frozen_zone.status, weight: 1 },
    { name: 'lifecycle', status: report.checks.lifecycle.status, weight: 1 },
  );

  // Determine exit code
  report.exit_code = report.errors.length > 0 ? 1 : report.warnings.length > 0 ? 0 : 0;

  console.log(JSON.stringify(report, null, 2));
  process.exit(report.exit_code);
}

function modeStatus(): void {
  const branches = getAllBranches();
  const counts = countActiveWorktrees();

  console.log('\n📊 Worktree Status Report\n');
  console.log(`Active: ${counts.active}/${CONCURRENCY_LIMIT}`);
  console.log(`Stale: ${counts.stale}`);
  console.log(`Abandoned: ${counts.abandoned}\n`);

  console.log('| Branch | Owner | Age (days) | Status |');
  console.log('|--------|-------|-----------|--------|');

  for (const branch of branches) {
    if (branch === 'main' || branch === 'master') continue;

    const lastCommit = getLastCommitDate(branch);
    const age = getAgeInDays(lastCommit);
    const state = getLifecycleState(age);
    const owner = getBranchOwner(branch) || '?';

    console.log(`| ${branch} | ${owner} | ${age} | ${state} |`);
  }

  console.log('');
}

function modeCleanup(): void {
  const branches = getAllBranches();
  const execute = hasFlag('--exec');
  const deleted: string[] = [];

  for (const branch of branches) {
    if (branch === 'main' || branch === 'master') continue;

    const lastCommit = getLastCommitDate(branch);
    const age = getAgeInDays(lastCommit);

    if (age > ABANDONED_TTL_DAYS) {
      deleted.push(`${branch} (${age} days old)`);

      if (execute) {
        run(`git branch -D ${branch}`, false);
        run(`git push origin :${branch}`, false);

        // Archive metadata
        const metadata = loadWorkTreeMetadata();
        const idx = metadata.worktrees.findIndex(w => w.branch === branch);
        if (idx !== -1) {
          metadata.worktrees[idx].status = 'deleted';
          saveWorkTreeMetadata(metadata);
        }
      }
    }
  }

  if (deleted.length === 0) {
    console.log('✅ No abandoned branches found');
  } else {
    const mode = execute ? 'Deleted' : 'Would delete';
    console.log(`${mode}:`);
    deleted.forEach(d => console.log(`  - ${d}`));
  }
}

function modeCountActive(): void {
  const counts = countActiveWorktrees();
  console.log(`${counts.active}/${CONCURRENCY_LIMIT}`);
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Entry
// ─────────────────────────────────────────────────────────────────────────────

const mode = process.argv[2];

if (mode === '--pre-commit') {
  modePreCommit();
} else if (mode === '--ci') {
  modeCI();
} else if (mode === '--status') {
  modeStatus();
} else if (mode === '--cleanup') {
  modeCleanup();
} else if (mode === '--count-active') {
  modeCountActive();
} else {
  console.error(`
Usage:
  bun scripts/worktree-validator.ts --pre-commit      Validate worktree before commit
  bun scripts/worktree-validator.ts --ci              Validate for CI/CD
  bun scripts/worktree-validator.ts --status          Show all worktree status
  bun scripts/worktree-validator.ts --cleanup         List abandoned branches (--exec to apply)
  bun scripts/worktree-validator.ts --count-active    Output count of active worktrees
`);
  process.exit(1);
}
