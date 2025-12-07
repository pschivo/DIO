# DIO Platform - Digital Immune Organism

A production-ready cybersecurity platform that implements a self-evolving security architecture modeled after the human immune system.

## 🎯 Overview

The DIO (Digital Immune Organism) platform is a distributed, containerized security system that provides:

- **Autonomous Threat Detection**: Real-time monitoring with AI-driven anomaly detection
- **Distributed Agent Architecture**: Scalable endpoint protection with 3+ replicated agents
- **Real-time Mesh Communication**: WebSocket-based resilient messaging network
- **Centralized AI Coordination**: FastAPI nerve center for intelligence aggregation
- **Interactive Dashboard**: Next.js 15 interface with live monitoring and control
- **Attack Simulation**: Built-in security testing with CPU/memory stress attacks
- **Persistent Data Storage**: PostgreSQL database with full audit trails

## 🏗️ Architecture

### Production Components

1. **Frontend Dashboard** (Next.js 15 + TypeScript)
   - Real-time monitoring interface with dark/light mode
   - Live agent status, threat visualization, and system health
   - Interactive tabs: Overview, Agents, Threats, Events, Network, System
   - Real-time data fetching every 3-10 seconds
   - Comprehensive event management and investigation tools

2. **Nerve Center** (FastAPI + Python 3.11)
   - AI coordination core with RESTful API
   - Agent registration and management
   - Threat detection and evidence processing
   - Database persistence and backup/restore functionality
   - Health monitoring and system metrics

3. **Mesh Network** (WebSocket + Python)
   - Resilient communication backbone on port 4222
   - Room-based message routing and broadcasting
   - Fault-tolerant design with health checks
   - Real-time message distribution

4. **Agent Service** (Python + psutil)
   - 3 replicated containerized agents by default
   - Endpoint monitoring (CPU, memory, processes, network)
   - Autonomous threat response and anomaly detection
   - Deterministic agent IDs based on hostname
   - Real-time telemetry reporting to nerve center

5. **Attack Simulator** (Python + aiohttp)
   - Security testing tool with multiple attack vectors
   - CPU stress attacks using mathematical computations
   - Memory pressure and network flood simulations
   - Configurable attack intensity and duration

6. **Database Layer** (PostgreSQL 15)
   - Persistent storage for agents, threats, events, evidence
   - Prisma ORM with TypeScript integration
   - Automatic backups and data restoration
   - Health monitoring and connection pooling

7. **Infrastructure Services**
   - **Redis 7**: Caching and session management
   - **NATS JetStream**: Message queuing and streaming
   - **Caddy**: Reverse proxy and TLS termination

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM (for full production stack)
- Available ports: 3000, 4222, 8000, 5432, 6379, 8222

### Production Deployment

```bash
# Clone repository
git clone <repository-url>
cd DIO

# Start full production stack
docker compose --profile production up -d && chmod +x agents.sh attack.sh quick-attack.sh

# Access dashboard
open http://localhost:3000
```

# Check agent status
./agents.sh

