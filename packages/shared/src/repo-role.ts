/**
 * Repo Role Detection — EGOS-049
 *
 * Detects whether the current repo is a kernel, lab, or leaf,
 * and which surfaces are available. This allows shared workflows
 * and scripts to adapt behavior per repo context.
 *
 * Usage:
 *   import { detectRepoRole, hasSurface } from '@egos/shared';
 *   const role = detectRepoRole('/path/to/repo');
 *   if (hasSurface(role, 'gem_hunter')) { ... }
 */

import { existsSync, readFileSync } from 'fs';
import { resolve } from 'path';

export type RepoRole = 'kernel' | 'lab' | 'leaf' | 'unknown';

export interface EgosConfig {
  role: RepoRole;
  version: string;
  surfaces: Record<string, boolean>;
  governance?: {
    check_command?: string;
    sync_command?: string;
    activation_command?: string;
  };
}

const DEFAULT_CONFIG: EgosConfig = {
  role: 'unknown',
  version: '0.0.0',
  surfaces: {},
};

/**
 * Reads egos.config.json from a repo root. Returns default if missing.
 */
export function detectRepoRole(repoRoot: string): EgosConfig {
  const configPath = resolve(repoRoot, 'egos.config.json');
  if (!existsSync(configPath)) {
    // Heuristic fallback: check for kernel markers
    const hasRunner = existsSync(resolve(repoRoot, 'agents/runtime/runner.ts'));
    const hasShared = existsSync(resolve(repoRoot, 'packages/shared/src/index.ts'));
    const hasGuarani = existsSync(resolve(repoRoot, '.guarani/IDENTITY.md'));

    if (hasRunner && hasShared && hasGuarani) {
      return { ...DEFAULT_CONFIG, role: 'kernel' };
    }
    if (hasGuarani) {
      return { ...DEFAULT_CONFIG, role: 'leaf' };
    }
    return DEFAULT_CONFIG;
  }

  try {
    const raw = readFileSync(configPath, 'utf-8');
    const parsed = JSON.parse(raw) as EgosConfig;
    return { ...DEFAULT_CONFIG, ...parsed };
  } catch {
    return DEFAULT_CONFIG;
  }
}

/**
 * Check if a repo has a specific surface available.
 */
export function hasSurface(config: EgosConfig, surface: string): boolean {
  return config.surfaces[surface] === true;
}

/**
 * Returns a human-readable summary of the repo role and surfaces.
 */
export function roleDescription(config: EgosConfig): string {
  const active = Object.entries(config.surfaces)
    .filter(([, v]) => v)
    .map(([k]) => k);
  const inactive = Object.entries(config.surfaces)
    .filter(([, v]) => !v)
    .map(([k]) => k);

  return [
    `Role: ${config.role} (v${config.version})`,
    `Active surfaces (${active.length}): ${active.join(', ') || 'none'}`,
    `Inactive (${inactive.length}): ${inactive.join(', ') || 'none'}`,
  ].join('\n');
}
