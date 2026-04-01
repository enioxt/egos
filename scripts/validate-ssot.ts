#!/usr/bin/env bun

/**
 * SSOT Consistency Validator (GH-040)
 *
 * Validates drift between:
 * - agents.json (agent registry)
 * - TASKS.md (work tracker)
 * - HARVEST.md (patterns + decisions)
 * - docs/CAPABILITY_REGISTRY.md
 *
 * Exit codes:
 * - 0: no drift detected
 * - 1: drift found, must fix before merge
 * - 2: fatal error (missing critical files)
 */

import * as fs from 'fs';
import * as path from 'path';

// ─── Config ────────────────────────────────────────────────────────────────

const ROOT = process.cwd();
const CRITICAL_FILES = [
  'TASKS.md',
  'agents/registry/agents.json',
  'docs/knowledge/HARVEST.md',
  'docs/CAPABILITY_REGISTRY.md',
  '.guarani/RULES_INDEX.md',
];

interface ValidationResult {
  passed: boolean;
  errors: string[];
  warnings: string[];
}

// ─── Validators ────────────────────────────────────────────────────────────

function validateFilesExist(): ValidationResult {
  const result: ValidationResult = { passed: true, errors: [], warnings: [] };

  for (const file of CRITICAL_FILES) {
    const fullPath = path.join(ROOT, file);
    if (!fs.existsSync(fullPath)) {
      result.errors.push(`❌ Critical file missing: ${file}`);
      result.passed = false;
    }
  }

  return result;
}

function validateAgentsJson(): ValidationResult {
  const result: ValidationResult = { passed: true, errors: [], warnings: [] };

  try {
    const agentsPath = path.join(ROOT, 'agents/registry/agents.json');
    const agentsJson = JSON.parse(fs.readFileSync(agentsPath, 'utf-8'));
    const agentIds = new Set<string>();

    // Collect all agent IDs (both direct agents and in groups)
    function collectIds(obj: any): void {
      if (Array.isArray(obj)) {
        for (const item of obj) {
          if (item.id) agentIds.add(item.id);
          collectIds(item);
        }
      } else if (typeof obj === 'object' && obj !== null) {
        for (const value of Object.values(obj)) {
          collectIds(value);
        }
      }
    }

    collectIds(agentsJson);

    // Check agents.json structure
    if (!agentsJson.agents && !Array.isArray(Object.values(agentsJson)[0])) {
      result.warnings.push('⚠️  agents.json structure non-standard (expected .agents array)');
    }

    // Verify all IDs are valid kebab-case
    for (const id of agentIds) {
      if (typeof id !== 'string' || !/^[a-z0-9\-]+$/.test(id)) {
        result.errors.push(`❌ Invalid agent ID format: ${id} (must be kebab-case)`);
        result.passed = false;
      }
    }

    result.warnings.push(`✓ Found ${agentIds.size} registered agent IDs`);
  } catch (e) {
    result.errors.push(`❌ Failed to parse agents.json: ${e}`);
    result.passed = false;
  }

  return result;
}

