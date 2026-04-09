#!/usr/bin/env bun
/**
 * LLM-MON-006 — Auto-Test Runner
 *
 * Queries Supabase llm_models for S-tier models not yet in llm_test_results,
 * runs the test suite for each, and sends Telegram summary.
 *
 * Called by llm-model-monitor.ts after detecting new S-tier models,
 * or run manually: bun scripts/llm-auto-test.ts [--dry] [--force <model-id>]
 *
 * Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN
 */

export {};

import { execSync } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const SUPABASE_URL = process.env.SUPABASE_URL ?? '';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? '';
const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? process.env.TELEGRAM_BOT_TOKEN_AI_AGENTS ?? '';
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID ?? '171767219';

const ARGS = process.argv.slice(2);
const isDry = ARGS.includes('--dry');
const forceModel = ARGS.find((_, i) => ARGS[i - 1] === '--force');

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));

// ── Supabase Queries ─────────────────────────────────────────────────────────
async function getUntestedSTierModels(): Promise<string[]> {
  // Get S-tier models from llm_models
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/llm_models?egos_recommendation=eq.S&select=model_id&order=discovery_date.desc&limit=20`,
    { headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY } }
  );
  if (!res.ok) return [];
  const models = await res.json() as Array<{ model_id: string }>;

  // Get already-tested models (last 7 days)
  const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
  const testRes = await fetch(
    `${SUPABASE_URL}/rest/v1/llm_test_results?tested_at=gte.${since}&select=model_id`,
    { headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY } }
  );
  const tested = testRes.ok ? (await testRes.json() as Array<{ model_id: string }>).map((t) => t.model_id) : [];
  const testedSet = new Set(tested);

  return models.map((m) => m.model_id).filter((id) => !testedSet.has(id));
}

async function getTestScore(modelId: string): Promise<{ score: number; passed: number; total: number } | null> {
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/llm_test_results?model_id=eq.${encodeURIComponent(modelId)}&order=tested_at.desc&limit=1&select=total_score,tests_passed,tests_total`,
    { headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY } }
  );
  if (!res.ok) return null;
  const rows = await res.json() as Array<{ total_score: number; tests_passed: number; tests_total: number }>;
  if (!rows[0]) return null;
  return { score: rows[0].total_score, passed: rows[0].tests_passed, total: rows[0].tests_total };
}

// ── Telegram ─────────────────────────────────────────────────────────────────
async function sendTelegram(msg: string): Promise<void> {
  if (!TELEGRAM_TOKEN) return;
  await fetch('https://api.telegram.org/bot' + TELEGRAM_TOKEN + '/sendMessage', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: TELEGRAM_CHAT_ID, text: msg, parse_mode: 'Markdown', disable_web_page_preview: true }),
  }).catch(() => {});
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function run(): Promise<void> {
  let models: string[];

  if (forceModel) {
    models = [forceModel];
    console.log(`[llm-auto-test] Force testing: ${forceModel}`);
  } else {
    if (!SUPABASE_URL || !SUPABASE_KEY) {
      console.error('[llm-auto-test] Missing Supabase credentials');
      process.exit(1);
    }
    models = await getUntestedSTierModels();
    console.log(`[llm-auto-test] Found ${models.length} untested S-tier model(s)`);
  }

  if (models.length === 0) {
    console.log('[llm-auto-test] Nothing to test — all S-tier models already tested this week');
    return;
  }

  const suiteScript = join(SCRIPT_DIR, 'llm-test-suite.ts');
  const summaries: string[] = [];

  for (const modelId of models) {
    console.log(`\n[llm-auto-test] Testing: ${modelId}`);

    if (isDry) {
      console.log('  [DRY] Would run: bun ' + suiteScript + ' --model ' + modelId);
      continue;
    }

    try {
      execSync(`bun ${suiteScript} --model "${modelId}"`, {
        env: process.env,
        stdio: 'inherit',
        timeout: 120_000,
      });

      const result = await getTestScore(modelId);
      if (result) {
        const grade = result.score >= 80 ? '🟢' : result.score >= 60 ? '🟡' : '🔴';
        const shortId = modelId.split('/').slice(-1)[0];
        summaries.push(`${grade} \`${shortId}\` — ${result.score}/100 (${result.passed}/${result.total} tests)`);
      }
    } catch (e) {
      console.error(`  ❌ Test failed: ${(e as Error).message}`);
      summaries.push(`❌ \`${modelId}\` — test suite error`);
    }
  }

  // Telegram summary
  if (summaries.length > 0 && TELEGRAM_TOKEN) {
    const msg = ['🧪 *LLM Auto-Test Results*', '', ...summaries, '', '#llm #egos #benchmark'].join('\n');
    await sendTelegram(msg);
  }

  console.log('\n[llm-auto-test] Done');
}

await run();
