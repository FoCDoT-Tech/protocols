#!/usr/bin/env python3
"""
Kubernetes Network Policy Implementation
Demonstrates traffic control and security policies for CNI
"""

import json
import time
import ipaddress
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum

class PolicyType(Enum):
    """Network policy types"""
    INGRESS = "Ingress"
    EGRESS = "Egress"

class Protocol(Enum):
    """Network protocols"""
    TCP = "TCP"
    UDP = "UDP"
    SCTP = "SCTP"

@dataclass
class NetworkPolicyPort:
    """Network policy port specification"""
    port: int
    protocol: Protocol = Protocol.TCP
    end_port: Optional[int] = None

@dataclass
class NetworkPolicyPeer:
    """Network policy peer specification"""
    pod_selector: Dict[str, str] = field(default_factory=dict)
    namespace_selector: Dict[str, str] = field(default_factory=dict)
    ip_block: Optional[str] = None
    except_ips: List[str] = field(default_factory=list)

@dataclass
class NetworkPolicyRule:
    """Network policy rule"""
    policy_type: PolicyType
    ports: List[NetworkPolicyPort] = field(default_factory=list)
    peers: List[NetworkPolicyPeer] = field(default_factory=list)

@dataclass
class NetworkPolicy:
    """Kubernetes Network Policy"""
    name: str
    namespace: str
    pod_selector: Dict[str, str]
    policy_types: List[PolicyType]
    ingress_rules: List[NetworkPolicyRule] = field(default_factory=list)
    egress_rules: List[NetworkPolicyRule] = field(default_factory=list)

