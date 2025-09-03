#!/usr/bin/env python3
"""
DNS Resolver Simulation
Demonstrates DNS query process, record types, and caching mechanisms
"""

import time
import random
import json
from collections import defaultdict

class DNSRecord:
    def __init__(self, name, record_type, value, ttl=3600):
        self.name = name
        self.record_type = record_type
        self.value = value
        self.ttl = ttl
        self.timestamp = time.time()
    
    def is_expired(self):
        return time.time() - self.timestamp > self.ttl
    
    def __str__(self):
        return f"{self.name} {self.ttl} IN {self.record_type} {self.value}"

class DNSCache:
    def __init__(self, name):
        self.name = name
        self.cache = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, query_name, record_type):
        key = f"{query_name}:{record_type}"
        if key in self.cache:
            record = self.cache[key]
            if not record.is_expired():
                self.hits += 1
                return record
            else:
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def put(self, record):
        key = f"{record.name}:{record.record_type}"
        self.cache[key] = record
    
    def stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return f"{self.name}: {self.hits} hits, {self.misses} misses ({hit_rate:.1f}% hit rate)"

class DNSServer:
    def __init__(self, name, server_type="authoritative"):
        self.name = name
        self.server_type = server_type
        self.records = {}
        self.query_count = 0
        
    def add_record(self, record):
        key = f"{record.name}:{record.record_type}"
        self.records[key] = record
    
    def query(self, name, record_type):
        self.query_count += 1
        key = f"{name}:{record_type}"
        
        # Simulate network delay
        delay = random.uniform(0.01, 0.05)
        time.sleep(delay)
        
        if key in self.records:
            return self.records[key]
        return None

class RecursiveResolver:
    def __init__(self):
        self.cache = DNSCache("Recursive Resolver")
        self.root_servers = []
        self.query_log = []
        
    def add_root_server(self, server):
        self.root_servers.append(server)
    
    def resolve(self, domain, record_type="A"):
        """Perform recursive DNS resolution"""
        print(f"\n=== Resolving {domain} ({record_type}) ===")
        
        # Check cache first
        cached_record = self.cache.get(domain, record_type)
        if cached_record:
            print(f"✓ Found in cache: {cached_record}")
            return cached_record
        
        # Start recursive resolution
        query_path = []
        
        # Query root server
        print(f"1. Querying root server for {domain}")
        root_server = random.choice(self.root_servers)
        query_path.append(f"Root: {root_server.name}")
        
        # Simulate getting TLD server referral
        tld = domain.split('.')[-1]
        print(f"2. Root server refers to .{tld} TLD server")
        query_path.append(f"TLD: .{tld} server")
        
        # Query TLD server
        print(f"3. Querying .{tld} TLD server for {domain}")
        
        # Simulate getting authoritative server referral
        auth_domain = '.'.join(domain.split('.')[-2:])
        print(f"4. TLD server refers to authoritative server for {auth_domain}")
        query_path.append(f"Auth: {auth_domain} server")
        
        # Query authoritative server
        print(f"5. Querying authoritative server for {domain}")
        
        # Simulate authoritative response
        if record_type == "A":
            ip = f"192.0.2.{random.randint(1, 254)}"
        elif record_type == "AAAA":
            ip = f"2001:db8::{random.randint(1, 255):x}"
        elif record_type == "CNAME":
            ip = f"canonical.{domain}"
        elif record_type == "MX":
            ip = f"mail.{domain}"
        else:
            ip = f"example.{domain}"
        
        # Create record and cache it
        ttl = random.randint(300, 3600)  # 5 minutes to 1 hour
        record = DNSRecord(domain, record_type, ip, ttl)
        self.cache.put(record)
        
        print(f"6. ✓ Resolved: {record}")
        
        # Log the query
        self.query_log.append({
            'domain': domain,
            'type': record_type,
            'result': ip,
            'path': query_path,
            'timestamp': time.time()
        })
        
        return record

def simulate_dns_queries():
    """Simulate various DNS queries and caching behavior"""
    print("=== DNS Resolution Simulation ===")
    
    # Create resolver and root servers
    resolver = RecursiveResolver()
    
    # Add some root servers
    for i in range(3):
        root_server = DNSServer(f"root-{chr(97+i)}.root-servers.net", "root")
        resolver.add_root_server(root_server)
    
    # Create caching layers
    browser_cache = DNSCache("Browser")
    os_cache = DNSCache("OS")
    isp_cache = DNSCache("ISP")
    
    # Simulate queries
    domains = [
        "www.example.com",
        "api.example.com", 
        "cdn.example.com",
        "mail.example.com",
        "www.google.com",
        "github.com"
    ]
    
    record_types = ["A", "AAAA", "CNAME", "MX"]
    
    print(f"\nSimulating DNS queries...")
    
    for i in range(10):
        domain = random.choice(domains)
        record_type = random.choice(record_types)
        
        # Simulate cache hierarchy
        print(f"\nQuery {i+1}: {domain} ({record_type})")
        
        # Check browser cache
        cached = browser_cache.get(domain, record_type)
        if cached:
            print(f"✓ Browser cache hit: {cached}")
            continue
            
        # Check OS cache
        cached = os_cache.get(domain, record_type)
        if cached:
            print(f"✓ OS cache hit: {cached}")
            browser_cache.put(cached)
            continue
            
        # Check ISP cache
        cached = isp_cache.get(domain, record_type)
        if cached:
            print(f"✓ ISP cache hit: {cached}")
            os_cache.put(cached)
            browser_cache.put(cached)
            continue
        
        # Perform recursive resolution
        record = resolver.resolve(domain, record_type)
        
        # Populate all cache layers
        isp_cache.put(record)
        os_cache.put(record)
        browser_cache.put(record)
        
        time.sleep(0.1)
    
    # Print cache statistics
    print(f"\n=== Cache Statistics ===")
    print(browser_cache.stats())
    print(os_cache.stats())
    print(isp_cache.stats())
    print(resolver.cache.stats())

