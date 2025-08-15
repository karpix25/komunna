#!/bin/bash

echo "🚀 Setting up MyApp development environment..."

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

# Create environment files from examples
echo "📝 Creating environment files..."
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
cp backend/.env.example backend/.env
cp bot/.env.example bot/.env

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p database/backups
mkdir -p nginx/ssl
mkdir -p nginx/logs

# Set executable permissions
chmod +x scripts/*.sh

echo "✅ Setup complete!"
echo "📝 Please edit the following files with your configuration:"
echo "   - .env"
echo "   - frontend/.env.local"
echo "   - backend/.env"
echo "   - bot/.env"
echo ""
echo "🚀 To start development:"
echo "   make dev"
