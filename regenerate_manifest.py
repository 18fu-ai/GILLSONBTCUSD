import hashlib
from pathlib import Path

# Define the canonical list of files that belong in the Sovereign Package
CANONICAL_FILES = [
    ".github/workflows/deploy.yml",
    "backend/main.py",
    "backend/enhancements.py",
    "backend/security.py",
    "backend/database.py",
    "backend/monitoring.py",
    "frontend/analytics.html",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/postcss.config.js",
    "frontend/tailwind.config.js",
    "frontend/vite.config.js",
    "frontend/src/App.jsx",
    "frontend/src/index.css",
    "regenerate_manifest.py",
    "verify_manifest.py",
    "requirements.txt",
    "README.md",
    "LICENSE",
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
    for f in sorted(files_to_hash, key=lambda p: str(p)):
        file_hash = sha256_file(f)
        manifest_lines.append(f"{file_hash}  {str(f)}")

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
