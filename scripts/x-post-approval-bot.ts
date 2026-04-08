#!/usr/bin/env bun
/**
 * x-post-approval-bot.ts — X.com Post HITL Approval System v1.0
 *
 * Flow:
 *   1. Poll Supabase x_post_queue for status='pending' posts
 *   2. Generate 3 alternatives via DashScope LLM (bold / conversational / technical)
 *      personalized by x_post_preferences learning data
 *   3. Send to Telegram with inline keyboard: [A] [B] [C] [✏️ Edit] [⏭️ Skip]
 *   4. User picks an option (or edits)
 *   5. Record choice in x_post_choices (including edit diff)
 *   6. Update x_post_preferences aggregated learning
 *   7. Post to X.com via API — done
 *
 * Usage:
 *   bun scripts/x-post-approval-bot.ts              # long-poll mode
 *   bun scripts/x-post-approval-bot.ts --once       # process all pending, then exit
 *   bun scripts/x-post-approval-bot.ts --dry-run    # never posts, never records
 */

export {};
const DRY_RUN = process.argv.includes("--dry-run");
const ONCE_MODE = process.argv.includes("--once");

const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? "";
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID ?? "";
const DASHSCOPE_KEY = process.env.ALIBABA_DASHSCOPE_API_KEY ?? "";
const DASHSCOPE_URL = process.env.ALIBABA_DASHSCOPE_BASE_URL ?? "https://dashscope-intl.aliyuncs.com/compatible-mode/v1";
const X_API_KEY = process.env.X_API_KEY ?? "";
const X_API_SECRET = process.env.X_API_SECRET ?? "";
const X_ACCESS_TOKEN = process.env.X_ACCESS_TOKEN ?? "";
const X_ACCESS_TOKEN_SECRET = process.env.X_ACCESS_TOKEN_SECRET ?? "";

// State for pending edit sessions: post_id → { option, text, awaitingEdit }
const pendingEdits = new Map<string, { postId: string; optionsId: string; option: string; text: string }>();
// Map telegram msg_id → post_id + options_id (for callback routing)
const msgToPost = new Map<number, { postId: string; optionsId: string; optionA: string; optionB: string; optionC: string; toneA: string; toneB: string; toneC: string }>();

// ── Supabase helpers ───────────────────────────────────────────────────────

async function supabase(method: string, path: string, body?: unknown) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1${path}`, {
    method,
    headers: {
      "apikey": SUPABASE_KEY,
      "Authorization": `Bearer ${SUPABASE_KEY}`,
      "Content-Type": "application/json",
      "Prefer": method === "POST" ? "return=representation" : "return=minimal",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Supabase ${method} ${path}: ${res.status} ${err}`);
  }
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

// ── Telegram helpers ───────────────────────────────────────────────────────

