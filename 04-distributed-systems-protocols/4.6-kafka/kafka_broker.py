#!/usr/bin/env python3
"""
Kafka Broker Simulation
Distributed streaming platform broker implementation with partitioning and replication.
"""

import time
import threading
import json
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict, deque
import hashlib
import bisect

class MessageCompression(Enum):
    NONE = "none"
    GZIP = "gzip"
    SNAPPY = "snappy"
    LZ4 = "lz4"

class AckLevel(Enum):
    NONE = 0      # Fire and forget
    LEADER = 1    # Wait for leader acknowledgment
    ALL = -1      # Wait for all in-sync replicas

@dataclass
class KafkaMessage:
    key: Optional[str]
    value: str
    timestamp: float
    offset: int
    partition: int
    headers: Dict[str, str] = field(default_factory=dict)
    
    def size(self) -> int:
        """Calculate message size in bytes"""
        key_size = len(self.key.encode('utf-8')) if self.key else 0
        value_size = len(self.value.encode('utf-8'))
        headers_size = sum(len(k.encode('utf-8')) + len(v.encode('utf-8')) 
                          for k, v in self.headers.items())
        return key_size + value_size + headers_size + 32  # Overhead

@dataclass
class TopicPartition:
    topic: str
    partition: int
    
    def __hash__(self):
        return hash((self.topic, self.partition))

@dataclass
class PartitionInfo:
    topic: str
    partition: int
    leader: int
    replicas: List[int]
    in_sync_replicas: List[int]
    log: deque = field(default_factory=deque)
    high_water_mark: int = 0
    log_end_offset: int = 0
    
    def append_message(self, message: KafkaMessage) -> int:
        """Append message to partition log"""
        message.offset = self.log_end_offset
        message.partition = self.partition
        self.log.append(message)
        self.log_end_offset += 1
        
        # Update high water mark (simplified)
        self.high_water_mark = self.log_end_offset
        
        return message.offset

@dataclass
class ConsumerGroup:
    group_id: str
    members: Dict[str, 'KafkaConsumer'] = field(default_factory=dict)
    partition_assignment: Dict[str, List[TopicPartition]] = field(default_factory=dict)
    offsets: Dict[TopicPartition, int] = field(default_factory=dict)
    generation_id: int = 0
    leader: Optional[str] = None

