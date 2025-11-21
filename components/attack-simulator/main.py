import asyncio
import aiohttp
import json
import random
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
import uuid

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
        """Send metrics to specific agent"""
        try:
            async with self.session.post(
                f"{self.nerve_center_url}/agents/{agent_id}/metrics",
                json=metrics
            ) as response:
                if response.status == 200:
                    return True
                else:
                    logger.error(f"Failed to send metrics to {agent_id}: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error sending metrics to {agent_id}: {e}")
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
            # Run on specific or random agent
            target_agents = [agent_id or random.choice(agents)['id']]
            logger.info(f"🎯 Running CPU exhaustion attack on agent: {target_agents[0]}")
        
        attack_id = str(uuid.uuid4())
        
        # Create threat for each target agent
        for target_agent in target_agents:
            await self.create_threat({
                'name': f'CPU Exhaustion Attack - {target_agent}',
                'type': 'crypto_mining',
                'severity': 'high',
                'description': 'Cryptocurrency mining malware detected',
                'agent_id': target_agent
            })
        
        # Run attack simulation for each target agent
        for target_agent in target_agents:
            await self.create_threat({
                'name': f'CPU Exhaustion Attack - {target_agent}',
                'type': 'crypto_mining',
                'severity': 'high',
                'description': 'Cryptocurrency mining malware detected',
                'agent_id': target_agent
            })
        
        # Simulate escalating CPU usage
        start_time = time.time()
        while time.time() - start_time < duration:
            # Gradually increase CPU usage to simulate mining
            cpu_usage = min(95, 50 + (time.time() - start_time) * 1.5)
            
            metrics = {
                'cpu': cpu_usage + random.uniform(-5, 5),
                'memory': random.uniform(60, 85),
                'disk': random.uniform(40, 60),
                'network': random.uniform(10, 30),
                'processes': random.randint(150, 300)
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
                        'attack_type': 'cpu_exhaustion'
                    },
                    'confidence': min(1.0, cpu_usage / 100)
                })
            
            await asyncio.sleep(2)
        
        # Recovery phase
        logger.info(f"🔄 Recovery phase - CPU usage returning to normal")
        for i in range(5):
            metrics = {
                'cpu': max(10, 95 - i * 15),
                'memory': random.uniform(40, 60),
                'disk': random.uniform(40, 60),
                'network': random.uniform(10, 30),
                'processes': random.randint(80, 150)
            }
            await self.send_agent_metrics(target_agent, metrics)
            await asyncio.sleep(2)
        
        logger.info(f"✅ CPU Exhaustion Attack completed on {target_agent}")
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
            # Run on specific or random agent
            target_agents = [agent_id or random.choice(agents)['id']]
            logger.info(f"🎯 Running memory leak attack on agent: {target_agents[0]}")
        
        attack_id = str(uuid.uuid4())
        
        # Create threat for each target agent
        for target_agent in target_agents:
            await self.create_threat({
                'name': f'Memory Leak Attack - {target_agent}',
                'type': 'memory_corruption',
                'severity': 'high',
                'description': 'Process with memory leak consuming system resources',
                'agent_id': target_agent
            })
        
        start_time = time.time()
        base_memory = 40
        
        # Run attack simulation for each target agent
        for target_agent in target_agents:
            start_time = time.time()
            base_memory = 40
            
            while time.time() - start_time < duration:
                # Gradually increase memory usage
                elapsed = time.time() - start_time
                memory_usage = min(95, base_memory + elapsed * 2)
                
                metrics = {
                    'cpu': random.uniform(20, 40),
                    'memory': memory_usage + random.uniform(-3, 3),
                    'disk': random.uniform(40, 60),
                    'network': random.uniform(5, 15),
                    'processes': random.randint(100, 200)
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
                            'attack_type': 'memory_leak'
                        },
                        'confidence': min(1.0, memory_usage / 100)
                    })
                
                await asyncio.sleep(1)  # Small delay between updates
        
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
        
        target_agent = random.choice(agents)['id'] if agent_id == 'all' else (agent_id or random.choice(agents)['id'])
        attack_id = str(uuid.uuid4())
        
        # Create threat
        await self.create_threat({
            'name': f'Network Flood Attack - {target_agent}',
            'type': 'network_flood',
            'severity': 'critical',
            'description': 'Suspicious network traffic flood detected',
            'agent_id': target_agent
        })
        
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
        
        target_agent = random.choice(agents)['id'] if agent_id == 'all' else (agent_id or random.choice(agents)['id'])
        
        # Create master threat
        await self.create_threat({
            'name': f'Coordinated Multi-Vector Attack - {target_agent}',
            'type': 'multi_vector',
            'severity': 'critical',
            'description': 'Coordinated attack using multiple vectors detected',
            'agent_id': target_agent
        })
        
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
            
    except KeyboardInterrupt:
        logger.info("Attack simulator stopped by user")
    except Exception as e:
        logger.error(f"Attack simulator error: {e}")
    finally:
        await simulator.stop()

if __name__ == "__main__":
    asyncio.run(main())