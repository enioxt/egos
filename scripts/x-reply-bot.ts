#!/usr/bin/env bun
/**
 * 🐦 EGOS X Reply Bot
 *
 * Monitora threads relevantes no X.com e responde com inteligência.
 * Rate limits (Free tier): 50 writes/day, 10 searches/15min
 * Estratégia: max 40 replies/day, 1-2/hora, só threads de alto valor
 *
 * Deploy: VPS cron `0 * * * *` (hourly) + state file para budget
 *
 * Usage:
 *   bun scripts/x-reply-bot.ts              # run (dry-run if no keys)
 *   bun scripts/x-reply-bot.ts --dry-run    # never posts, only logs
 *   bun scripts/x-reply-bot.ts --status     # show today's budget
 */

import { writeFileSync, readFileSync, existsSync } from "fs";
import { join } from "path";

const DRY_RUN = process.argv.includes("--dry-run") || !process.env.X_BEARER_TOKEN;
const AUTO_APPROVE = process.env.AUTO_APPROVE === "true"; // Set to post immediately without dashboard review
const SUPABASE_URL = process.env.SUPABASE_URL ?? process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
const STATUS_ONLY = process.argv.includes("--status");
const STATE_FILE = "/tmp/x-reply-bot-state.json";

// ── Rate Limit Budget ─────────────────────────────────────────────────────────

interface DailyState {
  date: string;
  replies_sent: number;
  replied_to: string[]; // tweet IDs we already replied to
}

const MAX_DAILY_REPLIES = 40; // conservative buffer below 50 hard limit
const MAX_PER_RUN = 3;        // max replies per hourly run

function loadState(): DailyState {
  const today = new Date().toISOString().slice(0, 10);
  if (existsSync(STATE_FILE)) {
    try {
      const s = JSON.parse(readFileSync(STATE_FILE, "utf8")) as DailyState;
      if (s.date === today) return s;
    } catch {}
  }
  return { date: today, replies_sent: 0, replied_to: [] };
}

function saveState(s: DailyState) {
  writeFileSync(STATE_FILE, JSON.stringify(s, null, 2));
}

// ── Topic Monitors ────────────────────────────────────────────────────────────

interface TopicQuery {
  query: string;
  category: string;
  our_angle: string;           // what we have to add
  min_likes: number;           // only reply to threads with at least this
  link?: string;               // optional link to share
}

const TOPICS: TopicQuery[] = [
  // AI Agents / Open Source
  {
    query: '"multi-agent" compounding errors lang:en -is:retweet',
    category: "agent_reliability",
    our_angle: "EGOS governance solves compounding errors via frozen zones + bounded execution (BRAID pattern). arXiv 2512.15959",
    min_likes: 20,
    link: "https://github.com/enioxt/egos",
  },
  {
    query: '"Claude Code" hooks OR "Claude Code" agents lang:en -is:retweet',
    category: "claude_code",
    our_angle: "EGOS has 10 custom hooks + 25 skills + governance layer on top of Claude Code. Open source.",
    min_likes: 15,
    link: "https://github.com/enioxt/egos",
  },
  {
    query: 'BRAID "SERV Reasoning" OR "bounded reasoning" OR "Guided Reasoning Diagram" lang:en -is:retweet',
    category: "braid",
    our_angle: "Building BRAID-compatible execution layer in EGOS — GRD generator via /coordinator skill",
    min_likes: 10,
    link: "https://github.com/enioxt/egos",
  },
  {
    query: 'OpenHarness OR "open harness" agent framework lang:en -is:retweet',
    category: "openharness",
    our_angle: "Tracking OpenHarness (HKUDS) — 44x smaller than Claude Code. Evaluating integration with EGOS harness layer.",
    min_likes: 5,
    link: "https://github.com/enioxt/egos",
  },
  {
    query: '"agent governance" OR "AI governance" open-source framework lang:en -is:retweet',
    category: "governance",
    our_angle: "EGOS: open-source multi-agent governance kernel. GUARANI rules, frozen zones, pre-commit enforcement.",
    min_likes: 20,
    link: "https://github.com/enioxt/egos",
  },
  {
    query: 'LGPD "PII detection" OR "dados pessoais" API open-source lang:pt -is:retweet',
    category: "guard_brasil",
    our_angle: "Guard Brasil — detecção PII/LGPD open source. 15 padrões BR (CPF, RG, CNPJ...), 85.3% F1.",
    min_likes: 10,
    link: "https://www.npmjs.com/package/@egosbr/guard-brasil",
  },
  {
    query: '"licitação" API OR "PNCP" dados abertos lang:pt -is:retweet',
    category: "eagle_eye",
    our_angle: "Eagle Eye: OSINT de licitações públicas BR em tempo real. 84 municípios, Querido Diário + PNCP. Open source.",
    min_likes: 10,
    link: "https://github.com/enioxt/egos",
  },
  {
    query: '"agent framework" "open source" release OR launched lang:en -is:retweet',
    category: "ecosystem",
    our_angle: "Watching the space. EGOS is an open-source governance kernel for multi-agent systems.",
    min_likes: 50,
    link: "https://github.com/enioxt/egos",
  },
];

