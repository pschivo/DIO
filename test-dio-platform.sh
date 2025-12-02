#!/bin/bash

echo "🗄️ Testing DIO Platform Configuration"

# Test docker compose file
if [ -f "docker-compose.yml" ]; then
    echo "✅ docker-compose.yml found"
    echo "📄 Configuration:"
    cat docker-compose.yml | grep -A 5 "DATABASE_URL"
else
    echo "❌ docker-compose.yml not found"
    exit 1
fi

echo ""
echo "🔍 Testing Docker availability"
if command -v docker >/dev/null 2>&1; then
    echo "✅ Docker is available"
else
    echo "❌ Docker is not available"
    exit 1
fi

echo ""
echo "🚀 Testing docker compose"
if docker compose version >/dev/null 2>&1; then
    echo "✅ docker compose is available"
    echo "📋 Version: $(docker compose version)"
else
    echo "❌ docker compose is not available"
    exit 1
fi

echo ""
echo "🐳 Starting DIO Platform (Production)"
if docker compose --profile production up -d --build; then
    echo "✅ DIO Platform started successfully!"
    echo "📊 Frontend: http://localhost:3000"
    echo "🔗 Nerve Center: http://localhost:8000"
    echo "🤖 Mesh Network: ws://localhost:4222"
    echo "📊 Database: PostgreSQL (production)"
    echo "🤖 Agent Count: 3 (default)"
else
    echo "❌ Failed to start DIO Platform"
    exit 1
fi