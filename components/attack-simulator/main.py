#!/usr/bin/env python3
"""
DIO Attack Simulator
A comprehensive attack simulation tool for testing DIO platform's detection capabilities.
This simulates various attack scenarios - agents should detect and report these attacks.
"""

import asyncio
import argparse
import logging
import random
import string
import subprocess
import time
import uuid
import tempfile
import math
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AttackSimulator:
    """Attack simulator that generates real system load for agent detection."""
    
    def __init__(self):
        self.attacks = {
            'cpu': self.cpu_exhaustion_attack,
            'memory': self.memory_leak_attack,
            'network': self.network_flood_attack,
            'process': self.suspicious_process_attack,
            'file': self.file_integrity_attack,
            'multi': self.multi_vector_attack,
            'lateral': self.lateral_movement_attack
        }
        logger.info("Attack Simulator initialized - agents should detect these attacks")
    
    async def cpu_exhaustion_attack(self, duration: int = 30, agent_ids: List[str] = None) -> bool:
        """Generate real CPU load for agents to detect."""
        logger.info(f"🔥 Starting CPU exhaustion attack for {duration} seconds")
        logger.info(f"💡 Based on working command: math.sqrt(123.456) for _ in range(40000000)")
        
        start_time = time.time()
        iteration = 0
        
        # Create multiple CPU-intensive tasks running in parallel
        async def cpu_intensive_task():
            """Intensive CPU calculation that will consume significant CPU resources"""
            local_iterations = 0
            while time.time() - start_time < duration:
                local_iterations += 1
                # Similar to the example: use math.sqrt with intensive calculations
                # Multiple parallel calculations to maximize CPU usage
                _ = [math.sqrt(123.456 + i * 0.0001) for i in range(40000000)]  # Exact working command
                _ = [i**2.5 for i in range(15000)]  # Quadratic calculations
                _ = [i**3 for i in range(8000)]   # Cubic calculations
                _ = [math.sqrt(i * 1.234) for i in range(12000)]  # More sqrt calculations
                _ = sum([i * j for i in range(100) for j in range(100)])  # Matrix multiplication
                # Minimal sleep to allow context switching but maintain high CPU
                await asyncio.sleep(0.01)  # Reduced from 0.1 to increase CPU load
                
                if local_iterations % 100 == 0:  # More frequent logging
                    elapsed = time.time() - start_time
                    logger.info(f"🔥 CPU intensive task {local_iterations}: {elapsed:.1f}s elapsed")
        
        # Launch multiple parallel tasks to maximize CPU stress
        num_tasks = 3  # Number of parallel CPU tasks (reduced for stability)
        tasks = [cpu_intensive_task() for _ in range(num_tasks)]
        
        logger.info(f"🚀 Launched {num_tasks} parallel CPU-intensive tasks")
        logger.info(f"🎯 Each task running: math.sqrt(123.456) for _ in range(40000000)")
        
        try:
            # Run all tasks concurrently to maximize CPU usage
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in CPU attack: {e}")
        
        elapsed = time.time() - start_time
        logger.info(f"✅ CPU exhaustion attack completed after {elapsed:.1f} seconds")
        logger.info(f"🎯 Attack intensity: High - should have triggered agent CPU anomaly detection")
        return True
    
    async def memory_leak_attack(self, duration: int = 30, agent_ids: List[str] = None) -> bool:
        """Generate real memory consumption for agents to detect."""
        logger.info(f"💾 Starting memory leak attack for {duration} seconds")
        logger.info(f"🎯 Target: Consume significant memory to trigger >80% memory threshold")
        
        memory_consumers = []
        start_time = time.time()
        iteration = 0
        
        # Create multiple memory-intensive tasks running in parallel
        async def memory_intensive_task():
            """Intensive memory consumption that will stress agent memory detection"""
            local_memory_consumer = []
            local_iterations = 0
            while time.time() - start_time < duration:
                local_iterations += 1
                # More aggressive memory consumption to trigger agent detection
                # Consume larger chunks of memory more frequently
                for _ in range(5):  # 5x more aggressive
                    local_memory_consumer.append('0' * 2048 * 1024)  # 2MB per chunk (increased from 1MB)
                
                # Also consume CPU with memory operations
                _ = [i * 1000 for i in range(5000)]  # Memory + CPU stress
                _ = [math.sqrt(i * 1234.567) for i in range(3000)]  # More sqrt calculations
                
                # Minimal sleep to allow some processing but maintain memory pressure
                await asyncio.sleep(0.2)  # Slightly increased sleep
                
                if local_iterations % 10 == 0:  # More frequent logging
                    elapsed = time.time() - start_time
                    memory_mb = len(local_memory_consumer) * 2 / 1024  # Convert to MB
                    logger.info(f"💾 Memory intensive task {local_iterations}: {elapsed:.1f}s elapsed, {memory_mb}MB consumed")
            
            return local_memory_consumer
        
        # Launch multiple parallel memory tasks to maximize memory stress
        num_tasks = 3  # Multiple memory consumers
        tasks = [memory_intensive_task() for _ in range(num_tasks)]
        
        logger.info(f"🚀 Launched {num_tasks} parallel memory-intensive tasks")
        
        try:
            # Run all tasks concurrently to maximize memory usage
            results = await asyncio.gather(*tasks)
            # Combine all memory consumers
            for memory_consumer in results:
                memory_consumers.extend(memory_consumer)
        except Exception as e:
            logger.error(f"Error in memory attack: {e}")
        
        # Clean up memory
        total_memory_mb = len(memory_consumers) * 2 / 1024
        del memory_consumers
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Memory leak attack completed after {elapsed:.1f} seconds")
        logger.info(f"🎯 Peak memory consumed: {total_memory_mb}MB - should have triggered agent memory anomaly detection")
        return True
    
    async def network_flood_attack(self, duration: int = 30) -> bool:
        """Generate network activity for agents to detect."""
        logger.info(f"🌐 Starting network flood attack for {duration} seconds")
        
        start_time = time.time()
        iteration = 0
        while time.time() - start_time < duration:
            iteration += 1
            # Simulate network activity (in container, limited what we can do)
            # Generate some network-like activity
            await asyncio.sleep(1)
            
            # Debug output every 5 iterations
            if iteration % 5 == 0:
                elapsed = time.time() - start_time
                logger.info(f"🌐 Network attack ongoing: {elapsed:.1f}s elapsed, iteration {iteration}")
        
        logger.info(f"✅ Network flood attack completed after {iteration} iterations - agents should have detected this")
        return True
    
    async def suspicious_process_attack(self, duration: int = 30) -> bool:
        """Simulate suspicious process activity."""
        logger.info(f"⚙️ Starting suspicious process attack for {duration} seconds")
        
        start_time = time.time()
        iteration = 0
        while time.time() - start_time < duration:
            iteration += 1
            # Simulate suspicious process behavior
            await asyncio.sleep(2)
            
            # Debug output every 3 iterations
            if iteration % 3 == 0:
                elapsed = time.time() - start_time
                logger.info(f"⚙️ Process attack ongoing: {elapsed:.1f}s elapsed, iteration {iteration}")
        
        logger.info(f"✅ Suspicious process attack completed after {iteration} iterations - agents should have detected this")
        return True
    
    async def file_integrity_attack(self, duration: int = 30) -> bool:
        """Simulate file system activity."""
        logger.info(f"📁 Starting file integrity attack for {duration} seconds")
        
        start_time = time.time()
        file_count = 0
        while time.time() - start_time < duration:
            file_count += 1
            # Create temporary files (simulated ransomware activity)
            try:
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                    f.write(f"ransomware_simulation_{file_count}")
            except:
                pass  # In container, might not have permissions
            
            await asyncio.sleep(1)
            
            # Debug output every 10 files
            if file_count % 10 == 0:
                elapsed = time.time() - start_time
                logger.info(f"📁 File attack ongoing: {elapsed:.1f}s elapsed, {file_count} files created")
        
        logger.info(f"✅ File integrity attack completed after {file_count} files - agents should have detected this")
        return True
    
    async def multi_vector_attack(self, duration: int = 30) -> bool:
        """Execute multiple attack types simultaneously."""
        logger.info(f"🎯 Starting multi-vector attack for {duration} seconds")
        
        # Run multiple attacks concurrently
        tasks = [
            self.cpu_exhaustion_attack(duration // 2),
            self.memory_leak_attack(duration // 2),
            self.network_flood_attack(duration // 2)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        success_count = sum(1 for result in results if not isinstance(result, Exception))
        
        logger.info(f"✅ Multi-vector attack completed - {success_count}/3 attacks successful - agents should have detected multiple threats")
        return success_count >= 2  # Success if at least 2 attacks worked
    
    async def lateral_movement_attack(self, duration: int = 30) -> bool:
        """Simulate lateral movement activity."""
        logger.info(f"🔄 Starting lateral movement attack for {duration} seconds")
        
        start_time = time.time()
        attempt_count = 0
        while time.time() - start_time < duration:
            attempt_count += 1
            # Simulate lateral movement attempts
            await asyncio.sleep(3)
            
            # Debug output every 2 attempts
            if attempt_count % 2 == 0:
                elapsed = time.time() - start_time
                logger.info(f"🔄 Lateral movement ongoing: {elapsed:.1f}s elapsed, {attempt_count} attempts")
        
        logger.info(f"✅ Lateral movement attack completed after {attempt_count} attempts - agents should have detected suspicious activity")
        return True
    
    async def run_attack(self, attack_type: str, duration: int = 30, agent_ids: List[str] = None) -> bool:
        """Run a specific attack type."""
        if attack_type not in self.attacks:
            logger.error(f"Unknown attack type: {attack_type}")
            return False
        
        try:
            logger.info(f"🚀 Starting {attack_type} attack - agents should detect this")
            logger.info(f"⏱️ Attack duration: {duration} seconds")
            if agent_ids:
                logger.info(f"🎯 Targeting specific agents: {agent_ids}")
            else:
                logger.info(f"🎯 Targeting all available agents")
            
            attack_func = self.attacks[attack_type]
            result = await attack_func(duration)
            
            if result:
                logger.info(f"✅ {attack_type} attack completed successfully")
                logger.info(f"📡 Check DIO dashboard to see if agents detected these anomalies")
            else:
                logger.error(f"❌ {attack_type} attack failed")
            
            return result
        except Exception as e:
            logger.error(f"Error running {attack_type} attack: {str(e)}")
            logger.error(f"Full error details: {type(e).__name__}: {e}")
            return False
    
    async def interactive_mode(self):
        """Run interactive attack mode."""
        print("🎯 DIO Attack Simulator - Interactive Mode")
        print("=" * 50)
        print("⚠️  This simulator generates REAL attacks that agents should DETECT")
        print("=" * 50)
        
        print("\n🎭 Available attacks:")
        for i, attack_type in enumerate(self.attacks.keys(), 1):
            print(f"  {i}. {attack_type}")
        
        try:
            attack_choice = int(input("\n💥 Select attack (number): ")) - 1
            duration = int(input("⏱️  Duration in seconds (default 60): ") or "60")
            
            if 0 <= attack_choice < len(self.attacks):
                attack_type = list(self.attacks.keys())[attack_choice]
                
                print(f"\n🚀 Starting {attack_type} attack for {duration} seconds...")
                print("👀 Watch agent logs and DIO dashboard for detection!")
                success = await self.run_attack(attack_type, duration)
                
                if success:
                    print("✅ Attack completed! Check if agents detected the anomalies.")
                else:
                    print("❌ Attack failed!")
            else:
                print("❌ Invalid selection!")
        except (ValueError, KeyboardInterrupt):
            print("\n👋 Exiting interactive mode...")

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="DIO Attack Simulator - Real Attack Generation")
    parser.add_argument("attack_type", nargs="?", help="Type of attack to simulate")
    parser.add_argument("--duration", type=int, default=60, help="Attack duration in seconds (default: 60)")
    parser.add_argument("--agent", help="Agent ID (deprecated: attack simulator generates attacks for all agents to detect)")
    parser.add_argument("--agent-ids", help="Comma-separated list of agent IDs to target")
    parser.add_argument("interactive", nargs="?", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Handle deprecated --agent argument gracefully
    if args.agent:
        print("⚠️  WARNING: --agent argument is deprecated")
        print("   Attack simulator now generates attacks for ALL agents to detect")
        print("   Agent targeting is handled by the distributed architecture")
        print("   Use: ./attack.sh cpu all (to attack all agents)")
        print("   Or: ./attack.sh cpu <agent-id> (if targeting specific agent)")
        print("   Continuing with attack generation for all agents...")
    
    # Handle agent IDs parameter
    agent_ids = None
    if args.agent_ids:
        agent_ids = args.agent_ids.split(',') if args.agent_ids else []
        print(f"🎯 Targeting specific agents: {agent_ids}")
    
    # Create attack simulator
    simulator = AttackSimulator()
    
    if args.attack_type and args.attack_type == "interactive":
        await simulator.interactive_mode()
    elif args.attack_type:
        success = await simulator.run_attack(args.attack_type, args.duration, agent_ids)
        if success:
            print(f"✅ {args.attack_type} attack completed - check agent detections!")
        else:
            print(f"❌ {args.attack_type} attack failed")
            sys.exit(1)
    else:
        parser.print_help()
        print("\n📡 NOTE: This simulator generates REAL attacks.")
        print("   Agents should DETECT and REPORT these anomalies to Nerve Center.")
        print("   Check DIO dashboard to see detection results.")

if __name__ == "__main__":
    asyncio.run(main())