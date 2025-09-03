#!/usr/bin/env python3
"""
ICMP Traceroute Implementation
Demonstrates ICMP Time Exceeded messages for path discovery
"""

import time
import random

class ICMPTraceroute:
    def __init__(self):
        self.max_hops = 30
        self.timeout = 3.0
        
    def simulate_traceroute(self, destination="8.8.8.8"):
        """Simulate traceroute using ICMP Time Exceeded messages"""
        print(f"traceroute to {destination}, {self.max_hops} hops max")
        
        # Simulated network path
        hops = [
            ("192.168.1.1", "home-router.local", 1.2),
            ("10.0.0.1", "isp-gateway.net", 15.3),
            ("203.0.113.1", "regional-hub.isp.com", 25.8),
            ("198.51.100.1", "backbone-router.net", 45.2),
            ("8.8.8.8", "dns.google", 52.1)
        ]
        
        for i, (ip, hostname, rtt) in enumerate(hops, 1):
            # Add some variation to RTT
            rtt_var = rtt + random.uniform(-2, 2)
            print(f"{i:2d}  {hostname} ({ip})  {rtt_var:.1f} ms")
            time.sleep(0.1)  # Brief pause for realism
        
        print(f"\nTrace complete to {destination}")
        return hops
    
    def explain_traceroute_mechanism(self):
        """Explain how traceroute works with ICMP"""
        print("\n=== How Traceroute Works ===")
        print("1. Send UDP/ICMP packet with TTL=1")
        print("2. First router decrements TTL to 0, sends ICMP Time Exceeded")
        print("3. Send packet with TTL=2")
        print("4. Second router decrements TTL to 0, sends ICMP Time Exceeded")
        print("5. Continue until destination reached")
        print("6. Destination sends ICMP Port Unreachable (UDP) or Echo Reply (ICMP)")

class ICMPErrorSimulator:
    def __init__(self):
        self.error_types = {
            3: "Destination Unreachable",
            11: "Time Exceeded", 
            12: "Parameter Problem"
        }
    
    def simulate_network_errors(self):
        """Simulate various ICMP error conditions"""
        print("\n=== ICMP Error Message Simulation ===")
        
        scenarios = [
            {
                "error": "Destination Host Unreachable",
                "type": 3,
                "code": 1,
                "description": "Router cannot reach destination host"
            },
            {
                "error": "Port Unreachable", 
                "type": 3,
                "code": 3,
                "description": "Destination port is not listening"
            },
            {
                "error": "TTL Exceeded in Transit",
                "type": 11,
                "code": 0, 
                "description": "Packet TTL reached 0 during transit"
            },
            {
                "error": "Fragmentation Needed",
                "type": 3,
                "code": 4,
                "description": "Packet too large, fragmentation required but DF bit set"
            }
        ]
        
        for scenario in scenarios:
            print(f"\nError: {scenario['error']}")
            print(f"ICMP Type: {scenario['type']}, Code: {scenario['code']}")
            print(f"Cause: {scenario['description']}")
            
            # Simulate error packet structure
            print(f"ICMP Header: Type={scenario['type']}, Code={scenario['code']}, Checksum=0x1234")

def demonstrate_icmp_diagnostics():
    """Demonstrate ICMP diagnostic tools"""
    print("=== ICMP Network Diagnostics ===\n")
    
    # Traceroute simulation
    tracer = ICMPTraceroute()
    tracer.simulate_traceroute("8.8.8.8")
    tracer.explain_traceroute_mechanism()
    
    # Error simulation
    error_sim = ICMPErrorSimulator()
    error_sim.simulate_network_errors()
    
    # Path MTU Discovery simulation
    print("\n=== Path MTU Discovery ===")
    print("1. Send large packet (1500 bytes) with DF bit set")
    print("2. Router sends ICMP Fragmentation Needed (Type 3, Code 4)")
    print("3. Adjust packet size and retry")
    print("4. Continue until optimal MTU found")
    
    mtu_sizes = [1500, 1400, 1300, 1200]
    for mtu in mtu_sizes:
        if mtu == 1300:
            print(f"MTU {mtu}: Success! Optimal path MTU discovered")
            break
        else:
            print(f"MTU {mtu}: ICMP Fragmentation Needed received")

if __name__ == "__main__":
    demonstrate_icmp_diagnostics()
