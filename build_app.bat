@echo off
:: ====================================================
:: OpenWRT Backup & Restore Tool - Build Script
:: EN: Creates a virtual environment, installs requirements, and packages the app via PyInstaller.
:: RU: Создает виртуальное окружение, устанавливает зависимости и упаковывает приложение через PyInstaller.
:: ====================================================

:: Ensure we are in the script's directory
:: Переход в директорию скрипта, чтобы избежать ошибок путей
cd /d "%~dp0"
setlocal enabledelayedexpansion

set "APP_NAME=OWrtBackup&RestoreWin.exe"
set "LOG_FILE=build_log.txt"
set "VENV_DIR=build_venv"
set "PYTHON_INSTALLER=%~dp0python-installer.exe"

:: Initialize log
:: Инициализация лог-файла
if exist "%LOG_FILE%" del /f /q "%LOG_FILE%"
echo [%time%] Starting build process for "%APP_NAME%" > "%LOG_FILE%"
echo Starting build process for "%APP_NAME%"... / Начинаем процесс сборки...

:: ==========================================
:: 0. Clean Previous Build
:: 0. Очистка старой сборки
:: ==========================================
if exist "%APP_NAME%" (
    echo Removing previous executable: "%APP_NAME%"... / Удаление старого исполняемого файла...
    echo [%time%] Removing previous executable... >> "%LOG_FILE%"
    
    REM Kill the process if it's currently running so we can delete the file
    REM Завершаем процесс, если программа запущена, чтобы файл не был заблокирован
    taskkill /IM "%APP_NAME%" /F >nul 2>nul
    
    del /f /q "%APP_NAME%"
)

echo Cleaning up previous build artifacts... / Очистка артефактов предыдущей сборки...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /f /q "*.spec"
if exist "__pycache__" rmdir /s /q "__pycache__"

:: ==========================================
:: 1. Check for Python
:: 1. Проверка наличия установленного Python
:: ==========================================
echo [%time%] Checking for Python... >> "%LOG_FILE%"
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo Python is already installed. / Python уже установлен.
    echo [%time%] Python is already installed. >> "%LOG_FILE%"
    goto :VENV_CREATION
)

echo Python not found. Downloading Python installer... / Python не найден. Скачиваем установщик...
echo [%time%] Python not found. Downloading installer... >> "%LOG_FILE%"

:: Use PowerShell to securely download python
:: Используем PowerShell для безопасного скачивания установщика Python
powershell -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile '%PYTHON_INSTALLER%'"

