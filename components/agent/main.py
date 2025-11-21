import asyncio
import json
import logging
import psutil
import platform
import socket
import time
import uuid
from datetime import datetime
from typing import Dict, Any
import aiohttp
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DIOAgent:
    def __init__(self, config: Dict[str, Any]):
        self.agent_id = config.get('agent_id', str(uuid.uuid4()))
        self.name = config.get('name', f'Agent-{self.agent_id[:8]}')
        self.nerve_center_url = config.get('nerve_center_url', 'http://localhost:8000')
        self.hostname = socket.gethostname()
        self.ip_address = self._get_local_ip()
        self.os_type = f"{platform.system()} {platform.release()}"
        self.rank = 0
        self.status = 'offline'
        self.threats_detected = 0
        
        # Monitoring configuration
        self.monitoring_interval = config.get('monitoring_interval', 5)
        self.anomaly_threshold = config.get('anomaly_threshold', 80.0)
        
        # Session for HTTP requests with better configuration
        self.session = None
        self.session_timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.max_retries = 3
        self.retry_delay = 2
        
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    async def register_with_nerve_center(self) -> bool:
        """Register this agent with the nerve center with retry logic"""
        for attempt in range(self.max_retries):
            try:
                registration_data = {
                    'id': self.agent_id,
                    'name': self.name,
                    'hostname': self.hostname,
                    'ip_address': self.ip_address,
                    'os_type': self.os_type
                }
                
                async with self.session.post(
                    f"{self.nerve_center_url}/agents/register",
                    json=registration_data,
                    timeout=self.session_timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Successfully registered agent: {self.agent_id}")
                        return True
                    else:
                        logger.error(f"Failed to register: HTTP {response.status}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))  # Increasing delay
                        continue
            except aiohttp.ClientConnectorError as e:
                logger.error(f"Connection error registering with nerve center (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Increasing delay
                continue
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout error registering with nerve center (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Increasing delay
                continue
            except Exception as e:
                logger.error(f"Unexpected error registering with nerve center (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Increasing delay
                continue
        
        return False
    
    async def send_metrics(self) -> bool:
        """Send system metrics to nerve center with better error handling"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            process_count = len(psutil.pids())
            
            metrics_data = {
                'cpu': cpu_percent,
                'memory': memory.percent,
                'disk': disk.percent,
                'network': (network.bytes_sent + network.bytes_recv) / (1024 * 1024),  # MB
                'processes': process_count,
                'timestamp': datetime.now().isoformat()
            }
            
            # Create a new session for each request to avoid broken pipe issues
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.post(
                    f"{self.nerve_center_url}/agents/{self.agent_id}/metrics",
                    json=metrics_data
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        logger.error(f"Failed to send metrics: HTTP {response.status}")
                        return False
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error sending metrics: {e}")
            return False
        except asyncio.CancelledError:
            logger.info("Metrics sending cancelled")
            return False
        except Exception as e:
            logger.error(f"Error sending metrics: {e}")
            return False
    
    def detect_anomalies(self, metrics: Dict[str, Any]) -> list:
        """Detect anomalies in system metrics"""
        anomalies = []
        
        # High CPU usage
        if metrics['cpu'] > self.anomaly_threshold:
            anomalies.append({
                'type': 'cpu_anomaly',
                'severity': 'high' if metrics['cpu'] > 90 else 'medium',
                'description': f"High CPU usage detected: {metrics['cpu']:.1f}%",
                'confidence': min(1.0, metrics['cpu'] / 100)
            })
        
        # High memory usage
        if metrics['memory'] > self.anomaly_threshold:
            anomalies.append({
                'type': 'memory_anomaly',
                'severity': 'high' if metrics['memory'] > 90 else 'medium',
                'description': f"High memory usage detected: {metrics['memory']:.1f}%",
                'confidence': min(1.0, metrics['memory'] / 100)
            })
        
        # Unusual process count
        if metrics['processes'] > 300:
            anomalies.append({
                'type': 'process_anomaly',
                'severity': 'medium',
                'description': f"Unusual process count: {metrics['processes']}",
                'confidence': min(1.0, metrics['processes'] / 500)
            })
        
        return anomalies
    
    async def report_threat(self, anomaly: Dict[str, Any]) -> bool:
        """Report a detected threat to nerve center"""
        try:
            threat_data = {
                'name': f"Threat from {self.name}",
                'type': anomaly['type'],
                'severity': anomaly['severity'],
                'description': anomaly['description'],
                'agent_id': self.agent_id,
                'detected_at': datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.post(
                    f"{self.nerve_center_url}/threats",
                    json=threat_data
                ) as response:
                    if response.status == 200:
                        self.threats_detected += 1
                        logger.info(f"Threat reported: {anomaly['type']}")
                        return True
                    else:
                        logger.error(f"Failed to report threat: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error reporting threat: {e}")
            return False
    
    async def create_evidence(self, anomaly: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        """Create evidence pack for anomaly"""
        try:
            evidence_data = {
                'agent_id': self.agent_id,
                'type': anomaly['type'],
                'severity': anomaly['severity'],
                'title': f"{anomaly['type'].replace('_', ' ').title()} on {self.hostname}",
                'description': anomaly['description'],
                'raw_data': {
                    'metrics': metrics,
                    'system_info': {
                        'hostname': self.hostname,
                        'os_type': self.os_type,
                        'agent_rank': self.rank
                    }
                },
                'confidence': anomaly['confidence']
            }
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.post(
                    f"{self.nerve_center_url}/evidence",
                    json=evidence_data
                ) as response:
                    if response.status == 200:
                        logger.info(f"Evidence created: {anomaly['type']}")
                        return True
                    else:
                        logger.error(f"Failed to create evidence: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error creating evidence: {e}")
            return False
    
    async def monitor_system(self):
        """Main monitoring loop"""
        logger.info(f"Starting system monitoring for {self.name}")
        
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        while True:
            try:
                # Get current metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                process_count = len(psutil.pids())
                
                metrics = {
                    'cpu': cpu_percent,
                    'memory': memory.percent,
                    'disk': disk.percent,
                    'network': (network.bytes_sent + network.bytes_recv) / (1024 * 1024),
                    'processes': process_count,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Send metrics to nerve center
                if await self.send_metrics():
                    consecutive_failures = 0  # Reset failure counter on success
                    self.status = 'active'
                else:
                    consecutive_failures += 1
                    logger.warning(f"Failed to send metrics (consecutive failures: {consecutive_failures})")
                    
                    # If too many consecutive failures, try to re-register
                    if consecutive_failures >= max_consecutive_failures:
                        logger.warning("Too many consecutive failures, attempting to re-register...")
                        try:
                            self.session = aiohttp.ClientSession(timeout=self.session_timeout)
                            if await self.register_with_nerve_center():
                                logger.info("Successfully re-registered with nerve center")
                                consecutive_failures = 0
                            await self.session.close()
                            self.session = None
                        except Exception as e:
                            logger.error(f"Failed to re-register: {e}")
                
                # Detect anomalies
                anomalies = self.detect_anomalies(metrics)
                
                # Report threats and create evidence for anomalies
                for anomaly in anomalies:
                    await self.report_threat(anomaly)
                    await self.create_evidence(anomaly, metrics)
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self.status = 'warning'
                consecutive_failures += 1
                await asyncio.sleep(self.monitoring_interval)
    
    async def start(self):
        """Start the agent"""
        logger.info(f"Starting DIO Agent: {self.name}")
        
        # Create HTTP session for registration only
        try:
            self.session = aiohttp.ClientSession(timeout=self.session_timeout)
            
            # Wait for nerve center to be ready with exponential backoff
            max_wait_time = 60  # Maximum wait time in seconds
            wait_interval = 2   # Initial wait interval
            total_waited = 0
            
            while total_waited < max_wait_time:
                try:
                    # Test connection to nerve center
                    async with self.session.get(
                        f"{self.nerve_center_url}/health",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            logger.info("Nerve center is ready, proceeding with registration")
                            break
                except Exception as e:
                    logger.info(f"Nerve center not ready yet, waiting {wait_interval}s... (attempt {total_waited + 1})")
                    await asyncio.sleep(wait_interval)
                    total_waited += wait_interval
                    wait_interval = min(wait_interval * 2, 10)  # Exponential backoff, max 10s
            
            # Register with nerve center
            if not await self.register_with_nerve_center():
                logger.error("Failed to register with nerve center after multiple attempts")
                await self.session.close()
                return
            
            # Close registration session
            await self.session.close()
            self.session = None
            
            # Start monitoring (will create its own sessions)
            await self.monitor_system()
            
        except Exception as e:
            logger.error(f"Error starting agent: {e}")
            if self.session:
                await self.session.close()
    
    async def stop(self):
        """Stop the agent"""
        logger.info(f"Stopping DIO Agent: {self.name}")
        if self.session:
            await self.session.close()

async def main():
    """Main entry point"""
    # Configuration
    config = {
        'agent_id': f"agent-{uuid.uuid4().hex[:8]}",
        'name': f"DIO-Agent-{platform.node()}",
        'nerve_center_url': 'http://nerve-center:8000',  # Use Docker service name
        'monitoring_interval': 5,
        'anomaly_threshold': 80.0
    }
    
    # Create and start agent
    agent = DIOAgent(config)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Agent error: {e}")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())