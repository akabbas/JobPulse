#!/bin/bash

echo "🚀 Starting JobPulse Local Development Server..."
echo "📍 Port: 5002 (Local Development)"
echo "🔍 Port 5001: Docker (Full Features)"
echo ""

# Kill any existing Flask processes on port 5002
echo "🧹 Cleaning up any existing processes on port 5002..."
pkill -f "python.*app_local.py" 2>/dev/null || true

# Navigate to web_dashboard directory
cd web_dashboard

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../venv/bin/activate

# Start the local development server
echo "🚀 Starting server on http://localhost:5002..."
echo "📝 Note: This is a mock server for fast local development"
echo "🔍 Real scraping features are available on Docker (port 5001)"
echo "=" * 60

python app_local.py





