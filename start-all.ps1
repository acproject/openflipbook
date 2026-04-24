# Endless Canvas - Startup Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Endless Canvas - Local Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found" -ForegroundColor Red
    pause
    exit 1
}

# Check Node.js
Write-Host "[2/4] Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = & node --version 2>&1
    Write-Host "  Found: Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Node.js not found" -ForegroundColor Red
    pause
    exit 1
}

# Check venv
$venvPath = Join-Path $PSScriptRoot "apps\modal-backend\.venv"
if (-Not (Test-Path $venvPath)) {
    Write-Host "[3/4] Creating Python venv..." -ForegroundColor Yellow
    Set-Location "apps\modal-backend"
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    Set-Location "..\.."
} else {
    Write-Host "[3/4] Python venv exists" -ForegroundColor Green
}

# Check node_modules
$nodeModulesPath = Join-Path $PSScriptRoot "node_modules"
if (-Not (Test-Path $nodeModulesPath)) {
    Write-Host "  Installing Node.js deps..." -ForegroundColor Yellow
    pnpm install
} else {
    Write-Host "  Node.js deps installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Python backend
Write-Host "Starting Python backend (port 8787)..." -ForegroundColor Yellow
$backendCmd = "cd '$PSScriptRoot\apps\modal-backend'; .\.venv\Scripts\activate; `$env:PORT=8787; python local_server.py"
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -PassThru -WindowStyle Normal

# Wait for backend
Start-Sleep -Seconds 3

# Start Next.js frontend
Write-Host "Starting Next.js frontend (port 3000)..." -ForegroundColor Yellow
$frontendCmd = "cd '$PSScriptRoot\apps\web'; pnpm dev"
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -PassThru -WindowStyle Normal

# Wait for frontend
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Services started successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Web App: http://localhost:3000/play" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8787/health" -ForegroundColor Cyan
Write-Host "Status Page: http://localhost:3000/status" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window (services will continue running)..." -ForegroundColor Yellow
pause
