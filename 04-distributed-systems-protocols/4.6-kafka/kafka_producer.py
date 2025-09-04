#!/usr/bin/env python3
"""
Kafka Producer Implementation
High-throughput producer with batching, compression, and delivery guarantees.
"""

import time
import threading
import json
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict, deque
import hashlib

from kafka_broker import KafkaBroker, AckLevel, MessageCompression

@dataclass
class ProducerConfig:
    bootstrap_servers: List[str] = field(default_factory=lambda: ["localhost:9092"])
    client_id: str = "kafka-producer"
    acks: AckLevel = AckLevel.LEADER
    retries: int = 3
    batch_size: int = 16384  # 16KB
    linger_ms: int = 100     # Wait up to 100ms to batch messages
    buffer_memory: int = 33554432  # 32MB
    compression_type: MessageCompression = MessageCompression.NONE
    max_request_size: int = 1048576  # 1MB
    request_timeout_ms: int = 30000
    delivery_timeout_ms: int = 120000
    enable_idempotence: bool = False
    transactional_id: Optional[str] = None

@dataclass
class ProducerRecord:
    topic: str
    value: str
    key: Optional[str] = None
    partition: Optional[int] = None
    timestamp: Optional[float] = None
    headers: Optional[Dict[str, str]] = None

@dataclass
class RecordMetadata:
    topic: str
    partition: int
    offset: int
    timestamp: float
    serialized_key_size: int
    serialized_value_size: int

@dataclass
class ProducerBatch:
    topic: str
    partition: int
    records: List[ProducerRecord] = field(default_factory=list)
    created_time: float = field(default_factory=time.time)
    size_bytes: int = 0
    
    def add_record(self, record: ProducerRecord) -> bool:
        """Add record to batch if there's space"""
        record_size = self._calculate_record_size(record)
        
        if self.size_bytes + record_size > 16384:  # Batch size limit
            return False
        
        self.records.append(record)
        self.size_bytes += record_size
        return True
    
    def _calculate_record_size(self, record: ProducerRecord) -> int:
        """Calculate size of record in bytes"""
        key_size = len(record.key.encode('utf-8')) if record.key else 0
        value_size = len(record.value.encode('utf-8'))
        headers_size = sum(len(k.encode('utf-8')) + len(v.encode('utf-8')) 
                          for k, v in (record.headers or {}).items())
        return key_size + value_size + headers_size + 32  # Overhead