class KafkaBroker:
    def __init__(self, broker_id: int, host: str = "localhost", port: int = 9092):
        self.broker_id = broker_id
        self.host = host
        self.port = port
        
        # Topic and partition management
        self.topics: Dict[str, int] = {}  # topic -> partition count
        self.partitions: Dict[TopicPartition, PartitionInfo] = {}
        self.partition_leaders: Dict[TopicPartition, int] = {}
        
        # Consumer group management
        self.consumer_groups: Dict[str, ConsumerGroup] = {}
        
        # Cluster coordination (simplified ZooKeeper)
        self.cluster_brokers: Dict[int, Dict] = {broker_id: {'host': host, 'port': port}}
        self.controller_id: int = broker_id
        
        # Statistics
        self.stats = {
            'messages_produced': 0,
            'messages_consumed': 0,
            'bytes_in': 0,
            'bytes_out': 0,
            'start_time': time.time()
        }
        
        self.running = False
        self._lock = threading.Lock()
        
        print(f"🚀 Kafka Broker {broker_id} initialized on {host}:{port}")
    
    def start(self):
        """Start the Kafka broker"""
        self.running = True
        threading.Thread(target=self._background_tasks, daemon=True).start()
        print(f"🚀 Kafka Broker {self.broker_id} started")
    
    def stop(self):
        """Stop the Kafka broker"""
        self.running = False
        print(f"🛑 Kafka Broker {self.broker_id} stopped")
    
    def create_topic(self, topic: str, partitions: int = 3, replication_factor: int = 1) -> bool:
        """Create a new topic with specified partitions"""
        with self._lock:
            if topic in self.topics:
                return False
            
            self.topics[topic] = partitions
            
            # Create partitions
            for partition_id in range(partitions):
                tp = TopicPartition(topic, partition_id)
                
                # Assign replicas (simplified - single broker for demo)
                replicas = [self.broker_id]
                leader = self.broker_id
                
                partition_info = PartitionInfo(
                    topic=topic,
                    partition=partition_id,
                    leader=leader,
                    replicas=replicas,
                    in_sync_replicas=replicas.copy()
                )
                
                self.partitions[tp] = partition_info
                self.partition_leaders[tp] = leader
            
            print(f"📁 Created topic '{topic}' with {partitions} partitions")
            return True
    
    def produce_message(self, topic: str, key: Optional[str], value: str, 
                       partition: Optional[int] = None, 
                       headers: Optional[Dict[str, str]] = None,
                       ack_level: AckLevel = AckLevel.LEADER) -> Tuple[int, int]:
        """Produce a message to a topic"""
        with self._lock:
            if topic not in self.topics:
                raise ValueError(f"Topic '{topic}' does not exist")
            
            # Determine partition
            if partition is None:
                if key:
                    # Hash-based partitioning
                    partition = hash(key) % self.topics[topic]
                else:
                    # Round-robin partitioning (simplified)
                    partition = self.stats['messages_produced'] % self.topics[topic]
            
            tp = TopicPartition(topic, partition)
            
            if tp not in self.partitions:
                raise ValueError(f"Partition {partition} does not exist for topic '{topic}'")
            
            # Create message
            message = KafkaMessage(
                key=key,
                value=value,
                timestamp=time.time(),
                offset=0,  # Will be set by partition
                partition=partition,
                headers=headers or {}
            )
            
            # Append to partition log
            partition_info = self.partitions[tp]
            offset = partition_info.append_message(message)
            
            # Update statistics
            self.stats['messages_produced'] += 1
            self.stats['bytes_in'] += message.size()
            
            print(f"📤 Produced message to {topic}[{partition}] at offset {offset}")
            
            return partition, offset
    
    def consume_messages(self, topic: str, partition: int, offset: int, 
                        max_messages: int = 100) -> List[KafkaMessage]:
        """Consume messages from a topic partition"""
        with self._lock:
            tp = TopicPartition(topic, partition)
            
            if tp not in self.partitions:
                return []
            
            partition_info = self.partitions[tp]
            messages = []
            
            # Find starting position in log
            current_offset = offset
            
            for message in partition_info.log:
                if message.offset >= current_offset and len(messages) < max_messages:
                    messages.append(message)
                    self.stats['messages_consumed'] += 1
                    self.stats['bytes_out'] += message.size()
            
            if messages:
                print(f"📥 Consumed {len(messages)} messages from {topic}[{partition}] starting at offset {offset}")
            
            return messages
    
    def join_consumer_group(self, group_id: str, consumer_id: str, 
                           topics: List[str]) -> Dict[str, List[int]]:
        """Join a consumer to a consumer group"""
        with self._lock:
            if group_id not in self.consumer_groups:
                self.consumer_groups[group_id] = ConsumerGroup(group_id)
            
            group = self.consumer_groups[group_id]
            
            # Add consumer to group (simplified)
            group.members[consumer_id] = None  # Would store consumer reference
            
            # Trigger rebalance
            assignment = self._rebalance_consumer_group(group_id, topics)
            
            print(f"👥 Consumer '{consumer_id}' joined group '{group_id}'")
            
            return assignment.get(consumer_id, {})
    
    def leave_consumer_group(self, group_id: str, consumer_id: str) -> bool:
        """Remove consumer from consumer group"""
        with self._lock:
            if group_id not in self.consumer_groups:
                return False
            
            group = self.consumer_groups[group_id]
            
            if consumer_id in group.members:
                del group.members[consumer_id]
                
                # Remove from partition assignment
                if consumer_id in group.partition_assignment:
                    del group.partition_assignment[consumer_id]
                
                print(f"👥 Consumer '{consumer_id}' left group '{group_id}'")
                
                # Trigger rebalance if there are remaining members
                if group.members:
                    self._rebalance_consumer_group(group_id, [])
                
                return True
            
            return False
    
    def commit_offset(self, group_id: str, topic: str, partition: int, offset: int) -> bool:
        """Commit consumer offset for a partition"""
        with self._lock:
            if group_id not in self.consumer_groups:
                return False
            
            group = self.consumer_groups[group_id]
            tp = TopicPartition(topic, partition)
            group.offsets[tp] = offset
            
            print(f"✅ Committed offset {offset} for {topic}[{partition}] in group '{group_id}'")
            
            return True
    
    def get_committed_offset(self, group_id: str, topic: str, partition: int) -> Optional[int]:
        """Get committed offset for a consumer group partition"""
        with self._lock:
            if group_id not in self.consumer_groups:
                return None
            
            group = self.consumer_groups[group_id]
            tp = TopicPartition(topic, partition)
            
            return group.offsets.get(tp, 0)  # Default to beginning
    
    def get_topic_metadata(self, topic: str) -> Optional[Dict]:
        """Get metadata for a topic"""
        with self._lock:
            if topic not in self.topics:
                return None
            
            partitions_info = []
            for partition_id in range(self.topics[topic]):
                tp = TopicPartition(topic, partition_id)
                if tp in self.partitions:
                    partition_info = self.partitions[tp]
                    partitions_info.append({
                        'partition': partition_id,
                        'leader': partition_info.leader,
                        'replicas': partition_info.replicas,
                        'in_sync_replicas': partition_info.in_sync_replicas,
                        'high_water_mark': partition_info.high_water_mark,
                        'log_end_offset': partition_info.log_end_offset
                    })
            
            return {
                'topic': topic,
                'partitions': partitions_info
            }
    
    def _rebalance_consumer_group(self, group_id: str, topics: List[str]) -> Dict[str, Dict[str, List[int]]]:
        """Rebalance partitions among consumers in a group"""
        group = self.consumer_groups[group_id]
        
        # Get all partitions for subscribed topics
        all_partitions = []
        for topic in topics:
            if topic in self.topics:
                for partition_id in range(self.topics[topic]):
                    all_partitions.append(TopicPartition(topic, partition_id))
        
        # Simple round-robin assignment
        consumers = list(group.members.keys())
        assignment = defaultdict(lambda: defaultdict(list))
        
        for i, tp in enumerate(all_partitions):
            if consumers:
                consumer = consumers[i % len(consumers)]
                assignment[consumer][tp.topic].append(tp.partition)
        
        # Update group assignment
        group.partition_assignment = dict(assignment)
        group.generation_id += 1
        
        if consumers:
            group.leader = consumers[0]
        
        print(f"🔄 Rebalanced consumer group '{group_id}' (generation {group.generation_id})")
        
        return dict(assignment)
    
    def _background_tasks(self):
        """Background maintenance tasks"""
        while self.running:
            try:
                # Log compaction, cleanup, etc. would go here
                time.sleep(10)
            except Exception as e:
                print(f"❌ Background task error: {e}")
    
    def get_broker_stats(self) -> Dict:
        """Get broker statistics"""
        with self._lock:
            return {
                'broker_id': self.broker_id,
                'uptime': time.time() - self.stats['start_time'],
                'topics': len(self.topics),
                'partitions': len(self.partitions),
                'consumer_groups': len(self.consumer_groups),
                'messages_produced': self.stats['messages_produced'],
                'messages_consumed': self.stats['messages_consumed'],
                'bytes_in': self.stats['bytes_in'],
                'bytes_out': self.stats['bytes_out']
            }

