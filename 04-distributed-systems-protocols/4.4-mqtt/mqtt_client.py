#!/usr/bin/env python3
"""
MQTT Client Implementation
Publisher and subscriber client for MQTT messaging.
"""

import time
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import uuid

from mqtt_broker import MQTTBroker, MQTTMessage, QoSLevel

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"

@dataclass
class MQTTClientConfig:
    broker_host: str = "localhost"
    broker_port: int = 1883
    client_id: str = ""
    clean_session: bool = True
    keep_alive: int = 60
    username: Optional[str] = None
    password: Optional[str] = None
    will_topic: Optional[str] = None
    will_payload: Optional[str] = None
    will_qos: QoSLevel = QoSLevel.AT_MOST_ONCE
    will_retain: bool = False

class MQTTClient:
    def __init__(self, config: MQTTClientConfig = None):
        self.config = config or MQTTClientConfig()
        
        # Generate client ID if not provided
        if not self.config.client_id:
            self.config.client_id = f"mqtt_client_{uuid.uuid4().hex[:8]}"
        
        self.broker: Optional[MQTTBroker] = None
        self.state = ConnectionState.DISCONNECTED
        
        # Subscriptions and callbacks
        self.subscriptions: Dict[str, Callable] = {}
        self.message_callbacks: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            'messages_published': 0,
            'messages_received': 0,
            'connection_attempts': 0,
            'successful_connections': 0,
            'last_connect_time': 0,
            'total_uptime': 0
        }
        
        # Threading
        self._lock = threading.Lock()
        self._ping_thread: Optional[threading.Thread] = None
        self._running = False
    
    def connect(self, broker: MQTTBroker = None) -> bool:
        """Connect to MQTT broker"""
        with self._lock:
            if self.state != ConnectionState.DISCONNECTED:
                return False
            
            self.state = ConnectionState.CONNECTING
            self.stats['connection_attempts'] += 1
            
            # Use provided broker or create new one
            if broker:
                self.broker = broker
            else:
                self.broker = MQTTBroker(self.config.broker_port)
                self.broker.start()
            
            # Prepare Last Will and Testament
            will_message = None
            if self.config.will_topic:
                will_message = MQTTMessage(
                    topic=self.config.will_topic,
                    payload=self.config.will_payload or "",
                    qos=self.config.will_qos,
                    retain=self.config.will_retain
                )
            
            # Connect to broker
            success = self.broker.connect(
                client_id=self.config.client_id,
                clean_session=self.config.clean_session,
                keep_alive=self.config.keep_alive,
                will_message=will_message
            )
            
            if success:
                self.state = ConnectionState.CONNECTED
                self.stats['successful_connections'] += 1
                self.stats['last_connect_time'] = time.time()
                self._running = True
                
                # Start ping thread for keep-alive
                self._ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
                self._ping_thread.start()
                
                print(f"🔌 MQTT Client '{self.config.client_id}' connected to {self.config.broker_host}:{self.config.broker_port}")
                return True
            else:
                self.state = ConnectionState.DISCONNECTED
                return False
    
    def disconnect(self) -> bool:
        """Disconnect from MQTT broker"""
        with self._lock:
            if self.state != ConnectionState.CONNECTED:
                return False
            
            self.state = ConnectionState.DISCONNECTING
            self._running = False
            
            # Calculate uptime
            if self.stats['last_connect_time']:
                self.stats['total_uptime'] += time.time() - self.stats['last_connect_time']
            
            # Disconnect from broker
            if self.broker:
                self.broker.disconnect(self.config.client_id, graceful=True)
            
            self.state = ConnectionState.DISCONNECTED
            print(f"🔌 MQTT Client '{self.config.client_id}' disconnected")
            return True
    
    def publish(self, topic: str, payload: str, qos: QoSLevel = QoSLevel.AT_MOST_ONCE, 
                retain: bool = False) -> bool:
        """Publish message to topic"""
        with self._lock:
            if self.state != ConnectionState.CONNECTED or not self.broker:
                print(f"❌ Cannot publish: client not connected")
                return False
            
            message = MQTTMessage(
                topic=topic,
                payload=payload,
                qos=qos,
                retain=retain
            )
            
            success = self.broker.publish(self.config.client_id, message)
            
            if success:
                self.stats['messages_published'] += 1
                print(f"📤 Published to '{topic}': {payload}")
            
            return success
    
    def subscribe(self, topic_filter: str, qos: QoSLevel = QoSLevel.AT_MOST_ONCE, 
                  callback: Callable = None) -> bool:
        """Subscribe to topic filter"""
        with self._lock:
            if self.state != ConnectionState.CONNECTED or not self.broker:
                print(f"❌ Cannot subscribe: client not connected")
                return False
            
            # Use provided callback or default message handler
            if callback:
                message_callback = callback
            else:
                message_callback = self._default_message_handler
            
            # Wrap callback to handle statistics
            def wrapped_callback(message: MQTTMessage):
                self.stats['messages_received'] += 1
                message_callback(message)
            
            success = self.broker.subscribe(
                client_id=self.config.client_id,
                topic_filter=topic_filter,
                qos=qos,
                callback=wrapped_callback
            )
            
            if success:
                self.subscriptions[topic_filter] = wrapped_callback
                print(f"📝 Subscribed to '{topic_filter}' (QoS {qos.value})")
            
            return success
    
    def unsubscribe(self, topic_filter: str) -> bool:
        """Unsubscribe from topic filter"""
        with self._lock:
            if self.state != ConnectionState.CONNECTED or not self.broker:
                return False
            
            success = self.broker.unsubscribe(self.config.client_id, topic_filter)
            
            if success and topic_filter in self.subscriptions:
                del self.subscriptions[topic_filter]
                print(f"📝 Unsubscribed from '{topic_filter}'")
            
            return success
    
    def set_message_callback(self, topic_pattern: str, callback: Callable):
        """Set callback for specific topic pattern"""
        self.message_callbacks[topic_pattern] = callback
    
    def _default_message_handler(self, message: MQTTMessage):
        """Default message handler"""
        print(f"📨 Received: {message.topic} = {message.payload} (QoS {message.qos.value})")
        
        # Check for specific topic callbacks
        for pattern, callback in self.message_callbacks.items():
            if self._topic_matches_pattern(message.topic, pattern):
                try:
                    callback(message)
                except Exception as e:
                    print(f"❌ Callback error for {pattern}: {e}")
    
    def _topic_matches_pattern(self, topic: str, pattern: str) -> bool:
        """Simple topic pattern matching"""
        if pattern == topic:
            return True
        
        # Handle simple wildcards
        if '+' in pattern or '#' in pattern:
            topic_parts = topic.split('/')
            pattern_parts = pattern.split('/')
            
            return self._match_topic_parts(topic_parts, pattern_parts)
        
        return False
    
    def _match_topic_parts(self, topic_parts: List[str], pattern_parts: List[str]) -> bool:
        """Match topic parts against pattern"""
        i = j = 0
        
        while i < len(topic_parts) and j < len(pattern_parts):
            if pattern_parts[j] == '#':
                return True
            elif pattern_parts[j] == '+':
                i += 1
                j += 1
            elif topic_parts[i] == pattern_parts[j]:
                i += 1
                j += 1
            else:
                return False
        
        return i == len(topic_parts) and j == len(pattern_parts)
    
    def _ping_loop(self):
        """Keep-alive ping loop"""
        ping_interval = self.config.keep_alive / 2
        
        while self._running and self.state == ConnectionState.CONNECTED:
            try:
                if self.broker:
                    self.broker.ping(self.config.client_id)
                
                time.sleep(ping_interval)
            except Exception as e:
                print(f"❌ Ping error: {e}")
                break
    
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self.state == ConnectionState.CONNECTED
    
    def get_stats(self) -> Dict:
        """Get client statistics"""
        with self._lock:
            current_uptime = 0
            if self.state == ConnectionState.CONNECTED and self.stats['last_connect_time']:
                current_uptime = time.time() - self.stats['last_connect_time']
            
            return {
                'client_id': self.config.client_id,
                'state': self.state.value,
                'subscriptions': len(self.subscriptions),
                'total_uptime': self.stats['total_uptime'] + current_uptime,
                **self.stats
            }

