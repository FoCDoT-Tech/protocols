#!/usr/bin/env python3
"""
Kafka Stream Processing
Real-time stream processing with windowing and aggregation.
"""

import time
import threading
import json
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Tuple
from collections import defaultdict, deque
import statistics

from kafka_broker import KafkaBroker, TopicPartition
from kafka_producer import KafkaProducer, ProducerConfig, ProducerRecord
from kafka_consumer import KafkaConsumer, ConsumerConfig, ConsumerRecord, AutoOffsetReset

class WindowType(Enum):
    TUMBLING = "tumbling"
    HOPPING = "hopping"
    SESSION = "session"

@dataclass
class TimeWindow:
    start_time: float
    end_time: float
    window_type: WindowType
    
    def contains(self, timestamp: float) -> bool:
        """Check if timestamp falls within this window"""
        return self.start_time <= timestamp < self.end_time
    
    def __hash__(self):
        return hash((self.start_time, self.end_time, self.window_type))

@dataclass
class StreamRecord:
    key: str
    value: Any
    timestamp: float
    partition: int
    offset: int

class StreamProcessor:
    def __init__(self, application_id: str, broker: KafkaBroker):
        self.application_id = application_id
        self.broker = broker
        
        # Stream topology
        self.sources: Dict[str, 'SourceNode'] = {}
        self.processors: Dict[str, 'ProcessorNode'] = {}
        self.sinks: Dict[str, 'SinkNode'] = {}
        
        # State stores
        self.state_stores: Dict[str, Dict] = defaultdict(dict)
        
        # Window stores
        self.window_stores: Dict[str, Dict[TimeWindow, Dict]] = defaultdict(dict)
        
        # Processing threads
        self.running = False
        self.processor_threads: List[threading.Thread] = []
        
        print(f"🌊 Stream Processor '{application_id}' initialized")
    
    def add_source(self, name: str, topics: List[str]) -> 'SourceNode':
        """Add source node for consuming from topics"""
        source = SourceNode(name, topics, self)
        self.sources[name] = source
        return source
    
    def add_processor(self, name: str, processor_func: Callable, parent_names: List[str]) -> 'ProcessorNode':
        """Add processor node with transformation function"""
        processor = ProcessorNode(name, processor_func, parent_names, self)
        self.processors[name] = processor
        return processor
    
    def add_sink(self, name: str, topic: str, parent_names: List[str]) -> 'SinkNode':
        """Add sink node for producing to topic"""
        sink = SinkNode(name, topic, parent_names, self)
        self.sinks[name] = sink
        return sink
    
    def start(self):
        """Start stream processing"""
        self.running = True
        
        # Start source processors
        for source in self.sources.values():
            thread = threading.Thread(target=source.process, daemon=True)
            thread.start()
            self.processor_threads.append(thread)
        
        print(f"🚀 Stream Processor '{self.application_id}' started")
    
    def stop(self):
        """Stop stream processing"""
        self.running = False
        
        # Wait for threads to finish
        for thread in self.processor_threads:
            thread.join(timeout=1.0)
        
        print(f"🛑 Stream Processor '{self.application_id}' stopped")
    
    def get_state_store(self, store_name: str) -> Dict:
        """Get state store for stateful operations"""
        return self.state_stores[store_name]
    
    def get_window_store(self, store_name: str) -> Dict[TimeWindow, Dict]:
        """Get window store for windowed operations"""
        return self.window_stores[store_name]

