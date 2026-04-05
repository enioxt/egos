/**
 * EGOS Gateway — Health Monitor (START-009)
 *
 * Polls system health every 5 minutes.
 * Sends Telegram alert when health score drops below 40%.
 *
 * Health score = average of weighted component checks:
 *   - Guard Brasil API  (30%)
 *   - Gateway itself    (25%)
 *   - Supabase          (25%)
 *   - Gem Hunter API    (20%)
 */

const BOT_TOKEN =
  process.env.TELEGRAM_BOT_TOKEN_AI_AGENTS ?? process.env.TELEGRAM_BOT_TOKEN ?? "";
const AUTHORIZED_CHAT_ID = Number(
  process.env.TELEGRAM_AUTHORIZED_USER_ID ?? process.env.TELEGRAM_ADMIN_CHAT_ID ?? "0"
);
const TELEGRAM_BASE = `https://api.telegram.org/bot${BOT_TOKEN}`;
const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";

const CHECK_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
const HEALTH_THRESHOLD = 40; // alert when below this

interface ComponentHealth {
  name: string;
  ok: boolean;
  latencyMs: number | null;
  detail?: string;
}

// Track last alert to avoid spam (min 15min between repeated alerts)
let lastAlertAt = 0;
const ALERT_COOLDOWN_MS = 15 * 60 * 1000;

async function pingUrl(url: string, timeoutMs = 5000): Promise<{ ok: boolean; latencyMs: number | null; detail?: string }> {
  try {
    const start = Date.now();
    const res = await fetch(url, { signal: AbortSignal.timeout(timeoutMs) });
    return { ok: res.ok, latencyMs: Date.now() - start };
  } catch (e) {
    return { ok: false, latencyMs: null, detail: String(e) };
  }
}

async function checkSupabase(): Promise<ComponentHealth> {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    return { name: "Supabase", ok: false, latencyMs: null, detail: "no credentials" };
  }
  try {
    const start = Date.now();
    const res = await fetch(`${SUPABASE_URL}/rest/v1/egos_agent_events?limit=1`, {
      headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}` },
      signal: AbortSignal.timeout(5000),
    });
    return { name: "Supabase", ok: res.ok, latencyMs: Date.now() - start };
  } catch (e) {
    return { name: "Supabase", ok: false, latencyMs: null, detail: String(e) };
  }
}

async function checkAllComponents(): Promise<ComponentHealth[]> {
  const [guard, gateway, gemHunter, supabase] = await Promise.all([
    pingUrl("https://guard.egos.ia.br/health").then(r => ({ name: "Guard Brasil", ...r })),
    pingUrl("https://gateway.egos.ia.br/health").then(r => ({ name: "EGOS Gateway", ...r })),
    pingUrl("https://gateway.egos.ia.br/gem-hunter/health").then(r => ({ name: "Gem Hunter", ...r })),
    checkSupabase(),
  ]);
  return [guard, gateway, gemHunter, supabase];
}

function computeScore(components: ComponentHealth[]): number {
  const weights: Record<string, number> = {
    "Guard Brasil": 30,
    "EGOS Gateway": 25,
    Supabase: 25,
    "Gem Hunter": 20,
  };
  let total = 0;
  let maxTotal = 0;
  for (const c of components) {
    const w = weights[c.name] ?? 10;
    maxTotal += w;
    if (c.ok) total += w;
  }
  return maxTotal > 0 ? Math.round((total / maxTotal) * 100) : 0;
}

async function sendTelegramAlert(text: string): Promise<void> {
  if (!BOT_TOKEN || !AUTHORIZED_CHAT_ID) return;
  try {
    await fetch(`${TELEGRAM_BASE}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: AUTHORIZED_CHAT_ID, text, parse_mode: "Markdown" }),
      signal: AbortSignal.timeout(8000),
    });
  } catch (e) {
    console.error("[health-monitor] sendTelegramAlert error:", e);
  }
}

function formatAlert(score: number, components: ComponentHealth[]): string {
  const statusLines = components
    .map(c => `${c.ok ? "✅" : "❌"} *${c.name}*${c.latencyMs ? ` (${c.latencyMs}ms)` : ""}${c.detail ? ` — ${c.detail}` : ""}`)
    .join("\n");

  return `🚨 *EGOS Health Alert*\n\nScore: *${score}/100* (abaixo do limiar de ${HEALTH_THRESHOLD})\n\n${statusLines}\n\n_${new Date().toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" })}_`;
}

async function runHealthCheck(): Promise<void> {
  try {
    const components = await checkAllComponents();
    const score = computeScore(components);

    const failed = components.filter(c => !c.ok).map(c => c.name);
    const logLine = `[health-monitor] score=${score} failed=[${failed.join(",")}]`;

    if (score < HEALTH_THRESHOLD) {
      console.warn(logLine);
      const now = Date.now();
      if (now - lastAlertAt > ALERT_COOLDOWN_MS) {
        lastAlertAt = now;
        await sendTelegramAlert(formatAlert(score, components));
        console.warn("[health-monitor] Telegram alert sent");
      } else {
        const cooldownLeft = Math.round((ALERT_COOLDOWN_MS - (now - lastAlertAt)) / 60000);
        console.warn(`[health-monitor] Alert suppressed (cooldown ${cooldownLeft}min remaining)`);
      }
    } else {
      console.log(logLine);
    }
  } catch (e) {
    console.error("[health-monitor] runHealthCheck error:", e);
  }
}

export function startHealthMonitor(): void {
  if (!BOT_TOKEN || !AUTHORIZED_CHAT_ID) {
    console.warn("[health-monitor] Skipped — TELEGRAM_BOT_TOKEN or TELEGRAM_AUTHORIZED_USER_ID not set");
    return;
  }

  console.log(`[health-monitor] Started — checking every ${CHECK_INTERVAL_MS / 60000}min, alert threshold=${HEALTH_THRESHOLD}%`);

  // Run immediately on start, then on interval
  runHealthCheck();
  setInterval(runHealthCheck, CHECK_INTERVAL_MS);
}
