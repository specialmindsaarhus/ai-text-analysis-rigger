@echo off
REM Creates a desktop shortcut for drag-and-drop file analysis

echo ========================================
echo AI Text Analysis - Desktop Shortcut
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

REM Desktop location
set "DESKTOP=%USERPROFILE%\Desktop"

REM Shortcut path
set "SHORTCUT=%DESKTOP%\AI Text Analyze.lnk"

echo Opretter genvej paa skrivebordet...
echo.

REM Create VBScript to make shortcut
set "VBSCRIPT=%TEMP%\create_desktop_shortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBSCRIPT%"
echo sLinkFile = "%SHORTCUT%" >> "%VBSCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBSCRIPT%"
echo oLink.TargetPath = "%BATCH_FILE%" >> "%VBSCRIPT%"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBSCRIPT%"
echo oLink.Description = "Traek og slip filer for at analysere med AI" >> "%VBSCRIPT%"
echo oLink.Save >> "%VBSCRIPT%"

REM Run VBScript
cscript //nologo "%VBSCRIPT%"

REM Clean up
del "%VBSCRIPT%"

echo.
echo ========================================
echo Genvej oprettet!
echo ========================================
echo.
echo Placering: %SHORTCUT%
echo.
echo Saadan bruger du det:
echo 1. Traek en eller flere filer fra File Explorer
echo 2. Slip dem paa "AI Text Analyze" genvejen paa skrivebordet
echo 3. Vent paa analysen er faerdig
echo.
echo Understottede formater: TXT, PDF, Word (DOCX/DOC)
echo.
pause
