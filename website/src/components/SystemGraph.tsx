/**
 * @file SystemGraph.tsx
 * @description React component for rendering the EGOS cross-reference network visualization using Sigma.js.
 * @module components/SystemGraph
 * @version 1.1.0
 * @date 2025-04-24
 * @license MIT
 *
 * @references
 * - mdc:website/ROADMAP.md#vis-int-001 (Task: Integrate Sigma Visualization Component)
 * - mdc:website/public/visualizations/static/graph-data.js (Data Source)
 * - mdc:docs/principles/conscious_modularity.mdc (EGOS Principle)
 * - mdc:website/src/app/system/visualization/page.tsx (Potential Usage Context - TBC)
 */

import React, { useEffect, useState, FC, useRef, useMemo, memo } from 'react';
// Import necessary components and hooks from @react-sigma/core
import { 
    SigmaContainer, 
    ControlsContainer, 
    ZoomControl, 
    FullScreenControl, 
    useLoadGraph, 
    useRegisterEvents, 
    useSigma 
} from "@react-sigma/core";
import "@react-sigma/core/lib/style.css"; // Import default styles
import Graph from 'graphology';
import ForceAtlas2 from 'graphology-layout-forceatlas2';
import { Attributes } from 'graphology-types';
import { EnrichedGraphData, GraphNode, GraphEdge } from '@/utils/graphDataUtils';

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

// --- Legend Component --- (Now Memoized)
interface LegendProps {
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
}

const Legend: FC<LegendProps> = memo(({ position }) => {
  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4',
  };

  return (
    <div className={`absolute ${positionClasses[position]} bg-background/80 backdrop-blur-sm p-3 rounded-md shadow-md border border-border z-10`}>
      <h3 className="text-sm font-medium mb-2">Subsystems</h3>
      <div className="flex flex-col space-y-1">
        {Object.entries(SUBSYSTEM_COLOR_MAP).map(([name, color]) => (
          <div key={name} className="flex items-center">
            <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: color }}></div>
            <span className="text-xs">{name}</span>
          </div>
        ))}
      </div>
    </div>
  );
});
// Add display name for better debugging
Legend.displayName = 'Legend';

// Define a more specific type for node display data modifications
interface CustomNodeDisplayData extends Attributes {
    highlighted?: boolean;
    forceLabel?: boolean;
    shadowSize?: number;
    shadowColor?: string;
}

// --- Sub-component for Graph Logic & Events --- 
interface GraphEventsProps {
    data: EnrichedGraphData;
    setHoveredNode: (node: string | null) => void;
}

