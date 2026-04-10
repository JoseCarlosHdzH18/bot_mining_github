#!/bin/bash

# Development script to run locally without Docker (requires local PostgreSQL + Redis)

set -e

echo "🚀 Starting GitHub Miner Bot (Development)..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencias..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Inicializando base de datos..."
python scripts/init_db.py || true

# Start Redis (if running locally)
if ! pgrep -x "redis-server" > /dev/null; then
    echo "🔴 Starting Redis..."
    redis-server --daemonize yes
fi

# Start worker in background
echo "👷 Iniciando worker..."
rq worker github_jobs &
WORKER_PID=$!

# Start API
echo "🌐 Iniciando API..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

echo ""
echo "✅ Started!"
echo "   API: http://localhost:8000"
echo "   Worker PID: $WORKER_PID"
echo "   API PID: $API_PID"
echo ""
echo "Press Ctrl+C to stop"

# Wait for interrupt
trap "kill $WORKER_PID $API_PID 2>/dev/null" EXIT

wait
