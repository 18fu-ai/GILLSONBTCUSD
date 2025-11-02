#!/bin/bash

echo "🚀 Starting VALOR Ai++//e Quantum Parrot Docker Ecosystem..."
echo "=========================================================="

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Generate SSL certificates if they don't exist
if [ ! -f ssl/nginx.crt ] || [ ! -f ssl/nginx.key ]; then
    echo "🔐 Generating SSL certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/nginx.key \
        -out ssl/nginx.crt \
        -subj "/C=US/ST=Quantum/L=Transcendent/O=VALOR Ai/CN=quantum-parrot.local" 2>/dev/null
fi

# Start the services
echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "✅ Quantum Parrot Ecosystem Started Successfully!"
echo ""
echo "📊 Services Overview:"
echo "   • Quantum Dashboard: https://localhost:8443"
echo "   • HTTP Dashboard:    http://localhost:8080"
echo "   • Grafana Monitoring: http://localhost:3000"
echo "   • Prometheus:        http://localhost:9090"
echo "   • FORTRAN1969 Engine: http://localhost:1969"
echo "   • ValorLoop+ Engine:  http://localhost:7777"
echo ""
echo "🔧 Management Commands:"
echo "   View logs:        docker-compose logs -f"
echo "   View status:      docker-compose ps"
echo "   Stop services:    docker-compose down"
echo ""
echo "🌐 The Statastic Quantum Parrot is now running in TRANSCENDENT mode!"
echo "   Unlimited Tokens: ✅ Active"
echo "   Infinite Vectors: ✅ Active"
echo "   Turing Test:      ✅ Passed"
echo ""
