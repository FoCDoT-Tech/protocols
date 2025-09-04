#!/usr/bin/env python3
"""
WebSocket Client Implementation and Communication Patterns
Demonstrates WebSocket client functionality, connection management, and messaging patterns
"""

import socket
import threading
import hashlib
import base64
import struct
import time
import json
import random
from datetime import datetime

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.host, self.port, self.path = self.parse_url(url)
        self.socket = None
        self.connected = False
        self.running = False
        self.message_handlers = {}
        self.ping_interval = 30  # seconds
        self.last_pong = time.time()
        
    def parse_url(self, url):
        """Parse WebSocket URL"""
        if url.startswith('ws://'):
            url = url[5:]
        elif url.startswith('wss://'):
            url = url[6:]
        
        if '/' in url:
            host_port, path = url.split('/', 1)
            path = '/' + path
        else:
            host_port = url
            path = '/'
        
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host = host_port
            port = 80
        
        return host, port, path
    
    def connect(self):
        """Connect to WebSocket server"""
        print(f"=== WebSocket Client Connection ===")
        print(f"Connecting to: {self.url}")
        print(f"Host: {self.host}:{self.port}")
        print(f"Path: {self.path}")
        
        try:
            # Create TCP connection
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print("✓ TCP connection established")
            
            # Perform WebSocket handshake
            if self.perform_handshake():
                self.connected = True
                self.running = True
                print("✓ WebSocket connection established")
                
                # Start message handling thread
                self.message_thread = threading.Thread(target=self.handle_messages)
                self.message_thread.daemon = True
                self.message_thread.start()
                
                # Start ping thread
                self.ping_thread = threading.Thread(target=self.ping_loop)
                self.ping_thread.daemon = True
                self.ping_thread.start()
                
                return True
            else:
                print("❌ WebSocket handshake failed")
                self.socket.close()
                return False
                
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def perform_handshake(self):
        """Perform WebSocket handshake"""
        print("\n=== Client Handshake Process ===")
        
        # Generate WebSocket key
        key_bytes = bytes([random.randint(0, 255) for _ in range(16)])
        websocket_key = base64.b64encode(key_bytes).decode('utf-8')
        
        print(f"1. Generated WebSocket key: {websocket_key}")
        
        # Create handshake request
        request = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {websocket_key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        
        print("2. Sending handshake request:")
        print(f"   GET {self.path} HTTP/1.1")
        print(f"   Upgrade: websocket")
        
        # Send request
        self.socket.send(request.encode('utf-8'))
        
        # Receive response
        response = self.socket.recv(1024).decode('utf-8')
        print("3. Received handshake response:")
        
        # Parse response
        lines = response.split('\r\n')
        status_line = lines[0]
        
        if '101 Switching Protocols' not in status_line:
            print(f"   ❌ Invalid status: {status_line}")
            return False
        
        print(f"   ✓ Status: {status_line}")
        
        # Parse headers
        headers = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        # Verify response key
        expected_key = self.generate_expected_key(websocket_key)
        received_key = headers.get('sec-websocket-accept', '')
        
        if received_key != expected_key:
            print(f"   ❌ Invalid response key")
            print(f"   Expected: {expected_key}")
            print(f"   Received: {received_key}")
            return False
        
        print(f"   ✓ Response key verified: {received_key}")
        print("   ✓ Protocol switched to WebSocket")
        
        return True
    
    def generate_expected_key(self, websocket_key):
        """Generate expected response key"""
        magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        combined = websocket_key + magic_string
        sha1_hash = hashlib.sha1(combined.encode('utf-8')).digest()
        return base64.b64encode(sha1_hash).decode('utf-8')
    
    def handle_messages(self):
        """Handle incoming messages"""
        while self.running and self.connected:
            try:
                frame = self.read_frame()
                if frame is None:
                    break
                
                opcode = frame['opcode']
                payload = frame['payload']
                
                if opcode == 0x1:  # Text frame
                    message = payload.decode('utf-8')
                    self.on_message(message)
                    
                elif opcode == 0x2:  # Binary frame
                    self.on_binary(payload)
                    
                elif opcode == 0x8:  # Close frame
                    print("📪 Received close frame")
                    self.close()
                    break
                    
                elif opcode == 0x9:  # Ping frame
                    print("🏓 Received ping")
                    self.send_pong(payload)
                    
                elif opcode == 0xA:  # Pong frame
                    print("🏓 Received pong")
                    self.last_pong = time.time()
                    
            except Exception as e:
                print(f"Message handling error: {e}")
                break
        
        self.connected = False
    
    def read_frame(self):
        """Read WebSocket frame"""
        try:
            # Read first 2 bytes
            data = self.socket.recv(2)
            if len(data) < 2:
                return None
            
            byte1, byte2 = struct.unpack('!BB', data)
            
            fin = (byte1 >> 7) & 1
            opcode = byte1 & 0x0F
            masked = (byte2 >> 7) & 1
            payload_length = byte2 & 0x7F
            
            # Extended payload length
            if payload_length == 126:
                data = self.socket.recv(2)
                payload_length = struct.unpack('!H', data)[0]
            elif payload_length == 127:
                data = self.socket.recv(8)
                payload_length = struct.unpack('!Q', data)[0]
            
            # Masking key (server frames should not be masked)
            if masked:
                mask = self.socket.recv(4)
            else:
                mask = None
            
            # Payload
            payload = b''
            if payload_length > 0:
                payload = self.socket.recv(payload_length)
                
                if masked and mask:
                    payload = bytes(payload[i] ^ mask[i % 4] for i in range(len(payload)))
            
            return {
                'fin': fin,
                'opcode': opcode,
                'payload': payload
            }
            
        except Exception as e:
            print(f"Frame reading error: {e}")
            return None
    
    def send_message(self, message):
        """Send text message"""
        if not self.connected:
            return False
        
        try:
            frame = self.create_frame(0x1, message.encode('utf-8'), masked=True)
            self.socket.send(frame)
            print(f"📤 Sent: {message}")
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def send_binary(self, data):
        """Send binary data"""
        if not self.connected:
            return False
        
        try:
            frame = self.create_frame(0x2, data, masked=True)
            self.socket.send(frame)
            print(f"📦 Sent binary: {len(data)} bytes")
            return True
        except Exception as e:
            print(f"Binary send error: {e}")
            return False
    
    def send_ping(self, data=b''):
        """Send ping frame"""
        if not self.connected:
            return False
        
        try:
            frame = self.create_frame(0x9, data, masked=True)
            self.socket.send(frame)
            print("🏓 Sent ping")
            return True
        except Exception as e:
            print(f"Ping send error: {e}")
            return False
    
    def send_pong(self, data=b''):
        """Send pong frame"""
        if not self.connected:
            return False
        
        try:
            frame = self.create_frame(0xA, data, masked=True)
            self.socket.send(frame)
            print("🏓 Sent pong")
            return True
        except Exception as e:
            print(f"Pong send error: {e}")
            return False
    
    def create_frame(self, opcode, payload, masked=False):
        """Create WebSocket frame"""
        frame = bytearray()
        
        # First byte: FIN (1) + RSV (000) + Opcode (4 bits)
        frame.append(0x80 | opcode)
        
        # Payload length and mask bit
        payload_length = len(payload)
        mask_bit = 0x80 if masked else 0x00
        
        if payload_length < 126:
            frame.append(mask_bit | payload_length)
        elif payload_length < 65536:
            frame.append(mask_bit | 126)
            frame.extend(struct.pack('!H', payload_length))
        else:
            frame.append(mask_bit | 127)
            frame.extend(struct.pack('!Q', payload_length))
        
        # Masking key (client frames should be masked)
        if masked:
            mask = bytes([random.randint(0, 255) for _ in range(4)])
            frame.extend(mask)
            
            # Mask payload
            masked_payload = bytes(payload[i] ^ mask[i % 4] for i in range(len(payload)))
            frame.extend(masked_payload)
        else:
            frame.extend(payload)
        
        return bytes(frame)
    
    def ping_loop(self):
        """Send periodic pings"""
        while self.running and self.connected:
            time.sleep(self.ping_interval)
            
            if self.connected:
                # Check if we received pong recently
                if time.time() - self.last_pong > self.ping_interval * 2:
                    print("⚠️ No pong received, connection may be dead")
                    self.close()
                    break
                
                self.send_ping()
    
    def close(self):
        """Close WebSocket connection"""
        if self.connected:
            print("📪 Closing WebSocket connection")
            
            # Send close frame
            try:
                close_frame = self.create_frame(0x8, b'', masked=True)
                self.socket.send(close_frame)
            except:
                pass
            
            self.connected = False
            self.running = False
            
            if self.socket:
                self.socket.close()
    
    def on_message(self, message):
        """Handle received text message"""
        print(f"📨 Received: {message}")
        
        try:
            data = json.loads(message)
            msg_type = data.get('type', 'unknown')
            
            if msg_type == 'welcome':
                print(f"🎉 Welcome message: {data.get('message', '')}")
            elif msg_type == 'echo_response':
                print(f"🔄 Echo response: {data.get('original_message', '')}")
            elif msg_type == 'broadcast':
                print(f"📡 Broadcast from {data.get('from', 'unknown')}: {data.get('message', '')}")
            elif msg_type == 'pong':
                print(f"🏓 Server pong received")
                
        except json.JSONDecodeError:
            # Handle plain text
            print(f"💬 Plain text: {message}")
    
    def on_binary(self, data):
        """Handle received binary data"""
        print(f"📦 Received binary: {len(data)} bytes")

def simulate_websocket_communication():
    """Simulate WebSocket client communication patterns"""
    print("=== WebSocket Communication Patterns ===")
    
    # Simulate different message types
    patterns = [
        {
            'name': 'Echo Pattern',
            'description': 'Send message and receive echo',
            'message': json.dumps({
                'type': 'echo',
                'message': 'Hello WebSocket!',
                'timestamp': datetime.now().isoformat()
            })
        },
        {
            'name': 'Broadcast Pattern',
            'description': 'Send message to all clients',
            'message': json.dumps({
                'type': 'broadcast',
                'message': 'Broadcasting to all clients',
                'timestamp': datetime.now().isoformat()
            })
        },
        {
            'name': 'Ping Pattern',
            'description': 'Application-level ping',
            'message': json.dumps({
                'type': 'ping',
                'timestamp': datetime.now().isoformat()
            })
        },
        {
            'name': 'Real-time Data',
            'description': 'Simulated sensor data',
            'message': json.dumps({
                'type': 'sensor_data',
                'temperature': 23.5,
                'humidity': 65.2,
                'timestamp': datetime.now().isoformat()
            })
        }
    ]
    
    for pattern in patterns:
        print(f"\n--- {pattern['name']} ---")
        print(f"Description: {pattern['description']}")
        print(f"Message: {pattern['message']}")
        
        # Simulate frame creation
        client = WebSocketClient('ws://localhost:8080')
        frame = client.create_frame(0x1, pattern['message'].encode('utf-8'), masked=True)
        print(f"Frame size: {len(frame)} bytes")
    
    return patterns

def demonstrate_websocket_features():
    """Demonstrate key WebSocket features"""
    print(f"\n=== WebSocket Features Demonstration ===")
    
    features = [
        {
            'feature': 'Full-Duplex Communication',
            'description': 'Both client and server can send messages at any time',
            'benefit': 'Real-time bidirectional data exchange'
        },
        {
            'feature': 'Low Latency',
            'description': 'No HTTP overhead for each message',
            'benefit': 'Minimal delay for real-time applications'
        },
        {
            'feature': 'Persistent Connection',
            'description': 'Single TCP connection for entire session',
            'benefit': 'Reduced connection overhead and state preservation'
        },
        {
            'feature': 'Binary and Text Support',
            'description': 'Can send both text and binary data',
            'benefit': 'Flexible data transmission for different use cases'
        },
        {
            'feature': 'Control Frames',
            'description': 'Ping/pong for keepalive, close for graceful termination',
            'benefit': 'Connection health monitoring and clean shutdown'
        },
        {
            'feature': 'Frame-based Protocol',
            'description': 'Efficient binary framing with minimal overhead',
            'benefit': 'Better performance than HTTP for frequent messages'
        }
    ]
    
    for feature in features:
        print(f"\n{feature['feature']}:")
        print(f"  Description: {feature['description']}")
        print(f"  Benefit: {feature['benefit']}")
    
    return features

def compare_websocket_vs_http():
    """Compare WebSocket vs HTTP for real-time scenarios"""
    print(f"\n=== WebSocket vs HTTP Comparison ===")
    
    scenarios = [
        {
            'scenario': 'Chat Application (100 messages/minute)',
            'http_requests': 100,
            'http_overhead': 100 * 800,  # ~800 bytes per HTTP request
            'websocket_frames': 100,
            'websocket_overhead': 100 * 6,  # ~6 bytes per WebSocket frame
            'latency_improvement': '50-90%'
        },
        {
            'scenario': 'Real-time Trading (1000 updates/second)',
            'http_requests': 60000,  # per minute
            'http_overhead': 60000 * 800,
            'websocket_frames': 60000,
            'websocket_overhead': 60000 * 6,
            'latency_improvement': '80-95%'
        },
        {
            'scenario': 'Live Gaming (60 FPS updates)',
            'http_requests': 3600,  # per minute
            'http_overhead': 3600 * 800,
            'websocket_frames': 3600,
            'websocket_overhead': 3600 * 6,
            'latency_improvement': '70-90%'
        }
    ]
    
    print(f"{'Scenario':<30} {'HTTP Overhead':<15} {'WebSocket Overhead':<20} {'Savings'}")
    print("-" * 80)
    
    for scenario in scenarios:
        http_kb = scenario['http_overhead'] / 1024
        ws_kb = scenario['websocket_overhead'] / 1024
        savings = ((scenario['http_overhead'] - scenario['websocket_overhead']) / scenario['http_overhead']) * 100
        
        print(f"{scenario['scenario'][:29]:<30} {http_kb:.1f} KB{'':<10} {ws_kb:.1f} KB{'':<15} {savings:.1f}%")
    
    print(f"\nKey Benefits:")
    print(f"  • Bandwidth savings: 90-99% reduction in overhead")
    print(f"  • Latency improvement: 50-95% faster message delivery")
    print(f"  • Server efficiency: Reduced connection management overhead")
    print(f"  • Real-time capability: True bidirectional communication")
    
    return scenarios

if __name__ == "__main__":
    # Simulate WebSocket client functionality
    client = WebSocketClient('ws://localhost:8080/chat')
    
    # Demonstrate communication patterns
    patterns = simulate_websocket_communication()
    
    # Show WebSocket features
    features = demonstrate_websocket_features()
    
    # Compare with HTTP
    comparison = compare_websocket_vs_http()
    
    print(f"\n=== WebSocket Client Summary ===")
    print(f"URL: {client.url}")
    print(f"Host: {client.host}:{client.port}")
    print(f"Path: {client.path}")
    print(f"Features: Full-duplex, low-latency, persistent connection")
    print(f"Use cases: Real-time chat, gaming, trading, live data feeds")
