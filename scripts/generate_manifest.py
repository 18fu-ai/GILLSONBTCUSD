#!/usr/bin/env python3
"""
Generates a manifest and checksums file from artifacts in the staging directory.

This script scans all files in the `./staging` directory, calculates their
SHA256 hashes and sizes, and then generates two output files in the
`./downloads-site-build` directory:
  1. VALORAIPLUSUNIVERSE.json: The comprehensive release manifest.
  2. checksums.json: A simple map of filenames to their SHA256 hashes.

It reads the release version from the `VERSION` environment variable.
"""
import os
import json
import hashlib
import time
import sys
from pathlib import Path

def calculate_sha256(filepath: Path) -> str:
    """Calculates the SHA256 hash of a file, reading it in chunks."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in 1MB chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    """Main execution function."""
    version = os.environ.get("VERSION", "0.0.0-dev")
    root_dir = Path(__file__).resolve().parents[1]
    staging_dir = root_dir / "staging"
    output_dir = root_dir / "downloads-site-build"

    if not staging_dir.is_dir():
        print(f"[ERROR] Staging directory not found at: {staging_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(exist_ok=True)

    print(f"Scanning artifacts in '{staging_dir}' for version '{version}'...")

    artifacts = []
    all_files = [p for p in staging_dir.iterdir() if p.is_file()]

    for path in all_files:
        print(f"  - Processing {path.name}...")
        artifacts.append({
            "name": path.name,
            "path": path.name,  # Path is relative to the release root
            "size_bytes": path.stat().st_size,
            "sha256": calculate_sha256(path),
            "description": ""  # This can be populated from another source if needed
        })

    # Create the main manifest file
    manifest = {
        "version": version,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "artifacts": sorted(artifacts, key=lambda x: x['name']) # Sort for consistent output
    }

    manifest_path = output_dir / "VALORAIPLUSUNIVERSE.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"[OK] Wrote manifest to {manifest_path}")

    # Create the simple checksums file for quick reference
    checksums = {a['name']: a['sha256'] for a in artifacts}
    checksums_path = output_dir / "checksums.json"
    checksums_path.write_text(json.dumps(checksums, indent=2, sort_keys=True))
    print(f"[OK] Wrote checksums to {checksums_path}")

if __name__ == "__main__":
    main()
