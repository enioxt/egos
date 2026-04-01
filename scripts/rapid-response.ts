#!/usr/bin/env bun
/**
 * 🚀 EGOS Rapid Response System
 *
 * Quando um trending topic tem match com nossas capacidades,
 * gera automaticamente:
 *   1. Thread X.com pronta para postar
 *   2. Showcase README limpo (não expõe repos sujos)
 *   3. Lista de repos/arquivos relevantes para linkar
 *
 * Usage:
 *   bun scripts/rapid-response.ts --topic "BRAID reasoning"
 *   bun scripts/rapid-response.ts --topic "PII LGPD" --post
 *   bun scripts/rapid-response.ts --scan  # check trending topics vs our capabilities
 */

import { writeFileSync } from "fs";
import { join } from "path";

const ROOT = "/home/enio/egos";
const TOPIC = process.argv.find(a => a.startsWith("--topic="))?.split("=").slice(1).join("=") ??
              process.argv[process.argv.indexOf("--topic") + 1];
const SCAN = process.argv.includes("--scan");
const POST = process.argv.includes("--post");

// ── EGOS Capability Map ───────────────────────────────────────────────────────
// Maps topics/keywords → what we have + links + 280-char pitch

interface EGOSCapability {
  id: string;
  keywords: string[];
  name: string;
  pitch: string;                  // ≤240 chars for X
  thread: string[];               // full thread (each item ≤280 chars)
  repos: { name: string; url: string; desc: string }[];
  clean_files: string[];          // files safe to share/link
}

