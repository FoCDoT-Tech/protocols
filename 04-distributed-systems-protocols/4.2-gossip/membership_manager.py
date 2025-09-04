#!/usr/bin/env python3
"""
Gossip-based Membership Manager
Manages cluster membership with failure detection and recovery.
"""

import time
import random
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Callable
import uuid

class MembershipEventType(Enum):
    JOIN = "join"
    LEAVE = "leave"
    FAIL = "fail"
    RECOVER = "recover"

@dataclass
class Member:
    member_id: str
    address: str
    metadata: Dict[str, str] = field(default_factory=dict)
    join_time: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    incarnation: int = 0
    is_alive: bool = True
    suspicion_count: int = 0

@dataclass
class MembershipEvent:
    event_type: MembershipEventType
    member_id: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)

class MembershipManager:
    def __init__(self, local_member_id: str, address: str):
        self.local_member_id = local_member_id
        self.local_address = address
        self.members: Dict[str, Member] = {}
        self.event_handlers: List[Callable[[MembershipEvent], None]] = []
        
        # Configuration
        self.heartbeat_interval = 1.0
        self.failure_timeout = 5.0
        self.suspicion_threshold = 3
        self.gossip_fanout = 3
        self.cleanup_interval = 10.0
        
        # State
        self.running = False
        self.incarnation = 0
        self.event_log: List[MembershipEvent] = []
        
        # Statistics
        self.stats = {
            'members_joined': 0,
            'members_left': 0,
            'failures_detected': 0,
            'recoveries': 0,
            'gossip_messages': 0
        }
        
        # Add self as member
        self._add_local_member()
    
    def _add_local_member(self):
        """Add local node as a member"""
        self.members[self.local_member_id] = Member(
            member_id=self.local_member_id,
            address=self.local_address,
            incarnation=self.incarnation
        )
    
    def start(self):
        """Start membership management"""
        self.running = True
        
        # Start background threads
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()
        threading.Thread(target=self._failure_detector_loop, daemon=True).start()
        threading.Thread(target=self._cleanup_loop, daemon=True).start()
        
        print(f"🚀 Membership manager started for {self.local_member_id}")
    
    def stop(self):
        """Stop membership management"""
        self.running = False
        print(f"🛑 Membership manager stopped for {self.local_member_id}")
    
    def add_event_handler(self, handler: Callable[[MembershipEvent], None]):
        """Add event handler for membership changes"""
        self.event_handlers.append(handler)
    
    def join_member(self, member_id: str, address: str, metadata: Dict[str, str] = None):
        """Add a new member to the cluster"""
        if member_id in self.members:
            return False
        
        member = Member(
            member_id=member_id,
            address=address,
            metadata=metadata or {}
        )
        
        self.members[member_id] = member
        self.stats['members_joined'] += 1
        
        event = MembershipEvent(
            event_type=MembershipEventType.JOIN,
            member_id=member_id,
            metadata={'address': address, 'metadata': metadata or {}}
        )
        
        self._emit_event(event)
        self._gossip_membership_change(event)
        
        print(f"🤝 Member {member_id} joined cluster")
        return True
    
    def leave_member(self, member_id: str):
        """Remove a member from the cluster"""
        if member_id not in self.members:
            return False
        
        del self.members[member_id]
        self.stats['members_left'] += 1
        
        event = MembershipEvent(
            event_type=MembershipEventType.LEAVE,
            member_id=member_id
        )
        
        self._emit_event(event)
        self._gossip_membership_change(event)
        
        print(f"👋 Member {member_id} left cluster")
        return True
    
    def update_member_metadata(self, member_id: str, metadata: Dict[str, str]):
        """Update member metadata"""
        if member_id not in self.members:
            return False
        
        self.members[member_id].metadata.update(metadata)
        self.members[member_id].incarnation += 1
        
        if member_id == self.local_member_id:
            self.incarnation += 1
        
        print(f"📝 Updated metadata for {member_id}: {metadata}")
        return True
    
    def get_members(self, alive_only: bool = True) -> List[Member]:
        """Get list of cluster members"""
        if alive_only:
            return [m for m in self.members.values() if m.is_alive]
        return list(self.members.values())
    
    def get_member_count(self, alive_only: bool = True) -> int:
        """Get count of cluster members"""
        return len(self.get_members(alive_only))
    
    def is_member_alive(self, member_id: str) -> bool:
        """Check if member is alive"""
        return member_id in self.members and self.members[member_id].is_alive
    
    def _heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self.running:
            try:
                self._send_heartbeats()
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                print(f"❌ Heartbeat loop error: {e}")
    
    def _send_heartbeats(self):
        """Send heartbeat to random members"""
        alive_members = [m for m in self.members.values() 
                        if m.is_alive and m.member_id != self.local_member_id]
        
        if not alive_members:
            return
        
        # Select random subset for heartbeat
        targets = random.sample(alive_members, 
                               min(self.gossip_fanout, len(alive_members)))
        
        for target in targets:
            self._send_heartbeat(target)
    
    def _send_heartbeat(self, target: Member):
        """Send heartbeat to specific member"""
        # Simulate heartbeat message
        current_time = time.time()
        
        # Simulate network delay and potential failure
        if random.random() < 0.95:  # 95% success rate
            target.last_heartbeat = current_time
            target.suspicion_count = 0
            
            # Simulate receiving heartbeat response
            self.members[self.local_member_id].last_heartbeat = current_time
        else:
            # Simulate heartbeat failure
            target.suspicion_count += 1
    
    def _failure_detector_loop(self):
        """Detect failed members"""
        while self.running:
            try:
                self._detect_failures()
                time.sleep(self.failure_timeout / 2)
            except Exception as e:
                print(f"❌ Failure detector error: {e}")
    
    def _detect_failures(self):
        """Detect and handle member failures"""
        current_time = time.time()
        
        for member_id, member in list(self.members.items()):
            if member_id == self.local_member_id:
                continue
            
            time_since_heartbeat = current_time - member.last_heartbeat
            
            # Mark as failed if no heartbeat for timeout period
            if member.is_alive and time_since_heartbeat > self.failure_timeout:
                member.is_alive = False
                self.stats['failures_detected'] += 1
                
                event = MembershipEvent(
                    event_type=MembershipEventType.FAIL,
                    member_id=member_id
                )
                
                self._emit_event(event)
                self._gossip_membership_change(event)
                
                print(f"💀 Member {member_id} detected as failed")
            
            # Check for recovery
            elif not member.is_alive and time_since_heartbeat < self.failure_timeout / 2:
                member.is_alive = True
                member.suspicion_count = 0
                self.stats['recoveries'] += 1
                
                event = MembershipEvent(
                    event_type=MembershipEventType.RECOVER,
                    member_id=member_id
                )
                
                self._emit_event(event)
                self._gossip_membership_change(event)
                
                print(f"🔄 Member {member_id} recovered")
    
    def _cleanup_loop(self):
        """Cleanup dead members periodically"""
        while self.running:
            try:
                self._cleanup_dead_members()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                print(f"❌ Cleanup loop error: {e}")
    
    def _cleanup_dead_members(self):
        """Remove members that have been dead for too long"""
        current_time = time.time()
        cleanup_threshold = self.failure_timeout * 3  # 3x failure timeout
        
        to_remove = []
        for member_id, member in self.members.items():
            if (not member.is_alive and 
                current_time - member.last_heartbeat > cleanup_threshold):
                to_remove.append(member_id)
        
        for member_id in to_remove:
            del self.members[member_id]
            print(f"🧹 Cleaned up dead member: {member_id}")
    
    def _gossip_membership_change(self, event: MembershipEvent):
        """Gossip membership change to other members"""
        self.stats['gossip_messages'] += 1
        
        # In a real implementation, this would send the event to random members
        # For simulation, we just log it
        print(f"📡 Gossiping event: {event.event_type.value} for {event.member_id}")
    
    def _emit_event(self, event: MembershipEvent):
        """Emit membership event to handlers"""
        self.event_log.append(event)
        
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"❌ Event handler error: {e}")
    
    def get_cluster_info(self) -> Dict:
        """Get comprehensive cluster information"""
        alive_members = self.get_members(alive_only=True)
        dead_members = [m for m in self.members.values() if not m.is_alive]
        
        return {
            'local_member': self.local_member_id,
            'total_members': len(self.members),
            'alive_members': len(alive_members),
            'dead_members': len(dead_members),
            'members': {
                member.member_id: {
                    'address': member.address,
                    'alive': member.is_alive,
                    'join_time': member.join_time,
                    'last_heartbeat': member.last_heartbeat,
                    'metadata': member.metadata,
                    'uptime': time.time() - member.join_time
                }
                for member in self.members.values()
            },
            'stats': self.stats,
            'recent_events': [
                {
                    'type': event.event_type.value,
                    'member': event.member_id,
                    'timestamp': event.timestamp
                }
                for event in self.event_log[-10:]  # Last 10 events
            ]
        }

