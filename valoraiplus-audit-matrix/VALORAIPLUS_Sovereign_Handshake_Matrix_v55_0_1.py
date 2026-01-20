"""
VALORAIPLUS® Sovereign Handshake Matrix v55.0.1
Author: Donny Gillson Poppa® (DG77.77X-Ξ)
Node: Saint Paul, MN
Hub: San Francisco Presidio
Purpose: Generate Merkle Proof Handshake Artifacts for Litigation Audit.
Dependencies: Standard lib + embedded pure Python Keccak-256.
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

# --- Embedded Pure Python Keccak-256 (ctz/keccak) ---
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

# --- Merkle Logic (Solidity Compatible) ---

def merkle_proof(leaves: list, leaf_index: int):
    level = []
    for leaf in leaves:
        if isinstance(leaf, str) and leaf.startswith("0x"): level.append(bytes.fromhex(leaf[2:]))
        elif isinstance(leaf, str): level.append(leaf.encode())
        else: level.append(leaf)

    proof = []
    idx = leaf_index
    current_level = level[:]

    while len(current_level) > 1:
        if len(current_level) % 2 == 1: current_level.append(current_level[-1])
        sibling_index = idx ^ 1
        proof.append(current_level[sibling_index])

        next_level = []
        for i in range(0, len(current_level), 2):
            h = KeccakHash(1152, 448, 256)
            combined = current_level[i] + current_level[i+1]
            h.update(combined)
            next_level.append(h.digest())
        current_level = next_level
        idx //= 2
    return proof, current_level[0]

# --- Main Generator ---

class ValorHandshakeMatrix:
    def __init__(self):
        self.output_file = "valoraiplus-audit-matrix/handshake_artifact.json"

    def generate(self):
        # Data from prompt specs
        leaves_raw = [
            "PTSD_SERVICE_DOG_UTILITY_CLAIM_V55",
            "VALUATION_16.89B_USD_VERIFIED",
            "CONSTITUTIONAL_ANCHOR_14TH_AMENDMENT",
            "GILLGOLD_RESERVE_TRITIUM_BACKING"
        ]

        # SHA-256 Leaves as per spec
        leaves_hashed = []
        for raw in leaves_raw:
            leaves_hashed.append("0x" + hashlib.sha256(raw.encode()).hexdigest())

        # Generate Proof for the Valuation Leaf (Index 1)
        target_index = 1
        proof, root = merkle_proof(leaves_hashed, target_index)

        artifact = {
            "version": "v55.0.1",
            "protocol": "VALORAIPLUS_SOVEREIGN_AUDIT",
            "valuation_usd": 16_890_000_000.00,
            "anchor_reality_sha256": "0x4a40b11e1b9d6a54b0e77965d49e079d5961beaa1820752cef06ce0af19aab53",
            "merkle_root_keccak": "0x" + root.hex(),
            "handshake": {
                "leaf_index": target_index,
                "leaf_label": leaves_raw[target_index],
                "leaf_hash": leaves_hashed[target_index],
                "proof": ["0x" + p.hex() for p in proof]
            },
            "status": "MASS ETERNAL ACHIEVED",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        with open(self.output_file, 'w') as f:
            json.dump(artifact, f, indent=4)

        print(f"MATRIX SYNTHESIZED: {self.output_file}")
        print(f"ROOT: {artifact['merkle_root_keccak']}")

if __name__ == "__main__":
    matrix = ValorHandshakeMatrix()
    matrix.generate()
