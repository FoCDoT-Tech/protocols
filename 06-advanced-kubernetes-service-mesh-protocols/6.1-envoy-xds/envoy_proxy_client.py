#!/usr/bin/env python3
"""
Envoy Proxy Client Implementation
Demonstrates xDS client behavior and configuration application
"""

import time
import threading
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib

class ConfigState(Enum):
    """Configuration application state"""
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    WARMING = "warming"

@dataclass
class ListenerConfig:
    """Envoy listener configuration"""
    name: str
    address: str
    port: int
    filter_chains: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "address": {"socket_address": {"address": self.address, "port_value": self.port}},
            "filter_chains": self.filter_chains
        }

@dataclass
class ClusterConfig:
    """Envoy cluster configuration"""
    name: str
    endpoints: List[Dict[str, Any]] = field(default_factory=list)
    connect_timeout: str = "0.25s"
    type: str = "STRICT_DNS"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "connect_timeout": self.connect_timeout,
            "type": self.type,
            "load_assignment": {
                "cluster_name": self.name,
                "endpoints": [{"lb_endpoints": self.endpoints}]
            }
        }

@dataclass
class RouteConfig:
    """Envoy route configuration"""
    name: str
    virtual_hosts: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "virtual_hosts": self.virtual_hosts
        }

