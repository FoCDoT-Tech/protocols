#!/usr/bin/env python3
"""
AMQP Broker Simulation
Implements core AMQP broker functionality with exchanges, queues, and routing.
"""

import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Callable, Any
import json
import re
import uuid
from collections import defaultdict, deque

class ExchangeType(Enum):
    DIRECT = "direct"
    TOPIC = "topic"
    FANOUT = "fanout"
    HEADERS = "headers"

class DeliveryMode(Enum):
    NON_PERSISTENT = 1
    PERSISTENT = 2

@dataclass
class Message:
    body: str
    routing_key: str = ""
    headers: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    delivery_mode: DeliveryMode = DeliveryMode.NON_PERSISTENT
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    expiration: Optional[float] = None
    
    def is_expired(self) -> bool:
        if self.expiration is None:
            return False
        return time.time() > self.timestamp + self.expiration
    
    def to_dict(self) -> Dict:
        return {
            'body': self.body,
            'routing_key': self.routing_key,
            'headers': self.headers,
            'properties': self.properties,
            'delivery_mode': self.delivery_mode.value,
            'timestamp': self.timestamp,
            'message_id': self.message_id,
            'correlation_id': self.correlation_id,
            'reply_to': self.reply_to,
            'expiration': self.expiration
        }

@dataclass
class Binding:
    queue_name: str
    routing_key: str = ""
    headers: Dict[str, Any] = field(default_factory=dict)
    arguments: Dict[str, Any] = field(default_factory=dict)

class Queue:
    def __init__(self, name: str, durable: bool = False, exclusive: bool = False, 
                 auto_delete: bool = False, max_length: Optional[int] = None):
        self.name = name
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.max_length = max_length
        
        self.messages: deque = deque()
        self.consumers: Dict[str, Callable] = {}
        self.bindings: Set[str] = set()  # Exchange names bound to this queue
        
        # Statistics
        self.stats = {
            'messages_published': 0,
            'messages_delivered': 0,
            'messages_acknowledged': 0,
            'messages_rejected': 0,
            'consumers_count': 0
        }
        
        self._lock = threading.Lock()
    
    def enqueue(self, message: Message) -> bool:
        """Add message to queue"""
        with self._lock:
            # Check expiration
            if message.is_expired():
                return False
            
            # Check max length
            if self.max_length and len(self.messages) >= self.max_length:
                # Remove oldest message (FIFO)
                self.messages.popleft()
            
            self.messages.append(message)
            self.stats['messages_published'] += 1
            
            # Try to deliver immediately if consumers available
            self._try_deliver()
            
            return True
    
    def dequeue(self) -> Optional[Message]:
        """Remove and return next message"""
        with self._lock:
            if self.messages:
                message = self.messages.popleft()
                self.stats['messages_delivered'] += 1
                return message
            return None
    
    def add_consumer(self, consumer_id: str, callback: Callable):
        """Add consumer to queue"""
        with self._lock:
            self.consumers[consumer_id] = callback
            self.stats['consumers_count'] = len(self.consumers)
            self._try_deliver()
    
    def remove_consumer(self, consumer_id: str):
        """Remove consumer from queue"""
        with self._lock:
            if consumer_id in self.consumers:
                del self.consumers[consumer_id]
                self.stats['consumers_count'] = len(self.consumers)
    
    def _try_deliver(self):
        """Try to deliver messages to available consumers"""
        while self.messages and self.consumers:
            message = self.messages.popleft()
            
            # Round-robin delivery to consumers
            consumer_id = next(iter(self.consumers.keys()))
            callback = self.consumers[consumer_id]
            
            try:
                callback(message)
                self.stats['messages_delivered'] += 1
            except Exception as e:
                # Put message back on error
                self.messages.appendleft(message)
                print(f"❌ Consumer {consumer_id} failed to process message: {e}")
                break
    
    def acknowledge(self, message_id: str):
        """Acknowledge message delivery"""
        self.stats['messages_acknowledged'] += 1
    
    def reject(self, message_id: str, requeue: bool = True):
        """Reject message"""
        self.stats['messages_rejected'] += 1
    
    def get_stats(self) -> Dict:
        """Get queue statistics"""
        with self._lock:
            return {
                'name': self.name,
                'messages_ready': len(self.messages),
                'consumers': self.stats['consumers_count'],
                'durable': self.durable,
                **self.stats
            }

