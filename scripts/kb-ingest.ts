#!/usr/bin/env bun
/**
 * KBS-006 — KB File Ingestor
 *
 * Ingests PDF, DOCX, Markdown, JSON, or JSONL files into the EGOS Knowledge Base.
 * Extracts text, runs Guard Brasil PII scan, indexes via wiki-compiler.
 * JSON/JSONL: each object/record becomes a separate wiki page.
 *
 * Usage:
 *   bun scripts/kb-ingest.ts --file path/to/doc.pdf [--category "metalurgia"] [--dry]
 *   bun scripts/kb-ingest.ts --file path/to/data.json [--category "delegacia"] [--dry]
 *   bun scripts/kb-ingest.ts --file path/to/records.jsonl [--category "advocacia"] [--dry]
 *   bun scripts/kb-ingest.ts --dir path/to/folder/ [--ext pdf,docx,json,jsonl] [--dry]
 *   bun scripts/kb-ingest.ts --notion <page-url> [--dry]
 *
 * Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GUARD_BRASIL_API_KEY (optional)
 */

export {};

import { readFileSync, existsSync, readdirSync, statSync } from 'fs';
import { join, basename, extname } from 'path';

// ── Config ──────────────────────────────────────────────────────────────────
const SUPABASE_URL = process.env.SUPABASE_URL ?? '';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? '';
const GUARD_API = process.env.GUARD_BRASIL_URL ?? 'https://guard.egos.ia.br';
const GUARD_KEY = process.env.GUARD_BRASIL_API_KEY ?? '';
const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? process.env.TELEGRAM_BOT_TOKEN_AI_AGENTS ?? '';
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID ?? '171767219';

const ARGS = process.argv.slice(2);
const isDry = ARGS.includes('--dry');
const fileArg = ARGS.find((_, i) => ARGS[i - 1] === '--file');
const dirArg = ARGS.find((_, i) => ARGS[i - 1] === '--dir');
const notionArg = ARGS.find((_, i) => ARGS[i - 1] === '--notion');
const categoryArg = ARGS.find((_, i) => ARGS[i - 1] === '--category') ?? 'geral';
const tenantArg = ARGS.find((_, i) => ARGS[i - 1] === '--tenant') ?? 'egos';
const extArg = ARGS.find((_, i) => ARGS[i - 1] === '--ext') ?? 'pdf,docx,md,json,jsonl';

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
  // JSON/JSONL: flatten to text (multi-object case handled by ingestJsonFile)
  if (ext === '.json' || ext === '.jsonl') return extractJsonAsText(filePath);
  throw new Error(`Unsupported file type: ${ext}`);
}

// ── JSON/JSONL Extractors ────────────────────────────────────────────────────

type JsonRecord = Record<string, unknown>;

/** Detect a human-readable title from a JSON object's keys */
function detectTitle(obj: JsonRecord, fallback: string): string {
  const titleKeys = ['title', 'name', 'nome', 'subject', 'assunto', 'id', 'slug', 'label'];
  for (const key of titleKeys) {
    if (typeof obj[key] === 'string' && (obj[key] as string).length > 0) {
      return (obj[key] as string).substring(0, 120);
    }
  }
  for (const val of Object.values(obj)) {
    if (typeof val === 'string' && val.length > 2 && val.length < 120) return val;
  }
  return fallback;
}

/** Convert a JSON object to readable markdown-like text */
function objToText(obj: JsonRecord): string {
  const lines: string[] = [];
  for (const [key, val] of Object.entries(obj)) {
    if (val === null || val === undefined) continue;
    const valStr =
      typeof val === 'object' ? JSON.stringify(val, null, 2) : String(val);
    lines.push(`**${key}:** ${valStr}`);
  }
  return lines.join('\n');
}

/** Extract all records from a JSON or JSONL file */
function extractJsonRecords(filePath: string): Array<{ title: string; content: string }> {
  const raw = readFileSync(filePath, 'utf-8').trim();
  const ext = extname(filePath).toLowerCase();
  const fileBase = basename(filePath, ext);

  let objects: JsonRecord[] = [];

  if (ext === '.jsonl') {
    objects = raw
      .split('\n')
      .filter((l) => l.trim().length > 0)
      .map((line, i) => {
        try { return JSON.parse(line) as JsonRecord; }
        catch { console.warn(`  ⚠️  JSONL line ${i + 1} parse error — skipping`); return null; }
      })
      .filter((o): o is JsonRecord => o !== null);
  } else {
    let parsed: unknown;
    try { parsed = JSON.parse(raw); }
    catch (e) { throw new Error(`JSON parse error: ${(e as Error).message}`); }

    if (Array.isArray(parsed)) {
      objects = parsed.filter((o) => o !== null && typeof o === 'object') as JsonRecord[];
    } else if (typeof parsed === 'object' && parsed !== null) {
      objects = [parsed as JsonRecord];
    } else {
      objects = [{ value: parsed }];
    }
  }

  return objects.map((obj, i) => ({
    title: detectTitle(obj, `${fileBase} #${i + 1}`),
    content: objToText(obj),
  }));
}

