#!/bin/bash

# DIO Docker Manager
# Simplified Docker commands for DIO platform

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
    echo -e "${BLUE}  DIO Docker Manager${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

show_usage() {
    print_header
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 <command> [options]"
    echo ""
    echo -e "${CYAN}Commands:${NC}"
    echo "  up [profile]        - Start DIO platform"
    echo "  down [options]      - Stop DIO platform"
    echo "  restart [profile]   - Restart DIO platform"
    echo "  status             - Show platform status"
    echo "  logs [service]     - Show service logs"
    echo "  clean              - Clean up unused resources"
    echo ""
    echo -e "${CYAN}Profiles:${NC}"
    echo "  production         - Production environment (default)"
    echo "  development        - Development environment with mock data"
    echo "  testing           - Testing environment with attack simulator"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 up production    # Start production environment"
    echo "  $0 down -v         # Stop and remove volumes"
    echo "  $0 restart         # Restart production"
    echo "  $0 logs frontend   # Show frontend logs"
}

start_platform() {
    local profile=${1:-production}
    echo -e "${GREEN}[INFO]${NC} Starting DIO platform with profile: ${profile}"
    
    case $profile in
        "production")
            docker compose --profile production up -d --build
            ;;
        "development")
            docker compose --profile development up -d --build
            ;;
        "testing")
            docker compose --profile testing up -d --build
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Unknown profile: $profile"
            echo -e "${YELLOW}Available profiles: production, development, testing${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}[INFO]${NC} Platform started successfully!"
    echo -e "${CYAN}Dashboard: http://localhost:3000${NC}"
    echo -e "${CYAN}API Docs: http://localhost:8000/docs${NC}"
}

stop_platform() {
    local options=$1
    echo -e "${GREEN}[INFO]${NC} Stopping DIO platform..."
    
    if [ "$options" = "-v" ]; then
        echo -e "${YELLOW}[INFO]${NC} Removing volumes..."
        docker compose down -v
    else
        docker compose down
    fi
    
    echo -e "${GREEN}[INFO]${NC} Platform stopped successfully!"
}

restart_platform() {
    local profile=${1:-production}
    echo -e "${GREEN}[INFO]${NC} Restarting DIO platform..."
    
    stop_platform
    sleep 2
    start_platform $profile
}

show_status() {
    print_header
    echo -e "${CYAN}DIO Platform Status:${NC}"
    echo ""
    
    # Show running containers
    echo -e "${GREEN}Running Services:${NC}"
    docker compose ps
    echo ""
    
    # Check if key services are accessible
    echo -e "${CYAN}Service Health:${NC}"
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Nerve Center (http://localhost:8000)"
    else
        echo -e "${RED}✗${NC} Nerve Center (http://localhost:8000)"
    fi
    
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend (http://localhost:3000)"
    else
        echo -e "${RED}✗${NC} Frontend (http://localhost:3000)"
    fi
    
    echo ""
}

show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        echo -e "${YELLOW}[INFO]${NC} Showing logs for all services..."
        docker compose logs -f
    else
        echo -e "${YELLOW}[INFO]${NC} Showing logs for $service..."
        docker compose logs -f "$service"
    fi
}

clean_resources() {
    echo -e "${GREEN}[INFO]${NC} Cleaning up unused Docker resources..."
    
    # Remove stopped containers
    echo -e "${CYAN}[INFO]${NC} Removing stopped containers..."
    docker container prune -f
    
    # Remove unused images
    echo -e "${CYAN}[INFO]${NC} Removing unused images..."
    docker image prune -f
    
    # Remove unused networks
    echo -e "${CYAN}[INFO]${NC} Removing unused networks..."
    docker network prune -f
    
    echo -e "${GREEN}[INFO]${NC} Cleanup completed!"
}

# Main script logic
main() {
    case "${1:-help}" in
        "up")
            start_platform $2
            ;;
        "down")
            stop_platform $2
            ;;
        "restart")
            restart_platform $2
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs $2
            ;;
        "clean")
            clean_resources
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

print_header
main "$@"