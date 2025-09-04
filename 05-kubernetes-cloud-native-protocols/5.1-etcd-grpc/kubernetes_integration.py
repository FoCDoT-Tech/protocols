#!/usr/bin/env python3
"""
Kubernetes Integration with etcd
Demonstrates how Kubernetes components interact with etcd for cluster state management.
"""

import time
import json
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

class ResourceType(Enum):
    POD = "pods"
    SERVICE = "services"
    DEPLOYMENT = "deployments"
    CONFIGMAP = "configmaps"
    SECRET = "secrets"
    NODE = "nodes"

@dataclass
class KubernetesResource:
    api_version: str
    kind: str
    metadata: Dict[str, Any]
    spec: Dict[str, Any] = field(default_factory=dict)
    status: Dict[str, Any] = field(default_factory=dict)
    
    def to_etcd_key(self) -> str:
        """Generate etcd key for this resource"""
        namespace = self.metadata.get('namespace', 'default')
        name = self.metadata['name']
        resource_type = self.kind.lower() + 's'
        return f"/registry/{resource_type}/{namespace}/{name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for etcd storage"""
        return {
            'apiVersion': self.api_version,
            'kind': self.kind,
            'metadata': self.metadata,
            'spec': self.spec,
            'status': self.status
        }

class KubernetesAPIServer:
    def __init__(self, etcd_client):
        self.etcd_client = etcd_client
        self.watchers = {}
        self.resource_versions = {}
        
        # Statistics
        self.stats = {
            'api_requests': 0,
            'resources_created': 0,
            'resources_updated': 0,
            'resources_deleted': 0,
            'watch_connections': 0
        }
    
    def create_resource(self, resource: KubernetesResource) -> bool:
        """Create a new Kubernetes resource in etcd"""
        key = resource.to_etcd_key()
        
        # Add metadata
        resource.metadata['uid'] = str(uuid.uuid4())
        resource.metadata['creationTimestamp'] = time.time()
        resource.metadata['resourceVersion'] = str(int(time.time() * 1000))
        
        # Store in etcd
        success = self.etcd_client.put(key, resource.to_dict())
        
        if success:
            self.stats['resources_created'] += 1
            print(f"✅ Created {resource.kind}: {resource.metadata['name']}")
        
        return success
    
    def get_resource(self, resource_type: str, namespace: str, name: str) -> Optional[Dict]:
        """Get a Kubernetes resource from etcd"""
        key = f"/registry/{resource_type}/{namespace}/{name}"
        self.stats['api_requests'] += 1
        return self.etcd_client.get(key)
    
    def update_resource(self, resource: KubernetesResource) -> bool:
        """Update an existing Kubernetes resource"""
        key = resource.to_etcd_key()
        
        # Update metadata
        resource.metadata['resourceVersion'] = str(int(time.time() * 1000))
        
        success = self.etcd_client.put(key, resource.to_dict())
        
        if success:
            self.stats['resources_updated'] += 1
            print(f"🔄 Updated {resource.kind}: {resource.metadata['name']}")
        
        return success
    
    def delete_resource(self, resource_type: str, namespace: str, name: str) -> bool:
        """Delete a Kubernetes resource from etcd"""
        key = f"/registry/{resource_type}/{namespace}/{name}"
        success = self.etcd_client.delete(key)
        
        if success:
            self.stats['resources_deleted'] += 1
            print(f"🗑️  Deleted {resource_type}: {name}")
        
        return success
    
    def list_resources(self, resource_type: str, namespace: str = None) -> List[Dict]:
        """List Kubernetes resources of a specific type"""
        if namespace:
            prefix = f"/registry/{resource_type}/{namespace}/"
        else:
            prefix = f"/registry/{resource_type}/"
        
        # Simulate range query
        self.stats['api_requests'] += 1
        return []  # Simplified for demo
    
    def watch_resources(self, resource_type: str, namespace: str, callback):
        """Watch for changes to Kubernetes resources"""
        prefix = f"/registry/{resource_type}/{namespace}/"
        
        def etcd_watch_callback(event):
            # Convert etcd event to Kubernetes watch event
            k8s_event = {
                'type': event.get('type', 'MODIFIED'),
                'object': event.get('value', {}),
                'resourceVersion': str(event.get('revision', 0))
            }
            callback(k8s_event)
        
        watch_id = self.etcd_client.watch(prefix, etcd_watch_callback)
        self.stats['watch_connections'] += 1
        
        print(f"👁️  Watching {resource_type} in namespace {namespace}")
        return watch_id

