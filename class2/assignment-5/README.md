# Assignment 5: Real Project - Simple Blog API

## Overview
This assignment builds a complete Blog API using Flask and SQLite, containerized with Docker. The blog data persists in a Docker volume, demonstrating real-world application of Docker concepts for stateful services.

## Docker Concepts Covered

### Core Concepts
- **Docker Image**: Packaged Flask application with all dependencies
- **Docker Container**: Running instance of the Blog API
- **Docker Volumes**: Persistent storage for SQLite database file
- **Custom Networks**: Isolated network environment for the blog service
- **Port Mapping**: Exposing API endpoints to host machine
- **Environment Variables**: Configuration management for database path

### Integration
This assignment combines concepts from all previous assignments:
- Assignment 1: Building and running containerized applications
- Assignment 2: Volume persistence for database storage
- Assignment 3: Custom network for service isolation
- Assignment 4: Understanding network behavior

## Project Structure
```
assignment-5/
  app.py              # Flask Blog API with CRUD operations
  requirements.txt    # Python dependencies (Flask)
  Dockerfile          # Docker image build instructions
  .dockerignore       # Files to exclude from build
  test_api.sh         # API testing script (optional)
  README.md          # This file
```

## Application Architecture

```
Browser/Postman
      |
      | HTTP Requests
      v
  localhost:5000 (Host)
      |
      | Port Mapping
      v
  blog-api:5000 (Container)
      |
      | SQLite Operations
      v
  /data/blog.db (Volume: blog-data)
```

## API Endpoints

### Documentation
- `GET /` - API documentation and available endpoints
- `GET /health` - Health check (API and database connectivity)
- `GET /stats` - Database statistics (total posts, DB path)

### Blog Operations (CRUD)
- `GET /posts` - Retrieve all blog posts
- `GET /posts/<id>` - Retrieve single post by ID
- `POST /posts` - Create new blog post
- `DELETE /posts/<id>` - Delete post by ID

### Post Data Format (JSON)
```json
{
  "title": "Post Title",
  "content": "Post content goes here",
  "author": "Author Name"
}
```

## Prerequisites
- Docker Desktop for Mac (Apple Silicon)
- Docker Hub account
- curl or Postman for API testing
- Basic understanding of REST APIs
- Git repository: devops-bootcamp
- Replace 'yourusername' with your docker username

## How It Works

### Database Persistence
1. Flask application connects to SQLite database at `/data/blog.db`
2. Container's `/data` directory is mounted to Docker volume `blog-data`
3. When container is deleted, volume persists with all data
4. New containers can mount same volume to access existing data

### Network Isolation
- Custom network `blog-network` isolates the blog service
- Enables future expansion (e.g., adding frontend, database containers)
- Provides DNS resolution for container-to-container communication

## Step-by-Step Implementation

### Step 1: Create Project Folder

```bash
cd ~/Documents/devops-bootcamp/class2
mkdir assignment-5
cd assignment-5
```

### Step 2: Create Application Files

Create the following files in `assignment-5/`:
- `app.py` - Flask application with CRUD operations
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker image definition
- `.dockerignore` - Exclude unnecessary files

**requirements.txt**:
```
Flask==3.0.0
```

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN mkdir -p /data

EXPOSE 5000

ENV DB_PATH=/data/blog.db

CMD ["python", "app.py"]
```

**.dockerignore**:
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.db
*.sqlite
.DS_Store
.git
.gitignore
```

### Step 3: Build Docker Image

```bash
# Build the image
docker build -t yourusername/blog-api:v1.0 .

# Verify image creation
docker images | grep blog-api
```

Replace `yourusername` with your Docker Hub username.

### Step 4: Create Docker Volume

```bash
# Create named volume for database
docker volume create blog-data

# Verify volume creation
docker volume ls

# Inspect volume (optional)
docker volume inspect blog-data
```

### Step 5: Create Custom Network

```bash
# Create custom bridge network
docker network create blog-network

# Verify network creation
docker network ls

# Inspect network (optional)
docker network inspect blog-network
```

### Step 6: Run Blog API Container

```bash
# Run container with volume and network
docker run -d \
  --name blog-api \
  --network blog-network \
  -v blog-data:/data \
  -p 5000:5000 \
  yourusername/blog-api:v1.0

# Verify container is running
docker ps

# Check application logs
docker logs blog-api

# Follow logs in real-time
docker logs -f blog-api
```

**Command Breakdown:**
- `--name blog-api`: Assigns friendly name to container
- `--network blog-network`: Connects to custom network
- `-v blog-data:/data`: Mounts volume to /data directory
- `-p 5000:5000`: Maps host port 5000 to container port 5000
- Container automatically initializes database on first run

## Testing the API

### Option 1: Using Test Script (Recommended)

If you created `test_api.sh`:

```bash
chmod +x test_api.sh
./test_api.sh
```

### Option 2: Manual Testing with curl

