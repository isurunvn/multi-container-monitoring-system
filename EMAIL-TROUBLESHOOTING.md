# Email Configuration Troubleshooting Guide

## Issue: SMTP Connection Timeouts

If you're experiencing connection timeouts or hanging when testing email, this is likely due to:

### 1. Network/Firewall Restrictions
- Corporate firewalls often block SMTP ports (587, 465, 25)
- Some ISPs block outbound SMTP connections
- Docker network configuration may prevent external SMTP access

### 2. Solutions & Alternatives

#### Option A: Use Alternative SMTP Port (Gmail)
Try Gmail's alternative port in your `.env` file:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
# ... rest of config
```

#### Option B: Use Outlook/Hotmail SMTP
Often more permissive than Gmail:
```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_FROM=your-email@outlook.com
SMTP_TO=naveenliyanaarachchi27@gmail.com
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-outlook-password
```

#### Option C: Test from Host Machine First
Before configuring Docker, test SMTP from your host machine:

```powershell
# Test with PowerShell
$smtpServer = "smtp.gmail.com"
$smtpPort = 587
$username = "isurunaveen27@gmail.com"
$password = "tkadymaqliojxlti"

$smtp = New-Object Net.Mail.SmtpClient($smtpServer, $smtpPort)
$smtp.EnableSsl = $true
$smtp.Credentials = New-Object System.Net.NetworkCredential($username, $password)

$message = New-Object System.Net.Mail.MailMessage
$message.From = $username
$message.To.Add("naveenliyanaarachchi27@gmail.com")
$message.Subject = "[Velaris] Host Test Email"
$message.Body = "Test email from host machine"

try {
    $smtp.Send($message)
    Write-Host "SUCCESS: Email sent from host!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
```

#### Option D: Use SendGrid or AWS SES
For production environments, use dedicated email services:

**SendGrid Example:**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM=verified-sender@yourdomain.com
SMTP_TO=naveenliyanaarachchi27@gmail.com
```

### 3. Current Workaround

For now, your system is configured to use Gmail but may have network connectivity issues. The monitoring and alerting logic is correct, but emails may not be delivered due to network restrictions.

**Alternative Testing:**
1. Check MailHog (http://localhost:8025) - alerts are still being sent there
2. Monitor the watchdog logs: `docker logs watchdog --follow`
3. Check database records: `docker exec -e PGPASSWORD=velaris db psql -U velaris -d velaris -c "SELECT * FROM checks ORDER BY created_at DESC LIMIT 5;"`

### 4. Verification Steps

If emails are working, you should see in watchdog logs:
```
INFO - Using authenticated SMTP with TLS
INFO - Alert sent successfully
```

If failing, you'll see:
```
ERROR - Failed to send alert: [connection error details]
```