const CAPABILITIES: EGOSCapability[] = [
  {
    id: "multi_agent_governance",
    keywords: ["multi-agent", "agent governance", "agent framework", "agent reliability", "compounding error"],
    name: "EGOS Multi-Agent Governance Kernel",
    pitch: "EGOS: open-source governance kernel for multi-agent AI systems. Frozen zones, pre-commit enforcement, 10 hooks, 25 skills, BRAID-compatible. github.com/enioxt/egos",
    thread: [
      "🧵 Built EGOS — an open-source governance kernel for multi-agent AI.\n\nProblem: Multi-agent chains compound errors. 95% accuracy per step → ~0% at 100 steps.\n\nOur fix isn't 'use a bigger model'. It's architecture.",
      "EGOS governance layer:\n• Frozen zones (critical files locked from agent drift)\n• Pre-commit enforcement (gitleaks + tsc + doc proliferation check)\n• 10 custom Claude Code hooks (frustration-detector, anti-compaction guard...)\n• BRAID-compatible /coordinator skill",
      "The executor pattern:\n1. Claude Code (Sonnet) generates a Guided Reasoning Diagram in Mermaid\n2. Cheap models (Qwen Flash/Hermes) execute nodes strictly\n3. Shadow auditor validates before handoff\n\n74-122× cheaper. Zero compounding errors.",
      "3 CCR autonomous jobs running 24/7:\n• Governance Drift Sentinel\n• Code Intel + Security Audit\n• Gem Hunter (discovers AI tools day-0)\n\nAll Haiku-powered (10× cheaper than Sonnet). Reports in docs/jobs/",
      "Open source. Built in Bun + TypeScript.\nAll governance rules are shareable (.guarani/ folder).\n\ngithub.com/enioxt/egos\n\nIf you're building multi-agent systems and tired of drift, check it out 👇",
    ],
    repos: [
      { name: "egos", url: "https://github.com/enioxt/egos", desc: "Governance kernel" },
    ],
    clean_files: [
      "docs/AI_COVERAGE_MAP.md",
      "docs/CAPABILITY_REGISTRY.md",
      "CLAUDE_CODE_INTEGRATIONS_MAP.md",
    ],
  },
  {
    id: "pii_lgpd",
    keywords: ["LGPD", "PII detection", "dados pessoais", "privacy", "compliance brazil", "CPF", "CNPJ"],
    name: "Guard Brasil — PII Detection LGPD",
    pitch: "Guard Brasil: open-source PII detection for Brazilian LGPD compliance. 15 patterns (CPF, RG, CNPJ...), 85.3% F1 score. npm install @egosbr/guard-brasil",
    thread: [
      "🧵 Built Guard Brasil — PII detection specifically for Brazil's LGPD.\n\nMost PII tools were built for GDPR/CCPA. None handled Brazilian-specific: CPF, RG, MASP, Electoral ID, CNH...",
      "15 patterns out of the box:\n• CPF (with validation algorithm)\n• RG (7 state formats)\n• CNPJ (with check digit)\n• CEP, CNH, Passaporte BR\n• Telefone, Email, Nome completo\n• MASP (funcional público SP)\n• Título de eleitor\n\nAll with regex + algorithmic validation.",
      "Benchmark vs alternatives:\n• Guard Brasil: 85.3% F1\n• Presidio (default): ~71% F1 on BR data\n• anonym.legal: closed source\n\nBetter recall on Brazilian CPF/RG patterns specifically.",
      "npm install @egosbr/guard-brasil\n\nOr use the REST API: guard.egos.ia.br/health\n\nPay-per-use: R$0.02/call. Free tier available.\n\ngithub.com/enioxt/egos",
    ],
    repos: [
      { name: "guard-brasil npm", url: "https://www.npmjs.com/package/@egosbr/guard-brasil", desc: "npm package" },
    ],
    clean_files: [
      "docs/products/GUARD_BRASIL.md",
      "packages/guard-brasil/src/pii-patterns.ts",
    ],
  },
  {
    id: "braid_serv",
    keywords: ["BRAID", "SERV reasoning", "bounded reasoning", "guided reasoning diagram", "OpenServ"],
    name: "BRAID-Compatible Execution in EGOS",
    pitch: "Implementing BRAID (arXiv 2512.15959) in EGOS: GRD generator via /coordinator skill + Hermes-3 as bounded executor. 74-122× cheaper. github.com/enioxt/egos",
    thread: [
      "🧵 BRAID (Bounded Reasoning for Autonomous Inference and Decisions) is the most important paper for multi-agent reliability I've read.\n\nHere's how we're implementing it in EGOS:",
      "The insight: LLMs don't reason, they predict tokens. 'Use a bigger model' just burns more tokens.\n\nBRAID fix: plan once with strong model → execute many times with cheap models following a strict graph.\n\nInput → GRD (Mermaid) → nano executors",
      "Our /coordinator skill is proto-BRAID:\n• Phase 1: Research (Explore agents, parallel)\n• Phase 2: Synthesis (Sonnet)\n• Phase 3: Implementation (Edit/Write, sequential)\n• Phase 4: Verification (tsc + tests)\n\nNext: add Mermaid GRD output in Phase 2.",
      "Hermes-3 (NousResearch) as the execution model:\n• nousresearch/hermes-3-llama-3.1-70b on OpenRouter\n• Best structured output + function calling at 70B\n• Perfect for strict node execution in GRD\n• ~10× cheaper than Sonnet for execution tasks",
      "Building this open-source in EGOS.\nIf you're working on BRAID or OpenHarness — let's compare notes.\n\ngithub.com/enioxt/egos",
    ],
    repos: [
      { name: "egos", url: "https://github.com/enioxt/egos", desc: "BRAID implementation" },
    ],
    clean_files: [
      "docs/knowledge/HARVEST.md",
      ".claude/commands/coordinator.md",
    ],
  },
  {
    id: "eagle_eye_procurement",
    keywords: ["licitação", "PNCP", "pregão", "compras públicas", "transparência pública", "govtech", "public procurement brazil"],
    name: "Eagle Eye — Brazilian Procurement Intelligence",
    pitch: "Eagle Eye: real-time Brazilian public procurement intelligence. 84 municipalities, Querido Diário + PNCP API (R$1tri/yr market). Open source. eagleeye.egos.ia.br",
    thread: [
      "🧵 Built Eagle Eye — OSINT for Brazilian public procurement (licitações).\n\nBrazil has R$1 trillion/year in public spending. It's all public data. But nobody aggregates it intelligently.",
      "Pipeline:\n1. Querido Diário API (official gazettes)\n2. Gemini Flash analyzes gazette text\n3. Extracts: object, value, deadline, winner\n4. Classifies: segment, modality, size tier\n5. Alerts via Telegram + email\n\n~$0.01/gazette analysis.",
      "Licitação taxonomy we built:\n• 9 segments (TI, SAUDE, OBRAS, SERVICOS...)\n• 12 modalities (PREGAO_ELETRONICO, DISPENSA...)\n• 4 size tiers by value (MICRO < 50K, GRANDE > 5M)\n• SRP flag (other agencies can adhere)\n• esfera (FEDERAL/ESTADUAL/MUNICIPAL)",
      "84 municipalities covered (all state capitals + tech hubs).\nDiscover-territories script: crosses IBGE + PNCP to rank uncovered cities by real procurement volume.\n\nOpen source. eagleeye.egos.ia.br",
    ],
    repos: [
      { name: "eagle-eye", url: "https://eagleeye.egos.ia.br", desc: "Live dashboard" },
    ],
    clean_files: [
      "docs/strategy/EAGLE_EYE_SSOT.md",
    ],
  },
];