class ConfigurationManager:
    """
    Manages Envoy proxy configuration state
    Handles configuration validation and application
    """
    
    def __init__(self, proxy_id: str):
        self.proxy_id = proxy_id
        self.listeners: Dict[str, ListenerConfig] = {}
        self.clusters: Dict[str, ClusterConfig] = {}
        self.routes: Dict[str, RouteConfig] = {}
        self.endpoints: Dict[str, List[Dict[str, Any]]] = {}
        self.config_versions: Dict[str, str] = {}
        self.config_state = ConfigState.PENDING
        self.lock = threading.Lock()
        
        print(f"[Config Manager {proxy_id}] Initialized")
    
    def apply_listener_config(self, listeners: List[Dict[str, Any]], version: str) -> bool:
        """Apply listener configuration"""
        try:
            with self.lock:
                new_listeners = {}
                
                for listener_data in listeners:
                    name = listener_data["name"]
                    address_info = listener_data["address"]["socket_address"]
                    
                    listener = ListenerConfig(
                        name=name,
                        address=address_info["address"],
                        port=address_info["port_value"],
                        filter_chains=listener_data.get("filter_chains", [])
                    )
                    
                    new_listeners[name] = listener
                
                # Validate configuration
                if self._validate_listeners(new_listeners):
                    self.listeners = new_listeners
                    self.config_versions["listeners"] = version
                    print(f"[Config Manager {self.proxy_id}] Applied {len(listeners)} listeners")
                    return True
                else:
                    print(f"[Config Manager {self.proxy_id}] Listener validation failed")
                    return False
                    
        except Exception as e:
            print(f"[Config Manager {self.proxy_id}] Listener config error: {e}")
            return False
    
    def apply_cluster_config(self, clusters: List[Dict[str, Any]], version: str) -> bool:
        """Apply cluster configuration"""
        try:
            with self.lock:
                new_clusters = {}
                
                for cluster_data in clusters:
                    name = cluster_data["name"]
                    load_assignment = cluster_data.get("load_assignment", {})
                    endpoints = []
                    
                    if "endpoints" in load_assignment:
                        for endpoint_group in load_assignment["endpoints"]:
                            for lb_endpoint in endpoint_group.get("lb_endpoints", []):
                                endpoints.append(lb_endpoint)
                    
                    cluster = ClusterConfig(
                        name=name,
                        endpoints=endpoints,
                        connect_timeout=cluster_data.get("connect_timeout", "0.25s"),
                        type=cluster_data.get("type", "STRICT_DNS")
                    )
                    
                    new_clusters[name] = cluster
                
                # Validate configuration
                if self._validate_clusters(new_clusters):
                    self.clusters = new_clusters
                    self.config_versions["clusters"] = version
                    print(f"[Config Manager {self.proxy_id}] Applied {len(clusters)} clusters")
                    return True
                else:
                    print(f"[Config Manager {self.proxy_id}] Cluster validation failed")
                    return False
                    
        except Exception as e:
            print(f"[Config Manager {self.proxy_id}] Cluster config error: {e}")
            return False
    
    def apply_route_config(self, routes: List[Dict[str, Any]], version: str) -> bool:
        """Apply route configuration"""
        try:
            with self.lock:
                new_routes = {}
                
                for route_data in routes:
                    name = route_data["name"]
                    virtual_hosts = route_data.get("virtual_hosts", [])
                    
                    route = RouteConfig(
                        name=name,
                        virtual_hosts=virtual_hosts
                    )
                    
                    new_routes[name] = route
                
                # Validate configuration
                if self._validate_routes(new_routes):
                    self.routes = new_routes
                    self.config_versions["routes"] = version
                    print(f"[Config Manager {self.proxy_id}] Applied {len(routes)} route configs")
                    return True
                else:
                    print(f"[Config Manager {self.proxy_id}] Route validation failed")
                    return False
                    
        except Exception as e:
            print(f"[Config Manager {self.proxy_id}] Route config error: {e}")
            return False
    
    def apply_endpoint_config(self, endpoints: List[Dict[str, Any]], version: str) -> bool:
        """Apply endpoint configuration"""
        try:
            with self.lock:
                new_endpoints = {}
                
                for endpoint_data in endpoints:
                    cluster_name = endpoint_data["cluster_name"]
                    endpoint_list = []
                    
                    for endpoint_group in endpoint_data.get("endpoints", []):
                        for lb_endpoint in endpoint_group.get("lb_endpoints", []):
                            endpoint_list.append(lb_endpoint)
                    
                    new_endpoints[cluster_name] = endpoint_list
                
                # Update cluster endpoints
                for cluster_name, endpoint_list in new_endpoints.items():
                    if cluster_name in self.clusters:
                        self.clusters[cluster_name].endpoints = endpoint_list
                
                self.endpoints = new_endpoints
                self.config_versions["endpoints"] = version
                print(f"[Config Manager {self.proxy_id}] Applied endpoints for {len(new_endpoints)} clusters")
                return True
                
        except Exception as e:
            print(f"[Config Manager {self.proxy_id}] Endpoint config error: {e}")
            return False
    
    def _validate_listeners(self, listeners: Dict[str, ListenerConfig]) -> bool:
        """Validate listener configuration"""
        # Check for port conflicts
        ports = set()
        for listener in listeners.values():
            if listener.port in ports:
                print(f"[Config Manager {self.proxy_id}] Port conflict: {listener.port}")
                return False
            ports.add(listener.port)
        
        return True
    
    def _validate_clusters(self, clusters: Dict[str, ClusterConfig]) -> bool:
        """Validate cluster configuration"""
        # Basic validation - ensure clusters have endpoints
        for cluster in clusters.values():
            if not cluster.endpoints:
                print(f"[Config Manager {self.proxy_id}] Cluster {cluster.name} has no endpoints")
        
        return True
    
    def _validate_routes(self, routes: Dict[str, RouteConfig]) -> bool:
        """Validate route configuration"""
        # Check that referenced clusters exist
        for route in routes.values():
            for vhost in route.virtual_hosts:
                for route_rule in vhost.get("routes", []):
                    if "route" in route_rule and "cluster" in route_rule["route"]:
                        cluster_name = route_rule["route"]["cluster"]
                        if cluster_name not in self.clusters:
                            print(f"[Config Manager {self.proxy_id}] Route references unknown cluster: {cluster_name}")
                            return False
        
        return True
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get current configuration summary"""
        with self.lock:
            return {
                "proxy_id": self.proxy_id,
                "listeners": len(self.listeners),
                "clusters": len(self.clusters),
                "routes": len(self.routes),
                "endpoint_groups": len(self.endpoints),
                "versions": self.config_versions.copy(),
                "state": self.config_state.value
            }

class TrafficManager:
    """
    Simulates Envoy traffic handling with applied configuration
    Demonstrates request routing and load balancing
    """
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.request_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "requests_by_cluster": {}
        }
        
        print(f"[Traffic Manager] Initialized for {config_manager.proxy_id}")
    
    def handle_request(self, method: str, path: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle incoming HTTP request"""
        self.request_stats["total_requests"] += 1
        
        try:
            # Find matching route
            route_match = self._find_route_match(path, headers)
            if not route_match:
                self.request_stats["failed_requests"] += 1
                return {"status": 404, "error": "No route match"}
            
            cluster_name = route_match["cluster"]
            
            # Select endpoint
            endpoint = self._select_endpoint(cluster_name)
            if not endpoint:
                self.request_stats["failed_requests"] += 1
                return {"status": 503, "error": "No healthy endpoints"}
            
            # Simulate request forwarding
            response = self._forward_request(endpoint, method, path, headers)
            
            # Update stats
            self.request_stats["successful_requests"] += 1
            if cluster_name not in self.request_stats["requests_by_cluster"]:
                self.request_stats["requests_by_cluster"][cluster_name] = 0
            self.request_stats["requests_by_cluster"][cluster_name] += 1
            
            return response
            
        except Exception as e:
            self.request_stats["failed_requests"] += 1
            return {"status": 500, "error": str(e)}
    
    def _find_route_match(self, path: str, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Find matching route for request"""
        for route in self.config_manager.routes.values():
            for vhost in route.virtual_hosts:
                # Check domain match
                host = headers.get("host", "*")
                if not self._domain_matches(host, vhost.get("domains", ["*"])):
                    continue
                
                # Check route rules
                for route_rule in vhost.get("routes", []):
                    if self._path_matches(path, route_rule.get("match", {})):
                        return route_rule.get("route", {})
        
        return None
    
    def _domain_matches(self, host: str, domains: List[str]) -> bool:
        """Check if host matches domain patterns"""
        return "*" in domains or host in domains
    
    def _path_matches(self, path: str, match: Dict[str, Any]) -> bool:
        """Check if path matches route match criteria"""
        if "prefix" in match:
            return path.startswith(match["prefix"])
        elif "path" in match:
            return path == match["path"]
        elif "regex" in match:
            # Simplified regex matching
            return match["regex"] in path
        
        return False
    
    def _select_endpoint(self, cluster_name: str) -> Optional[Dict[str, Any]]:
        """Select endpoint from cluster (round-robin simulation)"""
        if cluster_name not in self.config_manager.clusters:
            return None
        
        cluster = self.config_manager.clusters[cluster_name]
        if not cluster.endpoints:
            return None
        
        # Simple round-robin selection
        endpoint_index = self.request_stats["total_requests"] % len(cluster.endpoints)
        return cluster.endpoints[endpoint_index]
    
    def _forward_request(self, endpoint: Dict[str, Any], method: str, 
                        path: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Simulate request forwarding to upstream"""
        endpoint_addr = endpoint["endpoint"]["address"]["socket_address"]
        
        # Simulate network delay
        time.sleep(0.001)  # 1ms simulated latency
        
        return {
            "status": 200,
            "upstream": f"{endpoint_addr['address']}:{endpoint_addr['port_value']}",
            "method": method,
            "path": path,
            "response_time_ms": 1
        }
    
    def get_traffic_stats(self) -> Dict[str, Any]:
        """Get traffic statistics"""
        return self.request_stats.copy()

class EnvoyProxyClient:
    """
    Complete Envoy proxy client implementation
    Integrates configuration management and traffic handling
    """
    
    def __init__(self, proxy_id: str, cluster: str = "demo"):
        self.proxy_id = proxy_id
        self.cluster = cluster
        self.config_manager = ConfigurationManager(proxy_id)
        self.traffic_manager = TrafficManager(self.config_manager)
        self.running = False
        
        print(f"[Envoy Client {proxy_id}] Initialized")
    
    def start(self):
        """Start Envoy proxy client"""
        self.running = True
        
        # Initialize with default configuration
        self._apply_default_config()
        
        print(f"[Envoy Client {self.proxy_id}] Started with default configuration")
    
    def stop(self):
        """Stop Envoy proxy client"""
        self.running = False
        print(f"[Envoy Client {self.proxy_id}] Stopped")
    
    def _apply_default_config(self):
        """Apply default configuration"""
        # Default listener
        listeners = [{
            "name": "listener_0",
            "address": {"socket_address": {"address": "0.0.0.0", "port_value": 10000}},
            "filter_chains": [{
                "filters": [{
                    "name": "envoy.filters.network.http_connection_manager",
                    "typed_config": {
                        "stat_prefix": "ingress_http",
                        "route_config": {"name": "local_route"}
                    }
                }]
            }]
        }]
        
        # Default cluster
        clusters = [{
            "name": "service_cluster",
            "connect_timeout": "0.25s",
            "type": "STRICT_DNS",
            "load_assignment": {
                "cluster_name": "service_cluster",
                "endpoints": [{
                    "lb_endpoints": [{
                        "endpoint": {
                            "address": {"socket_address": {"address": "127.0.0.1", "port_value": 8080}}
                        }
                    }]
                }]
            }
        }]
        
        # Default routes
        routes = [{
            "name": "local_route",
            "virtual_hosts": [{
                "name": "local_service",
                "domains": ["*"],
                "routes": [{
                    "match": {"prefix": "/"},
                    "route": {"cluster": "service_cluster"}
                }]
            }]
        }]
        
        # Apply configurations
        self.config_manager.apply_listener_config(listeners, "1")
        self.config_manager.apply_cluster_config(clusters, "1")
        self.config_manager.apply_route_config(routes, "1")
    
    def update_configuration(self, config_type: str, resources: List[Dict[str, Any]], version: str) -> bool:
        """Update configuration from xDS"""
        if config_type == "listeners":
            return self.config_manager.apply_listener_config(resources, version)
        elif config_type == "clusters":
            return self.config_manager.apply_cluster_config(resources, version)
        elif config_type == "routes":
            return self.config_manager.apply_route_config(resources, version)
        elif config_type == "endpoints":
            return self.config_manager.apply_endpoint_config(resources, version)
        else:
            print(f"[Envoy Client {self.proxy_id}] Unknown config type: {config_type}")
            return False
    
    def handle_request(self, method: str, path: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Handle incoming request"""
        if headers is None:
            headers = {}
        
        return self.traffic_manager.handle_request(method, path, headers)
    
    def get_status(self) -> Dict[str, Any]:
        """Get proxy status"""
        config_summary = self.config_manager.get_configuration_summary()
        traffic_stats = self.traffic_manager.get_traffic_stats()
        
        return {
            "proxy_id": self.proxy_id,
            "cluster": self.cluster,
            "running": self.running,
            "configuration": config_summary,
            "traffic": traffic_stats
        }

def demonstrate_envoy_proxy_client():
    """Demonstrate Envoy proxy client functionality"""
    print("=== Envoy Proxy Client Demo ===")
    
    # Create proxy client
    proxy = EnvoyProxyClient("demo-proxy-1")
    proxy.start()
    
    print("\n1. Initial proxy status...")
    status = proxy.get_status()
    print(f"   Listeners: {status['configuration']['listeners']}")
    print(f"   Clusters: {status['configuration']['clusters']}")
    print(f"   Routes: {status['configuration']['routes']}")
    
    # Simulate some requests
    print("\n2. Simulating HTTP requests...")
    requests = [
        ("GET", "/", {"host": "example.com"}),
        ("POST", "/api/users", {"host": "api.example.com"}),
        ("GET", "/health", {"host": "example.com"}),
        ("GET", "/metrics", {"host": "example.com"})
    ]
    
    for method, path, headers in requests:
        response = proxy.handle_request(method, path, headers)
        print(f"   {method} {path} -> {response['status']} ({response.get('upstream', 'no upstream')})")
    
    # Update configuration
    print("\n3. Updating configuration...")
    new_clusters = [{
        "name": "api_cluster",
        "connect_timeout": "0.5s",
        "type": "STRICT_DNS",
        "load_assignment": {
            "cluster_name": "api_cluster",
            "endpoints": [{
                "lb_endpoints": [
                    {"endpoint": {"address": {"socket_address": {"address": "10.0.1.10", "port_value": 8080}}}},
                    {"endpoint": {"address": {"socket_address": {"address": "10.0.1.20", "port_value": 8080}}}}
                ]
            }]
        }
    }]
    
    proxy.update_configuration("clusters", new_clusters, "2")
    
    # Update routes
    new_routes = [{
        "name": "local_route",
        "virtual_hosts": [{
            "name": "local_service",
            "domains": ["*"],
            "routes": [
                {"match": {"prefix": "/api/"}, "route": {"cluster": "api_cluster"}},
                {"match": {"prefix": "/"}, "route": {"cluster": "service_cluster"}}
            ]
        }]
    }]
    
    proxy.update_configuration("routes", new_routes, "2")
    
    # Test updated configuration
    print("\n4. Testing updated configuration...")
    test_requests = [
        ("GET", "/api/users", {"host": "example.com"}),
        ("GET", "/", {"host": "example.com"})
    ]
    
    for method, path, headers in test_requests:
        response = proxy.handle_request(method, path, headers)
        print(f"   {method} {path} -> {response['status']} ({response.get('upstream', 'no upstream')})")
    
    # Show final status
    print("\n5. Final proxy status...")
    status = proxy.get_status()
    print(f"   Total requests: {status['traffic']['total_requests']}")
    print(f"   Successful: {status['traffic']['successful_requests']}")
    print(f"   Failed: {status['traffic']['failed_requests']}")
    print(f"   Requests by cluster: {status['traffic']['requests_by_cluster']}")
    
    proxy.stop()
    
    print("\n=== Envoy Proxy Client Demo Complete ===")

if __name__ == "__main__":
    demonstrate_envoy_proxy_client()
