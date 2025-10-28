#!/usr/bin/env python3
"""
Valor AI+® — Manifest Verifier
Checks SHA-256 hashes of all files in the current directory (or the path you pass)
against MANIFEST_SHA256.txt.
Usage:
  python3 verify_manifest.py            # verify current directory
  python3 verify_manifest.py /path/to/bundle
Exit codes: 0 = OK, 1 = mismatch or missing files, 2 = manifest missing.
"""
import sys, hashlib
from pathlib import Path

def sha256(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def sha256_file(p: Path) -> str:
    with p.open('rb') as f:
        return sha256(f.read())

def main():
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    manifest_path = base / "MANIFEST_SHA256.txt"
    if not manifest_path.exists():
        print("ERROR: MANIFEST_SHA256.txt not found.", file=sys.stderr)
        sys.exit(2)

    # Read manifest
    entries = []
    manifest_content_lines = []
    expected_manifest_hash = None

    with manifest_path.open("r", encoding="utf-8") as mf:
        all_lines = mf.readlines()
        for line in all_lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue

            parts = stripped_line.split(None, 1)
            if len(parts) < 2:
                continue

            hash_hex, fname = parts

            if fname == manifest_path.name:
                expected_manifest_hash = hash_hex
                # Store the line to be excluded from hashing
                self_hash_line = line
            else:
                entries.append((hash_hex, fname))

    ok_all = True
    # Verify all files *except* the manifest itself first
    for expected_hash, fname in entries:
        fp = base / fname
        if not fp.exists():
            print(f"[MISSING] {fname}")
            ok_all = False
            continue
        actual = sha256_file(fp)
        if actual.lower() == expected_hash.lower():
            print(f"[OK] {fname}")
        else:
            print(f"[MISMATCH] {fname}")
            print(f"  expected: {expected_hash}")
            print(f"  actual:   {actual}")
            ok_all = False

    # Now verify the manifest file itself
    if expected_manifest_hash:
        # Reconstruct the content that was originally hashed: everything *except* the manifest's own hash line
        content_to_hash = "".join([line for line in all_lines if line != self_hash_line])

        actual_manifest_hash = sha256(content_to_hash.encode('utf-8'))

        if actual_manifest_hash.lower() == expected_manifest_hash.lower():
            print(f"[OK] {manifest_path.name}")
        else:
            print(f"[MISMATCH] {manifest_path.name}")
            print(f"  expected: {expected_manifest_hash}")
            print(f"  actual:   {actual_manifest_hash}")
            ok_all = False

    if ok_all:
        print("All files match manifest. ✅")
        sys.exit(0)
    else:
        print("One or more files failed verification. ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()
