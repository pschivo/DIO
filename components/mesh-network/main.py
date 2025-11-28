import asyncio
import json
import logging
import websockets
from typing import Dict, Set, Any, List
from datetime import datetime
import uuid
import ssl
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    id: str
    type: str
    source: str
    destination: str
    data: Dict[str, Any]
    timestamp: str
    ttl: int = 10

@dataclass
class Node:
    id: str
    websocket: websockets.WebSocketServerProtocol
    last_seen: str
    node_type: str  # 'agent', 'nerve_center', 'surface'
    metadata: Dict[str, Any]

class DIOMeshNetwork:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.message_history: List[Message] = []
        self.rooms: Dict[str, Set[str]] = {}  # Room-based broadcasting
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'nodes_connected': 0,
            'active_rooms': 0
        }
        
    def add_node(self, node_id: str, websocket: websockets.WebSocketServerProtocol, 
                 node_type: str = 'agent', metadata: Dict[str, Any] = None):
        """Add a node to the mesh network"""
        self.nodes[node_id] = Node(
            id=node_id,
            websocket=websocket,
            last_seen=datetime.now().isoformat(),
            node_type=node_type,
            metadata=metadata or {}
        )
        self.stats['nodes_connected'] = len(self.nodes)
        logger.info(f"Node {node_id} ({node_type}) connected to mesh network")
        
    def remove_node(self, node_id: str):
        """Remove a node from the mesh network"""
        if node_id in self.nodes:
            node_type = self.nodes[node_id].node_type
            del self.nodes[node_id]
            self.stats['nodes_connected'] = len(self.nodes)
            
            # Remove from all rooms
            for room_id in self.rooms:
                self.rooms[room_id].discard(node_id)
            
            logger.info(f"Node {node_id} ({node_type}) disconnected from mesh network")
    
    def join_room(self, node_id: str, room_id: str):
        """Add node to a room for broadcasting"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(node_id)
        self.stats['active_rooms'] = len(self.rooms)
        logger.info(f"Node {node_id} joined room {room_id}")
    
    def leave_room(self, node_id: str, room_id: str):
        """Remove node from a room"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(node_id)
            if not self.rooms[room_id]:
                del self.rooms[room_id]
                self.stats['active_rooms'] = len(self.rooms)
        logger.info(f"Node {node_id} left room {room_id}")
    
    async def send_message(self, message: Message):
        """Send message to specific destination"""
        try:
            if message.destination == 'broadcast':
                # Broadcast to all nodes
                await self._broadcast_message(message)
            elif message.destination.startswith('room:'):
                # Broadcast to room
                room_id = message.destination.split(':')[1]
                await self._broadcast_to_room(message, room_id)
            else:
                # Send to specific node
                if message.destination in self.nodes:
                    await self._send_to_node(message, message.destination)
                else:
                    logger.warning(f"Destination node {message.destination} not found")
            
            self.stats['messages_sent'] += 1
            self.message_history.append(message)
            
            # Keep only last 1000 messages
            if len(self.message_history) > 1000:
                self.message_history = self.message_history[-1000:]
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def _send_to_node(self, message: Message, node_id: str):
        """Send message to specific node"""
        try:
            node = self.nodes[node_id]
            message_data = asdict(message)
            await node.websocket.send(json.dumps(message_data))
            logger.debug(f"Message sent to node {node_id}")
        except Exception as e:
            logger.error(f"Error sending to node {node_id}: {e}")
            # Remove disconnected node
            self.remove_node(node_id)
    
    async def _broadcast_message(self, message: Message):
        """Broadcast message to all nodes"""
        for node_id, node in self.nodes.items():
            if node_id != message.source:  # Don't send back to source
                await self._send_to_node(message, node_id)
    
    async def _broadcast_to_room(self, message: Message, room_id: str):
        """Broadcast message to all nodes in a room"""
        if room_id in self.rooms:
            for node_id in self.rooms[room_id]:
                if node_id != message.source:  # Don't send back to source
                    await self._send_to_node(message, node_id)
    
    async def handle_message(self, node_id: str, message_data: Dict[str, Any]):
        """Handle incoming message from node"""
        try:
            message = Message(
                id=message_data.get('id', str(uuid.uuid4())),
                type=message_data.get('type', 'unknown'),
                source=node_id,
                destination=message_data.get('destination', 'broadcast'),
                data=message_data.get('data', {}),
                timestamp=message_data.get('timestamp', datetime.now().isoformat()),
                ttl=message_data.get('ttl', 10)
            )
            
            self.stats['messages_received'] += 1
            
            # Update node last seen
            if node_id in self.nodes:
                self.nodes[node_id].last_seen = datetime.now().isoformat()
            
            # Route message based on type
            await self._route_message(message)
            
        except Exception as e:
            logger.error(f"Error handling message from {node_id}: {e}")
    
    async def _route_message(self, message: Message):
        """Route message based on type and destination"""
        if message.type == 'heartbeat':
            # Handle heartbeat messages
            await self._handle_heartbeat(message)
        elif message.type == 'agent_update':
            # Route agent updates to nerve center
            await self.send_message(Message(
                id=str(uuid.uuid4()),
                type='agent_update_forward',
                source='mesh_network',
                destination='nerve_center',
                data=message.data,
                timestamp=datetime.now().isoformat()
            ))
        elif message.type == 'threat_alert':
            # Broadcast threat alerts to all nodes
            await self.send_message(Message(
                id=str(uuid.uuid4()),
                type='threat_broadcast',
                source='mesh_network',
                destination='broadcast',
                data=message.data,
                timestamp=datetime.now().isoformat()
            ))
        else:
            # Forward message to destination
            await self.send_message(message)
    
    async def _handle_heartbeat(self, message: Message):
        """Handle heartbeat messages"""
        if message.source in self.nodes:
            self.nodes[message.source].last_seen = datetime.now().isoformat()
            # Send heartbeat response
            await self.send_message(Message(
                id=str(uuid.uuid4()),
                type='heartbeat_response',
                source='mesh_network',
                destination=message.source,
                data={'status': 'healthy'},
                timestamp=datetime.now().isoformat()
            ))
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        return {
            'nodes_connected': self.stats['nodes_connected'],
            'messages_sent': self.stats['messages_sent'],
            'messages_received': self.stats['messages_received'],
            'active_rooms': self.stats['active_rooms'],
            'nodes_by_type': {
                node_type: len([n for n in self.nodes.values() if n.node_type == node_type])
                for node_type in set(n.node_type for n in self.nodes.values())
            },
            'rooms': list(self.rooms.keys())
        }
    
    def get_node_list(self) -> List[Dict[str, Any]]:
        """Get list of connected nodes"""
        return [
            {
                'id': node.id,
                'type': node.node_type,
                'last_seen': node.last_seen,
                'metadata': node.metadata
            }
            for node in self.nodes.values()
        ]

