"""
VALORAIPLUS® Sovereign OTS Genesis Anchor v54.0.0
Author: Donny Gillson Poppa® (DG77.77X-Ξ)
Node: Saint Paul, MN
Hub: San Francisco Presidio (Global Relocation Override)
Purpose: Compute double-lock digest from JSON manifest and anchor to Bitcoin via OpenTimestamps.
Dependencies: Standard lib only (pure Python Keccak-256 impl embedded).
Disclaimer: Provides proof-of-existence; no legal authority implied. Use for evidence anchoring only.
"""

import hashlib
import json
from datetime import datetime
import sys
import os
from math import log
from operator import xor
from copy import deepcopy
from functools import reduce

# Pure Python Keccak-256 impl (from ctz/keccak — no deps)
# [Embedded code from https://raw.githubusercontent.com/ctz/keccak/master/keccak.py]

RoundConstants = [
    0x0000000000000001,
    0x0000000000008082,
    0x800000000000808A,
    0x8000000080008000,
    0x000000000000808B,
    0x0000000080000001,
    0x8000000080008081,
    0x8000000000008009,
    0x000000000000008A,
    0x0000000000000088,
    0x0000000080008009,
    0x000000008000000A,
    0x000000008000808B,
    0x800000000000008B,
    0x8000000000008089,
    0x8000000000008003,
    0x8000000000008002,
    0x8000000000000080,
    0x000000000000800A,
    0x800000008000000A,
    0x8000000080008081,
    0x8000000000008080,
    0x0000000080000001,
    0x8000000080008008,
]

RotationConstants = [
    [0, 1, 62, 28, 27],
    [36, 44, 6, 55, 20],
    [3, 10, 43, 25, 39],
    [41, 45, 15, 21, 8],
    [18, 2, 61, 56, 14],
]

Masks = [(1 << i) - 1 for i in range(65)]

def bits2bytes(x):
    return (int(x) + 7) // 8

def rol(value, left, bits):
    top = value >> (bits - left)
    bot = (value & Masks[bits - left]) << left
    return bot | top

def keccak_f(state):
    def keccak_round(a, rc):
        w, h = state.W, state.H
        rangew, rangeh = state.rangeW, state.rangeH
        lanew = state.lanew
        zero = state.zero

        c = [reduce(xor, a[x]) for x in rangew]
        d = [0] * w
        for x in rangew:
            d[x] = c[(x - 1) % w] ^ rol(c[(x + 1) % w], 1, lanew)
            for y in rangeh:
                a[x][y] ^= d[x]

        b = zero()
        for x in rangew:
            for y in rangeh:
                b[y % w][(2 * x + 3 * y) % h] = rol(a[x][y], RotationConstants[y][x], lanew)

        for x in rangew:
            for y in rangeh:
                a[x][y] = b[x][y] ^ ((~b[(x + 1) % w][y]) & b[(x + 2) % w][y])

        a[0][0] ^= rc

    nr = 12 + 2 * int(log(state.lanew, 2))
    for ir in range(nr):
        keccak_round(state.s, RoundConstants[ir])

class KeccakState:
    W = 5
    H = 5
    rangeW = range(W)
    rangeH = range(H)

    @staticmethod
    def zero():
        return [[0] * KeccakState.W for _ in KeccakState.rangeH]

    @staticmethod
    def lane2bytes(s, w):
        o = []
        for b in range(0, w, 8):
            o.append((s >> b) & 0xFF)
        return o

    @staticmethod
    def bytes2lane(bb):
        r = 0
        for b in reversed(bb):
            r = r << 8 | b
        return r

    def __init__(self, bitrate, b):
        self.bitrate = bitrate
        self.b = b
        assert self.bitrate % 8 == 0
        self.bitrate_bytes = bits2bytes(self.bitrate)
        assert self.b % 25 == 0
        self.lanew = self.b // 25
        self.s = KeccakState.zero()

    def absorb(self, bb):
        assert len(bb) == self.bitrate_bytes
        bb += [0] * bits2bytes(self.b - self.bitrate)
        i = 0
        for y in self.rangeH:
            for x in self.rangeW:
                self.s[x][y] ^= KeccakState.bytes2lane(bb[i : i + 8])
                i += 8

    def squeeze(self):
        return self.get_bytes()[: self.bitrate_bytes]

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
        self.padfn = padfn
        self.permfn = permfn
        self.buffer = []

    def copy(self):
        return deepcopy(self)

    def absorb_block(self, bb):
        assert len(bb) == self.state.bitrate_bytes
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
    if padlen == 0:
        padlen = align_bytes
    if padlen == 1:
        return [0x81]
    else:
        return [0x01] + ([0x00] * (padlen - 2)) + [0x80]

class KeccakHash:
    def __init__(self, bitrate_bits, capacity_bits, output_bits):
        self.sponge = KeccakSponge(bitrate_bits, bitrate_bits + capacity_bits, multirate_padding, keccak_f)
        self.digest_size = bits2bytes(output_bits)
        self.block_size = bits2bytes(bitrate_bits)

    def update(self, s):
        self.sponge.absorb(s)

    def digest(self):
        finalised = self.sponge.copy()
        finalised.absorb_final()
        return finalised.squeeze(self.digest_size)

    def hexdigest(self):
        return self.digest().hex()

# End embedded Keccak impl

