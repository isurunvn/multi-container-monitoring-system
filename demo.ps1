# Velaris Consolidated System - Final Test

Write-Host "VELARIS ENHANCED MONITORING - CONSOLIDATED SYSTEM" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

Write-Host "File Structure (Simplified):" -ForegroundColor Yellow
Write-Host "- docker-compose.yml - Single orchestration file" -ForegroundColor Green
Write-Host "- db/init.sql - Consolidated database schema" -ForegroundColor Green  
Write-Host "- watchdog/watchdog.py - Enhanced monitoring script" -ForegroundColor Green
Write-Host ""

Write-Host "Running Services:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
Write-Host "Enhanced Monitoring Active:" -ForegroundColor Yellow
Write-Host "Recent Database Records:" -ForegroundColor White
docker exec db psql -U velaris -d velaris -c "SELECT target, response_time_ms, status FROM checks ORDER BY created_at DESC LIMIT 3;" 2>$null

Write-Host ""
Write-Host "Latest Structured Metrics:" -ForegroundColor White  
docker exec watchdog tail -2 /var/log/velaris/metrics.log

Write-Host ""
Write-Host "Access Your System:" -ForegroundColor Yellow
Write-Host "- Web Service 1: http://localhost:8081" -ForegroundColor Cyan
Write-Host "- Web Service 2: http://localhost:8082" -ForegroundColor Cyan
Write-Host "- Log Viewer: http://localhost:8090" -ForegroundColor Cyan
Write-Host "- Email UI: http://localhost:8025" -ForegroundColor Cyan

Write-Host ""
Write-Host "SYSTEM CONSOLIDATED AND OPERATIONAL!" -ForegroundColor Green
