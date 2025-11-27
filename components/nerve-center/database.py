"""
Database module for DIO Nerve Center
Handles PostgreSQL database operations for events, threats, and evidence
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

logger = logging.getLogger(__name__)

Base = declarative_base()

# Database Models - Matching Prisma Schema
class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    hostname = Column(String, nullable=False)
    status = Column(String, nullable=False, default="offline")  # active, warning, offline
    rank = Column(Integer, nullable=False, default=0)  # R0 to R4
    cpu = Column(Float, nullable=False, default=0)
    memory = Column(Float, nullable=False, default=0)
    lastSeen = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    threats = Column(Integer, nullable=False, default=0)
    ipAddress = Column(String, nullable=False)  # Matching Prisma schema
    osType = Column(String, nullable=False)
    version = Column(String, nullable=False)
    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class Event(Base):
    __tablename__ = "events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # threat, anomaly, system, evidence
    severity = Column(String, nullable=False)  # low, medium, high, critical
    description = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    agentId = Column(String, nullable=True)  # Matching Prisma schema
    details = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default="active")  # active, acknowledged, resolved
    createdAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class Threat(Base):
    __tablename__ = "threats"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # malware, anomaly, intrusion
    severity = Column(String, nullable=False)  # low, medium, high, critical
    description = Column(String, nullable=False)
    signature = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")  # active, contained, resolved
    detectedAt = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    resolvedAt = Column(DateTime, nullable=True)

class Evidence(Base):
    __tablename__ = "evidences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agentId = Column(String, nullable=False)  # Matching Prisma schema
    type = Column(String, nullable=False)  # threat, anomaly, system_event
    severity = Column(String, nullable=False)  # low, medium, high, critical
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    rawData = Column(String, nullable=False)  # JSON data - Matching Prisma schema
    status = Column(String, nullable=False, default="open")  # open, investigating, resolved
    confidence = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class SystemHealth(Base):
    __tablename__ = "system_health"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    component = Column(String, nullable=False)  # nerve_center, mesh_network, database
    status = Column(String, nullable=False)  # healthy, warning, critical
    cpu = Column(Float, nullable=False)
    memory = Column(Float, nullable=False)
    disk = Column(Float, nullable=False)
    network = Column(Float, nullable=False)
    uptime = Column(Integer, nullable=False)
    lastCheck = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    errorMessage = Column(String, nullable=True)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            # Get database URL from environment or use default
            database_url = os.getenv('DATABASE_URL', 'postgresql://dio_user:dio_password@localhost:5432/dio_platform')
            
            logger.info(f"Attempting to connect to database: {database_url}")
            logger.info(f"Database URL from env: {os.getenv('DATABASE_URL')}")
            
            # Create engine
            self.engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False  # Set to True for SQL logging
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Test connection with retry
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    with self.engine.connect() as conn:
                        result = conn.execute(text("SELECT 1"))
                        logger.info(f"Database connection successful on attempt {attempt + 1}")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Database connection attempt {attempt + 1} failed, retrying in 5s: {e}")
                    import time
                    time.sleep(5)
            
            # Create tables if they don't exist
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified")
            
            self.connected = True
            logger.info("Database connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            logger.error(f"Database URL: {database_url}")
            self.connected = False
            return False
    
    def get_session(self) -> Optional[Session]:
        """Get database session"""
        if not self.connected:
            logger.warning("Database not connected, attempting to reconnect...")
            self.connect()
        
        if not self.connected:
            logger.error("Still cannot connect to database")
            return None
            
        try:
            return self.SessionLocal()
        except Exception as e:
            logger.error(f"Failed to create database session: {e}")
            return None
    
    def save_event(self, event_data: Dict[str, Any]) -> Optional[str]:
        """Save event to database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return None
                
            event = Event(
                id=event_data.get('id', str(uuid.uuid4())),
                name=event_data.get('name', 'Unknown Event'),
                type=event_data.get('type', 'system'),
                severity=event_data.get('severity', 'medium'),
                description=event_data.get('description', 'Event occurred'),
                timestamp=datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00')) if isinstance(event_data.get('timestamp'), str) else datetime.now(timezone.utc),
                agentId=event_data.get('agent_id') or event_data.get('agentId'),
                details=event_data.get('details', {}),
                status=event_data.get('status', 'active')
            )
            
            session.add(event)
            session.commit()
            session.refresh(event)
            
            logger.info(f"Event saved to database: {event.id}")
            return event.id
            
        except Exception as e:
            logger.error(f"Failed to save event to database: {e}")
            if session:
                session.rollback()
            return None
        finally:
            if session:
                session.close()
    
    def get_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events from database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return []
                
            events = session.query(Event).order_by(Event.timestamp.desc()).limit(limit).all()
            
            result = []
            for event in events:
                result.append({
                    'id': event.id,
                    'name': event.name,
                    'type': event.type,
                    'severity': event.severity,
                    'description': event.description,
                    'timestamp': event.timestamp.isoformat(),
                    'agent_id': event.agentId,  # Updated to match Prisma schema
                    'agentId': event.agentId,   # Added for compatibility
                    'details': event.details or {},
                    'status': event.status,
                    'createdAt': event.createdAt.isoformat(),
                    'updatedAt': event.updatedAt.isoformat()
                })
            
            logger.info(f"Retrieved {len(result)} events from database")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get events from database: {e}")
            return []
        finally:
            if session:
                session.close()
    
    def save_agent(self, agent_data: Dict[str, Any]) -> Optional[str]:
        """Save agent to database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return None
                
            # Check if agent already exists
            existing_agent = session.query(Agent).filter(Agent.id == agent_data['id']).first()
            if existing_agent:
                # Update existing agent
                existing_agent.name = agent_data.get('name', existing_agent.name)
                existing_agent.hostname = agent_data.get('hostname', existing_agent.hostname)
                existing_agent.status = agent_data.get('status', existing_agent.status)
                existing_agent.cpu = agent_data.get('cpu', existing_agent.cpu)
                existing_agent.memory = agent_data.get('memory', existing_agent.memory)
                existing_agent.lastSeen = datetime.fromisoformat(agent_data['lastSeen'].replace('Z', '+00:00')) if isinstance(agent_data.get('lastSeen'), str) else datetime.now(timezone.utc)
                existing_agent.threats = agent_data.get('threats', existing_agent.threats)
                existing_agent.ipAddress = agent_data.get('ipAddress', existing_agent.ipAddress)
                existing_agent.osType = agent_data.get('osType', existing_agent.osType)
                existing_agent.updatedAt = datetime.now(timezone.utc)
                
                session.commit()
                logger.info(f"Agent updated in database: {existing_agent.id}")
                return existing_agent.id
            else:
                # Create new agent
                agent = Agent(
                    id=agent_data.get('id', str(uuid.uuid4())),
                    name=agent_data.get('name', 'Unknown Agent'),
                    hostname=agent_data.get('hostname', 'unknown'),
                    status=agent_data.get('status', 'active'),
                    rank=agent_data.get('rank', 1),
                    cpu=agent_data.get('cpu', 0),
                    memory=agent_data.get('memory', 0),
                    lastSeen=datetime.fromisoformat(agent_data['lastSeen'].replace('Z', '+00:00')) if isinstance(agent_data.get('lastSeen'), str) else datetime.now(timezone.utc),
                    threats=agent_data.get('threats', 0),
                    ipAddress=agent_data.get('ipAddress', '0.0.0.0'),
                    osType=agent_data.get('osType', 'unknown'),
                    version=agent_data.get('version', '1.0.0')
                )
                
                session.add(agent)
                session.commit()
                session.refresh(agent)
                
                logger.info(f"Agent saved to database: {agent.id}")
                return agent.id
            
        except Exception as e:
            logger.error(f"Failed to save agent to database: {e}")
            if session:
                session.rollback()
            return None
        finally:
            if session:
                session.close()
    
    def save_threat(self, threat_data: Dict[str, Any]) -> Optional[str]:
        """Save threat to database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return None
                
            threat = Threat(
                id=threat_data.get('id', str(uuid.uuid4())),
                name=threat_data.get('name', 'Unknown Threat'),
                type=threat_data.get('type', 'unknown'),
                severity=threat_data.get('severity', 'medium'),
                description=threat_data.get('description', ''),
                signature=threat_data.get('signature'),
                status=threat_data.get('status', 'active'),
                detectedAt=datetime.fromisoformat(threat_data['detected_at'].replace('Z', '+00:00')) if isinstance(threat_data.get('detected_at'), str) else datetime.now(timezone.utc)
            )
            
            session.add(threat)
            session.commit()
            session.refresh(threat)
            
            logger.info(f"Threat saved to database: {threat.id}")
            return threat.id
            
        except Exception as e:
            logger.error(f"Failed to save threat to database: {e}")
            if session:
                session.rollback()
            return None
        finally:
            if session:
                session.close()
    
    def save_evidence(self, evidence_data: Dict[str, Any]) -> Optional[str]:
        """Save evidence to database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return None
                
            evidence = Evidence(
                id=evidence_data.get('id', str(uuid.uuid4())),
                agentId=evidence_data.get('agent_id'),  # Updated to match Prisma schema
                type=evidence_data.get('type'),
                severity=evidence_data.get('severity'),
                title=evidence_data.get('title'),
                description=evidence_data.get('description'),
                rawData=json.dumps(evidence_data.get('raw_data', {})),  # Updated to match Prisma schema
                status=evidence_data.get('status', 'open'),
                confidence=evidence_data.get('confidence', 0.0),
                timestamp=datetime.fromisoformat(evidence_data['timestamp'].replace('Z', '+00:00')) if isinstance(evidence_data.get('timestamp'), str) else datetime.now(timezone.utc)
            )
            
            session.add(evidence)
            session.commit()
            session.refresh(evidence)
            
            logger.info(f"Evidence saved to database: {evidence.id}")
            return evidence.id
            
        except Exception as e:
            logger.error(f"Failed to save evidence to database: {e}")
            if session:
                session.rollback()
            return None
        finally:
            if session:
                session.close()
    
    def get_old_events(self, cutoff_time: datetime) -> List[Event]:
        """Get events older than cutoff time"""
        try:
            session = self.get_session()
            if not session:
                return []
                
            events = session.query(Event).filter(Event.timestamp < cutoff_time).all()
            session.close()
            return events
        except Exception as e:
            logger.error(f"Failed to get old events: {e}")
            return []
    
    def get_old_threats(self, cutoff_time: datetime) -> List[Threat]:
        """Get threats older than cutoff time"""
        try:
            session = self.get_session()
            if not session:
                return []
                
            threats = session.query(Threat).filter(Threat.detectedAt < cutoff_time).all()
            session.close()
            return threats
        except Exception as e:
            logger.error(f"Failed to get old threats: {e}")
            return []
    
    def get_old_evidence(self, cutoff_time: datetime) -> List[Evidence]:
        """Get evidence older than cutoff time"""
        try:
            session = self.get_session()
            if not session:
                return []
                
            evidence = session.query(Evidence).filter(Evidence.timestamp < cutoff_time).all()
            session.close()
            return evidence
        except Exception as e:
            logger.error(f"Failed to get old evidence: {e}")
            return []
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents from database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return []
                
            agents = session.query(Agent).all()
            session.close()
            return agents
        except Exception as e:
            logger.error(f"Failed to get all agents: {e}")
            return []
    
    def get_all_events(self) -> List[Event]:
        """Get all events from database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return []
                
            events = session.query(Event).all()
            session.close()
            return events
        except Exception as e:
            logger.error(f"Failed to get all events: {e}")
            return []
    
    def get_all_threats(self) -> List[Threat]:
        """Get all threats from database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return []
                
            threats = session.query(Threat).all()
            session.close()
            return threats
        except Exception as e:
            logger.error(f"Failed to get all threats: {e}")
            return []
    
    def get_all_evidence(self) -> List[Evidence]:
        """Get all evidence from database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return []
                
            evidence = session.query(Evidence).all()
            session.close()
            return evidence
        except Exception as e:
            logger.error(f"Failed to get all evidence: {e}")
            return []
    
    def clear_agents(self) -> bool:
        """Clear all agents from database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return False
                
            session.query(Agent).delete()
            session.commit()
            logger.info("All agents cleared from database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear agents from database: {e}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close()
    
    def clear_events(self) -> bool:
        """Clear all agents from database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return False
                
            session.query(Agent).delete()
            session.commit()
            logger.info("All agents cleared from database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear agents from database: {e}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close()
    
    def clear_events(self) -> bool:
        """Clear all events from database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return False
                
            session.query(Event).delete()
            session.commit()
            logger.info("All events cleared from database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear events from database: {e}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close()
    
    def reset_database(self) -> bool:
        """Completely reset database to clean state"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return False
                
            # Clear all tables
            session.query(Event).delete()
            session.query(Threat).delete()
            session.query(Evidence).delete()
            session.query(Agent).delete()
            session.query(SystemHealth).delete()
            session.commit()
            logger.info("🧹 Database completely reset to clean state")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close()
    
    def clear_threats(self) -> bool:
        """Clear all threats from database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return False
                
            session.query(Threat).delete()
            session.commit()
            logger.info("All threats cleared from database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear threats from database: {e}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close()
    
    def clear_evidence(self) -> bool:
        """Clear all evidence from database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return False
                
            session.query(Evidence).delete()
            session.commit()
            logger.info("All evidence cleared from database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear evidence from database: {e}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close()
    
    def save_system_health(self, health_data: Dict[str, Any]) -> Optional[str]:
        """Save system health data to database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return None
                
            # Check if component already exists and update instead of creating duplicates
            existing_health = session.query(SystemHealth).filter(
                SystemHealth.component == health_data['component']
            ).first()
            
            if existing_health:
                # Update existing record
                existing_health.status = health_data['status']
                existing_health.cpu = health_data['cpu']
                existing_health.memory = health_data['memory']
                existing_health.disk = health_data['disk']
                existing_health.network = health_data['network']
                existing_health.uptime = health_data['uptime']
                existing_health.lastCheck = datetime.now(timezone.utc)
                existing_health.errorMessage = health_data.get('errorMessage')
                
                session.commit()
                logger.info(f"System Health updated - {health_data['component']}: {health_data['status']}")
                return existing_health.id
            else:
                # Create new SystemHealth record
                system_health = SystemHealth(
                    component=health_data['component'],
                    status=health_data['status'],
                    cpu=health_data['cpu'],
                    memory=health_data['memory'],
                    disk=health_data['disk'],
                    network=health_data['network'],
                    uptime=health_data['uptime'],
                    errorMessage=health_data.get('errorMessage')
                )
                
                session.add(system_health)
                session.commit()
                session.refresh(system_health)
                
                logger.info(f"System Health created - {health_data['component']}: {health_data['status']}")
                return system_health.id
            
        except Exception as e:
            logger.error(f"Failed to save system health: {e}")
            if session:
                session.rollback()
            return None
        finally:
            if session:
                session.close()
    
    def update_event_status(self, event_id: str, status: str) -> bool:
        """Update event status in database"""
        try:
            session = self.get_session()
            if not session:
                logger.error("No database session available")
                return False
                
            # Update event status
            event = session.query(Event).filter(Event.id == event_id).first()
            if event:
                event.status = status
                event.updatedAt = datetime.now(timezone.utc)
                session.commit()
                logger.info(f"Event {event_id} status updated to {status}")
                return True
            else:
                logger.warning(f"Event {event_id} not found in database")
                return False
            
        except Exception as e:
            logger.error(f"Failed to update event status: {e}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close()
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            if not self.connected:
                return {
                    'status': 'unhealthy',
                    'error': 'Not connected to database'
                }
            
            session = self.get_session()
            if not session:
                return {
                    'status': 'unhealthy',
                    'error': 'Cannot create database session'
                }
            
            # Test query
            from sqlalchemy import text
            session.execute(text("SELECT 1"))
            session.close()
            
            return {
                'status': 'healthy',
                'connected': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

# Global database manager instance
db_manager = DatabaseManager()