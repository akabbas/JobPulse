#!/bin/bash

# Docker Installation Script for Job Market Analytics
# This script installs Docker and Docker Compose for containerized deployment

set -e

echo "🐳 Installing Docker and Docker Compose..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        echo "📦 Installing Docker on Ubuntu/Debian..."
        
        # Update package index
        sudo apt-get update
        
        # Install prerequisites
        sudo apt-get install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # Add Docker's official GPG key
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # Set up the stable repository
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker Engine
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        
        # Add user to docker group
        sudo usermod -aG docker $USER
        
        # Start and enable Docker
        sudo systemctl start docker
        sudo systemctl enable docker
        
    elif command -v yum &> /dev/null; then
        echo "📦 Installing Docker on CentOS/RHEL..."
        
        # Install prerequisites
        sudo yum install -y yum-utils
        
        # Set up the repository
        sudo yum-config-manager \
            --add-repo \
            https://download.docker.com/linux/centos/docker-ce.repo
        
        # Install Docker Engine
        sudo yum install -y docker-ce docker-ce-cli containerd.io
        
        # Start and enable Docker
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Add user to docker group
        sudo usermod -aG docker $USER
        
    else
        echo "❌ Unsupported Linux distribution. Please install Docker manually."
        exit 1
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "🍎 Installing Docker on macOS..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "📦 Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install Docker Desktop
    brew install --cask docker
    
    echo "✅ Docker Desktop installed. Please start Docker Desktop from Applications."
    echo "   After starting Docker Desktop, run this script again to install Docker Compose."
    
else
    echo "❌ Unsupported operating system: $OSTYPE"
    echo "Please install Docker manually from https://docs.docker.com/get-docker/"
    exit 1
fi

# Install Docker Compose
echo "📦 Installing Docker Compose..."

# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
echo "🔍 Verifying installation..."
docker --version
docker-compose --version

echo ""
echo "✅ Docker and Docker Compose installed successfully!"
echo ""
echo "🔧 Next steps:"
echo "   1. If you're on Linux, log out and log back in for group changes to take effect"
echo "   2. If you're on macOS, start Docker Desktop from Applications"
echo "   3. Run the deployment script: ./deploy.sh"
echo ""
echo "📝 Note: You may need to restart your terminal for the docker group to take effect." 