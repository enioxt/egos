/**
 * @file Visualization.tsx
 * @description Feature component showcasing the system cross-reference visualization
 * @module components/Visualization
 * @version 1.0.0
 * @date 2025-04-23
 * @license MIT
 *
 * @references
 * - mdc:website/src/components/SystemGraph.tsx (Main Visualization Component)
 * - mdc:website/src/app/system-explorer/visualization/page.tsx (Visualization Page)
 * - mdc:docs/process/cross_reference_visualization.md (Visualization Process)
 * - mdc:docs/process/cross_reference_visualization_implementation.md (Implementation Documentation)
 */

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { NetworkIcon } from './svg/NetworkIcon';

export const Visualization = () => {
  return (
    <section id="visualization" className="py-16 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="order-2 lg:order-1">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-6">
              System Visualization
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Explore the interconnections within EGOS through our interactive 
              cross-reference network visualization. Discover how documents, components, 
              and subsystems relate to each other in a dynamic graph representation.
            </p>
            <ul className="space-y-4 mb-8">
              <li className="flex items-start">
                <span className="text-primary mr-2">•</span>
                <span className="text-muted-foreground">
                  Interactive visualization showing files and their relationships
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-2">•</span>
                <span className="text-muted-foreground">
                  Identify core files and high-reference components
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-2">•</span>
                <span className="text-muted-foreground">
                  Discover interconnections between subsystems
                </span>
              </li>
            </ul>
            <Link 
              href="/system-explorer/visualization" 
              className="inline-flex items-center px-6 py-3 rounded-md bg-primary hover:bg-primary/90 text-primary-foreground transition-colors"
            >
              <NetworkIcon className="w-5 h-5 mr-2" />
              Explore Visualization
            </Link>
          </div>
          <div className="order-1 lg:order-2 relative">
            <div className="aspect-video bg-gradient-to-br from-card to-accent/20 rounded-lg shadow-xl overflow-hidden border border-accent/30 relative">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative w-full h-full">
                  <Image 
                    src="/images/visualization-preview.svg" 
                    alt="EGOS Cross-Reference Network Visualization" 
                    fill 
                    className="object-contain p-4"
                    priority
                  />
                </div>
              </div>
              <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent flex items-end justify-center p-6">
                <Link 
                  href="/system-explorer/visualization" 
                  className="px-4 py-2 rounded-md bg-background/80 backdrop-blur-sm hover:bg-background text-foreground border border-accent/50 transition-all"
                >
                  View Interactive Visualization
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
