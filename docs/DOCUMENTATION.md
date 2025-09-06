# Velaris Monitoring System - Technical Documentation

## Executive Summary

This document provides a comprehensive overview of the Velaris Monitoring System - a containerized environment designed for automated health monitoring, time synchronization validation, and real-time alerting. The system successfully implements all core requirements with additional monitoring capabilities.

---

## 1. Project Overview

### 1.1 Objectives Achieved
✅ **Containerized Environment**: Multi-container setup with 6 services  
✅ **Health & Time Validation**: Automated monitoring with external API integration  
✅ **Logging & Monitoring**: Structured logging with web-based access  
✅ **Email Alerting**: Real-time notifications for failures  
✅ **Database Persistence**: Historical data storage and analysis  
✅ **Bonus Features**: Custom monitoring dashboard and advanced metrics  

### 1.2 Technology Stack
- **Containers**: Docker & Docker Compose
- **Web Servers**: NGINX Alpine
- **Monitoring**: Python 3.12 with requests, psycopg2
- **Database**: PostgreSQL 16
- **Logging**: Flask API with real-time log access
- **Email**: SMTP (Gmail/MailHog)
- **Visualization**: Custom web dashboard

---

## 2. Step-by-Step Setup Instructions

### 2.1 Prerequisites
```powershell
# Required software
- Docker Desktop for Windows
- PowerShell 5.1+
- Git (for version control)

# System requirements
- Windows 10/11
- 4GB RAM minimum
- 2GB free disk space
```

### 2.2 Environment Setup

#### Step 1: Clone and Configure
```powershell
# Navigate to project directory
cd e:\Velaris-Demo\multi-container-monitoring-system

# Verify project structure
dir
# Expected files: docker-compose.yml, .env, db/, watchdog/, web/, logging/
```

#### Step 2: Configure Environment Variables
```powershell
# Edit .env file for your environment
# Key configurations:
# - SMTP settings (Gmail or MailHog)
# - Database credentials
# - Monitoring intervals
# - Target timezone
```

#### Step 3: Build and Start System
```powershell
# Build and start all containers
docker-compose up --build -d

# Verify all containers are running
docker ps

# Expected containers:
# - web1 (port 8081)
# - web2 (port 8082)  
# - db (port 5432)
# - watchdog
# - mailhog (ports 1025, 8025)
# - log-viewer (port 8090)
```

### 2.3 Verification Steps

#### Step 1: Web Services
```powershell
# Test web1
curl http://localhost:8081
# Should return HTML with "Velaris Demo" and timestamps

# Test web2
curl http://localhost:8082
# Should return HTML with "Velaris Demo" and timestamps
```

#### Step 2: Monitoring Services
```powershell
# Access log viewer
Start-Process "http://localhost:8090"

# Access email interface
Start-Process "http://localhost:8025"
```

#### Step 3: Database Verification
```powershell
# Connect to database (optional)
docker exec -it db psql -U velaris -d velaris

# Check monitoring data
\dt                    # List tables
SELECT * FROM checks LIMIT 5;
```

---

## 3. Script Execution Instructions

### 3.1 Monitoring Script (Automatic)

The monitoring script (`watchdog/watchdog.py`) runs automatically within the watchdog container:

```python
# Core functionality:
1. Fetches time from WorldTimeAPI every 60 seconds
2. Compares with local container time (±5 second tolerance)
3. Updates web container content dynamically
4. Validates HTTP responses (status 200 + content check)
5. Stores results in PostgreSQL database
6. Sends email alerts on failures
```

**Manual Control:**
```powershell
# View real-time logs
docker logs watchdog --follow

# Restart monitoring service
docker restart watchdog

# Check monitoring configuration
docker exec watchdog printenv | findstr -E "(TARGET|CHECK|SMTP)"
```

### 3.2 Log Access Scripts