class KubernetesController:
    def __init__(self, name: str, api_server: KubernetesAPIServer):
        self.name = name
        self.api_server = api_server
        self.running = False
        self.reconcile_thread = None
        
        # Controller state
        self.desired_state = {}
        self.current_state = {}
        
        # Statistics
        self.stats = {
            'reconcile_loops': 0,
            'resources_reconciled': 0,
            'errors_encountered': 0
        }
    
    def start(self):
        """Start the controller reconcile loop"""
        self.running = True
        self.reconcile_thread = threading.Thread(target=self._reconcile_loop, daemon=True)
        self.reconcile_thread.start()
        print(f"🎮 Controller {self.name} started")
    
    def stop(self):
        """Stop the controller"""
        self.running = False
        if self.reconcile_thread:
            self.reconcile_thread.join(timeout=1)
        print(f"🛑 Controller {self.name} stopped")
    
    def _reconcile_loop(self):
        """Main reconcile loop"""
        while self.running:
            try:
                self._reconcile()
                self.stats['reconcile_loops'] += 1
                time.sleep(1)  # Reconcile every second
            except Exception as e:
                self.stats['errors_encountered'] += 1
                print(f"⚠️  Controller {self.name} error: {e}")
                time.sleep(5)  # Back off on error
    
    def _reconcile(self):
        """Reconcile desired vs current state"""
        # Simplified reconcile logic
        self.stats['resources_reconciled'] += 1

