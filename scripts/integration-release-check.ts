#!/usr/bin/env bun
import { readdirSync, readFileSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const ROOT = resolve(import.meta.dir, '..');
const MANIFESTS_DIR = join(ROOT, 'integrations', 'manifests');
const required = ['id', 'channel', 'name', 'version', 'owner', 'status', 'authType'];
const semver = /^\d+\.\d+\.\d+$/;
let failed = false;

function normalizeRef(ref?: string) {
  return ref?.split('#')[0];
}

function fileRefExists(ref?: string) {
  const normalized = normalizeRef(ref);
  return !!normalized && existsSync(join(ROOT, normalized));
}

for (const file of readdirSync(MANIFESTS_DIR).filter((name) => name.endsWith('.json'))) {
  const fullPath = join(MANIFESTS_DIR, file);
  const manifest = JSON.parse(readFileSync(fullPath, 'utf-8'));
  const errors: string[] = [];

  for (const key of required) {
    if (!manifest[key]) errors.push(`missing ${key}`);
  }
  if (manifest.version && !semver.test(manifest.version)) {
    errors.push(`invalid semver: ${manifest.version}`);
  }

  for (const ref of [manifest.documentation?.ssot, manifest.documentation?.setup, manifest.documentation?.runbook]) {
    if (!fileRefExists(ref)) errors.push(`missing doc ref: ${ref}`);
  }

  if (!Array.isArray(manifest.runtimeProof) || manifest.runtimeProof.length === 0) {
    errors.push('missing runtimeProof');
  } else {
    for (const proof of manifest.runtimeProof) {
      if (!proof.kind || !proof.ref) errors.push('runtimeProof entry incomplete');
      else if (!fileRefExists(proof.ref)) errors.push(`missing runtime proof ref: ${proof.ref}`);
    }
  }

  if (!manifest.distribution?.kind || !manifest.distribution?.artifactRef || !manifest.distribution?.installCommand) {
    errors.push('distribution contract incomplete');
  }

  if (!fileRefExists(manifest.distribution?.artifactRef)) {
    errors.push(`missing artifact: ${manifest.distribution?.artifactRef}`);
  }
  if (manifest.distribution?.envExampleRef && !fileRefExists(manifest.distribution.envExampleRef)) {
    errors.push(`missing env example: ${manifest.distribution.envExampleRef}`);
  }

  if (!manifest.validation?.smokeCommand) {
    errors.push('missing validation.smokeCommand');
  } else {
    const smoke = spawnSync('bash', ['-lc', manifest.validation.smokeCommand], { cwd: ROOT, encoding: 'utf-8' });
    if (smoke.status !== 0) errors.push(`smoke command failed: ${manifest.validation.smokeCommand}`);
  }

  if (errors.length > 0) {
    failed = true;
    console.log(`❌ ${file}`);
    for (const error of errors) console.log(`  - ${error}`);
  } else {
    console.log(`✅ ${file}`);
  }
}

if (failed) {
  console.log('\nIntegration release check failed.');
  process.exit(1);
}

console.log('\nIntegration release check passed.');
