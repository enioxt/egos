#!/usr/bin/env bun
// 💎 Gem Hunter Weekly Digest — GH-074
//
// Selects top 3-5 gems from the last N days and formats them for
// newsletter/email (Markdown), Telegram, and API (JSON).
//
// Tables used:
//   gem_hunter_gems  — Supabase (project: lhscgsqhiooyatkebose)
//     columns: url, name, source, category, description, stars,
//              first_seen, last_seen, run_count, max_score
//
// Usage:
//   bun run scripts/gem-hunter-digest.ts              # last 7 days, live
//   bun run scripts/gem-hunter-digest.ts --dry-run    # generate only, no save/send
//   bun run scripts/gem-hunter-digest.ts --days 14    # look back 14 days
//
// Cron: 0 2 * * 4  (02:00 UTC Thursday)

import { writeFileSync, mkdirSync, existsSync } from "fs";
import { join } from "path";

// ── Config ─────────────────────────────────────────────────────────────────

const DRY_RUN = process.argv.includes("--dry-run");
const DAYS_BACK = parseInt(
  process.argv.find((a) => a.startsWith("--days="))?.split("=")[1] ??
    process.argv[process.argv.indexOf("--days") + 1] ??
    "7",
  10,
) || 7;

const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
const DASHSCOPE_API_KEY = process.env.ALIBABA_DASHSCOPE_API_KEY ?? "";
const DASHSCOPE_BASE_URL =
  process.env.ALIBABA_DASHSCOPE_BASE_URL ??
  "https://dashscope-intl.aliyuncs.com/compatible-mode/v1";
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY ?? "";
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? "";
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID ?? "";

const TOP_N = 5; // max gems to include
const MIN_GEMS = 3; // warn if fewer than this
const DIGEST_DIR = "/home/enio/egos/docs/gem-hunter";

// ── Types ──────────────────────────────────────────────────────────────────

interface GemRow {
  url: string;
  name: string;
  source: string;
  category: string;
  description: string;
  stars: number | null;
  first_seen: string;
  last_seen: string;
  run_count: number;
  max_score: number;
}

interface DigestGem {
  rank: number;
  name: string;
  url: string;
  source: string;
  category: string;
  description: string;
  stars: number | null;
  max_score: number;
  run_count: number;
  why_it_matters: string; // generated or fallback
  llm_provider: string;
}

interface DigestOutput {
  generated_at: string;
  period_days: number;
  gem_count: number;
  gems: DigestGem[];
}

// ── Supabase query ─────────────────────────────────────────────────────────

async function fetchTopGems(days: number): Promise<GemRow[]> {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    console.warn("⚠️  SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set — skipping Supabase query");
    return [];
  }

  const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
  const url =
    `${SUPABASE_URL}/rest/v1/gem_hunter_gems` +
    `?select=url,name,source,category,description,stars,first_seen,last_seen,run_count,max_score` +
    `&first_seen=gte.${since}` +
    `&order=max_score.desc` +
    `&limit=${TOP_N}`;

  const res = await fetch(url, {
    headers: {
      apikey: SUPABASE_SERVICE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
      "Content-Type": "application/json",
    },
    signal: AbortSignal.timeout(15000),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Supabase query failed (${res.status}): ${text}`);
  }

  return (await res.json()) as GemRow[];
}

// ── LLM "why it matters" generation ────────────────────────────────────────

async function generateWhyItMatters(gem: GemRow): Promise<{ text: string; provider: string }> {
  const prompt = `You are a senior developer writing a weekly newsletter about exciting open-source discoveries.

Repo: ${gem.name}
URL: ${gem.url}
Category: ${gem.category}
Stars: ${gem.stars ?? "unknown"}
Description: ${gem.description.slice(0, 300)}

Write a single sentence (max 120 chars) explaining WHY this repo matters to developers building AI agents or data-compliance tools. Be concrete, not hype. Answer in English.`;

  const body = JSON.stringify({
    model: "qwen-plus",
    messages: [{ role: "user", content: prompt }],
    max_tokens: 100,
    temperature: 0.4,
  });

  // Primary: DashScope
  if (DASHSCOPE_API_KEY) {
    try {
      const res = await fetch(`${DASHSCOPE_BASE_URL}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${DASHSCOPE_API_KEY}`,
        },
        body,
        signal: AbortSignal.timeout(10000),
      });
      if (res.ok) {
        const data = (await res.json()) as {
          choices?: { message?: { content?: string } }[];
        };
        const text = data.choices?.[0]?.message?.content?.trim() ?? "";
        if (text) return { text: text.slice(0, 200), provider: "alibaba/qwen-plus" };
      }
    } catch {
      // fall through to OpenRouter
    }
  }

  // Fallback: OpenRouter free
  if (OPENROUTER_API_KEY) {
    try {
      const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${OPENROUTER_API_KEY}`,
        },
        body: JSON.stringify({ ...JSON.parse(body), model: "google/gemma-4-26b-a4b-it:free" }),
        signal: AbortSignal.timeout(15000),
      });
      if (res.ok) {
        const data = (await res.json()) as {
          choices?: { message?: { content?: string } }[];
        };
        const text = data.choices?.[0]?.message?.content?.trim() ?? "";
        if (text) return { text: text.slice(0, 200), provider: "openrouter/gemma-4-26b" };
      }
    } catch {
      // no LLM available
    }
  }

  // Fallback: use description excerpt
  const fallback = gem.description.slice(0, 120).trim() + (gem.description.length > 120 ? "…" : "");
  return { text: fallback, provider: "description-fallback" };
}

