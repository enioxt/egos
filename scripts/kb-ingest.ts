#!/usr/bin/env bun
/**
 * KBS-006 — KB File Ingestor
 *
 * Ingests PDF, DOCX, or Markdown files into the EGOS Knowledge Base.
 * Extracts text, runs Guard Brasil PII scan, indexes via wiki-compiler.
 *
 * Usage:
 *   bun scripts/kb-ingest.ts --file path/to/doc.pdf [--category "metalurgia"] [--dry]
 *   bun scripts/kb-ingest.ts --dir path/to/folder/ [--ext pdf,docx] [--dry]
 *   bun scripts/kb-ingest.ts --notion <page-url> [--dry]
 *
 * Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GUARD_BRASIL_API_KEY (optional)
 */

export {};

import { readFileSync, existsSync, readdirSync, statSync, writeFileSync } from 'fs';
import { join, basename, extname } from 'path';

// ── Config ──────────────────────────────────────────────────────────────────
const SUPABASE_URL = process.env.SUPABASE_URL ?? '';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? '';
const GUARD_API = process.env.GUARD_BRASIL_URL ?? 'https://guard.egos.ia.br';
const GUARD_KEY = process.env.GUARD_BRASIL_API_KEY ?? '';

const ARGS = process.argv.slice(2);
const isDry = ARGS.includes('--dry');
const fileArg = ARGS.find((_, i) => ARGS[i - 1] === '--file');
const dirArg = ARGS.find((_, i) => ARGS[i - 1] === '--dir');
const notionArg = ARGS.find((_, i) => ARGS[i - 1] === '--notion');
const categoryArg = ARGS.find((_, i) => ARGS[i - 1] === '--category') ?? 'geral';
const extArg = ARGS.find((_, i) => ARGS[i - 1] === '--ext') ?? 'pdf,docx,md';

// ── Text Extractors ─────────────────────────────────────────────────────────

async function extractPdf(filePath: string): Promise<string> {
  const { extractText } = await import('unpdf');
  const buf = readFileSync(filePath);
  const uint8 = new Uint8Array(buf.buffer, buf.byteOffset, buf.byteLength);
  const result = await extractText(uint8, { mergePages: true });
  return result.text ?? '';
}

async function extractDocx(filePath: string): Promise<string> {
  const mammoth = await import('mammoth');
  const result = await mammoth.extractRawText({ path: filePath });
  return result.value ?? '';
}

function extractMarkdown(filePath: string): string {
  return readFileSync(filePath, 'utf-8');
}

async function extractText(filePath: string): Promise<string> {
  const ext = extname(filePath).toLowerCase();
  if (ext === '.pdf') return extractPdf(filePath);
  if (ext === '.docx' || ext === '.doc') return extractDocx(filePath);
  if (ext === '.md' || ext === '.txt') return extractMarkdown(filePath);
  throw new Error(`Unsupported file type: ${ext}`);
}

// ── Guard Brasil PII Scan ───────────────────────────────────────────────────

type GuardResult = {
  has_pii: boolean;
  detections: Array<{ type: string; value: string; start: number; end: number }>;
  redacted?: string;
};

async function scanPii(text: string): Promise<GuardResult> {
  if (!GUARD_KEY) {
    console.warn('[kb-ingest] No GUARD_BRASIL_API_KEY — skipping PII scan');
    return { has_pii: false, detections: [] };
  }
  try {
    const res = await fetch(`${GUARD_API}/v1/inspect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GUARD_KEY}`,
      },
      body: JSON.stringify({ text: text.substring(0, 5000) }), // Guard has size limits
    });
    if (!res.ok) {
      console.warn(`[kb-ingest] Guard scan failed: HTTP ${res.status}`);
      return { has_pii: false, detections: [] };
    }
    return res.json() as Promise<GuardResult>;
  } catch (e) {
    console.warn(`[kb-ingest] Guard scan error: ${(e as Error).message}`);
    return { has_pii: false, detections: [] };
  }
}

// ── Supabase Upsert ─────────────────────────────────────────────────────────

function toSlug(title: string): string {
  return title
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .substring(0, 80);
}

function scoreQuality(text: string): number {
  let score = 50;
  if (text.length > 500) score += 10;
  if (text.length > 2000) score += 10;
  if (text.length > 5000) score += 10;
  if (/\d{2}\/\d{2}\/\d{4}|\d{4}-\d{2}-\d{2}/.test(text)) score += 5; // has dates
  if (/R\$\s?\d|[0-9]+,\d{2}/.test(text)) score += 5; // has monetary values (useful for metalurgy)
  return Math.min(score, 100);
}

