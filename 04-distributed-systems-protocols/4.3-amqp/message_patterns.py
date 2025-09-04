#!/usr/bin/env python3
"""
AMQP Message Patterns
Common messaging patterns and routing examples.
"""

import time
import threading
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json
import uuid

from amqp_broker import AMQPBroker, Message, ExchangeType
from amqp_client import AMQPConnection, AMQPChannel

class MessagePattern(Enum):
    WORK_QUEUE = "work_queue"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    ROUTING = "routing"
    TOPICS = "topics"
    RPC = "rpc"
    PRIORITY_QUEUE = "priority_queue"

@dataclass
class WorkItem:
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3

class MessagePatterns:
    def __init__(self, broker: AMQPBroker):
        self.broker = broker
        self.connection = AMQPConnection()
        self.connection.connect(broker)
        self.channels: Dict[str, AMQPChannel] = {}
        
        # Pattern-specific state
        self.rpc_responses: Dict[str, str] = {}
        self.work_results: List[str] = []
        self.notification_log: List[str] = []
    
    def get_channel(self, name: str) -> AMQPChannel:
        """Get or create a named channel"""
        if name not in self.channels:
            self.channels[name] = self.connection.channel()
        return self.channels[name]
    
    def work_queue_pattern(self):
        """Demonstrate work queue pattern for task distribution"""
        print("\n🏭 Work Queue Pattern")
        print("   Purpose: Distribute time-consuming tasks among multiple workers")
        
        channel = self.get_channel("work_queue")
        
        # Declare work queue
        channel.queue_declare("task_queue", durable=True)
        
        # Create workers
        def worker(worker_id: str):
            def process_task(message: Message, delivery_info: Dict):
                work_item = json.loads(message.body)
                processing_time = work_item.get('processing_time', 1)
                
                print(f"   👷 Worker {worker_id} processing task {work_item['task_id']} "
                      f"(estimated {processing_time}s)")
                
                # Simulate work
                time.sleep(processing_time)
                
                result = f"Task {work_item['task_id']} completed by worker {worker_id}"
                self.work_results.append(result)
                
                # Acknowledge task completion
                channel.basic_ack(delivery_info['delivery_tag'])
                print(f"   ✅ {result}")
            
            # Set QoS to process one task at a time
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume("task_queue", process_task)
        
        # Start workers
        for i in range(3):
            threading.Thread(target=worker, args=[f"W{i+1}"], daemon=True).start()
        
        # Send tasks
        tasks = [
            {"task_id": "T1", "task_type": "image_resize", "processing_time": 0.5},
            {"task_id": "T2", "task_type": "email_send", "processing_time": 0.3},
            {"task_id": "T3", "task_type": "report_generate", "processing_time": 0.8},
            {"task_id": "T4", "task_type": "backup_create", "processing_time": 0.4},
            {"task_id": "T5", "task_type": "data_sync", "processing_time": 0.6}
        ]
        
        for task in tasks:
            channel.basic_publish("", "task_queue", json.dumps(task),
                                properties={'delivery_mode': 2})  # Persistent
        
        time.sleep(2)  # Let workers process tasks
    
    def publish_subscribe_pattern(self):
        """Demonstrate publish-subscribe pattern for broadcasting"""
        print("\n📡 Publish-Subscribe Pattern")
        print("   Purpose: Broadcast messages to multiple subscribers")
        
        channel = self.get_channel("pubsub")
        
        # Declare fanout exchange
        channel.exchange_declare("news", "fanout")
        
        # Create subscribers
        subscribers = ["mobile_app", "web_app", "email_service"]
        
        for subscriber in subscribers:
            # Each subscriber gets its own temporary queue
            result = channel.queue_declare("", exclusive=True, auto_delete=True)
            queue_name = result['queue']
            
            # Bind to news exchange
            channel.queue_bind(queue_name, "news")
            
            def make_subscriber_handler(sub_name):
                def handle_news(message: Message, delivery_info: Dict):
                    news_item = json.loads(message.body)
                    log_entry = f"{sub_name} received: {news_item['headline']}"
                    self.notification_log.append(log_entry)
                    print(f"   📰 {log_entry}")
                    channel.basic_ack(delivery_info['delivery_tag'])
                return handle_news
            
            channel.basic_consume(queue_name, make_subscriber_handler(subscriber))
        
        # Publish news items
        news_items = [
            {"headline": "Breaking: New Product Launch", "category": "business"},
            {"headline": "Weather Alert: Storm Warning", "category": "weather"},
            {"headline": "Sports: Championship Finals Tonight", "category": "sports"}
        ]
        
        for news in news_items:
            channel.basic_publish("news", "", json.dumps(news))
        
        time.sleep(1)  # Let subscribers process
    
    def routing_pattern(self):
        """Demonstrate routing pattern with direct exchange"""
        print("\n🎯 Routing Pattern")
        print("   Purpose: Route messages based on severity/type")
        
        channel = self.get_channel("routing")
        
        # Declare direct exchange
        channel.exchange_declare("logs", "direct")
        
        # Create log handlers for different severities
        severities = ["info", "warning", "error"]
        
        for severity in severities:
            queue_name = f"logs_{severity}"
            channel.queue_declare(queue_name)
            channel.queue_bind(queue_name, "logs", severity)
            
            def make_log_handler(sev):
                def handle_log(message: Message, delivery_info: Dict):
                    log_entry = json.loads(message.body)
                    print(f"   📝 [{sev.upper()}] {log_entry['message']} "
                          f"from {log_entry['service']}")
                    channel.basic_ack(delivery_info['delivery_tag'])
                return handle_log
            
            channel.basic_consume(queue_name, make_log_handler(severity))
        
        # Send log messages
        log_messages = [
            {"service": "auth", "message": "User login successful", "severity": "info"},
            {"service": "payment", "message": "Payment processing slow", "severity": "warning"},
            {"service": "database", "message": "Connection timeout", "severity": "error"},
            {"service": "api", "message": "Request processed", "severity": "info"}
        ]
        
        for log in log_messages:
            channel.basic_publish("logs", log['severity'], json.dumps(log))
        
        time.sleep(1)  # Let handlers process
    
    def topics_pattern(self):
        """Demonstrate topic pattern with wildcard routing"""
        print("\n🏷️  Topics Pattern")
        print("   Purpose: Route messages based on topic patterns")
        
        channel = self.get_channel("topics")
        
        # Declare topic exchange
        channel.exchange_declare("events", "topic")
        
        # Create topic subscribers
        topic_bindings = [
            ("user_events", "user.*"),           # All user events
            ("order_events", "order.*"),         # All order events
            ("critical_events", "*.critical"),   # All critical events
            ("all_events", "#")                  # All events
        ]
        
        for queue_name, routing_pattern in topic_bindings:
            channel.queue_declare(queue_name)
            channel.queue_bind(queue_name, "events", routing_pattern)
            
            def make_topic_handler(queue, pattern):
                def handle_event(message: Message, delivery_info: Dict):
                    event = json.loads(message.body)
                    print(f"   🎫 {queue} ({pattern}): {event['type']} - {event['description']}")
                    channel.basic_ack(delivery_info['delivery_tag'])
                return handle_event
            
            channel.basic_consume(queue_name, make_topic_handler(queue_name, routing_pattern))
        
        # Send topic messages
        events = [
            {"type": "user.created", "description": "New user registered"},
            {"type": "user.critical", "description": "User account compromised"},
            {"type": "order.placed", "description": "New order received"},
            {"type": "order.critical", "description": "Payment failed multiple times"},
            {"type": "system.info", "description": "System maintenance scheduled"}
        ]
        
        for event in events:
            channel.basic_publish("events", event['type'], json.dumps(event))
        
        time.sleep(1)  # Let handlers process
    
    def rpc_pattern(self):
        """Demonstrate RPC pattern with request-response"""
        print("\n🔄 RPC Pattern")
        print("   Purpose: Remote procedure calls with request-response")
        
        channel = self.get_channel("rpc")
        
        # Declare RPC queue
        channel.queue_declare("rpc_queue")
        
        # Create RPC server
        def rpc_server():
            def handle_rpc_request(message: Message, delivery_info: Dict):
                request = json.loads(message.body)
                
                # Process RPC call
                if request['method'] == 'fibonacci':
                    n = request['params']['n']
                    result = self._fibonacci(n)
                elif request['method'] == 'factorial':
                    n = request['params']['n']
                    result = self._factorial(n)
                else:
                    result = {"error": "Unknown method"}
                
                # Send response
                response = {"id": request['id'], "result": result}
                
                if message.reply_to:
                    channel.basic_publish("", message.reply_to, json.dumps(response),
                                        properties={'correlation_id': message.correlation_id})
                
                channel.basic_ack(delivery_info['delivery_tag'])
                print(f"   🔧 RPC Server: {request['method']}({request['params']}) = {result}")
            
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume("rpc_queue", handle_rpc_request)
        
        # Start RPC server
        threading.Thread(target=rpc_server, daemon=True).start()
        
        # Create response queue for client
        result = channel.queue_declare("", exclusive=True, auto_delete=True)
        response_queue = result['queue']
        
        # Set up response handler
        def handle_rpc_response(message: Message, delivery_info: Dict):
            response = json.loads(message.body)
            correlation_id = message.correlation_id
            if correlation_id:
                self.rpc_responses[correlation_id] = response
            channel.basic_ack(delivery_info['delivery_tag'])
        
        channel.basic_consume(response_queue, handle_rpc_response)
        
        # Make RPC calls
        rpc_calls = [
            {"method": "fibonacci", "params": {"n": 10}},
            {"method": "factorial", "params": {"n": 5}},
            {"method": "fibonacci", "params": {"n": 15}}
        ]
        
        for rpc_call in rpc_calls:
            correlation_id = str(uuid.uuid4())
            rpc_call['id'] = correlation_id
            
            channel.basic_publish("", "rpc_queue", json.dumps(rpc_call),
                                properties={
                                    'reply_to': response_queue,
                                    'correlation_id': correlation_id
                                })
        
        # Wait for responses
        time.sleep(1)
        
        # Display RPC results
        for call_id, response in self.rpc_responses.items():
            print(f"   📞 RPC Response {call_id[:8]}: {response['result']}")
    
    def _fibonacci(self, n: int) -> int:
        """Calculate Fibonacci number"""
        if n <= 1:
            return n
        return self._fibonacci(n-1) + self._fibonacci(n-2)
    
    def _factorial(self, n: int) -> int:
        """Calculate factorial"""
        if n <= 1:
            return 1
        return n * self._factorial(n-1)
    
    def priority_queue_pattern(self):
        """Demonstrate priority queue pattern"""
        print("\n⭐ Priority Queue Pattern")
        print("   Purpose: Process high-priority messages first")
        
        channel = self.get_channel("priority")
        
        # Declare priority queue with x-max-priority argument
        channel.queue_declare("priority_queue", arguments={'x-max-priority': 10})
        
        # Create priority worker
        def priority_worker():
            def process_priority_message(message: Message, delivery_info: Dict):
                task = json.loads(message.body)
                priority = message.properties.get('priority', 0)
                
                print(f"   🎯 Processing priority {priority} task: {task['description']}")
                time.sleep(0.2)  # Simulate processing
                
                channel.basic_ack(delivery_info['delivery_tag'])
            
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume("priority_queue", process_priority_message)
        
        # Start priority worker
        threading.Thread(target=priority_worker, daemon=True).start()
        
        # Send messages with different priorities
        priority_tasks = [
            ({"description": "Regular backup task"}, 1),
            ({"description": "CRITICAL: Security alert"}, 10),
            ({"description": "Send newsletter"}, 2),
            ({"description": "URGENT: System failure"}, 9),
            ({"description": "Update user profile"}, 3),
            ({"description": "HIGH: Payment processing"}, 7)
        ]
        
        # Send in random order to demonstrate priority sorting
        for task, priority in priority_tasks:
            channel.basic_publish("", "priority_queue", json.dumps(task),
                                properties={'priority': priority})
        
        time.sleep(2)  # Let worker process all tasks
    
    def cleanup(self):
        """Clean up channels and connection"""
        for channel in self.channels.values():
            channel.close()
        self.connection.close()

