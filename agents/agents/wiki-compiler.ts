#!/usr/bin/env bun
/**
 * EGOS Wiki Compiler Agent
 *
 * Reads raw sources (handoffs, job reports, gem-hunter findings, session memory)
 * and compiles them into structured wiki pages in Supabase (egos_wiki_pages).
 *
 * Pattern: Karpathy LLM Wiki (3-layer: raw → wiki → schema)
 * Inspired by: PAL compiler agent + Karpathy gist
 *
 * Operations:
 *   --compile   Scan raw sources, create/update wiki pages
 *   --lint      Health-check: orphan pages, stale content, missing cross-refs
 *   --index     Generate index (returns JSON summary of all pages)
 *   --world     Generate wiki pages from world-model snapshot (tasks, agents, signals)
 *   --dry       Preview changes without writing to Supabase
 *
 * Usage:
 *   bun agents/agents/wiki-compiler.ts --compile --dry
 *   bun agents/agents/wiki-compiler.ts --lint
 *   bun agents/agents/wiki-compiler.ts --index
 */

import { readFileSync, readdirSync, existsSync, statSync } from "fs";
import { join, basename } from "path";

// ── Config ────────────────────────────────────────────────────────────

const ROOT = "/home/enio/egos";
const DRY_RUN = process.argv.includes("--dry");
const MODE = process.argv.includes("--lint")
  ? "lint"
  : process.argv.includes("--index")
    ? "index"
    : process.argv.includes("--world")
      ? "world"
      : "compile";

const SUPABASE_URL = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || "";

// Raw source directories to scan
const RAW_SOURCES = [
  { path: join(ROOT, "docs/jobs"), category: "synthesis" as const, prefix: "job" },
  { path: join(ROOT, "docs/gem-hunter"), category: "synthesis" as const, prefix: "gem" },
  { path: join(ROOT, "docs/_current_handoffs"), category: "synthesis" as const, prefix: "handoff" },
  { path: join(ROOT, "docs/strategy"), category: "decision" as const, prefix: "strategy" },
  { path: join(ROOT, "docs/research"), category: "pattern" as const, prefix: "research" },
];

// ── Types ─────────────────────────────────────────────────────────────

interface WikiPage {
  slug: string;
  title: string;
  content: string;
  category: "concept" | "entity" | "decision" | "pattern" | "synthesis" | "how-to";
  tags: string[];
  cross_refs: string[];
  source_files: string[];
  quality_score: number;
}

interface LintResult {
  type: "orphan" | "stale" | "missing_crossref" | "low_quality" | "duplicate_topic";
  page_slug: string;
  detail: string;
  severity: "info" | "warning" | "error";
}

interface RawSource {
  file: string;
  title: string;
  content: string;
  category: WikiPage["category"];
  modified: Date;
}

// ── Supabase Client (minimal, no SDK dep) ─────────────────────────────

async function supabaseQuery(table: string, method: string, body?: unknown, params?: string): Promise<unknown> {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    console.warn("[wiki-compiler] Supabase not configured — local-only mode");
    return null;
  }

  const url = `${SUPABASE_URL}/rest/v1/${table}${params ? `?${params}` : ""}`;
  const headers: Record<string, string> = {
    apikey: SUPABASE_KEY,
    Authorization: `Bearer ${SUPABASE_KEY}`,
    "Content-Type": "application/json",
    Prefer: method === "POST" ? "return=representation,resolution=merge-duplicates" : "return=representation",
  };

  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const err = await res.text();
    console.error(`[wiki-compiler] Supabase ${method} ${table}: ${res.status} ${err}`);
    return null;
  }

  return res.json();
}

// ── Raw Source Scanner ─────────────────────────────────────────────────

