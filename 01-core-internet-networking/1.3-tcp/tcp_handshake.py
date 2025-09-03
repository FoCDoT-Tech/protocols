#!/usr/bin/env python3
"""
TCP Three-Way Handshake Simulation
Demonstrates TCP connection establishment and termination
"""

import random
import time

class TCPConnection:
    def __init__(self, client_port=12345, server_port=80):
        self.client_port = client_port
        self.server_port = server_port
        self.client_seq = random.randint(1000, 9999)
        self.server_seq = random.randint(1000, 9999)
        self.state = "CLOSED"
        
    def simulate_handshake(self):
        """Simulate TCP three-way handshake"""
        print("=== TCP Three-Way Handshake ===\n")
        
        # Step 1: Client sends SYN
        print(f"1. Client -> Server: SYN")
        print(f"   Source Port: {self.client_port}")
        print(f"   Destination Port: {self.server_port}")
        print(f"   Sequence Number: {self.client_seq}")
        print(f"   Flags: SYN=1")
        print(f"   Client State: SYN-SENT")
        
        time.sleep(0.1)
        
        # Step 2: Server responds with SYN-ACK
        print(f"\n2. Server -> Client: SYN-ACK")
        print(f"   Source Port: {self.server_port}")
        print(f"   Destination Port: {self.client_port}")
        print(f"   Sequence Number: {self.server_seq}")
        print(f"   Acknowledgment Number: {self.client_seq + 1}")
        print(f"   Flags: SYN=1, ACK=1")
        print(f"   Server State: SYN-RECEIVED")
        
        time.sleep(0.1)
        
        # Step 3: Client sends ACK
        self.client_seq += 1
        print(f"\n3. Client -> Server: ACK")
        print(f"   Source Port: {self.client_port}")
        print(f"   Destination Port: {self.server_port}")
        print(f"   Sequence Number: {self.client_seq}")
        print(f"   Acknowledgment Number: {self.server_seq + 1}")
        print(f"   Flags: ACK=1")
        print(f"   Client State: ESTABLISHED")
        
        self.state = "ESTABLISHED"
        print(f"\n✓ Connection Established!")
        print(f"   Both sides in ESTABLISHED state")
        
    def simulate_data_transfer(self):
        """Simulate TCP data transfer with sequence numbers"""
        if self.state != "ESTABLISHED":
            print("Error: Connection not established")
            return
            
        print(f"\n=== TCP Data Transfer ===\n")
        
        data_segments = [
            ("GET /index.html HTTP/1.1", 24),
            ("Host: example.com", 17),
            ("Connection: close", 17)
        ]
        
        for i, (data, length) in enumerate(data_segments, 1):
            print(f"Segment {i}: Client -> Server")
            print(f"   Sequence Number: {self.client_seq}")
            print(f"   Data: '{data}'")
            print(f"   Data Length: {length} bytes")
            
            # Server ACK
            print(f"   Server -> Client: ACK")
            print(f"   Acknowledgment Number: {self.client_seq + length}")
            
            self.client_seq += length
            time.sleep(0.05)
            print()
    
    def simulate_connection_close(self):
        """Simulate TCP four-way handshake for connection termination"""
        print(f"=== TCP Connection Termination ===\n")
        
        # Step 1: Client initiates close
        print(f"1. Client -> Server: FIN")
        print(f"   Sequence Number: {self.client_seq}")
        print(f"   Flags: FIN=1")
        print(f"   Client State: FIN-WAIT-1")
        
        time.sleep(0.1)
        
        # Step 2: Server ACKs the FIN
        print(f"\n2. Server -> Client: ACK")
        print(f"   Acknowledgment Number: {self.client_seq + 1}")
        print(f"   Server State: CLOSE-WAIT")
        print(f"   Client State: FIN-WAIT-2")
        
        time.sleep(0.1)
        
        # Step 3: Server sends FIN
        self.server_seq += 1
        print(f"\n3. Server -> Client: FIN")
        print(f"   Sequence Number: {self.server_seq}")
        print(f"   Flags: FIN=1")
        print(f"   Server State: LAST-ACK")
        
        time.sleep(0.1)
        
        # Step 4: Client ACKs the FIN
        self.client_seq += 1
        print(f"\n4. Client -> Server: ACK")
        print(f"   Acknowledgment Number: {self.server_seq + 1}")
        print(f"   Client State: TIME-WAIT")
        
        time.sleep(0.1)
        
        print(f"\n✓ Connection Closed!")
        print(f"   Server State: CLOSED")
        print(f"   Client State: CLOSED (after TIME-WAIT)")
        
        self.state = "CLOSED"

class TCPStateMachine:
    def __init__(self):
        self.states = [
            "CLOSED", "LISTEN", "SYN-SENT", "SYN-RECEIVED",
            "ESTABLISHED", "FIN-WAIT-1", "FIN-WAIT-2", 
            "CLOSE-WAIT", "CLOSING", "LAST-ACK", "TIME-WAIT"
        ]
        
    def show_state_transitions(self):
        """Display TCP state machine transitions"""
        print("=== TCP State Machine ===\n")
        
        transitions = [
            ("CLOSED", "LISTEN", "passive open"),
            ("CLOSED", "SYN-SENT", "active open / send SYN"),
            ("LISTEN", "SYN-RECEIVED", "receive SYN / send SYN-ACK"),
            ("SYN-SENT", "ESTABLISHED", "receive SYN-ACK / send ACK"),
            ("SYN-RECEIVED", "ESTABLISHED", "receive ACK"),
            ("ESTABLISHED", "FIN-WAIT-1", "close / send FIN"),
            ("ESTABLISHED", "CLOSE-WAIT", "receive FIN / send ACK"),
            ("FIN-WAIT-1", "FIN-WAIT-2", "receive ACK"),
            ("FIN-WAIT-2", "TIME-WAIT", "receive FIN / send ACK"),
            ("CLOSE-WAIT", "LAST-ACK", "close / send FIN"),
            ("LAST-ACK", "CLOSED", "receive ACK"),
            ("TIME-WAIT", "CLOSED", "timeout")
        ]
        
        for from_state, to_state, condition in transitions:
            print(f"{from_state:<15} -> {to_state:<15} ({condition})")

def demonstrate_tcp():
    """Main TCP demonstration"""
    print("=== TCP Protocol Demonstration ===\n")
    
    # Create TCP connection
    conn = TCPConnection()
    
    # Show handshake
    conn.simulate_handshake()
    
    # Show data transfer
    conn.simulate_data_transfer()
    
    # Show connection close
    conn.simulate_connection_close()
    
    # Show state machine
    state_machine = TCPStateMachine()
    state_machine.show_state_transitions()

if __name__ == "__main__":
    demonstrate_tcp()
