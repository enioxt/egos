/**
 * Framework Benchmarker Agent — EGOS-113
 *
 * Compares MASA against major agent/orchestration competitors using official docs pages.
 * Output focuses on what EGOS should adopt, test, or reject.
 *
 * Usage:
 *   bun agent:run framework_benchmarker --dry
 */

import { runAgent, printResult, type Finding } from '../runtime/runner';

interface Target {
  id: string;
  url: string;
  category: 'architecture' | 'orchestration' | 'agent-platform';
  must: RegExp[];
}

const TARGETS: Target[] = [
  {
    id: 'masa_framework',
    url: 'https://www.masa-framework.org/',
    category: 'architecture',
    must: [/Modular Agentic Semantic Architecture/i, /cognizability/i, /SKILL\.md/i],
  },
  {
    id: 'langgraph',
    url: 'https://docs.langchain.com/oss/python/langgraph/overview',
    category: 'orchestration',
    must: [/LangGraph/i, /agent/i],
  },
  {
    id: 'autogen',
    url: 'https://microsoft.github.io/autogen/stable/',
    category: 'agent-platform',
    must: [/AutoGen/i, /agent/i],
  },
  {
    id: 'semantic_kernel',
    url: 'https://learn.microsoft.com/en-us/semantic-kernel/overview/',
    category: 'orchestration',
    must: [/Semantic Kernel/i, /plugin|planner|agent/i],
  },
  {
    id: 'llamaindex',
    url: 'https://docs.llamaindex.ai/en/stable/',
    category: 'orchestration',
    must: [/LlamaIndex/i, /data|agent|workflow/i],
  },
];

function stripHtml(input: string): string {
  return input
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

async function fetchText(url: string): Promise<string> {
  const res = await fetch(url, { headers: { 'User-Agent': 'egos-framework-benchmarker' } });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} @ ${url}`);
  const html = await res.text();
  return stripHtml(html).slice(0, 200_000);
}

async function runBenchmark(): Promise<Finding[]> {
  const findings: Finding[] = [];
  let success = 0;

  for (const t of TARGETS) {
    try {
      const text = await fetchText(t.url);
      const hits = t.must.map((rx) => Number(rx.test(text))).reduce((a, b) => a + b, 0);

      findings.push({
        severity: hits >= 1 ? 'info' : 'warning',
        category: `benchmark:${t.id}`,
        message: `${t.id} fetched (${t.category}) with ${hits}/${t.must.length} expected signal hits`,
        suggestion: `Source: ${t.url}`,
      });
      success++;
    } catch (err: unknown) {
      findings.push({
        severity: 'warning',
        category: `benchmark:${t.id}`,
        message: `${t.id} fetch failed`,
        suggestion: err instanceof Error ? err.message : String(err),
      });
    }
  }

  findings.unshift({
    severity: 'info',
    category: 'benchmark:summary',
    message: `Framework benchmark completed: ${success}/${TARGETS.length} sources fetched`,
    suggestion: 'Use keep/drop policy: adopt portable patterns; avoid lock-in and unnecessary runtime complexity.',
  });

  findings.push({
    severity: 'info',
    category: 'benchmark:recommendation',
    message: 'MASA makes sense as architecture skill input (naming, layering, static traceability), but EGOS should pilot it in one leaf repo first instead of kernel-wide enforcement.',
    suggestion: 'Next: create controlled pilot with compliance checks, then compare drift and lead-time metrics against EGOS baseline.',
  });

  return findings;
}

const mode = process.argv.includes('--exec') ? 'execute' as const : 'dry_run' as const;
runAgent('framework_benchmarker', mode, runBenchmark).then((result) => {
  printResult(result);
  process.exit(result.success ? 0 : 1);
});
