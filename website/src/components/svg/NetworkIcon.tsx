/**
 * @file NetworkIcon.tsx
 * @description Network icon component for the visualization feature
 * @module components/svg/NetworkIcon
 * @version 1.0.0
 * @date 2025-04-23
 * @license MIT
 *
 * @references
 * - mdc:website/src/components/svg/IconsSvg.tsx (Icon Collection)
 * - mdc:website/src/components/Visualization.tsx (Usage Context)
 */

import React from 'react';

interface NetworkIconProps {
  className?: string;
}

export const NetworkIcon = ({ className }: NetworkIconProps) => (
  <svg className={className} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="24" r="16" fill="#00AEEF" opacity="0.3" />
    <circle cx="17" cy="17" r="5" fill="#FFB3C1" stroke="#0A0A0A" strokeWidth="2" />
    <circle cx="34" cy="24" r="5" fill="#A5E887" opacity="0.7" stroke="#0A0A0A" strokeWidth="2" />
    <circle cx="17" cy="34" r="5" fill="#E8D9F0" opacity="0.7" stroke="#0A0A0A" strokeWidth="2" />
    <path 
      d="M20.5 20.5L30 24M20.5 30L30 24" 
      stroke="#0A0A0A" 
      strokeWidth="2" 
      strokeLinecap="round" 
    />
  </svg>
);

export default NetworkIcon;
