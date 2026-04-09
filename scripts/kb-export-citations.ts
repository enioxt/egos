#!/usr/bin/env bun
/**
 * KBS-018 — Citation Export
 *
 * Exports Knowledge Base pages as a Markdown document with numbered citations.
 * Each KB page referenced in the content gets a [N] citation and a bibliography
 * section at the end. Useful for generating formal reports and proposals.
 *
 * Usage:
 *   bun scripts/kb-export-citations.ts --query "LGPD metalurgia" [--format md|pdf] [--tenant egos]
 *   bun scripts/kb-export-citations.ts --slugs "abnt-nbr-6118,lgpd-dados-sensiveis" [--out report.md]
 *   bun scripts/kb-export-citations.ts --category "norma" --tenant forja --out normas-forja.md
 *
 * Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
 */

export {};

import { writeFileSync } from 'fs';
import { join } from 'path';

const SUPABASE_URL = process.env.SUPABASE_URL ?? '';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? '';

const ARGS = process.argv.slice(2);
const queryArg = ARGS.find((_, i) => ARGS[i - 1] === '--query');
const slugsArg = ARGS.find((_, i) => ARGS[i - 1] === '--slugs');
const categoryArg = ARGS.find((_, i) => ARGS[i - 1] === '--category');
const tenantArg = ARGS.find((_, i) => ARGS[i - 1] === '--tenant') ?? 'egos';
const outArg = ARGS.find((_, i) => ARGS[i - 1] === '--out');
const formatArg = (ARGS.find((_, i) => ARGS[i - 1] === '--format') ?? 'md') as 'md' | 'pdf';
const limitArg = parseInt(ARGS.find((_, i) => ARGS[i - 1] === '--limit') ?? '20', 10);

// ── Supabase Query ───────────────────────────────────────────────────────────
type WikiPage = {
  slug: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  quality_score: number;
  source_files: string[];
  updated_at: string;
};

async function fetchPages(): Promise<WikiPage[]> {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    throw new Error('Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY');
  }

  let url = `${SUPABASE_URL}/rest/v1/egos_wiki_pages?tenant_id=eq.${tenantArg}&order=quality_score.desc&limit=${limitArg}&select=slug,title,content,category,tags,quality_score,source_files,updated_at`;

  if (categoryArg) {
    url += `&category=eq.${encodeURIComponent(categoryArg)}`;
  }

  if (slugsArg) {
    const slugList = slugsArg.split(',').map((s) => s.trim()).join(',');
    url = `${SUPABASE_URL}/rest/v1/egos_wiki_pages?slug=in.(${slugList})&tenant_id=eq.${tenantArg}&select=slug,title,content,category,tags,quality_score,source_files,updated_at`;
  }

  const res = await fetch(url, {
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
    },
  });
  if (!res.ok) throw new Error(`Supabase query failed: HTTP ${res.status} — ${await res.text()}`);
  return res.json() as Promise<WikiPage[]>;
}

// ── Citation Engine ───────────────────────────────────────────────────────────
type Citation = {
  index: number;
  slug: string;
  title: string;
  category: string;
  quality_score: number;
  source_files: string[];
  updated_at: string;
};

/**
 * Scans content for cross-references like [[page-slug]] or [page title](slug)
 * and builds a numbered citation list.
 */
function buildCitations(pages: WikiPage[]): Map<string, Citation> {
  const citations = new Map<string, Citation>();
  let idx = 1;

  for (const page of pages) {
    if (!citations.has(page.slug)) {
      citations.set(page.slug, {
        index: idx++,
        slug: page.slug,
        title: page.title,
        category: page.category,
        quality_score: page.quality_score,
        source_files: page.source_files ?? [],
        updated_at: page.updated_at,
      });
    }

    // Scan content for cross-references [[slug]]
    const xrefPattern = /\[\[([a-z0-9-]+)\]\]/g;
    let match;
    while ((match = xrefPattern.exec(page.content)) !== null) {
      const refSlug = match[1];
      if (!citations.has(refSlug)) {
        citations.set(refSlug, {
          index: idx++,
          slug: refSlug,
          title: refSlug.replace(/-/g, ' '),
          category: 'reference',
          quality_score: 0,
          source_files: [],
          updated_at: '',
        });
      }
    }
  }

  return citations;
}

