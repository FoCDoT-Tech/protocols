#!/usr/bin/env python3
"""
WebSocket Server Implementation and Message Handling
Demonstrates WebSocket server functionality, handshake process, and real-time communication
"""

import socket
import threading
import hashlib
import base64
import struct
import time
import json
from datetime import datetime

class WebSocketServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.socket = None
        self.clients = {}
        self.running = False
        self.message_handlers = {}
        self.connection_count = 0
        
        # WebSocket constants
        self.WEBSOCKET_MAGIC_STRING = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        
    def start(self):
        """Start the WebSocket server"""
        print(f"=== WebSocket Server Starting ===")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print(f"✓ Server listening on ws://{self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    print(f"New connection from {address}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        print("Socket error occurred")
                    break
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the WebSocket server"""
        print("Stopping WebSocket server...")
        self.running = False
        if self.socket:
            self.socket.close()
    
    def handle_client(self, client_socket, address):
        """Handle individual client connection"""
        try:
            # Perform WebSocket handshake
            if self.perform_handshake(client_socket):
                self.connection_count += 1
                client_id = f"client_{self.connection_count}"
                
                self.clients[client_id] = {
                    'socket': client_socket,
                    'address': address,
                    'connected_at': datetime.now(),
                    'messages_sent': 0,
                    'messages_received': 0
                }
                
                print(f"✓ WebSocket handshake completed for {client_id}")
                self.on_client_connected(client_id)
                
                # Handle messages
                self.handle_messages(client_id)
            else:
                print(f"❌ WebSocket handshake failed for {address}")
                client_socket.close()
                
        except Exception as e:
            print(f"Client handling error: {e}")
        finally:
            if client_id in self.clients:
                self.on_client_disconnected(client_id)
                del self.clients[client_id]
            client_socket.close()
    
    def perform_handshake(self, client_socket):
        """Perform WebSocket handshake"""
        print("=== WebSocket Handshake Process ===")
        
        # Receive HTTP request
        request = client_socket.recv(1024).decode('utf-8')
        print("1. Received HTTP upgrade request:")
        
        # Parse request headers
        headers = {}
        lines = request.split('\r\n')
        
        if not lines[0].startswith('GET'):
            return False
        
        print(f"   {lines[0]}")
        
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        # Validate WebSocket headers
        required_headers = {
            'upgrade': 'websocket',
            'connection': 'upgrade',
            'sec-websocket-version': '13'
        }
        
        for header, expected_value in required_headers.items():
            if header not in headers:
                print(f"   ❌ Missing header: {header}")
                return False
            if headers[header].lower() != expected_value:
                print(f"   ❌ Invalid {header}: {headers[header]}")
                return False
        
        if 'sec-websocket-key' not in headers:
            print("   ❌ Missing Sec-WebSocket-Key")
            return False
        
        print("   ✓ All required headers present")
        
        # Generate response key
        websocket_key = headers['sec-websocket-key']
        response_key = self.generate_response_key(websocket_key)
        
        print(f"2. Generated response key:")
        print(f"   Client key: {websocket_key}")
        print(f"   Response key: {response_key}")
        
        # Send handshake response
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {response_key}\r\n"
            "\r\n"
        )
        
        client_socket.send(response.encode('utf-8'))
        print("3. Sent handshake response:")
        print("   HTTP/1.1 101 Switching Protocols")
        print("   ✓ Protocol switched to WebSocket")
        
        return True
    
    def generate_response_key(self, client_key):
        """Generate WebSocket response key"""
        # Concatenate client key with magic string
        combined = client_key + self.WEBSOCKET_MAGIC_STRING
        
        # SHA-1 hash and base64 encode
        sha1_hash = hashlib.sha1(combined.encode('utf-8')).digest()
        response_key = base64.b64encode(sha1_hash).decode('utf-8')
        
        return response_key
    
    def handle_messages(self, client_id):
        """Handle incoming WebSocket messages"""
        client = self.clients[client_id]
        client_socket = client['socket']
        
        while self.running and client_id in self.clients:
            try:
                # Read WebSocket frame
                frame = self.read_frame(client_socket)
                if frame is None:
                    break
                
                opcode = frame['opcode']
                payload = frame['payload']
                
                client['messages_received'] += 1
                
                if opcode == 0x1:  # Text frame
                    message = payload.decode('utf-8')
                    print(f"📨 Received from {client_id}: {message}")
                    self.on_message_received(client_id, message)
                    
                elif opcode == 0x2:  # Binary frame
                    print(f"📦 Received binary from {client_id}: {len(payload)} bytes")
                    self.on_binary_received(client_id, payload)
                    
                elif opcode == 0x8:  # Close frame
                    print(f"👋 Close frame from {client_id}")
                    break
                    
                elif opcode == 0x9:  # Ping frame
                    print(f"🏓 Ping from {client_id}")
                    self.send_pong(client_id, payload)
                    
                elif opcode == 0xA:  # Pong frame
                    print(f"🏓 Pong from {client_id}")
                    
            except Exception as e:
                print(f"Message handling error for {client_id}: {e}")
                break
    
    def read_frame(self, client_socket):
        """Read WebSocket frame from client"""
        try:
            # Read first 2 bytes
            data = client_socket.recv(2)
            if len(data) < 2:
                return None
            
            # Parse frame header
            byte1, byte2 = struct.unpack('!BB', data)
            
            fin = (byte1 >> 7) & 1
            opcode = byte1 & 0x0F
            masked = (byte2 >> 7) & 1
            payload_length = byte2 & 0x7F
            
            # Extended payload length
            if payload_length == 126:
                data = client_socket.recv(2)
                payload_length = struct.unpack('!H', data)[0]
            elif payload_length == 127:
                data = client_socket.recv(8)
                payload_length = struct.unpack('!Q', data)[0]
            
            # Masking key (client frames are always masked)
            if masked:
                mask = client_socket.recv(4)
            else:
                mask = None
            
            # Payload data
            payload = b''
            if payload_length > 0:
                payload = client_socket.recv(payload_length)
                
                # Unmask payload
                if masked and mask:
                    payload = bytes(payload[i] ^ mask[i % 4] for i in range(len(payload)))
            
            return {
                'fin': fin,
                'opcode': opcode,
                'masked': masked,
                'payload_length': payload_length,
                'payload': payload
            }
            
        except Exception as e:
            print(f"Frame reading error: {e}")
            return None
    
    def send_message(self, client_id, message):
        """Send text message to client"""
        if client_id not in self.clients:
            return False
        
        try:
            frame = self.create_frame(0x1, message.encode('utf-8'))
            self.clients[client_id]['socket'].send(frame)
            self.clients[client_id]['messages_sent'] += 1
            print(f"📤 Sent to {client_id}: {message}")
            return True
        except Exception as e:
            print(f"Send error to {client_id}: {e}")
            return False
    
    def send_binary(self, client_id, data):
        """Send binary data to client"""
        if client_id not in self.clients:
            return False
        
        try:
            frame = self.create_frame(0x2, data)
            self.clients[client_id]['socket'].send(frame)
            self.clients[client_id]['messages_sent'] += 1
            print(f"📦 Sent binary to {client_id}: {len(data)} bytes")
            return True
        except Exception as e:
            print(f"Binary send error to {client_id}: {e}")
            return False
    
    def send_pong(self, client_id, data=b''):
        """Send pong frame in response to ping"""
        if client_id not in self.clients:
            return False
        
        try:
            frame = self.create_frame(0xA, data)
            self.clients[client_id]['socket'].send(frame)
            print(f"🏓 Sent pong to {client_id}")
            return True
        except Exception as e:
            print(f"Pong send error to {client_id}: {e}")
            return False
    
    def broadcast_message(self, message, exclude_client=None):
        """Broadcast message to all connected clients"""
        sent_count = 0
        for client_id in list(self.clients.keys()):
            if client_id != exclude_client:
                if self.send_message(client_id, message):
                    sent_count += 1
        
        print(f"📡 Broadcast to {sent_count} clients: {message}")
        return sent_count
    
    def create_frame(self, opcode, payload):
        """Create WebSocket frame"""
        frame = bytearray()
        
        # First byte: FIN (1) + RSV (000) + Opcode (4 bits)
        frame.append(0x80 | opcode)
        
        # Payload length
        payload_length = len(payload)
        if payload_length < 126:
            frame.append(payload_length)
        elif payload_length < 65536:
            frame.append(126)
            frame.extend(struct.pack('!H', payload_length))
        else:
            frame.append(127)
            frame.extend(struct.pack('!Q', payload_length))
        
        # Payload (server frames are not masked)
        frame.extend(payload)
        
        return bytes(frame)
    
    def on_client_connected(self, client_id):
        """Handle client connection event"""
        client = self.clients[client_id]
        print(f"🔗 Client connected: {client_id} from {client['address']}")
        
        # Send welcome message
        welcome_msg = json.dumps({
            'type': 'welcome',
            'client_id': client_id,
            'server_time': datetime.now().isoformat(),
            'message': 'Welcome to WebSocket server!'
        })
        self.send_message(client_id, welcome_msg)
    
    def on_client_disconnected(self, client_id):
        """Handle client disconnection event"""
        if client_id in self.clients:
            client = self.clients[client_id]
            print(f"🔌 Client disconnected: {client_id}")
            print(f"   Messages sent: {client['messages_sent']}")
            print(f"   Messages received: {client['messages_received']}")
            print(f"   Session duration: {datetime.now() - client['connected_at']}")
    
    def on_message_received(self, client_id, message):
        """Handle received message"""
        try:
            # Try to parse as JSON
            data = json.loads(message)
            msg_type = data.get('type', 'unknown')
            
            if msg_type == 'echo':
                # Echo message back
                response = json.dumps({
                    'type': 'echo_response',
                    'original_message': data.get('message', ''),
                    'timestamp': datetime.now().isoformat()
                })
                self.send_message(client_id, response)
                
            elif msg_type == 'broadcast':
                # Broadcast to all other clients
                broadcast_msg = json.dumps({
                    'type': 'broadcast',
                    'from': client_id,
                    'message': data.get('message', ''),
                    'timestamp': datetime.now().isoformat()
                })
                self.broadcast_message(broadcast_msg, exclude_client=client_id)
                
            elif msg_type == 'ping':
                # Respond with pong
                pong_msg = json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
                self.send_message(client_id, pong_msg)
                
        except json.JSONDecodeError:
            # Handle plain text message
            echo_response = f"Echo: {message}"
            self.send_message(client_id, echo_response)
    
    def on_binary_received(self, client_id, data):
        """Handle received binary data"""
        # Echo binary data back
        self.send_binary(client_id, data)
    
    def get_server_stats(self):
        """Get server statistics"""
        total_sent = sum(client['messages_sent'] for client in self.clients.values())
        total_received = sum(client['messages_received'] for client in self.clients.values())
        
        return {
            'connected_clients': len(self.clients),
            'total_connections': self.connection_count,
            'messages_sent': total_sent,
            'messages_received': total_received,
            'uptime': datetime.now().isoformat()
        }

def simulate_websocket_server():
    """Simulate WebSocket server with mock clients"""
    print("=== WebSocket Server Simulation ===")
    
    # Create server instance
    server = WebSocketServer('localhost', 8080)
    
    # Simulate handshake process
    print("\nSimulating WebSocket handshake:")
    
    # Mock client request
    client_key = base64.b64encode(b'mock_client_key_16b').decode('utf-8')
    print(f"1. Client sends upgrade request with key: {client_key}")
    
    # Generate response key
    response_key = server.generate_response_key(client_key)
    print(f"2. Server generates response key: {response_key}")
    
    # Verify key generation
    expected_combined = client_key + server.WEBSOCKET_MAGIC_STRING
    expected_hash = hashlib.sha1(expected_combined.encode('utf-8')).digest()
    expected_key = base64.b64encode(expected_hash).decode('utf-8')
    
    print(f"3. Key verification: {'✓ Valid' if response_key == expected_key else '❌ Invalid'}")
    
    # Simulate frame creation
    print(f"\nSimulating WebSocket frames:")
    
    # Text frame
    text_message = "Hello WebSocket!"
    text_frame = server.create_frame(0x1, text_message.encode('utf-8'))
    print(f"Text frame created: {len(text_frame)} bytes")
    
    # Binary frame
    binary_data = b'\x01\x02\x03\x04'
    binary_frame = server.create_frame(0x2, binary_data)
    print(f"Binary frame created: {len(binary_frame)} bytes")
    
    # Control frames
    ping_frame = server.create_frame(0x9, b'ping')
    pong_frame = server.create_frame(0xA, b'pong')
    close_frame = server.create_frame(0x8, b'')
    
    print(f"Control frames: ping={len(ping_frame)}, pong={len(pong_frame)}, close={len(close_frame)} bytes")
    
    return server

if __name__ == "__main__":
    # Run WebSocket server simulation
    server = simulate_websocket_server()
    
    print(f"\n=== WebSocket Server Summary ===")
    print(f"Protocol: WebSocket (RFC 6455)")
    print(f"Handshake: HTTP/1.1 Upgrade mechanism")
    print(f"Communication: Full-duplex, frame-based")
    print(f"Features: Text/binary messages, control frames, real-time communication")
    print(f"Use cases: Chat, gaming, live data, collaborative apps")
