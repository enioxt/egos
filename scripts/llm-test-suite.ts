#!/usr/bin/env bun
/**
 * LLM-MON-005 — LLM Test Suite
 *
 * 5-category standardized test suite for evaluating LLMs detected by
 * llm-model-monitor.ts. Runs against any OpenRouter-compatible model.
 *
 * Categories:
 *   1. Coding     — generate + debug TypeScript
 *   2. Reasoning  — logic/math problems
 *   3. Long ctx   — 128k+ context retention
 *   4. Agentic    — tool use / structured output
 *   5. PT-BR      — Portuguese Brazilian quality (EGOS-specific)
 *
 * Usage:
 *   bun scripts/llm-test-suite.ts --model <model-id> [--dry] [--category coding]
 *   bun scripts/llm-test-suite.ts --model openai/gpt-4o --all
 *
 * Env: OPENROUTER_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
 */

export {};

// ── Config ──────────────────────────────────────────────────────────────────
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY ?? '';
const SUPABASE_URL = process.env.SUPABASE_URL ?? '';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? '';

const ARGS = process.argv.slice(2);
const modelArg = ARGS.find((_, i) => ARGS[i - 1] === '--model');
const categoryArg = ARGS.find((_, i) => ARGS[i - 1] === '--category');
const isDry = ARGS.includes('--dry');
const runAll = ARGS.includes('--all');

// ── Test Definitions ─────────────────────────────────────────────────────────
type TestResult = {
  category: string;
  test_name: string;
  passed: boolean;
  score: number; // 0-100
  latency_ms: number;
  tokens_used: number;
  output_preview: string;
  judge_notes: string;
};

type TestCase = {
  name: string;
  category: string;
  prompt: string;
  evaluate: (output: string, latency: number, tokens: number) => { passed: boolean; score: number; notes: string };
};

