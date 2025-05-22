/**
 * @file CrossReferenceGraph.tsx
 * @description Graph visualization component for the Cross-Reference Explorer
 * @module components/cross-reference/CrossReferenceGraph
 * @version 1.0.0
 * @date 2025-05-21
 *
 * @references
 * - mdc:website/src/components/SystemGraph.tsx (Base Graph Visualization)
 * - mdc:docs_egos/08_tooling_and_scripts/reference_implementations/file_reference_checker_ultra.md (Tool Documentation)
 * - mdc:scripts/cross_reference/integration/INTEGRATION_DESIGN.md (Integration Design)
 */

import React, { useEffect, useRef, useState, FC, useMemo } from 'react';
import { 
  SigmaContainer, 
  ControlsContainer, 
  ZoomControl, 
  FullScreenControl,
  useLoadGraph,
  useRegisterEvents,
  useSigma
} from "@react-sigma/core";
import "@react-sigma/core/lib/style.css";
import Graph from 'graphology';
import Dagre from 'graphology-layout-dagre';
import { CircularProgress } from '@/components/ui/progress-circular';
import { CrossReferenceData } from './CrossReferenceExplorer';
import { Card, CardContent } from '@/components/ui/card';
import { FileTextIcon, FolderIcon, AlertTriangleIcon } from 'lucide-react';

// --- Centralized Constants ---
const SUBSYSTEM_COLOR_MAP: Record<string, string> = {
  'KOIOS': '#4285F4', 'CRONOS': '#EA4335', 'ETHIK': '#34A853',
  'CORUJA': '#FBBC05', 'ATLAS': '#9C27B0', 'NEXUS': '#FF9800',
  'HARMONY': '#00BCD4', 'VIBE': '#795548', 'OTHER': '#9E9E9E'
};

// --- Helper: Define colors --- 
function getSubsystemColor(subsystem: string): string {
  return SUBSYSTEM_COLOR_MAP[subsystem] || SUBSYSTEM_COLOR_MAP['OTHER'];
}

// --- Helper: Node size based on reference count ---
function getNodeSize(referencedCount: number): number {
  const baseSize = 3;
  const maxSize = 15;
  return Math.max(baseSize, Math.min(maxSize, baseSize + Math.log2(referencedCount + 1)));
}

// --- Component to load the graph ---
interface GraphLoaderProps {
  data: CrossReferenceData;
  filterConfig: any;
}

const GraphLoader: FC<GraphLoaderProps> = ({ data, filterConfig }) => {
  const loadGraph = useLoadGraph();
  const registerEvents = useRegisterEvents();
  const sigma = useSigma();
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [hoveredEdge, setHoveredEdge] = useState<string | null>(null);

  // Create and load the graph when data changes
  useEffect(() => {
    // Initialize graph
    const graph = new Graph();
    
    // Apply filters to nodes
    const filteredNodes = data.nodes.filter(node => {
      const subsystemMatch = filterConfig.subsystems.includes('ALL') || 
                             (node.subsystem && filterConfig.subsystems.includes(node.subsystem));
      const orphanedMatch = !node.orphaned || filterConfig.showOrphaned;
      const warningsMatch = !node.hasWarnings || filterConfig.showWarnings;
      const searchMatch = !filterConfig.searchTerm || 
                         node.label.toLowerCase().includes(filterConfig.searchTerm.toLowerCase()) ||
                         node.path.toLowerCase().includes(filterConfig.searchTerm.toLowerCase());
      const referenceMatch = node.referenced >= filterConfig.referenceThreshold;
      
      return subsystemMatch && orphanedMatch && warningsMatch && searchMatch && referenceMatch;
    });
    
    // Get IDs of filtered nodes
    const filteredNodeIds = new Set(filteredNodes.map(node => node.id));
    
    // Add nodes to graph
    filteredNodes.forEach(node => {
      graph.addNode(node.id, {
        label: node.label,
        size: getNodeSize(node.referenced),
        color: node.orphaned ? '#FFA000' : getSubsystemColor(node.subsystem || 'OTHER'),
        type: node.type,
        x: Math.random(),
        y: Math.random(),
        ...node
      });
    });
    
    // Add edges that connect filtered nodes
    data.edges.forEach(edge => {
      if (filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target)) {
        graph.addEdge(edge.source, edge.target, {
          id: edge.id,
          size: 1,
          color: edge.valid ? '#34A853' : '#EA4335',
          type: edge.type,
          ...edge
        });
      }
    });
    
    // Layout the graph
    if (graph.order > 0) {
      const positions = Dagre.assign(graph, {
        hierarchize: true,
        directed: true,
        rankdir: 'LR', // Left to right layout
        align: 'DL',
        ranksep: 100,
        nodesep: 50,
        edgesep: 10,
      });
      
      // Load the graph into sigma
      loadGraph(graph);
    } else {
      // Create an empty graph if no nodes match the filters
      loadGraph(new Graph());
    }
    
    // Register mouse events
    registerEvents({
      enterNode: (event) => {
        setHoveredNode(event.node);
        const graph = sigma.getGraph();
        graph.setNodeAttribute(event.node, "highlighted", true);
      },
      leaveNode: (event) => {
        setHoveredNode(null);
        const graph = sigma.getGraph();
        if (graph.hasNode(event.node))
          graph.setNodeAttribute(event.node, "highlighted", false);
      },
      clickNode: (event) => {
        setSelectedNode(event.node);
      },
      enterEdge: (event) => {
        setHoveredEdge(event.edge);
        const graph = sigma.getGraph();
        graph.setEdgeAttribute(event.edge, "highlighted", true);
      },
      leaveEdge: (event) => {
        setHoveredEdge(null);
        const graph = sigma.getGraph();
        if (graph.hasEdge(event.edge))
          graph.setEdgeAttribute(event.edge, "highlighted", false);
      },
      clickStage: () => {
        setSelectedNode(null);
      },
    });
  }, [data, filterConfig, loadGraph, registerEvents, sigma]);

  return null;
};

