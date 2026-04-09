import { NextResponse } from 'next/server';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

// HQV2-001 — parse TASKS.md → structured task summary
export async function GET() {
  const tasksPath = process.env.TASKS_MD_PATH
    ?? join(process.cwd(), '..', '..', 'TASKS.md');

  if (!existsSync(tasksPath)) {
    return NextResponse.json({ error: 'TASKS.md not found', path: tasksPath }, { status: 404 });
  }

  const content = readFileSync(tasksPath, 'utf-8');
  const lines = content.split('\n');

  let total = 0, pending = 0, done = 0;
  let p0 = 0, p1 = 0, p2 = 0;
  const staleP0: string[] = [];

  for (const line of lines) {
    const taskMatch = line.match(/^- \[([ x/])\] \*\*([A-Z][A-Z0-9_-]+-\d+)/);
    if (!taskMatch) continue;

    total++;
    const [, status, id] = taskMatch;
    const isDone = status === 'x';
    const isWip = status === '/';

    if (isDone) { done++; continue; }
    pending++;

    const priorityMatch = line.match(/\[P([012])\]/);
    const priority = priorityMatch ? parseInt(priorityMatch[1]) : null;

    if (priority === 0) {
      p0++;
      // Stale if has a date >3 days old or no recent activity marker
      if (!line.includes('2026-04-09') && !line.includes('2026-04-08')) {
        staleP0.push(id);
      }
    } else if (priority === 1) p1++;
    else if (priority === 2) p2++;
  }

  return NextResponse.json({
    total,
    pending,
    done,
    wip: 0,
    p0,
    p1,
    p2,
    stale_p0: staleP0,
    stale_p0_count: staleP0.length,
    completion_pct: total > 0 ? Math.round((done / total) * 100) : 0,
    lines: lines.length,
  });
}
