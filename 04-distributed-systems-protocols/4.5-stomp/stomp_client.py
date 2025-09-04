#!/usr/bin/env python3
"""
STOMP Client Implementation
Simple Text Oriented Messaging Protocol client with WebSocket support.
"""

import time
import threading
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
import json

from stomp_broker import StompFrame, StompCommand, AckMode

@dataclass
class StompClientConfig:
    broker_host: str = "localhost"
    broker_port: int = 61613
    login: str = ""
    passcode: str = ""
    virtual_host: str = "/"
    heart_beat: tuple = (10000, 10000)  # (send, receive) in ms
    connect_timeout: float = 5.0
    receipt_timeout: float = 10.0

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"

class StompClient:
    def __init__(self, config: StompClientConfig):
        self.config = config
        self.state = ConnectionState.DISCONNECTED
        self.session_id = ""
        self.server_version = ""
        
        # Message handling
        self.subscriptions: Dict[str, Dict] = {}
        self.pending_receipts: Dict[str, threading.Event] = {}
        self.pending_acks: Dict[str, StompFrame] = {}
        
        # Callbacks
        self.message_handlers: Dict[str, Callable[[StompFrame], None]] = {}
        self.error_handler: Optional[Callable[[StompFrame], None]] = None
        self.connect_handler: Optional[Callable[[StompFrame], None]] = None
        self.disconnect_handler: Optional[Callable[[], None]] = None
        
        # Threading
        self._lock = threading.Lock()
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._stop_heartbeat = threading.Event()
        
        # Statistics
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'connect_time': 0,
            'last_activity': time.time(),
            'heartbeats_sent': 0,
            'heartbeats_received': 0
        }
        
        # Simulated broker for demonstration
        self._broker = None
        self._client_id = f"client_{uuid.uuid4().hex[:8]}"
    
    def connect(self, broker=None) -> bool:
        """Connect to STOMP broker"""
        if self.state != ConnectionState.DISCONNECTED:
            return False
        
        self.state = ConnectionState.CONNECTING
        self._broker = broker  # For simulation
        
        try:
            # Create CONNECT frame
            headers = {
                'accept-version': '1.2',
                'host': self.config.virtual_host,
                'heart-beat': f"{self.config.heart_beat[0]},{self.config.heart_beat[1]}"
            }
            
            if self.config.login:
                headers['login'] = self.config.login
            if self.config.passcode:
                headers['passcode'] = self.config.passcode
            
            connect_frame = StompFrame(StompCommand.CONNECT, headers)
            
            # Send to broker (simulated)
            if self._broker:
                response = self._broker.process_frame(self._client_id, connect_frame)
                if response and response.command == StompCommand.CONNECTED:
                    self._handle_connected(response)
                    return True
                else:
                    self.state = ConnectionState.DISCONNECTED
                    return False
            else:
                # Simulate successful connection
                self._simulate_connected()
                return True
        
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.state = ConnectionState.DISCONNECTED
            return False
    
    def disconnect(self, receipt: bool = True) -> bool:
        """Disconnect from STOMP broker"""
        if self.state != ConnectionState.CONNECTED:
            return False
        
        self.state = ConnectionState.DISCONNECTING
        
        try:
            headers = {}
            if receipt:
                receipt_id = str(uuid.uuid4())
                headers['receipt'] = receipt_id
                self._setup_receipt_wait(receipt_id)
            
            disconnect_frame = StompFrame(StompCommand.DISCONNECT, headers)
            
            # Send to broker
            if self._broker:
                self._broker.process_frame(self._client_id, disconnect_frame)
            
            # Wait for receipt if requested
            if receipt and receipt_id in self.pending_receipts:
                self.pending_receipts[receipt_id].wait(timeout=self.config.receipt_timeout)
            
            self._cleanup_connection()
            return True
        
        except Exception as e:
            print(f"❌ Disconnect failed: {e}")
            self._cleanup_connection()
            return False
    
    def send(self, destination: str, body: str, headers: Optional[Dict[str, str]] = None,
             transaction: Optional[str] = None, receipt: bool = False) -> Optional[str]:
        """Send message to destination"""
        if self.state != ConnectionState.CONNECTED:
            raise RuntimeError("Not connected to broker")
        
        send_headers = {'destination': destination}
        
        if headers:
            send_headers.update(headers)
        
        if transaction:
            send_headers['transaction'] = transaction
        
        receipt_id = None
        if receipt:
            receipt_id = str(uuid.uuid4())
            send_headers['receipt'] = receipt_id
            self._setup_receipt_wait(receipt_id)
        
        # Set content headers
        if 'content-type' not in send_headers:
            send_headers['content-type'] = 'text/plain'
        
        send_headers['content-length'] = str(len(body.encode('utf-8')))
        
        send_frame = StompFrame(StompCommand.SEND, send_headers, body)
        
        # Send to broker
        if self._broker:
            response = self._broker.process_frame(self._client_id, send_frame)
            if response and response.command == StompCommand.ERROR:
                raise RuntimeError(f"Send failed: {response.body}")
        
        self.stats['messages_sent'] += 1
        self.stats['last_activity'] = time.time()
        
        print(f"📤 Sent message to '{destination}': {body[:50]}...")
        
        return receipt_id
    
    def subscribe(self, destination: str, callback: Callable[[StompFrame], None],
                  ack_mode: AckMode = AckMode.AUTO, headers: Optional[Dict[str, str]] = None) -> str:
        """Subscribe to destination"""
        if self.state != ConnectionState.CONNECTED:
            raise RuntimeError("Not connected to broker")
        
        subscription_id = str(uuid.uuid4())
        
        subscribe_headers = {
            'destination': destination,
            'id': subscription_id,
            'ack': ack_mode.value
        }
        
        if headers:
            subscribe_headers.update(headers)
        
        subscribe_frame = StompFrame(StompCommand.SUBSCRIBE, subscribe_headers)
        
        # Send to broker
        if self._broker:
            response = self._broker.process_frame(self._client_id, subscribe_frame)
            if response and response.command == StompCommand.ERROR:
                raise RuntimeError(f"Subscribe failed: {response.body}")
        
        # Store subscription
        with self._lock:
            self.subscriptions[subscription_id] = {
                'destination': destination,
                'callback': callback,
                'ack_mode': ack_mode,
                'headers': headers or {}
            }
            self.message_handlers[subscription_id] = callback
        
        print(f"📝 Subscribed to '{destination}' (id: {subscription_id})")
        
        return subscription_id
    
    def unsubscribe(self, subscription_id: str, receipt: bool = False) -> Optional[str]:
        """Unsubscribe from destination"""
        if self.state != ConnectionState.CONNECTED:
            raise RuntimeError("Not connected to broker")
        
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Unknown subscription: {subscription_id}")
        
        headers = {'id': subscription_id}
        
        receipt_id = None
        if receipt:
            receipt_id = str(uuid.uuid4())
            headers['receipt'] = receipt_id
            self._setup_receipt_wait(receipt_id)
        
        unsubscribe_frame = StompFrame(StompCommand.UNSUBSCRIBE, headers)
        
        # Send to broker
        if self._broker:
            self._broker.process_frame(self._client_id, unsubscribe_frame)
        
        # Remove subscription
        with self._lock:
            destination = self.subscriptions[subscription_id]['destination']
            del self.subscriptions[subscription_id]
            if subscription_id in self.message_handlers:
                del self.message_handlers[subscription_id]
        
        print(f"📝 Unsubscribed from '{destination}'")
        
        return receipt_id
    
    def ack(self, message_frame: StompFrame, transaction: Optional[str] = None) -> None:
        """Acknowledge message"""
        if self.state != ConnectionState.CONNECTED:
            raise RuntimeError("Not connected to broker")
        
        message_id = message_frame.headers.get('message-id')
        if not message_id:
            raise ValueError("Message has no message-id header")
        
        headers = {'id': message_id}
        
        if transaction:
            headers['transaction'] = transaction
        
        ack_frame = StompFrame(StompCommand.ACK, headers)
        
        # Send to broker
        if self._broker:
            self._broker.process_frame(self._client_id, ack_frame)
        
        # Remove from pending acks
        with self._lock:
            if message_id in self.pending_acks:
                del self.pending_acks[message_id]
        
        print(f"✅ Acknowledged message '{message_id}'")
    
    def nack(self, message_frame: StompFrame, transaction: Optional[str] = None) -> None:
        """Reject message"""
        if self.state != ConnectionState.CONNECTED:
            raise RuntimeError("Not connected to broker")
        
        message_id = message_frame.headers.get('message-id')
        if not message_id:
            raise ValueError("Message has no message-id header")
        
        headers = {'id': message_id}
        
        if transaction:
            headers['transaction'] = transaction
        
        nack_frame = StompFrame(StompCommand.NACK, headers)
        
        # Send to broker
        if self._broker:
            self._broker.process_frame(self._client_id, nack_frame)
        
        # Remove from pending acks
        with self._lock:
            if message_id in self.pending_acks:
                del self.pending_acks[message_id]
        
        print(f"❌ Rejected message '{message_id}'")
    
    def begin_transaction(self, transaction_id: Optional[str] = None) -> str:
        """Begin transaction"""
        if self.state != ConnectionState.CONNECTED:
            raise RuntimeError("Not connected to broker")
        
        if not transaction_id:
            transaction_id = f"tx-{uuid.uuid4().hex[:8]}"
        
        begin_frame = StompFrame(StompCommand.BEGIN, {'transaction': transaction_id})
        
        # Send to broker
        if self._broker:
            response = self._broker.process_frame(self._client_id, begin_frame)
            if response and response.command == StompCommand.ERROR:
                raise RuntimeError(f"Begin transaction failed: {response.body}")
        
        print(f"🔄 Started transaction '{transaction_id}'")
        
        return transaction_id
    
    def commit_transaction(self, transaction_id: str, receipt: bool = False) -> Optional[str]:
        """Commit transaction"""
        if self.state != ConnectionState.CONNECTED:
            raise RuntimeError("Not connected to broker")
        
        headers = {'transaction': transaction_id}
        
        receipt_id = None
        if receipt:
            receipt_id = str(uuid.uuid4())
            headers['receipt'] = receipt_id
            self._setup_receipt_wait(receipt_id)
        
        commit_frame = StompFrame(StompCommand.COMMIT, headers)
        
        # Send to broker
        if self._broker:
            response = self._broker.process_frame(self._client_id, commit_frame)
            if response and response.command == StompCommand.ERROR:
                raise RuntimeError(f"Commit transaction failed: {response.body}")
        
        print(f"✅ Committed transaction '{transaction_id}'")
        
        return receipt_id
    
    def abort_transaction(self, transaction_id: str, receipt: bool = False) -> Optional[str]:
        """Abort transaction"""
        if self.state != ConnectionState.CONNECTED:
            raise RuntimeError("Not connected to broker")
        
        headers = {'transaction': transaction_id}
        
        receipt_id = None
        if receipt:
            receipt_id = str(uuid.uuid4())
            headers['receipt'] = receipt_id
            self._setup_receipt_wait(receipt_id)
        
        abort_frame = StompFrame(StompCommand.ABORT, headers)
        
        # Send to broker
        if self._broker:
            response = self._broker.process_frame(self._client_id, abort_frame)
            if response and response.command == StompCommand.ERROR:
                raise RuntimeError(f"Abort transaction failed: {response.body}")
        
        print(f"❌ Aborted transaction '{transaction_id}'")
        
        return receipt_id
    
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self.state == ConnectionState.CONNECTED
    
    def get_stats(self) -> Dict:
        """Get client statistics"""
        return {
            'state': self.state.value,
            'session_id': self.session_id,
            'subscriptions': len(self.subscriptions),
            'pending_acks': len(self.pending_acks),
            'stats': self.stats.copy()
        }
    
    def _handle_connected(self, frame: StompFrame):
        """Handle CONNECTED frame"""
        self.state = ConnectionState.CONNECTED
        self.session_id = frame.headers.get('session', '')
        self.server_version = frame.headers.get('version', '')
        self.stats['connect_time'] = time.time()
        
        # Start heartbeat if supported
        heart_beat = frame.headers.get('heart-beat', '0,0')
        try:
            send_interval, receive_interval = map(int, heart_beat.split(','))
            if send_interval > 0 or receive_interval > 0:
                self._start_heartbeat(send_interval, receive_interval)
        except ValueError:
            pass
        
        print(f"🔌 Connected to STOMP broker (session: {self.session_id})")
        
        if self.connect_handler:
            self.connect_handler(frame)
    
    def _simulate_connected(self):
        """Simulate successful connection for demonstration"""
        connected_frame = StompFrame(
            StompCommand.CONNECTED,
            {
                'version': '1.2',
                'session': f"session-{uuid.uuid4().hex[:8]}",
                'server': 'STOMP-Client-Demo/1.0',
                'heart-beat': '10000,10000'
            }
        )
        self._handle_connected(connected_frame)
    
    def _setup_receipt_wait(self, receipt_id: str):
        """Setup receipt waiting mechanism"""
        self.pending_receipts[receipt_id] = threading.Event()
    
    def _cleanup_connection(self):
        """Clean up connection state"""
        self.state = ConnectionState.DISCONNECTED
        self._stop_heartbeat.set()
        
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=1.0)
        
        with self._lock:
            self.subscriptions.clear()
            self.message_handlers.clear()
            self.pending_acks.clear()
            self.pending_receipts.clear()
        
        if self.disconnect_handler:
            self.disconnect_handler()
    
    def _start_heartbeat(self, send_interval: int, receive_interval: int):
        """Start heartbeat thread"""
        if send_interval > 0:
            self._heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop,
                args=(send_interval / 1000.0,),
                daemon=True
            )
            self._heartbeat_thread.start()
    
    def _heartbeat_loop(self, interval: float):
        """Heartbeat sending loop"""
        while not self._stop_heartbeat.wait(interval):
            if self.state == ConnectionState.CONNECTED:
                # Send heartbeat (simulated)
                self.stats['heartbeats_sent'] += 1
                self.stats['last_activity'] = time.time()
    
    def simulate_message_received(self, destination: str, body: str, headers: Optional[Dict[str, str]] = None):
        """Simulate receiving a message (for demonstration)"""
        message_headers = {
            'destination': destination,
            'message-id': str(uuid.uuid4()),
            'subscription': '',
            'content-type': 'text/plain',
            'content-length': str(len(body.encode('utf-8')))
        }
        
        if headers:
            message_headers.update(headers)
        
        # Find matching subscription
        for sub_id, subscription in self.subscriptions.items():
            if subscription['destination'] == destination:
                message_headers['subscription'] = sub_id
                
                message_frame = StompFrame(StompCommand.MESSAGE, message_headers, body)
                
                # Handle acknowledgment
                if subscription['ack_mode'] != AckMode.AUTO:
                    with self._lock:
                        self.pending_acks[message_headers['message-id']] = message_frame
                
                # Call handler
                subscription['callback'](message_frame)
                
                self.stats['messages_received'] += 1
                self.stats['last_activity'] = time.time()
                
                print(f"📨 Received message from '{destination}': {body[:50]}...")
                break

