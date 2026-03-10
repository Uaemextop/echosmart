#!/bin/bash
# EchoSmart Development Environment Setup

set -e

echo "🌱 Setting up EchoSmart development environment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required"; exit 1; }

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
fi

# Start infrastructure services
echo "🐳 Starting infrastructure services..."
docker-compose up -d postgres influxdb redis mosquitto

echo "⏳ Waiting for services to be ready..."
sleep 10

# Setup backend
echo "🐍 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Setup frontend
echo "⚛️ Setting up frontend..."
cd frontend
npm install
cd ..

echo "✅ Development environment ready!"
echo ""
echo "Start the backend:  cd backend && source venv/bin/activate && uvicorn src.main:app --reload"
echo "Start the frontend: cd frontend && npm run dev"
echo "API docs:          http://localhost:8000/docs"
echo "Dashboard:         http://localhost:3000"
