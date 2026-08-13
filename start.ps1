Write-Host "Starting Ataraxia v3..." -ForegroundColor Cyan

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; backend\.venv\Scripts\python -m uvicorn backend.main:app --reload --port 8001" -WindowStyle Normal -PassThru

$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev" -WindowStyle Normal -PassThru

Start-Sleep 3
Start-Process "http://localhost:5173"

Write-Host "Backend and frontend started. Close their windows to stop." -ForegroundColor Green
