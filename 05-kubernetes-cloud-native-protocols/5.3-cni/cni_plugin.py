#!/usr/bin/env python3
"""
CNI Plugin Implementation
Demonstrates Container Network Interface for Kubernetes networking
"""

import json
import subprocess
import ipaddress
import time
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class CNICommand(Enum):
    """CNI plugin commands"""
    ADD = "ADD"
    DEL = "DEL"
    CHECK = "CHECK"
    VERSION = "VERSION"

@dataclass
class CNIResult:
    """CNI plugin execution result"""
    cni_version: str
    interfaces: List[Dict[str, Any]]
    ips: List[Dict[str, Any]]
    routes: List[Dict[str, Any]]
    dns: Dict[str, Any] = None

class IPAMPlugin:
    """
    IP Address Management Plugin
    Handles IP allocation and deallocation for containers
    """
    
    def __init__(self, subnet: str, gateway: str = None):
        self.subnet = ipaddress.IPv4Network(subnet)
        self.gateway = gateway or str(self.subnet.network_address + 1)
        self.allocated_ips = set()
        self.ip_pool = list(self.subnet.hosts())[1:]  # Skip gateway
        
        print(f"[IPAM] Initialized with subnet {subnet}, gateway {self.gateway}")
    
    def allocate_ip(self, container_id: str) -> str:
        """Allocate IP address for container"""
        for ip in self.ip_pool:
            if ip not in self.allocated_ips:
                self.allocated_ips.add(ip)
                print(f"[IPAM] Allocated {ip} to container {container_id[:12]}")
                return str(ip)
        
        raise Exception("No available IP addresses in pool")
    
    def deallocate_ip(self, ip_addr: str, container_id: str):
        """Deallocate IP address"""
        ip = ipaddress.IPv4Address(ip_addr)
        if ip in self.allocated_ips:
            self.allocated_ips.remove(ip)
            print(f"[IPAM] Deallocated {ip} from container {container_id[:12]}")
    
    def get_network_config(self, ip_addr: str) -> Dict[str, Any]:
        """Get network configuration for allocated IP"""
        return {
            "address": f"{ip_addr}/{self.subnet.prefixlen}",
            "gateway": self.gateway,
            "subnet": str(self.subnet)
        }

