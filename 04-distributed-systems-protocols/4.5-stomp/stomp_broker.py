#!/usr/bin/env python3
"""
STOMP Broker Simulation
Simple Text Oriented Messaging Protocol broker implementation.
"""

import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Callable, Any
import uuid
from collections import defaultdict, deque

class StompCommand(Enum):
    CONNECT = "CONNECT"
    CONNECTED = "CONNECTED"
    SEND = "SEND"
    SUBSCRIBE = "SUBSCRIBE"
    UNSUBSCRIBE = "UNSUBSCRIBE"
    ACK = "ACK"
    NACK = "NACK"
    BEGIN = "BEGIN"
    COMMIT = "COMMIT"
    ABORT = "ABORT"
    DISCONNECT = "DISCONNECT"
    MESSAGE = "MESSAGE"
    RECEIPT = "RECEIPT"
    ERROR = "ERROR"

class AckMode(Enum):
    AUTO = "auto"
    CLIENT = "client"
    CLIENT_INDIVIDUAL = "client-individual"

@dataclass
class StompFrame:
    command: StompCommand
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    
    def to_string(self) -> str:
        """Convert frame to STOMP wire format"""
        lines = [self.command.value]
        
        for key, value in self.headers.items():
            lines.append(f"{key}:{value}")
        
        lines.append("")  # Empty line before body
        lines.append(self.body)
        
        return "\n".join(lines) + "\x00"  # NULL terminator
    
    @classmethod
    def from_string(cls, data: str) -> 'StompFrame':
        """Parse STOMP frame from wire format"""
        if data.endswith('\x00'):
            data = data[:-1]  # Remove NULL terminator
        
        lines = data.split('\n')
        
        if not lines:
            raise ValueError("Empty frame")
        
        command = StompCommand(lines[0])
        headers = {}
        body_start = 1
        
        # Parse headers
        for i, line in enumerate(lines[1:], 1):
            if line == "":  # Empty line indicates start of body
                body_start = i + 1
                break
            
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key] = value
        
        # Parse body
        body = "\n".join(lines[body_start:]) if body_start < len(lines) else ""
        
        return cls(command=command, headers=headers, body=body)

@dataclass
class Subscription:
    id: str
    destination: str
    ack_mode: AckMode
    client_id: str
    callback: Callable[[StompFrame], None]

@dataclass
class Transaction:
    id: str
    client_id: str
    messages: List[StompFrame] = field(default_factory=list)
    receipts: List[str] = field(default_factory=list)

class StompClient:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.connected = False
        self.subscriptions: Dict[str, Subscription] = {}
        self.pending_acks: Dict[str, StompFrame] = {}
        self.session = str(uuid.uuid4())
        self.heart_beat = (0, 0)  # (send, receive) intervals in ms
        self.last_activity = time.time()
        
        # Statistics
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'subscriptions_count': 0,
            'transactions_count': 0,
            'connect_time': 0
        }

