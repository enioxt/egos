/**
 * EGOS Gateway — WhatsApp Channel (Evolution API)
 *
 * Handles MESSAGES_UPSERT webhooks from Evolution API,
 * parses commands from authorized sender, executes them,
 * and replies via Evolution API sendText.
 */

import { Hono } from "hono";

// ─── Config ───────────────────────────────────────────────────────────────────

const EVOLUTION_BASE = process.env.EVOLUTION_API_URL ?? "http://localhost:8080";
const EVOLUTION_KEY = process.env.EVOLUTION_API_KEY ?? "";
const INSTANCE = "forja-notifications";
const AUTHORIZED_NUMBER = "553492374363";
const GUARD_HEALTH_URL = "https://guard.egos.ia.br/health";
const AGENTS_JSON_PATH =
  process.env.AGENTS_JSON_PATH ?? "/home/enio/egos-lab/agents.json";

// Supabase connection (read-only queries via environment)
const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";

// ─── Evolution API helpers ────────────────────────────────────────────────────

async function sendText(to: string, text: string): Promise<void> {
  const url = `${EVOLUTION_BASE}/message/sendText/${INSTANCE}`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      apikey: EVOLUTION_KEY,
    },
    body: JSON.stringify({
      number: to,
      text,
    }),
  });
  if (!res.ok) {
    console.error(
      `[whatsapp] sendText failed: ${res.status} ${await res.text()}`
    );
  }
}

// ─── Command handlers ─────────────────────────────────────────────────────────

async function handleStatus(): Promise<string> {
  const lines: string[] = ["*EGOS System Status*\n"];

  // Guard Brasil health
  try {
    const res = await fetch(GUARD_HEALTH_URL, { signal: AbortSignal.timeout(5000) });
    const data = await res.json();
    lines.push(`Guard Brasil: ${res.ok ? "OK" : "DEGRADED"} (${JSON.stringify(data)})`);
  } catch (e) {
    lines.push(`Guard Brasil: UNREACHABLE (${(e as Error).message})`);
  }

  // Docker containers
  try {
    const proc = Bun.spawn(["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"], {
      stdout: "pipe",
      stderr: "pipe",
    });
    const output = await new Response(proc.stdout).text();
    const containers = output.trim();
    lines.push(`\nContainers:\n${containers || "(none running)"}`);
  } catch {
    lines.push("\nDocker: unavailable");
  }

  return lines.join("\n");
}

async function handleGems(): Promise<string> {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    return "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.";
  }

  try {
    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/gem_findings?order=created_at.desc&limit=5`,
      {
        headers: {
          apikey: SUPABASE_KEY,
          Authorization: `Bearer ${SUPABASE_KEY}`,
        },
      }
    );
    if (!res.ok) return `Supabase error: ${res.status}`;
    const gems = (await res.json()) as Array<{
      title?: string;
      source?: string;
      created_at?: string;
    }>;
    if (gems.length === 0) return "No gem findings found.";

    const lines = ["*Latest Gem Findings*\n"];
    for (const g of gems) {
      lines.push(`- ${g.title ?? "untitled"} (${g.source ?? "?"}) — ${g.created_at?.slice(0, 10) ?? "?"}`);
    }
    return lines.join("\n");
  } catch (e) {
    return `Gems fetch error: ${(e as Error).message}`;
  }
}

async function handleCosts(): Promise<string> {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    return "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.";
  }

  const today = new Date().toISOString().slice(0, 10);
  try {
    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/api_usage?select=model,tokens_in,tokens_out,cost_usd&date=eq.${today}`,
      {
        headers: {
          apikey: SUPABASE_KEY,
          Authorization: `Bearer ${SUPABASE_KEY}`,
        },
      }
    );
    if (!res.ok) return `Supabase error: ${res.status}`;
    const rows = (await res.json()) as Array<{
      model?: string;
      tokens_in?: number;
      tokens_out?: number;
      cost_usd?: number;
    }>;
    if (rows.length === 0) return `No cost data for ${today}.`;

    let totalCost = 0;
    const lines = [`*Costs for ${today}*\n`];
    for (const r of rows) {
      const cost = r.cost_usd ?? 0;
      totalCost += cost;
      lines.push(
        `- ${r.model ?? "?"}: $${cost.toFixed(4)} (${r.tokens_in ?? 0} in / ${r.tokens_out ?? 0} out)`
      );
    }
    lines.push(`\n*Total: $${totalCost.toFixed(4)}*`);
    return lines.join("\n");
  } catch (e) {
    return `Costs fetch error: ${(e as Error).message}`;
  }
}

