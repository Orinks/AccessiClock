#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Start script for Accessible Talking Clock application
    
.DESCRIPTION
    This script activates the Python virtual environment and starts the 
    Accessible Talking Clock application in development mode using Briefcase.
    
.NOTES
    This application is designed for accessibility and works with screen readers
    like NVDA and JAWS on Windows.
#>

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "=== Starting Accessible Talking Clock ===" -ForegroundColor Green
Write-Host "Designed for accessibility with screen reader support" -ForegroundColor Cyan

try {
    # Check if virtual environment exists
    if (-not (Test-Path "..\..\.venv")) {
        Write-Host "ERROR: Virtual environment not found at ..\..\.venv" -ForegroundColor Red
        Write-Host "Please run setup first from the parent directory:" -ForegroundColor Yellow
        Write-Host "  uv venv && .venv\Scripts\activate && uv pip install briefcase toga pygame" -ForegroundColor Yellow
        exit 1
    }
    
    # Activate virtual environment
    Write-Host "Activating Python virtual environment..." -ForegroundColor Yellow
    & "..\..\..\.venv\Scripts\Activate.ps1"
    
    # Check if briefcase is available
    try {
        python -m briefcase --version | Out-Null
    }
    catch {
        Write-Host "ERROR: Briefcase not found. Installing..." -ForegroundColor Yellow
        python -m pip install briefcase
    }
    
    Write-Host "Starting Accessible Talking Clock..." -ForegroundColor Green
    Write-Host "Use Tab key to navigate controls, screen readers will announce all elements" -ForegroundColor Cyan
    
    # Start the application
    python -m briefcase dev
    
} catch {
    Write-Host "ERROR: Failed to start application: $_" -ForegroundColor Red
    Write-Host "Check that you're in the correct directory and virtual environment is set up" -ForegroundColor Yellow
    exit 1
}

Write-Host "Application closed." -ForegroundColor Green