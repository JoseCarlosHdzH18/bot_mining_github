#!/bin/bash

set -e

echo "========================================="
echo "🚀 GitHub Miner Bot - Starting..."
echo "========================================="

# Build and start services
echo "📦 Building containers..."
docker-compose build

echo "▶️ Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services..."
sleep 5

# Check status
echo ""
echo "========================================="
echo "✅ Services started!"
echo "========================================="
echo ""
echo "🌐 API:        http://localhost:8000"
echo "📊 Prometheus: http://localhost:9090"
echo "📈 Grafana:    http://localhost:3000 (admin/admin)"
echo ""
echo "📌 Quick commands:"
echo "   docker-compose logs -f api     # Ver logs API"
echo "   docker-compose logs -f worker  # Ver logs workers"
echo "   docker-compose down            # Detener todo"
echo ""
echo "🚀 Para iniciar mining:"
echo '   curl -X POST "http://localhost:8000/scraper/start?query=language:python"'
echo ""
