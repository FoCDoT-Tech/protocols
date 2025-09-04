#!/usr/bin/env python3
"""
Kubernetes Resource Manager Implementation
Demonstrates resource lifecycle management and controller patterns
"""

import json
import time
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class ResourcePhase(Enum):
    """Resource lifecycle phases"""
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"

class EventType(Enum):
    """Kubernetes event types"""
    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    DELETED = "DELETED"
    ERROR = "ERROR"

@dataclass
class ResourceEvent:
    """Kubernetes resource event"""
    type: EventType
    resource: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

class ResourceController:
    """
    Kubernetes resource controller
    Implements controller pattern for resource management
    """
    
    def __init__(self, name: str, resource_type: str):
        self.name = name
        self.resource_type = resource_type
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.watchers: List[callable] = []
        self.running = False
        self.reconcile_interval = 5.0
        
        print(f"[Controller] {name} initialized for {resource_type}")
    
    def add_watcher(self, callback: callable):
        """Add resource watcher callback"""
        self.watchers.append(callback)
        print(f"[Controller] Added watcher for {self.resource_type}")
    
    def notify_watchers(self, event: ResourceEvent):
        """Notify all watchers of resource changes"""
        for watcher in self.watchers:
            try:
                watcher(event)
            except Exception as e:
                print(f"[Controller] Watcher error: {e}")
    
    def create_resource(self, resource: Dict[str, Any]) -> bool:
        """Create new resource"""
        name = resource.get("metadata", {}).get("name")
        namespace = resource.get("metadata", {}).get("namespace", "default")
        key = f"{namespace}/{name}"
        
        if key in self.resources:
            print(f"[Controller] Resource {key} already exists")
            return False
        
        # Set initial status
        resource.setdefault("status", {})
        resource["status"]["phase"] = ResourcePhase.PENDING.value
        resource["metadata"]["creationTimestamp"] = time.time()
        resource["metadata"]["uid"] = f"uid-{int(time.time())}-{hash(key) % 10000}"
        
        self.resources[key] = resource
        
        # Notify watchers
        event = ResourceEvent(EventType.ADDED, resource)
        self.notify_watchers(event)
        
        print(f"[Controller] Created resource {key}")
        return True
    
    def update_resource(self, resource: Dict[str, Any]) -> bool:
        """Update existing resource"""
        name = resource.get("metadata", {}).get("name")
        namespace = resource.get("metadata", {}).get("namespace", "default")
        key = f"{namespace}/{name}"
        
        if key not in self.resources:
            print(f"[Controller] Resource {key} not found")
            return False
        
        # Update resource
        old_resource = self.resources[key].copy()
        self.resources[key].update(resource)
        self.resources[key]["metadata"]["lastModified"] = time.time()
        
        # Notify watchers
        event = ResourceEvent(EventType.MODIFIED, self.resources[key])
        self.notify_watchers(event)
        
        print(f"[Controller] Updated resource {key}")
        return True
    
    def delete_resource(self, name: str, namespace: str = "default") -> bool:
        """Delete resource"""
        key = f"{namespace}/{name}"
        
        if key not in self.resources:
            print(f"[Controller] Resource {key} not found")
            return False
        
        resource = self.resources.pop(key)
        
        # Notify watchers
        event = ResourceEvent(EventType.DELETED, resource)
        self.notify_watchers(event)
        
        print(f"[Controller] Deleted resource {key}")
        return True
    
    def get_resource(self, name: str, namespace: str = "default") -> Optional[Dict[str, Any]]:
        """Get specific resource"""
        key = f"{namespace}/{name}"
        return self.resources.get(key)
    
    def list_resources(self, namespace: str = None) -> List[Dict[str, Any]]:
        """List resources, optionally filtered by namespace"""
        if namespace:
            return [res for key, res in self.resources.items() if key.startswith(f"{namespace}/")]
        return list(self.resources.values())
    
    def reconcile(self):
        """Reconcile resource state (controller pattern)"""
        for key, resource in self.resources.items():
            try:
                self._reconcile_resource(resource)
            except Exception as e:
                print(f"[Controller] Reconcile error for {key}: {e}")
    
    def _reconcile_resource(self, resource: Dict[str, Any]):
        """Reconcile individual resource state"""
        current_phase = resource.get("status", {}).get("phase")
        
        # Simple state transitions for demo
        if current_phase == ResourcePhase.PENDING.value:
            # Simulate resource becoming ready
            if time.time() - resource["metadata"]["creationTimestamp"] > 2:
                resource["status"]["phase"] = ResourcePhase.RUNNING.value
                resource["status"]["conditions"] = [{
                    "type": "Ready",
                    "status": "True",
                    "lastTransitionTime": time.time()
                }]
                
                # Notify watchers of status change
                event = ResourceEvent(EventType.MODIFIED, resource)
                self.notify_watchers(event)
    
    def start(self):
        """Start controller reconciliation loop"""
        self.running = True
        
        def reconcile_loop():
            while self.running:
                self.reconcile()
                time.sleep(self.reconcile_interval)
        
        self.reconcile_thread = threading.Thread(target=reconcile_loop)
        self.reconcile_thread.daemon = True
        self.reconcile_thread.start()
        
        print(f"[Controller] {self.name} started")
    
    def stop(self):
        """Stop controller"""
        self.running = False
        print(f"[Controller] {self.name} stopped")

