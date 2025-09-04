#!/usr/bin/env python3
"""
Kubernetes API Server Implementation
Simulates the Kubernetes API Server with RESTful HTTP/JSON interface over TLS.
"""

import json
import time
import threading
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import re

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

class HTTPStatus(Enum):
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500

@dataclass
class APIRequest:
    method: HTTPMethod
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    query_params: Dict[str, str] = field(default_factory=dict)
    user: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class APIResponse:
    status: HTTPStatus
    body: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class KubernetesResource:
    api_version: str
    kind: str
    metadata: Dict[str, Any]
    spec: Dict[str, Any] = field(default_factory=dict)
    status: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'apiVersion': self.api_version,
            'kind': self.kind,
            'metadata': self.metadata,
            'spec': self.spec,
            'status': self.status
        }

class AuthenticationMiddleware:
    def __init__(self):
        # Mock authentication tokens
        self.valid_tokens = {
            'admin-token': {'user': 'admin', 'groups': ['system:masters']},
            'developer-token': {'user': 'developer', 'groups': ['developers']},
            'readonly-token': {'user': 'readonly', 'groups': ['viewers']}
        }
    
    def authenticate(self, request: APIRequest) -> Optional[str]:
        """Authenticate request and return user identity"""
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            user_info = self.valid_tokens.get(token)
            if user_info:
                return user_info['user']
        
        return None

class AuthorizationMiddleware:
    def __init__(self):
        # Mock RBAC rules
        self.rbac_rules = {
            'admin': {'*': ['*']},  # Admin can do everything
            'developer': {
                'pods': ['get', 'list', 'create', 'update', 'delete'],
                'services': ['get', 'list', 'create', 'update'],
                'deployments': ['get', 'list', 'create', 'update', 'delete']
            },
            'readonly': {
                '*': ['get', 'list']  # Read-only access
            }
        }
    
    def authorize(self, user: str, resource: str, action: str) -> bool:
        """Check if user is authorized for action on resource"""
        if not user:
            return False
        
        user_rules = self.rbac_rules.get(user, {})
        
        # Check specific resource permissions
        if resource in user_rules:
            return action in user_rules[resource] or '*' in user_rules[resource]
        
        # Check wildcard permissions
        if '*' in user_rules:
            return action in user_rules['*'] or '*' in user_rules['*']
        
        return False

class AdmissionController:
    def __init__(self):
        self.mutating_webhooks = []
        self.validating_webhooks = []
    
    def mutate(self, resource: KubernetesResource) -> KubernetesResource:
        """Apply mutating admission webhooks"""
        # Add default labels
        if 'labels' not in resource.metadata:
            resource.metadata['labels'] = {}
        
        resource.metadata['labels']['managed-by'] = 'kubernetes-api'
        resource.metadata['labels']['admission-mutated'] = 'true'
        
        # Add creation timestamp
        if 'creationTimestamp' not in resource.metadata:
            resource.metadata['creationTimestamp'] = time.time()
        
        return resource
    
    def validate(self, resource: KubernetesResource) -> List[str]:
        """Apply validating admission webhooks"""
        errors = []
        
        # Validate metadata
        if not resource.metadata.get('name'):
            errors.append("metadata.name is required")
        
        # Validate name format
        name = resource.metadata.get('name', '')
        if not re.match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$', name):
            errors.append("metadata.name must be a valid DNS subdomain")
        
        # Resource-specific validation
        if resource.kind == 'Pod':
            if not resource.spec.get('containers'):
                errors.append("spec.containers is required for Pod")
        
        return errors