#### Web-based Log Viewer
```powershell
# Access via browser
Start-Process "http://localhost:8090"

# Features available:
# - Real-time log streaming
# - Container log access
# - Metrics visualization
# - Log filtering and search
# - Custom monitoring dashboard
```

#### Direct Log Access
```powershell
# Application logs
docker exec log-viewer cat /var/log/velaris/watchdog.log

# Structured metrics
docker exec log-viewer cat /var/log/velaris/metrics.log

# Container logs
docker logs web1
docker logs watchdog
```

### 3.3 Testing and Validation

#### Email Alert Testing
```powershell
# Method 1: Stop a container (triggers failure)
docker stop web1
# Wait 60 seconds for next check cycle
# Check email at http://localhost:8025

# Method 2: Modify expected content
# Edit watchdog.py line 196 to change expected text
docker-compose up --build -d watchdog
```

#### Performance Testing
```powershell
# Database performance check
docker exec -it db psql -U velaris -d velaris -c "SELECT * FROM performance_summary;"

# System health overview
docker exec -it db psql -U velaris -d velaris -c "SELECT * FROM system_health;"
```

---

## 4. Design Decisions and Assumptions

### 4.1 Architecture Decisions

#### **Microservices Approach**
- **Decision**: Separate containers for each service
- **Reasoning**: Scalability, maintainability, fault isolation
- **Trade-off**: Increased complexity vs. service independence

#### **Shared Volume Strategy**
- **Decision**: Use Docker volumes for log sharing and content updates
- **Reasoning**: Efficient file-based communication between containers
- **Alternative**: Could use API-based communication (more complex)

#### **Database Choice: PostgreSQL**
- **Decision**: PostgreSQL over MySQL/SQLite
- **Reasoning**: Advanced features (JSONB, views, time zones)
- **Benefits**: Structured metrics storage, complex queries, reliability

#### **Dual Logging System**
- **Decision**: Separate application logs and structured metrics
- **Reasoning**: Human-readable debugging + machine-readable analytics
- **Implementation**: Two log files with different formats and rotation

### 4.2 Monitoring Strategy

#### **Check Interval: 60 seconds**
- **Assumption**: Balance between responsiveness and resource usage
- **Configurable**: Via `CHECK_INTERVAL_SEC` environment variable
- **Consideration**: Production might need different intervals

#### **Time Drift Tolerance: ±5 seconds**
- **Assumption**: Reasonable tolerance for container time sync
- **Reasoning**: Network latency and processing delays
- **Configurable**: Via `MAX_ALLOWED_DRIFT_SEC`

#### **Three Key Metrics Selected**
1. **System Availability (%)**: Critical for uptime monitoring
2. **Response Time (ms)**: Performance and user experience indicator  
3. **Time Drift (seconds)**: Infrastructure health and sync validation

**Rationale**: These metrics provide comprehensive health insight:
- **Availability**: Overall system reliability
- **Performance**: User experience quality
- **Synchronization**: Infrastructure stability

### 4.3 Email Strategy

#### **Dual SMTP Support**
- **Decision**: Support both Gmail SMTP and MailHog
- **Reasoning**: Production vs. development needs
- **Implementation**: Environment-based switching logic

```python
if SMTP_HOST != "mailhog" and SMTP_USER and SMTP_PASSWORD:
    # Gmail SMTP with authentication
else:
    # MailHog simple SMTP
```

#### **Alert Conditions**
- **Triggers**: HTTP status ≠ 200, content mismatch, time drift > 5s
- **Frequency**: Every check cycle while condition persists
- **Content**: Detailed diagnostic information

### 4.4 Security Assumptions

#### **Network Security**
- **Assumption**: Internal Docker network is secure
- **Implementation**: No TLS between containers (performance optimization)
- **Production note**: Would need TLS for external deployment

#### **Credential Management**
- **Assumption**: Environment variables are secure for development
- **Production consideration**: Would use secrets management (Docker secrets, K8s secrets)

