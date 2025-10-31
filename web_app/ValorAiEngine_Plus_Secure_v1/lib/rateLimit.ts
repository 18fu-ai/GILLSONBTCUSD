type Bucket = { count: number; resetAt: number };

const WINDOW_MS = 60_000; // 60s window
const MAX_REQ = 30;       // 30 requests per window

const store: Map<string, Bucket> = new Map();

export function rateLimit(key: string): { allowed: boolean; remaining: number; resetAt: number } {
  const now = Date.now();
  const b = store.get(key);
  if (!b || now > b.resetAt) {
    const nb = { count: 1, resetAt: now + WINDOW_MS };
    store.set(key, nb);
    return { allowed: true, remaining: MAX_REQ - 1, resetAt: nb.resetAt };
  }
  if (b.count >= MAX_REQ) {
    return { allowed: false, remaining: 0, resetAt: b.resetAt };
  }
  b.count += 1;
  return { allowed: true, remaining: MAX_REQ - b.count, resetAt: b.resetAt };
}