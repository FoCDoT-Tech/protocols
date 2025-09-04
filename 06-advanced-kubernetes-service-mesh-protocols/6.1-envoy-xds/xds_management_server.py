#!/usr/bin/env python3
"""
Envoy xDS Management Server Implementation
Demonstrates gRPC-based dynamic configuration distribution for service mesh
"""

import time
import threading
import json
import hashlib
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

class ResourceType(Enum):
    """xDS resource types"""
    LISTENER = "type.googleapis.com/envoy.config.listener.v3.Listener"
    ROUTE = "type.googleapis.com/envoy.config.route.v3.RouteConfiguration"
    CLUSTER = "type.googleapis.com/envoy.config.cluster.v3.Cluster"
    ENDPOINT = "type.googleapis.com/envoy.config.endpoint.v3.ClusterLoadAssignment"
    SECRET = "type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.Secret"

class ResponseType(Enum):
    """xDS response types"""
    ACK = "ACK"
    NACK = "NACK"

@dataclass
class XdsResource:
    """Individual xDS resource"""
    name: str
    type_url: str
    version: str
    resource: Dict[str, Any]
    last_updated: float = field(default_factory=time.time)

@dataclass
class XdsSnapshot:
    """Complete configuration snapshot for an Envoy node"""
    version: str
    listeners: Dict[str, XdsResource] = field(default_factory=dict)
    routes: Dict[str, XdsResource] = field(default_factory=dict)
    clusters: Dict[str, XdsResource] = field(default_factory=dict)
    endpoints: Dict[str, XdsResource] = field(default_factory=dict)
    secrets: Dict[str, XdsResource] = field(default_factory=dict)
    
    def get_resources(self, type_url: str) -> Dict[str, XdsResource]:
        """Get resources by type"""
        type_mapping = {
            ResourceType.LISTENER.value: self.listeners,
            ResourceType.ROUTE.value: self.routes,
            ResourceType.CLUSTER.value: self.clusters,
            ResourceType.ENDPOINT.value: self.endpoints,
            ResourceType.SECRET.value: self.secrets
        }
        return type_mapping.get(type_url, {})

@dataclass
class EnvoyNode:
    """Envoy proxy node information"""
    id: str
    cluster: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    locality: Optional[Dict[str, str]] = None
    build_version: str = "unknown"
    
    def __post_init__(self):
        if self.locality is None:
            self.locality = {"region": "us-west-2", "zone": "us-west-2a"}

@dataclass
class XdsSubscription:
    """Active xDS subscription from Envoy proxy"""
    node: EnvoyNode
    type_url: str
    resource_names: Set[str] = field(default_factory=set)
    version_info: str = ""
    response_nonce: str = ""
    last_request_time: float = field(default_factory=time.time)
    error_detail: Optional[str] = None

