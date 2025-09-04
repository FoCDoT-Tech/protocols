#!/usr/bin/env python3
"""
Anti-Entropy Mechanisms for Gossip Protocols
Handles state synchronization and partition recovery.
"""

import time
import random
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
import hashlib
import json

class SyncState(Enum):
    IN_SYNC = "in_sync"
    OUT_OF_SYNC = "out_of_sync"
    SYNCING = "syncing"

@dataclass
class StateEntry:
    key: str
    value: str
    version: int
    timestamp: float
    node_id: str
    
    def to_dict(self) -> Dict:
        return {
            'key': self.key,
            'value': self.value,
            'version': self.version,
            'timestamp': self.timestamp,
            'node_id': self.node_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StateEntry':
        return cls(**data)

@dataclass
class StateDiff:
    missing_entries: List[StateEntry] = field(default_factory=list)
    outdated_entries: List[StateEntry] = field(default_factory=list)
    conflicting_entries: List[Tuple[StateEntry, StateEntry]] = field(default_factory=list)

class AntiEntropyManager:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.state: Dict[str, StateEntry] = {}
        self.version_vector: Dict[str, int] = {}
        
        # Configuration
        self.sync_interval = 5.0
        self.full_sync_interval = 30.0
        self.max_sync_peers = 3
        self.conflict_resolution = "last_write_wins"
        
        # State tracking
        self.sync_state = SyncState.IN_SYNC
        self.last_full_sync = 0
        self.sync_peers: Set[str] = set()
        self.running = False
        
        # Statistics
        self.stats = {
            'sync_rounds': 0,
            'full_syncs': 0,
            'conflicts_resolved': 0,
            'entries_synchronized': 0,
            'bytes_transferred': 0
        }
    
    def start(self):
        """Start anti-entropy processes"""
        self.running = True
        threading.Thread(target=self._anti_entropy_loop, daemon=True).start()
        threading.Thread(target=self._full_sync_loop, daemon=True).start()
        print(f"🔄 Anti-entropy manager started for {self.node_id}")
    
    def stop(self):
        """Stop anti-entropy processes"""
        self.running = False
        print(f"🛑 Anti-entropy manager stopped for {self.node_id}")
    
    def put(self, key: str, value: str) -> bool:
        """Put a key-value pair with versioning"""
        current_version = self.version_vector.get(self.node_id, 0) + 1
        self.version_vector[self.node_id] = current_version
        
        entry = StateEntry(
            key=key,
            value=value,
            version=current_version,
            timestamp=time.time(),
            node_id=self.node_id
        )
        
        self.state[key] = entry
        print(f"📝 Put: {key} = {value} (v{current_version})")
        return True
    
    def get(self, key: str) -> Optional[str]:
        """Get value for a key"""
        entry = self.state.get(key)
        return entry.value if entry else None
    
    def delete(self, key: str) -> bool:
        """Delete a key (tombstone approach)"""
        if key in self.state:
            # Create tombstone entry
            current_version = self.version_vector.get(self.node_id, 0) + 1
            self.version_vector[self.node_id] = current_version
            
            tombstone = StateEntry(
                key=key,
                value="__DELETED__",
                version=current_version,
                timestamp=time.time(),
                node_id=self.node_id
            )
            
            self.state[key] = tombstone
            print(f"🗑️ Deleted: {key} (tombstone v{current_version})")
            return True
        return False
    
    def add_sync_peer(self, peer_id: str):
        """Add a peer for synchronization"""
        self.sync_peers.add(peer_id)
        print(f"🤝 Added sync peer: {peer_id}")
    
    def remove_sync_peer(self, peer_id: str):
        """Remove a peer from synchronization"""
        self.sync_peers.discard(peer_id)
        print(f"👋 Removed sync peer: {peer_id}")
    
    def _anti_entropy_loop(self):
        """Main anti-entropy loop"""
        while self.running:
            try:
                if self.sync_peers:
                    self._perform_incremental_sync()
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"❌ Anti-entropy loop error: {e}")
    
    def _full_sync_loop(self):
        """Full synchronization loop"""
        while self.running:
            try:
                current_time = time.time()
                if current_time - self.last_full_sync > self.full_sync_interval:
                    self._perform_full_sync()
                    self.last_full_sync = current_time
                time.sleep(self.full_sync_interval / 4)
            except Exception as e:
                print(f"❌ Full sync loop error: {e}")
    
    def _perform_incremental_sync(self):
        """Perform incremental synchronization with random peers"""
        if not self.sync_peers:
            return
        
        # Select random subset of peers
        peers_to_sync = random.sample(
            list(self.sync_peers),
            min(self.max_sync_peers, len(self.sync_peers))
        )
        
        for peer_id in peers_to_sync:
            self._sync_with_peer(peer_id, full_sync=False)
        
        self.stats['sync_rounds'] += 1
    
    def _perform_full_sync(self):
        """Perform full synchronization with all peers"""
        if not self.sync_peers:
            return
        
        print(f"🔄 Performing full sync with {len(self.sync_peers)} peers")
        
        for peer_id in self.sync_peers:
            self._sync_with_peer(peer_id, full_sync=True)
        
        self.stats['full_syncs'] += 1
        print(f"✅ Full sync completed")
    
    def _sync_with_peer(self, peer_id: str, full_sync: bool = False):
        """Synchronize state with a specific peer"""
        # Simulate peer communication
        peer_state = self._simulate_peer_state(peer_id)
        peer_version_vector = self._simulate_peer_version_vector(peer_id)
        
        # Calculate differences
        diff = self._calculate_state_diff(peer_state, peer_version_vector)
        
        if diff.missing_entries or diff.outdated_entries or diff.conflicting_entries:
            self.sync_state = SyncState.SYNCING
            self._apply_state_diff(diff, peer_id)
            self.sync_state = SyncState.IN_SYNC
        
        # Update statistics
        entries_synced = len(diff.missing_entries) + len(diff.outdated_entries)
        self.stats['entries_synchronized'] += entries_synced
        
        if entries_synced > 0:
            print(f"🔄 Synced {entries_synced} entries with {peer_id}")
    
    def _simulate_peer_state(self, peer_id: str) -> Dict[str, StateEntry]:
        """Simulate getting state from a peer"""
        # In real implementation, this would be network communication
        # For simulation, create some synthetic peer state
        
        peer_state = {}
        
        # Simulate peer having some of our entries with different versions
        for key, entry in random.sample(list(self.state.items()), 
                                       min(3, len(self.state))):
            # Sometimes peer has older version
            if random.random() < 0.3:
                peer_entry = StateEntry(
                    key=key,
                    value=entry.value + "_peer",
                    version=max(1, entry.version - 1),
                    timestamp=entry.timestamp - random.uniform(1, 10),
                    node_id=peer_id
                )
                peer_state[key] = peer_entry
            else:
                peer_state[key] = entry
        
        # Simulate peer having some unique entries
        for i in range(random.randint(0, 2)):
            unique_key = f"peer_{peer_id}_key_{i}"
            peer_state[unique_key] = StateEntry(
                key=unique_key,
                value=f"peer_value_{i}",
                version=random.randint(1, 5),
                timestamp=time.time() - random.uniform(0, 60),
                node_id=peer_id
            )
        
        return peer_state
    
    def _simulate_peer_version_vector(self, peer_id: str) -> Dict[str, int]:
        """Simulate getting version vector from a peer"""
        # Create a version vector that might be behind or ahead
        peer_vector = self.version_vector.copy()
        
        # Sometimes peer is behind
        if random.random() < 0.4:
            for node in list(peer_vector.keys()):
                if random.random() < 0.5:
                    peer_vector[node] = max(1, peer_vector[node] - random.randint(1, 3))
        
        # Peer might have updates from other nodes
        peer_vector[peer_id] = peer_vector.get(peer_id, 0) + random.randint(1, 3)
        
        return peer_vector
    
    def _calculate_state_diff(self, peer_state: Dict[str, StateEntry], 
                             peer_version_vector: Dict[str, int]) -> StateDiff:
        """Calculate differences between local and peer state"""
        diff = StateDiff()
        
        # Find entries we're missing
        for key, peer_entry in peer_state.items():
            if key not in self.state:
                diff.missing_entries.append(peer_entry)
            else:
                local_entry = self.state[key]
                
                # Check for conflicts or updates
                if peer_entry.version > local_entry.version:
                    diff.outdated_entries.append(peer_entry)
                elif (peer_entry.version == local_entry.version and 
                      peer_entry.value != local_entry.value):
                    diff.conflicting_entries.append((local_entry, peer_entry))
        
        return diff
    
    def _apply_state_diff(self, diff: StateDiff, peer_id: str):
        """Apply state differences from peer"""
        # Apply missing entries
        for entry in diff.missing_entries:
            self.state[entry.key] = entry
            self._update_version_vector(entry.node_id, entry.version)
            print(f"📥 Received missing entry: {entry.key} = {entry.value}")
        
        # Apply outdated entries (peer has newer version)
        for entry in diff.outdated_entries:
            self.state[entry.key] = entry
            self._update_version_vector(entry.node_id, entry.version)
            print(f"🔄 Updated entry: {entry.key} = {entry.value} (v{entry.version})")
        
        # Resolve conflicts
        for local_entry, peer_entry in diff.conflicting_entries:
            resolved_entry = self._resolve_conflict(local_entry, peer_entry)
            self.state[resolved_entry.key] = resolved_entry
            self.stats['conflicts_resolved'] += 1
            print(f"⚖️ Resolved conflict for {resolved_entry.key}: chose {resolved_entry.value}")
    
    def _resolve_conflict(self, local_entry: StateEntry, peer_entry: StateEntry) -> StateEntry:
        """Resolve conflicts between local and peer entries"""
        if self.conflict_resolution == "last_write_wins":
            return local_entry if local_entry.timestamp > peer_entry.timestamp else peer_entry
        elif self.conflict_resolution == "node_id_priority":
            return local_entry if local_entry.node_id < peer_entry.node_id else peer_entry
        else:
            # Default to local entry
            return local_entry
    
    def _update_version_vector(self, node_id: str, version: int):
        """Update version vector with new information"""
        current_version = self.version_vector.get(node_id, 0)
        self.version_vector[node_id] = max(current_version, version)
    
    def get_state_summary(self) -> Dict:
        """Get summary of current state"""
        total_entries = len(self.state)
        deleted_entries = sum(1 for entry in self.state.values() 
                             if entry.value == "__DELETED__")
        
        return {
            'node_id': self.node_id,
            'total_entries': total_entries,
            'active_entries': total_entries - deleted_entries,
            'deleted_entries': deleted_entries,
            'version_vector': self.version_vector,
            'sync_state': self.sync_state.value,
            'sync_peers': list(self.sync_peers),
            'stats': self.stats,
            'sample_entries': {
                key: entry.value 
                for key, entry in list(self.state.items())[:5]
                if entry.value != "__DELETED__"
            }
        }
    
    def simulate_partition_recovery(self, partition_duration: float):
        """Simulate recovery from network partition"""
        print(f"🔌 Simulating partition for {partition_duration}s")
        
        # Store current peers
        original_peers = self.sync_peers.copy()
        
        # Clear peers to simulate partition
        self.sync_peers.clear()
        self.sync_state = SyncState.OUT_OF_SYNC
        
        # Wait for partition duration
        time.sleep(partition_duration)
        
        # Restore peers and trigger recovery
        self.sync_peers = original_peers
        print(f"🔗 Partition healed, triggering recovery sync")
        
        # Force immediate full sync
        self._perform_full_sync()

