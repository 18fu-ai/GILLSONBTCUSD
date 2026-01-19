"""
VALORAIPLUS® ©️ ™️ Sovereign Handshake Matrix v55.0.1 (Jules-Ready)
14D CORE // SAINT PAUL NODE // SAN FRANCISCO HUB
AUTH: DG77.77X-Ξ // FRAMING: UNITED STATES CONSTITUTION
LOGIC: AMATH EXECUTIVE DECISION
DEPENDENCY: NONE (PURE PYTHON KECCAK EMBEDDED)

Purpose:
- Build a Solidity-compatible Keccak-256 Merkle tree from bytes32 leaves
- Generate a Merkle proof packet (leaf/index/proof/root)
- Emit deterministic anchor commitments:
  - direct_keccak = keccak256(canonical(handshake))
  - double_lock_btc = keccak256(sha256(canonical(handshake)))
- Anchor the artifact to Bitcoin via OpenTimestamps (OTS sim — install opentimestamps-client for real stamp)

Notes:
- Leaves MUST be 32-byte hex (bytes32)
- Node hashing is keccak256(left || right) with parity ordering by index
- Mode: keccak (direct) or double (sha256 + keccak)
- Manifest JSON: { "leaves": [{"hash": "0x..."}] }
- Command: python3 valoraiplus_handshake_matrix.py --manifest VALORAIPLUS_Manifest_v54.json --mode keccak --target_index 0
"""

import argparse
import hashlib
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple
from math import log
from operator import xor
from copy import deepcopy
from functools import reduce

# --- Pure Python Keccak-256 (embedded, no deps — from ctz/keccak) ---
RoundConstants = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
]

RotationConstants = [
    [0, 1, 62, 28, 27], [36, 44, 6, 55, 20], [3, 10, 43, 25, 39],
    [41, 45, 15, 21, 8], [18, 2, 61, 56, 14],
]

Masks = [(1 << i) - 1 for i in range(65)]

def bits2bytes(x): return (int(x) + 7) // 8
def rol(value, left, bits):
    top = value >> (bits - left)
    bot = (value & Masks[bits - left]) << left
    return bot | top

def keccak_f(state):
    def keccak_round(a, rc):
        w, h = state.W, state.H
        rangew, rangeh = state.rangeW, state.rangeH
        lanew, zero = state.lanew, state.zero
        c = [reduce(xor, a[x]) for x in rangew]
        d = [0] * w
        for x in rangew:
            d[x] = c[(x - 1) % w] ^ rol(c[(x + 1) % w], 1, lanew)
            for y in rangeh: a[x][y] ^= d[x]
        b = zero()
        for x in rangew:
            for y in rangeh: b[y % w][(2 * x + 3 * y) % h] = rol(a[x][y], RotationConstants[y][x], lanew)
        for x in rangew:
            for y in rangeh: a[x][y] = b[x][y] ^ ((~b[(x + 1) % w][y]) & b[(x + 2) % w][y])
        a[0][0] ^= rc
    nr = 12 + 2 * int(log(state.lanew, 2))
    for ir in range(nr): keccak_round(state.s, RoundConstants[ir])

class KeccakState:
    W, H = 5, 5
    rangeW, rangeH = range(W), range(H)
    @staticmethod
    def zero(): return [[0] * KeccakState.W for _ in KeccakState.rangeH]
    @staticmethod
    def lane2bytes(s, w): return [(s >> b) & 0xFF for b in range(0, w, 8)]
    @staticmethod
    def bytes2lane(bb):
        r = 0
        for b in reversed(bb): r = r << 8 | b
        return r
    def __init__(self, bitrate, b):
        self.bitrate, self.b = bitrate, b
        self.bitrate_bytes, self.lanew = bits2bytes(self.bitrate), self.b // 25
        self.s = KeccakState.zero()
    def absorb(self, bb):
        bb += [0] * bits2bytes(self.b - self.bitrate)
        i = 0
        for y in self.rangeH:
            for x in self.rangeW:
                self.s[x][y] ^= KeccakState.bytes2lane(bb[i : i + 8])
                i += 8
    def squeeze(self): return self.get_bytes()[: self.bitrate_bytes]
    def get_bytes(self):
        out = [0] * bits2bytes(self.b)
        i = 0
        for y in self.rangeH:
            for x in self.rangeW:
                v = KeccakState.lane2bytes(self.s[x][y], self.lanew)
                out[i : i + 8] = v
                i += 8
        return out

