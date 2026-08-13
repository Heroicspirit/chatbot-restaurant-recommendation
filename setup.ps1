$host.ui.RawUI.WindowTitle = "Ataraxia v3 - Setup"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "     Ataraxia v3 - Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ─── Check prerequisites ─────────────────────────────
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
$missing = @()

try { python --version 2>&1 | Out-Null; Write-Host "  [OK] Python" -ForegroundColor Green }
catch { Write-Host "  [MISS] Python (install from https://python.org)" -ForegroundColor Red; $missing += "Python" }

try { node --version 2>&1 | Out-Null; Write-Host "  [OK] Node.js" -ForegroundColor Green }
catch { Write-Host "  [MISS] Node.js (install from https://nodejs.org)" -ForegroundColor Red; $missing += "Node.js" }

$ollamaOk = $false
try {
    $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
    $ollamaOk = $true; Write-Host "  [OK] Ollama" -ForegroundColor Green
} catch { Write-Host "  [WARN] Ollama not running (install from https://ollama.com)" -ForegroundColor Yellow }

if ($missing.Count -gt 0) {
    Write-Host "`nInstall missing prerequisites first, then re-run this script." -ForegroundColor Red
    pause; exit 1
}

# ─── Create .env if missing ──────────────────────────
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Write-Host "`nCreating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "  [OK] .env created" -ForegroundColor Green
}

# ─── Python virtual env ──────────────────────────────
Write-Host "`nSetting up Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "backend/.venv")) {
    Push-Location backend
    python -m venv .venv
    Pop-Location
    Write-Host "  [OK] Virtual environment created" -ForegroundColor Green
}
Push-Location backend
Write-Host "  Installing pip packages..." -ForegroundColor Gray
& ".\.venv\Scripts\pip" install -r ..\requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Host "  [FAIL] pip install failed" -ForegroundColor Red; Pop-Location; pause; exit 1 }
Pop-Location
Write-Host "  [OK] Python dependencies installed" -ForegroundColor Green

# ─── Frontend dependencies ───────────────────────────
Write-Host "`nInstalling frontend dependencies..." -ForegroundColor Yellow
Push-Location frontend
npm install
if ($LASTEXITCODE -ne 0) { Write-Host "  [FAIL] npm install failed" -ForegroundColor Red; Pop-Location; pause; exit 1 }
Pop-Location
Write-Host "  [OK] Frontend dependencies installed" -ForegroundColor Green

# ─── Ollama model ────────────────────────────────────
if ($ollamaOk) {
    Write-Host "`nChecking Ollama model..." -ForegroundColor Yellow
    try {
        $models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags"
        $hasModel = $models.models | Where-Object { $_.name -like "llama3.2*" }
        if (-not $hasModel) {
            Write-Host "  Pulling llama3.2 model (this may take a while)..." -ForegroundColor Yellow
            Invoke-RestMethod -Uri "http://localhost:11434/api/pull" -Method Post -Body '{"name":"llama3.2"}' -ContentType "application/json"
            Write-Host "  [OK] Model pulled" -ForegroundColor Green
        } else { Write-Host "  [OK] llama3.2 already available" -ForegroundColor Green }
    } catch { Write-Host "  [WARN] Could not check/pull model" -ForegroundColor Yellow }
}

# ─── Create start.ps1 ────────────────────────────────
Write-Host "`nCreating start.ps1 for easy launch..." -ForegroundColor Yellow
@'
Write-Host "Starting Ataraxia v3..." -ForegroundColor Cyan

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; backend\.venv\Scripts\python -m uvicorn backend.main:app --reload --port 8001" -WindowStyle Normal -PassThru

$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev" -WindowStyle Normal -PassThru

Start-Sleep 3
Start-Process "http://localhost:5173"

Write-Host "Backend and frontend started. Close their windows to stop." -ForegroundColor Green
'@ | Set-Content "start.ps1"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "     Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "To run the app next time, double-click:  start.ps1" -ForegroundColor Cyan
Write-Host "Or run manually:" -ForegroundColor Gray
Write-Host "  Backend:  backend\.venv\Scripts\python -m uvicorn backend.main:app --reload --port 8001" -ForegroundColor White
Write-Host "  Frontend: cd frontend; npm run dev" -ForegroundColor White
Write-Host "  Browser:  http://localhost:5173" -ForegroundColor White
Write-Host ""
pause
