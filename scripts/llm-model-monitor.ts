#!/usr/bin/env bun
/**
 * LLM-MON-001..004 — LLM Model Monitor
 *
 * Polls OpenRouter /models every 6h, detects new/updated models,
 * researches S-tier candidates via Exa, stores in Supabase llm_models,
 * alerts via Telegram when a promising model is found.
 *
 * Usage:
 *   bun scripts/llm-model-monitor.ts --dry      # preview without writing
 *   bun scripts/llm-model-monitor.ts --exec     # fetch + store + alert
 *   bun scripts/llm-model-monitor.ts --report   # print current DB summary
 *
 * Env vars:
 *   OPENROUTER_API_KEY
 *   SUPABASE_URL
 *   SUPABASE_SERVICE_KEY
 *   EXA_API_KEY (optional — enables research)
 *   TELEGRAM_BOT_TOKEN
 *   TELEGRAM_ADMIN_CHAT_ID (or TELEGRAM_AUTHORIZED_USER_ID)
 */

export {};

// ── Config ─────────────────────────────────────────────────────────────────

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY ?? '';
const SUPABASE_URL = process.env.SUPABASE_URL ?? '';
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY ?? process.env.SUPABASE_SERVICE_ROLE_KEY ?? '';
const EXA_API_KEY = process.env.EXA_API_KEY ?? '';
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? process.env.TELEGRAM_BOT_TOKEN_AI_AGENTS ?? '';
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID ?? process.env.TELEGRAM_AUTHORIZED_USER_ID ?? '171767219';

// Models with context >= this threshold earn +1 tier point
const LONG_CONTEXT_THRESHOLD = 128_000;

// S-tier criteria: free OR cheap + large context OR known quality provider
const S_TIER_PROVIDERS = ['openai', 'anthropic', 'google', 'meta-llama', 'deepseek', 'qwen'];
const FREE_THRESHOLD_USD = 0; // free = $0/1M tokens

// ── Types ──────────────────────────────────────────────────────────────────

type OpenRouterModel = {
  id: string;
  name: string;
  context_length: number;
  pricing: { prompt: string; completion: string };
  architecture?: { modality?: string; tokenizer?: string };
  top_provider?: { context_length?: number };
};

type Recommendation = 'S' | 'A' | 'B' | 'C' | 'skip';

// ── Supabase helpers ───────────────────────────────────────────────────────

async function supabaseGet(path: string): Promise<unknown[]> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    headers: {
      'apikey': SUPABASE_SERVICE_KEY,
      'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
    },
  });
  if (!res.ok) throw new Error(`Supabase GET ${path} → ${res.status}`);
  return res.json();
}