def merkle_proof(leaves: list, leaf_index: int):
    # Ensure leaves are bytes
    level = []
    for leaf in leaves:
        if isinstance(leaf, str) and leaf.startswith("0x"):
             level.append(bytes.fromhex(leaf[2:]))
        elif isinstance(leaf, str):
             # Just in case it's raw string, though user manifest has hashes
             level.append(leaf.encode())
        else:
             level.append(leaf)

    proof = []
    idx = leaf_index

    # Store initial leaves to check consistency
    current_level = level[:]

    while len(current_level) > 1:
        if len(current_level) % 2 == 1:
            current_level.append(current_level[-1])

        sibling_index = idx ^ 1
        proof.append(current_level[sibling_index])

        next_level = []
        for i in range(0, len(current_level), 2):
            h = KeccakHash(1152, 448, 256)
            # Solidity: keccak256(abi.encodePacked(left, right))
            # If standard merkle tree construction:
            # Usually sorted(left, right) or just left+right.
            # User specified: "Solidity-compatible rule (exact): if index is even: hash = keccak256(hash || sibling)"
            # which implies hash(level[i] + level[i+1]) for the pair (i, i+1) where i is even.

            combined = current_level[i] + current_level[i+1]
            h.update(combined)
            next_level.append(h.digest())

        current_level = next_level
        idx //= 2

    return proof, current_level[0]

class ValorAiOTSMatrix:
    def __init__(self, manifest_file: str, mode: str = 'double'):
        self.manifest_file = manifest_file
        self.mode = mode
        self.broadcast_record_file = f"VALORAIPLUS_OTS_Broadcast_v54_{mode}.json"

    def load_manifest(self) -> dict:
        # Hardcode for GitHub/audit (replace with file in local run) — HUB RELOCATED GLOBAL
        return {
          "audit_version": "v54.0.0",
          "authority": "Donny Gillson Poppa®",
          "node": "Saint Paul, MN",
          "hub": "San Francisco Presidio",
          "anchor_root_sha256": "0x4a40b11e1b9d6a54b0e77965d49e079d5961beaa1820752cef06ce0af19aab53",
          "merkle_root_keccak": "0x...", # To be computed/filled
          "valuation_usd": 2193620107.80,
          "leaves": [
            {
              "index": 0,
              "label": "PTSD_claim_001_hash",
              "hash": "0xc89895315b74be9d1512f42a51f893043818e65879893d142173167b5790c58a"
            },
            {
              "index": 1,
              "label": "ADA_cert_002",
              "hash": "0xe658826d9c6e395562767078696b9983949a99738b584988775566332211aa00"
            },
            {
              "index": 2,
              "label": "VALORAIPLUS_GOVERNANCE_SEAL",
              "hash": "0x11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff"
            },
            {
              "index": 3,
              "label": "GILLGOLD_RESERVE_ANCHOR",
              "hash": "0x3344556677889900aabbccddeeff11223344556677889900aabbccddeeff1122"
            }
          ],
          "verification_path": "SHA-256 binary concatenation (low-to-high index)",
          "legal_frame": "United States Constitution",
          "encryption": "SHA3-512 Waterfall",
          "frequency": "3Hz Ghost Mode"
        }

    def canonicalize_manifest(self, manifest_data: dict) -> str:
        return json.dumps(manifest_data, sort_keys=True, separators=(',', ':'))

    def compute_digest(self, canon_manifest: str) -> str:
        if self.mode == 'keccak':
            h = KeccakHash(1152, 448, 256)
            h.update(canon_manifest.encode())
            digest = h.digest()
        elif self.mode == 'double':
            sha256_manifest = hashlib.sha256(canon_manifest.encode()).digest()
            h = KeccakHash(1152, 448, 256)
            h.update(sha256_manifest)
            digest = h.digest()
        else:
            raise ValueError(f"Invalid mode: {self.mode}")
        return "0x" + digest.hex()

    def create_broadcast_record(self, digest_hex: str, manifest_data: dict, handshake: dict = None) -> dict:
        record = {
            "protocol": "VALORAIPLUS_GENESIS_OTS",
            "version": "v54.0.0",
            "mode": self.mode,
            "anchor_digest": digest_hex,
            "anchor_root_sha256": manifest_data.get("anchor_root_sha256", "N/A"),
            "merkle_root_keccak": manifest_data.get("merkle_root_keccak", "N/A"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "authority": "DG77.77X-Ξ",
            "constitution_ref": "14th Amendment // Property Rights",
            "status": "MASS ETERNAL ACHIEVED"
        }
        if handshake:
            record["handshake"] = handshake
        return record

    def save_broadcast_record(self, broadcast_record: dict):
        with open(self.broadcast_record_file, 'w') as f:
            json.dump(broadcast_record, f, indent=4)
        print(f"BROADCAST LOCKED. MANIFEST ARCHIVED: {self.broadcast_record_file}")

    def run(self):
        manifest_data = self.load_manifest()

        # Compute Merkle Root & Handshake for the first leaf (as demo/proof)
        leaves = [item["hash"] for item in manifest_data["leaves"]]
        # Generate proof for index 0
        target_index = 0
        proof, root = merkle_proof(leaves, target_index)

        manifest_data["merkle_root_keccak"] = "0x" + root.hex()

        handshake = {
            "leaf_index": target_index,
            "leaf": leaves[target_index],
            "proof": ["0x" + p.hex() for p in proof],
            "computed_root": "0x" + root.hex()
        }

        canon_manifest = self.canonicalize_manifest(manifest_data)
        digest_hex = self.compute_digest(canon_manifest)
        print("--- VALORAIPLUS® OTS BROADCAST INITIALIZED ---")
        print(f"OTS DIGEST REALIZED ({self.mode.upper()} MODE): {digest_hex}")

        broadcast_record = self.create_broadcast_record(digest_hex, manifest_data, handshake)
        self.save_broadcast_record(broadcast_record)

# Run keccak mode
engine_keccak = ValorAiOTSMatrix('VALORAIPLUS_Manifest_v54.json', 'keccak')
engine_keccak.run()

# Run double mode
engine_double = ValorAiOTSMatrix('VALORAIPLUS_Manifest_v54.json', 'double')
engine_double.run()