// ── X API Client ──────────────────────────────────────────────────────────────

interface XTweet {
  id: string;
  text: string;
  author_id: string;
  public_metrics?: { like_count: number; reply_count: number; retweet_count: number };
  conversation_id?: string;
}

interface XSearchResult {
  data?: XTweet[];
  meta?: { result_count: number };
}

async function searchTweets(query: string, maxResults = 10): Promise<XTweet[]> {
  const params = new URLSearchParams({
    query: query,
    max_results: String(Math.min(maxResults, 10)),
    "tweet.fields": "author_id,public_metrics,conversation_id,created_at",
    sort_order: "recency",
  });

  const res = await fetch(`https://api.twitter.com/2/tweets/search/recent?${params}`, {
    headers: {
      Authorization: `Bearer ${process.env.X_BEARER_TOKEN}`,
    },
    signal: AbortSignal.timeout(10000),
  });

  if (!res.ok) {
    if (res.status === 429) throw new Error("X_RATE_LIMIT");
    console.warn(`  X search HTTP ${res.status}: ${query.slice(0, 50)}`);
    return [];
  }

  const data = (await res.json()) as XSearchResult;
  return data.data ?? [];
}

async function postReply(replyToId: string, text: string): Promise<boolean> {
  if (DRY_RUN) {
    console.log(`  [DRY RUN] Would reply to ${replyToId}:\n  "${text}"`);
    return true;
  }

  // Use OAuth 1.0a (requires X_API_KEY + X_ACCESS_TOKEN for write)
  // Note: Bearer Token is READ-ONLY. Write requires OAuth 1.0a.
  // Using oauth-1.0a pattern with Twitter API v2 POST /2/tweets
  const body = JSON.stringify({ text, reply: { in_reply_to_tweet_id: replyToId } });

  // Simple OAuth 1.0a implementation
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const nonce = Math.random().toString(36).substring(2);
  const method = "POST";
  const url = "https://api.twitter.com/2/tweets";

  const oauthParams = {
    oauth_consumer_key: process.env.X_API_KEY!,
    oauth_nonce: nonce,
    oauth_signature_method: "HMAC-SHA1",
    oauth_timestamp: timestamp,
    oauth_token: process.env.X_ACCESS_TOKEN!,
    oauth_version: "1.0",
  };

  // Build signature base string
  const sortedParams = Object.entries(oauthParams)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join("&");
  const signatureBase = `${method}&${encodeURIComponent(url)}&${encodeURIComponent(sortedParams)}`;
  const signingKey = `${encodeURIComponent(process.env.X_API_SECRET!)}&${encodeURIComponent(process.env.X_ACCESS_TOKEN_SECRET!)}`;

  // HMAC-SHA1
  const encoder = new TextEncoder();
  const keyData = encoder.encode(signingKey);
  const msgData = encoder.encode(signatureBase);
  const cryptoKey = await crypto.subtle.importKey("raw", keyData, { name: "HMAC", hash: "SHA-1" }, false, ["sign"]);
  const signature = await crypto.subtle.sign("HMAC", cryptoKey, msgData);
  const signatureB64 = btoa(String.fromCharCode(...new Uint8Array(signature)));

  const authHeader = "OAuth " + Object.entries({ ...oauthParams, oauth_signature: signatureB64 })
    .map(([k, v]) => `${encodeURIComponent(k)}="${encodeURIComponent(v)}"`)
    .join(", ");

  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: authHeader,
      "Content-Type": "application/json",
    },
    body,
    signal: AbortSignal.timeout(10000),
  });

  if (!res.ok) {
    const err = await res.text();
    console.warn(`  POST reply failed ${res.status}: ${err.slice(0, 100)}`);
    return false;
  }

  return true;
}

// ── Reply Generator ───────────────────────────────────────────────────────────

async function generateReply(tweet: XTweet, topic: TopicQuery): Promise<string> {
  if (!process.env.OPENROUTER_API_KEY) {
    // Fallback: template reply
    return `${topic.our_angle}${topic.link ? ` ${topic.link}` : ""}`;
  }

  const prompt = `You are Enio Rocha, a Brazilian open-source builder working on EGOS (multi-agent governance framework).

Tweet you're replying to:
"${tweet.text}"

Your angle: ${topic.our_angle}
${topic.link ? `Link to share: ${topic.link}` : ""}

Write a reply (max 240 chars) that:
- Adds genuine value to the conversation
- Mentions our relevant work naturally (not spammy)
- Is in the same language as the tweet (PT-BR or EN)
- Does NOT start with "I" or "We built"
- Sounds human, not a bot
- If sharing a link, include it naturally

Reply only with the tweet text, nothing else.`;

  try {
    const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "qwen/qwen-2.5-7b-instruct:free", // free tier, fast
        messages: [{ role: "user", content: prompt }],
        max_tokens: 100,
        temperature: 0.7,
      }),
    });
    if (res.ok) {
      const d = (await res.json()) as { choices?: Array<{ message?: { content?: string } }> };
      const text = d.choices?.[0]?.message?.content?.trim() ?? "";
      if (text && text.length < 270) return text;
    }
  } catch (_e) {}

  // Fallback
  return `${topic.our_angle.slice(0, 200)}${topic.link ? ` ${topic.link}` : ""}`.slice(0, 270);
}

