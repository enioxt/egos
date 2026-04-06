#!/usr/bin/env bun
/**
 * 🚀 EGOS Rapid Response System
 *
 * Quando um trending topic tem match com nossas capacidades,
 * gera automaticamente:
 *   1. Thread X.com pronta para postar
 *   2. Showcase README limpo (não expõe repos sujos)
 *   3. Lista de repos/arquivos relevantes para linkar
 *
 * Usage:
 *   bun scripts/rapid-response.ts --topic "BRAID reasoning"
 *   bun scripts/rapid-response.ts --topic "PII LGPD" --post
 *   bun scripts/rapid-response.ts --scan  # check trending topics vs our capabilities
 *   bun scripts/rapid-response.ts --post-thread /tmp/egos-rapid-response-123.md
 *   bun scripts/rapid-response.ts --topic "court data" --post-thread  # generate + post
 */

import { writeFileSync, readFileSync, existsSync } from "fs";
import { join } from "path";

const ROOT = "/home/enio/egos";
const TOPIC = process.argv.find(a => a.startsWith("--topic="))?.split("=").slice(1).join("=") ??
              (process.argv.includes("--topic") ? process.argv[process.argv.indexOf("--topic") + 1] : undefined);
const SCAN = process.argv.includes("--scan");
const POST = process.argv.includes("--post");

// --post-thread can be: --post-thread <file> or just --post-thread (uses last generated)
const POST_THREAD_IDX = process.argv.indexOf("--post-thread");
const POST_THREAD = POST_THREAD_IDX !== -1;
const POST_THREAD_FILE = POST_THREAD_IDX !== -1
  ? (process.argv[POST_THREAD_IDX + 1] && !process.argv[POST_THREAD_IDX + 1].startsWith("--")
      ? process.argv[POST_THREAD_IDX + 1]
      : null)
  : null;

// ── EGOS Capability Map ───────────────────────────────────────────────────────
// Maps topics/keywords → what we have + links + 280-char pitch

interface EGOSCapability {
  id: string;
  keywords: string[];
  name: string;
  pitch: string;                  // ≤240 chars for X
  thread: string[];               // full thread (each item ≤280 chars)
  repos: { name: string; url: string; desc: string }[];
  clean_files: string[];          // files safe to share/link
}

