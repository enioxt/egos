/**
 * Mycelium Reference Graph — Canonical Schema & Seed
 *
 * This is the Phase 1 implementation from REFERENCE_GRAPH_DESIGN.md.
 * It defines the canonical types for the EGOS mesh topology and seeds
 * the initial graph from current known surfaces.
 *
 * The reference graph answers: what exists, how it connects, and what
 * evidence proves each relation. It is NOT the event stream.
 *
 * @see docs/concepts/mycelium/REFERENCE_GRAPH_DESIGN.md
 */

// ═══════════════════════════════════════════════════════════
// Entity Types
// ═══════════════════════════════════════════════════════════

export type ReferenceEntityType =
  | 'workspace_root'
  | 'repository'
  | 'human'
  | 'artifact'
  | 'reference'
  | 'citation'
  | 'surface'
  | 'runtime'
  | 'agent'
  | 'worker'
  | 'endpoint'
  | 'event_topic'
  | 'queue'
  | 'database'
  | 'trigger'
  | 'bot'
  | 'document'
  | 'workflow'
  | 'issue'
  | 'task'
  | 'metric'
  | 'schema'
  | 'projection'
  | 'integration'
  | 'shadow_node'
  | 'policy'
  | 'reference_snapshot';

// ═══════════════════════════════════════════════════════════
// Relation Types
// ═══════════════════════════════════════════════════════════

export type ReferenceRelation =
  // Structural
  | 'belongs_to'
  | 'depends_on'
  | 'contains'
  | 'exposes'
  | 'subscribes_to'
  | 'emits'
  | 'persists_to'
  | 'reads_from'
  | 'writes_to'
  | 'routes_to'
  | 'references'
  | 'cites'
  | 'contributes_to'
  // Governance
  | 'documents'
  | 'governs'
  | 'tracks'
  | 'plans'
  | 'validates'
  | 'derives_from'
  | 'mirrors'
  | 'flags'
  // Evidence
  | 'observed_in_code'
  | 'observed_in_runtime'
  | 'observed_in_log'
  | 'observed_in_plan';

// ═══════════════════════════════════════════════════════════
// Evidence
// ═══════════════════════════════════════════════════════════

export type ReferenceEvidence = 'code' | 'runtime' | 'log' | 'plan' | 'issue';

export type NodeStatus = 'active' | 'degraded' | 'offline' | 'planned';

// ═══════════════════════════════════════════════════════════
// Core Interfaces
// ═══════════════════════════════════════════════════════════

export interface ReferenceNode {
  id: string;
  type: ReferenceEntityType;
  label: string;
  status: NodeStatus;
  evidence: ReferenceEvidence[];
  sourcePath?: string;
  note?: string;
  tags?: string[];
}

export interface ReferenceEdge {
  from: string;
  relation: ReferenceRelation;
  to: string;
  evidence: ReferenceEvidence[];
  note?: string;
}

export interface ReferenceGraph {
  version: string;
  generated: string;
  nodes: ReferenceNode[];
  edges: ReferenceEdge[];
}

// ═══════════════════════════════════════════════════════════
// Graph Utilities
// ═══════════════════════════════════════════════════════════

export function createGraph(
  nodes: ReferenceNode[],
  edges: ReferenceEdge[],
): ReferenceGraph {
  return {
    version: '1.0.0',
    generated: new Date().toISOString(),
    nodes,
    edges,
  };
}

export function findNode(graph: ReferenceGraph, id: string): ReferenceNode | undefined {
  return graph.nodes.find(n => n.id === id);
}

export function findEdgesFrom(graph: ReferenceGraph, nodeId: string): ReferenceEdge[] {
  return graph.edges.filter(e => e.from === nodeId);
}

export function findEdgesTo(graph: ReferenceGraph, nodeId: string): ReferenceEdge[] {
  return graph.edges.filter(e => e.to === nodeId);
}

export function nodesByType(graph: ReferenceGraph, type: ReferenceEntityType): ReferenceNode[] {
  return graph.nodes.filter(n => n.type === type);
}

