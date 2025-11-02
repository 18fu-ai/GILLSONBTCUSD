#!/usr/bin/env python3
# valoraiplus_: PSBT skeleton with symbolic OP_RETURN (mainnet)
import json
from pathlib import Path

DATA = Path("data")
opret_hex = (DATA/"VDL_v1.44g_OP_RETURN.symbolic.hex").read_text().strip()
scriptpubkey = f"6a50{opret_hex}"  # 0x6a OP_RETURN, 0x50 = 80 bytes

psbt = {
  "network":"main",
  "inputs":[
    {
      "txid":"<FUNDING_TXID_HEX>",
      "vout":0,
      "witness_utxo":{"amount":0.0002,"scriptPubKey":"<FUNDING_SCRIPT_HEX>"},
      "bip32_derivs":[]
    }
  ],
  "outputs":[
    {"amount":0,"scriptPubKey":scriptpubkey},   # OP_RETURN output
    {"amount":0.0001,"address":"<CHANGE_ADDRESS>"}  # change placeholder
  ],
  "unknowns":{
    "valoraiplus_module_id":"VALORAIPLUS_OMNI_STACK_v1.0",
    "valoraiplus_GILLBTC":"VALORCHAIN-G::GHOST25",
    "deployment_symbolic_txid":"d9a1015c8e211b7f9208b8c4c76745d1f8f3a3f5b71a2e3d4c5b6a7b8c9d0e1f"
  }
}
Path("data/tx_skeleton_psbt.json").write_text(json.dumps(psbt,indent=2))
print("PSBT skeleton -> data/tx_skeleton_psbt.json")