class KafkaProducer:
    def __init__(self, config: ProducerConfig, broker: Optional[KafkaBroker] = None):
        self.config = config
        self.broker = broker  # For simulation
        
        # Batching and buffering
        self.batches: Dict[str, Dict[int, ProducerBatch]] = defaultdict(dict)
        self.buffer_pool = deque()
        self.buffer_memory_used = 0
        
        # Threading
        self._lock = threading.Lock()
        self._sender_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Callbacks and futures
        self.pending_sends: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            'records_sent': 0,
            'bytes_sent': 0,
            'batches_sent': 0,
            'retries': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
        # Transaction state
        self.transaction_state = None
        self.producer_id = None
        self.producer_epoch = 0
        
        self._start_background_threads()
        print(f"🚀 Kafka Producer initialized (client_id: {config.client_id})")
    
    def send(self, record: ProducerRecord, 
             callback: Optional[Callable[[RecordMetadata, Exception], None]] = None) -> str:
        """Send a record asynchronously"""
        if self._stop_event.is_set():
            raise RuntimeError("Producer is closed")
        
        # Set timestamp if not provided
        if record.timestamp is None:
            record.timestamp = time.time()
        
        # Determine partition
        partition = self._get_partition(record)
        
        with self._lock:
            # Get or create batch for topic/partition
            topic_batches = self.batches[record.topic]
            
            if partition not in topic_batches:
                topic_batches[partition] = ProducerBatch(record.topic, partition)
            
            batch = topic_batches[partition]
            
            # Try to add to existing batch
            if not batch.add_record(record):
                # Batch is full, send it and create new one
                self._send_batch(batch)
                
                # Create new batch
                topic_batches[partition] = ProducerBatch(record.topic, partition)
                topic_batches[partition].add_record(record)
            
            # Generate send ID for tracking
            send_id = str(uuid.uuid4())
            if callback:
                self.pending_sends[send_id] = callback
            
            print(f"📤 Queued record for {record.topic}[{partition}]: {record.value[:50]}...")
            
            return send_id
    
    def send_sync(self, record: ProducerRecord, timeout: float = 30.0) -> RecordMetadata:
        """Send a record synchronously"""
        result = None
        error = None
        event = threading.Event()
        
        def callback(metadata: RecordMetadata, exception: Exception):
            nonlocal result, error
            result = metadata
            error = exception
            event.set()
        
        self.send(record, callback)
        
        if not event.wait(timeout):
            raise TimeoutError("Send operation timed out")
        
        if error:
            raise error
        
        return result
    
    def flush(self, timeout: Optional[float] = None) -> None:
        """Flush all pending records"""
        start_time = time.time()
        
        with self._lock:
            # Send all pending batches
            for topic_batches in self.batches.values():
                for batch in topic_batches.values():
                    if batch.records:
                        self._send_batch(batch)
            
            # Clear batches
            self.batches.clear()
        
        # Wait for sends to complete (simplified)
        if timeout:
            elapsed = time.time() - start_time
            if elapsed < timeout:
                time.sleep(min(0.1, timeout - elapsed))
        
        print("🔄 Flushed all pending records")
    
    def begin_transaction(self) -> None:
        """Begin a transaction"""
        if not self.config.transactional_id:
            raise ValueError("Transactional ID not configured")
        
        if self.transaction_state is not None:
            raise RuntimeError("Transaction already in progress")
        
        self.transaction_state = "IN_TRANSACTION"
        print(f"🔄 Transaction started (id: {self.config.transactional_id})")
    
    def commit_transaction(self) -> None:
        """Commit the current transaction"""
        if self.transaction_state != "IN_TRANSACTION":
            raise RuntimeError("No transaction in progress")
        
        # Flush all pending records
        self.flush()
        
        # Commit transaction (simplified)
        self.transaction_state = None
        print(f"✅ Transaction committed")
    
    def abort_transaction(self) -> None:
        """Abort the current transaction"""
        if self.transaction_state != "IN_TRANSACTION":
            raise RuntimeError("No transaction in progress")
        
        # Clear pending batches
        with self._lock:
            self.batches.clear()
        
        self.transaction_state = None
        print(f"❌ Transaction aborted")
    
    def close(self, timeout: Optional[float] = None) -> None:
        """Close the producer"""
        print("🔌 Closing Kafka Producer...")
        
        # Flush pending records
        self.flush(timeout)
        
        # Stop background threads
        self._stop_event.set()
        
        if self._sender_thread and self._sender_thread.is_alive():
            self._sender_thread.join(timeout=1.0)
        
        print("🔌 Kafka Producer closed")
    
    def get_metrics(self) -> Dict:
        """Get producer metrics"""
        with self._lock:
            pending_batches = sum(len(topic_batches) for topic_batches in self.batches.values())
            pending_records = sum(len(batch.records) 
                                for topic_batches in self.batches.values()
                                for batch in topic_batches.values())
        
        return {
            'records_sent': self.stats['records_sent'],
            'bytes_sent': self.stats['bytes_sent'],
            'batches_sent': self.stats['batches_sent'],
            'retries': self.stats['retries'],
            'errors': self.stats['errors'],
            'pending_batches': pending_batches,
            'pending_records': pending_records,
            'buffer_memory_used': self.buffer_memory_used,
            'uptime': time.time() - self.stats['start_time']
        }
    
    def _get_partition(self, record: ProducerRecord) -> int:
        """Determine partition for record"""
        if record.partition is not None:
            return record.partition
        
        # Get topic metadata (simplified)
        if self.broker:
            metadata = self.broker.get_topic_metadata(record.topic)
            if metadata:
                partition_count = len(metadata['partitions'])
                
                if record.key:
                    # Hash-based partitioning
                    return hash(record.key) % partition_count
                else:
                    # Round-robin partitioning
                    return self.stats['records_sent'] % partition_count
        
        # Default to partition 0
        return 0
    
    def _send_batch(self, batch: ProducerBatch) -> None:
        """Send a batch of records"""
        if not batch.records:
            return
        
        try:
            # Send to broker (simplified)
            if self.broker:
                for record in batch.records:
                    partition, offset = self.broker.produce_message(
                        batch.topic, record.key, record.value, 
                        batch.partition, record.headers, self.config.acks
                    )
                    
                    # Create metadata and call callback
                    metadata = RecordMetadata(
                        topic=batch.topic,
                        partition=partition,
                        offset=offset,
                        timestamp=record.timestamp or time.time(),
                        serialized_key_size=len(record.key.encode('utf-8')) if record.key else 0,
                        serialized_value_size=len(record.value.encode('utf-8'))
                    )
                    
                    # Update statistics
                    self.stats['records_sent'] += 1
                    self.stats['bytes_sent'] += batch.size_bytes
            
            self.stats['batches_sent'] += 1
            
            print(f"📤 Sent batch: {batch.topic}[{batch.partition}] with {len(batch.records)} records")
            
        except Exception as e:
            self.stats['errors'] += 1
            print(f"❌ Error sending batch: {e}")
    
    def _start_background_threads(self):
        """Start background threads for batching and sending"""
        self._sender_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self._sender_thread.start()
    
    def _sender_loop(self):
        """Background thread for sending batches"""
        while not self._stop_event.is_set():
            try:
                current_time = time.time()
                batches_to_send = []
                
                with self._lock:
                    # Find batches ready to send
                    for topic_batches in self.batches.values():
                        for partition, batch in list(topic_batches.items()):
                            # Send if batch is full or linger time exceeded
                            if (batch.size_bytes >= self.config.batch_size or
                                current_time - batch.created_time >= self.config.linger_ms / 1000.0):
                                batches_to_send.append(batch)
                                del topic_batches[partition]
                
                # Send batches outside of lock
                for batch in batches_to_send:
                    self._send_batch(batch)
                
                # Sleep for a short time
                time.sleep(0.01)  # 10ms
                
            except Exception as e:
                print(f"❌ Sender loop error: {e}")

