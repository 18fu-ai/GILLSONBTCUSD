import { NextRequest, NextResponse } from 'next/server';
import { rateLimit } from '../../../lib/rateLimit';
import { signState } from '../../../lib/attestation';

export async function POST(req: NextRequest) {
  const ip = req.headers.get('x-forwarded-for') || req.headers.get('x-real-ip') || 'unknown';
  const { allowed, remaining, resetAt } = rateLimit(`attest:${ip}`);
  if (!allowed) {
    return NextResponse.json({ error: 'Rate limit exceeded', resetAt }, { status: 429 });
  }

  try {
    const state = await req.json();
    const att = signState(state);
    return NextResponse.json({ ...att, rateLimit: { remaining, resetAt } });
  } catch (e: any) {
    return NextResponse.json({ error: e.message || 'Bad Request' }, { status: 400 });
  }
}