// ── Supabase HQ Dashboard Integration ────────────────────────────────────────

async function saveToSupabase(tweet: XTweet, topic: string, generatedReply: string): Promise<void> {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) return;
  try {
    await fetch(`${SUPABASE_URL}/rest/v1/x_reply_runs`, {
      method: "POST",
      headers: {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": `Bearer ${SUPABASE_SERVICE_KEY}`,
        "Content-Type": "application/json",
        "Prefer": "return=minimal,resolution=ignore-duplicates",
      },
      body: JSON.stringify({
        topic,
        tweet_id: tweet.id,
        tweet_text: tweet.text,
        tweet_author: tweet.author_id,
        tweet_likes: tweet.public_metrics?.like_count ?? 0,
        generated_reply: generatedReply,
        status: DRY_RUN ? "dry_run" : "pending",
      }),
    });
    console.log(`  💾 Saved to HQ dashboard (status=${DRY_RUN ? "dry_run" : "pending"})`);
  } catch (e) {
    console.warn(`  ⚠️ Supabase save failed: ${String(e)}`);
  }
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  const state = loadState();

  if (STATUS_ONLY) {
    console.log(`📊 X Reply Bot — Today's Budget`);
    console.log(`  Date: ${state.date}`);
    console.log(`  Replies sent: ${state.replies_sent}/${MAX_DAILY_REPLIES}`);
    console.log(`  Remaining budget: ${MAX_DAILY_REPLIES - state.replies_sent}`);
    console.log(`  Already replied to: ${state.replied_to.length} tweets`);
    return;
  }

  const budgetLeft = MAX_DAILY_REPLIES - state.replies_sent;
  if (budgetLeft <= 0) {
    console.log(`⛔ Daily budget exhausted (${state.replies_sent}/${MAX_DAILY_REPLIES}). Next reset at midnight.`);
    return;
  }

  console.log(`🐦 X Reply Bot — Run ${new Date().toISOString()}`);
  console.log(`  Budget: ${state.replies_sent}/${MAX_DAILY_REPLIES} used, ${Math.min(budgetLeft, MAX_PER_RUN)} this run`);
  if (DRY_RUN) console.log(`  [DRY RUN MODE — no actual posts]`);

  let repliesThisRun = 0;
  const runLimit = Math.min(budgetLeft, MAX_PER_RUN);

  for (const topic of TOPICS) {
    if (repliesThisRun >= runLimit) break;

    try {
      const tweets = await searchTweets(topic.query);
      await new Promise(r => setTimeout(r, 2000)); // rate limit buffer between searches

      for (const tweet of tweets) {
        if (repliesThisRun >= runLimit) break;
        if (state.replied_to.includes(tweet.id)) continue;

        const likes = tweet.public_metrics?.like_count ?? 0;
        if (likes < topic.min_likes) continue;

        // Don't reply to our own tweets
        if (tweet.author_id === process.env.X_USER_ID) continue;

        console.log(`\n  📌 [${topic.category}] Tweet ${tweet.id} (${likes} likes)`);
        console.log(`     "${tweet.text.slice(0, 100)}..."`);

        const reply = await generateReply(tweet, topic);
        console.log(`  💬 Reply: "${reply}"`);

        // Save to HQ dashboard for approval (replaces auto-posting)
        await saveToSupabase(tweet, topic.category, reply);

        if (AUTO_APPROVE && !DRY_RUN) {
          // Legacy auto-approve mode — post immediately
          const ok = await postReply(tweet.id, reply);
          if (ok) {
            state.replies_sent++;
            state.replied_to.push(tweet.id);
            repliesThisRun++;
            saveState(state);
            console.log(`  ✅ Replied (${state.replies_sent}/${MAX_DAILY_REPLIES} today)`);
            await new Promise(r => setTimeout(r, 5000)); // 5s between posts
          }
        } else {
          // Dashboard approval mode — mark as seen, wait for Enio to approve in HQ
          state.replied_to.push(tweet.id);
          repliesThisRun++;
          saveState(state);
          if (!DRY_RUN) {
            console.log(`  📋 Queued for HQ approval — hq.egos.ia.br/x`);
          }
        }
      }
    } catch (e: any) {
      if (e.message === "X_RATE_LIMIT") {
        console.warn(`  ⚠️ Rate limited — stopping this run`);
        break;
      }
      console.warn(`  ⚠️ Topic error [${topic.category}]: ${e.message}`);
    }
  }

  console.log(`\n✅ Run complete: ${repliesThisRun} replies sent (${state.replies_sent}/${MAX_DAILY_REPLIES} today)`);
}

main().catch(console.error);
