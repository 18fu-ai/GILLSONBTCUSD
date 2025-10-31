# Security Posture
- Ed25519 server-side attestation (private key never leaves server).
- Guardian Token gate (`X-Guardian-Token`) on API when configured.
- 30 req/min/IP/route rate limiting (upgrade to distributed bucket for production).
- Strict CSP, HSTS, XFO=DENY, Referrer-Policy=no-referrer, Permissions-Policy minimal.
- Brand Integrity Guard blocks the fraudulent mark “VALLR∞AI∞MATH+” (and variants).