class NetworkPolicyEngine:
    """
    Network Policy Engine
    Enforces Kubernetes NetworkPolicy rules
    """
    
    def __init__(self):
        self.policies: Dict[str, NetworkPolicy] = {}
        self.pod_registry: Dict[str, Dict[str, Any]] = {}
        self.traffic_log: List[Dict[str, Any]] = []
        
        print("[Policy Engine] Initialized")
    
    def register_pod(self, pod_id: str, labels: Dict[str, str], 
                    namespace: str, ip_address: str):
        """Register pod with policy engine"""
        self.pod_registry[pod_id] = {
            "labels": labels,
            "namespace": namespace,
            "ip_address": ip_address
        }
        print(f"[Policy Engine] Registered pod {pod_id[:12]} in namespace {namespace}")
    
    def add_network_policy(self, policy: NetworkPolicy):
        """Add network policy"""
        policy_key = f"{policy.namespace}/{policy.name}"
        self.policies[policy_key] = policy
        print(f"[Policy Engine] Added policy {policy_key}")
    
    def remove_network_policy(self, name: str, namespace: str):
        """Remove network policy"""
        policy_key = f"{namespace}/{name}"
        if policy_key in self.policies:
            del self.policies[policy_key]
            print(f"[Policy Engine] Removed policy {policy_key}")
    
    def _matches_selector(self, labels: Dict[str, str], 
                         selector: Dict[str, str]) -> bool:
        """Check if labels match selector"""
        if not selector:  # Empty selector matches all
            return True
        
        for key, value in selector.items():
            if labels.get(key) != value:
                return False
        return True
    
    def _get_applicable_policies(self, pod_id: str) -> List[NetworkPolicy]:
        """Get policies applicable to pod"""
        if pod_id not in self.pod_registry:
            return []
        
        pod_info = self.pod_registry[pod_id]
        applicable_policies = []
        
        for policy in self.policies.values():
            # Check if policy applies to pod's namespace
            if policy.namespace != pod_info["namespace"]:
                continue
            
            # Check if pod matches policy selector
            if self._matches_selector(pod_info["labels"], policy.pod_selector):
                applicable_policies.append(policy)
        
        return applicable_policies
    
    def _check_peer_match(self, source_pod: str, target_pod: str, 
                         peer: NetworkPolicyPeer) -> bool:
        """Check if traffic matches peer specification"""
        if source_pod not in self.pod_registry or target_pod not in self.pod_registry:
            return False
        
        source_info = self.pod_registry[source_pod]
        target_info = self.pod_registry[target_pod]
        
        # Check pod selector
        if peer.pod_selector:
            if not self._matches_selector(source_info["labels"], peer.pod_selector):
                return False
        
        # Check namespace selector
        if peer.namespace_selector:
            # For simplicity, assume namespace has labels matching its name
            namespace_labels = {"name": source_info["namespace"]}
            if not self._matches_selector(namespace_labels, peer.namespace_selector):
                return False
        
        # Check IP block
        if peer.ip_block:
            source_ip = ipaddress.IPv4Address(source_info["ip_address"])
            allowed_network = ipaddress.IPv4Network(peer.ip_block)
            
            if source_ip not in allowed_network:
                return False
            
            # Check exceptions
            for except_ip in peer.except_ips:
                except_network = ipaddress.IPv4Network(except_ip)
                if source_ip in except_network:
                    return False
        
        return True
    
    def _check_port_match(self, target_port: int, protocol: Protocol,
                         policy_ports: List[NetworkPolicyPort]) -> bool:
        """Check if traffic matches port specification"""
        if not policy_ports:  # Empty ports list allows all ports
            return True
        
        for policy_port in policy_ports:
            if policy_port.protocol != protocol:
                continue
            
            if policy_port.end_port:
                # Port range
                if policy_port.port <= target_port <= policy_port.end_port:
                    return True
            else:
                # Single port
                if policy_port.port == target_port:
                    return True
        
        return False
    
    def check_traffic_allowed(self, source_pod: str, target_pod: str,
                            target_port: int, protocol: Protocol = Protocol.TCP) -> bool:
        """Check if traffic is allowed by network policies"""
        if target_pod not in self.pod_registry:
            return False
        
        # Get applicable policies for target pod
        applicable_policies = self._get_applicable_policies(target_pod)
        
        if not applicable_policies:
            # No policies apply - default allow
            return True
        
        # Check ingress policies
        ingress_policies = [p for p in applicable_policies 
                          if PolicyType.INGRESS in p.policy_types]
        
        if ingress_policies:
            # At least one ingress policy exists - default deny
            ingress_allowed = False
            
            for policy in ingress_policies:
                for rule in policy.ingress_rules:
                    # Check port match
                    if not self._check_port_match(target_port, protocol, rule.ports):
                        continue
                    
                    # Check peer match
                    if not rule.peers:
                        # Empty peers list allows all sources
                        ingress_allowed = True
                        break
                    
                    for peer in rule.peers:
                        if self._check_peer_match(source_pod, target_pod, peer):
                            ingress_allowed = True
                            break
                    
                    if ingress_allowed:
                        break
                
                if ingress_allowed:
                    break
            
            if not ingress_allowed:
                self._log_traffic(source_pod, target_pod, target_port, protocol, False, "Ingress denied")
                return False
        
        # Log allowed traffic
        self._log_traffic(source_pod, target_pod, target_port, protocol, True, "Allowed")
        return True
    
    def _log_traffic(self, source_pod: str, target_pod: str, target_port: int,
                    protocol: Protocol, allowed: bool, reason: str):
        """Log traffic decision"""
        log_entry = {
            "timestamp": time.time(),
            "source_pod": source_pod,
            "target_pod": target_pod,
            "target_port": target_port,
            "protocol": protocol.value,
            "allowed": allowed,
            "reason": reason
        }
        
        self.traffic_log.append(log_entry)
        
        status = "ALLOW" if allowed else "DENY"
        print(f"[Policy Engine] {status}: {source_pod[:12]} -> {target_pod[:12]}:{target_port}/{protocol.value} ({reason})")
    
    def get_traffic_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent traffic log entries"""
        return self.traffic_log[-limit:]
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of active policies"""
        summary = {
            "total_policies": len(self.policies),
            "policies_by_namespace": {},
            "total_pods": len(self.pod_registry)
        }
        
        for policy in self.policies.values():
            namespace = policy.namespace
            if namespace not in summary["policies_by_namespace"]:
                summary["policies_by_namespace"][namespace] = 0
            summary["policies_by_namespace"][namespace] += 1
        
        return summary

