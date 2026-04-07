#!/usr/bin/env bun
/**
 * ssot-router.ts — Pre-commit SSOT Gate
 *
 * Checks if a newly created .md file belongs to an existing SSOT domain.
 * Uses LLM (Gemini Flash → Alibaba Qwen → local keyword matching) with fallback.
 *
 * Triggered by .husky/pre-commit when new .md files are staged.
 *
 * Usage (called by hook, not manually):
 *   bun scripts/ssot-router.ts --file docs/foo/BAR.md
 *   bun scripts/ssot-router.ts --file docs/foo/BAR.md --warn-only
 *
 * Exit codes:
 *   0 — OK (file is fine, or skip)
 *   1 — BLOCK (file should go to an existing SSOT)
 *
 * Override: include "SSOT-NEW: <reason>" in commit message
 *   git commit -m "feat: add new X report\n\nSSOT-NEW: creates new standalone doc, not GTM"
 *
 * Part of: EGOS Doc-Drift Shield + SSOT-First Rule (CLAUDE.md §26)
 */

import { existsSync, readFileSync } from "fs";
import { basename, extname } from "path";
import { parse as parseYaml } from "yaml";

// ─── Types ────────────────────────────────────────────────────────────────────

interface SsotDomain {
  id: string;
  description: string;
  ssot: string;
  ssot_social?: string;
  keywords: string[];
  forbidden_paths: string[];
  note?: string;
}

interface SsotMap {
  version: string;
  domains: SsotDomain[];
  always_ok: string[];
}

interface RouterResult {
  action: "ok" | "block" | "warn";
  domain?: string;
  ssot?: string;
  reason: string;
  method: "keyword" | "llm-gemini" | "llm-alibaba" | "skip";
}

// ─── Load SSOT map ─────────────────────────────────────────────────────────────

function loadSsotMap(): SsotMap | null {
  const paths = [
    `${process.cwd()}/.ssot-map.yaml`,
    `/home/enio/egos/.ssot-map.yaml`,
  ];
  for (const p of paths) {
    if (existsSync(p)) {
      return parseYaml(readFileSync(p, "utf-8")) as SsotMap;
    }
  }
  return null;
}

// ─── Skip check ───────────────────────────────────────────────────────────────

function shouldSkip(filePath: string, ssotMap: SsotMap): boolean {
  const ext = extname(filePath);
  const name = basename(filePath);

  // Not a markdown file
  if (ext !== ".md") return true;

  // Check always_ok patterns
  for (const pattern of ssotMap.always_ok) {
    if (matchGlob(name, pattern)) return true;
  }

  // Core governance files are always OK
  const alwaysOkNames = ["AGENTS.md", "CLAUDE.md", "README.md", "TASKS.md", "HARVEST.md"];
  if (alwaysOkNames.includes(name)) return true;

  // Files in docs/_current_handoffs/ or docs/_archived_handoffs/ are ok
  if (filePath.includes("_handoffs/") || filePath.includes("_archived_")) return true;

  return false;
}

function matchGlob(name: string, pattern: string): boolean {
  const escaped = pattern.replace(/\./g, "\\.").replace(/\*/g, ".*");
  return new RegExp(`^${escaped}$`).test(name);
}

// ─── Keyword-based routing ────────────────────────────────────────────────────

function keywordRoute(filePath: string, content: string, ssotMap: SsotMap): RouterResult | null {
  const combined = (filePath + " " + content.slice(0, 2000)).toLowerCase();

  let bestMatch: { domain: SsotDomain; score: number } | null = null;

  for (const domain of ssotMap.domains) {
    let score = 0;

    // Check forbidden paths first
    for (const forbidden of domain.forbidden_paths) {
      if (matchGlob(basename(filePath), forbidden) || filePath.includes(forbidden.replace("*", ""))) {
        score += 10; // strong signal: path itself is forbidden
      }
    }

    // Count keyword matches
    for (const kw of domain.keywords) {
      if (combined.includes(kw.toLowerCase())) {
        score += 1;
      }
    }

    if (score > 0 && (!bestMatch || score > bestMatch.score)) {
      bestMatch = { domain, score };
    }
  }

  if (!bestMatch || bestMatch.score < 2) return null; // not confident enough

  const domain = bestMatch.domain;
  const ssot = domain.ssot_social && filePath.includes("social")
    ? domain.ssot_social
    : domain.ssot;

  return {
    action: "block",
    domain: domain.id,
    ssot,
    reason: `Content matches "${domain.id}" domain (score ${bestMatch.score}). Add to ${ssot} instead.`,
    method: "keyword",
  };
}

// ─── LLM routing via Gemini Flash ─────────────────────────────────────────────

