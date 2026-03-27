#!/usr/bin/env bun

/**
 * FASE 3: Progressive Agent Interligação
 *
 * Executes kernel agents progressively (1→2→...→6) and observes:
 * - Event bus correlations
 * - Shared findings across agents
 * - Cross-agent insights
 *
 * Usage: bun scripts/agent-chain-runner.ts [--dry|--exec]
 */

import { spawn } from "bun";
import { readFileSync, appendFileSync } from "fs";
import { existsSync, mkdirSync } from "fs";
import path from "path";

const AGENTS = [
  "dep_auditor",
  "archaeology_digger",
  "chatbot_compliance_checker",
  "dead_code_detector",
  "capability_drift_checker",
  "context_tracker",
];

interface ChainEvent {
  step: number;
  agent: string;
  timestamp: string;
  correlation: string;
  findings: number;
  duration: number;
  events: string[];
  sharedEvents?: string[];
}

const mode = Bun.argv[2] || "--dry";
const outputDir = "./docs/agent-tests";
const chainLogFile = `${outputDir}/20260327_CHAIN_RUN.json`;
const correlationMap: Map<string, string[]> = new Map();
let allEvents: ChainEvent[] = [];

async function runAgent(agentId: string, step: number): Promise<ChainEvent> {
  console.log(`\n[Step ${step}] Running ${agentId}...`);

  const proc = spawn(["bun", "agent:run", agentId, mode], {
    cwd: process.cwd(),
    stdout: "pipe",
    stderr: "pipe",
  });

  const output = await new Response(proc.stdout).text();
  const startTime = Date.now();

  // Parse output for correlation ID and findings count
  const correlationMatch = output.match(/\[([a-f0-9]+)\]/);
  const correlation = correlationMatch ? correlationMatch[1] : `unknown-${step}`;

  const durMatch = output.match(/Duration:\s*(\d+)ms/);
  const duration = durMatch ? parseInt(durMatch[1]) : 0;

  const findingsMatch = output.match(/Findings?\s*\((\d+)\)/);
  const findings = findingsMatch ? parseInt(findingsMatch[1]) : 0;

  // Extract event types from output
  const events = extractEventTypes(output);

  const chainEvent: ChainEvent = {
    step,
    agent: agentId,
    timestamp: new Date().toISOString(),
    correlation,
    findings,
    duration,
    events,
    sharedEvents: findSharedEvents(agentId, events, correlationMap),
  };

  // Track correlations for later analysis
  if (!correlationMap.has(correlation)) {
    correlationMap.set(correlation, events);
  } else {
    const existing = correlationMap.get(correlation) || [];
    correlationMap.set(correlation, [...new Set([...existing, ...events])]);
  }

  allEvents.push(chainEvent);

  console.log(
    `  ✅ ${agentId}: ${findings} findings, ${duration}ms, ${events.length} event types`
  );

  if (chainEvent.sharedEvents && chainEvent.sharedEvents.length > 0) {
    console.log(
      `  🔗 Shared events: ${chainEvent.sharedEvents.join(", ")}`
    );
  }

  return chainEvent;
}

function extractEventTypes(output: string): string[] {
  const events: Set<string> = new Set();

  // Parse agent:event:type patterns
  const eventRegex = /agent:(\w+):(\w+)/g;
  let match;
  while ((match = eventRegex.exec(output)) !== null) {
    events.add(`${match[1]}:${match[2]}`);
  }

  return Array.from(events);
}

function findSharedEvents(
  currentAgent: string,
  currentEvents: string[],
  correlationMap: Map<string, string[]>
): string[] {
  const shared: Set<string> = new Set();

  for (const [, events] of correlationMap) {
    for (const event of currentEvents) {
      if (events.includes(event)) {
        shared.add(event);
      }
    }
  }

  return Array.from(shared);
}

interface AnalysisResult {
  executionDate: string;
  mode: string;
  summary: {
    totalSteps: number;
    totalFindings: number;
    totalDuration: number;
    eventTypes: number;
  };
  steps: ChainEvent[];
  eventCorrelations: any[];
  insights: any;
}

function generateAnalysis(): AnalysisResult {
  const analysis: AnalysisResult = {
    executionDate: new Date().toISOString(),
    mode,
    summary: {
      totalSteps: AGENTS.length,
      totalFindings: allEvents.reduce((sum, e) => sum + e.findings, 0),
      totalDuration: allEvents.reduce((sum, e) => sum + e.duration, 0),
      eventTypes: new Set(allEvents.flatMap((e) => e.events)).size,
    },
    steps: allEvents,
    eventCorrelations: Array.from(correlationMap.entries()).map(
      ([correlation, events]) => ({
        correlation,
        eventCount: events.length,
        events,
      })
    ),
    insights: {
      mostCommonEvents: getMostCommonEvents(allEvents),
      agentInteractions: analyzeInteractions(allEvents),
      sequentialPattern: analyzeSequentialPattern(allEvents),
    },
  };

  return analysis;
}

function getMostCommonEvents(events: ChainEvent[]): object {
  const eventCounts: Record<string, number> = {};

  for (const evt of events) {
    for (const eventType of evt.events) {
      eventCounts[eventType] = (eventCounts[eventType] || 0) + 1;
    }
  }

  return Object.entries(eventCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
    .reduce(
      (acc, [event, count]) => {
        acc[event] = count;
        return acc;
      },
      {} as Record<string, number>
    );
}

function analyzeInteractions(events: ChainEvent[]): object {
  const interactions: Record<string, number> = {};

  for (let i = 0; i < events.length; i++) {
    for (let j = i + 1; j < events.length; j++) {
      const key = `${events[i].agent} → ${events[j].agent}`;
      const shared = events[i].events.filter((e) =>
        events[j].events.includes(e)
      );

      if (shared.length > 0) {
        interactions[key] = shared.length;
      }
    }
  }

  return interactions;
}

function analyzeSequentialPattern(events: ChainEvent[]): string {
  // Analyze how findings accumulate and change across the chain
  const pattern = events.map((e) => e.findings).join(" → ");
  const trend = events[events.length - 1].findings > events[0].findings
    ? "escalating" : "stable/decreasing";

  return `${pattern} (${trend})`;
}

async function main() {
  console.log("═══════════════════════════════════════════════════════════");
  console.log("FASE 3: Progressive Agent Interligação (Chain Runner)");
  console.log(`Mode: ${mode}`);
  console.log("═══════════════════════════════════════════════════════════");

  // Ensure output directory exists
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }

  // Execute agents progressively
  for (let i = 0; i < AGENTS.length; i++) {
    await runAgent(AGENTS[i], i + 1);
  }

  // Generate analysis
  const analysis = generateAnalysis() as AnalysisResult;

  // Write results
  appendFileSync(chainLogFile, JSON.stringify(analysis, null, 2));

  console.log("\n═══════════════════════════════════════════════════════════");
  console.log("CHAIN EXECUTION COMPLETE");
  console.log("═══════════════════════════════════════════════════════════");
  console.log(
    `📊 Analysis saved to: ${chainLogFile}`
  );
  console.log(`✅ Steps executed: ${analysis.summary.totalSteps}`);
  console.log(`📈 Total findings: ${analysis.summary.totalFindings}`);
  console.log(`⏱️  Total duration: ${analysis.summary.totalDuration}ms`);
  console.log(`🔗 Unique event types: ${analysis.summary.eventTypes}`);
}

main().catch(console.error);
