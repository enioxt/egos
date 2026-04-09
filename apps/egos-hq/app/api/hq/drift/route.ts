import { NextResponse } from 'next/server';
import { readFileSync, readdirSync, existsSync } from 'fs';
import { join } from 'path';

// HQV2-004 — parse latest doc-drift-verifier.json → structured drift summary
export async function GET() {
  const jobsDir = process.env.JOBS_DIR ?? join(process.cwd(), '..', '..', 'docs', 'jobs');

  if (!existsSync(jobsDir)) {
    return NextResponse.json({ error: 'jobs dir not found', path: jobsDir }, { status: 404 });
  }

  // Find latest drift verifier JSON
  const files = readdirSync(jobsDir)
    .filter(f => f.includes('doc-drift-verifier') && f.endsWith('.json'))
    .sort()
    .reverse();

  if (files.length === 0) {
    return NextResponse.json({ error: 'no drift report found', checked: jobsDir }, { status: 404 });
  }

  const latestFile = join(jobsDir, files[0]);
  const raw = readFileSync(latestFile, 'utf-8');
  const report = JSON.parse(raw);

  const drifted = (report.results ?? []).filter((r: { status: string }) => r.status !== 'ok');

  return NextResponse.json({
    report_date: files[0].substring(0, 10),
    repo: report.repo,
    verified_at: report.verified_at,
    summary: report.summary,
    drifted_claims: drifted,
    status: drifted.length === 0 ? 'clean' : 'drifted',
  });
}