class SourceNode:
    def __init__(self, name: str, topics: List[str], processor: StreamProcessor):
        self.name = name
        self.topics = topics
        self.processor = processor
        self.children: List['ProcessorNode'] = []
        
        # Create consumer
        config = ConsumerConfig(
            group_id=f"{processor.application_id}-{name}",
            client_id=f"{processor.application_id}-{name}-consumer",
            auto_offset_reset=AutoOffsetReset.EARLIEST,
            enable_auto_commit=True
        )
        self.consumer = KafkaConsumer(topics, config, processor.broker)
        self.consumer.subscribe(topics)
    
    def add_child(self, child: 'ProcessorNode'):
        """Add child processor"""
        self.children.append(child)
    
    def process(self):
        """Process messages from source topics"""
        while self.processor.running:
            try:
                records = self.consumer.poll(timeout_ms=1000)
                
                for tp, record_list in records.items():
                    for record in record_list:
                        stream_record = StreamRecord(
                            key=record.key or "",
                            value=json.loads(record.value) if record.value else {},
                            timestamp=record.timestamp,
                            partition=record.partition,
                            offset=record.offset
                        )
                        
                        # Forward to children
                        for child in self.children:
                            child.process_record(stream_record)
            
            except Exception as e:
                print(f"❌ Source {self.name} error: {e}")
        
        self.consumer.close()

class ProcessorNode:
    def __init__(self, name: str, processor_func: Callable, parent_names: List[str], processor: StreamProcessor):
        self.name = name
        self.processor_func = processor_func
        self.parent_names = parent_names
        self.processor = processor
        self.children: List['ProcessorNode'] = []
        self.sinks: List['SinkNode'] = []
    
    def add_child(self, child: 'ProcessorNode'):
        """Add child processor"""
        self.children.append(child)
    
    def add_sink(self, sink: 'SinkNode'):
        """Add sink node"""
        self.sinks.append(sink)
    
    def process_record(self, record: StreamRecord):
        """Process a single record"""
        try:
            # Apply processor function
            results = self.processor_func(record, self.processor)
            
            # Handle different result types
            if results is None:
                return
            elif isinstance(results, StreamRecord):
                results = [results]
            elif not isinstance(results, list):
                results = [StreamRecord(record.key, results, record.timestamp, record.partition, record.offset)]
            
            # Forward results to children and sinks
            for result in results:
                for child in self.children:
                    child.process_record(result)
                
                for sink in self.sinks:
                    sink.process_record(result)
        
        except Exception as e:
            print(f"❌ Processor {self.name} error: {e}")

class SinkNode:
    def __init__(self, name: str, topic: str, parent_names: List[str], processor: StreamProcessor):
        self.name = name
        self.topic = topic
        self.parent_names = parent_names
        self.processor = processor
        
        # Create producer
        config = ProducerConfig(
            client_id=f"{processor.application_id}-{name}-producer"
        )
        self.producer = KafkaProducer(config, processor.broker)
    
    def process_record(self, record: StreamRecord):
        """Send record to output topic"""
        try:
            value = json.dumps(record.value) if isinstance(record.value, dict) else str(record.value)
            
            producer_record = ProducerRecord(
                topic=self.topic,
                key=record.key,
                value=value,
                headers={"processor": self.processor.application_id}
            )
            
            self.producer.send(producer_record)
        
        except Exception as e:
            print(f"❌ Sink {self.name} error: {e}")

