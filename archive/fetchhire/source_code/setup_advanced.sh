#!/bin/bash
# FetchHire Advanced Setup Script
# This script sets up the complete environment for FetchHire

echo "🚀 Setting up FetchHire..."
echo "======================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Install advanced dependencies
echo ""
echo "📦 Installing advanced dependencies..."
pip3 install -r requirements_advanced.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check for Chrome/Chromium
echo ""
echo "🔍 Checking for Chrome/Chromium..."

if command -v google-chrome &> /dev/null; then
    echo "✅ Google Chrome found"
elif command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium found"
elif command -v chromium &> /dev/null; then
    echo "✅ Chromium found"
else
    echo "⚠️  Chrome/Chromium not found"
    echo "💡 Please install Chrome or Chromium:"
    echo "   macOS: brew install --cask google-chrome"
    echo "   Ubuntu: sudo apt install chromium-browser"
    echo "   Windows: Download from https://www.google.com/chrome/"
fi

# Create cache directory
echo ""
echo "📁 Creating cache directory..."
mkdir -p cache
echo "✅ Cache directory created"

# Check if proxies.txt exists
if [ -f "proxies.txt" ]; then
    echo "✅ Proxy configuration file found"
    echo "💡 Edit proxies.txt to add your proxy servers"
else
    echo "⚠️  proxies.txt not found, creating template..."
    cat > proxies.txt << 'EOF'
# Proxy Configuration File
# Add your proxy servers here, one per line
# Format: http://username:password@proxy_host:port
# Example:
# http://user:pass@proxy1.example.com:8080
# http://user:pass@proxy2.example.com:8080
# https://user:pass@proxy3.example.com:3128

# Free proxy examples (replace with your own paid proxies for better reliability)
# http://proxy1.example.com:8080
# http://proxy2.example.com:8080
# http://proxy3.example.com:3128

# Note: Free proxies are often unreliable and may be blocked by job sites
# For production use, consider using paid proxy services like:
# - Bright Data (formerly Luminati)
# - SmartProxy
# - Oxylabs
# - ProxyMesh
# - Rotating proxies from cloud providers
EOF
    echo "✅ Created proxies.txt template"
fi

# Test Selenium setup
echo ""
echo "🤖 Testing Selenium setup..."
python3 -c "
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys

try:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.quit()
    print('✅ Selenium WebDriver working correctly')
except Exception as e:
    print(f'❌ Selenium setup failed: {e}')
    print('💡 Try installing ChromeDriver manually')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Selenium test passed"
else
    echo "❌ Selenium test failed"
    echo "💡 Try: pip3 install webdriver-manager"
fi

# Run basic test
echo ""
echo "🧪 Running basic test..."
python3 test_advanced_scraper.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Advanced scraper setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Edit proxies.txt to add your proxy servers"
    echo "   2. Configure cache duration in advanced_scraper.py"
    echo "   3. Test with: python3 test_advanced_scraper.py"
    echo "   4. Run web app: python3 app.py"
    echo ""
    echo "📚 Documentation: README_ADVANCED.md"
    echo "🔧 Configuration: proxies.txt, cache/ directory"
    echo "🧪 Testing: test_advanced_scraper.py"
else
    echo ""
    echo "⚠️  Setup completed with warnings"
    echo "💡 Check the output above for issues"
fi

echo ""
echo "�� Happy scraping!" 