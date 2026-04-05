/**
 * EGOS Gateway — Main Server
 *
 * Central ingress for external channel webhooks (WhatsApp, Telegram, etc.)
 * Runs on Hono + Bun.
 *
 * Routes:
 *   GET  /health              — gateway health
 *   GET  /ui                  — Knowledge System visual dashboard
 *   GET  /knowledge/*         — Knowledge API (wiki pages + learnings)
 *   GET  /gem-hunter/*        — Gem Hunter API (discovery engine)
 *   POST /channels/whatsapp/* — Evolution API webhooks
 */

import { Hono } from "hono";
import { logger } from "hono/logger";
import { whatsapp } from "./channels/whatsapp.js";
import { knowledge } from "./channels/knowledge.js";
import { ui } from "./channels/ui.js";
import { gemHunter } from "./channels/gem-hunter-api.js";

const app = new Hono();
const PORT = Number(process.env.GATEWAY_PORT ?? 3000);

// ─── Middleware ────────────────────────────────────────────────────────────────

app.use("*", logger());

// ─── Routes ───────────────────────────────────────────────────────────────────

app.get("/health", (c) => {
  return c.json({
    service: "egos-gateway",
    version: "0.2.0",
    uptime: process.uptime(),
    channels: ["whatsapp", "knowledge", "gem-hunter"],
    ui: "/ui",
  });
});

app.route("/ui", ui);
app.route("/channels/whatsapp", whatsapp);
app.route("/knowledge", knowledge);
app.route("/gem-hunter", gemHunter);

// ─── Start ────────────────────────────────────────────────────────────────────

console.log(`[egos-gateway] Starting on port ${PORT}`);
console.log(`[egos-gateway] UI: http://localhost:${PORT}/ui`);
console.log(`[egos-gateway] Gem Hunter API: http://localhost:${PORT}/gem-hunter/product`);

export default {
  port: PORT,
  fetch: app.fetch,
};
