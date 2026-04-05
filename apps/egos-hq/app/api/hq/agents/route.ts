import { NextResponse } from 'next/server';
import { readFileSync } from 'fs';
import { join } from 'path';

export async function GET() {
  try {
    // Support custom path via env var (needed for standalone VPS deploy)
    const registryPath = process.env.AGENTS_REGISTRY_PATH
      ?? join(process.cwd(), '..', '..', 'agents', 'registry', 'agents.json');
    const raw = readFileSync(registryPath, 'utf-8');
    const registry = JSON.parse(raw);

    const agents = Object.entries(registry.agents ?? {}).map(([id, a]: [string, unknown]) => {
      const agent = a as Record<string, unknown>;
      return {
        id,
        name: agent.name,
        area: agent.area,
        kind: agent.kind,
        status: agent.status,
        risk_level: agent.risk_level ?? 'low',
        triggers: agent.triggers ?? [],
        entrypoint: agent.entrypoint,
        description: agent.description,
      };
    });

    return NextResponse.json({ agents, count: agents.length, version: registry.version });
  } catch (err) {
    return NextResponse.json({ error: `Failed to load registry: ${String(err)}`, agents: [] }, { status: 500 });
  }
}
