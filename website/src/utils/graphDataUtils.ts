/**
 * @file graphDataUtils.ts
 * @description Utility functions for extracting and processing graph data for the visualization.
 * @module utils/graphDataUtils
 * @version 1.0.0
 * @date 2025-04-23
 * @license MIT
 *
 * @references
 * - mdc:website/src/data/graph-data.js (Graph Data Source)
 * - mdc:website/src/components/SystemGraph.tsx (Visualization Component)
 * - mdc:website/src/components/FilterControls.tsx (Filter Controls Component)
 * - mdc:docs/process/cross_reference_visualization.md (Visualization Process)
 */

import graphData from '@/data/graph-data.js';

/**
 * Interface for a node in the graph data
 */
export interface GraphNode {
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

/**
 * Interface for an edge in the graph data
 */
export interface GraphEdge {
  source: string;
  target: string;
  weight?: number;
}

/**
 * Extract unique file types from the graph data
 * @returns Array of unique file types sorted alphabetically
 */
export function extractFileTypes(): string[] {
  const fileTypes = new Set<string>();
  
  if (graphData && graphData.nodes) {
    graphData.nodes.forEach((node: any) => {
      if (node.type) fileTypes.add(node.type);
    });
  }
  
  return Array.from(fileTypes).sort();
}

/**
 * Extract subsystems from the graph data based on file paths
 * @returns Array of unique subsystems sorted alphabetically
 */
export function extractSubsystems(): string[] {
  const subsystems = new Set<string>();
  
  if (graphData && graphData.nodes) {
    graphData.nodes.forEach((node: any) => {
      // Extract subsystem from path
      const path = node.path || '';
      
      // Match common subsystem patterns in paths
      const subsystemPatterns = [
        /\\subsystems\\([^\\]+)\\/i,  // Standard subsystem folder
        /\\([A-Z]{3,})\\/i,           // All caps folder names (like KOIOS, ETHIK)
        /\\(cronos|atlas|nexus|koios|ethik|coruja|harmony|vibe|slop)\\?/i  // Known subsystem names
      ];
      
      for (const pattern of subsystemPatterns) {
        const match = path.match(pattern);
        if (match && match[1]) {
          subsystems.add(match[1].toUpperCase());
          break;
        }
      }
    });
  }
  
  return Array.from(subsystems).sort();
}

/**
 * Enrich graph data with additional metadata like subsystem information
 * @returns Enriched graph data with additional properties
 */
export function getEnrichedGraphData() {
  if (!graphData) return { nodes: [], edges: [] };
  
  const enrichedNodes = graphData.nodes.map((node: any) => {
    // Extract subsystem from path
    let subsystem = "OTHER";
    const path = node.path || '';
    
    const subsystemPatterns = [
      { pattern: /\\subsystems\\([^\\]+)\\/i, group: 1 },
      { pattern: /\\([A-Z]{3,})\\/i, group: 1 },
      { pattern: /\\(cronos|atlas|nexus|koios|ethik|coruja|harmony|vibe|slop)\\?/i, group: 1 }
    ];
    
    for (const { pattern, group } of subsystemPatterns) {
      const match = path.match(pattern);
      if (match && match[group]) {
        subsystem = match[group].toUpperCase();
        break;
      }
    }
    
    return {
      ...node,
      subsystem
    };
  });
  
  return {
    nodes: enrichedNodes,
    edges: graphData.edges
  };
}

/**
 * Get the maximum number of connections in the graph data
 * @returns The maximum number of connections any node has
 */
export function getMaxConnections(): number {
  let maxConnections = 0;
  
  if (graphData && graphData.nodes) {
    graphData.nodes.forEach((node: any) => {
      const connections = (node.referenced_by || 0) + (node.references || 0);
      if (connections > maxConnections) {
        maxConnections = connections;
      }
    });
  }
  
  return maxConnections;
}

/**
 * Apply filters to graph data
 * @param data Graph data to filter
 * @param filters Filter options to apply
 * @returns Filtered graph data
 */
export function applyFiltersToData(
  data: EnrichedGraphData,
  filters: {
    fileTypes: string[];
    subsystems: string[];
    minConnections: number;
    showCore: boolean | null;
  }
) {
  // Use provided data instead of fetching it again
  const enrichedData = data;
  
  // Filter nodes
  const filteredNodes = enrichedData.nodes.filter((node: any) => {
    // File type filter
    if (filters.fileTypes.length > 0 && !filters.fileTypes.includes(node.type)) {
      return false;
    }
    
    // Subsystem filter
    if (filters.subsystems.length > 0 && !filters.subsystems.includes(node.subsystem)) {
      return false;
    }
    
    // Connection threshold filter
    const connections = (node.referenced_by || 0) + (node.references || 0);
    if (connections < filters.minConnections) {
      return false;
    }
    
    // Core files filter
    if (filters.showCore !== null && node.is_core !== filters.showCore) {
      return false;
    }
    
    return true;
  });
  
  // Get IDs of filtered nodes for edge filtering
  const filteredNodeIds = new Set(filteredNodes.map((node: any) => node.id));
  
  // Filter edges to only include those between filtered nodes
  const filteredEdges = enrichedData.edges.filter((edge: any) => 
    filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target)
  );
  
  return {
    nodes: filteredNodes,
    edges: filteredEdges
  };
}
