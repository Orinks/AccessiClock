#!/bin/bash
# AccessiClock startup script for Linux/Mac

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
echo "Checking dependencies..."
pip install -e . --quiet

# Run the application
echo "Starting AccessiClock..."
python -m accessiclock
