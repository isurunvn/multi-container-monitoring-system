# My Velaris Demo Project - Complete Monitoring System

## What I Built

I created a complete containerized monitoring system from scratch. It's like having a smart assistant that watches over multiple websites and tells me immediately if anything goes wrong. Here's what I accomplished:

### The System I Created
- **Two Web Servers**: I set up two NGINX containers that serve different content
- **Smart Monitoring**: A Python watchdog that checks everything every minute
- **Database Storage**: PostgreSQL keeps track of all the monitoring history
- **Real Email Alerts**: Actual Gmail notifications when problems happen
- **Testing Tools**: Scripts to verify everything works perfectly

### Why I Built This
I wanted to learn how to create a real monitoring system that businesses use. This project taught me Docker, networking, databases, email systems, and how to make everything work together reliably.

## How to Use My System

### Starting Everything Up
1. **Launch the entire system:**
   ```bash
   docker-compose up --build -d
   ```
   This starts all 5 containers and they begin working together automatically.

2. **Check if everything is working:**
   - Visit Web Server 1: http://localhost:8081
   - Visit Web Server 2: http://localhost:8082
   - View email interface: http://localhost:8025
   - The database runs on localhost:5432

3. **When you're done:**
   ```bash
   docker-compose down
   ```

### Testing Everything Works
I created several PowerShell scripts to test the system:
- `.\test-system.ps1` - Runs all health checks
- `.\test-email.ps1` - Tests real Gmail email delivery
- `.\monitor.ps1` - Shows live monitoring data

## What My System Does

### The Smart Monitoring I Built
My watchdog service is like a security guard that never sleeps. Every 60 seconds, it:

1. **Checks the Time**: Gets the current time from a world time API
2. **Compares Times**: Makes sure all containers have the right time (within 5 seconds)
3. **Tests Websites**: Visits both web servers to ensure they respond correctly
4. **Updates Content**: Refreshes each website with new timestamps
5. **Saves Everything**: Stores all results in a PostgreSQL database
6. **Sends Alerts**: Emails me immediately if anything fails

### Real Email Notifications
I configured actual Gmail SMTP so I get real email alerts at `naveenliyanaarachchi27@gmail.com` when:
- A web server stops responding
- Time drift becomes too large (over 5 seconds)
- The monitoring system detects any problems

### What Each Container Does
- **web1 & web2**: Serve websites that show live time information
- **database**: Stores all monitoring history so I can see trends
- **watchdog**: The brain that monitors everything continuously
- **mailhog**: Originally for testing emails, now we use real Gmail

## Problems I Solved

### Major Issues I Fixed
When I first started, the system had several critical problems:

1. **Time Sync Issues**: Containers had 7700+ seconds of time drift! I fixed this by properly configuring timezones across all containers.

2. **Silent Failures**: The monitoring script was failing quietly without any logs. I added comprehensive logging so I can see exactly what's happening.

3. **Network Problems**: The watchdog couldn't connect to the world time API. I added fallback mechanisms and proper error handling.

4. **Email Setup**: Getting real Gmail alerts working was tricky. I had to:
   - Generate a Gmail App Password
   - Configure SMTP with TLS encryption
   - Handle authentication properly
   - Test actual email delivery

### How I Debugged Everything
I learned to use these tools effectively:
- `docker logs watchdog` - To see what the monitoring script is doing
- `docker exec` commands - To check database contents
- PowerShell scripts - To automate testing and validation
- Gmail SMTP testing - To verify real email delivery

## My Configuration Setup

The system uses environment variables I configured in `.env`:
```
# Email Configuration (Real Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_FROM=isurunaveen27@gmail.com
SMTP_TO=naveenliyanaarachchi27@gmail.com
SMTP_PASSWORD=[My Gmail App Password]

# Monitoring Settings
TARGET_TIMEZONE=Asia/Colombo
CHECK_INTERVAL_SEC=60
MAX_ALLOWED_DRIFT_SEC=5
EXPECT_TEXT=Velaris Demo OK
```

## How to Check My System is Working

### Quick Health Check
```bash
.\test-system.ps1
```
This script checks everything and gives me a report card.

### See What's Happening Live
```bash
docker logs watchdog --follow
```
This shows me real-time monitoring activity.

### Check Email Alerts Work
```bash
.\test-email.ps1
```
This sends a test email to verify Gmail delivery.

### View Monitoring History
```bash
docker exec -e PGPASSWORD=velaris db psql -U velaris -d velaris -c "SELECT target, status, created_at FROM checks ORDER BY created_at DESC LIMIT 10;"
```
This shows the last 10 monitoring results.

## What I Learned

### Technical Skills
- **Docker Compose**: How to orchestrate multiple containers
- **Networking**: Making containers communicate with each other
- **Database Integration**: Storing and retrieving monitoring data
- **Email Systems**: Setting up real SMTP with Gmail
- **Error Handling**: Building resilient systems with fallbacks
- **Logging**: Creating detailed logs for debugging

### Problem-Solving Process
1. **Identify Issues**: Found timezone drift and silent failures
2. **Systematic Debugging**: Used logs and testing to understand problems
3. **Incremental Fixes**: Solved one problem at a time
4. **Validation**: Tested each fix thoroughly
5. **Documentation**: Recorded everything for future reference

## Current System Status

✅ **All containers running smoothly**  
✅ **Zero time drift between containers**  
✅ **Web servers responding correctly**  
✅ **Database storing 111+ monitoring records**  
✅ **Real Gmail alerts working perfectly**  
✅ **Comprehensive logging and error handling**  

## Future Improvements I Could Add

- Web dashboard to visualize monitoring data
- SMS alerts in addition to email
- More sophisticated health checks
- Performance metrics collection
- Automated scaling based on load