const CAPABILITIES: EGOSCapability[] = [
  {
    id: "multi_agent_governance",
    keywords: ["multi-agent", "agent governance", "agent framework", "agent reliability", "compounding error"],
    name: "EGOS Multi-Agent Governance Kernel",
    pitch: "EGOS: open-source governance kernel for multi-agent AI systems. Frozen zones, pre-commit enforcement, 10 hooks, 25 skills, BRAID-compatible. github.com/enioxt/egos",
    thread: [
      "🧵 Built EGOS — an open-source governance kernel for multi-agent AI.\n\nProblem: Multi-agent chains compound errors. 95% accuracy per step → ~0% at 100 steps.\n\nOur fix isn't 'use a bigger model'. It's architecture.",
      "EGOS governance layer:\n• Frozen zones (critical files locked from agent drift)\n• Pre-commit enforcement (gitleaks + tsc + doc proliferation check)\n• 10 custom Claude Code hooks (frustration-detector, anti-compaction guard...)\n• BRAID-compatible /coordinator skill",
      "The executor pattern:\n1. Claude Code (Sonnet) generates a Guided Reasoning Diagram in Mermaid\n2. Cheap models (Qwen Flash/Hermes) execute nodes strictly\n3. Shadow auditor validates before handoff\n\n74-122× cheaper. Zero compounding errors.",
      "3 CCR autonomous jobs running 24/7:\n• Governance Drift Sentinel\n• Code Intel + Security Audit\n• Gem Hunter (discovers AI tools day-0)\n\nAll Haiku-powered (10× cheaper than Sonnet). Reports in docs/jobs/",
      "Open source. Built in Bun + TypeScript.\nAll governance rules are shareable (.guarani/ folder).\n\ngithub.com/enioxt/egos\n\nIf you're building multi-agent systems and tired of drift, check it out 👇",
    ],
    repos: [
      { name: "egos", url: "https://github.com/enioxt/egos", desc: "Governance kernel" },
    ],
    clean_files: [
      "docs/AI_COVERAGE_MAP.md",
      "docs/CAPABILITY_REGISTRY.md",
      "CLAUDE_CODE_INTEGRATIONS_MAP.md",
    ],
  },
  {
    id: "pii_lgpd",
    keywords: ["LGPD", "PII detection", "dados pessoais", "privacy", "compliance brazil", "CPF", "CNPJ"],
    name: "Guard Brasil — PII Detection LGPD",
    pitch: "Guard Brasil: open-source PII detection for Brazilian LGPD compliance. 15 patterns (CPF, RG, CNPJ...), 85.3% F1 score. npm install @egosbr/guard-brasil",
    thread: [
      "🧵 Built Guard Brasil — PII detection specifically for Brazil's LGPD.\n\nMost PII tools were built for GDPR/CCPA. None handled Brazilian-specific: CPF, RG, MASP, Electoral ID, CNH...",
      "15 patterns out of the box:\n• CPF (with validation algorithm)\n• RG (7 state formats)\n• CNPJ (with check digit)\n• CEP, CNH, Passaporte BR\n• Telefone, Email, Nome completo\n• MASP (funcional público SP)\n• Título de eleitor\n\nAll with regex + algorithmic validation.",
      "Benchmark vs alternatives:\n• Guard Brasil: 85.3% F1\n• Presidio (default): ~71% F1 on BR data\n• anonym.legal: closed source\n\nBetter recall on Brazilian CPF/RG patterns specifically.",
      "npm install @egosbr/guard-brasil\n\nOr use the REST API: guard.egos.ia.br/health\n\nPay-per-use: R$0.02/call. Free tier available.\n\ngithub.com/enioxt/egos",
    ],
    repos: [
      { name: "guard-brasil npm", url: "https://www.npmjs.com/package/@egosbr/guard-brasil", desc: "npm package" },
    ],
    clean_files: [
      "docs/products/GUARD_BRASIL.md",
      "packages/guard-brasil/src/pii-patterns.ts",
    ],
  },
  {
    id: "braid_serv",
    keywords: ["BRAID", "SERV reasoning", "bounded reasoning", "guided reasoning diagram", "OpenServ"],
    name: "BRAID-Compatible Execution in EGOS",
    pitch: "Implementing BRAID (arXiv 2512.15959) in EGOS: GRD generator via /coordinator skill + Hermes-3 as bounded executor. 74-122× cheaper. github.com/enioxt/egos",
    thread: [
      "🧵 BRAID (Bounded Reasoning for Autonomous Inference and Decisions) is the most important paper for multi-agent reliability I've read.\n\nHere's how we're implementing it in EGOS:",
      "The insight: LLMs don't reason, they predict tokens. 'Use a bigger model' just burns more tokens.\n\nBRAID fix: plan once with strong model → execute many times with cheap models following a strict graph.\n\nInput → GRD (Mermaid) → nano executors",
      "Our /coordinator skill is proto-BRAID:\n• Phase 1: Research (Explore agents, parallel)\n• Phase 2: Synthesis (Sonnet)\n• Phase 3: Implementation (Edit/Write, sequential)\n• Phase 4: Verification (tsc + tests)\n\nNext: add Mermaid GRD output in Phase 2.",
      "Hermes-3 (NousResearch) as the execution model:\n• nousresearch/hermes-3-llama-3.1-70b on OpenRouter\n• Best structured output + function calling at 70B\n• Perfect for strict node execution in GRD\n• ~10× cheaper than Sonnet for execution tasks",
      "Building this open-source in EGOS.\nIf you're working on BRAID or OpenHarness — let's compare notes.\n\ngithub.com/enioxt/egos",
    ],
    repos: [
      { name: "egos", url: "https://github.com/enioxt/egos", desc: "BRAID implementation" },
    ],
    clean_files: [
      "docs/knowledge/HARVEST.md",
      ".claude/commands/coordinator.md",
    ],
  },
  {
    id: "eagle_eye_procurement",
    keywords: ["licitação", "PNCP", "pregão", "compras públicas", "transparência pública", "govtech", "public procurement brazil"],
    name: "Eagle Eye — Brazilian Procurement Intelligence",
    pitch: "Eagle Eye: real-time Brazilian public procurement intelligence. 84 municipalities, Querido Diário + PNCP API (R$1tri/yr market). Open source. eagleeye.egos.ia.br",
    thread: [
      "🧵 Built Eagle Eye — OSINT for Brazilian public procurement (licitações).\n\nBrazil has R$1 trillion/year in public spending. It's all public data. But nobody aggregates it intelligently.",
      "Pipeline:\n1. Querido Diário API (official gazettes)\n2. Gemini Flash analyzes gazette text\n3. Extracts: object, value, deadline, winner\n4. Classifies: segment, modality, size tier\n5. Alerts via Telegram + email\n\n~$0.01/gazette analysis.",
      "Licitação taxonomy we built:\n• 9 segments (TI, SAUDE, OBRAS, SERVICOS...)\n• 12 modalities (PREGAO_ELETRONICO, DISPENSA...)\n• 4 size tiers by value (MICRO < 50K, GRANDE > 5M)\n• SRP flag (other agencies can adhere)\n• esfera (FEDERAL/ESTADUAL/MUNICIPAL)",
      "84 municipalities covered (all state capitals + tech hubs).\nDiscover-territories script: crosses IBGE + PNCP to rank uncovered cities by real procurement volume.\n\nOpen source. eagleeye.egos.ia.br",
    ],
    repos: [
      { name: "eagle-eye", url: "https://eagleeye.egos.ia.br", desc: "Live dashboard" },
    ],
    clean_files: [
      "docs/strategy/EAGLE_EYE_SSOT.md",
    ],
  },
  // ── X-006: New capability profiles ─────────────────────────────────────────
  {
    id: "br_acc",
    keywords: ["BRACC", "br-acc", "Brazilian court data", "STF data", "judicial intelligence", "tribunal", "processo judicial"],
    name: "BR-ACC — Brazilian Court Intelligence",
    pitch: "BR-ACC: real-time intelligence from 47M+ entities in Brazilian courts (STF, STJ, CNJ). PEP detection, network analysis, watchlists. Open source.",
    thread: [
      "🧵 BR-ACC: we scraped and indexed 47M+ entities from Brazilian courts (STF, STJ, CNJ, TRFs).\n\nWhy? Because Brazil's judicial data is public but completely unstructured. Nobody was connecting the dots.",
      "What the data reveals:\n• PEP detection: identify Politically Exposed Persons appearing in court records\n• Network analysis: map relationships between entities across cases\n• Watchlist matching: flag sanctioned individuals and companies\n• Timeline: track how cases evolve across years",
      "The pipeline:\n1. Scrape court portals (CNJ, STF, STJ, all TRFs)\n2. Entity extraction via NLP (names, CPF, CNPJ, OAB)\n3. Graph ingestion → Neo4j (47M+ nodes, 120M+ edges)\n4. Dedup + canonical entity resolution\n5. REST API for queries\n\nAll open source.",
      "Use cases:\n• KYC/AML compliance checks against court records\n• Due diligence for M&A and investments\n• Investigative journalism (follow the money through litigation)\n• Competitive intelligence (who's suing your supplier?)\n\nBR-ACC: open-source judicial intelligence for Brazil.",
    ],
    repos: [
      { name: "br-acc", url: "https://github.com/enioxt/br-acc", desc: "Brazilian court intelligence" },
    ],
    clean_files: [
      "docs/strategy/BR_ACC_SSOT.md",
    ],
  },
  {
    id: "sistema_852",
    keywords: ["citizen reporting", "civic tech", "transparência municipal", "denúncia pública", "open government brazil"],
    name: "Sistema 852 — Civic Intelligence Platform",
    pitch: "Sistema 852: civic reporting platform for Brazilian citizens. Municipal transparency, issue tracking, AI-powered resolution routing. 852.egos.ia.br",
    thread: [
      "🧵 Sistema 852: a civic reporting platform built for Brazilian citizens.\n\nThe problem: citizens have no effective way to report local issues, track government responses, or hold municipalities accountable.",
      "How it works:\n• Citizen submits issue (pothole, broken light, irregular construction, etc.)\n• AI classifies and routes to the right municipal department\n• Issue tracked publicly until resolution\n• Escalation alerts if ignored beyond SLA\n\nTransparência real, não teatro.",
      "The AI routing layer:\n• NLP classifies issue type (infraestrutura, saúde, educação, meio ambiente...)\n• Matches to correct secretaria and contact chain\n• Priority scoring based on: affected area, population density, recurrence\n• Auto-generates formal request in correct ABNT format for municipal protocols",
      "Open government, not open theater:\n• All reported issues are public and indexed\n• Resolution rates by municipality and department are tracked\n• Exports for journalists and researchers (CSV, API)\n• Citizens can upvote others' reports to escalate priority\n\n852.egos.ia.br — civic intelligence for Brazil.",
    ],
    repos: [
      { name: "sistema-852", url: "https://852.egos.ia.br", desc: "Civic intelligence platform" },
    ],
    clean_files: [
      "docs/strategy/SISTEMA_852_SSOT.md",
    ],
  },
  {
    id: "gem_hunter",
    keywords: ["open source discovery", "gem hunter", "AI tool discovery", "github trending", "best new repos", "open source radar"],
    name: "Gem Hunter — AI Tool Discovery Engine",
    pitch: "Gem Hunter: discovers the best open-source AI tools before they go viral. 20+ sources, BRAID-scoring, daily runs. gemhunter.egos.ia.br",
    thread: [
      "🧵 Gem Hunter: an AI-powered discovery engine for open-source tools.\n\nProblem: GitHub trending is gamed. Twitter is noise. Great tools go unnoticed for months while hype repos top the charts.",
      "20+ sources we monitor:\n• GitHub (stars velocity, fork ratio, contributor growth)\n• arXiv (new papers with code)\n• Hacker News (Show HN + Ask HN)\n• Reddit (r/MachineLearning, r/LocalLLaMA, r/programming)\n• Product Hunt, Discord servers, X.com\n\nCross-source signal = signal. Single-source = noise.",
      "BRAID scoring system (0-100):\n• B — Breakthrough potential (novel approach?)\n• R — Real usage (non-trivial forks, issues, PRs?)\n• A — Author credibility (track record, affiliations)\n• I — Integration fit (can EGOS ecosystem use this?)\n• D — Documentation quality (can you actually run it?)\n\nCuts 97% of noise. Surfaces day-0 gems.",
      "Daily automated runs:\n• Haiku-powered (10× cheaper than Sonnet)\n• Results on live dashboard: gemhunter.egos.ia.br\n• Telegram alerts for gems scoring >80\n• Weekly digest with detailed analysis\n\nOpen source. If you're tired of missing the real gems — gemhunter.egos.ia.br",
    ],
    repos: [
      { name: "gem-hunter", url: "https://gemhunter.egos.ia.br", desc: "AI tool discovery dashboard" },
    ],
    clean_files: [
      "docs/strategy/GEM_HUNTER_SSOT.md",
    ],
  },
];

