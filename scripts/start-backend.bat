@echo off
echo ========================================
echo Starting Endless Canvas Backend
echo ========================================
echo.

cd apps\modal-backend

if not exist .venv (
    echo ERROR: Virtual environment not found. Run setup-local.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting FastAPI server on port 8787...
echo Backend will be available at: http://localhost:8787
echo.

set PORT=8787
python local_server.py

cd ..\..
