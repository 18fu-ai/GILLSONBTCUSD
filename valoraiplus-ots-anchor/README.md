# VALORAIPLUS® Sovereign OTS Genesis Anchor

## Overview
Production-grade Python engine for computing tamper-evident digests from JSON manifests and anchoring to Bitcoin via OpenTimestamps (OTS). Supports evidence preservation for legal/compliance use. Grounded in SHA-256 + SHA3-256 (Keccak approx). No unsubstantiated claims — verifiable proof-of-existence only.

## Features
- Canonical JSON hashing for determinism.
- Double-lock digest (SHA-256 + SHA3-256).
- JSON broadcast archive for audits.
- Real Bitcoin anchoring via OTS (install opentimestamps-client).
- Litigation-grade: Timestamps, authority seals, constitutional refs.

## Installation
1. Clone repo: `git clone https://github.com/donadams1969/valoraiplus-ots-anchor.git`
2. Install deps: `pip install -r requirements.txt`
3. For real OTS: `pip install opentimestamps-client` (anchors to Bitcoin mainnet calendars).

## Usage
```bash
python valoraiplus_ots_anchor.py VALORAIPLUS_Manifest_v54.json
```
- Input: JSON manifest (e.g., with leaves, merkle_root, valuation).
- Output: Digest hex, broadcast JSON, .ots proof file (if OTS installed).
- Verify OTS: `ots verify manifest.json.ots`

## Dependencies (requirements.txt)
See below.

## License
MIT — Open-source, reproducible. © Donny Gillson Poppa® 2026.

## Disclaimer
Provides cryptographic integrity; no legal guarantees. Use for anchoring only — consult attorneys for evidentiary value.