class KubernetesScheduler:
    def __init__(self, api_server: KubernetesAPIServer):
        self.api_server = api_server
        self.running = False
        self.schedule_thread = None
        
        # Scheduler state
        self.pending_pods = []
        self.node_resources = {}
        
        # Statistics
        self.stats = {
            'pods_scheduled': 0,
            'scheduling_failures': 0,
            'nodes_evaluated': 0
        }
    
    def start(self):
        """Start the scheduler"""
        self.running = True
        self.schedule_thread = threading.Thread(target=self._schedule_loop, daemon=True)
        self.schedule_thread.start()
        print("📅 Kubernetes Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.schedule_thread:
            self.schedule_thread.join(timeout=1)
        print("🛑 Kubernetes Scheduler stopped")
    
    def _schedule_loop(self):
        """Main scheduling loop"""
        while self.running:
            try:
                self._schedule_pending_pods()
                time.sleep(0.5)  # Check for new pods every 500ms
            except Exception as e:
                print(f"⚠️  Scheduler error: {e}")
                time.sleep(2)
    
    def _schedule_pending_pods(self):
        """Schedule pending pods to nodes"""
        # Simulate finding and scheduling pods
        if random.random() > 0.7:  # 30% chance of finding a pod to schedule
            pod_name = f"pod-{int(time.time()) % 1000}"
            node_name = f"node-{random.randint(1, 3)}"
            
            print(f"📅 Scheduled pod {pod_name} to node {node_name}")
            self.stats['pods_scheduled'] += 1

def demonstrate_kubernetes_integration():
    """Demonstrate Kubernetes integration with etcd"""
    print("=== Kubernetes Integration with etcd ===")
    
    # Mock etcd client for demonstration
    class MockEtcdClient:
        def __init__(self):
            self.data = {}
            self.watchers = {}
        
        def put(self, key, value):
            self.data[key] = value
            self._notify_watchers(key, 'PUT', value)
            return True
        
        def get(self, key):
            return self.data.get(key)
        
        def delete(self, key):
            if key in self.data:
                value = self.data[key]
                del self.data[key]
                self._notify_watchers(key, 'DELETE', value)
                return True
            return False
        
        def watch(self, prefix, callback):
            watch_id = str(uuid.uuid4())
            self.watchers[watch_id] = {'prefix': prefix, 'callback': callback}
            return watch_id
        
        def _notify_watchers(self, key, event_type, value):
            for watch_id, watcher in self.watchers.items():
                if key.startswith(watcher['prefix']):
                    try:
                        watcher['callback']({
                            'type': event_type,
                            'key': key,
                            'value': value,
                            'revision': int(time.time() * 1000) % 10000
                        })
                    except Exception as e:
                        print(f"⚠️  Watcher error: {e}")
    
    # Create components
    etcd_client = MockEtcdClient()
    api_server = KubernetesAPIServer(etcd_client)
    
    # Create controllers
    deployment_controller = KubernetesController("deployment-controller", api_server)
    replicaset_controller = KubernetesController("replicaset-controller", api_server)
    
    # Create scheduler
    scheduler = KubernetesScheduler(api_server)
    
    try:
        # Start Kubernetes components
        deployment_controller.start()
        replicaset_controller.start()
        scheduler.start()
        
        print("\n📝 Creating Kubernetes Resources:")
        
        # Create a Pod
        pod = KubernetesResource(
            api_version="v1",
            kind="Pod",
            metadata={
                "name": "nginx-pod",
                "namespace": "default",
                "labels": {"app": "nginx"}
            },
            spec={
                "containers": [{
                    "name": "nginx",
                    "image": "nginx:1.20",
                    "ports": [{"containerPort": 80}]
                }]
            }
        )
        api_server.create_resource(pod)
        
        # Create a Service
        service = KubernetesResource(
            api_version="v1",
            kind="Service",
            metadata={
                "name": "nginx-service",
                "namespace": "default"
            },
            spec={
                "selector": {"app": "nginx"},
                "ports": [{"port": 80, "targetPort": 80}],
                "type": "ClusterIP"
            }
        )
        api_server.create_resource(service)
        
        # Create a Deployment
        deployment = KubernetesResource(
            api_version="apps/v1",
            kind="Deployment",
            metadata={
                "name": "nginx-deployment",
                "namespace": "default"
            },
            spec={
                "replicas": 3,
                "selector": {"matchLabels": {"app": "nginx"}},
                "template": {
                    "metadata": {"labels": {"app": "nginx"}},
                    "spec": {
                        "containers": [{
                            "name": "nginx",
                            "image": "nginx:1.20",
                            "ports": [{"containerPort": 80}]
                        }]
                    }
                }
            }
        )
        api_server.create_resource(deployment)
        
        # Set up watches
        print("\n👁️  Setting up Kubernetes Watches:")
        
        def pod_watch_handler(event):
            print(f"🔔 Pod event: {event['type']} - {event.get('object', {}).get('metadata', {}).get('name', 'unknown')}")
        
        def service_watch_handler(event):
            print(f"🔔 Service event: {event['type']} - {event.get('object', {}).get('metadata', {}).get('name', 'unknown')}")
        
        api_server.watch_resources("pods", "default", pod_watch_handler)
        api_server.watch_resources("services", "default", service_watch_handler)
        
        # Simulate some updates
        print("\n🔄 Simulating Kubernetes Operations:")
        time.sleep(1)
        
        # Update pod status
        pod.status = {
            "phase": "Running",
            "conditions": [{
                "type": "Ready",
                "status": "True",
                "lastTransitionTime": time.time()
            }]
        }
        api_server.update_resource(pod)
        
        # Create another pod
        pod2 = KubernetesResource(
            api_version="v1",
            kind="Pod",
            metadata={
                "name": "nginx-pod-2",
                "namespace": "default",
                "labels": {"app": "nginx"}
            },
            spec={
                "containers": [{
                    "name": "nginx",
                    "image": "nginx:1.21",
                    "ports": [{"containerPort": 80}]
                }]
            }
        )
        api_server.create_resource(pod2)
        
        time.sleep(2)
        
        # Delete a resource
        api_server.delete_resource("pods", "default", "nginx-pod")
        
        time.sleep(1)
        
        # Show statistics
        print("\n📊 Kubernetes Component Statistics:")
        print(f"API Server:")
        print(f"  API requests: {api_server.stats['api_requests']}")
        print(f"  Resources created: {api_server.stats['resources_created']}")
        print(f"  Resources updated: {api_server.stats['resources_updated']}")
        print(f"  Resources deleted: {api_server.stats['resources_deleted']}")
        print(f"  Watch connections: {api_server.stats['watch_connections']}")
        
        print(f"\nDeployment Controller:")
        print(f"  Reconcile loops: {deployment_controller.stats['reconcile_loops']}")
        print(f"  Resources reconciled: {deployment_controller.stats['resources_reconciled']}")
        
        print(f"\nScheduler:")
        print(f"  Pods scheduled: {scheduler.stats['pods_scheduled']}")
        print(f"  Scheduling failures: {scheduler.stats['scheduling_failures']}")
        
        print(f"\netcd Data:")
        print(f"  Keys stored: {len(etcd_client.data)}")
        for key in sorted(etcd_client.data.keys()):
            print(f"    {key}")
    
    finally:
        # Cleanup
        deployment_controller.stop()
        replicaset_controller.stop()
        scheduler.stop()
    
    print("\n🎯 Kubernetes Integration demonstrates:")
    print("💡 API Server storing all resources in etcd")
    print("💡 Controllers watching for resource changes")
    print("💡 Scheduler coordinating pod placement")
    print("💡 Real-time event propagation via etcd watches")
    print("💡 Distributed coordination using etcd as single source of truth")

if __name__ == "__main__":
    import random
    demonstrate_kubernetes_integration()
