# Docker Container Monitoring System


A lightweight, cost-effective monitoring and alerting solution for Dockerized applications. Built with Docker Compose, this system provides real-time metrics, automated alerting via AWS SES, and a live web dashboard—without the overhead of enterprise monitoring tools.

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/) [![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/) [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/) [![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![AWS](https://img.shields.io/badge/AWS_SES-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/ses/)

---


##  Overview

This project demonstrates a **production-ready approach to monitoring containerized applications** when you have limited budget and want full control over your monitoring stack. Instead of expensive enterprise solutions, it uses Docker's native capabilities combined with shell scripting and Python to provide:

- **Real-time monitoring** of CPU, memory, and latency
- **Automated alerting** with smart cooldown periods
- **Live web dashboard** for visualization
- **Load testing** capabilities to validate performance
- **Cost-effective** AWS SES integration for notifications

### Use Case

Perfect for:

- Small teams running internal applications
- Development and staging environments
- Learning DevOps monitoring fundamentals
- Cost-conscious production deployments
- Applications with 100-500 users



---

##  Features

### Monitoring Dashboard

- **Real-time metrics** updated every 30 seconds
- **Terminal-style UI** with color-coded alerts
-  **Historical data** tracking in log files
-  **Auto-refresh** for continuous monitoring

### Intelligent Alerting

- **Multi-level severity** (Critical, Warning, Info)
-  **Cooldown periods** to prevent alert fatigue
-  **Email notifications** via AWS SES
-  **Configurable thresholds** for all metrics

### Performance Testing

- **Load generation** with multiple stress levels
-  **Multi-threaded** request simulation
-  **Configurable load patterns** (low, medium, high, extreme)
-  **Realistic traffic** across multiple endpoints

### Production-Ready Patterns

-  **Docker Compose** orchestration
-  **Health checks** and service dependencies
-  **Volume persistence** for logs and data
-  **Custom networking** with DNS resolution
-  **Resource limits** to prevent resource exhaustion
-  **Restart policies** for high availability

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                   Docker Compose Network                         │
│                                                                   │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   Flask App  │────▶│  PostgreSQL  │     │    Monitor   │    │
│  │  (Port 8000) │     │   Database   │     │   Dashboard  │    │
│  └──────┬───────┘     └──────────────┘     │  (Port 8001) │    │
│         │                                    └──────┬───────┘    │
│         │                                           │            │
│  ┌──────▼───────┐                          ┌───────▼────────┐   │
│  │     Load     │                          │     Alert      │   │
│  │  Generator   │                          │    Service     │   │
│  └──────────────┘                          └────────┬───────┘   │
│                                                      │           │
└──────────────────────────────────────────────────────┼───────────┘
                                                       │
                                              ┌────────▼────────┐
                                              │    AWS SES      │
                                              │  (Email Alerts) │
                                              └─────────────────┘
```

### Data Flow

1. **Flask App** handles HTTP requests and database operations
2. **Monitor Service** collects metrics via `docker stats` command
3. **Logs** are written to mounted volumes (persistent storage)
4. **Alert Service** parses logs and sends notifications when thresholds are exceeded
5. **Load Generator** simulates user traffic for stress testing
6. **AWS SES** delivers email alerts to configured recipients

### Technology Stack

|Component|Technology|Purpose|
|---|---|---|
|**Application**|Flask + Python 3.11|Web application framework|
|**Database**|PostgreSQL 15|Data persistence|
|**Monitoring**|Shell scripting + Docker CLI|Metrics collection|
|**Dashboard**|Flask + HTML/CSS|Visualization|
|**Alerts**|Python + Boto3|Notification system|
|**Load Testing**|Python + Threading|Performance testing|
|**Orchestration**|Docker Compose|Container management|
|**Email**|AWS SES|Alert delivery|

---

## 🎬 Demo

### Live Monitoring Dashboard

<img width="1363" height="971" alt="image" src="https://github.com/user-attachments/assets/c375fa33-83fd-42aa-a719-6641226cd7d4" />


 _Real-time container metrics with color-coded status indicators_

### Alert Email Example



 _Critical alert notification for container down event_

<img width="1548" height="559" alt="image" src="https://github.com/user-attachments/assets/c906e6e3-4c35-4048-8814-7e800407ea48" />


### Load Testing in Action

<img width="1333" height="404" alt="image" src="https://github.com/user-attachments/assets/4c1beb5c-175d-4ed9-a12e-fbc9f51b8cf9" />




---

## 📦 Prerequisites

### Required Software

- **Docker Desktop** 20.10+ 
- **Docker Compose** 2.0+ (included with Docker Desktop)
- **AWS Account** with SES access 
- **AWS CLI** configured 
- **Git** for version control

### AWS SES Setup

1. **Create AWS Account** (if you don't have one)
2. **Verify email addresses** in AWS SES
3. **Create IAM user** with SES permissions
4. **Generate access keys** for programmatic access
5. **Configure AWS CLI** with credentials


---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/docker-monitoring-system.git
cd docker-monitoring-system
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your AWS credentials and email addresses
nano .env
```

**Required variables:**

```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
SENDER_EMAIL=verified-sender@yourdomain.com
RECIPIENT_EMAILS=recipient1@email.com,recipient2@email.com
```

### 3. Start the System

```bash
# Build and start all services
docker-compose up --build -d

# Verify all containers are running
docker-compose ps
```

### 4. Access the Dashboard

Open your browser and navigate to:

- **Application:** http://localhost:8000
- **Monitoring Dashboard:** http://localhost:8001

### 5. Test the System

```bash
# Test application endpoints
curl http://localhost:8000/health

# Check monitoring logs
tail -f logs/metrics.log

# View service logs
docker-compose logs -f monitor
```

---

##  Configuration

### Environment Variables

All configuration is managed through the `.env` file:

#### AWS Configuration

```bash
AWS_ACCESS_KEY_ID          # IAM user access key
AWS_SECRET_ACCESS_KEY      # IAM user secret key
AWS_REGION                 # AWS region (e.g., us-east-1)
```

#### Email Configuration

```bash
SENDER_EMAIL               # Verified sender email in SES
RECIPIENT_EMAILS           # Comma-separated recipient emails
```

#### Alert Thresholds

```bash
CPU_THRESHOLD=80           # Alert when CPU exceeds this %
MEMORY_THRESHOLD=80        # Alert when memory exceeds this %
ALERT_COOLDOWN=300         # Seconds between repeated alerts
CHECK_INTERVAL=30          # Seconds between metric checks
```

#### Application Settings

```bash
DB_HOST=db                 # Database hostname (container name)
DB_PORT=5432              # PostgreSQL port
DB_NAME=monitoring_db      # Database name
DB_USER=postgres          # Database username
DB_PASSWORD=postgres      # Database password
```

### Resource Limits

Modify `docker-compose.yml` to adjust container resources:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'          # Maximum CPU cores
      memory: 512M         # Maximum memory
    reservations:
      cpus: '0.5'          # Guaranteed CPU
      memory: 256M         # Guaranteed memory
```

### Load Testing Levels

Edit `STRESS_LEVEL` in `docker-compose.yml`:

|Level|Threads|Requests/sec|Use Case|
|---|---|---|---|
|`low`|2|5|Normal operations|
|`medium`|5|20|Peak hours simulation|
|`high`|10|50|Stress testing|
|`extreme`|20|100|Failure scenario testing|

---

## Monitoring Metrics

### Collected Metrics

#### Container Health

- **Uptime Status:** UP / DOWN
- **HTTP Response Code:** 200 (healthy) / 500 (error)
- **Container Restarts:** Count and timestamps

#### Performance Metrics

- **CPU Usage:** Percentage of allocated CPU
- **Memory Usage:** Current usage / limit (percentage)
- **Response Latency:** Time to complete HTTP request
- **Request Rate:** Requests per second (from load generator)

#### Database Metrics

- **Connection Status:** Connected / Failed
- **Query Performance:** Response times
- **Record Count:** Database size tracking

### Metric Storage

All metrics are stored in three log files:

```bash
logs/
├── metrics.log    # CPU, memory, latency data
├── status.log     # Container status and HTTP codes
└── report.log     # Detailed formatted reports
```

### Log Format

**metrics.log example:**

```
2024-01-13 10:30:00 | CPU: 45.2% | Memory: 52.1% | Latency: 0.234s
2024-01-13 10:30:30 | CPU: 78.5% | Memory: 58.3% | Latency: 0.891s
```

**status.log example:**

```
2024-01-13 10:30:00 | Container: UP | HTTP: 200
2024-01-13 10:30:30 | Container: UP | HTTP: 200
```

---

## Alert System

### Alert Severity Levels

#### 🔴 Critical (Immediate Action Required)

- Container is DOWN
- HTTP 5xx errors
- CPU usage > 80%
- Memory usage > 90%

**Response time:** Within minutes

#### 🟡 Warning (Monitor Closely)

- Memory usage > 60%
- Response latency > 1 second
- CPU sustained > 60%

**Response time:** Within 30 minutes

#### ℹ️ Info (Awareness)

- Container restart events
- Configuration changes
- Deployment notifications

**Response time:** Review in next business hours

### Alert Cooldown

To prevent alert fatigue, the system implements a **cooldown period** (default: 5 minutes).

**How it works:**

1. Alert condition detected (e.g., CPU > 80%)
2. Email sent immediately
3. Timer starts (5 minutes)
4. During cooldown: No alerts sent even if condition persists
5. After cooldown: If condition still exists, new alert sent

**Example:**

```
10:00:00 - CPU hits 85% → Email sent
10:01:00 - CPU still 85% → No email (cooldown)
10:04:59 - CPU still 85% → No email (cooldown)
10:05:00 - Cooldown expires
10:05:30 - CPU still 85% → Email sent again
```

### Email Alert Format

Alerts include:

- **Severity level** (Critical/Warning)
- **Specific issue** description
- **Current metrics** values
- **Timestamp** of detection
- **Recent history** (last 10 log entries)
- **Recommended actions**

---

## Load Testing

### Starting Load Tests

```bash
# Low load (development testing)
docker-compose up -d load

# Medium load (peak hours simulation)
# Edit docker-compose.yml: STRESS_LEVEL: medium
docker-compose up -d load

# High load (stress testing)
# Edit docker-compose.yml: STRESS_LEVEL: high
docker-compose up -d load
```

### Load Testing Configuration

**Stress levels defined in `load/stress.py`:**

```python
STRESS_CONFIG = {
    'low': {
        'threads': 2,
        'requests_per_second': 5,
        'delay': 0.2
    },
    'medium': {
        'threads': 5,
        'requests_per_second': 20,
        'delay': 0.05
    },
    'high': {
        'threads': 10,
        'requests_per_second': 50,
        'delay': 0.02
    },
    'extreme': {
        'threads': 20,
        'requests_per_second': 100,
        'delay': 0.01
    }
}
```

### Endpoints Tested

The load generator randomly hits these endpoints:

- `/` - Home page
- `/health` - Health check
- `/cpu-test` - CPU-intensive task
- `/memory-test` - Memory allocation test
- `/db-test` - Database query test

### Monitoring Load Impact

```bash
# Watch real-time container stats
docker stats webapp

# Watch metrics in dashboard
open http://localhost:8001

# Follow monitoring logs
tail -f logs/metrics.log
```

---

## Project Structure

```
docker-monitoring-system/
│
├── app/                          # Flask application
│   ├── app.py                   # Main application logic
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile.app           # Application container definition
│
├── monitor/                      # Monitoring service
│   ├── monitor.sh               # Bash monitoring script
│   ├── dashboard.py             # Web dashboard application
│   └── Dockerfile.monitor       # Monitor container definition
│
├── alert/                        # Alert service
│   ├── alert.py                 # Alert logic and SES integration
│   └── Dockerfile.alert         # Alert container definition
│
├── load/                         # Load testing service
│   ├── stress.py                # Load generator script
│   └── Dockerfile.load          # Load container definition
│
├── logs/                         # Generated logs (not in git)
│   ├── metrics.log              # Performance metrics
│   ├── status.log               # Container status
│   └── report.log               # Detailed reports
│
├── docker-compose.yml            # Service orchestration
├── .env.example                  # Environment template
├── .gitignore                    # Git exclusions
├── README.md                     # This file


```

### Key Files Explained

|File|Purpose|
|---|---|
|`docker-compose.yml`|Defines all services, networks, and volumes|
|`.env`|Stores sensitive configuration (not in git)|
|`app/app.py`|Flask web application with test endpoints|
|`monitor/monitor.sh`|Collects metrics using Docker CLI|
|`monitor/dashboard.py`|Web UI for visualization|
|`alert/alert.py`|Parses logs and sends email alerts|
|`load/stress.py`|Generates HTTP traffic for testing|

---

## Usage

### Common Commands

#### Starting and Stopping

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d webapp

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Restart a service
docker-compose restart monitor
```

#### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service with follow
docker-compose logs -f monitor

# Last 100 lines
docker-compose logs --tail 100 webapp

# Monitor system logs
tail -f logs/metrics.log
```

#### Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health

# CPU stress test
curl http://localhost:8000/cpu-test

# Database test
curl http://localhost:8000/db-test

# Combined test (all resources)
curl http://localhost:8000/combined-test
```

#### Inspecting Containers

```bash
# View running containers
docker-compose ps

# Container resource usage
docker stats

# Enter container shell
docker-compose exec webapp bash

# Test database connection
docker-compose exec webapp python -c "
from app import get_db_connection
conn = get_db_connection()
print('Connected!')
"
```

#### Load Testing

```bash
# Start low load
docker-compose up -d load

# Stop load
docker-compose stop load

# Change load level (edit docker-compose.yml first)
docker-compose up -d load

# Watch load impact
watch -n 2 'docker stats --no-stream webapp'
```

### Accessing Services

|Service|URL|Purpose|
|---|---|---|
|**Flask App**|http://localhost:8000|Main application|
|**Health Check**|http://localhost:8000/health|Application status|
|**Dashboard**|http://localhost:8001|Monitoring UI|
|**Metrics API**|http://localhost:8001/api/metrics|JSON metrics|

---


### Tools

- **Docker** for containerization
- **Python** for scripting
- **PostgreSQL** for data persistence
- **AWS SES** for email delivery
- **VS Code** with Docker extension for development

---

## Learning Outcomes

By building and understanding this project, you'll learn:

### Docker & Orchestration

- Multi-container application architecture
- Docker Compose configuration
- Service dependencies and health checks
- Volume management and persistence
- Network configuration
- Resource limits and constraints

### Monitoring & Observability

- Metrics collection strategies
- Log aggregation patterns
- Dashboard development
- Real-time data visualization
- Historical data tracking

### Alerting & Incident Response

- Alert threshold configuration
- Severity level classification
- Cooldown period implementation
- Email notification systems
- Incident documentation

### DevOps Practices

- Infrastructure as Code (IaC)
- Configuration management
- Environment variable management
- Secrets handling
- Documentation best practices

### Cloud Integration

- AWS SES setup and configuration
- IAM user management
- Cloud service integration
- Cost-conscious architecture decisions

---

Built as part of the **DevOps Bootcamp (Nov 2025 Cohort)**