def demonstrate_kafka_broker():
    """Demonstrate Kafka broker functionality"""
    print("=== Kafka Broker Demonstration ===")
    
    broker = KafkaBroker(broker_id=1)
    broker.start()
    
    try:
        # Create topics
        print(f"\n📁 Creating topics...")
        broker.create_topic("orders", partitions=3, replication_factor=1)
        broker.create_topic("inventory", partitions=2, replication_factor=1)
        broker.create_topic("user-activity", partitions=4, replication_factor=1)
        
        # Produce messages
        print(f"\n📤 Producing messages...")
        
        # Orders topic
        orders = [
            ("user123", '{"order_id": "ORD-001", "user_id": "user123", "amount": 99.99}'),
            ("user456", '{"order_id": "ORD-002", "user_id": "user456", "amount": 149.50}'),
            ("user123", '{"order_id": "ORD-003", "user_id": "user123", "amount": 79.99}'),
            ("user789", '{"order_id": "ORD-004", "user_id": "user789", "amount": 199.99}')
        ]
        
        for key, value in orders:
            broker.produce_message("orders", key, value, 
                                 headers={"source": "order-service", "version": "1.0"})
        
        # Inventory updates
        inventory_updates = [
            ("widget-123", '{"product_id": "widget-123", "quantity": 50, "warehouse": "US-WEST"}'),
            ("gadget-456", '{"product_id": "gadget-456", "quantity": 25, "warehouse": "US-EAST"}')
        ]
        
        for key, value in inventory_updates:
            broker.produce_message("inventory", key, value)
        
        # User activity
        activities = [
            ("user123", '{"user_id": "user123", "action": "view_product", "product_id": "widget-123"}'),
            ("user456", '{"user_id": "user456", "action": "add_to_cart", "product_id": "gadget-456"}'),
            ("user123", '{"user_id": "user123", "action": "purchase", "order_id": "ORD-001"}')
        ]
        
        for key, value in activities:
            broker.produce_message("user-activity", key, value)
        
        # Set up consumer groups
        print(f"\n👥 Setting up consumer groups...")
        
        # Order processing group
        assignment1 = broker.join_consumer_group("order-processing", "processor-1", ["orders"])
        assignment2 = broker.join_consumer_group("order-processing", "processor-2", ["orders"])
        
        # Analytics group
        assignment3 = broker.join_consumer_group("analytics", "analytics-1", ["orders", "user-activity"])
        
        # Consume messages
        print(f"\n📥 Consuming messages...")
        
        # Consume from orders topic
        for partition in range(3):
            messages = broker.consume_messages("orders", partition, 0, max_messages=10)
            for msg in messages:
                print(f"   Order[{partition}:{msg.offset}]: {msg.value[:50]}...")
        
        # Consume from user-activity
        for partition in range(2):
            messages = broker.consume_messages("user-activity", partition, 0, max_messages=10)
            for msg in messages:
                print(f"   Activity[{partition}:{msg.offset}]: {msg.value[:50]}...")
        
        # Commit offsets
        print(f"\n✅ Committing offsets...")
        broker.commit_offset("order-processing", "orders", 0, 2)
        broker.commit_offset("order-processing", "orders", 1, 1)
        broker.commit_offset("analytics", "user-activity", 0, 2)
        
        # Get topic metadata
        print(f"\n📊 Topic metadata:")
        orders_metadata = broker.get_topic_metadata("orders")
        if orders_metadata:
            print(f"   Topic: {orders_metadata['topic']}")
            for partition_info in orders_metadata['partitions']:
                print(f"     Partition {partition_info['partition']}: "
                     f"leader={partition_info['leader']}, "
                     f"HW={partition_info['high_water_mark']}, "
                     f"LEO={partition_info['log_end_offset']}")
        
        time.sleep(1)  # Let background tasks run
        
        # Display statistics
        print(f"\n📊 Broker Statistics:")
        stats = broker.get_broker_stats()
        print(f"   Broker ID: {stats['broker_id']}")
        print(f"   Uptime: {stats['uptime']:.1f}s")
        print(f"   Topics: {stats['topics']}")
        print(f"   Partitions: {stats['partitions']}")
        print(f"   Consumer Groups: {stats['consumer_groups']}")
        print(f"   Messages Produced: {stats['messages_produced']}")
        print(f"   Messages Consumed: {stats['messages_consumed']}")
        print(f"   Bytes In: {stats['bytes_in']}")
        print(f"   Bytes Out: {stats['bytes_out']}")
        
        # Clean up consumer groups
        broker.leave_consumer_group("order-processing", "processor-1")
        broker.leave_consumer_group("order-processing", "processor-2")
        broker.leave_consumer_group("analytics", "analytics-1")
    
    finally:
        broker.stop()
    
    print("\n🎯 Kafka Broker demonstrates:")
    print("💡 Distributed streaming with partitioned topics")
    print("💡 Producer and consumer coordination")
    print("💡 Consumer groups with automatic rebalancing")
    print("💡 Offset management and message replay")
    print("💡 High-throughput message processing")

if __name__ == "__main__":
    demonstrate_kafka_broker()