def demonstrate_stomp_client():
    """Demonstrate STOMP client functionality"""
    print("=== STOMP Client Demonstration ===")
    
    # Create client configuration
    config = StompClientConfig(
        broker_host="localhost",
        broker_port=61613,
        heart_beat=(10000, 10000)
    )
    
    client = StompClient(config)
    
    # Message handlers
    def chat_handler(frame: StompFrame):
        print(f"💬 Chat message: {frame.body}")
    
    def order_handler(frame: StompFrame):
        try:
            order_data = json.loads(frame.body)
            print(f"📦 Order received: {order_data}")
            
            # Acknowledge if needed
            if frame.headers.get('subscription') in client.subscriptions:
                subscription = client.subscriptions[frame.headers['subscription']]
                if subscription['ack_mode'] != AckMode.AUTO:
                    client.ack(frame)
        except json.JSONDecodeError:
            print(f"❌ Invalid order JSON: {frame.body}")
            client.nack(frame)
    
    def error_handler(frame: StompFrame):
        print(f"❌ Error: {frame.body}")
    
    # Set handlers
    client.error_handler = error_handler
    
    try:
        # Connect to broker
        print(f"\n🔌 Connecting to STOMP broker...")
        if client.connect():
            print(f"✅ Connected successfully")
        else:
            print(f"❌ Connection failed")
            return
        
        # Subscribe to destinations
        print(f"\n📝 Setting up subscriptions...")
        
        chat_sub = client.subscribe("/topic/chat", chat_handler, AckMode.AUTO)
        order_sub = client.subscribe("/queue/orders", order_handler, AckMode.CLIENT)
        
        # Send messages
        print(f"\n📤 Sending messages...")
        
        # Send chat message
        client.send("/topic/chat", "Hello from STOMP client!", 
                   headers={'user': 'demo_user'})
        
        # Send order message
        order_data = {
            "order_id": "ORD-12345",
            "customer": "John Doe",
            "items": [
                {"product": "Widget", "quantity": 2, "price": 19.99}
            ],
            "total": 39.98
        }
        
        client.send("/queue/orders", json.dumps(order_data),
                   headers={'content-type': 'application/json'})
        
        # Test transactions
        print(f"\n🔄 Testing transactions...")
        
        tx_id = client.begin_transaction()
        
        # Send messages in transaction
        client.send("/topic/chat", "Message 1 in transaction", 
                   transaction=tx_id)
        client.send("/topic/chat", "Message 2 in transaction", 
                   transaction=tx_id)
        
        # Commit transaction
        client.commit_transaction(tx_id)
        
        # Simulate receiving messages
        print(f"\n📨 Simulating received messages...")
        
        client.simulate_message_received("/topic/chat", "Welcome to the chat!")
        client.simulate_message_received("/queue/orders", 
                                       '{"order_id": "ORD-67890", "status": "processing"}',
                                       headers={'content-type': 'application/json'})
        
        time.sleep(1)  # Let messages process
        
        # Display statistics
        print(f"\n📊 Client Statistics:")
        stats = client.get_stats()
        print(f"   State: {stats['state']}")
        print(f"   Session ID: {stats['session_id']}")
        print(f"   Subscriptions: {stats['subscriptions']}")
        print(f"   Messages sent: {stats['stats']['messages_sent']}")
        print(f"   Messages received: {stats['stats']['messages_received']}")
        
        # Unsubscribe and disconnect
        print(f"\n🔌 Cleaning up...")
        client.unsubscribe(chat_sub)
        client.unsubscribe(order_sub)
        
    finally:
        client.disconnect()
    
    print("\n🎯 STOMP Client demonstrates:")
    print("💡 Simple text-based messaging protocol")
    print("💡 Subscribe and publish to destinations")
    print("💡 Transaction support for atomic operations")
    print("💡 Message acknowledgment and rejection")
    print("💡 WebSocket-compatible frame format")

if __name__ == "__main__":
    demonstrate_stomp_client()
