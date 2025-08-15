#!/bin/bash

echo "🚀 Deploying MyApp..."

# Build production images
echo "🔨 Building production images..."
docker-compose -f docker-compose.yml build

# Run database migrations
echo "📊 Running database migrations..."
docker-compose -f docker-compose.yml run --rm backend alembic upgrade head

# Start services
echo "🏃 Starting services..."
docker-compose -f docker-compose.yml up -d

echo "✅ Deployment complete!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