function validateTasksCompleteness(): ValidationResult {
  const result: ValidationResult = { passed: true, errors: [], warnings: [] };

  try {
    const tasksPath = path.join(ROOT, 'TASKS.md');
    const content = fs.readFileSync(tasksPath, 'utf-8');

    // Check for required sections (P0/P1/P2 priority markers)
    const requiredPatterns = [/\*\*P0\s*[—–]/m, /\*\*P1\s*[—–]/m, /\*\*P2\s*[—–]/m];
    for (const pattern of requiredPatterns) {
      if (!pattern.test(content)) {
        result.errors.push(`❌ TASKS.md missing priority section: ${pattern.source}`);
        result.passed = false;
      }
    }

    // Check line count (should be < 500 per governance rule)
    const lines = content.split('\n').length;
    if (lines > 500) {
      result.warnings.push(
        `⚠️  TASKS.md is ${lines} lines (governance target: < 500). Consider archiving to TASKS_ARCHIVE.md.`,
      );
    }

    // Warn if P0 section has many open items
    const p0Match = content.match(/## P0[\s\S]*?(?=## P1|$)/);
    if (p0Match) {
      const p0Content = p0Match[0];
      const openItems = (p0Content.match(/\- \[ \]/g) || []).length;
      if (openItems > 5) {
        result.warnings.push(`⚠️  ${openItems} open P0 items (high priority)`);
      }
    }

    result.warnings.push(`✓ TASKS.md structure valid (${lines} lines)`);
  } catch (e) {
    result.errors.push(`❌ Failed to validate TASKS.md: ${e}`);
    result.passed = false;
  }

  return result;
}

function validateHarvestReferences(): ValidationResult {
  const result: ValidationResult = { passed: true, errors: [], warnings: [] };

  try {
    const harvestPath = path.join(ROOT, 'docs/knowledge/HARVEST.md');
    const content = fs.readFileSync(harvestPath, 'utf-8');

    // Check for dead markdown links [text](path)
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    let match;
    const deadLinks: string[] = [];

    while ((match = linkRegex.exec(content)) !== null) {
      const linkText = match[1];
      const linkPath = match[2];

      // Skip external URLs
      if (linkPath.startsWith('http://') || linkPath.startsWith('https://')) {
        continue;
      }

      // Skip relative paths that point to valid files
      const resolvedPath = path.join(ROOT, 'docs/knowledge', linkPath);
      if (!fs.existsSync(resolvedPath)) {
        deadLinks.push(linkPath);
      }
    }

    if (deadLinks.length > 0) {
      result.errors.push(`❌ HARVEST.md has ${deadLinks.length} broken links: ${deadLinks.join(', ')}`);
      result.passed = false;
    } else {
      result.warnings.push('✓ HARVEST.md links validated');
    }

    // Check for timestamp markers (should be removed per SSOT)
    if (content.match(/\*\*Data de análise:\*\*/i) || content.match(/2026-\d{2}-\d{2}/)) {
      result.warnings.push('⚠️  HARVEST.md contains date markers (should be evergreen, no timestamps)');
    }
  } catch (e) {
    result.errors.push(`❌ Failed to validate HARVEST.md: ${e}`);
    result.passed = false;
  }

  return result;
}

function validateCapabilityRegistry(): ValidationResult {
  const result: ValidationResult = { passed: true, errors: [], warnings: [] };

  try {
    const regPath = path.join(ROOT, 'docs/CAPABILITY_REGISTRY.md');
    const content = fs.readFileSync(regPath, 'utf-8');

    // Check structure
    if (!content.includes('##')) {
      result.errors.push('❌ CAPABILITY_REGISTRY.md has no section headers');
      result.passed = false;
    }

    // Verify sync with HARVEST
    const harvestPath = path.join(ROOT, 'docs/knowledge/HARVEST.md');
    const harvestContent = fs.readFileSync(harvestPath, 'utf-8');

    // Both should reference key patterns
    const patterns = ['fire-and-forget', 'lazy-init', 'contract-test'];
    for (const pattern of patterns) {
      const inCapability = content.toLowerCase().includes(pattern);
      const inHarvest = harvestContent.toLowerCase().includes(pattern);

      if (inCapability !== inHarvest) {
        result.warnings.push(
          `⚠️  Pattern "${pattern}" mentioned in one but not both of CAPABILITY_REGISTRY and HARVEST`,
        );
      }
    }

    result.warnings.push('✓ CAPABILITY_REGISTRY.md structure valid');
  } catch (e) {
    result.errors.push(`❌ Failed to validate CAPABILITY_REGISTRY: ${e}`);
    result.passed = false;
  }

  return result;
}

// ─── Runner ────────────────────────────────────────────────────────────────

async function validate() {
  console.log('🔍 SSOT Consistency Validator (GH-040)\n');

  const validators = [
    { name: 'Critical Files', fn: validateFilesExist },
    { name: 'agents.json', fn: validateAgentsJson },
    { name: 'TASKS.md', fn: validateTasksCompleteness },
    { name: 'HARVEST.md', fn: validateHarvestReferences },
    { name: 'CAPABILITY_REGISTRY', fn: validateCapabilityRegistry },
  ];

  let allPassed = true;
  const allErrors: string[] = [];
  const allWarnings: string[] = [];

  for (const { name, fn } of validators) {
    console.log(`\n📋 Validating: ${name}`);
    const result = fn();

    if (result.errors.length > 0) {
      allPassed = false;
      result.errors.forEach((err) => console.log(`  ${err}`));
    }

    result.warnings.forEach((warn) => console.log(`  ${warn}`));

    allErrors.push(...result.errors);
    allWarnings.push(...result.warnings);
  }

  // Summary
  console.log('\n' + '─'.repeat(70));
  if (allPassed) {
    console.log('✅ SSOT VALIDATION PASSED');
    console.log(`   ${allWarnings.length} info/warnings (non-blocking)`);
    process.exit(0);
  } else {
    console.log('❌ SSOT VALIDATION FAILED');
    console.log(`   ${allErrors.length} errors (must fix before merge)`);
    console.log(`   ${allWarnings.length} warnings`);
    process.exit(1);
  }
}

validate().catch((e) => {
  console.error('💥 Fatal error:', e);
  process.exit(2);
});
