# Velaris Demo - Real Email Setup
# PowerShell script to configure real email alerts

param(
    [Parameter(Mandatory=$true)]
    [string]$FromEmail,
    
    [Parameter(Mandatory=$true)]
    [string]$ToEmail,
    
    [Parameter(Mandatory=$true)]
    [string]$SmtpPassword,
    
    [string]$SmtpProvider = "gmail"
)

Write-Host "=== Configuring Real Email Alerts ===" -ForegroundColor Green
Write-Host ""

# Determine SMTP settings based on provider
$smtpConfig = switch ($SmtpProvider.ToLower()) {
    "gmail" {
        @{
            Host = "smtp.gmail.com"
            Port = "587"
            User = $FromEmail
        }
    }
    "outlook" {
        @{
            Host = "smtp-mail.outlook.com"
            Port = "587"
            User = $FromEmail
        }
    }
    "sendgrid" {
        @{
            Host = "smtp.sendgrid.net"
            Port = "587"
            User = "apikey"
        }
    }
    default {
        Write-Host "Unsupported provider. Using Gmail settings." -ForegroundColor Yellow
        @{
            Host = "smtp.gmail.com"
            Port = "587"
            User = $FromEmail
        }
    }
}

Write-Host "Provider: $SmtpProvider" -ForegroundColor Cyan
Write-Host "SMTP Host: $($smtpConfig.Host)" -ForegroundColor Cyan
Write-Host "SMTP Port: $($smtpConfig.Port)" -ForegroundColor Cyan
Write-Host "From Email: $FromEmail" -ForegroundColor Cyan
Write-Host "To Email: $ToEmail" -ForegroundColor Cyan
Write-Host ""

# Create .env file
$envContent = @"
# Velaris Demo Environment Configuration - Real Email Setup
TARGET_TIMEZONE=Asia/Colombo
WEB_TARGETS=web1:80,web2:80
EXPECT_TEXT=Velaris Demo OK

# Database configuration
DB_HOST=db
DB_PORT=5432
DB_NAME=velaris
DB_USER=velaris
DB_PASSWORD=velaris

# Real SMTP configuration
SMTP_HOST=$($smtpConfig.Host)
SMTP_PORT=$($smtpConfig.Port)
SMTP_FROM=$FromEmail
SMTP_TO=$ToEmail
SMTP_USER=$($smtpConfig.User)
SMTP_PASSWORD=$SmtpPassword

# Monitoring configuration
CHECK_INTERVAL_SEC=60
MAX_ALLOWED_DRIFT_SEC=5
TZ=Asia/Colombo
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "✅ Created .env file with real email configuration" -ForegroundColor Green

# Update docker-compose to disable MailHog when using real email
Write-Host "✅ Configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart the system: docker-compose --env-file .env up --build -d"
Write-Host "2. Test email: .\test-email.ps1"
Write-Host "3. Monitor logs: docker logs watchdog --follow"
Write-Host ""
Write-Host "Note: Make sure you're using an App Password if using Gmail!" -ForegroundColor Red