if not exist "%PYTHON_INSTALLER%" (
    echo Failed to download Python installer. File not found. / Ошибка скачивания установщика.
    echo [%time%] Failed to download Python installer. >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Check if the installer file size is valid
:: Проверка размера файла установщика на предмет повреждения
for %%I in ("%PYTHON_INSTALLER%") do set "FILESIZE=%%~zI"
if !FILESIZE! LSS 1000000 (
    echo Downloaded installer is corrupted or empty! Size: !FILESIZE! bytes. / Файл установщика поврежден!
    echo Please check your internet connection or antivirus. / Проверьте интернет или антивирус.
    echo [%time%] Installer corrupted. >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo Installing Python quietly... (this may take a few minutes) / Устанавливаем Python в скрытом режиме...
echo [%time%] Installing Python quietly... >> "%LOG_FILE%"
start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

if %errorLevel% neq 0 (
    echo Failed to install Python. Exit code: %errorLevel% / Ошибка установки Python.
    echo [%time%] Failed to install Python. >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo Python installed successfully. / Python успешно установлен.
echo [%time%] Python installed. >> "%LOG_FILE%"

:: Refresh environment variables using powershell trick to get updated PATH
:: Обновление переменных окружения для подхвата новых путей Python без перезагрузки
for /f "tokens=*" %%i in ('powershell -Command "[Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')"') do set "PATH=%%i"

:VENV_CREATION
:: ==========================================
:: 2. Create Virtual Environment
:: 2. Создание виртуального окружения
:: ==========================================
if exist "%VENV_DIR%" (
    echo Removing existing virtual environment... / Удаление старого виртуального окружения...
    rmdir /s /q "%VENV_DIR%"
)

echo Creating virtual environment... / Создаем виртуальное окружение...
echo [%time%] Creating virtual environment... >> "%LOG_FILE%"
python -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Failed to create virtual environment! / Не удалось создать виртуальное окружение!
    echo [%time%] Failed to create virtual environment! >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: ==========================================
:: 3. Install Requirements & PyInstaller
:: 3. Установка зависимостей и сборщика PyInstaller
:: ==========================================
set "VENV_PYTHON=%~dp0%VENV_DIR%\Scripts\python.exe"
set "VENV_PIP=%~dp0%VENV_DIR%\Scripts\pip.exe"

echo Upgrading pip... / Обновление менеджера пакетов pip...
echo [%time%] Upgrading pip... >> "%LOG_FILE%"
"%VENV_PYTHON%" -m pip install --no-cache-dir --upgrade pip >> "%LOG_FILE%" 2>&1

if exist "requirements.txt" (
    echo Installing requirements... / Установка библиотек из requirements.txt...
    echo [%time%] Installing requirements... >> "%LOG_FILE%"
    "%VENV_PIP%" install --no-cache-dir -r requirements.txt >> "%LOG_FILE%" 2^>^&1
)

echo Installing PyInstaller... / Установка PyInstaller...
echo [%time%] Installing PyInstaller... >> "%LOG_FILE%"
"%VENV_PIP%" install --no-cache-dir pyinstaller >> "%LOG_FILE%" 2>&1

:: ==========================================
:: 4. Build EXE
:: 4. Сборка исполняемого файла (.exe)
:: ==========================================
set "PYINSTALLER_EXE=%~dp0%VENV_DIR%\Scripts\pyinstaller.exe"

echo Building executable with PyInstaller/PyWebView... / Запуск сборки через PyInstaller (PyWebView)...
echo [%time%] Building executable... >> "%LOG_FILE%"
"%PYINSTALLER_EXE%" --noconsole --onefile --name "OWrtBackup&RestoreWin" --icon "icon.ico" --add-data "web;web" "main_webview.py" >> "%LOG_FILE%" 2>&1

:: ==========================================
:: 5. Move EXE and Cleanup
:: 5. Перенос готового EXE и очистка временных файлов
:: ==========================================
if exist "dist\OWrtBackup&RestoreWin.exe" (
    echo Build successful. Moving executable... / Сборка успешна. Перенос файла...
    echo [%time%] Build successful. Moving executable... >> "%LOG_FILE%"
    if exist "%APP_NAME%" del /f /q "%APP_NAME%"
    move "dist\OWrtBackup&RestoreWin.exe" "%APP_NAME%" >nul
) else (
    echo Error: Executable was not found in dist folder! / Ошибка: EXE файл не найден!
    echo [%time%] Error: Executable was not found in dist folder! >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo Cleaning up temporary files... / Удаление временных файлов сборки...
echo [%time%] Cleaning up... >> "%LOG_FILE%"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /f /q "*.spec"
if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
if exist "%PYTHON_INSTALLER%" del /f /q "%PYTHON_INSTALLER%"

echo ====================================================
echo SUCCESS! Executable is ready: "%APP_NAME%"
echo NOTE: It is now a single standalone executable.
echo ----------------------------------------------------
echo ГОТОВО! Исполняемый файл создан: "%APP_NAME%"
echo ВАЖНО: Это полностью автономный исполняемый файл.
echo ====================================================
echo [%time%] Build script finished successfully. >> "%LOG_FILE%"

:: ==========================================
:: 6. Launch Application / Запуск приложения
:: ==========================================
echo.
echo Build process completed successfully! / Сборка успешно завершена!
echo The application will start in 10 seconds... / Приложение запустится через 10 секунд...
echo.
timeout /t 10
start "" "OWrtBackup&RestoreWin.exe"

exit /b 0
