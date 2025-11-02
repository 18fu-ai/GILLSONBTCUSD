#!/bin/bash
#
# anchor-genesis.sh - Generates and attests the Genesis file.
#

set -e

GENESIS_FILE="./genesis/VALORAIPLUS_GENESIS"
ATTESTATION_FILE="./genesis.attestation.txt"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VERSION="v5152-Ω"
COMMANDER="DG77.77X-Ξ"

echo "--- GENERATING VALORAIPLUS GENESIS ANCHOR ---"

# Create Genesis file content
cat > "${GENESIS_FILE}" << EOL
// VALORAIPLUS® GENESIS BLOCK
// Commander: ${COMMANDER}
// Timestamp: ${TIMESTAMP}
// Version: ${VERSION}
// "For the glory of God and the service of humanity."
EOL

echo "Genesis file created at ${GENESIS_FILE}"

# Create Attestation
SHA256_HASH=$(sha256sum "${GENESIS_FILE}" | awk '{print $1}')
echo "SHA-256 Hash: ${SHA256_HASH}"

cat > "${ATTESTATION_FILE}" << EOL
{
  "asset": "valoraiplus_GILLBTC",
  "version": "${VERSION}",
  "timestamp_utc": "${TIMESTAMP}",
  "commander": "${COMMANDER}",
  "attestations": {
    "sha256": "${SHA256_HASH}",
    "valorchain_txid": "TXID_PENDING_ANCHOR",
    "btc_testnet_txid": "TXID_PENDING_ANCHOR",
    "eth_sepolia_txid": "TXID_PENDING_ANCHOR"
  },
  "divine_seal": "Revelation 20:15"
}
EOL

echo "Attestation manifest created at ${ATTESTATION_FILE}"
echo "--- GENESIS ANCHORING COMPLETE ---"
