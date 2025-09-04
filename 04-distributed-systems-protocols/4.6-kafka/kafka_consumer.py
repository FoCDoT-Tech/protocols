#!/usr/bin/env python3
"""
Kafka Consumer Implementation
High-throughput consumer with group coordination and offset management.
"""

import time
import threading
import json
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Set
from collections import defaultdict

from kafka_broker import KafkaBroker, KafkaMessage, TopicPartition

class AutoOffsetReset(Enum):
    EARLIEST = "earliest"
    LATEST = "latest"
    NONE = "none"

class IsolationLevel(Enum):
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"

@dataclass
class ConsumerConfig:
    bootstrap_servers: List[str] = field(default_factory=lambda: ["localhost:9092"])
    group_id: Optional[str] = None
    client_id: str = "kafka-consumer"
    auto_offset_reset: AutoOffsetReset = AutoOffsetReset.LATEST
    enable_auto_commit: bool = True
    auto_commit_interval_ms: int = 5000
    max_poll_records: int = 500
    max_poll_interval_ms: int = 300000
    session_timeout_ms: int = 10000
    heartbeat_interval_ms: int = 3000
    fetch_min_bytes: int = 1
    fetch_max_wait_ms: int = 500
    isolation_level: IsolationLevel = IsolationLevel.READ_UNCOMMITTED

@dataclass
class ConsumerRecord:
    topic: str
    partition: int
    offset: int
    key: Optional[str]
    value: str
    timestamp: float
    headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class OffsetAndMetadata:
    offset: int
    metadata: str = ""
    timestamp: Optional[float] = None