export function nodesByStatus(graph: ReferenceGraph, status: NodeStatus): ReferenceNode[] {
  return graph.nodes.filter(n => n.status === status);
}

/**
 * Returns a health summary of the graph.
 */
export function graphHealth(graph: ReferenceGraph): {
  totalNodes: number;
  totalEdges: number;
  active: number;
  degraded: number;
  planned: number;
  offline: number;
  orphanNodes: string[];
} {
  const connectedIds = new Set<string>();
  for (const e of graph.edges) {
    connectedIds.add(e.from);
    connectedIds.add(e.to);
  }
  const orphanNodes = graph.nodes
    .filter(n => !connectedIds.has(n.id))
    .map(n => n.id);

  return {
    totalNodes: graph.nodes.length,
    totalEdges: graph.edges.length,
    active: graph.nodes.filter(n => n.status === 'active').length,
    degraded: graph.nodes.filter(n => n.status === 'degraded').length,
    planned: graph.nodes.filter(n => n.status === 'planned').length,
    offline: graph.nodes.filter(n => n.status === 'offline').length,
    orphanNodes,
  };
}

// ═══════════════════════════════════════════════════════════
// Kernel Seed Graph — Current EGOS Reality
// ═══════════════════════════════════════════════════════════

const KERNEL_NODES: ReferenceNode[] = [
  // Workspace roots
  { id: 'ws:egos-home', type: 'workspace_root', label: '~/.egos (Shared Governance)', status: 'active', evidence: ['code'], sourcePath: '~/.egos' },
  { id: 'ws:egos-kernel', type: 'repository', label: 'egos (Kernel)', status: 'active', evidence: ['code', 'runtime'], sourcePath: '/home/enio/egos' },

  // Leaf repos
  { id: 'repo:egos-lab', type: 'repository', label: 'egos-lab', status: 'active', evidence: ['code', 'runtime'], sourcePath: '/home/enio/egos-lab' },
  { id: 'repo:carteira-livre', type: 'repository', label: 'carteira-livre', status: 'active', evidence: ['code', 'runtime'], sourcePath: '/home/enio/carteira-livre' },
  { id: 'repo:br-acc', type: 'repository', label: 'br-acc', status: 'active', evidence: ['code', 'runtime'], sourcePath: '/home/enio/br-acc' },
  { id: 'repo:forja', type: 'repository', label: 'forja', status: 'degraded', evidence: ['code'], sourcePath: '/home/enio/forja' },
  { id: 'repo:852', type: 'repository', label: '852', status: 'active', evidence: ['code', 'runtime'], sourcePath: '/home/enio/852' },
  { id: 'repo:policia', type: 'repository', label: 'policia', status: 'degraded', evidence: ['code'], sourcePath: '/home/enio/policia' },
  { id: 'repo:egos-self', type: 'repository', label: 'egos-self', status: 'degraded', evidence: ['code'], sourcePath: '/home/enio/egos-self' },

  // Runtime surfaces
  { id: 'runtime:agent-runner', type: 'runtime', label: 'Agent Runner', status: 'active', evidence: ['code'], sourcePath: 'agents/runtime/runner.ts' },
  { id: 'runtime:event-bus', type: 'runtime', label: 'Event Bus', status: 'active', evidence: ['code'], sourcePath: 'agents/runtime/event-bus.ts' },

  // Agents
  { id: 'agent:context-tracker', type: 'agent', label: 'Context Tracker', status: 'active', evidence: ['code'], sourcePath: 'agents/agents/context-tracker.ts' },

  // Shared packages
  { id: 'pkg:llm-provider', type: 'integration', label: 'LLM Provider', status: 'active', evidence: ['code', 'runtime'], sourcePath: 'packages/shared/src/llm-provider.ts' },
  { id: 'pkg:model-router', type: 'integration', label: 'Model Router', status: 'active', evidence: ['code', 'runtime'], sourcePath: 'packages/shared/src/model-router.ts' },
  { id: 'pkg:atrian', type: 'integration', label: 'ATRiAN Validator', status: 'active', evidence: ['code'], sourcePath: 'packages/shared/src/atrian.ts' },
  { id: 'pkg:pii-scanner', type: 'integration', label: 'PII Scanner', status: 'active', evidence: ['code'], sourcePath: 'packages/shared/src/pii-scanner.ts' },
  { id: 'pkg:conversation-memory', type: 'integration', label: 'Conversation Memory', status: 'active', evidence: ['code'], sourcePath: 'packages/shared/src/conversation-memory.ts' },

  // Governance
  { id: 'doc:guarani', type: 'document', label: '.guarani Governance DNA', status: 'active', evidence: ['code'], sourcePath: '.guarani/' },
  { id: 'doc:domain-rules', type: 'document', label: 'Domain Rules', status: 'active', evidence: ['code'], sourcePath: '.guarani/orchestration/DOMAIN_RULES.md' },
  { id: 'doc:pipeline', type: 'document', label: 'Orchestration Pipeline', status: 'active', evidence: ['code'], sourcePath: '.guarani/orchestration/PIPELINE.md' },
  { id: 'script:gov-sync', type: 'workflow', label: 'Governance Sync', status: 'active', evidence: ['code', 'runtime'], sourcePath: 'scripts/governance-sync.sh' },

  // Workflows
  { id: 'wf:start', type: 'workflow', label: '/start Workflow', status: 'active', evidence: ['code'], sourcePath: '.windsurf/workflows/start.md' },
  { id: 'wf:end', type: 'workflow', label: '/end Workflow', status: 'active', evidence: ['code'], sourcePath: '.windsurf/workflows/end.md' },
  { id: 'wf:mycelium', type: 'workflow', label: '/mycelium Workflow', status: 'active', evidence: ['code'], sourcePath: '.windsurf/workflows/mycelium.md' },

  // Meta-prompts
  { id: 'prompt:strategist', type: 'document', label: 'Universal Strategist', status: 'active', evidence: ['code'], sourcePath: '.guarani/prompts/meta/universal-strategist.md' },
  { id: 'prompt:brainet', type: 'document', label: 'Brainet Collective', status: 'active', evidence: ['code'], sourcePath: '.guarani/prompts/meta/brainet-collective.md' },
  { id: 'prompt:mycelium', type: 'document', label: 'Mycelium Orchestrator', status: 'active', evidence: ['code'], sourcePath: '.guarani/prompts/meta/mycelium-orchestrator.md' },
  { id: 'prompt:audit', type: 'document', label: 'Ecosystem Audit', status: 'active', evidence: ['code'], sourcePath: '.guarani/prompts/meta/ecosystem-audit.md' },
];

