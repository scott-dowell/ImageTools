# ImageTools run script
# Activates the virtual environment and starts the Flask development server

param(
    [switch]$Fresh = $false
)

$ErrorActionPreference = "Stop"

# Resolve the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Virtual environment path
$venvPath = Join-Path $scriptDir ".venv"

# Check if virtual environment exists
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv $venvPath
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "$venvPath\Scripts\Activate.ps1"

# Install or upgrade requirements if fresh flag is set
if ($Fresh) {
    Write-Host "Installing requirements..." -ForegroundColor Cyan
    pip install --upgrade pip
    pip install -r requirements.txt
}

# Run the Flask development server
Write-Host "Starting ImageTools server on http://127.0.0.1:5002" -ForegroundColor Green
python app.py