def demonstrate_message_patterns():
    """Demonstrate various AMQP messaging patterns"""
    print("=== AMQP Message Patterns Demonstration ===")
    
    # Create and start broker
    broker = AMQPBroker()
    broker.start()
    
    try:
        patterns = MessagePatterns(broker)
        
        # Demonstrate each pattern
        patterns.work_queue_pattern()
        patterns.publish_subscribe_pattern()
        patterns.routing_pattern()
        patterns.topics_pattern()
        patterns.rpc_pattern()
        patterns.priority_queue_pattern()
        
        # Summary
        print(f"\n📊 Pattern Results Summary:")
        print(f"   Work Queue: {len(patterns.work_results)} tasks completed")
        print(f"   Pub-Sub: {len(patterns.notification_log)} notifications sent")
        print(f"   RPC: {len(patterns.rpc_responses)} calls completed")
        
        patterns.cleanup()
    
    finally:
        broker.stop()
    
    print("\n🎯 AMQP Patterns demonstrate:")
    print("💡 Work Queue: Task distribution among workers")
    print("💡 Pub-Sub: Broadcasting to multiple subscribers")
    print("💡 Routing: Message routing by type/severity")
    print("💡 Topics: Pattern-based routing with wildcards")
    print("💡 RPC: Request-response communication")
    print("💡 Priority Queue: Processing by message priority")

if __name__ == "__main__":
    demonstrate_message_patterns()