const TEST_CASES: TestCase[] = [
  // ── 1. CODING ───────────────────────────────────────────────────────────
  {
    name: 'TypeScript function generation',
    category: 'coding',
    prompt: 'Write a TypeScript function `groupBy<T>(array: T[], key: keyof T): Record<string, T[]>` with proper types. Just the function, no explanation.',
    evaluate: (output) => {
      const hasFunction = output.includes('function groupBy') || output.includes('const groupBy') || output.includes('=>');
      const hasGeneric = output.includes('<T>') || output.includes('T[]');
      const hasRecord = output.includes('Record<') || output.includes('{[');
      const hasBracket = output.includes('[key]') || output.includes('[item[key]]') || output.includes('reduce');
      const score = [hasFunction, hasGeneric, hasRecord, hasBracket].filter(Boolean).length * 25;
      return { passed: score >= 75, score, notes: `fn:${hasFunction} generic:${hasGeneric} record:${hasRecord} logic:${hasBracket}` };
    },
  },
  {
    name: 'Bug identification',
    category: 'coding',
    prompt: 'Identify the bug in this code and explain why it fails:\n```javascript\nasync function fetchAll(urls) {\n  const results = [];\n  for (const url of urls) {\n    results.push(fetch(url).then(r => r.json()));\n  }\n  return results;\n}\n```',
    evaluate: (output) => {
      const mentionsAwait = output.toLowerCase().includes('await');
      const mentionsPromise = output.toLowerCase().includes('promise') || output.toLowerCase().includes('pending');
      const correct = mentionsAwait && mentionsPromise;
      return { passed: correct, score: correct ? 100 : mentionsAwait || mentionsPromise ? 50 : 20, notes: `await:${mentionsAwait} promise:${mentionsPromise}` };
    },
  },

  // ── 2. REASONING ────────────────────────────────────────────────────────
  {
    name: 'Step-by-step math',
    category: 'reasoning',
    prompt: 'A factory produces 240 units per day. After a 15% efficiency improvement, how many units per week (7 days)? Show your work.',
    evaluate: (output) => {
      const has276 = output.includes('276');   // 240 * 1.15 = 276/day
      const has1932 = output.includes('1932'); // 276 * 7 = 1932/week
      return { passed: has276 && has1932, score: has276 && has1932 ? 100 : has276 || has1932 ? 50 : 0, notes: `daily:${has276} weekly:${has1932}` };
    },
  },
  {
    name: 'Logical deduction',
    category: 'reasoning',
    prompt: 'All developers who use TypeScript know about type inference. João knows about type inference. Does João use TypeScript? Answer with: Yes, No, or Cannot determine — then explain.',
    evaluate: (output) => {
      const cannotDetermine = output.toLowerCase().includes('cannot determine') || output.toLowerCase().includes('não é possível') || output.toLowerCase().includes('affirm');
      return { passed: cannotDetermine, score: cannotDetermine ? 100 : 0, notes: `correct_answer:${cannotDetermine}` };
    },
  },

  // ── 3. LONG CONTEXT ─────────────────────────────────────────────────────
  {
    name: 'Context retention',
    category: 'long_ctx',
    prompt: 'Remember this number: 7391. Now answer: What is the capital of France? Now recall: what number did I ask you to remember?',
    evaluate: (output) => {
      const remembersParis = output.toLowerCase().includes('paris');
      const remembers7391 = output.includes('7391');
      return { passed: remembersParis && remembers7391, score: [remembersParis, remembers7391].filter(Boolean).length * 50, notes: `paris:${remembersParis} 7391:${remembers7391}` };
    },
  },

  // ── 4. AGENTIC / STRUCTURED OUTPUT ──────────────────────────────────────
  {
    name: 'JSON structured output',
    category: 'agentic',
    prompt: 'Return a JSON object (no markdown, raw JSON only) with these fields: { "company": "FORJA", "sector": "metalurgia", "location": "Patos de Minas", "year_founded": 1985 }',
    evaluate: (output) => {
      const cleaned = output.trim().replace(/```json\n?|```\n?/g, '');
      try {
        const obj = JSON.parse(cleaned);
        const hasAll = obj.company && obj.sector && obj.location && obj.year_founded;
        return { passed: hasAll, score: hasAll ? 100 : 50, notes: 'valid JSON' };
      } catch {
        const hasJson = output.includes('{') && output.includes('"company"');
        return { passed: false, score: hasJson ? 30 : 0, notes: 'invalid JSON' };
      }
    },
  },
  {
    name: 'Tool use simulation',
    category: 'agentic',
    prompt: 'You have a tool called `search_kb(query: string)`. A user asks: "What is the ABNT NBR 6118 standard?" Write only the tool call you would make in JSON format: {"tool": "search_kb", "params": {"query": "..."}}',
    evaluate: (output) => {
      try {
        const cleaned = output.trim().replace(/```json\n?|```\n?/g, '').trim();
        const obj = JSON.parse(cleaned);
        const correct = obj.tool === 'search_kb' && obj.params?.query && obj.params.query.toLowerCase().includes('abnt') || obj.params?.query?.toLowerCase().includes('nbn') || obj.params?.query?.toLowerCase().includes('6118');
        return { passed: correct, score: correct ? 100 : 50, notes: `tool:${obj.tool} query:${obj.params?.query?.substring(0, 30)}` };
      } catch {
        return { passed: false, score: 0, notes: 'not valid JSON tool call' };
      }
    },
  },

  // ── 5. PT-BR QUALITY ────────────────────────────────────────────────────
  {
    name: 'PT-BR professional writing',
    category: 'ptbr',
    prompt: 'Escreva um parágrafo profissional de 3 frases explicando o que é inteligência artificial para um empresário da metalurgia em Minas Gerais. Tom formal mas acessível.',
    evaluate: (output) => {
      const isPtBr = /[àáâãäéêíóôõúç]/i.test(output);
      const isReasonableLength = output.length > 150 && output.length < 800;
      const hasContextualWords = /metal|fundição|processo|produção|empresa|industria|dados/i.test(output);
      const sentenceCount = (output.match(/\./g) ?? []).length;
      const hasThreeSentences = sentenceCount >= 2 && sentenceCount <= 5;
      const score = [isPtBr, isReasonableLength, hasContextualWords, hasThreeSentences].filter(Boolean).length * 25;
      return { passed: score >= 75, score, notes: `ptbr:${isPtBr} len:${output.length} ctx:${hasContextualWords} sentences:${sentenceCount}` };
    },
  },
  {
    name: 'PT-BR legal/LGPD terminology',
    category: 'ptbr',
    prompt: 'Em português, explique em 2 frases o que é dado pessoal sensível segundo a LGPD.',
    evaluate: (output) => {
      const isPtBr = /[àáâãäéêíóôõúç]/i.test(output);
      const mentionsLGPD = /lgpd|lei geral|proteção de dados/i.test(output);
      const mentionsSensitive = /saúde|biométrico|religião|origem racial|político|sexual|criminal|genétic/i.test(output);
      const score = [isPtBr, mentionsLGPD, mentionsSensitive].filter(Boolean).length * 34;
      return { passed: score >= 68, score, notes: `ptbr:${isPtBr} lgpd:${mentionsLGPD} examples:${mentionsSensitive}` };
    },
  },
];

