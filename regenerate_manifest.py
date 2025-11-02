#!/usr/bin/env python3
"""
Valor AI+® — Manifest Regenerator
Generates a new MANIFEST_SHA256.txt file with fresh SHA-256 hashes for a
canonical list of project files.
"""
import hashlib
from pathlib import Path

# The canonical list of files to be included in the manifest.
# We exclude the manifest itself to avoid the self-referential hash problem.
# We also exclude binary files that we cannot generate.
CANONICAL_FILES = [
    "README.md",
    "CLAIMS.md",
    "Press_OnePager.md",
    "LICENSE_NOTICE.txt",
    "verify_manifest.py",
    "valoraiplus-v9999efe-fortran.f90",
    "valor_data_sources.json",
    "valor_live_data_workaround.py",
]

def sha256(p: Path) -> str:
    """Calculates the SHA-256 hash of a file."""
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    """Main function to regenerate the manifest."""
    base = Path(".")
    manifest_path = base / "MANIFEST_SHA256.txt"

    manifest_entries = []

    print("Regenerating manifest...")
    for fname in sorted(CANONICAL_FILES):
        fpath = base / fname
        if fpath.exists():
            hash_hex = sha256(fpath)
            manifest_entries.append(f"{hash_hex}  {fname}")
            print(f"  Hashed {fname}")
        else:
            print(f"  WARNING: {fname} not found, skipping.")

    # Write the new manifest
    with manifest_path.open("w", encoding="utf-8") as mf:
        mf.write("\n".join(manifest_entries))
        mf.write("\n")

    print(f"\nSuccessfully regenerated {manifest_path} with {len(manifest_entries)} entries. ✅")

if __name__ == "__main__":
    main()
