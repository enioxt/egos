#!/usr/bin/env bun
/**
 * manifest-generator.ts — DRIFT-011
 *
 * Auto-generates or updates .egos-manifest.yaml from a repo's README.md
 * using LLM extraction (Gemini Flash → Alibaba Qwen → regex fallback).
 *
 * Extracts quantitative claims like:
 *   - "83.7M nodes" → claim: neo4j_nodes
 *   - "15 PII patterns" → claim: pii_patterns
 *   - "4ms latency" → claim: latency_ms
 *
 * Usage:
 *   bun scripts/manifest-generator.ts --repo /home/enio/852
 *   bun scripts/manifest-generator.ts --repo /home/enio/852 --dry
 *   bun scripts/manifest-generator.ts --all     # all KNOWN_REPOS
 *
 * Part of: docs/DOC_DRIFT_SHIELD.md (Layer 1 bootstrapping)
 */

import { existsSync, readFileSync, writeFileSync } from "fs";
import { join } from "path";
import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

// ─── Config ───────────────────────────────────────────────────────────────────

const KNOWN_REPOS = [
  "/home/enio/egos",
  "/home/enio/carteira-livre",
  "/home/enio/br-acc",
  "/home/enio/852",
  "/home/enio/forja",
  "/home/enio/egos-lab",
  "/home/enio/egos-inteligencia",
];

const GEMINI_KEY =
  process.env.GOOGLE_AI_STUDIO_API_KEY ||
  process.env.GEMINI_API_KEY ||
  "AIzaSyBrM3iLF8TmXXgIoUVdDq06y_ka2qbHzMg";

const DASHSCOPE_KEY = process.env.ALIBABA_DASHSCOPE_API_KEY ?? "";

// ─── Types ────────────────────────────────────────────────────────────────────

interface ExtractedClaim {
  id: string;
  description: string;
  value: string;
  unit: string;
  raw: string; // original text snippet
}

interface GeneratedManifest {
  repo: string;
  last_full_verification: string;
  claims: Array<{
    id: string;
    description: string;
    command: string;
    tolerance: string;
    last_value: string;
    last_verified_at: string;
    note?: string;
  }>;
}

// ─── Regex-based fallback extraction ─────────────────────────────────────────

const CLAIM_PATTERNS: Array<{
  regex: RegExp;
  id: (m: RegExpMatchArray) => string;
  description: (m: RegExpMatchArray) => string;
  value: (m: RegExpMatchArray) => string;
}> = [
  {
    regex: /(\d[\d.,]+)\s*[Mm]illion?\s*(?:nodes?|nós|entidades|entities)/i,
    id: () => "neo4j_nodes",
    description: () => "Neo4j graph node count",
    value: (m) => String(Math.round(parseFloat(m[1].replace(/,/g, ".")) * 1_000_000)),
  },
  {
    regex: /(\d[\d.,]+[Mm]?)\s*(?:nodes?|nós|entidades)\s/i,
    id: () => "neo4j_nodes",
    description: () => "Neo4j graph node count",
    value: (m) => {
      const raw = m[1].replace(/,/g, "").replace(/M/i, "000000");
      return String(parseInt(raw, 10));
    },
  },
  {
    regex: /(\d+)\s*(?:PII\s+)?padrões?|patterns?(?:\s+PII|\s+brasileiros?)?/i,
    id: () => "pii_patterns",
    description: () => "PII detection patterns",
    value: (m) => m[1],
  },
  {
    regex: /(\d+)ms\s*(?:de\s*)?(?:latência|latency)/i,
    id: () => "latency_ms",
    description: () => "API response latency in ms",
    value: (m) => m[1],
  },
  {
    regex: /F1\s*(?:score)?\s*[:=]?\s*([\d.]+)%/i,
    id: () => "f1_score_pct",
    description: () => "F1 score percentage",
    value: (m) => m[1],
  },
  {
    regex: /(\d+)\s*(?:Docker\s*)?containers?/i,
    id: () => "docker_containers",
    description: () => "Docker containers in production",
    value: (m) => m[1],
  },
  {
    regex: /(\d+)\s*(?:ETL\s+)?pipelines?/i,
    id: () => "etl_pipelines",
    description: () => "ETL pipeline count",
    value: (m) => m[1],
  },
  {
    regex: /(\d[\d.,]+)\s*(?:commits?)/i,
    id: () => "total_commits",
    description: () => "Total git commits",
    value: (m) => m[1].replace(/,/g, ""),
  },
  {
    regex: /(\d+)\s*(?:agents?|agentes?)\s/i,
    id: () => "registered_agents",
    description: () => "Registered agents",
    value: (m) => m[1],
  },
  {
    regex: /(\d+)\s*(?:tools?|ferramentas?)\b/i,
    id: () => "tool_count",
    description: () => "Tool count",
    value: (m) => m[1],
  },
  {
    regex: /(\d+)\s*territórios?|territories/i,
    id: () => "territories",
    description: () => "Monitored territories",
    value: (m) => m[1],
  },
];