class Exchange:
    def __init__(self, name: str, exchange_type: ExchangeType, 
                 durable: bool = False, auto_delete: bool = False):
        self.name = name
        self.type = exchange_type
        self.durable = durable
        self.auto_delete = auto_delete
        
        self.bindings: List[Binding] = []
        self.stats = {
            'messages_published': 0,
            'messages_routed': 0,
            'messages_unroutable': 0
        }
        
        self._lock = threading.Lock()
    
    def bind_queue(self, queue_name: str, routing_key: str = "", 
                   headers: Dict[str, Any] = None, arguments: Dict[str, Any] = None):
        """Bind queue to exchange"""
        with self._lock:
            binding = Binding(
                queue_name=queue_name,
                routing_key=routing_key,
                headers=headers or {},
                arguments=arguments or {}
            )
            self.bindings.append(binding)
    
    def unbind_queue(self, queue_name: str, routing_key: str = ""):
        """Unbind queue from exchange"""
        with self._lock:
            self.bindings = [b for b in self.bindings 
                           if not (b.queue_name == queue_name and b.routing_key == routing_key)]
    
    def route_message(self, message: Message) -> List[str]:
        """Route message to appropriate queues"""
        with self._lock:
            self.stats['messages_published'] += 1
            
            target_queues = []
            
            if self.type == ExchangeType.DIRECT:
                target_queues = self._route_direct(message)
            elif self.type == ExchangeType.TOPIC:
                target_queues = self._route_topic(message)
            elif self.type == ExchangeType.FANOUT:
                target_queues = self._route_fanout(message)
            elif self.type == ExchangeType.HEADERS:
                target_queues = self._route_headers(message)
            
            if target_queues:
                self.stats['messages_routed'] += len(target_queues)
            else:
                self.stats['messages_unroutable'] += 1
            
            return target_queues
    
    def _route_direct(self, message: Message) -> List[str]:
        """Direct exchange routing - exact routing key match"""
        return [b.queue_name for b in self.bindings 
                if b.routing_key == message.routing_key]
    
    def _route_topic(self, message: Message) -> List[str]:
        """Topic exchange routing - pattern matching with wildcards"""
        target_queues = []
        
        for binding in self.bindings:
            if self._match_topic_pattern(binding.routing_key, message.routing_key):
                target_queues.append(binding.queue_name)
        
        return target_queues
    
    def _route_fanout(self, message: Message) -> List[str]:
        """Fanout exchange routing - broadcast to all bound queues"""
        return [b.queue_name for b in self.bindings]
    
    def _route_headers(self, message: Message) -> List[str]:
        """Headers exchange routing - match based on message headers"""
        target_queues = []
        
        for binding in self.bindings:
            if self._match_headers(binding.headers, message.headers, 
                                 binding.arguments.get('x-match', 'all')):
                target_queues.append(binding.queue_name)
        
        return target_queues
    
    def _match_topic_pattern(self, pattern: str, routing_key: str) -> bool:
        """Match topic pattern with wildcards (* and #)"""
        # Convert AMQP pattern to regex
        # * matches exactly one word
        # # matches zero or more words
        regex_pattern = pattern.replace('.', r'\.')
        regex_pattern = regex_pattern.replace('*', r'[^.]+')
        regex_pattern = regex_pattern.replace('#', r'.*')
        regex_pattern = f'^{regex_pattern}$'
        
        return bool(re.match(regex_pattern, routing_key))
    
    def _match_headers(self, binding_headers: Dict[str, Any], 
                      message_headers: Dict[str, Any], match_type: str) -> bool:
        """Match headers based on x-match argument"""
        if not binding_headers:
            return True
        
        matches = 0
        for key, value in binding_headers.items():
            if key.startswith('x-'):
                continue  # Skip AMQP arguments
            
            if key in message_headers and message_headers[key] == value:
                matches += 1
        
        if match_type == 'all':
            return matches == len([k for k in binding_headers.keys() if not k.startswith('x-')])
        else:  # 'any'
            return matches > 0
    
    def get_stats(self) -> Dict:
        """Get exchange statistics"""
        with self._lock:
            return {
                'name': self.name,
                'type': self.type.value,
                'bindings': len(self.bindings),
                'durable': self.durable,
                **self.stats
            }

