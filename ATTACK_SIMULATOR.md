# DIO Attack Simulator Guide

## 🎯 Overview

The DIO Attack Simulator is a comprehensive tool designed to test the detection and response capabilities of your DIO platform. It simulates various types of cyberattacks in a controlled environment, allowing you to validate that your agents, nerve center, and overall system are working correctly.

## 🚀 Quick Start

### Option 1: Use Attack Scripts (Recommended)

**Windows:**
```cmd
# List all available attacks
attack.bat help

# Launch specific attack
attack.bat cpu

# Interactive mode
attack.bat interactive

# Run attack sequence
attack.bat sequence
```

**Linux/Mac:**
```bash
# Make script executable
chmod +x attack.sh

# List all available attacks
./attack.sh help

# Launch specific attack
./attack.sh cpu

# Interactive mode
./attack.sh interactive

# Run attack sequence
./attack.sh sequence
```

### Option 2: Manual Docker Commands

```bash
# Build attack simulator
cd components/attack-simulator
docker build -t dio-attack-simulator .

# Run specific attack
docker run --rm --network dio-platform_dio-network dio-attack-simulator python main.py cpu

# Interactive mode
docker run --rm -it --network dio-platform_dio-network dio-attack-simulator python main.py interactive
```

## 🎭 Available Attack Scenarios

### 1. **CPU Exhaustion Attack** (`cpu`)
- **Simulates**: Cryptocurrency mining malware
- **Duration**: 30 seconds
- **Symptoms**: Gradually increasing CPU usage from 50% to 95%
- **Evidence**: Critical CPU usage alerts, process anomalies
- **Severity**: High

```bash
./attack.sh cpu
```

### 2. **Memory Leak Attack** (`memory`)
- **Simulates**: Process with memory leak
- **Duration**: 25 seconds
- **Symptoms**: Gradually increasing memory usage from 40% to 95%
- **Evidence**: Memory anomaly alerts, resource exhaustion
- **Severity**: High

```bash
./attack.sh memory
```

### 3. **Network Flood Attack** (`network`)
- **Simulates**: DDoS attack or network flood
- **Duration**: 20 seconds
- **Symptoms**: Network usage spikes to 70-95%
- **Evidence**: Network anomaly alerts, traffic analysis
- **Severity**: Critical

```bash
./attack.sh network
```

### 4. **Process Anomaly Attack** (`process`)
- **Simulates**: Suspicious process creation/injection
- **Duration**: 15 seconds
- **Symptoms**: Process count spikes to 300-500
- **Evidence**: Process anomaly alerts, suspicious process names
- **Severity**: Medium

```bash
./attack.sh process
```

### 5. **File Integrity Attack** (`file`)
- **Simulates**: Critical system file modification
- **Duration**: Immediate
- **Symptoms**: File integrity violations
- **Evidence**: Critical file modification alerts, checksum mismatches
- **Severity**: Critical

```bash
./attack.sh file
```

### 6. **Multi-Vector Attack** (`multi`)
- **Simulates**: Coordinated attack using multiple vectors
- **Duration**: ~60 seconds
- **Phases**: Recon → Process injection → Resource exhaustion → File compromise
- **Evidence**: Multiple correlated threat alerts
- **Severity**: Critical

```bash
./attack.sh multi
```

### 7. **Lateral Movement Attack** (`lateral`)
- **Simulates**: Attack spreading across multiple agents
- **Duration**: Varies by number of agents
- **Symptoms**: Sequential compromise of multiple endpoints
- **Evidence**: Lateral movement alerts, attack chain analysis
- **Severity**: High

```bash
./attack.sh lateral
```

## 🎮 Interactive Mode

Launch the interactive mode for a menu-driven experience:

```bash
./attack.sh interactive
```

**Interactive Features:**
- Menu-driven attack selection
- Real-time agent listing
- Random attack sequences
- Continuous attack simulation

## 🔄 Attack Sequences

### Predefined Sequence
Runs all basic attack types in sequence with delays:

```bash
./attack.sh sequence
```

**Sequence Order:**
1. CPU Exhaustion → 10s delay
2. Memory Leak → 10s delay
3. Network Flood → 10s delay
4. Process Anomaly → 10s delay
5. File Integrity

### Random Sequence
Runs 3-5 random attacks:

```bash
./attack.sh random
```

## 📊 Monitoring Attack Results

### Real-time Dashboard
Watch attacks in real-time at: **http://localhost:3000**

**What to look for:**
- **Threats Tab**: New threats appearing with correct severity
- **Agents Tab**: Target agents showing status changes
- **Overview Tab**: Real-time threat count increases
- **Network Tab**: Mesh network activity