async function llmRouteGemini(
  filePath: string,
  content: string,
  ssotMap: SsotMap
): Promise<RouterResult | null> {
  const apiKey = process.env.GOOGLE_AI_STUDIO_API_KEY
    || process.env.GEMINI_API_KEY
    || "AIzaSyBrM3iLF8TmXXgIoUVdDq06y_ka2qbHzMg"; // fallback to configured key

  const domainSummary = ssotMap.domains
    .map((d) => `- ${d.id}: ${d.description} → ${d.ssot}`)
    .join("\n");

  const prompt = `You are an SSOT routing gate. Given a new documentation file, decide if its content belongs to an existing SSOT domain.

SSOT domains:
${domainSummary}

New file path: ${filePath}
Content preview (first 500 chars):
${content.slice(0, 500)}

Respond with JSON only:
{"action": "ok"|"block", "domain": "<domain_id or null>", "ssot": "<ssot_path or null>", "reason": "<1 sentence>"}

Rules:
- "block" only if content clearly belongs to an existing SSOT domain
- "ok" if it's a new standalone document that doesn't fit any domain
- "ok" if unsure
`;

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);

    const resp = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: 0, maxOutputTokens: 200 },
        }),
        signal: controller.signal,
      }
    );
    clearTimeout(timeout);

    if (!resp.ok) return null;
    const data = await resp.json() as any;
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text ?? "";
    const jsonMatch = text.match(/\{[^}]+\}/s);
    if (!jsonMatch) return null;

    const parsed = JSON.parse(jsonMatch[0]) as {
      action: "ok" | "block";
      domain: string | null;
      ssot: string | null;
      reason: string;
    };

    return {
      action: parsed.action === "block" ? "block" : "ok",
      domain: parsed.domain ?? undefined,
      ssot: parsed.ssot ?? undefined,
      reason: parsed.reason,
      method: "llm-gemini",
    };
  } catch {
    return null; // timeout or error — fall through to next
  }
}

// ─── LLM routing via Alibaba DashScope ────────────────────────────────────────

async function llmRouteAlibaba(
  filePath: string,
  content: string,
  ssotMap: SsotMap
): Promise<RouterResult | null> {
  const apiKey = process.env.ALIBABA_DASHSCOPE_API_KEY;
  if (!apiKey) return null;

  const domainSummary = ssotMap.domains
    .map((d) => `- ${d.id}: ${d.description} → ${d.ssot}`)
    .join("\n");

  const prompt = `SSOT routing gate. File: ${filePath}\nDomains:\n${domainSummary}\nContent: ${content.slice(0, 400)}\nJSON: {"action":"ok"|"block","domain":null,"ssot":null,"reason":""}`;

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);

    const resp = await fetch("https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "qwen-turbo",
        messages: [{ role: "user", content: prompt }],
        max_tokens: 100,
        temperature: 0,
      }),
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (!resp.ok) return null;
    const data = await resp.json() as any;
    const text = data?.choices?.[0]?.message?.content ?? "";
    const jsonMatch = text.match(/\{[^}]+\}/s);
    if (!jsonMatch) return null;

    const parsed = JSON.parse(jsonMatch[0]);
    return {
      action: parsed.action === "block" ? "block" : "ok",
      domain: parsed.domain ?? undefined,
      ssot: parsed.ssot ?? undefined,
      reason: parsed.reason ?? "LLM routed",
      method: "llm-alibaba",
    };
  } catch {
    return null;
  }
}

// ─── Main ─────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const fileIdx = args.indexOf("--file");
const warnOnly = args.includes("--warn-only");
const filePath = fileIdx !== -1 ? args[fileIdx + 1] : undefined;

if (!filePath) {
  console.error("Usage: bun scripts/ssot-router.ts --file <path> [--warn-only]");
  process.exit(0); // non-blocking on missing args
}

const ssotMap = loadSsotMap();
if (!ssotMap) {
  // No SSOT map found — silent skip (non-blocking)
  process.exit(0);
}

if (shouldSkip(filePath, ssotMap)) {
  process.exit(0); // OK, skip
}

const content = existsSync(filePath) ? readFileSync(filePath, "utf-8") : "";

// Phase 1: fast keyword check
const keywordResult = keywordRoute(filePath, content, ssotMap);

let result: RouterResult;

if (keywordResult && keywordResult.action === "block") {
  // Confirm with LLM before blocking
  const geminiResult = await llmRouteGemini(filePath, content, ssotMap);
  if (geminiResult && geminiResult.action === "ok") {
    // LLM says OK — trust it over keywords
    result = { action: "ok", reason: "LLM overrode keyword match", method: "llm-gemini" };
  } else if (geminiResult && geminiResult.action === "block") {
    result = { ...geminiResult, method: "llm-gemini" };
  } else {
    // Gemini unavailable — try Alibaba
    const alibabaResult = await llmRouteAlibaba(filePath, content, ssotMap);
    if (alibabaResult && alibabaResult.action === "ok") {
      result = { action: "ok", reason: "Alibaba LLM overrode keyword match", method: "llm-alibaba" };
    } else if (alibabaResult && alibabaResult.action === "block") {
      result = { ...alibabaResult, method: "llm-alibaba" };
    } else {
      // All LLMs unavailable — fall back to keyword with warn-only
      result = { ...keywordResult, action: warnOnly ? "warn" : "block" };
    }
  }
} else {
  result = { action: "ok", reason: "No SSOT domain match", method: "keyword" };
}

// Output and exit
if (result.action === "ok") {
  process.exit(0);
} else if (result.action === "warn") {
  console.warn(`\n⚠️  [ssot-router] ${filePath}`);
  console.warn(`   ${result.reason}`);
  console.warn(`   SSOT: ${result.ssot}`);
  console.warn(`   To suppress: add "SSOT-NEW: <reason>" to your commit message\n`);
  process.exit(0); // warn but don't block
} else {
  // BLOCK
  console.error(`\n🚫 [ssot-router] SSOT violation — commit blocked`);
  console.error(`   File: ${filePath}`);
  console.error(`   Domain: ${result.domain} | Method: ${result.method}`);
  console.error(`   → Add content to: ${result.ssot}`);
  console.error(`   → Or override: include "SSOT-NEW: <reason>" in commit message`);
  console.error(`   Reason: ${result.reason}\n`);
  process.exit(1);
}