const KERNEL_EDGES: ReferenceEdge[] = [
  // Governance flow
  { from: 'ws:egos-kernel', relation: 'contains', to: 'doc:guarani', evidence: ['code'] },
  { from: 'doc:guarani', relation: 'contains', to: 'doc:domain-rules', evidence: ['code'] },
  { from: 'doc:guarani', relation: 'contains', to: 'doc:pipeline', evidence: ['code'] },
  { from: 'script:gov-sync', relation: 'mirrors', to: 'ws:egos-home', evidence: ['code', 'runtime'] },
  { from: 'ws:egos-home', relation: 'governs', to: 'repo:egos-lab', evidence: ['code'] },
  { from: 'ws:egos-home', relation: 'governs', to: 'repo:carteira-livre', evidence: ['code'] },
  { from: 'ws:egos-home', relation: 'governs', to: 'repo:br-acc', evidence: ['code'] },
  { from: 'ws:egos-home', relation: 'governs', to: 'repo:forja', evidence: ['code'] },
  { from: 'ws:egos-home', relation: 'governs', to: 'repo:egos-self', evidence: ['code'] },

  // Runtime
  { from: 'ws:egos-kernel', relation: 'contains', to: 'runtime:agent-runner', evidence: ['code'] },
  { from: 'ws:egos-kernel', relation: 'contains', to: 'runtime:event-bus', evidence: ['code'] },
  { from: 'runtime:agent-runner', relation: 'depends_on', to: 'pkg:llm-provider', evidence: ['code'] },
  { from: 'pkg:llm-provider', relation: 'depends_on', to: 'pkg:model-router', evidence: ['code'] },

  // Shared packages
  { from: 'ws:egos-kernel', relation: 'contains', to: 'pkg:llm-provider', evidence: ['code'] },
  { from: 'ws:egos-kernel', relation: 'contains', to: 'pkg:model-router', evidence: ['code'] },
  { from: 'ws:egos-kernel', relation: 'contains', to: 'pkg:atrian', evidence: ['code'] },
  { from: 'ws:egos-kernel', relation: 'contains', to: 'pkg:pii-scanner', evidence: ['code'] },
  { from: 'ws:egos-kernel', relation: 'contains', to: 'pkg:conversation-memory', evidence: ['code'] },

  // Leaf repos consume shared packages
  { from: 'repo:egos-lab', relation: 'depends_on', to: 'pkg:llm-provider', evidence: ['code'] },
  { from: 'repo:carteira-livre', relation: 'depends_on', to: 'pkg:atrian', evidence: ['code'] },
  { from: 'repo:carteira-livre', relation: 'depends_on', to: 'pkg:pii-scanner', evidence: ['code'] },
  { from: 'repo:852', relation: 'derives_from', to: 'pkg:atrian', evidence: ['code'], note: 'Source of ATRiAN pattern' },
  { from: 'repo:852', relation: 'derives_from', to: 'pkg:conversation-memory', evidence: ['code'], note: 'Source of conversation memory pattern' },
  // Cross-repo chatbot hardening (verified 100/100 compliance-checker)
  { from: 'repo:forja', relation: 'depends_on', to: 'pkg:atrian', evidence: ['code'] },
  { from: 'repo:forja', relation: 'depends_on', to: 'pkg:pii-scanner', evidence: ['code'] },
  { from: 'repo:forja', relation: 'depends_on', to: 'pkg:conversation-memory', evidence: ['code'] },
  { from: 'repo:egos-lab', relation: 'depends_on', to: 'pkg:atrian', evidence: ['code'] },
  { from: 'repo:egos-lab', relation: 'depends_on', to: 'pkg:pii-scanner', evidence: ['code'] },
  { from: 'repo:egos-lab', relation: 'depends_on', to: 'pkg:conversation-memory', evidence: ['code'] },
  // Context tracker governs session lifecycle
  { from: 'ws:egos-kernel', relation: 'contains', to: 'agent:context-tracker', evidence: ['code'] },
  { from: 'agent:context-tracker', relation: 'emits', to: 'wf:end', evidence: ['code'], note: 'Auto-trigger at CTX >= 250' },

  // Workflows
  { from: 'ws:egos-kernel', relation: 'contains', to: 'wf:start', evidence: ['code'] },
  { from: 'ws:egos-kernel', relation: 'contains', to: 'wf:end', evidence: ['code'] },
  { from: 'ws:egos-kernel', relation: 'contains', to: 'wf:mycelium', evidence: ['code'] },
  { from: 'script:gov-sync', relation: 'routes_to', to: 'wf:start', evidence: ['code'], note: 'Propagates workflow files' },

  // Meta-prompts belong to guarani
  { from: 'doc:guarani', relation: 'contains', to: 'prompt:strategist', evidence: ['code'] },
  { from: 'doc:guarani', relation: 'contains', to: 'prompt:brainet', evidence: ['code'] },
  { from: 'doc:guarani', relation: 'contains', to: 'prompt:mycelium', evidence: ['code'] },
  { from: 'doc:guarani', relation: 'contains', to: 'prompt:audit', evidence: ['code'] },

  // policia is mapped but not auto-synced
  { from: 'ws:egos-home', relation: 'references', to: 'repo:policia', evidence: ['code'], note: 'Mapped-only, not auto-synced' },
];

/**
 * Returns the canonical kernel seed graph representing current EGOS reality.
 */
export function getKernelSeedGraph(): ReferenceGraph {
  return createGraph(KERNEL_NODES, KERNEL_EDGES);
}
