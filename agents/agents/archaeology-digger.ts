/**
 * Archaeology Digger Agent
 *
 * Recursively traverses git history, agent registries, governance files,
 * and handoff documents to reconstruct the complete evolution lineage
 * of the EGOS ecosystem.
 *
 * Outputs:
 * - Timeline of feature additions with commit evidence
 * - Agent lineage matrix (creation date, wave, catalyst)
 * - Governance file creation/migration history
 * - Breakpoint detection (LLM shifts, prompt engineering, external refs)
 *
 * Modes:
 * - dry_run: Scan and print findings
 * - execute: Scan, write JSON + Markdown report to docs/archaeology/
 */

import { readFileSync, writeFileSync, readdirSync, statSync, existsSync, mkdirSync } from 'fs';
import { join, basename } from 'path';
import { execSync } from 'child_process';
import { runAgent, printResult, log, type RunContext, type Finding } from '../runtime/runner';
import { Topics } from '../runtime/event-bus';

// --- Types ---

interface TimelineEvent {
  date: string;
  hash: string;
  message: string;
  files: string[];
  category: Category;
  wave?: number;
  tags: string[];
}

interface AgentLineage {
  id: string;
  name: string;
  createdAt: string;
  commitHash: string;
  wave: number;
  area: string;
  catalyst: string;
  entrypoint: string;
}

type Category =
  | 'governance'
  | 'agents'
  | 'mycelium'
  | 'research'
  | 'infra'
  | 'apps'
  | 'philosophy';

// --- Category Detection ---

function detectCategory(files: string[], message: string): Category {
  const msg = message.toLowerCase();
  const paths = files.join(' ').toLowerCase();
  if (paths.includes('.guarani/') || paths.includes('.windsurfrules') || msg.includes('governance'))
    return 'governance';
  if (paths.includes('agents/agents/') || msg.includes('agent'))
    return 'agents';
  if (paths.includes('mycelium') || msg.includes('mycelium'))
    return 'mycelium';
  if (paths.includes('docs/research/') || msg.includes('research') || msg.includes('study'))
    return 'research';
  if (paths.includes('apps/') || msg.includes('bot') || msg.includes('telegram') || msg.includes('discord'))
    return 'apps';
  if (paths.includes('philosophy') || msg.includes('ethik') || msg.includes('sacred'))
    return 'philosophy';
  return 'infra';
}

// --- Tag Detection ---

function detectTags(message: string, files: string[]): string[] {
  const tags: string[] = [];
  const msg = message.toLowerCase();
  if (msg.includes('breakpoint') || msg.includes('breaking'))
    tags.push('breakpoint');
  if (msg.includes('gemini') || msg.includes('gpt') || msg.includes('qwen') || msg.includes('alibaba') || msg.includes('codex'))
    tags.push('llm-shift');
  if (msg.includes('prompt') || msg.includes('pipeline') || msg.includes('refinery'))
    tags.push('prompt-engineering');
  if (msg.includes('consciousness') || msg.includes('tsun-cha') || msg.includes('philosophy'))
    tags.push('consciousness');
  if (msg.includes('ocean') || msg.includes('bittensor') || msg.includes('vana') || msg.includes('external'))
    tags.push('external-reference');
  if (msg.includes('archaeology') || msg.includes('recover') || msg.includes('gems'))
    tags.push('archaeology');
  return tags;
}

// --- Wave Assignment ---

function assignWave(date: string): number {
  const d = new Date(date);
  const day = d.getDate();
  const month = d.getMonth() + 1;
  if (month === 2 && day <= 16) return 0; // Survival Coding
  if (month === 2 && day <= 17) return 1; // Agent Kernel
  if (month === 2 && day <= 20) return 2; // QA/Design
  if (month === 2 && day <= 25) return 3; // Orchestration
  if (month === 3 && day <= 6) return 4;  // Research/Ecosystem
  return 5; // Kernel Extraction
}

// --- Git History Traversal ---

