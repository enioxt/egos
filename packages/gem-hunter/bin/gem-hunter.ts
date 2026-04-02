#!/usr/bin/env bun
/**
 * @egosbr/gem-hunter CLI
 *
 * Usage:
 *   npx @egosbr/gem-hunter                    # show findings
 *   npx @egosbr/gem-hunter hunt               # trigger a run
 *   npx @egosbr/gem-hunter hunt --quick       # quick run
 *   npx @egosbr/gem-hunter papers             # list scaffolded papers
 *   npx @egosbr/gem-hunter signals            # show world-model signals
 *   npx @egosbr/gem-hunter wait <jobId>       # wait for a job to finish
 *
 * Env:
 *   GEM_HUNTER_API_URL   (default: http://localhost:3097)
 *   GEM_HUNTER_API_KEY   (optional, for auth)
 */

import { GemHunter } from "../src/index.ts";

const args = process.argv.slice(2);
const cmd = args[0] ?? "findings";

const hunter = new GemHunter({
  apiUrl: process.env.GEM_HUNTER_API_URL ?? "http://localhost:3097",
  apiKey: process.env.GEM_HUNTER_API_KEY,
});

async function main() {
  switch (cmd) {
    case "hunt": {
      const quick = args.includes("--quick");
      const trackArg = args.find(a => a.startsWith("--track="));
      const track = trackArg ? trackArg.split("=")[1] : undefined;
      console.log("🔎 Triggering gem hunt...");
      const job = await hunter.hunt({ quick, track });
      console.log(`✅ Job started: ${job.jobId}`);
      console.log(`   Status: ${job.status}`);
      console.log(`   Started: ${job.startedAt}`);
      console.log(`\nRun: gem-hunter wait ${job.jobId}  — to wait for completion`);
      break;
    }

    case "wait": {
      const jobId = args[1];
      if (!jobId) { console.error("Usage: gem-hunter wait <jobId>"); process.exit(1); }
      console.log(`⏳ Waiting for job ${jobId}...`);
      const result = await hunter.waitForJob(jobId);
      console.log(`${result.status === "done" ? "✅" : "❌"} Job ${result.status}: ${jobId}`);
      break;
    }

    case "papers": {
      const { count, papers } = await hunter.papers();
      console.log(`📄 ${count} scaffolded paper(s):\n`);
      for (const p of papers) {
        console.log(`  [${p.score ?? "??"}/100] ${p.title}`);
        console.log(`         ${p.file}`);
      }
      break;
    }

    case "signals": {
      const { signals } = await hunter.signals();
      console.log(`📡 World-model signals (${signals.length}):\n`);
      for (const s of signals.slice(0, 10)) {
        console.log(`  [${s.score}/100] ${s.name}`);
        console.log(`         ${s.url}`);
        console.log(`         ${s.headline}`);
      }
      break;
    }

    case "findings":
    default: {
      const { latest, topSignals } = await hunter.findings();
      console.log(`📊 Latest run: ${latest.generatedAt}`);
      console.log(`   Total gems: ${latest.totalGems}`);
      console.log(`\n   By category:`);
      for (const [cat, count] of Object.entries(latest.byCategory)) {
        console.log(`     ${cat}: ${count}`);
      }
      if (topSignals.length > 0) {
        console.log(`\n🔥 Top signals:`);
        for (const s of topSignals.slice(0, 5)) {
          console.log(`  [${s.score}/100] ${s.name}`);
        }
      }
      break;
    }
  }
}

main().catch(err => {
  console.error("❌ Error:", err.message);
  process.exit(1);
});