def demonstrate_anti_entropy():
    """Demonstrate anti-entropy mechanisms"""
    print("=== Anti-Entropy Mechanisms Demonstration ===")
    
    # Create multiple nodes
    nodes = []
    for i in range(4):
        node = AntiEntropyManager(f"node_{i}")
        nodes.append(node)
    
    try:
        # Start all nodes
        for node in nodes:
            node.start()
        
        # Set up peer relationships
        for i, node in enumerate(nodes):
            for j, other_node in enumerate(nodes):
                if i != j:
                    node.add_sync_peer(other_node.node_id)
        
        print(f"\n🌐 Created cluster with {len(nodes)} nodes")
        
        # Add some initial data
        print(f"\n📝 Adding initial data...")
        nodes[0].put("config", "production")
        nodes[0].put("version", "1.0.0")
        nodes[1].put("region", "us-west")
        nodes[1].put("datacenter", "dc1")
        nodes[2].put("service", "web-server")
        
        # Let synchronization happen
        time.sleep(3)
        
        # Create conflicts
        print(f"\n⚔️ Creating conflicts...")
        nodes[0].put("config", "staging")  # Conflict with production
        nodes[1].put("config", "development")  # Another conflict
        
        # Let conflict resolution happen
        time.sleep(2)
        
        # Simulate network partition
        print(f"\n🔌 Simulating network partition...")
        
        # Partition nodes[0] and nodes[1] from nodes[2] and nodes[3]
        for node in nodes[:2]:
            node.sync_peers = {n.node_id for n in nodes[:2] if n != node}
        for node in nodes[2:]:
            node.sync_peers = {n.node_id for n in nodes[2:] if n != node}
        
        # Make changes during partition
        nodes[0].put("partition_data", "group_a")
        nodes[2].put("partition_data", "group_b")
        nodes[1].put("status", "partitioned_a")
        nodes[3].put("status", "partitioned_b")
        
        time.sleep(3)
        
        # Heal partition
        print(f"\n🔗 Healing network partition...")
        for i, node in enumerate(nodes):
            node.sync_peers = {n.node_id for n in nodes if n != node}
        
        # Force full sync after partition healing
        for node in nodes:
            node._perform_full_sync()
        
        time.sleep(3)
        
        # Print final state
        print(f"\n📊 Final State Summary:")
        for node in nodes:
            summary = node.get_state_summary()
            print(f"\n   Node {summary['node_id']}:")
            print(f"     Active entries: {summary['active_entries']}")
            print(f"     Version vector: {summary['version_vector']}")
            print(f"     Sync state: {summary['sync_state']}")
            print(f"     Sample entries: {summary['sample_entries']}")
            print(f"     Stats: {summary['stats']['sync_rounds']} rounds, "
                  f"{summary['stats']['conflicts_resolved']} conflicts resolved")
    
    finally:
        # Cleanup
        for node in nodes:
            try:
                node.stop()
            except:
                pass
    
    print("\n🎯 Anti-entropy demonstrates:")
    print("💡 Automatic state synchronization across nodes")
    print("💡 Conflict detection and resolution")
    print("💡 Partition tolerance and recovery")
    print("💡 Version vector-based consistency")

if __name__ == "__main__":
    demonstrate_anti_entropy()
