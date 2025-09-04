#!/usr/bin/env python3
"""
etcd gRPC Client Implementation
Simulates gRPC client operations against etcd cluster.
"""

import time
import json
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
import uuid

@dataclass
class GrpcRequest:
    method: str
    key: str
    value: Any = None
    revision: int = 0
    lease_id: int = 0

@dataclass
class GrpcResponse:
    success: bool
    value: Any = None
    revision: int = 0
    error: str = ""

class EtcdGrpcClient:
    def __init__(self, endpoints: List[str]):
        self.endpoints = endpoints
        self.current_endpoint = 0
        self.connection_pool = {}
        self.watch_streams = {}
        self.connected = False
        
        # Client configuration
        self.timeout = 5.0
        self.retry_attempts = 3
        self.keepalive_interval = 30
        
        # Statistics
        self.stats = {
            'requests_sent': 0,
            'responses_received': 0,
            'watch_events_received': 0,
            'connection_failures': 0,
            'retries_attempted': 0
        }
    
    def connect(self) -> bool:
        """Establish gRPC connection to etcd cluster"""
        for attempt in range(self.retry_attempts):
            try:
                endpoint = self.endpoints[self.current_endpoint]
                print(f"🔌 Connecting to etcd at {endpoint}")
                
                # Simulate gRPC connection establishment
                self.connection_pool[endpoint] = {
                    'connected': True,
                    'last_used': time.time(),
                    'requests_sent': 0
                }
                
                self.connected = True
                print(f"✅ Connected to etcd cluster via {endpoint}")
                return True
                
            except Exception as e:
                self.stats['connection_failures'] += 1
                self.stats['retries_attempted'] += 1
                self.current_endpoint = (self.current_endpoint + 1) % len(self.endpoints)
                print(f"❌ Connection failed: {e}")
                time.sleep(0.1)
        
        return False
    
    def disconnect(self):
        """Close gRPC connections"""
        self.connected = False
        self.connection_pool.clear()
        print("🔌 Disconnected from etcd cluster")
    
    def put(self, key: str, value: Any, lease_id: int = 0) -> GrpcResponse:
        """gRPC Put operation"""
        if not self.connected:
            return GrpcResponse(False, error="Not connected")
        
        request = GrpcRequest("PUT", key, value, lease_id=lease_id)
        return self._send_request(request)
    
    def get(self, key: str, revision: int = 0) -> GrpcResponse:
        """gRPC Get operation"""
        if not self.connected:
            return GrpcResponse(False, error="Not connected")
        
        request = GrpcRequest("GET", key, revision=revision)
        return self._send_request(request)
    
    def get_range(self, key_prefix: str, limit: int = 0) -> GrpcResponse:
        """gRPC Range operation for prefix queries"""
        if not self.connected:
            return GrpcResponse(False, error="Not connected")
        
        request = GrpcRequest("RANGE", key_prefix)
        
        # Simulate range query
        self.stats['requests_sent'] += 1
        
        # Mock response with multiple keys
        mock_results = []
        for i in range(min(3, limit or 3)):
            mock_results.append({
                'key': f"{key_prefix}item-{i}",
                'value': f"value-{i}",
                'revision': 100 + i
            })
        
        response = GrpcResponse(True, mock_results, revision=103)
        self.stats['responses_received'] += 1
        
        print(f"📋 Range query: {key_prefix}* returned {len(mock_results)} items")
        return response
    
    def delete(self, key: str) -> GrpcResponse:
        """gRPC Delete operation"""
        if not self.connected:
            return GrpcResponse(False, error="Not connected")
        
        request = GrpcRequest("DELETE", key)
        return self._send_request(request)
    
    def watch(self, key_prefix: str, callback: Callable[[Dict], None], start_revision: int = 0):
        """gRPC Watch stream for real-time notifications"""
        if not self.connected:
            print("❌ Cannot start watch: not connected")
            return
        
        watch_id = str(uuid.uuid4())
        self.watch_streams[watch_id] = {
            'key_prefix': key_prefix,
            'callback': callback,
            'start_revision': start_revision,
            'active': True
        }
        
        # Start watch stream in background thread
        watch_thread = threading.Thread(
            target=self._watch_stream,
            args=(watch_id, key_prefix, callback),
            daemon=True
        )
        watch_thread.start()
        
        print(f"👁️  Started watch stream for {key_prefix} (id: {watch_id[:8]})")
        return watch_id
    
    def _watch_stream(self, watch_id: str, key_prefix: str, callback: Callable[[Dict], None]):
        """Background watch stream processor"""
        while self.connected and watch_id in self.watch_streams:
            # Simulate receiving watch events
            time.sleep(0.5)
            
            if not self.watch_streams.get(watch_id, {}).get('active'):
                break
            
            # Mock watch event
            event = {
                'type': 'PUT',
                'key': f"{key_prefix}dynamic-key",
                'value': f"updated-value-{int(time.time())}",
                'revision': int(time.time() * 1000) % 10000
            }
            
            try:
                callback(event)
                self.stats['watch_events_received'] += 1
            except Exception as e:
                print(f"⚠️  Watch callback error: {e}")
                break
    
    def cancel_watch(self, watch_id: str):
        """Cancel a watch stream"""
        if watch_id in self.watch_streams:
            self.watch_streams[watch_id]['active'] = False
            del self.watch_streams[watch_id]
            print(f"🛑 Cancelled watch stream {watch_id[:8]}")
    
    def transaction(self, compare_ops: List[Dict], success_ops: List[Dict], failure_ops: List[Dict] = None) -> GrpcResponse:
        """gRPC Transaction with compare-and-swap semantics"""
        if not self.connected:
            return GrpcResponse(False, error="Not connected")
        
        print(f"🔄 Starting transaction with {len(compare_ops)} conditions")
        
        # Simulate transaction processing
        self.stats['requests_sent'] += 1
        
        # Mock transaction success
        transaction_succeeded = True
        for op in success_ops:
            print(f"   ✅ {op.get('type', 'UNKNOWN')}: {op.get('key', 'unknown')}")
        
        response = GrpcResponse(transaction_succeeded, revision=int(time.time() * 1000) % 10000)
        self.stats['responses_received'] += 1
        
        return response
    
    def lease_grant(self, ttl_seconds: int) -> GrpcResponse:
        """gRPC Lease Grant for key expiration"""
        if not self.connected:
            return GrpcResponse(False, error="Not connected")
        
        lease_id = int(time.time() * 1000) % 100000
        
        self.stats['requests_sent'] += 1
        response = GrpcResponse(True, {'lease_id': lease_id, 'ttl': ttl_seconds})
        self.stats['responses_received'] += 1
        
        print(f"⏰ Granted lease {lease_id} with TTL {ttl_seconds}s")
        return response
    
    def lease_revoke(self, lease_id: int) -> GrpcResponse:
        """gRPC Lease Revoke"""
        if not self.connected:
            return GrpcResponse(False, error="Not connected")
        
        self.stats['requests_sent'] += 1
        response = GrpcResponse(True)
        self.stats['responses_received'] += 1
        
        print(f"🗑️  Revoked lease {lease_id}")
        return response
    
    def _send_request(self, request: GrpcRequest) -> GrpcResponse:
        """Send gRPC request and handle response"""
        self.stats['requests_sent'] += 1
        
        # Simulate network latency
        time.sleep(0.001)
        
        # Mock successful response
        if request.method == "PUT":
            print(f"📝 Put: {request.key} = {request.value}")
            response = GrpcResponse(True, revision=int(time.time() * 1000) % 10000)
        elif request.method == "GET":
            mock_value = f"value-for-{request.key.split('/')[-1]}"
            print(f"📖 Get: {request.key} = {mock_value}")
            response = GrpcResponse(True, mock_value, revision=int(time.time() * 1000) % 10000)
        elif request.method == "DELETE":
            print(f"🗑️  Delete: {request.key}")
            response = GrpcResponse(True, revision=int(time.time() * 1000) % 10000)
        else:
            response = GrpcResponse(False, error=f"Unknown method: {request.method}")
        
        self.stats['responses_received'] += 1
        return response

