#!/bin/bash

# DIO Network Checker
# Finds the correct Docker network for DIO platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  DIO Network Checker${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_header

echo -e "${GREEN}Available Docker Networks:${NC}"
echo ""

# List all networks and find DIO-related ones
docker network ls --format "table {{.Name}}\t{{.Driver}}" | while IFS=$'\t' read -r name driver; do
    if [[ "$name" == *"dio"* ]] || [[ "$name" == *"DIO"* ]]; then
        echo -e "${GREEN}✓${NC} ${name} (${driver})"
    else
        echo "  ${name} (${driver})"
    fi
done

echo ""
echo -e "${YELLOW}Network Names to Try:${NC}"
echo "  dio_dio-network"
echo "  dio-network" 
echo "  my-project_dio-network"
echo "  $(basename $(pwd))_dio-network"
echo ""

echo -e "${CYAN}Testing Network Connectivity:${NC}"
echo ""

# Test common network names
networks_to_test=("dio_dio-network" "dio-network" "my-project_dio-network" "$(basename $(pwd))_dio-network")

for network in "${networks_to_test[@]}"; do
    if docker network inspect "$network" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Network '$network' exists"
        
        # Test if we can reach nerve center
        if docker run --rm --network "$network" alpine ping -c 1 nerve-center >/dev/null 2>&1; then
            echo -e "${GREEN}  ✓${NC} Can reach nerve-center on '$network'"
        else
            echo -e "${YELLOW}  ⚠${NC} Cannot reach nerve-center on '$network'"
        fi
    else
        echo -e "${RED}✗${NC} Network '$network' not found"
    fi
done

echo ""
echo -e "${BLUE}================================${NC}"