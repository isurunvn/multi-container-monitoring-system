# Velaris Monitoring System

## Overview
Complete containerized monitoring system with automated health checks, real-time logging, and email notifications.

## Quick Start
```powershell
# Start the system
docker-compose up --build -d

# Run demo
.\demo.ps1

# Stop system
docker-compose down
```

## Services
- **Web Services**: http://localhost:8081, http://localhost:8082
- **Log Viewer**: http://localhost:8090  
- **Email UI**: http://localhost:8025
- **Database**: PostgreSQL on localhost:5432

## Features
- **Health Monitoring**: Automated checks every 60 seconds
- **Response Time Tracking**: Millisecond precision measurements
- **Email Alerts**: Real Gmail notifications for failures
- **Structured Logging**: JSON metrics with rotation
- **Performance Analytics**: Database views for monitoring trends
- **Web Log Viewer**: Browser-based log access

## System Architecture
- **Watchdog**: Python monitoring service with enhanced logging
- **Database**: PostgreSQL with performance tracking schema
- **Web Interface**: NGINX log viewer with metrics display
- **Email System**: SMTP integration with Gmail/MailHog

## Monitoring Capabilities
- Time drift detection (±5 second tolerance)
- HTTP response validation
- Network connectivity checks
- Resource utilization tracking
- Error rate analysis
- Recovery time measurement

## File Structure
```
docker-compose.yml    # Single orchestration file
db/init.sql          # Consolidated database schema  
watchdog/watchdog.py # Enhanced monitoring script
logging/index.html   # Web log viewer interface
demo.ps1            # System demonstration
```

## Development
The system is designed for reliability and maintainability with:
- Consolidated single-file architecture
- Enhanced error handling and recovery
- Structured metrics collection
- Real-time performance tracking
- Comprehensive logging with web access

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