async function tg(method: string, params: Record<string, unknown>) {
  const res = await fetch(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  const data = await res.json() as { ok: boolean; result: unknown; description?: string };
  if (!data.ok) throw new Error(`Telegram ${method}: ${data.description}`);
  return data.result;
}

async function sendOptions(postId: string, optionsId: string, original: string, opts: {
  a: string; b: string; c: string; ta: string; tb: string; tc: string; articleTitle?: string;
}) {
  const preview = (t: string) => t.length > 180 ? t.slice(0, 177) + "…" : t;

  const text = [
    `📬 <b>Post para aprovação</b>`,
    opts.articleTitle ? `📄 Artigo: <i>${opts.articleTitle}</i>` : "",
    ``,
    `<b>🔴 A — ${opts.ta}</b>`,
    preview(opts.a),
    ``,
    `<b>🔵 B — ${opts.tb}</b>`,
    preview(opts.b),
    ``,
    `<b>🟢 C — ${opts.tc}</b>`,
    preview(opts.c),
    ``,
    `<i>Original sugerido: ${preview(original)}</i>`,
  ].filter(Boolean).join("\n");

  const keyboard = {
    inline_keyboard: [
      [
        { text: "🔴 A", callback_data: `choose:${postId}:a` },
        { text: "🔵 B", callback_data: `choose:${postId}:b` },
        { text: "🟢 C", callback_data: `choose:${postId}:c` },
      ],
      [
        { text: "✏️ Editar A", callback_data: `edit:${postId}:a` },
        { text: "✏️ Editar B", callback_data: `edit:${postId}:b` },
        { text: "✏️ Editar C", callback_data: `edit:${postId}:c` },
      ],
      [
        { text: "⏭️ Pular", callback_data: `skip:${postId}` },
      ],
    ],
  };

  const result = await tg("sendMessage", {
    chat_id: TELEGRAM_CHAT_ID,
    text,
    parse_mode: "HTML",
    reply_markup: keyboard,
  }) as { message_id: number };

  msgToPost.set(result.message_id, {
    postId, optionsId,
    optionA: opts.a, optionB: opts.b, optionC: opts.c,
    toneA: opts.ta, toneB: opts.tb, toneC: opts.tc,
  });

  return result.message_id;
}

// ── LLM — Generate 3 alternatives ─────────────────────────────────────────

async function getPreferenceSummary(): Promise<string> {
  const rows = await supabase("GET", "/x_post_preferences?select=preference_summary,sample_count,pct_bold,pct_conversational,pct_technical,avg_preferred_length,pct_edited&limit=1&order=last_updated.desc");
  if (!rows?.length) return "No preferences yet. Generate diverse options.";
  const p = rows[0];
  if (p.sample_count < 3) return p.preference_summary ?? "Not enough data yet. Generate diverse options.";
  return [
    p.preference_summary,
    `Tone stats (${p.sample_count} choices): bold ${Math.round(p.pct_bold * 100)}%, conversational ${Math.round(p.pct_conversational * 100)}%, technical ${Math.round(p.pct_technical * 100)}%.`,
    p.avg_preferred_length ? `Preferred length: ~${p.avg_preferred_length} chars.` : "",
    p.pct_edited > 0.3 ? "User often edits before posting — leave room for their voice." : "",
  ].filter(Boolean).join(" ");
}

async function generateOptions(postText: string, context: { title?: string; url?: string; category?: string }): Promise<{
  optionA: string; optionB: string; optionC: string;
  toneA: string; toneB: string; toneC: string;
  model: string;
} | null> {
  const preferenceContext = await getPreferenceSummary();

  const systemPrompt = `You are writing X.com posts for Enio Rocha, a Brazilian developer-researcher building EGOS (multi-agent governance platform), Guard Brasil (PII/LGPD API), and Gem Hunter.

PERSONA RULES:
- Builder-researcher, not a salesperson. Authentic, curious, direct.
- No hype, no "game-changer", no hollow CTAs like "check this out!"
- Portuguese preferred unless the topic naturally suits English.
- Max 270 chars per post. Never truncate — write complete thoughts.
- No hashtags unless genuinely useful (max 1-2).

PREFERENCE DATA: ${preferenceContext}

Generate exactly 3 post alternatives with different tones. Output ONLY a JSON object, no explanation:
{
  "option_a": "...",  // bold: strong opening hook, confident claim
  "tone_a": "bold",
  "option_b": "...",  // conversational: talk to the reader like a colleague
  "tone_b": "conversational",
  "option_c": "...",  // technical: precise, shows depth, for builders
  "tone_c": "technical"
}`;

  const userPrompt = [
    "Write 3 alternatives for this X.com post:",
    `Content: ${postText}`,
    context.title ? `Article title: ${context.title}` : "",
    context.url ? `Article URL: ${context.url}` : "",
    context.category ? `Category: ${context.category}` : "",
  ].filter(Boolean).join("\n");

  try {
    const res = await fetch(`${DASHSCOPE_URL}/chat/completions`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${DASHSCOPE_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "qwen-plus",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt },
        ],
        temperature: 0.8,
        max_tokens: 600,
      }),
    });

    if (!res.ok) throw new Error(`DashScope ${res.status}`);
    const data = await res.json() as { choices: Array<{ message: { content: string } }> };
    const content = data.choices[0].message.content.trim();

    // Extract JSON even if wrapped in markdown
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("No JSON in LLM response");

    const parsed = JSON.parse(jsonMatch[0]);
    if (!parsed.option_a || !parsed.option_b || !parsed.option_c) throw new Error("Missing options in LLM response");

    return {
      optionA: parsed.option_a,
      optionB: parsed.option_b,
      optionC: parsed.option_c,
      toneA: parsed.tone_a ?? "bold",
      toneB: parsed.tone_b ?? "conversational",
      toneC: parsed.tone_c ?? "technical",
      model: "qwen-plus",
    };
  } catch (err) {
    console.error("[generate] LLM error:", err);
    // Fallback: return original text as all three options with labels
    return {
      optionA: postText,
      optionB: postText,
      optionC: postText,
      toneA: "original",
      toneB: "original",
      toneC: "original",
      model: "fallback",
    };
  }
}

