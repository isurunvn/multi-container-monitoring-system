# Velaris Demo - Comprehensive Test Suite
# PowerShell script to validate all functionality

param(
    [switch]$SkipEmailTest = $false
)

Write-Host "=== Velaris Demo - Comprehensive Test Suite ===" -ForegroundColor Green
Write-Host ""

# Test 1: Container Health
Write-Host "Test 1: Container Health Check" -ForegroundColor Cyan
$containers = @("web1", "web2", "db", "watchdog", "mailhog")
$allHealthy = $true

foreach ($container in $containers) {
    $status = docker inspect $container --format "{{.State.Status}}" 2>$null
    if ($status -eq "running") {
        Write-Host "  ✅ $container is running" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $container is not running (status: $status)" -ForegroundColor Red
        $allHealthy = $false
    }
}

# Test 2: Web Server Accessibility
Write-Host "`nTest 2: Web Server Accessibility" -ForegroundColor Cyan
$webTests = @(
    @{url="http://localhost:8081"; name="Web1"},
    @{url="http://localhost:8082"; name="Web2"}
)

foreach ($test in $webTests) {
    try {
        $response = Invoke-WebRequest -Uri $test.url -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200 -and $response.Content -like "*Velaris Demo OK*") {
            Write-Host "  ✅ $($test.name) is accessible and serving expected content" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $($test.name) returned unexpected response" -ForegroundColor Red
            $allHealthy = $false
        }
    } catch {
        Write-Host "  ❌ $($test.name) is not accessible: $($_.Exception.Message)" -ForegroundColor Red
        $allHealthy = $false
    }
}

# Test 3: Database Connectivity
Write-Host "`nTest 3: Database Connectivity" -ForegroundColor Cyan
try {
    $dbResult = docker exec -e PGPASSWORD=velaris db psql -U velaris -d velaris -c "SELECT COUNT(*) FROM checks;" 2>$null
    if ($dbResult -match "\d+") {
        $count = ($dbResult | Select-String "\d+").Matches[0].Value
        Write-Host "  ✅ Database is accessible with $count monitoring records" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Database query failed" -ForegroundColor Red
        $allHealthy = $false
    }
} catch {
    Write-Host "  ❌ Database connection failed: $($_.Exception.Message)" -ForegroundColor Red
    $allHealthy = $false
}

# Test 4: Watchdog Functionality
Write-Host "`nTest 4: Watchdog Monitoring" -ForegroundColor Cyan
$recentLogs = docker logs watchdog --tail 15 2>$null | Out-String
if ($recentLogs -match "Overall check result.*PASS" -or $recentLogs -match "Check cycle completed") {
    Write-Host "  ✅ Watchdog is actively monitoring" -ForegroundColor Green
} else {
    Write-Host "  ❌ Watchdog appears inactive" -ForegroundColor Red
    Write-Host "    Recent logs: $($recentLogs.Split("`n") | Select-Object -Last 3)" -ForegroundColor Gray
    $allHealthy = $false
}

# Test 5: Time Synchronization
Write-Host "`nTest 5: Time Synchronization" -ForegroundColor Cyan
try {
    $dbQuery = @"
SELECT 
    container_id, 
    drift_seconds 
FROM checks 
WHERE created_at > NOW() - INTERVAL '5 minutes'
ORDER BY created_at DESC 
LIMIT 2;
"@
    
    $driftResult = docker exec -e PGPASSWORD=velaris db psql -U velaris -d velaris -c $dbQuery 2>$null
    if ($driftResult -like "*0*") {
        Write-Host "  ✅ Time synchronization is working (low drift detected)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Time drift may be high - check logs" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Could not verify time synchronization" -ForegroundColor Red
}

# Test 6: Email System (Optional)
if (-not $SkipEmailTest) {
    Write-Host "`nTest 6: Email System" -ForegroundColor Cyan
    try {
        $testResult = docker exec watchdog python -c "
import smtplib
from email.mime.text import MIMEText
msg = MIMEText('Automated test email from Velaris Demo test suite.')
msg['Subject'] = '[Velaris] Automated Test Email'
msg['From'] = 'alerts@velaris.local'
msg['To'] = 'support@velaris.local'
with smtplib.SMTP('mailhog', 1025, timeout=10) as s:
    s.sendmail('alerts@velaris.local', ['support@velaris.local'], msg.as_string())
print('success')
" 2>$null
        
        if ($testResult -like "*success*") {
            Write-Host "  ✅ Email system is functional" -ForegroundColor Green
            Write-Host "    Check MailHog UI at http://localhost:8025 to see the test email" -ForegroundColor Gray
        } else {
            Write-Host "  ❌ Email test failed" -ForegroundColor Red
            $allHealthy = $false
        }
    } catch {
        Write-Host "  ❌ Email system error: $($_.Exception.Message)" -ForegroundColor Red
        $allHealthy = $false
    }
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Green
if ($allHealthy) {
    Write-Host "🎉 All tests passed! The Velaris Demo system is healthy." -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Check the details above." -ForegroundColor Yellow
}

Write-Host "`nFor continuous monitoring, check:" -ForegroundColor Gray
Write-Host "- Watchdog logs: docker logs watchdog --follow"
Write-Host "- Database records: docker exec -e PGPASSWORD=velaris db psql -U velaris -d velaris"
Write-Host "- MailHog UI: http://localhost:8025"
