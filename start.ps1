# AccessiClock startup script for Windows

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate virtual environment
& ".venv\Scripts\Activate.ps1"

# Install/update dependencies
Write-Host "Checking dependencies..."
pip install -e . --quiet

# Run the application
Write-Host "Starting AccessiClock..."
python -m accessiclock