class KafkaConsumer:
    def __init__(self, topics: List[str], config: ConsumerConfig, broker: Optional[KafkaBroker] = None):
        self.topics = set(topics)
        self.config = config
        self.broker = broker  # For simulation
        
        # Consumer state
        self.consumer_id = f"{config.client_id}-{uuid.uuid4().hex[:8]}"
        self.assignment: Dict[TopicPartition, int] = {}  # partition -> next offset
        self.committed_offsets: Dict[TopicPartition, OffsetAndMetadata] = {}
        
        # Group coordination
        self.group_coordinator = None
        self.generation_id = -1
        self.member_id = ""
        
        # Threading
        self._lock = threading.Lock()
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._auto_commit_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Message processing
        self.message_buffer: Dict[TopicPartition, List[ConsumerRecord]] = defaultdict(list)
        self.last_poll_time = time.time()
        
        # Statistics
        self.stats = {
            'records_consumed': 0,
            'bytes_consumed': 0,
            'commits': 0,
            'rebalances': 0,
            'start_time': time.time()
        }
        
        # Callbacks
        self.rebalance_listener: Optional['ConsumerRebalanceListener'] = None
        
        self._initialize_consumer()
        print(f"🚀 Kafka Consumer initialized (id: {self.consumer_id}, group: {config.group_id})")
    
    def subscribe(self, topics: List[str], listener: Optional['ConsumerRebalanceListener'] = None) -> None:
        """Subscribe to topics with optional rebalance listener"""
        with self._lock:
            self.topics = set(topics)
            self.rebalance_listener = listener
            
            # Join consumer group if group_id is set
            if self.config.group_id and self.broker:
                assignment = self.broker.join_consumer_group(
                    self.config.group_id, self.consumer_id, topics
                )
                self._update_assignment(assignment)
        
        print(f"📝 Subscribed to topics: {topics}")
    
    def assign(self, partitions: List[TopicPartition]) -> None:
        """Manually assign partitions (disables group coordination)"""
        with self._lock:
            self.assignment.clear()
            
            for tp in partitions:
                # Get starting offset
                if self.config.auto_offset_reset == AutoOffsetReset.EARLIEST:
                    offset = 0
                elif self.config.auto_offset_reset == AutoOffsetReset.LATEST:
                    # Get latest offset from broker
                    if self.broker:
                        metadata = self.broker.get_topic_metadata(tp.topic)
                        if metadata:
                            for partition_info in metadata['partitions']:
                                if partition_info['partition'] == tp.partition:
                                    offset = partition_info['log_end_offset']
                                    break
                            else:
                                offset = 0
                        else:
                            offset = 0
                    else:
                        offset = 0
                else:
                    raise ValueError("Cannot assign partitions with auto_offset_reset=none")
                
                self.assignment[tp] = offset
        
        print(f"📍 Manually assigned partitions: {[f'{tp.topic}[{tp.partition}]' for tp in partitions]}")
    
    def poll(self, timeout_ms: int = 1000) -> Dict[TopicPartition, List[ConsumerRecord]]:
        """Poll for new messages"""
        start_time = time.time()
        timeout_seconds = timeout_ms / 1000.0
        
        records = defaultdict(list)
        
        with self._lock:
            # Check if we need to rejoin group
            if time.time() - self.last_poll_time > self.config.max_poll_interval_ms / 1000.0:
                print("⚠️  Max poll interval exceeded, rejoining group")
                if self.config.group_id and self.broker:
                    self._rejoin_group()
            
            self.last_poll_time = time.time()
            
            # Fetch messages for assigned partitions
            for tp, offset in self.assignment.items():
                if self.broker:
                    messages = self.broker.consume_messages(
                        tp.topic, tp.partition, offset, 
                        max_messages=min(self.config.max_poll_records, 100)
                    )
                    
                    for msg in messages:
                        record = ConsumerRecord(
                            topic=msg.topic if hasattr(msg, 'topic') else tp.topic,
                            partition=msg.partition,
                            offset=msg.offset,
                            key=msg.key,
                            value=msg.value,
                            timestamp=msg.timestamp,
                            headers=msg.headers
                        )
                        
                        records[tp].append(record)
                        
                        # Update next offset
                        self.assignment[tp] = msg.offset + 1
                        
                        # Update statistics
                        self.stats['records_consumed'] += 1
                        self.stats['bytes_consumed'] += msg.size()
                
                # Break if we have enough records or timeout
                total_records = sum(len(record_list) for record_list in records.values())
                if total_records >= self.config.max_poll_records:
                    break
                
                if time.time() - start_time >= timeout_seconds:
                    break
        
        if records:
            total_records = sum(len(record_list) for record_list in records.values())
            print(f"📥 Polled {total_records} records from {len(records)} partitions")
        
        return dict(records)
    
    def commit_sync(self, offsets: Optional[Dict[TopicPartition, OffsetAndMetadata]] = None) -> None:
        """Synchronously commit offsets"""
        with self._lock:
            if offsets is None:
                # Commit current position for all assigned partitions
                offsets = {tp: OffsetAndMetadata(offset) for tp, offset in self.assignment.items()}
            
            # Commit to broker
            if self.config.group_id and self.broker:
                for tp, offset_metadata in offsets.items():
                    success = self.broker.commit_offset(
                        self.config.group_id, tp.topic, tp.partition, offset_metadata.offset
                    )
                    if success:
                        self.committed_offsets[tp] = offset_metadata
            
            self.stats['commits'] += 1
        
        print(f"✅ Committed offsets for {len(offsets)} partitions")
    
    def commit_async(self, offsets: Optional[Dict[TopicPartition, OffsetAndMetadata]] = None,
                    callback: Optional[Callable[[Dict[TopicPartition, OffsetAndMetadata], Exception], None]] = None) -> None:
        """Asynchronously commit offsets"""
        def commit_task():
            try:
                self.commit_sync(offsets)
                if callback:
                    callback(offsets or {}, None)
            except Exception as e:
                if callback:
                    callback(offsets or {}, e)
        
        threading.Thread(target=commit_task, daemon=True).start()
    
    def seek(self, partition: TopicPartition, offset: int) -> None:
        """Seek to a specific offset"""
        with self._lock:
            if partition in self.assignment:
                self.assignment[partition] = offset
                print(f"🎯 Seeking {partition.topic}[{partition.partition}] to offset {offset}")
            else:
                raise ValueError(f"Partition {partition} not assigned to this consumer")
    
    def seek_to_beginning(self, partitions: Optional[List[TopicPartition]] = None) -> None:
        """Seek to the beginning of partitions"""
        with self._lock:
            target_partitions = partitions or list(self.assignment.keys())
            
            for tp in target_partitions:
                if tp in self.assignment:
                    self.assignment[tp] = 0
                    print(f"⏮️  Seeking {tp.topic}[{tp.partition}] to beginning")
    
    def seek_to_end(self, partitions: Optional[List[TopicPartition]] = None) -> None:
        """Seek to the end of partitions"""
        with self._lock:
            target_partitions = partitions or list(self.assignment.keys())
            
            for tp in target_partitions:
                if tp in self.assignment and self.broker:
                    metadata = self.broker.get_topic_metadata(tp.topic)
                    if metadata:
                        for partition_info in metadata['partitions']:
                            if partition_info['partition'] == tp.partition:
                                self.assignment[tp] = partition_info['log_end_offset']
                                print(f"⏭️  Seeking {tp.topic}[{tp.partition}] to end")
                                break
    
    def position(self, partition: TopicPartition) -> int:
        """Get current position for partition"""
        with self._lock:
            return self.assignment.get(partition, -1)
    
    def committed(self, partition: TopicPartition) -> Optional[OffsetAndMetadata]:
        """Get committed offset for partition"""
        with self._lock:
            if self.config.group_id and self.broker:
                offset = self.broker.get_committed_offset(
                    self.config.group_id, partition.topic, partition.partition
                )
                if offset is not None:
                    return OffsetAndMetadata(offset)
            
            return self.committed_offsets.get(partition)
    
    def assignment(self) -> Set[TopicPartition]:
        """Get current partition assignment"""
        with self._lock:
            return set(self.assignment.keys())
    
    def subscription(self) -> Set[str]:
        """Get current topic subscription"""
        return self.topics.copy()
    
    def pause(self, partitions: List[TopicPartition]) -> None:
        """Pause consumption from partitions"""
        # Implementation would mark partitions as paused
        print(f"⏸️  Paused partitions: {[f'{tp.topic}[{tp.partition}]' for tp in partitions]}")
    
    def resume(self, partitions: List[TopicPartition]) -> None:
        """Resume consumption from partitions"""
        # Implementation would unmark partitions as paused
        print(f"▶️  Resumed partitions: {[f'{tp.topic}[{tp.partition}]' for tp in partitions]}")
    
    def close(self, timeout: Optional[float] = None) -> None:
        """Close the consumer"""
        print("🔌 Closing Kafka Consumer...")
        
        # Leave consumer group
        if self.config.group_id and self.broker:
            self.broker.leave_consumer_group(self.config.group_id, self.consumer_id)
        
        # Stop background threads
        self._stop_event.set()
        
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=1.0)
        
        if self._auto_commit_thread and self._auto_commit_thread.is_alive():
            self._auto_commit_thread.join(timeout=1.0)
        
        print("🔌 Kafka Consumer closed")
    
    def get_metrics(self) -> Dict:
        """Get consumer metrics"""
        with self._lock:
            return {
                'records_consumed': self.stats['records_consumed'],
                'bytes_consumed': self.stats['bytes_consumed'],
                'commits': self.stats['commits'],
                'rebalances': self.stats['rebalances'],
                'assigned_partitions': len(self.assignment),
                'subscribed_topics': len(self.topics),
                'uptime': time.time() - self.stats['start_time']
            }
    
    def _initialize_consumer(self):
        """Initialize consumer and start background threads"""
        if self.config.enable_auto_commit:
            self._auto_commit_thread = threading.Thread(target=self._auto_commit_loop, daemon=True)
            self._auto_commit_thread.start()
        
        if self.config.group_id:
            self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self._heartbeat_thread.start()
    
    def _update_assignment(self, assignment: Dict[str, List[int]]) -> None:
        """Update partition assignment from group coordinator"""
        old_assignment = set(self.assignment.keys())
        new_assignment = set()
        
        self.assignment.clear()
        
        for topic, partitions in assignment.items():
            for partition in partitions:
                tp = TopicPartition(topic, partition)
                new_assignment.add(tp)
                
                # Get starting offset
                committed = self.committed(tp)
                if committed:
                    self.assignment[tp] = committed.offset
                elif self.config.auto_offset_reset == AutoOffsetReset.EARLIEST:
                    self.assignment[tp] = 0
                else:
                    # Get latest offset
                    if self.broker:
                        metadata = self.broker.get_topic_metadata(topic)
                        if metadata:
                            for partition_info in metadata['partitions']:
                                if partition_info['partition'] == partition:
                                    self.assignment[tp] = partition_info['log_end_offset']
                                    break
                            else:
                                self.assignment[tp] = 0
                        else:
                            self.assignment[tp] = 0
                    else:
                        self.assignment[tp] = 0
        
        # Call rebalance listener
        if self.rebalance_listener:
            revoked = old_assignment - new_assignment
            assigned = new_assignment - old_assignment
            
            if revoked:
                self.rebalance_listener.on_partitions_revoked(list(revoked))
            if assigned:
                self.rebalance_listener.on_partitions_assigned(list(assigned))
        
        self.stats['rebalances'] += 1
        print(f"🔄 Partition assignment updated: {len(new_assignment)} partitions")
    
    def _rejoin_group(self):
        """Rejoin consumer group after timeout"""
        if self.config.group_id and self.broker:
            assignment = self.broker.join_consumer_group(
                self.config.group_id, self.consumer_id, list(self.topics)
            )
            self._update_assignment(assignment)
    
    def _auto_commit_loop(self):
        """Background thread for automatic offset commits"""
        while not self._stop_event.is_set():
            try:
                if self.assignment:
                    self.commit_sync()
                
                self._stop_event.wait(self.config.auto_commit_interval_ms / 1000.0)
            except Exception as e:
                print(f"❌ Auto-commit error: {e}")
    
    def _heartbeat_loop(self):
        """Background thread for sending heartbeats"""
        while not self._stop_event.is_set():
            try:
                # Send heartbeat to group coordinator (simplified)
                self._stop_event.wait(self.config.heartbeat_interval_ms / 1000.0)
            except Exception as e:
                print(f"❌ Heartbeat error: {e}")