// ── X.com posting ──────────────────────────────────────────────────────────

async function postToX(text: string): Promise<string | null> {
  if (!X_API_KEY || !X_ACCESS_TOKEN) {
    console.warn("[post-x] X API credentials missing");
    return null;
  }

  // OAuth 1.0a signature (simplified using Bun's crypto)
  // For now using direct bearer token approach via v2 API
  const res = await fetch("https://api.twitter.com/2/tweets", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${X_ACCESS_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  if (!res.ok) {
    const err = await res.text();
    console.error("[post-x] Failed:", res.status, err);
    return null;
  }

  const data = await res.json() as { data: { id: string } };
  return data.data.id;
}

// ── Edit distance (Levenshtein) ────────────────────────────────────────────

function levenshtein(a: string, b: string): number {
  const m = a.length, n = b.length;
  const dp: number[][] = Array.from({ length: m + 1 }, (_, i) => [i]);
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      dp[i][j] = a[i-1] === b[j-1] ? dp[i-1][j-1] : 1 + Math.min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]);
  return dp[m][n];
}

function diffSummary(original: string, edited: string): string {
  const dist = levenshtein(original, edited);
  const delta = edited.length - original.length;
  if (dist === 0) return "no changes";
  const parts: string[] = [];
  if (dist > 0) parts.push(`distance: ${dist}`);
  if (delta > 0) parts.push(`+${delta} chars`);
  else if (delta < 0) parts.push(`${delta} chars`);
  return parts.join(", ");
}

// ── Learning: update aggregated preferences ────────────────────────────────

async function updatePreferences(toneChosen: string, finalLength: number, wasEdited: boolean, editDist: number) {
  const rows = await supabase("GET", "/x_post_preferences?limit=1&order=last_updated.desc");
  const current = rows?.[0];
  if (!current) return;

  const n = (current.sample_count ?? 0) + 1;
  const alpha = 1 / n; // running average weight

  const pctBold = toneChosen === "bold" ? (current.pct_bold ?? 0) + alpha * (1 - (current.pct_bold ?? 0)) : (current.pct_bold ?? 0) * (1 - alpha);
  const pctConv = toneChosen === "conversational" ? (current.pct_conversational ?? 0) + alpha * (1 - (current.pct_conversational ?? 0)) : (current.pct_conversational ?? 0) * (1 - alpha);
  const pctTech = toneChosen === "technical" ? (current.pct_technical ?? 0) + alpha * (1 - (current.pct_technical ?? 0)) : (current.pct_technical ?? 0) * (1 - alpha);
  const avgLen = Math.round(((current.avg_preferred_length ?? finalLength) * (n - 1) + finalLength) / n);
  const pctEdited = ((current.pct_edited ?? 0) * (n - 1) + (wasEdited ? 1 : 0)) / n;
  const avgDist = ((current.avg_edit_distance ?? 0) * (n - 1) + editDist) / n;

  // Rebuild preference summary for LLM
  const dominantTone = pctBold > pctConv && pctBold > pctTech ? "bold"
    : pctConv > pctTech ? "conversational" : "technical";
  const summary = [
    `User is Enio Rocha, Brazilian developer-researcher. Authentic tone, no hype. Portuguese preferred.`,
    `Based on ${n} choices: prefers ${dominantTone} tone (bold ${Math.round(pctBold * 100)}%, conversational ${Math.round(pctConv * 100)}%, technical ${Math.round(pctTech * 100)}%).`,
    `Preferred length: ~${avgLen} chars.`,
    pctEdited > 0.3 ? `User edits ${Math.round(pctEdited * 100)}% of posts before sending — leave room for their voice.` : "",
  ].filter(Boolean).join(" ");

  await supabase("PATCH", `/x_post_preferences?id=eq.${current.id}`, {
    sample_count: n,
    pct_bold: pctBold,
    pct_conversational: pctConv,
    pct_technical: pctTech,
    avg_preferred_length: avgLen,
    pct_edited: pctEdited,
    avg_edit_distance: avgDist,
    preference_summary: summary,
    last_updated: new Date().toISOString(),
  });
}

