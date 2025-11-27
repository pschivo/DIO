# DIO Platform - Troubleshooting Guide

## 🔧 Common Issues and Solutions

### ❌ "version attribute is obsolete" Warning

**Problem**: Docker Compose shows warning about version attribute being obsolete.

**Solution**: This is just a warning - it's been fixed in the updated docker-compose.yml. The platform will still work.

### ❌ "npm ci" Error

**Problem**: Frontend build fails with npm ci error about missing package-lock.json.

**Solution**: This has been fixed by updating Dockerfile.frontend to use `npm install` instead of `npm ci`.

### ❌ Build Context Issues

**Problem**: Docker build context is too large or slow.

**Solution**: Added .dockerignore files to reduce build context.

---

## 🚀 Quick Start Commands (Updated)

### Linux/Mac:
```bash
# Start development environment
./start.sh dev

# Start attack simulator
./attack.sh cpu

# Check status
./start.sh status

# View logs
./start.sh logs

# Stop services
./start.sh stop
```

### Windows:
```cmd
# Start development environment
start.bat dev

# Start attack simulator
attack.bat cpu

# Check status
start.bat status

# View logs
start.bat logs

# Stop services
start.bat stop
```

---

## 🔍 Debugging Steps

### 1. Check Docker Environment
```bash
# Check Docker version
docker --version
docker compose version

# Check Docker is running
docker info
```

### 2. Check Network
```bash
# Check if network exists
docker network ls | grep dio

# Check network details
docker network inspect dio-platform_dio-network
```

### 3. Check Individual Services
```bash
# Check service logs
docker compose logs nerve-center
docker compose logs frontend
docker compose logs mock-data

# Check service status
docker compose ps
```

### 4. Manual Service Testing
```bash
# Test nerve center directly
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Test API endpoints
curl http://localhost:8000/agents
curl http://localhost:8000/threats
```

---

## 🛠️ Common Build Issues

### Frontend Build Fails
```bash
# Clear Docker cache
docker system prune -a

# Rebuild frontend only
docker compose build --no-cache frontend

# Check package.json exists
ls -la package.json package-lock.json
```

### Python Service Build Fails
```bash
# Check Python files exist
ls -la components/nerve-center/main.py
ls -la components/agent/main.py

# Check requirements.txt
cat components/nerve-center/requirements.txt
```

### Network Issues
```bash
# Remove and recreate network
docker network rm dio-platform_dio-network
docker compose up -d

# Check port conflicts
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000
netstat -tulpn | grep :4222
```

---

## 📊 Service Health Checks

### Nerve Center Health
```bash
# Health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "component": "nerve_center", ...}
```

### Frontend Health
```bash
# Should return HTML
curl http://localhost:3000

# Check browser console for errors
# Open http://localhost:3000 in browser
```

### Mock Data Service
```bash
# Check logs
docker compose logs mock-data

# Should see agent registration messages
```

---

## 🔄 Reset and Restart

### Full Reset
```bash
# Stop all services
docker compose down

# Remove volumes (WARNING: This deletes data)
docker compose down -v

# Remove all containers
docker system prune -a

# Restart
./start.sh dev
```

### Database Reset
```bash
# Reset database only
rm -f db/app.db
npm run db:push

# Restart services
docker compose restart frontend nerve-center
```

---

## 🎯 Attack Simulator Issues

### Attack Simulator Not Working
```bash
# Check if nerve center is running
curl http://localhost:8000/health

# Build attack simulator manually
cd components/attack-simulator
docker build -t dio-attack-simulator .

# Run attack simulator
docker run --rm --network dio-platform_dio-network dio-attack-simulator python main.py cpu
```

### No Agents Available for Attack
```bash
# Check if mock data is running
docker compose logs mock-data

# Check if agents are registered
curl http://localhost:8000/agents

# Restart mock data service
docker compose restart mock-data
```

### Attack Not Visible in Dashboard
```bash
# Check browser console for WebSocket errors
# Refresh dashboard page
# Check real-time updates are enabled

# Verify threat creation
curl http://localhost:8000/threats
```

---

## 📱 Browser Issues

### Dashboard Not Loading
1. **Clear browser cache**
2. **Check browser console** (F12 → Console)
3. **Try different browser**
4. **Check WebSocket connection** in Network tab

### Real-time Updates Not Working
1. **Check WebSocket connection** in browser Network tab
2. **Look for WebSocket errors** in console
3. **Verify mesh network is running**:
   ```bash
   docker compose logs mesh-network
   ```

---

## 🔧 Port Conflicts

### Check Port Usage
```bash
# Check all required ports
netstat -tulpn | grep :3000  # Frontend
netstat -tulpn | grep :8000  # Nerve Center
netstat -tulpn | grep :4222  # Mesh Network
netstat -tulpn | grep :5432  # Database (production)
```

### Change Ports
Edit `docker-compose.yml` to change ports:
```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # Change to 3001
  nerve-center:
    ports:
      - "8001:8000"  # Change to 8001
```

---

## 📈 Performance Issues

### High Memory Usage
```bash
# Check Docker resource usage
docker stats

# Limit service resources in docker-compose.yml:
services:
  nerve-center:
    deploy:
      resources:
        limits:
          memory: 1G
```

### Slow Dashboard
1. **Check network latency**
2. **Reduce mock data update interval**
3. **Check browser performance**
4. **Disable browser extensions**

---

## 📞 Getting Help

### Log Collection
```bash
# Collect all logs
docker compose logs > dio-logs.txt

# Collect system info
docker info > docker-info.txt
docker compose ps > docker-ps.txt
```

### Environment Information
```bash
# Check OS
uname -a

# Check Docker
docker --version
docker compose version

# Check available resources
free -h
df -h
```

### Contact Support
Provide the following information:
1. **Operating System**: Linux/Mac/Windows + version
2. **Docker Version**: `docker --version`
3. **Error Messages**: Full error output
4. **Logs**: `docker compose logs` output
5. **Steps to Reproduce**: What you were doing

---

## 🎯 Quick Validation Checklist

After starting the platform, verify:

- [ ] Frontend loads at http://localhost:3000
- [ ] Nerve Center responds at http://localhost:8000/health
- [ ] Mock data creates agents (check logs)
- [ ] Dashboard shows agent data
- [ ] Attack simulator can launch attacks
- [ ] Threats appear in dashboard
- [ ] Evidence packs are generated
- [ ] Real-time updates work

---

## 🔚 Emergency Recovery

If nothing works, try this:

```bash
# 1. Clean everything
docker compose down -v --remove-orphans
docker system prune -a

# 2. Remove all Docker artifacts
docker volume prune
docker network prune

# 3. Restart Docker service
sudo systemctl restart docker  # Linux
# Or restart Docker Desktop  # Windows/Mac

# 4. Start fresh
./start.sh dev
```

---

**💡 Most issues are resolved by:**
1. **Running `./start.sh stop` then `./start.sh dev`**
2. **Checking Docker is running and updated**
3. **Clearing browser cache**
4. **Checking port conflicts**

**🎯 For continued issues, collect logs and environment information for support.**