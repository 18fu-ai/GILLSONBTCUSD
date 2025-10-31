#!/usr/bin/env python3
    import os, json, hashlib, pathlib, time
    from datetime import datetime, timezone

    def sha256_file(path: pathlib.Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def main():
        root = pathlib.Path(".").resolve()
        files = []
        for p in root.rglob("*"):
            if p.is_dir():
                continue
            if p.name == "MANIFEST.json":
                continue
            rel = p.relative_to(root).as_posix()
            sha = sha256_file(p)
            files.append({"path": rel, "sha256": sha, "bytes": p.stat().st_size})
        manifest = {
            "name": "ValorAiEngine_Modular_Kit",
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files": files
        }
        pathlib.Path("MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        with open("SHA256SUMS.txt", "w", encoding="utf-8") as f:
            for fobj in files:
                f.write(f"{fobj['sha256']}  {fobj['path']}
")
        print("Wrote MANIFEST.json and SHA256SUMS.txt")

    if __name__ == "__main__":
        main()