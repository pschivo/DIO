@echo off
REM DIO Attack Simulator Launch Script for Windows
REM This script helps you easily launch attack simulations against DIO platform

setlocal enabledelayedexpansion

print_header() {
    echo =================================
    echo   DIO Attack Simulator
    echo =================================
    echo.
}

print_attack_header() {
    echo 🎯 Attack Simulation Options
    echo ============================
    echo.
}

show_usage() {
    print_header
    print_attack_header
    echo Quick Attack Commands:
    echo   %0 cpu         - Simulate CPU exhaustion (crypto-mining)
    echo   %0 memory      - Simulate memory leak attack
    echo   %0 network     - Simulate network flood/DDoS
    echo   %0 process     - Simulate suspicious process activity
    echo   %0 file        - Simulate file integrity violation
    echo   %0 multi       - Simulate multi-vector coordinated attack
    echo   %0 lateral     - Simulate lateral movement across agents
    echo.
    echo Interactive Mode:
    echo   %0 interactive - Launch interactive attack simulator
    echo.
    echo Attack Sequences:
    echo   %0 sequence    - Run predefined attack sequence
    echo   %0 random      - Run random attacks
    echo.
    echo Utility:
    echo   %0 status      - Check platform status
    echo   %0 help        - Show this help
    echo.
    echo Examples:
    echo   %0 cpu                    # Launch CPU exhaustion attack
    echo   %0 interactive            # Enter interactive mode
    echo   %0 sequence               # Run attack sequence
}

check_platform() {
    echo [INFO] Checking DIO Platform status...
    
    curl -s http://localhost:8000/health >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Nerve Center is not running
        echo [WARNING] Please start DIO platform first:
        echo   start.bat dev
        pause
        exit /b 1
    ) else (
        echo [INFO] ✓ Nerve Center is running
    )
    
    curl -s http://localhost:3000 >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Frontend is not running
    ) else (
        echo [INFO] ✓ Frontend is running
    )
    
    echo.
}

run_attack_simulator() {
    set attack_type=%1
    
    echo [INFO] Starting attack simulator...
    echo [WARNING] This is a simulation for testing purposes only
    echo.
    
    REM Navigate to attack simulator
    cd components\attack-simulator
    
    REM Build image
    echo [INFO] Building attack simulator...
    docker build -t dio-attack-simulator .
    
    REM Run attack
    echo [INFO] Launching %attack_type% attack simulation...
    docker run --rm --network dio-network dio-attack-simulator python main.py %attack_type%
    
    cd ..\..
    
    echo.
    echo [INFO] Attack simulation completed!
    echo [INFO] Check dashboard at http://localhost:3000 to see the results
}

run_interactive_mode() {
    echo [INFO] Starting interactive attack simulator...
    echo [WARNING] This is a simulation for testing purposes only
    echo.
    
    cd components\attack-simulator
    
    REM Build image
    echo [INFO] Building attack simulator...
    docker build -t dio-attack-simulator .
    
    REM Run interactive mode
    echo [INFO] Launching interactive mode...
    docker run --rm -it --network dio-network dio-attack-simulator python main.py interactive
    
    cd ..\..
}

run_attack_sequence() {
    echo [INFO] Running predefined attack sequence...
    echo [INFO] This will demonstrate multiple attack types in sequence
    echo.
    
    call :run_attack_simulator cpu
    echo [INFO] Waiting 10 seconds before next attack...
    timeout /t 10 /nobreak >nul
    echo.
    
    call :run_attack_simulator memory
    echo [INFO] Waiting 10 seconds before next attack...
    timeout /t 10 /nobreak >nul
    echo.
    
    call :run_attack_simulator network
    echo [INFO] Waiting 10 seconds before next attack...
    timeout /t 10 /nobreak >nul
    echo.
    
    call :run_attack_simulator process
    echo [INFO] Waiting 10 seconds before next attack...
    timeout /t 10 /nobreak >nul
    echo.
    
    call :run_attack_simulator file
    
    echo [INFO] Attack sequence completed!
    echo [INFO] Check dashboard to see all detected threats and evidence
}

run_random_attacks() {
    echo [INFO] Running random attack sequence...
    echo [INFO] This will run 3-5 random attacks
    echo.
    
    set /a num_attacks=%random% %% 3 + 3
    
    for /l %%i in (1,1,!num_attacks!) do (
        set /a attack_choice=%random% %% 7
        if !attack_choice! == 0 set attack_type=cpu
        if !attack_choice! == 1 set attack_type=memory
        if !attack_choice! == 2 set attack_type=network
        if !attack_choice! == 3 set attack_type=process
        if !attack_choice! == 4 set attack_type=file
        if !attack_choice! == 5 set attack_type=multi
        if !attack_choice! == 6 set attack_type=lateral
        
        echo === Attack %%i/!num_attacks!: !attack_type! ===
        call :run_attack_simulator !attack_type!
        echo [INFO] Waiting 5 seconds before next attack...
        timeout /t 5 /nobreak >nul
        echo.
    )
    
    echo [INFO] Random attack sequence completed!
}

show_status() {
    call :check_platform
    
    echo Agent Status:
    echo   Dashboard: http://localhost:3000
    echo   API Docs:  http://localhost:8000/docs
    echo.
    echo Open the dashboard to see real-time agent status and threats
}

REM Main script logic
if "%1"=="cpu" goto cpu
if "%1"=="memory" goto memory
if "%1"=="network" goto network
if "%1"=="process" goto process
if "%1"=="file" goto file
if "%1"=="multi" goto multi
if "%1"=="lateral" goto lateral
if "%1"=="interactive" goto interactive
if "%1"=="sequence" goto sequence
if "%1"=="random" goto random
if "%1"=="status" goto status
goto help

:cpu
call :check_platform
call :run_attack_simulator cpu
goto end

:memory
call :check_platform
call :run_attack_simulator memory
goto end

:network
call :check_platform
call :run_attack_simulator network
goto end

:process
call :check_platform
call :run_attack_simulator process
goto end

:file
call :check_platform
call :run_attack_simulator file
goto end

:multi
call :check_platform
call :run_attack_simulator multi
goto end

:lateral
call :check_platform
call :run_attack_simulator lateral
goto end

:interactive
call :check_platform
call :run_interactive_mode
goto end

:sequence
call :check_platform
call :run_attack_sequence
goto end

:random
call :check_platform
call :run_random_attacks
goto end

:status
call :show_status
goto end

:help
call :show_usage
goto end

:end
pause