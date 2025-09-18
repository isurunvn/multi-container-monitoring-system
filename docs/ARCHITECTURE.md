# Multi-Container Monitoring System - Complete Architecture Guide

This document provides comprehensive architectural views for both Docker Compose and Kubernetes deployments of the monitoring system.

---

## 🐳 Docker Compose Architecture

### **System Overview - Docker Environment**

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

---

## ☸️ Kubernetes Architecture

### **System Overview - Production-Style Ingress Configuration**

```
🌍 Internet (Your Computer)
    |
    | Single Entry Point: 192.168.49.2
    |
┌───▼─────────────────────────────────────────────────────────────┐
│  🎮 Kubernetes Cluster - Modern Ingress Architecture            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                🌐 NGINX Ingress Controller                  │ │
│  │              (Production-Style Routing)                     │ │
│  │                                                             │ │
│  │  ┌─────────────┬─────────────┬─────────────────────────┐   │ │
│  │  │  /web1/*    │   /web2/*   │    /log-monitor/*       │   │ │
│  │  │             │             │                         │   │ │
│  │  │     ▼       │      ▼      │           ▼             │   │ │
│  │  └─────────────┴─────────────┴─────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │              │                    │                  │
│  ┌────────▼──────┐ ┌─────▼──────┐ ┌───────────▼──────────────┐   │
│  │🌐 Web1 Service│ │🌐 Web2     │ │📊 LogViewer Service      │   │
│  │(ClusterIP)    │ │Service     │ │(ClusterIP)               │   │
│  │Port: 80       │ │(ClusterIP) │ │Port: 80                  │   │
│  │               │ │Port: 80    │ │                          │   │
│  └────────┬──────┘ └─────┬──────┘ └───────────┬──────────────┘   │
│           │              │                    │                  │
│  ┌────────▼──────┐ ┌─────▼──────┐ ┌───────────▼──────────────┐   │
│  │🏠 Web1 Pod    │ │🏠 Web2 Pod │ │🏠 LogViewer Pod          │   │
│  │NGINX Server   │ │NGINX Server│ │Flask Dashboard           │   │
│  │Port: 80       │ │Port: 80    │ │Port: 80                  │   │
│  └───────────────┘ └────────────┘ └──────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │         👮‍♂️ Watchdog Service (Background Monitor)           │ │
│  │         (ClusterIP - Internal Communication Only)            │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────┐   │ │
│  │  │  🏠 Watchdog Pod                                    │   │ │
│  │  │  • Python Monitor Service                          │   │ │
│  │  │  • Checks: web1-service, web2-service via DNS      │   │ │
│  │  │  • Timezone sync with WorldTimeAPI                 │   │ │
│  │  │  • Stores data in PostgreSQL                       │   │ │
│  │  │  📝 Writes Reports to Shared Storage ──────────────┼───┐│ │
│  │  └─────────────────────────────────────────────────────┘   ││ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                               │ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │           💾 Shared Storage Room                            │ │
│  │           (monitoring-logs-pvc)                             │ │
│  │                                                             │ │
│  │    📄 watchdog.log  📄 metrics.log                         │ │
│  │                                                             │ │
│  │    📊 LogViewer Pod reads from here ◄──────────────────────┼─┘
│  └─────────────────────────────────────────────────────────────┘
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              🗄️ Database System                        │   │
│  │                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────────────────┐ │   │
│  │  │ 🚪 DB Service   │    │     🏠 Database Pod         │ │   │
│  │  │ Port: 5432      │◄───┤     PostgreSQL              │ │   │
│  │  │                 │    │                             │ │   │
│  │  └─────────────────┘    └─────────────┬───────────────┘ │   │
│  │                                       │                 │   │
│  │  ┌─────────────────────────────────────▼──────────────┐  │   │
│  │  │          💾 Database Storage                       │  │   │
│  │  │          (postgres-pvc)                           │  │   │
│  │  │          📊 Monitoring data stored here           │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │        📧 MailHog System (NodePort Exception)           │   │
│  │        ⚠️ Cannot use Ingress due to asset path issues   │   │
│  │                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────────────────┐ │   │
│  │  │ 🚪 Mail Service │    │     🏠 MailHog Pod          │ │   │
│  │  │ (NodePort)      │◄───┤     Email Catcher           │ │   │
│  │  │ Port: 1025/8025 │    │     Web UI (Legacy App)     │ │   │
│  │  │ External: 31026 │    │                             │ │   │
│  │  └─────────────────┘    └─────────────────────────────┘ │   │
│  │                                                         │   │
│  │  💡 WHY NODEPORT? MailHog's web interface expects       │   │
│  │     to run at root path (/) and has hardcoded          │   │
│  │     relative paths for CSS/JS assets. When served      │   │
│  │     under /mailhog, assets load from wrong URLs        │   │
│  │     causing broken styling. NodePort provides          │   │
│  │     root path access: http://ip:31026                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           ⚙️ Configuration Management                   │   │
│  │                                                         │   │
│  │  📝 ConfigMap (monitoring-config)                      │   │
│  │  ├── DB_HOST=db-service                                │   │
│  │  ├── WEB1_URL=http://web1-service:80                   │   │
│  │  └── WEB2_URL=http://web2-service:80                   │   │
│  │                                                         │   │
│  │  🔐 Secret (monitoring-secret)                         │   │
│  │  ├── DB_PASSWORD=•••••••••                             │   │
│  │  └── DB_USER=•••••••••                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 System Components (Both Deployments)

### 🌐 **Web Services Layer**
- **WEB1 & WEB2**: NGINX containers serving dynamic content
  - **Docker**: Ports 8081, 8082 | **Kubernetes**: Ingress paths /web1, /web2
  - ClusterIP services with Ingress routing (production-style)
  - Shared volume for content updates
  - Container-specific identification
  - Real-time timestamp display

### 🔍 **Monitoring Layer**
- **WATCHDOG**: Core monitoring service
  - Python-based health checker
  - 60-second check intervals
  - Multi-dimensional validation
  - **Docker**: Direct container communication | **Kubernetes**: Service discovery via DNS

### 📊 **Data Layer**
- **DATABASE**: PostgreSQL with enhanced schema
  - **Docker**: Port 5432 | **Kubernetes**: Internal service + PersistentVolume
  - Check results persistence
  - Performance metrics storage
  - Historical trend analysis

### 📧 **Communication Layer**
- **MAILHOG**: Email testing service
  - **Docker**: Port 8025 | **Kubernetes**: NodePort 31026 (legacy app exception)
  - Cannot use Ingress due to hardcoded asset paths in web interface
  - SMTP server simulation
  - Web UI for email inspection (requires root path deployment)

### 🎛️ **Observability Layer**
- **LOG-VIEWER**: Real-time log access
  - **Docker**: Port 8090 | **Kubernetes**: Ingress path /log-monitor
  - ClusterIP service with Ingress routing
  - Flask API backend with absolute path routing
  - Web-based interface (ingress-compatible)
  - Container log aggregation
  - Custom monitoring dashboard

---

## 🔄 Complete Data Flow (Both Environments)

### **1. Monitoring Cycle**
```
🌍 External Time API ← Watchdog → Web1:80 & Web2:80 (Health Checks)
                          ↓
