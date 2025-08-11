#!/bin/bash
# 🚀 FetchHire Setup Script
# Complete setup for the FetchHire job scraping platform

set -e  # Exit on any error

echo "🚀 Setting up FetchHire - Advanced Job Scraper"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.13+ is installed
print_status "Checking Python version..."
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
    print_success "Python 3.13+ found"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ "$PYTHON_VERSION" == "3.13" ]] || [[ "$PYTHON_VERSION" > "3.13" ]]; then
        PYTHON_CMD="python3"
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.13+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3.13+ not found. Please install Python 3.13 or later."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "bin" ]; then
    print_status "Creating virtual environment..."
    $PYTHON_CMD -m venv .
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip
print_success "Pip upgraded"

# Install core dependencies
print_status "Installing core dependencies..."
pip install -r requirements.txt
print_success "Core dependencies installed"

# Install Playwright browsers
print_status "Installing Playwright browsers..."
playwright install chromium
print_success "Playwright browsers installed"

# Install development dependencies (optional)
read -p "Do you want to install development dependencies? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Installing development dependencies..."
    pip install -r requirements_advanced.txt
    print_success "Development dependencies installed"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p tests/results
print_success "Directories created"

# Copy environment file
if [ ! -f ".env" ]; then
    print_status "Setting up environment configuration..."
    cp env.example .env
    print_warning "Please edit .env file with your actual configuration values"
    print_success "Environment file created"
else
    print_success "Environment file already exists"
fi

# Test the installation
print_status "Testing the installation..."
$PYTHON_CMD -c "import flask, playwright, beautifulsoup4, requests; print('All imports successful!')"
print_success "Installation test passed"

# Run a quick test
print_status "Running quick test..."
$PYTHON_CMD tests/test_quick_playwright.py
print_success "Quick test completed"

echo ""
echo "🎉 FetchHire setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: python FetchHire.py"
echo "3. Open: http://localhost:5000"
echo ""
echo "For development:"
echo "- Run tests: python -m pytest"
echo "- Format code: black ."
echo "- Check code: flake8 ."
echo ""
echo "Happy scraping! 🚀"