def demonstrate_grpc_client():
    """Demonstrate etcd gRPC client operations"""
    print("=== etcd gRPC Client Demonstration ===")
    
    # Create client with multiple endpoints for HA
    client = EtcdGrpcClient([
        "etcd-1.cluster.local:2379",
        "etcd-2.cluster.local:2379", 
        "etcd-3.cluster.local:2379"
    ])
    
    try:
        # Connect to cluster
        if not client.connect():
            print("❌ Failed to connect to etcd cluster")
            return
        
        # Basic operations
        print("\n📝 Basic gRPC Operations:")
        
        # Put operations
        client.put("/kubernetes/pods/default/nginx-1", {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "nginx-1", "namespace": "default"},
            "spec": {"containers": [{"name": "nginx", "image": "nginx:1.20"}]}
        })
        
        client.put("/kubernetes/services/default/nginx-service", {
            "apiVersion": "v1", 
            "kind": "Service",
            "metadata": {"name": "nginx-service", "namespace": "default"},
            "spec": {"selector": {"app": "nginx"}, "ports": [{"port": 80}]}
        })
        
        # Get operations
        print("\n📖 Retrieving Data:")
        pod_response = client.get("/kubernetes/pods/default/nginx-1")
        service_response = client.get("/kubernetes/services/default/nginx-service")
        
        # Range query
        print("\n📋 Range Queries:")
        pods_response = client.get_range("/kubernetes/pods/default/", limit=10)
        
        # Watch streams
        print("\n👁️  Watch Streams:")
        def pod_watch_handler(event):
            print(f"🔔 Pod watch event: {event['type']} {event['key']} (rev {event['revision']})")
        
        def service_watch_handler(event):
            print(f"🔔 Service watch event: {event['type']} {event['key']} (rev {event['revision']})")
        
        pod_watch = client.watch("/kubernetes/pods/", pod_watch_handler)
        service_watch = client.watch("/kubernetes/services/", service_watch_handler)
        
        # Let watch streams receive some events
        time.sleep(1.5)
        
        # Lease operations
        print("\n⏰ Lease Operations:")
        lease_response = client.lease_grant(30)  # 30 second TTL
        if lease_response.success:
            lease_id = lease_response.value['lease_id']
            
            # Put with lease
            client.put("/kubernetes/ephemeral/session-123", 
                      {"user": "admin", "login_time": time.time()}, 
                      lease_id=lease_id)
        
        # Transaction operations
        print("\n🔄 Transaction Operations:")
        client.transaction(
            compare_ops=[
                {"key": "/kubernetes/pods/default/nginx-1", "target": "VERSION", "version": 1}
            ],
            success_ops=[
                {"type": "PUT", "key": "/kubernetes/pods/default/nginx-1", "value": {"status": "updated"}},
                {"type": "PUT", "key": "/kubernetes/events/pod-updated", "value": {"timestamp": time.time()}}
            ],
            failure_ops=[
                {"type": "PUT", "key": "/kubernetes/events/update-failed", "value": {"reason": "version_mismatch"}}
            ]
        )
        
        time.sleep(0.5)
        
        # Cleanup
        print("\n🧹 Cleanup:")
        client.cancel_watch(pod_watch)
        client.cancel_watch(service_watch)
        
        if lease_response.success:
            client.lease_revoke(lease_response.value['lease_id'])
        
        # Show statistics
        print("\n📊 Client Statistics:")
        print(f"   Requests sent: {client.stats['requests_sent']}")
        print(f"   Responses received: {client.stats['responses_received']}")
        print(f"   Watch events: {client.stats['watch_events_received']}")
        print(f"   Connection failures: {client.stats['connection_failures']}")
        print(f"   Retries attempted: {client.stats['retries_attempted']}")
    
    finally:
        client.disconnect()
    
    print("\n🎯 gRPC Client demonstrates:")
    print("💡 High-performance binary protocol communication")
    print("💡 Connection pooling and automatic failover")
    print("💡 Real-time watch streams with callbacks")
    print("💡 Atomic transactions with compare-and-swap")
    print("💡 Lease-based key expiration management")

if __name__ == "__main__":
    demonstrate_grpc_client()
