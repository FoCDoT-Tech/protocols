#!/usr/bin/env python3
"""
TCP Client-Server Implementation
Demonstrates basic TCP socket programming with client-server communication.
"""

import socket
import threading
import time
import json
from typing import Dict, List, Optional

class TCPServer:
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.clients: Dict[str, socket.socket] = {}
        
    def start(self):
        """Start the TCP server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print(f"🚀 TCP Server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    client_id = f"{client_address[0]}:{client_address[1]}"
                    self.clients[client_id] = client_socket
                    
                    print(f"🔌 Client connected: {client_id}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_id),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        print("❌ Server socket error")
                    break
                    
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.stop()
    
    def _handle_client(self, client_socket: socket.socket, client_id: str):
        """Handle individual client connection"""
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8')
                print(f"📥 Received from {client_id}: {message}")
                
                # Echo response
                response = f"Echo: {message}"
                client_socket.send(response.encode('utf-8'))
                
        except socket.error:
            pass
        finally:
            client_socket.close()
            if client_id in self.clients:
                del self.clients[client_id]
            print(f"🔌 Client disconnected: {client_id}")
    
    def stop(self):
        """Stop the TCP server"""
        self.running = False
        if self.socket:
            self.socket.close()
        
        # Close all client connections
        for client_socket in self.clients.values():
            client_socket.close()
        self.clients.clear()
        
        print("🛑 TCP Server stopped")

class TCPClient:
    def __init__(self, server_host: str = "localhost", server_port: int = 8080):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to TCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            print(f"🔌 Connected to {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def send_message(self, message: str) -> Optional[str]:
        """Send message to server and receive response"""
        if not self.connected or not self.socket:
            return None
        
        try:
            self.socket.send(message.encode('utf-8'))
            response = self.socket.recv(1024)
            return response.decode('utf-8')
        except Exception as e:
            print(f"❌ Send error: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            self.socket.close()
            self.connected = False
            print("🔌 Disconnected from server")

def demonstrate_tcp_client_server():
    """Demonstrate TCP client-server communication"""
    print("=== TCP Client-Server Demonstration ===")
    
    # Start server in background thread
    server = TCPServer("localhost", 8080)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(0.5)
    
    try:
        # Create and connect clients
        client1 = TCPClient("localhost", 8080)
        client2 = TCPClient("localhost", 8080)
        
        if client1.connect() and client2.connect():
            # Send messages
            messages = [
                ("Client 1", "Hello from client 1!"),
                ("Client 2", "Hello from client 2!"),
                ("Client 1", "How are you?"),
                ("Client 2", "TCP is working great!")
            ]
            
            for client_name, message in messages:
                if client_name == "Client 1":
                    response = client1.send_message(message)
                else:
                    response = client2.send_message(message)
                
                if response:
                    print(f"📤 {client_name} sent: {message}")
                    print(f"📥 {client_name} received: {response}")
                
                time.sleep(0.2)
        
        # Disconnect clients
        client1.disconnect()
        client2.disconnect()
        
    finally:
        server.stop()
    
    print("\n🎯 TCP Client-Server demonstrates:")
    print("💡 Reliable connection-oriented communication")
    print("💡 Full-duplex bidirectional data transfer")
    print("💡 Multiple concurrent client connections")
    print("💡 Error handling and connection management")

if __name__ == "__main__":
    demonstrate_tcp_client_server()
