#!/usr/bin/env bun
// 📝 Article Writer Agent — TL-002
//
// Reads a git commit, calls qwen-plus to generate a transparent article draft,
// runs Guard Brasil PII check, and inserts into timeline_drafts (Supabase).
//
// Usage:
//   bun run agents/agents/article-writer.ts --commit ae7b9ad
//   bun run agents/agents/article-writer.ts --commit ae7b9ad --topic "Hermes decommission"
//   bun run agents/agents/article-writer.ts --dry-run --commit ae7b9ad
//   bun run agents/agents/article-writer.ts --dry-run --commit HEAD

import { execSync } from "child_process";
import { readFileSync, existsSync } from "fs";

// ── CLI Args ───────────────────────────────────────────────────────────────

const DRY_RUN = process.argv.includes("--dry-run");
const COMMIT_ARG = (() => {
  const idx = process.argv.indexOf("--commit");
  return idx >= 0 ? (process.argv[idx + 1] ?? "HEAD") : "HEAD";
})();
const TOPIC_ARG = (() => {
  const idx = process.argv.indexOf("--topic");
  return idx >= 0 ? process.argv[idx + 1] : undefined;
})();

// ── Config ─────────────────────────────────────────────────────────────────

const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
const DASHSCOPE_API_KEY = process.env.ALIBABA_DASHSCOPE_API_KEY ?? "";
const DASHSCOPE_BASE_URL =
  process.env.ALIBABA_DASHSCOPE_BASE_URL ??
  "https://dashscope-intl.aliyuncs.com/compatible-mode/v1";
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY ?? "";
const GUARD_BRASIL_URL = "https://guard.egos.ia.br/v1/inspect";
const GUARD_BRASIL_API_KEY = process.env.GUARD_BRASIL_API_KEY ?? "";

// Rough token cost estimates (USD per 1k tokens)
const COST_PER_1K_INPUT_QWEN = 0.0004;
const COST_PER_1K_OUTPUT_QWEN = 0.0012;

// ── Types ──────────────────────────────────────────────────────────────────

interface ArticleContent {
  title: string;
  summary: string; // ≤ 280 chars for X snippet
  body_md: string;
  tags: string[];
  word_count: number;
}

interface LLMResult {
  content: ArticleContent;
  provider: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
}

interface GuardInspectResult {
  hasPii: boolean;
  detections: Array<{ type: string; value: string; start: number; end: number }>;
  sanitized?: string;
}

interface CommitInfo {
  hash: string;
  shortHash: string;
  subject: string;
  author: string;
  date: string;
  stat: string;
  diff: string;
  files: string[];
}

// ── Git helpers ────────────────────────────────────────────────────────────

