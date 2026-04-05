/**
 * EGOS Gateway — Telegram Channel (egosin_bot)
 *
 * Handles messages from Telegram bot via:
 *   1. Webhook: POST /telegram/webhook (preferred in production)
 *   2. Long-polling: started via startTelegramPolling() (for local dev)
 *
 * Features: text, audio (Whisper), photos (Qwen-VL vision), documents
 * Security: restricted to AUTHORIZED_USER_ID only
 *
 * Bot: @egosin_bot
 * Token: TELEGRAM_BOT_TOKEN_AI_AGENTS env var
 */

import { Hono } from "hono";
import { orchestrate, transcribeAudio, describeImage, type IncomingMessage } from "../orchestrator.js";

// ─── Config ───────────────────────────────────────────────────────────────────

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN_AI_AGENTS ?? process.env.TELEGRAM_BOT_TOKEN ?? "";
const AUTHORIZED_USER_ID = Number(process.env.TELEGRAM_AUTHORIZED_USER_ID ?? process.env.TELEGRAM_ADMIN_CHAT_ID ?? "0");
const TELEGRAM_BASE = `https://api.telegram.org/bot${BOT_TOKEN}`;
const TELEGRAM_FILE_BASE = `https://api.telegram.org/file/bot${BOT_TOKEN}`;

// ─── Telegram API helpers ─────────────────────────────────────────────────────