### Evidence Analysis
Each attack generates detailed evidence packs:
- **Attack ID**: Unique identifier for correlation
- **Confidence Score**: AI confidence in detection (0.0-1.0)
- **Raw Data**: Technical details for forensics
- **Timestamp**: Precise attack timing

### API Monitoring
Check threat creation via API:
```bash
curl http://localhost:8000/threats
```

Check evidence creation:
```bash
curl http://localhost:8000/evidence
```

## 🎯 Testing Scenarios

### Scenario 1: Single Agent Detection
```bash
# Start DIO platform
./start.sh dev

# Wait for agents to register (30 seconds)
./attack.sh status

# Launch attack on specific agent
./attack.sh cpu
```

### Scenario 2: Multi-Agent Coordination
```bash
# Launch lateral movement attack
./attack.sh lateral

# Watch how threat spreads across agents
# Check mesh network coordination
```

### Scenario 3: Stress Testing
```bash
# Run multiple attacks in sequence
./attack.sh sequence

# Follow with random attacks
./attack.sh random

# Monitor system performance under load
```

### Scenario 4: Recovery Testing
```bash
# Launch severe attack
./attack.sh multi

# Monitor automatic recovery
# Check evidence pack completeness
# Verify agent rank progression
```

## 🔍 Validation Checklist

### ✅ Attack Detection
- [ ] Threat appears in dashboard within 5 seconds
- [ ] Correct severity classification
- [ ] Appropriate threat type assigned
- [ ] Target agent correctly identified

### ✅ Evidence Generation
- [ ] Evidence pack created for each attack
- [ ] Confidence score > 0.7 for clear attacks
- [ ] Raw data contains relevant technical details
- [ ] Timestamps correlate with attack timing

### ✅ Agent Response
- [ ] Target agent status changes (active → warning)
- [ ] Metrics reflect attack characteristics
- [ ] Autonomous response initiated
- [ ] Recovery phase completes successfully

### ✅ System Coordination
- [ ] Nerve center receives alerts
- [ ] Mesh network broadcasts threat intelligence
- [ ] Other agents show awareness
- [ ] No single points of failure

### ✅ Dashboard Updates
- [ ] Real-time threat count updates
- [ ] Agent status reflects current state
- [ ] Evidence appears in evidence tab
- [ ] System health indicators update

## 🛠️ Advanced Usage

### Custom Attack Parameters
Modify attack behavior by editing the simulator:

```python
# In components/attack-simulator/main.py
await simulator.simulate_cpu_exhaustion_attack(
    agent_id="agent-001",  # Target specific agent
    duration=45              # Custom duration
)
```

### Targeting Specific Agents
```bash
# Get list of agents
curl http://localhost:8000/agents

# Target specific agent
docker run --rm --network dio-platform_dio-network dio-attack-simulator \
    python main.py cpu agent-001
```

### Continuous Attack Simulation
```bash
# Run attacks in loop
while true; do
    ./attack.sh random
    sleep 30
done
```

## 🔧 Troubleshooting

### Common Issues

**"No agents available"**
- Ensure DIO platform is running: `./start.sh dev`
- Wait 30 seconds for agent registration
- Check agent status: `./attack.sh status`

**"Failed to create threat"**
- Verify nerve center is accessible: `curl http://localhost:8000/health`
- Check network connectivity
- Restart attack simulator container

**"Attack not visible in dashboard"**
- Refresh browser
- Check WebSocket connection
- Verify real-time updates are enabled

**"Evidence not generated"**
- Check nerve center logs: `docker-compose logs nerve-center`
- Verify database connectivity
- Restart mock data service

### Debug Mode
Enable detailed logging:
```bash
docker run --rm --network dio-platform_dio-network \
    -e LOG_LEVEL=DEBUG \
    dio-attack-simulator python main.py cpu
```

## 📈 Performance Metrics

### Expected Detection Times
- **CPU/Memory Attacks**: < 5 seconds
- **Network Attacks**: < 3 seconds
- **File Integrity**: < 2 seconds
- **Multi-Vector**: < 10 seconds (first vector)

### Expected Evidence Quality
- **Confidence Score**: > 0.8 for clear attacks
- **Data Completeness**: > 95% relevant fields populated
- **Correlation**: Proper attack chain linking

### System Performance
- **Dashboard Latency**: < 2 seconds
- **API Response**: < 500ms
- **Mesh Network**: < 100ms message delivery

---

**🎯 The DIO Attack Simulator provides comprehensive testing capabilities to validate your cybersecurity platform's detection and response mechanisms. Use it regularly to ensure your system remains effective against evolving threats!**