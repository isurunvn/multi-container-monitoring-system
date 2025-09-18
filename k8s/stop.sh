#!/bin/bash

# Multi-Container Monitoring System - Kubernetes Stop Script
# This script stops and cleans up the Kubernetes deployment

set -e

echo "🛑 Stopping Multi-Container Monitoring System (Kubernetes)..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if we're connected to a Kubernetes cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Not connected to a Kubernetes cluster. Please check your connection."
    exit 1
fi

# Step 1: Show current status before stopping
echo "📊 Current deployment status:"
kubectl get pods 2>/dev/null || echo "No pods found"
echo ""

# Step 2: Delete all deployments
echo "🗑️ Removing deployments..."
kubectl delete deployment --ignore-not-found=true \
    db \
    web1 \
    web2 \
    watchdog \
    logviewer \
    mailhog

# Step 3: Delete all services (except kubernetes system service)
echo "🗑️ Removing services..."
kubectl delete service --ignore-not-found=true \
    db-service \
    web1-service \
    web2-service \
    logviewer-service \
    mailhog-service

# Step 4: Delete ConfigMaps and Secrets
echo "🗑️ Removing ConfigMaps and Secrets..."
kubectl delete configmap --ignore-not-found=true \
    monitoring-config \
    db-init

kubectl delete secret --ignore-not-found=true \
    monitoring-secret

# Step 5: Delete PersistentVolumeClaims (optional - ask user)
echo ""
echo "🤔 Do you want to delete persistent volumes (this will remove all stored data)?"
echo "   - Database data will be lost"
echo "   - Log files will be lost"
echo "   - Web content will be lost"
echo ""
read -p "Delete persistent volumes? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removing PersistentVolumeClaims..."
    kubectl delete pvc --ignore-not-found=true \
        db-pvc \
        monitoring-logs-pvc \
        web1-content-pvc \
        web2-content-pvc
    
    echo "⚠️  All persistent data has been deleted!"
else
    echo "ℹ️  Keeping persistent volumes. Data will be preserved for next deployment."
fi

# Step 6: Clean up any remaining pods (force if needed)
echo "🧹 Cleaning up any remaining pods..."
kubectl delete pods --all --grace-period=0 --force 2>/dev/null || true

# Step 7: Wait for cleanup to complete
echo "⏳ Waiting for cleanup to complete..."
sleep 5

# Step 8: Show final status
echo "📊 Final status:"
kubectl get all 2>/dev/null | grep -v "service/kubernetes" || echo "All resources cleaned up!"

# Step 9: Clean up generated configuration files
echo "🗑️ Cleaning up generated configuration files..."
if [ -f "monitoring-configmap-generated.yaml" ]; then
    rm monitoring-configmap-generated.yaml
    echo "   ✅ Removed monitoring-configmap-generated.yaml"
fi

if [ -f "monitoring-secret-generated.yaml" ]; then
    rm monitoring-secret-generated.yaml
    echo "   ✅ Removed monitoring-secret-generated.yaml"
fi

echo ""
echo "✅ Kubernetes deployment stopped and cleaned up successfully!"

echo ""
echo "🔍 Useful commands to verify cleanup:"
echo "  - Check remaining pods: kubectl get pods"
echo "  - Check remaining services: kubectl get services"
echo "  - Check remaining PVCs: kubectl get pvc"
echo "  - Check cluster status: kubectl cluster-info"

echo ""
echo "🔄 To redeploy the system:"
echo "  - Run: ./deploy.sh"
echo "  - Or apply manually: kubectl apply -f ."

echo ""
echo "🚪 To stop minikube (if using):"
echo "  - Pause: minikube pause"
echo "  - Stop: minikube stop"
echo "  - Delete: minikube delete"

echo ""
echo "🎉 Kubernetes cleanup completed!"
