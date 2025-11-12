@echo off
REM Batch wrapper for AI Text Analysis
REM This script calls the Python CLI to analyze files

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo FEJL: Python er ikke installeret eller ikke i PATH
    echo.
    echo Installer Python fra https://www.python.org/downloads/
    echo Husk at vaelge "Add Python to PATH" under installation
    pause
    exit /b 1
)

REM Run the Python CLI with all arguments
python analyze_cli.py %*

REM Pause to see results if run directly (not from Send To)
if "%1"=="" pause
