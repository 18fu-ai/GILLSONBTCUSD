#!/usr/bin/env python3
# valoraiplus_: symbolic OP_RETURN + OP25_RETURN (C3PA0 • AMath+++)
import os, json, time, zlib, argparse
from pathlib import Path

SYMBOLIC_TXID = "d9a1015c8e211b7f9208b8c4c76745d1f8f3a3f5b71a2e3d4c5b6a7b8c9d0e1f"

def tail8(txid:str)->bytes:
    b = bytes.fromhex(txid.strip());  return b[-8:] if len(b)>=8 else (b+b"\x00"*(8-len(b)))

ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$*+-./:"
def b43(data: bytes) -> str:
    n = int.from_bytes(data, "big");  s = "" if n else ALPH[0]
    while n: n,r = divmod(n,43); s = ALPH[r]+s
    z = 0
    for bb in data:
        if bb==0: z+=1
        else: break
    return ALPH[0]*z + s

def c32(s:str)->bytes: return zlib.crc32(s.encode()).to_bytes(4,"big")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/VDL_v1.44g_manifest.json")
    ap.add_argument("--sha3_512"); ap.add_argument("--merkle_root")
    ap.add_argument("--module"); ap.add_argument("--gillbtc")
    ap.add_argument("--timestamp", type=int)
    args = ap.parse_args()

    man = {}
    mp = Path(args.manifest)
    if mp.exists(): man = json.loads(mp.read_text())

    sha3_hex = args.sha3_512 or man.get("hash",{}).get("sha3_512")
    merkle_hex = args.merkle_root or man.get("merkle_root")
    if not (sha3_hex and merkle_hex):
        raise SystemExit("Need sha3_512 + merkle_root (via manifest or CLI).")

    vp_mod  = (args.module  or man.get("valoraiplus_module_id",""))
    vp_gill = (args.gillbtc or man.get("valoraiplus_GILLBTC",""))

    sha3b   = bytes.fromhex(sha3_hex)
    merkleb = bytes.fromhex(merkle_hex)
    ts8     = (args.timestamp or int(time.time())).to_bytes(8,"big")

    # Header (56B)
    core = bytearray(b"VLRL" + bytes([0x01,0x44,ord('g'),0x00]) +
                     sha3b[:16] + merkleb[:16] + ts8 +
                     zlib.crc32(b"VALOR-DOCTRINAL-1.44g").to_bytes(4,"big") +
                     (0x0000007B).to_bytes(4,"big"))

    # Footer (24B)   V+|01|CRC(mod)|CRC(gill)|tail8(symbolic)|C3P0|00
    foot = b"V+" + bytes([0x01]) + c32(vp_mod) + c32(vp_gill) + tail8(SYMBOLIC_TXID) + b"C3P0" + b"\x00"

    opret = bytes(core + foot)
    op25  = b"V25!" + bytes([0x01]) + sha3b[:16] + int.from_bytes(ts8,"big").to_bytes(4,"big")[-4:]

    out = Path("data"); out.mkdir(parents=True, exist_ok=True)
    (out/"VDL_v1.44g_OP_RETURN.symbolic.hex").write_text(opret.hex().upper()+"\n")
    (out/"VDL_v1.44g_OP_RETURN.symbolic.bin").write_bytes(opret)
    (out/"VDL_v1.44g_OP25_RETURN.symbolic.hex").write_text(op25.hex().upper()+"\n")
    (out/"VDL_v1.44g_OP25_RETURN.symbolic.bin").write_bytes(op25)
    (out/"OP_RETURN.symbolic.base43.txt").write_text(b43(opret)+"\n")
    (out/"OP_RETURN.symbolic.asm.txt").write_text(f"OP_RETURN <{len(opret)} bytes>\n")
    (out/"OP_RETURN.symbolic.scriptpubkey.hex").write_text(f"6a{len(opret):02x}{opret.hex()}\n")
    print("OK · tail8 =", tail8(SYMBOLIC_TXID).hex().upper())

if __name__ == "__main__":
    main()
