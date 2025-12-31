# Docker Deployment Guide

## 📦 What You Have

I've created 4 Docker files for you:

1. **Dockerfile** - Builds your FastAPI application image
2. **.dockerignore** - Tells Docker what files to exclude
3. **docker-compose.yml** - Development setup (database + API)
4. **docker-compose.prod.yml** - Production setup (with more features)

## 🏗️ Project Structure with Docker

```
backend/
├── app/                          # Your application code
│   ├── main.py
│   ├── database.py
│   └── ...
├── Dockerfile                    # ← NEW: Builds API image
├── .dockerignore                 # ← NEW: Exclude files from image
├── docker-compose.yml            # ← UPDATED: Dev setup
├── docker-compose.prod.yml       # ← NEW: Production setup
├── requirements.txt
├── .env                          # Environment variables
└── .env.prod                     # ← NEW: Production env vars
```

## 🚀 Development Usage

### Option 1: Database Only (Recommended for Development)

Run database in Docker, run API locally for hot reload:

```bash
# Start just the database
docker-compose up -d db

# Install dependencies locally
pip install -r requirements.txt

# Run API locally with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Benefits:**
- ✅ Fast hot reload (code changes immediately reflected)
- ✅ Easy debugging
- ✅ Database in Docker (consistent environment)

### Option 2: Full Docker Setup (Both Database + API)

Run everything in Docker:

```bash
# Start both database and API
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose down -v
```

**Benefits:**
- ✅ Closer to production environment
- ✅ No local Python dependencies needed
- ✅ Consistent across team members

## 🏭 Production Deployment

### Step 1: Create Production Environment File

Create `.env.prod`:

```bash
# Database credentials (CHANGE THESE!)
DB_USER=booking_user_prod
DB_PASSWORD=super_secret_password_here
DB_NAME=booking_db_prod

# Build metadata
BUILD_DATE=2025-01-15
VERSION=1.0.0

# Application settings
ENVIRONMENT=production
LOG_LEVEL=info
```

### Step 2: Build and Run

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f api

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### Step 3: Production Checklist

- [ ] Change default database password in `.env.prod`
- [ ] Set up SSL certificates for HTTPS
- [ ] Configure proper CORS origins in `app/main.py`
- [ ] Set up automated backups
- [ ] Configure monitoring and alerting
- [ ] Set up log aggregation
- [ ] Configure firewall rules
- [ ] Test health check endpoints
- [ ] Set up CI/CD pipeline

## 🔧 Common Docker Commands

### Building

```bash
# Build API image
docker build -t booking-api:latest .

# Build with specific tag
docker build -t booking-api:v1.0.0 .

# Build without cache (fresh build)
docker build --no-cache -t booking-api:latest .
```

### Running Containers

```bash
# Run database only
docker-compose up -d db

# Run API only (requires database)
docker-compose up -d api

# Run everything
docker-compose up -d

# Run in foreground (see logs)
docker-compose up

# Run specific version
docker-compose -f docker-compose.prod.yml up -d
```

### Managing Containers

```bash
# List running containers
docker-compose ps
# or
docker ps

# Stop containers
docker-compose stop

# Start stopped containers
docker-compose start

# Restart containers
docker-compose restart

# Remove containers
docker-compose down

# Remove containers AND volumes (deletes data!)
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs api
docker-compose logs db

# Follow logs (live updates)
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Logs from specific time
docker-compose logs --since 2h
```

### Debugging

```bash
# Execute command in running container
docker-compose exec api bash

# Check container health
docker inspect --format='{{.State.Health.Status}}' booking_api

# View resource usage
docker stats

# View container details
docker-compose exec api env  # View environment variables
docker-compose exec db psql -U booking_user booking_db  # Connect to database
```

### Cleaning Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused (BE CAREFUL!)
docker system prune -a

# See disk usage
docker system df
```

## 🔄 Database Management

### Backup Database

```bash
# Create backup
docker-compose exec db pg_dump -U booking_user booking_db > backup.sql

# Create compressed backup
docker-compose exec db pg_dump -U booking_user booking_db | gzip > backup.sql.gz

# Backup with timestamp
docker-compose exec db pg_dump -U booking_user booking_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database

```bash
# Restore from backup
cat backup.sql | docker-compose exec -T db psql -U booking_user booking_db

