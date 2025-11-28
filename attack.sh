#!/bin/bash

# DIO Attack Simulator Launch Script
# This script helps you easily launch attack simulations against the DIO platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  DIO Attack Simulator${NC}"
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
    echo -e "${CYAN}Quick Attack Commands:${NC}"
    echo "  $0 cpu [agent-id]         - Simulate CPU exhaustion (crypto-mining)"
    echo "  $0 memory [agent-id]      - Simulate memory leak attack"
    echo "  $0 network [agent-id]     - Simulate network flood/DDoS"
    echo "  $0 process [agent-id]     - Simulate suspicious process activity"
    echo "  $0 file [agent-id]        - Simulate file integrity violation"
    echo "  $0 multi [agent-id]       - Simulate multi-vector coordinated attack"
    echo "  $0 lateral               - Simulate lateral movement across agents"
    echo ""
    echo -e "${CYAN}Agent Targeting:${NC}"
    echo "  $0 cpu                   # Target random agent"
    echo "  $0 cpu agent-123        # Target specific agent by ID"
    echo "  $0 cpu all              # Target ALL agents"
    echo ""
    echo -e "${CYAN}Interactive Mode:${NC}"
    echo "  $0 interactive - Launch interactive attack simulator"
    echo ""
    echo -e "${CYAN}Attack Sequences:${NC}"
    echo "  $0 sequence    - Run predefined attack sequence"
    echo "  $0 random      - Run random attacks"
    echo ""
    echo -e "${CYAN}Utility:${NC}"
    echo "  $0 status      - Check platform status"
    echo "  $0 help        - Show this help"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 cpu                    # Launch CPU exhaustion attack"
    echo "  $0 cpu agent-001        # Target specific agent"
    echo "  $0 cpu all              # Target all agents"
    echo "  $0 interactive            # Enter interactive mode"
    echo "  $0 sequence               # Run attack sequence"
}

check_platform() {
    echo -e "${GREEN}[INFO]${NC} Checking DIO Platform status..."
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Nerve Center is running"
    else
        echo -e "${RED}✗${NC} Nerve Center is not running"
        echo -e "${YELLOW}Please start DIO platform first:${NC}"
        echo "  ./start.sh dev"
        exit 1
    fi
    
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend is running"
    else
        echo -e "${RED}✗${NC} Frontend is not running"
    fi
    
    echo ""
}

run_attack_simulator() {
    local attack_type=$1
    local target_agent=$2
    
    echo -e "${GREEN}[INFO]${NC} Starting attack simulator..."
    echo -e "${YELLOW}[WARNING]${NC} This is a simulation for testing purposes only"
    echo ""
    
    # Build and run attack simulator
    cd components/attack-simulator
    
    if [ ! -f "Dockerfile" ]; then
        echo -e "${RED}[ERROR]${NC} Attack simulator not found"
        exit 1
    fi
    
    # Build image
    echo -e "${GREEN}[INFO]${NC} Building attack simulator..."
    docker build -t dio-attack-simulator .
    
    # Prepare command arguments
    local cmd_args="${attack_type}"
    if [ -n "$target_agent" ]; then
        cmd_args="${cmd_args} --agent ${target_agent}"
    fi
    
    # Get the project name (directory name) to determine network name
    local project_name=$(basename $(pwd))
    local network_name="${project_name}_dio-network"
    
    # Run attack with proper network and host configuration
    echo -e "${GREEN}[INFO]${NC} Launching ${attack_type} attack simulation..."
    echo -e "${CYAN}[INFO]${NC} Using network: ${network_name}"
    
    # Try different network naming conventions
    if docker network inspect "${network_name}" >/dev/null 2>&1; then
        docker run --rm --network "${network_name}" dio-attack-simulator python main.py ${cmd_args}
    elif docker network inspect "dio_dio-network" >/dev/null 2>&1; then
        docker run --rm --network "dio_dio-network" dio-attack-simulator python main.py ${cmd_args}
    elif docker network inspect "dio-network" >/dev/null 2>&1; then
        docker run --rm --network "dio-network" dio-attack-simulator python main.py ${cmd_args}
    else
        echo -e "${YELLOW}[WARNING]${NC} Network not found, trying host network..."
        docker run --rm --network host dio-attack-simulator python main.py ${cmd_args}
    fi
    
    cd ../..
    
    echo ""
    echo -e "${GREEN}[INFO]${NC} Attack simulation completed!"
    echo -e "${CYAN}Check the dashboard at http://localhost:3000 to see the results${NC}"
}

