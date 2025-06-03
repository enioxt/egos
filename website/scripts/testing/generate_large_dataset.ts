/**
 * @file generate_large_dataset.ts
 * @description Script to generate large synthetic graph datasets for performance testing
 * @module scripts/testing/generate_large_dataset
 * @version 1.0.0
 * @date 2025-05-21
 * @license MIT
 *
 * @references
 * - mdc:website/src/utils/graphDataUtils.ts (Graph data structure)
 * - mdc:website/src/data/graph-data.js (Reference data format)
 * - mdc:docs/testing/performance_benchmarks.md (Testing specifications)
 */

import * as fs from 'fs';
import * as path from 'path';

// Define types matching our application's graph data structure
interface GraphNode {
  id: string;
  label: string;
  path: string;
  type: string;
  references: number;
  referenced_by: number;
  has_mqp: boolean;
  has_roadmap: boolean;
  is_core: boolean;
  last_modified: string;
  subsystem?: string;
}

interface GraphEdge {
  source: string;
  target: string;
  weight?: number;
  id?: string;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/**
 * Generates a synthetic dataset with specified size and characteristics
 * 
 * @param nodeCount Number of nodes to generate
 * @param edgeDensity Density of connections (0-1), where 1 means all nodes connected to all others
 * @param subsystemCount Number of distinct subsystems to simulate
 * @param fileTypeCount Number of distinct file types to simulate
 * @returns Generated graph data
 */
function generateLargeDataset(
  nodeCount: number, 
  edgeDensity: number = 0.05, 
  subsystemCount: number = 8, 
  fileTypeCount: number = 10
): GraphData {
  // Validate inputs
  if (nodeCount <= 0) throw new Error('Node count must be positive');
  if (edgeDensity < 0 || edgeDensity > 1) throw new Error('Edge density must be between 0 and 1');
  
  console.log(`Generating dataset with ${nodeCount} nodes and ~${Math.round(nodeCount * nodeCount * edgeDensity)} edges...`);
  
  const subsystems = [
    'KOIOS', 'CRONOS', 'ETHIK', 'CORUJA', 
    'ATLAS', 'NEXUS', 'HARMONY', 'VIBE', 'OTHER'
  ].slice(0, subsystemCount);
  
  const fileTypes = [
    'markdown', 'python', 'typescript', 'json', 'yaml', 
    'javascript', 'css', 'html', 'rust', 'cpp', 'c', 'go'
  ].slice(0, fileTypeCount);
  
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];
  
  // Generate nodes
  for (let i = 0; i < nodeCount; i++) {
    const subsystem = subsystems[Math.floor(Math.random() * subsystems.length)];
    const fileType = fileTypes[Math.floor(Math.random() * fileTypes.length)];
    const isCore = Math.random() < 0.15; // 15% chance of being a core file
    const hasMqp = Math.random() < 0.3; // 30% chance of having MQP
    const hasRoadmap = Math.random() < 0.25; // 25% chance of having roadmap reference
    
    nodes.push({
      id: `file-${i}.${fileType}`,
      label: `file-${i}.${fileType}`,
      path: `C:\\EGOS\\${subsystem.toLowerCase()}\\src\\file-${i}.${fileType}`,
      type: fileType,
      references: 0, // Will be calculated later
      referenced_by: 0, // Will be calculated later
      has_mqp: hasMqp,
      has_roadmap: hasRoadmap,
      is_core: isCore,
      last_modified: new Date().toISOString(),
      subsystem
    });
  }
  
  // Generate edges based on density parameter
  const maxPossibleEdges = nodeCount * (nodeCount - 1);
  const targetEdgeCount = Math.floor(maxPossibleEdges * edgeDensity);
  
  // First pass: ensure every node has at least one connection
  for (let i = 0; i < nodeCount; i++) {
    // Connect to a random node that's not itself
    let target;
    do {
      target = Math.floor(Math.random() * nodeCount);
    } while (target === i);
    
    edges.push({
      source: nodes[i].id,
      target: nodes[target].id,
      weight: Math.random() * 5 + 1,
      id: `edge-${i}-${target}`
    });
  }
  
  // Second pass: add remaining edges to reach target density
  let remainingEdges = targetEdgeCount - edges.length;
  let attempts = 0;
  const maxAttempts = remainingEdges * 10; // Avoid infinite loop
  
  while (remainingEdges > 0 && attempts < maxAttempts) {
    const source = Math.floor(Math.random() * nodeCount);
    const target = Math.floor(Math.random() * nodeCount);
    
    // Skip self-references
    if (source === target) {
      attempts++;
      continue;
    }
    
    // Skip if edge already exists
    const edgeExists = edges.some(e => 
      e.source === nodes[source].id && e.target === nodes[target].id
    );
    
    if (!edgeExists) {
      edges.push({
        source: nodes[source].id,
        target: nodes[target].id,
        weight: Math.random() * 5 + 1,
        id: `edge-${edges.length}`
      });
      remainingEdges--;
    }
    
    attempts++;
  }
  
  // Calculate reference counts
  const referenceMap = new Map<string, number>();
  const referencedByMap = new Map<string, number>();
  
  nodes.forEach(node => {
    referenceMap.set(node.id, 0);
    referencedByMap.set(node.id, 0);
  });
  
  edges.forEach(edge => {
    referenceMap.set(edge.source, (referenceMap.get(edge.source) || 0) + 1);
    referencedByMap.set(edge.target, (referencedByMap.get(edge.target) || 0) + 1);
  });
  
  // Update reference counts in nodes
  nodes.forEach(node => {
    node.references = referenceMap.get(node.id) || 0;
    node.referenced_by = referencedByMap.get(node.id) || 0;
  });
  
  console.log(`Generated ${nodes.length} nodes and ${edges.length} edges.`);
  
  return { nodes, edges };
}

/**
 * Saves the generated graph data to a file
 * 
 * @param data The graph data to save
 * @param size The size indicator (small, medium, large, etc.)
 */
function saveDataset(data: GraphData, size: string): void {
  const outputDir = path.join(__dirname, '..', '..', 'public', 'test-data');
  
  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  const outputPath = path.join(outputDir, `graph-data-${size}.js`);
  
  // Format as JavaScript module
  const content = `/**
 * EGOS Cross-Reference Network Test Data (${size})
 * Generated: ${new Date().toISOString()}
 * Node count: ${data.nodes.length}
 * Edge count: ${data.edges.length}
 */

const graphData = ${JSON.stringify(data, null, 2)};

export default graphData;
`;
  
  fs.writeFileSync(outputPath, content);
  console.log(`Dataset saved to ${outputPath}`);
}

/**
 * Main function to generate and save datasets of various sizes
 */
function main() {
  console.log('Generating test datasets for performance testing...');
  
  // Generate small dataset (1,000 nodes)
  const smallData = generateLargeDataset(1000, 0.01);
  saveDataset(smallData, 'small');
  
  // Generate medium dataset (5,000 nodes)
  const mediumData = generateLargeDataset(5000, 0.005);
  saveDataset(mediumData, 'medium');
  
  // Generate large dataset (10,000 nodes)
  const largeData = generateLargeDataset(10000, 0.001);
  saveDataset(largeData, 'large');
  
  // Generate extra large dataset (20,000 nodes) with lower density
  const xlargeData = generateLargeDataset(20000, 0.0005);
  saveDataset(xlargeData, 'xlarge');
  
  console.log('All datasets generated successfully.');
}

// Run the main function
main();
