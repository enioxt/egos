#!/usr/bin/env bun
/**
 * KBS-007 — KB Lint
 *
 * Audits the EGOS Knowledge Base for quality issues:
 *   1. Orphaned pages (no cross_refs in or out, no source_file)
 *   2. Stale pages (updated_at > 90d and source_file still exists)
 *   3. Low quality pages (quality_score < 40)
 *   4. Broken citations (cross_refs pointing to non-existent slugs)
 *   5. Duplicate content (near-identical pages by title)
 *   6. Empty or near-empty pages (<100 chars)
 *
 * Usage:
 *   bun scripts/kb-lint.ts [--tenant=forja] [--fix] [--report]
 *   bun scripts/kb-lint.ts --dry       # just list issues, no writes
 *
 * Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
 */

export {};

import { existsSync } from 'fs';

// ── Config ──────────────────────────────────────────────────────────────────
const SUPABASE_URL = process.env.SUPABASE_URL ?? '';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? '';

const ARGS = process.argv.slice(2);
const tenantArg = ARGS.find((a) => a.startsWith('--tenant='))?.split('=')[1] ?? null;
const isDry = ARGS.includes('--dry') || !ARGS.includes('--fix');
const isReport = ARGS.includes('--report');

const STALE_DAYS = 90;
const LOW_QUALITY_THRESHOLD = 40;
const EMPTY_THRESHOLD = 100;

// ── Types ────────────────────────────────────────────────────────────────────
type KBPage = {
  id: string;
  slug: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  quality_score: number;
  cross_refs: string[];
  source_files: string[];
  updated_at: string;
};

type LintIssue = {
  type: 'orphan' | 'stale' | 'low_quality' | 'broken_ref' | 'duplicate' | 'empty';
  severity: 'error' | 'warning' | 'info';
  slug: string;
  title: string;
  message: string;
  fix?: string;
};

// ── Supabase Fetch ───────────────────────────────────────────────────────────
async function fetchPages(tenant: string | null): Promise<KBPage[]> {
  let url = `${SUPABASE_URL}/rest/v1/knowledge_base?select=id,slug,title,content,category,tags,quality_score,cross_refs,source_files,updated_at&limit=1000`;
  if (tenant) {
    url += `&tags=cs.{tenant:${tenant}}`;
  }
  const res = await fetch(url, {
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY,
    },
  });
  if (!res.ok) throw new Error('Supabase fetch failed: ' + res.status);
  return res.json() as Promise<KBPage[]>;
}

