# Multi-Container Monitoring System - Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   MULTI-CONTAINER MONITORING SYSTEM                    │
│                             (Docker Environment)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │     WEB1     │    │     WEB2     │    │   LOG-VIEWER │                   │
│  │  (NGINX)     │    │  (NGINX)     │    │   (NGINX +   │                   │
│  │ Port: 8081   │    │ Port: 8082   │    │  Flask API)  │                   │
│  │              │    │              │    │ Port: 8090   │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         │                    │                    │                         │
│         └────────────────────┼────────────────────┘                         │
│                              │                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                       WATCHDOG                                      │    │
│  │                   (Python Service)                                  │    │
│  │                                                                     │    │
│  │ • Health Monitoring (every 60s)                                     │    │
│  │ • Time Sync Validation                                              │    │
│  │ • Dynamic Content Generation                                        │    │
│  │ • Email Alerting                                                    │    │
│  │ • Metrics Collection                                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                              │
│         ┌────────────────────┴────────────────────┐                         │
│         │                                         │                         │
│  ┌──────────────┐                        ┌──────────────┐                   │
│  │   DATABASE   │                        │   MAILHOG    │                   │
│  │ (PostgreSQL) │                        │ (Email Test) │                   │
│  │ Port: 5432   │                        │ Port: 8025   │                   │
│  │              │                        │              │                   │
│  └──────────────┘                        └──────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                          ┌─────────────────┐
                          │  EXTERNAL APIs  │
                          │                 │
                          │ WorldTimeAPI    │
                          │ (Time Source)   │
                          └─────────────────┘
```

## Component Details

### 🌐 **Web Services Layer**
- **WEB1 & WEB2**: NGINX containers serving dynamic content
  - Shared volume for content updates
  - Container-specific identification
  - Real-time timestamp display

### 🔍 **Monitoring Layer**
- **WATCHDOG**: Core monitoring service
  - Python-based health checker
  - 60-second check intervals
  - Multi-dimensional validation

### 📊 **Data Layer**
- **DATABASE**: PostgreSQL with enhanced schema
  - Check results persistence
  - Performance metrics storage
  - Historical trend analysis

### 📧 **Communication Layer**
- **MAILHOG**: Email testing service
  - SMTP server simulation
  - Web UI for email inspection

### 🎛️ **Observability Layer**
- **LOG-VIEWER**: Real-time log access
  - Flask API backend
  - Web-based interface
  - Container log aggregation
  - Custom monitoring dashboard

## Data Flow

### 1. **Monitoring Cycle**
```
Watchdog → WorldTimeAPI → Time Comparison → Content Update → HTTP Check → Database → Email Alert (if failure)
```

### 2. **Log Flow**
```
All Containers → Shared Volume → Log-Viewer API → Web Interface
```

### 3. **Metrics Flow**
```
Watchdog → Structured Logs → Database → Custom Dashboard
```

## Network Architecture

### **Internal Communication**
- All services communicate via Docker internal network
- Service discovery through container names
- Shared volumes for file-based communication

### **External Access Points**
- **8081**: Web1 service
- **8082**: Web2 service  
- **8090**: Log viewer interface
- **8025**: MailHog web UI
- **5432**: Database (for external tools)

## Security Considerations

### **Email Configuration**
- Gmail SMTP for production alerts
- MailHog for development testing
- Configurable via environment variables

### **Data Protection**
- Database credentials via environment variables
- Log file rotation to prevent disk overflow
- Container isolation for service separation