function regexExtract(readmeContent: string): ExtractedClaim[] {
  const seen = new Set<string>();
  const claims: ExtractedClaim[] = [];

  for (const pattern of CLAIM_PATTERNS) {
    const match = readmeContent.match(pattern.regex);
    if (match) {
      const id = pattern.id(match);
      if (seen.has(id)) continue;
      seen.add(id);
      claims.push({
        id,
        description: pattern.description(match),
        value: pattern.value(match),
        unit: "",
        raw: match[0],
      });
    }
  }

  return claims;
}

// ─── LLM extraction via Gemini Flash ─────────────────────────────────────────

async function llmExtractGemini(
  repoName: string,
  readmeContent: string
): Promise<ExtractedClaim[]> {
  if (!GEMINI_KEY) return [];

  const prompt = `Extract ALL quantitative claims from this README. Return a JSON array only.

README (first 2000 chars):
${readmeContent.slice(0, 2000)}

For each claim, return:
{"id": "snake_case_unique_id", "description": "what it measures", "value": "numeric value as string", "unit": "unit (nodes, ms, %, count, etc.)", "raw": "original text snippet"}

Examples of claims to find:
- "83.7M nodes" → id: "neo4j_nodes", value: "83700000"
- "15 PII patterns" → id: "pii_patterns", value: "15"
- "4ms latency" → id: "latency_ms", value: "4"
- "F1 85.3%" → id: "f1_score_pct", value: "85.3"
- "1690 commits" → id: "total_commits", value: "1690"

Return [] if no quantitative claims found. JSON array only, no markdown.`;

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);

    const resp = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: 0, maxOutputTokens: 1000 },
        }),
        signal: controller.signal,
      }
    );
    clearTimeout(timeout);

    if (!resp.ok) return [];
    const data = await resp.json() as any;
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text ?? "";
    const jsonMatch = text.match(/\[[\s\S]*\]/);
    if (!jsonMatch) return [];

    return JSON.parse(jsonMatch[0]) as ExtractedClaim[];
  } catch {
    return [];
  }
}

// ─── LLM extraction via Alibaba ───────────────────────────────────────────────

async function llmExtractAlibaba(
  repoName: string,
  readmeContent: string
): Promise<ExtractedClaim[]> {
  if (!DASHSCOPE_KEY) return [];

  const prompt = `Extract quantitative claims from README. JSON array: [{"id":"snake_id","description":"...","value":"numeric_string","unit":"...","raw":"..."}]
README: ${readmeContent.slice(0, 1000)}`;

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);

    const resp = await fetch("https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${DASHSCOPE_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "qwen-turbo",
        messages: [{ role: "user", content: prompt }],
        max_tokens: 800,
        temperature: 0,
      }),
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (!resp.ok) return [];
    const data = await resp.json() as any;
    const text = data?.choices?.[0]?.message?.content ?? "";
    const jsonMatch = text.match(/\[[\s\S]*\]/);
    if (!jsonMatch) return [];

    return JSON.parse(jsonMatch[0]) as ExtractedClaim[];
  } catch {
    return [];
  }
}