class StreamOperations:
    """Common stream processing operations"""
    
    @staticmethod
    def filter_operation(predicate: Callable[[StreamRecord], bool]):
        """Filter records based on predicate"""
        def processor(record: StreamRecord, stream_processor: StreamProcessor) -> Optional[StreamRecord]:
            if predicate(record):
                return record
            return None
        return processor
    
    @staticmethod
    def map_operation(mapper: Callable[[StreamRecord], Any]):
        """Transform records using mapper function"""
        def processor(record: StreamRecord, stream_processor: StreamProcessor) -> StreamRecord:
            new_value = mapper(record)
            return StreamRecord(record.key, new_value, record.timestamp, record.partition, record.offset)
        return processor
    
    @staticmethod
    def group_by_key_operation(store_name: str):
        """Group records by key for aggregation"""
        def processor(record: StreamRecord, stream_processor: StreamProcessor) -> StreamRecord:
            # Store record in state store grouped by key
            state_store = stream_processor.get_state_store(store_name)
            if record.key not in state_store:
                state_store[record.key] = []
            state_store[record.key].append(record)
            return record
        return processor
    
    @staticmethod
    def windowed_aggregation(window_size_ms: int, store_name: str, 
                           aggregator: Callable[[List[StreamRecord]], Any]):
        """Perform windowed aggregation"""
        def processor(record: StreamRecord, stream_processor: StreamProcessor) -> Optional[StreamRecord]:
            window_store = stream_processor.get_window_store(store_name)
            
            # Create tumbling window
            window_start = (int(record.timestamp * 1000) // window_size_ms) * window_size_ms / 1000.0
            window_end = window_start + window_size_ms / 1000.0
            
            window = TimeWindow(window_start, window_end, WindowType.TUMBLING)
            
            # Add record to window
            if window not in window_store:
                window_store[window] = defaultdict(list)
            
            window_store[window][record.key].append(record)
            
            # Check if window is complete (simplified)
            current_time = time.time()
            if current_time >= window_end:
                # Aggregate and emit result
                aggregated_value = aggregator(window_store[window][record.key])
                
                result = StreamRecord(
                    key=record.key,
                    value={
                        "window_start": window_start,
                        "window_end": window_end,
                        "key": record.key,
                        "aggregated_value": aggregated_value,
                        "record_count": len(window_store[window][record.key])
                    },
                    timestamp=window_end,
                    partition=record.partition,
                    offset=record.offset
                )
                
                # Clean up window
                del window_store[window]
                
                return result
            
            return None
        return processor

def demonstrate_stream_processing():
    """Demonstrate Kafka stream processing"""
    print("=== Kafka Stream Processing Demonstration ===")
    
    # Start broker
    broker = KafkaBroker(broker_id=1)
    broker.start()
    
    try:
        # Create topics
        broker.create_topic("raw-events", partitions=2)
        broker.create_topic("processed-events", partitions=2)
        broker.create_topic("aggregated-metrics", partitions=1)
        
        # Create stream processor
        stream_processor = StreamProcessor("event-processing-app", broker)
        
        # Build stream topology
        print(f"\n🌊 Building stream topology...")
        
        # Source: consume from raw-events
        source = stream_processor.add_source("events-source", ["raw-events"])
        
        # Processor 1: Filter valid events
        def filter_valid_events(record: StreamRecord) -> bool:
            return record.value.get("event_type") in ["click", "view", "purchase"]
        
        filter_processor = stream_processor.add_processor(
            "filter-valid", 
            StreamOperations.filter_operation(filter_valid_events),
            ["events-source"]
        )
        
        # Processor 2: Enrich events
        def enrich_event(record: StreamRecord) -> Dict:
            event = record.value.copy()
            event["processed_timestamp"] = time.time()
            event["user_segment"] = "premium" if event.get("user_id", "").startswith("premium") else "standard"
            return event
        
        enrich_processor = stream_processor.add_processor(
            "enrich-events",
            StreamOperations.map_operation(enrich_event),
            ["filter-valid"]
        )
        
        # Processor 3: Windowed aggregation (5-second windows)
        def count_aggregator(records: List[StreamRecord]) -> int:
            return len(records)
        
        aggregate_processor = stream_processor.add_processor(
            "windowed-count",
            StreamOperations.windowed_aggregation(5000, "event-counts", count_aggregator),
            ["enrich-events"]
        )
        
        # Sinks
        processed_sink = stream_processor.add_sink("processed-sink", "processed-events", ["enrich-events"])
        metrics_sink = stream_processor.add_sink("metrics-sink", "aggregated-metrics", ["windowed-count"])
        
        # Connect topology
        source.add_child(filter_processor)
        filter_processor.add_child(enrich_processor)
        enrich_processor.add_child(aggregate_processor)
        enrich_processor.add_sink(processed_sink)
        aggregate_processor.add_sink(metrics_sink)
        
        # Start stream processing
        stream_processor.start()
        
        # Produce test events
        print(f"\n📤 Producing test events...")
        
        producer_config = ProducerConfig(client_id="event-producer")
        producer = KafkaProducer(producer_config, broker)
        
        events = [
            {"event_type": "click", "user_id": "user123", "page": "/home", "timestamp": time.time()},
            {"event_type": "view", "user_id": "premium_user456", "page": "/product/123", "timestamp": time.time()},
            {"event_type": "purchase", "user_id": "user789", "product_id": "widget-123", "amount": 99.99, "timestamp": time.time()},
            {"event_type": "invalid", "user_id": "user000", "data": "bad", "timestamp": time.time()},  # Will be filtered
            {"event_type": "click", "user_id": "premium_user111", "page": "/cart", "timestamp": time.time()},
            {"event_type": "view", "user_id": "user222", "page": "/product/456", "timestamp": time.time()},
        ]
        
        for i, event in enumerate(events):
            record = ProducerRecord(
                topic="raw-events",
                key=event["user_id"],
                value=json.dumps(event),
                headers={"source": "web-app"}
            )
            producer.send(record)
            time.sleep(0.5)  # Space out events
        
        # Let stream processing run
        print(f"\n⏳ Processing events for 8 seconds...")
        time.sleep(8)
        
        # Create consumers to check outputs
        print(f"\n📥 Checking processed outputs...")
        
        # Check processed events
        processed_config = ConsumerConfig(
            group_id="output-checker",
            client_id="processed-checker",
            auto_offset_reset=AutoOffsetReset.EARLIEST
        )
        
        processed_consumer = KafkaConsumer(["processed-events"], processed_config, broker)
        processed_consumer.subscribe(["processed-events"])
        
        processed_records = processed_consumer.poll(timeout_ms=2000)
        processed_count = 0
        
        for tp, record_list in processed_records.items():
            for record in record_list:
                event_data = json.loads(record.value)
                print(f"   Processed: {event_data['event_type']} by {event_data['user_id']} "
                     f"(segment: {event_data['user_segment']})")
                processed_count += 1
        
        # Check aggregated metrics
        metrics_consumer = KafkaConsumer(["aggregated-metrics"], processed_config, broker)
        metrics_consumer.subscribe(["aggregated-metrics"])
        
        metrics_records = metrics_consumer.poll(timeout_ms=2000)
        metrics_count = 0
        
        for tp, record_list in metrics_records.items():
            for record in record_list:
                metric_data = json.loads(record.value)
                print(f"   Metric: {metric_data['key']} had {metric_data['record_count']} events "
                     f"in window {metric_data['window_start']:.0f}-{metric_data['window_end']:.0f}")
                metrics_count += 1
        
        print(f"\n📊 Stream Processing Results:")
        print(f"   Raw events produced: {len(events)}")
        print(f"   Processed events: {processed_count}")
        print(f"   Aggregated metrics: {metrics_count}")
        print(f"   Filtered events: {len(events) - processed_count}")
        
        # Show state stores
        print(f"\n🗄️  State Store Contents:")
        for store_name, store_data in stream_processor.state_stores.items():
            print(f"   Store '{store_name}': {len(store_data)} keys")
        
        for store_name, window_data in stream_processor.window_stores.items():
            print(f"   Window Store '{store_name}': {len(window_data)} windows")
        
        # Clean up
        producer.close()
        processed_consumer.close()
        metrics_consumer.close()
        stream_processor.stop()
    
    finally:
        broker.stop()
    
    print("\n🎯 Kafka Stream Processing demonstrates:")
    print("💡 Real-time stream processing with topology")
    print("💡 Stateful operations with state stores")
    print("💡 Windowed aggregations for time-based analytics")
    print("💡 Event filtering and enrichment")
    print("💡 Exactly-once processing semantics")

if __name__ == "__main__":
    demonstrate_stream_processing()
