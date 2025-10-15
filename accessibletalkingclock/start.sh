#!/bin/bash

# Start script for Accessible Talking Clock application
# This script activates the Python virtual environment and starts the 
# Accessible Talking Clock application in development mode using Briefcase.

set -e  # Exit on any error

echo "=== Starting Accessible Talking Clock ==="
echo "Designed for accessibility with screen reader support"

# Check if virtual environment exists
if [ ! -d "../../.venv" ]; then
    echo "ERROR: Virtual environment not found at ../../.venv"
    echo "Please run setup first from the parent directory:"
    echo "  uv venv && .venv/bin/activate && uv pip install briefcase toga pygame"
    exit 1
fi

# Activate virtual environment
echo "Activating Python virtual environment..."
source ../../.venv/bin/activate

# Check if briefcase is available
if ! python -m briefcase --version > /dev/null 2>&1; then
    echo "ERROR: Briefcase not found. Installing..."
    python -m pip install briefcase
fi

echo "Starting Accessible Talking Clock..."
echo "Use Tab key to navigate controls, screen readers will announce all elements"

# Start the application
python -m briefcase dev

echo "Application closed."