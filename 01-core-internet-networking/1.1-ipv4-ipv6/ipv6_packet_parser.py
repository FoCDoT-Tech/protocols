#!/usr/bin/env python3
"""
IPv6 Packet Parser and Generator
Demonstrates IPv6 packet structure and addressing
"""

import struct
import socket
import ipaddress

class IPv6Packet:
    def __init__(self, src_ip="2001:db8::1", dst_ip="2001:db8::2", data=b"Hello IPv6"):
        self.version = 6
        self.traffic_class = 0
        self.flow_label = 0
        self.payload_length = len(data)
        self.next_header = 59  # No Next Header
        self.hop_limit = 64
        self.src_ip = ipaddress.IPv6Address(src_ip)
        self.dst_ip = ipaddress.IPv6Address(dst_ip)
        self.data = data
    
    def pack(self):
        """Pack IPv6 packet into bytes"""
        # Version (4) + Traffic Class (8) + Flow Label (20) = 32 bits
        version_tc_fl = (self.version << 28) | (self.traffic_class << 20) | self.flow_label
        
        header = struct.pack("!IHBB16s16s",
            version_tc_fl,
            self.payload_length,
            self.next_header,
            self.hop_limit,
            self.src_ip.packed,
            self.dst_ip.packed
        )
        
        return header + self.data
    
    def display(self):
        """Display packet information"""
        print(f"IPv6 Packet:")
        print(f"  Version: {self.version}")
        print(f"  Traffic Class: {self.traffic_class}")
        print(f"  Flow Label: {self.flow_label}")
        print(f"  Payload Length: {self.payload_length} bytes")
        print(f"  Next Header: {self.next_header}")
        print(f"  Hop Limit: {self.hop_limit}")
        print(f"  Source IP: {self.src_ip}")
        print(f"  Destination IP: {self.dst_ip}")
        print(f"  Data: {self.data.decode('utf-8', errors='ignore')}")

class IPv6AddressManager:
    def __init__(self):
        self.address_types = {
            "loopback": "::1",
            "link_local": "fe80::/10",
            "unique_local": "fc00::/7",
            "global_unicast": "2000::/3",
            "multicast": "ff00::/8"
        }
    
    def classify_address(self, addr_str):
        """Classify IPv6 address type"""
        addr = ipaddress.IPv6Address(addr_str)
        
        if addr.is_loopback:
            return "loopback"
        elif addr.is_link_local:
            return "link_local"
        elif addr.is_private:
            return "unique_local"
        elif addr.is_multicast:
            return "multicast"
        elif addr.is_global:
            return "global_unicast"
        else:
            return "unspecified"
    
    def generate_link_local(self, mac_address="02:42:ac:11:00:02"):
        """Generate link-local address from MAC (simplified)"""
        # Remove colons and convert to int
        mac_int = int(mac_address.replace(":", ""), 16)
        
        # Split MAC into two parts and insert FFFE
        mac_high = (mac_int >> 24) & 0xFFFFFF
        mac_low = mac_int & 0xFFFFFF
        
        # Flip universal/local bit
        mac_high ^= 0x020000
        
        # Create EUI-64
        eui64 = (mac_high << 40) | (0xFFFE << 24) | mac_low
        
        # Combine with link-local prefix
        link_local = ipaddress.IPv6Address(0xFE800000000000000000000000000000 | eui64)
        return str(link_local)

def demonstrate_ipv6():
    """Demonstrate IPv6 packet creation and addressing"""
    print("=== IPv6 Packet Demonstration ===\n")
    
    # Create and display IPv6 packet
    packet = IPv6Packet("2001:db8:85a3::8a2e:370:7334", "2001:db8:85a3::1", b"IPv6 Test Data")
    packet.display()
    
    print(f"\nPacked packet size: {len(packet.pack())} bytes")
    
    # Demonstrate address classification
    print("\n=== IPv6 Address Classification ===")
    addr_manager = IPv6AddressManager()
    
    test_addresses = [
        "::1",
        "fe80::1",
        "2001:db8::1",
        "fc00::1",
        "ff02::1"
    ]
    
    for addr in test_addresses:
        addr_type = addr_manager.classify_address(addr)
        print(f"{addr:<20} -> {addr_type}")
    
    # Generate link-local address
    print(f"\nGenerated link-local: {addr_manager.generate_link_local()}")
    
    # Address space comparison
    print(f"\n=== Address Space Comparison ===")
    print(f"IPv4 total addresses: {2**32:,}")
    print(f"IPv6 total addresses: {2**128:,}")
    print(f"IPv6 addresses per square meter of Earth: {2**128 / (510_000_000 * 1_000_000):,.0f}")

if __name__ == "__main__":
    demonstrate_ipv6()