def demonstrate_dns_record_types():
    """Demonstrate different DNS record types"""
    print(f"\n=== DNS Record Types ===")
    
    # Create authoritative server
    auth_server = DNSServer("ns1.example.com", "authoritative")
    
    # Add various record types
    records = [
        DNSRecord("example.com", "A", "192.0.2.1", 3600),
        DNSRecord("example.com", "AAAA", "2001:db8::1", 3600),
        DNSRecord("www.example.com", "CNAME", "example.com", 3600),
        DNSRecord("example.com", "MX", "10 mail.example.com", 3600),
        DNSRecord("example.com", "NS", "ns1.example.com", 86400),
        DNSRecord("example.com", "TXT", "v=spf1 include:_spf.google.com ~all", 3600),
        DNSRecord("_sip._tcp.example.com", "SRV", "10 5 5060 sip.example.com", 3600)
    ]
    
    for record in records:
        auth_server.add_record(record)
    
    print(f"Authoritative server for example.com:")
    for record in records:
        print(f"  {record}")
    
    # Simulate queries
    queries = [
        ("example.com", "A"),
        ("example.com", "AAAA"), 
        ("www.example.com", "CNAME"),
        ("example.com", "MX"),
        ("example.com", "NS"),
        ("example.com", "TXT")
    ]
    
    print(f"\nQuerying authoritative server:")
    for domain, record_type in queries:
        result = auth_server.query(domain, record_type)
        if result:
            print(f"  Query: {domain} {record_type} → {result.value}")
        else:
            print(f"  Query: {domain} {record_type} → NXDOMAIN")

def simulate_dns_load_balancing():
    """Simulate DNS-based load balancing"""
    print(f"\n=== DNS Load Balancing ===")
    
    # Create load balancer
    lb_server = DNSServer("lb.example.com", "load_balancer")
    
    # Add multiple A records for load balancing
    servers = [
        "192.0.2.10",
        "192.0.2.11", 
        "192.0.2.12",
        "192.0.2.13"
    ]
    
    for i, ip in enumerate(servers):
        record = DNSRecord("api.example.com", "A", ip, 60)  # Short TTL for load balancing
        lb_server.add_record(record)
    
    print(f"Load balancer configuration:")
    print(f"  Domain: api.example.com")
    print(f"  Servers: {servers}")
    print(f"  TTL: 60 seconds (short for dynamic load balancing)")
    
    # Simulate round-robin responses
    print(f"\nSimulating DNS round-robin responses:")
    for i in range(8):
        # Rotate through servers
        server_ip = servers[i % len(servers)]
        print(f"  Query {i+1}: api.example.com → {server_ip}")
        time.sleep(0.1)

def analyze_dns_performance():
    """Analyze DNS performance characteristics"""
    print(f"\n=== DNS Performance Analysis ===")
    
    # Simulate query times
    query_times = []
    
    scenarios = [
        ("Cache hit", 0.001, 0.002),
        ("Recursive query", 0.050, 0.200),
        ("Timeout/retry", 1.000, 2.000)
    ]
    
    for scenario, min_time, max_time in scenarios:
        times = [random.uniform(min_time, max_time) for _ in range(10)]
        avg_time = sum(times) / len(times)
        print(f"{scenario}:")
        print(f"  Average: {avg_time*1000:.1f}ms")
        print(f"  Range: {min_time*1000:.1f}-{max_time*1000:.1f}ms")
    
    # TTL impact analysis
    print(f"\nTTL Impact on Performance:")
    ttl_scenarios = [
        ("Static content", 3600, "1 hour"),
        ("Dynamic API", 300, "5 minutes"),
        ("Load balancing", 60, "1 minute"),
        ("Failover", 30, "30 seconds")
    ]
    
    for use_case, ttl, description in ttl_scenarios:
        cache_efficiency = min(95, 60 + (ttl / 60))  # Simplified model
        print(f"  {use_case}: TTL {description} → {cache_efficiency:.0f}% cache hit rate")

if __name__ == "__main__":
    # DNS resolution simulation
    simulate_dns_queries()
    
    # DNS record types
    demonstrate_dns_record_types()
    
    # Load balancing
    simulate_dns_load_balancing()
    
    # Performance analysis
    analyze_dns_performance()