// ── Format helpers ─────────────────────────────────────────────────────────

function starsLabel(stars: number | null): string {
  if (stars === null) return "n/a";
  if (stars >= 1000) return `${(stars / 1000).toFixed(1)}k`;
  return String(stars);
}

function categoryEmoji(category: string): string {
  const map: Record<string, string> = {
    agents: "🤖",
    blockchain: "⛓️",
    "control-plane": "🎛️",
    research: "🔬",
    "research-gems": "🔬",
    security: "🔒",
    compliance: "⚖️",
    llm: "🧠",
    tools: "🛠️",
    infra: "🏗️",
    "report-generators": "📊",
    crypto: "💰",
    "crypto-gems": "💰",
  };
  return map[category] ?? "💎";
}

function formatMarkdown(gems: DigestGem[], period: number, dateStr: string): string {
  const lines: string[] = [
    `# 💎 Gem Hunter Weekly Digest — ${dateStr}`,
    "",
    `> Top ${gems.length} repositories discovered in the last ${period} days, curated by score and relevance.`,
    "",
    "---",
    "",
  ];

  for (const gem of gems) {
    const emoji = categoryEmoji(gem.category);
    lines.push(`## ${gem.rank}. ${emoji} [${gem.name}](${gem.url})`);
    lines.push("");
    lines.push(`**Why it matters:** ${gem.why_it_matters}`);
    lines.push("");
    lines.push(
      `| Score | Stars | Source | Category | Seen |`,
    );
    lines.push(`|-------|-------|--------|----------|------|`);
    lines.push(
      `| ${gem.max_score} | ${starsLabel(gem.stars)} | ${gem.source} | ${gem.category} | ${gem.run_count}x |`,
    );
    lines.push("");
    if (gem.description) {
      lines.push(`> ${gem.description.slice(0, 200)}${gem.description.length > 200 ? "…" : ""}`);
      lines.push("");
    }
    lines.push("---");
    lines.push("");
  }

  lines.push(`*Generated at ${new Date().toISOString()} by gem-hunter-digest.ts (GH-074)*`);
  return lines.join("\n");
}

function formatTelegram(gems: DigestGem[], period: number, dateStr: string): string {
  const header = `💎 <b>Gem Hunter Weekly — ${dateStr}</b>\nTop ${gems.length} repos dos últimos ${period} dias\n`;
  const items = gems
    .map((gem) => {
      const emoji = categoryEmoji(gem.category);
      return (
        `\n${gem.rank}. ${emoji} <b><a href="${gem.url}">${gem.name}</a></b>\n` +
        `⭐ ${starsLabel(gem.stars)} | score ${gem.max_score} | ${gem.category}\n` +
        `📌 ${gem.why_it_matters}`
      );
    })
    .join("\n");

  return header + items;
}

function formatJson(gems: DigestGem[], period: number): DigestOutput {
  return {
    generated_at: new Date().toISOString(),
    period_days: period,
    gem_count: gems.length,
    gems,
  };
}

// ── Telegram send ──────────────────────────────────────────────────────────

