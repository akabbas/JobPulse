#!/bin/bash

echo "🚀 Starting JobPulse Local Development Server..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the JobPulse root directory."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if Flask is installed
python -c "import flask" 2>/dev/null || {
    echo "❌ Flask not found. Please run setup_local.sh first."
    exit 1
}

# Change to web_dashboard directory
cd web_dashboard

echo "🌐 Starting Flask development server..."
echo "📱 Server will be available at: http://localhost:5001"
echo "🔧 Press Ctrl+C to stop the server"
echo ""

# Start Flask development server
python app.py
