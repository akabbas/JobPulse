#!/bin/bash

# 🚀 JobPulse Working Version Deployment Script
# Version: 20250824_232928
# Status: ✅ FULLY FUNCTIONAL & PRODUCTION READY

echo "🚀 Deploying JobPulse Working Version 20250824_232928"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if Flask app exists
if [ ! -f "web_dashboard/app.py" ]; then
    echo "❌ Flask app not found. Please check the backup structure."
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "🚀 To start JobPulse:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Navigate to web_dashboard: cd web_dashboard"
echo "   3. Start Flask server: python app.py"
echo ""
echo "🌐 Access your application:"
echo "   - Main Dashboard: http://localhost:5002/"
echo "   - Skills Network: http://localhost:5002/skills-network"
echo "   - Health Check: http://localhost:5002/health"
echo ""
echo "🧪 Test the API:"
echo "   python test_skills_network_api.py"
echo ""
echo "📚 Documentation: SKILLS_NETWORK_README.md"
echo "📋 Version Summary: VERSION_SUMMARY.md"
echo ""
echo "✨ JobPulse is ready to impress recruiters!"

