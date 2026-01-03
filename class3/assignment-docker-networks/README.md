# Class 3 Assignment: Docker Networks - Isolated Application Stacks

## Assignment Overview

This assignment demonstrates Docker network isolation by running two separate application stacks on the same machine, testing both cross-network communication and network isolation.

## Stacks Deployed

### Stack 1: Flask + MongoDB
- **Application**: Flask (Python web framework)
- **Database**: MongoDB 7.0 (NoSQL document database)
- **Purpose**: RESTful API with visitor tracking

### Stack 2: WordPress + MySQL
- **Application**: WordPress (PHP CMS)
- **Database**: MySQL 8.0 (Relational database)
- **Purpose**: Content management system

## Docker Concepts Covered

### Network Isolation
- **Custom Bridge Networks**: User-defined networks providing automatic DNS resolution
- **Network Isolation**: Containers on different networks cannot communicate
- **Service Discovery**: Containers on the same network can reach each other by name
- **DNS Resolution**: Docker provides automatic name-to-IP mapping within custom networks

### Multi-Stack Architecture
- **Stack Separation**: Running multiple independent applications on same host
- **Database Diversity**: Working with both NoSQL (MongoDB) and SQL (MySQL)
- **Security**: Using network isolation for multi-tenant environments
- **Real-world Scenario**: Multiple development teams sharing infrastructure

## Project Structure

```
assignment-docker-networks/
flask-app/
 app.py              # Flask application with MongoDB
 requirements.txt    # Python dependencies
 Dockerfile          # Flask image definition
 .dockerignore       # Exclude files
 README.md              # This file
```

## Part A: Same Network Setup

### Objective
Run both stacks on the same network (network-one) to demonstrate cross-stack communication.

### Commands Used

```bash
# Create single network
docker network create network-one

# Run Flask + MongoDB stack
docker run -d --name flask-db --network network-one -e MONGO_INITDB_DATABASE=flaskdb mongo:7.0
docker run -d --name flask-app --network network-one -e MONGO_HOST=flask-db -p 5000:5000 yourusername/flask-mongodb-test:v1.0

# Run WordPress + MySQL stack
docker run -d --name wordpress-db --network network-one -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=wordpress mysql:8.0
docker run -d --name wordpress-app --network network-one -e WORDPRESS_DB_HOST=wordpress-db -p 8080:80 wordpress:latest
```

### Test Results

**From Flask Container:**
```bash
docker exec -it flask-app /bin/bash
ping -c 3 flask-db          # SUCCESS - same network
ping -c 3 wordpress-db      # SUCCESS - same network (cross-stack)
```

**Observations:**
- All 4 containers on network-one can communicate
- Flask app can ping WordPress database (cross-stack communication works)
- DNS resolution works for all container names
- Both applications function normally

**Security Concern:** Cross-stack communication on same network means Flask could potentially access WordPress database, which may not be desired in production.

## Part B: Different Networks Setup (Isolation)

### Objective
Run stacks on separate networks (network-one and network-two) to demonstrate isolation.

### Commands Used

```bash
# Create two separate networks
docker network create network-one
docker network create network-two

# Flask stack on network-one
docker run -d --name flask-db --network network-one -e MONGO_INITDB_DATABASE=flaskdb mongo:7.0
docker run -d --name flask-app --network network-one -e MONGO_HOST=flask-db -p 5000:5000 yourusername/flask-mongodb-test:v1.0

# WordPress stack on network-two
docker run -d --name wordpress-db --network network-two -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=wordpress mysql:8.0
docker run -d --name wordpress-app --network network-two -e WORDPRESS_DB_HOST=wordpress-db -p 8080:80 wordpress:latest
```

### Test Results

**From Flask Container (network-one):**
```bash
docker exec -it flask-app /bin/bash
ping -c 3 flask-db          # SUCCESS - same network
ping -c 3 wordpress-db      # FAILURE - different network (isolated!)
```

**From WordPress Container (network-two):**
```bash
docker exec -it wordpress-app /bin/bash
ping -c 3 wordpress-db      # SUCCESS - same network
ping -c 3 flask-db          # FAILURE - different network (isolated!)
```

**Observations:**
- Containers can only communicate within their own network
- Flask stack completely isolated from WordPress stack
- DNS resolution fails across networks
- Both applications still function independently
- Network isolation provides security boundary

## Key Learnings

### 1. Why Custom Networks Are Important

**Better than Default Bridge:**
- Automatic DNS resolution (use container names, not IPs)
- Better isolation from other containers
- More control over container communication
- Easier service discovery for microservices

**Default bridge network limitations:**
- No automatic DNS resolution (must use IPs)
- All containers share same network (security risk)
- Cannot control which containers communicate

### 2. How Network Isolation Works

**Container Network Namespace:**
- Each container has its own network stack
- Custom networks create isolated network namespaces
- Docker engine manages routing between networks
- Containers on different networks cannot see each other

**DNS Resolution:**
- Docker provides embedded DNS server (127.0.0.11)
- DNS only resolves names within same network
- Cross-network DNS queries fail (isolation enforced)

### 3. Real-World Use Cases