#### 1. Health Check
```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{"status": "healthy", "database": "connected"}
```

#### 2. API Documentation
```bash
curl http://localhost:5000/
```

#### 3. Create Blog Posts
```bash
# Create first post
curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started with Docker",
    "content": "Docker makes it easy to containerize applications and manage dependencies.",
    "author": "Your Name"
  }'

# Create second post
curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Docker Volumes Explained",
    "content": "Volumes provide persistent storage that survives container restarts and deletions.",
    "author": "DevOps Engineer"
  }'

# Create third post
curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "REST API Best Practices",
    "content": "Design clean, intuitive APIs with proper HTTP methods and status codes.",
    "author": "API Developer"
  }'
```

**Expected Response:**
```json
{
  "message": "Post created successfully",
  "id": 1,
  "title": "Getting Started with Docker"
}
```

#### 4. Get All Posts
```bash
curl http://localhost:5000/posts
```

**Expected Response:**
```json
{
  "count": 3,
  "posts": [
    {
      "id": 3,
      "title": "REST API Best Practices",
      "content": "Design clean, intuitive APIs...",
      "author": "API Developer",
      "created_at": "2025-12-19 12:00:00"
    },
    ...
  ]
}
```

#### 5. Get Single Post
```bash
curl http://localhost:5000/posts/1
```

#### 6. Get Database Statistics
```bash
curl http://localhost:5000/stats
```

**Expected Response:**
```json
{
  "total_posts": 3,
  "database_path": "/data/blog.db",
  "database_exists": true
}
```

#### 7. Delete a Post
```bash
curl -X DELETE http://localhost:5000/posts/2
```

**Expected Response:**
```json
{
  "message": "Post deleted successfully",
  "id": 2
}
```

### Option 3: Using Browser

Open `http://localhost:5000` in your browser to see API documentation.

## Verifying Data Persistence (Critical Test)

This test proves that data persists in the volume even after container deletion.

### Step 1: Create Test Data

```bash
# Create some posts
curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"Persistence Test","content":"This data should survive container deletion","author":"Tester"}'

# Verify posts exist
curl http://localhost:5000/posts
curl http://localhost:5000/stats
```

### Step 2: Delete the Container

```bash
# Stop the container
docker stop blog-api

# Remove the container completely
docker rm blog-api

# Verify container is gone
docker ps -a | grep blog-api
# Should return nothing

# Verify volume still exists
docker volume ls | grep blog-data
# Should show blog-data volume
```

### Step 3: Start New Container with Same Volume

```bash
# Run a BRAND NEW container with the SAME volume
docker run -d \
  --name blog-api-new \
  --network blog-network \
  -v blog-data:/data \
  -p 5000:5000 \
  yourusername/blog-api:v1.0

# Wait a few seconds for startup
sleep 3

# Check logs
docker logs blog-api-new
```

### Step 4: Verify Data Still Exists

```bash
# Get all posts
curl http://localhost:5000/posts

# Check statistics
curl http://localhost:5000/stats
```

**SUCCESS CRITERIA:**
- All previously created posts are still present
- Post IDs are unchanged
- Created timestamps are preserved
- Total post count matches before container deletion

If you see your data, **VOLUME PERSISTENCE WORKS!** ðŸŽ‰

## Inspecting the Database

### Access Container Shell

```bash
docker exec -it blog-api-new /bin/bash
```

### Inside Container

```bash
# Check if database file exists
ls -lh /data/

# View database schema
sqlite3 /data/blog.db ".schema"

# Query all posts
sqlite3 /data/blog.db "SELECT * FROM posts;"

# Count posts
sqlite3 /data/blog.db "SELECT COUNT(*) FROM posts;"

# Exit container
exit
```

## Push to Docker Hub

### Login and Push

```bash
# Login to Docker Hub
docker login

# Push versioned image
docker push yourusername/blog-api:v1.0

# Tag as latest
docker tag yourusername/blog-api:v1.0 yourusername/blog-api:latest

# Push latest tag
docker push yourusername/blog-api:latest
```

### Verify on Docker Hub

Visit: `https://hub.docker.com/r/yourusername/blog-api`

## Useful Commands

### Container Management
```bash
# View container logs
docker logs blog-api

# Follow logs in real-time
docker logs -f blog-api

# View container resource usage
docker stats blog-api

# Inspect container details
docker inspect blog-api

# Execute commands in running container
docker exec -it blog-api /bin/bash

# Restart container
docker restart blog-api
```

### Volume Management
```bash
# List all volumes
docker volume ls

# Inspect volume details
docker volume inspect blog-data

# Check volume disk usage
docker system df -v

# Backup volume (create tar archive)
docker run --rm -v blog-data:/data -v $(pwd):/backup ubuntu tar czf /backup/blog-backup.tar.gz /data
```