async function upsertPage(doc: {
  title: string;
  slug: string;
  content: string;
  category: string;
  source_file: string;
  has_pii: boolean;
  pii_types: string[];
}): Promise<void> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/knowledge_base`, {
    method: 'POST',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'resolution=merge-duplicates',
    },
    body: JSON.stringify({
      slug: doc.slug,
      title: doc.title,
      content: doc.content,
      category: doc.category,
      tags: doc.pii_types.length > 0 ? [...doc.pii_types, 'file-ingested'] : ['file-ingested'],
      quality_score: scoreQuality(doc.content),
      source_files: [doc.source_file],
      has_pii_warning: doc.has_pii,
      updated_at: new Date().toISOString(),
    }),
  });
  if (!res.ok) throw new Error(`Supabase upsert failed: HTTP ${res.status} — ${await res.text()}`);
}

// ── Main Ingest ─────────────────────────────────────────────────────────────

async function ingestFile(filePath: string, category: string): Promise<void> {
  const fileName = basename(filePath);
  const title = basename(filePath, extname(filePath)).replace(/[-_]/g, ' ');
  const slug = toSlug(title);

  console.log(`[kb-ingest] Processing: ${fileName}`);

  // Extract text
  let text: string;
  try {
    text = await extractText(filePath);
  } catch (e) {
    console.error(`  ❌ Extract failed: ${(e as Error).message}`);
    return;
  }

  if (text.trim().length < 50) {
    console.warn(`  ⚠️  Very short content (${text.length} chars) — skipping`);
    return;
  }

  console.log(`  📄 Extracted ${text.length.toLocaleString()} chars`);

  // PII scan
  const guard = await scanPii(text);
  if (guard.has_pii) {
    const types = [...new Set(guard.detections.map((d) => d.type))];
    console.warn(`  ⚠️  PII detected: ${types.join(', ')} (${guard.detections.length} occurrences)`);
    // Use redacted version if available
    if (guard.redacted) {
      text = guard.redacted;
      console.log(`  🔒 Using Guard Brasil redacted version`);
    }
  }

  if (isDry) {
    console.log(`  [DRY] Would upsert: slug="${slug}", category="${category}", chars=${text.length}`);
    return;
  }

  // Upsert to Supabase
  await upsertPage({
    title,
    slug,
    content: text,
    category,
    source_file: filePath,
    has_pii: guard.has_pii,
    pii_types: guard.has_pii ? [...new Set(guard.detections.map((d) => d.type))] : [],
  });

  console.log(`  ✅ Indexed: ${slug} [${category}]`);
}

async function ingestDir(dirPath: string, category: string, extensions: string[]): Promise<void> {
  const files = readdirSync(dirPath).filter((f) => {
    const s = statSync(join(dirPath, f));
    return s.isFile() && extensions.includes(extname(f).toLowerCase().replace('.', ''));
  });

  console.log(`[kb-ingest] Found ${files.length} files in ${dirPath}`);
  let ok = 0;
  let fail = 0;

  for (const file of files) {
    try {
      await ingestFile(join(dirPath, file), category);
      ok++;
    } catch (e) {
      console.error(`  ❌ ${file}: ${(e as Error).message}`);
      fail++;
    }
  }

  console.log(`\n[kb-ingest] Done — ${ok} indexed, ${fail} failed`);
}

// ── Entry Point ─────────────────────────────────────────────────────────────

if (!fileArg && !dirArg && !notionArg) {
  console.error('Usage:');
  console.error('  bun scripts/kb-ingest.ts --file <path> [--category <cat>] [--dry]');
  console.error('  bun scripts/kb-ingest.ts --dir <path> [--ext pdf,docx,md] [--category <cat>] [--dry]');
  process.exit(1);
}

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error('[kb-ingest] Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY');
  process.exit(1);
}

if (fileArg) {
  if (!existsSync(fileArg)) {
    console.error(`File not found: ${fileArg}`);
    process.exit(1);
  }
  await ingestFile(fileArg, categoryArg);
} else if (dirArg) {
  if (!existsSync(dirArg)) {
    console.error(`Directory not found: ${dirArg}`);
    process.exit(1);
  }
  const exts = extArg.split(',').map((e) => e.trim());
  await ingestDir(dirArg, categoryArg, exts);
}
