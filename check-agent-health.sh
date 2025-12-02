#!/bin/bash

# DIO Agent Health Check Script
echo "=========================================="
echo "DIO Agent Health Check"
echo "=========================================="
echo ""

# Check running agent containers
echo "📡 Checking Agent Containers..."
agent_containers=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep "dio-agent" | wc -l)
echo "Active agent containers: $agent_containers"

if [ "$agent_containers" -gt 0 ]; then
    echo ""
    echo "📊 Agent Container Details:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "dio-agent"
else
    echo "❌ No agent containers are running!"
fi

echo ""

# Check agent logs for errors
echo "🔍 Checking Agent Logs for Errors..."
for i in {1..3}; do
    container="dio-agent-$i"
    if docker ps --format "{{.Names}}" | grep -q "$container"; then
        echo ""
        echo "--- Agent $i Container Log (Last 20 lines) ---"
        
        # Check for common error patterns
        error_count=$(docker logs "$container" 2>&1 | tail -20 | grep -c -i "error\|exception\|failed\|crash\|traceback")
        if [ "$error_count" -gt 0 ]; then
            echo "🚨 Found $error_count error(s) in recent logs!"
            docker logs "$container" 2>&1 | tail -20 | grep -i "error\|exception\|failed\|crash\|traceback"
        else
            echo "✅ No errors found in recent logs"
        fi
        
        # Check for registration status
        reg_count=$(docker logs "$container" 2>&1 | tail -50 | grep -c "Successfully registered")
        if [ "$reg_count" -gt 0 ]; then
            echo "✅ Agent registered successfully"
        else
            echo "⚠️ Agent may not be registered"
        fi
        
        # Check for threat reporting
        threat_count=$(docker logs "$container" 2>&1 | tail -50 | grep -c "REPORT SUCCESS")
        if [ "$threat_count" -gt 0 ]; then
            echo "✅ Agent has reported threats"
        else
            echo "⚠️ No threat reports detected"
        fi
    fi
done

echo ""

# Check nerve center connectivity
echo "🌐 Checking Nerve Center Connectivity..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Nerve Center is accessible"
else
    echo "❌ Nerve Center is not accessible"
fi

echo ""

# Check agent registration with nerve center
echo "📋 Checking Agent Registration..."
agents_json=$(curl -s http://localhost:8000/agents 2>/dev/null)
if [ -n "$agents_json" ]; then
    agent_count=$(echo "$agents_json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data) if isinstance(data, list) else len(data.get('data', [])))" 2>/dev/null)
    echo "✅ $agent_count agents registered with Nerve Center"
    
    echo "📝 Registered Agents:"
    echo "$agents_json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if isinstance(data, list):
    for agent in data:
        print(f'  - {agent.get(\"id\", \"unknown\")} ({agent.get(\"hostname\", \"unknown\")})')
else:
    for agent in data.get('data', []):
        print(f'  - {agent.get(\"id\", \"unknown\")} ({agent.get(\"hostname\", \"unknown\")})')
"
else
    echo "❌ Could not fetch agent registration data"
fi

echo ""
echo "=========================================="
echo "Health Check Complete"
echo "=========================================="