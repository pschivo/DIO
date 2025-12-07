#!/bin/bash

# DIO Test Script
# Tests all the fixes we've made

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  DIO Test Suite${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

test_nerve_center_api() {
    echo -e "${CYAN}[TEST]${NC} Testing Nerve Center API..."
    
    # Test agents endpoint
    if curl -s http://localhost:8000/agents > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Nerve Center API is accessible"
        
        # Test JSON response
        agents_response=$(curl -s http://localhost:8000/agents)
        if echo "$agents_response" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Agents API returns valid JSON"
            
            # Check for camelCase fields
            if echo "$agents_response" | grep -q "lastSeen"; then
                echo -e "${GREEN}✓${NC} Using camelCase field names (lastSeen)"
            else
                echo -e "${RED}✗${NC} Not using camelCase field names"
            fi
            
            if echo "$agents_response" | grep -q "ipAddress"; then
                echo -e "${GREEN}✓${NC} Using camelCase field names (ipAddress)"
            else
                echo -e "${RED}✗${NC} Not using camelCase field names"
            fi
            
        else
            echo -e "${RED}✗${NC} Agents API returns invalid JSON"
        fi
    else
        echo -e "${RED}✗${NC} Nerve Center API is not accessible"
    fi
}

test_frontend_api() {
    echo -e "${CYAN}[TEST]${NC} Testing Frontend API..."
    
    # Test frontend agents endpoint
    if curl -s http://localhost:3000/api/agents > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend API is accessible"
        
        # Test JSON response
        agents_response=$(curl -s http://localhost:3000/api/agents)
        if echo "$agents_response" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Frontend API returns valid JSON"
        else
            echo -e "${RED}✗${NC} Frontend API returns invalid JSON"
        fi
    else
        echo -e "${RED}✗${NC} Frontend API is not accessible"
    fi
}

test_docker_networks() {
    echo -e "${CYAN}[TEST]${NC} Testing Docker Networks..."
    
    # Check for common network names
    networks_found=0
    
    if docker network inspect "dio_dio-network" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Found network: dio_dio-network"
        networks_found=$((networks_found + 1))
    fi
    
    if docker network inspect "dio-network" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Found network: dio-network"
        networks_found=$((networks_found + 1))
    fi
    
    if docker network inspect "$(basename $(pwd))_dio-network" >/dev/null 2>&1; then
        local network_name="$(basename $(pwd))_dio-network"
        echo -e "${GREEN}✓${NC} Found network: ${network_name}"
        networks_found=$((networks_found + 1))
    fi
    
    if [ $networks_found -eq 0 ]; then
        echo -e "${YELLOW}⚠${NC} No DIO networks found, will use host network"
    else
        echo -e "${GREEN}✓${NC} Found $networks_found DIO network(s)"
    fi
}

test_attack_simulator() {
    echo -e "${CYAN}[TEST]${NC} Testing Attack Simulator..."
    
    # Build attack simulator
    cd components/attack-simulator
    if docker build -t dio-attack-simulator . --quiet; then
        echo -e "${GREEN}✓${NC} Attack simulator builds successfully"
        
        # Test basic functionality
        if docker run --rm --network host dio-attack-simulator python main.py --help >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Attack simulator runs successfully"
        else
            echo -e "${RED}✗${NC} Attack simulator failed to run"
        fi
    else
        echo -e "${RED}✗${NC} Attack simulator build failed"
    fi
    cd ../..
}

run_all_tests() {
    print_header
    echo -e "${YELLOW}Running comprehensive DIO tests...${NC}"
    echo ""
    
    test_nerve_center_api
    echo ""
    
    test_frontend_api
    echo ""
    
    test_docker_networks
    echo ""
    
    test_attack_simulator
    echo ""
    
    echo -e "${BLUE}================================${NC}"
    echo -e "${GREEN}Test Suite Complete!${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Main script logic
main() {
    case "${1:-all}" in
        "api")
            print_header
            test_nerve_center_api
            echo ""
            test_frontend_api
            ;;
        "network")
            print_header
            test_docker_networks
            ;;
        "attack")
            print_header
            test_attack_simulator
            ;;
        "all"|*)
            run_all_tests
            ;;
    esac
}

main "$@"