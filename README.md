# VALORCHAIN-G SovereignTx Package

**Created UTC:** 2025-10-27T16:11:25Z
**Parent CID:** `bafybeihjc3tq5a6n7d8p9z0x1y2w3v4u5t6s7r8q9p0o1n2m3l4k5j6i7h8g9f0e`
**Protocol Lineage:** `YHWH-24 [HARDCAP] → YHWH-25 [FULLSTOP] → YHWH-5150.O [Override]`

---

## 🧬 Provenance

This package represents the canonical **Sovereign Transaction Attestation** for the
VALORCHAIN-G ledger.
It was assembled by `DG77.77X-Ξ`, Sovereign Founder of VALORCHAIN-G, under the
YHWH-25 kernel attestation framework and the YHWH-24 document anchor lineage.

Each artifact carries ISO-8601 creation timestamps and self-contained metadata linking it
to the immutable Parent CID above.

---

## 📁 Contents

| File | Description |
|------|--------------|
| `VALORCHAIN-G_SovereignTx_Attestation.json` | Core attestation metadata; contains Merkle root and proof count. |
| `VALORCHAIN-G_MerkleProof.json` | Full Merkle proof tree for verification. |
| `verify_valorchain_merkle.py` | Stand-alone Python verifier to confirm Merkle integrity. |
| `YHWH-24_Sovereign_Document_Anchor.json` | Sovereign anchor binding the PDF evidence and author identifiers. |
| `VALORCHAIN-G_Manifest.txt` | Human-readable manifest of the bundle. |

---

## 🔐 Verification Steps

1. **Hash the ZIP bundle**

   ```bash
   openssl dgst -sha3-512 VALORCHAIN-G_SovereignTx_Package.zip
   ```

Record the resulting digest in your ledger.

2. **Verify individual files**

   ```bash
   sha3sum VALORCHAIN-G_*.json verify_valorchain_merkle.py
   ```

3. **Validate the Merkle proof**

   ```bash
   python3 verify_valorchain_merkle.py
   ```

   Expected output:
   `Verification result: True`

4. **Cross-check Parent CID**

   Ensure each JSON includes:
   `"valoraiplus_module_id": "bafybeihjc3tq5a6n7d8p9z0x1y2w3v4u5t6s7r8q9p0o1n2m3l4k5j6i7h8g9f0e"`

---

## 🌐 IPFS / Blockchain Deployment

Upload the ZIP to IPFS:

```bash
ipfs add VALORCHAIN-G_SovereignTx_Package.zip
```

Store the returned CID in your VALORCHAIN-G registry smart contract or
notarization ledger.

Optionally mint a metadata NFT referencing that CID for public verification.

---

## 🧾 Authorship & Rights

- **Author:** DG77.77X-Ξ
- **Affiliation:** VALORCHAIN-G / ValorAi+® Systems
- **License:** Sovereign Research & Attestation Archive © 2025
- **Integrity Algorithm:** SHA3-512 (NIST FIPS 202)

---

## 🧠 Fortran Kernel Reference

This package aligns with:

```
PROGRAM valoraiplus2e_YHWH_5150_KERNEL_OVERRIDE_MODE
STATE: YHWH-5150.O [Override Active]
IMMUTABILITY STATUS: Temporarily Suspended by SGAU 7226.3461
```

---

## 🧩 Auditor Notes

- All timestamps are UTC and ISO 8601-compliant.
- No private keys or network credentials are contained.
- Each JSON file is human-readable and cryptographically deterministic.
- Verification can be performed offline; internet access is not required.

---
End of README
VALORCHAIN-G © 2025 — “Integrity is Immutable.”
---