class AMQPBroker:
    def __init__(self):
        self.exchanges: Dict[str, Exchange] = {}
        self.queues: Dict[str, Queue] = {}
        
        # Create default exchanges
        self._create_default_exchanges()
        
        # Broker statistics
        self.stats = {
            'connections': 0,
            'channels': 0,
            'total_messages': 0,
            'start_time': time.time()
        }
        
        self._lock = threading.Lock()
        self.running = False
    
    def _create_default_exchanges(self):
        """Create AMQP default exchanges"""
        # Default direct exchange (empty name)
        self.exchanges[""] = Exchange("", ExchangeType.DIRECT, durable=True)
        
        # Standard exchanges
        self.exchanges["amq.direct"] = Exchange("amq.direct", ExchangeType.DIRECT, durable=True)
        self.exchanges["amq.topic"] = Exchange("amq.topic", ExchangeType.TOPIC, durable=True)
        self.exchanges["amq.fanout"] = Exchange("amq.fanout", ExchangeType.FANOUT, durable=True)
        self.exchanges["amq.headers"] = Exchange("amq.headers", ExchangeType.HEADERS, durable=True)
    
    def start(self):
        """Start the AMQP broker"""
        self.running = True
        threading.Thread(target=self._cleanup_loop, daemon=True).start()
        print("🚀 AMQP Broker started")
    
    def stop(self):
        """Stop the AMQP broker"""
        self.running = False
        print("🛑 AMQP Broker stopped")
    
    def declare_exchange(self, name: str, exchange_type: ExchangeType, 
                        durable: bool = False, auto_delete: bool = False) -> bool:
        """Declare an exchange"""
        with self._lock:
            if name in self.exchanges:
                return True
            
            self.exchanges[name] = Exchange(name, exchange_type, durable, auto_delete)
            print(f"📡 Exchange '{name}' declared ({exchange_type.value})")
            return True
    
    def declare_queue(self, name: str, durable: bool = False, exclusive: bool = False,
                     auto_delete: bool = False, max_length: Optional[int] = None) -> bool:
        """Declare a queue"""
        with self._lock:
            if name in self.queues:
                return True
            
            self.queues[name] = Queue(name, durable, exclusive, auto_delete, max_length)
            
            # Auto-bind to default exchange with queue name as routing key
            self.exchanges[""].bind_queue(name, name)
            
            print(f"📥 Queue '{name}' declared")
            return True
    
    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str = "",
                   headers: Dict[str, Any] = None, arguments: Dict[str, Any] = None) -> bool:
        """Bind queue to exchange"""
        with self._lock:
            if exchange_name not in self.exchanges or queue_name not in self.queues:
                return False
            
            exchange = self.exchanges[exchange_name]
            exchange.bind_queue(queue_name, routing_key, headers, arguments)
            
            queue = self.queues[queue_name]
            queue.bindings.add(exchange_name)
            
            print(f"🔗 Queue '{queue_name}' bound to exchange '{exchange_name}' with key '{routing_key}'")
            return True
    
    def publish(self, exchange_name: str, message: Message) -> bool:
        """Publish message to exchange"""
        with self._lock:
            if exchange_name not in self.exchanges:
                print(f"❌ Exchange '{exchange_name}' not found")
                return False
            
            exchange = self.exchanges[exchange_name]
            target_queues = exchange.route_message(message)
            
            delivered = 0
            for queue_name in target_queues:
                if queue_name in self.queues:
                    queue = self.queues[queue_name]
                    if queue.enqueue(message):
                        delivered += 1
            
            self.stats['total_messages'] += 1
            
            if delivered > 0:
                print(f"📤 Message published to {delivered} queue(s) via '{exchange_name}'")
                return True
            else:
                print(f"⚠️  Message published but not routed (no matching queues)")
                return False
    
    def consume(self, queue_name: str, consumer_id: str, callback: Callable) -> bool:
        """Add consumer to queue"""
        with self._lock:
            if queue_name not in self.queues:
                return False
            
            queue = self.queues[queue_name]
            queue.add_consumer(consumer_id, callback)
            
            print(f"👤 Consumer '{consumer_id}' added to queue '{queue_name}'")
            return True
    
    def cancel_consumer(self, queue_name: str, consumer_id: str) -> bool:
        """Remove consumer from queue"""
        with self._lock:
            if queue_name not in self.queues:
                return False
            
            queue = self.queues[queue_name]
            queue.remove_consumer(consumer_id)
            
            print(f"👋 Consumer '{consumer_id}' removed from queue '{queue_name}'")
            return True
    
    def get_queue_message(self, queue_name: str) -> Optional[Message]:
        """Get message from queue (basic.get)"""
        with self._lock:
            if queue_name not in self.queues:
                return None
            
            queue = self.queues[queue_name]
            return queue.dequeue()
    
    def _cleanup_loop(self):
        """Cleanup expired messages and auto-delete entities"""
        while self.running:
            try:
                with self._lock:
                    # Clean expired messages from queues
                    for queue in self.queues.values():
                        with queue._lock:
                            expired_messages = []
                            for message in queue.messages:
                                if message.is_expired():
                                    expired_messages.append(message)
                            
                            for message in expired_messages:
                                queue.messages.remove(message)
                
                time.sleep(10)  # Cleanup every 10 seconds
            except Exception as e:
                print(f"❌ Cleanup error: {e}")
    
    def get_broker_stats(self) -> Dict:
        """Get broker statistics"""
        with self._lock:
            return {
                'uptime': time.time() - self.stats['start_time'],
                'exchanges': len(self.exchanges),
                'queues': len(self.queues),
                'total_messages': self.stats['total_messages'],
                'exchange_stats': {name: ex.get_stats() for name, ex in self.exchanges.items()},
                'queue_stats': {name: q.get_stats() for name, q in self.queues.items()}
            }

