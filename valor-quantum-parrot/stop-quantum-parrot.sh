#!/bin/bash

echo "🛑 Stopping VALOR Ai++//e Quantum Parrot Docker Ecosystem..."
echo "=========================================================="

docker-compose down

echo ""
echo "✅ Quantum Parrot Ecosystem Stopped Successfully!"
echo ""
echo "Note: All transcendent data has been preserved in Docker volumes."
echo "Run './start-quantum-parrot.sh' to restart the ecosystem."
echo ""
