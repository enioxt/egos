/**
 * EGOS Gateway — WhatsApp Channel v2 (Evolution API)
 *
 * Handles ALL message types from Evolution API:
 *   text, audio (+ Groq Whisper transcription), image (+ Qwen-VL vision),
 *   video, document, sticker
 *
 * Routes incoming messages to AI Orchestrator → tool calls → curated reply.
 * Restricted to AUTHORIZED_NUMBER only for security.
 *
 * Evolution API webhook events handled:
 *   MESSAGES_UPSERT — new message received
 */

import { Hono } from "hono";
import { orchestrate, type IncomingMessage, type MediaType } from "../orchestrator.js";

// ─── Config ───────────────────────────────────────────────────────────────────

const EVOLUTION_BASE = process.env.EVOLUTION_API_URL ?? "http://localhost:8080";
const EVOLUTION_KEY = process.env.EVOLUTION_API_KEY ?? "";
const INSTANCE = process.env.EVOLUTION_INSTANCE ?? "forja-notifications";
const AUTHORIZED_NUMBER = process.env.WA_AUTHORIZED_NUMBER ?? "553492374363";

// ─── Evolution API helpers ────────────────────────────────────────────────────

async function sendText(to: string, text: string): Promise<void> {
  const url = `${EVOLUTION_BASE}/message/sendText/${INSTANCE}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", apikey: EVOLUTION_KEY },
    body: JSON.stringify({ number: to, text }),
    signal: AbortSignal.timeout(10000),
  });
  if (!res.ok) {
    console.error(`[whatsapp] sendText failed: ${res.status} ${await res.text()}`);
  }
}

async function sendTyping(to: string): Promise<void> {
  // Simulate typing indicator (Evolution API presence update)
  try {
    await fetch(`${EVOLUTION_BASE}/chat/sendPresence/${INSTANCE}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", apikey: EVOLUTION_KEY },
      body: JSON.stringify({ number: to, presence: "composing", delay: 1000 }),
      signal: AbortSignal.timeout(3000),
    });
  } catch { /* non-critical */ }
}

/** Download media as base64 from Evolution API */
async function downloadMedia(message: EvolutionMessage): Promise<{ base64: string; mimetype: string } | null> {
  try {
    const url = `${EVOLUTION_BASE}/chat/getBase64FromMediaMessage/${INSTANCE}`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", apikey: EVOLUTION_KEY },
      body: JSON.stringify({ message }),
      signal: AbortSignal.timeout(30000),
    });
    if (!res.ok) return null;
    const data = await res.json() as { base64?: string; mimetype?: string };
    if (!data.base64 || !data.mimetype) return null;
    return { base64: data.base64, mimetype: data.mimetype };
  } catch (e) {
    console.error("[whatsapp] downloadMedia error:", e);
    return null;
  }
}

// ─── Evolution API message types ─────────────────────────────────────────────

interface EvolutionMessageKey {
  remoteJid?: string;
  fromMe?: boolean;
  id?: string;
}

interface EvolutionMessage {
  key?: EvolutionMessageKey;
  message?: {
    conversation?: string;
    extendedTextMessage?: { text?: string; contextInfo?: unknown };
    audioMessage?: { mimetype?: string; seconds?: number; ptt?: boolean };
    imageMessage?: { mimetype?: string; caption?: string };
    videoMessage?: { mimetype?: string; caption?: string; seconds?: number };
    documentMessage?: { mimetype?: string; fileName?: string; caption?: string };
    stickerMessage?: { mimetype?: string };
    reactionMessage?: { text?: string };
  };
  messageType?: string;
  messageTimestamp?: number;
}

interface EvolutionWebhookPayload {
  event: string;
  instance: string;
  data: EvolutionMessage;
}

// ─── Message parser ───────────────────────────────────────────────────────────

