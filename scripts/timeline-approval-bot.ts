#!/usr/bin/env bun
// 🤖 Timeline Approval Bot — TL-004
//
// Polls timeline_drafts WHERE status='pending' every 5 minutes,
// sends Telegram notifications with inline approval buttons,
// and handles callbacks to approve/reject drafts.
//
// Usage:
//   bun run scripts/timeline-approval-bot.ts          # run daemon
//   bun run scripts/timeline-approval-bot.ts --dry-run # list pending without sending

const DRY_RUN = process.argv.includes("--dry-run");

// ── Config ─────────────────────────────────────────────────────────────────

const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? "";
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID ?? "";

const POLL_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
const HQ_BASE_URL = "https://hq.egos.ia.br";

// Track which drafts we've already notified (in-memory, resets on restart)
const notifiedDraftIds = new Set<string>();
// Track last Telegram update offset for long polling
let telegramOffset = 0;

// ── Types ──────────────────────────────────────────────────────────────────

interface TimelineDraft {
  id: string;
  slug: string;
  title: string;
  summary: string;
  source_commits: string[];
  source_files: string[] | null;
  tags: string[] | null;
  status: string;
  llm_provider: string | null;
  llm_cost_usd: number | null;
  pii_check_passed: boolean | null;
  drift_check_passed: boolean | null;
  created_at: string | null;
  body_md: string;
}

interface TelegramUpdate {
  update_id: number;
  callback_query?: {
    id: string;
    from: { id: number; username?: string };
    message?: { message_id: number; chat: { id: number } };
    data: string;
  };
}

// ── Supabase helpers ───────────────────────────────────────────────────────

async function fetchPendingDrafts(): Promise<TimelineDraft[]> {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set");
  }

  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/timeline_drafts?status=eq.pending&order=created_at.asc`,
    {
      headers: {
        apikey: SUPABASE_SERVICE_KEY,
        Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
        "Content-Type": "application/json",
      },
      signal: AbortSignal.timeout(15000),
    }
  );

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Supabase query failed (${res.status}): ${err}`);
  }

  return (await res.json()) as TimelineDraft[];
}

async function updateDraftStatus(
  id: string,
  status: "approved" | "rejected",
  extra: Record<string, unknown> = {}
): Promise<void> {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set");
  }

  const body: Record<string, unknown> = { status, ...extra };
  if (status === "approved") {
    body.approved_at = new Date().toISOString();
    body.approved_by = "enio";
  }

  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/timeline_drafts?id=eq.${encodeURIComponent(id)}`,
    {
      method: "PATCH",
      headers: {
        apikey: SUPABASE_SERVICE_KEY,
        Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
        "Content-Type": "application/json",
        Prefer: "return=minimal",
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(15000),
    }
  );

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Supabase update failed (${res.status}): ${err}`);
  }
}

// ── Telegram helpers ───────────────────────────────────────────────────────

