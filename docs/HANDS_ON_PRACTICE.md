# 🎯 Kubernetes Hands-On Practice Guide

## 🎮 Welcome to Your Kubernetes Playground!

This guide contains fun exercises and experiments you can do with your working Kubernetes system to deepen your understanding. Think of it as your personal Kubernetes laboratory! 🧪

---

## 🚀 Level 1: Basic Exploration (Beginner)

### **Exercise 1.1: Pod Inspector**
Let's explore your running pods like a detective! 🕵️‍♂️

```bash
# See all your pods
kubectl get pods

# Pick any pod and investigate it deeply
kubectl describe pod <pod-name>

# Go inside a pod and look around (like entering a house)
kubectl exec -it <pod-name> -- /bin/sh

# Once inside, explore:
ls -la                    # What files are here?
env                       # What environment variables do I have?
ps aux                    # What programs are running?
exit                      # Leave the pod
```

**🎯 Learning Goal:** Understand that pods are like small computers with their own filesystem and processes.

### **Exercise 1.2: Service Network Detective**
Let's see how services connect to pods! 🌐

```bash
# See all services and their endpoints
kubectl get services -o wide

# See which pods each service connects to
kubectl get endpoints

# Test internal connectivity (from inside watchdog pod)
kubectl exec -it deployment/watchdog -- ping web1-service
kubectl exec -it deployment/watchdog -- ping web2-service
kubectl exec -it deployment/watchdog -- ping db-service
```

**🎯 Learning Goal:** Services provide stable network addresses that automatically find the right pods.

### **Exercise 1.3: Storage Explorer**
Let's understand how storage works! 💾

```bash
# See your persistent volumes
kubectl get pv
kubectl get pvc

# Check what's in your shared storage
kubectl exec deployment/watchdog -- ls -la /var/log/monitoring/
kubectl exec deployment/logviewer -- ls -la /var/log/monitoring/

# Write a test file from one pod and read it from another
kubectl exec deployment/watchdog -- sh -c 'echo "Hello from watchdog!" > /var/log/monitoring/test.txt'
kubectl exec deployment/logviewer -- cat /var/log/monitoring/test.txt
```

**🎯 Learning Goal:** Understand how multiple pods can share the same storage.

---

## 🎯 Level 2: Intermediate Experiments (Getting Confident)

### **Exercise 2.1: The Great Pod Restart Experiment**
Let's see Kubernetes self-healing in action! 🔄

```bash
# First, note your current pods
kubectl get pods

# Kill a pod (don't worry, Kubernetes will bring it back!)
kubectl delete pod <any-pod-name>

# Watch what happens (Kubernetes creates a new pod automatically)
kubectl get pods -w

# Check if your websites still work
curl http://192.168.49.2:30081
curl http://192.168.49.2:30082
```

**🎯 Learning Goal:** Kubernetes automatically replaces failed pods to maintain your desired state.

### **Exercise 2.2: Scale Your Web Servers**
Let's run multiple copies of your web servers! 📈

```bash
# Scale web1 to 3 replicas
kubectl scale deployment web1 --replicas=3

# Watch the new pods being created
kubectl get pods -w

# See how the service distributes traffic to all 3 pods
kubectl get endpoints web1-service

# Test load balancing (run this multiple times)
for i in {1..10}; do
  kubectl exec deployment/watchdog -- curl -s web1-service | grep -o "nginx.*"
done
```

**🎯 Learning Goal:** Kubernetes can easily scale applications and automatically load balance traffic.

### **Exercise 2.3: Configuration Experiment**
Let's modify configuration without rebuilding containers! ⚙️

```bash
# Look at current config
kubectl get configmap monitoring-config -o yaml

# Edit the configmap
kubectl edit configmap monitoring-config

# Add a new environment variable:
# NEW_SETTING: "Hello from Kubernetes!"

# Restart a deployment to pick up the new config
kubectl rollout restart deployment watchdog

# Check if the pod got the new environment variable
kubectl exec deployment/watchdog -- env | grep NEW_SETTING
```

**🎯 Learning Goal:** Configuration can be changed without rebuilding container images.

---

## 🏆 Level 3: Advanced Challenges (Kubernetes Ninja)

### **Exercise 3.1: The Resource Monitor**
Let's see how much CPU and memory your pods use! 📊