async function parseMessage(data: EvolutionMessage): Promise<IncomingMessage | null> {
  const remoteJid = data.key?.remoteJid ?? "";
  const senderNumber = remoteJid.replace("@s.whatsapp.net", "");
  const msgType = data.messageType ?? "";
  const msg = data.message ?? {};

  const base: Omit<IncomingMessage, "text" | "mediaType" | "mediaBase64" | "mediaMime" | "caption" | "fileName"> = {
    from: senderNumber,
    channel: "whatsapp",
  };

  // Text message
  if (msgType === "conversation" || msgType === "extendedTextMessage") {
    const text = msg.conversation ?? msg.extendedTextMessage?.text ?? "";
    if (!text) return null;
    return { ...base, text };
  }

  // Audio message (voice note or audio file)
  if (msgType === "audioMessage") {
    const mime = msg.audioMessage?.mimetype ?? "audio/ogg; codecs=opus";
    const media = await downloadMedia(data);
    if (!media) return { ...base, mediaType: "audio", mediaMime: mime, text: "[Áudio recebido mas falhou no download]" };
    return { ...base, mediaType: "audio", mediaBase64: media.base64, mediaMime: media.mimetype };
  }

  // Image message
  if (msgType === "imageMessage") {
    const mime = msg.imageMessage?.mimetype ?? "image/jpeg";
    const caption = msg.imageMessage?.caption;
    const media = await downloadMedia(data);
    if (!media) return { ...base, mediaType: "image", caption, text: `[Imagem recebida${caption ? `: "${caption}"` : ""} — falhou no download]` };
    return { ...base, mediaType: "image", mediaBase64: media.base64, mediaMime: media.mimetype, caption };
  }

  // Video message
  if (msgType === "videoMessage") {
    const caption = msg.videoMessage?.caption;
    return { ...base, mediaType: "video", caption };
  }

  // Document / file
  if (msgType === "documentMessage") {
    const fileName = msg.documentMessage?.fileName ?? "arquivo";
    const caption = msg.documentMessage?.caption;
    return { ...base, mediaType: "document", fileName, caption };
  }

  // Sticker
  if (msgType === "stickerMessage") {
    return { ...base, mediaType: "sticker" };
  }

  // Reaction
  if (msgType === "reactionMessage") {
    return null; // ignore reactions
  }

  // Unknown — log and ignore
  console.log(`[whatsapp] Unhandled messageType: ${msgType}`);
  return null;
}

// ─── Webhook handler ──────────────────────────────────────────────────────────

export const whatsapp = new Hono();

whatsapp.post("/webhook", async (c) => {
  let body: EvolutionWebhookPayload;
  try {
    body = await c.req.json() as EvolutionWebhookPayload;
  } catch {
    return c.json({ error: "Invalid JSON" }, 400);
  }

  // Only process MESSAGES_UPSERT
  if (body.event !== "MESSAGES_UPSERT") {
    return c.json({ ignored: true, reason: "not MESSAGES_UPSERT" });
  }

  const { data } = body;

  // Ignore our own messages
  if (data.key?.fromMe) {
    return c.json({ ignored: true, reason: "fromMe" });
  }

  const remoteJid = data.key?.remoteJid ?? "";
  const senderNumber = remoteJid.replace("@s.whatsapp.net", "");

  // Security: only authorized number
  if (senderNumber !== AUTHORIZED_NUMBER) {
    console.warn(`[whatsapp] Blocked unauthorized sender: ${senderNumber}`);
    return c.json({ ignored: true, reason: "unauthorized" });
  }

  const incoming = await parseMessage(data);
  if (!incoming) {
    return c.json({ ignored: true, reason: "unparseable or ignored message type" });
  }

  const msgType = data.messageType ?? "text";
  console.log(`[whatsapp] ${senderNumber} → ${msgType}: ${incoming.text?.slice(0, 50) ?? "[media]"}`);

  // Send typing indicator (non-blocking)
  sendTyping(senderNumber).catch(() => {});

  // Route to AI orchestrator
  const result = await orchestrate(incoming);

  // Send response (non-fatal if Evolution API is unreachable)
  try {
    await sendText(senderNumber, result.text);
  } catch (e) {
    console.error("[whatsapp] sendText failed (Evolution API unreachable?):", (e as Error).message);
  }

  if (result.toolsUsed?.length) {
    console.log(`[whatsapp] Tools used: ${result.toolsUsed.join(", ")}`);
  }

  return c.json({ ok: true, msgType, toolsUsed: result.toolsUsed ?? [] });
});

// Channel health
whatsapp.get("/health", (c) => {
  return c.json({
    channel: "whatsapp",
    version: "2.0.0",
    instance: INSTANCE,
    authorizedNumber: AUTHORIZED_NUMBER,
    evolutionBase: EVOLUTION_BASE,
    capabilities: ["text", "audio+transcription", "image+vision", "video", "document", "sticker"],
    orchestrator: "qwen-plus (DashScope)",
    transcription: "whisper-large-v3-turbo (Groq)",
  });
});