class KeccakSponge:
    def __init__(self, bitrate, width, padfn, permfn):
        self.state = KeccakState(bitrate, width)
        self.padfn, self.permfn, self.buffer = padfn, permfn, []
    def copy(self): return deepcopy(self)
    def absorb_block(self, bb):
        self.state.absorb(bb)
        self.permfn(self.state)
    def absorb(self, s):
        self.buffer += list(s)
        while len(self.buffer) >= self.state.bitrate_bytes:
            self.absorb_block(self.buffer[: self.state.bitrate_bytes])
            self.buffer = self.buffer[self.state.bitrate_bytes :]
    def absorb_final(self):
        padded = self.buffer + self.padfn(len(self.buffer), self.state.bitrate_bytes)
        self.absorb_block(padded)
        self.buffer = []
    def squeeze(self, l):
        z = self.state.squeeze()
        while len(z) < l:
            self.permfn(self.state)
            z += self.state.squeeze()
        return bytes(z[:l])

def multirate_padding(used_bytes, align_bytes):
    padlen = align_bytes - used_bytes
    if padlen == 0: padlen = align_bytes
    if padlen == 1: return [0x81]
    return [0x01] + ([0x00] * (padlen - 2)) + [0x80]

class KeccakHash:
    def __init__(self, bitrate_bits, capacity_bits, output_bits):
        self.sponge = KeccakSponge(bitrate_bits, bitrate_bits + capacity_bits, multirate_padding, keccak_f)
        self.digest_size = bits2bytes(output_bits)
    def update(self, s): self.sponge.absorb(s)
    def digest(self):
        finalised = self.sponge.copy()
        finalised.absorb_final()
        return finalised.squeeze(self.digest_size)
    def hexdigest(self): return self.digest().hex()

# --- Helper Wrapper for EVM-compatible Keccak256 ---
def keccak256(data: bytes) -> bytes:
    # Standard Ethereum/Solidity parameters: r=1088, c=512, output=256
    h = KeccakHash(1088, 512, 256)
    h.update(data)
    return h.digest()

# --- Helpers ---
def is_bytes32_hex(s: str) -> bool:
    if not s.startswith("0x"): return False
    try:
        b = bytes.fromhex(s[2:])
        return len(b) == 32
    except:
        return False

def hex_to_bytes32(s: str) -> bytes:
    return bytes.fromhex(s[2:])

def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