/** For single-object JSON, return as text; multi-record: concatenate */
function extractJsonAsText(filePath: string): string {
  const records = extractJsonRecords(filePath);
  if (records.length === 1) return records[0].content;
  return records.map((r) => `## ${r.title}\n\n${r.content}`).join('\n\n---\n\n');
}

/** Ingest JSON/JSONL: one wiki page per record */
async function ingestJsonFile(filePath: string, category: string): Promise<void> {
  const fileName = basename(filePath);
  console.log(`[kb-ingest] Processing JSON: ${fileName}`);

  let records: Array<{ title: string; content: string }>;
  try {
    records = extractJsonRecords(filePath);
  } catch (e) {
    console.error(`  ❌ Parse failed: ${(e as Error).message}`);
    return;
  }

  console.log(`  📋 ${records.length} record(s) found`);
  let ok = 0;
  let skipped = 0;

  for (const record of records) {
    if (record.content.trim().length < 10) { skipped++; continue; }
    const slug = toSlug(record.title);
    const guard = await scanPii(record.content);
    let content = record.content;

    if (guard.has_pii) {
      const types = [...new Set(guard.detections.map((d) => d.type))];
      console.warn(`  ⚠️  PII in "${record.title}": ${types.join(', ')}`);
      if (guard.redacted) {
        content = guard.redacted;
      } else {
        console.error(`  ❌ Skipping "${record.title}" — PII found, no redaction available`);
        skipped++;
        continue;
      }
    }

    if (isDry) {
      console.log(`  [DRY] Would upsert: slug="${slug}", chars=${content.length}`);
      ok++;
      continue;
    }

    await upsertPage({
      title: record.title,
      slug,
      content,
      category,
      source_file: filePath,
      has_pii: guard.has_pii,
      pii_types: guard.has_pii ? [...new Set(guard.detections.map((d) => d.type))] : [],
      tenant_id: tenantArg,
    });
    console.log(`  ✅ ${slug}`);
    ok++;
  }

  console.log(`  Done — ${ok} indexed, ${skipped} skipped`);
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
  tenant_id: string;
}): Promise<void> {
  const piiTags = doc.has_pii ? ['pii-detected', ...doc.pii_types] : [];
  const res = await fetch(`${SUPABASE_URL}/rest/v1/egos_wiki_pages`, {
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
      tags: [...piiTags, 'file-ingested'],
      quality_score: scoreQuality(doc.content),
      source_files: [doc.source_file],
      compiled_by: 'kb-ingest',
      tenant_id: doc.tenant_id,
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
    // Telegram alert
    if (TELEGRAM_TOKEN && !isDry) {
      await fetch(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: TELEGRAM_CHAT_ID,
          text: `🔒 *KB Ingest — PII Detectada*\n\nArquivo: \`${fileName}\`\nTipos: ${types.join(', ')}\nOcorrências: ${guard.detections.length}\n${guard.redacted ? '✅ Versão redatada usada' : '⚠️ Sem redação disponível — conteúdo NÃO indexado'}\n\n#pii #lgpd #kb-ingest`,
          parse_mode: 'Markdown',
          disable_web_page_preview: true,
        }),
      }).catch(() => {});
    }
    // If no redaction available: skip indexing to protect PII
    if (!guard.redacted) {
      console.error(`  ❌ Skipping indexing — PII found and no redacted version available`);
      return;
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
    tenant_id: tenantArg,
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
      const fExt = extname(file).toLowerCase();
      if (fExt === '.json' || fExt === '.jsonl') {
        await ingestJsonFile(join(dirPath, file), category);
      } else {
        await ingestFile(join(dirPath, file), category);
      }
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
  const fileExt = extname(fileArg).toLowerCase();
  if (fileExt === '.json' || fileExt === '.jsonl') {
    await ingestJsonFile(fileArg, categoryArg);
  } else {
    await ingestFile(fileArg, categoryArg);
  }
} else if (dirArg) {
  if (!existsSync(dirArg)) {
    console.error(`Directory not found: ${dirArg}`);
    process.exit(1);
  }
  const exts = extArg.split(',').map((e) => e.trim());
  await ingestDir(dirArg, categoryArg, exts);
}