function scanRawSources(): RawSource[] {
  const sources: RawSource[] = [];

  for (const src of RAW_SOURCES) {
    if (!existsSync(src.path)) continue;

    const files = readdirSync(src.path).filter((f) => f.endsWith(".md"));
    for (const file of files) {
      const fullPath = join(src.path, file);
      const stat = statSync(fullPath);
      const content = readFileSync(fullPath, "utf8");
      const titleMatch = content.match(/^#\s+(.+)/m);
      const title = titleMatch?.[1] ?? basename(file, ".md").replace(/[-_]/g, " ");

      sources.push({
        file: fullPath.replace(ROOT + "/", ""),
        title: title.slice(0, 120),
        content,
        category: src.category,
        modified: stat.mtime,
      });
    }
  }

  return sources;
}

// ── Slug Generator ────────────────────────────────────────────────────

function toSlug(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 80)
    .replace(/^-|-$/g, "");
}

// ── Tag Extractor ─────────────────────────────────────────────────────

function extractTags(content: string): string[] {
  const tags = new Set<string>();

  // Domain keywords
  const keywords: Record<string, RegExp> = {
    "guard-brasil": /guard.?brasil|pii|lgpd/i,
    "gem-hunter": /gem.?hunter|discovery|trending/i,
    "eagle-eye": /eagle.?eye|licita/i,
    "stripe": /stripe|billing|monetiz/i,
    "governance": /governance|drift|ssot|audit/i,
    "security": /security|cve|vulnerab/i,
    "infrastructure": /vps|docker|caddy|deploy/i,
    "agents": /agent|runner|orchestrat/i,
    "supabase": /supabase|postgres/i,
  };

  for (const [tag, pattern] of Object.entries(keywords)) {
    if (pattern.test(content)) tags.add(tag);
  }

  return [...tags];
}

// ── Cross-Reference Detector ──────────────────────────────────────────

function extractCrossRefs(content: string, allSlugs: string[]): string[] {
  const refs: string[] = [];
  for (const slug of allSlugs) {
    // Check if content mentions terms that would match another page's slug
    const pattern = slug.replace(/-/g, "[\\s-]?");
    if (new RegExp(pattern, "i").test(content)) {
      refs.push(slug);
    }
  }
  return refs;
}

// ── Quality Scorer ────────────────────────────────────────────────────

function scoreQuality(content: string): number {
  let score = 30; // base

  const lines = content.split("\n");
  const wordCount = content.split(/\s+/).length;

  // Length (max 20 pts)
  if (wordCount > 100) score += 5;
  if (wordCount > 300) score += 5;
  if (wordCount > 500) score += 5;
  if (wordCount > 1000) score += 5;

  // Structure (max 20 pts)
  if (lines.some((l) => l.startsWith("## "))) score += 5;
  if (lines.some((l) => l.startsWith("### "))) score += 5;
  if (lines.some((l) => l.startsWith("- "))) score += 5;
  if (lines.some((l) => l.startsWith("|"))) score += 5;

  // Metadata (max 15 pts)
  if (/\*\*Date\*\*|\*\*Status\*\*|date:/i.test(content)) score += 5;
  if (/\*\*Author\*\*|author:/i.test(content)) score += 5;
  if (content.includes("```")) score += 5;

  // Freshness (max 15 pts) — check for recent dates
  const dateMatch = content.match(/2026-04/);
  if (dateMatch) score += 15;
  else if (content.match(/2026-03/)) score += 10;
  else score += 0;

  return Math.min(score, 100);
}

// ── Compile Operation ─────────────────────────────────────────────────