class PodController(ResourceController):
    """Pod-specific controller with container management"""
    
    def __init__(self):
        super().__init__("pod-controller", "Pod")
    
    def _reconcile_resource(self, pod: Dict[str, Any]):
        """Reconcile pod state with container lifecycle"""
        current_phase = pod.get("status", {}).get("phase")
        containers = pod.get("spec", {}).get("containers", [])
        
        if current_phase == ResourcePhase.PENDING.value:
            # Simulate container image pull and start
            creation_time = pod["metadata"]["creationTimestamp"]
            if time.time() - creation_time > 3:
                pod["status"]["phase"] = ResourcePhase.RUNNING.value
                pod["status"]["podIP"] = f"10.244.{hash(pod['metadata']['name']) % 255}.{hash(pod['metadata']['name']) % 255}"
                pod["status"]["containerStatuses"] = []
                
                for container in containers:
                    pod["status"]["containerStatuses"].append({
                        "name": container["name"],
                        "ready": True,
                        "restartCount": 0,
                        "state": {"running": {"startedAt": time.time()}}
                    })
                
                # Notify watchers
                event = ResourceEvent(EventType.MODIFIED, pod)
                self.notify_watchers(event)

class ServiceController(ResourceController):
    """Service controller for network abstraction"""
    
    def __init__(self):
        super().__init__("service-controller", "Service")
    
    def _reconcile_resource(self, service: Dict[str, Any]):
        """Reconcile service endpoints"""
        current_phase = service.get("status", {}).get("phase")
        
        if current_phase == ResourcePhase.PENDING.value:
            # Simulate endpoint discovery
            creation_time = service["metadata"]["creationTimestamp"]
            if time.time() - creation_time > 1:
                service["status"]["phase"] = ResourcePhase.RUNNING.value
                service["status"]["clusterIP"] = f"10.96.{hash(service['metadata']['name']) % 255}.{hash(service['metadata']['name']) % 255}"
                
                # Notify watchers
                event = ResourceEvent(EventType.MODIFIED, service)
                self.notify_watchers(event)