async function sendTelegramMessage(
  chatId: string | number,
  text: string,
  extra: Record<string, unknown> = {}
): Promise<number | null> {
  if (!TELEGRAM_BOT_TOKEN) return null;

  try {
    const truncated = text.length > 4000 ? text.slice(0, 3990) + "\n…" : text;
    const res = await fetch(
      `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: chatId,
          text: truncated,
          parse_mode: "HTML",
          disable_web_page_preview: true,
          ...extra,
        }),
        signal: AbortSignal.timeout(10000),
      }
    );

    if (!res.ok) {
      const err = await res.text();
      console.error(`❌ Telegram sendMessage error (${res.status}): ${err}`);
      return null;
    }

    const data = (await res.json()) as { result?: { message_id?: number } };
    return data.result?.message_id ?? null;
  } catch (err) {
    console.error(`❌ Telegram exception: ${err}`);
    return null;
  }
}

async function answerCallbackQuery(callbackQueryId: string, text: string): Promise<void> {
  if (!TELEGRAM_BOT_TOKEN) return;
  try {
    await fetch(
      `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/answerCallbackQuery`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ callback_query_id: callbackQueryId, text }),
        signal: AbortSignal.timeout(5000),
      }
    );
  } catch {
    // best-effort
  }
}

async function getUpdates(offset: number): Promise<TelegramUpdate[]> {
  if (!TELEGRAM_BOT_TOKEN) return [];
  try {
    const res = await fetch(
      `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates?offset=${offset}&limit=100&timeout=5`,
      { signal: AbortSignal.timeout(15000) }
    );
    const data = (await res.json()) as { result?: TelegramUpdate[] };
    return data.result ?? [];
  } catch {
    return [];
  }
}

// ── Format draft notification ──────────────────────────────────────────────

function formatDraftNotification(draft: TimelineDraft): string {
  const wordCount = draft.body_md.split(/\s+/).length;
  const summaryLen = draft.summary.length;
  const commits = draft.source_commits.join(" + ");
  const piiStatus = draft.pii_check_passed === true ? "✅" : "⚠️ unverified";
  const created = draft.created_at
    ? new Date(draft.created_at).toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" })
    : "—";

  return (
    `📝 <b>New article ready for review</b>\n\n` +
    `<b>Title:</b> ${escapeHtml(draft.title)}\n` +
    `<b>Summary</b> (${summaryLen} chars):\n${escapeHtml(draft.summary)}\n\n` +
    `<b>Source:</b> ${escapeHtml(commits)}\n` +
    `<b>Length:</b> ~${wordCount} words\n` +
    `<b>LLM:</b> ${draft.llm_provider ?? "unknown"} | Cost: $${(draft.llm_cost_usd ?? 0).toFixed(5)}\n` +
    `<b>PII:</b> ${piiStatus}\n` +
    `<b>Created:</b> ${created}\n` +
    `<b>ID:</b> <code>${draft.id}</code>`
  );
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function buildInlineKeyboard(draftId: string) {
  return {
    inline_keyboard: [
      [
        { text: "✅ Approve", callback_data: `tl_approve:${draftId}` },
        { text: "❌ Reject", callback_data: `tl_reject:${draftId}` },
      ],
      [
        { text: "✏️ Edit in HQ", callback_data: `tl_edit:${draftId}` },
      ],
    ],
  };
}

// ── Notify draft via Telegram ─────────────────────────────────────────────

async function notifyDraft(draft: TimelineDraft): Promise<boolean> {
  if (DRY_RUN) {
    console.log(`  [DRY-RUN] Would notify: ${draft.id} — ${draft.title.slice(0, 60)}`);
    return true;
  }

  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.warn("⚠️  Telegram not configured (TELEGRAM_BOT_TOKEN / TELEGRAM_ADMIN_CHAT_ID)");
    return false;
  }

  const text = formatDraftNotification(draft);
  const replyMarkup = buildInlineKeyboard(draft.id);

  const msgId = await sendTelegramMessage(TELEGRAM_CHAT_ID, text, {
    reply_markup: replyMarkup,
  });

  return msgId !== null;
}

// ── Poll cycle ─────────────────────────────────────────────────────────────

async function pollAndNotify(): Promise<void> {
  let drafts: TimelineDraft[];
  try {
    drafts = await fetchPendingDrafts();
  } catch (err) {
    console.error(`❌ Failed to fetch pending drafts: ${err}`);
    return;
  }

  if (drafts.length === 0) {
    console.log(`  No pending drafts.`);
    return;
  }

  console.log(`  Found ${drafts.length} pending draft(s)`);

  for (const draft of drafts) {
    if (notifiedDraftIds.has(draft.id)) {
      // Already notified this session
      continue;
    }

    const ok = await notifyDraft(draft);
    if (ok) {
      notifiedDraftIds.add(draft.id);
      console.log(`  ✅ Notified: ${draft.id} — ${draft.title.slice(0, 60)}`);
    } else {
      console.log(`  ⚠️  Failed to notify: ${draft.id}`);
    }
  }
}

// ── Handle Telegram callbacks ─────────────────────────────────────────────

async function processCallbacks(): Promise<void> {
  const updates = await getUpdates(telegramOffset);

  for (const update of updates) {
    telegramOffset = Math.max(telegramOffset, update.update_id + 1);

    if (!update.callback_query) continue;
    const { id: callbackId, data, from } = update.callback_query;
    const chatId = update.callback_query.message?.chat.id ?? TELEGRAM_CHAT_ID;

    const [action, draftId] = data.split(":") as [string, string];

    if (!action.startsWith("tl_") || !draftId) continue;

    const username = from.username ?? String(from.id);
    console.log(`  📩 Callback: ${action} on ${draftId} from @${username}`);

    if (DRY_RUN) {
      await answerCallbackQuery(callbackId, `[DRY-RUN] ${action} acknowledged`);
      continue;
    }

    try {
      switch (action) {
        case "tl_approve":
          await updateDraftStatus(draftId, "approved");
          await answerCallbackQuery(callbackId, "✅ Approved!");
          await sendTelegramMessage(
            chatId,
            `✅ <b>Draft approved</b>\nID: <code>${draftId}</code>\nApproved by @${username}`
          );
          // Remove from notified set so it can be re-notified if it somehow goes back to pending
          notifiedDraftIds.delete(draftId);
          console.log(`  ✅ Approved: ${draftId}`);
          break;

        case "tl_reject":
          await updateDraftStatus(draftId, "rejected", { rejected_reason: "manual" });
          await answerCallbackQuery(callbackId, "❌ Rejected.");
          await sendTelegramMessage(
            chatId,
            `❌ <b>Draft rejected</b>\nID: <code>${draftId}</code>`
          );
          notifiedDraftIds.delete(draftId);
          console.log(`  ❌ Rejected: ${draftId}`);
          break;

        case "tl_edit":
          await answerCallbackQuery(callbackId, "Opening HQ editor...");
          await sendTelegramMessage(
            chatId,
            `✏️ <b>Edit draft in HQ:</b>\n${HQ_BASE_URL}/timeline/pending/${draftId}`
          );
          console.log(`  ✏️  Edit link sent: ${draftId}`);
          break;

        default:
          await answerCallbackQuery(callbackId, "Unknown action");
      }
    } catch (err) {
      console.error(`  ❌ Error processing callback ${action}: ${err}`);
      await answerCallbackQuery(callbackId, "Error processing request");
    }
  }
}

// ── Main loop ──────────────────────────────────────────────────────────────

async function main() {
  console.log("🤖 Timeline Approval Bot — TL-004");
  console.log(`Mode: ${DRY_RUN ? "DRY-RUN (no DB updates, no Telegram sends)" : "LIVE"}`);

  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    console.error("❌ SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set");
    process.exit(1);
  }

  if (!DRY_RUN && (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID)) {
    console.error("❌ TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_CHAT_ID must be set for LIVE mode");
    process.exit(1);
  }

  if (DRY_RUN) {
    // In dry-run: just list pending drafts and exit
    console.log("\n📋 Pending drafts (dry-run):");
    try {
      const drafts = await fetchPendingDrafts();
      if (drafts.length === 0) {
        console.log("  No pending drafts found.");
      } else {
        for (const d of drafts) {
          const wordCount = d.body_md.split(/\s+/).length;
          console.log(`  • ${d.id}`);
          console.log(`    Title:   ${d.title}`);
          console.log(`    Summary: ${d.summary.slice(0, 80)}...`);
          console.log(`    Words:   ~${wordCount}`);
          console.log(`    PII:     ${d.pii_check_passed === true ? "✅" : "⚠️  unverified"}`);
          console.log(`    Created: ${d.created_at ?? "—"}`);
          console.log();
        }
      }
    } catch (err) {
      console.error(`❌ Failed to fetch drafts: ${err}`);
      process.exit(1);
    }
    console.log("✅ Dry-run complete.");
    return;
  }

  // LIVE: daemon loop
  console.log(`\nPoll interval: ${POLL_INTERVAL_MS / 1000}s`);
  console.log("Waiting for pending drafts and Telegram callbacks...\n");

  // Initial poll immediately
  console.log(`[${new Date().toISOString()}] Polling...`);
  await pollAndNotify();
  await processCallbacks();

  // Continuous loop
  while (true) {
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
    console.log(`[${new Date().toISOString()}] Polling...`);
    await pollAndNotify();
    await processCallbacks();
  }
}

main().catch((err) => {
  console.error("❌ Fatal error:", err);
  process.exit(1);
});

export {}; // make this a module — prevents global namespace collision with other scripts
