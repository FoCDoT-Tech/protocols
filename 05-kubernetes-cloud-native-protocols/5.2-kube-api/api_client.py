#!/usr/bin/env python3
"""
Kubernetes API Client Implementation
Demonstrates HTTP/1.1 + TLS client for Kubernetes API operations
"""

import json
import time
import ssl
import socket
from urllib.parse import urlparse
from typing import Dict, Any, Optional, List
import threading

class KubernetesAPIClient:
    """
    Kubernetes API client using HTTP/1.1 over TLS
    Simulates kubectl and client-go library functionality
    """
    
    def __init__(self, api_server_url: str, token: str = None, cert_file: str = None):
        self.api_server_url = api_server_url
        self.token = token
        self.cert_file = cert_file
        self.session_id = f"client-{int(time.time())}"
        
        # Parse URL
        parsed = urlparse(api_server_url)
        self.host = parsed.hostname
        self.port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        self.use_tls = parsed.scheme == 'https'
        
        print(f"[API Client] Initialized for {api_server_url}")
    
    def _create_connection(self) -> socket.socket:
        """Create HTTP/1.1 connection with optional TLS"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if self.use_tls:
            # Create TLS context (simplified for demo)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE  # Demo only - use proper certs in production
            sock = context.wrap_socket(sock, server_hostname=self.host)
        
        sock.connect((self.host, self.port))
        return sock
    
    def _send_request(self, method: str, path: str, body: str = None, 
                     headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Send HTTP/1.1 request to Kubernetes API"""
        if headers is None:
            headers = {}
        
        # Add authentication header
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        # Standard headers
        headers.update({
            'Host': f'{self.host}:{self.port}',
            'User-Agent': 'kubernetes-client/1.0',
            'Accept': 'application/json',
            'Connection': 'close'
        })
        
        if body:
            headers['Content-Type'] = 'application/json'
            headers['Content-Length'] = str(len(body))
        
        # Build HTTP request
        request_line = f"{method} {path} HTTP/1.1\r\n"
        header_lines = '\r\n'.join([f"{k}: {v}" for k, v in headers.items()])
        request = f"{request_line}{header_lines}\r\n\r\n"
        
        if body:
            request += body
        
        # Send request
        sock = self._create_connection()
        try:
            sock.send(request.encode())
            
            # Read response
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                if b'\r\n\r\n' in response and not body:
                    break
            
            # Parse response
            response_str = response.decode()
            lines = response_str.split('\r\n')
            status_line = lines[0]
            
            # Extract status code
            status_code = int(status_line.split()[1])
            
            # Find body
            body_start = response_str.find('\r\n\r\n') + 4
            response_body = response_str[body_start:] if body_start < len(response_str) else ""
            
            # Parse JSON response
            try:
                data = json.loads(response_body) if response_body.strip() else {}
            except json.JSONDecodeError:
                data = {"raw": response_body}
            
            print(f"[API Client] {method} {path} -> {status_code}")
            return {
                "status_code": status_code,
                "data": data
            }
            
        finally:
            sock.close()
    
    def get_resource(self, api_version: str, kind: str, namespace: str = None, 
                    name: str = None) -> Dict[str, Any]:
        """Get Kubernetes resource(s)"""
        # Build API path
        if api_version == "v1":
            base_path = "/api/v1"
        else:
            group, version = api_version.split('/')
            base_path = f"/apis/{group}/{version}"
        
        if namespace:
            path = f"{base_path}/namespaces/{namespace}/{kind.lower()}s"
        else:
            path = f"{base_path}/{kind.lower()}s"
        
        if name:
            path += f"/{name}"
        
        return self._send_request("GET", path)
    
    def create_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kubernetes resource"""
        api_version = resource.get("apiVersion", "v1")
        kind = resource.get("kind", "").lower()
        namespace = resource.get("metadata", {}).get("namespace")
        
        # Build API path
        if api_version == "v1":
            base_path = "/api/v1"
        else:
            group, version = api_version.split('/')
            base_path = f"/apis/{group}/{version}"
        
        if namespace:
            path = f"{base_path}/namespaces/{namespace}/{kind}s"
        else:
            path = f"{base_path}/{kind}s"
        
        body = json.dumps(resource)
        return self._send_request("POST", path, body)
    
    def update_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Update Kubernetes resource"""
        api_version = resource.get("apiVersion", "v1")
        kind = resource.get("kind", "").lower()
        namespace = resource.get("metadata", {}).get("namespace")
        name = resource.get("metadata", {}).get("name")
        
        # Build API path
        if api_version == "v1":
            base_path = "/api/v1"
        else:
            group, version = api_version.split('/')
            base_path = f"/apis/{group}/{version}"
        
        if namespace:
            path = f"{base_path}/namespaces/{namespace}/{kind}s/{name}"
        else:
            path = f"{base_path}/{kind}s/{name}"
        
        body = json.dumps(resource)
        return self._send_request("PUT", path, body)
    
    def delete_resource(self, api_version: str, kind: str, name: str, 
                       namespace: str = None) -> Dict[str, Any]:
        """Delete Kubernetes resource"""
        # Build API path
        if api_version == "v1":
            base_path = "/api/v1"
        else:
            group, version = api_version.split('/')
            base_path = f"/apis/{group}/{version}"
        
        if namespace:
            path = f"{base_path}/namespaces/{namespace}/{kind.lower()}s/{name}"
        else:
            path = f"{base_path}/{kind.lower()}s/{name}"
        
        return self._send_request("DELETE", path)
    
    def watch_resources(self, api_version: str, kind: str, namespace: str = None,
                       callback=None, duration: int = 10):
        """Watch Kubernetes resources for changes"""
        # Build API path with watch parameter
        if api_version == "v1":
            base_path = "/api/v1"
        else:
            group, version = api_version.split('/')
            base_path = f"/apis/{group}/{version}"
        
        if namespace:
            path = f"{base_path}/namespaces/{namespace}/{kind.lower()}s?watch=true"
        else:
            path = f"{base_path}/{kind.lower()}s?watch=true"
        
        print(f"[API Client] Starting watch on {path}")
        
        def watch_worker():
            try:
                response = self._send_request("GET", path)
                if callback:
                    callback(response)
            except Exception as e:
                print(f"[API Client] Watch error: {e}")
        
        # Start watch in background
        watch_thread = threading.Thread(target=watch_worker)
        watch_thread.daemon = True
        watch_thread.start()
        
        # Wait for specified duration
        time.sleep(duration)
        print(f"[API Client] Watch completed")
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """Get cluster information"""
        return self._send_request("GET", "/api/v1")
    
    def get_api_resources(self) -> Dict[str, Any]:
        """Get available API resources"""
        return self._send_request("GET", "/api/v1")

