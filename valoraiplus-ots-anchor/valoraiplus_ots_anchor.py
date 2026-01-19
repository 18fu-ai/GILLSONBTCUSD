"""
VALORAIPLUS® Sovereign OTS Genesis Anchor v54.0.0
Author: Donny Gillson Poppa® (DG77.77X-Ξ)
Node: Saint Paul, MN
Purpose: Compute double-lock digest from JSON manifest and anchor to Bitcoin via OpenTimestamps.
Dependencies: Standard lib + opentimestamps-client + eth-hash[pycryptodome].
Disclaimer: Provides proof-of-existence; no legal authority implied. Use for evidence anchoring only.
"""

import hashlib
import json
from datetime import datetime, timezone
import sys
import os
import argparse
import subprocess
import tempfile
import shutil

# Check for OTS CLI availability
OTS_CLI_AVAILABLE = shutil.which("ots") is not None

try:
    from eth_hash.auto import keccak
    ETH_HASH_AVAILABLE = True
except ImportError:
    ETH_HASH_AVAILABLE = False
    print("Warning: eth-hash not installed. Install via 'pip install eth-hash[pycryptodome]'.")

def keccak256_bytes(data: bytes) -> bytes:
    if ETH_HASH_AVAILABLE:
        return keccak(data)
    else:
        # Fallback if eth-hash is missing (though requirements specify it)
        # Note: This fallback is the NIST SHA3, not true Keccak-256
        return hashlib.sha3_256(data).digest()

def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def hex0x(b: bytes) -> str:
    return "0x" + b.hex()

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

class ValorAiOTSMatrix:
    def __init__(self, manifest_file: str, mode: str = "keccak"):
        self.manifest_file = manifest_file
        self.mode = mode
        self.broadcast_record_file = "VALORAIPLUS_OTS_Broadcast_v54.json"
        self.ots_file = f"{manifest_file}.ots"

    def load_manifest(self) -> dict:
        if not os.path.exists(self.manifest_file):
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_file}")
        with open(self.manifest_file, 'r') as f:
            return json.load(f)

    def canonicalize_manifest(self, manifest_data: dict) -> str:
        return json.dumps(manifest_data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

    def run(self):
        manifest_data = self.load_manifest()
        canon_manifest = self.canonicalize_manifest(manifest_data)
        canon_bytes = canon_manifest.encode("utf-8")

        digest_sha256 = sha256_bytes(canon_bytes)
        digest_keccak = keccak256_bytes(canon_bytes)
        digest_double = keccak256_bytes(digest_sha256)

        anchor_digest_bytes = b""
        anchor_mode = ""

        if self.mode == "keccak":
            anchor_digest_bytes = digest_keccak
            anchor_mode = "keccak256(canonical_json)"
        elif self.mode == "sha256":
            anchor_digest_bytes = digest_sha256
            anchor_mode = "sha256(canonical_json)"
        else:
            anchor_digest_bytes = digest_double
            anchor_mode = "keccak256(sha256(canonical_json))"

        anchor_digest = hex0x(anchor_digest_bytes)

        print("--- VALORAIPLUS® OTS BROADCAST INITIALIZED ---")
        print(f"MODE: {self.mode}")
        print(f"ANCHOR DIGEST: {anchor_digest}")

        broadcast_record = {
            "protocol": "VALORAIPLUS_GENESIS_OTS",
            "version": "v54.0.0",
            "timestamp_utc": utc_now_iso(),
            "authority": "DG77.77X-Ξ",
            "input_manifest": os.path.basename(self.manifest_file),
            "canonicalization": "json.dumps(sort_keys=True,separators=(',',':'),ensure_ascii=False) UTF-8",
            "commitment_mode": anchor_mode,
            "commitments": {
                "sha256_canon_json": hex0x(digest_sha256),
                "keccak256_canon_json": hex0x(digest_keccak),
                "double_lock_sha256_to_keccak": hex0x(digest_double),
                "selected_anchor_digest": anchor_digest,
            },
            "manifest_fields": {
                "merkle_root": manifest_data.get("merkle_root") or manifest_data.get("merkle_root_anchor") or "N/A",
                "schema": manifest_data.get("schema", "N/A"),
                "manifest_version": manifest_data.get("version", "N/A"),
            },
            "ots": {"stamped": False, "method": None, "proof_file": None},
        }

        # OTS Anchoring via CLI
        if OTS_CLI_AVAILABLE:
            try:
                # Create a detached file containing just the digest bytes to stamp
                # Note: OTS usually stamps a FILE. If we want to stamp the digest as a "detached" timestamp
                # representing the manifest, we can create a temp file with the digest bytes OR just stamp the manifest
                # but we want to stamp the SPECIFIC digest we calculated (keccak, etc).
                # The most standard OTS way is `ots stamp <file>`, which calculates SHA256 internally.
                # To stamp a specific digest (like Keccak), we need to trick it or use advanced options,
                # BUT the user requirement is to anchor the *digest*.
                # OpenTimestamps protocols fundamentally use SHA256 merkle trees.
                # If we want to anchor a Keccak hash, we serve the Keccak hash AS the data to be SHA256'd by OTS.
                # This creates a "SHA256(Keccak(Data))" commitment on Bitcoin.

                with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_digest_file:
                    tmp_digest_file.write(anchor_digest_bytes)
                    tmp_path = tmp_digest_file.name

                # Stamp the detached digest file
                # This produces a .ots file for the temp file
                subprocess.run(["ots", "stamp", tmp_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

                # The output is tmp_path.ots
                tmp_ots = tmp_path + ".ots"
                if os.path.exists(tmp_ots):
                    shutil.move(tmp_ots, self.ots_file)
                    print(f"OTS ANCHOR SUCCESS: Proof saved to {self.ots_file}. Verify via 'ots verify {self.ots_file}'.")
                    broadcast_record["ots"]["stamped"] = True
                    broadcast_record["ots"]["method"] = "opentimestamps-client (CLI)"
                    broadcast_record["ots"]["proof_file"] = self.ots_file
                else:
                    print("OTS CLI failed to generate proof file.")

                os.remove(tmp_path)
            except Exception as e:
                print(f"OTS Anchoring Failed: {e}")
        else:
            print("OTS CLI not available — simulating anchor.")

        with open(self.broadcast_record_file, 'w') as f:
            json.dump(broadcast_record, f, indent=4)
        print(f"BROADCAST LOCKED. MANIFEST ARCHIVED: {self.broadcast_record_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VALORAIPLUS Sovereign OTS Genesis Anchor")
    parser.add_argument("manifest_json", help="Path to the JSON manifest file")
    parser.add_argument(
        "--mode",
        choices=["keccak", "sha256", "double"],
        default="keccak",
        help="Commitment mode: keccak (EVM), sha256, or double (sha256->keccak)",
    )
    args = parser.parse_args()

    engine = ValorAiOTSMatrix(args.manifest_json, mode=args.mode)
    engine.run()
