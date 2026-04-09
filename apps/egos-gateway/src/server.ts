/**
 * EGOS Gateway — Main Server v0.3.0
 *
 * Central ingress for external channel webhooks and chatbot interactions.
 * Runs on Hono + Bun.
 *
 * Routes:
 *   GET  /health                — gateway health
 *   GET  /ui                    — Knowledge System visual dashboard
 *   GET  /knowledge/*           — Knowledge API (wiki pages + learnings)
 *   GET  /gem-hunter/*          — Gem Hunter API (discovery engine)
 *   POST /channels/whatsapp/*   — Evolution API webhooks → AI Orchestrator
 *   POST /telegram/webhook      — Telegram bot webhook (egosin_bot)
 *   GET  /telegram/health       — Telegram channel health
 *   POST /telegram/setup-webhook — Register Telegram webhook URL
 *   GET  /guard-brasil/health   — x402 channel health (free)
 *   POST /guard-brasil/inspect  — PII inspection ($0.001 USDC via x402)
 */

import { Hono } from "hono";
import { logger } from "hono/logger";
import { whatsapp } from "./channels/whatsapp.js";
import { knowledge } from "./channels/knowledge.js";
import { ui } from "./channels/ui.js";
import { gemHunter } from "./channels/gem-hunter-api.js";
import { telegram, startTelegramPolling } from "./channels/telegram.js";
import { guardBrasil } from "./channels/guard-brasil.js";
import { startHealthMonitor } from "./health-monitor.js";

const app = new Hono();
const PORT = Number(process.env.GATEWAY_PORT ?? 3000);

// ─── Middleware ────────────────────────────────────────────────────────────────

app.use("*", logger());

// ─── Routes ───────────────────────────────────────────────────────────────────

app.get("/health", (c) => {
  return c.json({
    service: "egos-gateway",
    version: "0.4.0",
    uptime: process.uptime(),
    channels: ["whatsapp", "telegram", "knowledge", "gem-hunter", "guard-brasil-x402"],
    ui: "/ui",
    docs: {
      whatsapp: "/channels/whatsapp/health",
      telegram: "/telegram/health",
      knowledge: "/knowledge/stats",
      "gem-hunter": "/gem-hunter/product",
      "guard-brasil": "/guard-brasil/health",
    },
  });
});

app.route("/ui", ui);
app.route("/channels/whatsapp", whatsapp);
app.route("/telegram", telegram);
app.route("/knowledge", knowledge);
app.route("/gem-hunter", gemHunter);
app.route("/guard-brasil", guardBrasil);

// ─── Start ────────────────────────────────────────────────────────────────────

console.log(`[egos-gateway] v0.4.0 — starting on port ${PORT}`);
console.log(`[egos-gateway] UI:          http://localhost:${PORT}/ui`);
console.log(`[egos-gateway] WhatsApp:    http://localhost:${PORT}/channels/whatsapp/health`);
console.log(`[egos-gateway] Telegram:    http://localhost:${PORT}/telegram/health`);
console.log(`[egos-gateway] Gem Hunter:  http://localhost:${PORT}/gem-hunter/health`);

// Start Telegram long-polling (runs in background)
// Switch to webhook when gateway is deployed to VPS:
//   curl -X POST http://localhost:3000/telegram/setup-webhook -d '{"webhookUrl":"https://gateway.egos.ia.br"}'
startTelegramPolling().catch(console.error);

// Start health monitor — alerts via Telegram when system health < 40% (START-009)
startHealthMonitor();

export default {
  port: PORT,
  fetch: app.fetch,
};
