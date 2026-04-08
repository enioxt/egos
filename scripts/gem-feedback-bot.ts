/**
 * GH-093: Gem Hunter Feedback Bot
 * Long-polls Telegram for callback_query reactions to gem alerts.
 * Saves feedback to Supabase gem_feedback table.
 *
 * Usage:
 *   bun scripts/gem-feedback-bot.ts              # run once (process pending updates)
 *   bun scripts/gem-feedback-bot.ts --daemon     # keep polling continuously
 *
 * Callback data format (set by sendGemTelegramAlert in gem-hunter.ts):
 *   gf:{reaction}:{alert_id}
 *   e.g. gf:👍:a3f9e2c14d7b8e1a0f
 *
 * Alert index: /tmp/gem-alert-index.json
 *   { [alert_id]: { gem_url, gem_name, score, run_id } }
 */

import { readFileSync, existsSync, writeFileSync } from "fs";

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? "";
const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
const GEM_ALERT_INDEX_PATH = "/tmp/gem-alert-index.json";
const OFFSET_FILE = "/tmp/gem-feedback-bot-offset.txt";
const DAEMON = process.argv.includes("--daemon");
const POLL_INTERVAL_MS = 5_000;

if (!TELEGRAM_BOT_TOKEN) {
  console.error("[GemFeedbackBot] TELEGRAM_BOT_TOKEN not set — exiting");
  process.exit(1);
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function getSupabaseClient(): any {
  const { createClient } = require("@supabase/supabase-js");
  return createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
}
const supabase = getSupabaseClient();

type AlertEntry = { gem_url: string; gem_name: string; score: number; run_id: string };
type AlertIndex = Record<string, AlertEntry>;

function loadAlertIndex(): AlertIndex {
  if (!existsSync(GEM_ALERT_INDEX_PATH)) return {};
  try {
    return JSON.parse(readFileSync(GEM_ALERT_INDEX_PATH, "utf-8"));
  } catch {
    return {};
  }
}

function loadOffset(): number {
  if (!existsSync(OFFSET_FILE)) return 0;
  try {
    return parseInt(readFileSync(OFFSET_FILE, "utf-8").trim(), 10) || 0;
  } catch {
    return 0;
  }
}

function saveOffset(offset: number): void {
  try {
    writeFileSync(OFFSET_FILE, String(offset));
  } catch { /* non-critical */ }
}

async function tgCall(method: string, body: Record<string, unknown>): Promise<unknown> {
  const res = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

interface TgUpdate {
  update_id: number;
  callback_query?: {
    id: string;
    from: { id: number; username?: string };
    data: string;
    message?: { message_id: number; chat: { id: number } };
  };
}

async function processUpdate(update: TgUpdate, alertIndex: AlertIndex): Promise<void> {
  const cb = update.callback_query;
  if (!cb?.data?.startsWith("gf:")) return;

  const parts = cb.data.split(":");
  if (parts.length < 3) return;

  const reaction = parts[1];    // 👍 | 👎 | 🔍 | 💬
  const alertId = parts[2];     // 20-char md5 hex
  const validReactions = ["👍", "👎", "🔍", "💬"];
  if (!validReactions.includes(reaction)) return;

  const alertEntry = alertIndex[alertId];
  if (!alertEntry) {
    console.warn(`[GemFeedbackBot] Unknown alert_id: ${alertId}`);
    // Still acknowledge the callback to remove loading spinner
    await tgCall("answerCallbackQuery", { callback_query_id: cb.id, text: "⚠️ Alert not found in index" });
    return;
  }

  // Save to Supabase gem_feedback
  const { error } = await supabase.from("gem_feedback").insert({
    alert_id: alertId,
    gem_url: alertEntry.gem_url,
    gem_name: alertEntry.gem_name,
    run_id: alertEntry.run_id,
    reaction,
    score_at_alert: alertEntry.score,
    // comment: null (only set via follow-up message, not implemented in v1)
  });

  if (error) {
    console.error(`[GemFeedbackBot] Supabase insert error: ${error.message}`);
    await tgCall("answerCallbackQuery", { callback_query_id: cb.id, text: "❌ Failed to save feedback" });
    return;
  }

  const reactionLabels: Record<string, string> = {
    "👍": "Gem marked as valuable!",
    "👎": "Gem marked as noise",
    "🔍": "Gem flagged for research",
    "💬": "Gem flagged for comment",
  };

  console.log(`[GemFeedbackBot] ✅ Feedback saved: ${reaction} for ${alertEntry.gem_name} (${alertId})`);

  // Acknowledge callback (removes spinner from Telegram button)
  await tgCall("answerCallbackQuery", {
    callback_query_id: cb.id,
    text: reactionLabels[reaction] ?? "Feedback saved",
  });
}

async function pollOnce(): Promise<number> {
  const offset = loadOffset();
  const alertIndex = loadAlertIndex();

  const result = await tgCall("getUpdates", {
    offset,
    timeout: 10,
    allowed_updates: ["callback_query"],
  }) as { ok: boolean; result: TgUpdate[] };

  if (!result.ok || !Array.isArray(result.result)) return offset;

  let lastOffset = offset;
  for (const update of result.result) {
    await processUpdate(update, alertIndex);
    lastOffset = update.update_id + 1;
  }

  if (lastOffset !== offset) saveOffset(lastOffset);
  return lastOffset;
}

async function main(): Promise<void> {
  console.log(`[GemFeedbackBot] Starting (daemon=${DAEMON})`);

  if (DAEMON) {
    while (true) {
      try {
        await pollOnce();
      } catch (err) {
        console.error("[GemFeedbackBot] Poll error:", err);
      }
      await Bun.sleep(POLL_INTERVAL_MS);
    }
  } else {
    await pollOnce();
    console.log("[GemFeedbackBot] One-shot poll complete");
  }
}

main().catch((err) => {
  console.error("[GemFeedbackBot] Fatal:", err);
  process.exit(1);
});