# Global mesh network instance
mesh_network = DIOMeshNetwork()

async def handle_client(websocket, path):
    """Handle WebSocket client connection"""
    node_id = None
    try:
        # Wait for initial authentication message
        auth_message = await websocket.recv()
        auth_data = json.loads(auth_message)
        
        node_id = auth_data.get('node_id')
        node_type = auth_data.get('node_type', 'agent')
        metadata = auth_data.get('metadata', {})
        
        if not node_id:
            logger.warning("Client connected without node_id")
            await websocket.close(1008, "Missing node_id")
            return
        
        # Add node to mesh network
        mesh_network.add_node(node_id, websocket, node_type, metadata)
        
        # Join default rooms based on node type
        if node_type == 'agent':
            mesh_network.join_room(node_id, 'agents')
        elif node_type == 'nerve_center':
            mesh_network.join_room(node_id, 'nerve_center')
        elif node_type == 'surface':
            mesh_network.join_room(node_id, 'surface')
        
        # Send welcome message
        welcome_message = Message(
            id=str(uuid.uuid4()),
            type='welcome',
            source='mesh_network',
            destination=node_id,
            data={'message': 'Connected to DIO Mesh Network'},
            timestamp=datetime.now().isoformat()
        )
        await mesh_network._send_to_node(welcome_message, node_id)
        
        # Handle messages from client
        async for message in websocket:
            try:
                message_data = json.loads(message)
                await mesh_network.handle_message(node_id, message_data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from node {node_id}")
            except Exception as e:
                logger.error(f"Error processing message from {node_id}: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client {node_id} disconnected")
    except Exception as e:
        logger.error(f"Error handling client {node_id}: {e}")
    finally:
        if node_id:
            mesh_network.remove_node(node_id)

async def main():
    """Main entry point for mesh network"""
    logger.info("Starting DIO Mesh Network")
    
    # WebSocket server
    server = await websockets.serve(
        handle_client,
        "0.0.0.0",
        4222,  # NATS default port
        ping_interval=20,
        ping_timeout=10
    )
    
    logger.info("Mesh Network listening on ws://0.0.0.0:4222")
    
    # Keep server running
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())