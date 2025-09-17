#!/bin/bash

# Multi-Container Monitoring System - Docker Compose Stop Script
# This script stops and cleans up the Docker Compose deployment

set -e

echo "🛑 Stopping Multi-Container Monitoring System (Docker Compose)..."

# Step 1: Stop and remove containers
echo "📦 Stopping all services..."
docker compose down

# Step 2: Show what was stopped
echo "✅ All services stopped successfully!"

# Step 3: Ask about additional cleanup
echo ""
echo "� Additional cleanup options:"
echo ""

# Ask about volumes
read -p "Remove volumes (this will delete all data)? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removing volumes..."
    docker compose down -v
    docker volume prune -f
    echo "⚠️  All persistent data has been deleted!"
else
    echo "ℹ️  Keeping volumes. Data will be preserved."
fi

echo ""

# Ask about removing project images
read -p "Remove project Docker images (watchdog, logviewer)? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removing project images..."
    
    # Remove images built by this project
    docker rmi watchdog:latest 2>/dev/null || echo "   watchdog:latest not found"
    docker rmi logviewer:latest 2>/dev/null || echo "   logviewer:latest not found"
    
    # Remove any dangling images from builds
    docker image prune -f
    
    echo "✅ Project images removed!"
else
    echo "ℹ️  Keeping project images for faster next startup."
fi

echo ""

# Ask about removing all unused containers and images
read -p "Clean up all unused Docker resources (containers, networks, images)? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Performing system cleanup..."
    
    # Remove all stopped containers
    docker container prune -f
    
    # Remove all unused networks
    docker network prune -f
    
    # Remove all unused images (not just dangling ones)
    docker image prune -a -f
    
    # Remove build cache
    docker builder prune -f
    
    echo "✅ System cleanup completed!"
    echo "⚠️  This may have removed other unused Docker resources not related to this project."
else
    echo "ℹ️  Skipping system cleanup."
fi

# Step 4: Show final Docker status
echo ""
echo "📊 Final Docker status:"
echo "Containers:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -10
echo ""
echo "Images:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | head -10

echo ""
echo "🔍 Useful commands:"
echo "  - Check containers: docker ps -a"
echo "  - Check images: docker images"
echo "  - Check volumes: docker volume ls"
echo "  - Check disk usage: docker system df"

echo ""
echo "🔄 To restart the system:"
echo "  - Quick restart: ./docker-deploy.sh"
echo "  - Or manual: docker compose up -d"

echo ""
echo "🎉 Docker Compose cleanup completed!"
