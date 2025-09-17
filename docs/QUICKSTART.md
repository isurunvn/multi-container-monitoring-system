# Multi-Container Monitoring System - Quick Start

## 🎯 What This System Does

This is a **production-ready monitoring system** that demonstrates:
- **🌐 Dual Web Server Monitoring** - Continuously monitors 2 NGINX servers (web1, web2)
- **⏰ Timezone Synchronization** - Validates container time against external WorldTimeAPI
- **🏥 Health Tracking** - Stores all monitoring data in PostgreSQL database
- **📊 Real-Time Dashboard** - Live log viewer showing system status and metrics
- **📧 Alert System** - Email notifications via MailHog for failures
- **📁 Centralized Logging** - Shared log files with real-time monitoring

## 🚀 Choose Your Deployment Method

### **🐳 Option A: Docker Compose (Simple & Fast)**
**Best for:** Local development, testing, quick demos

#### Prerequisites
- Docker Desktop installed and running
- 4GB RAM available

#### 1. Deploy Everything
```bash
# One-click deployment with fresh builds
./docker-deploy.sh

# Or manual deployment
docker compose up -d --build
```

#### 2. Access Services
- **Web1:** http://localhost:8081
- **Web2:** http://localhost:8082
- **Monitoring Dashboard:** http://localhost:8090
- **Email Interface:** http://localhost:8025
- **Database:** localhost:5432

#### 3. Verify Monitoring System
```bash
# Check watchdog monitoring logs
docker compose logs -f watchdog

# Should see continuous monitoring cycles:
# - HTTP health checks every 60 seconds
# - Timezone validation against WorldTimeAPI
# - Database storage of monitoring results
```

#### 4. Test Alert System
```bash
# Stop a web server to trigger monitoring alert
docker compose stop web1

# Check email alert at http://localhost:8025 within 60 seconds
# Restart the server
docker compose start web1
```

#### 5. Stop System
```bash
# Simple stop
./docker-stop.sh

# Or manual stop
docker compose down
```

---

### **☸️ Option B: Kubernetes (Production-Ready)**
**Best for:** Production deployments, learning Kubernetes, scaling

#### Prerequisites
- Kubernetes cluster (minikube, Docker Desktop, or cloud)
- kubectl configured
- 4GB RAM available

#### 1. Start Kubernetes Cluster
```bash
# For local development (minikube)
minikube start

# Get cluster info
kubectl cluster-info
```

#### 2. Deploy Everything
```bash
# One-click deployment with custom image builds
cd k8s/
./deploy.sh

# System builds custom Docker images and deploys 6 services
```

#### 3. Access Services
```bash
# Get cluster IP (for minikube)
minikube ip

# Access URLs (replace <cluster-ip> with actual IP):
```
- **Web1:** http://`<cluster-ip>`:30081
- **Web2:** http://`<cluster-ip>`:30082
- **Monitoring Dashboard:** http://`<cluster-ip>`:30090
- **Email Interface:** http://`<cluster-ip>`:30825
- **Database:** `<cluster-ip>`:30432

#### 4. Verify Monitoring System
```bash
# Check all pods are running
kubectl get pods

# Monitor watchdog logs in real-time
kubectl logs -f deployment/watchdog

# Should see the same monitoring pattern as Docker Compose
```

#### 5. Test Kubernetes Features
```bash
# Scale web servers
kubectl scale deployment web1 --replicas=3
kubectl scale deployment web2 --replicas=2

# Watch pods self-heal (delete a pod, watch it restart)
kubectl delete pod <any-pod-name>
kubectl get pods -w
```

#### 6. Stop System
```bash
# Quick stop (preserves data)
./quick-stop.sh

# Complete cleanup (removes data)
./stop.sh
```

---

## � Understanding Your Monitoring System

### **🔄 How It Works (Both Docker & Kubernetes)**

1. **📦 6 Services Working Together:**
   - **web1, web2** - NGINX web servers serving content
   - **watchdog** - Python monitor checking web servers + timezone sync
   - **db** - PostgreSQL storing all monitoring history
   - **logviewer** - Flask dashboard showing real-time monitoring
   - **mailhog** - Email catcher for testing alerts

2. **⏱️ Monitoring Cycle (Every 60 seconds):**
   ```
   Watchdog → Checks web1:80 & web2:80 → Measures response time
          → Validates timezone with WorldTimeAPI → Compares container time
          → Stores results in PostgreSQL → Writes to shared logs
          → Dashboard reads shared logs → Displays real-time status
   ```

3. **📈 Data Flow:**
   ```
   Web Servers ← HTTP Checks ← Watchdog → Database Storage
                                      ↓
   Real-time Dashboard ← Shared Logs ← Log Files
   ```

### **🎯 Key Monitoring Features**

- **🌐 Web Server Health:** HTTP status codes, response times, availability %
- **⏰ Time Synchronization:** Container vs external time drift detection  
- **💾 Historical Data:** All monitoring results stored in PostgreSQL
- **📊 Live Dashboard:** Real-time log viewing and system status
- **📧 Instant Alerts:** Email notifications for failures and issues
- **📁 Centralized Logs:** All services write to shared storage

### **🔍 What You Can Monitor**

1. **System Health Dashboard** - http://localhost:8090 (Docker) or http://cluster-ip:30090 (K8s)
2. **Database Queries:**
   ```sql
   -- View recent health checks
   SELECT * FROM checks ORDER BY created_at DESC LIMIT 10;
   
   -- Check availability statistics
   SELECT * FROM performance_summary;
   
   -- Monitor system health metrics
   SELECT * FROM system_health;
   ```
3. **Email Alerts** - http://localhost:8025 (Docker) or http://cluster-ip:30825 (K8s)

---

## � Project Structure
```
multi-container-monitoring-system/
├── 🐳 Docker Compose Deployment
│   ├── docker-compose.yml          # Service orchestration
│   ├── docker-deploy.sh            # One-click Docker deployment
│   └── docker-stop.sh              # One-click Docker cleanup
├── ☸️ Kubernetes Deployment
│   └── k8s/
│       ├── deploy.sh               # One-click K8s deployment
│       ├── quick-stop.sh           # Fast K8s cleanup
│       ├── stop.sh                 # Complete K8s cleanup
│       └── *.yaml                  # All Kubernetes resources
├── 🔧 Configuration
│   ├── .env                        # Environment variables
│   └── db/init.sql                 # Database schema
├── 📊 Monitoring Services
│   ├── watchdog/                   # Python monitoring service
│   │   ├── Dockerfile
│   │   └── watchdog.py            # Main monitoring logic
│   └── logging/                    # Real-time dashboard
│       ├── Dockerfile
│       ├── log_api.py             # Flask API
│       └── index.html             # Web interface
└── 📚 Documentation
    ├── QUICKSTART.md              # This file
    ├── README.md                  # Complete system overview
    ├── ARCHITECTURE.md            # Technical architecture
    └── KUBERNETES_BEGINNERS_GUIDE.md  # Detailed learning guide
```

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
docker exec -it db psql -U monitoruser -d monitoring

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
