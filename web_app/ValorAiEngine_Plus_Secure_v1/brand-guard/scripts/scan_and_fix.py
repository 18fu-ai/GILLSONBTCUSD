#!/usr/bin/env python3
import argparse, json, os, re, sys
from pathlib import Path
DEFAULT_IGNORE_DIRS = {".git","node_modules",".next","dist","build","out","target","__pycache__",".venv","venv",".yarn",".pnpm-store",".cache"}
TEXT_EXTS = {".js",".ts",".tsx",".jsx",".json",".jsonc",".md",".mdx",".yml",".yaml",".toml",".py",".c",".cc",".cpp",".h",".hpp",".cs",".java",".kt",".go",".rb",".rs",".php",".sh",".bash",".zsh",".fish",".ini",".cfg",".conf",".env",".txt",".html",".css",".scss",".less",".sql",".graphql",".gql",".sbt"}
def load_rules(p: Path):
    d=json.loads(p.read_text(encoding="utf-8"))
    out=[]
    for i in d.get("banned",[]):
        out.append((i.get("name","rule"), re.compile(i["regex"]), i.get("replacement","")))
    return out
def is_text(path: Path)->bool:
    if path.suffix.lower() in TEXT_EXTS: return True
    try:
        b=path.read_bytes()[:2048]
        if b"\x00" in b: return False
        b.decode("utf-8"); return True
    except: return False
def iter_files(root: Path):
    for dp, dns, fns in os.walk(root):
        dns[:]=[d for d in dns if d not in DEFAULT_IGNORE_DIRS and not d.startswith(".git")]
        for fn in fns:
            yield Path(dp)/fn
def scan(path: Path, rules):
    try: text=path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try: text=path.read_text(encoding="latin-1")
        except: return []
    out=[]
    for (name,pat,_) in rules:
        for m in pat.finditer(text):
            start=m.start()
            line_no=text[:start].count("\n")+1
            line=text.splitlines()[line_no-1] if line_no-1 < len(text.splitlines()) else ""
            out.append((name,line_no,line.strip()))
    return out
def fix(path: Path, rules)->int:
    try:
        content=path.read_text(encoding="utf-8"); enc="utf-8"
    except UnicodeDecodeError:
        try: content=path.read_text(encoding="latin-1"); enc="latin-1"
        except: return 0
    orig=content; total=0
    for (_,pat,repl) in rules:
        content,n=pat.subn(repl,content); total+=n
    if total>0 and content!=orig: path.write_text(content,encoding=enc)
    return total
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--path",default="."); ap.add_argument("--denylist",default="brand-guard/denylist.json")
    ap.add_argument("--mode",choices=["scan","fix"],default="scan"); ap.add_argument("--json",action="store_true")
    args=ap.parse_args()
    root=Path(args.path).resolve(); rules=load_rules(Path(args.denylist).resolve())
    findings=[]; repl=0; scanned=0
    for p in iter_files(root):
        if not is_text(p): continue
        scanned+=1
        if args.mode=="scan":
            f=scan(p,rules)
            for (n,l,t) in f: findings.append({"file":str(p),"rule":n,"line":l,"snippet":t})
        else:
            repl+=fix(p,rules)
    if args.json:
        print(json.dumps({"scanned_files":scanned,"findings":findings,"total_replacements":repl,"mode":args.mode},indent=2))
    else:
        if args.mode=="scan":
            print(f"Scanned {scanned} files; findings: {len(findings)}")
        else:
            print(f"Applied {repl} replacements across {scanned} files.")
    if args.mode=="scan" and len(findings)>0: sys.exit(2)
if __name__=="__main__": main()
