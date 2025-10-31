import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const config = {
  matcher: ['/api/:path*']
};

export function middleware(req: NextRequest) {
  const token = req.headers.get('x-guardian-token') || '';
  const required = process.env.GUARDIAN_TOKEN || '';
  if (!required) {
    // If no token configured, allow but warn via header (for dev/demo).
    const res = NextResponse.next();
    res.headers.set('X-Guardian-Warn', 'GUARDIAN_TOKEN not set; API is open in this environment.');
    return res;
  }
  if (token !== required) {
    return new NextResponse(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'content-type': 'application/json' } });
  }
  return NextResponse.next();
}