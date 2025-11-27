# 🎯 DIO Attack Simulator Guide

## Overview

The DIO Attack Simulator is a comprehensive testing tool designed to simulate various types of cyber attacks against the DIO platform. This allows you to test the detection capabilities, response times, and overall effectiveness of your security agents.

## 🚀 Quick Start

### Prerequisites
- DIO Platform must be running (`start.sh dev` or `start.bat dev`)
- Docker must be available
- Access to terminal/command prompt

### Launch Attack Simulator

**Linux/Mac:**
```bash
# Make script executable
chmod +x attack.sh

# Run specific attack
./attack.sh cpu

# Interactive mode
./attack.sh interactive

# Run attack sequence
./attack.sh sequence
```

**Windows:**
```cmd
# Run specific attack
attack.bat cpu

# Interactive mode
attack.bat interactive

# Run attack sequence
attack.bat sequence
```

## 🔥 Attack Types

### 1. CPU Exhaustion Attack (`cpu`)
**Simulates:** Cryptocurrency mining malware or resource-intensive attacks

**Behavior:**
- Gradually increases CPU usage from 50% to 95%
- Creates high-priority threat alerts
- Generates evidence packs with confidence scores
- Simulates recovery phase

**Expected Detection:**
- CPU anomaly detection within 5 seconds
- Threat classification: "Resource Exhaustion"
- Severity: High
- Evidence: Process analysis, resource usage patterns

### 2. Memory Leak Attack (`memory`)
**Simulates:** Memory corruption or leak-based attacks

**Behavior:**
- Gradually increases memory usage from 40% to 95%
- Creates sustained high memory usage
- Triggers memory-based anomaly detection

**Expected Detection:**
- Memory anomaly detection within 10 seconds
- Threat classification: "Memory Corruption"
- Severity: High
- Evidence: Memory usage patterns, process analysis

### 3. Network Flood Attack (`network`)
**Simulates:** DDoS attacks or network-based floods

**Behavior:**
- Spikes network usage to 70-95%
- Simulates high packet volume
- Creates network-based threat alerts

**Expected Detection:**
- Network anomaly detection within 3 seconds
- Threat classification: "Network Flood"
- Severity: Critical
- Evidence: Traffic analysis, packet counts

### 4. Process Anomaly Attack (`process`)
**Simulates:** Process injection or suspicious process creation

**Behavior:**
- Creates unusual process count spikes (300-500 processes)
- Simulates malicious process execution
- Triggers process-based monitoring

**Expected Detection:**
- Process anomaly detection within 8 seconds
- Threat classification: "Process Injection"
- Severity: Medium
- Evidence: Process lists, execution patterns

### 5. File Integrity Attack (`file`)
**Simulates:** System file modification or ransomware activity

**Behavior:**
- Simulates critical system file modification
- Creates immediate high-severity alerts
- Generates comprehensive evidence packs

**Expected Detection:**
- File integrity violation detection within 2 seconds
- Threat classification: "File Integrity Violation"
- Severity: Critical
- Evidence: File change logs, checksum analysis

### 6. Multi-Vector Attack (`multi`)
**Simulates:** Coordinated attacks using multiple techniques

**Behavior:**
- Executes sequence of different attack types
- Demonstrates correlation capabilities
- Tests coordinated response mechanisms

**Expected Detection:**
- Multi-vector threat correlation
- Coordinated response across attack vectors
- Comprehensive evidence collection

### 7. Lateral Movement Attack (`lateral`)
**Simulates:** Attack spreading across multiple agents

**Behavior:**
- Compromises multiple agents sequentially
- Simulates internal network propagation
- Tests isolation and containment capabilities

**Expected Detection:**
- Cross-agent threat correlation
- Lateral movement pattern detection
- Network segmentation effectiveness

## 🎮 Interactive Mode

The interactive mode provides a user-friendly interface for launching attacks:

```bash
./attack.sh interactive
```

**Features:**
- Menu-driven attack selection
- Real-time agent status display
- Attack progress monitoring
- Multiple attack combinations

## 📊 Monitoring Attack Results

### Dashboard Monitoring
1. **Open Dashboard:** http://localhost:3000
2. **Navigate to "Threats" tab** to see detected attacks
3. **Check "Agents" tab** to see affected agents
4. **Review "System Health"** for overall impact

