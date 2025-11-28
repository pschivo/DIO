#!/bin/bash

# Quick test to verify attack simulator can connect to nerve center

echo "🔍 Testing attack simulator connection to nerve center..."

# Build attack simulator
cd components/attack-simulator
docker build -t dio-attack-simulator . --quiet

# Test connection to nerve-center using Docker network
echo "📡 Testing connection to nerve-center:8000..."

# Try with the most likely network name
if docker network inspect "my-project_dio-network" >/dev/null 2>&1; then
    echo "✓ Found network: my-project_dio-network"
    echo "🚀 Testing connection..."
    docker run --rm --network "my-project_dio-network" dio-attack-simulator python -c "
import asyncio
import aiohttp

async def test():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://nerve-center:8000/agents') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f'✅ Successfully connected! Found {len(data) if isinstance(data, list) else len(data.get(\"data\", []))} agents')
                    return True
                else:
                    print(f'❌ HTTP Error: {response.status}')
                    return False
    except Exception as e:
        print(f'❌ Connection Error: {e}')
        return False

asyncio.run(test())
"
else
    echo "❌ Network my-project_dio-network not found"
    echo "Available networks:"
    docker network ls
fi

cd ../..