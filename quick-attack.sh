#!/bin/bash

# DIO Quick Attack Script
# Simplified attack launcher with automatic network detection

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  DIO Quick Attack${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

show_usage() {
    print_header
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 <attack_type> [agent_id]"
    echo ""
    echo -e "${CYAN}Attack Types:${NC}"
    echo "  cpu      - CPU Exhaustion Attack"
    echo "  memory   - Memory Leak Attack"
    echo "  network  - Network Flood Attack"
    echo "  process  - Process Anomaly Attack"
    echo "  file     - File Integrity Attack"
    echo ""
    echo -e "${CYAN}Targeting:${NC}"
    echo "  $0 cpu              # Random agent"
    echo "  $0 cpu agent-123    # Specific agent"
    echo "  $0 cpu all          # All agents"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 cpu agent-89a2a04f"
    echo "  $0 memory all"
}

check_platform() {
    echo -e "${GREEN}[INFO]${NC} Checking DIO Platform status..."
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Nerve Center is running"
    else
        echo -e "${RED}✗${NC} Nerve Center is not running"
        echo -e "${YELLOW}Please start DIO platform first:${NC}"
        echo "  docker compose --profile production up -d"
        exit 1
    fi
    
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend is running"
    else
        echo -e "${RED}✗${NC} Frontend is not running"
    fi
    
    echo ""
}

run_attack() {
    local attack_type=$1
    local target_agent=$2
    
    echo -e "${GREEN}[INFO]${NC} Starting ${attack_type} attack..."
    if [ -n "$target_agent" ]; then
        echo -e "${CYAN}[INFO]${NC} Target: ${target_agent}"
    else
        echo -e "${CYAN}[INFO]${NC} Target: Random agent"
    fi
    echo -e "${YELLOW}[WARNING]${NC} This is a simulation for testing purposes only"
    echo ""
    
    # Build attack simulator
    cd components/attack-simulator
    
    if [ ! -f "Dockerfile" ]; then
        echo -e "${RED}[ERROR]${NC} Attack simulator not found"
        exit 1
    fi
    
    echo -e "${GREEN}[INFO]${NC} Building attack simulator..."
    docker build -t dio-attack-simulator . --quiet
    
    # Prepare command arguments
    local cmd_args="${attack_type}"
    if [ -n "$target_agent" ]; then
        cmd_args="${cmd_args} --agent ${target_agent}"
    fi
    
    # Try to find the correct network
    echo -e "${GREEN}[INFO]${NC} Determining network configuration..."
    
    # Test different network options
    if docker network inspect "dio_dio-network" >/dev/null 2>&1; then
        echo -e "${CYAN}[INFO]${NC} Using network: dio_dio-network"
        docker run --rm --network dio_dio-network dio-attack-simulator python main.py ${cmd_args}
    elif docker network inspect "dio-network" >/dev/null 2>&1; then
        echo -e "${CYAN}[INFO]${NC} Using network: dio-network"
        docker run --rm --network dio-network dio-attack-simulator python main.py ${cmd_args}
    elif docker network inspect "$(basename $(pwd))_dio-network" >/dev/null 2>&1; then
        local network_name="$(basename $(pwd))_dio-network"
        echo -e "${CYAN}[INFO]${NC} Using network: ${network_name}"
        docker run --rm --network "${network_name}" dio-attack-simulator python main.py ${cmd_args}
    else
        echo -e "${YELLOW}[WARNING]${NC} Network not found, trying host network..."
        docker run --rm --network host dio-attack-simulator python main.py ${cmd_args}
    fi
    
    local exit_code=$?
    
    cd ../..
    
    if [ $exit_code -eq 0 ]; then
        echo ""
        echo -e "${GREEN}[INFO]${NC} Attack simulation completed successfully!"
        echo -e "${CYAN}Check the dashboard at http://localhost:3000 to see the results${NC}"
    else
        echo ""
        echo -e "${RED}[ERROR]${NC} Attack simulation failed with exit code $exit_code"
        echo -e "${YELLOW}Try checking the network configuration with:${NC}"
        echo "  ./check-network.sh"
    fi
}

# Main script logic
main() {
    case "${1:-help}" in
        "cpu"|"memory"|"network"|"process"|"file")
            check_platform
            run_attack $1 $2
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

print_header
main "$@"