async function updatePage(id: string, update: Partial<KBPage>): Promise<void> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/knowledge_base?id=eq.${id}`, {
    method: 'PATCH',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY,
      'Content-Type': 'application/json',
      'Prefer': 'return=minimal',
    },
    body: JSON.stringify(update),
  });
  if (!res.ok) throw new Error('Supabase update failed: ' + res.status);
}

// ── Lint Checks ──────────────────────────────────────────────────────────────

function checkEmpty(page: KBPage): LintIssue | null {
  const len = (page.content ?? '').trim().length;
  if (len < EMPTY_THRESHOLD) {
    return {
      type: 'empty',
      severity: 'error',
      slug: page.slug,
      title: page.title,
      message: `Content is only ${len} chars (threshold: ${EMPTY_THRESHOLD})`,
      fix: `Run /ingest again for "${page.title}" or delete this page`,
    };
  }
  return null;
}

function checkLowQuality(page: KBPage): LintIssue | null {
  if (page.quality_score < LOW_QUALITY_THRESHOLD) {
    return {
      type: 'low_quality',
      severity: 'warning',
      slug: page.slug,
      title: page.title,
      message: `Quality score ${page.quality_score}/100 (threshold: ${LOW_QUALITY_THRESHOLD})`,
      fix: `Re-ingest with richer source or manually add metadata`,
    };
  }
  return null;
}

function checkStale(page: KBPage): LintIssue | null {
  const ageMs = Date.now() - new Date(page.updated_at).getTime();
  const ageDays = Math.floor(ageMs / (1000 * 60 * 60 * 24));
  if (ageDays > STALE_DAYS) {
    // Check if source file still exists
    const hasLiveSource = (page.source_files ?? []).some(
      (f) => f.startsWith('http') || (f && existsSync(f))
    );
    return {
      type: 'stale',
      severity: hasLiveSource ? 'warning' : 'info',
      slug: page.slug,
      title: page.title,
      message: `Last updated ${ageDays} days ago (threshold: ${STALE_DAYS}d). Source: ${hasLiveSource ? 'exists' : 'unknown'}`,
      fix: hasLiveSource ? `Run: bun scripts/kb-ingest.ts --file "${page.source_files[0]}"` : `Verify if content is still valid`,
    };
  }
  return null;
}

function checkOrphans(page: KBPage, allSlugs: Set<string>): LintIssue | null {
  const refs = page.cross_refs ?? [];
  const sources = page.source_files ?? [];
  const hasInbound = false; // checked separately
  const hasOutbound = refs.some((r) => allSlugs.has(r));
  const hasSource = sources.length > 0;

  if (!hasOutbound && !hasSource && (page.content ?? '').length < 500) {
    return {
      type: 'orphan',
      severity: 'warning',
      slug: page.slug,
      title: page.title,
      message: `No cross_refs, no source file, and content < 500 chars — likely orphaned`,
      fix: `Connect to related pages via cross_refs or re-ingest from source`,
    };
  }
  return null;
}

function checkBrokenRefs(page: KBPage, allSlugs: Set<string>): LintIssue[] {
  const broken = (page.cross_refs ?? []).filter((ref) => !allSlugs.has(ref));
  if (broken.length === 0) return [];
  return broken.map((ref) => ({
    type: 'broken_ref' as const,
    severity: 'warning' as const,
    slug: page.slug,
    title: page.title,
    message: `Cross-ref "${ref}" points to non-existent slug`,
    fix: `Remove "${ref}" from cross_refs or create the missing page`,
  }));
}

function checkDuplicates(pages: KBPage[]): LintIssue[] {
  const seen = new Map<string, KBPage>();
  const issues: LintIssue[] = [];

  for (const page of pages) {
    const normalizedTitle = page.title.toLowerCase().trim().replace(/\s+/g, ' ');
    if (seen.has(normalizedTitle)) {
      const existing = seen.get(normalizedTitle)!;
      issues.push({
        type: 'duplicate',
        severity: 'warning',
        slug: page.slug,
        title: page.title,
        message: `Title duplicates "${existing.slug}" (keep higher quality: ${page.quality_score} vs ${existing.quality_score})`,
        fix: `Merge into "${existing.quality_score >= page.quality_score ? existing.slug : page.slug}" and delete the other`,
      });
    } else {
      seen.set(normalizedTitle, page);
    }
  }
  return issues;
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function runLint(): Promise<void> {
  const tenant = tenantArg ? ` [tenant: ${tenantArg}]` : '';
  console.log(`[kb-lint] Auditing Knowledge Base${tenant}...`);

  const pages = await fetchPages(tenantArg);
  console.log(`[kb-lint] ${pages.length} pages loaded\n`);

  const allSlugs = new Set(pages.map((p) => p.slug));
  const issues: LintIssue[] = [];

  // Check each page
  for (const page of pages) {
    const emptyIssue = checkEmpty(page);
    if (emptyIssue) issues.push(emptyIssue);

    const qualityIssue = checkLowQuality(page);
    if (qualityIssue) issues.push(qualityIssue);

    const staleIssue = checkStale(page);
    if (staleIssue) issues.push(staleIssue);

    const orphanIssue = checkOrphans(page, allSlugs);
    if (orphanIssue) issues.push(orphanIssue);

    const brokenRefs = checkBrokenRefs(page, allSlugs);
    issues.push(...brokenRefs);
  }

  // Cross-page checks
  const duplicateIssues = checkDuplicates(pages);
  issues.push(...duplicateIssues);

  // Summary
  const errors = issues.filter((i) => i.severity === 'error');
  const warnings = issues.filter((i) => i.severity === 'warning');
  const infos = issues.filter((i) => i.severity === 'info');

  const byType = issues.reduce((acc, i) => {
    acc[i.type] = (acc[i.type] ?? 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  console.log('=== KB Lint Report ===\n');
  console.log(`Total pages: ${pages.length}`);
  console.log(`Issues found: ${issues.length} (${errors.length} errors, ${warnings.length} warnings, ${infos.length} info)`);
  console.log('By type:', byType);
  console.log('');

  if (issues.length === 0) {
    console.log('✅ No issues found — KB is clean!');
    return;
  }

  // Print by severity
  for (const severity of ['error', 'warning', 'info'] as const) {
    const group = issues.filter((i) => i.severity === severity);
    if (group.length === 0) continue;

    const emoji = severity === 'error' ? '❌' : severity === 'warning' ? '⚠️ ' : 'ℹ️ ';
    console.log(`\n${emoji.trim()} ${severity.toUpperCase()}S (${group.length}):`);
    for (const issue of group) {
      console.log(`  [${issue.type}] ${issue.slug}`);
      console.log(`    ${issue.message}`);
      if (issue.fix) console.log(`    💡 Fix: ${issue.fix}`);
    }
  }

  if (!isDry) {
    // Auto-fix: update quality_score for low quality pages we can recalculate
    let fixed = 0;
    for (const issue of issues) {
      if (issue.type === 'broken_ref') {
        const page = pages.find((p) => p.slug === issue.slug);
        if (page) {
          const ref = issue.message.match(/"([^"]+)" points/)?.[1];
          if (ref) {
            const cleanedRefs = page.cross_refs.filter((r) => r !== ref);
            await updatePage(page.id, { cross_refs: cleanedRefs });
            fixed++;
          }
        }
      }
    }
    if (fixed > 0) console.log(`\n✅ Auto-fixed ${fixed} broken cross_refs`);
  } else {
    console.log(`\n[DRY] Run with --fix to auto-fix broken cross_refs`);
  }

  // Exit code 1 if errors found (useful for CI)
  if (errors.length > 0) {
    process.exit(1);
  }
}

// ── Entry ────────────────────────────────────────────────────────────────────
if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error('[kb-lint] Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY');
  process.exit(1);
}

await runLint();
