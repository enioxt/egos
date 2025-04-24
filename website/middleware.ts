/**
 * @metadata
 * @description Middleware for handling internationalization (DISABLED)
 * @koios_ref CORUJA-I18N-MIDDLEWARE-001
 * @references 
 * - `mdc:website/next-intl.config.js` (next-intl configuration)
 * - `mdc:website/src/app/layout.tsx` (root layout with i18n)
 */

// Middleware is temporarily disabled to move all content to the root path
// This prevents automatic redirects to locale-based paths like /en
export function middleware() {
  // No-op middleware - pass through all requests
  return;
}

export const config = {
  // Match all pathnames except for static files, API routes, etc.
  matcher: ['/((?!api|_next|.*\\..*).*)']  
};
