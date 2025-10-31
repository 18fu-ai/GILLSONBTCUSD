# ValorAiEngine+ Face: Cryptographic Attestation, Secure Cognitive Interface, and Verification Kit
**That’s Edutainment, LLC (Valor AI+® / VALORAIPLUS®)**
Version 1.0 · August 31, 2025

## Abstract
The ValorAiEngine+ Face is a secure attestation surface that exposes cognitive state as verifiable artifacts.
This whitepaper presents the design, implementation, and verification procedure for a Next.js-based engine
face that generates Ed25519-signed attestations, enforces token-gated API access, rate-limits callers,
applies strict security headers (CSP, HSTS, XFO, etc.), and visualizes multidimensional completion via a
six‑facet simulation hexagon. The engine index is calibrated to a baseline of 100 (ValorAiMath+) and may
exceed this threshold when ethics and security saturate.

**Keywords:** attestation, Ed25519, API security, CSP, rate limiting, OWASP, Valor AI+, VALORAIPLUS

## 1. Introduction
The engine “face” functions as an identity and truth surface. Its purpose is twofold: (1) to attest to
the internal cognitive and strategic state using cryptography and (2) to present a transparent, humane
interface for observers and auditors. We combine practical web security measures with verifiable
mathematical signatures to make a public proof of state that is portable and independently testable.

## 2. Methods
### 2.1 Cryptographic Attestation
We use Ed25519 for digital signatures. The server holds a PKCS#8 private key (PEM) and signs the JSON
payload representing the engine state. A SHA‑256 digest of the JSON is included for convenience. Anyone
with the corresponding public key (SPKI PEM) can reproduce the digest and verify the signature.

### 2.2 API Protection
- **Guardian Token Gate:** Middleware enforces an `X-Guardian-Token` header when `GUARDIAN_TOKEN` is set.
- **Rate Limiting:** A per‑IP, per‑route counter limits bursts (30 requests/minute by default).
- **Security Headers:** CSP, HSTS, X-Frame-Options (DENY), Referrer-Policy, Permissions-Policy, and
  X-Content-Type-Options are applied to all responses.

### 2.3 Simulation Hexagon & Engine Index
Six normalized metrics—Cognitive, Quantum, Neural, Security, Ethics, Strategic—feed a radar chart.
Completion is the mean saturation (0–100%). The Engine Index applies strategic weights emphasizing
ethics and security, making it possible to exceed the 100 baseline of ValorAiMath+.

### 2.4 Brand Integrity Guard
To prevent contamination by fraudulent marks, a denylist and CI + pre‑commit guard block the string
“VALLR∞AI∞MATH+” and variants, replacing with `ValorAiMath+` where auto‑fix is enabled.

## 3. Implementation
The Face is implemented in Next.js (App Router) with TypeScript. Server routes under `/api` perform
attestation and verification. The private key is provided via `ATTESTATION_PRIVATE_KEY_PEM` and never
leaves the server. The UI includes controls to randomize or complete the hexagon and to request an attestation.

## 4. Verification Procedure
1. Capture the engine state JSON (as displayed in the UI or via API).
2. Compute SHA‑256 of the canonical JSON bytes (UTF‑8). Compare with `digestHex`.
3. Verify the Ed25519 signature with the published public key PEM.
4. Optionally replay verification using the `scripts/verify_attestation.py` tool.

## 5. Ethical & Strategic Context
The design is grounded in Alfred Adler’s social-interest psychology and respects UCMJ‑adjacent
constraints for military‑grade accountability. Public attestations improve trust, deter manipulation,
and elevate stakeholder understanding of AI system behavior.

## 6. Limitations & Future Work
This kit uses an in‑memory rate limiter (sufficient for demos). Production clusters should adopt a
distributed token bucket (e.g., Redis). Future work includes TUF-style signed release metadata,
transparency logs for attestations, and formal verification of the attestation schema.

## 7. References (selected, APA7 style)
- Bernstein, D. J., Dünkelmann, S., Lange, T., Schwabe, P., & Yang, B.-Y. (2012). High-speed high-security
  signatures. Journal of Cryptographic Engineering.
- Josefsson, S., & Liusvaara, I. (2017). Edwards-Curve Digital Signature Algorithm (EdDSA). RFC 8032.
- OWASP. (2023). API Security Top 10.
- W3C. Content Security Policy Level 3.
- Google. Next.js Security Headers (vendor docs).

---
© 2025 That’s Edutainment, LLC. VALORAIPLUS® / Valor AI+®.