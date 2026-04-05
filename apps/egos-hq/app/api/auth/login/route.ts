import { NextRequest, NextResponse } from 'next/server';
import { SignJWT } from 'jose';

const JWT_SECRET = new TextEncoder().encode(
  process.env.DASHBOARD_MASTER_SECRET ?? 'egos-hq-dev-secret-change-in-prod'
);

export async function POST(req: NextRequest) {
  const { secret } = await req.json();
  const expected = process.env.DASHBOARD_MASTER_SECRET ?? 'egos-hq-dev-secret-change-in-prod';

  if (!secret || secret !== expected) {
    return NextResponse.json({ error: 'Invalid credentials' }, { status: 401 });
  }

  const token = await new SignJWT({ sub: 'enio', role: 'admin' })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('7d')
    .sign(JWT_SECRET);

  const res = NextResponse.json({ ok: true });
  res.cookies.set('hq_session', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: '/',
  });
  return res;
}
