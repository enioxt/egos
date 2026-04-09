import { NextResponse } from 'next/server';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

// HQV2-002 — World Model health snapshot
// Reads /data/world-model/current.json (volume-mounted on VPS)
// Falls back to parsing TASKS.md for basic health metrics

type WorldModelSnapshot = {
  timestamp: string;
  health_score: number;
  blockers: string[];
  active_goals: string[];
  infrastructure: Record<string, string>;
  domains: Record<string, { status: string; last_activity: string }>;
};

function parseTasksForHealth(tasksPath: string): WorldModelSnapshot {
  const content = readFileSync(tasksPath, 'utf-8');
  const lines = content.split('\n');

  const p0Open = lines.filter((l) => l.includes('[ ]') && l.includes('[P0]')).length;
  const p1Open = lines.filter((l) => l.includes('[ ]') && l.includes('[P1]')).length;
  const totalDone = lines.filter((l) => l.includes('[x]')).length;
  const totalOpen = lines.filter((l) => l.includes('[ ]')).length;

  const completionPct = totalDone + totalOpen > 0
    ? Math.round((totalDone / (totalDone + totalOpen)) * 100)
    : 0;

  // health: 100 - penalty for P0 open items
  const health = Math.max(0, Math.min(100, 100 - p0Open * 10 - p1Open * 2));

  // Extract P0 blockers (first 5)
  const blockers = lines
    .filter((l) => l.includes('[ ]') && l.includes('[P0]'))
    .slice(0, 5)
    .map((l) => l.replace(/^- \[ \] \*\*/, '').replace(/\*\*.*$/, '').trim());

  return {
    timestamp: new Date().toISOString(),
    health_score: health,
    blockers,
    active_goals: [
      'Guard Brasil GTM — first paying customer',
      'KBS FORJA pilot — 14-day dogfooding',
      'Notion Claude Agents waitlist + integration',
    ],
    infrastructure: {
      vps: 'hetzner-204.168.217.125',
      supabase: 'lhscgsqhiooyatkebose',
      git: 'enioxt/egos',
    },
    domains: {
      guard_brasil: { status: 'live', last_activity: new Date().toISOString().slice(0, 10) },
      kb_as_service: { status: 'beta', last_activity: new Date().toISOString().slice(0, 10) },
      gem_hunter: { status: 'live', last_activity: new Date().toISOString().slice(0, 10) },
      eagle_eye: { status: 'live', last_activity: new Date().toISOString().slice(0, 10) },
    },
  };
}

export async function GET() {
  // Try volume-mounted world-model first
  const wmPath = process.env.WORLD_MODEL_PATH
    ?? join(process.env.JOBS_DIR ?? '/data/docs/jobs', '..', 'world-model', 'current.json');

  if (existsSync(wmPath)) {
    try {
      const raw = readFileSync(wmPath, 'utf-8');
      const snapshot = JSON.parse(raw) as WorldModelSnapshot;
      return NextResponse.json({ ok: true, source: 'file', data: snapshot });
    } catch {
      // fall through to TASKS.md parser
    }
  }

  // Fallback: derive from TASKS.md
  const tasksPath = process.env.TASKS_MD_PATH
    ?? join(process.cwd(), '..', '..', 'TASKS.md');

  if (!existsSync(tasksPath)) {
    return NextResponse.json({ ok: false, error: 'world-model file and TASKS.md not found' }, { status: 404 });
  }

  try {
    const snapshot = parseTasksForHealth(tasksPath);
    return NextResponse.json({ ok: true, source: 'tasks_md', data: snapshot });
  } catch (e) {
    return NextResponse.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}