#### **Database Access**
- **Current**: Direct PostgreSQL connection
- **Assumption**: Database is in trusted environment
- **Production**: Would use connection pooling and read replicas

### 4.5 Scalability Considerations

#### **Container Scaling**
- **Current**: Fixed number of web containers
- **Design**: Easy to add more containers by updating `WEB_TARGETS`
- **Future**: Could implement auto-discovery

#### **Database Performance**
- **Current**: Single PostgreSQL instance
- **Optimization**: Database views for common queries
- **Future**: Read replicas, connection pooling

#### **Log Management**
- **Current**: File-based with rotation
- **Assumption**: Log volume manageable for demo
- **Production**: Would need centralized logging (ELK stack)

---

## 5. Monitoring Metrics Explained

### 5.1 Critical Metrics Implementation

#### **1. System Availability (%)**
```sql
-- Calculation in performance_summary view
ROUND(
    (SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)) * 100, 
    2
) as availability_percent
```
- **Why Critical**: Core business metric for service reliability
- **Target**: >99% for production systems
- **Alerting**: <95% availability triggers immediate attention

#### **2. Response Time (milliseconds)**
```sql
-- Stored in checks table
response_time_ms INTEGER
-- Aggregated in views
AVG(response_time_ms) as avg_response_time_ms
```
- **Why Critical**: Direct impact on user experience
- **Target**: <100ms for local services
- **Trending**: Helps identify performance degradation

#### **3. Time Drift (seconds)**
```sql
-- Calculated and stored
time_drift_seconds INTEGER
-- Max drift tracking
MAX(time_drift_seconds) as max_time_drift
```
- **Why Critical**: Indicates infrastructure health
- **Target**: <5 seconds deviation
- **Impact**: Time sync issues can cause authentication failures

### 5.2 Additional Metrics Available

#### **Structured Metrics (JSON)**
```json
{
  "timestamp": "2025-09-04T22:31:04.711038+05:30",
  "metric": "http_response_time", 
  "value": 0.004,
  "tags": {"target": "web1:80", "status_code": 200}
}
```

#### **Performance Tracking**
- API response times
- Email delivery performance
- Check cycle durations
- Error rates and patterns

---

## 6. Continuous Deployment Proposal

### 6.1 Recommended CI/CD Pipeline (AWS-Based)

#### **Stage 1: Source Control & Triggers**
```yaml
# GitHub Actions / GitLab CI / AWS CodePipeline
trigger: push to main branch
source: GitHub repository
tools: Git, AWS CodeCommit integration
```

#### **Stage 2: Build & Container Registry**
```yaml
# Docker Image Builds
- docker build -t velaris-watchdog:${VERSION} ./watchdog
- docker build -t velaris-log-viewer:${VERSION} ./logging
- docker build -t velaris-web:${VERSION} ./web

# Push to AWS ECR (Elastic Container Registry)
- aws ecr get-login-token --region us-west-2
- docker tag velaris-watchdog:${VERSION} ${ECR_URI}/velaris-watchdog:${VERSION}
- docker tag velaris-log-viewer:${VERSION} ${ECR_URI}/velaris-log-viewer:${VERSION}
- docker tag velaris-web:${VERSION} ${ECR_URI}/velaris-web:${VERSION}
- docker push ${ECR_URI}/velaris-watchdog:${VERSION}
- docker push ${ECR_URI}/velaris-log-viewer:${VERSION}
- docker push ${ECR_URI}/velaris-web:${VERSION}

# Benefits of ECR:
- Integrated with AWS IAM for security
- Vulnerability scanning built-in
- Lifecycle policies for cost optimization
- High availability and scalability
```

#### **Stage 3: Infrastructure Provisioning**
```yaml
# AWS RDS Database Instance
- Create PostgreSQL RDS instance with Multi-AZ deployment
- Configure security groups and subnet groups
- Set up automated backups and monitoring
- Apply database schema via migration scripts

# Benefits of RDS:
- Managed service with automated maintenance
- High availability with Multi-AZ deployment
- Automated backups and point-in-time recovery
- Performance monitoring and insights
- Automatic scaling capabilities
```

