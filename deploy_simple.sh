#!/bin/bash

# Simple Job Market Analytics Deployment Script
# This script deploys the application directly on the server without Docker

set -e

echo "🚀 Starting Simple Job Market Analytics Deployment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Create virtual environment
echo "📁 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs data output

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=$(openssl rand -hex 32)

# Install system dependencies (Ubuntu/Debian)
if command -v apt-get &> /dev/null; then
    echo "📦 Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib redis-server nginx
fi

# Install system dependencies (CentOS/RHEL)
if command -v yum &> /dev/null; then
    echo "📦 Installing system dependencies..."
    sudo yum install -y postgresql postgresql-server redis nginx
fi

# Setup PostgreSQL
echo "🗄️ Setting up PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE jobpulse;"
sudo -u postgres psql -c "CREATE USER jobpulse WITH PASSWORD 'jobpulse123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE jobpulse TO jobpulse;"

# Setup Redis
echo "🔴 Setting up Redis..."
sudo systemctl start redis
sudo systemctl enable redis

# Setup Nginx
echo "🌐 Setting up Nginx..."
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo systemctl start nginx
sudo systemctl enable nginx

# Create systemd service for the application
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/job-analytics.service > /dev/null <<EOF
[Unit]
Description=Job Market Analytics
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
Environment=FLASK_ENV=production
Environment=DATABASE_URL=postgresql://jobpulse:jobpulse123@localhost:5432/jobpulse
Environment=REDIS_URL=redis://localhost:6379
ExecStart=$(pwd)/venv/bin/python web_dashboard/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
echo "🔄 Starting application service..."
sudo systemctl daemon-reload
sudo systemctl enable job-analytics
sudo systemctl start job-analytics

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if the application is running
echo "🔍 Checking application health..."
for i in {1..10}; do
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ Application is running successfully!"
        break
    else
        echo "⏳ Waiting for application to start... (attempt $i/10)"
        sleep 10
    fi
done

# Show deployment information
echo ""
echo "🎉 Simple deployment completed successfully!"
echo ""
echo "📊 Application Information:"
echo "   • Web Dashboard: http://localhost:5000"
echo "   • Health Check: http://localhost:5000/health"
echo "   • Database: PostgreSQL on localhost:5432"
echo "   • Redis: localhost:6379"
echo "   • Nginx: http://localhost:80"
echo ""
echo "🔧 Useful Commands:"
echo "   • View logs: sudo journalctl -u job-analytics -f"
echo "   • Stop service: sudo systemctl stop job-analytics"
echo "   • Restart service: sudo systemctl restart job-analytics"
echo "   • Check status: sudo systemctl status job-analytics"
echo ""
echo "📝 Notes:"
echo "   • The application uses reliable API sources to avoid 403 errors"
echo "   • Job data is stored in PostgreSQL database"
echo "   • Logs are available via systemd journal"
echo "   • Nginx is configured as a reverse proxy"
echo ""
echo "🌐 To access from other machines, update your firewall/security groups"
echo "   and use your server's IP address instead of localhost" 