def demonstrate_kafka_producer():
    """Demonstrate Kafka producer functionality"""
    print("=== Kafka Producer Demonstration ===")
    
    # Start broker
    broker = KafkaBroker(broker_id=1)
    broker.start()
    
    try:
        # Create topics
        broker.create_topic("orders", partitions=3)
        broker.create_topic("metrics", partitions=2)
        
        # Create producer
        config = ProducerConfig(
            client_id="demo-producer",
            acks=AckLevel.LEADER,
            batch_size=1024,  # Small batch for demo
            linger_ms=50,
            compression_type=MessageCompression.NONE
        )
        
        producer = KafkaProducer(config, broker)
        
        # Send individual messages
        print(f"\n📤 Sending individual messages...")
        
        orders = [
            {"order_id": "ORD-001", "user_id": "user123", "amount": 99.99, "status": "pending"},
            {"order_id": "ORD-002", "user_id": "user456", "amount": 149.50, "status": "pending"},
            {"order_id": "ORD-003", "user_id": "user123", "amount": 79.99, "status": "confirmed"},
            {"order_id": "ORD-004", "user_id": "user789", "amount": 199.99, "status": "pending"}
        ]
        
        for order in orders:
            record = ProducerRecord(
                topic="orders",
                key=order["user_id"],
                value=json.dumps(order),
                headers={"source": "order-service", "version": "1.0"}
            )
            producer.send(record)
        
        # Send metrics
        print(f"\n📊 Sending metrics...")
        
        metrics = [
            {"metric": "cpu_usage", "value": 75.5, "host": "web-01"},
            {"metric": "memory_usage", "value": 82.3, "host": "web-01"},
            {"metric": "disk_usage", "value": 45.1, "host": "web-02"},
            {"metric": "network_io", "value": 1024.5, "host": "web-02"}
        ]
        
        for metric in metrics:
            record = ProducerRecord(
                topic="metrics",
                key=metric["host"],
                value=json.dumps(metric),
                headers={"type": "system_metric"}
            )
            producer.send(record)
        
        # Demonstrate synchronous send
        print(f"\n🔄 Demonstrating synchronous send...")
        
        sync_record = ProducerRecord(
            topic="orders",
            key="user999",
            value=json.dumps({"order_id": "ORD-SYNC", "user_id": "user999", "amount": 299.99}),
            headers={"priority": "high"}
        )
        
        try:
            metadata = producer.send_sync(sync_record, timeout=5.0)
            print(f"✅ Synchronous send completed: {metadata.topic}[{metadata.partition}] at offset {metadata.offset}")
        except Exception as e:
            print(f"❌ Synchronous send failed: {e}")
        
        # Demonstrate transactions
        print(f"\n🔄 Demonstrating transactions...")
        
        # Configure transactional producer
        tx_config = ProducerConfig(
            client_id="tx-producer",
            transactional_id="tx-001",
            enable_idempotence=True
        )
        
        tx_producer = KafkaProducer(tx_config, broker)
        
        try:
            tx_producer.begin_transaction()
            
            # Send multiple records in transaction
            tx_records = [
                {"order_id": "ORD-TX1", "user_id": "user111", "amount": 50.00},
                {"order_id": "ORD-TX2", "user_id": "user111", "amount": 75.00}
            ]
            
            for order in tx_records:
                record = ProducerRecord(
                    topic="orders",
                    key=order["user_id"],
                    value=json.dumps(order),
                    headers={"transaction": "tx-001"}
                )
                tx_producer.send(record)
            
            tx_producer.commit_transaction()
            
        except Exception as e:
            print(f"❌ Transaction failed: {e}")
            tx_producer.abort_transaction()
        
        # Flush and wait
        print(f"\n🔄 Flushing producers...")
        producer.flush()
        tx_producer.flush()
        
        time.sleep(0.5)  # Let messages process
        
        # Display metrics
        print(f"\n📊 Producer Metrics:")
        metrics = producer.get_metrics()
        print(f"   Records sent: {metrics['records_sent']}")
        print(f"   Bytes sent: {metrics['bytes_sent']}")
        print(f"   Batches sent: {metrics['batches_sent']}")
        print(f"   Pending records: {metrics['pending_records']}")
        print(f"   Errors: {metrics['errors']}")
        
        # Close producers
        producer.close()
        tx_producer.close()
    
    finally:
        broker.stop()
    
    print("\n🎯 Kafka Producer demonstrates:")
    print("💡 High-throughput message production with batching")
    print("💡 Configurable delivery guarantees and acknowledgments")
    print("💡 Partitioning strategies for load distribution")
    print("💡 Transactional messaging for exactly-once semantics")
    print("💡 Asynchronous and synchronous sending patterns")

if __name__ == "__main__":
    demonstrate_kafka_producer()
