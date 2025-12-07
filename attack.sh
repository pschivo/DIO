#!/bin/bash

# DIO Attack Simulator with Dynamic Agent Targeting
# This script replaces the hardcoded agent targeting with dynamic discovery

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[1;36m'
NC='\033[0;37m'

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} DIO Attack Simulator${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_attack_header() {
    echo -e "${PURPLE}🎯 Attack Simulation Options${NC}"
    echo -e "${PURPLE}============================${NC}"
    echo ""
}

show_usage() {
    print_header
    print_attack_header
    echo -e "${CYAN}Available attacks:${NC}"
    echo "  $0 cpu                 - Simulate CPU exhaustion (crypto-mining)"
    echo "  $0 memory              - Simulate memory leak attack"
    echo "  $0 network             - Simulate network flood/DDoS"
    echo "  $0 process            - Simulate suspicious process activity"
    echo "  $0 file               - Simulate file integrity violation"
    echo "  $0 multi              - Simulate multi-vector coordinated attack"
    echo " 0 lateral             - Simulate lateral movement across agents"
    echo " 0 interactive         - Launch interactive attack mode"
    echo ""
    echo -e "${CYAN}Agent Targeting:${NC}"
    echo "  $0 all                 - Target ALL agents"
    echo "  $0 <agent-id>         - Target specific agent by ID"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 cpu agent-123      - Target specific agent"
    echo "  $0 memory agent-456     - Target specific agent"
    echo " 0 network all         - Network attack on all agents"
    echo " 0 process all         - Process attack on all agents"
    echo ""
    echo -e "${YELLOW}WARNING]${NC} This is a simulation for testing purposes only"
    echo ""
}

# Get available agents dynamically and target them all
get_agents() {
    curl -s http://localhost:8000/agents 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    agents = data if isinstance(data, list) else data.get('data', [])
    if agents:
        for agent in agents:
            print(f'{agent[\"id\"]}')
    else:
            print('No agents found')
            sys.exit(1)
except:
        print('Error getting agents')
        sys.exit(1)
    }
    
    # Get all available agent IDs
    AGENT_IDS=$(get_agents)
    
    if [ -z "$AGENT_IDS" ]; then
        echo -e "${YELLOW}[WARNING]${NC} No agents found. Starting general attack..."
        local cmd_args="${attack_type}"
    else
        echo -e "${GREEN}[INFO]${NC} Found ${#AGENT_IDS} agents. Targeting all agents."
        echo -e "${CYAN}[INFO]${NC} Agent IDs: $AGENT_IDS"
        local cmd_args="${attack_type}"
    fi
}

# Build and run attack simulator
build_and_run() {
    echo -e "${GREEN}[INFO]${NC} Building attack simulator..."
    if [ ! -f "Dockerfile" ]; then
        echo -e "${RED}[ERROR]${NC} Attack simulator not found"
        exit 1
    fi
    
    docker build -t dio-attack-simulator .
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Build failed"
        exit 1
    fi
    
    echo -e "${GREEN}[INFO]${NC} Attack simulator built successfully"
    
    # Prepare command arguments - simplified since attack simulator doesn't target specific agents
    local cmd_args="${attack_type}"
    
    # Get project name (directory name) to determine network name
    local project_name=$(basename $(pwd))
    local network_name="${project_name}_dio-network"
    
    # Get available agents from nerve center (for targeting)
    get_agents() {
        if curl -s http://localhost:8000/agents > /dev/null 2>&1; then
            curl -s http://localhost:8000/agents | python3 -c "
            import sys, json
            data = json.load(sys.stdin)
            agents = data.get('data', [])
            for agent in agents:
                print(f"{agent['id']}")
            done
        else
            echo "[]" 2>/dev/null
        fi
    }
    
    # Build and run attack simulator
    echo -e "${GREEN}[INFO]${NC} Launching ${attack_type} attack against all agents..."
    echo -e "${CYAN}[INFO]${NC} Using network: ${network_name}"
    
    # Try different network naming conventions
    if docker network inspect "${network_name}" >/dev/null 2>&1; then
        docker run --rm --network "${network_name}" dio-attack-simulator python main.py ${cmd_args} --agent-ids "$AGENT_IDS"
    elif docker network inspect "dio_dio-network" >/dev/null 2>&1; then
        docker run --rm --network "dio_dio-network" dio-attack-simulator python main.py ${cmd_args} --agent-ids "$AGENT_IDS"
    elif docker network inspect "dio-network" >/dev/null 2>&1; then
        docker run --rm --network "dio-network" dio-attack-simulator python main.py ${cmd_args} --agent-ids "$AGENT_IDS"
    else
        echo -e "${YELLOW}[WARNING]${NC} Network not found, trying host network..."
        docker run --rm --network host dio-attack-simulator python main.py ${cmd_args} --agent-ids "$AGENT_IDS"
    fi
    
    echo -e "${GREEN}[INFO]${NC} Attack simulation completed!"
    echo -e "${CYAN}Check DIO dashboard to see results${NC}"
}

# Main script logic
main() {
    print_header
    print_attack_header
    
    case "${1:-help}" in
        show_usage
        ;;
    "cpu"|"memory"|"network"|"process"|"file"|"multi"|"lateral"|"interactive")
        build_and_run "$@"
        ;;
    *)
        echo -e "${RED}[ERROR]${NC} Unknown attack type: ${1}"
        show_usage
        exit 1
        ;;
    esac
}

# Execute main function
main "$@"