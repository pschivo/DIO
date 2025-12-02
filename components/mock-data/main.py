import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
import aiohttp
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockDataService:
    def __init__(self):
        self.nerve_center_url = 'http://nerve-center:8000'
        self.mesh_network_url = 'ws://mesh-network:4222'
        self.agents = []
        self.threats = []
        self.session = None
        
        # Mock data configuration
        self.num_agents = 12
        self.threat_probability = 0.1  # 10% chance per cycle
        self.update_interval = 10  # seconds
        
    async def generate_agents(self) -> List[Dict[str, Any]]:
        """Generate mock agent data"""
        agent_templates = [
            {'name_prefix': 'WebServer', 'os_type': 'Ubuntu 22.04', 'ip_prefix': '192.168.1.'},
            {'name_prefix': 'Database', 'os_type': 'Ubuntu 22.04', 'ip_prefix': '192.168.2.'},
            {'name_prefix': 'Workstation', 'os_type': 'Windows 11', 'ip_prefix': '192.168.3.'},
            {'name_prefix': 'DevMachine', 'os_type': 'macOS 13', 'ip_prefix': '192.168.4.'}
        ]
        
        agents = []
        for i in range(self.num_agents):
            template = random.choice(agent_templates)
            agent = {
                'id': f"agent-{i+1:03d}",
                'name': f"{template['name_prefix']}-{i+1:03d}",
                'hostname': f"endpoint-{i+1:03d}.local",
                'ip_address': f"{template['ip_prefix']}{100+i}",
                'os_type': template['os_type'],
                'status': random.choice(['active', 'active', 'active', 'warning']),  # More active
                'rank': random.choices([0, 1, 2, 3, 4], weights=[40, 30, 20, 8, 2])[0],
                'cpu': random.uniform(10, 90),
                'memory': random.uniform(20, 85),
                'disk': random.uniform(30, 70),
                'network': random.uniform(5, 60),
                'processes': random.randint(50, 300),
                'threats': random.randint(0, 5),
                'last_seen': datetime.now().isoformat()
            }
            agents.append(agent)
        
        return agents
    
    def generate_threats(self) -> List[Dict[str, Any]]:
        """Generate mock threat data"""
        threat_types = [
            {
                'name': 'Suspicious Process Activity',
                'type': 'anomaly',
                'severity_choices': ['low', 'medium', 'high'],
                'description': 'Unusual CPU usage detected in system processes'
            },
            {
                'name': 'Network Anomaly Detected',
                'type': 'intrusion',
                'severity_choices': ['medium', 'high', 'critical'],
                'description': 'Unusual network traffic pattern detected'
            },
            {
                'name': 'File Integrity Violation',
                'type': 'malware',
                'severity_choices': ['high', 'critical'],
                'description': 'Critical system file modification detected'
            },
            {
                'name': 'Unauthorized Access Attempt',
                'type': 'intrusion',
                'severity_choices': ['medium', 'high'],
                'description': 'Failed login attempts from unknown source'
            },
            {
                'name': 'Data Exfiltration Risk',
                'type': 'data_breach',
                'severity_choices': ['high', 'critical'],
                'description': 'Unusual data transfer patterns detected'
            }
        ]
        
        threats = []
        for _ in range(random.randint(1, 4)):
            threat_template = random.choice(threat_types)
            threat = {
                'id': f"threat-{uuid.uuid4().hex[:8]}",
                'name': threat_template['name'],
                'type': threat_template['type'],
                'severity': random.choice(threat_template['severity_choices']),
                'description': threat_template['description'],
                'status': random.choice(['active', 'investigating', 'contained']),
                'detected_at': (datetime.now() - timedelta(minutes=random.randint(5, 120))).isoformat(),
                'agent_id': random.choice(self.agents)['id'] if self.agents else None
            }
            threats.append(threat)
        
        return threats
    
    async def register_agents(self):
        """Register mock agents with nerve center"""
        logger.info("Registering mock agents...")
        
        for agent in self.agents:
            try:
                registration_data = {
                    'id': agent['id'],
                    'name': agent['name'],
                    'hostname': agent['hostname'],
                    'ip_address': agent['ip_address'],
                    'os_type': agent['os_type']
                }
                
                async with self.session.post(
                    f"{self.nerve_center_url}/agents/register",
                    json=registration_data
                ) as response:
                    if response.status == 200:
                        logger.info(f"Registered agent: {agent['id']}")
                    else:
                        logger.error(f"Failed to register agent {agent['id']}: {response.status}")
                        
            except Exception as e:
                logger.error(f"Error registering agent {agent['id']}: {e}")
    
    async def send_agent_metrics(self):
        """Send mock metrics for all agents"""
        for agent in self.agents:
            # Update metrics with some randomness
            agent['cpu'] = max(0, min(100, agent['cpu'] + random.uniform(-10, 10)))
            agent['memory'] = max(0, min(100, agent['memory'] + random.uniform(-5, 5)))
            agent['network'] = max(0, min(100, agent['network'] + random.uniform(-15, 15)))
            agent['processes'] = max(10, agent['processes'] + random.randint(-20, 20))
            agent['last_seen'] = datetime.now().isoformat()
            
            # Randomly change status
            if random.random() < 0.05:  # 5% chance
                agent['status'] = random.choice(['active', 'warning', 'offline'])
            
            try:
                metrics_data = {
                    'cpu': agent['cpu'],
                    'memory': agent['memory'],
                    'disk': agent['disk'],
                    'network': agent['network'],
                    'processes': agent['processes']
                }
                
                async with self.session.post(
                    f"{self.nerve_center_url}/agents/{agent['id']}/metrics",
                    json=metrics_data
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to send metrics for {agent['id']}: {response.status}")
                        
            except Exception as e:
                logger.error(f"Error sending metrics for {agent['id']}: {e}")
    
    async def send_threats(self):
        """Send mock threats to nerve center"""
        if random.random() < self.threat_probability:
            new_threats = self.generate_threats()
            
            for threat in new_threats:
                try:
                    async with self.session.post(
                        f"{self.nerve_center_url}/threats",
                        json=threat
                    ) as response:
                        if response.status == 200:
                            logger.info(f"Created threat: {threat['name']}")
                            self.threats.append(threat)
                        else:
                            logger.error(f"Failed to create threat: {response.status}")
                            
                except Exception as e:
                    logger.error(f"Error creating threat: {e}")
    
    async def send_evidence(self, threat: Dict[str, Any]):
        """Send evidence for a threat"""
        try:
            evidence_data = {
                'agent_id': threat.get('agent_id', 'unknown'),
                'type': threat['type'],
                'severity': threat['severity'],
                'title': f"Evidence: {threat['name']}",
                'description': threat['description'],
                'raw_data': {
                    'threat_id': threat['id'],
                    'detection_method': 'ai_anomaly_detection',
                    'confidence_score': random.uniform(0.7, 0.95)
                },
                'confidence': random.uniform(0.7, 0.95)
            }
            
            async with self.session.post(
                f"{self.nerve_center_url}/evidence",
                json=evidence_data
            ) as response:
                if response.status == 200:
                    logger.info(f"Created evidence for threat: {threat['id']}")
                else:
                    logger.error(f"Failed to create evidence: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error creating evidence: {e}")
    
    async def update_system_health(self):
        """Update system health metrics"""
        components = ['nerve_center', 'mesh_network', 'database']
        
        for component in components:
            try:
                health_data = {
                    'component': component,
                    'status': random.choices(['healthy', 'healthy', 'healthy', 'warning'], weights=[70, 20, 5, 5])[0],
                    'cpu': random.uniform(10, 80),
                    'memory': random.uniform(20, 90),
                    'disk': random.uniform(30, 85),
                    'network': random.uniform(5, 70),
                    'uptime': random.randint(3600, 86400)
                }
                
                # This would be sent to a health endpoint if available
                logger.debug(f"Health update for {component}: {health_data['status']}")
                
            except Exception as e:
                logger.error(f"Error updating health for {component}: {e}")
    
    async def run_simulation(self):
        """Main simulation loop"""
        logger.info("Starting mock data simulation")
        
        # Generate initial data
        self.agents = await self.generate_agents()
        logger.info(f"Generated {len(self.agents)} mock agents")
        
        # Register agents
        await self.register_agents()
        
        # Main loop
        while True:
            try:
                # Send metrics
                await self.send_agent_metrics()
                
                # Send threats
                await self.send_threats()
                
                # Update system health
                await self.update_system_health()
                
                # Send evidence for existing threats
                for threat in random.sample(self.threats, min(3, len(self.threats))):
                    await self.send_evidence(threat)
                
                logger.info(f"Simulation cycle completed. Active agents: {len([a for a in self.agents if a['status'] == 'active'])}")
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in simulation cycle: {e}")
                await asyncio.sleep(self.update_interval)
    
    async def start(self):
        """Start the mock data service"""
        logger.info("Starting DIO Mock Data Service")
        
        # Create HTTP session
        self.session = aiohttp.ClientSession()
        
        try:
            await self.run_simulation()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Mock data service error: {e}")
        finally:
            if self.session:
                await self.session.close()

async def main():
    """Main entry point"""
    service = MockDataService()
    await service.start()

if __name__ == "__main__":
    asyncio.run(main())