async function sendMessage(chatId: number, text: string, parseMode: "Markdown" | "HTML" = "Markdown"): Promise<void> {
  if (!BOT_TOKEN) return;
  try {
    // Telegram Markdown has strict rules — escape problematic chars
    const safeText = parseMode === "Markdown"
      ? text.replace(/([_*[\]()~`>#+\-=|{}.!])/g, "\\$1")
      : text;
    const res = await fetch(`${TELEGRAM_BASE}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chatId, text: safeText, parse_mode: parseMode }),
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) {
      // Retry without parse_mode on failure
      await fetch(`${TELEGRAM_BASE}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: chatId, text }),
        signal: AbortSignal.timeout(10000),
      });
    }
  } catch (e) {
    console.error("[telegram] sendMessage error:", e);
  }
}

async function sendTypingAction(chatId: number): Promise<void> {
  if (!BOT_TOKEN) return;
  try {
    await fetch(`${TELEGRAM_BASE}/sendChatAction`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chatId, action: "typing" }),
      signal: AbortSignal.timeout(3000),
    });
  } catch { /* non-critical */ }
}

/** Download file from Telegram and return as base64 */
async function downloadTelegramFile(fileId: string): Promise<{ base64: string; mime: string; path: string } | null> {
  try {
    // Step 1: Get file path
    const infoRes = await fetch(`${TELEGRAM_BASE}/getFile?file_id=${fileId}`, {
      signal: AbortSignal.timeout(10000),
    });
    if (!infoRes.ok) return null;
    const info = await infoRes.json() as { ok: boolean; result?: { file_path?: string } };
    const filePath = info.result?.file_path;
    if (!filePath) return null;

    // Step 2: Download file
    const fileRes = await fetch(`${TELEGRAM_FILE_BASE}/${filePath}`, {
      signal: AbortSignal.timeout(60000),
    });
    if (!fileRes.ok) return null;

    const arrayBuffer = await fileRes.arrayBuffer();
    const bytes = new Uint8Array(arrayBuffer);
    let binary = "";
    for (const b of bytes) binary += String.fromCharCode(b);
    const base64 = btoa(binary);

    // Infer MIME from file extension
    const ext = filePath.split(".").pop()?.toLowerCase() ?? "";
    const mime = ext === "ogg" ? "audio/ogg"
      : ext === "mp3" ? "audio/mpeg"
      : ext === "mp4" ? "audio/mp4"
      : ext === "m4a" ? "audio/mp4"
      : ext === "jpg" || ext === "jpeg" ? "image/jpeg"
      : ext === "png" ? "image/png"
      : ext === "webp" ? "image/webp"
      : "application/octet-stream";

    return { base64, mime, path: filePath };
  } catch (e) {
    console.error("[telegram] downloadFile error:", e);
    return null;
  }
}

// ─── Telegram update types ────────────────────────────────────────────────────

interface TelegramUser {
  id: number;
  first_name?: string;
  username?: string;
}

interface TelegramMessage {
  message_id: number;
  from?: TelegramUser;
  chat: { id: number; type: string };
  date: number;
  text?: string;
  caption?: string;
  voice?: { file_id: string; duration: number; mime_type?: string };
  audio?: { file_id: string; duration: number; mime_type?: string; file_name?: string };
  photo?: Array<{ file_id: string; width: number; height: number }>;
  video?: { file_id: string; duration: number; mime_type?: string };
  document?: { file_id: string; file_name?: string; mime_type?: string };
  sticker?: { file_id: string; emoji?: string };
}

interface TelegramUpdate {
  update_id: number;
  message?: TelegramMessage;
  edited_message?: TelegramMessage;
}

// ─── Message processor ────────────────────────────────────────────────────────

async function processTelegramMessage(msg: TelegramMessage): Promise<void> {
  const chatId = msg.chat.id;
  const userId = msg.from?.id ?? 0;

  // Security: only authorized user
  if (AUTHORIZED_USER_ID === 0) {
    // Not configured yet — reveal ID to caller so they can set it in .env
    console.warn(`[telegram] SETUP NEEDED: first message from user ${userId} (@${msg.from?.username ?? "?"})`);
    await sendMessage(chatId,
      `🔧 *EGOS Bot — Setup Necessário*\n\nSeu Telegram ID: \`${userId}\`\n\nAdicione no \`.env\`:\n\`TELEGRAM_AUTHORIZED_USER_ID=${userId}\`\n\nReinicie o gateway para ativar o bloqueio de segurança.`
    );
    // Continue processing (owner is setting up)
  } else if (userId !== AUTHORIZED_USER_ID) {
    console.warn(`[telegram] Blocked unauthorized user: ${userId} (@${msg.from?.username ?? "?"})`);
    await sendMessage(chatId, "❌ Não autorizado. Este bot é privado.");
    return;
  }

  sendTypingAction(chatId).catch(() => {});

  let incoming: IncomingMessage = {
    from: String(userId),
    channel: "telegram",
  };

  // ── Text message ──
  if (msg.text) {
    // Handle slash commands with context
    const text = msg.text;
    if (text === "/start") {
      await sendMessage(chatId, `*EGOS Assistant* 🤖\n\nOlá! Sou o EGOS — seu assistente pessoal com acesso ao sistema completo.\n\n*Capacidades:*\n• Texto, áudio, imagens, arquivos\n• Buscar gems (repositórios/ferramentas)\n• Knowledge Base\n• Status dos sistemas\n• Custos de API\n\nEnvie qualquer mensagem!`);
      return;
    }
    if (text === "/status") {
      incoming.text = "Mostre o status completo do sistema EGOS";
    } else if (text === "/gems" || text.startsWith("/gems ")) {
      const query = text.replace("/gems", "").trim();
      incoming.text = query ? `Busque gems sobre: ${query}` : "Mostre os melhores gems recentes";
    } else if (text === "/wiki" || text.startsWith("/wiki ")) {
      const query = text.replace("/wiki", "").trim();
      incoming.text = query ? `Busque no Knowledge Base: ${query}` : "Mostre o índice do Knowledge Base";
    } else if (text === "/agents") {
      incoming.text = "Liste todos os agentes EGOS registrados";
    } else if (text === "/costs") {
      incoming.text = "Mostre os custos de API de hoje";
    } else if (text === "/help") {
      await sendMessage(chatId, `*EGOS Commands*\n\n/start — Boas-vindas\n/status — Status do sistema\n/gems [query] — Buscar gems\n/wiki [query] — Knowledge Base\n/agents — Listar agentes\n/costs — Custos de hoje\n\nOu envie mensagem livre, áudio ou imagem!`);
      return;
    } else {
      incoming.text = text;
    }
  }
  // ── Voice note ──
  else if (msg.voice) {
    const media = await downloadTelegramFile(msg.voice.file_id);
    if (media) {
      incoming = { ...incoming, mediaType: "audio", mediaBase64: media.base64, mediaMime: msg.voice.mime_type ?? media.mime };
    } else {
      incoming.text = "[Nota de voz recebida mas falhou no download]";
    }
  }
  // ── Audio file ──
  else if (msg.audio) {
    const media = await downloadTelegramFile(msg.audio.file_id);
    if (media) {
      incoming = { ...incoming, mediaType: "audio", mediaBase64: media.base64, mediaMime: msg.audio.mime_type ?? media.mime };
    } else {
      incoming.text = "[Arquivo de áudio recebido mas falhou no download]";
    }
  }
  // ── Photo ──
  else if (msg.photo && msg.photo.length > 0) {
    // Use largest photo
    const largest = msg.photo.sort((a, b) => b.width - a.width)[0];
    const media = await downloadTelegramFile(largest.file_id);
    if (media) {
      incoming = { ...incoming, mediaType: "image", mediaBase64: media.base64, mediaMime: media.mime, caption: msg.caption };
    } else {
      incoming.text = `[Foto recebida${msg.caption ? `: "${msg.caption}"` : ""} — falhou no download]`;
    }
  }
  // ── Document ──
  else if (msg.document) {
    incoming = { ...incoming, mediaType: "document", fileName: msg.document.file_name, caption: msg.caption };
  }
  // ── Video ──
  else if (msg.video) {
    incoming = { ...incoming, mediaType: "video", caption: msg.caption };
  }
  // ── Sticker ──
  else if (msg.sticker) {
    incoming = { ...incoming, mediaType: "sticker" };
  } else {
    return; // ignore other types
  }

  const result = await orchestrate(incoming);

  if (result.toolsUsed?.length) {
    console.log(`[telegram] Tools: ${result.toolsUsed.join(", ")}`);
  }

  await sendMessage(chatId, result.text);
}

// ─── Long polling (for local dev / VPS without public HTTPS) ─────────────────

let pollingActive = false;
let lastUpdateId = 0;

export async function startTelegramPolling(): Promise<void> {
  if (!BOT_TOKEN) {
    console.log("[telegram] Polling skipped — TELEGRAM_BOT_TOKEN_AI_AGENTS not set");
    return;
  }
  if (pollingActive) return;
  pollingActive = true;

  // Get bot info
  try {
    const me = await fetch(`${TELEGRAM_BASE}/getMe`).then((r) => r.json()) as { ok: boolean; result?: { username?: string } };
    console.log(`[telegram] Polling started — @${me.result?.username ?? "?"}`);
    if (AUTHORIZED_USER_ID === 0) {
      console.warn("[telegram] ⚠️  TELEGRAM_AUTHORIZED_USER_ID not set — bot will respond to anyone!");
    }
  } catch (e) {
    console.error("[telegram] getMe failed:", e);
    pollingActive = false;
    return;
  }

  const poll = async () => {
    if (!pollingActive) return;
    try {
      const url = `${TELEGRAM_BASE}/getUpdates?offset=${lastUpdateId + 1}&timeout=25&allowed_updates=["message"]`;
      const res = await fetch(url, { signal: AbortSignal.timeout(35000) });
      if (!res.ok) {
        await new Promise((r) => setTimeout(r, 5000));
        poll();
        return;
      }
      const data = await res.json() as { ok: boolean; result?: TelegramUpdate[] };
      const updates = data.result ?? [];

      for (const update of updates) {
        if (update.update_id > lastUpdateId) lastUpdateId = update.update_id;
        const msg = update.message ?? update.edited_message;
        if (msg) processTelegramMessage(msg).catch(console.error);
      }
    } catch (e) {
      if ((e as Error).name !== "AbortError") {
        console.error("[telegram] poll error:", e);
        await new Promise((r) => setTimeout(r, 5000));
      }
    }
    poll();
  };

  poll();
}

export function stopTelegramPolling(): void {
  pollingActive = false;
}

// ─── Webhook handler ──────────────────────────────────────────────────────────

export const telegram = new Hono();

telegram.post("/webhook", async (c) => {
  let update: TelegramUpdate;
  try {
    update = await c.req.json() as TelegramUpdate;
  } catch {
    return c.json({ error: "Invalid JSON" }, 400);
  }

  const msg = update.message ?? update.edited_message;
  if (msg) {
    processTelegramMessage(msg).catch(console.error);
  }

  return c.json({ ok: true });
});

telegram.get("/health", (c) => {
  return c.json({
    channel: "telegram",
    bot: "@egosin_bot",
    token_configured: !!BOT_TOKEN,
    authorized_user: AUTHORIZED_USER_ID !== 0 ? `${AUTHORIZED_USER_ID}` : "not set ⚠️",
    polling_active: pollingActive,
    capabilities: ["text", "voice+transcription", "photo+vision", "audio", "document"],
  });
});

// Register webhook URL with Telegram
telegram.post("/setup-webhook", async (c) => {
  const { webhookUrl } = await c.req.json() as { webhookUrl: string };
  if (!webhookUrl) return c.json({ error: "webhookUrl required" }, 400);

  const res = await fetch(`${TELEGRAM_BASE}/setWebhook?url=${encodeURIComponent(webhookUrl + "/telegram/webhook")}`, {
    signal: AbortSignal.timeout(10000),
  });
  const data = await res.json();
  return c.json(data);
});
