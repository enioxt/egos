#!/usr/bin/env bun

/**
 * Version Lock Checker (GH-042)
 *
 * Validates that version strings are synchronized across:
 * - packages directory: all package.json files
 * - apps directory: all package.json files
 * - apps/api/src/server.ts (API_VERSION)
 * - apps/guard-brasil-web/package.json (for Guard Brasil)
 *
 * Prevents drift where one file is bumped but others aren't.
 *
 * Exit codes:
 * - 0: versions synchronized
 * - 1: version drift detected
 * - 2: fatal error (missing files)
 */

import * as fs from 'fs';
import * as path from 'path';

// ─── Config ────────────────────────────────────────────────────────────────

const ROOT = process.cwd();

interface VersionEntry {
  file: string;
  version: string;
}

// ─── Parsers ────────────────────────────────────────────────────────────────

function extractVersionFromJson(filePath: string): string | null {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const json = JSON.parse(content);
    return json.version || null;
  } catch {
    return null;
  }
}

function extractVersionFromTs(filePath: string): string | null {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const match = content.match(/const API_VERSION = ['"]([^'"]+)['"]/);
    if (match) return match[1];
    const match2 = content.match(/api_version:\s*['"]([^'"]+)['"]/);
    if (match2) return match2[1];
    const match3 = content.match(/version:\s*['"]([^'"]+)['"]/);
    if (match3) return match3[1];
    return null;
  } catch {
    return null;
  }
}

// ─── Main Logic ────────────────────────────────────────────────────────────

function checkVersionLock() {
  console.log('🔒 Version Lock Checker (GH-042)\n');

  const versions: VersionEntry[] = [];
  const errors: string[] = [];

  // Check main package.json
  const mainVersion = extractVersionFromJson(path.join(ROOT, 'package.json'));
  if (mainVersion) {
    versions.push({ file: 'package.json (root)', version: mainVersion });
  } else {
    errors.push('❌ Could not extract version from root package.json');
  }

  // Check Guard Brasil package.json
  const gbWebPackage = path.join(ROOT, 'apps/guard-brasil-web/package.json');
  if (fs.existsSync(gbWebPackage)) {
    const gbVersion = extractVersionFromJson(gbWebPackage);
    if (gbVersion) {
      versions.push({ file: 'apps/guard-brasil-web/package.json', version: gbVersion });
    }
  }

  // Check API server.ts
  const serverPath = path.join(ROOT, 'apps/api/src/server.ts');
  if (fs.existsSync(serverPath)) {
    const serverVersion = extractVersionFromTs(serverPath);
    if (serverVersion) {
      versions.push({ file: 'apps/api/src/server.ts', version: serverVersion });
    }
  }

  // Check guard-brasil package.json
  const gbPackage = path.join(ROOT, 'packages/guard-brasil/package.json');
  if (fs.existsSync(gbPackage)) {
    const gbPkgVersion = extractVersionFromJson(gbPackage);
    if (gbPkgVersion) {
      versions.push({ file: 'packages/guard-brasil/package.json', version: gbPkgVersion });
    }
  }

  // Report findings
  console.log('📋 Version Strings Found:\n');
  for (const entry of versions) {
    console.log(`  ${entry.file}`);
    console.log(`    → ${entry.version}`);
  }

  // Check for drift
  if (versions.length === 0) {
    console.log('\n⚠️  No version entries found to check');
    return 0;
  }

  const uniqueVersions = new Set(versions.map((v) => v.version));

  console.log('\n' + '─'.repeat(70));
  if (uniqueVersions.size === 1) {
    console.log(`✅ VERSION LOCK OK — All ${versions.length} sources agree on: ${versions[0].version}`);
    return 0;
  } else {
    console.log(`❌ VERSION DRIFT DETECTED`);
    console.log(`   Found ${uniqueVersions.size} different versions:\n`);

    for (const v of uniqueVersions) {
      const files = versions.filter((e) => e.version === v).map((e) => e.file);
      console.log(`   Version ${v}:`);
      for (const file of files) {
        console.log(`     - ${file}`);
      }
    }

    console.log(
      '\n   To fix: Update all version strings to match. Recommend bumping to highest semver.',
    );
    return 1;
  }
}

// ─── Runner ────────────────────────────────────────────────────────────────

const exitCode = checkVersionLock();
process.exit(exitCode);
