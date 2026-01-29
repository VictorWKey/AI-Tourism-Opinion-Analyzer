@echo off
REM ============================================
REM Windows Setup Script - AI Tourism Opinion Analyzer
REM ============================================

echo ============================================
echo AI Tourism Opinion Analyzer - Windows Setup
echo ============================================
echo.

REM Check for Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check for Node.js
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js found
node --version

REM Check for npm
npm --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm is not installed or not in PATH
    pause
    exit /b 1
)

echo [OK] npm found
npm --version

echo.
echo ============================================
echo Step 1: Installing Node.js dependencies
echo ============================================
call npm install
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
)
echo [OK] Node.js dependencies installed

echo.
echo ============================================
echo Step 2: Setting up Python virtual environment
echo ============================================

cd python

if exist "venv\Scripts\python.exe" (
    echo [OK] Virtual environment already exists
) else (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo [INFO] Installing Python dependencies...
call venv\Scripts\pip install --upgrade pip
call venv\Scripts\pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo [WARNING] Some dependencies may have failed to install
    echo Continuing anyway...
) else (
    echo [OK] Python dependencies installed
)

cd ..

echo.
echo ============================================
echo Step 3: Checking Ollama (Optional)
echo ============================================

ollama --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] Ollama is not installed
    echo If you want to use local LLM, download Ollama from:
    echo   https://ollama.com/download/windows
    echo.
    echo You can also use OpenAI API instead of local LLM.
) else (
    echo [OK] Ollama is installed
    ollama --version
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo To start the application, run:
echo   npm start
echo.
echo For development:
echo   npm run start
echo.
pause