📊 Time Comparison → Content Update → Response Time Measurement
                          ↓
💾 Database Storage → 📁 Log Files → 📧 Email Alerts (if failure)
                          ↓
📱 Real-time Dashboard ← Log Viewer ← Shared Storage
```

### **2. Docker Compose Flow**
```
1. 🌍 User visits http://localhost:8081
2. 🐳 Docker routes to web1 container
3. 📝 NGINX serves content with timestamp
4. 👮‍♂️ Watchdog monitors via container name resolution
5. 💾 Data stored in PostgreSQL volume
6. 📊 Log viewer reads shared volume
7. 🌍 User views dashboard at http://localhost:8090
```

### **3. Modern Kubernetes Flow (Ingress-Based)**
```
1. 🌍 User visits http://192.168.49.2/web1
2. 🌐 NGINX Ingress Controller receives request
3. 🔀 Ingress routes /web1/* to web1-service:80
4. 🏠 ClusterIP service routes to web1-pod:80
5. 👮‍♂️ Watchdog monitors via internal DNS (web1-service.monitoring.svc.cluster.local)
6. 💾 Data stored in PersistentVolume
7. 📊 Log viewer reads shared PVC
8. 🌍 User views dashboard at http://192.168.49.2/log-monitor

Special Case - MailHog:
🌍 User visits http://192.168.49.2:31026 → NodePort → mailhog-pod:8025
(Direct routing needed for asset compatibility)
```

---

## 🌐 Network Architecture Comparison

### **🐳 Docker Compose Networking**
```
External World → Docker Bridge Network → Containers
                        │
                        ├─► web1:80 (published as 8081)
                        ├─► web2:80 (published as 8082)
                        ├─► logviewer:80 (published as 8090)
                        ├─► mailhog:8025 (published as 8025)
                        └─► db:5432 (published as 5432)

Service Discovery: Container names (web1, web2, db, mailhog, logviewer)
```

### **☸️ Modern Kubernetes Networking (Ingress + NodePort Hybrid)**
```
🌐 External World
    │
    ├─► 192.168.49.2/web1 ──────► NGINX Ingress Controller
    ├─► 192.168.49.2/web2 ──────►        │
    ├─► 192.168.49.2/log-monitor ►       │
    │                                    │
    │   ┌─────────────────────────────────▼─────────────────────────────┐
    │   │              Path-Based Routing                              │
    │   │  /web1/* → web1-service:80 → web1-pod:80                    │
    │   │  /web2/* → web2-service:80 → web2-pod:80                    │
    │   │  /log-monitor/* → logviewer-service:80 → logviewer-pod:80   │
    │   └──────────────────────────────────────────────────────────────┘
    │
    └─► 192.168.49.2:31026 ──────► MailHog NodePort Service (Legacy)
                                          │
                                          └─► mailhog-pod:8025

Internal Service Discovery: 
├── web1-service.monitoring.svc.cluster.local:80
├── web2-service.monitoring.svc.cluster.local:80  
├── logviewer-service.monitoring.svc.cluster.local:80
├── mailhog-service.monitoring.svc.cluster.local:8025
└── db-service.monitoring.svc.cluster.local:5432
```

**🎯 Why This Hybrid Approach?**
- **Ingress Services**: Clean URLs, production-ready, path-based routing
- **NodePort for MailHog**: Legacy app with hardcoded asset paths incompatible with subpaths

---

## 💾 Storage Architecture Comparison

### **🐳 Docker Compose Storage**
```
Host Machine
├── 💾 Named Volumes
│   ├── postgres_data → /var/lib/postgresql/data (database persistence)
│   ├── web_content → /usr/share/nginx/html (shared web content)
│   └── monitoring_logs → /var/log/monitoring (shared logs)
└── 📁 Bind Mounts
    └── ./db/init.sql → /docker-entrypoint-initdb.d/init.sql
```

### **☸️ Kubernetes Storage**
```
Cluster Storage
├── 💾 PersistentVolumeClaims
│   ├── postgres-pvc (1GB) → Database Pod
│   ├── web-content-pvc (100MB) → Web Pods
│   └── monitoring-logs-pvc (500MB) → Watchdog + LogViewer Pods
└── 📝 ConfigMaps & Secrets
    ├── monitoring-config → Environment variables
    └── monitoring-secret → Encrypted credentials
```

---

## ⚙️ Configuration Management

### **🐳 Docker Compose**
```
📄 .env file → docker-compose.yml → Container environment variables
              ↓
🐳 All containers share same .env configuration
🔒 Secrets stored as plain text in .env (development only)
```

### **☸️ Kubernetes**
```
📄 .env file → generate-k8s-config.sh → ConfigMap & Secret YAML files
              ↓
📝 ConfigMap: Non-sensitive configuration (DB_HOST, URLs)
🔐 Secret: Sensitive data (passwords, keys) - base64 encoded
              ↓
🏠 Pods consume both via environment variables
```

---

## 🚀 Deployment Timeline Comparison

### **🐳 Docker Compose Deployment**
```
⏰ 0s  → docker compose up -d
⏰ 10s → PostgreSQL container starting
⏰ 15s → Database initialization with init.sql
⏰ 20s → Web containers starting (nginx:alpine)
⏰ 25s → Watchdog building custom image
⏰ 30s → Log viewer building custom image
⏰ 35s → MailHog starting
⏰ 40s → All services ready!
```

### **☸️ Kubernetes Deployment**
```
⏰ 0s  → generate-k8s-config.sh + kubectl apply
⏰ 5s  → PVCs, ConfigMaps, Secrets created
⏰ 15s → PostgreSQL pod starting + image pull
⏰ 30s → Web pods starting + nginx image pull
⏰ 45s → Watchdog pod + custom image build/pull
⏰ 60s → Log viewer pod + custom image build/pull
⏰ 70s → MailHog pod starting
⏰ 75s → All services ready + self-healing active!
```

---

## 🔒 Security Considerations

### **Both Environments:**
- **Email Configuration**: Gmail SMTP for production, MailHog for testing
- **Data Protection**: Credentials via environment variables
- **Container Isolation**: Services separated in their own containers/pods
- **Log Management**: Rotation to prevent disk overflow

### **Docker Compose Security:**
- ✅ Good for development and testing
- ⚠️ .env file contains plain text secrets
- ✅ Internal network isolation between containers
- ✅ Host-level firewall protection

### **Kubernetes Security:**
- ✅ Production-ready security model
- ✅ Secrets are base64 encoded and encrypted at rest
- ✅ RBAC for pod-to-pod communication
- ✅ Network policies for micro-segmentation
- ✅ Service accounts for fine-grained permissions

---

## 🎯 Architecture Benefits

### **🐳 Docker Compose Advantages:**
- ✅ **Simplicity**: One command deployment
- ✅ **Development Speed**: Fast iteration and testing
- ✅ **Resource Efficiency**: Lower overhead
- ✅ **Debugging**: Easy log access and container inspection
- ✅ **Local Development**: Perfect for development workflows

### **☸️ Kubernetes Advantages:**
- ✅ **Production Ready**: Enterprise-grade orchestration
- ✅ **High Availability**: Automatic pod restart and healing
- ✅ **Scalability**: Easy horizontal scaling
- ✅ **Service Discovery**: Built-in DNS and load balancing
- ✅ **Rolling Updates**: Zero-downtime deployments
- ✅ **Configuration Management**: Secure secrets handling
- ✅ **Monitoring Integration**: Built-in health checks and metrics

### **Why Both Matter:**
This dual-deployment approach teaches you the progression from development (Docker Compose) to production (Kubernetes) - exactly how real-world applications evolve! 🚀
