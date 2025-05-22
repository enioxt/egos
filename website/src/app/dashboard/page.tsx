/**
 * @file page.tsx
 * @description Main dashboard page for EGOS, integrating Cross-Reference Visualizer and Streamlit Dashboard.
 * @module app/dashboard/page
 * @version 0.2.0
 * @date 2025-05-21
 *
 * @references
 * - mdc:website/src/components/dashboard/CrossReferenceVisualizer.tsx (CrossReferenceVisualizer Component)
 * - mdc:docs_egos/products/dashboard/dashboard_feature_matrix.md (Feature Matrix)
 */

import React from 'react';
import CrossReferenceVisualizer from '@/components/dashboard/CrossReferenceVisualizer';
import ErrorBoundary from '@/components/ErrorBoundary';

export default function DashboardPage() {
  return (
    <main className="min-h-screen w-full flex flex-col items-center bg-background pt-8 pb-8 px-4 md:px-0">
      <div className="w-full max-w-6xl space-y-8">
        <h1 className="text-3xl font-bold text-foreground text-center md:text-left">
          EGOS Monitoring Dashboard
        </h1>

        {/* Cross-Reference Visualizer Section */}
        <div>
          <h2 className="text-2xl font-semibold text-foreground mb-4">Cross-Reference System Status</h2>
          <ErrorBoundary>
            <CrossReferenceVisualizer className="w-full" />
          </ErrorBoundary>
        </div>

        {/* Streamlit Dashboard Section */}
        <div>
          <h2 className="text-2xl font-semibold text-foreground mb-4">Overall System Monitoring (Streamlit)</h2>
          <div className="w-full h-[80vh] min-h-[600px] rounded-lg overflow-hidden shadow-lg border border-border bg-card">
            <iframe
              src="https://egosos.streamlit.app/"
              title="EGOS Streamlit Dashboard"
              width="100%"
              height="100%"
              style={{ border: 'none' }}
              allowFullScreen
            />
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            The Streamlit dashboard is hosted 24/7 on Streamlit Cloud and is synchronized with the <a href="https://github.com/enioxt/egos" target="_blank" rel="noopener noreferrer" className="underline text-primary hover:text-primary/80">EGOS GitHub repository</a>.<br />
            Alternatively, you can <a href="https://egosos.streamlit.app/" target="_blank" rel="noopener noreferrer" className="underline text-primary hover:text-primary/80">open the Streamlit dashboard in a new tab</a>.
          </p>
        </div>
      </div>
    </main>
  );
}
