#!/usr/bin/env powershell
# Velaris Error Testing Script
# This script provides various ways to trigger errors and test the monitoring system

Write-Host "🔥 VELARIS ERROR TESTING TOOLKIT 🔥" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Yellow

function Show-Menu {
    Write-Host ""
    Write-Host "Select a test scenario:" -ForegroundColor Cyan
    Write-Host "1. 🚫 Stop Web1 Container (HTTP Error)" -ForegroundColor White
    Write-Host "2. 🚫 Stop Web2 Container (HTTP Error)" -ForegroundColor White  
    Write-Host "3. 🗃️  Stop Database (Connection Error)" -ForegroundColor White
    Write-Host "4. 🐕 Stop Watchdog (System Failure)" -ForegroundColor White
    Write-Host "5. ⏰ Simulate Time Drift Error" -ForegroundColor White
    Write-Host "6. 🌐 Break Network (Invalid Content)" -ForegroundColor White
    Write-Host "7. 📧 Test Email System Directly" -ForegroundColor White
    Write-Host "8. 📊 View Current System Status" -ForegroundColor White
    Write-Host "9. 🔄 Restore All Services" -ForegroundColor White
    Write-Host "0. ❌ Exit" -ForegroundColor White
    Write-Host ""
}

function Test-WebContainer {
    param([string]$ContainerName)
    
    Write-Host "🚫 Stopping $ContainerName container..." -ForegroundColor Red
    docker stop $ContainerName
    
    Write-Host "⏳ Waiting for watchdog to detect failure..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    Write-Host "📋 Recent watchdog logs:" -ForegroundColor Cyan
    docker logs watchdog --tail 10
    
    Write-Host ""
    Write-Host "📧 Check your email at: http://localhost:8025" -ForegroundColor Green
    Write-Host "🔍 View logs at: http://localhost:8090" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "To restore: docker start $ContainerName" -ForegroundColor Magenta
}

function Test-Database {
    Write-Host "🗃️ Stopping database container..." -ForegroundColor Red
    docker stop db
    
    Write-Host "⏳ Waiting for watchdog to detect database failure..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    Write-Host "📋 Recent watchdog logs:" -ForegroundColor Cyan
    docker logs watchdog --tail 10
    
    Write-Host ""
    Write-Host "⚠️ WARNING: This will cause multiple cascading failures!" -ForegroundColor Red
    Write-Host "📧 Check your email at: http://localhost:8025" -ForegroundColor Green
    Write-Host "🔍 View logs at: http://localhost:8090" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "To restore: docker start db" -ForegroundColor Magenta
}

function Test-TimeDrift {
    Write-Host "⏰ Simulating time drift by changing container time..." -ForegroundColor Red
    
    # Method 1: Change container time
    Write-Host "Changing watchdog container time..." -ForegroundColor Yellow
    docker exec watchdog date -s "2025-01-01 10:00:00" 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Time changed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Time change failed. Trying alternative method..." -ForegroundColor Yellow
        
        # Method 2: Restart with different drift tolerance
        Write-Host "Restarting watchdog with strict time drift (1 second tolerance)..." -ForegroundColor Yellow
        $env:MAX_ALLOWED_DRIFT_SEC = "1"
        docker-compose restart watchdog
    }
    
    Write-Host "⏳ Waiting for time drift detection..." -ForegroundColor Yellow
    Start-Sleep -Seconds 70  # Wait for next monitoring cycle
    
    Write-Host "📋 Recent watchdog logs:" -ForegroundColor Cyan
    docker logs watchdog --tail 15
    
    Write-Host ""
    Write-Host "📧 Check your email at: http://localhost:8025" -ForegroundColor Green
    Write-Host "🔍 View logs at: http://localhost:8090" -ForegroundColor Green
}

function Test-NetworkContent {
    Write-Host "🌐 Breaking web content to simulate content validation failure..." -ForegroundColor Red
    
    # Change expected text in web containers
    Write-Host "Modifying web1 content..." -ForegroundColor Yellow
    docker exec web1 sh -c 'echo "<h1>BROKEN CONTENT</h1>" > /usr/share/nginx/html/index.html'
    
    Write-Host "⏳ Waiting for content validation failure..." -ForegroundColor Yellow
    Start-Sleep -Seconds 70  # Wait for next monitoring cycle
    
    Write-Host "📋 Recent watchdog logs:" -ForegroundColor Cyan
    docker logs watchdog --tail 10
    
    Write-Host ""
    Write-Host "📧 Check your email at: http://localhost:8025" -ForegroundColor Green
    Write-Host "🔍 View logs at: http://localhost:8090" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "To restore: docker-compose restart web1" -ForegroundColor Magenta
}

