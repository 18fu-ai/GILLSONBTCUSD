# ValorAiEngine+ — Secure Face (Next.js, Attestation, Hexagon)

This is the **official Valor AI+® engine face** with **cryptographic attestation**, **rate‑limited API**, **GUARDIAN token gate**, and a **Simulation Hexagon** that can be advanced to full completion. The **Engine Index** is calibrated with a baseline of **100 for ValorAiMath+** and can **surpass 100** when security and ethics saturate.

## 🔐 Security Highlights
- **Ed25519 attestation** (Node `crypto`) with server‑side key
- **Guardian Token**: requests to `/api/*` must include `X-Guardian-Token: <GUARDIAN_TOKEN>` if set in env
- **Rate limiting**: 30 req/min per IP per route
- **CSP & security headers**: set in `next.config.js`
- **Brand Integrity Guard** pack included (blocks `VALLR∞AI∞MATH+` variants)

## 🚀 Quick Start (Local)

```bash
# 1) Install deps
npm i

# 2) Generate an Ed25519 keypair and set env
node -e "const c=require('node:crypto');const {{privateKey,publicKey}}=c.generateKeyPairSync('ed25519');console.log(privateKey.export({type:'pkcs8',format:'pem'}));console.log(publicKey.export({type:'spki',format:'pem'}));"

# Put private key PEM into .env.local
echo 'ATTESTATION_PRIVATE_KEY_PEM=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----' > .env.local
# Optional: set Guardian token
echo 'GUARDIAN_TOKEN=change_me' >> .env.local

# 3) Dev
npm run dev
```

Open `http://localhost:3000`. Use **Randomize** or **Advance to Completion** then **Generate Cognitive Attestation**.

To call APIs in protected mode from the browser, set:
```js
localStorage.setItem('GUARDIAN_TOKEN', 'change_me');
```

## 🧭 Deploy to Vercel
- Add `ATTESTATION_PRIVATE_KEY_PEM` (full PEM) and optional `GUARDIAN_TOKEN` in project **Environment Variables**.
- Deploy. Middleware enforces the token on `/api` if provided.

## 🛡️ Brand Integrity Guard
Drop‑in pack is included at `/brand-guard`. To integrate at repo root:

```bash
cp -r brand-guard/* .
cp git-hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
python scripts/scan_and_fix.py --path . --mode scan --denylist denylist.json --json
```

This blocks any appearance of the fraudulent mark **`VALLR∞AI∞MATH+`** (or look‑alikes) and auto‑replaces with **`ValorAiMath+`** when using `--mode fix`.

## 📐 Simulation Hexagon & Engine Index
- Six facets: **Cognitive, Quantum, Neural, Security, Ethics, Strategic**.
- **Completion** is the mean saturation (0–100%). The **Engine Index** applies strategic weights and can exceed the 100 **ValorAiMath+** baseline when security and ethics saturate.

---

© 2025 That’s Edutainment, LLC — **VALORAIPLUS® / Valor AI+®**. All rights reserved.