class ResourceManager:
    """
    Central resource manager coordinating multiple controllers
    """
    
    def __init__(self):
        self.controllers: Dict[str, ResourceController] = {}
        self.event_log: List[ResourceEvent] = []
        
        # Initialize built-in controllers
        self.register_controller("Pod", PodController())
        self.register_controller("Service", ServiceController())
        
        print("[ResourceManager] Initialized with built-in controllers")
    
    def register_controller(self, resource_type: str, controller: ResourceController):
        """Register resource controller"""
        self.controllers[resource_type] = controller
        
        # Add event logging watcher
        controller.add_watcher(self._log_event)
        
        print(f"[ResourceManager] Registered {resource_type} controller")
    
    def _log_event(self, event: ResourceEvent):
        """Log resource events"""
        self.event_log.append(event)
        resource_name = event.resource.get("metadata", {}).get("name", "unknown")
        print(f"[ResourceManager] Event: {event.type.value} {resource_name}")
    
    def create_resource(self, resource: Dict[str, Any]) -> bool:
        """Create resource using appropriate controller"""
        kind = resource.get("kind")
        controller = self.controllers.get(kind)
        
        if not controller:
            print(f"[ResourceManager] No controller for {kind}")
            return False
        
        return controller.create_resource(resource)
    
    def update_resource(self, resource: Dict[str, Any]) -> bool:
        """Update resource using appropriate controller"""
        kind = resource.get("kind")
        controller = self.controllers.get(kind)
        
        if not controller:
            print(f"[ResourceManager] No controller for {kind}")
            return False
        
        return controller.update_resource(resource)
    
    def delete_resource(self, kind: str, name: str, namespace: str = "default") -> bool:
        """Delete resource using appropriate controller"""
        controller = self.controllers.get(kind)
        
        if not controller:
            print(f"[ResourceManager] No controller for {kind}")
            return False
        
        return controller.delete_resource(name, namespace)
    
    def get_resource(self, kind: str, name: str, namespace: str = "default") -> Optional[Dict[str, Any]]:
        """Get resource using appropriate controller"""
        controller = self.controllers.get(kind)
        
        if not controller:
            return None
        
        return controller.get_resource(name, namespace)
    
    def list_resources(self, kind: str, namespace: str = None) -> List[Dict[str, Any]]:
        """List resources using appropriate controller"""
        controller = self.controllers.get(kind)
        
        if not controller:
            return []
        
        return controller.list_resources(namespace)
    
    def start_all_controllers(self):
        """Start all registered controllers"""
        for controller in self.controllers.values():
            controller.start()
        print("[ResourceManager] All controllers started")
    
    def stop_all_controllers(self):
        """Stop all controllers"""
        for controller in self.controllers.values():
            controller.stop()
        print("[ResourceManager] All controllers stopped")
    
    def get_events(self, limit: int = 10) -> List[ResourceEvent]:
        """Get recent resource events"""
        return self.event_log[-limit:]

def demonstrate_resource_manager():
    """Demonstrate Kubernetes resource management"""
    print("=== Kubernetes Resource Manager Demo ===")
    
    # Initialize resource manager
    manager = ResourceManager()
    manager.start_all_controllers()
    
    # Create a pod
    print("\n1. Creating a pod...")
    pod_spec = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "demo-pod",
            "namespace": "default",
            "labels": {"app": "demo"}
        },
        "spec": {
            "containers": [{
                "name": "demo-container",
                "image": "nginx:1.20",
                "ports": [{"containerPort": 80}]
            }]
        }
    }
    
    manager.create_resource(pod_spec)
    
    # Create a service
    print("\n2. Creating a service...")
    service_spec = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": "demo-service",
            "namespace": "default"
        },
        "spec": {
            "selector": {"app": "demo"},
            "ports": [{
                "port": 80,
                "targetPort": 80
            }]
        }
    }
    
    manager.create_resource(service_spec)
    
    # Wait for reconciliation
    print("\n3. Waiting for resource reconciliation...")
    time.sleep(5)
    
    # Check resource status
    print("\n4. Checking resource status...")
    pod = manager.get_resource("Pod", "demo-pod")
    if pod:
        print(f"Pod phase: {pod.get('status', {}).get('phase')}")
        print(f"Pod IP: {pod.get('status', {}).get('podIP', 'Not assigned')}")
    
    service = manager.get_resource("Service", "demo-service")
    if service:
        print(f"Service phase: {service.get('status', {}).get('phase')}")
        print(f"Cluster IP: {service.get('status', {}).get('clusterIP', 'Not assigned')}")
    
    # List all pods
    print("\n5. Listing all pods...")
    pods = manager.list_resources("Pod")
    print(f"Found {len(pods)} pods")
    
    # Show recent events
    print("\n6. Recent events...")
    events = manager.get_events(5)
    for event in events:
        resource_name = event.resource.get("metadata", {}).get("name")
        print(f"  {event.type.value}: {resource_name}")
    
    # Update pod labels
    print("\n7. Updating pod labels...")
    pod_spec["metadata"]["labels"]["updated"] = "true"
    manager.update_resource(pod_spec)
    
    # Delete resources
    print("\n8. Cleaning up resources...")
    manager.delete_resource("Pod", "demo-pod")
    manager.delete_resource("Service", "demo-service")
    
    # Stop controllers
    manager.stop_all_controllers()
    
    print("\n=== Resource Manager Demo Complete ===")

if __name__ == "__main__":
    demonstrate_resource_manager()