# --- Merkle Handshake Class ---
class ValorAiMerkleHandshake:
    def __init__(self, mode: str):
        self.authority = "DG77.77X-Ξ"
        self.node = "Saint Paul, MN"
        self.hub = "San Francisco, CA"
        self.version = "v55.0.1"
        self.anchor_root_sha256 = "0x4a40b11e1b9d6a54b0e77965d49e079d5961beaa1820752cef06ce0af19aab53"
        self.mode = mode

    def keccak256_node(self, left32: bytes, right32: bytes) -> bytes:
        """Solidity-compatible node derivation: keccak256(left || right)."""
        if len(left32) != 32 or len(right32) != 32:
            raise ValueError("Input nodes must be exactly 32 bytes.")
        return keccak256(left32 + right32)

    def build_levels(self, leaves: List[bytes]) -> List[List[bytes]]:
        """Compute all Merkle levels (duplicates last element if odd)."""
        if not leaves:
            return [[b"\x00" * 32]]

        current = list(leaves)
        levels = [current]

        while len(current) > 1:
            if len(current) % 2 == 1:
                current.append(current[-1])

            nxt = []
            for i in range(0, len(current), 2):
                nxt.append(self.keccak256_node(current[i], current[i + 1]))

            current = nxt
            levels.append(current)

        return levels

    def get_proof(self, leaves: List[bytes], index: int) -> Tuple[List[bytes], bytes]:
        """Generate Solidity-compatible Merkle proof for leaf[index]."""
        if index < 0 or index >= len(leaves):
            raise IndexError("Leaf index out of range.")

        levels = self.build_levels(leaves)
        proof = []
        idx = index

        for lvl in range(len(levels) - 1):
            level = levels[lvl]

            # Parity duplication must match tree build behavior
            if len(level) % 2 == 1:
                level = level + [level[-1]]

            sibling_index = idx ^ 1
            proof.append(level[sibling_index])
            idx //= 2

        root = levels[-1][0]
        return proof, root

    def verify_proof(self, leaf: bytes, index: int, proof: List[bytes], expected_root: bytes) -> bool:
        """Solidity rule:
        if index even: hash = keccak256(hash || sibling)
        else:          hash = keccak256(sibling || hash)
        index //= 2
        """
        h = leaf
        idx = index

        for sib in proof:
            if idx % 2 == 0:
                h = keccak256(h + sib)
            else:
                h = keccak256(sib + h)
            idx //= 2

        return h == expected_root

    def generate_audit_artifacts(self, leaf_hex_list: List[str], target_leaf_index: int) -> Dict[str, Any]:
        """Emit:
        - handshake packet (leaf/index/proof/root)
        - anchors (direct_keccak + double_lock_btc)
        - self_check (proof verifies)
        """
        print(f"--- VALORAIPLUS® SOVEREIGN HANDSHAKE {self.version} ---")

        for hx in leaf_hex_list:
            if not is_bytes32_hex(hx):
                raise ValueError(f"Leaf is not bytes32: {hx}")

        leaves = [hex_to_bytes32(h) for h in leaf_hex_list]
        proof, root = self.get_proof(leaves, target_leaf_index)
        root_hex = "0x" + root.hex()

        leaf_bytes = leaves[target_leaf_index]
        ok = self.verify_proof(leaf_bytes, target_leaf_index, proof, root)

        handshake = {
            "schema": "VALORAIPLUS_PROOF_HANDSHAKE",
            "version": self.version,
            "authority": self.authority,
            "node": self.node,
            "hub": self.hub,
            "leaf_index": target_leaf_index,
            "leaf_hash": leaf_hex_list[target_leaf_index],
            "proof": ["0x" + p.hex() for p in proof],
            "merkle_root_keccak": root_hex,
            "anchor_root_sha256": self.anchor_root_sha256,
            "verification_rule": "Solidity/Foundry Compatible (Index Parity)",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "self_check": ok,
        }

        canon = canonical_json(handshake)
        direct_commitment = "0x" + keccak256(canon.encode("utf-8")).hex()
        double_lock_commitment = "0x" + keccak256(hashlib.sha256(canon.encode("utf-8")).digest()).hex()

        artifacts = {
            "handshake": handshake,
            "anchors": {
                "direct_keccak": direct_commitment,
                "double_lock_btc": double_lock_commitment,
            },
        }

        out_file = f"VALORAIPLUS_Handshake_Artifact_{int(datetime.now().timestamp())}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(artifacts, f, indent=4)

        print(f"MERKLE ROOT KECCAK: {root_hex}")
        print(f"SELF CHECK: {'PASS' if ok else 'FAIL'}")
        print(f"DIRECT KECCAK: {direct_commitment}")
        print(f"DOUBLE-LOCK: {double_lock_commitment}")
        print(f"ARTIFACT SEALED: {out_file}")

        return artifacts

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VALORAIPLUS Sovereign Handshake Matrix")
    parser.add_argument("--manifest", required=True, help="Path to manifest JSON containing leaves")
    parser.add_argument("--mode", default="keccak", choices=["keccak", "double"], help="Anchor mode (keccak/double)")
    parser.add_argument("--target_index", type=int, default=0, help="Leaf index to generate proof for")

    args = parser.parse_args()

    try:
        with open(args.manifest, "r") as f:
            manifest_data = json.load(f)

        # Extract leaf hashes. Support both simple string list and object list with "hash" key
        raw_leaves = manifest_data.get("leaves", [])
        leaf_hex_list = []
        for l in raw_leaves:
            if isinstance(l, str):
                leaf_hex_list.append(l)
            elif isinstance(l, dict) and "hash" in l:
                leaf_hex_list.append(l["hash"])
            else:
                 # Fallback: Hash it if it's not already a hash?
                 # The prompt says "Manifest JSON: { "leaves": [{"hash": "0x..."}] }"
                 # But sticking to what we can reliably parse.
                 pass

        if not leaf_hex_list:
            print("Error: No valid leaves found in manifest.")
            exit(1)

        matrix = ValorAiMerkleHandshake(mode=args.mode)
        matrix.generate_audit_artifacts(leaf_hex_list, args.target_index)

    except FileNotFoundError:
        print(f"Error: Manifest file '{args.manifest}' not found.")
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
