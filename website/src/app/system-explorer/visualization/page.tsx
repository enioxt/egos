/**
 * @file page.tsx
 * @description System Cross-Reference Visualization page using the Sigma.js graph visualization.
 * @module app/system-explorer/visualization
 * @version 1.0.0
 * @date 2025-04-23
 * @license MIT
 *
 * @references
 * - mdc:website/ROADMAP.md#vis-int-001 (Task: Integrate Sigma Visualization Component)
 * - mdc:website/ROADMAP.md#vis-005 (Task: Add filtering capabilities)
 * - mdc:website/src/components/SystemGraph.tsx (Visualization Component)
 * - mdc:website/src/components/FilterControls.tsx (Filter Controls Component)
 * - mdc:docs/process/cross_reference_visualization.md (Visualization Process)
 * - mdc:docs/guides/SYSTEM_VISUALIZATION_GUIDE.md (User Guide)
 */

'use client';

import React, { useState, useEffect } from 'react';
import ClientSystemGraph from '@/components/ClientSystemGraph';
import FilterControls, { FilterOptions } from '@/components/FilterControls';
import { extractFileTypes, extractSubsystems } from '@/utils/graphDataUtils';

/**
 * SystemVisualizationPage component for rendering the cross-reference network visualization.
 * This page integrates the SystemGraph component which handles the Sigma.js visualization.
 * It also includes filter controls for customizing the visualization view.
 */
export default function SystemVisualizationPage() {
  // State for filters
  const [filters, setFilters] = useState<FilterOptions>({
    fileTypes: [],
    subsystems: [],
    minConnections: 0,
    showCore: null
  });
  
  // State for available filter options
  const [availableFileTypes, setAvailableFileTypes] = useState<string[]>([]);
  const [availableSubsystems, setAvailableSubsystems] = useState<string[]>([]);
  
  // Load available filter options on mount
  useEffect(() => {
    // Extract unique file types and subsystems from graph data
    setAvailableFileTypes(extractFileTypes());
    setAvailableSubsystems(extractSubsystems());
  }, []);
  
  // Handle filter changes
  const handleFilterChange = (newFilters: FilterOptions) => {
    setFilters(newFilters);
  };
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">EGOS Cross-Reference Network</h1>
      <div className="mb-6 space-y-3 text-gray-600">
        <p>
          This interactive visualization maps the interconnections between files in the EGOS ecosystem,
          revealing the underlying structure and relationships that embody our <strong>Conscious Modularity</strong> and <strong>Systemic Cartography</strong> principles.
        </p>
        <p>
          Each node represents a file in the codebase, with edges showing cross-references between files.
          The size of nodes indicates the number of connections, highlighting central components in our ecosystem.
          Colors represent different subsystems within EGOS.
        </p>
        <p>
          Explore this living map to discover how information and functionality flow through the system,
          identify key integration points, and understand the holistic architecture of EGOS.
        </p>
      </div>
      
      <div className="bg-white rounded-lg shadow-lg p-4 mb-8">
        <h2 className="text-xl font-semibold mb-4">Visualization Controls</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-medium mb-2">Basic Navigation</h3>
            <ul className="list-disc pl-6 mb-4 text-sm space-y-1">
              <li><strong>Zoom:</strong> Use mouse wheel or pinch gesture to zoom in/out</li>
              <li><strong>Pan:</strong> Click and drag on the background to move around</li>
              <li><strong>Reset View:</strong> Double-click on the background to reset the view</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-medium mb-2">Node Interaction</h3>
            <ul className="list-disc pl-6 mb-4 text-sm space-y-1">
              <li><strong>Select Node:</strong> Click on a file node to highlight its direct connections</li>
              <li><strong>Node Details:</strong> Hover over a node to see file details and metadata</li>
              <li><strong>Move Node:</strong> Drag individual nodes to rearrange the layout</li>
            </ul>
          </div>
        </div>
        <div className="mt-2 text-sm">
          <h3 className="text-lg font-medium mb-2">Understanding the Visualization</h3>
          <ul className="list-disc pl-6 text-sm space-y-1">
            <li><strong>Node Size:</strong> Larger nodes have more connections (higher centrality)</li>
            <li><strong>Node Color:</strong> Represents the subsystem the file belongs to</li>
            <li><strong>Edge Thickness:</strong> Indicates the strength of the relationship between files</li>
            <li><strong>Clusters:</strong> Files that are closely related tend to group together</li>
          </ul>
        </div>
      </div>
      
      <FilterControls
        onFilterChange={handleFilterChange}
        fileTypes={availableFileTypes}
        subsystems={availableSubsystems}
      />
      
      <div className="h-[700px] border border-gray-300 rounded-lg overflow-hidden">
        <ClientSystemGraph filters={filters} />
      </div>
      
      <div className="mt-6 text-sm text-gray-500">
        <p>
          This visualization is powered by Sigma.js and uses the ForceAtlas2 layout algorithm to position nodes.
          Data is sourced from the EGOS cross-reference analysis system, which continuously maps relationships
          between files as the project evolves.
        </p>
        <p className="mt-3">
          <strong>Tip:</strong> For the best experience, try focusing on one subsystem at a time by selecting a node
          from that subsystem and exploring its connections. This helps understand the internal structure of each
          component while revealing cross-subsystem integration points.
        </p>
        <p className="mt-2">
          <strong>Last Updated:</strong> {new Date().toLocaleDateString()}
        </p>
      </div>
    </div>
  );
}