class BridgeCNIPlugin:
    """
    Bridge CNI Plugin Implementation
    Creates bridge networks for container communication
    """
    
    def __init__(self, bridge_name: str = "cni0"):
        self.bridge_name = bridge_name
        self.ipam = IPAMPlugin("10.244.0.0/16")
        self.interfaces = {}
        
        print(f"[Bridge CNI] Initialized with bridge {bridge_name}")
    
    def create_bridge(self) -> bool:
        """Create bridge interface if it doesn't exist"""
        try:
            # Simulate bridge creation
            print(f"[Bridge CNI] Creating bridge interface {self.bridge_name}")
            
            # In real implementation, this would use netlink or ip commands:
            # subprocess.run(['ip', 'link', 'add', self.bridge_name, 'type', 'bridge'])
            # subprocess.run(['ip', 'link', 'set', self.bridge_name, 'up'])
            # subprocess.run(['ip', 'addr', 'add', self.ipam.gateway + '/16', 'dev', self.bridge_name])
            
            print(f"[Bridge CNI] Bridge {self.bridge_name} created successfully")
            return True
            
        except Exception as e:
            print(f"[Bridge CNI] Failed to create bridge: {e}")
            return False
    
    def create_veth_pair(self, container_id: str, netns_path: str) -> tuple:
        """Create veth pair for container networking"""
        host_veth = f"veth{container_id[:8]}"
        container_veth = "eth0"
        
        try:
            # Simulate veth pair creation
            print(f"[Bridge CNI] Creating veth pair: {host_veth} <-> {container_veth}")
            
            # In real implementation:
            # subprocess.run(['ip', 'link', 'add', host_veth, 'type', 'veth', 'peer', 'name', container_veth])
            # subprocess.run(['ip', 'link', 'set', container_veth, 'netns', netns_path])
            # subprocess.run(['ip', 'link', 'set', host_veth, 'master', self.bridge_name])
            # subprocess.run(['ip', 'link', 'set', host_veth, 'up'])
            
            return host_veth, container_veth
            
        except Exception as e:
            print(f"[Bridge CNI] Failed to create veth pair: {e}")
            raise
    
    def configure_container_interface(self, container_id: str, netns_path: str, 
                                    container_veth: str, ip_addr: str) -> bool:
        """Configure network interface inside container"""
        try:
            network_config = self.ipam.get_network_config(ip_addr)
            
            print(f"[Bridge CNI] Configuring container interface {container_veth}")
            print(f"[Bridge CNI] IP: {network_config['address']}, Gateway: {network_config['gateway']}")
            
            # In real implementation:
            # subprocess.run(['ip', 'netns', 'exec', netns_path, 'ip', 'addr', 'add', 
            #                network_config['address'], 'dev', container_veth])
            # subprocess.run(['ip', 'netns', 'exec', netns_path, 'ip', 'link', 'set', container_veth, 'up'])
            # subprocess.run(['ip', 'netns', 'exec', netns_path, 'ip', 'route', 'add', 'default', 
            #                'via', network_config['gateway']])
            
            return True
            
        except Exception as e:
            print(f"[Bridge CNI] Failed to configure container interface: {e}")
            return False
    
    def add_container(self, container_id: str, netns_path: str) -> CNIResult:
        """Add container to network (CNI ADD command)"""
        print(f"[Bridge CNI] Adding container {container_id[:12]} to network")
        
        # Ensure bridge exists
        self.create_bridge()
        
        # Allocate IP address
        ip_addr = self.ipam.allocate_ip(container_id)
        
        # Create veth pair
        host_veth, container_veth = self.create_veth_pair(container_id, netns_path)
        
        # Configure container interface
        self.configure_container_interface(container_id, netns_path, container_veth, ip_addr)
        
        # Store interface information
        self.interfaces[container_id] = {
            "host_veth": host_veth,
            "container_veth": container_veth,
            "ip_address": ip_addr,
            "netns_path": netns_path
        }
        
        # Build CNI result
        network_config = self.ipam.get_network_config(ip_addr)
        
        result = CNIResult(
            cni_version="1.0.0",
            interfaces=[
                {
                    "name": host_veth,
                    "mac": f"02:42:{container_id[:2]}:{container_id[2:4]}:{container_id[4:6]}:{container_id[6:8]}"
                },
                {
                    "name": container_veth,
                    "mac": f"02:42:{container_id[8:10]}:{container_id[10:12]}:00:01",
                    "sandbox": netns_path
                }
            ],
            ips=[
                {
                    "address": network_config["address"],
                    "gateway": network_config["gateway"],
                    "interface": 1  # Index of container interface
                }
            ],
            routes=[
                {
                    "dst": "0.0.0.0/0",
                    "gw": network_config["gateway"]
                }
            ],
            dns={
                "nameservers": ["8.8.8.8", "8.8.4.4"],
                "domain": "cluster.local",
                "search": ["default.svc.cluster.local", "svc.cluster.local", "cluster.local"]
            }
        )
        
        print(f"[Bridge CNI] Container {container_id[:12]} added successfully with IP {ip_addr}")
        return result
    
    def delete_container(self, container_id: str) -> bool:
        """Remove container from network (CNI DEL command)"""
        print(f"[Bridge CNI] Removing container {container_id[:12]} from network")
        
        if container_id not in self.interfaces:
            print(f"[Bridge CNI] Container {container_id[:12]} not found")
            return False
        
        interface_info = self.interfaces[container_id]
        
        try:
            # Remove veth interface (automatically removes peer)
            host_veth = interface_info["host_veth"]
            print(f"[Bridge CNI] Removing veth interface {host_veth}")
            
            # In real implementation:
            # subprocess.run(['ip', 'link', 'delete', host_veth])
            
            # Deallocate IP address
            self.ipam.deallocate_ip(interface_info["ip_address"], container_id)
            
            # Remove from tracking
            del self.interfaces[container_id]
            
            print(f"[Bridge CNI] Container {container_id[:12]} removed successfully")
            return True
            
        except Exception as e:
            print(f"[Bridge CNI] Failed to remove container: {e}")
            return False
    
    def check_container(self, container_id: str) -> bool:
        """Check container network configuration (CNI CHECK command)"""
        if container_id not in self.interfaces:
            return False
        
        interface_info = self.interfaces[container_id]
        print(f"[Bridge CNI] Container {container_id[:12]} network check: OK")
        print(f"[Bridge CNI] IP: {interface_info['ip_address']}, Interface: {interface_info['container_veth']}")
        
        return True

