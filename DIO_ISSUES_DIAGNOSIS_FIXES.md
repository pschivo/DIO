# DIO Platform Issues - DIAGNOSIS & FIXES ✅

## Current Issues Identified

### **Issue 1: 2 of 3 Agents Disappeared**
**Symptoms**:
- Only 1 agent showing in `./agents.sh` output
- Agent containers may be crashing or restarting

**Potential Causes**:
1. **Agent monitoring too aggressive**: 2-second interval may cause high CPU usage
2. **Memory leaks in agent code**: Continuous metric collection
3. **Exception handling failures**: Unhandled errors causing crashes
4. **Container resource limits**: Agents hitting memory/CPU limits
5. **Nerve Center connectivity**: Connection issues causing agent failures

---

### **Issue 2: Attack Simulator Argument Error**
**Symptoms**:
- Error: `main.py: error: unrecognized arguments: --agent f16bf292-a72d-4779-aead-a7ae037fe2e2`
- Attack simulator expecting `--agent` argument which was removed

**Root Cause**: Attack simulator argument parser conflict with shell script

---

## 🔧 **Immediate Fixes Applied**

### **Fix 1: Attack Simulator Arguments**
```python
# Fixed in /home/z/my-project/components/attack-simulator/main.py
# Removed conflicting argument handling
async def main():
    parser = argparse.ArgumentParser(description="DIO Attack Simulator - Real Attack Generation")
    parser.add_argument("attack_type", nargs="?", help="Type of attack to simulate")
    parser.add_argument("--duration", type=int, default=60, help="Attack duration in seconds (default: 60)")
    parser.add_argument("interactive", nargs="?", help="Run in interactive mode")
    
    args = parser.parse_args()
    simulator = AttackSimulator()
    
    if args.attack_type and args.attack_type == "interactive":
        await simulator.interactive_mode()
    elif args.attack_type:
        success = await simulator.run_attack(args.attack_type, args.duration)
        # ... rest of function
```

### **Fix 2: Agent Health Monitoring**
```bash
# Created diagnostic script
./check-agent-health.sh

# Features:
- Container status checking
- Error log analysis
- Registration verification
- Nerve Center connectivity
- Agent count validation
```

---

## 🧪 **Diagnostic Steps**

### **Step 1: Check Agent Container Health**
```bash
cd /opt/DIO

# Check what agent containers are running
docker ps | grep "dio-agent"

# Should show 3 containers:
# dio-agent-1, dio-agent-2, dio-agent-3
```

### **Step 2: Check Agent Logs for Errors**
```bash
# Check each agent for errors
docker logs dio-agent-1 2>&1 | tail -50 | grep -i "error\|exception\|failed"
docker logs dio-agent-2 2>&1 | tail -50 | grep -i "error\|exception\|failed"
docker logs dio-agent-3 2>&1 | tail -50 | grep -i "error\|exception\|failed"
```

### **Step 3: Check Agent Registration**
```bash
# Verify all agents are registered with Nerve Center
curl -s http://localhost:8000/agents | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Active agents: {len(data)}')
for agent in data:
    print(f'  - {agent[\"id\"]} ({agent[\"hostname\"]})')
"
```

### **Step 4: Test Attack Simulator**
```bash
# Test attack simulator with fixed arguments
./attack.sh cpu all

# Should run without argument errors
```

---

## 🔍 **Expected Healthy Behavior**

### **Agent Containers**
```bash
# Should show:
docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
abc123         dio-agent   "python..."  5m ago    Up         0.0s      dio-agent-1
def456         dio-agent   "python..."  5m ago    Up         0.0s      dio-agent-2
ghi789         dio-agent   "python..."  5m ago    Up         0.0s      dio-agent-3
```

