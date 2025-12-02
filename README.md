# DIO Platform - Digital Immune Organism

A comprehensive cybersecurity platform that simulates a self-evolving security architecture modeled after the human immune system.

## 🎯 Overview

The DIO (Digital Immune Organism) platform is a distributed AI-driven security system that provides:

- **Autonomous Threat Detection**: Real-time monitoring and response capabilities
- **Federated Learning**: Privacy-preserving collective intelligence
- **Mesh Network Communication**: Resilient peer-to-peer messaging
- **Agent-Based Architecture**: Scalable endpoint protection
- **Real-time Dashboard**: Comprehensive visibility and control

## 🏗️ Architecture

### Core Components

1. **Frontend Dashboard** (Next.js 15)
   - Real-time monitoring interface
   - Threat visualization and analysis
   - Agent management and control

2. **Nerve Center** (FastAPI)
   - AI coordination core
   - Federated learning orchestration
   - Evidence and explanation management

3. **Mesh Network** (WebSocket)
   - Resilient communication backbone
   - Room-based message routing
   - Fault-tolerant design

4. **Agents** (Python)
   - Endpoint monitoring
   - Autonomous threat response
   - Local anomaly detection

5. **Mock Data Service** (Development)
   - Realistic test data generation
   - Controlled threat simulation
   - Performance testing

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 4GB+ RAM
- Available ports: 3000, 8000, 4222

### Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd dio-platform

# Start with mock data
docker-compose --profile mock up -d

# Access the dashboard
open http://localhost:3000
```

### Production Environment

```bash
# Start production services
docker-compose --profile production up -d

# Initialize database
docker-compose exec frontend npm run db:push
```

## 📊 Features

### Real-time Monitoring
- Live agent status and metrics
- Threat detection and alerting
- System health monitoring
- Network performance metrics

### Autonomous Defense
- CPU and memory anomaly detection
- Process behavior analysis
- Network traffic monitoring
- File integrity verification

### Federated Learning
- Privacy-preserving model updates
- Collective intelligence sharing
- Adaptive threat detection
- Agent rank progression system

### Evidence & Audit
- Complete evidence packs
- AI-generated explanations
- Immutable audit trails
- Compliance reporting

## 🎮 Phase 1 POC Use Cases

1. **Autonomous Threat Detection and Response**
2. **Federated Learning for Adaptive Defense**
3. **Real-time Mesh Network Resilience**
4. **Multi-Vector Attack Coordination**
5. **Agent Promotion and Accountability System**

Detailed use case documentation: [PHASE1_USE_CASES.md](./PHASE1_USE_CASES.md)

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4
- **Components**: shadcn/ui
- **State**: Zustand + TanStack Query

### Backend
- **API**: FastAPI (Python 3.11)
- **Database**: SQLite (Dev) / PostgreSQL (Prod)
- **ORM**: Prisma
- **Real-time**: WebSocket (Socket.IO)
- **Containerization**: Docker

### Infrastructure
- **Communication**: Custom Mesh Network
- **Monitoring**: System metrics + health checks
- **Security**: mTLS, SPIFFE identities
- **Deployment**: Docker Compose

## 📁 Project Structure

```
dio-platform/
├── src/                          # Frontend source
│   ├── app/                      # Next.js App Router
│   ├── components/               # React components
│   ├── hooks/                    # Custom hooks
│   └── lib/                      # Utilities
├── components/                   # Backend services
│   ├── nerve-center/             # AI coordination
│   ├── agent/                    # Endpoint monitoring
│   ├── mesh-network/             # Communication
│   └── mock-data/                # Test data
├── prisma/                       # Database schema
├── docker-compose.yml            # Service orchestration
└── docs/                         # Documentation
```

## 🔧 Configuration

### Environment Variables

#### Frontend
```env
NEXT_PUBLIC_WS_URL=ws://localhost:4222
DATABASE_URL=sqlite:./db/app.db
```

#### Services
```env
NERVE_CENTER_URL=http://nerve-center:8000
MONITORING_INTERVAL=5
ANOMALY_THRESHOLD=80.0
```

### Database Setup

```bash
# Initialize database
npm run db:push

# Generate Prisma client
npm run db:generate
```

## 📈 Monitoring

### Health Endpoints
- Frontend: http://localhost:3000
- Nerve Center: http://localhost:8000/health
- Mesh Network: ws://localhost:4222

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nerve-center
```

## 🔒 Security

- **Transport Security**: mTLS encryption
- **Identity Management**: SPIFFE/SPIRE
- **Supply Chain**: Signed artifacts
- **Runtime Protection**: Sandboxed agents
- **Data Privacy**: Federated learning without raw data sharing

## 🧪 Testing

### Development Testing
```bash
# Run linting
npm run lint

# Type checking
npm run type-check

# Build test
npm run build
```

### POC Execution
1. Start services with mock data
2. Execute 5 defined use cases
3. Monitor success metrics
4. Collect performance data

## 📚 Documentation

- [Deployment Guide](./DEPLOYMENT.md)
- [Phase 1 Use Cases](./PHASE1_USE_CASES.md)
- [API Documentation](http://localhost:8000/docs)
- [Component Architecture](./docs/ARCHITECTURE.md)

## 🤝 Contributing

1. Follow established patterns
2. Maintain type safety
3. Update documentation
4. Test thoroughly
5. Use conventional commits

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Future Roadmap

### Phase 2
- GPU acceleration for AI models
- Advanced threat intelligence
- Integration with SIEM systems
- Mobile agent deployment

### Phase 3
- Multi-cloud deployment
- Advanced federated learning
- Threat hunting automation
- Compliance automation

---

**DIO Platform** - Where cybersecurity meets biological intelligence.