### API Monitoring
1. **API Documentation:** http://localhost:8000/docs
2. **Agent Status:** http://localhost:8000/agents
3. **Threat List:** http://localhost:8000/threats
4. **System Status:** http://localhost:8000/system/status

### Evidence Analysis
Each attack generates comprehensive evidence packs containing:
- Attack timeline and progression
- System metrics and anomalies
- Confidence scores and classifications
- Raw data for forensic analysis

## 🧪 Testing Scenarios

### Scenario 1: Single Attack Testing
Test individual attack types to verify specific detection capabilities:

```bash
# Test CPU-based detection
./attack.sh cpu

# Test network-based detection  
./attack.sh network

# Test file integrity monitoring
./attack.sh file
```

### Scenario 2: Attack Sequence Testing
Run predefined sequence to test overall system response:

```bash
# Run complete attack sequence
./attack.sh sequence
```

This executes: CPU → Memory → Network → Process → File attacks

### Scenario 3: Random Attack Testing
Test system resilience against unexpected attack patterns:

```bash
# Run random attacks
./attack.sh random
```

### Scenario 4: Stress Testing
Launch multiple simultaneous attacks:

```bash
# Terminal 1: CPU attack
./attack.sh cpu

# Terminal 2: Network attack  
./attack.sh network

# Terminal 3: Process attack
./attack.sh process
```

## 📈 Success Metrics

### Detection Time
- **Excellent:** < 2 seconds
- **Good:** 2-5 seconds  
- **Acceptable:** 5-10 seconds
- **Poor:** > 10 seconds

### Response Accuracy
- **True Positive Rate:** > 95%
- **False Positive Rate:** < 5%
- **Classification Accuracy:** > 90%

### Evidence Quality
- **Completeness:** > 95%
- **Accuracy:** > 90%
- **Confidence Score:** > 0.8

## 🔧 Advanced Configuration

### Custom Attack Parameters
Modify attack behavior by editing the simulator:

```python
# In components/attack-simulator/main.py

await simulator.simulate_cpu_exhaustion_attack(
    agent_id="agent-001",    # Target specific agent
    duration=60              # Attack duration in seconds
)
```

### Attack Intensity
Adjust attack severity and detection thresholds:

```python
# CPU exhaustion parameters
cpu_usage = min(95, 50 + (time.time() - start_time) * 1.5)  # Gradual increase

# Network flood parameters  
network_usage = random.uniform(70, 95)  # Random spikes
```

### Custom Attack Scenarios
Create new attack types by extending the simulator:

```python
async def simulate_custom_attack(self, agent_id: str = None):
    # Custom attack logic here
    pass
```

## 🛡️ Testing Agent Capabilities

### Autonomous Response
- Verify agents automatically throttle suspicious processes
- Check isolation mechanisms activate correctly
- Confirm evidence collection is complete

### Federated Learning
- Monitor model improvement after attack detection
- Verify threat intelligence sharing between agents
- Check rank progression for successful detections

### Network Resilience
- Test mesh network during attacks
- Verify communication persists under stress
- Check message delivery and correlation

## 📝 Testing Checklist

### Pre-Attack Preparation
- [ ] DIO platform running and healthy
- [ ] Dashboard accessible at http://localhost:3000
- [ ] At least 3 agents active
- [ ] Mock data service running

### During Attack
- [ ] Monitor real-time dashboard updates
- [ ] Verify threat detection within expected time
- [ ] Check evidence pack generation
- [ ] Monitor system health impact

### Post-Attack Analysis
- [ ] Review threat classification accuracy
- [ ] Analyze evidence completeness
- [ ] Check agent response effectiveness
- [ ] Verify system recovery

### Documentation
- [ ] Record detection times
- [ ] Document false positives/negatives
- [ ] Note system performance impact
- [ ] Collect lessons learned

## 🚨 Safety Notes

⚠️ **Important:** This is a simulation environment only
- All attacks are simulated through API calls
- No actual system compromise occurs
- Network traffic is simulated, not real
- File modifications are virtual

✅ **Safe Testing Practices:**
- Use isolated development environment
- Monitor system resources during testing
- Stop attacks if system becomes unstable
- Keep backups of configuration data

---

This attack simulator provides comprehensive testing capabilities for the DIO platform, allowing you to validate detection effectiveness, response times, and overall security posture in a controlled, safe environment.