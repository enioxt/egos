/**
 * @file cross-reference-explorer/page.tsx
 * @description Cross-Reference Explorer page component that provides interactive visualization 
 *              and management of documentation cross-references.
 * @module app/cross-reference-explorer/page
 * @version 1.0.0
 * @date 2025-05-21
 * 
 * @references
 * - mdc:website/ROADMAP.md#cross-reference-standardization (Initiative: Cross-Reference Standardization)
 * - mdc:docs_egos/08_tooling_and_scripts/reference_implementations/file_reference_checker_ultra.md (Tool Documentation)
 * - mdc:scripts/cross_reference/integration/INTEGRATION_DESIGN.md (Integration Architecture)
 * - mdc:website/src/components/SystemGraph.tsx (Graph Visualization Component)
 */

import React from 'react';
import { Metadata } from 'next';
import CrossReferenceExplorer from '@/components/cross-reference/CrossReferenceExplorer';
import { PageHeader } from '@/components/layout/PageHeader';

export const metadata: Metadata = {
  title: 'Cross-Reference Explorer | EGOS',
  description: 'Interactive visualization and management of documentation cross-references across the EGOS ecosystem',
};

export default function CrossReferencePage() {
  return (
    <main className="container mx-auto px-4 py-8">
      <PageHeader 
        title="Cross-Reference Explorer" 
        subtitle="Visualize, analyze, and manage documentation integrity across the EGOS ecosystem"
        icon="network"
      />
      
      <section className="my-8">
        <div className="prose max-w-none mb-8">
          <p className="text-lg">
            The Cross-Reference Explorer provides an interactive view of all documentation and code references, 
            helping identify broken links, orphaned files, and critical reference implementations.
          </p>
        </div>
        
        {/* Main visualization component */}
        <div className="border rounded-lg bg-card shadow-sm h-[calc(100vh-300px)] min-h-[600px]">
          <CrossReferenceExplorer />
        </div>
      </section>
    </main>
  );
}