```bash
# Install metrics server (if not already installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Wait a minute, then check resource usage
kubectl top pods
kubectl top nodes

# Add resource limits to a deployment
kubectl edit deployment web1

# Add this to the container spec:
# resources:
#   requests:
#     cpu: 100m
#     memory: 128Mi
#   limits:
#     cpu: 200m
#     memory: 256Mi
```

**🎯 Learning Goal:** Kubernetes can monitor and limit resource usage.

### **Exercise 3.2: The Health Check Master**
Let's add health checks to your applications! 🏥

```bash
# Edit your web1 deployment to add health checks
kubectl edit deployment web1

# Add this to the container spec:
# livenessProbe:
#   httpGet:
#     path: /
#     port: 80
#   initialDelaySeconds: 30
#   periodSeconds: 10
# readinessProbe:
#   httpGet:
#     path: /
#     port: 80
#   initialDelaySeconds: 5
#   periodSeconds: 5

# Watch the deployment update
kubectl rollout status deployment web1

# See the health check status
kubectl describe pod <web1-pod-name>
```

**🎯 Learning Goal:** Health checks help Kubernetes know when your applications are working properly.

### **Exercise 3.3: The Rolling Update**
Let's update your application with zero downtime! 🔄

```bash
# Build a new version of your web server with a custom message
# (This is just a simulation - we'll change the image)

# Update web1 to use a different nginx image
kubectl set image deployment/web1 nginx=nginx:1.21

# Watch the rolling update happen
kubectl rollout status deployment web1

# See the update history
kubectl rollout history deployment web1

# Rollback if needed
kubectl rollout undo deployment web1
```

**🎯 Learning Goal:** Kubernetes can update applications without downtime.

---

## 🎪 Fun Challenges & Experiments

### **Challenge 1: The Communication Test**
Can you make all your services talk to each other? 🗣️

```bash
# From watchdog pod, test connectivity to all services
kubectl exec deployment/watchdog -- sh -c '
  echo "Testing web1..." && curl -s web1-service | head -1
  echo "Testing web2..." && curl -s web2-service | head -1  
  echo "Testing database..." && nc -zv db-service 5432
  echo "Testing logviewer..." && curl -s logviewer-service | head -1
'
```

### **Challenge 2: The Log File Race**
Can you create a file in one pod and immediately read it from another? 🏃‍♂️

```bash
# Terminal 1: Watch files in logviewer
kubectl exec deployment/logviewer -- sh -c 'watch ls -la /var/log/monitoring/'

# Terminal 2: Create files in watchdog  
kubectl exec deployment/watchdog -- sh -c 'for i in {1..5}; do echo "File $i created at $(date)" > /var/log/monitoring/race-$i.txt; sleep 1; done'
```

### **Challenge 3: The Environment Variable Hunt**
Find all the environment variables in your pods! 🔍

```bash
# Create a script to check env vars in all pods
for pod in $(kubectl get pods -o name); do
  echo "=== $pod ==="
  kubectl exec $pod -- env | grep -E "(DB_|WEB_|POSTGRES_)" | sort
  echo
done
```

### **Challenge 4: The Storage Size Calculator**
How much space is each pod using? 📏

```bash
# Check storage usage in each pod
kubectl exec deployment/db -- df -h
kubectl exec deployment/watchdog -- df -h /var/log/monitoring/
kubectl exec deployment/logviewer -- df -h /var/log/monitoring/
```

---

## 🧪 Advanced Experiments

### **Experiment 1: Create a New Service**
Add a simple HTTP service to your cluster! 🆕

```bash
# Create a simple HTTP server pod
kubectl run simple-server --image=httpd --port=80

# Expose it as a service
kubectl expose pod simple-server --port=80 --target-port=80 --type=NodePort

# Find the external port
kubectl get service simple-server

# Test it
curl http://192.168.49.2:<node-port>
```

### **Experiment 2: Network Policy Playground**
Control network traffic between pods! 🛡️

```yaml
# Create network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

```bash
# Apply the policy (this will block all traffic!)
kubectl apply -f network-policy.yaml

# Test that services don't work
curl http://192.168.49.2:30081  # Should fail

# Remove the policy
kubectl delete networkpolicy deny-all
```

### **Experiment 3: Secret Management**
Create and use your own secrets! 🔐

```bash
# Create a secret manually
kubectl create secret generic my-secret \
  --from-literal=username=admin \
  --from-literal=password=supersecret

