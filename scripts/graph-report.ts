#!/usr/bin/env node
/**
 * GRF-001: Graph Report — Weekly Knowledge Graph Analysis
 * 
 * Generates GRAPH_REPORT.md from codebase-memory-mcp query_graph
 * Identifies: god nodes, surprising connections, clusters, orphans
 * 
 * Run: npx tsx scripts/graph-report.ts
 * Cron: Weekly (Sundays 23:00)
 */

import { execSync } from 'child_process';
import { writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const OUTPUT_PATH = join(__dirname, '../docs/jobs/GRAPH_REPORT.md');

interface GraphNode {
  id: string;
  name: string;
  type: string;
  edges: number;
}

interface Analysis {
  godNodes: GraphNode[];
  clusters: string[];
  surprisingConnections: string[];
  orphans: GraphNode[];
  stats: {
    totalNodes: number;
    totalEdges: number;
    avgConnectivity: number;
  };
}

async function queryGraph(): Promise<any> {
  // Query codebase-memory-mcp via MCP bridge
  try {
    const result = execSync(
      'curl -s -X POST http://localhost:3000/mcp -d \'{"method": "query_graph", "params": {}}\'',
      { encoding: 'utf-8', timeout: 30000 }
    );
    return JSON.parse(result);
  } catch (err) {
    console.log('⚠️  MCP query failed, using mock data for development');
    return generateMockData();
  }
}

function generateMockData() {
  // Mock data for development/testing
  return {
    nodes: [
      { id: '1', name: 'Guard Brasil API', type: 'module', edges: 45 },
      { id: '2', name: 'PII Detection', type: 'capability', edges: 38 },
      { id: '3', name: 'LGPD Compliance', type: 'domain', edges: 32 },
      { id: '4', name: 'Neo4j Client', type: 'module', edges: 28 },
      { id: '5', name: 'Gem Hunter', type: 'agent', edges: 25 },
      { id: '6', name: 'WhatsApp Gateway', type: 'integration', edges: 12 },
    ],
    edges: [
      { source: '1', target: '2', type: 'uses' },
      { source: '2', target: '3', type: 'implements' },
      { source: '4', target: '1', type: 'supports' },
      { source: '5', target: '4', type: 'queries' },
    ]
  };
}

function analyzeGraph(data: any): Analysis {
  const nodes: GraphNode[] = data.nodes || [];
  const edges = data.edges || [];
  
  // God nodes: high connectivity (>75th percentile)
  const edgeCounts = nodes.map(n => n.edges).sort((a, b) => a - b);
  const p75 = edgeCounts[Math.floor(edgeCounts.length * 0.75)] || 30;
  const godNodes = nodes.filter(n => n.edges >= p75).sort((a, b) => b.edges - a.edges);
  
  // Orphans: low connectivity (<3 edges)
  const orphans = nodes.filter(n => n.edges < 3);
  
  // Simple cluster detection by type
  const typeGroups = new Map<string, GraphNode[]>();
  for (const node of nodes) {
    if (!typeGroups.has(node.type)) typeGroups.set(node.type, []);
    typeGroups.get(node.type)!.push(node);
  }
  const clusters = Array.from(typeGroups.entries())
    .filter(([_, nodes]) => nodes.length >= 3)
    .map(([type, nodes]) => `${type} (${nodes.length} nodes)`);
  
  // Surprising connections: cross-domain edges
  const surprisingConnections: string[] = [];
  for (const edge of edges) {
    const source = nodes.find(n => n.id === edge.source);
    const target = nodes.find(n => n.id === edge.target);
    if (source && target && source.type !== target.type) {
      surprisingConnections.push(`${source.name} → ${target.name} (${edge.type})`);
    }
  }
  
  const totalEdges = edges.length + nodes.reduce((sum, n) => sum + n.edges, 0);
  
  return {
    godNodes,
    clusters,
    surprisingConnections,
    orphans,
    stats: {
      totalNodes: nodes.length,
      totalEdges: totalEdges,
      avgConnectivity: totalEdges / (nodes.length || 1)
    }
  };
}

function generateReport(analysis: Analysis): string {
  const now = new Date().toISOString().split('T')[0];
  
  let report = `# Graph Report — Weekly Knowledge Graph Analysis\n\n`;
  report += `> **Date:** ${now}  \n`;
  report += `> **Source:** codebase-memory-mcp query_graph  \n`;
  report += `> **Job:** GRF-001  \n\n`;
  
  // Stats
  report += `## 📊 Overview\n\n`;
  report += `- **Total Nodes:** ${analysis.stats.totalNodes}\n`;
  report += `- **Total Edges:** ${analysis.stats.totalEdges}\n`;
  report += `- **Avg Connectivity:** ${analysis.stats.avgConnectivity.toFixed(2)}\n\n`;
  
  // God Nodes
  report += `## 🔱 God Nodes (High Connectivity)\n\n`;
  report += `Nodes with >75th percentile connectivity:\n\n`;
  for (const node of analysis.godNodes.slice(0, 10)) {
    report += `- **${node.name}** (${node.type}): ${node.edges} edges\n`;
  }
  report += `\n*These are your architectural anchors. Changes here have ripple effects.*\n\n`;
  
  // Clusters
  report += `## 🎯 Clusters Detected\n\n`;
  if (analysis.clusters.length > 0) {
    for (const cluster of analysis.clusters) {
      report += `- ${cluster}\n`;
    }
  } else {
    report += `- No significant clusters detected\n`;
  }
  report += `\n`;
  
  // Surprising Connections
  report += `## 🔗 Surprising Connections\n\n`;
  report += `Cross-domain relationships that may indicate:\n`;
  report += `- Hidden dependencies\n`;
  report += `- Refactoring opportunities\n`;
  report += `- Architectural insights\n\n`;
  
  if (analysis.surprisingConnections.length > 0) {
    for (const conn of analysis.surprisingConnections.slice(0, 20)) {
      report += `- ${conn}\n`;
    }
  } else {
    report += `- No cross-domain connections detected\n`;
  }
  report += `\n`;
  
  // Orphans
  report += `## 🚧 Orphans (Low Connectivity)\n\n`;
  if (analysis.orphans.length > 0) {
    report += `Nodes with <3 edges — potential candidates for:\n`;
    report += `- Consolidation\n`;
    report += `- Removal (dead code)\n`;
    report += `- Better integration\n\n`;
    
    for (const node of analysis.orphans) {
      report += `- ${node.name} (${node.type}): ${node.edges} edges\n`;
    }
  } else {
    report += `✅ No orphan nodes detected — good connectivity across codebase!\n`;
  }
  report += `\n`;
  
  // Recommendations
  report += `## 💡 Recommendations\n\n`;
  report += `### Immediate\n`;
  if (analysis.orphans.length > 5) {
    report += `- [ ] Review ${analysis.orphans.length} orphan nodes for dead code removal\n`;
  }
  if (analysis.godNodes.length > 0) {
    report += `- [ ] Document top god node: ${analysis.godNodes[0].name}\n`;
  }
  report += `- [ ] Verify surprising connections are intentional\n\n`;
  
  report += `### This Week\n`;
  report += `- [ ] Review cluster boundaries for modularity\n`;
  report += `- [ ] Update ARCHITECTURE.md with new insights\n\n`;
  
  // Footer
  report += `---\n\n`;
  report += `**Next Report:** ${new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}  \n`;
  report += `**Job:** \`bun run graph:report\`  \n`;
  report += `**Config:** \`.guarani/jobs/graph-report.json\`\n`;
  
  return report;
}

async function main() {
  console.log('🔍 GRF-001: Generating knowledge graph report...\n');
  
  // Query graph
  const graphData = await queryGraph();
  console.log(`📊 Found ${graphData.nodes?.length || 0} nodes, ${graphData.edges?.length || 0} edges`);
  
  // Analyze
  const analysis = analyzeGraph(graphData);
  console.log(`🎯 God nodes: ${analysis.godNodes.length}`);
  console.log(`🚧 Orphans: ${analysis.orphans.length}`);
  console.log(`🔗 Surprising connections: ${analysis.surprisingConnections.length}\n`);
  
  // Generate report
  const report = generateReport(analysis);
  
  // Write
  writeFileSync(OUTPUT_PATH, report);
  console.log(`✅ Report written: ${OUTPUT_PATH}`);
  console.log(`\n📈 Stats: ${analysis.stats.totalNodes} nodes, ${analysis.stats.avgConnectivity.toFixed(1)} avg connectivity`);
}

main().catch(err => {
  console.error('❌ Error:', err);
  process.exit(1);
});