// ─── Merge with existing manifest ─────────────────────────────────────────────

function mergeWithExisting(
  repoDir: string,
  claims: ExtractedClaim[]
): GeneratedManifest {
  const manifestPath = join(repoDir, ".egos-manifest.yaml");
  const repoName = repoDir.split("/").pop() ?? repoDir;
  const today = new Date().toISOString().slice(0, 10);

  let existing: GeneratedManifest | null = null;
  if (existsSync(manifestPath)) {
    try {
      existing = parseYaml(readFileSync(manifestPath, "utf-8")) as GeneratedManifest;
    } catch {}
  }

  const existingClaims = new Map(
    (existing?.claims ?? []).map((c) => [c.id, c])
  );

  // Only add NEW claims (don't overwrite manually curated ones)
  for (const claim of claims) {
    if (!existingClaims.has(claim.id)) {
      existingClaims.set(claim.id, {
        id: claim.id,
        description: claim.description,
        command: `echo '${claim.value}'  # TODO: replace with real verification command`,
        tolerance: "±10%",
        last_value: claim.value,
        last_verified_at: today,
        note: `Auto-extracted from README: "${claim.raw}"`,
      });
    }
  }

  return {
    repo: existing?.repo ?? repoName,
    last_full_verification: today,
    claims: Array.from(existingClaims.values()),
  };
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function processRepo(repoDir: string, dry: boolean): Promise<void> {
  const readmePath = join(repoDir, "README.md");
  if (!existsSync(readmePath)) {
    console.log(`  ⏭️  ${repoDir} — no README.md, skipping`);
    return;
  }

  const content = readFileSync(readmePath, "utf-8");
  const repoName = repoDir.split("/").pop() ?? repoDir;

  console.log(`\n── ${repoName}`);

  // Try LLM first, fall back to regex
  let claims = await llmExtractGemini(repoName, content);
  let method = "gemini";

  if (claims.length === 0) {
    claims = await llmExtractAlibaba(repoName, content);
    method = "alibaba";
  }

  if (claims.length === 0) {
    claims = regexExtract(content);
    method = "regex";
  }

  console.log(`  Method: ${method} | Claims found: ${claims.length}`);
  for (const c of claims) {
    console.log(`  + ${c.id}: ${c.value} (${c.raw.trim().slice(0, 60)})`);
  }

  const manifest = mergeWithExisting(repoDir, claims);

  if (dry) {
    console.log(`  [dry] Would write ${manifest.claims.length} claims to .egos-manifest.yaml`);
    return;
  }

  const manifestPath = join(repoDir, ".egos-manifest.yaml");
  const header = `# .egos-manifest.yaml — ${manifest.repo}\n# Auto-generated/updated by manifest-generator.ts (DRIFT-011)\n# Full spec: /home/enio/egos/docs/DOC_DRIFT_SHIELD.md\n\n`;
  writeFileSync(manifestPath, header + stringifyYaml(manifest));
  console.log(`  ✅ Written: ${manifestPath} (${manifest.claims.length} claims)`);
}

const args = process.argv.slice(2);
const dry = args.includes("--dry");
const all = args.includes("--all");
const repoIdx = args.indexOf("--repo");
const singleRepo = repoIdx !== -1 ? args[repoIdx + 1] : undefined;

const repos = all
  ? KNOWN_REPOS.filter((r) => existsSync(join(r, "README.md")))
  : singleRepo
  ? [singleRepo]
  : [process.cwd()];

console.log(`\n🧠 Manifest Generator${dry ? " (dry)" : ""} — ${repos.length} repo(s)`);
console.log(`   Strategy: Gemini Flash → Alibaba Qwen → regex`);

for (const repo of repos) {
  await processRepo(repo, dry);
}

console.log("\n✅ Done");
