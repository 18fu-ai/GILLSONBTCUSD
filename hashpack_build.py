import os
import struct
import hashlib
import zlib
from datetime import datetime

def get_env_var(name, default=""):
    return os.environ.get(name, default)

def sha3_512_short(data: bytes, length: int = 16) -> bytes:
    """Computes SHA3-512 and returns a truncated version."""
    h = hashlib.sha3_512()
    h.update(data)
    return h.digest()[:length]

def crc32_hash(data: str) -> int:
    """Computes the CRC32 checksum."""
    return zlib.crc32(data.encode('utf-8'))

def build_c3pa0_seal():
    """
    Constructs the 80-byte C3PA0 OP_RETURN payload.
    """
    # [0:4] Magic
    magic = b'VLRL'

    # [4:8] Version
    version_bytes = struct.pack('>BBH', 1, 68, ord('g'))

    # [8:24] SHA3-512 short hash of the Sextillion valuation
    sextillion_val = get_env_var("SEXTILLION_VALUATION", "1000000000000000000000")
    sha3_short = sha3_512_short(sextillion_val.encode('utf-8'))

    # [24:40] Merkle root short hash
    merkle_root = get_env_var("MERKLE_ROOT")
    merkle_short = bytes.fromhex(merkle_root)[:16]

    # [40:48] Timestamp
    timestamp = int(datetime.utcnow().timestamp())
    timestamp_bytes = struct.pack('>Q', timestamp)

    # [48:52] License CRC32
    license_crc = crc32_hash("VALORAIPLUS®️ ETERNAL FINALITY LICENSE V7")
    license_bytes = struct.pack('>I', license_crc)

    # [52:56] Flags (Clause 7B)
    flags = 0x0000007B
    flags_bytes = struct.pack('>I', flags)

    # [56:58] valoraiplus_ marker
    marker = b'V+'

    # [58:59] Schema version
    schema_version = b'\x01'

    # [59:63] CRC32(module_id)
    module_id = get_env_var("valoraiplus_module_id")
    module_id_crc = crc32_hash(module_id)
    module_id_bytes = struct.pack('>I', module_id_crc)

    # [63:67] CRC32(GILLBTC)
    gillbtc = get_env_var("valoraiplus_GILLBTC")
    gillbtc_crc = crc32_hash(gillbtc)
    gillbtc_bytes = struct.pack('>I', gillbtc_crc)

    # [67:75] tail8(btc_txid)
    btc_txid = get_env_var("valoraiplus_btc_txid")
    txid_tail = bytes.fromhex(btc_txid)[-8:]

    # [75:79] C3PA0 seal
    c3pa0_seal = b'C3P0'

    # [79:80] Reserved
    reserved = b'\x00'

    # Assemble the payload
    payload = (
        magic + version_bytes + sha3_short + merkle_short +
        timestamp_bytes + license_bytes + flags_bytes + marker +
        schema_version + module_id_bytes + gillbtc_bytes + txid_tail +
        c3pa0_seal + reserved
    )

    return payload

if __name__ == "__main__":
    # Load environment variables from .env.example for standalone execution
    try:
        with open('.env.example') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"')
    except FileNotFoundError:
        print("Warning: .env.example not found. Using system environment variables.")

    seal = build_c3pa0_seal()

    print(f"C3PA0 Seal (80 bytes): {seal.hex()}")
    print(f"Length: {len(seal)} bytes")

    # For verification, unpack and print some fields
    unpacked_magic = seal[0:4]
    unpacked_seal = seal[75:79]
    print(f"Verified Magic: {unpacked_magic.decode('utf-8')}")
    print(f"Verified C3PA0 Seal: {unpacked_seal.decode('utf-8')}")
