<#
  Sobe o backend (FastAPI) e o frontend (Vite) em um único terminal.
  Uso: .\run.ps1
  Ctrl+C encerra os dois.
#>

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

$venvPython = Join-Path $root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Criando ambiente virtual do backend..." -ForegroundColor Yellow
    python -m venv (Join-Path $root "backend\.venv")
    & $venvPython -m pip install -q -r (Join-Path $root "backend\requirements.txt")
}

if (-not (Test-Path (Join-Path $root "frontend\node_modules"))) {
    Write-Host "Instalando dependências do frontend..." -ForegroundColor Yellow
    Push-Location (Join-Path $root "frontend")
    npm install
    Pop-Location
}

$backendJob = Start-Job -Name backend -ScriptBlock {
    param($root, $venvPython)
    Set-Location (Join-Path $root "backend")
    & $venvPython -m uvicorn app.main:app --reload
} -ArgumentList $root, $venvPython

$frontendJob = Start-Job -Name frontend -ScriptBlock {
    param($root)
    Set-Location (Join-Path $root "frontend")
    npm run dev
} -ArgumentList $root

Write-Host ""
Write-Host "Backend:  http://localhost:8000 (docs em /docs)" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "Pressione Ctrl+C para encerrar os dois." -ForegroundColor Cyan
Write-Host ""

try {
    while ($true) {
        Receive-Job -Job $backendJob, $frontendJob
        Start-Sleep -Milliseconds 300
    }
}
finally {
    Write-Host "`nEncerrando servidores..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $backendJob, $frontendJob -Force -ErrorAction SilentlyContinue
}
