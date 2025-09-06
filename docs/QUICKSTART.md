# Velaris Monitoring System - Quick Start

## 🚀 Fast Setup (5 minutes)

### Prerequisites
- Docker Desktop installed and running
- PowerShell or Command Prompt
- 4GB RAM available

### 1. Start the System
```powershell
# In project directory
docker-compose up -d

# Wait for containers to start (30-60 seconds)
docker ps
```

### 2. Access Services
- **Web Services**: http://localhost:8081 and http://localhost:8082
- **Log Viewer**: http://localhost:8090
- **Email Interface**: http://localhost:8025

### 3. Verify Monitoring
```powershell
# Check monitoring logs
docker logs watchdog --tail 10

# Should see regular check cycles every 60 seconds
```

### 4. Test Email Alerts
```powershell
# Stop a container to trigger alert
docker stop web1

# Check for email at http://localhost:8025 within 60 seconds
# Restart container
docker start web1
```

### 5. Stop System
```powershell
docker-compose down
```

---

## 📁 Project Structure
```
multi-container-monitoring-system/
├── docker-compose.yml          # Main orchestration
├── .env                        # Configuration
├── ARCHITECTURE.md             # System design
├── DOCUMENTATION.md            # Complete guide
├── QUICKSTART.md              # This file
├── db/
│   └── init.sql               # Database schema
├── watchdog/
│   ├── Dockerfile             # Monitoring service
│   └── watchdog.py            # Main monitoring script
├── web/
│   └── default.conf           # NGINX configuration
└── logging/
    ├── Dockerfile             # Log viewer service
    ├── log_api.py             # Flask API
    ├── index.html             # Web interface
    └── nginx.conf             # Proxy configuration
```

---

## 🎯 Core Features Demonstrated

### ✅ Requirements Met
1. **Containerized Environment**: 6 containers with NGINX web servers
2. **Health Monitoring**: Python script with WorldTimeAPI integration
3. **Database Persistence**: PostgreSQL with check results and metrics
4. **Email Alerting**: Gmail SMTP with MailHog testing
5. **Logging System**: Structured logs with web viewer

### 🔍 Key Metrics Monitored
1. **System Availability** - Uptime percentage tracking
2. **Response Time** - Millisecond-precision measurements  
3. **Time Drift** - Container synchronization validation

### 📊 Monitoring Dashboards
- Real-time log viewer with filtering
- Custom analytics dashboard built from scratch
- Email alert history via MailHog
- Database performance views

---

## 🛠️ Troubleshooting

### Container Issues
```powershell
# Check container status
docker ps -a

# View container logs
docker logs [container_name]

# Restart specific service
docker-compose restart [service_name]
```

### Database Issues
```powershell
# Connect to database
docker exec -it db psql -U velaris -d velaris

# Check tables
\dt

# View recent checks
SELECT * FROM checks ORDER BY created_at DESC LIMIT 5;
```

### Email Issues
```powershell
# Check SMTP configuration
docker exec watchdog printenv | findstr SMTP

# View email logs
docker logs mailhog
```

---

## 📞 Support

For detailed technical documentation, see:
- **ARCHITECTURE.md** - System design and component details
- **DOCUMENTATION.md** - Complete setup and configuration guide

System demonstrates production-ready monitoring practices with containerization, automated health checks, and comprehensive observability.