// ── Score matching ────────────────────────────────────────────────────────────

function scoreMatch(topic: string, cap: EGOSCapability): number {
  const topicLower = topic.toLowerCase();
  let score = 0;
  for (const kw of cap.keywords) {
    if (topicLower.includes(kw.toLowerCase())) {
      score += kw.split(" ").length; // multi-word keywords score higher
    }
  }
  return score;
}

function findBestCapability(topic: string): EGOSCapability | null {
  const scored = CAPABILITIES.map(c => ({ cap: c, score: scoreMatch(topic, c) }))
    .filter(x => x.score > 0)
    .sort((a, b) => b.score - a.score);
  return scored[0]?.cap ?? null;
}

// ── Output Generator ──────────────────────────────────────────────────────────

function generateShowcaseREADME(cap: EGOSCapability, topic: string): string {
  return `# EGOS — ${cap.name}

> **Context:** Generated for rapid response to topic: "${topic}"
> **Date:** ${new Date().toISOString().slice(0, 10)}

## One-liner
${cap.pitch}

## Thread (X.com ready)
${cap.thread.map((t, i) => `**${i + 1}/${cap.thread.length}:**\n${t}`).join("\n\n")}

## Links
${cap.repos.map(r => `- **${r.name}**: ${r.url} — ${r.desc}`).join("\n")}

## Key Files to Share
${cap.clean_files.map(f => `- \`${f}\``).join("\n")}