### Network Management
```bash
# List networks
docker network ls

# Inspect network
docker network inspect blog-network

# View containers on network
docker network inspect blog-network --format '{{range .Containers}}{{.Name}} {{end}}'
```

### Image Management
```bash
# List images
docker images

# Remove image
docker rmi yourusername/blog-api:v1.0

# View image history
docker history yourusername/blog-api:v1.0

# Check image size
docker images yourusername/blog-api --format "{{.Size}}"
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 5000
lsof -i :5000

# Kill process using the port
kill -9 <PID>

# Or use different port
docker run -d --name blog-api -p 5001:5000 ...
```

### Database Connection Error
```bash
# Check if volume is mounted correctly
docker inspect blog-api | grep -A 10 Mounts

# Verify database file exists
docker exec blog-api ls -la /data/

# Check application logs
docker logs blog-api
```

### Container Won't Start
```bash
# Check logs for errors
docker logs blog-api

# Verify image was built correctly
docker images | grep blog-api

# Check if port is already in use
docker ps | grep 5000
```

### Data Not Persisting
```bash
# Verify volume is specified in run command
docker inspect blog-api | grep -A 5 Mounts

# Check volume exists
docker volume ls | grep blog-data

# Verify database path in container
docker exec blog-api env | grep DB_PATH
```

## Cleanup Commands

### Remove Everything
```bash
# Stop and remove container
docker stop blog-api-new
docker rm blog-api-new

# Remove custom network
docker network rm blog-network

# Remove volume (WARNING: Deletes all blog data permanently!)
docker volume rm blog-data

# Remove image
docker rmi yourusername/blog-api:v1.0 yourusername/blog-api:latest

# Verify cleanup
docker ps -a
docker volume ls
docker network ls
docker images
```

### Preserve Data (Remove Container Only)
```bash
# Stop and remove container but keep volume
docker stop blog-api
docker rm blog-api

# Volume blog-data remains with all data intact
docker volume ls | grep blog-data
```

## Key Learnings

### Technical Skills
1. Built a complete REST API with CRUD operations
2. Implemented database persistence using Docker volumes
3. Configured custom networks for service isolation
4. Managed container lifecycle and data persistence
5. Tested API endpoints using curl
6. Published Docker images to Docker Hub

### Docker Concepts Mastered
- Volume mounting and data persistence
- Custom bridge networks
- Port mapping and exposure
- Environment variable configuration
- Multi-layer Docker images
- Container inspection and debugging

### Real-World Applications
- **Microservices**: Each service in its own container
- **Development**: Consistent dev environment across teams
- **Data Persistence**: Databases that survive container restarts
- **API Development**: Containerized backend services
- **DevOps**: Infrastructure as code with Dockerfile

## Best Practices Demonstrated

1. **Volume for Data**: Database stored in volume, not container filesystem
2. **Custom Network**: Isolated network for better security
3. **Environment Variables**: Configurable database path
4. **Health Checks**: `/health` endpoint for monitoring
5. **API Documentation**: Self-documenting `/` endpoint
6. **Minimal Base Image**: Used `python:3.9-slim` for smaller size
7. **Layer Caching**: Copied requirements before code for better caching
8. **.dockerignore**: Excluded unnecessary files from image
9. **Clear Logging**: Application logs startup and database location
10. **RESTful Design**: Proper HTTP methods and status codes

## Extension Ideas

### Add More Features
- Update existing posts (PUT endpoint)
- Search posts by title or author
- Pagination for large result sets
- Add timestamps for updated_at
- Add categories/tags to posts
- User authentication

### Add Frontend
- Create React/Vue frontend container
- Connect frontend to backend API via custom network
- Serve frontend on different port

### Add Database Container
- Replace SQLite with PostgreSQL container
- Create separate volume for PostgreSQL data
- Connect backend to PostgreSQL via network

### Add Reverse Proxy
- Add Nginx container as reverse proxy
- Route requests to appropriate services
- Enable HTTPS with SSL certificates

## Real-World Production Considerations

1. **Security**: Use secrets management for sensitive data
2. **Monitoring**: Add Prometheus/Grafana for metrics
3. **Logging**: Centralized logging with ELK stack
4. **Backups**: Automated volume backups
5. **High Availability**: Multiple container replicas
6. **Load Balancing**: Distribute traffic across containers
7. **CI/CD**: Automated builds and deployments
8. **Environment Management**: Separate dev/staging/prod configs

## Project Completion Checklist

- [ ] Created all required files (app.py, Dockerfile, requirements.txt)
- [ ] Built Docker image successfully
- [ ] Created Docker volume and custom network
- [ ] Ran container with volume mounted
- [ ] Tested all API endpoints
- [ ] Created multiple blog posts
- [ ] Verified data persistence after container deletion
- [ ] Pushed image to Docker Hub
- [ ] Documented all steps in README
- [ ] Committed and pushed to GitHub

## Author
Velayutham

## Date Completed
December 19, 2025