const GraphEvents: FC<GraphEventsProps> = ({ data, setHoveredNode }) => {
    const loadGraph = useLoadGraph();
    const registerEvents = useRegisterEvents();
    const sigma = useSigma();

    // Memoize graph construction to avoid rebuilding unless data changes
    const graph = useMemo(() => {
        if (!data) return null;

        console.log("[GraphEvents] Building graphology instance...");
        const g = new Graph();

        // Add nodes
        data.nodes.forEach(node => {
            if (node.id && node.type && node.path) {
                const references = node.references || 0;
                const referencedBy = node.referenced_by || 0;
                const totalConnections = references + referencedBy;
                const baseSize = 3 + Math.min(5, Math.log(totalConnections + 1));
                
                g.addNode(node.id, {
                    ...node,
                    x: Math.random() * 100, // Initial random position
                    y: Math.random() * 100,
                    size: baseSize,
                    type: "circle", // Ensure type is set
                    fileType: node.type,
                    color: node.subsystem ? getSubsystemColor(node.subsystem) : '#888',
                    label: node.label || node.id,
                    originalSize: baseSize, // Store original size for hover effect
                    borderColor: node.is_core ? '#000' : undefined,
                    borderWidth: node.is_core ? 1 : 0
                });
            } else {
                console.warn('[GraphEvents] Skipping node due to missing properties:', node);
            }
        });

        // Add edges (using GraphEdge type)
        data.edges.forEach((edge: GraphEdge, i: number) => {
            const edgeId = edge.id || `edge-${i}`;
            if (g.hasNode(edge.source) && g.hasNode(edge.target)) {
                // Avoid adding duplicate edges
                if (!g.hasEdge(edge.source, edge.target)) {
                    g.addEdgeWithKey(edgeId, edge.source, edge.target, {
                        color: '#555', 
                        size: 1.5, 
                        type: 'arrow', 
                        weight: 1 
                    });
                } else {
                   // console.warn(`[GraphEvents] Skipping duplicate edge: ${edgeId} (${edge.source} -> ${edge.target})`);
                }
            } else {
                console.warn(`[GraphEvents] Skipping edge ${edgeId} due to missing node(s): ${edge.source} -> ${edge.target}`);
            }
        });

        console.log(`[GraphEvents] Graphology instance created: ${g.order} nodes, ${g.size} edges`);
        return g;

    }, [data]); // Dependency: only rebuild if data changes

    useEffect(() => {
        if (!sigma || !graph) return;

        console.log("[GraphEvents] Loading graph and running layout...");
        
        // Ensure camera is usable
        sigma.getCamera().enable();
        
        // Load the graphology instance into Sigma
        loadGraph(graph);

        // Run layout only if graph has nodes
        if (graph.order > 0) {
            try {
                console.log("[GraphEvents] Starting ForceAtlas2 layout...");
                const settings = {
                    barnesHutOptimize: graph.order > 500,
                    strongGravityMode: true,
                    gravity: 0.1,
                    scalingRatio: 8,
                    slowDown: 2 + Math.log(graph.order) / 8,
                    startAlpha: 1,
                    easing: 0.7,
                    linLogMode: true,
                    outboundAttractionDistribution: true,
                    adjustSizes: true,
                    edgeWeightInfluence: 1.5,
                    preventOverlap: true
                };
                const iterations = Math.min(200, Math.max(50, Math.ceil(graph.order / 5)));
                
                // ForceAtlas2.assign is synchronous
                ForceAtlas2.assign(graph, { iterations, settings });
                console.log("[GraphEvents] ForceAtlas2 layout finished.");

                // Fix node positions immediately after layout
                graph.forEachNode((node) => {
                    graph.setNodeAttribute(node, 'fixed', true);
                });

                // Freeze the graph state in Sigma AFTER layout and fixing
                sigma.getGraph().setAttribute('frozen', true);
                
                // Refresh Sigma to apply changes
                sigma.refresh();

            } catch (err) {
                console.error("[GraphEvents] Layout error:", err);
            }
        }

        // Register Sigma events
        const events = registerEvents({
            enterNode: (event) => setHoveredNode(event.node),
            leaveNode: () => setHoveredNode(null),
            // Add other events like clickNode if needed later
        });
        console.log("[GraphEvents] Event listeners registered.");

        // Cleanup function
        return () => {
            console.log("[GraphEvents] Cleaning up graph events and potentially Sigma instance...");
            if (events && typeof events.unbind === 'function') {
                 events.unbind(); // Unbind specific listeners if method exists
            }
            // Note: `useSigma` hooks might handle deeper Sigma instance cleanup automatically
            // If memory leaks persist, explicit sigma.kill() might be needed here.
            setHoveredNode(null); // Reset hover state on unmount
        };
    }, [graph, loadGraph, registerEvents, sigma, setHoveredNode]); // Dependencies: Re-run if these change

    return null; // This component manages effects, doesn't render UI
};

// --- Main SystemGraph Component --- 
interface SystemGraphProps {
    enrichedGraphData: EnrichedGraphData | null;
    isLoading: boolean;
    error: string | null;
}