---
*Auto-generated by EGOS Rapid Response System*
`;
}

// ── X API: Post Tweet ─────────────────────────────────────────────────────────
// Pattern borrowed from x-reply-bot.ts (OAuth 1.0a for write access)

async function postTweet(text: string): Promise<{ id: string } | null> {
  const url = "https://api.twitter.com/2/tweets";
  const method = "POST";
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const nonce = Math.random().toString(36).substring(2);

  const oauthParams = {
    oauth_consumer_key: process.env.X_API_KEY!,
    oauth_nonce: nonce,
    oauth_signature_method: "HMAC-SHA1",
    oauth_timestamp: timestamp,
    oauth_token: process.env.X_ACCESS_TOKEN!,
    oauth_version: "1.0",
  };

  const sortedParams = Object.entries(oauthParams)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join("&");
  const signatureBase = `${method}&${encodeURIComponent(url)}&${encodeURIComponent(sortedParams)}`;
  const signingKey = `${encodeURIComponent(process.env.X_API_SECRET!)}&${encodeURIComponent(process.env.X_ACCESS_TOKEN_SECRET!)}`;

  const encoder = new TextEncoder();
  const keyData = encoder.encode(signingKey);
  const msgData = encoder.encode(signatureBase);
  const cryptoKey = await crypto.subtle.importKey(
    "raw", keyData, { name: "HMAC", hash: "SHA-1" }, false, ["sign"]
  );
  const signature = await crypto.subtle.sign("HMAC", cryptoKey, msgData);
  const signatureB64 = btoa(String.fromCharCode(...new Uint8Array(signature)));

  const authHeader = "OAuth " + Object.entries({ ...oauthParams, oauth_signature: signatureB64 })
    .map(([k, v]) => `${encodeURIComponent(k)}="${encodeURIComponent(v)}"`)
    .join(", ");

  const res = await fetch(url, {
    method,
    headers: { Authorization: authHeader, "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
    signal: AbortSignal.timeout(10000),
  });

  if (!res.ok) {
    const err = await res.text();
    console.error(`  POST /2/tweets failed ${res.status}: ${err.slice(0, 200)}`);
    return null;
  }

  const data = (await res.json()) as { data?: { id: string } };
  return data.data ?? null;
}

// ── --post-thread handler ─────────────────────────────────────────────────────

function parseThreadFromFile(filePath: string): string[] {
  const content = readFileSync(filePath, "utf8");
  // Extract thread tweets from the "## Thread (X.com ready)" section
  const threadSection = content.match(/## Thread \(X\.com ready\)\n([\s\S]*?)(?:\n## |$)/);
  if (!threadSection) {
    throw new Error("Could not find '## Thread (X.com ready)' section in file");
  }

  const tweets: string[] = [];
  // Each tweet block starts with **N/M:** then the content
  const tweetBlocks = threadSection[1].split(/\*\*\d+\/\d+:\*\*\n/);
  for (const block of tweetBlocks) {
    const trimmed = block.trim();
    if (trimmed) {
      // Remove trailing section markers
      const clean = trimmed.replace(/\n\n## [\s\S]*$/, "").trim();
      if (clean) tweets.push(clean);
    }
  }
  return tweets;
}

async function handlePostThread(filePath: string | null): Promise<void> {
  // Resolve file: explicit path, or find last generated file
  let resolvedFile = filePath;
  if (!resolvedFile) {
    // Find most recent /tmp/egos-rapid-response-*.md
    const { execSync } = await import("child_process");
    try {
      resolvedFile = execSync("ls -t /tmp/egos-rapid-response-*.md 2>/dev/null | head -1")
        .toString()
        .trim();
    } catch {
      resolvedFile = "";
    }
    if (!resolvedFile) {
      console.error("No --post-thread file specified and no generated file found in /tmp.");
      console.error("Run: bun scripts/rapid-response.ts --topic \"<topic>\" first.");
      process.exit(1);
    }
    console.log(`Using last generated file: ${resolvedFile}`);
  }

  if (!existsSync(resolvedFile)) {
    console.error(`File not found: ${resolvedFile}`);
    process.exit(1);
  }

  let tweets: string[];
  try {
    tweets = parseThreadFromFile(resolvedFile);
  } catch (e: any) {
    console.error(`Failed to parse thread from file: ${e.message}`);
    process.exit(1);
  }

  if (tweets.length === 0) {
    console.error("No tweets found in the thread file.");
    process.exit(1);
  }

  console.log(`\nThread loaded: ${tweets.length} tweets from ${resolvedFile}\n`);
  tweets.forEach((t, i) => {
    console.log(`[${i + 1}/${tweets.length}] (${t.length} chars)`);
    console.log(t);
    console.log();
  });

  // Check for X_BEARER_TOKEN (read) or full OAuth credentials (write)
  const hasOAuth = process.env.X_API_KEY && process.env.X_API_SECRET &&
                   process.env.X_ACCESS_TOKEN && process.env.X_ACCESS_TOKEN_SECRET;

  if (!hasOAuth) {
    console.log("No X_BEARER_TOKEN / OAuth credentials — manual posting required.");
    console.log("\nCopy tweets above and post manually at x.com/compose/tweet");
    console.log("Tip: set X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET to enable auto-posting.");
    return;
  }

  // Post first tweet via X API
  console.log("Posting first tweet via X API...");
  const result = await postTweet(tweets[0]);

  if (!result) {
    console.error("Failed to post first tweet. Check credentials and try again.");
    process.exit(1);
  }

  console.log(`\nFirst tweet posted: https://x.com/i/web/status/${result.id}`);

  if (tweets.length > 1) {
    console.log("\nRemaining tweets (post as replies to the above, in order):\n");
    for (let i = 1; i < tweets.length; i++) {
      console.log(`[${i + 1}/${tweets.length}] Reply to previous tweet:`);
      console.log(tweets[i]);
      console.log();
    }
    console.log("Note: Full thread auto-posting (reply chaining) requires X Pro API tier.");
    console.log("Copy remaining tweets and reply manually to continue the thread.");
  }
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  // Handle --post-thread as a standalone flag (can combine with --topic)
  if (POST_THREAD && !SCAN && !TOPIC) {
    await handlePostThread(POST_THREAD_FILE);
    return;
  }

  if (SCAN) {
    console.log("EGOS Capability Map — Topics We Can Respond To:\n");
    for (const cap of CAPABILITIES) {
      console.log(`  OK ${cap.name}`);
      console.log(`     Keywords: ${cap.keywords.join(", ")}`);
      console.log(`     Pitch: "${cap.pitch.slice(0, 80)}..."\n`);
    }
    console.log(`Total: ${CAPABILITIES.length} capabilities mapped`);
    console.log(`\nUsage: bun scripts/rapid-response.ts --topic "BRAID reasoning"`);
    return;
  }

  if (!TOPIC) {
    console.error("Provide --topic or --scan");
    console.error("   Example: bun scripts/rapid-response.ts --topic 'BRAID multi-agent'");
    process.exit(1);
  }

  const cap = findBestCapability(TOPIC);
  if (!cap) {
    console.log(`No matching capability for topic: "${TOPIC}"`);
    console.log("   Run --scan to see available capabilities");
    return;
  }

  console.log(`Rapid Response for: "${TOPIC}"`);
  console.log(`   Matched: ${cap.name} (score: ${scoreMatch(TOPIC, cap)})\n`);

  // Print thread
  console.log("X Thread:\n");
  cap.thread.forEach((t, i) => {
    console.log(`[${i + 1}/${cap.thread.length}] ${t.length} chars`);
    console.log(t);
    console.log();
  });

  // Generate showcase README
  const readme = generateShowcaseREADME(cap, TOPIC);
  const outFile = `/tmp/egos-rapid-response-${Date.now()}.md`;
  writeFileSync(outFile, readme);
  console.log(`\nShowcase README: ${outFile}`);
  console.log(`Pitch: ${cap.pitch}`);

  if (POST_THREAD) {
    console.log("\nPosting thread from generated file...");
    await handlePostThread(outFile);
  } else if (POST) {
    console.log("\n--post flag detected. To auto-post thread, use --post-thread flag.");
    console.log(`   bun scripts/rapid-response.ts --post-thread ${outFile}`);
  }
}

main().catch(console.error);