async function sendTelegram(message: string): Promise<boolean> {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.log("⚠️  Telegram not configured (TELEGRAM_BOT_TOKEN / TELEGRAM_ADMIN_CHAT_ID missing)");
    return false;
  }

  try {
    // Telegram HTML messages max 4096 chars — truncate if needed
    const truncated = message.length > 4000 ? message.slice(0, 3990) + "\n…" : message;
    const response = await fetch(
      `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: TELEGRAM_CHAT_ID,
          text: truncated,
          parse_mode: "HTML",
          disable_web_page_preview: true,
        }),
        signal: AbortSignal.timeout(10000),
      },
    );

    if (!response.ok) {
      const err = await response.text();
      console.error(`❌ Telegram error (${response.status}): ${err}`);
      return false;
    }
    return true;
  } catch (error) {
    console.error("❌ Telegram exception:", error);
    return false;
  }
}

// ── Save digest file ───────────────────────────────────────────────────────

function saveDigest(markdown: string, dateStr: string): string {
  if (!existsSync(DIGEST_DIR)) {
    mkdirSync(DIGEST_DIR, { recursive: true });
  }
  const filePath = join(DIGEST_DIR, `digest-${dateStr}.md`);
  writeFileSync(filePath, markdown, "utf8");
  return filePath;
}

// ── Main ───────────────────────────────────────────────────────────────────

async function main() {
  console.log("💎 Gem Hunter Weekly Digest — GH-074");
  console.log(`Mode: ${DRY_RUN ? "DRY-RUN (no save/send)" : "LIVE"}`);
  console.log(`Period: last ${DAYS_BACK} days`);

  // 1. Fetch top gems
  console.log("\n🔍 Fetching top gems from Supabase...");
  let rows: GemRow[];
  try {
    rows = await fetchTopGems(DAYS_BACK);
  } catch (err) {
    console.error("❌ Failed to fetch gems:", err);
    process.exit(1);
  }

  if (rows.length === 0) {
    console.warn(`⚠️  No gems found for the last ${DAYS_BACK} days in gem_hunter_gems.`);
    process.exit(0);
  }

  if (rows.length < MIN_GEMS) {
    console.warn(`⚠️  Only ${rows.length} gems found (min recommended: ${MIN_GEMS}). Continuing...`);
  }

  console.log(`✅ Found ${rows.length} gems`);

  // 2. Generate "why it matters" for each gem
  console.log("\n🤖 Generating insights via LLM...");
  const gems: DigestGem[] = [];

  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    console.log(`   ${i + 1}/${rows.length} ${row.name} (score=${row.max_score})`);
    const { text: why, provider } = await generateWhyItMatters(row);
    gems.push({
      rank: i + 1,
      name: row.name,
      url: row.url,
      source: row.source,
      category: row.category,
      description: row.description,
      stars: row.stars,
      max_score: row.max_score,
      run_count: row.run_count,
      why_it_matters: why,
      llm_provider: provider,
    });
    console.log(`   ✓ [${provider}] ${why.slice(0, 80)}...`);
  }

  // 3. Format outputs
  const dateStr = new Date().toISOString().slice(0, 10);
  const markdown = formatMarkdown(gems, DAYS_BACK, dateStr);
  const telegram = formatTelegram(gems, DAYS_BACK, dateStr);
  const jsonOutput = formatJson(gems, DAYS_BACK);

  // 4. Print previews
  console.log("\n" + "=".repeat(60));
  console.log("📄 MARKDOWN PREVIEW (first 20 lines):");
  console.log(markdown.split("\n").slice(0, 20).join("\n"));
  console.log("\n📱 TELEGRAM PREVIEW:");
  console.log(telegram.slice(0, 600));
  console.log("\n📦 JSON (compact):");
  console.log(JSON.stringify({ gem_count: jsonOutput.gem_count, gems: jsonOutput.gems.map(g => ({ name: g.name, score: g.max_score })) }, null, 2));
  console.log("=".repeat(60));

  if (DRY_RUN) {
    console.log("\n⚠️  DRY-RUN: skipping save and Telegram send.");
    console.log("✅ Digest generated successfully.");
    return;
  }

  // 5. Save markdown
  console.log("\n💾 Saving digest...");
  const savedPath = saveDigest(markdown, dateStr);
  console.log(`✅ Saved: ${savedPath}`);

  // 6. Save JSON alongside markdown
  const jsonPath = join(DIGEST_DIR, `digest-${dateStr}.json`);
  writeFileSync(jsonPath, JSON.stringify(jsonOutput, null, 2), "utf8");
  console.log(`✅ JSON saved: ${jsonPath}`);

  // 7. Send Telegram
  console.log("\n📱 Sending Telegram notification...");
  const sent = await sendTelegram(telegram);
  console.log(sent ? "✅ Telegram sent" : "⚠️  Telegram send failed (check token/chat_id)");

  console.log("\n✅ Digest complete.");
}

main().catch((err) => {
  console.error("❌ Fatal error:", err);
  process.exit(1);
});
