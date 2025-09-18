#!/bin/bash

echo "🚀 Setting up Kubernetes Ingress for Multi-Container Monitoring System"
echo "=================================================================="

# Enable NGINX Ingress controller on Minikube
echo "📦 Enabling NGINX Ingress controller on Minikube..."
minikube addons enable ingress

# Wait for ingress controller to be ready
echo "⏳ Waiting for NGINX Ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Apply all service updates (ClusterIP instead of NodePort)
echo "🔧 Updating services to use ClusterIP..."
kubectl apply -f web1-service.yaml
kubectl apply -f web2-service.yaml
kubectl apply -f logviewer-service.yaml
kubectl apply -f mailhog-service.yaml
kubectl apply -f db-service.yaml

# Apply the ingress resource
echo "🌐 Applying Ingress configuration..."
kubectl apply -f ingress.yaml

# Wait for ingress to be ready
echo "⏳ Waiting for Ingress to be ready..."
sleep 10

# Get the ingress IP
echo "📋 Getting Ingress information..."
kubectl get ingress monitoring-ingress -n monitoring

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)
echo ""
echo "🎉 Ingress setup complete!"
echo "=================================================================="
echo "🌍 Access your services at:"
echo "   Base URL: http://$MINIKUBE_IP"
echo ""
echo "📱 Service URLs:"
echo "   • Web1:        http://$MINIKUBE_IP/web1"
echo "   • Web2:        http://$MINIKUBE_IP/web2" 
echo "   • Log Monitor: http://$MINIKUBE_IP/log-monitor"
echo "   • MailHog:     http://$MINIKUBE_IP/mailhog"
echo ""
echo "🔍 Verify ingress status:"
echo "   kubectl get ingress -n monitoring"
echo "   kubectl describe ingress monitoring-ingress -n monitoring"