function Test-EmailSystem {
    Write-Host "📧 Testing email system directly..." -ForegroundColor Cyan
    
    # Send test email via watchdog
    Write-Host "Triggering manual test alert..." -ForegroundColor Yellow
    
    $testScript = @"
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

msg = MIMEText('''
🔥 MANUAL TEST ALERT 🔥

This is a test email triggered manually to verify the email system is working.

Timestamp: $((Get-Date).ToString())
Test Type: Manual breakpoint test
System: Velaris Monitoring

If you received this email, the alerting system is functioning correctly!
''')

msg['Subject'] = '[Velaris TEST] Manual Test Alert'
msg['From'] = 'alerts@velaris.local'
msg['To'] = 'support@velaris.local'

try:
    with smtplib.SMTP('mailhog', 1025, timeout=10) as s:
        s.sendmail('alerts@velaris.local', ['support@velaris.local'], msg.as_string())
    print('✅ Test email sent successfully!')
except Exception as e:
    print(f'❌ Email failed: {e}')
"@

    # Write test script and execute it in watchdog container
    $testScript | docker exec -i watchdog python
    
    Write-Host ""
    Write-Host "📧 Check your email at: http://localhost:8025" -ForegroundColor Green
}

function Show-SystemStatus {
    Write-Host "📊 CURRENT SYSTEM STATUS" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Yellow
    
    Write-Host "🐳 Container Status:" -ForegroundColor White
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    Write-Host ""
    Write-Host "📈 Recent Database Metrics:" -ForegroundColor White
    docker exec -e PGPASSWORD=velaris db psql -U velaris -d velaris -c "
        SELECT 
            target, 
            status, 
            response_time_ms,
            time_drift_seconds,
            created_at 
        FROM checks 
        ORDER BY created_at DESC 
        LIMIT 5;" 2>$null
    
    Write-Host ""
    Write-Host "📋 Recent Watchdog Activity:" -ForegroundColor White
    docker logs watchdog --tail 5
    
    Write-Host ""
    Write-Host "🌐 Service URLs:" -ForegroundColor Green
    Write-Host "  Web1: http://localhost:8081" -ForegroundColor Cyan
    Write-Host "  Web2: http://localhost:8082" -ForegroundColor Cyan
    Write-Host "  Email: http://localhost:8025" -ForegroundColor Cyan
    Write-Host "  Logs: http://localhost:8090" -ForegroundColor Cyan
}

function Restore-AllServices {
    Write-Host "🔄 Restoring all services..." -ForegroundColor Green
    
    Write-Host "Starting all containers..." -ForegroundColor Yellow
    docker-compose up -d
    
    Write-Host "Resetting environment variables..." -ForegroundColor Yellow
    Remove-Item Env:MAX_ALLOWED_DRIFT_SEC -ErrorAction SilentlyContinue
    
    Write-Host "Waiting for services to stabilize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    Write-Host "✅ All services restored!" -ForegroundColor Green
    Show-SystemStatus
}

# Main execution loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice (0-9)"
    
    switch ($choice) {
        "1" { Test-WebContainer "web1" }
        "2" { Test-WebContainer "web2" }
        "3" { Test-Database }
        "4" { 
            Write-Host "🚫 Stopping watchdog..." -ForegroundColor Red
            docker stop watchdog
            Write-Host "⚠️ Monitoring system is now down!" -ForegroundColor Red
            Write-Host "To restore: docker start watchdog" -ForegroundColor Magenta
        }
        "5" { Test-TimeDrift }
        "6" { Test-NetworkContent }
        "7" { Test-EmailSystem }
        "8" { Show-SystemStatus }
        "9" { Restore-AllServices }
        "0" { 
            Write-Host "👋 Goodbye!" -ForegroundColor Green
            break 
        }
        default { 
            Write-Host "❌ Invalid choice. Please try again." -ForegroundColor Red 
        }
    }
    
    if ($choice -ne "0") {
        Write-Host ""
        Read-Host "Press Enter to continue..."
    }
    
} while ($choice -ne "0")

Write-Host ""
Write-Host "🔧 Remember to restore services when done testing!" -ForegroundColor Yellow
Write-Host "Run: docker-compose up -d" -ForegroundColor Cyan
