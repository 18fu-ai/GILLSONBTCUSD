#!/usr/bin/env python3
import sys, json, hashlib, pathlib

def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    if len(sys.argv) != 2:
        print("Usage: verify_hashes.py MANIFEST.json")
        sys.exit(1)
    mpath = pathlib.Path(sys.argv[1])
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    root = mpath.parent
    ok = True
    for f in manifest.get("files", []):
        p = root / f["path"]
        digest = sha256_file(p)
        if digest != f["sha256"]:
            ok = False
            print(f"[MISMATCH] {f['path']} expected {f['sha256']}, got {digest}")
    print("OK" if ok else "FAIL")
    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()