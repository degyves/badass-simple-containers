# Container Configuration Issues & Solutions

This document covers common pitfalls when working with containerized applications and their solutions.

## 🚨 Volume Mount Issues

### Problem: Code changes not reflected in containers
**Symptoms**: You edit source code but changes don't appear in the running application.

```yaml
# ❌ Wrong - Container copies code at build time only
services:
  app:
    build: ./backend
    # No volumes = changes require complete rebuild
```

**Solution**:
```yaml
# ✅ Correct - Live reload with volume mounts
services:
  app:
    build: ./backend
    volumes:
      - ./backend:/app  # Mount source for live reload
    command: ["python", "-m", "uvicorn", "app:app", "--reload"]
```

**Project-specific fix**:
```bash
# If file watching fails (common with Podman Desktop on macOS)
/opt/podman/bin/podman restart october_app_1
```

## 🔐 Environment Variables & Secrets

### Problem: Secrets exposed in version control
**Symptoms**: Passwords and API keys visible in docker-compose.yml.

```yaml
# ❌ Wrong - Secrets exposed in version control
environment:
  DB_PASSWORD: supersecretpassword123
  API_KEY: sk-1234567890abcdef
```

**Solution**:
```yaml
# ✅ Correct - Use .env files (gitignored)
environment:
  DB_PASSWORD: ${DB_PASSWORD}  # From .env file
  API_KEY: ${API_KEY}
```

Create `.env` file:
```bash
DB_PASSWORD=supersecretpassword123
API_KEY=sk-1234567890abcdef
```

Add to `.gitignore`:
```gitignore
.env
.env.local
.env.production
```

## 🌐 Networking Issues

### Problem: Wrong host names for inter-service communication
**Symptoms**: "Connection refused" errors between containers.

```javascript
// ❌ Wrong - Frontend trying to reach backend
const API_BASE = 'http://localhost:8000'  // Only works from browser
```

**Solution**:
```yaml
# ✅ Correct - Use service names for internal communication
services:
  frontend:
    environment:
      # For browser-to-container (external)
      REACT_APP_API_URL: http://localhost:8000  
  app:
    environment:
      # For container-to-container (internal)
      EXTERNAL_API: http://other-service:3000
```

**Rule**: 
- Browser → Container: Use `localhost:PORT`
- Container → Container: Use `service-name:PORT`

## 🚪 Port Conflicts

### Problem: "Port already in use" errors
**Symptoms**: Container fails to start with "bind: address already in use".

```yaml
# ❌ Wrong - Common ports might be taken
ports:
  - "80:80"      # Might conflict with local web server
  - "3000:3000"  # Might conflict with other React apps
  - "5432:5432"  # Might conflict with local PostgreSQL
```

**Solution**:
```yaml
# ✅ Correct - Use non-standard host ports
ports:
  - "8080:80"    # Map to different host port
  - "3001:3000"  # Avoid conflicts
  - "5433:5432"  # Use different external port
```

**Debug command**:
```bash
# Check what's using a port
lsof -i :3000
netstat -tulpn | grep :3000
```

## ⏱️ Dependency Order Issues

### Problem: Services starting before dependencies are ready
**Symptoms**: "Connection to database failed" on app startup.

```yaml
# ❌ Wrong - App starts before DB is ready
services:
  app:
    depends_on:
      - postgres  # Only waits for container start, not readiness
```

**Solution**:
```yaml
# ✅ Correct - Wait for service health
services:
  app:
    depends_on:
      postgres:
        condition: service_healthy  # Wait for health check
  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## 🔒 File Permissions Issues

### Problem: Permission denied errors in containers
**Symptoms**: "Permission denied" when accessing files or running commands.

```dockerfile
# ❌ Wrong - Running as root, permission mismatches
FROM node:18
COPY . /app
RUN npm install  # Creates files as root
USER node  # Switches to non-root user who can't access root files
```

**Solution**:
```dockerfile
# ✅ Correct - Consistent user throughout
FROM node:18
RUN addgroup -g 1001 -S appgroup
RUN adduser -S appuser -u 1001 -G appgroup
USER appuser  # Switch early
COPY --chown=appuser:appgroup . /app
RUN npm install
```

**Alternative solution**:
```dockerfile
# ✅ Also correct - Stay as root but fix ownership
FROM node:18
COPY . /app
RUN npm install
RUN chown -R node:node /app
USER node
```

## 📦 Build Context Issues

### Problem: Slow builds due to large context
**Symptoms**: "Sending build context" takes forever.

```dockerfile
# ❌ Wrong - Copies unnecessary files
COPY . /app  # Copies .git, node_modules, logs, etc.
```

**Solution**: Create `.dockerignore`:
```dockerignore
# .dockerignore
node_modules
.git
*.log
.env
.DS_Store
Thumbs.db
README.md
.gitignore
```

```dockerfile
# ✅ Correct - Only copy what's needed
COPY package*.json ./
RUN npm install
COPY src/ ./src/
COPY public/ ./public/
```

## 💾 Resource Limits Issues

### Problem: Containers consuming all system resources
**Symptoms**: System becomes unresponsive, other apps crash.

```yaml
# ❌ Wrong - No resource limits
services:
  app:
    build: ./backend
    # Can consume all CPU/memory
