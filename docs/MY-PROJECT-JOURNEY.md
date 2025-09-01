# My Velaris Demo Project Journey

*A personal account of building a containerized monitoring system*

## Day 1: Starting the Project

### What I Wanted to Build
I set out to create a real monitoring system like the ones used in production environments. My goal was to build something that could:
- Monitor multiple web servers automatically
- Send me email alerts when problems happen
- Store monitoring data for analysis
- Handle failures gracefully

### My Initial Setup
I started with a basic Docker Compose file that had:
- Two NGINX web servers (web1 and web2)
- A PostgreSQL database
- A Python monitoring script (watchdog)
- MailHog for email testing

## The Problems I Discovered

### Issue #1: Massive Time Drift
When I first ran the system, I was shocked to find that my containers had **over 7700 seconds** of time difference! That's more than 2 hours of drift. This was a critical problem because:
- Time synchronization is essential for monitoring
- Log timestamps were completely wrong
- My monitoring logic was failing

**How I Fixed It:**
- Added proper timezone configuration to all containers
- Set `TZ=Asia/Colombo` environment variable consistently
- Verified time sync across all services

### Issue #2: Silent Failures
The monitoring script was failing but I had no idea why because there were no logs. It was running but not doing anything useful.

**How I Fixed It:**
- Added comprehensive logging to the Python script
- Used different log levels (INFO, WARNING, ERROR)
- Made sure every action was logged with timestamps
- Now I can see exactly what's happening at any moment

### Issue #3: Network Connectivity
The watchdog couldn't connect to the external time API (worldtimeapi.org) from inside the Docker container.

**How I Fixed It:**
- Added fallback mechanisms to use system time when API fails
- Implemented proper error handling for network issues
- Made the system resilient to external service outages

### Issue #4: Real Email Alerts
The biggest challenge was getting actual email alerts working instead of just using the test MailHog service.

**How I Fixed It:**
- Set up Gmail App Password authentication
- Configured SMTP with TLS encryption
- Updated environment variables with real email addresses
- Tested actual email delivery to my Gmail account

## My Technical Implementation

### The Monitoring Script (watchdog.py)
This is the heart of my system. Here's what I made it do:

1. **Fetch World Time**: Gets accurate time from worldtimeapi.org
2. **Check Each Server**: Tests both web1 and web2 every minute
3. **Compare Times**: Ensures time drift stays under 5 seconds
4. **Update Content**: Refreshes web pages with current time info
5. **Validate Responses**: Checks HTTP status and expected content
6. **Store Results**: Saves everything to PostgreSQL database
7. **Send Alerts**: Emails me immediately when problems occur

