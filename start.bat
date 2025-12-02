@echo off
REM DIO Platform Startup Script for Windows
REM This script helps you quickly start the DIO platform in different modes

setlocal enabledelayedexpansion

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo [INFO] Docker is running

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] docker-compose is not installed. Please install docker-compose first.
    pause
    exit /b 1
)
echo [INFO] docker-compose is available

REM Parse command
if "%1"=="dev" goto dev
if "%1"=="prod" goto prod
if "%1"=="stop" goto stop
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="clean" goto clean
goto help

:dev
echo [INFO] Starting DIO Platform in development mode...
echo [INFO] This will start: Frontend, Nerve Center, Mesh Network, Agents, and Mock Data
echo.

REM Initialize database
echo [INFO] Initializing database...
if docker compose ps | findstr /C:"database" >nul 2>&1 (
    echo [INFO] PostgreSQL is running, running migrations...
    docker compose exec frontend npm run db:migrate
) else (
    echo [INFO] SQLite mode, pushing schema...
    docker compose exec frontend npm run db:push
)

REM Start services with mock data
echo [INFO] Starting Docker services...
docker compose --profile mock up -d

echo [INFO] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo [INFO] Development environment is ready!
echo.
echo [INFO] 🚀 DIO Platform is now running:
echo   Frontend Dashboard: http://localhost:3000
echo   Nerve Center API:   http://localhost:8000
echo   API Documentation:  http://localhost:8000/docs
echo   Mesh Network:       ws://localhost:4222
echo.
echo [INFO] To view logs: %0 logs
echo [INFO] To stop services: %0 stop
goto end

:prod
echo [INFO] Starting DIO Platform in production mode...
echo [INFO] This will start: Frontend, Nerve Center, Mesh Network, Agents, Database, Redis, NATS
echo.

REM Initialize database
echo [INFO] Initializing database...
echo [INFO] PostgreSQL is running, running migrations...
docker compose exec frontend npm run db:migrate

REM Start production services
echo [INFO] Starting Docker services...
docker compose --profile production up -d

echo [INFO] Waiting for services to be ready...
timeout /t 15 /nobreak >nul

echo [INFO] Production environment is ready!
echo.
echo [INFO] 🚀 DIO Platform is now running:
echo   Frontend Dashboard: http://localhost:3000
echo   Nerve Center API:   http://localhost:8000
echo   API Documentation:  http://localhost:8000/docs
echo   Database:           postgresql://localhost:5432
echo.
echo [INFO] To view logs: %0 logs
echo [INFO] To stop services: %0 stop
goto end

:stop
echo [INFO] Stopping all DIO Platform services...
docker compose down
echo [INFO] All services stopped
goto end

:logs
echo [INFO] Showing logs for all services (Press Ctrl+C to exit)...
docker compose logs -f
goto end

:status
echo [INFO] DIO Platform Service Status:
echo.
docker compose ps
echo.

REM Check if services are responding
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo   Frontend: ✗ Not responding
) else (
    echo   Frontend: ✓ Running
)

curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo   Nerve Center: ✗ Not responding
) else (
    echo   Nerve Center: ✓ Running
)

curl -s http://localhost:4222 >nul 2>&1
if errorlevel 1 (
    echo   Mesh Network: ✗ Not responding
) else (
    echo   Mesh Network: ✓ Running
)
goto end

:clean
echo [WARNING] This will remove all containers, networks, and volumes.
set /p confirm="Are you sure you want to continue? (y/N): "
if /i "!confirm!"=="y" (
    echo [INFO] Cleaning up Docker resources...
    docker compose down -v --remove-orphans
    docker system prune -f
    echo [INFO] Cleanup completed
) else (
    echo [INFO] Cleanup cancelled
)
goto end

:help
echo Usage: %0 [COMMAND]
echo.
echo Commands:
echo   dev       Start development environment with mock data
echo   prod      Start production environment
echo   stop      Stop all services
echo   logs      Show logs for all services
echo   status    Show status of all services
echo   clean     Clean up all containers and volumes
echo   help      Show this help message
echo.
echo Examples:
echo   %0 dev    # Start with mock data for development
echo   %0 prod   # Start production environment
echo   %0 stop   # Stop all services

:end
pause