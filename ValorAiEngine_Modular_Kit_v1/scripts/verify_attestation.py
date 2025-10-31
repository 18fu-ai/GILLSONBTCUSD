#!/usr/bin/env python3
# Verify an attestation JSON using ed25519
import sys, json, base64
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
except Exception as e:
    print("This tool requires 'cryptography' package. Install via: pip install cryptography")
    sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: verify_attestation.py attestation.json")
        sys.exit(1)
    data = json.loads(open(sys.argv[1], "r", encoding="utf-8").read())
    state = data["state"]
    signature_b64 = data["signature"]
    pub_pem = data["publicKeyPem"]
    payload = json.dumps(state, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sig = base64.b64decode(signature_b64)
    pub = serialization.load_pem_public_key(pub_pem.encode("utf-8"))
    try:
        pub.verify(sig, payload)
        print("VALID: signature verifies for the provided state JSON")
        sys.exit(0)
    except Exception as e:
        print("INVALID:", e)
        sys.exit(2)

if __name__ == "__main__":
    main()