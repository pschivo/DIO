# DIO Platform Deployment Guide

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 3000, 8000, 4222, 5432 available

### Development Environment (with Mock Data)

```bash
# Clone and navigate to project
cd dio-platform

# Start all services with mock data
docker-compose --profile mock up -d

# View logs
docker-compose logs -f

# Access the dashboard
open http://localhost:3000
```

### Production Environment

```bash
# Start production services
docker-compose --profile production up -d

# Initialize database
docker-compose exec frontend npm run db:push

# Access the dashboard
open http://localhost:3000
```

## Service Architecture

### Frontend (Port 3000)
- **Technology**: Next.js 15 with TypeScript
- **UI**: shadcn/ui components with Tailwind CSS
- **Features**: Real-time dashboard, agent monitoring, threat visualization

### Nerve Center (Port 8000)
- **Technology**: FastAPI with Python 3.11
- **Purpose**: AI core for coordination and federated learning
- **API Documentation**: http://localhost:8000/docs

### Mesh Network (Port 4222)
- **Technology**: WebSocket-based Python service
- **Purpose**: Real-time communication between all components
- **Protocol**: Custom message routing with room-based broadcasting

### Agent Services
- **Technology**: Python with psutil for system monitoring
- **Purpose**: Endpoint monitoring and autonomous threat response
- **Scaling**: Multiple instances for different endpoint types

### Mock Data Service (Development Only)
- **Purpose**: Generates realistic test data for development
- **Features**: 12 mock agents, controlled threat generation
- **Configuration**: Adjustable via environment variables

## Configuration

### Environment Variables

#### Frontend
```env
NEXT_PUBLIC_WS_URL=ws://localhost:4222
DATABASE_URL=sqlite:./db/app.db
```

#### Nerve Center
```env
PYTHONUNBUFFERED=1
```

#### Agent
```env
NERVE_CENTER_URL=http://nerve-center:8000
MONITORING_INTERVAL=5
ANOMALY_THRESHOLD=80.0
```

#### Mock Data
```env
NUM_AGENTS=12
UPDATE_INTERVAL=10
THREAT_PROBABILITY=0.1
```

### Database Setup

#### Development (SQLite)
```bash
# Initialize database
npm run db:push

# Generate Prisma client
npm run db:generate
```

#### Production (PostgreSQL)
```bash
# Start with production profile
docker-compose --profile production up -d

# Run migrations
docker-compose exec frontend npm run db:migrate
```

## Monitoring and Logs

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f nerve-center
docker-compose logs -f mesh-network
docker-compose logs -f agent
```

### Health Checks
```bash
# Check service health
curl http://localhost:8000/health  # Nerve Center
curl http://localhost:3000          # Frontend
```

### System Metrics
- **Frontend Dashboard**: Real-time metrics at http://localhost:3000
- **Nerve Center API**: System status at http://localhost:8000/system/status
- **Mesh Network**: WebSocket monitoring on port 4222

## Scaling and Performance

### Horizontal Scaling
```yaml
# In docker-compose.yml
agent:
  deploy:
    replicas: 5  # Scale agents
```

### Resource Limits
```yaml
services:
  nerve-center:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

## Security Configuration

### Production Security
1. **Change Default Passwords**: Update database credentials
2. **Network Isolation**: Use Docker networks and firewall rules
3. **SSL/TLS**: Enable HTTPS for production deployments
4. **Secrets Management**: Use Docker secrets or environment files

### Environment Variables File
```bash
# .env file (not committed to version control)
DATABASE_URL=postgresql://dio_user:secure_password@database:5432/dio_platform
NEXTAUTH_SECRET=your-secret-key
```

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Kill conflicting processes
sudo kill -9 <PID>
```

#### Database Connection Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d database
docker-compose exec frontend npm run db:push
```

#### Memory Issues
```bash
# Check Docker resource usage
docker stats

# Clean up unused containers
docker system prune -a
```

### Debug Mode
```bash
# Run services in debug mode
docker-compose --profile mock up --build

# Access container shell
docker-compose exec nerve-center bash
docker-compose exec agent bash
```

## Backup and Recovery

### Database Backup
```bash
# SQLite (Development)
cp db/app.db db/app.backup.db

# PostgreSQL (Production)
docker-compose exec database pg_dump -U dio_user dio_platform > backup.sql
```

### Configuration Backup
```bash
# Backup Docker configuration
tar -czf dio-config-backup.tar.gz docker-compose.yml .env components/
```

## Development Workflow

### Adding New Components
1. Create component directory in `/components/`
2. Add Dockerfile and requirements.txt
3. Update docker-compose.yml
4. Add to deployment documentation

### Testing
```bash
# Run linting
npm run lint

# Type checking
npm run type-check

# Build test
npm run build
```

### Code Quality
- ESLint for JavaScript/TypeScript
- Black for Python code
- Docker best practices
- Security scanning with `docker scan`

## Production Deployment

### Using Docker Swarm
```bash
# Initialize Swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml dio
```

### Using Kubernetes
```bash
# Convert to Kubernetes manifests
kompose convert -f docker-compose.yml

# Apply to cluster
kubectl apply -f k8s/
```

### Monitoring Stack
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Loki**: Log aggregation
- **AlertManager**: Alerting

## Support

### Documentation
- API Documentation: http://localhost:8000/docs
- Component Documentation: `/docs/` directory
- Architecture Overview: `README.md`

### Getting Help
1. Check logs for error messages
2. Verify service health endpoints
3. Review configuration files
4. Consult troubleshooting section

---

This deployment guide provides comprehensive instructions for setting up, configuring, and maintaining the DIO Platform in both development and production environments.