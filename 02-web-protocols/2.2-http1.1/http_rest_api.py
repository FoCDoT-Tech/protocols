#!/usr/bin/env python3
"""
HTTP/1.1 RESTful API Simulation
Demonstrates REST principles, API design patterns, and HTTP status codes
"""

import time
import random
import json
from datetime import datetime

class RESTResource:
    def __init__(self, resource_type, data=None):
        self.resource_type = resource_type
        self.data = data or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.version = 1

class RESTfulAPIServer:
    def __init__(self):
        self.resources = {
            'users': {},
            'products': {},
            'orders': {}
        }
        self.next_ids = {
            'users': 1,
            'products': 1,
            'orders': 1
        }
        
        # Populate with sample data
        self._populate_sample_data()
    
    def _populate_sample_data(self):
        """Add sample data for demonstration"""
        # Sample users
        users = [
            {'name': 'John Doe', 'email': 'john@example.com', 'role': 'customer'},
            {'name': 'Jane Smith', 'email': 'jane@example.com', 'role': 'admin'},
            {'name': 'Bob Wilson', 'email': 'bob@example.com', 'role': 'customer'}
        ]
        
        for user_data in users:
            user_id = self.next_ids['users']
            self.resources['users'][user_id] = RESTResource('user', user_data)
            self.next_ids['users'] += 1
        
        # Sample products
        products = [
            {'name': 'Laptop', 'price': 999.99, 'category': 'electronics'},
            {'name': 'Book', 'price': 19.99, 'category': 'books'},
            {'name': 'Coffee Mug', 'price': 12.99, 'category': 'home'}
        ]
        
        for product_data in products:
            product_id = self.next_ids['products']
            self.resources['products'][product_id] = RESTResource('product', product_data)
            self.next_ids['products'] += 1
    
    def handle_request(self, method, path, headers=None, body=None):
        """Handle REST API request"""
        headers = headers or {}
        
        # Parse path
        path_parts = [p for p in path.split('/') if p]
        
        if not path_parts:
            return self._create_response(404, {'error': 'Not Found'})
        
        # Route to appropriate handler
        if path_parts[0] == 'api' and len(path_parts) >= 2:
            resource_type = path_parts[1]
            resource_id = int(path_parts[2]) if len(path_parts) > 2 and path_parts[2].isdigit() else None
            
            if resource_type in self.resources:
                return self._handle_resource_request(method, resource_type, resource_id, headers, body)
            else:
                return self._create_response(404, {'error': 'Resource not found'})
        else:
            return self._create_response(404, {'error': 'Not Found'})
    
    def _handle_resource_request(self, method, resource_type, resource_id, headers, body):
        """Handle requests for specific resource types"""
        if method == 'GET':
            if resource_id is None:
                # GET /api/users - List all resources
                return self._list_resources(resource_type, headers)
            else:
                # GET /api/users/123 - Get specific resource
                return self._get_resource(resource_type, resource_id, headers)
        
        elif method == 'POST':
            if resource_id is None:
                # POST /api/users - Create new resource
                return self._create_resource(resource_type, body, headers)
            else:
                return self._create_response(405, {'error': 'Method not allowed'})
        
        elif method == 'PUT':
            if resource_id is not None:
                # PUT /api/users/123 - Update resource
                return self._update_resource(resource_type, resource_id, body, headers)
            else:
                return self._create_response(405, {'error': 'Method not allowed'})
        
        elif method == 'DELETE':
            if resource_id is not None:
                # DELETE /api/users/123 - Delete resource
                return self._delete_resource(resource_type, resource_id, headers)
            else:
                return self._create_response(405, {'error': 'Method not allowed'})
        
        else:
            return self._create_response(405, {'error': 'Method not allowed'})
    
    def _list_resources(self, resource_type, headers):
        """List all resources of a type"""
        resources = []
        for resource_id, resource in self.resources[resource_type].items():
            resource_data = {
                'id': resource_id,
                **resource.data,
                'created_at': resource.created_at,
                'updated_at': resource.updated_at
            }
            resources.append(resource_data)
        
        # Support pagination
        page = 1
        per_page = 10
        total = len(resources)
        
        response_data = {
            'data': resources,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }
        
        return self._create_response(200, response_data)
    
    def _get_resource(self, resource_type, resource_id, headers):
        """Get specific resource"""
        if resource_id in self.resources[resource_type]:
            resource = self.resources[resource_type][resource_id]
            
            # Check conditional requests
            if 'If-None-Match' in headers:
                etag = f'"{resource.version}"'
                if headers['If-None-Match'] == etag:
                    return self._create_response(304, None, {'ETag': etag})
            
            resource_data = {
                'id': resource_id,
                **resource.data,
                'created_at': resource.created_at,
                'updated_at': resource.updated_at
            }
            
            response_headers = {
                'ETag': f'"{resource.version}"',
                'Last-Modified': resource.updated_at
            }
            
            return self._create_response(200, resource_data, response_headers)
        else:
            return self._create_response(404, {'error': f'{resource_type[:-1].title()} not found'})
    
    def _create_resource(self, resource_type, body, headers):
        """Create new resource"""
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            return self._create_response(400, {'error': 'Invalid JSON'})
        
        # Validate required fields (simplified)
        if resource_type == 'users' and 'email' not in data:
            return self._create_response(400, {'error': 'Email is required'})
        
        # Create resource
        resource_id = self.next_ids[resource_type]
        self.resources[resource_type][resource_id] = RESTResource(resource_type[:-1], data)
        self.next_ids[resource_type] += 1
        
        # Return created resource
        resource_data = {
            'id': resource_id,
            **data,
            'created_at': self.resources[resource_type][resource_id].created_at
        }
        
        response_headers = {
            'Location': f'/api/{resource_type}/{resource_id}'
        }
        
        return self._create_response(201, resource_data, response_headers)
    
    def _update_resource(self, resource_type, resource_id, body, headers):
        """Update existing resource"""
        if resource_id not in self.resources[resource_type]:
            return self._create_response(404, {'error': f'{resource_type[:-1].title()} not found'})
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            return self._create_response(400, {'error': 'Invalid JSON'})
        
        # Update resource
        resource = self.resources[resource_type][resource_id]
        resource.data.update(data)
        resource.updated_at = datetime.now().isoformat()
        resource.version += 1
        
        resource_data = {
            'id': resource_id,
            **resource.data,
            'updated_at': resource.updated_at
        }
        
        return self._create_response(200, resource_data)
    
    def _delete_resource(self, resource_type, resource_id, headers):
        """Delete resource"""
        if resource_id in self.resources[resource_type]:
            del self.resources[resource_type][resource_id]
            return self._create_response(204, None)
        else:
            return self._create_response(404, {'error': f'{resource_type[:-1].title()} not found'})
    
    def _create_response(self, status_code, data, headers=None):
        """Create HTTP response"""
        status_phrases = {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            304: 'Not Modified',
            400: 'Bad Request',
            404: 'Not Found',
            405: 'Method Not Allowed',
            500: 'Internal Server Error'
        }
        
        response_headers = {
            'Content-Type': 'application/json',
            'Server': 'RESTful-API/1.0'
        }
        
        if headers:
            response_headers.update(headers)
        
        body = json.dumps(data) if data is not None else None
        if body:
            response_headers['Content-Length'] = str(len(body))
        
        return {
            'status_code': status_code,
            'status_phrase': status_phrases.get(status_code, 'Unknown'),
            'headers': response_headers,
            'body': body
        }

