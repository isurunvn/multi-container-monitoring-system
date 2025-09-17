#!/bin/bash

# Multi-Container Monitoring System - Kubernetes Quick Stop Script
# This script quickly stops Kubernetes deployment without interactive prompts

set -e

echo "🛑 Quick stop: Multi-Container Monitoring System (Kubernetes)..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed."
    exit 1
fi

# Delete everything quickly (keep PVCs by default)
echo "🗑️ Removing all resources (keeping persistent volumes)..."

kubectl delete deployment,service,configmap,secret --all --ignore-not-found=true 2>/dev/null || true

# Don't delete the kubernetes system service
kubectl delete service --ignore-not-found=true \
    db-service \
    web1-service \
    web2-service \
    logviewer-service \
    mailhog-service 2>/dev/null || true

# Clean up generated files
rm -f monitoring-configmap-generated.yaml monitoring-secret-generated.yaml

echo "✅ Quick cleanup completed!"
echo "ℹ️  Persistent volumes preserved. Run './stop.sh' for complete cleanup."