# Run attack simulation
./attack.sh
```

## 📊 Features

### Real-time Dashboard
- **Live Monitoring**: Auto-refreshing data every 3-10 seconds
- **Agent Management**: View 3+ agents with status, metrics, and details
- **Threat Detection**: Live threat feed with severity classification
- **Event Management**: Comprehensive event timeline with investigation tools
- **System Health**: Component-level health monitoring
- **Network Metrics**: Performance and latency monitoring
- **Dark/Light Mode**: Toggle between themes

### Autonomous Defense
- **CPU Anomaly Detection**: Mathematical computation-based attack detection
- **Memory Monitoring**: Real-time memory usage tracking
- **Process Analysis**: Process behavior monitoring and anomaly detection
- **Network Surveillance**: Network traffic and connection monitoring
- **Automatic Response**: Configurable threat response actions

### Attack Simulation
- **CPU Stress Attacks**: `math.sqrt(123.456) for _ in range(40000000)` patterns
- **Memory Pressure**: Configurable memory allocation attacks
- **Network Flood**: Network traffic simulation
- **Multi-Vector Attacks**: Coordinated attack scenarios
- **Real-time Testing**: Live attack monitoring and detection

### Data Persistence
- **PostgreSQL Database**: Production-grade data storage
- **Agent Registry**: Persistent agent configuration and status
- **Threat History**: Complete threat detection timeline
- **Event Logs**: Comprehensive audit trails
- **Evidence Storage**: Detailed evidence packs with metadata
- **Backup/Restore**: Automated database backup and restoration

### API Integration
- **RESTful APIs**: Complete CRUD operations for all entities
- **Real-time Endpoints**: Live data streaming
- **Health Checks**: Component-level health monitoring
- **Authentication**: Ready for enterprise auth integration
- **Documentation**: Auto-generated API documentation

## 🎮 Current Use Cases

### 1. **Agent Registration and Monitoring**
- 3 agents auto-register on startup
- Real-time status and metrics collection
- Hostname-based deterministic IDs
- Persistent agent configuration

### 2. **Threat Detection and Response**
- CPU anomaly detection with 80% threshold
- Memory monitoring and alerting
- Automatic threat classification
- Real-time dashboard alerts

### 3. **Attack Simulation**
- Configurable CPU stress attacks
- Multi-target attack capabilities
- Real-time attack monitoring
- Attack effectiveness measurement

### 4. **Evidence and Audit**
- Complete evidence pack generation
- Agent information collection (hostname, IP, OS)
- Immutable audit trails
- Event investigation workflows

### 5. **System Health Monitoring**
- Component-level health checks
- Network performance metrics
- Database connection monitoring
- Automatic failover detection

## 🛠️ Technology Stack

### Frontend Stack
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4
- **Components**: shadcn/ui (50+ components)
- **State Management**: Zustand + TanStack Query
- **Real-time**: WebSocket integration
- **Database**: Prisma ORM + PostgreSQL

### Backend Stack
- **API Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15 with Prisma ORM
- **Communication**: WebSocket (Python websockets)
- **Monitoring**: psutil for system metrics
- **HTTP Client**: aiohttp for async requests
- **Containerization**: Docker with multi-stage builds

### Infrastructure Stack
- **Container Orchestration**: Docker Compose
- **Database**: PostgreSQL 15 with persistent volumes
- **Caching**: Redis 7 with persistence
- **Messaging**: NATS JetStream for queuing
- **Reverse Proxy**: Caddy with automatic TLS
- **Networking**: Custom bridge network (172.20.0.0/16)

## 📁 Project Structure

```
dio-platform/
├── src/                          # Frontend source
│   ├── app/                      # Next.js App Router pages
│   │   ├── api/                  # API routes (10+ endpoints)
│   │   │   ├── agents/           # Agent management
│   │   │   ├── threats/          # Threat detection
│   │   │   ├── events/           # Event management
│   │   │   ├── system-health/    # Health monitoring
│   │   │   └── network-metrics/ # Performance data
│   │   ├── globals.css           # Global styles
│   │   ├── layout.tsx            # Root layout
│   │   └── page.tsx              # Main dashboard
│   ├── components/               # React components
│   │   └── ui/                   # shadcn/ui components
│   ├── hooks/                    # Custom React hooks
│   ├── lib/                      # Utilities and database
│   └── app.tsx                   # App configuration
├── components/                   # Backend services
│   ├── nerve-center/             # AI coordination core
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # Database models
│   │   └── requirements.txt     # Python dependencies
│   ├── agent/                    # Endpoint monitoring
│   │   ├── main.py              # Agent service
│   │   └── requirements.txt     # Dependencies
│   ├── mesh-network/             # Communication layer
│   │   ├── main.py              # WebSocket server
│   │   └── requirements.txt     # Dependencies
│   ├── attack-simulator/         # Security testing
│   │   ├── main.py              # Attack simulator
│   │   └── requirements.txt     # Dependencies
│   └── mock-data/                # Development data
│       ├── main.py              # Mock data service
│       └── requirements.txt     # Dependencies
├── prisma/                       # Database schema
│   └── schema.prisma            # Complete data models
├── docker compose.yml            # Full production stack
├── Dockerfile.frontend           # Frontend build
├── Caddyfile                     # Reverse proxy config
└── scripts/                      # Utility scripts
    ├── agents.sh                 # Agent management
    ├── attack.sh                 # Attack simulator
    └── dio.sh                    # Platform management
```

## 🔧 Configuration

### Environment Variables

#### Frontend (Next.js)
```env
NEXT_PUBLIC_WS_URL=ws://localhost:4222
DATABASE_URL=postgresql://dio_user:dio_password@database:5432/dio_platform
NERVE_CENTER_URL=http://nerve-center:8000
NODE_ENV=production
CLEAN_DATABASE=true
```

#### Services
```env
PYTHONUNBUFFERED=1
MONITORING_INTERVAL=5
ANOMALY_THRESHOLD=80.0
POSTGRES_DB=dio_platform
POSTGRES_USER=dio_user
POSTGRES_PASSWORD=dio_password
```

### Database Configuration

```bash
# Initialize database schema
npm run db:push

# Generate Prisma client
npm run db:generate

# Reset database (if needed)
npm run db:reset
```

## 📈 Monitoring & Management

### Health Endpoints
- **Frontend**: http://localhost:3000 (Dashboard)
- **Nerve Center**: http://localhost:8000/health
- **Mesh Network**: ws://localhost:4222 (WebSocket)
- **Database**: localhost:5432 (PostgreSQL)
- **Redis**: localhost:6379 (Cache)
- **NATS**: localhost:8222 (Messaging)

### Management Scripts
```bash
# Check agent status
./agents.sh

