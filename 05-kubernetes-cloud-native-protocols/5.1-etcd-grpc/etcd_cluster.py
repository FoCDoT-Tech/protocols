#!/usr/bin/env python3
"""
etcd Cluster Implementation with Raft Consensus
Simulates etcd cluster with gRPC-style operations and Raft consensus.
"""

import time
import json
import threading
import random
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import uuid

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass
class LogEntry:
    term: int
    index: int
    key: str
    value: Any
    operation: str  # PUT, DELETE, etc.
    timestamp: float = field(default_factory=time.time)

@dataclass
class WatchEvent:
    event_type: str  # PUT, DELETE
    key: str
    value: Any
    revision: int
    timestamp: float = field(default_factory=time.time)

class EtcdNode:
    def __init__(self, node_id: str, cluster_nodes: List[str]):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.state = NodeState.FOLLOWER
        
        # Raft state
        self.current_term = 0
        self.voted_for = None
        self.log: List[LogEntry] = []
        self.commit_index = 0
        self.last_applied = 0
        
        # Leader state
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}
        
        # Key-value store
        self.kv_store: Dict[str, Any] = {}
        self.revision = 0
        
        # Watch streams
        self.watchers: Dict[str, List[Callable[[WatchEvent], None]]] = {}
        
        # Cluster communication
        self.leader_id = None
        self.election_timeout = random.uniform(150, 300) / 1000  # 150-300ms
        self.heartbeat_interval = 50 / 1000  # 50ms
        self.last_heartbeat = time.time()
        
        # Threading
        self.running = False
        self.election_thread = None
        self.heartbeat_thread = None
        
        # Statistics
        self.stats = {
            'requests_served': 0,
            'elections_started': 0,
            'heartbeats_sent': 0,
            'log_entries_replicated': 0
        }
    
    def start(self):
        """Start the etcd node"""
        self.running = True
        self.last_heartbeat = time.time()
        
        # Start election timer
        self.election_thread = threading.Thread(target=self._election_loop, daemon=True)
        self.election_thread.start()
        
        print(f"🚀 etcd node {self.node_id} started")
    
    def stop(self):
        """Stop the etcd node"""
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=1)
        print(f"🛑 etcd node {self.node_id} stopped")
    
    def _election_loop(self):
        """Main election timeout loop"""
        while self.running:
            time.sleep(0.01)  # 10ms check interval
            
            if self.state != NodeState.LEADER:
                time_since_heartbeat = time.time() - self.last_heartbeat
                if time_since_heartbeat > self.election_timeout:
                    self._start_election()
    
    def _start_election(self):
        """Start leader election"""
        if not self.running:
            return
            
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.last_heartbeat = time.time()
        self.stats['elections_started'] += 1
        
        print(f"🗳️  Node {self.node_id} starting election for term {self.current_term}")
        
        # In a real implementation, we would send RequestVote RPCs
        # For simulation, assume we get majority votes
        votes_received = 1  # Vote for self
        required_votes = len(self.cluster_nodes) // 2 + 1
        
        # Simulate receiving votes from other nodes
        for node in self.cluster_nodes:
            if node != self.node_id and random.random() > 0.3:  # 70% chance of vote
                votes_received += 1
        
        if votes_received >= required_votes:
            self._become_leader()
        else:
            self.state = NodeState.FOLLOWER
            self.voted_for = None
    
    def _become_leader(self):
        """Become cluster leader"""
        self.state = NodeState.LEADER
        self.leader_id = self.node_id
        
        # Initialize leader state
        self.next_index = {node: len(self.log) + 1 for node in self.cluster_nodes if node != self.node_id}
        self.match_index = {node: 0 for node in self.cluster_nodes if node != self.node_id}
        
        print(f"👑 Node {self.node_id} became leader for term {self.current_term}")
        
        # Start sending heartbeats
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=0.1)
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
    
    def _heartbeat_loop(self):
        """Send periodic heartbeats as leader"""
        while self.running and self.state == NodeState.LEADER:
            self._send_heartbeats()
            time.sleep(self.heartbeat_interval)
    
    def _send_heartbeats(self):
        """Send heartbeat to all followers"""
        if self.state != NodeState.LEADER:
            return
        
        self.stats['heartbeats_sent'] += 1
        # In real implementation, send AppendEntries RPC to all followers
        # For simulation, just update our heartbeat timestamp
        self.last_heartbeat = time.time()
    
    def receive_heartbeat(self, leader_id: str, term: int):
        """Receive heartbeat from leader"""
        if term >= self.current_term:
            self.current_term = term
            self.state = NodeState.FOLLOWER
            self.leader_id = leader_id
            self.last_heartbeat = time.time()
            self.voted_for = None
    
    def put(self, key: str, value: Any) -> bool:
        """Put key-value pair (gRPC Put operation)"""
        if self.state != NodeState.LEADER:
            return False
        
        # Create log entry
        entry = LogEntry(
            term=self.current_term,
            index=len(self.log) + 1,
            key=key,
            value=value,
            operation="PUT"
        )
        
        self.log.append(entry)
        self.stats['log_entries_replicated'] += 1
        
        # Apply to state machine immediately (simplified)
        self._apply_entry(entry)
        
        print(f"📝 Put: {key} = {value} (revision {self.revision})")
        return True
    
    def get(self, key: str) -> Optional[Any]:
        """Get value by key (gRPC Get operation)"""
        self.stats['requests_served'] += 1
        value = self.kv_store.get(key)
        if value is not None:
            print(f"📖 Get: {key} = {value}")
        return value
    
    def delete(self, key: str) -> bool:
        """Delete key (gRPC Delete operation)"""
        if self.state != NodeState.LEADER:
            return False
        
        if key not in self.kv_store:
            return False
        
        # Create log entry
        entry = LogEntry(
            term=self.current_term,
            index=len(self.log) + 1,
            key=key,
            value=None,
            operation="DELETE"
        )
        
        self.log.append(entry)
        self._apply_entry(entry)
        
        print(f"🗑️  Delete: {key} (revision {self.revision})")
        return True
    
    def watch(self, key_prefix: str, callback: Callable[[WatchEvent], None]):
        """Watch for changes to keys with prefix (gRPC Watch operation)"""
        if key_prefix not in self.watchers:
            self.watchers[key_prefix] = []
        self.watchers[key_prefix].append(callback)
        print(f"👁️  Watching: {key_prefix}")
    
    def _apply_entry(self, entry: LogEntry):
        """Apply log entry to state machine"""
        self.revision += 1
        
        if entry.operation == "PUT":
            old_value = self.kv_store.get(entry.key)
            self.kv_store[entry.key] = entry.value
            
            # Notify watchers
            self._notify_watchers(WatchEvent(
                event_type="PUT",
                key=entry.key,
                value=entry.value,
                revision=self.revision
            ))
            
        elif entry.operation == "DELETE":
            if entry.key in self.kv_store:
                del self.kv_store[entry.key]
                
                # Notify watchers
                self._notify_watchers(WatchEvent(
                    event_type="DELETE",
                    key=entry.key,
                    value=None,
                    revision=self.revision
                ))
        
        self.last_applied = entry.index
    
    def _notify_watchers(self, event: WatchEvent):
        """Notify all relevant watchers of an event"""
        for prefix, callbacks in self.watchers.items():
            if event.key.startswith(prefix):
                for callback in callbacks:
                    try:
                        callback(event)
                    except Exception as e:
                        print(f"⚠️  Watcher error: {e}")
    
    def transaction(self, operations: List[Dict[str, Any]]) -> bool:
        """Execute transaction (gRPC Txn operation)"""
        if self.state != NodeState.LEADER:
            return False
        
        # Simplified transaction - just execute all operations
        success = True
        for op in operations:
            if op['type'] == 'PUT':
                success &= self.put(op['key'], op['value'])
            elif op['type'] == 'DELETE':
                success &= self.delete(op['key'])
        
        return success

