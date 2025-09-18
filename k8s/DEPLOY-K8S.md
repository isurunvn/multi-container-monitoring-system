# Kubernetes Deployment Guide

This directory contains all Kubernetes configurations and deployment scripts for the Multi-Container Monitoring System with **Kubernetes Ingress** support.

## 🌐 Ingress Architecture Overview

This deployment uses **Kubernetes Ingress** with NGINX Ingress Controller to provide path-based routing through a single entry point. This replaces NodePort services with a more production-ready approach.

### **Architecture Flow:**
```
Internet → Minikube IP → NGINX Ingress Controller → Path-based Routing → Services
```

### **Path-based Routing:**
- `http://<minikube-ip>/web1` → web1-service:80
- `http://<minikube-ip>/web2` → web2-service:80  
- `http://<minikube-ip>/log-monitor` → logviewer-service:80
- `http://<minikube-ip>/mailhog` → mailhog-service:8025

### **Benefits over NodePort:**
✅ **Production Ready** - Single entry point, standard HTTP/HTTPS ports  
✅ **Better Security** - No multiple high ports, centralized traffic control  
✅ **Easier Management** - One ingress resource, simpler firewall rules

---

## 🚀 Quick Commands

### Deploy Everything:
```bash
./deploy.sh         # Complete deployment with automatic ingress setup
```

### Stop Everything:
```bash
./stop.sh           # Interactive - asks about deleting data
./quick-stop.sh     # Quick - preserves persistent volumes
```

### Manual Ingress Setup:
```bash
./setup-ingress.sh  # Setup ingress manually if needed
```

### Generate Configuration:
```bash
./generate-k8s-config.sh  # Generate ConfigMap/Secret from .env
```

## 📁 Files Overview

### 🤖 **Deployment Scripts:**
- **`deploy.sh`** - Complete deployment automation with automatic ingress setup
- **`setup-ingress.sh`** - Dedicated ingress configuration script
- **`stop.sh`** - Interactive cleanup (asks about data deletion)
- **`quick-stop.sh`** - Quick cleanup (preserves data)
- **`generate-k8s-config.sh`** - Generates ConfigMap and Secret from .env file

### ⚙️ **Resource Definitions:**

**Ingress & Networking:**
- `ingress.yaml` - NGINX Ingress Controller with path-based routing
- All services use ClusterIP (internal networking via ingress)

**Database:**
- `db-deployment.yaml` - PostgreSQL 16 with auto-initialization
- `db-service.yaml` - Database service (ClusterIP)
- `db-pvc.yaml` - 1GB persistent storage for database

**Web Services:**
- `web1-deployment.yaml` + `web1-service.yaml` - First web server (ClusterIP)
- `web2-deployment.yaml` + `web2-service.yaml` - Second web server (ClusterIP)
- `web-content-pvc.yaml` - Shared 100MB storage for web content

**Monitoring:**
- `watchdog-deployment.yaml` - Custom monitoring service
- `logviewer-deployment.yaml` + `logviewer-service.yaml` - Dashboard (ClusterIP)
- `monitoring-logs-pvc.yaml` - 500MB shared storage for logs

**Email Testing:**
- `mailhog-deployment.yaml` + `mailhog-service.yaml` - Email catcher (ClusterIP)

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

### **Ingress URLs (Production-Ready):**
After deployment, access services via path-based routing:
- **Web1:** http://`<minikube-ip>`/web1
- **Web2:** http://`<minikube-ip>`/web2
- **Live Dashboard:** http://`<minikube-ip>`/log-monitor
- **Email UI:** http://`<minikube-ip>`/mailhog

Get minikube IP: `minikube ip`

---

## 🔧 Ingress Configuration Details

### **Automatic Deployment Process:**
The deployment automatically:
1. **Enables NGINX Ingress** on Minikube
2. **Converts Services** from NodePort to ClusterIP
3. **Creates Ingress Resource** with path-based routing
4. **Waits for Ready State** before showing URLs

### **Manual Ingress Setup:**
```bash
# Enable ingress addon
minikube addons enable ingress

# Apply the ingress configuration
kubectl apply -f ingress.yaml

# Or run the setup script
./setup-ingress.sh
```

### **Ingress Resource Configuration:**
- Uses `nginx.ingress.kubernetes.io/rewrite-target: /$2` to strip path prefix
- Uses `pathType: ImplementationSpecific` for regex support
- All services use ClusterIP (internal networking)
- Everything deployed in `monitoring` namespace

---

## 🔍 Verification & Troubleshooting

### **Check Ingress Status:**
```bash
# View ingress resource
kubectl get ingress -n monitoring

# Describe ingress for details
kubectl describe ingress monitoring-ingress -n monitoring

# Check ingress controller pods
kubectl get pods -n ingress-nginx
```

### **Common Issues & Solutions:**

1. **Ingress not ready**: Wait for NGINX controller to be ready
2. **404 errors**: Check path rewrite rules and service names
3. **Can't reach services**: Verify services are ClusterIP type

### **Debug Commands:**
```bash
# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Test service connectivity
kubectl run test --image=busybox --rm -it -- wget -qO- web1-service:80

# Check service endpoints
kubectl get endpoints -n monitoring
```

## 💡 Tips & Best Practices

### **Getting Started:**
- **First time:** Run `minikube start` before deployment
- **Logs:** Use `kubectl logs -f deployment/<service-name> -n monitoring`
- **Debug:** Use `kubectl describe pod <pod-name> -n monitoring`
- **Status:** Use `kubectl get all -n monitoring` to see everything

### **Ingress Management:**
- **Test URLs:** Use `curl http://$(minikube ip)/web1` to test services
- **SSL Ready:** Can easily add TLS certificates for HTTPS
- **Scaling:** Services can be scaled without affecting ingress routing
- **Monitoring:** All traffic flows through single ingress point for easy monitoring

### **Production Considerations:**
- **Authentication:** Add ingress annotations for auth requirements
- **Rate Limiting:** Configure traffic policies via ingress annotations  
- **Multiple Hosts:** Easy to add different domains to same ingress
- **Load Balancing:** Automatic load balancing across multiple pod replicas

---

## 🚀 Next Steps After Deployment

Once Ingress is working, you can easily add:
- **SSL/TLS certificates** for HTTPS encryption
- **Authentication** via ingress annotations (Basic Auth, OAuth)
- **Rate limiting** and traffic policies
- **Multiple hosts** for different domains
- **Monitoring dashboards** for ingress traffic analysis