function getGitTimeline(repoPath: string, pathFilter: string): TimelineEvent[] {
  if (!existsSync(join(repoPath, '.git'))) return [];
  try {
    const raw = execSync(
      `git log --all --diff-filter=A --name-only --pretty=format:"__COMMIT__%ai|%H|%s" -- '${pathFilter}'`,
      { cwd: repoPath, maxBuffer: 10 * 1024 * 1024, encoding: 'utf-8' }
    );
    const events: TimelineEvent[] = [];
    let current: { date: string; hash: string; message: string } | null = null;
    let files: string[] = [];

    for (const line of raw.split('\n')) {
      if (line.startsWith('__COMMIT__')) {
        if (current && files.length > 0) {
          events.push({
            date: current.date.slice(0, 10),
            hash: current.hash,
            message: current.message,
            files,
            category: detectCategory(files, current.message),
            wave: assignWave(current.date),
            tags: detectTags(current.message, files),
          });
        }
        const parts = line.replace('__COMMIT__', '').split('|');
        current = { date: parts[0], hash: parts[1], message: parts.slice(2).join('|') };
        files = [];
      } else if (line.trim()) {
        files.push(line.trim());
      }
    }
    if (current && files.length > 0) {
      events.push({
        date: current.date.slice(0, 10),
        hash: current.hash,
        message: current.message,
        files,
        category: detectCategory(files, current.message),
        wave: assignWave(current.date),
        tags: detectTags(current.message, files),
      });
    }
    return events.sort((a, b) => a.date.localeCompare(b.date));
  } catch {
    return [];
  }
}

// --- Agent Lineage Extraction ---

function extractAgentLineage(repoPath: string): AgentLineage[] {
  const registryPath = join(repoPath, 'agents', 'registry', 'agents.json');
  if (!existsSync(registryPath)) return [];

  const registry = JSON.parse(readFileSync(registryPath, 'utf-8'));
  const agents: AgentLineage[] = [];

  for (const agent of registry.agents || []) {
    let createdAt = 'unknown';
    let commitHash = 'unknown';
    try {
      const logLine = execSync(
        `git log --all --diff-filter=A --format="%ai|%H" -- '${agent.entrypoint}' | tail -1`,
        { cwd: repoPath, encoding: 'utf-8' }
      ).trim();
      if (logLine) {
        const [date, hash] = logLine.split('|');
        createdAt = date.slice(0, 10);
        commitHash = hash;
      }
    } catch { /* no git data */ }

    agents.push({
      id: agent.id,
      name: agent.name,
      createdAt,
      commitHash,
      wave: assignWave(createdAt),
      area: agent.area || 'unknown',
      catalyst: inferCatalyst(agent, createdAt),
      entrypoint: agent.entrypoint,
    });
  }
  return agents.sort((a, b) => a.createdAt.localeCompare(b.createdAt));
}

function inferCatalyst(agent: Record<string, unknown>, date: string): string {
  const desc = ((agent.description || '') as string).toLowerCase();
  if (desc.includes('security') || desc.includes('scan')) return 'tactical-need';
  if (desc.includes('test') || desc.includes('contract') || desc.includes('regression'))
    return 'qa-architecture';
  if (desc.includes('ssot') || desc.includes('governance') || desc.includes('drift'))
    return 'governance-enforcement';
  if (desc.includes('research') || desc.includes('gem') || desc.includes('discover'))
    return 'research-expansion';
  if (desc.includes('social') || desc.includes('telegram') || desc.includes('discord'))
    return 'external-communication';
  if (desc.includes('domain') || desc.includes('laboratory') || desc.includes('ambient'))
    return 'self-observation';
  return 'organic-growth';
}

// --- Governance File History ---

function getGovernanceHistory(repoPath: string): TimelineEvent[] {
  const guaraniEvents = getGitTimeline(repoPath, '.guarani/');
  const workflowEvents = getGitTimeline(repoPath, '.windsurf/');
  return [...guaraniEvents, ...workflowEvents].sort((a, b) => a.date.localeCompare(b.date));
}