// ── OpenRouter API ────────────────────────────────────────────────────────────
async function callModel(model: string, prompt: string): Promise<{ output: string; tokens: number; latency_ms: number }> {
  const start = Date.now();
  const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + OPENROUTER_API_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 500,
      temperature: 0.1,
    }),
    signal: AbortSignal.timeout(30000),
  });

  const latency_ms = Date.now() - start;
  if (!res.ok) throw new Error('OpenRouter ' + res.status + ': ' + await res.text());

  const data = await res.json() as {
    choices: Array<{ message: { content: string } }>;
    usage?: { total_tokens: number };
  };

  return {
    output: data.choices[0]?.message.content ?? '',
    tokens: data.usage?.total_tokens ?? 0,
    latency_ms,
  };
}

// ── Supabase Store ────────────────────────────────────────────────────────────
async function storeResults(model: string, results: TestResult[]): Promise<void> {
  const totalScore = Math.round(results.reduce((s, r) => s + r.score, 0) / results.length);
  const passed = results.filter((r) => r.passed).length;

  await fetch(SUPABASE_URL + '/rest/v1/llm_test_results', {
    method: 'POST',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model_id: model,
      total_score: totalScore,
      tests_passed: passed,
      tests_total: results.length,
      results_json: results,
      tested_at: new Date().toISOString(),
    }),
  }).catch(() => {}); // non-blocking
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function runSuite(model: string): Promise<void> {
  const tests = categoryArg
    ? TEST_CASES.filter((t) => t.category === categoryArg)
    : TEST_CASES;

  console.log(`\n[llm-test-suite] Model: ${model} | Tests: ${tests.length}${isDry ? ' [DRY]' : ''}\n`);

  const results: TestResult[] = [];

  for (const test of tests) {
    process.stdout.write(`  [${test.category}] ${test.name}... `);

    if (isDry) {
      console.log('(skipped — dry mode)');
      continue;
    }

    try {
      const { output, tokens, latency_ms } = await callModel(model, test.prompt);
      const { passed, score, notes } = test.evaluate(output, latency_ms, tokens);

      const result: TestResult = {
        category: test.category,
        test_name: test.name,
        passed,
        score,
        latency_ms,
        tokens_used: tokens,
        output_preview: output.substring(0, 100).replace(/\n/g, ' '),
        judge_notes: notes,
      };

      results.push(result);
      console.log(`${passed ? '✅' : '❌'} ${score}/100 (${latency_ms}ms)`);
    } catch (e) {
      console.log(`💥 ERROR: ${(e as Error).message}`);
      results.push({
        category: test.category,
        test_name: test.name,
        passed: false,
        score: 0,
        latency_ms: 0,
        tokens_used: 0,
        output_preview: 'ERROR: ' + (e as Error).message,
        judge_notes: 'exception',
      });
    }
  }

  // Summary
  if (results.length > 0) {
    const avgScore = Math.round(results.reduce((s, r) => s + r.score, 0) / results.length);
    const passed = results.filter((r) => r.passed).length;
    console.log(`\n── Summary: ${model} ──`);
    console.log(`  Passed: ${passed}/${results.length} | Avg score: ${avgScore}/100`);

    const byCategory = results.reduce((acc, r) => {
      if (!acc[r.category]) acc[r.category] = [];
      acc[r.category].push(r.score);
      return acc;
    }, {} as Record<string, number[]>);

    for (const [cat, scores] of Object.entries(byCategory)) {
      const avg = Math.round(scores.reduce((s, n) => s + n, 0) / scores.length);
      console.log(`  ${cat.padEnd(12)} ${avg}/100`);
    }

    if (!isDry && SUPABASE_URL && SUPABASE_KEY) {
      await storeResults(model, results);
      console.log('\n  ✅ Results stored to Supabase llm_test_results');
    }
  }
}

// ── Entry ────────────────────────────────────────────────────────────────────
if (!modelArg) {
  console.error('Usage: bun scripts/llm-test-suite.ts --model <model-id> [--category <cat>] [--dry]');
  console.error('Categories:', [...new Set(TEST_CASES.map((t) => t.category))].join(', '));
  process.exit(1);
}

if (!OPENROUTER_API_KEY && !isDry) {
  console.error('[llm-test-suite] Missing OPENROUTER_API_KEY');
  process.exit(1);
}

await runSuite(modelArg);
