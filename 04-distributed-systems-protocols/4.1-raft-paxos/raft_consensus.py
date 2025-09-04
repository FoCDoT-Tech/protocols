#!/usr/bin/env python3
"""
Raft Consensus Algorithm Simulation
Implements leader election, log replication, and safety properties.
"""

import time
import random
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import json

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass
class LogEntry:
    term: int
    index: int
    command: str
    committed: bool = False

@dataclass
class RaftNode:
    node_id: int
    current_term: int = 0
    voted_for: Optional[int] = None
    log: List[LogEntry] = field(default_factory=list)
    commit_index: int = 0
    last_applied: int = 0
    state: NodeState = NodeState.FOLLOWER
    
    # Leader state
    next_index: Dict[int, int] = field(default_factory=dict)
    match_index: Dict[int, int] = field(default_factory=dict)
    
    # Timing
    last_heartbeat: float = 0
    election_timeout: float = 0
    heartbeat_interval: float = 0.1
    
    def __post_init__(self):
        self.reset_election_timeout()
        self.last_heartbeat = time.time()

    def reset_election_timeout(self):
        # Randomized timeout between 150-300ms
        self.election_timeout = random.uniform(0.15, 0.3)

class RaftCluster:
    def __init__(self, node_count: int = 5):
        self.nodes = {i: RaftNode(i) for i in range(node_count)}
        self.network_partition = set()
        self.message_delay = 0.01  # 10ms network delay
        self.running = True
        self.stats = {
            'elections': 0,
            'log_entries': 0,
            'heartbeats': 0,
            'leader_changes': 0
        }
        
    def is_partitioned(self, from_node: int, to_node: int) -> bool:
        """Check if nodes are network partitioned"""
        return (from_node in self.network_partition) != (to_node in self.network_partition)
    
    def send_message(self, from_node: int, to_node: int, message: dict) -> bool:
        """Simulate network message with delay and partition handling"""
        if self.is_partitioned(from_node, to_node):
            return False
        
        # Simulate network delay
        time.sleep(self.message_delay)
        return True
    
    def request_vote(self, candidate_id: int, term: int, last_log_index: int, last_log_term: int) -> Dict[int, bool]:
        """RequestVote RPC implementation"""
        votes = {}
        candidate = self.nodes[candidate_id]
        
        for node_id, node in self.nodes.items():
            if node_id == candidate_id:
                votes[node_id] = True
                continue
                
            if not self.send_message(candidate_id, node_id, {
                'type': 'RequestVote',
                'term': term,
                'candidate_id': candidate_id,
                'last_log_index': last_log_index,
                'last_log_term': last_log_term
            }):
                votes[node_id] = False
                continue
            
            # Vote decision logic
            vote_granted = False
            if term > node.current_term:
                node.current_term = term
                node.voted_for = None
                node.state = NodeState.FOLLOWER
            
            if (term == node.current_term and 
                (node.voted_for is None or node.voted_for == candidate_id)):
                
                # Check log up-to-date condition
                node_last_log_term = node.log[-1].term if node.log else 0
                node_last_log_index = len(node.log) - 1 if node.log else -1
                
                log_ok = (last_log_term > node_last_log_term or 
                         (last_log_term == node_last_log_term and last_log_index >= node_last_log_index))
                
                if log_ok:
                    vote_granted = True
                    node.voted_for = candidate_id
                    node.reset_election_timeout()
            
            votes[node_id] = vote_granted
        
        return votes
    
    def append_entries(self, leader_id: int, term: int, prev_log_index: int, 
                      prev_log_term: int, entries: List[LogEntry], leader_commit: int) -> Dict[int, bool]:
        """AppendEntries RPC implementation"""
        responses = {}
        leader = self.nodes[leader_id]
        
        for node_id, node in self.nodes.items():
            if node_id == leader_id:
                continue
                
            if not self.send_message(leader_id, node_id, {
                'type': 'AppendEntries',
                'term': term,
                'leader_id': leader_id,
                'prev_log_index': prev_log_index,
                'prev_log_term': prev_log_term,
                'entries': [{'term': e.term, 'command': e.command} for e in entries],
                'leader_commit': leader_commit
            }):
                responses[node_id] = False
                continue
            
            success = False
            if term >= node.current_term:
                node.current_term = term
                node.state = NodeState.FOLLOWER
                node.voted_for = None
                node.last_heartbeat = time.time()
                
                # Log consistency check
                if (prev_log_index == -1 or 
                    (prev_log_index < len(node.log) and 
                     node.log[prev_log_index].term == prev_log_term)):
                    
                    # Append new entries
                    if entries:
                        # Remove conflicting entries
                        node.log = node.log[:prev_log_index + 1]
                        node.log.extend(entries)
                    
                    # Update commit index
                    if leader_commit > node.commit_index:
                        node.commit_index = min(leader_commit, len(node.log) - 1)
                    
                    success = True
            
            responses[node_id] = success
        
        return responses
    
    def start_election(self, node_id: int):
        """Start leader election for a node"""
        node = self.nodes[node_id]
        node.current_term += 1
        node.state = NodeState.CANDIDATE
        node.voted_for = node_id
        node.reset_election_timeout()
        
        self.stats['elections'] += 1
        
        print(f"🗳️  Node {node_id} starting election for term {node.current_term}")
        
        # Get vote requests
        last_log_index = len(node.log) - 1 if node.log else -1
        last_log_term = node.log[-1].term if node.log else 0
        
        votes = self.request_vote(node_id, node.current_term, last_log_index, last_log_term)
        vote_count = sum(1 for granted in votes.values() if granted)
        majority = len(self.nodes) // 2 + 1
        
        print(f"   Votes received: {vote_count}/{len(self.nodes)} (need {majority})")
        
        if vote_count >= majority:
            self.become_leader(node_id)
        else:
            node.state = NodeState.FOLLOWER
            print(f"   Election failed for node {node_id}")
    
    def become_leader(self, node_id: int):
        """Node becomes leader"""
        node = self.nodes[node_id]
        node.state = NodeState.LEADER
        
        # Initialize leader state
        for other_id in self.nodes:
            if other_id != node_id:
                node.next_index[other_id] = len(node.log)
                node.match_index[other_id] = -1
        
        self.stats['leader_changes'] += 1
        print(f"👑 Node {node_id} became leader for term {node.current_term}")
        
        # Send initial heartbeat
        self.send_heartbeat(node_id)
    
    def send_heartbeat(self, leader_id: int):
        """Send heartbeat to all followers"""
        leader = self.nodes[leader_id]
        if leader.state != NodeState.LEADER:
            return
        
        self.stats['heartbeats'] += 1
        
        for follower_id in self.nodes:
            if follower_id == leader_id:
                continue
            
            prev_log_index = leader.next_index.get(follower_id, 0) - 1
            prev_log_term = leader.log[prev_log_index].term if prev_log_index >= 0 else 0
            
            # Send empty entries for heartbeat
            responses = self.append_entries(
                leader_id, leader.current_term, prev_log_index, 
                prev_log_term, [], leader.commit_index
            )
    
    def replicate_log(self, leader_id: int, command: str):
        """Replicate log entry to followers"""
        leader = self.nodes[leader_id]
        if leader.state != NodeState.LEADER:
            return False
        
        # Create new log entry
        entry = LogEntry(
            term=leader.current_term,
            index=len(leader.log),
            command=command
        )
        leader.log.append(entry)
        self.stats['log_entries'] += 1
        
        print(f"📝 Leader {leader_id} replicating: {command}")
        
        # Replicate to followers
        success_count = 1  # Leader counts as success
        for follower_id in self.nodes:
            if follower_id == leader_id:
                continue
            
            prev_log_index = leader.next_index.get(follower_id, 0) - 1
            prev_log_term = leader.log[prev_log_index].term if prev_log_index >= 0 else 0
            
            responses = self.append_entries(
                leader_id, leader.current_term, prev_log_index,
                prev_log_term, [entry], leader.commit_index
            )
            
            if responses.get(follower_id, False):
                success_count += 1
                leader.match_index[follower_id] = entry.index
                leader.next_index[follower_id] = entry.index + 1
        
        # Check if majority replicated
        majority = len(self.nodes) // 2 + 1
        if success_count >= majority:
            entry.committed = True
            leader.commit_index = entry.index
            print(f"   ✅ Entry committed (replicated to {success_count}/{len(self.nodes)} nodes)")
            return True
        else:
            print(f"   ❌ Entry not committed (only {success_count}/{len(self.nodes)} nodes)")
            return False
    
    def get_leader(self) -> Optional[int]:
        """Find current leader"""
        for node_id, node in self.nodes.items():
            if node.state == NodeState.LEADER:
                return node_id
        return None
    
    def simulate_partition(self, partitioned_nodes: List[int]):
        """Simulate network partition"""
        self.network_partition = set(partitioned_nodes)
        print(f"🔌 Network partition: {partitioned_nodes} vs {list(set(self.nodes.keys()) - self.network_partition)}")
    
    def heal_partition(self):
        """Heal network partition"""
        self.network_partition.clear()
        print("🔗 Network partition healed")
    
    def run_simulation(self, duration: float = 5.0):
        """Run Raft simulation"""
        print("🚀 Starting Raft consensus simulation")
        print(f"   Cluster size: {len(self.nodes)} nodes")
        print(f"   Simulation duration: {duration}s")
        
        start_time = time.time()
        
        # Start with election
        self.start_election(0)
        
        simulation_events = [
            (1.0, lambda: self.replicate_log(self.get_leader(), "SET x=1")),
            (1.5, lambda: self.replicate_log(self.get_leader(), "SET y=2")),
            (2.0, lambda: self.simulate_partition([0, 1])),
            (2.5, lambda: self.replicate_log(self.get_leader(), "SET z=3")),
            (3.0, lambda: self.heal_partition()),
            (3.5, lambda: self.replicate_log(self.get_leader(), "SET w=4")),
            (4.0, lambda: self.replicate_log(self.get_leader(), "SET v=5"))
        ]
        
        event_index = 0
        
        while time.time() - start_time < duration:
            current_time = time.time() - start_time
            
            # Execute scheduled events
            while (event_index < len(simulation_events) and 
                   simulation_events[event_index][0] <= current_time):
                try:
                    simulation_events[event_index][1]()
                except:
                    pass  # Handle leader not available
                event_index += 1
            
            # Check for election timeouts
            for node_id, node in self.nodes.items():
                if (node.state in [NodeState.FOLLOWER, NodeState.CANDIDATE] and
                    time.time() - node.last_heartbeat > node.election_timeout):
                    self.start_election(node_id)
            
            # Send heartbeats
            leader_id = self.get_leader()
            if leader_id is not None:
                leader = self.nodes[leader_id]
                if time.time() - leader.last_heartbeat > leader.heartbeat_interval:
                    self.send_heartbeat(leader_id)
                    leader.last_heartbeat = time.time()
            
            time.sleep(0.01)  # 10ms simulation tick
        
        self.print_final_state()
    
    def print_final_state(self):
        """Print final cluster state"""
        print("\n📊 Final Cluster State:")
        
        for node_id, node in self.nodes.items():
            status = "👑" if node.state == NodeState.LEADER else "👥"
            print(f"   {status} Node {node_id}: {node.state.value} (term {node.current_term})")
            print(f"      Log entries: {len(node.log)}, Committed: {node.commit_index + 1}")
            if node.log:
                for i, entry in enumerate(node.log[:3]):  # Show first 3 entries
                    committed = "✅" if entry.committed else "⏳"
                    print(f"        {committed} [{i}] {entry.command} (term {entry.term})")
                if len(node.log) > 3:
                    print(f"        ... and {len(node.log) - 3} more entries")
        
        print(f"\n📈 Simulation Statistics:")
        print(f"   Elections: {self.stats['elections']}")
        print(f"   Leader changes: {self.stats['leader_changes']}")
        print(f"   Log entries: {self.stats['log_entries']}")
        print(f"   Heartbeats: {self.stats['heartbeats']}")

def demonstrate_raft():
    """Demonstrate Raft consensus algorithm"""
    print("=== Raft Consensus Algorithm Demonstration ===")
    
    # Create cluster
    cluster = RaftCluster(node_count=5)
    
    # Run simulation
    cluster.run_simulation(duration=5.0)
    
    print("\n🎯 Raft demonstrates:")
    print("💡 Leader election with randomized timeouts")
    print("💡 Log replication with majority consensus")
    print("💡 Safety: committed entries never lost")
    print("💡 Partition tolerance: minority cannot make progress")

if __name__ == "__main__":
    demonstrate_raft()
