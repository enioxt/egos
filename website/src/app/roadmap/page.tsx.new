/**
 * @file page.tsx (roadmap)
 * @description Full roadmap page that shows all EGOS project tasks
 * @module app/roadmap/page
 * @version 1.0.0
 * @date 2025-04-24
 * @license MIT
 *
 * @references
 * - mdc:website/src/components/Roadmap.tsx (Main Roadmap component)
 * - mdc:website/src/data/roadmapData.ts (Task data structure)
 */

'use client';

import React from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { Button } from '@/components/ui/button';

// Use dynamic import to prevent any SSR/hydration issues with the complex component
const Roadmap = dynamic(() => import('@/components/Roadmap').then(mod => mod.Roadmap), {
  ssr: true,
  loading: () => <div className="p-4 text-center">Loading roadmap data...</div>
});

export default function RoadmapPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="flex flex-col gap-6">
        <div className="flex items-center"> 
          <Link href="/" passHref>
            <Button variant="outline" className="mb-2">&larr; Back to Home</Button>
          </Link>
        </div>
        
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-3">EGOS Project Roadmap</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Complete view of all tasks and initiatives across the EGOS ecosystem
          </p>
        </div>
        
        {/* Display the full roadmap with showAll option enabled */}
        <Roadmap showAll={true} />
      </div>
    </div>
  );
}