def simulate_rest_api_operations():
    """Simulate RESTful API operations"""
    print("=== RESTful API Operations Simulation ===")
    
    api = RESTfulAPIServer()
    
    # Test scenarios
    scenarios = [
        {
            'name': 'List all users',
            'method': 'GET',
            'path': '/api/users',
            'headers': {'Accept': 'application/json'}
        },
        {
            'name': 'Get specific user',
            'method': 'GET',
            'path': '/api/users/1',
            'headers': {'Accept': 'application/json'}
        },
        {
            'name': 'Create new user',
            'method': 'POST',
            'path': '/api/users',
            'headers': {'Content-Type': 'application/json'},
            'body': '{"name": "Alice Brown", "email": "alice@example.com", "role": "customer"}'
        },
        {
            'name': 'Update user',
            'method': 'PUT',
            'path': '/api/users/1',
            'headers': {'Content-Type': 'application/json'},
            'body': '{"name": "John Updated", "role": "admin"}'
        },
        {
            'name': 'Conditional GET (not modified)',
            'method': 'GET',
            'path': '/api/users/1',
            'headers': {'If-None-Match': '"2"'}  # Current version after update
        },
        {
            'name': 'Delete user',
            'method': 'DELETE',
            'path': '/api/users/2'
        },
        {
            'name': 'Get non-existent user',
            'method': 'GET',
            'path': '/api/users/999'
        },
        {
            'name': 'Invalid JSON',
            'method': 'POST',
            'path': '/api/users',
            'headers': {'Content-Type': 'application/json'},
            'body': '{"name": "Invalid JSON"'  # Missing closing brace
        }
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\n{'='*60}")
        print(f"Scenario {i+1}: {scenario['name']}")
        print(f"{'='*60}")
        
        # Show request
        print(f"REQUEST:")
        print(f"  {scenario['method']} {scenario['path']} HTTP/1.1")
        for name, value in scenario.get('headers', {}).items():
            print(f"  {name}: {value}")
        if scenario.get('body'):
            print(f"  \n  {scenario['body']}")
        
        # Process request
        response = api.handle_request(
            scenario['method'],
            scenario['path'],
            scenario.get('headers'),
            scenario.get('body')
        )
        
        # Show response
        print(f"\nRESPONSE:")
        print(f"  HTTP/1.1 {response['status_code']} {response['status_phrase']}")
        for name, value in response['headers'].items():
            print(f"  {name}: {value}")
        if response['body']:
            print(f"  \n  {response['body']}")
        
        time.sleep(0.1)

def demonstrate_http_status_codes():
    """Demonstrate HTTP status codes and their meanings"""
    print(f"\n=== HTTP Status Codes ===")
    
    status_codes = [
        # 2xx Success
        (200, 'OK', 'Request successful'),
        (201, 'Created', 'Resource created successfully'),
        (204, 'No Content', 'Request successful, no content to return'),
        
        # 3xx Redirection
        (301, 'Moved Permanently', 'Resource permanently moved'),
        (302, 'Found', 'Resource temporarily moved'),
        (304, 'Not Modified', 'Resource not modified (caching)'),
        
        # 4xx Client Error
        (400, 'Bad Request', 'Invalid request syntax'),
        (401, 'Unauthorized', 'Authentication required'),
        (403, 'Forbidden', 'Access denied'),
        (404, 'Not Found', 'Resource not found'),
        (405, 'Method Not Allowed', 'HTTP method not supported'),
        (409, 'Conflict', 'Request conflicts with current state'),
        (422, 'Unprocessable Entity', 'Validation errors'),
        (429, 'Too Many Requests', 'Rate limit exceeded'),
        
        # 5xx Server Error
        (500, 'Internal Server Error', 'Server encountered an error'),
        (502, 'Bad Gateway', 'Invalid response from upstream'),
        (503, 'Service Unavailable', 'Server temporarily unavailable'),
        (504, 'Gateway Timeout', 'Upstream server timeout')
    ]
    
    print(f"{'Code':<4} {'Status':<25} {'Description'}")
    print("-" * 60)
    
    for code, status, description in status_codes:
        print(f"{code:<4} {status:<25} {description}")

def analyze_rest_principles():
    """Analyze REST architectural principles"""
    print(f"\n=== REST Architectural Principles ===")
    
    principles = [
        {
            'principle': 'Client-Server',
            'description': 'Separation of concerns between client and server',
            'example': 'Web browser (client) requests data from API server'
        },
        {
            'principle': 'Stateless',
            'description': 'Each request contains all information needed',
            'example': 'Authentication token sent with each request'
        },
        {
            'principle': 'Cacheable',
            'description': 'Responses must define if they are cacheable',
            'example': 'Cache-Control: max-age=3600 header'
        },
        {
            'principle': 'Uniform Interface',
            'description': 'Consistent interface between components',
            'example': 'Standard HTTP methods (GET, POST, PUT, DELETE)'
        },
        {
            'principle': 'Layered System',
            'description': 'Architecture composed of hierarchical layers',
            'example': 'Load balancer → API gateway → Microservices'
        },
        {
            'principle': 'Code on Demand',
            'description': 'Server can send executable code (optional)',
            'example': 'JavaScript sent to browser for execution'
        }
    ]
    
    for principle in principles:
        print(f"\n{principle['principle']}:")
        print(f"  Description: {principle['description']}")
        print(f"  Example: {principle['example']}")

def demonstrate_api_versioning():
    """Demonstrate API versioning strategies"""
    print(f"\n=== API Versioning Strategies ===")
    
    strategies = [
        {
            'strategy': 'URL Path Versioning',
            'example': 'GET /api/v1/users vs GET /api/v2/users',
            'pros': 'Clear, cacheable, easy to implement',
            'cons': 'URL pollution, multiple endpoints'
        },
        {
            'strategy': 'Query Parameter',
            'example': 'GET /api/users?version=1',
            'pros': 'Clean URLs, optional versioning',
            'cons': 'Easy to forget, caching issues'
        },
        {
            'strategy': 'Header Versioning',
            'example': 'Accept: application/vnd.api+json;version=1',
            'pros': 'Clean URLs, content negotiation',
            'cons': 'Less visible, harder to test'
        },
        {
            'strategy': 'Subdomain',
            'example': 'v1.api.example.com vs v2.api.example.com',
            'pros': 'Complete separation, easy routing',
            'cons': 'DNS management, SSL certificates'
        }
    ]
    
    for strategy in strategies:
        print(f"\n{strategy['strategy']}:")
        print(f"  Example: {strategy['example']}")
        print(f"  Pros: {strategy['pros']}")
        print(f"  Cons: {strategy['cons']}")

if __name__ == "__main__":
    # REST API operations simulation
    simulate_rest_api_operations()
    
    # HTTP status codes
    demonstrate_http_status_codes()
    
    # REST principles
    analyze_rest_principles()
    
    # API versioning
    demonstrate_api_versioning()
