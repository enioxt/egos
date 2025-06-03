'use client';

/**
 * @file HomeContent.tsx
 * @description Client component for the homepage content
 * @module components/HomeContent
 * @version 1.0.0
 * @date 2025-04-24
 * @license MIT
 * 
 * @references
 * - mdc:website/src/components/Hero.tsx
 * - mdc:website/src/components/Principles.tsx
 * - mdc:website/src/components/Subsystems.tsx
 * - mdc:website/src/components/Roadmap.tsx
 * - mdc:website/src/components/Visualization.tsx
 * - mdc:website/src/components/CallToAction.tsx
 */

import { Hero } from '@/components/Hero';
import { Principles } from '@/components/Principles';
import { Subsystems } from '@/components/Subsystems';
import { Roadmap } from '@/components/Roadmap';
import { Visualization } from '@/components/Visualization';
import { CallToAction } from '@/components/CallToAction';

export function HomeContent() {
  return (
    <>
      <Hero />
      <Principles />
      <Subsystems />
      <Roadmap />
      <Visualization />
      <CallToAction />
    </>
  );
}