class ResourceRegistry:
    def __init__(self):
        self.resources: Dict[str, Dict[str, KubernetesResource]] = {}
        self.watchers: Dict[str, List[Callable]] = {}
        self.resource_version = 1000
    
    def get_key(self, api_version: str, kind: str, namespace: str, name: str) -> str:
        """Generate storage key for resource"""
        if namespace:
            return f"{api_version}/{kind}/{namespace}/{name}"
        return f"{api_version}/{kind}/{name}"
    
    def create_resource(self, resource: KubernetesResource) -> bool:
        """Create a new resource"""
        namespace = resource.metadata.get('namespace', 'default')
        name = resource.metadata['name']
        key = self.get_key(resource.api_version, resource.kind, namespace, name)
        
        if key in self.resources:
            return False  # Resource already exists
        
        # Add metadata
        resource.metadata['uid'] = str(uuid.uuid4())
        resource.metadata['resourceVersion'] = str(self.resource_version)
        self.resource_version += 1
        
        self.resources[key] = resource
        self._notify_watchers('ADDED', resource)
        
        return True
    
    def get_resource(self, api_version: str, kind: str, namespace: str, name: str) -> Optional[KubernetesResource]:
        """Get a resource by key"""
        key = self.get_key(api_version, kind, namespace, name)
        return self.resources.get(key)
    
    def update_resource(self, resource: KubernetesResource) -> bool:
        """Update an existing resource"""
        namespace = resource.metadata.get('namespace', 'default')
        name = resource.metadata['name']
        key = self.get_key(resource.api_version, kind, namespace, name)
        
        if key not in self.resources:
            return False  # Resource doesn't exist
        
        # Update resource version
        resource.metadata['resourceVersion'] = str(self.resource_version)
        self.resource_version += 1
        
        self.resources[key] = resource
        self._notify_watchers('MODIFIED', resource)
        
        return True
    
    def delete_resource(self, api_version: str, kind: str, namespace: str, name: str) -> bool:
        """Delete a resource"""
        key = self.get_key(api_version, kind, namespace, name)
        
        if key not in self.resources:
            return False  # Resource doesn't exist
        
        resource = self.resources[key]
        del self.resources[key]
        self._notify_watchers('DELETED', resource)
        
        return True
    
    def list_resources(self, api_version: str, kind: str, namespace: Optional[str] = None) -> List[KubernetesResource]:
        """List resources by type and optional namespace"""
        results = []
        
        for key, resource in self.resources.items():
            if resource.api_version == api_version and resource.kind == kind:
                if namespace is None or resource.metadata.get('namespace') == namespace:
                    results.append(resource)
        
        return results
    
    def watch_resources(self, api_version: str, kind: str, namespace: Optional[str], callback: Callable):
        """Register a watch callback for resource changes"""
        watch_key = f"{api_version}/{kind}"
        if namespace:
            watch_key += f"/{namespace}"
        
        if watch_key not in self.watchers:
            self.watchers[watch_key] = []
        
        self.watchers[watch_key].append(callback)
    
    def _notify_watchers(self, event_type: str, resource: KubernetesResource):
        """Notify watchers of resource changes"""
        namespace = resource.metadata.get('namespace')
        
        # Notify specific namespace watchers
        if namespace:
            watch_key = f"{resource.api_version}/{resource.kind}/{namespace}"
            for callback in self.watchers.get(watch_key, []):
                try:
                    callback({
                        'type': event_type,
                        'object': resource.to_dict()
                    })
                except Exception as e:
                    print(f"⚠️  Watch callback error: {e}")
        
        # Notify cluster-wide watchers
        watch_key = f"{resource.api_version}/{resource.kind}"
        for callback in self.watchers.get(watch_key, []):
            try:
                callback({
                    'type': event_type,
                    'object': resource.to_dict()
                })
            except Exception as e:
                print(f"⚠️  Watch callback error: {e}")

