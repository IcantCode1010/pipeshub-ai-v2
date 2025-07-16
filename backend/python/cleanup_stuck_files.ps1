# PowerShell script to clean up stuck files
# Run this script from the backend/python directory

Write-Host "🚀 Starting cleanup of stuck files..." -ForegroundColor Green

# Check if we're in the correct directory
if (-not (Test-Path "app")) {
    Write-Host "❌ Error: Please run this script from the backend/python directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python not found. Please install Python or add it to PATH" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    # Activate virtual environment
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path ".venv") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️ Warning: No virtual environment found. Using system Python" -ForegroundColor Yellow
}

# Run the cleanup script
Write-Host "🔄 Running cleanup script..." -ForegroundColor Cyan
try {
    python quick_cleanup.py
    Write-Host "✅ Cleanup script completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error running cleanup script: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Optional: Check if Kafka consumer needs to be restarted
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Check the logs above for any errors" -ForegroundColor White
Write-Host "2. Files marked as FAILED can be retried using the 'Retry Indexing' button in the UI" -ForegroundColor White
Write-Host "3. Consider restarting the Kafka consumer if many files were stuck" -ForegroundColor White
Write-Host "4. Monitor the system for a few minutes to ensure processing resumes normally" -ForegroundColor White

Write-Host ""
Write-Host "🎯 Cleanup completed! Check the UI to verify file statuses." -ForegroundColor Green 