/**
 * REAL tests for repo-role.ts — Repository role detection.
 * Tests verify kernel/leaf/unknown detection and surface checks.
 *
 * Run: bun test packages/shared/src/__tests__/repo-role.test.ts
 */
import { describe, it, expect } from 'bun:test';
import { detectRepoRole, hasSurface, roleDescription } from '../repo-role';
import { resolve } from 'path';

const REPO_ROOT = resolve(import.meta.dir, '../../../../');

// ═══════════════════════════════════════════════════════════
// Kernel detection — this repo IS the kernel
// ═══════════════════════════════════════════════════════════
describe('Repo Role — Kernel detection', () => {
  it('detects current repo as kernel via heuristics', () => {
    const config = detectRepoRole(REPO_ROOT);
    // This repo has agents/runtime/runner.ts, packages/shared/src/index.ts, .guarani/IDENTITY.md
    expect(config.role).toBe('kernel');
  });
});

// ═══════════════════════════════════════════════════════════
// Unknown detection — non-EGOS directory
// ═══════════════════════════════════════════════════════════
describe('Repo Role — Unknown detection', () => {
  it('returns unknown for non-EGOS directory', () => {
    const config = detectRepoRole('/tmp');
    expect(config.role).toBe('unknown');
    expect(config.version).toBe('0.0.0');
  });
});

// ═══════════════════════════════════════════════════════════
// Surface checks
// ═══════════════════════════════════════════════════════════
describe('Repo Role — Surface checks', () => {
  it('returns false for non-existent surface', () => {
    const config = detectRepoRole(REPO_ROOT);
    expect(hasSurface(config, 'non_existent_surface')).toBe(false);
  });

  it('returns false for surfaces on unknown repos', () => {
    const config = detectRepoRole('/tmp');
    expect(hasSurface(config, 'gem_hunter')).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════
// Role description
// ═══════════════════════════════════════════════════════════
describe('Repo Role — Description', () => {
  it('generates readable description', () => {
    const config = detectRepoRole(REPO_ROOT);
    const desc = roleDescription(config);
    expect(desc).toContain('Role: kernel');
  });

  it('shows version in description', () => {
    const config = detectRepoRole('/tmp');
    const desc = roleDescription(config);
    expect(desc).toContain('0.0.0');
  });
});
