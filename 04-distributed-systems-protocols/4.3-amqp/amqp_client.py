#!/usr/bin/env python3
"""
AMQP Client Implementation
Producer and consumer client implementations for AMQP messaging.
"""

import time
import threading
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

from amqp_broker import AMQPBroker, Message, ExchangeType, DeliveryMode

class ConnectionState(Enum):
    CLOSED = "closed"
    OPENING = "opening"
    OPEN = "open"
    CLOSING = "closing"

@dataclass
class ConnectionParams:
    host: str = "localhost"
    port: int = 5672
    virtual_host: str = "/"
    username: str = "guest"
    password: str = "guest"
    heartbeat: int = 60
    frame_max: int = 131072
    channel_max: int = 65535

class AMQPChannel:
    def __init__(self, channel_id: int, connection: 'AMQPConnection'):
        self.channel_id = channel_id
        self.connection = connection
        self.broker = connection.broker
        
        self.is_open = True
        self.consumer_tags: Dict[str, str] = {}  # consumer_tag -> queue_name
        self.confirm_mode = False
        self.transaction_active = False
        
        # QoS settings
        self.prefetch_count = 0
        self.prefetch_size = 0
        
        # Statistics
        self.stats = {
            'messages_published': 0,
            'messages_consumed': 0,
            'messages_acked': 0,
            'messages_nacked': 0,
            'messages_rejected': 0
        }
    
    def exchange_declare(self, exchange: str, exchange_type: str, 
                        durable: bool = False, auto_delete: bool = False,
                        passive: bool = False) -> bool:
        """Declare an exchange"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        if passive:
            # Just check if exchange exists
            return exchange in self.broker.exchanges
        
        exchange_type_enum = ExchangeType(exchange_type)
        return self.broker.declare_exchange(exchange, exchange_type_enum, durable, auto_delete)
    
    def queue_declare(self, queue: str = "", durable: bool = False, 
                     exclusive: bool = False, auto_delete: bool = False,
                     passive: bool = False, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Declare a queue"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        # Generate queue name if empty
        if not queue:
            queue = f"amq.gen-{uuid.uuid4().hex[:8]}"
        
        if passive:
            # Just check if queue exists
            if queue in self.broker.queues:
                queue_obj = self.broker.queues[queue]
                return {
                    'queue': queue,
                    'message_count': len(queue_obj.messages),
                    'consumer_count': len(queue_obj.consumers)
                }
            else:
                raise Exception(f"Queue '{queue}' does not exist")
        
        max_length = arguments.get('x-max-length') if arguments else None
        success = self.broker.declare_queue(queue, durable, exclusive, auto_delete, max_length)
        
        if success:
            queue_obj = self.broker.queues[queue]
            return {
                'queue': queue,
                'message_count': len(queue_obj.messages),
                'consumer_count': len(queue_obj.consumers)
            }
        else:
            raise Exception(f"Failed to declare queue '{queue}'")
    
    def queue_bind(self, queue: str, exchange: str, routing_key: str = "",
                   arguments: Dict[str, Any] = None) -> bool:
        """Bind queue to exchange"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        return self.broker.bind_queue(queue, exchange, routing_key, arguments=arguments)
    
    def basic_publish(self, exchange: str, routing_key: str, body: str,
                     properties: Dict[str, Any] = None, mandatory: bool = False,
                     immediate: bool = False) -> bool:
        """Publish a message"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        properties = properties or {}
        
        message = Message(
            body=body,
            routing_key=routing_key,
            properties=properties,
            delivery_mode=DeliveryMode(properties.get('delivery_mode', 1)),
            correlation_id=properties.get('correlation_id'),
            reply_to=properties.get('reply_to'),
            expiration=properties.get('expiration')
        )
        
        success = self.broker.publish(exchange, message)
        
        if success:
            self.stats['messages_published'] += 1
        
        if mandatory and not success:
            # In real AMQP, this would trigger a basic.return
            print(f"⚠️  Mandatory message could not be routed")
        
        return success
    
    def basic_consume(self, queue: str, callback: Callable, 
                     consumer_tag: str = "", no_ack: bool = False,
                     exclusive: bool = False, arguments: Dict[str, Any] = None) -> str:
        """Start consuming messages from queue"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        if not consumer_tag:
            consumer_tag = f"ctag-{uuid.uuid4().hex[:8]}"
        
        def wrapped_callback(message: Message):
            try:
                # Create delivery info
                delivery_info = {
                    'consumer_tag': consumer_tag,
                    'delivery_tag': self.stats['messages_consumed'] + 1,
                    'redelivered': False,
                    'exchange': '',  # Would be filled by broker in real implementation
                    'routing_key': message.routing_key
                }
                
                callback(message, delivery_info)
                self.stats['messages_consumed'] += 1
                
                if no_ack:
                    self.stats['messages_acked'] += 1
                
            except Exception as e:
                print(f"❌ Consumer callback error: {e}")
        
        success = self.broker.consume(queue, consumer_tag, wrapped_callback)
        
        if success:
            self.consumer_tags[consumer_tag] = queue
        
        return consumer_tag
    
    def basic_cancel(self, consumer_tag: str) -> bool:
        """Cancel a consumer"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        if consumer_tag not in self.consumer_tags:
            return False
        
        queue = self.consumer_tags[consumer_tag]
        success = self.broker.cancel_consumer(queue, consumer_tag)
        
        if success:
            del self.consumer_tags[consumer_tag]
        
        return success
    
    def basic_get(self, queue: str, no_ack: bool = False) -> Optional[Dict]:
        """Get a single message from queue"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        message = self.broker.get_queue_message(queue)
        
        if message:
            delivery_tag = self.stats['messages_consumed'] + 1
            self.stats['messages_consumed'] += 1
            
            if no_ack:
                self.stats['messages_acked'] += 1
            
            return {
                'message': message,
                'delivery_tag': delivery_tag,
                'redelivered': False,
                'exchange': '',
                'routing_key': message.routing_key,
                'message_count': 0  # Remaining messages (would be calculated by broker)
            }
        
        return None
    
    def basic_ack(self, delivery_tag: int, multiple: bool = False) -> bool:
        """Acknowledge message delivery"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        # In real implementation, would track delivery tags and acknowledge specific messages
        self.stats['messages_acked'] += 1
        return True
    
    def basic_nack(self, delivery_tag: int, multiple: bool = False, requeue: bool = True) -> bool:
        """Negative acknowledge message"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        self.stats['messages_nacked'] += 1
        return True
    
    def basic_reject(self, delivery_tag: int, requeue: bool = True) -> bool:
        """Reject message"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        self.stats['messages_rejected'] += 1
        return True
    
    def basic_qos(self, prefetch_size: int = 0, prefetch_count: int = 0, global_qos: bool = False) -> bool:
        """Set QoS parameters"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        self.prefetch_size = prefetch_size
        self.prefetch_count = prefetch_count
        return True
    
    def confirm_select(self) -> bool:
        """Enable publisher confirms"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        self.confirm_mode = True
        return True
    
    def tx_select(self) -> bool:
        """Start transaction"""
        if not self.is_open:
            raise Exception("Channel is closed")
        
        self.transaction_active = True
        return True
    
    def tx_commit(self) -> bool:
        """Commit transaction"""
        if not self.is_open or not self.transaction_active:
            raise Exception("No active transaction")
        
        self.transaction_active = False
        return True
    
    def tx_rollback(self) -> bool:
        """Rollback transaction"""
        if not self.is_open or not self.transaction_active:
            raise Exception("No active transaction")
        
        self.transaction_active = False
        return True
    
    def close(self):
        """Close the channel"""
        # Cancel all consumers
        for consumer_tag in list(self.consumer_tags.keys()):
            self.basic_cancel(consumer_tag)
        
        self.is_open = False
        print(f"📪 Channel {self.channel_id} closed")

class AMQPConnection:
    def __init__(self, params: ConnectionParams = None):
        self.params = params or ConnectionParams()
        self.broker: Optional[AMQPBroker] = None
        self.state = ConnectionState.CLOSED
        
        self.channels: Dict[int, AMQPChannel] = {}
        self.next_channel_id = 1
        
        # Connection properties
        self.server_properties = {
            'product': 'AMQP Broker Simulation',
            'version': '1.0.0',
            'platform': 'Python',
            'capabilities': {
                'publisher_confirms': True,
                'consumer_cancel_notify': True,
                'exchange_exchange_bindings': False
            }
        }
        
        self.client_properties = {
            'product': 'AMQP Client Simulation',
            'version': '1.0.0',
            'platform': 'Python'
        }
    
    def connect(self, broker: AMQPBroker = None) -> bool:
        """Connect to AMQP broker"""
        if self.state != ConnectionState.CLOSED:
            return False
        
        self.state = ConnectionState.OPENING
        
        # In real implementation, this would establish TCP connection
        # and perform AMQP handshake
        if broker:
            self.broker = broker
        else:
            self.broker = AMQPBroker()
            self.broker.start()
        
        self.state = ConnectionState.OPEN
        print(f"🔌 Connected to AMQP broker at {self.params.host}:{self.params.port}")
        return True
    
    def channel(self, channel_id: int = None) -> AMQPChannel:
        """Open a new channel"""
        if self.state != ConnectionState.OPEN:
            raise Exception("Connection is not open")
        
        if channel_id is None:
            channel_id = self.next_channel_id
            self.next_channel_id += 1
        
        if channel_id in self.channels:
            raise Exception(f"Channel {channel_id} already exists")
        
        channel = AMQPChannel(channel_id, self)
        self.channels[channel_id] = channel
        
        print(f"📺 Channel {channel_id} opened")
        return channel
    
    def close(self):
        """Close the connection"""
        if self.state != ConnectionState.OPEN:
            return
        
        self.state = ConnectionState.CLOSING
        
        # Close all channels
        for channel in list(self.channels.values()):
            channel.close()
        
        self.channels.clear()
        self.state = ConnectionState.CLOSED
        
        print(f"🔌 Connection closed")
    
    def is_open(self) -> bool:
        """Check if connection is open"""
        return self.state == ConnectionState.OPEN

def demonstrate_amqp_client():
    """Demonstrate AMQP client functionality"""
    print("=== AMQP Client Demonstration ===")
    
    # Create and start broker
    broker = AMQPBroker()
    broker.start()
    
    try:
        # Create connection and channel
        connection = AMQPConnection()
        connection.connect(broker)
        
        channel = connection.channel()
        
        # Declare exchanges and queues
        channel.exchange_declare("orders", "direct", durable=True)
        channel.exchange_declare("notifications", "topic", durable=True)
        
        result = channel.queue_declare("order_queue", durable=True)
        print(f"📥 Declared queue: {result}")
        
        result = channel.queue_declare("notification_queue")
        print(f"📥 Declared queue: {result}")
        
        # Bind queues
        channel.queue_bind("order_queue", "orders", "new_order")
        channel.queue_bind("notification_queue", "notifications", "user.*.created")
        
        # Set up consumer
        def message_handler(message: Message, delivery_info: Dict):
            print(f"📨 Received: {message.body} (routing_key: {message.routing_key})")
            # Acknowledge message
            channel.basic_ack(delivery_info['delivery_tag'])
        
        # Start consuming
        consumer_tag = channel.basic_consume("order_queue", message_handler)
        print(f"👤 Started consumer: {consumer_tag}")
        
        # Publish messages
        print(f"\n📤 Publishing messages...")
        
        # Direct exchange
        channel.basic_publish("orders", "new_order", "Order #12345: 2x Widget", 
                             properties={'delivery_mode': 2, 'correlation_id': 'order-12345'})
        
        # Topic exchange
        channel.basic_publish("notifications", "user.john.created", "New user: john@example.com")
        channel.basic_publish("notifications", "user.jane.created", "New user: jane@example.com")
        
        time.sleep(1)  # Let messages process
        
        # Get message manually
        print(f"\n📨 Getting message manually...")
        result = channel.basic_get("notification_queue", no_ack=True)
        if result:
            print(f"Got message: {result['message'].body}")
        
        # Publisher confirms
        channel.confirm_select()
        print(f"✅ Publisher confirms enabled")
        
        # QoS settings
        channel.basic_qos(prefetch_count=10)
        print(f"⚙️  QoS set: prefetch_count=10")
        
        # Transaction example
        channel.tx_select()
        channel.basic_publish("orders", "new_order", "Order #12346: 1x Gadget")
        channel.tx_commit()
        print(f"💳 Transaction committed")
        
        time.sleep(1)  # Let final messages process
        
        # Display statistics
        print(f"\n📊 Channel Statistics:")
        print(f"   Published: {channel.stats['messages_published']}")
        print(f"   Consumed: {channel.stats['messages_consumed']}")
        print(f"   Acknowledged: {channel.stats['messages_acked']}")
        
        # Cancel consumer and close
        channel.basic_cancel(consumer_tag)
        channel.close()
        connection.close()
    
    finally:
        broker.stop()
    
    print("\n🎯 AMQP Client demonstrates:")
    print("💡 Connection and channel management")
    print("💡 Exchange and queue declarations")
    print("💡 Message publishing and consuming")
    print("💡 Acknowledgments and QoS settings")
    print("💡 Publisher confirms and transactions")

if __name__ == "__main__":
    demonstrate_amqp_client()
