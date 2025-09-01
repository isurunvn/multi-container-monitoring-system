# Real Email Configuration Guide

## Setup Instructions for Real Email Alerts

### Option 1: Gmail SMTP (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account Settings → Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. **Create a .env file** (copy from .env.example):
   ```
   # Real Gmail SMTP Configuration
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_FROM=your-email@gmail.com
   SMTP_TO=recipient@email.com
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

4. **Update docker-compose.yml** to use real SMTP:
   ```yaml
   environment:
     - SMTP_HOST=${SMTP_HOST:-mailhog}
     - SMTP_PORT=${SMTP_PORT:-1025}
     - SMTP_FROM=${SMTP_FROM:-alerts@velaris.local}
     - SMTP_TO=${SMTP_TO:-support@velaris.local}
     - SMTP_USER=${SMTP_USER:-}
     - SMTP_PASSWORD=${SMTP_PASSWORD:-}
   ```

5. **Restart the system**:
   ```bash
   docker-compose down
   docker-compose --env-file .env up --build -d
   ```

### Option 2: Other SMTP Providers

#### Outlook/Hotmail:
```
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_FROM=your-email@outlook.com
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
```

#### SendGrid:
```
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_FROM=your-verified-sender@domain.com
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

#### AWS SES:
```
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_FROM=your-verified-email@domain.com
SMTP_USER=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
```

### Testing Real Email

1. **Create .env file** with your real email configuration
2. **Restart containers**: `docker-compose --env-file .env up --build -d`
3. **Trigger a test alert**:
   ```powershell
   docker exec watchdog python -c "
   import sys, os
   sys.path.append('/app')
   from watchdog import send_alert
   send_alert('[Velaris] Test Alert - Real Email', 'This is a test to verify real email delivery works!')
   "
   ```
4. **Check your email** for the test alert

### Triggering Alerts for Testing

You can manually trigger alerts by:

1. **Stopping a web container**:
   ```bash
   docker stop web1
   # Wait 60 seconds for watchdog to detect and alert
   docker start web1
   ```

2. **Simulating time drift** (temporarily change MAX_ALLOWED_DRIFT_SEC to 1):
   ```yaml
   - MAX_ALLOWED_DRIFT_SEC=1
   ```

3. **Changing expected text** to cause content validation failure:
   ```yaml
   - EXPECT_TEXT=Different Text
   ```

### Security Notes

- Never commit real passwords to git repositories
- Use environment variables or Docker secrets for sensitive data
- Consider using API keys instead of passwords where possible
- For production, use a dedicated SMTP service like SendGrid or AWS SES
