#!/usr/bin/env python3
"""
ICMPv6 Neighbor Discovery Simulation
Demonstrates IPv6 neighbor discovery protocol using ICMPv6
"""

import time
import random

class NeighborDiscovery:
    def __init__(self):
        self.neighbor_solicitation = 135
        self.neighbor_advertisement = 136
        self.router_solicitation = 133
        self.router_advertisement = 134
        
    def simulate_neighbor_discovery(self):
        """Simulate IPv6 neighbor discovery process"""
        print("=== IPv6 Neighbor Discovery Simulation ===\n")
        
        # Scenario: Host wants to communicate with neighbor
        target_ip = "2001:db8::2"
        source_ip = "2001:db8::1"
        
        print(f"Host {source_ip} wants to reach {target_ip}")
        print("1. Check neighbor cache... MISS")
        
        # Step 1: Neighbor Solicitation
        print(f"\n2. Sending Neighbor Solicitation:")
        print(f"   ICMPv6 Type: {self.neighbor_solicitation}")
        print(f"   Target: {target_ip}")
        print(f"   Multicast destination: ff02::1:ff00:2")
        
        time.sleep(0.2)
        
        # Step 2: Neighbor Advertisement
        target_mac = "02:42:ac:11:00:02"
        print(f"\n3. Received Neighbor Advertisement:")
        print(f"   ICMPv6 Type: {self.neighbor_advertisement}")
        print(f"   Target: {target_ip}")
        print(f"   Link-layer address: {target_mac}")
        
        # Step 3: Cache update
        print(f"\n4. Neighbor cache updated:")
        print(f"   {target_ip} -> {target_mac} (REACHABLE)")
        
        print(f"\n5. Communication can now proceed!")
        
    def simulate_router_discovery(self):
        """Simulate IPv6 router discovery process"""
        print("\n=== IPv6 Router Discovery Simulation ===\n")
        
        # Host startup scenario
        print("Host starting up, needs default router...")
        
        # Step 1: Router Solicitation
        print(f"\n1. Sending Router Solicitation:")
        print(f"   ICMPv6 Type: {self.router_solicitation}")
        print(f"   Destination: ff02::2 (all-routers multicast)")
        
        time.sleep(0.2)
        
        # Step 2: Router Advertisement
        router_ip = "2001:db8::1"
        prefix = "2001:db8::/64"
        print(f"\n2. Received Router Advertisement:")
        print(f"   ICMPv6 Type: {self.router_advertisement}")
        print(f"   Router: {router_ip}")
        print(f"   Prefix: {prefix}")
        print(f"   Prefix lifetime: 86400 seconds")
        
        # Step 3: Address configuration
        host_ip = "2001:db8::42:acff:fe11:2"
        print(f"\n3. Host configures address:")
        print(f"   Generated address: {host_ip}")
        print(f"   Default router: {router_ip}")
        
    def demonstrate_icmpv6_types(self):
        """Show ICMPv6 message types and their purposes"""
        print("\n=== ICMPv6 Message Types ===\n")
        
        message_types = {
            1: ("Destination Unreachable", "Error reporting"),
            2: ("Packet Too Big", "Path MTU discovery"),
            3: ("Time Exceeded", "Hop limit exceeded"),
            4: ("Parameter Problem", "Header field error"),
            128: ("Echo Request", "Ping request"),
            129: ("Echo Reply", "Ping response"),
            133: ("Router Solicitation", "Request router info"),
            134: ("Router Advertisement", "Router announces presence"),
            135: ("Neighbor Solicitation", "Address resolution"),
            136: ("Neighbor Advertisement", "Address resolution response"),
            137: ("Redirect", "Better route available")
        }
        
        for type_num, (name, purpose) in message_types.items():
            print(f"Type {type_num:3d}: {name:<25} - {purpose}")

class IPv6AddressResolution:
    def __init__(self):
        self.neighbor_cache = {}
        
    def resolve_address(self, target_ip):
        """Simulate address resolution process"""
        print(f"\n=== Resolving {target_ip} ===")
        
        # Check cache first
        if target_ip in self.neighbor_cache:
            mac = self.neighbor_cache[target_ip]
            print(f"Cache HIT: {target_ip} -> {mac}")
            return mac
        
        print("Cache MISS - initiating neighbor discovery")
        
        # Simulate neighbor solicitation/advertisement
        print("1. Sending Neighbor Solicitation...")
        time.sleep(0.1)
        
        # Generate random MAC for simulation
        mac = f"02:42:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}"
        
        print(f"2. Received Neighbor Advertisement")
        print(f"3. Caching: {target_ip} -> {mac}")
        
        self.neighbor_cache[target_ip] = mac
        return mac

def demonstrate_ipv6_neighbor_discovery():
    """Main demonstration function"""
    print("=== ICMPv6 Neighbor Discovery Protocol ===\n")
    
    # Basic neighbor discovery
    nd = NeighborDiscovery()
    nd.simulate_neighbor_discovery()
    nd.simulate_router_discovery()
    nd.demonstrate_icmpv6_types()
    
    # Address resolution examples
    resolver = IPv6AddressResolution()
    
    print("\n=== Address Resolution Examples ===")
    targets = ["2001:db8::10", "2001:db8::20", "2001:db8::10"]  # Note: duplicate
    
    for target in targets:
        resolver.resolve_address(target)
    
    print(f"\nFinal neighbor cache:")
    for ip, mac in resolver.neighbor_cache.items():
        print(f"  {ip} -> {mac}")

if __name__ == "__main__":
    demonstrate_ipv6_neighbor_discovery()