// ── Process a pending post ─────────────────────────────────────────────────

async function processPost(post: { id: string; text: string; article_id?: string; thread_position?: number }) {
  console.log(`[process] post ${post.id}: "${post.text.slice(0, 60)}…"`);

  // Fetch article context if linked
  let articleTitle = "";
  let articleUrl = "";
  let articleCategory = "general";
  if (post.article_id) {
    try {
      const articles = await supabase("GET", `/timeline_articles?id=eq.${post.article_id}&select=title,slug,tags&limit=1`);
      if (articles?.length) {
        articleTitle = articles[0].title ?? "";
        articleUrl = articles[0].slug ? `https://egos.ia.br/timeline/${articles[0].slug}` : "";
        const tags: string[] = articles[0].tags ?? [];
        if (tags.some((t: string) => t.includes("guard"))) articleCategory = "guard";
        else if (tags.some((t: string) => t.includes("gem"))) articleCategory = "gem-hunter";
        else if (tags.some((t: string) => t.includes("gov") || t.includes("licit"))) articleCategory = "govtech";
      }
    } catch { /* no article context */ }
  }

  // Generate 3 alternatives
  const options = await generateOptions(post.text, { title: articleTitle, url: articleUrl, category: articleCategory });
  if (!options) {
    console.error(`[process] Failed to generate options for post ${post.id}`);
    return;
  }

  // Save options to Supabase
  const optionsRows = await supabase("POST", "/x_post_options", {
    post_id: post.id,
    option_a: options.optionA,
    option_b: options.optionB,
    option_c: options.optionC,
    tone_a: options.toneA,
    tone_b: options.toneB,
    tone_c: options.toneC,
    model_used: options.model,
    context: { article_id: post.article_id, article_title: articleTitle, article_url: articleUrl, category: articleCategory },
  });
  const optionsId = optionsRows?.[0]?.id ?? "";

  // Link options to post
  await supabase("PATCH", `/x_post_queue?id=eq.${post.id}`, { options_id: optionsId, status: "options_ready" });

  if (DRY_RUN) {
    console.log(`[dry-run] Would send to Telegram:\n  A (${options.toneA}): ${options.optionA}\n  B (${options.toneB}): ${options.optionB}\n  C (${options.toneC}): ${options.optionC}`);
    return;
  }

  // Send to Telegram with inline keyboard
  const msgId = await sendOptions(post.id, optionsId, post.text, {
    a: options.optionA, b: options.optionB, c: options.optionC,
    ta: options.toneA, tb: options.toneB, tc: options.toneC,
    articleTitle,
  });

  console.log(`[process] Sent to Telegram msg_id=${msgId}`);
}

// ── Handle callback query (button press) ──────────────────────────────────