async function supabaseUpsert(table: string, row: Record<string, unknown>): Promise<void> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}`, {
    method: 'POST',
    headers: {
      'apikey': SUPABASE_SERVICE_KEY,
      'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'resolution=merge-duplicates',
    },
    body: JSON.stringify(row),
  });
  if (!res.ok) throw new Error(`Supabase upsert ${table} → ${res.status}: ${await res.text()}`);
}

// ── OpenRouter ─────────────────────────────────────────────────────────────

async function fetchOpenRouterModels(): Promise<OpenRouterModel[]> {
  const res = await fetch('https://openrouter.ai/api/v1/models', {
    headers: { 'Authorization': `Bearer ${OPENROUTER_API_KEY}` },
  });
  if (!res.ok) throw new Error(`OpenRouter /models → ${res.status}`);
  const data = await res.json() as { data: OpenRouterModel[] };
  return data.data ?? [];
}

// ── Scoring ────────────────────────────────────────────────────────────────

function scoreModel(model: OpenRouterModel): Recommendation {
  const promptPrice = parseFloat(model.pricing.prompt ?? '999');
  const isFree = promptPrice === FREE_THRESHOLD_USD;
  const isLongContext = model.context_length >= LONG_CONTEXT_THRESHOLD;
  const provider = model.id.split('/')[0] ?? '';
  const isTrustedProvider = S_TIER_PROVIDERS.includes(provider);

  let score = 0;
  if (isFree) score += 3;
  if (isLongContext) score += 2;
  if (isTrustedProvider) score += 2;
  if (promptPrice < 0.5) score += 1; // cheap enough for agents
  if (model.context_length >= 1_000_000) score += 2; // 1M+ context

  if (score >= 7) return 'S';
  if (score >= 5) return 'A';
  if (score >= 3) return 'B';
  if (score >= 1) return 'C';
  return 'skip';
}

// ── Exa Research ──────────────────────────────────────────────────────────

async function researchModel(modelName: string): Promise<string> {
  if (!EXA_API_KEY) return 'Exa API key not configured';

  try {
    const query = `${modelName} LLM review benchmark performance 2025 2026`;
    const res = await fetch('https://api.exa.ai/search', {
      method: 'POST',
      headers: {
        'x-api-key': EXA_API_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        numResults: 3,
        useAutoprompt: true,
        startCrawlDate: '2024-01-01',
        contents: { text: { maxCharacters: 500 } },
      }),
    });
    if (!res.ok) return `Exa error: ${res.status}`;
    const data = await res.json() as { results: Array<{ title: string; text?: string; url: string }> };
    const results = data.results ?? [];
    if (results.length === 0) return 'No research found';
    return results
      .map(r => `[${r.title}](${r.url}): ${(r.text ?? '').substring(0, 200)}`)
      .join('\n\n');
  } catch (err) {
    return `Research failed: ${(err as Error).message}`;
  }
}

// ── Telegram ───────────────────────────────────────────────────────────────

async function sendTelegram(message: string): Promise<void> {
  if (!TELEGRAM_BOT_TOKEN) {
    console.log('[telegram] No token — would send:', message.substring(0, 100));
    return;
  }
  await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: TELEGRAM_CHAT_ID,
      text: message,
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
    }),
  });
}

// ── Main logic ─────────────────────────────────────────────────────────────

async function runMonitor(dry: boolean): Promise<void> {
  console.log('[llm-monitor] Fetching OpenRouter models...');
  const models = await fetchOpenRouterModels();
  console.log(`[llm-monitor] ${models.length} models fetched`);

  // Get known model IDs from Supabase
  const knownRows = await supabaseGet('llm_models?select=id,egos_recommendation,alerted') as Array<{
    id: string; egos_recommendation: string; alerted: boolean;
  }>;
  const knownIds = new Set(knownRows.map(r => r.id));
  const alertedIds = new Set(knownRows.filter(r => r.alerted).map(r => r.id));

  const newModels = models.filter(m => !knownIds.has(m.id));
  const allSrTier = models.filter(m => scoreModel(m) === 'S');
  const newSTier = allSrTier.filter(m => !alertedIds.has(m.id));

  console.log(`[llm-monitor] ${newModels.length} new models, ${newSTier.length} new S-tier`);

  if (dry) {
    console.log('\n[DRY] New models:');
    for (const m of newModels.slice(0, 5)) {
      const rec = scoreModel(m);
      const price = parseFloat(m.pricing.prompt);
      console.log(`  [${rec}] ${m.id} | ctx: ${(m.context_length/1000).toFixed(0)}k | $${price}/1M`);
    }
    console.log(`\n[DRY] S-tier models (${allSrTier.length} total):`);
    for (const m of allSrTier.slice(0, 10)) {
      const price = parseFloat(m.pricing.prompt);
      console.log(`  ⭐ ${m.id} | ctx: ${(m.context_length/1000).toFixed(0)}k | free: ${price === 0}`);
    }
    return;
  }

  // Upsert all models
  let upserted = 0;
  for (const model of models) {
    const rec = scoreModel(model);
    if (rec === 'skip') continue;

    const promptPrice = parseFloat(model.pricing.prompt ?? '0');
    const completionPrice = parseFloat(model.pricing.completion ?? '0');
    const provider = model.id.split('/')[0] ?? 'unknown';

    await supabaseUpsert('llm_models', {
      id: model.id,
      provider,
      name: model.name,
      context_length: model.context_length,
      is_free: promptPrice === 0,
      pricing_prompt_per_1m: isNaN(promptPrice) ? null : Math.min(promptPrice * 1_000_000, 9999.999999),
      pricing_completion_per_1m: isNaN(completionPrice) ? null : Math.min(completionPrice * 1_000_000, 9999.999999),
      egos_recommendation: rec,
      last_seen: new Date().toISOString(),
    });
    upserted++;
  }
  console.log(`[llm-monitor] ${upserted} models upserted to Supabase`);

  // Research and alert new S-tier models
  for (const model of newSTier.slice(0, 3)) { // max 3 alerts per run
    console.log(`[llm-monitor] Researching S-tier: ${model.id}...`);
    const research = await researchModel(model.name);

    await supabaseUpsert('llm_models', {
      id: model.id,
      provider: model.id.split('/')[0],
      name: model.name,
      context_length: model.context_length,
      is_free: parseFloat(model.pricing.prompt) === 0,
      exa_research_summary: research,
      alerted: true,
      egos_recommendation: 'S',
    });

    const price = parseFloat(model.pricing.prompt);
    const msg = [
      `⭐ *New S-tier LLM detected*`,
      ``,
      `*Model:* \`${model.id}\``,
      `*Context:* ${(model.context_length / 1000).toFixed(0)}k tokens`,
      `*Price:* ${price === 0 ? 'FREE' : `$${(price * 1_000_000).toFixed(2)}/1M`}`,
      ``,
      `*Research preview:*`,
      research.substring(0, 400),
      ``,
      `_EGOS LLM Monitor — check Supabase \`llm_models\` for full details_`,
    ].join('\n');

    await sendTelegram(msg);
    console.log(`  ✅ alerted: ${model.id}`);
  }

  console.log(`[llm-monitor] Done`);
}

async function printReport(): Promise<void> {
  const rows = await supabaseGet(
    'llm_models?select=id,provider,is_free,egos_recommendation,context_length,alerted&order=egos_recommendation.asc,context_length.desc&limit=50'
  ) as Array<{ id: string; provider: string; is_free: boolean; egos_recommendation: string; context_length: number; alerted: boolean }>;

  const byTier = { S: [] as string[], A: [] as string[], B: [] as string[], C: [] as string[] };
  for (const r of rows) {
    const tier = r.egos_recommendation as keyof typeof byTier;
    if (byTier[tier]) {
      byTier[tier].push(`${r.id} (ctx: ${(r.context_length/1000).toFixed(0)}k, ${r.is_free ? 'free' : 'paid'})`);
    }
  }

  console.log('\n=== EGOS LLM Model Monitor Report ===\n');
  for (const [tier, models] of Object.entries(byTier)) {
    console.log(`${tier}-tier (${models.length}):`);
    for (const m of models.slice(0, 10)) console.log(`  ${m}`);
    if (models.length > 10) console.log(`  ... +${models.length - 10} more`);
    console.log();
  }
}

// ── Entry point ────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const isDry = args.includes('--dry');
const isReport = args.includes('--report');

if (!OPENROUTER_API_KEY) {
  console.error('[llm-monitor] Missing OPENROUTER_API_KEY');
  process.exit(1);
}

if (isReport) {
  await printReport();
} else {
  await runMonitor(isDry);
}
