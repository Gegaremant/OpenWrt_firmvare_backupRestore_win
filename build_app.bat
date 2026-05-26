@echo off
setlocal enabledelayedexpansion

:: ==========================================
:: Request Administrator Privileges
:: ==========================================
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

:: Ensure we are in the script's directory
cd /d "%~dp0"

set "APP_NAME=OWrtBackup&RestoreWin.exe"
set "LOG_FILE=build_log.txt"
set "VENV_DIR=build_venv"
set "PYTHON_INSTALLER=%~dp0python-installer.exe"

:: Initialize log
if exist "%LOG_FILE%" del /f /q "%LOG_FILE%"
echo [%time%] Starting build process for "%APP_NAME%" > "%LOG_FILE%"
echo Starting build process for "%APP_NAME%"...

:: ==========================================
:: 1. Check for Python
:: ==========================================
echo [%time%] Checking for Python... >> "%LOG_FILE%"
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo Python is already installed.
    echo [%time%] Python is already installed. >> "%LOG_FILE%"
    goto :VENV_CREATION
)

echo Python not found. Downloading Python installer...
echo [%time%] Python not found. Downloading installer... >> "%LOG_FILE%"

:: Use PowerShell to securely download python
powershell -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile '%PYTHON_INSTALLER%'"

if not exist "%PYTHON_INSTALLER%" (
    echo Failed to download Python installer. File not found.
    echo [%time%] Failed to download Python installer. >> "%LOG_FILE%"
    pause
    exit /b 1
)

for %%I in ("%PYTHON_INSTALLER%") do set "FILESIZE=%%~zI"
if !FILESIZE! LSS 1000000 (
    echo Downloaded installer is corrupted or empty! Size: !FILESIZE! bytes.
    echo Please check your internet connection or antivirus.
    echo [%time%] Installer corrupted. >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo Installing Python quietly... (this may take a few minutes)
echo [%time%] Installing Python quietly... >> "%LOG_FILE%"
start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

if %errorLevel% neq 0 (
    echo Failed to install Python. Exit code: %errorLevel%
    echo [%time%] Failed to install Python. >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo Python installed successfully.
echo [%time%] Python installed. >> "%LOG_FILE%"

:: Refresh environment variables using powershell trick to get updated PATH
for /f "tokens=*" %%i in ('powershell -Command "[Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')"') do set "PATH=%%i"

:VENV_CREATION
:: ==========================================
:: 2. Create Virtual Environment
:: ==========================================
if exist "%VENV_DIR%" (
    echo Removing existing virtual environment...
    rmdir /s /q "%VENV_DIR%"
)

echo Creating virtual environment...
echo [%time%] Creating virtual environment... >> "%LOG_FILE%"
python -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Failed to create virtual environment!
    echo [%time%] Failed to create virtual environment! >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: ==========================================
:: 3. Install Requirements & PyInstaller
:: ==========================================
set "VENV_PYTHON=%~dp0%VENV_DIR%\Scripts\python.exe"
set "VENV_PIP=%~dp0%VENV_DIR%\Scripts\pip.exe"

echo Upgrading pip...
echo [%time%] Upgrading pip... >> "%LOG_FILE%"
"%VENV_PYTHON%" -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1

if exist "requirements.txt" (
    echo Installing requirements...
    echo [%time%] Installing requirements... >> "%LOG_FILE%"
    "%VENV_PIP%" install -r requirements.txt >> "%LOG_FILE%" 2>&1
)

echo Installing PyInstaller...
echo [%time%] Installing PyInstaller... >> "%LOG_FILE%"
"%VENV_PIP%" install pyinstaller >> "%LOG_FILE%" 2>&1

:: ==========================================
:: 4. Build EXE
:: ==========================================
set "PYINSTALLER_EXE=%~dp0%VENV_DIR%\Scripts\pyinstaller.exe"

echo Building executable with PyInstaller...
echo [%time%] Building executable... >> "%LOG_FILE%"
"%PYINSTALLER_EXE%" --noconsole --onefile --name "OWrtBackup&RestoreWin" "OWrtBackup&RestoreWin.py" >> "%LOG_FILE%" 2>&1

:: ==========================================
:: 5. Move EXE and Cleanup
:: ==========================================
if exist "dist\OWrtBackup&RestoreWin.exe" (
    echo Build successful. Moving executable...
    echo [%time%] Build successful. Moving executable... >> "%LOG_FILE%"
    if exist "%APP_NAME%" del /f /q "%APP_NAME%"
    move "dist\OWrtBackup&RestoreWin.exe" "%APP_NAME%" >nul
) else (
    echo Error: Executable was not found in dist folder!
    echo [%time%] Error: Executable was not found in dist folder! >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo Cleaning up temporary files...
echo [%time%] Cleaning up... >> "%LOG_FILE%"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "OWrtBackup&RestoreWin.spec" del /f /q "OWrtBackup&RestoreWin.spec"
if exist "app.spec" del /f /q "app.spec"
if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
if exist "%PYTHON_INSTALLER%" del /f /q "%PYTHON_INSTALLER%"

echo ====================================================
echo SUCCESS! Executable is ready: "%APP_NAME%"
echo NOTE: Make sure the 'locales' folder is located next 
echo to the executable for translations to work.
echo ====================================================
echo [%time%] Build script finished successfully. >> "%LOG_FILE%"
pause