const SystemGraph: FC<SystemGraphProps> = ({ enrichedGraphData, isLoading, error }) => {
    const [hoveredNode, setHoveredNode] = useState<string | null>(null);

    if (isLoading) return (
        <div className="flex flex-col justify-center items-center h-full bg-background/50 dark:bg-gray-900/50 rounded-lg p-8">
            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
            <p className="text-lg font-medium text-foreground">Loading System Graph</p>
            <p className="text-sm text-muted-foreground mt-2">Preparing visualization of EGOS interconnections...</p>
        </div>
    );
    
    if (error) return (
        <div className="flex flex-col justify-center items-center h-full bg-background/50 dark:bg-gray-900/50 rounded-lg p-8 border border-destructive/20">
            <div className="w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-destructive" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            </div>
            <p className="text-lg font-medium text-foreground">Error Loading Graph</p>
            <p className="text-sm text-destructive mt-2 text-center max-w-md">{error}</p>
            <p className="text-xs text-muted-foreground mt-4">Please check the console for more details or try refreshing the page.</p>
        </div>
    );
    
    if (!enrichedGraphData || !enrichedGraphData.nodes.length) return (
        <div className="flex flex-col justify-center items-center h-full bg-background/50 dark:bg-gray-900/50 rounded-lg p-8 border border-border">
            <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            </div>
            <p className="text-lg font-medium text-foreground">No Graph Data Available</p>
            <p className="text-sm text-muted-foreground mt-2 text-center">The system couldn't find any visualization data to display.</p>
        </div>
    );

    return (
        <div className="relative w-full h-full">
          <SigmaContainer 
            style={{ height: '100%', width: '100%' }}
            settings={{
              allowInvalidContainer: true,
              defaultNodeType: 'circle', // Ensure this matches a registered program or default
              defaultEdgeType: 'arrow',
              labelDensity: 0.07,
              labelGridCellSize: 60,
              labelRenderedSizeThreshold: 6,
              labelFont: 'Roboto, sans-serif',
              zIndex: true,
              // Enable necessary features for good UX while preventing node movement
              enableCamera: true, // Enable camera for zoom
              renderLabels: true,
              enableEdgeWheelEvents: true,
              // Prevent layout from running during interaction
              enableNodeHovering: true,
              // Improve visual appearance with darker background and better contrast
              renderEdgeLabels: true,
              defaultEdgeColor: '#555',
              edgeLabelSize: 12,
              stagePadding: 30,
              minEdgeSize: 1.5,
              maxEdgeSize: 3,
              edgeColor: 'default',
              // Use a dark theme for better visibility
              labelColor: {
                color: '#333'
              },
              // Node hover effect (using refined types)
              nodeReducer: (node, data): CustomNodeDisplayData => {
                const newData: CustomNodeDisplayData = { ...data };
                const originalSize = data.originalSize as number; // Access stored original size

                // Reset to defaults first
                newData.highlighted = false;
                newData.size = originalSize;
                newData.borderWidth = data.borderWidth as number || 0;
                newData.borderColor = data.borderColor as string; // Keep original border if any
                newData.color = data.color as string; // Keep original color
                newData.shadowSize = undefined;
                newData.shadowColor = undefined;
                newData.forceLabel = false;
                newData.label = data.label as string; // Default label

                if (hoveredNode === node) {
                  // Only force the label to show on the hovered node
                  newData.label = data.label as string;
                  newData.forceLabel = true;
                } else if (hoveredNode !== null) {
                  // Hide labels of non-hovered nodes when something else is hovered
                  newData.label = '';
                } else {
                  // Default state: show labels based on Sigma's settings
                  newData.label = data.label as string;
                }
                
                return newData;
              }
            }}
            className="w-full h-full rounded-lg bg-background dark:bg-gray-900"
          >
              <GraphEvents data={enrichedGraphData} setHoveredNode={setHoveredNode} />
              <ControlsContainer position={"bottom-right"}>
                  <ZoomControl />
                  <FullScreenControl />
              </ControlsContainer>
          </SigmaContainer>
          
          {/* Use the memoized legend component */}
          <Legend position="top-right" />
        </div>
    );
};

export default SystemGraph;