# Create a pod that uses this secret
kubectl run secret-test --image=busybox --command -- sleep 3600

# Add the secret to the pod (edit the deployment)
kubectl edit pod secret-test

# Add this to the container spec:
# env:
# - name: SECRET_USERNAME
#   valueFrom:
#     secretKeyRef:
#       name: my-secret
#       key: username

# Test that the pod can read the secret
kubectl exec secret-test -- env | grep SECRET
```

---

## 🎯 Learning Challenges

### **Challenge A: The Troubleshooter**
Break something and fix it! 🔧

```bash
# Break 1: Delete a service
kubectl delete service web1-service
# Can you access web1 now? How do you fix it?

# Break 2: Fill up storage
kubectl exec deployment/watchdog -- sh -c 'dd if=/dev/zero of=/var/log/monitoring/big-file bs=1M count=100'
# What happens? How do you clean up?

# Break 3: Wrong image
kubectl set image deployment/web2 nginx=nginx:nonexistent
# What error do you see? How do you fix it?
```

### **Challenge B: The Performance Tester**
How fast is your system? 🏎️

```bash
# Test 1: How many requests can your web server handle?
kubectl exec deployment/watchdog -- sh -c 'for i in {1..100}; do curl -s web1-service > /dev/null && echo -n "."; done'

# Test 2: How quickly does a pod start?
time kubectl delete pod <web1-pod-name>
# Time how long it takes for a new pod to become ready

# Test 3: Storage performance
kubectl exec deployment/watchdog -- sh -c 'time dd if=/dev/zero of=/var/log/monitoring/test-speed bs=1M count=10'
```

### **Challenge C: The Multi-Environment Setup**
Create dev and prod environments! 🏗️

```bash
# Create namespaces
kubectl create namespace dev
kubectl create namespace prod

# Deploy to dev
kubectl apply -f k8s/ --namespace=dev

# Deploy to prod  
kubectl apply -f k8s/ --namespace=prod

# See both environments
kubectl get pods --all-namespaces

# Test both environments
kubectl port-forward -n dev service/web1-service 8080:80
kubectl port-forward -n prod service/web1-service 8081:80
```

---

## 📚 Self-Study Projects

### **Project 1: Add Monitoring Dashboard**
Install Prometheus and Grafana to monitor your cluster!

### **Project 2: Implement Auto-scaling**
Make your web servers automatically scale based on CPU usage!

### **Project 3: Add Ingress Controller**
Replace NodePort services with proper domain names!

### **Project 4: CI/CD Pipeline**
Automatically deploy when you push code changes!

### **Project 5: Backup System**
Create automated backups of your database!

---

## 🎓 Knowledge Check

After doing these exercises, you should be able to answer:

1. **What happens when a pod dies?**
2. **How do services find pods?**
3. **Why do we need persistent volumes?**
4. **What's the difference between ConfigMaps and Secrets?**
5. **How does Kubernetes achieve zero-downtime deployments?**
6. **What are the benefits of running multiple replicas?**
7. **How do health checks help with reliability?**
8. **What happens when you scale a deployment?**

---

## 🏆 Your Kubernetes Journey

**Beginner Level (✅ Completed):**
- Understanding basic concepts
- Deploying applications
- Managing storage and configuration

**Intermediate Level (🎯 Working On):**
- Scaling and load balancing
- Health checks and monitoring
- Network policies and security

**Advanced Level (🚀 Future Goals):**
- Service mesh (Istio)
- Operators and CRDs
- Multi-cluster deployments
- GitOps workflows

---

## 🎮 Make It Fun!

**Kubernetes Bingo:** Check off concepts as you master them!
- [ ] Deployed a pod
- [ ] Scaled a deployment  
- [ ] Created a service
- [ ] Used persistent storage
- [ ] Applied a ConfigMap
- [ ] Created a Secret
- [ ] Performed a rolling update
- [ ] Added health checks
- [ ] Monitored resources
- [ ] Debugged a failed pod

**Achievement Unlocked:** 🏆 When you can explain Kubernetes to someone else, you've truly mastered it!

---

Remember: The best way to learn Kubernetes is by breaking things and fixing them. Don't be afraid to experiment - you have a complete working system to play with! 🚀

Happy learning! 🎉
