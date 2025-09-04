#!/usr/bin/env python3
"""
Gossip Protocol Implementation
SWIM-style failure detection and information dissemination.
"""

import time
import random
import threading
import socket
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
import json
import hashlib

class NodeState(Enum):
    ALIVE = "alive"
    SUSPICIOUS = "suspicious"
    DEAD = "dead"

@dataclass
class GossipMessage:
    message_type: str
    sender_id: str
    data: Dict
    timestamp: float = field(default_factory=time.time)
    
    def to_json(self) -> str:
        return json.dumps({
            'type': self.message_type,
            'sender': self.sender_id,
            'data': self.data,
            'timestamp': self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'GossipMessage':
        data = json.loads(json_str)
        return cls(
            message_type=data['type'],
            sender_id=data['sender'],
            data=data['data'],
            timestamp=data['timestamp']
        )

@dataclass
class NodeInfo:
    node_id: str
    address: str
    port: int
    state: NodeState = NodeState.ALIVE
    incarnation: int = 0
    last_seen: float = field(default_factory=time.time)
    suspicion_timeout: float = 5.0

@dataclass
class GossipNode:
    node_id: str
    address: str
    port: int
    
    # Gossip configuration
    gossip_interval: float = 1.0
    fanout: int = 3
    suspicion_timeout: float = 5.0
    failure_timeout: float = 10.0
    
    # State
    members: Dict[str, NodeInfo] = field(default_factory=dict)
    local_state: Dict[str, any] = field(default_factory=dict)
    incarnation: int = 0
    running: bool = False
    
    # Statistics
    stats: Dict[str, int] = field(default_factory=lambda: {
        'messages_sent': 0,
        'messages_received': 0,
        'failures_detected': 0,
        'recoveries_detected': 0,
        'gossip_rounds': 0
    })
    
    def __post_init__(self):
        # Add self to members
        self.members[self.node_id] = NodeInfo(
            node_id=self.node_id,
            address=self.address,
            port=self.port,
            state=NodeState.ALIVE,
            incarnation=self.incarnation
        )

class GossipProtocol:
    def __init__(self, node: GossipNode):
        self.node = node
        self.socket = None
        self.gossip_thread = None
        self.failure_detector_thread = None
        
    def start(self):
        """Start the gossip protocol"""
        self.node.running = True
        
        # Start UDP socket for communication
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.node.address, self.node.port))
        self.socket.settimeout(0.1)  # Non-blocking with timeout
        
        # Start background threads
        self.gossip_thread = threading.Thread(target=self._gossip_loop, daemon=True)
        self.failure_detector_thread = threading.Thread(target=self._failure_detector_loop, daemon=True)
        
        self.gossip_thread.start()
        self.failure_detector_thread.start()
        
        print(f"🚀 Gossip node {self.node.node_id} started on {self.node.address}:{self.node.port}")
    
    def stop(self):
        """Stop the gossip protocol"""
        self.node.running = False
        if self.socket:
            self.socket.close()
        print(f"🛑 Gossip node {self.node.node_id} stopped")
    
    def join_cluster(self, seed_nodes: List[Tuple[str, int]]):
        """Join cluster by contacting seed nodes"""
        for address, port in seed_nodes:
            try:
                join_msg = GossipMessage(
                    message_type="join",
                    sender_id=self.node.node_id,
                    data={
                        'address': self.node.address,
                        'port': self.node.port,
                        'incarnation': self.node.incarnation
                    }
                )
                self._send_message(address, port, join_msg)
                print(f"📡 Sent join request to {address}:{port}")
            except Exception as e:
                print(f"❌ Failed to contact seed node {address}:{port}: {e}")
    
    def update_local_state(self, key: str, value: any):
        """Update local state and trigger gossip"""
        self.node.local_state[key] = value
        self.node.incarnation += 1
        print(f"📝 Updated local state: {key} = {value}")
    
    def _gossip_loop(self):
        """Main gossip loop"""
        while self.node.running:
            try:
                self._perform_gossip_round()
                self._listen_for_messages()
                time.sleep(self.node.gossip_interval)
            except Exception as e:
                print(f"❌ Gossip loop error: {e}")
    
    def _perform_gossip_round(self):
        """Perform one round of gossip"""
        if len(self.node.members) <= 1:
            return
        
        # Select random peers for gossip
        alive_members = [m for m in self.node.members.values() 
                        if m.state == NodeState.ALIVE and m.node_id != self.node.node_id]
        
        if not alive_members:
            return
        
        gossip_targets = random.sample(alive_members, 
                                     min(self.node.fanout, len(alive_members)))
        
        # Create gossip message with membership and state info
        gossip_data = {
            'members': {
                node_id: {
                    'address': info.address,
                    'port': info.port,
                    'state': info.state.value,
                    'incarnation': info.incarnation,
                    'last_seen': info.last_seen
                }
                for node_id, info in self.node.members.items()
            },
            'local_state': self.node.local_state,
            'incarnation': self.node.incarnation
        }
        
        gossip_msg = GossipMessage(
            message_type="gossip",
            sender_id=self.node.node_id,
            data=gossip_data
        )
        
        # Send to selected targets
        for target in gossip_targets:
            self._send_message(target.address, target.port, gossip_msg)
        
        self.node.stats['gossip_rounds'] += 1
    
    def _failure_detector_loop(self):
        """Failure detection loop"""
        while self.node.running:
            try:
                self._detect_failures()
                time.sleep(self.node.suspicion_timeout / 2)
            except Exception as e:
                print(f"❌ Failure detector error: {e}")
    
    def _detect_failures(self):
        """Detect failed nodes based on timeouts"""
        current_time = time.time()
        
        for node_id, member in self.node.members.items():
            if node_id == self.node.node_id:
                continue
            
            time_since_seen = current_time - member.last_seen
            
            # Mark as suspicious if not seen for suspicion timeout
            if (member.state == NodeState.ALIVE and 
                time_since_seen > self.node.suspicion_timeout):
                member.state = NodeState.SUSPICIOUS
                print(f"⚠️  Node {node_id} marked as suspicious")
                self._gossip_state_change(node_id, NodeState.SUSPICIOUS)
            
            # Mark as dead if suspicious for too long
            elif (member.state == NodeState.SUSPICIOUS and 
                  time_since_seen > self.node.failure_timeout):
                member.state = NodeState.DEAD
                self.node.stats['failures_detected'] += 1
                print(f"💀 Node {node_id} marked as dead")
                self._gossip_state_change(node_id, NodeState.DEAD)
    
    def _gossip_state_change(self, node_id: str, new_state: NodeState):
        """Gossip a state change to the cluster"""
        state_change_msg = GossipMessage(
            message_type="state_change",
            sender_id=self.node.node_id,
            data={
                'target_node': node_id,
                'new_state': new_state.value,
                'incarnation': self.node.incarnation
            }
        )
        
        # Send to all alive members
        alive_members = [m for m in self.node.members.values() 
                        if m.state == NodeState.ALIVE and m.node_id != self.node.node_id]
        
        for member in alive_members:
            self._send_message(member.address, member.port, state_change_msg)
    
    def _listen_for_messages(self):
        """Listen for incoming gossip messages"""
        try:
            data, addr = self.socket.recvfrom(4096)
            message = GossipMessage.from_json(data.decode())
            self._handle_message(message, addr)
            self.node.stats['messages_received'] += 1
        except socket.timeout:
            pass  # Normal timeout, continue
        except Exception as e:
            print(f"❌ Error receiving message: {e}")
    
    def _handle_message(self, message: GossipMessage, sender_addr):
        """Handle incoming gossip message"""
        if message.message_type == "join":
            self._handle_join_message(message)
        elif message.message_type == "gossip":
            self._handle_gossip_message(message)
        elif message.message_type == "state_change":
            self._handle_state_change_message(message)
        elif message.message_type == "ping":
            self._handle_ping_message(message, sender_addr)
        elif message.message_type == "ack":
            self._handle_ack_message(message)
    
    def _handle_join_message(self, message: GossipMessage):
        """Handle node join request"""
        node_data = message.data
        new_node = NodeInfo(
            node_id=message.sender_id,
            address=node_data['address'],
            port=node_data['port'],
            incarnation=node_data['incarnation']
        )
        
        self.node.members[message.sender_id] = new_node
        print(f"🤝 Node {message.sender_id} joined cluster")
        
        # Send current membership back
        self._send_membership_update(new_node.address, new_node.port)
    
    def _handle_gossip_message(self, message: GossipMessage):
        """Handle gossip message with membership updates"""
        gossip_data = message.data
        
        # Update membership information
        for node_id, member_data in gossip_data.get('members', {}).items():
            if node_id not in self.node.members:
                # New member discovered
                self.node.members[node_id] = NodeInfo(
                    node_id=node_id,
                    address=member_data['address'],
                    port=member_data['port'],
                    state=NodeState(member_data['state']),
                    incarnation=member_data['incarnation'],
                    last_seen=member_data['last_seen']
                )
                print(f"🆕 Discovered new node: {node_id}")
            else:
                # Update existing member
                existing = self.node.members[node_id]
                if member_data['incarnation'] > existing.incarnation:
                    existing.state = NodeState(member_data['state'])
                    existing.incarnation = member_data['incarnation']
                    existing.last_seen = member_data['last_seen']
        
        # Update sender's last seen time
        if message.sender_id in self.node.members:
            self.node.members[message.sender_id].last_seen = time.time()
    
    def _handle_state_change_message(self, message: GossipMessage):
        """Handle state change notification"""
        data = message.data
        target_node = data['target_node']
        new_state = NodeState(data['new_state'])
        
        if target_node in self.node.members:
            self.node.members[target_node].state = new_state
            print(f"📢 Received state change: {target_node} -> {new_state.value}")
    
    def _handle_ping_message(self, message: GossipMessage, sender_addr):
        """Handle ping message and send ack"""
        ack_msg = GossipMessage(
            message_type="ack",
            sender_id=self.node.node_id,
            data={'ping_id': message.data.get('ping_id')}
        )
        
        self.socket.sendto(ack_msg.to_json().encode(), sender_addr)
    
    def _handle_ack_message(self, message: GossipMessage):
        """Handle ack message"""
        # Update last seen time for sender
        if message.sender_id in self.node.members:
            self.node.members[message.sender_id].last_seen = time.time()
    
    def _send_message(self, address: str, port: int, message: GossipMessage):
        """Send message to specific node"""
        try:
            self.socket.sendto(message.to_json().encode(), (address, port))
            self.node.stats['messages_sent'] += 1
        except Exception as e:
            print(f"❌ Failed to send message to {address}:{port}: {e}")
    
    def _send_membership_update(self, address: str, port: int):
        """Send current membership to a node"""
        membership_data = {
            'members': {
                node_id: {
                    'address': info.address,
                    'port': info.port,
                    'state': info.state.value,
                    'incarnation': info.incarnation,
                    'last_seen': info.last_seen
                }
                for node_id, info in self.node.members.items()
            }
        }
        
        update_msg = GossipMessage(
            message_type="gossip",
            sender_id=self.node.node_id,
            data=membership_data
        )
        
        self._send_message(address, port, update_msg)
    
    def get_cluster_state(self) -> Dict:
        """Get current cluster state"""
        return {
            'node_id': self.node.node_id,
            'members': {
                node_id: {
                    'state': info.state.value,
                    'address': f"{info.address}:{info.port}",
                    'last_seen': time.time() - info.last_seen
                }
                for node_id, info in self.node.members.items()
            },
            'local_state': self.node.local_state,
            'stats': self.node.stats
        }

