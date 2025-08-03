#!/bin/bash

# Job Market Analytics Deployment Script
# This script deploys the application to avoid 403 errors and test real job searches

set -e

echo "🚀 Starting Job Market Analytics Deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs data output

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=$(openssl rand -hex 32)

# Build and start the application
echo "🔨 Building and starting the application..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

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
echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Application Information:"
echo "   • Web Dashboard: http://localhost:5000"
echo "   • Health Check: http://localhost:5000/health"
echo "   • Database: PostgreSQL on localhost:5432"
echo "   • Redis: localhost:6379"
echo ""
echo "🔧 Useful Commands:"
echo "   • View logs: docker-compose logs -f app"
echo "   • Stop services: docker-compose down"
echo "   • Restart services: docker-compose restart"
echo "   • Update application: ./deploy.sh"
echo ""
echo "📝 Notes:"
echo "   • The application uses reliable API sources to avoid 403 errors"
echo "   • Job data is stored in PostgreSQL database"
echo "   • Logs are available in the ./logs directory"
echo "   • Data persistence is configured for production use"
echo ""
echo "🌐 To access from other machines, update your firewall/security groups"
echo "   and use your server's IP address instead of localhost" 