class StompBroker:
    def __init__(self, host: str = "localhost", port: int = 61613):
        self.host = host
        self.port = port
        
        # Client management
        self.clients: Dict[str, StompClient] = {}
        self.destinations: Dict[str, List[Subscription]] = defaultdict(list)
        self.transactions: Dict[str, Transaction] = {}
        
        # Message storage
        self.message_queue: Dict[str, deque] = defaultdict(deque)
        self.message_id_counter = 1
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_processed': 0,
            'destinations_count': 0,
            'start_time': time.time()
        }
        
        self.running = False
        self._lock = threading.Lock()
    
    def start(self):
        """Start the STOMP broker"""
        self.running = True
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()
        print(f"🚀 STOMP Broker started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the STOMP broker"""
        self.running = False
        print("🛑 STOMP Broker stopped")
    
    def process_frame(self, client_id: str, frame: StompFrame) -> Optional[StompFrame]:
        """Process incoming STOMP frame"""
        with self._lock:
            if frame.command == StompCommand.CONNECT:
                return self._handle_connect(client_id, frame)
            elif frame.command == StompCommand.SEND:
                return self._handle_send(client_id, frame)
            elif frame.command == StompCommand.SUBSCRIBE:
                return self._handle_subscribe(client_id, frame)
            elif frame.command == StompCommand.UNSUBSCRIBE:
                return self._handle_unsubscribe(client_id, frame)
            elif frame.command == StompCommand.ACK:
                return self._handle_ack(client_id, frame)
            elif frame.command == StompCommand.NACK:
                return self._handle_nack(client_id, frame)
            elif frame.command == StompCommand.BEGIN:
                return self._handle_begin(client_id, frame)
            elif frame.command == StompCommand.COMMIT:
                return self._handle_commit(client_id, frame)
            elif frame.command == StompCommand.ABORT:
                return self._handle_abort(client_id, frame)
            elif frame.command == StompCommand.DISCONNECT:
                return self._handle_disconnect(client_id, frame)
            else:
                return self._create_error_frame(f"Unknown command: {frame.command}")
    
    def _handle_connect(self, client_id: str, frame: StompFrame) -> StompFrame:
        """Handle CONNECT frame"""
        # Create or update client
        if client_id not in self.clients:
            self.clients[client_id] = StompClient(client_id)
            self.stats['total_connections'] += 1
        
        client = self.clients[client_id]
        client.connected = True
        client.stats['connect_time'] = time.time()
        
        # Parse heart-beat header
        if 'heart-beat' in frame.headers:
            try:
                send_interval, receive_interval = map(int, frame.headers['heart-beat'].split(','))
                client.heart_beat = (send_interval, receive_interval)
            except ValueError:
                pass
        
        self.stats['active_connections'] = sum(1 for c in self.clients.values() if c.connected)
        
        print(f"🔌 Client '{client_id}' connected")
        
        # Send CONNECTED frame
        response_headers = {
            'version': '1.2',
            'session': client.session,
            'server': 'STOMP-Broker/1.0',
            'heart-beat': '10000,10000'  # 10 second intervals
        }
        
        return StompFrame(StompCommand.CONNECTED, response_headers)
    
    def _handle_send(self, client_id: str, frame: StompFrame) -> Optional[StompFrame]:
        """Handle SEND frame"""
        if client_id not in self.clients or not self.clients[client_id].connected:
            return self._create_error_frame("Not connected")
        
        destination = frame.headers.get('destination')
        if not destination:
            return self._create_error_frame("Missing destination header")
        
        # Check for transaction
        transaction_id = frame.headers.get('transaction')
        if transaction_id:
            if transaction_id not in self.transactions:
                return self._create_error_frame(f"Unknown transaction: {transaction_id}")
            
            # Add to transaction
            self.transactions[transaction_id].messages.append(frame)
            print(f"📝 Message added to transaction '{transaction_id}'")
            return None
        
        # Send message immediately
        return self._deliver_message(client_id, frame)
    
    def _handle_subscribe(self, client_id: str, frame: StompFrame) -> Optional[StompFrame]:
        """Handle SUBSCRIBE frame"""
        if client_id not in self.clients or not self.clients[client_id].connected:
            return self._create_error_frame("Not connected")
        
        destination = frame.headers.get('destination')
        subscription_id = frame.headers.get('id', str(uuid.uuid4()))
        ack_mode = AckMode(frame.headers.get('ack', 'auto'))
        
        if not destination:
            return self._create_error_frame("Missing destination header")
        
        client = self.clients[client_id]
        
        # Create subscription
        def message_callback(message_frame: StompFrame):
            self._send_message_to_client(client_id, message_frame)
        
        subscription = Subscription(
            id=subscription_id,
            destination=destination,
            ack_mode=ack_mode,
            client_id=client_id,
            callback=message_callback
        )
        
        # Add to client and destination
        client.subscriptions[subscription_id] = subscription
        self.destinations[destination].append(subscription)
        
        client.stats['subscriptions_count'] = len(client.subscriptions)
        self.stats['destinations_count'] = len(self.destinations)
        
        print(f"📝 Client '{client_id}' subscribed to '{destination}' (id: {subscription_id})")
        
        # Send receipt if requested
        if 'receipt' in frame.headers:
            return StompFrame(StompCommand.RECEIPT, {'receipt-id': frame.headers['receipt']})
        
        return None
    
    def _handle_unsubscribe(self, client_id: str, frame: StompFrame) -> Optional[StompFrame]:
        """Handle UNSUBSCRIBE frame"""
        if client_id not in self.clients:
            return self._create_error_frame("Not connected")
        
        subscription_id = frame.headers.get('id')
        if not subscription_id:
            return self._create_error_frame("Missing id header")
        
        client = self.clients[client_id]
        
        if subscription_id in client.subscriptions:
            subscription = client.subscriptions[subscription_id]
            
            # Remove from destination
            self.destinations[subscription.destination] = [
                sub for sub in self.destinations[subscription.destination]
                if sub.id != subscription_id
            ]
            
            # Remove from client
            del client.subscriptions[subscription_id]
            
            client.stats['subscriptions_count'] = len(client.subscriptions)
            
            print(f"📝 Client '{client_id}' unsubscribed from '{subscription.destination}'")
        
        # Send receipt if requested
        if 'receipt' in frame.headers:
            return StompFrame(StompCommand.RECEIPT, {'receipt-id': frame.headers['receipt']})
        
        return None
    
    def _handle_ack(self, client_id: str, frame: StompFrame) -> Optional[StompFrame]:
        """Handle ACK frame"""
        if client_id not in self.clients:
            return self._create_error_frame("Not connected")
        
        message_id = frame.headers.get('id') or frame.headers.get('message-id')
        if not message_id:
            return self._create_error_frame("Missing message id")
        
        client = self.clients[client_id]
        
        if message_id in client.pending_acks:
            del client.pending_acks[message_id]
            print(f"✅ Client '{client_id}' acknowledged message '{message_id}'")
        
        return None
    
    def _handle_nack(self, client_id: str, frame: StompFrame) -> Optional[StompFrame]:
        """Handle NACK frame"""
        if client_id not in self.clients:
            return self._create_error_frame("Not connected")
        
        message_id = frame.headers.get('id') or frame.headers.get('message-id')
        if not message_id:
            return self._create_error_frame("Missing message id")
        
        client = self.clients[client_id]
        
        if message_id in client.pending_acks:
            # Requeue message or handle rejection
            del client.pending_acks[message_id]
            print(f"❌ Client '{client_id}' rejected message '{message_id}'")
        
        return None
    
    def _handle_begin(self, client_id: str, frame: StompFrame) -> Optional[StompFrame]:
        """Handle BEGIN frame"""
        if client_id not in self.clients:
            return self._create_error_frame("Not connected")
        
        transaction_id = frame.headers.get('transaction')
        if not transaction_id:
            return self._create_error_frame("Missing transaction header")
        
        if transaction_id in self.transactions:
            return self._create_error_frame(f"Transaction '{transaction_id}' already exists")
        
        # Create transaction
        transaction = Transaction(id=transaction_id, client_id=client_id)
        self.transactions[transaction_id] = transaction
        
        client = self.clients[client_id]
        client.stats['transactions_count'] += 1
        
        print(f"🔄 Transaction '{transaction_id}' started for client '{client_id}'")
        
        # Send receipt if requested
        if 'receipt' in frame.headers:
            return StompFrame(StompCommand.RECEIPT, {'receipt-id': frame.headers['receipt']})
        
        return None
    
    def _handle_commit(self, client_id: str, frame: StompFrame) -> Optional[StompFrame]:
        """Handle COMMIT frame"""
        if client_id not in self.clients:
            return self._create_error_frame("Not connected")
        
        transaction_id = frame.headers.get('transaction')
        if not transaction_id:
            return self._create_error_frame("Missing transaction header")
        
        if transaction_id not in self.transactions:
            return self._create_error_frame(f"Unknown transaction: {transaction_id}")
        
        transaction = self.transactions[transaction_id]
        
        if transaction.client_id != client_id:
            return self._create_error_frame("Transaction belongs to different client")
        
        # Commit all messages in transaction
        for message_frame in transaction.messages:
            self._deliver_message(client_id, message_frame)
        
        # Clean up transaction
        del self.transactions[transaction_id]
        
        print(f"✅ Transaction '{transaction_id}' committed ({len(transaction.messages)} messages)")
        
        # Send receipt if requested
        if 'receipt' in frame.headers:
            return StompFrame(StompCommand.RECEIPT, {'receipt-id': frame.headers['receipt']})
        
        return None
    
    def _handle_abort(self, client_id: str, frame: StompFrame) -> Optional[StompFrame]:
        """Handle ABORT frame"""
        if client_id not in self.clients:
            return self._create_error_frame("Not connected")
        
        transaction_id = frame.headers.get('transaction')
        if not transaction_id:
            return self._create_error_frame("Missing transaction header")
        
        if transaction_id not in self.transactions:
            return self._create_error_frame(f"Unknown transaction: {transaction_id}")
        
        transaction = self.transactions[transaction_id]
        
        if transaction.client_id != client_id:
            return self._create_error_frame("Transaction belongs to different client")
        
        # Abort transaction - discard all messages
        message_count = len(transaction.messages)
        del self.transactions[transaction_id]
        
        print(f"❌ Transaction '{transaction_id}' aborted ({message_count} messages discarded)")
        
        # Send receipt if requested
        if 'receipt' in frame.headers:
            return StompFrame(StompCommand.RECEIPT, {'receipt-id': frame.headers['receipt']})
        
        return None
    
    def _handle_disconnect(self, client_id: str, frame: StompFrame) -> Optional[StompFrame]:
        """Handle DISCONNECT frame"""
        if client_id in self.clients:
            client = self.clients[client_id]
            client.connected = False
            
            # Clean up subscriptions
            for subscription in client.subscriptions.values():
                self.destinations[subscription.destination] = [
                    sub for sub in self.destinations[subscription.destination]
                    if sub.client_id != client_id
                ]
            
            self.stats['active_connections'] = sum(1 for c in self.clients.values() if c.connected)
            
            print(f"🔌 Client '{client_id}' disconnected")
        
        # Send receipt if requested
        if 'receipt' in frame.headers:
            return StompFrame(StompCommand.RECEIPT, {'receipt-id': frame.headers['receipt']})
        
        return None
    
    def _deliver_message(self, sender_id: str, frame: StompFrame) -> Optional[StompFrame]:
        """Deliver message to subscribers"""
        destination = frame.headers.get('destination')
        if not destination:
            return self._create_error_frame("Missing destination")
        
        subscribers = self.destinations.get(destination, [])
        
        if not subscribers:
            print(f"⚠️  No subscribers for destination '{destination}'")
            return None
        
        # Create message frame
        message_id = str(self.message_id_counter)
        self.message_id_counter += 1
        
        message_headers = {
            'destination': destination,
            'message-id': message_id,
            'subscription': '',  # Will be set per subscriber
            'content-type': frame.headers.get('content-type', 'text/plain'),
            'content-length': str(len(frame.body.encode('utf-8')))
        }
        
        # Copy custom headers
        for key, value in frame.headers.items():
            if key not in ['destination', 'transaction']:
                message_headers[key] = value
        
        delivered = 0
        for subscription in subscribers:
            # Skip sender if it's the same client
            if subscription.client_id == sender_id:
                continue
            
            # Set subscription-specific headers
            message_headers['subscription'] = subscription.id
            
            message_frame = StompFrame(
                command=StompCommand.MESSAGE,
                headers=message_headers.copy(),
                body=frame.body
            )
            
            # Handle acknowledgment mode
            if subscription.ack_mode != AckMode.AUTO:
                client = self.clients[subscription.client_id]
                client.pending_acks[message_id] = message_frame
            
            # Deliver message
            subscription.callback(message_frame)
            delivered += 1
        
        self.stats['messages_processed'] += 1
        
        print(f"📤 Message delivered to {delivered} subscribers on '{destination}'")
        
        # Send receipt if requested
        if 'receipt' in frame.headers:
            return StompFrame(StompCommand.RECEIPT, {'receipt-id': frame.headers['receipt']})
        
        return None
    
    def _send_message_to_client(self, client_id: str, message_frame: StompFrame):
        """Send message frame to specific client"""
        if client_id in self.clients:
            client = self.clients[client_id]
            client.stats['messages_received'] += 1
            print(f"📨 Sent message to client '{client_id}': {message_frame.headers.get('destination')}")
    
    def _create_error_frame(self, message: str) -> StompFrame:
        """Create ERROR frame"""
        return StompFrame(
            command=StompCommand.ERROR,
            headers={'message': message},
            body=message
        )
    
    def _heartbeat_loop(self):
        """Heartbeat monitoring loop"""
        while self.running:
            try:
                current_time = time.time()
                
                # Check for inactive clients
                inactive_clients = []
                for client_id, client in self.clients.items():
                    if client.connected and client.heart_beat[1] > 0:
                        timeout = client.heart_beat[1] / 1000.0 * 2  # 2x receive interval
                        if current_time - client.last_activity > timeout:
                            inactive_clients.append(client_id)
                
                # Disconnect inactive clients
                for client_id in inactive_clients:
                    print(f"💔 Client '{client_id}' heartbeat timeout")
                    self._handle_disconnect(client_id, StompFrame(StompCommand.DISCONNECT))
                
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"❌ Heartbeat loop error: {e}")
    
    def get_broker_stats(self) -> Dict:
        """Get broker statistics"""
        with self._lock:
            return {
                'uptime': time.time() - self.stats['start_time'],
                'total_connections': self.stats['total_connections'],
                'active_connections': self.stats['active_connections'],
                'destinations': len(self.destinations),
                'active_transactions': len(self.transactions),
                'messages_processed': self.stats['messages_processed'],
                'client_stats': {
                    client_id: client.stats for client_id, client in self.clients.items()
                    if client.connected
                }
            }

