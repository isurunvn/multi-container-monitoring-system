#!/bin/bash
# Simple monitoring script to check system status

echo "=== Velaris Demo System Status ==="
echo

echo "Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

echo "Recent Health Checks (last 5):"
docker exec -e PGPASSWORD=velaris db psql -U velaris -d velaris -c "
SELECT 
    container_id, 
    drift_seconds, 
    http_status, 
    CASE WHEN ok THEN 'PASS' ELSE 'FAIL' END as status,
    created_at 
FROM checks 
ORDER BY created_at DESC 
LIMIT 5;" 2>/dev/null || echo "Database not accessible"

echo
echo "Email Alerts:"
echo "Check MailHog UI at: http://localhost:8025"

echo
echo "Service URLs:"
echo "- Web1: http://localhost:8081"
echo "- Web2: http://localhost:8082"
echo "- MailHog: http://localhost:8025"
