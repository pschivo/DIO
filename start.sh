#!/bin/bash

# DIO Platform Startup Script
# This script helps you quickly start the DIO platform in different modes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  DIO Platform Startup Script${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_status "Docker is running"
}

# Check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install docker-compose first."
        exit 1
    fi
    print_status "docker-compose is available"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  dev       Start development environment with mock data"
    echo "  prod      Start production environment"
    echo "  stop      Stop all services"
    echo "  logs      Show logs for all services"
    echo "  status    Show status of all services"
    echo "  clean     Clean up all containers and volumes"
    echo "  help      Show this help message"
    echo ""
    echo "Options:"
    echo "  --agents=N    Set number of agents (default: 3 for prod, 0 for dev)"
    echo "  --mock=N     Set number of mock agents (default: 12)"
    echo ""
    echo "Examples:"
    echo "  $0 dev                    # Start with defaults"
    echo "  $0 dev --mock=20          # Start with 20 mock agents"
    echo "  $0 prod                   # Start production with 3 agents"
    echo "  $0 prod --agents=5        # Start production with 5 agents"
    echo "  $0 stop                   # Stop all services"
}

# Start development environment
start_dev() {
    local mock_agents=12
    
    # Parse arguments
    for arg in "$@"; do
        case $arg in
            --mock=*)
                mock_agents="${arg#*=}"
                ;;
        esac
    done
    
    print_status "Starting DIO Platform in development mode..."
    print_status "This will start: Frontend, Nerve Center, Mesh Network, Agents, and Mock Data"
    print_status "Mock agents: $mock_agents"
    echo ""
    
    # Initialize database
    print_status "Initializing database..."
    if docker compose ps | grep -q database; then
        print_status "PostgreSQL is running, running migrations..."
        docker compose exec frontend npm run db:migrate
    else
        print_status "SQLite mode, pushing schema..."
        docker compose exec frontend npm run db:push
    fi
    
    # Start services with mock data
    print_status "Starting Docker services..."
    MOCK_AGENT_COUNT=$mock_agents docker compose --profile development up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    check_services
    
    print_status "Development environment is ready!"
    echo ""
    echo -e "${GREEN}🚀 DIO Platform is now running:${NC}"
    echo -e "  Frontend Dashboard: ${BLUE}http://localhost:3000${NC}"
    echo -e "  Nerve Center API:   ${BLUE}http://localhost:8000${NC}"
    echo -e "  API Documentation:  ${BLUE}http://localhost:8000/docs${NC}"
    echo -e "  Mesh Network:       ${BLUE}ws://localhost:4222${NC}"
    echo ""
    echo -e "${YELLOW}To view logs: $0 logs${NC}"
    echo -e "${YELLOW}To stop services: $0 stop${NC}"
}

# Start production environment
start_prod() {
    local agent_count=3
    
    # Parse arguments
    for arg in "$@"; do
        case $arg in
            --agents=*)
                agent_count="${arg#*=}"
                ;;
        esac
    done
    
    print_status "Starting DIO Platform in production mode..."
    print_status "This will start: Frontend, Nerve Center, Mesh Network, Real Agents, Database, Redis, NATS"
    print_status "Real agents: $agent_count"
    echo ""
    
    # Initialize database
    print_status "Initializing database..."
    print_status "PostgreSQL is running, running migrations..."
    docker compose exec frontend npm run db:migrate
    
    # Start production services
    print_status "Starting Docker services..."
    AGENT_COUNT=$agent_count docker compose --profile production up -d
    
    print_status "Waiting for services to be ready..."
    sleep 15
    
    # Check service health
    check_services
    
    print_status "Production environment is ready!"
    echo ""
    echo -e "${GREEN}🚀 DIO Platform is now running:${NC}"
    echo -e "  Frontend Dashboard: ${BLUE}http://localhost:3000${NC}"
    echo -e "  Nerve Center API:   ${BLUE}http://localhost:8000${NC}"
    echo -e "  API Documentation:  ${BLUE}http://localhost:8000/docs${NC}"
    echo -e "  Database:           ${BLUE}postgresql://localhost:5432${NC}"
    echo ""
    echo -e "${YELLOW}To view logs: $0 logs${NC}"
    echo -e "${YELLOW}To stop services: $0 stop${NC}"
}

# Stop all services
stop_services() {
    print_status "Stopping all DIO Platform services..."
    docker compose down
    print_status "All services stopped"
}

# Show logs
show_logs() {
    print_status "Showing logs for all services (Press Ctrl+C to exit)..."
    docker compose logs -f
}

# Show status
show_status() {
    print_status "DIO Platform Service Status:"
    echo ""
    docker compose ps
    echo ""
    
    # Check if services are responding
    print_status "Checking service health..."
    
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "  Frontend: ${GREEN}✓ Running${NC}"
    else
        echo -e "  Frontend: ${RED}✗ Not responding${NC}"
    fi
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "  Nerve Center: ${GREEN}✓ Running${NC}"
    else
        echo -e "  Nerve Center: ${RED}✗ Not responding${NC}"
    fi
    
    if curl -s http://localhost:4222 > /dev/null 2>&1; then
        echo -e "  Mesh Network: ${GREEN}✓ Running${NC}"
    else
        echo -e "  Mesh Network: ${RED}✗ Not responding${NC}"
    fi
}

# Clean up
clean_up() {
    print_warning "This will remove all containers, networks, and volumes."
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up Docker resources..."
        docker compose down -v --remove-orphans
        docker system prune -f
        print_status "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Check service health
check_services() {
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Checking service health (attempt $attempt/$max_attempts)..."
        
        local healthy=true
        
        # Check frontend
        if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
            healthy=false
        fi
        
        # Check nerve center
        if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
            healthy=false
        fi
        
        if [ "$healthy" = true ]; then
            print_status "All services are healthy!"
            return 0
        fi
        
        sleep 2
        ((attempt++))
    done
    
    print_warning "Some services may not be fully ready yet. Check logs for details."
}

# Main script logic
main() {
    print_header
    
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Parse command
    case "${1:-help}" in
        "dev")
            start_dev "${@:2}"
            ;;
        "prod")
            start_prod "${@:2}"
            ;;
        "stop")
            stop_services
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "clean")
            clean_up
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

# Run main function with all arguments
main "$@"