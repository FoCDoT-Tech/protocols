#!/usr/bin/env python3
"""
UDP Client-Server Communication Simulation
Demonstrates UDP's connectionless nature and packet handling
"""

import socket
import time
import random
import threading

class UDPServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
    def simulate_server(self):
        """Simulate UDP server behavior"""
        print(f"=== UDP Server Simulation ===")
        print(f"Server listening on {self.host}:{self.port}")
        
        # Simulate receiving packets
        clients = [
            ("192.168.1.100", 12345),
            ("192.168.1.101", 12346),
            ("192.168.1.102", 12347)
        ]
        
        messages = [
            "Hello Server!",
            "Game state update",
            "Player position: x=100, y=200",
            "Voice data packet",
            "Ping request"
        ]
        
        for i in range(10):
            # Simulate random client sending data
            client_addr = random.choice(clients)
            message = random.choice(messages)
            
            # Simulate packet loss (10% chance)
            if random.random() < 0.9:
                print(f"Received from {client_addr[0]}:{client_addr[1]}: '{message}'")
                
                # Simulate response
                response = f"ACK: {message[:10]}..."
                print(f"Sent to {client_addr[0]}:{client_addr[1]}: '{response}'")
            else:
                print(f"Packet lost from {client_addr[0]}:{client_addr[1]}")
            
            time.sleep(0.1)

class UDPClient:
    def __init__(self, server_host='localhost', server_port=8888):
        self.server_host = server_host
        self.server_port = server_port
        
    def simulate_client(self, client_id):
        """Simulate UDP client behavior"""
        print(f"\n=== UDP Client {client_id} Simulation ===")
        
        messages = [
            f"Client {client_id}: Hello",
            f"Client {client_id}: Data packet 1",
            f"Client {client_id}: Data packet 2",
            f"Client {client_id}: Goodbye"
        ]
        
        for message in messages:
            print(f"Client {client_id} sending: '{message}'")
            
            # Simulate network delay
            delay = random.uniform(0.01, 0.05)
            time.sleep(delay)
            
            # Simulate response (90% success rate)
            if random.random() < 0.9:
                print(f"Client {client_id} received: 'ACK: {message[:10]}...'")
            else:
                print(f"Client {client_id}: No response (timeout)")
            
            time.sleep(0.1)

def demonstrate_udp_communication():
    """Demonstrate UDP client-server communication"""
    print("=== UDP Communication Demonstration ===\n")
    
    # Server simulation
    server = UDPServer()
    server.simulate_server()
    
    # Client simulations
    for client_id in range(1, 4):
        client = UDPClient()
        client.simulate_client(client_id)

def compare_udp_tcp():
    """Compare UDP and TCP characteristics"""
    print("\n=== UDP vs TCP Comparison ===\n")
    
    characteristics = [
        ("Connection", "Connectionless", "Connection-oriented"),
        ("Reliability", "Unreliable", "Reliable"),
        ("Ordering", "No guarantee", "Ordered delivery"),
        ("Speed", "Fast", "Slower"),
        ("Overhead", "Low (8 bytes)", "High (20+ bytes)"),
        ("Flow Control", "None", "Yes"),
        ("Congestion Control", "None", "Yes"),
        ("Use Cases", "Real-time, Gaming", "Web, Email, File transfer")
    ]
    
    print(f"{'Characteristic':<20} {'UDP':<20} {'TCP':<20}")
    print("-" * 60)
    
    for char, udp_val, tcp_val in characteristics:
        print(f"{char:<20} {udp_val:<20} {tcp_val:<20}")

if __name__ == "__main__":
    demonstrate_udp_communication()
    compare_udp_tcp()