class CNIPluginManager:
    """
    CNI Plugin Manager
    Coordinates multiple CNI plugins and handles plugin chaining
    """
    
    def __init__(self):
        self.plugins = {}
        self.plugin_configs = {}
        
        # Register built-in plugins
        self.register_plugin("bridge", BridgeCNIPlugin())
        
        print("[CNI Manager] Initialized with built-in plugins")
    
    def register_plugin(self, plugin_type: str, plugin_instance):
        """Register CNI plugin"""
        self.plugins[plugin_type] = plugin_instance
        print(f"[CNI Manager] Registered plugin: {plugin_type}")
    
    def load_network_config(self, config_path: str) -> Dict[str, Any]:
        """Load network configuration from file"""
        # Simulate loading network configuration
        default_config = {
            "cniVersion": "1.0.0",
            "name": "mynet",
            "type": "bridge",
            "bridge": "cni0",
            "isGateway": True,
            "ipMasq": True,
            "ipam": {
                "type": "host-local",
                "subnet": "10.244.0.0/16",
                "routes": [
                    {"dst": "0.0.0.0/0"}
                ]
            }
        }
        
        print(f"[CNI Manager] Loaded network config: {default_config['name']}")
        return default_config
    
    def execute_plugin_chain(self, command: CNICommand, container_id: str, 
                           netns_path: str, config: Dict[str, Any]) -> CNIResult:
        """Execute CNI plugin chain"""
        plugin_type = config.get("type", "bridge")
        plugin = self.plugins.get(plugin_type)
        
        if not plugin:
            raise Exception(f"Plugin {plugin_type} not found")
        
        print(f"[CNI Manager] Executing {command.value} for container {container_id[:12]}")
        
        if command == CNICommand.ADD:
            return plugin.add_container(container_id, netns_path)
        elif command == CNICommand.DEL:
            plugin.delete_container(container_id)
            return None
        elif command == CNICommand.CHECK:
            plugin.check_container(container_id)
            return None
        elif command == CNICommand.VERSION:
            return CNIResult(
                cni_version="1.0.0",
                interfaces=[],
                ips=[],
                routes=[]
            )
    
    def add_pod_network(self, pod_id: str, netns_path: str) -> CNIResult:
        """Add pod to network"""
        config = self.load_network_config("mynet.conf")
        return self.execute_plugin_chain(CNICommand.ADD, pod_id, netns_path, config)
    
    def delete_pod_network(self, pod_id: str) -> bool:
        """Remove pod from network"""
        config = self.load_network_config("mynet.conf")
        self.execute_plugin_chain(CNICommand.DEL, pod_id, "", config)
        return True
    
    def list_pod_networks(self) -> List[Dict[str, Any]]:
        """List all pod networks"""
        networks = []
        for plugin in self.plugins.values():
            if hasattr(plugin, 'interfaces'):
                for container_id, interface_info in plugin.interfaces.items():
                    networks.append({
                        "container_id": container_id,
                        "ip_address": interface_info["ip_address"],
                        "interface": interface_info["container_veth"]
                    })
        return networks

def demonstrate_cni_plugin():
    """Demonstrate CNI plugin functionality"""
    print("=== CNI Plugin Demo ===")
    
    # Initialize CNI manager
    cni_manager = CNIPluginManager()
    
    # Simulate pod creation
    print("\n1. Creating pod networks...")
    
    pods = [
        {"id": "pod-web-frontend-abc123", "netns": "/var/run/netns/pod-web"},
        {"id": "pod-api-backend-def456", "netns": "/var/run/netns/pod-api"},
        {"id": "pod-database-ghi789", "netns": "/var/run/netns/pod-db"}
    ]
    
    pod_results = []
    for pod in pods:
        result = cni_manager.add_pod_network(pod["id"], pod["netns"])
        pod_results.append({"pod": pod, "result": result})
        time.sleep(0.5)
    
    # List pod networks
    print("\n2. Listing pod networks...")
    networks = cni_manager.list_pod_networks()
    for network in networks:
        print(f"  Pod: {network['container_id'][:12]}... IP: {network['ip_address']}")
    
    # Simulate network policy enforcement
    print("\n3. Simulating network policies...")
    print("  • Allow: web-frontend -> api-backend on port 8080")
    print("  • Allow: api-backend -> database on port 5432")
    print("  • Deny: web-frontend -> database (direct access)")
    
    # Check network connectivity
    print("\n4. Checking network connectivity...")
    for pod_result in pod_results:
        pod_id = pod_result["pod"]["id"]
        bridge_plugin = cni_manager.plugins["bridge"]
        bridge_plugin.check_container(pod_id)
    
    # Simulate pod deletion
    print("\n5. Cleaning up pod networks...")
    for pod in pods:
        cni_manager.delete_pod_network(pod["id"])
        time.sleep(0.2)
    
    print("\n=== CNI Plugin Demo Complete ===")

if __name__ == "__main__":
    demonstrate_cni_plugin()
