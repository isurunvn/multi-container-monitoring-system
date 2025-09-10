#!/bin/bash
echo "Starting Multi-Container Monitoring Log Viewer..."

# Create necessary directories
mkdir -p /var/log/nginx
mkdir -p /var/lib/nginx/tmp/client_body
chown -R nginx:nginx /var/lib/nginx /var/log/nginx

# Start Flask API server in background
cd /app
echo "Starting Python Flask API on port 5000..."
python log_api.py &

# Wait a moment for Flask to start
sleep 2

# Start nginx in foreground
echo "Starting NGINX..."
nginx -g "daemon off;"
