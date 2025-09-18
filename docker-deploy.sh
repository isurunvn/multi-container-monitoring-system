#!/bin/bash

# Multi-Container Monitoring System - Docker Compose Deployment Script
# This script deploys the monitoring system using Docker Compose

set -e

echo "🚀 Deploying Multi-Container Monitoring System with Docker Compose..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available (v2 uses 'docker compose')
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Step 1: Stop any existing containers
echo "🧹 Cleaning up any existing containers..."
docker compose down --remove-orphans

# Step 2: Build images from scratch
echo "🔨 Building Docker images from scratch..."
echo "   Building watchdog service..."
docker compose build watchdog
#docker compose build --no-cache watchdog

echo "   Building log-viewer service..."
docker compose build log-viewer
#docker compose build --no-cache log-viewer

# Step 3: Start all services
echo "📦 Starting all services..."
docker compose up -d

# Step 4: Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Step 5: Check service status
echo "📊 Checking service status..."
docker compose ps

# Step 6: Wait for database to be fully ready
echo "⏳ Waiting for database to be fully initialized..."
timeout=60
counter=0
while ! docker compose exec -T db pg_isready -U ${POSTGRES_USER:-monitoruser} > /dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        echo "❌ Database failed to start within $timeout seconds"
        exit 1
    fi
    echo "   Database not ready yet... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

echo "✅ Database is ready!"

# Step 7: Verify database initialization
echo "🔍 Verifying database tables..."
timeout=30
counter=0
while ! docker compose exec -T db psql -U ${POSTGRES_USER:-monitoruser} -d ${POSTGRES_DB:-monitoring} -c "SELECT 1 FROM checks LIMIT 1;" > /dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        echo "❌ Database tables not created within $timeout seconds"
        echo "   Checking database logs..."
        docker compose logs db | tail -10
        break
    fi
    echo "   Database tables not ready yet... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

if docker compose exec -T db psql -U ${POSTGRES_USER:-monitoruser} -d ${POSTGRES_DB:-monitoring} -c "SELECT 1 FROM checks LIMIT 1;" > /dev/null 2>&1; then
    echo "✅ Database tables are ready!"
else
    echo "⚠️  Database tables may not be properly initialized"
fi

# Step 8: Test web services
echo "🌐 Testing web services..."
timeout=30
counter=0
while ! curl -s http://localhost:8081 > /dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "❌ Web1 service failed to start within $timeout seconds"
        break
    fi
    echo "   Web1 not ready yet... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

timeout=30
counter=0
while ! curl -s http://localhost:8082 > /dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "❌ Web2 service failed to start within $timeout seconds"
        break
    fi
    echo "   Web2 not ready yet... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

echo "✅ Deployment complete!"

# Step 9: Show final status and access information
echo ""
echo "📊 Final service status:"
docker compose ps

echo ""
echo "🌐 Access URLs:"
echo "  - Web1: http://localhost:8081"
echo "  - Web2: http://localhost:8082"
echo "  - Log Viewer: http://localhost:8090"
echo "  - MailHog UI: http://localhost:8025"
echo "  - Database: localhost:5432"

echo ""
echo "🔍 Useful commands:"
echo "  - View all logs: docker compose logs -f"
echo "  - View specific service logs: docker compose logs -f watchdog"
echo "  - Stop all services: docker compose down"
echo "  - Restart a service: docker compose restart <service-name>"
echo "  - Check service status: docker compose ps"

echo ""
echo "📝 Quick test:"
echo "  - Open http://localhost:8081 and http://localhost:8082 to see web services"
echo "  - Open http://localhost:8090 to see monitoring dashboard"
echo "  - Open http://localhost:8025 to see email interface"
echo "  - Check logs: docker compose logs -f watchdog"

echo ""
echo "🎉 Your monitoring system is now running with Docker Compose!"