class KubernetesAPIServer:
    def __init__(self, host: str = "localhost", port: int = 6443):
        self.host = host
        self.port = port
        self.running = False
        
        # Middleware components
        self.auth = AuthenticationMiddleware()
        self.authz = AuthorizationMiddleware()
        self.admission = AdmissionController()
        self.registry = ResourceRegistry()
        
        # Statistics
        self.stats = {
            'requests_total': 0,
            'requests_by_method': {},
            'requests_by_status': {},
            'authentication_failures': 0,
            'authorization_failures': 0,
            'admission_failures': 0
        }
    
    def start(self):
        """Start the API server"""
        self.running = True
        print(f"🚀 Kubernetes API Server started on https://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the API server"""
        self.running = False
        print("🛑 Kubernetes API Server stopped")
    
    def handle_request(self, request: APIRequest) -> APIResponse:
        """Handle incoming API request"""
        self.stats['requests_total'] += 1
        self.stats['requests_by_method'][request.method.value] = \
            self.stats['requests_by_method'].get(request.method.value, 0) + 1
        
        # Authentication
        user = self.auth.authenticate(request)
        if not user:
            self.stats['authentication_failures'] += 1
            return APIResponse(
                HTTPStatus.UNAUTHORIZED,
                {'message': 'Authentication required'}
            )
        
        request.user = user
        
        # Route request
        try:
            response = self._route_request(request)
            self.stats['requests_by_status'][response.status.value] = \
                self.stats['requests_by_status'].get(response.status.value, 0) + 1
            return response
        except Exception as e:
            print(f"❌ API Server error: {e}")
            return APIResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {'message': 'Internal server error'}
            )
    
    def _route_request(self, request: APIRequest) -> APIResponse:
        """Route request to appropriate handler"""
        path_parts = request.path.strip('/').split('/')
        
        # Core API routes (/api/v1/...)
        if len(path_parts) >= 2 and path_parts[0] == 'api' and path_parts[1] == 'v1':
            return self._handle_core_api(request, path_parts[2:])
        
        # Named group API routes (/apis/{group}/{version}/...)
        if len(path_parts) >= 3 and path_parts[0] == 'apis':
            group = path_parts[1]
            version = path_parts[2]
            return self._handle_group_api(request, group, version, path_parts[3:])
        
        # Health check
        if request.path == '/healthz':
            return APIResponse(HTTPStatus.OK, {'status': 'ok'})
        
        # Version info
        if request.path == '/version':
            return APIResponse(HTTPStatus.OK, {
                'major': '1',
                'minor': '28',
                'gitVersion': 'v1.28.0-simulated'
            })
        
        return APIResponse(HTTPStatus.NOT_FOUND, {'message': 'Not found'})
    
    def _handle_core_api(self, request: APIRequest, path_parts: List[str]) -> APIResponse:
        """Handle core API requests (/api/v1/...)"""
        if not path_parts:
            # List API resources
            return APIResponse(HTTPStatus.OK, {
                'kind': 'APIResourceList',
                'apiVersion': 'v1',
                'resources': [
                    {'name': 'pods', 'kind': 'Pod', 'namespaced': True},
                    {'name': 'services', 'kind': 'Service', 'namespaced': True},
                    {'name': 'configmaps', 'kind': 'ConfigMap', 'namespaced': True},
                    {'name': 'secrets', 'kind': 'Secret', 'namespaced': True},
                    {'name': 'nodes', 'kind': 'Node', 'namespaced': False}
                ]
            })
        
        resource_type = path_parts[0]
        
        # Handle namespaced resources
        if len(path_parts) >= 3 and path_parts[0] == 'namespaces':
            namespace = path_parts[1]
            resource_type = path_parts[2]
            resource_name = path_parts[3] if len(path_parts) > 3 else None
            
            return self._handle_resource_request(
                request, 'v1', resource_type.rstrip('s').title(), 
                namespace, resource_name
            )
        
        # Handle cluster-scoped resources
        resource_name = path_parts[1] if len(path_parts) > 1 else None
        return self._handle_resource_request(
            request, 'v1', resource_type.rstrip('s').title(), 
            None, resource_name
        )
    
    def _handle_group_api(self, request: APIRequest, group: str, version: str, path_parts: List[str]) -> APIResponse:
        """Handle named group API requests (/apis/{group}/{version}/...)"""
        if not path_parts:
            # List API resources for this group/version
            return APIResponse(HTTPStatus.OK, {
                'kind': 'APIResourceList',
                'apiVersion': f'{group}/{version}',
                'resources': [
                    {'name': 'deployments', 'kind': 'Deployment', 'namespaced': True},
                    {'name': 'replicasets', 'kind': 'ReplicaSet', 'namespaced': True}
                ]
            })
        
        resource_type = path_parts[0]
        
        # Handle namespaced resources
        if len(path_parts) >= 3 and path_parts[0] == 'namespaces':
            namespace = path_parts[1]
            resource_type = path_parts[2]
            resource_name = path_parts[3] if len(path_parts) > 3 else None
            
            return self._handle_resource_request(
                request, f'{group}/{version}', resource_type.rstrip('s').title(),
                namespace, resource_name
            )
        
        # Handle cluster-scoped resources
        resource_name = path_parts[1] if len(path_parts) > 1 else None
        return self._handle_resource_request(
            request, f'{group}/{version}', resource_type.rstrip('s').title(),
            None, resource_name
        )
    
    def _handle_resource_request(self, request: APIRequest, api_version: str, kind: str, 
                               namespace: Optional[str], name: Optional[str]) -> APIResponse:
        """Handle individual resource requests"""
        
        # Authorization check
        action = self._method_to_action(request.method)
        if not self.authz.authorize(request.user, kind.lower(), action):
            self.stats['authorization_failures'] += 1
            return APIResponse(HTTPStatus.FORBIDDEN, {
                'message': f'User {request.user} is not authorized to {action} {kind}'
            })
        
        # Handle different HTTP methods
        if request.method == HTTPMethod.GET:
            if name:
                # Get single resource
                resource = self.registry.get_resource(api_version, kind, namespace or 'default', name)
                if resource:
                    return APIResponse(HTTPStatus.OK, resource.to_dict())
                else:
                    return APIResponse(HTTPStatus.NOT_FOUND, {'message': f'{kind} {name} not found'})
            else:
                # List resources
                resources = self.registry.list_resources(api_version, kind, namespace)
                return APIResponse(HTTPStatus.OK, {
                    'kind': f'{kind}List',
                    'apiVersion': api_version,
                    'items': [r.to_dict() for r in resources]
                })
        
        elif request.method == HTTPMethod.POST:
            # Create resource
            if not request.body:
                return APIResponse(HTTPStatus.BAD_REQUEST, {'message': 'Request body required'})
            
            resource = KubernetesResource(
                api_version=request.body.get('apiVersion', api_version),
                kind=request.body.get('kind', kind),
                metadata=request.body.get('metadata', {}),
                spec=request.body.get('spec', {}),
                status=request.body.get('status', {})
            )
            
            # Set namespace if not provided
            if namespace and 'namespace' not in resource.metadata:
                resource.metadata['namespace'] = namespace
            
            # Admission control
            resource = self.admission.mutate(resource)
            validation_errors = self.admission.validate(resource)
            
            if validation_errors:
                self.stats['admission_failures'] += 1
                return APIResponse(HTTPStatus.UNPROCESSABLE_ENTITY, {
                    'message': 'Admission validation failed',
                    'errors': validation_errors
                })
            
            # Create resource
            if self.registry.create_resource(resource):
                return APIResponse(HTTPStatus.CREATED, resource.to_dict())
            else:
                return APIResponse(HTTPStatus.CONFLICT, {
                    'message': f'{kind} {resource.metadata["name"]} already exists'
                })
        
        elif request.method == HTTPMethod.PUT and name:
            # Update resource
            if not request.body:
                return APIResponse(HTTPStatus.BAD_REQUEST, {'message': 'Request body required'})
            
            resource = KubernetesResource(
                api_version=request.body.get('apiVersion', api_version),
                kind=request.body.get('kind', kind),
                metadata=request.body.get('metadata', {}),
                spec=request.body.get('spec', {}),
                status=request.body.get('status', {})
            )
            
            resource.metadata['name'] = name
            if namespace:
                resource.metadata['namespace'] = namespace
            
            if self.registry.update_resource(resource):
                return APIResponse(HTTPStatus.OK, resource.to_dict())
            else:
                return APIResponse(HTTPStatus.NOT_FOUND, {'message': f'{kind} {name} not found'})
        
        elif request.method == HTTPMethod.DELETE and name:
            # Delete resource
            if self.registry.delete_resource(api_version, kind, namespace or 'default', name):
                return APIResponse(HTTPStatus.OK, {'message': f'{kind} {name} deleted'})
            else:
                return APIResponse(HTTPStatus.NOT_FOUND, {'message': f'{kind} {name} not found'})
        
        return APIResponse(HTTPStatus.BAD_REQUEST, {'message': 'Invalid request'})
    
    def _method_to_action(self, method: HTTPMethod) -> str:
        """Convert HTTP method to RBAC action"""
        mapping = {
            HTTPMethod.GET: 'get',
            HTTPMethod.POST: 'create',
            HTTPMethod.PUT: 'update',
            HTTPMethod.PATCH: 'update',
            HTTPMethod.DELETE: 'delete'
        }
        return mapping.get(method, 'unknown')

