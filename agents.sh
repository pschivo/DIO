#!/bin/bash

# DIO Agent List Script
# Shows available agents for attack targeting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  DIO Active Agents${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

if ! curl -s http://localhost:8000/agents > /dev/null 2>&1; then
    echo -e "${RED}[ERROR]${NC} Cannot connect to nerve center"
    echo -e "${YELLOW}Please make sure DIO platform is running:${NC}"
    echo "  ./start.sh production"
    exit 1
fi

print_header

# Get agents from nerve center
agents_json=$(curl -s http://localhost:8000/agents)

if [ -z "$agents_json" ] || [ "$agents_json" = "[]" ]; then
    echo -e "${YELLOW}No active agents found${NC}"
    echo ""
    echo -e "${CYAN}Start agents with:${NC}"
    echo "  docker compose --profile production up -d --scale agent=3"
    exit 0
fi

echo -e "${GREEN}Available Agents:${NC}"
echo ""

# Parse and display agents
echo "$agents_json" | python3 -c "
import sys, json
try:
    agents = json.load(sys.stdin)
    if isinstance(agents, dict) and 'data' in agents:
        agents = agents['data']
    
    if not agents:
        print('No agents found')
        sys.exit(0)
    
    for i, agent in enumerate(agents, 1):
        agent_id = agent.get('id', 'Unknown')
        name = agent.get('name', 'Unknown')
        status = agent.get('status', 'unknown')
        cpu = agent.get('cpu', 0)
        memory = agent.get('memory', 0)
        threats = agent.get('threats', 0)
        
        status_color = '🟢' if status == 'active' else '🟡' if status == 'warning' else '🔴'
        
        print(f'{i}. {agent_id}')
        print(f'   Name: {name}')
        print(f'   Status: {status_color} {status}')
        print(f'   CPU: {cpu:.1f}% | Memory: {memory:.1f}% | Threats: {threats}')
        print('')
    
    print('Usage Examples:')
    print('  ./attack.sh cpu all              # Attack all agents')
    print('  ./attack.sh cpu', agents[0]['id'] if agents else 'agent-id', '# Attack first agent')
    print('  ./attack.sh memory all           # Memory attack on all agents')
    
except Exception as e:
    print(f'Error parsing agent data: {e}')
    sys.exit(1)
"

echo ""
echo -e "${BLUE}================================${NC}"