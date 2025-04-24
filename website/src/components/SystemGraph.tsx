/**
 * @file SystemGraph.tsx
 * @description React component for rendering the EGOS cross-reference network visualization using Sigma.js.
 * @module components/SystemGraph
 * @version 1.0.0
 * @date 2025-04-23
 * @license MIT
 *
 * @references
 * - mdc:website/ROADMAP.md#vis-int-001 (Task: Integrate Sigma Visualization Component)
 * - mdc:website/public/visualizations/static/graph-data.js (Data Source)
 * - mdc:docs/principles/conscious_modularity.mdc (EGOS Principle)
 * - mdc:website/src/app/system/visualization/page.tsx (Potential Usage Context - TBC)
 */

import React, { useEffect, useRef, useState } from 'react';
// Use standard imports with type safety handled through dynamic loading
import Sigma from 'sigma';
import Graph from 'graphology';
import ForceAtlas2 from 'graphology-layout-forceatlas2'; 
// Import actual graph data
import graphData from '@/data/graph-data';
// Import filter options type
import { FilterOptions } from './FilterControls';
// Import graph data utilities
import { applyFiltersToData } from '@/utils/graphDataUtils';

// Import CSS for Sigma if needed
// import 'sigma/sigma.min.css';

interface SystemGraphProps {
    /** Filter options to apply to the visualization */
    filters?: FilterOptions;
}

