import hashlib
import os

def sha256(fname):
    hash_sha256 = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def main():
    with open("MANIFEST_SHA256.txt", "w") as manifest:
        files = sorted([f for f in os.listdir('.') if os.path.isfile(f)])
        for fname in files:
            # Exclude the manifest script and the manifest itself to prevent cycles
            if fname in ["MANIFEST_SHA256.txt", "verify_manifest.py", "regenerate_manifest.py"]:
                continue
            if fname.startswith("."):
                continue
            h = sha256(fname)
            manifest.write(f"{h}  {fname}\n")

if __name__ == "__main__":
    main()