def demonstrate_membership_manager():
    """Demonstrate gossip-based membership management"""
    print("=== Gossip-based Membership Manager Demonstration ===")
    
    # Create membership managers for multiple nodes
    managers = []
    for i in range(5):
        manager = MembershipManager(f"node_{i}", f"192.168.1.{i+10}")
        managers.append(manager)
    
    # Add event handler to track membership changes
    def membership_event_handler(event: MembershipEvent):
        print(f"📢 Event: {event.event_type.value} - {event.member_id}")
    
    for manager in managers:
        manager.add_event_handler(membership_event_handler)
        manager.start()
    
    try:
        # Simulate cluster formation
        print("\n🌐 Simulating cluster formation...")
        
        # Nodes join each other
        for i, manager in enumerate(managers):
            for j, other_manager in enumerate(managers):
                if i != j:
                    manager.join_member(
                        other_manager.local_member_id,
                        other_manager.local_address,
                        {'role': 'worker', 'zone': f'zone_{j % 3}'}
                    )
        
        time.sleep(2)
        
        # Update some metadata
        print("\n📝 Updating member metadata...")
        managers[0].update_member_metadata(managers[0].local_member_id, 
                                         {'role': 'leader', 'version': '1.2.3'})
        managers[1].update_member_metadata(managers[1].local_member_id,
                                         {'load': 'high', 'cpu': '80%'})
        
        time.sleep(1)
        
        # Simulate node failures
        print("\n💥 Simulating node failures...")
        managers[3].stop()  # Node 3 fails
        
        # Let failure detection work
        time.sleep(6)
        
        # Simulate node recovery
        print("\n🔄 Simulating node recovery...")
        managers[3].start()
        
        # Re-join the recovered node
        for i, manager in enumerate(managers):
            if i != 3:
                manager.join_member(
                    managers[3].local_member_id,
                    managers[3].local_address,
                    {'role': 'worker', 'status': 'recovered'}
                )
        
        time.sleep(3)
        
        # Print cluster information
        print("\n📊 Final Cluster Information:")
        for i, manager in enumerate(managers[:3]):  # Show first 3 nodes
            info = manager.get_cluster_info()
            print(f"\n   Node {info['local_member']}:")
            print(f"     Total members: {info['total_members']}")
            print(f"     Alive members: {info['alive_members']}")
            print(f"     Dead members: {info['dead_members']}")
            
            print(f"     Member details:")
            for member_id, details in info['members'].items():
                status = "🟢" if details['alive'] else "🔴"
                print(f"       {status} {member_id}: {details['address']} "
                      f"(uptime: {details['uptime']:.1f}s)")
                if details['metadata']:
                    print(f"         Metadata: {details['metadata']}")
            
            print(f"     Stats: {info['stats']}")
            
            if info['recent_events']:
                print(f"     Recent events:")
                for event in info['recent_events'][-3:]:
                    print(f"       {event['type']}: {event['member']}")
    
    finally:
        # Cleanup
        for manager in managers:
            try:
                manager.stop()
            except:
                pass
    
    print("\n🎯 Membership manager demonstrates:")
    print("💡 Automatic member discovery and tracking")
    print("💡 Failure detection and recovery")
    print("💡 Metadata management and propagation")
    print("💡 Event-driven architecture for membership changes")

if __name__ == "__main__":
    demonstrate_membership_manager()