async function handleAgents(): Promise<string> {
  try {
    const file = Bun.file(AGENTS_JSON_PATH);
    if (!(await file.exists())) {
      return `agents.json not found at ${AGENTS_JSON_PATH}`;
    }
    const data = (await file.json()) as Record<
      string,
      { status?: string; description?: string }
    >;
    const entries = Object.entries(data);
    if (entries.length === 0) return "No agents registered.";

    const lines = [`*Registered Agents (${entries.length})*\n`];
    for (const [id, info] of entries) {
      const status = info.status ?? "unknown";
      lines.push(`- ${id}: ${status} — ${info.description ?? ""}`);
    }
    return lines.join("\n");
  } catch (e) {
    return `Agents read error: ${(e as Error).message}`;
  }
}

// ─── Command router ───────────────────────────────────────────────────────────

const COMMANDS: Record<string, () => Promise<string>> = {
  status: handleStatus,
  gems: handleGems,
  costs: handleCosts,
  agents: handleAgents,
};

async function routeCommand(text: string): Promise<string> {
  const keyword = text.trim().toLowerCase().split(/\s+/)[0];
  const handler = COMMANDS[keyword];
  if (handler) return handler();
  return "Command not recognized. Try: status, gems, costs, agents";
}

// ─── Evolution API webhook types ──────────────────────────────────────────────

interface EvolutionWebhookPayload {
  event: string;
  instance: string;
  data: {
    key?: { remoteJid?: string; fromMe?: boolean };
    message?: { conversation?: string; extendedTextMessage?: { text?: string } };
    messageType?: string;
  };
}

// ─── Hono routes ──────────────────────────────────────────────────────────────

export const whatsapp = new Hono();

whatsapp.post("/webhook", async (c) => {
  const body = (await c.req.json()) as EvolutionWebhookPayload;

  // Only process MESSAGES_UPSERT
  if (body.event !== "MESSAGES_UPSERT") {
    return c.json({ ignored: true, reason: "not MESSAGES_UPSERT" });
  }

  const { data } = body;

  // Ignore messages sent by us
  if (data.key?.fromMe) {
    return c.json({ ignored: true, reason: "fromMe" });
  }

  // Extract sender number (strip @s.whatsapp.net)
  const remoteJid = data.key?.remoteJid ?? "";
  const senderNumber = remoteJid.replace("@s.whatsapp.net", "");

  // Only respond to authorized sender
  if (senderNumber !== AUTHORIZED_NUMBER) {
    console.warn(`[whatsapp] Unauthorized sender: ${senderNumber}`);
    return c.json({ ignored: true, reason: "unauthorized" });
  }

  // Extract message text
  const text =
    data.message?.conversation ??
    data.message?.extendedTextMessage?.text ??
    "";

  if (!text) {
    return c.json({ ignored: true, reason: "no text" });
  }

  console.log(`[whatsapp] Command from ${senderNumber}: ${text}`);

  // Route and respond
  const response = await routeCommand(text);
  await sendText(senderNumber, response);

  return c.json({ ok: true, command: text.trim().toLowerCase().split(/\s+/)[0] });
});

// Health check for the channel
whatsapp.get("/health", (c) => {
  return c.json({
    channel: "whatsapp",
    instance: INSTANCE,
    authorizedNumber: AUTHORIZED_NUMBER,
    evolutionBase: EVOLUTION_BASE,
  });
});
