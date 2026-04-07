import { NextRequest, NextResponse } from 'next/server';

const PROTECTED_PREFIXES = ['/dashboard-v1', '/dashboard-v2', '/dashboard-v3', '/x-dashboard'];

function isProtected(pathname: string): boolean {
  return PROTECTED_PREFIXES.some(p => pathname.startsWith(p));
}

export function middleware(req: NextRequest): NextResponse {
  const { pathname } = req.nextUrl;

  if (!isProtected(pathname)) {
    return NextResponse.next();
  }

  const secret = process.env.DASHBOARD_SECRET;
  if (!secret) {
    // No secret configured — block access entirely in production
    if (process.env.NODE_ENV === 'production') {
      return new NextResponse('Dashboard not configured.', { status: 503 });
    }
    return NextResponse.next(); // Allow in local dev if no secret set
  }

  const authHeader = req.headers.get('authorization') ?? '';
  const [scheme, encoded] = authHeader.split(' ');

  if (scheme === 'Basic' && encoded) {
    const decoded = Buffer.from(encoded, 'base64').toString('utf-8');
    const [, password] = decoded.split(':');
    if (password === secret) {
      return NextResponse.next();
    }
  }

  return new NextResponse('Unauthorized', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="Guard Brasil Dashboard"',
    },
  });
}

export const config = {
  matcher: ['/dashboard-v1/:path*', '/dashboard-v2/:path*', '/dashboard-v3/:path*', '/x-dashboard/:path*'],
};
