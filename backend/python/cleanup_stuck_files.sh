#!/bin/bash

# Bash script to clean up stuck files
# Run this script from the backend/python directory

echo "🚀 Starting cleanup of stuck files..."

# Check if we're in the correct directory
if [ ! -d "app" ]; then
    echo "❌ Error: Please run this script from the backend/python directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Error: Python not found. Please install Python or add it to PATH"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Python found: $($PYTHON_CMD --version)"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "✅ Virtual environment found"
    source .venv/bin/activate
else
    echo "⚠️ Warning: No virtual environment found. Using system Python"
fi

# Run the cleanup script
echo "🔄 Running cleanup script..."
if $PYTHON_CMD quick_cleanup.py; then
    echo "✅ Cleanup script completed successfully!"
else
    echo "❌ Error running cleanup script"
    exit 1
fi

# Next steps
echo ""
echo "📋 Next steps:"
echo "1. Check the logs above for any errors"
echo "2. Files marked as FAILED can be retried using the 'Retry Indexing' button in the UI"
echo "3. Consider restarting the Kafka consumer if many files were stuck"
echo "4. Monitor the system for a few minutes to ensure processing resumes normally"
echo ""
echo "🎯 Cleanup completed! Check the UI to verify file statuses." 