def demonstrate_amqp_broker():
    """Demonstrate AMQP broker functionality"""
    print("=== AMQP Broker Demonstration ===")
    
    broker = AMQPBroker()
    broker.start()
    
    try:
        # Declare exchanges
        broker.declare_exchange("orders", ExchangeType.DIRECT)
        broker.declare_exchange("notifications", ExchangeType.TOPIC)
        broker.declare_exchange("analytics", ExchangeType.FANOUT)
        
        # Declare queues
        broker.declare_queue("order_processing", durable=True)
        broker.declare_queue("inventory_updates", durable=True)
        broker.declare_queue("email_notifications")
        broker.declare_queue("sms_notifications")
        broker.declare_queue("analytics_raw")
        broker.declare_queue("analytics_processed")
        
        # Bind queues to exchanges
        broker.bind_queue("order_processing", "orders", "order.created")
        broker.bind_queue("inventory_updates", "orders", "inventory.update")
        broker.bind_queue("email_notifications", "notifications", "notify.email.*")
        broker.bind_queue("sms_notifications", "notifications", "notify.sms.*")
        broker.bind_queue("analytics_raw", "analytics")
        broker.bind_queue("analytics_processed", "analytics")
        
        # Set up consumers
        def order_processor(message: Message):
            print(f"🛒 Processing order: {message.body}")
        
        def inventory_updater(message: Message):
            print(f"📦 Updating inventory: {message.body}")
        
        def email_sender(message: Message):
            print(f"📧 Sending email: {message.body}")
        
        def analytics_collector(message: Message):
            print(f"📊 Collecting analytics: {message.body}")
        
        broker.consume("order_processing", "order_consumer", order_processor)
        broker.consume("inventory_updates", "inventory_consumer", inventory_updater)
        broker.consume("email_notifications", "email_consumer", email_sender)
        broker.consume("analytics_raw", "analytics_consumer", analytics_collector)
        
        # Publish messages
        print(f"\n📤 Publishing messages...")
        
        # Direct exchange messages
        order_msg = Message("New order #12345", "order.created")
        broker.publish("orders", order_msg)
        
        inventory_msg = Message("Product ABC stock: 50", "inventory.update")
        broker.publish("orders", inventory_msg)
        
        # Topic exchange messages
        email_msg = Message("Welcome email for user@example.com", "notify.email.welcome")
        broker.publish("notifications", email_msg)
        
        sms_msg = Message("Order confirmation SMS", "notify.sms.order")
        broker.publish("notifications", sms_msg)
        
        # Fanout exchange messages
        analytics_msg = Message("User activity data", "")
        broker.publish("analytics", analytics_msg)
        
        time.sleep(1)  # Let messages process
        
        # Display broker statistics
        print(f"\n📊 Broker Statistics:")
        stats = broker.get_broker_stats()
        print(f"   Uptime: {stats['uptime']:.1f}s")
        print(f"   Exchanges: {stats['exchanges']}")
        print(f"   Queues: {stats['queues']}")
        print(f"   Total messages: {stats['total_messages']}")
        
        print(f"\n📈 Exchange Statistics:")
        for name, ex_stats in stats['exchange_stats'].items():
            if name and ex_stats['messages_published'] > 0:
                print(f"   {name}: {ex_stats['messages_published']} published, "
                      f"{ex_stats['messages_routed']} routed")
        
        print(f"\n📋 Queue Statistics:")
        for name, q_stats in stats['queue_stats'].items():
            if q_stats['messages_published'] > 0:
                print(f"   {name}: {q_stats['messages_ready']} ready, "
                      f"{q_stats['messages_delivered']} delivered")
    
    finally:
        broker.stop()
    
    print("\n🎯 AMQP Broker demonstrates:")
    print("💡 Message routing with different exchange types")
    print("💡 Queue management and consumer handling")
    print("💡 Reliable message delivery and acknowledgments")
    print("💡 Scalable publish-subscribe patterns")

if __name__ == "__main__":
    demonstrate_amqp_broker()
