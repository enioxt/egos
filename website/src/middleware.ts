import { NextRequest, NextResponse } from 'next/server';

/**
 * @metadata
 * @description No-op middleware for non-i18n routing setup
 * @koios_ref CORUJA-I18N-MIDDLEWARE-001
 * @references 
 * - `mdc:website/src/app/layout.tsx` (Handles i18n in layout)
 * - `mdc:website/src/i18n.ts` (i18n config)
 */

export function middleware(request: NextRequest) {
  // Pass through the request without modification
  return NextResponse.next();
}

export const config = {
  // Empty matcher effectively disables the middleware for all paths
  matcher: [], 
};
