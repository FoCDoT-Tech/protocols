#!/usr/bin/env python3
"""
DNS for Microservices Architecture
Demonstrates service discovery, load balancing, and health checks using DNS
"""

import time
import random
import json
from collections import defaultdict

class ServiceRegistry:
    def __init__(self):
        self.services = defaultdict(list)
        self.health_checks = {}
        
    def register_service(self, service_name, instance_id, host, port, health_check_url=None):
        """Register a service instance"""
        instance = {
            'id': instance_id,
            'host': host,
            'port': port,
            'health_check_url': health_check_url,
            'status': 'healthy',
            'registered_at': time.time()
        }
        self.services[service_name].append(instance)
        print(f"Registered {service_name} instance: {host}:{port}")
        
    def deregister_service(self, service_name, instance_id):
        """Deregister a service instance"""
        instances = self.services[service_name]
        self.services[service_name] = [i for i in instances if i['id'] != instance_id]
        print(f"Deregistered {service_name} instance: {instance_id}")
        
    def get_healthy_instances(self, service_name):
        """Get all healthy instances of a service"""
        return [i for i in self.services[service_name] if i['status'] == 'healthy']
        
    def perform_health_checks(self):
        """Simulate health checks for all registered services"""
        print("\n=== Performing Health Checks ===")
        for service_name, instances in self.services.items():
            for instance in instances:
                # Simulate health check (90% success rate)
                is_healthy = random.random() < 0.9
                old_status = instance['status']
                instance['status'] = 'healthy' if is_healthy else 'unhealthy'
                
                if old_status != instance['status']:
                    print(f"  {service_name} {instance['id']}: {old_status} → {instance['status']}")

class DNSServiceDiscovery:
    def __init__(self, service_registry):
        self.registry = service_registry
        self.dns_cache = {}
        self.load_balancer_strategy = 'round_robin'
        self.round_robin_counters = defaultdict(int)
        
    def resolve_service(self, service_name):
        """Resolve service name to IP addresses"""
        healthy_instances = self.registry.get_healthy_instances(service_name)
        
        if not healthy_instances:
            print(f"✗ No healthy instances found for {service_name}")
            return []
            
        # Apply load balancing strategy
        if self.load_balancer_strategy == 'round_robin':
            return self._round_robin_select(service_name, healthy_instances)
        elif self.load_balancer_strategy == 'random':
            return [random.choice(healthy_instances)]
        else:
            return healthy_instances
            
    def _round_robin_select(self, service_name, instances):
        """Round-robin load balancing"""
        if not instances:
            return []
            
        counter = self.round_robin_counters[service_name]
        selected = instances[counter % len(instances)]
        self.round_robin_counters[service_name] += 1
        
        return [selected]
        
    def create_srv_record(self, service_name):
        """Create SRV record for service"""
        instances = self.registry.get_healthy_instances(service_name)
        srv_records = []
        
        for i, instance in enumerate(instances):
            # SRV format: priority weight port target
            priority = 10
            weight = 100 // len(instances)  # Equal weight distribution
            srv_record = f"{priority} {weight} {instance['port']} {instance['host']}"
            srv_records.append(srv_record)
            
        return srv_records

def simulate_microservices_deployment():
    """Simulate microservices deployment with DNS service discovery"""
    print("=== Microservices DNS Service Discovery ===\n")
    
    # Create service registry
    registry = ServiceRegistry()
    dns_sd = DNSServiceDiscovery(registry)
    
    # Register microservices
    services = [
        ("user-service", [
            ("user-1", "10.0.1.10", 8080),
            ("user-2", "10.0.1.11", 8080),
            ("user-3", "10.0.1.12", 8080)
        ]),
        ("payment-service", [
            ("payment-1", "10.0.2.10", 8081),
            ("payment-2", "10.0.2.11", 8081)
        ]),
        ("inventory-service", [
            ("inventory-1", "10.0.3.10", 8082),
            ("inventory-2", "10.0.3.11", 8082),
            ("inventory-3", "10.0.3.12", 8082),
            ("inventory-4", "10.0.3.13", 8082)
        ]),
        ("notification-service", [
            ("notification-1", "10.0.4.10", 8083)
        ])
    ]
    
    print("Registering microservices:")
    for service_name, instances in services:
        for instance_id, host, port in instances:
            registry.register_service(service_name, instance_id, host, port, f"http://{host}:{port}/health")
    
    print(f"\n=== Service Discovery Simulation ===")
    
    # Simulate service discovery requests
    for i in range(8):
        service_name = random.choice([s[0] for s in services])
        print(f"\nRequest {i+1}: Discovering {service_name}")
        
        instances = dns_sd.resolve_service(service_name)
        if instances:
            instance = instances[0]
            print(f"  Resolved to: {instance['host']}:{instance['port']}")
            print(f"  Load balancing: Round-robin")
        
        # Simulate health check failures
        if random.random() < 0.3:  # 30% chance of health check
            registry.perform_health_checks()
        
        time.sleep(0.1)

