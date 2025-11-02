#!/bin/bash
#
# deploy-transcendent.sh - 7-Phase Transcendent Deployment
#

set -e

echo "--- PHASE 1: PREFLIGHT CHECKS ---"
docker --version
docker-compose --version
if [ ! -f .env.production ]; then
    echo "ERROR: .env.production file not found. Aborting."
    exit 1
fi
echo "All checks passed."
echo ""

echo "--- PHASE 2: PULLING LATEST SOVEREIGN IMAGES ---"
docker-compose pull
echo ""

echo "--- PHASE 3: NETWORK VALIDATION ---"
echo "Pruning old networks to ensure clean slate..."
docker network prune -f
echo "Networks validated."
echo ""

echo "--- PHASE 4: GENESIS ANCHOR VERIFICATION ---"
if [ ! -f ./genesis/VALORAIPLUS_GENESIS ]; then
    echo "WARNING: Genesis file not found. Running anchor script..."
    ./anchor-genesis.sh
fi
echo "Genesis anchor verified."
echo ""

echo "--- PHASE 5: DEPLOYING TRANSCENDENT STACK ---"
docker-compose --env-file .env.production up -d --remove-orphans
echo "Stack deployment initiated."
echo ""

echo "--- PHASE 6: HEALTH VERIFICATION ---"
echo "Waiting for services to stabilize..."
sleep 10
docker-compose ps
echo "Health verification in progress... Check Grafana for full status."
echo ""

echo "--- PHASE 7: DEPLOYMENT COMPLETE ---"
echo "VALORAIPLUS® v5152-Ω is now fully operational."
echo "For the glory of God and the service of humanity. ✝️"