def demonstrate_network_policy():
    """Demonstrate network policy enforcement"""
    print("=== Network Policy Demo ===")
    
    # Initialize policy engine
    policy_engine = NetworkPolicyEngine()
    
    # Register pods
    print("\n1. Registering pods...")
    pods = [
        {
            "id": "pod-web-frontend-abc123",
            "labels": {"app": "web", "tier": "frontend"},
            "namespace": "production",
            "ip": "10.244.1.10"
        },
        {
            "id": "pod-api-backend-def456", 
            "labels": {"app": "api", "tier": "backend"},
            "namespace": "production",
            "ip": "10.244.1.20"
        },
        {
            "id": "pod-database-ghi789",
            "labels": {"app": "postgres", "tier": "database"},
            "namespace": "production", 
            "ip": "10.244.1.30"
        },
        {
            "id": "pod-monitoring-jkl012",
            "labels": {"app": "prometheus", "tier": "monitoring"},
            "namespace": "monitoring",
            "ip": "10.244.2.10"
        }
    ]
    
    for pod in pods:
        policy_engine.register_pod(pod["id"], pod["labels"], pod["namespace"], pod["ip"])
    
    # Create network policies
    print("\n2. Creating network policies...")
    
    # Policy 1: Allow web -> api on port 8080
    web_to_api_policy = NetworkPolicy(
        name="allow-web-to-api",
        namespace="production",
        pod_selector={"app": "api"},
        policy_types=[PolicyType.INGRESS],
        ingress_rules=[
            NetworkPolicyRule(
                policy_type=PolicyType.INGRESS,
                ports=[NetworkPolicyPort(port=8080, protocol=Protocol.TCP)],
                peers=[NetworkPolicyPeer(pod_selector={"app": "web"})]
            )
        ]
    )
    
    # Policy 2: Allow api -> database on port 5432
    api_to_db_policy = NetworkPolicy(
        name="allow-api-to-db",
        namespace="production", 
        pod_selector={"app": "postgres"},
        policy_types=[PolicyType.INGRESS],
        ingress_rules=[
            NetworkPolicyRule(
                policy_type=PolicyType.INGRESS,
                ports=[NetworkPolicyPort(port=5432, protocol=Protocol.TCP)],
                peers=[NetworkPolicyPeer(pod_selector={"app": "api"})]
            )
        ]
    )
    
    # Policy 3: Allow monitoring access from monitoring namespace
    monitoring_policy = NetworkPolicy(
        name="allow-monitoring",
        namespace="production",
        pod_selector={},  # Apply to all pods
        policy_types=[PolicyType.INGRESS],
        ingress_rules=[
            NetworkPolicyRule(
                policy_type=PolicyType.INGRESS,
                ports=[NetworkPolicyPort(port=9090, protocol=Protocol.TCP)],
                peers=[NetworkPolicyPeer(namespace_selector={"name": "monitoring"})]
            )
        ]
    )
    
    policy_engine.add_network_policy(web_to_api_policy)
    policy_engine.add_network_policy(api_to_db_policy)
    policy_engine.add_network_policy(monitoring_policy)
    
    # Test traffic scenarios
    print("\n3. Testing traffic scenarios...")
    
    test_cases = [
        # Allowed traffic
        ("pod-web-frontend-abc123", "pod-api-backend-def456", 8080, Protocol.TCP),
        ("pod-api-backend-def456", "pod-database-ghi789", 5432, Protocol.TCP),
        ("pod-monitoring-jkl012", "pod-web-frontend-abc123", 9090, Protocol.TCP),
        
        # Denied traffic
        ("pod-web-frontend-abc123", "pod-database-ghi789", 5432, Protocol.TCP),  # Direct web->db
        ("pod-web-frontend-abc123", "pod-api-backend-def456", 3000, Protocol.TCP),  # Wrong port
        ("pod-database-ghi789", "pod-api-backend-def456", 8080, Protocol.TCP),  # Reverse direction
    ]
    
    for source, target, port, protocol in test_cases:
        allowed = policy_engine.check_traffic_allowed(source, target, port, protocol)
        time.sleep(0.1)
    
    # Show policy summary
    print("\n4. Policy summary...")
    summary = policy_engine.get_policy_summary()
    print(f"Total policies: {summary['total_policies']}")
    print(f"Total pods: {summary['total_pods']}")
    for namespace, count in summary["policies_by_namespace"].items():
        print(f"  {namespace}: {count} policies")
    
    # Show traffic log
    print("\n5. Recent traffic log...")
    traffic_log = policy_engine.get_traffic_log(8)
    for entry in traffic_log:
        status = "ALLOW" if entry["allowed"] else "DENY"
        print(f"  {status}: {entry['source_pod'][:12]} -> {entry['target_pod'][:12]}:{entry['target_port']}")
    
    print("\n=== Network Policy Demo Complete ===")

if __name__ == "__main__":
    demonstrate_network_policy()