```

**Solution**:
```yaml
# ✅ Correct - Set reasonable limits
services:
  app:
    build: ./backend
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

**Monitor resources**:
```bash
# Check container resource usage
podman stats
docker stats
```

## 💿 Database Persistence Issues

### Problem: Data lost when container restarts
**Symptoms**: All data disappears when you restart containers.

```yaml
# ❌ Wrong - No volume for database
services:
  postgres:
    image: postgres:14
    # Data stored in container filesystem = lost on restart
```

**Solution**:
```yaml
# ✅ Correct - Use named volumes
services:
  postgres:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:  # Persisted outside container
```

**Backup/restore**:
```bash
# Backup
podman exec postgres_container pg_dump -U postgres dbname > backup.sql

# Restore
podman exec -i postgres_container psql -U postgres dbname < backup.sql
```

## 🏗️ Development vs Production Config Issues

### Problem: Same config for both environments
**Symptoms**: Development tools in production, security issues.

```yaml
# ❌ Wrong - Development config in production
services:
  app:
    volumes:
      - ./src:/app/src  # Source code mounted in production!
    command: ["npm", "run", "dev"]  # Development server in production!
    environment:
      NODE_ENV: development  # Wrong environment
```

**Solution**: Separate compose files
```yaml
# docker-compose.yml (development)
services:
  app:
    volumes:
      - ./src:/app/src
    command: ["npm", "run", "dev"]
    environment:
      NODE_ENV: development
```

```yaml
# docker-compose.prod.yml (production)
services:
  app:
    # No source volumes
    command: ["npm", "start"]
    environment:
      NODE_ENV: production
```

**Usage**:
```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up
```

## 📋 Log Management Issues

### Problem: Logs filling up disk space
**Symptoms**: Docker/Podman consuming all disk space.

```yaml
# ❌ Wrong - Unlimited log growth
services:
  app:
    build: ./backend
    # No log configuration = logs grow forever
```

**Solution**:
```yaml
# ✅ Correct - Configure log rotation
services:
  app:
    build: ./backend
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Log management commands**:
```bash
# View logs
podman logs container_name --tail=50

# Follow logs
podman logs container_name -f

# Clear logs (be careful!)
podman logs container_name --since=0 > /dev/null
```

## 🔧 File Watching Issues (macOS/Podman)

### Problem: Live reload not working with volume mounts
**Symptoms**: Code changes don't trigger container restarts.

**Solution for React**:
```yaml
# Add polling for better file watching
services:
  frontend:
    environment:
      CHOKIDAR_USEPOLLING: "true"
      WATCHPACK_POLLING: "true"
```

**Solution for Python/uvicorn**:
```yaml
services:
  backend:
    command: ["python", "-m", "uvicorn", "app:app", "--reload", "--reload-dir", "/app"]
```

**Manual restart when needed**:
```bash
# Restart specific container
/opt/podman/bin/podman restart october_app_1
```

## 🩺 Quick Debugging Checklist

When things go wrong, check these in order:

1. **Container status**:
   ```bash
   podman ps -a  # Check if containers are running
   ```

2. **Port conflicts**:
   ```bash
   lsof -i :3000,8000,5432  # Check what's using ports
   ```

3. **Container logs**:
   ```bash
   podman logs container_name --tail=20
   ```

4. **Network connectivity**:
   ```bash
   podman exec container_name ping other_container
   ```

5. **Volume mounts**:
   ```bash
   podman exec container_name ls -la /app
   ```

6. **Environment variables**:
   ```bash
   podman exec container_name env
   ```

7. **Resource usage**:
   ```bash
   podman stats
   ```

## 🚀 Project-Specific Commands

For this specific project:

```bash
# Check all containers
/opt/podman/bin/podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Restart backend after code changes
/opt/podman/bin/podman restart october_app_1

# View backend logs
/opt/podman/bin/podman logs october_app_1 --tail=20

# Restart frontend after package.json changes
/opt/podman/bin/podman restart october_frontend_1

# Rebuild everything
/opt/podman/bin/podman-compose down
/opt/podman/bin/podman-compose up --build

# Test API directly
curl http://localhost:8000/hello/testuser
curl http://localhost:8000/users
```

## 📚 Additional Resources

- [Docker Compose documentation](https://docs.docker.com/compose/)
- [Podman Compose documentation](https://github.com/containers/podman-compose)
- [Container best practices](https://docs.docker.com/develop/dev-best-practices/)
- [Security best practices](https://docs.docker.com/engine/security/)