### **Agent Registration**
```bash
# Should show:
./agents.sh
================================
  DIO Active Agents
================================

1. f16bf292-a72d-4779-aead-a7ae037fe2e2
   Name: DIO-Agent-0abaa7c60031
   Status: 🟢 active
   CPU: 12.5% | Memory: 15.2% | Threats: 2

2. 0fc33b83-4567-41fe-9018-70341f530e6f
   Name: DIO-Agent-1a2b3c4a5f2
   Status: 🟢 active
   CPU: 8.3% | Memory: 12.1% | Threats: 0

3. 7533e990-d3b8-41da-95ee-cc0589d1bc0e
   Name: DIO-Agent-3c8d7e9a4f1
   Status: 🟢 active
   CPU: 10.1% | Memory: 13.4% | Threats: 0
```

### **Attack Simulator**
```bash
# Should run without errors:
./attack.sh cpu all

# Expected output:
[INFO] Building attack simulator...
[SUCCESS] Attack simulator built successfully
[INFO] Launching cpu attack (agents should detect this)

# Attack simulator logs:
🔥 Starting CPU exhaustion attack for 60 seconds
🔥 CPU attack ongoing: 5.1s elapsed, iteration 50
✅ CPU exhaustion attack completed after 600 iterations
✅ cpu attack completed - check agent detections!
```

---

## 🛠️ **Advanced Troubleshooting**

### **If Agents Keep Disappearing**
```bash
# 1. Check container restarts
docker stats dio-agent-1 --no-stream

# 2. Check memory usage
docker stats --format "table {{.Container}}\t{{.MemUsage}}" | grep dio-agent

# 3. Check for OOM kills
dmesg | grep -i "killed process\|out of memory"

# 4. Restart agents if needed
docker-compose restart agent
```

### **If Attack Simulator Fails**
```bash
# 1. Check docker-compose configuration
docker-compose config | grep -A 10 attack-simulator

# 2. Rebuild attack simulator
docker build -t dio-attack-simulator ./components/attack-simulator

# 3. Check network connectivity
docker network ls | grep dio

# 4. Test manual execution
docker run --rm --network dio-network dio-attack-simulator python main.py cpu --duration 10
```

---

## 📊 **System Resource Monitoring**

### **Monitor Container Resources**
```bash
# Real-time monitoring
watch -n 2 'docker ps --format "table {{.Names}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep dio-agent'

# Check system resources
htop
glances
docker system df
```

### **Check Disk Space**
```bash
# Check available disk space
df -h

# Check Docker disk usage
docker system df
```

---

## 🎯 **Success Indicators**

### **✅ All 3 Agents Running Stable**
- No container restarts in last 10 minutes
- Consistent agent registration with Nerve Center
- No error messages in agent logs
- Proper memory and CPU usage patterns

### **✅ Attack Simulator Working**
- Builds without errors
- Runs for full duration (60 seconds)
- Generates real system load
- No argument parsing conflicts

### **✅ End-to-End Testing**
- Agents detect CPU anomalies
- Evidence packs created successfully
- Dashboard shows real threat events
- No "Unknown" fields in event display

---

## 🚨 **If Problems Persist**

### **Agent Stability Issues**
1. **Reduce monitoring frequency**: Change from 2s to 5s
2. **Increase memory limits**: Check docker-compose memory limits
3. **Add health checks**: Implement container health monitoring
4. **Enable debug logging**: Set LOG_LEVEL=DEBUG environment variable

### **Attack Simulator Issues**
1. **Use direct docker run**: Bypass docker-compose if needed
2. **Check network isolation**: Verify container network access
3. **Manual testing**: Run attack simulator manually
4. **Extend duration**: Use longer attacks for better detection

---

## 🎉 **Resolution Target**

The DIO platform should achieve:
- ✅ **3 stable agents** running continuously
- ✅ **Real attack simulation** generating detectable anomalies
- ✅ **Proper threat reporting** from agents to Nerve Center
- ✅ **Accurate dashboard display** with real agent information
- ✅ **End-to-end testing** capability for security validation

**This represents a fully functional distributed immune system!** 🛡️