class ConfigurationStore:
    """
    Stores and manages xDS configuration snapshots
    Simulates integration with Kubernetes API and service discovery
    """
    
    def __init__(self):
        self.snapshots: Dict[str, XdsSnapshot] = {}
        self.version_counter = 0
        self.lock = threading.Lock()
        
        # Initialize with default configuration
        self._create_default_snapshot()
        
        print("[Config Store] Initialized with default configuration")
    
    def _create_default_snapshot(self):
        """Create default configuration snapshot"""
        version = self._next_version()
        snapshot = XdsSnapshot(version=version)
        
        # Default listener for HTTP traffic
        listener = XdsResource(
            name="listener_0",
            type_url=ResourceType.LISTENER.value,
            version=version,
            resource={
                "name": "listener_0",
                "address": {
                    "socket_address": {
                        "address": "0.0.0.0",
                        "port_value": 10000
                    }
                },
                "filter_chains": [{
                    "filters": [{
                        "name": "envoy.filters.network.http_connection_manager",
                        "typed_config": {
                            "@type": "type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager",
                            "stat_prefix": "ingress_http",
                            "route_config": {
                                "name": "local_route",
                                "virtual_hosts": [{
                                    "name": "local_service",
                                    "domains": ["*"],
                                    "routes": [{
                                        "match": {"prefix": "/"},
                                        "route": {"cluster": "service_cluster"}
                                    }]
                                }]
                            },
                            "http_filters": [{
                                "name": "envoy.filters.http.router"
                            }]
                        }
                    }]
                }]
            }
        )
        snapshot.listeners[listener.name] = listener
        
        # Default cluster
        cluster = XdsResource(
            name="service_cluster",
            type_url=ResourceType.CLUSTER.value,
            version=version,
            resource={
                "name": "service_cluster",
                "connect_timeout": "0.25s",
                "type": "LOGICAL_DNS",
                "dns_lookup_family": "V4_ONLY",
                "load_assignment": {
                    "cluster_name": "service_cluster",
                    "endpoints": [{
                        "lb_endpoints": [{
                            "endpoint": {
                                "address": {
                                    "socket_address": {
                                        "address": "127.0.0.1",
                                        "port_value": 8080
                                    }
                                }
                            }
                        }]
                    }]
                }
            }
        )
        snapshot.clusters[cluster.name] = cluster
        
        # Store default snapshot for all nodes
        self.snapshots["default"] = snapshot
    
    def _next_version(self) -> str:
        """Generate next configuration version"""
        with self.lock:
            self.version_counter += 1
            return str(self.version_counter)
    
    def get_snapshot(self, node_id: str) -> Optional[XdsSnapshot]:
        """Get configuration snapshot for node"""
        # For demo, all nodes get the same configuration
        return self.snapshots.get("default")
    
    def update_service_endpoints(self, service_name: str, endpoints: List[Dict[str, Any]]):
        """Update service endpoints (simulates EDS updates)"""
        with self.lock:
            snapshot = self.snapshots.get("default")
            if not snapshot:
                return
            
            version = self._next_version()
            
            # Update cluster endpoints
            if service_name in snapshot.clusters:
                cluster = snapshot.clusters[service_name]
                cluster.resource["load_assignment"]["endpoints"] = [{
                    "lb_endpoints": [{
                        "endpoint": {
                            "address": {
                                "socket_address": ep
                            }
                        }
                    } for ep in endpoints]
                }]
                cluster.version = version
                cluster.last_updated = time.time()
            
            snapshot.version = version
            print(f"[Config Store] Updated endpoints for {service_name}: {len(endpoints)} endpoints")
    
    def add_route_rule(self, route_name: str, match_prefix: str, cluster_name: str):
        """Add new route rule (simulates RDS updates)"""
        with self.lock:
            snapshot = self.snapshots.get("default")
            if not snapshot:
                return
            
            version = self._next_version()
            
            # Create or update route configuration
            route = XdsResource(
                name=route_name,
                type_url=ResourceType.ROUTE.value,
                version=version,
                resource={
                    "name": route_name,
                    "virtual_hosts": [{
                        "name": "local_service",
                        "domains": ["*"],
                        "routes": [{
                            "match": {"prefix": match_prefix},
                            "route": {"cluster": cluster_name}
                        }]
                    }]
                }
            )
            
            snapshot.routes[route_name] = route
            snapshot.version = version
            print(f"[Config Store] Added route rule: {match_prefix} -> {cluster_name}")