def demonstrate_api_client():
    """Demonstrate Kubernetes API client functionality"""
    print("=== Kubernetes API Client Demo ===")
    
    # Initialize client
    client = KubernetesAPIClient(
        api_server_url="https://kubernetes.default.svc:443",
        token="demo-service-account-token"
    )
    
    # Get cluster info
    print("\n1. Getting cluster information...")
    cluster_info = client.get_cluster_info()
    print(f"Cluster API version: {cluster_info.get('data', {}).get('kind', 'Unknown')}")
    
    # Create a pod
    print("\n2. Creating a pod...")
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
    
    create_result = client.create_resource(pod_spec)
    print(f"Pod creation status: {create_result.get('status_code')}")
    
    # Get pods
    print("\n3. Listing pods...")
    pods = client.get_resource("v1", "Pod", namespace="default")
    print(f"Found {len(pods.get('data', {}).get('items', []))} pods")
    
    # Watch pods
    print("\n4. Watching pod changes...")
    def pod_watch_callback(event):
        print(f"Pod watch event: {event.get('data', {}).get('type', 'Unknown')}")
    
    client.watch_resources("v1", "Pod", namespace="default", 
                          callback=pod_watch_callback, duration=3)
    
    # Update pod
    print("\n5. Updating pod...")
    pod_spec["metadata"]["labels"]["updated"] = "true"
    update_result = client.update_resource(pod_spec)
    print(f"Pod update status: {update_result.get('status_code')}")
    
    # Delete pod
    print("\n6. Deleting pod...")
    delete_result = client.delete_resource("v1", "Pod", "demo-pod", namespace="default")
    print(f"Pod deletion status: {delete_result.get('status_code')}")
    
    print("\n=== API Client Demo Complete ===")

if __name__ == "__main__":
    demonstrate_api_client()