def demonstrate_dns_srv_records():
    """Demonstrate DNS SRV records for service discovery"""
    print(f"\n=== DNS SRV Records for Service Discovery ===\n")
    
    registry = ServiceRegistry()
    dns_sd = DNSServiceDiscovery(registry)
    
    # Register services with different priorities and weights
    services = [
        ("api-gateway", "gateway-1", "10.0.0.10", 80),
        ("api-gateway", "gateway-2", "10.0.0.11", 80),
        ("database", "db-primary", "10.0.5.10", 5432),
        ("database", "db-replica-1", "10.0.5.11", 5432),
        ("database", "db-replica-2", "10.0.5.12", 5432)
    ]
    
    for service_name, instance_id, host, port in services:
        registry.register_service(service_name, instance_id, host, port)
    
    # Generate SRV records
    for service_name in ["api-gateway", "database"]:
        srv_records = dns_sd.create_srv_record(service_name)
        print(f"SRV records for _{service_name}._tcp.example.com:")
        for i, record in enumerate(srv_records):
            print(f"  {record}")
        print()

def simulate_canary_deployment():
    """Simulate canary deployment using DNS traffic splitting"""
    print("=== Canary Deployment with DNS ===\n")
    
    registry = ServiceRegistry()
    
    # Deploy stable version
    print("1. Deploying stable version (v1.0):")
    stable_instances = [
        ("api-v1-1", "10.0.1.10", 8080),
        ("api-v1-2", "10.0.1.11", 8080),
        ("api-v1-3", "10.0.1.12", 8080)
    ]
    
    for instance_id, host, port in stable_instances:
        registry.register_service("api-service", instance_id, host, port)
        print(f"  Deployed {instance_id} at {host}:{port}")
    
    # Deploy canary version (5% traffic)
    print(f"\n2. Deploying canary version (v1.1) - 5% traffic:")
    canary_instance = ("api-v1.1-1", "10.0.1.20", 8080)
    registry.register_service("api-service-canary", canary_instance[0], canary_instance[1], canary_instance[2])
    print(f"  Deployed {canary_instance[0]} at {canary_instance[1]}:{canary_instance[2]}")
    
    # Simulate traffic distribution
    print(f"\n3. Traffic distribution simulation:")
    for i in range(20):
        # 95% to stable, 5% to canary
        if random.random() < 0.95:
            target = "api-service (stable v1.0)"
        else:
            target = "api-service-canary (canary v1.1)"
        
        print(f"  Request {i+1:2d}: → {target}")
    
    print(f"\n4. Monitoring canary metrics...")
    print(f"  Error rate: 0.1% (within threshold)")
    print(f"  Latency: 95ms (acceptable)")
    print(f"  ✓ Canary deployment successful")
    
    # Promote canary to stable
    print(f"\n5. Promoting canary to stable...")
    print(f"  Updating DNS records to point to v1.1")
    print(f"  Decommissioning v1.0 instances")

def analyze_dns_service_discovery_patterns():
    """Analyze different service discovery patterns"""
    print(f"\n=== Service Discovery Patterns ===\n")
    
    patterns = [
        {
            'name': 'Client-Side Discovery',
            'description': 'Client queries service registry directly',
            'pros': ['Simple', 'Low latency', 'Client controls load balancing'],
            'cons': ['Client complexity', 'Service registry dependency']
        },
        {
            'name': 'Server-Side Discovery', 
            'description': 'Load balancer queries service registry',
            'pros': ['Client simplicity', 'Centralized load balancing'],
            'cons': ['Additional network hop', 'Load balancer complexity']
        },
        {
            'name': 'Service Mesh Discovery',
            'description': 'Sidecar proxy handles service discovery',
            'pros': ['Language agnostic', 'Advanced traffic management'],
            'cons': ['Infrastructure complexity', 'Resource overhead']
        },
        {
            'name': 'DNS-Based Discovery',
            'description': 'Standard DNS resolution for service names',
            'pros': ['Universal support', 'Caching benefits', 'Simple integration'],
            'cons': ['Limited load balancing', 'TTL constraints']
        }
    ]
    
    for pattern in patterns:
        print(f"{pattern['name']}:")
        print(f"  Description: {pattern['description']}")
        print(f"  Pros: {', '.join(pattern['pros'])}")
        print(f"  Cons: {', '.join(pattern['cons'])}")
        print()

def benchmark_service_discovery_performance():
    """Benchmark service discovery performance"""
    print("=== Service Discovery Performance ===\n")
    
    # Simulate different discovery mechanisms
    mechanisms = [
        ('DNS Resolution', 0.005, 0.015),
        ('Service Registry API', 0.010, 0.030),
        ('Consul Discovery', 0.008, 0.025),
        ('Kubernetes DNS', 0.003, 0.010)
    ]
    
    print("Service Discovery Latency Comparison:")
    print(f"{'Mechanism':<20} {'Avg Latency':<12} {'95th Percentile'}")
    print("-" * 50)
    
    for mechanism, avg_latency, p95_latency in mechanisms:
        print(f"{mechanism:<20} {avg_latency*1000:6.1f}ms{'':<5} {p95_latency*1000:6.1f}ms")
    
    # Cache hit rates
    print(f"\nDNS Cache Hit Rates:")
    cache_scenarios = [
        ('Local DNS cache', 95),
        ('Service mesh cache', 88),
        ('Application cache', 75),
        ('No caching', 0)
    ]
    
    for scenario, hit_rate in cache_scenarios:
        print(f"  {scenario:<20}: {hit_rate:2d}%")

if __name__ == "__main__":
    # Microservices deployment simulation
    simulate_microservices_deployment()
    
    # SRV records demonstration
    demonstrate_dns_srv_records()
    
    # Canary deployment
    simulate_canary_deployment()
    
    # Service discovery patterns
    analyze_dns_service_discovery_patterns()
    
    # Performance benchmarks
    benchmark_service_discovery_performance()