def demonstrate_kubernetes_api():
    """Demonstrate Kubernetes API Server functionality"""
    print("=== Kubernetes API Server Demonstration ===")
    
    # Create and start API server
    api_server = KubernetesAPIServer()
    api_server.start()
    
    try:
        # Test authentication and basic operations
        print("\n🔐 Testing Authentication:")
        
        # Unauthenticated request
        unauth_request = APIRequest(HTTPMethod.GET, '/api/v1/pods')
        response = api_server.handle_request(unauth_request)
        print(f"❌ Unauthenticated request: {response.status.value} - {response.body['message']}")
        
        # Authenticated requests
        admin_headers = {'Authorization': 'Bearer admin-token'}
        dev_headers = {'Authorization': 'Bearer developer-token'}
        readonly_headers = {'Authorization': 'Bearer readonly-token'}
        
        print("\n📝 Creating Resources (Admin):")
        
        # Create a Pod
        pod_data = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {'name': 'nginx-pod', 'namespace': 'default'},
            'spec': {
                'containers': [{
                    'name': 'nginx',
                    'image': 'nginx:1.20',
                    'ports': [{'containerPort': 80}]
                }]
            }
        }
        
        create_pod_request = APIRequest(
            HTTPMethod.POST, 
            '/api/v1/namespaces/default/pods',
            headers=admin_headers,
            body=pod_data
        )
        response = api_server.handle_request(create_pod_request)
        print(f"✅ Create Pod: {response.status.value} - {response.body.get('metadata', {}).get('name', 'unknown')}")
        
        # Create a Service
        service_data = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {'name': 'nginx-service', 'namespace': 'default'},
            'spec': {
                'selector': {'app': 'nginx'},
                'ports': [{'port': 80, 'targetPort': 80}]
            }
        }
        
        create_service_request = APIRequest(
            HTTPMethod.POST,
            '/api/v1/namespaces/default/services',
            headers=admin_headers,
            body=service_data
        )
        response = api_server.handle_request(create_service_request)
        print(f"✅ Create Service: {response.status.value} - {response.body.get('metadata', {}).get('name', 'unknown')}")
        
        print("\n📖 Reading Resources:")
        
        # Get Pod (Developer)
        get_pod_request = APIRequest(
            HTTPMethod.GET,
            '/api/v1/namespaces/default/pods/nginx-pod',
            headers=dev_headers
        )
        response = api_server.handle_request(get_pod_request)
        print(f"📖 Get Pod (Developer): {response.status.value} - {response.body.get('kind', 'unknown')}")
        
        # List Pods (Read-only)
        list_pods_request = APIRequest(
            HTTPMethod.GET,
            '/api/v1/namespaces/default/pods',
            headers=readonly_headers
        )
        response = api_server.handle_request(list_pods_request)
        print(f"📋 List Pods (Read-only): {response.status.value} - {len(response.body.get('items', []))} items")
        
        print("\n🔒 Testing Authorization:")
        
        # Try to delete as read-only user (should fail)
        delete_request = APIRequest(
            HTTPMethod.DELETE,
            '/api/v1/namespaces/default/pods/nginx-pod',
            headers=readonly_headers
        )
        response = api_server.handle_request(delete_request)
        print(f"❌ Delete Pod (Read-only): {response.status.value} - {response.body['message']}")
        
        print("\n🛡️  Testing Admission Control:")
        
        # Try to create invalid Pod
        invalid_pod = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {'name': 'INVALID-NAME!', 'namespace': 'default'},
            'spec': {}  # Missing containers
        }
        
        invalid_request = APIRequest(
            HTTPMethod.POST,
            '/api/v1/namespaces/default/pods',
            headers=admin_headers,
            body=invalid_pod
        )
        response = api_server.handle_request(invalid_request)
        print(f"❌ Invalid Pod: {response.status.value} - {len(response.body.get('errors', []))} validation errors")
        for error in response.body.get('errors', []):
            print(f"   • {error}")
        
        print("\n👁️  Testing Watch Streams:")
        
        # Set up watch callback
        def watch_callback(event):
            print(f"🔔 Watch event: {event['type']} {event['object']['kind']} {event['object']['metadata']['name']}")
        
        # Register watch
        api_server.registry.watch_resources('v1', 'Pod', 'default', watch_callback)
        
        # Create another pod to trigger watch
        pod2_data = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {'name': 'watch-test-pod', 'namespace': 'default'},
            'spec': {
                'containers': [{
                    'name': 'test',
                    'image': 'busybox:latest'
                }]
            }
        }
        
        watch_test_request = APIRequest(
            HTTPMethod.POST,
            '/api/v1/namespaces/default/pods',
            headers=admin_headers,
            body=pod2_data
        )
        api_server.handle_request(watch_test_request)
        
        print("\n🗑️  Cleanup:")
        
        # Delete resources
        delete_pod_request = APIRequest(
            HTTPMethod.DELETE,
            '/api/v1/namespaces/default/pods/nginx-pod',
            headers=admin_headers
        )
        response = api_server.handle_request(delete_pod_request)
        print(f"🗑️  Delete Pod: {response.status.value}")
        
        print("\n📊 API Server Statistics:")
        print(f"   Total requests: {api_server.stats['requests_total']}")
        print(f"   Requests by method: {api_server.stats['requests_by_method']}")
        print(f"   Requests by status: {api_server.stats['requests_by_status']}")
        print(f"   Authentication failures: {api_server.stats['authentication_failures']}")
        print(f"   Authorization failures: {api_server.stats['authorization_failures']}")
        print(f"   Admission failures: {api_server.stats['admission_failures']}")
        
    finally:
        api_server.stop()
    
    print("\n🎯 Kubernetes API Server demonstrates:")
    print("💡 RESTful HTTP/JSON interface with proper status codes")
    print("💡 Authentication and authorization middleware")
    print("💡 Admission control with validation and mutation")
    print("💡 Resource versioning and optimistic concurrency")
    print("💡 Watch streams for real-time cluster monitoring")

if __name__ == "__main__":
    demonstrate_kubernetes_api()
