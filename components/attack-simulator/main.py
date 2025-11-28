import asyncio
import aiohttp
import json
import random
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
import uuid

# Agent data storage
agents = {}

# Agent class definition
class Agent:
    def __init__(self, id: str, name: str, hostname: str, status: str, rank: int, 
                 cpu: float, memory: float, lastSeen: str, threats: int, 
                 ipAddress: str, osType: str, version: str):
        self.id = id
        self.name = name
        self.hostname = hostname
        self.status = status
        self.rank = rank
        self.cpu = cpu
        self.memory = memory
        self.lastSeen = lastSeen
        self.threats = threats
        self.ipAddress = ipAddress
        self.osType = osType
        self.version = version

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttackSimulator:
    def __init__(self):
        self.nerve_center_url = 'http://nerve-center:8000'  # Use Docker service name
        self.session = None
        self.attack_scenarios = []
        
    async def start(self):
        """Initialize the attack simulator"""
        self.session = aiohttp.ClientSession()
        logger.info("🎯 DIO Attack Simulator Started")
        logger.info("Use simulate_attack() to launch specific attack scenarios")
        
        # Give database time to initialize
        await asyncio.sleep(1)  # Wait for database to be ready
        
        # Check for existing agents - DO NOT CREATE NEW ONES
        existing_agents = await self.get_agents()
        if len(existing_agents) == 0:
            logger.warning("⚠️ No agents found in system. Attack simulator requires existing agents to simulate attacks.")
            logger.info("💡 Attack simulator will only simulate attacks on existing agents.")
        else:
            logger.info(f"✅ Found {len(existing_agents)} existing agents ready for attack simulation")
            for agent in existing_agents[:3]:  # Show first 3 agents
                logger.info(f"   - {agent.get('id', 'unknown')} ({agent.get('name', 'unknown')})")
        
    async def stop(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
    
    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get list of active agents"""
        try:
            async with self.session.get(f"{self.nerve_center_url}/agents") as response:
                if response.status == 200:
                    data = await response.json()
                    # Handle both list and object with 'data' property
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'data' in data:
                        return data['data']
                    else:
                        return []
                return []
        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            return []
    
    async def send_agent_metrics(self, agent_id: str, metrics: Dict[str, Any]):
        """Send metrics to specific agent using main agents API"""
        try:
            # Use the main agents API instead of direct metrics endpoint
            response = await self.session.post(
                f"{self.nerve_center_url}/agents/{agent_id}/metrics",
                json=metrics
            )
            
            if response.status == 200:
                logger.info(f"✅ Metrics sent to main API for agent {agent_id}")
                return True
            else:
                logger.error(f"Failed to send metrics to main API for agent {agent_id}: {response.status}")
                return False
        except Exception as e:
            logger.error(f"Error sending metrics to main API for agent {agent_id}: {e}")
            return False
    
    async def create_threat(self, threat_data: Dict[str, Any]):
        """Create a threat in the system"""
        try:
            async with self.session.post(
                f"{self.nerve_center_url}/threats",
                json=threat_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"🚨 Threat created: {threat_data['name']}")
                    return result.get('threat_id')
                else:
                    logger.error(f"Failed to create threat: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error creating threat: {e}")
            return None
    
    async def create_evidence(self, evidence_data: Dict[str, Any]):
        """Create evidence for an attack"""
        try:
            async with self.session.post(
                f"{self.nerve_center_url}/evidence",
                json=evidence_data
            ) as response:
                if response.status == 200:
                    logger.info(f"📋 Evidence created: {evidence_data['title']}")
                    return True
                else:
                    logger.error(f"Failed to create evidence: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error creating evidence: {e}")
            return False

    # ==================== ATTACK SCENARIOS ====================
    
    async def validate_agent_exists(self, agent_id: str) -> bool:
        """Validate that an agent exists before attacking it"""
        try:
            response = await self.session.get(f"{self.nerve_center_url}/agents/{agent_id}")
            return response.status == 200
        except Exception as e:
            logger.error(f"Error validating agent {agent_id}: {e}")
            return False
    
    async def send_attack_simulation_to_agents(self, target_agents: list, attack_type: str, intensity: float = 0.9):
        """Send attack simulation data to agents so they can detect and report real threats"""
        for agent_id in target_agents:
            try:
                # Send simulated attack metrics to agent for detection
                attack_metrics = {
                    'attack_simulation': True,
                    'attack_type': attack_type,
                    'intensity': intensity,
                    'duration': 30,  # seconds
                    'timestamp': datetime.now().isoformat()
                }
                
                response = await self.session.post(
                    f"{self.nerve_center_url}/agents/{agent_id}/simulate-attack",
                    json=attack_metrics
                )
                
                if response.status == 200:
                    logger.info(f"✅ Attack simulation sent to agent {agent_id} for {attack_type} detection")
                else:
                    logger.warning(f"⚠️ Failed to send attack simulation to agent {agent_id}")
                    
            except Exception as e:
                logger.error(f"Error sending attack simulation to agent {agent_id}: {e}")
    
    async def simulate_cpu_exhaustion_attack(self, agent_id: str = None, duration: int = 30):
        """
        Simulate CPU exhaustion attack (cryptocurrency mining)
        
        Args:
            agent_id: Target agent (random if None)
            duration: Attack duration in seconds
        """
        logger.info(f"🔥 Starting CPU Exhaustion Attack on agent {agent_id or 'random'}")
        
        agents = await self.get_agents()
        if not agents:
            logger.error("No agents available")
            return
        
        if agent_id == 'all':
            # Run attack on ALL agents
            target_agents = [agent['id'] for agent in agents]
            logger.info(f"🎯 Running CPU exhaustion attack on ALL {len(agents)} agents: {target_agents}")
        else:
            # Validate that the specified agent exists
            if agent_id:
                # Check if the specified agent exists
                existing_agent_ids = [agent['id'] for agent in agents]
                if agent_id not in existing_agent_ids:
                    logger.error(f"❌ Agent '{agent_id}' not found in system. Available agents: {existing_agent_ids}")
                    logger.error(f"💡 To create new agents, modify AGENT_COUNT in docker-compose.yml")
                    return
                target_agents = [agent_id]
                logger.info(f"🎯 Running CPU exhaustion attack on specific agent: {agent_id}")
            else:
                # Run on random agent
                target_agents = [random.choice(agents)['id']]
                logger.info(f"🎯 Running CPU exhaustion attack on random agent: {target_agents[0]}")
        
        attack_id = str(uuid.uuid4())
        
        # NOTE: Attack simulator should ONLY perform attacks, NOT create threats
        # Agents should detect the actual system anomalies and report them
        logger.info(f"🔥 Starting real CPU attack - agents should detect this and report threats")
        
        # Send attack simulation to agents for detection
        await self.send_attack_simulation_to_agents(target_agents, 'cpu_exhaustion', 0.9)
        
        # Also perform actual system CPU attack to affect real metrics
        logger.info(f"🔥 Performing actual CPU-intensive operations...")
        
        # Simulate escalating CPU usage by actually consuming CPU
        start_time = time.time()
        cpu_load_processes = []
        
        try:
            # Start CPU-intensive processes to actually load the system
            import subprocess
            import signal
            
            # Create multiple CPU-intensive processes
            for i in range(4):  # Start 4 processes
                proc = subprocess.Popen([
                    'python3', '-c', '''
import time
import math
import random

# CPU-intensive computation
start_time = time.time()
while time.time() - start_time < 30:  # Run for 30 seconds
    # Perform intensive calculations
    result = 0
    for i in range(1000000):
        result += math.sqrt(random.random() * 1000000)
        if i % 10000 == 0:
            time.sleep(0.01)  # Small sleep to allow other processes
'''
                ])
                cpu_load_processes.append(proc)
                logger.info(f"Started CPU-intensive process {i+1} with PID: {proc.pid}")
            
            # Monitor and send metrics for each target agent
            while time.time() - start_time < duration:
                # Gradually increase simulated CPU usage for reporting
                cpu_usage = min(95, 50 + (time.time() - start_time) * 1.5)
                
                # Send metrics to each target agent
                for target_agent in target_agents:
                    metrics = {
                        'cpu': cpu_usage + random.uniform(-5, 5),
                        'memory': random.uniform(60, 85),
                        'disk': random.uniform(40, 60),
                        'network': random.uniform(10, 30),
                        'processes': random.randint(150, 300) + len(cpu_load_processes)  # Include real processes
                    }
                    
                    await self.send_agent_metrics(target_agent, metrics)
                    
                    # Create evidence for critical CPU usage
                    if cpu_usage > 85:
                        await self.create_evidence({
                            'agent_id': target_agent,
                            'type': 'cpu_anomaly',
                            'severity': 'critical',
                            'title': f'Critical CPU Usage Detected - {target_agent}',
                            'description': f'CPU usage reached {cpu_usage:.1f}%, indicating potential crypto-mining malware',
                            'raw_data': {
                                'attack_id': attack_id,
                                'cpu_usage': cpu_usage,
                                'timestamp': datetime.now().isoformat(),
                                'attack_type': 'cpu_exhaustion',
                                'active_processes': len(cpu_load_processes)
                            },
                            'confidence': min(1.0, cpu_usage / 100)
                        })
                    
                    await asyncio.sleep(0.5)  # Small delay between agents
            
        except Exception as e:
            logger.error(f"Error in CPU attack simulation: {e}")
        finally:
            # Clean up CPU-intensive processes
            for i, proc in enumerate(cpu_load_processes):
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                    logger.info(f"Terminated CPU-intensive process {i+1}")
                except:
                    pass
        
        # Recovery phase
        logger.info(f"🔄 Recovery phase - CPU usage returning to normal")
        for target_agent in target_agents:
            for i in range(5):
                metrics = {
                    'cpu': max(10, 95 - i * 15),
                    'memory': random.uniform(40, 60),
                    'disk': random.uniform(40, 60),
                    'network': random.uniform(10, 30),
                    'processes': random.randint(80, 150)
                }
                await self.send_agent_metrics(target_agent, metrics)
                await asyncio.sleep(0.5)  # Small delay between agents
        
        logger.info(f"✅ CPU Exhaustion Attack completed on {len(target_agents)} agents")
        return attack_id
    
    async def simulate_memory_leak_attack(self, agent_id: str = None, duration: int = 25):
        """
        Simulate memory leak attack
        
        Args:
            agent_id: Target agent (random if None)
            duration: Attack duration in seconds
        """
        logger.info(f"💾 Starting Memory Leak Attack on agent {agent_id or 'random'}")
        
        agents = await self.get_agents()
        if not agents:
            logger.error("No agents available")
            return
        
        if agent_id == 'all':
            # Run attack on ALL agents
            target_agents = [agent['id'] for agent in agents]
            logger.info(f"🎯 Running memory leak attack on ALL {len(agents)} agents: {target_agents}")
        else:
            # Validate that the specified agent exists
            if agent_id:
                # Check if the specified agent exists
                existing_agent_ids = [agent['id'] for agent in agents]
                if agent_id not in existing_agent_ids:
                    logger.error(f"❌ Agent '{agent_id}' not found in system. Available agents: {existing_agent_ids}")
                    logger.error(f"💡 To create new agents, modify AGENT_COUNT in docker-compose.yml")
                    return
                target_agents = [agent_id]
                logger.info(f"🎯 Running memory leak attack on specific agent: {agent_id}")
            else:
                # Run on random agent
                target_agents = [random.choice(agents)['id']]
                logger.info(f"🎯 Running memory leak attack on random agent: {target_agents[0]}")
        
        attack_id = str(uuid.uuid4())
        
        # NOTE: Attack simulator should ONLY perform attacks, NOT create threats
        # Agents should detect the actual system anomalies and report them
        logger.info(f"💾 Starting real memory attack - agents should detect this and report threats")
        
        # Send attack simulation to agents for detection
        await self.send_attack_simulation_to_agents(target_agents, 'memory_leak', 0.85)
        
        # Also perform actual system memory attack to affect real metrics
        logger.info(f"💾 Performing actual memory-intensive operations...")
        
        start_time = time.time()
        base_memory = 40
        
        # Run attack simulation for each target agent
        for target_agent in target_agents:
            start_time = time.time()
            base_memory = 40
            memory_hog_processes = []
            
            try:
                # Start memory-intensive processes to actually consume memory
                import subprocess
                import gc
                
                # Create memory hog processes
                for i in range(3):  # Start 3 processes
                    proc = subprocess.Popen([
                        'python3', '-c', '''
import time
import random

# Memory-intensive allocation
memory_blocks = []
try:
    for i in range(100):  # Allocate memory in chunks
        # Allocate 10MB block
        block = bytearray(10 * 1024 * 1024)  # 10MB
        memory_blocks.append(block)
        time.sleep(0.1)  # Small delay to allow allocation
    
    # Hold memory for duration
    start_time = time.time()
    while time.time() - start_time < 25:  # Hold for 25 seconds
        time.sleep(1)
        
except MemoryError:
    print("Memory limit reached, continuing...")
    time.sleep(25)
finally:
    # Clean up memory blocks
    memory_blocks = []
    gc.collect()
'''
                    ])
                    memory_hog_processes.append(proc)
                    logger.info(f"Started memory-intensive process {i+1} with PID: {proc.pid}")
                
                while time.time() - start_time < duration:
                    # Gradually increase memory usage
                    elapsed = time.time() - start_time
                    memory_usage = min(95, base_memory + elapsed * 2)
                    
                    metrics = {
                        'cpu': random.uniform(20, 40),
                        'memory': memory_usage + random.uniform(-3, 3),
                        'disk': random.uniform(40, 60),
                        'network': random.uniform(5, 15),
                        'processes': random.randint(100, 200) + len(memory_hog_processes)
                    }
                    
                    await self.send_agent_metrics(target_agent, metrics)
                    
                    # Create evidence for high memory usage
                    if memory_usage > 80:
                        await self.create_evidence({
                            'agent_id': target_agent,
                            'type': 'memory_anomaly',
                            'severity': 'high',
                            'title': f'Memory Leak Detected - {target_agent}',
                            'description': f'Memory usage reached {memory_usage:.1f}%, indicating potential memory leak attack',
                            'raw_data': {
                                'attack_id': attack_id,
                                'memory_usage': memory_usage,
                                'timestamp': datetime.now().isoformat(),
                                'attack_type': 'memory_leak',
                                'active_processes': len(memory_hog_processes)
                            },
                            'confidence': min(1.0, memory_usage / 100)
                        })
                    
                    await asyncio.sleep(1)  # Small delay between updates
                
            except Exception as e:
                logger.error(f"Error in memory leak attack for {target_agent}: {e}")
            finally:
                # Clean up memory hog processes
                for i, proc in enumerate(memory_hog_processes):
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                        logger.info(f"Terminated memory-intensive process {i+1}")
                    except:
                        pass
        
        logger.info(f"✅ Memory Leak Attack completed on {len(target_agents)} agents")
        return attack_id
    
    async def simulate_network_flood_attack(self, agent_id: str = None, duration: int = 20):
        """
        Simulate network flood/DDoS attack
        
        Args:
            agent_id: Target agent (random if None)
            duration: Attack duration in seconds
        """
        logger.info(f"🌊 Starting Network Flood Attack on agent {agent_id or 'random'}")
        
        agents = await self.get_agents()
        if not agents:
            logger.error("No agents available")
            return
        
        if agent_id == 'all':
            # Run attack on ALL agents
            target_agents = [agent['id'] for agent in agents]
            logger.info(f"🎯 Running network flood attack on ALL {len(agents)} agents: {target_agents}")
        else:
            # Validate that the specified agent exists
            if agent_id:
                existing_agent_ids = [agent['id'] for agent in agents]
                if agent_id not in existing_agent_ids:
                    logger.error(f"❌ Agent '{agent_id}' not found in system. Available agents: {existing_agent_ids}")
                    logger.error(f"💡 To create new agents, modify AGENT_COUNT in docker-compose.yml")
                    return
                target_agents = [agent_id]
                logger.info(f"🎯 Running network flood attack on specific agent: {agent_id}")
            else:
                # Run on random agent
                target_agents = [random.choice(agents)['id']]
                logger.info(f"🎯 Running network flood attack on random agent: {target_agents[0]}")
        
        attack_id = str(uuid.uuid4())
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Simulate network traffic spikes
            network_usage = random.uniform(70, 95)
            
            metrics = {
                'cpu': random.uniform(30, 60),
                'memory': random.uniform(40, 70),
                'disk': random.uniform(40, 60),
                'network': network_usage,
                'processes': random.randint(120, 250)
            }
            
            await self.send_agent_metrics(target_agent, metrics)
            
            # Create evidence for network anomaly
            if network_usage > 85:
                await self.create_evidence({
                    'agent_id': target_agent,
                    'type': 'network_anomaly',
                    'severity': 'critical',
                    'title': f'Network Flood Detected - {target_agent}',
                    'description': f'Network usage reached {network_usage:.1f}%, indicating potential DDoS attack',
                    'raw_data': {
                        'attack_id': attack_id,
                        'network_usage': network_usage,
                        'timestamp': datetime.now().isoformat(),
                        'attack_type': 'network_flood',
                        'packets_per_second': random.randint(10000, 50000)
                    },
                    'confidence': min(1.0, network_usage / 100)
                })
            
            await asyncio.sleep(1)
        
        logger.info(f"✅ Network Flood Attack completed on {target_agent}")
        return attack_id
    
    async def simulate_process_anomaly_attack(self, agent_id: str = None, duration: int = 15):
        """
        Simulate suspicious process creation attack
        
        Args:
            agent_id: Target agent (random if None)
            duration: Attack duration in seconds
        """
        logger.info(f"⚙️ Starting Process Anomaly Attack on agent {agent_id or 'random'}")
        
        agents = await self.get_agents()
        if not agents:
            logger.error("No agents available")
            return
        
        target_agent = random.choice(agents)['id'] if agent_id == 'all' else (agent_id or random.choice(agents)['id'])
        attack_id = str(uuid.uuid4())
        
        # Create threat
        await self.create_threat({
            'name': f'Process Anomaly Attack - {target_agent}',
            'type': 'process_injection',
            'severity': 'medium',
            'description': 'Unusual process creation and execution detected',
            'agent_id': target_agent
        })
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Simulate unusual process count spikes
            process_count = random.randint(300, 500)
            
            metrics = {
                'cpu': random.uniform(40, 70),
                'memory': random.uniform(50, 80),
                'disk': random.uniform(40, 60),
                'network': random.uniform(20, 40),
                'processes': process_count
            }
            
            await self.send_agent_metrics(target_agent, metrics)
            
            # Create evidence for process anomaly
            if process_count > 400:
                await self.create_evidence({
                    'agent_id': target_agent,
                    'type': 'process_anomaly',
                    'severity': 'medium',
                    'title': f'Suspicious Process Activity - {target_agent}',
                    'description': f'Unusual process count detected: {process_count} processes',
                    'raw_data': {
                        'attack_id': attack_id,
                        'process_count': process_count,
                        'timestamp': datetime.now().isoformat(),
                        'attack_type': 'process_anomaly',
                        'suspicious_processes': [
                            'malware.exe',
                            'crypto_miner.exe',
                            'backdoor.dll'
                        ]
                    },
                    'confidence': min(1.0, process_count / 500)
                })
            
            await asyncio.sleep(2)
        
        logger.info(f"✅ Process Anomaly Attack completed on {target_agent}")
        return attack_id
    
    async def simulate_file_integrity_attack(self, agent_id: str = None):
        """
        Simulate file integrity violation attack
        
        Args:
            agent_id: Target agent (random if None)
        """
        logger.info(f"📁 Starting File Integrity Attack on agent {agent_id or 'random'}")
        
        agents = await self.get_agents()
        if not agents:
            logger.error("No agents available")
            return
        
        target_agent = random.choice(agents)['id'] if agent_id == 'all' else (agent_id or random.choice(agents)['id'])
        attack_id = str(uuid.uuid4())
        
        # Create critical threat
        threat_id = await self.create_threat({
            'name': f'File Integrity Violation - {target_agent}',
            'type': 'file_integrity',
            'severity': 'critical',
            'description': 'Critical system file modification detected',
            'agent_id': target_agent
        })
        
        # Simulate normal metrics with sudden file integrity alert
        metrics = {
            'cpu': random.uniform(20, 40),
            'memory': random.uniform(40, 60),
            'disk': random.uniform(40, 60),
            'network': random.uniform(10, 20),
            'processes': random.randint(80, 150)
        }
        
        await self.send_agent_metrics(target_agent, metrics)
        
        # Create critical evidence
        await self.create_evidence({
            'agent_id': target_agent,
            'type': 'file_integrity',
            'severity': 'critical',
            'title': f'Critical System File Modified - {target_agent}',
            'description': 'Unauthorized modification of critical system file detected',
            'raw_data': {
                'attack_id': attack_id,
                'modified_files': [
                    '/etc/passwd',
                    '/usr/bin/sudo',
                    'C:\\Windows\\System32\\kernel32.dll'
                ],
                'checksum_mismatch': True,
                'timestamp': datetime.now().isoformat(),
                'attack_type': 'file_integrity',
                'integrity_violations': 3
            },
            'confidence': 0.95
        })
        
        logger.info(f"✅ File Integrity Attack completed on {target_agent}")
        return attack_id
    
    # ==================== COMPLEX ATTACK SCENARIOS ====================
    
    async def simulate_multi_vector_attack(self, agent_id: str = None):
        """
        Simulate coordinated multi-vector attack
        """
        logger.info(f"🎯 Starting Multi-Vector Attack on agent {agent_id or 'random'}")
        
        agents = await self.get_agents()
        if not agents:
            logger.error("No agents available")
            return
        
        if agent_id == 'all':
            # Run attack on ALL agents
            target_agents = [agent['id'] for agent in agents]
            logger.info(f"🎯 Running lateral movement attack on ALL {len(agents)} agents: {target_agents}")
        else:
            # Validate that the specified agent exists
            if agent_id:
                existing_agent_ids = [agent['id'] for agent in agents]
                if agent_id not in existing_agent_ids:
                    logger.error(f"❌ Agent '{agent_id}' not found in system. Available agents: {existing_agent_ids}")
                    logger.error(f"💡 To create new agents, modify AGENT_COUNT in docker-compose.yml")
                    return
                target_agents = [agent_id]
                logger.info(f"🎯 Running lateral movement attack on specific agent: {agent_id}")
            else:
                # Run on random agent
                target_agents = [random.choice(agents)['id']]
                logger.info(f"🎯 Running lateral movement attack on random agent: {target_agents[0]}")
        
        attack_id = str(uuid.uuid4())
        
        # Execute attack sequence
        logger.info("Phase 1: Network reconnaissance")
        await asyncio.sleep(2)
        
        logger.info("Phase 2: Process injection")
        await self.simulate_process_anomaly_attack(target_agent, duration=10)
        await asyncio.sleep(3)
        
        logger.info("Phase 3: Resource exhaustion")
        await self.simulate_cpu_exhaustion_attack(target_agent, duration=15)
        await asyncio.sleep(3)
        
        logger.info("Phase 4: File system compromise")
        await self.simulate_file_integrity_attack(target_agent)
        
        logger.info(f"✅ Multi-Vector Attack completed on {target_agent}")
    
    async def simulate_lateral_movement_attack(self):
        """Simulate lateral movement attack"""
        logger.info("🔓 Starting Lateral Movement Attack")
        
        agents = await self.get_agents()
        if not agents:
            logger.error("No agents available for lateral movement simulation")
            return
        
        # Simulate attacker moving from one compromised agent to others
        compromised_agent = random.choice(agents)['id']
        target_agents = [agent['id'] for agent in agents if agent['id'] != compromised_agent]
        
        logger.info(f"🎯 Compromised agent: {compromised_agent}")
        logger.info(f"🎯 Target agents: {target_agents}")
        
        attack_id = str(uuid.uuid4())
        
        # Create initial compromise threat
        await self.create_threat({
            'name': f'Lateral Movement - {compromised_agent}',
            'type': 'lateral_movement',
            'severity': 'critical',
            'description': f'Lateral movement detected from {compromised_agent}',
            'agent_id': compromised_agent
        })
        
        # Simulate lateral movement to each target
        for i, target_agent in enumerate(target_agents[:3]):  # Limit to 3 targets
            logger.info(f"🔓 Moving laterally from {compromised_agent} to {target_agent}")
            
            # Create evidence of lateral movement attempt
            await self.create_evidence({
                'agent_id': target_agent,
                'type': 'lateral_movement',
                'severity': 'high',
                'title': f'Lateral Movement Attempt - {target_agent}',
                'description': f'Suspicious lateral movement from {compromised_agent} detected',
                'raw_data': {
                    'attack_id': attack_id,
                    'source_agent': compromised_agent,
                    'attack_vector': 'pass_the_hash',
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.9
            })
            
            # Simulate some metrics on target
            metrics = {
                'cpu': random.uniform(60, 85),
                'memory': random.uniform(50, 75),
                'disk': random.uniform(30, 50),
                'network': random.uniform(40, 80),
                'processes': random.randint(200, 400)
            }
            
            await self.send_agent_metrics(target_agent, metrics)
            await asyncio.sleep(2)  # Simulate movement time
        
        logger.info(f"✅ Lateral Movement Attack completed")
        return attack_id

    async def simulate_privilege_escalation_attack(self, agent_id: str = None):
        """Simulate privilege escalation attack"""
        logger.info(f"🔑 Starting Privilege Escalation Attack on agent {agent_id or 'random'}")
        
        agents = await self.get_agents()
        if not agents:
            logger.error("No agents available for privilege escalation simulation")
            return
        
        target_agent = agent_id or random.choice(agents)['id']
        attack_id = str(uuid.uuid4())
        
        # Create privilege escalation threat
        await self.create_threat({
            'name': f'Privilege Escalation - {target_agent}',
            'type': 'privilege_escalation',
            'severity': 'critical',
            'description': f'Privilege escalation attempt detected on {target_agent}',
            'agent_id': target_agent
        })
        
        # Simulate escalating privileges with suspicious activity
        escalation_phases = [
            {'cpu': random.uniform(70, 95), 'memory': random.uniform(60, 90), 'processes': random.randint(300, 500)},
            {'cpu': random.uniform(80, 100), 'memory': random.uniform(70, 95), 'processes': random.randint(400, 600)},
            {'cpu': random.uniform(90, 100), 'memory': random.uniform(80, 100), 'processes': random.randint(500, 700)}
        ]
        
        for i, phase_metrics in enumerate(escalation_phases):
            logger.info(f"🔑 Escalation phase {i+1} on {target_agent}")
            
            await self.create_evidence({
                'agent_id': target_agent,
                'type': 'privilege_escalation',
                'severity': 'critical',
                'title': f'Privilege Escalation Phase {i+1} - {target_agent}',
                'description': f'Privilege escalation phase {i+1} with elevated privileges detected',
                'raw_data': {
                    'attack_id': attack_id,
                    'escalation_phase': i + 1,
                    'privileges_gained': ['admin', 'root', 'system'] if i == 2 else ['user', 'power_user'],
                    'attack_vector': 'exploit_vulnerability',
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.95
            })
            
            await self.send_agent_metrics(target_agent, phase_metrics)
            await asyncio.sleep(3)  # Simulate escalation time
        
        logger.info(f"✅ Privilege Escalation Attack completed on {target_agent}")
        return attack_id

    async def simulate_data_exfiltration_attack(self, agent_id: str = None):
        """Simulate data exfiltration attack"""
        logger.info(f"💾 Starting Data Exfiltration Attack on agent {agent_id or 'random'}")
        
        agents = await self.get_agents()
        if not agents:
            logger.error("No agents available for data exfiltration simulation")
            return
        
        target_agent = agent_id or random.choice(agents)['id']
        attack_id = str(uuid.uuid4())
        
        # Create data exfiltration threat
        await self.create_threat({
            'name': f'Data Exfiltration - {target_agent}',
            'type': 'data_exfiltration',
            'severity': 'critical',
            'description': f'Data exfiltration detected from {target_agent}',
            'agent_id': target_agent
        })
        
        # Simulate data theft phases
        exfiltration_data = [
            {'size_mb': 50, 'type': 'credentials', 'severity': 'high'},
            {'size_mb': 200, 'type': 'documents', 'severity': 'critical'},
            {'size_mb': 500, 'type': 'database', 'severity': 'critical'}
        ]
        
        for i, data in enumerate(exfiltration_data):
            logger.info(f"💾 Exfiltrating {data['type']} data ({data['size_mb']}MB) from {target_agent}")
            
            await self.create_evidence({
                'agent_id': target_agent,
                'type': 'data_exfiltration',
                'severity': 'critical',
                'title': f'Data Exfiltration - {data["type"]} - {target_agent}',
                'description': f'Exfiltration of {data["type"]} data ({data["size_mb"]}MB) detected',
                'raw_data': {
                    'attack_id': attack_id,
                    'data_type': data['type'],
                    'data_size_mb': data['size_mb'],
                    'exfiltration_method': 'encrypted_channel',
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.98
            })
            
            # Simulate network traffic for exfiltration
            metrics = {
                'cpu': random.uniform(40, 70),
                'memory': random.uniform(30, 60),
                'disk': random.uniform(20, 40),
                'network': random.uniform(80, 100),  # High network for exfil
                'processes': random.randint(150, 300)
            }
            
            await self.send_agent_metrics(target_agent, metrics)
            await asyncio.sleep(2)  # Simulate exfiltration time
        
        logger.info(f"✅ Data Exfiltration Attack completed on {target_agent}")
        return attack_id

    async def simulate_ransomware_attack(self, agent_id: str = None):
        """Simulate ransomware attack"""
        logger.info(f"🔒 Starting Ransomware Attack on agent {agent_id or 'random'}")
        
        agents = await self.get_agents()
        if not agents:
            logger.error("No agents available for ransomware simulation")
            return
        
        target_agent = agent_id or random.choice(agents)['id']
        attack_id = str(uuid.uuid4())
        
        # Create ransomware threat
        await self.create_threat({
            'name': f'Ransomware Infection - {target_agent}',
            'type': 'ransomware',
            'severity': 'critical',
            'description': f'Ransomware infection detected on {target_agent}',
            'agent_id': target_agent
        })
        
        # Simulate ransomware encryption phases
        encryption_phases = [
            {'cpu': random.uniform(60, 80), 'memory': random.uniform(50, 70), 'disk_io': random.uniform(50, 80)},
            {'cpu': random.uniform(80, 95), 'memory': random.uniform(70, 85), 'disk_io': random.uniform(70, 90)},
            {'cpu': random.uniform(95, 100), 'memory': random.uniform(85, 95), 'disk_io': random.uniform(85, 95)}
        ]
        
        for i, phase_metrics in enumerate(encryption_phases):
            logger.info(f"🔒 Ransomware encryption phase {i+1} on {target_agent}")
            
            await self.create_evidence({
                'agent_id': target_agent,
                'type': 'ransomware',
                'severity': 'critical',
                'title': f'Ransomware Encryption Phase {i+1} - {target_agent}',
                'description': f'Ransomware encryption phase {i+1} with high disk I/O detected',
                'raw_data': {
                    'attack_id': attack_id,
                    'encryption_phase': i + 1,
                    'files_encrypted': random.randint(1000, 5000),
                    'ransom_note': f'PAY_{random.randint(100000, 999999)}.BTC',
                    'attack_vector': 'phishing_email',
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.99
            })
            
            await self.send_agent_metrics(target_agent, phase_metrics)
            await asyncio.sleep(4)  # Simulate encryption time
        
        # Final ransom note
        await self.create_evidence({
            'agent_id': target_agent,
            'type': 'ransomware',
            'severity': 'critical',
            'title': f'Ransomware Demand - {target_agent}',
            'description': f'Ransomware demand note left for {target_agent}',
            'raw_data': {
                'attack_id': attack_id,
                'final_phase': 'complete',
                'ransom_amount': random.randint(5, 50),  # BTC
                'payment_deadline': (datetime.now() + timedelta(hours=48)).isoformat(),
                'timestamp': datetime.now().isoformat()
            },
            'confidence': 1.0
        })
        
        logger.info(f"✅ Ransomware Attack completed on {target_agent}")
        return attack_id
        """
        Simulate lateral movement across multiple agents
        """
        logger.info("🔄 Starting Lateral Movement Attack")
        
        agents = await self.get_agents()
        if len(agents) < 3:
            logger.error("Need at least 3 agents for lateral movement simulation")
            return
        
        # Select sequential targets
        target_agents = random.sample(agents, min(5, len(agents)))
        
        for i, agent in enumerate(target_agents):
            logger.info(f"Stage {i+1}: Compromising agent {agent['id']}")
            
            # Create lateral movement threat
            await self.create_threat({
                'name': f'Lateral Movement - Stage {i+1}',
                'type': 'lateral_movement',
                'severity': 'high',
                'description': f'Attack spreading from agent {target_agents[i-1]["id"] if i > 0 else "external"} to {agent["id"]}',
                'agent_id': agent['id']
            })
            
            # Simulate brief compromise
            await self.simulate_process_anomaly_attack(agent['id'], duration=8)
            await asyncio.sleep(2)
        
        logger.info("✅ Lateral Movement Attack completed")
    
    # ==================== INTERACTIVE MODE ====================
    
    async def interactive_mode(self):
        """Interactive attack simulation mode"""
        print("\n🎯 DIO Attack Simulator - Interactive Mode")
        print("=" * 50)
        print("Available attack scenarios:")
        print("1. CPU Exhaustion Attack")
        print("2. Memory Leak Attack")
        print("3. Network Flood Attack")
        print("4. Process Anomaly Attack")
        print("5. File Integrity Attack")
        print("6. Multi-Vector Attack")
        print("7. Lateral Movement Attack")
        print("8. Random Attack Sequence")
        print("9. List Agents")
        print("0. Exit")
        print("=" * 50)
        
        agents = await self.get_agents()
        if agents:
            print(f"\n📊 Active Agents: {len(agents)}")
            for agent in agents[:5]:
                print(f"  • {agent['id']} ({agent['name']}) - {agent['status']}")
        
        while True:
            try:
                choice = input("\nSelect attack scenario (0-9): ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    await self.simulate_cpu_exhaustion_attack()
                elif choice == '2':
                    await self.simulate_memory_leak_attack()
                elif choice == '3':
                    await self.simulate_network_flood_attack()
                elif choice == '4':
                    await self.simulate_process_anomaly_attack()
                elif choice == '5':
                    await self.simulate_file_integrity_attack()
                elif choice == '6':
                    await self.simulate_multi_vector_attack()
                elif choice == '7':
                    await self.simulate_lateral_movement_attack()
                elif choice == '8':
                    # Random attack sequence
                    attacks = [
                        self.simulate_cpu_exhaustion_attack,
                        self.simulate_memory_leak_attack,
                        self.simulate_network_flood_attack,
                        self.simulate_process_anomaly_attack,
                        self.simulate_file_integrity_attack
                    ]
                    for _ in range(random.randint(2, 4)):
                        attack = random.choice(attacks)
                        await attack()
                        await asyncio.sleep(5)
                elif choice == '9':
                    agents = await self.get_agents()
                    print(f"\n📊 Active Agents: {len(agents)}")
                    for agent in agents:
                        print(f"  • {agent['id']} ({agent['name']}) - {agent['status']}")
                else:
                    print("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error during attack simulation: {e}")

async def main():
    """Main entry point for attack simulator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DIO Attack Simulator')
    parser.add_argument('attack_type', 
                       choices=['cpu', 'memory', 'network', 'process', 'file', 'multi', 'lateral', 'interactive'],
                       help='Type of attack to simulate')
    parser.add_argument('--agent', 
                       help='Target agent ID or "all" for all agents')
    parser.add_argument('--duration', 
                       type=int, 
                       default=30,
                       help='Attack duration in seconds (default: 30)')
    
    args = parser.parse_args()
    
    simulator = AttackSimulator()
    
    try:
        await simulator.start()
        
        if args.attack_type == 'interactive':
            await simulator.interactive_mode()
        elif args.attack_type == 'cpu':
            await simulator.simulate_cpu_exhaustion_attack(args.agent, args.duration)
        elif args.attack_type == 'memory':
            await simulator.simulate_memory_leak_attack(args.agent, args.duration)
        elif args.attack_type == 'network':
            await simulator.simulate_network_flood_attack(args.agent, args.duration)
        elif args.attack_type == 'process':
            await simulator.simulate_process_anomaly_attack(args.agent, args.duration)
        elif args.attack_type == 'file':
            await simulator.simulate_file_integrity_attack(args.agent)
        elif args.attack_type == 'multi':
            await simulator.simulate_multi_vector_attack(args.agent, args.duration)
        elif args.attack_type == 'lateral':
            await simulator.simulate_lateral_movement_attack(args.duration)
        else:
            print(f"Unknown attack type: {args.attack_type}")
            print(f"Available attack types: cpu, memory, network, process, file, multi, lateral, privilege, exfiltration, ransomware, test, sequence")
        logger.info("Attack simulator stopped by user")
    except Exception as e:
        logger.error(f"Attack simulator error: {e}")
    finally:
        await simulator.stop()

if __name__ == "__main__":
    asyncio.run(main())