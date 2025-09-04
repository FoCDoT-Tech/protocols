#!/usr/bin/env python3
"""
Paxos Consensus Algorithm Simulation
Implements Multi-Paxos with proposers, acceptors, and learners.
"""

import time
import random
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
import json

@dataclass
class Proposal:
    proposal_id: int
    value: str
    
@dataclass
class Promise:
    proposal_id: int
    accepted_proposal_id: Optional[int] = None
    accepted_value: Optional[str] = None

@dataclass
class PaxosNode:
    node_id: int
    # Proposer state
    proposal_number: int = 0
    promised_proposals: Set[int] = field(default_factory=set)
    
    # Acceptor state
    highest_proposal_seen: int = -1
    accepted_proposal: Optional[Proposal] = None
    
    # Learner state
    learned_values: Dict[int, str] = field(default_factory=dict)
    
    # Network simulation
    active: bool = True
    message_delay: float = 0.01

class PaxosCluster:
    def __init__(self, node_count: int = 5):
        self.nodes = {i: PaxosNode(i) for i in range(node_count)}
        self.network_partition = set()
        self.message_delay = 0.01
        self.stats = {
            'proposals': 0,
            'promises': 0,
            'accepts': 0,
            'learns': 0,
            'rounds': 0
        }
    
    def is_partitioned(self, from_node: int, to_node: int) -> bool:
        """Check if nodes are network partitioned"""
        return (from_node in self.network_partition) != (to_node in self.network_partition)
    
    def send_message(self, from_node: int, to_node: int, message: dict) -> bool:
        """Simulate network message with delay and partition handling"""
        if not self.nodes[to_node].active or self.is_partitioned(from_node, to_node):
            return False
        
        # Simulate network delay
        time.sleep(self.message_delay)
        return True
    
    def generate_proposal_id(self, node_id: int) -> int:
        """Generate unique proposal ID using node ID and timestamp"""
        timestamp = int(time.time() * 1000000)  # microseconds
        return (timestamp << 8) | node_id  # Combine timestamp and node ID
    
    def phase1_prepare(self, proposer_id: int, proposal_id: int) -> Dict[int, Promise]:
        """Phase 1: Prepare - Send prepare requests to acceptors"""
        proposer = self.nodes[proposer_id]
        promises = {}
        
        print(f"📤 Phase 1: Node {proposer_id} sending PREPARE({proposal_id})")
        
        for acceptor_id, acceptor in self.nodes.items():
            if not self.send_message(proposer_id, acceptor_id, {
                'type': 'prepare',
                'proposal_id': proposal_id
            }):
                continue
            
            # Acceptor logic
            if proposal_id > acceptor.highest_proposal_seen:
                acceptor.highest_proposal_seen = proposal_id
                promise = Promise(
                    proposal_id=proposal_id,
                    accepted_proposal_id=acceptor.accepted_proposal.proposal_id if acceptor.accepted_proposal else None,
                    accepted_value=acceptor.accepted_proposal.value if acceptor.accepted_proposal else None
                )
                promises[acceptor_id] = promise
                self.stats['promises'] += 1
        
        majority = len(self.nodes) // 2 + 1
        print(f"   Promises received: {len(promises)}/{len(self.nodes)} (need {majority})")
        
        return promises
    
    def phase2_accept(self, proposer_id: int, proposal_id: int, value: str, 
                     promises: Dict[int, Promise]) -> Dict[int, bool]:
        """Phase 2: Accept - Send accept requests to acceptors"""
        
        # Choose value based on promises
        chosen_value = value
        highest_accepted_id = -1
        
        for promise in promises.values():
            if (promise.accepted_proposal_id is not None and 
                promise.accepted_proposal_id > highest_accepted_id):
                highest_accepted_id = promise.accepted_proposal_id
                chosen_value = promise.accepted_value
        
        print(f"📤 Phase 2: Node {proposer_id} sending ACCEPT({proposal_id}, '{chosen_value}')")
        
        accepts = {}
        proposal = Proposal(proposal_id, chosen_value)
        
        for acceptor_id, acceptor in self.nodes.items():
            if acceptor_id not in promises:
                continue
                
            if not self.send_message(proposer_id, acceptor_id, {
                'type': 'accept',
                'proposal_id': proposal_id,
                'value': chosen_value
            }):
                continue
            
            # Acceptor logic
            if proposal_id >= acceptor.highest_proposal_seen:
                acceptor.accepted_proposal = proposal
                accepts[acceptor_id] = True
                self.stats['accepts'] += 1
            else:
                accepts[acceptor_id] = False
        
        majority = len(self.nodes) // 2 + 1
        accept_count = sum(1 for accepted in accepts.values() if accepted)
        print(f"   Accepts received: {accept_count}/{len(promises)} (need {majority})")
        
        # If majority accepted, notify learners
        if accept_count >= majority:
            self.notify_learners(proposal_id, chosen_value)
            return accepts
        
        return accepts
    
    def notify_learners(self, proposal_id: int, value: str):
        """Notify all learners of the chosen value"""
        print(f"📢 Notifying learners: CHOSEN({proposal_id}, '{value}')")
        
        for learner_id, learner in self.nodes.items():
            learner.learned_values[proposal_id] = value
            self.stats['learns'] += 1
    
    def propose_value(self, proposer_id: int, value: str) -> bool:
        """Full Paxos proposal process"""
        proposer = self.nodes[proposer_id]
        proposal_id = self.generate_proposal_id(proposer_id)
        
        self.stats['proposals'] += 1
        self.stats['rounds'] += 1
        
        print(f"\n🎯 Node {proposer_id} proposing value: '{value}'")
        
        # Phase 1: Prepare
        promises = self.phase1_prepare(proposer_id, proposal_id)
        majority = len(self.nodes) // 2 + 1
        
        if len(promises) < majority:
            print(f"   ❌ Phase 1 failed: insufficient promises")
            return False
        
        # Phase 2: Accept
        accepts = self.phase2_accept(proposer_id, proposal_id, value, promises)
        accept_count = sum(1 for accepted in accepts.values() if accepted)
        
        if accept_count >= majority:
            print(f"   ✅ Consensus reached for '{value}'")
            return True
        else:
            print(f"   ❌ Phase 2 failed: insufficient accepts")
            return False
    
    def simulate_partition(self, partitioned_nodes: List[int]):
        """Simulate network partition"""
        self.network_partition = set(partitioned_nodes)
        print(f"🔌 Network partition: {partitioned_nodes} vs {list(set(self.nodes.keys()) - self.network_partition)}")
    
    def heal_partition(self):
        """Heal network partition"""
        self.network_partition.clear()
        print("🔗 Network partition healed")
    
    def crash_node(self, node_id: int):
        """Simulate node crash"""
        self.nodes[node_id].active = False
        print(f"💥 Node {node_id} crashed")
    
    def recover_node(self, node_id: int):
        """Simulate node recovery"""
        self.nodes[node_id].active = True
        print(f"🔄 Node {node_id} recovered")
    
    def run_simulation(self):
        """Run Paxos simulation with various scenarios"""
        print("🚀 Starting Paxos consensus simulation")
        print(f"   Cluster size: {len(self.nodes)} nodes")
        
        # Scenario 1: Normal operation
        print("\n=== Scenario 1: Normal Operation ===")
        self.propose_value(0, "initial_config")
        time.sleep(0.1)
        
        # Scenario 2: Competing proposals
        print("\n=== Scenario 2: Competing Proposals ===")
        # Simulate concurrent proposals
        threading.Thread(target=lambda: self.propose_value(1, "config_v1")).start()
        time.sleep(0.05)  # Small delay
        threading.Thread(target=lambda: self.propose_value(2, "config_v2")).start()
        time.sleep(0.2)
        
        # Scenario 3: Network partition
        print("\n=== Scenario 3: Network Partition ===")
        self.simulate_partition([0, 1])
        self.propose_value(2, "partition_config")  # Should succeed (majority in larger partition)
        self.propose_value(0, "minority_config")   # Should fail (minority partition)
        time.sleep(0.1)
        
        # Scenario 4: Partition healing
        print("\n=== Scenario 4: Partition Healing ===")
        self.heal_partition()
        self.propose_value(3, "healed_config")
        time.sleep(0.1)
        
        # Scenario 5: Node failure
        print("\n=== Scenario 5: Node Failure ===")
        self.crash_node(4)
        self.propose_value(1, "failure_config")
        self.recover_node(4)
        time.sleep(0.1)
        
        self.print_final_state()
    
    def print_final_state(self):
        """Print final cluster state"""
        print("\n📊 Final Cluster State:")
        
        for node_id, node in self.nodes.items():
            status = "🟢" if node.active else "🔴"
            print(f"   {status} Node {node_id}:")
            print(f"      Highest proposal seen: {node.highest_proposal_seen}")
            if node.accepted_proposal:
                print(f"      Accepted: {node.accepted_proposal.proposal_id} -> '{node.accepted_proposal.value}'")
            print(f"      Learned values: {len(node.learned_values)}")
            for prop_id, value in list(node.learned_values.items())[:3]:
                print(f"        {prop_id}: '{value}'")
        
        print(f"\n📈 Simulation Statistics:")
        print(f"   Proposals: {self.stats['proposals']}")
        print(f"   Rounds: {self.stats['rounds']}")
        print(f"   Promises: {self.stats['promises']}")
        print(f"   Accepts: {self.stats['accepts']}")
        print(f"   Learns: {self.stats['learns']}")

def demonstrate_paxos():
    """Demonstrate Paxos consensus algorithm"""
    print("=== Paxos Consensus Algorithm Demonstration ===")
    
    # Create cluster
    cluster = PaxosCluster(node_count=5)
    
    # Run simulation
    cluster.run_simulation()
    
    print("\n🎯 Paxos demonstrates:")
    print("💡 Two-phase protocol: prepare and accept")
    print("💡 Safety: at most one value chosen per instance")
    print("💡 Liveness: progress despite failures (with majority)")
    print("💡 Theoretical foundation for distributed consensus")

if __name__ == "__main__":
    demonstrate_paxos()
