# Kubernetes Deployment Scripts

This directory contains all Kubernetes configurations and deployment scripts for the Multi-Container Monitoring System.

## 🚀 Quick Commands

### Deploy Everything:
```bash
./deploy.sh
```

### Stop Everything:
```bash
./stop.sh           # Interactive - asks about deleting data
./quick-stop.sh     # Quick - preserves persistent volumes
```

### Generate Configuration:
```bash
./generate-k8s-config.sh
```

## 📁 Files Overview

### 🤖 **Deployment Scripts:**
- **`deploy.sh`** - Complete deployment automation (builds images, deploys, waits for readiness)
- **`stop.sh`** - Interactive cleanup (asks about data deletion)
- **`quick-stop.sh`** - Quick cleanup (preserves data)
- **`generate-k8s-config.sh`** - Generates ConfigMap and Secret from .env file

### ⚙️ **Resource Definitions:**

**Database:**
- `db-deployment.yaml` - PostgreSQL 16 with auto-initialization
- `db-service.yaml` - Database service (port 30432)
- `db-pvc.yaml` - 1GB persistent storage for database

**Web Services:**
- `web1-deployment.yaml` + `web1-service.yaml` - First web server (port 30081)
- `web2-deployment.yaml` + `web2-service.yaml` - Second web server (port 30082)
- `web-content-pvc.yaml` - Shared 100MB storage for web content

**Monitoring:**
- `watchdog-deployment.yaml` - Custom monitoring service
- `logviewer-deployment.yaml` + `logviewer-service.yaml` - Dashboard (port 30090)
- `monitoring-logs-pvc.yaml` - 500MB shared storage for logs

**Email Testing:**
- `mailhog-deployment.yaml` + `mailhog-service.yaml` - Email catcher (port 30825)

### 📋 **Generated Files:**
- `monitoring-configmap-generated.yaml` - Auto-generated from .env
- `monitoring-secret-generated.yaml` - Auto-generated from .env

## 🔧 Usage Examples

### Deploy and Monitor:
```bash
./deploy.sh
kubectl get pods -w
kubectl logs -f deployment/watchdog
```

### Stop with Data Preservation:
```bash
./quick-stop.sh
```

### Complete Cleanup:
```bash
./stop.sh
# Choose 'y' when asked about persistent volumes
```

### Redeploy After Stop:
```bash
./deploy.sh
# Data will be restored if PVCs were preserved
```

## 🌐 Access URLs

After deployment, access services at:
- **Web1:** http://`<minikube-ip>`:30081
- **Web2:** http://`<minikube-ip>`:30082
- **Dashboard:** http://`<minikube-ip>`:30090
- **Email UI:** http://`<minikube-ip>`:30825
- **Database:** `<minikube-ip>`:30432

Get minikube IP: `minikube ip`

## 💡 Tips

- **First time:** Run `minikube start` before deployment
- **Logs:** Use `kubectl logs -f deployment/<service-name>` 
- **Debug:** Use `kubectl describe pod <pod-name>`
- **Status:** Use `kubectl get all` to see everything
