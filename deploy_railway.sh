#!/bin/bash

# Railway Deployment Script for JobPulse
# This script helps deploy the enhanced JobPulse application to Railway

set -e

echo "🚀 Deploying JobPulse to Railway..."
echo "=================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    
    # Install Railway CLI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        curl -fsSL https://railway.app/install.sh | sh
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://railway.app/install.sh | sh
    else
        echo "❌ Unsupported OS. Please install Railway CLI manually:"
        echo "   https://railway.app/docs/develop/cli"
        exit 1
    fi
fi

echo "✅ Railway CLI installed/verified"

# Check if we're in a Railway project
if [ ! -f "railway.json" ]; then
    echo "🔧 Initializing Railway project..."
    railway init
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to initialize Railway project"
        echo "Please run 'railway login' first and try again"
        exit 1
    fi
fi

echo "✅ Railway project initialized"

# Install Playwright browsers for production
echo "🌐 Installing Playwright browsers..."
cd web_dashboard
playwright install --with-deps chromium
cd ..

echo "✅ Playwright browsers installed"

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment completed!"
echo ""
echo "🎉 Your JobPulse application is now live on Railway!"
echo ""
echo "📋 Next steps:"
echo "1. Set up your environment variables in Railway dashboard"
echo "2. Configure your database (Railway provides PostgreSQL)"
echo "3. Set SECRET_KEY to a secure random string"
echo "4. Test your application"
echo ""
echo "🔗 Useful commands:"
echo "  railway status          - Check deployment status"
echo "  railway logs            - View application logs"
echo "  railway open            - Open your app in browser"
echo "  railway variables       - Manage environment variables"
echo "  railway domain          - Get your app's URL"
