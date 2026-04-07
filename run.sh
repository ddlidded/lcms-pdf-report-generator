#!/bin/bash
# LCMS PDF Report Generator Launcher Script

echo "Starting LCMS PDF Report Generator..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if dependencies are installed
python3 -c "import PyQt5" 2>/dev/null || {
    echo "Installing dependencies..."
    pip install -r requirements.txt
}

# Run the application
python3 main.py