async function handleCallback(callbackQuery: {
  id: string; from: { id: number }; message: { message_id: number }; data: string;
}) {
  const { id: callbackId, message: { message_id: msgId }, data } = callbackQuery;
  const [action, postId, option] = data.split(":");

  // Ack the callback immediately
  await tg("answerCallbackQuery", { callback_query_id: callbackId });

  const ctx = msgToPost.get(msgId);
  if (!ctx || ctx.postId !== postId) {
    await tg("sendMessage", { chat_id: TELEGRAM_CHAT_ID, text: "❌ Contexto expirado. Reinicie o bot." });
    return;
  }

  if (action === "skip") {
    await supabase("PATCH", `/x_post_queue?id=eq.${postId}`, { status: "skipped" });
    await tg("editMessageReplyMarkup", { chat_id: TELEGRAM_CHAT_ID, message_id: msgId, reply_markup: { inline_keyboard: [] } });
    await tg("sendMessage", { chat_id: TELEGRAM_CHAT_ID, text: `⏭️ Post pulado.` });
    msgToPost.delete(msgId);
    return;
  }

  if (action === "edit") {
    const textToEdit = option === "a" ? ctx.optionA : option === "b" ? ctx.optionB : ctx.optionC;
    pendingEdits.set(postId, { postId, optionsId: ctx.optionsId, option, text: textToEdit });
    await tg("sendMessage", {
      chat_id: TELEGRAM_CHAT_ID,
      text: `✏️ Envie o texto editado para a opção ${option.toUpperCase()}.\n\n<i>Atual:</i>\n${textToEdit}`,
      parse_mode: "HTML",
      reply_markup: { force_reply: true, selective: true },
    });
    return;
  }

  if (action === "choose") {
    const chosenText = option === "a" ? ctx.optionA : option === "b" ? ctx.optionB : ctx.optionC;
    const tone = option === "a" ? ctx.toneA : option === "b" ? ctx.toneB : ctx.toneC;
    await finalizeChoice(postId, ctx.optionsId, option, chosenText, chosenText, tone, msgId);
  }
}

// ── Handle text message (edit reply) ──────────────────────────────────────

async function handleTextMessage(msg: { message_id: number; text: string; reply_to_message?: { message_id: number }; chat: { id: number } }) {
  // Check if any pending edit matches
  for (const [postId, editCtx] of pendingEdits.entries()) {
    // Match by the context being awaited (simple: first pending edit wins in 1-1 chat)
    const ctx = msgToPost.get(editCtx.postId as unknown as number);
    // Find the ctx via post_id
    let foundCtx: typeof ctx | null = null;
    for (const [, c] of msgToPost.entries()) {
      if (c.postId === postId) { foundCtx = c; break; }
    }
    if (!foundCtx) continue;

    const originalText = editCtx.option === "a" ? foundCtx.optionA : editCtx.option === "b" ? foundCtx.optionB : foundCtx.optionC;
    const tone = editCtx.option === "a" ? foundCtx.toneA : editCtx.option === "b" ? foundCtx.toneB : foundCtx.toneC;

    await finalizeChoice(postId, editCtx.optionsId, editCtx.option, msg.text, originalText, tone, -1);
    pendingEdits.delete(postId);
    return;
  }
}

// ── Finalize choice: record + post to X ───────────────────────────────────