class XdsManagementServer:
    """
    Envoy xDS Management Server
    Implements gRPC streaming for dynamic configuration distribution
    """
    
    def __init__(self):
        self.config_store = ConfigurationStore()
        self.subscriptions: Dict[str, Dict[str, XdsSubscription]] = {}
        self.running = False
        self.stats = {
            "total_requests": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "active_connections": 0
        }
        
        print("[xDS Server] Management server initialized")
    
    def start(self):
        """Start xDS management server"""
        self.running = True
        
        # Start background tasks
        config_thread = threading.Thread(target=self._config_update_loop)
        config_thread.daemon = True
        config_thread.start()
        
        print("[xDS Server] Started management server")
    
    def stop(self):
        """Stop xDS management server"""
        self.running = False
        print("[xDS Server] Stopped management server")
    
    def _config_update_loop(self):
        """Background loop for configuration updates"""
        while self.running:
            try:
                # Simulate periodic configuration updates
                time.sleep(10)
                
                # Update service endpoints
                endpoints = [
                    {"address": "10.0.1.10", "port_value": 8080},
                    {"address": "10.0.1.20", "port_value": 8080},
                    {"address": "10.0.1.30", "port_value": 8080}
                ]
                self.config_store.update_service_endpoints("service_cluster", endpoints)
                
                # Notify all subscribed proxies
                self._push_config_updates()
                
            except Exception as e:
                print(f"[xDS Server] Config update error: {e}")
    
    def _push_config_updates(self):
        """Push configuration updates to subscribed proxies"""
        for node_id, node_subscriptions in self.subscriptions.items():
            for type_url, subscription in node_subscriptions.items():
                try:
                    self._send_discovery_response(subscription)
                except Exception as e:
                    print(f"[xDS Server] Failed to push update to {node_id}: {e}")
    
    def handle_discovery_request(self, node: EnvoyNode, type_url: str, 
                                resource_names: List[str], version_info: str = "",
                                response_nonce: str = "", error_detail: str = None) -> Dict[str, Any]:
        """Handle xDS discovery request from Envoy proxy"""
        self.stats["total_requests"] += 1
        
        # Create or update subscription
        if node.id not in self.subscriptions:
            self.subscriptions[node.id] = {}
            self.stats["active_connections"] += 1
        
        subscription = XdsSubscription(
            node=node,
            type_url=type_url,
            resource_names=set(resource_names),
            version_info=version_info,
            response_nonce=response_nonce,
            last_request_time=time.time(),
            error_detail=error_detail
        )
        
        self.subscriptions[node.id][type_url] = subscription
        
        # Handle ACK/NACK
        if response_nonce:
            if error_detail:
                print(f"[xDS Server] NACK from {node.id} for {type_url}: {error_detail}")
                self.stats["failed_responses"] += 1
            else:
                print(f"[xDS Server] ACK from {node.id} for {type_url}")
                self.stats["successful_responses"] += 1
        
        # Send discovery response
        return self._send_discovery_response(subscription)
    
    def _send_discovery_response(self, subscription: XdsSubscription) -> Dict[str, Any]:
        """Send xDS discovery response"""
        snapshot = self.config_store.get_snapshot(subscription.node.id)
        if not snapshot:
            return {"error": "No configuration available"}
        
        # Get resources for this type
        resources = snapshot.get_resources(subscription.type_url)
        
        # Filter by requested resource names (if specified)
        if subscription.resource_names:
            filtered_resources = {
                name: resource for name, resource in resources.items()
                if name in subscription.resource_names
            }
        else:
            filtered_resources = resources
        
        # Generate response nonce
        nonce = str(uuid.uuid4())
        
        response = {
            "version_info": snapshot.version,
            "resources": [resource.resource for resource in filtered_resources.values()],
            "canary": False,
            "type_url": subscription.type_url,
            "nonce": nonce,
            "control_plane": {
                "identifier": "xds-management-server"
            }
        }
        
        print(f"[xDS Server] Sent {subscription.type_url} response to {subscription.node.id}: "
              f"version={snapshot.version}, resources={len(filtered_resources)}")
        
        return response
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            **self.stats,
            "total_subscriptions": sum(len(subs) for subs in self.subscriptions.values()),
            "nodes_connected": len(self.subscriptions)
        }

