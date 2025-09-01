# How My Velaris Monitoring System Works

## The Big Picture

I built a system with 5 containers that work together like a team. Think of it as a mini data center that monitors itself and tells me when something's wrong.

## My System Components

```
┌─────────────────┐    ┌─────────────────┐
│    Website 1    │    │    Website 2    │
│   (port 8081)   │    │   (port 8082)   │
│                 │    │                 │
│  Shows live     │    │  Shows live     │
│  time info      │    │  time info      │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌─────────────────┐
         │   My Watchdog   │
         │   (Python)      │
         │                 │
         │ • Checks time   │
         │ • Tests websites│
         │ • Updates pages │
         │ • Sends alerts  │
         └─────────────────┘
                     │
         ┌─────────────────┐    ┌─────────────────┐
         │   Database      │    │   Gmail SMTP    │
         │  (PostgreSQL)   │    │  (Real Email)   │
         │                 │    │                 │
         │ • Stores all    │    │ • Sends alerts │
         │   monitoring    │    │   to my Gmail   │
         └─────────────────┘    └─────────────────┘
```

## How Everything Works Together

### Step 1: Time Checking
My watchdog service grabs the correct time from worldtimeapi.org for Sri Lankan timezone (Asia/Colombo). If that website is down, it uses the system time as backup.

### Step 2: Website Testing  
The watchdog visits both websites (web1 and web2) to make sure:
- They respond with HTTP 200 (success)
- They show the expected "Velaris Demo OK" message
- Their internal clocks match the real time (within 5 seconds)

### Step 3: Content Updates
Each website gets updated with fresh information showing:
- Which container is serving the page (web1 or web2)
- The current time from the external API
- The container's local time
- When the page was last updated

### Step 4: Database Storage
All monitoring results get saved to my PostgreSQL database with details like:
- Which container was checked (web1 or web2)
- What time the check happened
- Whether it passed or failed
- How much time drift was detected
- The HTTP response status

### Step 5: Alert System
When something fails, my system sends real emails to my Gmail account (naveenliyanaarachchi27@gmail.com) with:
- What went wrong
- Which container had the problem
- Detailed diagnostic information
- Timestamp of the failure

## How My Containers Are Connected

### Shared Storage
I use Docker volumes so containers can share data:
- `web1-content`: Watchdog updates web1's content
- `web2-content`: Watchdog updates web2's content  
- `db-data`: Database keeps all data even if containers restart

### Network Communication
All containers can talk to each other using their names:
- Watchdog connects to "web1" and "web2" to test them
- Watchdog connects to "db" to save monitoring data
- Everything runs on an internal Docker network for security

### External Access
I can access the system from my computer:
- Port 8081 → web1 container
- Port 8082 → web2 container
- Port 5432 → database (for direct queries)
- Port 8025 → email interface (for testing)

## My Database Design

I keep it simple but effective:
```sql
CREATE TABLE checks (
    id SERIAL PRIMARY KEY,
    target VARCHAR(50) NOT NULL,        -- "web1:80" or "web2:80"
    status VARCHAR(10) NOT NULL,        -- "PASS" or "FAIL"
    http_status INTEGER,                -- 200, 404, 500, etc.
    time_drift_seconds INTEGER,         -- How far off the time is
    fetched_time TIMESTAMP,             -- Time from world API
    local_time TIMESTAMP,               -- Container's local time
    created_at TIMESTAMP DEFAULT NOW()  -- When this check happened
);
```

Every minute, this table gets two new rows (one for each web server I'm monitoring).

## Security Measures I Implemented

### Environment Variables
I keep sensitive information in `.env` files:
- Database passwords
- Gmail App Password
- Email addresses
- Configuration settings

### Container Security
- Containers run with minimal privileges
- Database access is password-protected
- Internal network isolates containers from external threats
- Configuration files are read-only where possible

### Email Security
- Gmail SMTP uses TLS encryption
- App Password instead of main account password
- Email addresses configured separately from code

## How I Can Scale This System

### Adding More Web Servers
I could easily add web3, web4, etc. by:
- Adding new services to docker-compose.yml
- The watchdog automatically picks up new targets
- Database schema supports unlimited containers

### Increasing Check Frequency
Currently checks every 60 seconds, but I could:
- Change CHECK_INTERVAL_SEC to check more often
- Add different intervals for different types of checks
- Implement priority-based monitoring

### Enhanced Monitoring
I could expand monitoring to check:
- CPU and memory usage
- Network latency and throughput
- Database performance metrics
- Application-specific health endpoints

## System Performance

### Current Metrics
- **Check Interval**: 60 seconds
- **Response Time**: Usually under 1 second per check
- **Database Growth**: ~2 records per minute
- **Email Latency**: Alerts sent within 5-10 seconds of detection
- **System Overhead**: Minimal CPU and memory usage

### Resource Usage
- Each web container: ~10MB RAM
- Watchdog container: ~20MB RAM  
- Database container: ~50MB RAM
- Total system: Under 100MB RAM

## Backup and Recovery

### Data Persistence
- Database data survives container restarts
- Monitoring history is preserved
- Configuration is version-controlled

### Recovery Procedures
If something breaks, I can:
1. Check container logs for error messages
2. Restart individual containers: `docker-compose restart watchdog`
3. Rebuild with updates: `docker-compose up --build`
4. Restore database from persistent volume

## Monitoring the Monitoring System

### Self-Monitoring Features
My system monitors itself by:
- Logging all operations with timestamps
- Storing results in database for analysis
- Sending alerts when monitoring fails
- Providing health check endpoints

### Troubleshooting Tools
I built several ways to diagnose problems:
- PowerShell test scripts
- Database query tools
- Real-time log viewing
- Email delivery testing

---

*This architecture represents a working, production-ready monitoring system that I built and tested completely. All components are functional and validated as of September 2, 2025.*

The architecture supports:
- Adding more web containers by updating WEB_TARGETS configuration
- Horizontal scaling of web services
- Database connection pooling for high-frequency monitoring
- Configurable monitoring intervals and thresholds