run_interactive_mode() {
    echo -e "${GREEN}[INFO]${NC} Starting interactive attack simulator..."
    echo -e "${YELLOW}[WARNING]${NC} This is a simulation for testing purposes only"
    echo ""
    
    cd components/attack-simulator
    
    # Build image
    echo -e "${GREEN}[INFO]${NC} Building attack simulator..."
    docker build -t dio-attack-simulator .
    
    # Get the project name (directory name) to determine network name
    local project_name=$(basename $(pwd))
    local network_name="${project_name}_dio-network"
    
    # Run interactive mode
    echo -e "${GREEN}[INFO]${NC} Launching interactive mode..."
    echo -e "${CYAN}[INFO]${NC} Using network: ${network_name}"
    
    # Try different network naming conventions
    if docker network inspect "${network_name}" >/dev/null 2>&1; then
        docker run --rm -it --network "${network_name}" dio-attack-simulator python main.py interactive
    elif docker network inspect "dio_dio-network" >/dev/null 2>&1; then
        docker run --rm -it --network "dio_dio-network" dio-attack-simulator python main.py interactive
    elif docker network inspect "dio-network" >/dev/null 2>&1; then
        docker run --rm -it --network "dio-network" dio-attack-simulator python main.py interactive
    else
        echo -e "${YELLOW}[WARNING]${NC} Network not found, trying host network..."
        docker run --rm -it --network host dio-attack-simulator python main.py interactive
    fi
    
    cd ../..
}

run_attack_sequence() {
    echo -e "${GREEN}[INFO]${NC} Running predefined attack sequence..."
    echo -e "${CYAN}This will demonstrate multiple attack types in sequence${NC}"
    echo ""
    
    attacks=("cpu" "memory" "network" "process" "file")
    
    for attack in "${attacks[@]}"; do
        echo -e "${PURPLE}=== Stage: ${attack} attack ===${NC}"
        run_attack_simulator ${attack}
        echo -e "${YELLOW}Waiting 10 seconds before next attack...${NC}"
        sleep 10
        echo ""
    done
    
    echo -e "${GREEN}[INFO]${NC} Attack sequence completed!"
    echo -e "${CYAN}Check the dashboard to see all detected threats and evidence${NC}"
}

run_random_attacks() {
    echo -e "${GREEN}[INFO]${NC} Running random attack sequence..."
    echo -e "${CYAN}This will run 3-5 random attacks${NC}"
    echo ""
    
    num_attacks=$((RANDOM % 3 + 3))
    attacks=("cpu" "memory" "network" "process" "file" "multi" "lateral")
    
    for ((i=1; i<=num_attacks; i++)); do
        attack=${attacks[$RANDOM % ${#attacks[@]}]}
        echo -e "${PURPLE}=== Attack ${i}/${num_attacks}: ${attack} ===${NC}"
        run_attack_simulator ${attack}
        echo -e "${YELLOW}Waiting 5 seconds before next attack...${NC}"
        sleep 5
        echo ""
    done
    
    echo -e "${GREEN}[INFO]${NC} Random attack sequence completed!"
}

show_status() {
    check_platform
    
    echo -e "${CYAN}Agent Status:${NC}"
    if curl -s http://localhost:8000/agents > /dev/null 2>&1; then
        agents=$(curl -s http://localhost:8000/agents | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', [])))")
        echo -e "  Active Agents: ${GREEN}${agents}${NC}"
    fi
    
    echo -e "${CYAN}Recent Threats:${NC}"
    if curl -s http://localhost:8000/threats > /dev/null 2>&1; then
        threats=$(curl -s http://localhost:8000/threats | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', [])))")
        echo -e "  Total Threats: ${YELLOW}${threats}${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}Dashboard:${NC} http://localhost:3000"
    echo -e "${CYAN}API Docs:${NC}  http://localhost:8000/docs"
}

# Main script logic
main() {
    case "${1:-help}" in
        "cpu")
            check_platform
            run_attack_simulator cpu $2
            ;;
        "memory")
            check_platform
            run_attack_simulator memory $2
            ;;
        "network")
            check_platform
            run_attack_simulator network $2
            ;;
        "process")
            check_platform
            run_attack_simulator process $2
            ;;
        "file")
            check_platform
            run_attack_simulator file $2
            ;;
        "multi")
            check_platform
            run_attack_simulator multi $2
            ;;
        "lateral")
            check_platform
            run_attack_simulator lateral $2
            ;;
        "interactive")
            check_platform
            run_interactive_mode
            ;;
        "sequence")
            check_platform
            run_attack_sequence
            ;;
        "random")
            check_platform
            run_random_attacks
            ;;
        "status")
            show_status
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

print_header
main "$@"