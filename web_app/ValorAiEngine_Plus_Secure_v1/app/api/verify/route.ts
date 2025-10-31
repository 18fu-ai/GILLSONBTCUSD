import { NextRequest, NextResponse } from 'next/server';
import { rateLimit } from '../../../lib/rateLimit';
import { verifyState } from '../../../lib/attestation';

export async function POST(req: NextRequest) {
  const ip = req.headers.get('x-forwarded-for') || req.headers.get('x-real-ip') || 'unknown';
  const { allowed, remaining, resetAt } = rateLimit(`verify:${ip}`);
  if (!allowed) {
    return NextResponse.json({ error: 'Rate limit exceeded', resetAt }, { status: 429 });
  }

  try {
    const { state, signature, publicKeyPem } = await req.json();
    const ok = verifyState(state, signature, publicKeyPem);
    return NextResponse.json({ ok, rateLimit: { remaining, resetAt } });
  } catch (e: any) {
    return NextResponse.json({ error: e.message || 'Bad Request' }, { status: 400 });
  }
}