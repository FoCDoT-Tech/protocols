#!/usr/bin/env python3
"""
ICMP Ping Implementation
Demonstrates ICMP Echo Request/Reply mechanism
"""

import socket
import struct
import time
import os
import sys

class ICMPPing:
    def __init__(self):
        self.icmp_echo_request = 8
        self.icmp_echo_reply = 0
        self.icmp_code = 0
        self.packet_id = os.getpid() & 0xFFFF
        
    def checksum(self, data):
        """Calculate ICMP checksum"""
        # Pad data to even length
        if len(data) % 2:
            data += b'\x00'
        
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
        
        # Add carry bits
        checksum = (checksum >> 16) + (checksum & 0xFFFF)
        checksum += (checksum >> 16)
        
        return ~checksum & 0xFFFF
    
    def create_packet(self, sequence):
        """Create ICMP Echo Request packet"""
        # Create header with checksum = 0
        header = struct.pack("!BBHHH", 
                           self.icmp_echo_request, 
                           self.icmp_code, 
                           0,  # checksum placeholder
                           self.packet_id, 
                           sequence)
        
        # Add timestamp data
        timestamp = struct.pack("!d", time.time())
        data = timestamp + b"Python ICMP Ping Test Data"
        
        # Calculate checksum
        packet = header + data
        checksum = self.checksum(packet)
        
        # Recreate header with correct checksum
        header = struct.pack("!BBHHH", 
                           self.icmp_echo_request, 
                           self.icmp_code, 
                           checksum, 
                           self.packet_id, 
                           sequence)
        
        return header + data
    
    def parse_reply(self, packet):
        """Parse ICMP Echo Reply packet"""
        # Skip IP header (typically 20 bytes)
        icmp_header = packet[20:28]
        
        if len(icmp_header) < 8:
            return None
        
        type_field, code, checksum, packet_id, sequence = struct.unpack("!BBHHH", icmp_header)
        
        if type_field == self.icmp_echo_reply and packet_id == self.packet_id:
            # Extract timestamp from data
            data_start = 28
            if len(packet) >= data_start + 8:
                timestamp = struct.unpack("!d", packet[data_start:data_start + 8])[0]
                return {
                    'sequence': sequence,
                    'timestamp': timestamp,
                    'rtt': (time.time() - timestamp) * 1000  # RTT in ms
                }
        
        return None
    
    def simulate_ping(self, host="127.0.0.1", count=4):
        """Simulate ping functionality (without raw sockets)"""
        print(f"PING {host} simulation")
        print(f"Simulating {count} ICMP Echo Request packets")
        
        rtts = []
        
        for seq in range(1, count + 1):
            # Create packet for demonstration
            packet = self.create_packet(seq)
            
            # Simulate network delay
            simulated_rtt = 0.5 + (seq * 0.1)  # Increasing RTT
            rtts.append(simulated_rtt)
            
            print(f"64 bytes from {host}: icmp_seq={seq} time={simulated_rtt:.1f}ms")
            time.sleep(0.1)  # Brief pause between pings
        
        # Statistics
        print(f"\n--- {host} ping statistics ---")
        print(f"{count} packets transmitted, {count} received, 0% packet loss")
        print(f"round-trip min/avg/max = {min(rtts):.1f}/{sum(rtts)/len(rtts):.1f}/{max(rtts):.1f} ms")
        
        return rtts

class ICMPv6Ping:
    def __init__(self):
        self.icmpv6_echo_request = 128
        self.icmpv6_echo_reply = 129
        
    def simulate_ipv6_ping(self, host="::1", count=3):
        """Simulate IPv6 ping functionality"""
        print(f"\nPING {host} IPv6 simulation")
        print(f"Simulating {count} ICMPv6 Echo Request packets")
        
        for seq in range(1, count + 1):
            # Simulate IPv6 ping with different characteristics
            rtt = 0.3 + (seq * 0.05)
            print(f"64 bytes from {host}: icmp_seq={seq} time={rtt:.1f}ms")
            time.sleep(0.1)
        
        print(f"\n--- {host} IPv6 ping statistics ---")
        print(f"{count} packets transmitted, {count} received, 0% packet loss")

def demonstrate_icmp():
    """Demonstrate ICMP functionality"""
    print("=== ICMP/ICMPv6 Demonstration ===\n")
    
    # IPv4 ICMP ping simulation
    ping = ICMPPing()
    ping.simulate_ping("192.168.1.1", 4)
    
    # IPv6 ICMPv6 ping simulation
    ping6 = ICMPv6Ping()
    ping6.simulate_ipv6_ping("2001:db8::1", 3)
    
    # Demonstrate packet structure
    print("\n=== ICMP Packet Structure ===")
    packet = ping.create_packet(1)
    print(f"ICMP packet size: {len(packet)} bytes")
    print(f"Header: {packet[:8].hex()}")
    print(f"Data: {packet[8:16].hex()}...")
    
    # Show message types
    print("\n=== ICMP Message Types ===")
    message_types = {
        0: "Echo Reply",
        3: "Destination Unreachable", 
        5: "Redirect",
        8: "Echo Request",
        11: "Time Exceeded",
        12: "Parameter Problem"
    }
    
    for type_num, description in message_types.items():
        print(f"Type {type_num}: {description}")
    
    print("\n=== ICMPv6 Message Types ===")
    icmpv6_types = {
        1: "Destination Unreachable",
        2: "Packet Too Big", 
        3: "Time Exceeded",
        4: "Parameter Problem",
        128: "Echo Request",
        129: "Echo Reply",
        135: "Neighbor Solicitation",
        136: "Neighbor Advertisement"
    }
    
    for type_num, description in icmpv6_types.items():
        print(f"Type {type_num}: {description}")

if __name__ == "__main__":
    demonstrate_icmp()