def demonstrate_mqtt_client():
    """Demonstrate MQTT client functionality"""
    print("=== MQTT Client Demonstration ===")
    
    # Create and start broker
    broker = MQTTBroker()
    broker.start()
    
    try:
        # Create clients
        sensor_config = MQTTClientConfig(
            client_id="temperature_sensor",
            clean_session=True,
            will_topic="sensors/temperature/status",
            will_payload="offline",
            will_qos=QoSLevel.AT_LEAST_ONCE
        )
        
        app_config = MQTTClientConfig(
            client_id="mobile_app",
            clean_session=False,
            keep_alive=120
        )
        
        sensor_client = MQTTClient(sensor_config)
        app_client = MQTTClient(app_config)
        
        # Connect clients
        sensor_client.connect(broker)
        app_client.connect(broker)
        
        # Set up message handlers
        def temperature_handler(message: MQTTMessage):
            temp = float(message.payload)
            if temp > 25:
                print(f"🔥 High temperature alert: {temp}°C")
            else:
                print(f"🌡️  Temperature normal: {temp}°C")
        
        def status_handler(message: MQTTMessage):
            print(f"📊 Device status: {message.topic.split('/')[-2]} is {message.payload}")
        
        # Subscribe to topics
        app_client.set_message_callback("sensors/+/temperature", temperature_handler)
        app_client.set_message_callback("sensors/+/status", status_handler)
        
        app_client.subscribe("sensors/+/temperature", QoSLevel.AT_LEAST_ONCE)
        app_client.subscribe("sensors/+/status", QoSLevel.AT_LEAST_ONCE)
        app_client.subscribe("alerts/#", QoSLevel.EXACTLY_ONCE)
        
        # Publish sensor data
        print(f"\n📤 Publishing sensor readings...")
        
        # Temperature readings
        sensor_client.publish("sensors/temperature/temperature", "22.5", QoSLevel.AT_LEAST_ONCE, retain=True)
        sensor_client.publish("sensors/temperature/temperature", "24.1", QoSLevel.AT_LEAST_ONCE, retain=True)
        sensor_client.publish("sensors/temperature/temperature", "26.8", QoSLevel.AT_LEAST_ONCE, retain=True)
        
        # Status updates
        sensor_client.publish("sensors/temperature/status", "online", QoSLevel.AT_LEAST_ONCE, retain=True)
        
        # Alert message
        sensor_client.publish("alerts/temperature/high", "Temperature exceeded threshold", QoSLevel.EXACTLY_ONCE)
        
        time.sleep(1)  # Let messages process
        
        # Test retained messages
        print(f"\n🔄 Testing retained messages with new client...")
        
        new_config = MQTTClientConfig(client_id="new_subscriber")
        new_client = MQTTClient(new_config)
        new_client.connect(broker)
        
        def retained_handler(message: MQTTMessage):
            print(f"🆕 New client received retained: {message.topic} = {message.payload}")
        
        new_client.set_message_callback("sensors/+/+", retained_handler)
        new_client.subscribe("sensors/+/+", QoSLevel.AT_MOST_ONCE)
        
        time.sleep(0.5)
        
        # Test Last Will and Testament
        print(f"\n💀 Testing Last Will and Testament...")
        
        # Simulate unexpected disconnect
        broker.disconnect("temperature_sensor", graceful=False)
        
        time.sleep(0.5)
        
        # Display client statistics
        print(f"\n📊 Client Statistics:")
        
        for client, name in [(app_client, "Mobile App"), (new_client, "New Subscriber")]:
            if client.is_connected():
                stats = client.get_stats()
                print(f"   {name} ({stats['client_id']}):")
                print(f"     State: {stats['state']}")
                print(f"     Subscriptions: {stats['subscriptions']}")
                print(f"     Messages published: {stats['messages_published']}")
                print(f"     Messages received: {stats['messages_received']}")
                print(f"     Uptime: {stats['total_uptime']:.1f}s")
        
        # Cleanup
        app_client.disconnect()
        new_client.disconnect()
    
    finally:
        broker.stop()
    
    print("\n🎯 MQTT Client demonstrates:")
    print("💡 Lightweight client connections with keep-alive")
    print("💡 Topic-based publish and subscribe operations")
    print("💡 Quality of Service levels and message delivery")
    print("💡 Retained messages for last known state")
    print("💡 Last Will and Testament for unexpected disconnects")

if __name__ == "__main__":
    demonstrate_mqtt_client()