// --- Node info display component ---
interface NodeInfoProps {
  nodeId: string;
  sigmaInstance: any;
}

const NodeInfo: FC<NodeInfoProps> = ({ nodeId, sigmaInstance }) => {
  const graph = sigmaInstance.getGraph();
  const node = graph.getNodeAttributes(nodeId);
  
  return (
    <Card className="absolute bottom-4 left-4 w-64 z-10 shadow-lg">
      <CardContent className="p-4">
        <div className="flex items-center mb-2">
          {node.type === 'file' ? 
            <FileTextIcon className="h-4 w-4 mr-2" /> : 
            <FolderIcon className="h-4 w-4 mr-2" />
          }
          <h3 className="font-medium text-sm truncate">{node.label}</h3>
        </div>
        
        <div className="text-xs text-muted-foreground mb-1 truncate">
          Caminho: {node.path}
        </div>
        
        {node.subsystem && (
          <div className="text-xs mb-1">
            Subsistema: <span style={{ color: getSubsystemColor(node.subsystem) }}>{node.subsystem}</span>
          </div>
        )}
        
        <div className="text-xs mb-1">
          Referenciado: {node.referenced} {node.referenced === 1 ? 'vez' : 'vezes'}
        </div>
        
        {node.orphaned && (
          <div className="text-xs text-warning flex items-center mt-2">
            <AlertTriangleIcon className="h-3 w-3 mr-1" />
            Arquivo órfão (sem referências de entrada)
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// --- Main component ---
interface CrossReferenceGraphProps {
  data: CrossReferenceData;
  filterConfig: any;
}

const CrossReferenceGraph: FC<CrossReferenceGraphProps> = ({ data, filterConfig }) => {
  return (
    <SigmaContainer style={{ height: '100%', width: '100%' }}
      settings={{
        renderEdgeLabels: false,
        defaultNodeType: "circle",
        defaultEdgeType: "arrow",
        labelDensity: 0.07,
        labelGridCellSize: 60,
        labelRenderedSizeThreshold: 6,
        labelFont: "Inter, sans-serif",
        zIndex: true
      }}>
      <GraphLoader data={data} filterConfig={filterConfig} />
      
      <ControlsContainer position={"bottom-right"}>
        <ZoomControl />
        <FullScreenControl />
      </ControlsContainer>
      
      {/* To add node info panel, would need to access selected node from sigma */}
    </SigmaContainer>
  );
};

export default CrossReferenceGraph;