def demonstrate_gossip_protocol():
    """Demonstrate gossip protocol with multiple nodes"""
    print("=== Gossip Protocol Demonstration ===")
    
    # Create multiple nodes
    nodes = []
    protocols = []
    
    base_port = 9000
    for i in range(5):
        node = GossipNode(
            node_id=f"node_{i}",
            address="127.0.0.1",
            port=base_port + i,
            gossip_interval=0.5,
            fanout=2
        )
        protocol = GossipProtocol(node)
        nodes.append(node)
        protocols.append(protocol)
    
    try:
        # Start all nodes
        for protocol in protocols:
            protocol.start()
            time.sleep(0.1)
        
        # Join nodes to cluster
        seed_nodes = [("127.0.0.1", base_port)]
        for i, protocol in enumerate(protocols[1:], 1):
            protocol.join_cluster(seed_nodes)
            time.sleep(0.2)
        
        print(f"\n🌐 Cluster formation complete with {len(nodes)} nodes")
        
        # Let gossip propagate
        time.sleep(2)
        
        # Update some local state
        protocols[0].update_local_state("service", "web-server")
        protocols[1].update_local_state("version", "1.2.3")
        protocols[2].update_local_state("region", "us-west")
        
        # Let state propagate
        time.sleep(3)
        
        # Simulate node failure
        print(f"\n💥 Simulating failure of {nodes[3].node_id}")
        protocols[3].stop()
        
        # Let failure detection work
        time.sleep(6)
        
        # Print final cluster state
        print(f"\n📊 Final Cluster State:")
        for i, protocol in enumerate(protocols[:3]):  # Only running nodes
            state = protocol.get_cluster_state()
            print(f"\n   Node {state['node_id']}:")
            print(f"     Members: {len(state['members'])}")
            for member_id, member_info in state['members'].items():
                status = "🟢" if member_info['state'] == 'alive' else "🔴" if member_info['state'] == 'dead' else "🟡"
                print(f"       {status} {member_id}: {member_info['state']} (last seen: {member_info['last_seen']:.1f}s ago)")
            
            if state['local_state']:
                print(f"     Local state: {state['local_state']}")
            
            print(f"     Stats: {state['stats']['gossip_rounds']} rounds, "
                  f"{state['stats']['messages_sent']} sent, "
                  f"{state['stats']['messages_received']} received")
    
    finally:
        # Cleanup
        for protocol in protocols:
            try:
                protocol.stop()
            except:
                pass
    
    print("\n🎯 Gossip protocol demonstrates:")
    print("💡 Decentralized information dissemination")
    print("💡 Automatic failure detection and recovery")
    print("💡 Eventual consistency across the cluster")
    print("💡 Scalable membership management")

if __name__ == "__main__":
    demonstrate_gossip_protocol()
