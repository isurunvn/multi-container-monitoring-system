# Velaris Demo System Status Monitor
# PowerShell script for Windows

Write-Host "=== Velaris Demo System Status ===" -ForegroundColor Green
Write-Host ""

Write-Host "Container Status:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"
Write-Host ""

Write-Host "Recent Health Checks (last 5):" -ForegroundColor Yellow
$dbQuery = @"
SELECT 
    container_id, 
    drift_seconds, 
    http_status, 
    CASE WHEN ok THEN 'PASS' ELSE 'FAIL' END as status,
    created_at 
FROM checks 
ORDER BY created_at DESC 
LIMIT 5;
"@

try {
    docker exec -e PGPASSWORD=velaris db psql -U velaris -d velaris -c $dbQuery
} catch {
    Write-Host "Database not accessible" -ForegroundColor Red
}

Write-Host ""
Write-Host "Email Alerts:" -ForegroundColor Yellow
Write-Host "Check MailHog UI at: http://localhost:8025"

Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Yellow
Write-Host "- Web1: http://localhost:8081"
Write-Host "- Web2: http://localhost:8082"
Write-Host "- MailHog: http://localhost:8025"
Write-Host ""

Write-Host "Recent Watchdog Logs:" -ForegroundColor Yellow
docker logs watchdog --tail 10