function resolveCommit(ref: string): string {
  try {
    return execSync(`git -C /home/enio/egos rev-parse --short ${ref}`, {
      encoding: "utf8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();
  } catch {
    throw new Error(`Cannot resolve commit ref: ${ref}`);
  }
}

function getCommitInfo(commitHash: string): CommitInfo {
  const shortHash = resolveCommit(commitHash);

  const subject = execSync(
    `git -C /home/enio/egos log -1 --format="%s" ${shortHash}`,
    { encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }
  ).trim();

  const author = execSync(
    `git -C /home/enio/egos log -1 --format="%an" ${shortHash}`,
    { encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }
  ).trim();

  const date = execSync(
    `git -C /home/enio/egos log -1 --format="%ci" ${shortHash}`,
    { encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }
  ).trim();

  // stat: changed files summary
  const stat = execSync(
    `git -C /home/enio/egos show ${shortHash} --stat --no-color`,
    { encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }
  ).trim();

  // diff (max 4000 chars to avoid token explosion)
  let diff = "";
  try {
    diff = execSync(
      `git -C /home/enio/egos diff ${shortHash}~1 ${shortHash} --no-color`,
      { encoding: "utf8", stdio: ["pipe", "pipe", "pipe"], maxBuffer: 1024 * 1024 }
    ).trim();
    if (diff.length > 4000) diff = diff.slice(0, 4000) + "\n... [diff truncated]";
  } catch {
    diff = "[diff unavailable — initial commit or merge]";
  }

  // list of changed files
  const files = execSync(
    `git -C /home/enio/egos diff --name-only ${shortHash}~1 ${shortHash}`,
    { encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }
  )
    .trim()
    .split("\n")
    .filter(Boolean);

  return { hash: shortHash, shortHash, subject, author, date, stat, diff, files };
}

// ── Read related docs ──────────────────────────────────────────────────────

function readRelatedDocs(files: string[]): string {
  const docSnippets: string[] = [];

  // Read relevant files changed in commit (only docs/ts/sh, max 1500 chars each)
  const readableExtensions = [".md", ".ts", ".sh", ".json", ".yaml", ".yml"];
  const filesToRead = files
    .filter((f) => readableExtensions.some((ext) => f.endsWith(ext)))
    .slice(0, 5); // max 5 files for context

  for (const file of filesToRead) {
    const fullPath = `/home/enio/egos/${file}`;
    if (!existsSync(fullPath)) continue;
    try {
      const content = readFileSync(fullPath, "utf8").slice(0, 1500);
      docSnippets.push(`### ${file}\n\`\`\`\n${content}\n\`\`\``);
    } catch {
      // skip unreadable files
    }
  }

  // Always include X_POSTS_SSOT.md for tone reference (first 800 chars)
  const ssotPath = "/home/enio/egos/docs/X_POSTS_SSOT.md";
  if (existsSync(ssotPath)) {
    try {
      const toneRef = readFileSync(ssotPath, "utf8").slice(0, 800);
      docSnippets.push(`### X_POSTS_SSOT.md (tone reference)\n${toneRef}`);
    } catch {
      // skip
    }
  }

  return docSnippets.join("\n\n");
}

// ── Slug generator ─────────────────────────────────────────────────────────

function generateSlug(title: string, date: string): string {
  const datePrefix = date.slice(0, 10); // YYYY-MM-DD
  const slug = title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 60)
    .replace(/-$/, "");
  return `${datePrefix}-${slug}`;
}

// ── LLM: generate article ──────────────────────────────────────────────────

function buildPrompt(commit: CommitInfo, topic: string | undefined, relatedDocs: string): string {
  const topicLine = topic ? `\nFocal topic: "${topic}"` : "";
  return `You are writing a transparent technical article for the EGOS project blog at egos.ia.br/timeline.
The article is in Portuguese (Brazil) and follows the "transparência radical" principle: show everything being built and why.
Tone: direct, technical, human. No corporate jargon. Real commit hashes and file paths as sources.${topicLine}

## Commit info
Hash: ${commit.shortHash}
Subject: ${commit.subject}
Author: ${commit.author}
Date: ${commit.date}

## Changed files
${commit.files.join("\n")}

## Stat
${commit.stat.slice(0, 800)}

## Diff (excerpt)
\`\`\`diff
${commit.diff}
\`\`\`

## Related docs context
${relatedDocs.slice(0, 3000)}

---

Write a JSON object with this exact structure (no markdown fence, just raw JSON):
{
  "title": "<max 80 chars, Portuguese, direct>",
  "summary": "<max 280 chars, Portuguese, X.com snippet — starts with a verb, no hashtags>",
  "body_md": "<full article in Markdown, 600-1000 words, includes: what changed, why, commit ${commit.shortHash}, file paths, 1-2 code blocks max>",
  "tags": ["<tag1>", "<tag2>", "<tag3>"]
}

Rules:
- summary must be ≤ 280 chars (count them)
- body_md must cite the commit hash ${commit.shortHash} at least once
- body_md must NOT contain CPF, email addresses, phone numbers, or API keys
- Return ONLY the JSON, no preamble, no explanation`;
}

async function callLLM(prompt: string): Promise<LLMResult> {
  const messages = [{ role: "user" as const, content: prompt }];

  // Primary: DashScope qwen-plus
  if (DASHSCOPE_API_KEY) {
    try {
      const res = await fetch(`${DASHSCOPE_BASE_URL}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${DASHSCOPE_API_KEY}`,
        },
        body: JSON.stringify({
          model: "qwen-plus",
          messages,
          max_tokens: 1500,
          temperature: 0.6,
        }),
        signal: AbortSignal.timeout(30000),
      });

      if (res.ok) {
        const data = (await res.json()) as {
          choices?: Array<{ message?: { content?: string } }>;
          usage?: { prompt_tokens?: number; completion_tokens?: number };
        };
        const raw = data.choices?.[0]?.message?.content?.trim() ?? "";
        const inputTokens = data.usage?.prompt_tokens ?? Math.floor(prompt.length / 4);
        const outputTokens = data.usage?.completion_tokens ?? Math.floor(raw.length / 4);
        const costUsd =
          (inputTokens / 1000) * COST_PER_1K_INPUT_QWEN +
          (outputTokens / 1000) * COST_PER_1K_OUTPUT_QWEN;

        const content = parseArticleJSON(raw);
        if (content) {
          return { content, provider: "alibaba/qwen-plus", input_tokens: inputTokens, output_tokens: outputTokens, cost_usd: costUsd };
        }
      }
    } catch (err) {
      console.warn(`⚠️  DashScope error: ${err} — falling back to OpenRouter`);
    }
  }

  // Fallback: OpenRouter free model
  if (OPENROUTER_API_KEY) {
    try {
      const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${OPENROUTER_API_KEY}`,
        },
        body: JSON.stringify({
          model: "google/gemma-4-26b-a4b-it:free",
          messages,
          max_tokens: 1500,
          temperature: 0.6,
        }),
        signal: AbortSignal.timeout(30000),
      });

      if (res.ok) {
        const data = (await res.json()) as {
          choices?: Array<{ message?: { content?: string } }>;
          usage?: { prompt_tokens?: number; completion_tokens?: number };
        };
        const raw = data.choices?.[0]?.message?.content?.trim() ?? "";
        const inputTokens = data.usage?.prompt_tokens ?? Math.floor(prompt.length / 4);
        const outputTokens = data.usage?.completion_tokens ?? Math.floor(raw.length / 4);

        const content = parseArticleJSON(raw);
        if (content) {
          return { content, provider: "openrouter/gemma-4-26b-free", input_tokens: inputTokens, output_tokens: outputTokens, cost_usd: 0 };
        }
      }
    } catch (err) {
      console.warn(`⚠️  OpenRouter error: ${err}`);
    }
  }

  throw new Error("No LLM available (ALIBABA_DASHSCOPE_API_KEY or OPENROUTER_API_KEY required)");
}

function parseArticleJSON(raw: string): ArticleContent | null {
  // Strip markdown code fence if present
  let clean = raw.replace(/^```(?:json)?\s*/m, "").replace(/\s*```\s*$/m, "").trim();

  // Find first { and last } to extract JSON
  const start = clean.indexOf("{");
  const end = clean.lastIndexOf("}");
  if (start < 0 || end < 0) return null;
  clean = clean.slice(start, end + 1);

  try {
    const obj = JSON.parse(clean) as Partial<ArticleContent>;
    if (!obj.title || !obj.summary || !obj.body_md) return null;

    return {
      title: String(obj.title).slice(0, 80),
      summary: String(obj.summary).slice(0, 280),
      body_md: String(obj.body_md),
      tags: Array.isArray(obj.tags) ? obj.tags.map(String).slice(0, 10) : [],
      word_count: String(obj.body_md).split(/\s+/).length,
    };
  } catch {
    return null;
  }
}

// ── Guard Brasil PII check ─────────────────────────────────────────────────

async function checkAndSanitizePII(text: string): Promise<{ clean: string; passed: boolean }> {
  // Headers for Guard Brasil
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (GUARD_BRASIL_API_KEY) {
    headers["X-API-Key"] = GUARD_BRASIL_API_KEY;
  }

  try {
    const res = await fetch(GUARD_BRASIL_URL, {
      method: "POST",
      headers,
      body: JSON.stringify({ text }),
      signal: AbortSignal.timeout(10000),
    });

    if (!res.ok) {
      console.warn(`⚠️  Guard Brasil returned ${res.status} — skipping PII check`);
      return { clean: text, passed: false };
    }

    const data = (await res.json()) as GuardInspectResult;

    if (!data.hasPii) {
      return { clean: text, passed: true };
    }

    // Strip detected PII
    let sanitized = text;
    // Sort detections by position descending to avoid offset shifts
    const sorted = [...data.detections].sort((a, b) => b.start - a.start);
    for (const det of sorted) {
      const mask = `[${det.type}]`;
      sanitized = sanitized.slice(0, det.start) + mask + sanitized.slice(det.end);
    }

    console.log(`🛡️  PII detected (${data.detections.length} items) — sanitized`);

    // Re-check after sanitization
    const reRes = await fetch(GUARD_BRASIL_URL, {
      method: "POST",
      headers,
      body: JSON.stringify({ text: sanitized }),
      signal: AbortSignal.timeout(10000),
    });

    if (reRes.ok) {
      const reData = (await reRes.json()) as GuardInspectResult;
      return { clean: sanitized, passed: !reData.hasPii };
    }

    return { clean: sanitized, passed: false };
  } catch (err) {
    console.warn(`⚠️  Guard Brasil unreachable: ${err} — continuing without PII check`);
    return { clean: text, passed: false };
  }
}

// ── Supabase insert ────────────────────────────────────────────────────────

async function insertDraft(
  slug: string,
  title: string,
  summary: string,
  body_md: string,
  source_commits: string[],
  source_files: string[],
  tags: string[],
  llm_provider: string,
  llm_cost_usd: number,
  pii_check_passed: boolean
): Promise<string> {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set");
  }

  const res = await fetch(`${SUPABASE_URL}/rest/v1/timeline_drafts`, {
    method: "POST",
    headers: {
      apikey: SUPABASE_SERVICE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
      "Content-Type": "application/json",
      Prefer: "return=representation",
    },
    body: JSON.stringify({
      slug,
      title,
      summary,
      body_md,
      source_commits,
      source_files: source_files.length > 0 ? source_files : null,
      tags: tags.length > 0 ? tags : null,
      status: "pending",
      llm_provider,
      llm_cost_usd,
      pii_check_passed,
    }),
    signal: AbortSignal.timeout(15000),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Supabase insert failed (${res.status}): ${err}`);
  }

  const rows = (await res.json()) as Array<{ id: string }>;
  return rows[0]?.id ?? "unknown";
}

