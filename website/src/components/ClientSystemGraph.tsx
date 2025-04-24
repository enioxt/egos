/**
 * @file ClientSystemGraph.tsx
 * @description Client-side wrapper for the SystemGraph component to ensure it only renders in the browser.
 * @module components/ClientSystemGraph
 * @version 1.0.0
 * @date 2025-04-23
 * @license MIT
 *
 * @references
 * - mdc:website/src/components/SystemGraph.tsx (Main Visualization Component)
 * - mdc:website/src/app/system-explorer/visualization/page.tsx (Usage Context)
 * - mdc:docs/process/cross_reference_visualization.md (Visualization Process)
 */

'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { FilterOptions } from './FilterControls';

// Dynamically import the SystemGraph component with no SSR
const SystemGraph = dynamic(() => import('./SystemGraph'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full w-full bg-gray-100 rounded-lg">
      <div className="text-center p-6">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-gray-600">Loading visualization...</p>
      </div>
    </div>
  ),
});

/**
 * Props interface for the ClientSystemGraph component
 */
interface ClientSystemGraphProps {
  /** Filter options to apply to the visualization */
  filters?: FilterOptions;
}

/**
 * ClientSystemGraph component that wraps the SystemGraph component
 * to ensure it only renders on the client side.
 * 
 * @param props Component props including optional filter options
 */
const ClientSystemGraph: React.FC<ClientSystemGraphProps> = ({ filters }) => {
  return <SystemGraph filters={filters} />;
};

export default ClientSystemGraph;
