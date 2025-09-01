# 📧 Gmail App Password Setup Instructions

## Steps to Enable Real Email Alerts

### 1. Generate Gmail App Password

**Important**: You need an App Password, NOT your regular Gmail password.

1. **Go to Google Account Settings**: https://myaccount.google.com/
2. **Click on "Security"** in the left sidebar
3. **Enable 2-Step Verification** (if not already enabled)
4. **Go to "App passwords"** section
5. **Generate new app password**:
   - Select app: "Mail"
   - Select device: "Other (custom name)" → Enter "Velaris Demo"
   - Click "Generate"
6. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### 2. Update Configuration

Open the `.env` file and replace `your-gmail-app-password` with your actual app password:

```bash
SMTP_PASSWORD=abcd-efgh-ijkl-mnop
```

### 3. Restart System with Real Email

```powershell
# Stop current system
docker-compose down

# Start with real email configuration
docker-compose --env-file .env up --build -d
```

### 4. Test Email Functionality

```powershell
# Run email test
.\test-email.ps1
```

### 5. Trigger Real Alerts

To test the alert system:

```powershell
# Stop a web container to trigger an alert
docker stop web1

# Wait 60 seconds for watchdog to detect and send alert
# Then restart
docker start web1
```

You should receive an email at `naveenliyanaarachchi27@gmail.com` with details about the failure!

### 🔐 Security Notes

- The App Password is stored in the `.env` file
- **Never commit .env to git** (it's in .gitignore)
- App passwords are safer than your main Gmail password
- You can revoke app passwords anytime from Google Account settings

### 📬 What You'll Receive

When alerts are triggered, you'll get emails with:
- Alert subject: `[Velaris] Validation failed for web1`
- Detailed error information
- HTTP status codes
- Time drift measurements
- Timestamps for debugging

Ready to set up? Just replace `your-gmail-app-password` in the `.env` file with your actual App Password!