// ── Main ───────────────────────────────────────────────────────────────────

async function main() {
  console.log("📝 Article Writer Agent — TL-002");
  console.log(`Mode: ${DRY_RUN ? "DRY-RUN (no DB insert)" : "LIVE"}`);
  console.log(`Commit: ${COMMIT_ARG}${TOPIC_ARG ? ` | Topic: "${TOPIC_ARG}"` : ""}`);

  // 1. Get commit info
  console.log("\n📦 Reading commit...");
  let commit: CommitInfo;
  try {
    commit = getCommitInfo(COMMIT_ARG);
    console.log(`  ✓ ${commit.shortHash}: ${commit.subject}`);
    console.log(`  📁 ${commit.files.length} files changed`);
  } catch (err) {
    console.error(`❌ Failed to read commit: ${err}`);
    process.exit(1);
  }

  // 2. Read related docs
  console.log("\n📚 Reading related docs...");
  const relatedDocs = readRelatedDocs(commit.files);
  console.log(`  ✓ ${relatedDocs.length} chars of context`);

  // 3. Generate article via LLM
  console.log("\n🤖 Generating article via LLM...");
  const prompt = buildPrompt(commit, TOPIC_ARG, relatedDocs);
  let llmResult: LLMResult;
  try {
    llmResult = await callLLM(prompt);
    console.log(`  ✓ Provider: ${llmResult.provider}`);
    console.log(`  ✓ Tokens: ${llmResult.input_tokens} in / ${llmResult.output_tokens} out`);
    console.log(`  ✓ Cost: $${llmResult.cost_usd.toFixed(5)}`);
    console.log(`  ✓ Title: ${llmResult.content.title}`);
    console.log(`  ✓ Summary (${llmResult.content.summary.length} chars): ${llmResult.content.summary.slice(0, 100)}...`);
    console.log(`  ✓ Word count: ~${llmResult.content.word_count}`);
  } catch (err) {
    console.error(`❌ LLM generation failed: ${err}`);
    process.exit(1);
  }

  // 4. Guard Brasil PII check
  console.log("\n🛡️  Running Guard Brasil PII check...");
  const fullText = `${llmResult.content.title}\n${llmResult.content.summary}\n${llmResult.content.body_md}`;
  const { clean: cleanedText, passed: piiPassed } = await checkAndSanitizePII(fullText);
  console.log(`  ${piiPassed ? "✅" : "⚠️ "} PII check ${piiPassed ? "passed" : "could not verify"}`);

  // Reconstruct body_md from cleaned text if sanitized
  let finalBodyMd = llmResult.content.body_md;
  if (cleanedText !== fullText) {
    // Extract body portion from cleaned text (after title + summary + 2 newlines)
    const titleSummaryLen = llmResult.content.title.length + llmResult.content.summary.length + 2;
    finalBodyMd = cleanedText.slice(titleSummaryLen);
  }

  // 5. Generate slug
  const slug = generateSlug(llmResult.content.title, commit.date);
  console.log(`\n🔗 Slug: ${slug}`);

  // 6. Print draft
  console.log("\n" + "=".repeat(60));
  console.log("📄 DRAFT PREVIEW");
  console.log("=".repeat(60));
  console.log(`Title:   ${llmResult.content.title}`);
  console.log(`Slug:    ${slug}`);
  console.log(`Summary: ${llmResult.content.summary}`);
  console.log(`Tags:    ${llmResult.content.tags.join(", ")}`);
  console.log(`Words:   ~${llmResult.content.word_count}`);
  console.log(`PII:     ${piiPassed ? "✅ passed" : "⚠️  unverified"}`);
  console.log(`LLM:     ${llmResult.provider} ($${llmResult.cost_usd.toFixed(5)})`);
  console.log("\n--- BODY (first 500 chars) ---");
  console.log(finalBodyMd.slice(0, 500) + (finalBodyMd.length > 500 ? "\n..." : ""));
  console.log("=".repeat(60));

  if (DRY_RUN) {
    console.log("\n⚠️  DRY-RUN: skipping Supabase insert.");
    console.log("✅ Draft generated successfully.");
    return;
  }

  // 7. Insert into Supabase
  console.log("\n💾 Inserting into timeline_drafts...");
  try {
    const draftId = await insertDraft(
      slug,
      llmResult.content.title,
      llmResult.content.summary,
      finalBodyMd,
      [commit.shortHash],
      commit.files,
      llmResult.content.tags,
      llmResult.provider,
      llmResult.cost_usd,
      piiPassed
    );
    console.log(`✅ Draft inserted: ${draftId}`);
    console.log(`\nReview at: https://hq.egos.ia.br/timeline/pending`);
    console.log(`Draft ID: ${draftId}`);
    // Output draft ID on last line for capture by publish.sh
    process.stdout.write(`DRAFT_ID=${draftId}\n`);
  } catch (err) {
    console.error(`❌ Supabase insert failed: ${err}`);
    process.exit(1);
  }
}

main().catch((err) => {
  console.error("❌ Fatal error:", err);
  process.exit(1);
});

export {}; // make this a module — prevents global namespace collision with other scripts