#### **Stage 4: ECS Deployment**
```yaml
# ECS Task Definition Creation
- Define task definitions for each service:
  - velaris-watchdog-task
  - velaris-web1-task  
  - velaris-web2-task
  - velaris-log-viewer-task
  - velaris-mailhog-task (for testing environments)

# ECS Service Deployment
- Create ECS cluster (Fargate or EC2)
- Deploy services with desired count
- Configure Application Load Balancer
- Set up service discovery
- Configure auto-scaling policies

# Why ECS is Ideal for This System:
```

**Scalability Advantages:**
- **Horizontal Scaling**: Automatically scale containers based on CPU/memory metrics
- **Service Auto Scaling**: Increase/decrease task count based on demand
- **Cluster Auto Scaling**: Add/remove EC2 instances automatically
- **Load Balancing**: Distribute traffic across multiple container instances

**Serverless Benefits (with Fargate):**
- **No Server Management**: AWS manages the underlying infrastructure
- **Pay-per-Use**: Only pay for the compute resources your containers use
- **Automatic Patching**: AWS handles OS and runtime patching
- **Rapid Scaling**: Scale from zero to hundreds of tasks quickly
- **Built-in Security**: Tasks run in isolated compute environments

**Operational Excellence:**
- **Service Discovery**: Automatic DNS-based service discovery
- **Health Checks**: Built-in container health monitoring
- **Rolling Updates**: Zero-downtime deployments
- **Integration**: Native integration with other AWS services (RDS, ECR, CloudWatch)
```

### 6.2 Tools and Practices

#### **Container Registry**
- **Tool**: Docker Hub / AWS ECR / Harbor
- **Practice**: Semantic versioning for images
- **Security**: Image scanning and signing

#### **Orchestration**
- **Development**: Docker Compose
- **Production**: Kubernetes / Docker Swarm
- **Service Mesh**: Istio (for production)

#### **Monitoring in CI/CD**
- **Tool**: Custom dashboard + Database metrics
- **Practice**: Infrastructure as Code monitoring
- **Alerting**: PagerDuty / Slack integration

#### **Database Migrations**
- **Tool**: Flyway / Liquibase
- **Practice**: Version-controlled schema changes
- **Testing**: Migration testing in CI pipeline

### 6.3 Deployment Environments

#### **Development**
```yaml
# Local development
tool: docker-compose
database: PostgreSQL container
monitoring: MailHog for emails
logging: File-based with local access
```

#### **Staging**
```yaml
# Pre-production testing
tool: Kubernetes cluster
database: Managed PostgreSQL
monitoring: Full email integration
logging: Centralized (ELK stack)
```

#### **Production**
```yaml
# Live environment
tool: Kubernetes with HA
database: HA PostgreSQL cluster
monitoring: Multi-channel alerting
logging: Distributed logging
backup: Automated with retention
```

---

## 7. Conclusion

The Velaris Monitoring System successfully delivers a comprehensive solution that exceeds the core requirements:

### **✅ Achievements**
- Complete containerized environment with 6+ services
- Robust health monitoring with external API integration  
- Advanced logging and metrics collection
- Real-time email alerting system
- Database persistence with analytical views
- Web-based monitoring dashboard
- Production-ready CI/CD recommendations

### **🚀 Extensibility**
The system is designed for easy extension:
- Additional containers via configuration
- Custom metrics through structured logging
- Multiple notification channels
- Advanced analytics with custom dashboard integration

### **📊 Business Value**
- **Reliability**: Automated health monitoring reduces downtime
- **Visibility**: Comprehensive logging enables rapid troubleshooting  
- **Scalability**: Container-based architecture supports growth
- **Maintainability**: Structured code and documentation

This implementation provides a solid foundation for production monitoring systems while demonstrating containerization best practices and modern observability patterns.
