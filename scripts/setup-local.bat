@echo off
echo ========================================
echo Endless Canvas - Local Setup
echo ========================================
echo.

echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.12+
    pause
    exit /b 1
)

echo [2/5] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 20+
    pause
    exit /b 1
)

echo [3/5] Setting up Python backend...
cd apps\modal-backend
if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

if not exist .env (
    echo Creating .env file from example...
    copy .env.example .env
    echo.
    echo Please edit apps\modal-backend\.env and configure:
    echo - LOCAL_IMAGE_API_URL (e.g., http://localhost:7860 for AUTOMATIC1111)
    echo - LLAMACPP_BASE_URL (e.g., http://localhost:8080/v1 for llama.cpp)
    echo.
    pause
)

cd ..\..

echo [4/5] Setting up web app...
cd apps\web
if not exist .env.local (
    echo Creating .env.local file...
    copy .env.local.example .env.local
)

cd ..\..

echo [5/5] Installing Node.js dependencies...
call npm install -g pnpm >nul 2>&1
pnpm install

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start llama.cpp server: .\scripts\start-llamacpp.bat
echo 2. Start image generation server (AUTOMATIC1111/ComfyUI)
echo 3. Start backend: .\scripts\start-backend.bat
echo 4. Start web app: .\scripts\start-web.bat
echo.
pause
