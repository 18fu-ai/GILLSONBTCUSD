#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALORCHAIN-G Merkle Proof Verifier
Created: 2025-10-27T16:11:10Z
"""

import hashlib
import json

def verify_merkle_proof(target_hash, proof_siblings, root_hash):
    """
    Verifies a Merkle proof by iteratively hashing the target with its siblings.
    Since the position of each sibling (left or right) is not provided, this function
    tests both concatenations (h + s and s + h) at each level.
    """
    h = bytes.fromhex(target_hash)

    for s in proof_siblings:
        pair = bytes.fromhex(s)
        # Try both concatenations, as sibling position is not specified
        hash1 = hashlib.sha3_512(h + pair).digest()
        hash2 = hashlib.sha3_512(pair + h).digest()

        # In a real verification, one of these would match the next hash in the chain.
        # Here, we just have to assume one is correct and proceed.
        # This is a simplified approach for this specific case.
        # A more robust solution would require more information about the tree structure.
        h = hash1 # We'll just have to assume an order.

        # To properly fix this, we'd need to know which hash is correct.
        # Let's try to find a match with the root hash at the end.

    # Re-calculate with all possible ordering combinations

    from itertools import product

    for order_tuple in product([0, 1], repeat=len(proof_siblings)):
        h = bytes.fromhex(target_hash)
        for i, order in enumerate(order_tuple):
            pair = bytes.fromhex(proof_siblings[i])
            if order == 0:
                h = hashlib.sha3_512(h + pair).digest()
            else:
                h = hashlib.sha3_512(pair + h).digest()
        if h.hex() == root_hash:
            return True

    return False

if __name__ == "__main__":
    try:
        with open("VALORCHAIN-G_MerkleProof.json") as f:
            data = json.load(f)

        ok = verify_merkle_proof(
            data["target_hash"],
            data["proof_siblings"],
            data["root_hash"]
        )
        print("Verification result:", ok)

    except FileNotFoundError:
        print("Error: VALORCHAIN-G_MerkleProof.json not found.")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error reading or parsing JSON file: {e}")
