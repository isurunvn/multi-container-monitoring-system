#!/bin/bash

# Multi-Container Monitoring System - Kubernetes Deployment Script
# This script deploys the monitoring system to Kubernetes

set -e

echo "🚀 Deploying Multi-Container Monitoring System to Kubernetes..."

# Step 1: Build Docker images locally (for local Kubernetes like minikube)
echo "📦 Building Docker images..."
cd ..
docker build -t watchdog:latest ./watchdog/
docker build -t logviewer:latest ./logging/

# Step 2: Generate config from .env file
echo "🔧 Generating configuration from .env file..."
cd k8s
./generate-k8s-config.sh

# Step 3: Deploy resources in correct order
echo "🔧 Deploying Kubernetes resources..."

# Deploy secrets and config first
kubectl apply -f monitoring-secret-generated.yaml
kubectl apply -f monitoring-configmap-generated.yaml

# Create database init script ConfigMap
kubectl create configmap db-init --from-file=../db/init.sql --dry-run=client -o yaml | kubectl apply -f -

# Deploy storage
kubectl apply -f db-pvc.yaml
kubectl apply -f monitoring-logs-pvc.yaml
kubectl apply -f web-content-pvc.yaml

# Deploy database
kubectl apply -f db-deployment.yaml
kubectl apply -f db-service.yaml

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
kubectl wait --for=condition=Ready pod -l app=db --timeout=120s

# Deploy web services
kubectl apply -f web1-deployment.yaml
kubectl apply -f web1-service.yaml
kubectl apply -f web2-deployment.yaml
kubectl apply -f web2-service.yaml

# Deploy MailHog
kubectl apply -f mailhog-deployment.yaml
kubectl apply -f mailhog-service.yaml

# Deploy monitoring services
kubectl apply -f watchdog-deployment.yaml
kubectl apply -f logviewer-deployment.yaml
kubectl apply -f logviewer-service.yaml

echo "✅ Deployment complete!"

# Show status
echo "📊 Checking deployment status..."
kubectl get pods
kubectl get services

echo "🌐 Access URLs:"
echo "  - Log Viewer: http://localhost:30090"
echo "  - Web1: http://localhost:30081"
echo "  - Web2: http://localhost:30082"
echo "  - MailHog UI: http://localhost:30825"
echo "  - Database: localhost:30432"

echo "🔍 To monitor deployment:"
echo "  kubectl get pods -w"
echo "  kubectl logs -f deployment/watchdog"
echo "  kubectl logs -f deployment/logviewer"