### The Database Schema
I designed a simple but effective table structure:
```sql
CREATE TABLE checks (
    id SERIAL PRIMARY KEY,
    target VARCHAR(50) NOT NULL,
    status VARCHAR(10) NOT NULL,
    http_status INTEGER,
    time_drift_seconds INTEGER,
    fetched_time TIMESTAMP,
    local_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Email Configuration
Getting real Gmail alerts was tricky, but I figured it out:
- From: isurunaveen27@gmail.com
- To: naveenliyanaarachchi27@gmail.com
- SMTP: smtp.gmail.com:587 with TLS
- Authentication: Gmail App Password (not regular password)

## Testing and Validation

### My Testing Strategy
I created several PowerShell scripts to validate everything:

1. **test-system.ps1**: Comprehensive health check
2. **test-email.ps1**: Verifies real email delivery
3. **monitor.ps1**: Shows live monitoring data

### What I Validated
- ✅ All 5 containers running properly
- ✅ Web servers responding with HTTP 200
- ✅ Time drift reduced to 0 seconds
- ✅ Database storing monitoring records (111+ entries)
- ✅ Real Gmail alerts successfully delivered
- ✅ Dynamic content updating every minute

## Challenges I Overcame

### Gmail SMTP Setup
The hardest part was getting Gmail authentication working:
- Regular passwords don't work with SMTP
- Had to enable 2-factor authentication
- Generated an App Password specifically for this project
- Configured TLS encryption properly

### Container Networking
Learning how containers communicate was tricky:
- Understanding Docker Compose networks
- Resolving container names (web1, web2, db)
- Handling temporary network issues gracefully

### PowerShell Scripting
Writing effective test scripts required learning:
- Docker command integration
- Output parsing and formatting
- Error handling in PowerShell
- JSON processing for API responses

## What Works Now

### Monitoring Dashboard (via logs)
I can see real-time monitoring with:
```bash
docker logs watchdog --follow
```

Sample output shows exactly what's happening:
```
2025-09-02 01:00:46,447 - INFO - HTTP check for web1: status=200, contains_expected=True
2025-09-02 01:00:46,447 - INFO - Overall check result for web1: PASS
2025-09-02 01:00:46,490 - INFO - Overall check result for web2: PASS
```

### Database Tracking
Every check is stored permanently:
```bash
docker exec -e PGPASSWORD=velaris db psql -U velaris -d velaris -c "SELECT COUNT(*) FROM checks;"
```
Shows 111+ monitoring records and growing!

### Real Alert System
When I tested the email system, I actually received emails at my Gmail account with subjects like:
- "[Velaris] Error while checking web1:80"
- "[Velaris] Validation failed for web2:80"

## My Key Learnings

### Technical Knowledge
- **Container Orchestration**: How to make multiple containers work together
- **Health Monitoring**: Building reliable monitoring systems
- **Database Integration**: Persistent data storage and retrieval
- **Email Systems**: SMTP configuration and authentication
- **Error Handling**: Building resilient systems

### Best Practices I Learned
- Always log everything for debugging
- Build fallback mechanisms for external dependencies
- Test real-world scenarios, not just happy paths
- Document problems and solutions as you go
- Use environment variables for configuration

### Problem-Solving Skills
- Systematic debugging approach
- Reading logs to understand failures
- Testing one component at a time
- Validating fixes thoroughly before moving on

## Current System Metrics

As of my latest check:
- **Uptime**: All containers running smoothly
- **Time Drift**: 0 seconds (perfect synchronization)
- **HTTP Checks**: 100% success rate on recent checks
- **Database Records**: 111+ monitoring entries
- **Email Alerts**: Successfully delivered to real Gmail
- **Check Frequency**: Every 60 seconds as designed

## What This Project Taught Me

This wasn't just about writing code - it was about building a complete, production-ready system. I learned:

1. **Real-world complexity**: Production systems have many moving parts
2. **Debugging skills**: How to trace problems across multiple containers
3. **Reliability engineering**: Building systems that work even when things fail
4. **Documentation importance**: Writing clear docs saved me time later
5. **Testing methodology**: How to validate complex systems thoroughly

## Files I Created/Modified

### Core System Files
- `docker-compose.yml` - Orchestrates all containers
- `watchdog/watchdog.py` - Main monitoring logic
- `watchdog/Dockerfile` - Container setup for monitoring
- `.env` - Configuration with real Gmail credentials

### Database Setup
- `db/init.sql` - Database schema and initialization

### Web Configuration
- `web/default.conf` - NGINX configuration for both servers

### Testing Tools
- `test-system.ps1` - Comprehensive system validation
- `test-email.ps1` - Real email delivery testing
- `monitor.ps1` - Live monitoring dashboard
- `setup-real-email.ps1` - Email configuration helper

### Documentation
- `docs/README.md` - Main project documentation (this file)
- `docs/architecture.md` - Technical architecture details
- `docs/email-setup.md` - Email configuration guide
- `docs/GMAIL-SETUP.md` - Gmail-specific setup instructions
- `docs/EMAIL-TROUBLESHOOTING.md` - Common email issues and fixes

## Conclusion

I'm proud of what I built here. This started as a learning project but became a fully functional monitoring system that I could actually use in production. The fact that I'm getting real email alerts proves the system works end-to-end.

The most rewarding part was solving real problems systematically and building something that actually works reliably. Every component serves a purpose, and the whole system is greater than the sum of its parts.

**Final Status: All Part 1 requirements completed successfully! ✅**

---
*Project completed on September 2, 2025*  
*Total development time: Multiple sessions over several days*  
*Key achievement: Real email alerts with Gmail SMTP integration*
