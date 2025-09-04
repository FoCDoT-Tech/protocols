#!/usr/bin/env python3
"""
MQTT Broker Simulation
Lightweight publish-subscribe messaging for IoT devices.
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

class QoSLevel(Enum):
    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACTLY_ONCE = 2

class PacketType(Enum):
    CONNECT = 1
    CONNACK = 2
    PUBLISH = 3
    PUBACK = 4
    PUBREC = 5
    PUBREL = 6
    PUBCOMP = 7
    SUBSCRIBE = 8
    SUBACK = 9
    UNSUBSCRIBE = 10
    UNSUBACK = 11
    PINGREQ = 12
    PINGRESP = 13
    DISCONNECT = 14

@dataclass
class MQTTMessage:
    topic: str
    payload: str
    qos: QoSLevel = QoSLevel.AT_MOST_ONCE
    retain: bool = False
    packet_id: Optional[int] = None
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            'topic': self.topic,
            'payload': self.payload,
            'qos': self.qos.value,
            'retain': self.retain,
            'packet_id': self.packet_id,
            'timestamp': self.timestamp
        }

@dataclass
class Subscription:
    topic_filter: str
    qos: QoSLevel
    client_id: str
    callback: Callable

@dataclass
class ClientSession:
    client_id: str
    clean_session: bool
    connected: bool = False
    keep_alive: int = 60
    last_seen: float = field(default_factory=time.time)
    subscriptions: Dict[str, Subscription] = field(default_factory=dict)
    pending_messages: deque = field(default_factory=deque)
    will_message: Optional[MQTTMessage] = None
    
    def is_alive(self) -> bool:
        return time.time() - self.last_seen < self.keep_alive * 1.5

class TopicTree:
    def __init__(self):
        self.retained_messages: Dict[str, MQTTMessage] = {}
        self.subscriptions: Dict[str, List[Subscription]] = defaultdict(list)
    
    def add_subscription(self, subscription: Subscription):
        """Add subscription to topic tree"""
        self.subscriptions[subscription.topic_filter].append(subscription)
    
    def remove_subscription(self, client_id: str, topic_filter: str):
        """Remove subscription from topic tree"""
        if topic_filter in self.subscriptions:
            self.subscriptions[topic_filter] = [
                sub for sub in self.subscriptions[topic_filter] 
                if sub.client_id != client_id
            ]
    
    def get_matching_subscriptions(self, topic: str) -> List[Subscription]:
        """Get all subscriptions that match the given topic"""
        matching = []
        
        for topic_filter, subscriptions in self.subscriptions.items():
            if self._topic_matches_filter(topic, topic_filter):
                matching.extend(subscriptions)
        
        return matching
    
    def set_retained_message(self, message: MQTTMessage):
        """Set retained message for topic"""
        if message.retain:
            if message.payload:  # Non-empty payload
                self.retained_messages[message.topic] = message
            else:  # Empty payload clears retained message
                self.retained_messages.pop(message.topic, None)
    
    def get_retained_messages(self, topic_filter: str) -> List[MQTTMessage]:
        """Get retained messages matching topic filter"""
        matching = []
        
        for topic, message in self.retained_messages.items():
            if self._topic_matches_filter(topic, topic_filter):
                matching.append(message)
        
        return matching
    
    def _topic_matches_filter(self, topic: str, topic_filter: str) -> bool:
        """Check if topic matches topic filter with wildcards"""
        # Handle exact match
        if topic == topic_filter:
            return True
        
        # Handle wildcards
        topic_parts = topic.split('/')
        filter_parts = topic_filter.split('/')
        
        return self._match_parts(topic_parts, filter_parts)
    
    def _match_parts(self, topic_parts: List[str], filter_parts: List[str]) -> bool:
        """Match topic parts against filter parts"""
        i = j = 0
        
        while i < len(topic_parts) and j < len(filter_parts):
            if filter_parts[j] == '#':
                # Multi-level wildcard matches everything remaining
                return True
            elif filter_parts[j] == '+':
                # Single-level wildcard matches one level
                i += 1
                j += 1
            elif topic_parts[i] == filter_parts[j]:
                # Exact match
                i += 1
                j += 1
            else:
                # No match
                return False
        
        # Check if we consumed all parts
        if j < len(filter_parts) and filter_parts[j] == '#':
            return True
        
        return i == len(topic_parts) and j == len(filter_parts)

class MQTTBroker:
    def __init__(self, port: int = 1883):
        self.port = port
        self.topic_tree = TopicTree()
        self.sessions: Dict[str, ClientSession] = {}
        self.packet_id_counter = 1
        
        # Statistics
        self.stats = {
            'clients_connected': 0,
            'messages_published': 0,
            'messages_delivered': 0,
            'subscriptions_active': 0,
            'retained_messages': 0,
            'start_time': time.time()
        }
        
        self.running = False
        self._lock = threading.Lock()
    
    def start(self):
        """Start the MQTT broker"""
        self.running = True
        threading.Thread(target=self._session_cleanup_loop, daemon=True).start()
        print(f"🚀 MQTT Broker started on port {self.port}")
    
    def stop(self):
        """Stop the MQTT broker"""
        self.running = False
        print("🛑 MQTT Broker stopped")
    
    def connect(self, client_id: str, clean_session: bool = True, 
                keep_alive: int = 60, will_message: Optional[MQTTMessage] = None) -> bool:
        """Handle client connection"""
        with self._lock:
            # Check for existing session
            if client_id in self.sessions and not clean_session:
                # Resume existing session
                session = self.sessions[client_id]
                session.connected = True
                session.last_seen = time.time()
            else:
                # Create new session
                session = ClientSession(
                    client_id=client_id,
                    clean_session=clean_session,
                    connected=True,
                    keep_alive=keep_alive,
                    will_message=will_message
                )
                self.sessions[client_id] = session
            
            self.stats['clients_connected'] += 1
            print(f"🔌 Client '{client_id}' connected (clean_session={clean_session})")
            
            # Send retained messages for existing subscriptions
            if not clean_session:
                self._send_retained_messages(session)
            
            return True
    
    def disconnect(self, client_id: str, graceful: bool = True):
        """Handle client disconnection"""
        with self._lock:
            if client_id not in self.sessions:
                return
            
            session = self.sessions[client_id]
            session.connected = False
            
            if not graceful and session.will_message:
                # Send Last Will and Testament
                self._publish_message(session.will_message)
                print(f"💀 Published Last Will for '{client_id}': {session.will_message.topic}")
            
            if session.clean_session:
                # Clean up session
                self._cleanup_session(client_id)
            
            print(f"🔌 Client '{client_id}' disconnected ({'graceful' if graceful else 'unexpected'})")
    
    def publish(self, client_id: str, message: MQTTMessage) -> bool:
        """Publish message to topic"""
        with self._lock:
            if client_id not in self.sessions or not self.sessions[client_id].connected:
                return False
            
            # Update client last seen
            self.sessions[client_id].last_seen = time.time()
            
            # Handle retained message
            if message.retain:
                self.topic_tree.set_retained_message(message)
                self.stats['retained_messages'] = len(self.topic_tree.retained_messages)
            
            # Publish to subscribers
            return self._publish_message(message)
    
    def subscribe(self, client_id: str, topic_filter: str, qos: QoSLevel, 
                  callback: Callable) -> bool:
        """Subscribe client to topic filter"""
        with self._lock:
            if client_id not in self.sessions:
                return False
            
            session = self.sessions[client_id]
            session.last_seen = time.time()
            
            # Create subscription
            subscription = Subscription(
                topic_filter=topic_filter,
                qos=qos,
                client_id=client_id,
                callback=callback
            )
            
            # Add to session and topic tree
            session.subscriptions[topic_filter] = subscription
            self.topic_tree.add_subscription(subscription)
            
            self.stats['subscriptions_active'] = sum(
                len(s.subscriptions) for s in self.sessions.values()
            )
            
            print(f"📝 Client '{client_id}' subscribed to '{topic_filter}' (QoS {qos.value})")
            
            # Send retained messages
            retained_messages = self.topic_tree.get_retained_messages(topic_filter)
            for retained_msg in retained_messages:
                self._deliver_message(subscription, retained_msg)
            
            return True
    
    def unsubscribe(self, client_id: str, topic_filter: str) -> bool:
        """Unsubscribe client from topic filter"""
        with self._lock:
            if client_id not in self.sessions:
                return False
            
            session = self.sessions[client_id]
            session.last_seen = time.time()
            
            # Remove from session
            if topic_filter in session.subscriptions:
                del session.subscriptions[topic_filter]
            
            # Remove from topic tree
            self.topic_tree.remove_subscription(client_id, topic_filter)
            
            self.stats['subscriptions_active'] = sum(
                len(s.subscriptions) for s in self.sessions.values()
            )
            
            print(f"📝 Client '{client_id}' unsubscribed from '{topic_filter}'")
            return True
    
    def ping(self, client_id: str) -> bool:
        """Handle ping request"""
        with self._lock:
            if client_id in self.sessions:
                self.sessions[client_id].last_seen = time.time()
                return True
            return False
    
    def _publish_message(self, message: MQTTMessage) -> bool:
        """Publish message to all matching subscribers"""
        matching_subscriptions = self.topic_tree.get_matching_subscriptions(message.topic)
        
        if not matching_subscriptions:
            print(f"⚠️  No subscribers for topic '{message.topic}'")
            return False
        
        delivered = 0
        for subscription in matching_subscriptions:
            if self._deliver_message(subscription, message):
                delivered += 1
        
        self.stats['messages_published'] += 1
        self.stats['messages_delivered'] += delivered
        
        print(f"📤 Published to '{message.topic}': delivered to {delivered} subscribers")
        return delivered > 0
    
    def _deliver_message(self, subscription: Subscription, message: MQTTMessage) -> bool:
        """Deliver message to specific subscriber"""
        session = self.sessions.get(subscription.client_id)
        if not session:
            return False
        
        # Adjust QoS to minimum of publisher and subscriber
        delivery_qos = QoSLevel(min(message.qos.value, subscription.qos.value))
        
        # Create delivery message
        delivery_message = MQTTMessage(
            topic=message.topic,
            payload=message.payload,
            qos=delivery_qos,
            retain=False,  # Don't set retain flag on delivery
            packet_id=self._get_next_packet_id() if delivery_qos != QoSLevel.AT_MOST_ONCE else None
        )
        
        try:
            if session.connected:
                # Deliver immediately
                subscription.callback(delivery_message)
            else:
                # Queue for later delivery (persistent session)
                if not session.clean_session:
                    session.pending_messages.append(delivery_message)
            
            return True
        except Exception as e:
            print(f"❌ Failed to deliver message to '{subscription.client_id}': {e}")
            return False
    
    def _send_retained_messages(self, session: ClientSession):
        """Send retained messages for session subscriptions"""
        for subscription in session.subscriptions.values():
            retained_messages = self.topic_tree.get_retained_messages(subscription.topic_filter)
            for retained_msg in retained_messages:
                self._deliver_message(subscription, retained_msg)
    
    def _get_next_packet_id(self) -> int:
        """Get next packet ID"""
        packet_id = self.packet_id_counter
        self.packet_id_counter = (self.packet_id_counter % 65535) + 1
        return packet_id
    
    def _session_cleanup_loop(self):
        """Clean up inactive sessions"""
        while self.running:
            try:
                with self._lock:
                    inactive_clients = []
                    
                    for client_id, session in self.sessions.items():
                        if session.connected and not session.is_alive():
                            # Client timed out
                            inactive_clients.append(client_id)
                    
                    for client_id in inactive_clients:
                        self.disconnect(client_id, graceful=False)
                
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"❌ Session cleanup error: {e}")
    
    def _cleanup_session(self, client_id: str):
        """Clean up session data"""
        if client_id in self.sessions:
            session = self.sessions[client_id]
            
            # Remove subscriptions
            for topic_filter in session.subscriptions:
                self.topic_tree.remove_subscription(client_id, topic_filter)
            
            # Remove session
            del self.sessions[client_id]
    
    def get_broker_stats(self) -> Dict:
        """Get broker statistics"""
        with self._lock:
            connected_clients = sum(1 for s in self.sessions.values() if s.connected)
            total_subscriptions = sum(len(s.subscriptions) for s in self.sessions.values())
            
            return {
                'uptime': time.time() - self.stats['start_time'],
                'connected_clients': connected_clients,
                'total_sessions': len(self.sessions),
                'active_subscriptions': total_subscriptions,
                'retained_messages': len(self.topic_tree.retained_messages),
                'messages_published': self.stats['messages_published'],
                'messages_delivered': self.stats['messages_delivered']
            }

def demonstrate_mqtt_broker():
    """Demonstrate MQTT broker functionality"""
    print("=== MQTT Broker Demonstration ===")
    
    broker = MQTTBroker()
    broker.start()
    
    try:
        # Connect clients
        broker.connect("sensor_01", clean_session=True, keep_alive=60)
        broker.connect("mobile_app", clean_session=False, keep_alive=120)
        broker.connect("automation", clean_session=False, keep_alive=300)
        
        # Set up subscribers
        def temperature_handler(message: MQTTMessage):
            print(f"🌡️  Temperature: {message.payload}°C (topic: {message.topic})")
        
        def motion_handler(message: MQTTMessage):
            print(f"🚶 Motion detected: {message.payload} (topic: {message.topic})")
        
        def all_sensors_handler(message: MQTTMessage):
            print(f"📱 Mobile app received: {message.topic} = {message.payload}")
        
        # Subscribe to topics
        broker.subscribe("mobile_app", "home/+/+", QoSLevel.AT_LEAST_ONCE, all_sensors_handler)
        broker.subscribe("automation", "home/+/temperature", QoSLevel.AT_MOST_ONCE, temperature_handler)
        broker.subscribe("automation", "home/+/motion", QoSLevel.EXACTLY_ONCE, motion_handler)
        
        # Publish messages
        print(f"\n📤 Publishing sensor data...")
        
        # Temperature readings with retention
        temp_msg = MQTTMessage("home/living/temperature", "22.5", QoSLevel.AT_LEAST_ONCE, retain=True)
        broker.publish("sensor_01", temp_msg)
        
        temp_msg2 = MQTTMessage("home/bedroom/temperature", "20.1", QoSLevel.AT_LEAST_ONCE, retain=True)
        broker.publish("sensor_01", temp_msg2)
        
        # Motion detection
        motion_msg = MQTTMessage("home/entry/motion", "detected", QoSLevel.EXACTLY_ONCE)
        broker.publish("sensor_01", motion_msg)
        
        # Humidity reading
        humid_msg = MQTTMessage("home/bathroom/humidity", "65", QoSLevel.AT_MOST_ONCE)
        broker.publish("sensor_01", humid_msg)
        
        time.sleep(1)  # Let messages process
        
        # Test retained messages with new subscriber
        print(f"\n🔄 Testing retained messages...")
        
        def new_subscriber_handler(message: MQTTMessage):
            print(f"🆕 New subscriber received retained: {message.topic} = {message.payload}")
        
        broker.connect("new_device", clean_session=True)
        broker.subscribe("new_device", "home/+/temperature", QoSLevel.AT_MOST_ONCE, new_subscriber_handler)
        
        time.sleep(0.5)
        
        # Test Last Will and Testament
        print(f"\n💀 Testing Last Will and Testament...")
        
        will_msg = MQTTMessage("home/sensor_02/status", "offline", QoSLevel.AT_LEAST_ONCE)
        broker.connect("sensor_02", clean_session=True, will_message=will_msg)
        
        def status_handler(message: MQTTMessage):
            print(f"📊 Status update: {message.topic} = {message.payload}")
        
        broker.subscribe("automation", "home/+/status", QoSLevel.AT_LEAST_ONCE, status_handler)
        
        # Simulate unexpected disconnect
        broker.disconnect("sensor_02", graceful=False)
        
        time.sleep(0.5)
        
        # Display broker statistics
        print(f"\n📊 Broker Statistics:")
        stats = broker.get_broker_stats()
        print(f"   Uptime: {stats['uptime']:.1f}s")
        print(f"   Connected clients: {stats['connected_clients']}")
        print(f"   Total sessions: {stats['total_sessions']}")
        print(f"   Active subscriptions: {stats['active_subscriptions']}")
        print(f"   Retained messages: {stats['retained_messages']}")
        print(f"   Messages published: {stats['messages_published']}")
        print(f"   Messages delivered: {stats['messages_delivered']}")
    
    finally:
        broker.stop()
    
    print("\n🎯 MQTT Broker demonstrates:")
    print("💡 Lightweight publish-subscribe messaging")
    print("💡 Topic-based routing with wildcards")
    print("💡 Quality of Service levels (0, 1, 2)")
    print("💡 Retained messages and session persistence")
    print("💡 Last Will and Testament for device failures")

if __name__ == "__main__":
    demonstrate_mqtt_broker()
