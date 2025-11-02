#!/usr/bin/env python3
# valoraiplus_: QR maker for Base43 OP_RETURN payload
from pathlib import Path
import qrcode
b43 = (Path("data")/"OP_RETURN.symbolic.base43.txt").read_text().strip()
img = qrcode.make(b43)  # default PIL backend
out = Path("data")/"OP_RETURN_symbolic_QR.png"
img.save(out)
print("QR ->", out)
