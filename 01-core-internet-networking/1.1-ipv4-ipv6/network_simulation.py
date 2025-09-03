#!/usr/bin/env python3
"""
Network Simulation - IPv4/IPv6 Basic Demonstration
Simplified for quick execution (<5 seconds)
"""

def demonstrate_ip_addressing():
    """Quick demonstration of IPv4/IPv6 addressing concepts"""
    print("=== IP Addressing Demonstration ===\n")
    
    # IPv4 examples
    print("IPv4 Address Examples:")
    print("  Private: 192.168.1.100/24 (Class C)")
    print("  Private: 10.0.1.50/16 (Class A)")
    print("  Public:  8.8.8.8/32 (Google DNS)")
    
    # IPv6 examples
    print("\nIPv6 Address Examples:")
    print("  Global:     2001:db8:85a3::8a2e:370:7334/64")
    print("  Link-local: fe80::1/64")
    print("  Loopback:   ::1/128")
    
    # Subnetting example
    print("\nSubnetting Example (10.0.0.0/16):")
    for i in range(3):
        subnet = f"10.0.{i}.0/24"
        print(f"  Subnet {i+1}: {subnet} (254 hosts)")
    
    # Routing simulation
    print("\nSimple Routing:")
    routes = [
        ("192.168.1.100", "192.168.1.200", "Direct (same subnet)"),
        ("192.168.1.100", "10.0.1.50", "Via gateway"),
        ("10.0.1.50", "8.8.8.8", "Via internet gateway")
    ]
    
    for src, dst, route_type in routes:
        print(f"  {src} -> {dst}: {route_type}")

def demonstrate_packet_structure():
    """Show basic packet structure differences"""
    print("\n=== Packet Structure Comparison ===\n")
    
    print("IPv4 Header (20 bytes minimum):")
    print("  Version(4) | IHL(4) | ToS(8) | Length(16)")
    print("  ID(16) | Flags(3) | Fragment(13)")
    print("  TTL(8) | Protocol(8) | Checksum(16)")
    print("  Source IP(32) | Destination IP(32)")
    
    print("\nIPv6 Header (40 bytes fixed):")
    print("  Version(4) | Traffic Class(8) | Flow Label(20)")
    print("  Payload Length(16) | Next Header(8) | Hop Limit(8)")
    print("  Source IP(128)")
    print("  Destination IP(128)")
    
    print("\nKey Differences:")
    print("  - IPv6 has no checksum (handled by upper layers)")
    print("  - IPv6 has no fragmentation in header")
    print("  - IPv6 uses extension headers for options")

if __name__ == "__main__":
    demonstrate_ip_addressing()
    demonstrate_packet_structure()
