#!/usr/bin/env python3
"""
IPv4 Packet Parser and Generator
Demonstrates IPv4 packet structure and basic routing simulation
"""

import struct
import socket
import random

class IPv4Packet:
    def __init__(self, src_ip="192.168.1.100", dst_ip="192.168.1.1", data=b"Hello World"):
        self.version = 4
        self.header_length = 5  # 5 * 4 = 20 bytes (minimum)
        self.tos = 0
        self.total_length = 20 + len(data)
        self.identification = random.randint(1, 65535)
        self.flags = 2  # Don't fragment
        self.fragment_offset = 0
        self.ttl = 64
        self.protocol = 1  # ICMP
        self.checksum = 0
        self.src_ip = self._ip_to_int(src_ip)
        self.dst_ip = self._ip_to_int(dst_ip)
        self.data = data
    
    def _ip_to_int(self, ip_str):
        """Convert IP string to 32-bit integer"""
        return struct.unpack("!I", socket.inet_aton(ip_str))[0]
    
    def _int_to_ip(self, ip_int):
        """Convert 32-bit integer to IP string"""
        return socket.inet_ntoa(struct.pack("!I", ip_int))
    
    def _calculate_checksum(self, header):
        """Calculate IPv4 header checksum"""
        checksum = 0
        for i in range(0, len(header), 2):
            word = (header[i] << 8) + header[i + 1]
            checksum += word
        
        # Add carry bits
        checksum = (checksum >> 16) + (checksum & 0xFFFF)
        checksum += (checksum >> 16)
        return ~checksum & 0xFFFF
    
    def pack(self):
        """Pack IPv4 packet into bytes"""
        # Pack header without checksum
        version_ihl = (self.version << 4) + self.header_length
        flags_fragment = (self.flags << 13) + self.fragment_offset
        
        header = struct.pack("!BBHHHBBH4s4s",
            version_ihl,
            self.tos,
            self.total_length,
            self.identification,
            flags_fragment,
            self.ttl,
            self.protocol,
            0,  # Checksum placeholder
            struct.pack("!I", self.src_ip),
            struct.pack("!I", self.dst_ip)
        )
        
        # Calculate and update checksum
        self.checksum = self._calculate_checksum(header)
        
        # Repack with correct checksum
        header = struct.pack("!BBHHHBBH4s4s",
            version_ihl,
            self.tos,
            self.total_length,
            self.identification,
            flags_fragment,
            self.ttl,
            self.protocol,
            self.checksum,
            struct.pack("!I", self.src_ip),
            struct.pack("!I", self.dst_ip)
        )
        
        return header + self.data
    
    def display(self):
        """Display packet information"""
        print(f"IPv4 Packet:")
        print(f"  Version: {self.version}")
        print(f"  Header Length: {self.header_length * 4} bytes")
        print(f"  Total Length: {self.total_length} bytes")
        print(f"  TTL: {self.ttl}")
        print(f"  Protocol: {self.protocol}")
        print(f"  Source IP: {self._int_to_ip(self.src_ip)}")
        print(f"  Destination IP: {self._int_to_ip(self.dst_ip)}")
        print(f"  Checksum: 0x{self.checksum:04x}")
        print(f"  Data: {self.data.decode('utf-8', errors='ignore')}")

class SimpleRouter:
    def __init__(self):
        self.routing_table = {
            "192.168.1.0/24": "192.168.1.1",
            "10.0.0.0/8": "10.0.0.1",
            "0.0.0.0/0": "192.168.1.1"  # Default route
        }
    
    def route_packet(self, dst_ip):
        """Simple routing table lookup"""
        dst_int = struct.unpack("!I", socket.inet_aton(dst_ip))[0]
        
        for network, next_hop in self.routing_table.items():
            if network == "0.0.0.0/0":  # Default route
                return next_hop
            
            net_ip, prefix = network.split("/")
            net_int = struct.unpack("!I", socket.inet_aton(net_ip))[0]
            mask = (0xFFFFFFFF << (32 - int(prefix))) & 0xFFFFFFFF
            
            if (dst_int & mask) == (net_int & mask):
                return next_hop
        
        return None

def demonstrate_ipv4():
    """Demonstrate IPv4 packet creation and routing"""
    print("=== IPv4 Packet Demonstration ===\n")
    
    # Create and display IPv4 packet
    packet = IPv4Packet("192.168.1.100", "8.8.8.8", b"DNS Query")
    packet.display()
    
    print(f"\nPacked packet size: {len(packet.pack())} bytes")
    
    # Demonstrate routing
    print("\n=== Routing Demonstration ===")
    router = SimpleRouter()
    
    test_destinations = ["192.168.1.50", "10.0.0.100", "8.8.8.8"]
    
    for dst in test_destinations:
        next_hop = router.route_packet(dst)
        print(f"Route to {dst} -> Next hop: {next_hop}")

if __name__ == "__main__":
    demonstrate_ipv4()
