FROM python:3.11-alpine

# Install system dependencies
RUN apk add --no-cache \
    nginx \
    docker-cli \
    postgresql-client \
    bash \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Copy Python dependencies and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY log_api.py /app/
COPY index.html /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/http.d/default.conf
COPY start.sh /start.sh

# Make startup script executable
RUN chmod +x /start.sh

# Create nginx directories
RUN mkdir -p /var/log/nginx /var/lib/nginx/tmp/client_body \
    && chown -R nginx:nginx /var/lib/nginx /var/log/nginx

EXPOSE 80 5000

CMD ["/start.sh"]
