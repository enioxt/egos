import { NextResponse } from 'next/server';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

// HQV2-005 — agents.json + areas → graph nodes/edges for D3
export async function GET() {
  const agentsPath = process.env.AGENTS_REGISTRY_PATH
    ?? join(process.cwd(), '..', '..', 'agents', 'registry', 'agents.json');

  if (!existsSync(agentsPath)) {
    return NextResponse.json({ error: 'agents.json not found', path: agentsPath }, { status: 404 });
  }

  const raw = readFileSync(agentsPath, 'utf-8');
  const registry = JSON.parse(raw);
  const agents = registry.agents ?? {};

  // Build nodes
  const nodes: Array<{ id: string; name: string; area: string; kind: string; status: string }> = [];
  const areaSet = new Set<string>();
  const edges: Array<{ source: string; target: string; type: string }> = [];

  for (const [id, a] of Object.entries(agents)) {
    const agent = a as Record<string, unknown>;
    const area = (agent.area as string) ?? 'unknown';
    areaSet.add(area);
    nodes.push({
      id,
      name: (agent.name as string) ?? id,
      area,
      kind: (agent.kind as string) ?? 'agent',
      status: (agent.status as string) ?? 'active',
    });
  }

  // Area nodes (clusters)
  const areaNodes = [...areaSet].map(area => ({
    id: `area:${area}`,
    name: area,
    area,
    kind: 'area',
    status: 'active',
  }));

  // Agent → area edges
  for (const node of nodes) {
    edges.push({ source: node.id, target: `area:${node.area}`, type: 'belongs_to' });
  }

  return NextResponse.json({
    nodes: [...areaNodes, ...nodes],
    edges,
    stats: {
      total_agents: nodes.length,
      total_areas: areaSet.size,
      areas: [...areaSet],
    },
  });
}
