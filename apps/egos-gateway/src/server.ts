/**
 * EGOS Gateway — Main Server
 *
 * Central ingress for external channel webhooks (WhatsApp, Telegram, etc.)
 * Runs on Hono + Bun.
 *
 * Routes:
 *   GET  /health              — gateway health
 *   POST /channels/whatsapp/* — Evolution API webhooks
 */

import { Hono } from "hono";
import { logger } from "hono/logger";
import { whatsapp } from "./channels/whatsapp.js";
import { knowledge } from "./channels/knowledge.js";

const app = new Hono();
const PORT = Number(process.env.GATEWAY_PORT ?? 3000);

// ─── Middleware ────────────────────────────────────────────────────────────────

app.use("*", logger());

// ─── Routes ───────────────────────────────────────────────────────────────────

app.get("/health", (c) => {
  return c.json({
    service: "egos-gateway",
    version: "0.1.0",
    uptime: process.uptime(),
    channels: ["whatsapp", "knowledge"],
  });
});

app.route("/channels/whatsapp", whatsapp);
app.route("/knowledge", knowledge);

// ─── Start ────────────────────────────────────────────────────────────────────

console.log(`[egos-gateway] Starting on port ${PORT}`);

export default {
  port: PORT,
  fetch: app.fetch,
};
