import hashlib
from pathlib import Path

# Define the canonical list of files that belong in the Sovereign Package
CANONICAL_FILES = [
    "README.md",
    "VALORCHAIN-G_SovereignTx_Attestation.json",
    "VALORCHAIN-G_MerkleProof.json",
    "verify_valorchain_merkle.py",
    "YHWH-24_Sovereign_Document_Anchor.json",
    "VALORCHAIN-G_Manifest.txt",
    "LICENSE.txt",
    "DAO_Proposal_SGMN.md",
    "verify_manifest.py",
    "regenerate_manifest.py" # Include the generation script itself for completeness
]

def sha256(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def sha256_file(p: Path) -> str:
    with p.open('rb') as f:
        return sha256(f.read())

def generate_manifest():
    base = Path(".")
    manifest_path = base / "MANIFEST_SHA256.txt"

    # Use the canonical list of files
    files_to_hash = [base / f for f in CANONICAL_FILES if (base / f).exists()]

    # Calculate hashes and store them
    manifest_lines = []
    for f in sorted(files_to_hash, key=lambda p: p.name):
        file_hash = sha256_file(f)
        manifest_lines.append(f"{file_hash}  {f.name}")

    # This is the content that will be hashed for the manifest's own entry
    content_for_manifest_hash = "\n".join(manifest_lines) + "\n"

    # Calculate the hash of the manifest content
    manifest_hash = sha256(content_for_manifest_hash.encode('utf-8'))

    # Add the manifest's own hash to the list of lines
    manifest_lines.append(f"{manifest_hash}  {manifest_path.name}")

    # Write the final manifest file
    final_manifest_content = "\n".join(manifest_lines) + "\n"
    with manifest_path.open("w", encoding="utf-8") as mf:
        mf.write(final_manifest_content)

    print("Manifest regenerated successfully with canonical file list.")

if __name__ == "__main__":
    generate_manifest()
