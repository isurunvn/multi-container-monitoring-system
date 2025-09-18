#!/bin/bash

# Generate Kubernetes ConfigMaps and Secrets from .env file
# This script reads the .env file and creates appropriate Kubernetes resources

set -e

ENV_FILE="../.env"
NAMESPACE="default"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found at $ENV_FILE"
    exit 1
fi

echo "🔧 Generating Kubernetes resources from .env file..."

# Function to create ConfigMap from .env (non-sensitive data)
create_configmap() {
    cat > monitoring-configmap-generated.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: monitoring-config
  namespace: monitoring
data:
EOF

    # Read .env file and extract non-sensitive variables
    while IFS='=' read -r key value || [ -n "$key" ]; do
        # Skip comments and empty lines
        if [[ $key =~ ^[[:space:]]*# ]] || [[ -z "$key" ]]; then
            continue
        fi
        
        # Remove any trailing comments and whitespace/newlines
        key=$(echo "$key" | sed 's/[[:space:]]*#.*//' | tr -d '\r\n' | xargs)
        value=$(echo "$value" | sed 's/[[:space:]]*#.*//' | tr -d '\r\n' | xargs)
        
        # Skip if empty after processing
        if [[ -z "$key" || -z "$value" ]]; then
            continue
        fi
        
        # Skip sensitive data (passwords, tokens, etc.)
        if [[ $key == *"PASSWORD"* ]] || [[ $key == *"TOKEN"* ]] || [[ $key == *"SECRET"* ]]; then
            continue
        fi
        
        # Adapt values for Kubernetes service names
        case $key in
            "WEB_TARGETS")
                value="web1-service:80,web2-service:80"
                ;;
            "DB_HOST")
                value="db-service"
                ;;
            "SMTP_HOST")
                if [[ $value == "mailhog" ]]; then
                    value="mailhog-service"
                fi
                ;;
        esac
        
        echo "  $key: \"$value\"" >> monitoring-configmap-generated.yaml
    done < "$ENV_FILE"
    
    echo "✅ Created monitoring-configmap-generated.yaml"
}

# Function to create Secret from .env (sensitive data)
create_secret() {
    cat > monitoring-secret-generated.yaml << 'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: monitoring-secret
  namespace: monitoring
type: Opaque
stringData:
EOF

    # Read .env file and extract sensitive variables
    while IFS='=' read -r key value || [ -n "$key" ]; do
        # Skip comments and empty lines
        if [[ $key =~ ^[[:space:]]*# ]] || [[ -z "$key" ]]; then
            continue
        fi
        
        # Remove any trailing comments and whitespace/newlines
        key=$(echo "$key" | sed 's/[[:space:]]*#.*//' | tr -d '\r\n' | xargs)
        value=$(echo "$value" | sed 's/[[:space:]]*#.*//' | tr -d '\r\n' | xargs)
        
        # Skip if empty after processing
        if [[ -z "$key" || -z "$value" ]]; then
            continue
        fi
        
        # Only include sensitive data
        if [[ $key == *"PASSWORD"* ]] || [[ $key == *"TOKEN"* ]] || [[ $key == *"SECRET"* ]]; then
            echo "  $key: \"$value\"" >> monitoring-secret-generated.yaml
        fi
    done < "$ENV_FILE"
    
    echo "✅ Created monitoring-secret-generated.yaml"
}

# Generate the resources
create_configmap
create_secret

echo ""
echo "📝 Generated files:"
echo "  - monitoring-configmap-generated.yaml (non-sensitive config)"
echo "  - monitoring-secret-generated.yaml (sensitive data)"
echo ""
echo "🚀 To apply:"
echo "  kubectl apply -f monitoring-secret-generated.yaml"
echo "  kubectl apply -f monitoring-configmap-generated.yaml"
echo ""
echo "💡 Then update your deployments to use envFrom instead of hardcoded values"