def demonstrate_stomp_broker():
    """Demonstrate STOMP broker functionality"""
    print("=== STOMP Broker Demonstration ===")
    
    broker = StompBroker()
    broker.start()
    
    try:
        # Simulate client connections
        print(f"\n🔌 Simulating client connections...")
        
        # Client 1: Producer
        connect_frame = StompFrame(
            command=StompCommand.CONNECT,
            headers={'accept-version': '1.2', 'host': 'localhost'}
        )
        response = broker.process_frame("producer_client", connect_frame)
        print(f"Producer connected: {response.command}")
        
        # Client 2: Consumer
        response = broker.process_frame("consumer_client", connect_frame)
        print(f"Consumer connected: {response.command}")
        
        # Subscribe to topic
        subscribe_frame = StompFrame(
            command=StompCommand.SUBSCRIBE,
            headers={'destination': '/topic/chat', 'id': 'sub-1', 'ack': 'client'}
        )
        broker.process_frame("consumer_client", subscribe_frame)
        
        # Subscribe to queue
        subscribe_frame2 = StompFrame(
            command=StompCommand.SUBSCRIBE,
            headers={'destination': '/queue/orders', 'id': 'sub-2', 'ack': 'auto'}
        )
        broker.process_frame("consumer_client", subscribe_frame2)
        
        # Send messages
        print(f"\n📤 Sending messages...")
        
        # Send to topic
        send_frame = StompFrame(
            command=StompCommand.SEND,
            headers={'destination': '/topic/chat', 'content-type': 'text/plain'},
            body='Hello, chat room!'
        )
        broker.process_frame("producer_client", send_frame)
        
        # Send to queue
        send_frame2 = StompFrame(
            command=StompCommand.SEND,
            headers={'destination': '/queue/orders', 'content-type': 'application/json'},
            body='{"order_id": 12345, "item": "Widget", "quantity": 2}'
        )
        broker.process_frame("producer_client", send_frame2)
        
        # Test transactions
        print(f"\n🔄 Testing transactions...")
        
        # Begin transaction
        begin_frame = StompFrame(
            command=StompCommand.BEGIN,
            headers={'transaction': 'tx-1'}
        )
        broker.process_frame("producer_client", begin_frame)
        
        # Send message in transaction
        send_frame3 = StompFrame(
            command=StompCommand.SEND,
            headers={
                'destination': '/topic/chat',
                'transaction': 'tx-1',
                'content-type': 'text/plain'
            },
            body='This is a transactional message'
        )
        broker.process_frame("producer_client", send_frame3)
        
        # Commit transaction
        commit_frame = StompFrame(
            command=StompCommand.COMMIT,
            headers={'transaction': 'tx-1'}
        )
        broker.process_frame("producer_client", commit_frame)
        
        time.sleep(1)  # Let messages process
        
        # Display statistics
        print(f"\n📊 Broker Statistics:")
        stats = broker.get_broker_stats()
        print(f"   Uptime: {stats['uptime']:.1f}s")
        print(f"   Active connections: {stats['active_connections']}")
        print(f"   Destinations: {stats['destinations']}")
        print(f"   Messages processed: {stats['messages_processed']}")
        
        # Disconnect clients
        disconnect_frame = StompFrame(command=StompCommand.DISCONNECT)
        broker.process_frame("producer_client", disconnect_frame)
        broker.process_frame("consumer_client", disconnect_frame)
    
    finally:
        broker.stop()
    
    print("\n🎯 STOMP Broker demonstrates:")
    print("💡 Simple text-based messaging protocol")
    print("💡 Frame-based communication with headers")
    print("💡 Topic and queue destination types")
    print("💡 Transaction support for atomic operations")
    print("💡 Multiple acknowledgment modes")

if __name__ == "__main__":
    demonstrate_stomp_broker()