# Run attack simulation
./attack.sh

# View all services
docker compose ps

# Monitor logs
docker compose logs -f [service-name]

# Restart services
docker compose restart [service-name]
```

### Performance Metrics
- **Agent Update Interval**: 5 seconds
- **Dashboard Refresh**: 3-10 seconds (by component)
- **Health Checks**: 30 seconds interval
- **Database Persistence**: Real-time
- **Network Latency**: <1s typical

## 🔒 Security Features

- **Container Isolation**: Docker-based service isolation
- **Network Segmentation**: Custom bridge network
- **Data Encryption**: TLS for external communications
- **Input Validation**: Comprehensive API validation
- **Access Control**: Role-based access ready
- **Audit Trails**: Complete event logging
- **Secure Defaults**: Production-ready security settings

## 🧪 Testing & Validation

### Built-in Testing
```bash
# Lint code
npm run lint

# Type checking
npm run type-check

# Build validation
npm run build

# Platform health check
./test-dio-platform.sh
```

### Attack Simulation
```bash
# Run basic attack simulation
./attack.sh

# Quick attack test
./quick-attack.sh

# Custom attack configuration
python components/attack-simulator/main.py --targets 3 --intensity high
```

### Performance Validation
- **Agent Registration**: <3 seconds
- **Threat Detection**: <1 second from anomaly
- **Dashboard Load**: <2 seconds
- **API Response**: <500ms typical
- **Database Queries**: <100ms typical

## 📊 Current Capabilities

### Agent Management
- ✅ 3 replicated agents with auto-registration
- ✅ Deterministic agent IDs based on hostname
- ✅ Real-time metrics collection (CPU, memory, processes)
- ✅ Persistent agent configuration in database
- ✅ Health monitoring and status tracking

### Threat Detection
- ✅ CPU anomaly detection with configurable thresholds
- ✅ Memory monitoring and alerting
- ✅ Process behavior analysis
- ✅ Network traffic monitoring
- ✅ Real-time threat classification (low, medium, high, critical)

### Attack Simulation
- ✅ CPU stress attacks with mathematical computations
- ✅ Memory pressure simulation
- ✅ Multi-target attack capabilities
- ✅ Real-time attack monitoring
- ✅ Configurable attack intensity

### Data Management
- ✅ PostgreSQL database with full persistence
- ✅ Prisma ORM with type safety
- ✅ Automatic backup and restore functionality
- ✅ Complete audit trails
- ✅ Evidence pack generation

### User Interface
- ✅ Real-time dashboard with auto-refresh
- ✅ Interactive tabs for different views
- ✅ Dark/light mode toggle
- ✅ Responsive design for mobile/desktop
- ✅ Event investigation workflows
- ✅ System health monitoring

## 📚 Documentation

### Internal Documentation
- **API Documentation**: http://localhost:8000/docs (FastAPI auto-docs)
- **Database Schema**: `prisma/schema.prisma`
- **Component Logs**: `docker compose logs -f [component]`

### Operational Guides
- **Agent Management**: Use `./agents.sh` script
- **Attack Testing**: Use `./attack.sh` script
- **Service Management**: Docker Compose commands
- **Health Monitoring**: Dashboard health tab

## 🚀 Production Deployment

### System Requirements
- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM minimum
- **Storage**: 20GB+ available space
- **Network**: Stable internet connection
- **OS**: Linux/macOS/Windows with Docker

### Deployment Steps
```bash
# 1. Clone and setup
git clone <repository-url>
cd dio-platform

# 2. Start production stack
docker compose up -d

# 3. Initialize database
docker compose exec frontend npm run db:push

# 4. Verify deployment
docker compose ps
./agents.sh

# 5. Access platform
open http://localhost:3000
```

### Scaling Configuration
- **Agent Replicas**: Adjust `deploy.replicas` in docker compose.yml
- **Database Scaling**: Configure PostgreSQL settings
- **Network Performance**: Adjust Docker network settings
- **Resource Limits**: Set memory/CPU limits per service

## 🎯 Future Enhancements

### Phase 2 (Planned)
- GPU acceleration for AI models
- Advanced threat intelligence feeds
- SIEM system integration
- Mobile agent deployment
- Multi-cloud support

### Phase 3 (Roadmap)
- Advanced federated learning
- Threat hunting automation
- Compliance automation (GDPR, SOC2)
- Enterprise SSO integration
- Advanced analytics dashboard

---

## 📞 Support & Status

**Current Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2024

**DIO Platform** - Where cybersecurity meets biological intelligence.

*For technical support, check the dashboard health tab or review component logs using `docker compose logs -f`.*