class EtcdCluster:
    def __init__(self, node_count: int = 3):
        self.nodes: Dict[str, EtcdNode] = {}
        self.node_count = node_count
        
        # Create cluster nodes
        node_ids = [f"etcd-{i}" for i in range(node_count)]
        
        for node_id in node_ids:
            self.nodes[node_id] = EtcdNode(node_id, node_ids)
    
    def start(self):
        """Start all nodes in the cluster"""
        for node in self.nodes.values():
            node.start()
        
        # Wait for leader election
        time.sleep(0.5)
        print(f"🌐 etcd cluster started with {self.node_count} nodes")
    
    def stop(self):
        """Stop all nodes in the cluster"""
        for node in self.nodes.values():
            node.stop()
        print("🛑 etcd cluster stopped")
    
    def get_leader(self) -> Optional[EtcdNode]:
        """Get current cluster leader"""
        for node in self.nodes.values():
            if node.state == NodeState.LEADER:
                return node
        return None
    
    def get_client_node(self) -> Optional[EtcdNode]:
        """Get a node for client operations (prefer leader)"""
        leader = self.get_leader()
        if leader:
            return leader
        
        # Fallback to any running node
        for node in self.nodes.values():
            if node.running:
                return node
        return None

def demonstrate_etcd_cluster():
    """Demonstrate etcd cluster with gRPC-style operations"""
    print("=== etcd Cluster with gRPC Operations ===")
    
    # Create and start cluster
    cluster = EtcdCluster(3)
    cluster.start()
    
    try:
        # Get client connection
        client = cluster.get_client_node()
        if not client:
            print("❌ No available etcd nodes")
            return
        
        print(f"\n📡 Using etcd node: {client.node_id}")
        
        # Demonstrate basic operations
        print("\n📝 Basic Key-Value Operations:")
        client.put("/registry/pods/default/web-1", {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "web-1", "namespace": "default"},
            "spec": {"containers": [{"name": "nginx", "image": "nginx:1.20"}]}
        })
        
        client.put("/registry/services/default/web-service", {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "web-service", "namespace": "default"},
            "spec": {"ports": [{"port": 80, "targetPort": 8080}]}
        })
        
        # Get operations
        print("\n📖 Retrieving Kubernetes Objects:")
        pod = client.get("/registry/pods/default/web-1")
        service = client.get("/registry/services/default/web-service")
        
        # Watch for changes
        print("\n👁️  Setting up Watch Streams:")
        def pod_watcher(event: WatchEvent):
            print(f"🔔 Pod event: {event.event_type} {event.key} (rev {event.revision})")
        
        def service_watcher(event: WatchEvent):
            print(f"🔔 Service event: {event.event_type} {event.key} (rev {event.revision})")
        
        client.watch("/registry/pods/", pod_watcher)
        client.watch("/registry/services/", service_watcher)
        
        # Simulate updates
        print("\n🔄 Simulating Kubernetes Updates:")
        time.sleep(0.1)
        
        client.put("/registry/pods/default/web-2", {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "web-2", "namespace": "default"},
            "spec": {"containers": [{"name": "nginx", "image": "nginx:1.21"}]}
        })
        
        client.put("/registry/services/default/api-service", {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "api-service", "namespace": "default"},
            "spec": {"ports": [{"port": 443, "targetPort": 8443}]}
        })
        
        # Transaction example
        print("\n🔄 Atomic Transaction:")
        client.transaction([
            {"type": "PUT", "key": "/registry/configmaps/default/app-config", "value": {"data": {"env": "production"}}},
            {"type": "PUT", "key": "/registry/secrets/default/app-secret", "value": {"data": {"password": "encrypted_value"}}}
        ])
        
        time.sleep(0.2)
        
        # Delete operations
        print("\n🗑️  Cleanup Operations:")
        client.delete("/registry/pods/default/web-1")
        
        time.sleep(0.1)
        
        # Show cluster state
        print("\n📊 Cluster State:")
        leader = cluster.get_leader()
        if leader:
            print(f"   Leader: {leader.node_id} (term {leader.current_term})")
            print(f"   Keys stored: {len(leader.kv_store)}")
            print(f"   Current revision: {leader.revision}")
            print(f"   Log entries: {len(leader.log)}")
        
        # Show statistics
        print("\n📈 Node Statistics:")
        for node_id, node in cluster.nodes.items():
            print(f"   {node_id}: {node.state.value}")
            print(f"     Requests served: {node.stats['requests_served']}")
            print(f"     Elections started: {node.stats['elections_started']}")
            print(f"     Heartbeats sent: {node.stats['heartbeats_sent']}")
            print(f"     Log entries: {node.stats['log_entries_replicated']}")
    
    finally:
        cluster.stop()
    
    print("\n🎯 etcd Cluster demonstrates:")
    print("💡 Raft consensus for distributed consistency")
    print("💡 gRPC-style key-value operations")
    print("💡 Real-time watch streams for change notifications")
    print("💡 Kubernetes-style resource storage patterns")
    print("💡 Leader election and cluster coordination")

if __name__ == "__main__":
    demonstrate_etcd_cluster()
