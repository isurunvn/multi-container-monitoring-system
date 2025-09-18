# Multi-Container Monitoring System - Deployment Guide

This project can be deployed using either **Docker Compose** or **Kubernetes**. Choose the approach that fits your needs.

## 🐳 Docker Compose Approach (Simple & Quick)

**Best for:** Local development, testing, simple deployments

### Quick Start:
```bash
# Deploy everything (builds images from scratch)
./docker-deploy.sh

# Stop everything (with cleanup options)
./docker-stop.sh
```

### Manual Commands:
```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f
```

### Access URLs:
- **Web1:** http://localhost:8081
- **Web2:** http://localhost:8082  
- **Log Viewer:** http://localhost:8090
- **MailHog UI:** http://localhost:8025
- **Database:** localhost:5432

---

## ☸️ Kubernetes Approach (Production-Ready)

**Best for:** Production deployments, scaling, cloud environments

### Prerequisites:
```bash
# Start minikube (for local testing)
minikube start

# Or use any Kubernetes cluster
```

### Quick Start:
```bash
# Deploy everything
cd k8s/
./deploy.sh

# Stop everything
./stop.sh           # Interactive cleanup (asks about data)
./quick-stop.sh     # Quick cleanup (preserves data)
```

### Access Services:
```bash
# Get minikube IP
minikube ip

# Access URLs (replace <minikube-ip> with actual IP):
# - Web1: http://<minikube-ip>:30081
# - Web2: http://<minikube-ip>:30082
# - Log Viewer: http://<minikube-ip>:30090
# - MailHog UI: http://<minikube-ip>:30825
# - Database: <minikube-ip>:30432
```

---

## 📋 Comparison

| Feature | Docker Compose | Kubernetes |
|---------|----------------|------------|
| **Setup Complexity** | Simple | Moderate |
| **Resource Usage** | Lower | Higher |
| **Scaling** | Limited | Excellent |
| **Production Ready** | Basic | Advanced |
| **Port Access** | localhost:port | minikube-ip:nodeport |
| **Persistence** | Docker volumes | PersistentVolumes |
| **Service Discovery** | Container names | DNS names |

---

## 🚀 Quick Commands Summary

### Docker Compose:
```bash
./docker-deploy.sh    # Start everything
./docker-stop.sh      # Stop everything
docker compose logs -f watchdog  # View watchdog logs
```

### Kubernetes:
```bash
cd k8s/
./deploy.sh           # Deploy everything
./stop.sh             # Stop everything (interactive)
./quick-stop.sh       # Quick stop (preserves data)
kubectl logs -f deployment/watchdog  # View watchdog logs
```

---

## 📁 Project Structure

```
├── docker-deploy.sh       # Docker Compose deployment script
├── docker-stop.sh         # Docker Compose stop script
├── docker-compose.yml     # Docker Compose configuration
├── k8s/                   # Kubernetes configurations
│   ├── deploy.sh          # Kubernetes deployment script
│   └── *.yaml             # Kubernetes resource files
├── watchdog/              # Monitoring service
├── logging/               # Log viewer service
├── web/                   # Web server configurations
└── docs/                  # Documentation
```

Choose your preferred deployment method and get started! 🎉