**Multi-Tenant SaaS Applications:**
- Each customer's stack on separate network
- Prevents data leakage between tenants
- Maintains security and compliance requirements

**Development Teams:**
- Team A: Frontend + API on network-one
- Team B: Analytics + Database on network-two
- Teams share infrastructure without interference

**Environment Separation:**
- Development network: dev-network
- Staging network: staging-network
- Production network: prod-network

**Microservices Architecture:**
- Frontend tier: frontend-network
- Backend tier: backend-network
- Database tier: db-network
- Services only connect to networks they need

### 4. MongoDB vs MySQL Learning

**MongoDB (NoSQL):**
- Document-based storage (JSON-like)
- Flexible schema (no predefined structure)
- Horizontal scaling (sharding)
- Good for: Unstructured data, rapid development

**MySQL (SQL):**
- Table-based storage (rows and columns)
- Rigid schema (predefined structure)
- ACID compliance (strong consistency)
- Good for: Structured data, complex queries, transactions

**Both work seamlessly with Docker:**
- Official images available
- Easy configuration via environment variables
- Volume support for data persistence

## Technical Implementation Details

### Flask Application Features
- RESTful API with health checks
- MongoDB connection with error handling
- Visitor tracking (demonstrates database writes)
- Beautiful web interface showing network info
- Environment variable configuration

### Docker Networking
- Custom bridge networks (user-defined)
- Automatic DNS resolution
- Network isolation enforcement
- Port mapping for external access

### Database Connectivity
- Flask connects to MongoDB via hostname (flask-db)
- WordPress connects to MySQL via hostname (wordpress-db)
- No hardcoded IPs required
- Connection parameters via environment variables

## Screenshots



## Commands Reference

### Network Management
```bash
# Create network
docker network create <network-name>

# List networks
docker network ls

# Inspect network
docker network inspect <network-name>

# Remove network
docker network rm <network-name>

# Connect container to network
docker network connect <network-name> <container-name>

# Disconnect container from network
docker network disconnect <network-name> <container-name>
```

### Container Management
```bash
# Run container on specific network
docker run -d --name <name> --network <network-name> <image>

# Check container network
docker inspect <container-name> | grep -A 20 NetworkSettings

# Execute command in container
docker exec -it <container-name> <command>

# View container logs
docker logs <container-name>
```

### Testing Commands
```bash
# Ping from inside container
docker exec -it <container> ping -c 3 <target>

# DNS lookup from inside container
docker exec -it <container> nslookup <target>

# Test HTTP endpoints
curl http://localhost:5000/health
curl http://localhost:8080
```

## Comparison: Same Network vs Isolated Networks

| Aspect | Part A (Same Network) | Part B (Isolated Networks) |
|--------|----------------------|---------------------------|
| **Communication** | Full cross-stack | Only within stack |
| **DNS Resolution** | All containers | Only same network |
| **Security** | Lower (shared access) | Higher (isolated) |
| **Use Case** | Development/testing | Production/multi-tenant |
| **Complexity** | Simpler setup | Better architecture |
| **Best Practice** | Not recommended | Recommended |

## Best Practices Learned

1. **Always use custom networks** instead of default bridge
2. **Isolate different applications** on separate networks
3. **Use container names** for service discovery (not IPs)
4. **Apply principle of least privilege** - only connect necessary containers
5. **Document network topology** for team understanding
6. **Test network isolation** before deploying to production
7. **Use environment variables** for configuration
8. **Implement health checks** for all services

## Troubleshooting Guide

### Problem: Container cannot connect to database
```bash
# Check if both on same network
docker network inspect <network-name>

# Verify database is running
docker ps | grep <db-name>

# Check database logs
docker logs <db-name>

# Test DNS resolution
docker exec -it <app> nslookup <db-name>
```

### Problem: Ping fails between containers
```bash
# Verify network assignment
docker inspect <container> | grep NetworkMode

# Ensure both on same network
docker network connect <network> <container>

# Check if ping is installed
docker exec -it <container> which ping
```

### Problem: Application cannot start
```bash
# Check application logs
docker logs <container>

# Verify environment variables
docker inspect <container> | grep -A 10 Env

# Test database connectivity
docker exec -it <container> curl <db-host>:<port>
```

## Cleanup Commands

```bash
# Stop all containers
docker stop flask-app flask-db wordpress-app wordpress-db

# Remove all containers
docker rm flask-app flask-db wordpress-app wordpress-db

# Remove networks
docker network rm network-one network-two

# Remove images (optional)
docker rmi yourusername/flask-mongodb-test:v1.0

# Clean up everything
docker system prune -a
```

## Conclusion

This assignment successfully demonstrated:
- Creating isolated application stacks using Docker networks
- Testing cross-stack communication on shared networks
- Verifying network isolation on separate networks
- Understanding DNS resolution within Docker networks
- Applying real-world multi-tenant architecture patterns

The key takeaway is that **network isolation is essential for security and proper application architecture** in containerized environments.

## Author
Velayutham

## Date Completed
January 4, 2026

## Course
DevOps Bootcamp - Class 3 - Docker Networks