class EnvoyProxySimulator:
    """
    Simulates Envoy proxy xDS client behavior
    Demonstrates subscription, ACK/NACK, and configuration application
    """
    
    def __init__(self, node_id: str, cluster: str = "demo-cluster"):
        self.node = EnvoyNode(
            id=node_id,
            cluster=cluster,
            metadata={"version": "1.0.0"},
            build_version="envoy-1.24.0"
        )
        self.subscriptions: Dict[str, str] = {}  # type_url -> version
        self.applied_config: Dict[str, Any] = {}
        self.running = False
        
        print(f"[Envoy {node_id}] Proxy simulator initialized")
    
    def start(self, management_server: XdsManagementServer):
        """Start Envoy proxy and subscribe to xDS"""
        self.running = True
        self.management_server = management_server
        
        # Subscribe to all xDS resource types
        resource_types = [
            ResourceType.LISTENER.value,
            ResourceType.ROUTE.value,
            ResourceType.CLUSTER.value,
            ResourceType.ENDPOINT.value
        ]
        
        for type_url in resource_types:
            self._subscribe_to_resource(type_url)
        
        print(f"[Envoy {self.node.id}] Started and subscribed to xDS")
    
    def _subscribe_to_resource(self, type_url: str):
        """Subscribe to specific xDS resource type"""
        try:
            response = self.management_server.handle_discovery_request(
                node=self.node,
                type_url=type_url,
                resource_names=[],  # Subscribe to all resources
                version_info="",
                response_nonce=""
            )
            
            if "error" not in response:
                # Apply configuration
                self._apply_configuration(type_url, response)
                
                # Send ACK
                self.management_server.handle_discovery_request(
                    node=self.node,
                    type_url=type_url,
                    resource_names=[],
                    version_info=response["version_info"],
                    response_nonce=response["nonce"]
                )
                
                self.subscriptions[type_url] = response["version_info"]
                
        except Exception as e:
            print(f"[Envoy {self.node.id}] Subscription error for {type_url}: {e}")
            
            # Send NACK
            self.management_server.handle_discovery_request(
                node=self.node,
                type_url=type_url,
                resource_names=[],
                version_info="",
                response_nonce="",
                error_detail=str(e)
            )
    
    def _apply_configuration(self, type_url: str, response: Dict[str, Any]):
        """Apply received xDS configuration"""
        resources = response.get("resources", [])
        version = response.get("version_info", "")
        
        self.applied_config[type_url] = {
            "version": version,
            "resources": resources,
            "applied_at": time.time()
        }
        
        print(f"[Envoy {self.node.id}] Applied {type_url} config: "
              f"version={version}, resources={len(resources)}")
    
    def get_proxy_status(self) -> Dict[str, Any]:
        """Get proxy status and configuration"""
        return {
            "node_id": self.node.id,
            "cluster": self.node.cluster,
            "subscriptions": self.subscriptions,
            "config_versions": {
                type_url: config["version"] 
                for type_url, config in self.applied_config.items()
            },
            "last_update": max(
                (config["applied_at"] for config in self.applied_config.values()),
                default=0
            )
        }

def demonstrate_envoy_xds():
    """Demonstrate Envoy xDS management server and proxy interaction"""
    print("=== Envoy xDS Management Server Demo ===")
    
    # Initialize management server
    management_server = XdsManagementServer()
    management_server.start()
    
    print("\n1. Starting xDS management server...")
    time.sleep(1)
    
    # Create Envoy proxy simulators
    print("\n2. Creating Envoy proxy simulators...")
    proxies = []
    for i in range(3):
        proxy = EnvoyProxySimulator(f"envoy-proxy-{i+1}")
        proxy.start(management_server)
        proxies.append(proxy)
        time.sleep(0.5)
    
    # Show initial state
    print("\n3. Initial configuration state...")
    for proxy in proxies:
        status = proxy.get_proxy_status()
        print(f"   {status['node_id']}: {len(status['config_versions'])} resource types configured")
    
    # Simulate configuration updates
    print("\n4. Simulating configuration updates...")
    time.sleep(2)
    
    # Add new route rule
    management_server.config_store.add_route_rule(
        "api_route", "/api/", "api_cluster"
    )
    
    # Update service endpoints
    new_endpoints = [
        {"address": "10.0.2.10", "port_value": 8080},
        {"address": "10.0.2.20", "port_value": 8080}
    ]
    management_server.config_store.update_service_endpoints("service_cluster", new_endpoints)
    
    time.sleep(2)
    
    # Show updated state
    print("\n5. Updated configuration state...")
    for proxy in proxies:
        status = proxy.get_proxy_status()
        print(f"   {status['node_id']}: last update {time.time() - status['last_update']:.1f}s ago")
    
    # Show server statistics
    print("\n6. Management server statistics...")
    stats = management_server.get_server_stats()
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Successful responses: {stats['successful_responses']}")
    print(f"   Failed responses: {stats['failed_responses']}")
    print(f"   Active connections: {stats['active_connections']}")
    print(f"   Total subscriptions: {stats['total_subscriptions']}")
    
    # Cleanup
    print("\n7. Stopping management server...")
    management_server.stop()
    
    print("\n=== Envoy xDS Demo Complete ===")

if __name__ == "__main__":
    demonstrate_envoy_xds()
