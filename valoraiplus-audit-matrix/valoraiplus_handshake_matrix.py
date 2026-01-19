#!/usr/bin/env python3
"""
VALORAIPLUS® ©️ ™️ Sovereign Handshake Matrix v55.0.1 (Jules-Ready)
14D CORE // SAINT PAUL NODE // SAN FRANCISCO HUB
AUTH: DG77.77X-Ξ // FRAMING: UNITED STATES CONSTITUTION
LOGIC: AMATH EXECUTIVE DECISION
DEPENDENCY: pip install eth-hash[pycryptodome] opentimestamps-client

AMath Determination:
- Hybrid Merkle Tree: SHA-256 Leaves (FIPS) / Keccak-256 Nodes (EVM).
- Solidity-Compatible Index Parity: even index = keccak(h||sib), odd = keccak(sib||h).
- Bitcoin OTS Double-Lock: keccak256(sha256(canonical_json)).
"""

import argparse
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple

try:
    from eth_hash.auto import keccak as keccak256
except ImportError:
    print("CRITICAL: eth-hash[pycryptodome] missing. Run: pip install eth-hash[pycryptodome]")
    raise SystemExit(1)


def hex32_to_bytes(h: str) -> bytes:
    h = h.strip()
    if h.startswith("0x"):
        h = h[2:]
    b = bytes.fromhex(h)
    if len(b) != 32:
        raise ValueError(f"Leaf must be 32 bytes: {h}")
    return b


def bytes_to_hex32(b: bytes) -> str:
    if len(b) != 32:
        raise ValueError("Expected 32-byte value.")
    return "0x" + b.hex()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def keccak_node(left32: bytes, right32: bytes) -> bytes:
    if len(left32) != 32 or len(right32) != 32:
        raise ValueError("Nodes must be 32 bytes each.")
    return keccak256(left32 + right32)


def build_merkle_levels(leaves: List[bytes]) -> List[List[bytes]]:
    if not leaves:
        return [[b"\x00" * 32]]

    current = list(leaves)
    levels = [current]

    while len(current) > 1:
        if len(current) % 2 == 1:
            current.append(current[-1])

        nxt: List[bytes] = []
        for i in range(0, len(current), 2):
            nxt.append(keccak_node(current[i], current[i + 1]))

        current = nxt
        levels.append(current)

    return levels


def merkle_proof(leaves: List[bytes], target_index: int) -> Tuple[List[bytes], bytes]:
    levels = build_merkle_levels(leaves)
    proof: List[bytes] = []
    idx = target_index

    for lvl in range(len(levels) - 1):
        level = list(levels[lvl])

        if len(level) % 2 == 1:
            level.append(level[-1])

        sibling_index = idx ^ 1
        proof.append(level[sibling_index])
        idx //= 2

    root = levels[-1][0]
    return proof, root


def load_leaf_hexes(manifest_path: str) -> List[str]:
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    leaves = data.get("leaves")
    if not leaves:
        raise ValueError("Manifest missing leaves[]")

    if isinstance(leaves[0], str):
        return leaves

    if isinstance(leaves[0], dict) and "hash" in leaves[0]:
        return [l["hash"] for l in leaves]

    raise ValueError("Unsupported leaves format. Use list[str] or list[{'hash': str}].")


def ots_stamp(path: str) -> None:
    subprocess.run(["ots", "stamp", path], check=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True, help="VALORAIPLUS Manifest JSON")
    p.add_argument("--mode", choices=["keccak", "double"], default="double")
    p.add_argument("--target_index", type=int, default=0)
    p.add_argument("--jules", action="store_true", help="Infuse PTSD/ADA Metadata")
    p.add_argument("--ots", action="store_true", help="Bitcoin Genesis Anchor (OpenTimestamps)")
    args = p.parse_args()

    leaf_hexes = load_leaf_hexes(args.manifest)
    leaves = [hex32_to_bytes(h) for h in leaf_hexes]

    if args.target_index < 0 or args.target_index >= len(leaves):
        raise ValueError(f"target_index out of range: {args.target_index}")

    proof_bytes, root_bytes = merkle_proof(leaves, args.target_index)

    handshake: Dict[str, Any] = {
        "schema": "VALORAIPLUS_PROOF_HANDSHAKE",
        "version": "v55.0.1",
        "authority": "DG77.77X-Ξ",
        "leaf_index": args.target_index,
        "leaf_hash": leaf_hexes[args.target_index],
        "proof": [bytes_to_hex32(x) for x in proof_bytes],
        "merkle_root_keccak": bytes_to_hex32(root_bytes),
        "verification_rule": "Index Parity (Solidity Compatible)",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if args.jules:
        handshake["jules_audit"] = {
            "node": "Saint Paul, MN",
            "hub": "San Francisco, CA",
            "frame": "US Constitution Art 14",
            "mass_valuation": "$16.89B USD",
            "ghost_freq": "3Hz",
        }

    canon = canonical_json(handshake).encode("utf-8")

    direct = keccak256(canon)
    double = keccak256(hashlib.sha256(canon).digest())

    anchors = {
        "direct_keccak": bytes_to_hex32(direct),
        "double_lock_btc": bytes_to_hex32(double),
    }

    primary_anchor = anchors["direct_keccak"] if args.mode == "keccak" else anchors["double_lock_btc"]

    artifact_name = f"VALORAIPLUS_Handshake_Artifact_{int(time.time())}.json"
    with open(artifact_name, "w", encoding="utf-8") as f:
        json.dump({"handshake": handshake, "anchors": anchors, "primary_anchor": primary_anchor}, f, indent=4)

    print("--- VALORAIPLUS® HANDSHAKE REALIZED ---")
    print(f"ROOT (KECCAK): {handshake['merkle_root_keccak']}")
    print(f"PRIMARY ANCHOR ({args.mode.upper()}): {primary_anchor}")
    print(f"ARTIFACT SEALED: {artifact_name}")

    if args.ots:
        try:
            ots_stamp(artifact_name)
            print(f"OTS PROOF CREATED: {artifact_name}.ots")
        except FileNotFoundError:
            print("OTS ERROR: 'ots' CLI not found. Install: pip install opentimestamps-client")
        except subprocess.CalledProcessError as e:
            print(f"OTS ERROR: ots stamp failed ({e})")


if __name__ == "__main__":
    main()