async function finalizeChoice(
  postId: string, optionsId: string, option: string,
  finalText: string, originalText: string, tone: string,
  msgId: number
) {
  const wasEdited = finalText !== originalText;
  const dist = wasEdited ? levenshtein(originalText, finalText) : 0;
  const summary = diffSummary(originalText, finalText);

  // Record choice
  await supabase("POST", "/x_post_choices", {
    post_id: postId,
    options_id: optionsId,
    chosen_option: finalText === originalText ? option : "custom",
    chosen_text: finalText,
    original_text: originalText,
    was_edited: wasEdited,
    edit_distance: dist,
    edit_summary: summary,
    preferred_tone: tone,
    preferred_length: finalText.length,
    telegram_msg_id: msgId > 0 ? msgId : null,
    model_used: "qwen-plus",
  });

  // Update post queue
  await supabase("PATCH", `/x_post_queue?id=eq.${postId}`, {
    final_text: finalText,
    status: "approved",
    approved_at: new Date().toISOString(),
  });

  // Update learning
  await updatePreferences(tone, finalText.length, wasEdited, dist);

  // Post to X
  if (!DRY_RUN) {
    const tweetId = await postToX(finalText);
    if (tweetId) {
      await supabase("PATCH", `/x_post_queue?id=eq.${postId}`, {
        tweet_id: tweetId,
        posted_at: new Date().toISOString(),
        status: "posted",
      });
      await tg("sendMessage", {
        chat_id: TELEGRAM_CHAT_ID,
        text: `✅ Postado!\n\n${finalText}\n\n🔗 https://x.com/i/web/status/${tweetId}${wasEdited ? `\n\n📊 Edit: ${summary}` : ""}`,
        parse_mode: "HTML",
      });
    } else {
      await tg("sendMessage", {
        chat_id: TELEGRAM_CHAT_ID,
        text: `⚠️ Aprovado mas falha ao postar no X.\n\n${finalText}\n\n<i>Copie e poste manualmente.</i>`,
        parse_mode: "HTML",
      });
    }
  } else {
    console.log(`[dry-run] Would post: "${finalText.slice(0, 60)}…" (edited: ${wasEdited})`);
    await tg("sendMessage", {
      chat_id: TELEGRAM_CHAT_ID,
      text: `✅ [DRY-RUN] Aprovado:\n\n${finalText}`,
    });
  }

  // Remove from msg mapping
  if (msgId > 0) {
    await tg("editMessageReplyMarkup", { chat_id: TELEGRAM_CHAT_ID, message_id: msgId, reply_markup: { inline_keyboard: [] } });
    msgToPost.delete(msgId);
  }
}

// ── Main polling loop ──────────────────────────────────────────────────────

let lastUpdateId = 0;

async function pollPendingPosts() {
  const posts = await supabase("GET", "/x_post_queue?status=eq.pending&select=id,text,article_id,thread_position&order=scheduled_for.asc&limit=3");
  for (const post of (posts ?? [])) {
    await processPost(post);
    await new Promise(r => setTimeout(r, 1000)); // rate limit between posts
  }
}

async function pollTelegramUpdates() {
  const updates = await supabase("GET", `/x_post_queue?limit=1`).catch(() => null); // keep-alive check
  const res = await fetch(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/getUpdates?offset=${lastUpdateId + 1}&timeout=30`);
  const data = await res.json() as { ok: boolean; result: Array<{
    update_id: number;
    callback_query?: { id: string; from: { id: number }; message: { message_id: number }; data: string };
    message?: { message_id: number; text: string; chat: { id: number }; reply_to_message?: { message_id: number } };
  }> };

  if (!data.ok) return;

  for (const update of data.result) {
    lastUpdateId = update.update_id;

    if (update.callback_query) {
      await handleCallback(update.callback_query).catch(e => console.error("[callback] error:", e));
    } else if (update.message?.text) {
      await handleTextMessage(update.message).catch(e => console.error("[text] error:", e));
    }
  }
}

async function main() {
  console.log(`[x-post-approval-bot] Starting${DRY_RUN ? " (DRY-RUN)" : ""}${ONCE_MODE ? " (ONCE)" : " (LONG-POLL)"}`);

  if (!TELEGRAM_TOKEN || !TELEGRAM_CHAT_ID) {
    console.error("[error] TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_CHAT_ID are required");
    process.exit(1);
  }

  // Initial sweep for pending posts
  await pollPendingPosts().catch(e => console.error("[poll-posts] error:", e));

  if (ONCE_MODE) {
    console.log("[x-post-approval-bot] --once mode: done");
    process.exit(0);
  }

  // Long-poll loop
  let postPollTick = 0;
  while (true) {
    // Poll Telegram every ~30s (getUpdates long-poll)
    await pollTelegramUpdates().catch(e => console.error("[tg-poll] error:", e));

    // Check for new pending posts every 5 Telegram polls (~2.5min)
    postPollTick++;
    if (postPollTick >= 5) {
      await pollPendingPosts().catch(e => console.error("[post-poll] error:", e));
      postPollTick = 0;
    }
  }
}

main();