const SystemGraph: React.FC<SystemGraphProps> = ({ filters }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [graphInstance, setGraphInstance] = useState<Graph | null>(null);
    const [sigmaInstance, setSigmaInstance] = useState<Sigma | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    // Effect for initializing the graph and sigma renderer
    useEffect(() => {
        if (!containerRef.current) {
            console.error("SystemGraph: Container reference not found.");
            setError("Initialization failed: Container element missing.");
            setIsLoading(false);
            return;
        }

        let sigmaRenderer: Sigma | null = null;
        let layout: any = null;

        try {
            console.log("SystemGraph: Initializing graph...");
            // Import data from graphData
            const graph = new Graph();
            if (graphData && graphData.nodes && graphData.edges) {
                // Create nodes and edges manually to avoid type issues
                graphData.nodes.forEach((node: any) => {
                    graph.addNode(node.id, {
                        label: node.label,
                        size: 5 + (node.referenced_by / 10),
                        color: node.is_core ? '#ff4500' : '#1E88E5',
                        x: Math.random(),
                        y: Math.random(),
                        // Use 'default' type for all nodes to avoid Sigma renderer errors
                        type: 'default',
                        // Keep original type as a custom property
                        originalType: node.type,
                        // Keep other properties
                        ...node
                    });
                });
                
                graphData.edges.forEach((edge: any) => {
                    if (graph.hasNode(edge.source) && graph.hasNode(edge.target)) {
                        graph.addEdge(edge.source, edge.target, {
                            size: 1,
                            color: '#ccc'
                        });
                    }
                });
                console.log(`SystemGraph: Imported ${graph.order} nodes and ${graph.size} edges.`);
            } else {
                console.error("SystemGraph: graphData format is invalid or missing.", graphData);
                setError("Failed to load graph data: Invalid format.");
                setIsLoading(false);
                return; // Exit useEffect if data is bad
            }

            setGraphInstance(graph);

            console.log("SystemGraph: Initializing Sigma...");
            sigmaRenderer = new Sigma(graph, containerRef.current, {
                renderEdgeLabels: false, // Adjust settings as needed
                labelRenderedSizeThreshold: 1,
                labelFont: 'Inter, sans-serif',
                allowInvalidContainer: true, // Consider if needed for dynamic containers
                // Define default node type for all nodes
                defaultNodeType: 'circle',
                // Define node and edge reducers to customize appearance
                nodeReducer: (node, data) => {
                    // Return data with customizations based on node properties
                    const fileType = data.originalType || data.type;
                    // Color coding based on file type
                    let color = data.color;
                    
                    // Adjust size based on references
                    const size = 3 + Math.min(10, (data.referenced_by || 0) / 10);
                    
                    return {
                        ...data,
                        size,
                        color,
                        // Force the type to be a valid Sigma renderer type
                        type: 'circle'
                    };
                }
            });
            setSigmaInstance(sigmaRenderer);

            console.log("SystemGraph: Initializing ForceAtlas2 layout...");
             if (typeof ForceAtlas2 === 'function') {
                // Apply ForceAtlas2 layout with specified iterations
                layout = ForceAtlas2(graph, 100); // Run for 100 iterations
                
                // Alternative approach if the above doesn't work:
                // Try using the async version if available
                try {
                  const asyncFA2 = require('graphology-layout-forceatlas2/worker');
                  if (asyncFA2 && typeof asyncFA2.default === 'function') {
                    layout = asyncFA2.default(graph, {
                      settings: {
                        gravity: 1,
                        scalingRatio: 10
                      }
                    });
                  }
                } catch (e) {
                  console.log('Async ForceAtlas2 not available, using synchronous version');
                }

                // Optional: Configure layout parameters
                // layout.assign({ settings: { barnesHutOptimize: true, gravity: 1 } });

                console.log("SystemGraph: Starting layout...");
                // Run layout - synchronous or asynchronous depending on implementation
                // Use Web Workers for large graphs to avoid blocking the main thread
                 if (layout.start) {
                    layout.start(); // Handle potential async nature if needed
                 } else if (typeof layout === 'function') {
                     // Legacy or different structure support
                     const positions = layout(); // Or however the layout is applied
                     // Apply positions manually if needed: graph.updateNodeAttribute(...)
                     console.log("SystemGraph: Layout function called.");
                 } else {
                     // Fallback or error if layout structure is unexpected
                     console.warn("SystemGraph: ForceAtlas2Layout structure not recognized or start method missing. Applying random layout.");
                     // applyRandomLayout(graph); // Implement or use a random layout function
                 }

            
            } else {
                console.error("SystemGraph: ForceAtlas2Layout is not available or not a constructor.");
                setError("Layout algorithm failed to load.");
                // applyRandomLayout(graph); // Fallback
            }

            setIsLoading(false);
            console.log("SystemGraph: Initialization complete.");

        } catch (err) {
            console.error("SystemGraph: Error during initialization:", err);
            setError(`Initialization failed: ${err instanceof Error ? err.message : String(err)}`);
            setIsLoading(false);
        }

        // Cleanup function
        return () => {
            console.log("SystemGraph: Cleaning up Sigma instance...");
            if (layout && layout.stop) layout.stop(); // Stop layout if running
            if (sigmaRenderer) sigmaRenderer.kill();
            setSigmaInstance(null);
            setGraphInstance(null);
            if (containerRef.current) {
                containerRef.current.innerHTML = ''; // Clear the container
            }
            console.log("SystemGraph: Cleanup complete.");
        };
    }, []); // Run effect only once on mount
    
    // Effect for applying filters when they change
    useEffect(() => {
        if (!graphInstance || !filters) return;
        
        console.log("SystemGraph: Applying filters...", filters);
        
        try {
            // Apply filters to the graph
            const { nodes: filteredNodes, edges: filteredEdges } = applyFiltersToData(filters);
            
            // Get all node IDs in the graph
            const allNodeIds = graphInstance.nodes();
            
            // Create a set of filtered node IDs for quick lookup
            const filteredNodeIds = new Set(filteredNodes.map((node: any) => node.id));
            
            // Update node visibility based on filters
            allNodeIds.forEach((nodeId: string) => {
                const isVisible = filteredNodeIds.has(nodeId);
                
                // Update node visibility
                graphInstance.setNodeAttribute(nodeId, 'hidden', !isVisible);
                
                // If node is visible, ensure it has the correct attributes
                if (isVisible) {
                    const nodeData = filteredNodes.find((n: any) => n.id === nodeId);
                    if (nodeData) {
                        // Update node attributes if needed
                        graphInstance.setNodeAttribute(nodeId, 'color', nodeData.is_core ? '#ff4500' : '#1E88E5');
                        graphInstance.setNodeAttribute(nodeId, 'size', 5 + (nodeData.referenced_by / 10));
                    }
                }
            });
            
            // Update edge visibility
            graphInstance.edges().forEach((edgeId: string) => {
                const edge = graphInstance.getEdgeAttributes(edgeId);
                const sourceVisible = !graphInstance.getNodeAttribute(edge.source, 'hidden');
                const targetVisible = !graphInstance.getNodeAttribute(edge.target, 'hidden');
                
                // Edge is visible only if both source and target nodes are visible
                graphInstance.setEdgeAttribute(edgeId, 'hidden', !(sourceVisible && targetVisible));
            });
            
            // Refresh the sigma renderer
            if (sigmaInstance) {
                sigmaInstance.refresh();
            }
            
            console.log(`SystemGraph: Applied filters. Visible nodes: ${filteredNodes.length}, Visible edges: ${filteredEdges.length}`);
        } catch (err) {
            console.error("SystemGraph: Error applying filters:", err);
            setError(`Filter application failed: ${err instanceof Error ? err.message : String(err)}`);
        }
    }, [filters, graphInstance, sigmaInstance]); // Re-run when filters or graph instance changes

    // TODO: Implement data loading logic if graphData is not imported directly
    // useEffect(() => {
    //     // Fetch data or load from props
    // }, [/* dependencies */]);


    return (
        <div style={{ position: 'relative', width: '100%', height: '600px', border: '1px solid #ccc' }}>
            {isLoading && <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>Loading graph...</div>}
            {error && <div style={{ position: 'absolute', top: '10px', left: '10px', color: 'red', backgroundColor: 'rgba(255, 200, 200, 0.8)', padding: '10px', borderRadius: '5px' }}>Error: {error}</div>}
            <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
        </div>
    );
};

export default SystemGraph;
