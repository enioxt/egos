/**
 * @file page.tsx (root)
 * @description Main homepage for the EGOS website
 * @module app/page
 * @version 1.0.0
 * @date 2025-04-24
 * @license MIT
 *
 * @references
 * - mdc:website/src/app/layout.tsx (Root Layout)
 * - mdc:website/src/components/HomeContent.tsx (Client-side content wrapper)
 */

// Dynamic import for the client component to ensure proper bundling
import dynamic from 'next/dynamic';

// Import HomeContent with explicit path to avoid path resolution issues
const HomeContent = dynamic(() => import('../components/HomeContent').then(mod => mod.HomeContent), {
  ssr: true,
  loading: () => <div className="p-8 text-center">Loading EGOS homepage content...</div>
});

export const metadata = {
  title: 'EGOS - Ethical Global Operating System',
  description: 'The homepage for the Ethical Global Operating System (EGOS)',
};

export default function Home() {
  console.log('[Root Page] Rendering HomeContent');
  return <HomeContent />;
}
