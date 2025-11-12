@echo off
REM Installer for AI Text Analysis - Send To Menu
REM This script creates a shortcut in the Send To folder

echo ========================================
echo AI Text Analysis - Send To Installer
echo ========================================
echo.

REM Get the current directory
set "SCRIPT_DIR=%~dp0"

REM Remove trailing backslash
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Path to the batch file
set "BATCH_FILE=%SCRIPT_DIR%\analyze_file.bat"

REM Check if batch file exists
if not exist "%BATCH_FILE%" (
    echo FEJL: analyze_file.bat blev ikke fundet!
    echo Placering: %BATCH_FILE%
    echo.
    pause
    exit /b 1
)

REM Send To folder location
set "SENDTO=%APPDATA%\Microsoft\Windows\SendTo"

REM Shortcut path
set "SHORTCUT=%SENDTO%\AI Text Analyze.lnk"

echo Opretter genvej i Send To menuen...
echo.

REM Create VBScript to make shortcut
set "VBSCRIPT=%TEMP%\create_shortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBSCRIPT%"
echo sLinkFile = "%SHORTCUT%" >> "%VBSCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBSCRIPT%"
echo oLink.TargetPath = "%BATCH_FILE%" >> "%VBSCRIPT%"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBSCRIPT%"
echo oLink.Description = "Analyser tekstfil med AI" >> "%VBSCRIPT%"
echo oLink.Save >> "%VBSCRIPT%"

REM Run VBScript
cscript //nologo "%VBSCRIPT%"

REM Clean up
del "%VBSCRIPT%"

echo.
echo ========================================
echo Installation gennemfoert!
echo ========================================
echo.
echo Genvej oprettet: %SHORTCUT%
echo.
echo Saadan bruger du det:
echo 1. Hojreklik paa en fil (TXT, PDF, eller Word)
echo 2. Vaelg "Send to" ^> "AI Text Analyze"
echo 3. Vent paa analysen er faerdig
echo.
pause
