#!/bin/bash

# Quick Railway Deployment for JobPulse
# This script provides a simple way to deploy to Railway

echo "🚀 Quick Railway Deployment for JobPulse"
echo "========================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📥 Installing Railway CLI..."
    curl -fsSL https://railway.app/install.sh | sh
    echo "✅ Railway CLI installed"
else
    echo "✅ Railway CLI already installed"
fi

# Check if we're logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway..."
    railway login
else
    echo "✅ Already logged in to Railway"
fi

# Initialize project if needed
if [ ! -f "railway.json" ]; then
    echo "🔧 Initializing Railway project..."
    railway init
fi

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "🔗 Next steps:"
echo "1. Set SECRET_KEY in Railway dashboard"
echo "2. Test your application: railway open"
echo "3. Check logs: railway logs"
echo "4. Get your URL: railway domain"