// ── Score matching ────────────────────────────────────────────────────────────

function scoreMatch(topic: string, cap: EGOSCapability): number {
  const topicLower = topic.toLowerCase();
  let score = 0;
  for (const kw of cap.keywords) {
    if (topicLower.includes(kw.toLowerCase())) {
      score += kw.split(" ").length; // multi-word keywords score higher
    }
  }
  return score;
}

function findBestCapability(topic: string): EGOSCapability | null {
  const scored = CAPABILITIES.map(c => ({ cap: c, score: scoreMatch(topic, c) }))
    .filter(x => x.score > 0)
    .sort((a, b) => b.score - a.score);
  return scored[0]?.cap ?? null;
}

// ── Output Generator ──────────────────────────────────────────────────────────

function generateShowcaseREADME(cap: EGOSCapability, topic: string): string {
  return `# EGOS — ${cap.name}

> **Context:** Generated for rapid response to topic: "${topic}"
> **Date:** ${new Date().toISOString().slice(0, 10)}

## One-liner
${cap.pitch}

## Thread (X.com ready)
${cap.thread.map((t, i) => `**${i + 1}/${cap.thread.length}:**\n${t}`).join("\n\n")}

## Links
${cap.repos.map(r => `- **${r.name}**: ${r.url} — ${r.desc}`).join("\n")}

## Key Files to Share
${cap.clean_files.map(f => `- \`${f}\``).join("\n")}

---
*Auto-generated by EGOS Rapid Response System*
`;
}

// ── Main ──────────────────────────────────────────────────────────────────────

function main() {
  if (SCAN) {
    console.log("🔍 EGOS Capability Map — Topics We Can Respond To:\n");
    for (const cap of CAPABILITIES) {
      console.log(`  ✅ ${cap.name}`);
      console.log(`     Keywords: ${cap.keywords.join(", ")}`);
      console.log(`     Pitch: "${cap.pitch.slice(0, 80)}..."\n`);
    }
    console.log(`Total: ${CAPABILITIES.length} capabilities mapped`);
    console.log(`\nUsage: bun scripts/rapid-response.ts --topic "BRAID reasoning"`);
    return;
  }

  if (!TOPIC) {
    console.error("❌ Provide --topic or --scan");
    console.error("   Example: bun scripts/rapid-response.ts --topic 'BRAID multi-agent'");
    process.exit(1);
  }

  const cap = findBestCapability(TOPIC);
  if (!cap) {
    console.log(`⚠️  No matching capability for topic: "${TOPIC}"`);
    console.log("   Run --scan to see available capabilities");
    return;
  }

  console.log(`🚀 Rapid Response for: "${TOPIC}"`);
  console.log(`   Matched: ${cap.name} (score: ${scoreMatch(TOPIC, cap)})\n`);

  // Print thread
  console.log("📱 X Thread:\n");
  cap.thread.forEach((t, i) => {
    console.log(`[${i + 1}/${cap.thread.length}] ${t.length} chars`);
    console.log(t);
    console.log();
  });

  // Generate showcase README
  const readme = generateShowcaseREADME(cap, TOPIC);
  const outFile = `/tmp/egos-rapid-response-${Date.now()}.md`;
  writeFileSync(outFile, readme);
  console.log(`\n📄 Showcase README: ${outFile}`);
  console.log(`💡 Pitch: ${cap.pitch}`);

  if (POST) {
    console.log("\n⚠️  --post flag detected. To auto-post thread, pipe first tweet to x-reply-bot.");
    console.log("   Implement: bun scripts/x-reply-bot.ts --post-thread <file>");
  }
}

main();