/**
 * Replaces [[slug]] cross-refs with [Title][N] format.
 */
function injectCitations(content: string, citations: Map<string, Citation>): string {
  return content.replace(/\[\[([a-z0-9-]+)\]\]/g, (match, slug) => {
    const cite = citations.get(slug);
    if (!cite) return match;
    return `[${cite.title}][${cite.index}]`;
  });
}

// ── Markdown Generator ────────────────────────────────────────────────────────
function generateMarkdown(pages: WikiPage[], citations: Map<string, Citation>, title: string): string {
  const dateStr = new Date().toISOString().slice(0, 10);
  const lines: string[] = [
    `# ${title}`,
    '',
    `> **Gerado em:** ${dateStr} | **Tenant:** ${tenantArg} | **Documentos:** ${pages.length} | **Citações:** ${citations.size}`,
    `> *Exportado do EGOS Knowledge Base via kb-export-citations.ts*`,
    '',
    '---',
    '',
    '## Conteúdo',
    '',
  ];

  for (const page of pages) {
    const cite = citations.get(page.slug)!;
    lines.push(`## [${cite.index}] ${page.title}`);
    lines.push('');
    lines.push(`**Categoria:** ${page.category} | **Qualidade:** ${page.quality_score}/100 | **Tags:** ${(page.tags ?? []).join(', ')}`);
    if (page.source_files?.length) {
      lines.push(`**Fontes:** ${page.source_files.join(', ')}`);
    }
    lines.push('');
    // Inject citations into content
    lines.push(injectCitations(page.content, citations));
    lines.push('');
    lines.push('---');
    lines.push('');
  }

  // Bibliography
  lines.push('## Referências Bibliográficas');
  lines.push('');
  const sortedCites = [...citations.values()].sort((a, b) => a.index - b.index);
  for (const cite of sortedCites) {
    const date = cite.updated_at ? ` (atualizado: ${cite.updated_at.slice(0, 10)})` : '';
    const sources = cite.source_files.length > 0 ? ` — Fontes: ${cite.source_files.join(', ')}` : '';
    lines.push(`[${cite.index}] **${cite.title}** [${cite.category}]${sources}${date}`);
  }
  lines.push('');
  lines.push(`---`);
  lines.push(`*Relatório gerado por EGOS Knowledge Base as a Service — ${dateStr}*`);

  return lines.join('\n');
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function run(): Promise<void> {
  if (!queryArg && !slugsArg && !categoryArg) {
    console.error('Usage: bun scripts/kb-export-citations.ts [--query <text>] [--slugs <s1,s2>] [--category <cat>] [--tenant <t>] [--out report.md]');
    process.exit(1);
  }

  console.log(`[kb-export-citations] Fetching pages (tenant=${tenantArg}, format=${formatArg})...`);
  const pages = await fetchPages();

  if (pages.length === 0) {
    console.log('[kb-export-citations] No pages found');
    return;
  }

  console.log(`[kb-export-citations] Found ${pages.length} pages`);

  const citations = buildCitations(pages);
  const title = queryArg ? `Relatório KB: ${queryArg}` : categoryArg ? `Relatório KB: Categoria ${categoryArg}` : 'Relatório Knowledge Base';
  const markdown = generateMarkdown(pages, citations, title);

  const outPath = outArg ?? `kb-export-${Date.now()}.md`;
  const fullPath = outArg?.startsWith('/') ? outArg : join(process.cwd(), outPath);

  writeFileSync(fullPath, markdown, 'utf-8');
  console.log(`[kb-export-citations] ✅ Exported ${pages.length} pages, ${citations.size} citations → ${fullPath}`);

  if (formatArg === 'pdf') {
    console.log('[kb-export-citations] ℹ️  PDF generation requires pandoc: pandoc ' + fullPath + ' -o ' + fullPath.replace('.md', '.pdf'));
    console.log('[kb-export-citations] Install: apt-get install pandoc texlive-xetex');
  }
}

await run();
