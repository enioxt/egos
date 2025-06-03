import React from 'react';

export default function SystemExplorerPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">System Explorer</h1>
      <p className="mb-4">
        Explore the interconnectedness of the EGOS subsystems and documentation using the interactive visualization below.
      </p>
      {/* TODO: Investigate why data might not be loading in the iframe */}
      <div className="w-full h-[80vh] border rounded-lg overflow-hidden">
        <iframe
          src="/visualizations/cross_reference_network_enhanced.html"
          title="EGOS Cross-Reference Network Visualization"
          className="w-full h-full border-0"
        />
      </div>
    </div>
  );
}