class ConsumerRebalanceListener:
    """Callback interface for partition rebalance events"""
    
    def on_partitions_revoked(self, partitions: List[TopicPartition]) -> None:
        """Called when partitions are revoked from consumer"""
        print(f"🔄 Partitions revoked: {[f'{tp.topic}[{tp.partition}]' for tp in partitions]}")
    
    def on_partitions_assigned(self, partitions: List[TopicPartition]) -> None:
        """Called when partitions are assigned to consumer"""
        print(f"🔄 Partitions assigned: {[f'{tp.topic}[{tp.partition}]' for tp in partitions]}")

def demonstrate_kafka_consumer():
    """Demonstrate Kafka consumer functionality"""
    print("=== Kafka Consumer Demonstration ===")
    
    # Start broker and create topics
    broker = KafkaBroker(broker_id=1)
    broker.start()
    
    try:
        # Create topics with data
        broker.create_topic("orders", partitions=3)
        broker.create_topic("metrics", partitions=2)
        
        # Produce some test data
        print(f"\n📤 Producing test data...")
        
        orders = [
            ("user123", '{"order_id": "ORD-001", "user_id": "user123", "amount": 99.99}'),
            ("user456", '{"order_id": "ORD-002", "user_id": "user456", "amount": 149.50}'),
            ("user123", '{"order_id": "ORD-003", "user_id": "user123", "amount": 79.99}'),
            ("user789", '{"order_id": "ORD-004", "user_id": "user789", "amount": 199.99}'),
            ("user456", '{"order_id": "ORD-005", "user_id": "user456", "amount": 299.99}')
        ]
        
        for key, value in orders:
            broker.produce_message("orders", key, value)
        
        metrics = [
            ("host1", '{"metric": "cpu_usage", "value": 75.5, "timestamp": 1234567890}'),
            ("host2", '{"metric": "memory_usage", "value": 82.3, "timestamp": 1234567891}'),
            ("host1", '{"metric": "disk_usage", "value": 45.1, "timestamp": 1234567892}')
        ]
        
        for key, value in metrics:
            broker.produce_message("metrics", key, value)
        
        # Create consumer group
        print(f"\n👥 Creating consumer group...")
        
        config = ConsumerConfig(
            group_id="order-processing-group",
            client_id="order-processor",
            auto_offset_reset=AutoOffsetReset.EARLIEST,
            enable_auto_commit=False,  # Manual commit for demo
            max_poll_records=10
        )
        
        # Create rebalance listener
        class OrderRebalanceListener(ConsumerRebalanceListener):
            def on_partitions_revoked(self, partitions):
                print(f"🔄 Order processor: partitions revoked {len(partitions)}")
            
            def on_partitions_assigned(self, partitions):
                print(f"🔄 Order processor: partitions assigned {len(partitions)}")
        
        consumer = KafkaConsumer(["orders"], config, broker)
        consumer.subscribe(["orders"], OrderRebalanceListener())
        
        # Poll for messages
        print(f"\n📥 Consuming messages...")
        
        total_consumed = 0
        for poll_round in range(3):
            records = consumer.poll(timeout_ms=1000)
            
            for tp, record_list in records.items():
                for record in record_list:
                    order_data = json.loads(record.value)
                    print(f"   Processed order: {order_data['order_id']} "
                         f"from {tp.topic}[{tp.partition}] at offset {record.offset}")
                    total_consumed += 1
            
            # Commit after processing
            if records:
                consumer.commit_sync()
        
        # Demonstrate manual assignment
        print(f"\n📍 Demonstrating manual assignment...")
        
        manual_config = ConsumerConfig(
            client_id="metrics-processor",
            auto_offset_reset=AutoOffsetReset.EARLIEST
        )
        
        manual_consumer = KafkaConsumer([], manual_config, broker)
        
        # Manually assign partitions
        partitions = [
            TopicPartition("metrics", 0),
            TopicPartition("metrics", 1)
        ]
        manual_consumer.assign(partitions)
        
        # Consume from assigned partitions
        records = manual_consumer.poll(timeout_ms=1000)
        
        for tp, record_list in records.items():
            for record in record_list:
                metric_data = json.loads(record.value)
                print(f"   Processed metric: {metric_data['metric']} = {metric_data['value']} "
                     f"from {tp.topic}[{tp.partition}] at offset {record.offset}")
        
        # Demonstrate seeking
        print(f"\n🎯 Demonstrating seeking...")
        
        # Seek to beginning
        manual_consumer.seek_to_beginning()
        
        # Poll again
        records = manual_consumer.poll(timeout_ms=500)
        print(f"   After seeking to beginning: {sum(len(r) for r in records.values())} records")
        
        # Seek to end
        manual_consumer.seek_to_end()
        
        # Poll again (should be empty)
        records = manual_consumer.poll(timeout_ms=500)
        print(f"   After seeking to end: {sum(len(r) for r in records.values())} records")
        
        # Display metrics
        print(f"\n📊 Consumer Metrics:")
        metrics = consumer.get_metrics()
        print(f"   Records consumed: {metrics['records_consumed']}")
        print(f"   Bytes consumed: {metrics['bytes_consumed']}")
        print(f"   Commits: {metrics['commits']}")
        print(f"   Rebalances: {metrics['rebalances']}")
        print(f"   Assigned partitions: {metrics['assigned_partitions']}")
        
        # Close consumers
        consumer.close()
        manual_consumer.close()
    
    finally:
        broker.stop()
    
    print("\n🎯 Kafka Consumer demonstrates:")
    print("💡 Consumer group coordination and rebalancing")
    print("💡 Automatic and manual partition assignment")
    print("💡 Offset management and seeking capabilities")
    print("💡 Configurable consumption patterns")
    print("💡 High-throughput message processing")

if __name__ == "__main__":
    demonstrate_kafka_consumer()