async function compile(): Promise<void> {
  console.log("[wiki-compiler] Scanning raw sources...");
  const sources = scanRawSources();
  console.log(`[wiki-compiler] Found ${sources.length} raw source files`);

  // Build pages from raw sources
  const pages: WikiPage[] = [];
  const allSlugs: string[] = [];

  for (const src of sources) {
    const slug = toSlug(src.title);
    if (!slug || allSlugs.includes(slug)) continue;
    allSlugs.push(slug);

    pages.push({
      slug,
      title: src.title,
      content: src.content,
      category: src.category,
      tags: extractTags(src.content),
      cross_refs: [], // filled after all slugs known
      source_files: [src.file],
      quality_score: scoreQuality(src.content),
    });
  }

  // Second pass: cross-references
  for (const page of pages) {
    page.cross_refs = extractCrossRefs(page.content, allSlugs).filter(
      (ref) => ref !== page.slug
    );
  }

  console.log(`[wiki-compiler] Compiled ${pages.length} wiki pages`);

  // Stats
  const byCategory = pages.reduce(
    (acc, p) => {
      acc[p.category] = (acc[p.category] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );
  console.log(`[wiki-compiler] Categories: ${JSON.stringify(byCategory)}`);

  const avgQuality = Math.round(
    pages.reduce((s, p) => s + p.quality_score, 0) / (pages.length || 1)
  );
  console.log(`[wiki-compiler] Avg quality score: ${avgQuality}/100`);

  if (DRY_RUN) {
    console.log("\n[wiki-compiler] DRY RUN — pages that would be upserted:");
    for (const p of pages.slice(0, 15)) {
      console.log(
        `  ${p.slug} [${p.category}] q=${p.quality_score} tags=[${p.tags.join(",")}] refs=${p.cross_refs.length}`
      );
    }
    if (pages.length > 15) console.log(`  ... and ${pages.length - 15} more`);
    return;
  }

  // Upsert to Supabase
  let upserted = 0;
  for (const page of pages) {
    const result = await supabaseQuery(
      "egos_wiki_pages",
      "POST",
      {
        slug: page.slug,
        title: page.title,
        content: page.content,
        category: page.category,
        tags: page.tags,
        cross_refs: page.cross_refs,
        source_files: page.source_files,
        compiled_by: "wiki-compiler",
        quality_score: page.quality_score,
        updated_at: new Date().toISOString(),
      },
      "on_conflict=slug"
    );

    if (result) {
      upserted++;
      // Log to changelog
      await supabaseQuery("egos_wiki_changelog", "POST", {
        page_id: (result as any[])?.[0]?.id,
        action: "updated",
        diff_summary: `Compiled from ${page.source_files.join(", ")}`,
        compiled_by: "wiki-compiler",
      });
    }
  }

  console.log(`[wiki-compiler] Upserted ${upserted}/${pages.length} pages to Supabase`);
}

// ── Lint Operation ────────────────────────────────────────────────────

async function lint(): Promise<void> {
  console.log("[wiki-compiler] Running knowledge base lint...");

  const results: LintResult[] = [];

  // Fetch all pages from Supabase
  const pages = (await supabaseQuery(
    "egos_wiki_pages",
    "GET",
    undefined,
    "select=slug,title,category,tags,cross_refs,quality_score,updated_at,source_files"
  )) as WikiPage[] | null;

  if (!pages || pages.length === 0) {
    console.log("[wiki-compiler] No pages in wiki — run --compile first");
    return;
  }

  const allSlugs = new Set(pages.map((p) => p.slug));

  for (const page of pages) {
    // Check broken cross-refs
    for (const ref of page.cross_refs || []) {
      if (!allSlugs.has(ref)) {
        results.push({
          type: "missing_crossref",
          page_slug: page.slug,
          detail: `Cross-ref "${ref}" points to non-existent page`,
          severity: "warning",
        });
      }
    }

    // Check low quality
    if (page.quality_score < 40) {
      results.push({
        type: "low_quality",
        page_slug: page.slug,
        detail: `Quality score ${page.quality_score}/100 — needs enrichment`,
        severity: "warning",
      });
    }

    // Check stale content (>7 days without update)
    const updatedAt = new Date((page as any).updated_at);
    const daysSinceUpdate = (Date.now() - updatedAt.getTime()) / (1000 * 60 * 60 * 24);
    if (daysSinceUpdate > 7) {
      results.push({
        type: "stale",
        page_slug: page.slug,
        detail: `Last updated ${Math.round(daysSinceUpdate)} days ago`,
        severity: daysSinceUpdate > 30 ? "error" : "info",
      });
    }

    // Check orphan pages (no cross-refs pointing to them)
    const incomingRefs = pages.filter(
      (p) => p.slug !== page.slug && (p.cross_refs || []).includes(page.slug)
    );
    if (incomingRefs.length === 0 && (page.cross_refs || []).length === 0) {
      results.push({
        type: "orphan",
        page_slug: page.slug,
        detail: "No incoming or outgoing cross-references",
        severity: "info",
      });
    }

    // Check source files still exist
    for (const src of page.source_files || []) {
      if (!existsSync(join(ROOT, src))) {
        results.push({
          type: "stale",
          page_slug: page.slug,
          detail: `Source file "${src}" no longer exists`,
          severity: "warning",
        });
      }
    }
  }

  // Report
  const errors = results.filter((r) => r.severity === "error");
  const warnings = results.filter((r) => r.severity === "warning");
  const infos = results.filter((r) => r.severity === "info");

  console.log(`\n[wiki-compiler] Lint Results:`);
  console.log(`  Pages: ${pages.length}`);
  console.log(`  Errors: ${errors.length}`);
  console.log(`  Warnings: ${warnings.length}`);
  console.log(`  Info: ${infos.length}`);

  if (errors.length > 0) {
    console.log(`\n  ERRORS:`);
    for (const r of errors) console.log(`    [${r.type}] ${r.page_slug}: ${r.detail}`);
  }
  if (warnings.length > 0) {
    console.log(`\n  WARNINGS:`);
    for (const r of warnings) console.log(`    [${r.type}] ${r.page_slug}: ${r.detail}`);
  }

  // Log lint run
  if (!DRY_RUN) {
    await supabaseQuery("egos_learnings", "POST", {
      domain: "governance",
      outcome: errors.length > 0 ? "failure" : "success",
      summary: `Wiki lint: ${pages.length} pages, ${errors.length} errors, ${warnings.length} warnings`,
      detail: JSON.stringify(results.slice(0, 20)),
      pattern: "wiki-lint",
      impact: errors.length > 3 ? "high" : warnings.length > 5 ? "medium" : "low",
    });
  }
}

// ── Index Operation ───────────────────────────────────────────────────

async function generateIndex(): Promise<void> {
  console.log("[wiki-compiler] Generating wiki index...");

  // Fetch all pages
  const pages = (await supabaseQuery(
    "egos_wiki_pages",
    "GET",
    undefined,
    "select=slug,title,category,tags,quality_score,updated_at&order=category,title"
  )) as Array<{ slug: string; title: string; category: string; tags: string[]; quality_score: number; updated_at: string }> | null;

  if (!pages || pages.length === 0) {
    console.log("[wiki-compiler] No pages — run --compile first");
    return;
  }

  // Group by category
  const grouped: Record<string, typeof pages> = {};
  for (const p of pages) {
    if (!grouped[p.category]) grouped[p.category] = [];
    grouped[p.category].push(p);
  }

  const avgQuality = Math.round(pages.reduce((s, p) => s + p.quality_score, 0) / pages.length);

  console.log(`\n  EGOS Knowledge Base Index`);
  console.log(`  ========================`);
  console.log(`  Total pages: ${pages.length} | Avg quality: ${avgQuality}/100`);
  console.log(`  Last compiled: ${new Date().toISOString().slice(0, 16)}\n`);

  for (const [cat, catPages] of Object.entries(grouped)) {
    console.log(`  ## ${cat} (${catPages.length})`);
    for (const p of catPages) {
      const freshness = ((Date.now() - new Date(p.updated_at).getTime()) / 86400000) < 3 ? "NEW" : "";
      console.log(`    - [${p.slug}] ${p.title} (q=${p.quality_score}) ${freshness}`);
    }
    console.log();
  }
}

// ── World Model → Wiki ────────────────────────────────────────────────

async function compileWorldModel(): Promise<void> {
  console.log("[wiki-compiler] Generating wiki pages from world-model snapshot...");

  let worldModel: any;
  try {
    const wmModule = await import("../../packages/shared/src/world-model.js");
    worldModel = wmModule.buildWorldModel();
  } catch (err) {
    console.error("[wiki-compiler] Failed to import world-model:", err);
    return;
  }

  const pages: WikiPage[] = [];

  // System overview page
  pages.push({
    slug: "egos-system-overview",
    title: "EGOS System Overview",
    content: [
      `# EGOS System Overview`,
      ``,
      `**Generated:** ${worldModel.generated_at}`,
      `**Git:** ${worldModel.git_sha} (${worldModel.git_branch})`,
      `**Health:** ${worldModel.health_pct}% (${worldModel.tasks.done}/${worldModel.tasks.total} tasks done)`,
      ``,
      `## Agents (${worldModel.agents.total} active)`,
      ...worldModel.agents.active.map((a: any) => `- **${a.id}** [${a.role}]: ${a.description}`),
      ``,
      worldModel.agents.killed.length > 0 ? `### Killed: ${worldModel.agents.killed.join(", ")}` : "",
      ``,
      `## Capabilities`,
      `Total: ${worldModel.capabilities.total} across ${worldModel.capabilities.domains.length} domains`,
      ...worldModel.capabilities.domains.map((d: any) => `- ${d.domain}: ${d.count}`),
    ].filter(Boolean).join("\n"),
    category: "entity",
    tags: ["system", "agents", "overview"],
    cross_refs: [],
    source_files: ["TASKS.md", "agents/registry/agents.json"],
    quality_score: 90,
  });

  // P0 blockers page (if any)
  if (worldModel.tasks.p0_blockers.length > 0) {
    pages.push({
      slug: "current-p0-blockers",
      title: "Current P0 Blockers",
      content: [
        `# Current P0 Blockers`,
        ``,
        `**Count:** ${worldModel.tasks.p0_blockers.length} | **Generated:** ${worldModel.generated_at}`,
        ``,
        ...worldModel.tasks.p0_blockers.map((t: any) => `- **${t.id}** [${t.section}]: ${t.text.slice(0, 100)}`),
      ].join("\n"),
      category: "synthesis",
      tags: ["blockers", "p0", "priority"],
      cross_refs: ["egos-system-overview"],
      source_files: ["TASKS.md"],
      quality_score: 85,
    });
  }

  // Signals page
  if (worldModel.signals.length > 0) {
    pages.push({
      slug: "active-signals",
      title: "Active Signals & Alerts",
      content: [
        `# Active Signals & Alerts`,
        ``,
        `**Generated:** ${worldModel.generated_at}`,
        ``,
        ...worldModel.signals.map((s: any) => `- [${s.severity}] **${s.source}** (${s.date}): ${s.headline}`),
      ].join("\n"),
      category: "synthesis",
      tags: ["signals", "alerts", "monitoring"],
      cross_refs: ["egos-system-overview"],
      source_files: ["docs/jobs/", "docs/gem-hunter/signals.json"],
      quality_score: 80,
    });
  }

  console.log(`[wiki-compiler] Generated ${pages.length} world-model pages`);

  if (DRY_RUN) {
    for (const p of pages) {
      console.log(`  ${p.slug} [${p.category}] q=${p.quality_score} tags=[${p.tags.join(",")}]`);
    }
    return;
  }

  // Upsert
  for (const page of pages) {
    await supabaseQuery("egos_wiki_pages", "POST", {
      slug: page.slug,
      title: page.title,
      content: page.content,
      category: page.category,
      tags: page.tags,
      cross_refs: page.cross_refs,
      source_files: page.source_files,
      compiled_by: "wiki-compiler:world-model",
      quality_score: page.quality_score,
      updated_at: new Date().toISOString(),
    }, "on_conflict=slug");
  }

  console.log(`[wiki-compiler] Upserted ${pages.length} world-model pages`);
}

// ── Main ──────────────────────────────────────────────────────────────

async function main(): Promise<void> {
  console.log(`[wiki-compiler] Mode: ${MODE} | Dry: ${DRY_RUN}`);
  console.log(`[wiki-compiler] Supabase: ${SUPABASE_URL ? "configured" : "NOT SET"}`);

  switch (MODE) {
    case "compile":
      await compile();
      break;
    case "lint":
      await lint();
      break;
    case "index":
      await generateIndex();
      break;
    case "world":
      await compileWorldModel();
      break;
  }
}

main().catch((err) => {
  console.error("[wiki-compiler] Fatal:", err);
  process.exit(1);
});
