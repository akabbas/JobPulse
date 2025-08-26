#!/bin/bash

echo "🚀 Setting up JobPulse Local Development Environment..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the JobPulse root directory."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium
playwright install-deps

# Create required directories
echo "📁 Creating required directories..."
mkdir -p logs data output

# Check if Flask is installed
echo "🔍 Checking Flask installation..."
python -c "import flask; print('✅ Flask is installed')" || {
    echo "❌ Flask not found. Installing Flask..."
    pip install flask
}

# Check if Playwright is installed
echo "🔍 Checking Playwright installation..."
python -c "import playwright; print('✅ Playwright is installed')" || {
    echo "❌ Playwright not found. Installing Playwright..."
    pip install playwright
}

echo "✅ Local environment setup complete!"
echo ""
echo "🚀 To start the local development server:"
echo "   cd web_dashboard"
echo "   source ../venv/bin/activate"
echo "   python app.py"
echo ""
echo "🌐 Then open your browser to: http://localhost:5001"
echo ""
echo "🔧 For testing API endpoints:"
echo "   curl -X POST http://localhost:5001/search -H 'Content-Type: application/json' -d '{\"keyword\": \"python developer\", \"limit\": 5}'"
