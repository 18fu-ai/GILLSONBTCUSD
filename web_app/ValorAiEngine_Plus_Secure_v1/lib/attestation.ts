import { createPrivateKey, createPublicKey, sign as nodeSign, verify as nodeVerify, KeyObject } from 'node:crypto';

let PRIVATE_KEY_OBJ: KeyObject | null = null;
let PUBLIC_KEY_PEM: string | null = null;

function loadPrivateKey(): KeyObject {
  if (PRIVATE_KEY_OBJ) return PRIVATE_KEY_OBJ;
  const pem = process.env.ATTESTATION_PRIVATE_KEY_PEM;
  if (!pem) {
    throw new Error('ATTESTATION_PRIVATE_KEY_PEM not set (ED25519 PKCS#8 PEM).');
  }
  PRIVATE_KEY_OBJ = createPrivateKey(pem);
  return PRIVATE_KEY_OBJ;
}

function ensurePublicKeyPem(): string {
  if (PUBLIC_KEY_PEM) return PUBLIC_KEY_PEM;
  const priv = loadPrivateKey();
  const pub = createPublicKey(priv);
  PUBLIC_KEY_PEM = pub.export({ type: 'spki', format: 'pem' }).toString();
  return PUBLIC_KEY_PEM;
}

export function publicKeyPem(): string {
  return ensurePublicKeyPem();
}

export function signState(state: unknown): { signature: string; publicKeyPem: string; digestHex: string } {
  const payload = Buffer.from(JSON.stringify(state));
  // For transparency, sign the raw payload (could hash first; ED25519 signs message directly)
  const priv = loadPrivateKey();
  const sig = nodeSign(null, payload, priv); // null for ed25519
  const pubPem = ensurePublicKeyPem();
  const digestHex = require('node:crypto').createHash('sha256').update(payload).digest('hex');
  return { signature: sig.toString('base64'), publicKeyPem: pubPem, digestHex };
}

export function verifyState(state: unknown, signatureB64: string, publicKeyPemStr: string): boolean {
  try {
    const payload = Buffer.from(JSON.stringify(state));
    const pub = createPublicKey(publicKeyPemStr);
    const ok = nodeVerify(null, payload, pub, Buffer.from(signatureB64, 'base64'));
    return ok;
  } catch {
    return false;
  }
}