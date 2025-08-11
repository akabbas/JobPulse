#!/bin/bash

# JobPulse Setup Script
echo "🚀 Setting up JobPulse Project..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the JobPulse directory"
    echo "   cd ~/Documents/JobPulse"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "~/beautifulsoup_env" ]; then
    echo "❌ Error: Virtual environment not found at ~/beautifulsoup_env"
    echo "   Please create it first: python3 -m venv ~/beautifulsoup_env"
    exit 1
fi

echo "✅ Found project directory and virtual environment"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source ~/beautifulsoup_env/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p output data logs

# Test the setup
echo "🧪 Testing setup..."
python test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Run the application: python main.py"
    echo "   2. View results in the output/ directory"
    echo "   3. Check logs in the logs/ directory"
    echo ""
    echo "📖 For detailed instructions, see README.md"
else
    echo ""
    echo "❌ Setup failed. Please check the error messages above."
    echo "   Common solutions:"
    echo "   - Make sure you're in the correct directory"
    echo "   - Ensure virtual environment is activated"
    echo "   - Check internet connection for package installation"
fi 