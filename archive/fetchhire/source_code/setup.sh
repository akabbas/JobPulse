#!/bin/bash
# 🚀 FetchHire Setup Script
# This script sets up the FetchHire environment

echo "🚀 Setting up FetchHire with 403 Error Bypass"
echo "=================================================="

# Check if Python 3.13+ is installed
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.13"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected"
else
    echo "❌ Python 3.13+ is required. Current version: $python_version"
    echo "Please install Python 3.13+ and try again."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install

# Create necessary directories
echo "📁 Creating project structure..."
mkdir -p tests templates database docs

# Test the installation
echo "🧪 Testing installation..."
python3 tests/test_quick_playwright.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Test the scraper: python3 tests/test_quick_playwright.py"
echo "3. Start the Flask app: python3 app.py"
echo "4. Open in browser: http://localhost:5000"
echo ""
echo "📚 Documentation: README.md"
echo "🐛 Issues: Create an issue on GitHub"
echo ""
echo "⭐ Star this repository if you found it helpful!" 