# Restore from compressed backup
gunzip < backup.sql.gz | docker-compose exec -T db psql -U booking_user booking_db
```

### Connect to Database

```bash
# Using docker-compose
docker-compose exec db psql -U booking_user booking_db

# Using docker directly
docker exec -it booking_db psql -U booking_user booking_db

# Run SQL query
docker-compose exec db psql -U booking_user booking_db -c "SELECT * FROM providers;"
```

## 📊 Monitoring Production

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check Docker health status
docker inspect --format='{{.State.Health.Status}}' booking_api

# Check all container health
docker-compose ps
```

### View Metrics

```bash
# CPU and memory usage
docker stats

# Container logs
docker-compose logs -f --tail=100

# Database connections
docker-compose exec db psql -U booking_user booking_db -c "SELECT count(*) FROM pg_stat_activity;"
```

## 🚨 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs api

# Check if port is in use
lsof -i :8000

# Rebuild image
docker-compose build --no-cache api
docker-compose up -d
```

### Database connection fails

```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec db pg_isready -U booking_user

# Verify environment variables
docker-compose exec api env | grep DATABASE_URL
```

### Cannot connect to API from host

```bash
# Check if container is running
docker-compose ps

# Check port mapping
docker port booking_api

# Check firewall
sudo ufw status

# Test from within container
docker-compose exec api curl http://localhost:8000/health
```

### Out of disk space

```bash
# Check disk usage
docker system df

# Clean up unused resources
docker system prune -a

# Remove old images
docker image prune -a

# Remove unused volumes (WARNING: may delete data)
docker volume prune
```

### Database data lost after restart

```bash
# Check if volumes are mounted
docker volume ls

# Inspect volume
docker volume inspect booking_postgres_data

# Make sure not using docker-compose down -v
# Use docker-compose down instead (keeps volumes)
```

## 🔐 Security Best Practices

### Production Security

1. **Never expose database port** in production:
   ```yaml
   # Remove this in production docker-compose.prod.yml:
   # ports:
   #   - "5432:5432"
   ```

2. **Use secrets management**:
   ```bash
   # Use Docker secrets instead of environment variables
   echo "super_secret_password" | docker secret create db_password -
   ```

3. **Run as non-root user** (already in Dockerfile):
   ```dockerfile
   USER appuser  # ✅ Already implemented
   ```

4. **Scan images for vulnerabilities**:
   ```bash
   docker scan booking-api:latest
   ```

5. **Use specific image versions**:
   ```dockerfile
   FROM python:3.11-slim  # ✅ Good
   # FROM python:latest   # ❌ Bad
   ```

## 📈 Scaling

### Horizontal Scaling (Multiple API Instances)

```bash
# Run 3 API instances
docker-compose -f docker-compose.prod.yml up -d --scale api=3

# Behind a load balancer (Nginx, Traefik, etc.)
# Add load balancer to docker-compose.prod.yml
```

### Vertical Scaling (More Resources)

```yaml
# In docker-compose.prod.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'      # Increase CPU
          memory: 4G       # Increase memory
```

## 🎯 Best Practices Summary

### Development
- ✅ Use `docker-compose.yml` for local development
- ✅ Mount code as volume for hot reload
- ✅ Expose database port for tools (pgAdmin, DBeaver)
- ✅ Use `--reload` flag for uvicorn

### Production
- ✅ Use `docker-compose.prod.yml`
- ✅ Don't mount code as volume (use image)
- ✅ Don't expose database port
- ✅ Use environment variables from secure source
- ✅ Enable health checks
- ✅ Set resource limits
- ✅ Use multiple workers
- ✅ Set up automated backups
- ✅ Monitor logs and metrics

### Both
- ✅ Use `.dockerignore` to reduce image size
- ✅ Use multi-stage builds (already in Dockerfile)
- ✅ Tag images with versions
- ✅ Run containers as non-root user
- ✅ Keep images updated (security patches)
- ✅ Use named volumes for data persistence