// --- Handoff Document Scanner ---

function scanHandoffs(repoPath: string): { date: string; file: string; summary: string }[] {
  const handoffDir = join(repoPath, 'docs', '_current_handoffs');
  if (!existsSync(handoffDir)) return [];
  const results: { date: string; file: string; summary: string }[] = [];
  for (const file of readdirSync(handoffDir)) {
    if (!file.endsWith('.md')) continue;
    const content = readFileSync(join(handoffDir, file), 'utf-8');
    const dateMatch = file.match(/(\d{4}-\d{2}-\d{2})/);
    const titleMatch = content.match(/^#\s+(.+)$/m);
    results.push({
      date: dateMatch ? dateMatch[1] : 'unknown',
      file,
      summary: titleMatch ? titleMatch[1].slice(0, 120) : basename(file, '.md'),
    });
  }
  return results.sort((a, b) => a.date.localeCompare(b.date));
}

// --- Report Generator ---

function generateMarkdownReport(
  timeline: TimelineEvent[],
  agents: AgentLineage[],
  governance: TimelineEvent[],
  handoffs: { date: string; file: string; summary: string }[]
): string {
  const lines: string[] = [];
  lines.push('# EGOS Archaeological Lineage Report');
  lines.push(`> Generated: ${new Date().toISOString().slice(0, 10)}`);
  lines.push('');

  lines.push('## Agent Lineage Matrix');
  lines.push('| Wave | Date | Agent | Area | Catalyst |');
  lines.push('|------|------|-------|------|----------|');
  for (const a of agents) {
    lines.push(`| ${a.wave} | ${a.createdAt} | ${a.name} | ${a.area} | ${a.catalyst} |`);
  }
  lines.push('');

  lines.push('## Feature Timeline');
  lines.push(`Total events: ${timeline.length}`);
  lines.push('');
  const byWave = new Map<number, TimelineEvent[]>();
  for (const ev of timeline) {
    const w = ev.wave ?? 0;
    if (!byWave.has(w)) byWave.set(w, []);
    byWave.get(w)!.push(ev);
  }
  for (const [wave, events] of [...byWave.entries()].sort((a, b) => a[0] - b[0])) {
    lines.push(`### Wave ${wave} (${events.length} events)`);
    for (const ev of events.slice(0, 20)) {
      const tags = ev.tags.length ? ` [${ev.tags.join(', ')}]` : '';
      lines.push(`- **${ev.date}** ${ev.message}${tags}`);
    }
    lines.push('');
  }

  lines.push('## Governance File History');
  lines.push(`Total governance events: ${governance.length}`);
  for (const g of governance.slice(0, 30)) {
    lines.push(`- **${g.date}** ${g.message}`);
  }
  lines.push('');

  lines.push('## Handoff Documents');
  for (const h of handoffs) {
    lines.push(`- **${h.date}** ${h.summary}`);
  }

  return lines.join('\n');
}

// --- Main Agent ---

async function archaeologyDigger(ctx: RunContext): Promise<Finding[]> {
  const findings: Finding[] = [];
  const egosLabPath = join(ctx.repoRoot, '..', 'egos-lab');
  const egosPath = ctx.repoRoot;

  log(ctx, 'info', 'Scanning egos-lab git history...');
  const labPaths = ['agents/', '.guarani/', 'packages/', 'scripts/', 'apps/'];
  const labTimeline = labPaths.flatMap(p => getGitTimeline(egosLabPath, p));
  labTimeline.sort((a, b) => a.date.localeCompare(b.date));
  findings.push({
    severity: 'info',
    category: 'archaeology',
    message: `egos-lab timeline: ${labTimeline.length} feature-addition events found`,
  });

  log(ctx, 'info', 'Scanning egos git history...');
  const corePaths = ['agents/', '.guarani/', 'packages/', 'scripts/'];
  const coreTimeline = corePaths.flatMap(p => getGitTimeline(egosPath, p));
  coreTimeline.sort((a, b) => a.date.localeCompare(b.date));
  findings.push({
    severity: 'info',
    category: 'archaeology',
    message: `egos timeline: ${coreTimeline.length} feature-addition events found`,
  });

  log(ctx, 'info', 'Extracting agent lineage from egos-lab registry...');
  const labAgents = extractAgentLineage(egosLabPath);
  findings.push({
    severity: 'info',
    category: 'archaeology',
    message: `egos-lab agent lineage: ${labAgents.length} agents with creation dates`,
  });

  log(ctx, 'info', 'Extracting agent lineage from egos registry...');
  const coreAgents = extractAgentLineage(egosPath);
  findings.push({
    severity: 'info',
    category: 'archaeology',
    message: `egos agent lineage: ${coreAgents.length} agents with creation dates`,
  });

  log(ctx, 'info', 'Scanning governance file history...');
  const governance = getGovernanceHistory(egosLabPath);
  findings.push({
    severity: 'info',
    category: 'archaeology',
    message: `Governance events: ${governance.length} .guarani/ and .windsurf/ additions`,
  });

  log(ctx, 'info', 'Scanning handoff documents...');
  const handoffs = scanHandoffs(egosLabPath);
  findings.push({
    severity: 'info',
    category: 'archaeology',
    message: `Handoff documents: ${handoffs.length} session handoffs found`,
  });

  // Detect breakpoints
  const allTimeline = [...labTimeline, ...coreTimeline].sort((a, b) => a.date.localeCompare(b.date));
  const breakpoints = allTimeline.filter(ev => ev.tags.includes('llm-shift') || ev.tags.includes('breakpoint'));
  for (const bp of breakpoints) {
    findings.push({
      severity: 'warning',
      category: 'breakpoint',
      message: `Breakpoint detected: ${bp.message} (${bp.date})`,
      file: bp.files[0],
    });
  }

  // Detect tag distribution
  const tagCounts: Record<string, number> = {};
  for (const ev of allTimeline) {
    for (const tag of ev.tags) {
      tagCounts[tag] = (tagCounts[tag] || 0) + 1;
    }
  }
  for (const [tag, count] of Object.entries(tagCounts)) {
    findings.push({
      severity: 'info',
      category: 'evolution-tag',
      message: `Tag "${tag}": ${count} occurrences across timeline`,
    });
  }

  ctx.bus.emit(Topics.KNOWLEDGE_HARVESTED, {
    type: 'archaeology-lineage',
    agentCount: labAgents.length + coreAgents.length,
    timelineEvents: allTimeline.length,
    breakpoints: breakpoints.length,
  }, ctx.agentId, ctx.correlationId);

  if (ctx.mode === 'execute') {
    const reportDir = join(egosPath, 'docs', 'archaeology');
    if (!existsSync(reportDir)) mkdirSync(reportDir, { recursive: true });

    const allAgents = [...labAgents, ...coreAgents];
    const report = generateMarkdownReport(allTimeline, allAgents, governance, handoffs);
    writeFileSync(join(reportDir, 'LINEAGE_REPORT.md'), report);
    log(ctx, 'info', 'Wrote docs/archaeology/LINEAGE_REPORT.md');

    const jsonData = { generated: new Date().toISOString(), timeline: allTimeline, agents: allAgents, governance, handoffs, tagCounts };
    writeFileSync(join(reportDir, 'lineage-data.json'), JSON.stringify(jsonData, null, 2));
    log(ctx, 'info', 'Wrote docs/archaeology/lineage-data.json');

    findings.push({
      severity: 'info',
      category: 'archaeology',
      message: 'Reports written to docs/archaeology/',
    });
  }

  return findings;
}

// --- Entrypoint ---

const mode = process.argv.includes('--exec') ? 'execute' : 'dry_run';
const result = await runAgent('archaeology_digger', mode, archaeologyDigger);
printResult(result);
