# Integration Guide (Quick)
1. Deploy the secure engine app (see `engine/ValorAiEngine_Plus_Secure_v1.zip`).
2. Set `ATTESTATION_PRIVATE_KEY_PEM` and optional `GUARDIAN_TOKEN` in your runtime.
3. Call `/api/attest` with the engine state JSON to receive `{ signature, publicKeyPem, digestHex }`.
4. Verify on your side:
   - Compute SHA-256 over the JSON payload bytes.
   - Verify Ed25519 signature against the `publicKeyPem`.
5. Store or broadcast the attestation as needed.