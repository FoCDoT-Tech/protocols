#!/usr/bin/env python3
"""
HTTP/1.1 Client-Server Communication Simulation
Demonstrates HTTP request/response cycle, methods, headers, and status codes
"""

import time
import random
import json
from urllib.parse import urlparse, parse_qs

class HTTPRequest:
    def __init__(self, method, path, version="HTTP/1.1", headers=None, body=None):
        self.method = method
        self.path = path
        self.version = version
        self.headers = headers or {}
        self.body = body
        self.timestamp = time.time()
    
    def __str__(self):
        lines = [f"{self.method} {self.path} {self.version}"]
        for name, value in self.headers.items():
            lines.append(f"{name}: {value}")
        lines.append("")  # Empty line
        if self.body:
            lines.append(self.body)
        return "\r\n".join(lines)

class HTTPResponse:
    def __init__(self, status_code, reason_phrase, version="HTTP/1.1", headers=None, body=None):
        self.status_code = status_code
        self.reason_phrase = reason_phrase
        self.version = version
        self.headers = headers or {}
        self.body = body
        self.timestamp = time.time()
    
    def __str__(self):
        lines = [f"{self.version} {self.status_code} {self.reason_phrase}"]
        for name, value in self.headers.items():
            lines.append(f"{name}: {value}")
        lines.append("")  # Empty line
        if self.body:
            lines.append(self.body)
        return "\r\n".join(lines)

class HTTPServer:
    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port
        self.resources = {}
        self.request_count = 0
        
    def add_resource(self, path, content, content_type="text/html"):
        """Add a resource to the server"""
        self.resources[path] = {
            'content': content,
            'content_type': content_type,
            'last_modified': time.time(),
            'etag': f'"{hash(content) % 1000000}"'
        }
    
    def handle_request(self, request):
        """Handle HTTP request and return response"""
        self.request_count += 1
        
        print(f"\n=== Request {self.request_count} ===")
        print(f"Method: {request.method}")
        print(f"Path: {request.path}")
        print(f"Headers: {dict(request.headers)}")
        
        # Route request based on method and path
        if request.method == "GET":
            return self.handle_get(request)
        elif request.method == "POST":
            return self.handle_post(request)
        elif request.method == "PUT":
            return self.handle_put(request)
        elif request.method == "DELETE":
            return self.handle_delete(request)
        elif request.method == "HEAD":
            return self.handle_head(request)
        else:
            return self.create_error_response(405, "Method Not Allowed")
    
    def handle_get(self, request):
        """Handle GET request"""
        path = request.path.split('?')[0]  # Remove query string
        
        if path in self.resources:
            resource = self.resources[path]
            
            # Check conditional requests
            if 'If-None-Match' in request.headers:
                if request.headers['If-None-Match'] == resource['etag']:
                    return HTTPResponse(304, "Not Modified", headers={
                        'ETag': resource['etag'],
                        'Cache-Control': 'max-age=3600'
                    })
            
            # Return resource
            headers = {
                'Content-Type': resource['content_type'],
                'Content-Length': str(len(resource['content'])),
                'ETag': resource['etag'],
                'Last-Modified': time.strftime('%a, %d %b %Y %H:%M:%S GMT', 
                                              time.gmtime(resource['last_modified'])),
                'Cache-Control': 'max-age=3600'
            }
            
            return HTTPResponse(200, "OK", headers=headers, body=resource['content'])
        else:
            return self.create_error_response(404, "Not Found")
    
    def handle_post(self, request):
        """Handle POST request"""
        if request.path == "/api/users":
            # Simulate creating a user
            user_data = json.loads(request.body) if request.body else {}
            user_id = random.randint(1000, 9999)
            
            response_data = {
                'id': user_id,
                'name': user_data.get('name', 'Unknown'),
                'email': user_data.get('email', 'unknown@example.com'),
                'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Location': f'/api/users/{user_id}',
                'Content-Length': str(len(json.dumps(response_data)))
            }
            
            return HTTPResponse(201, "Created", headers=headers, body=json.dumps(response_data))
        else:
            return self.create_error_response(404, "Not Found")
    
    def handle_put(self, request):
        """Handle PUT request"""
        if request.path.startswith("/api/users/"):
            user_id = request.path.split('/')[-1]
            user_data = json.loads(request.body) if request.body else {}
            
            response_data = {
                'id': int(user_id),
                'name': user_data.get('name', 'Updated User'),
                'email': user_data.get('email', 'updated@example.com'),
                'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Content-Length': str(len(json.dumps(response_data)))
            }
            
            return HTTPResponse(200, "OK", headers=headers, body=json.dumps(response_data))
        else:
            return self.create_error_response(404, "Not Found")
    
    def handle_delete(self, request):
        """Handle DELETE request"""
        if request.path.startswith("/api/users/"):
            return HTTPResponse(204, "No Content")
        else:
            return self.create_error_response(404, "Not Found")
    
    def handle_head(self, request):
        """Handle HEAD request (like GET but no body)"""
        get_response = self.handle_get(request)
        return HTTPResponse(get_response.status_code, get_response.reason_phrase, 
                          headers=get_response.headers)
    
    def create_error_response(self, status_code, reason_phrase):
        """Create error response"""
        error_body = f"<html><body><h1>{status_code} {reason_phrase}</h1></body></html>"
        headers = {
            'Content-Type': 'text/html',
            'Content-Length': str(len(error_body))
        }
        return HTTPResponse(status_code, reason_phrase, headers=headers, body=error_body)

def simulate_http_communication():
    """Simulate HTTP client-server communication"""
    print("=== HTTP/1.1 Client-Server Communication ===")
    
    # Create server and add resources
    server = HTTPServer()
    
    # Add some resources
    server.add_resource("/", "<html><body><h1>Welcome to Example.com</h1></body></html>")
    server.add_resource("/about", "<html><body><h1>About Us</h1><p>We are awesome!</p></body></html>")
    server.add_resource("/api/status", '{"status": "ok", "version": "1.0"}', "application/json")
    
    # Simulate various HTTP requests
    requests = [
        HTTPRequest("GET", "/", headers={
            "Host": "example.com",
            "User-Agent": "Mozilla/5.0 (compatible; HTTPClient/1.0)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }),
        
        HTTPRequest("GET", "/api/status", headers={
            "Host": "api.example.com",
            "Accept": "application/json",
            "Authorization": "Bearer abc123"
        }),
        
        HTTPRequest("POST", "/api/users", headers={
            "Host": "api.example.com",
            "Content-Type": "application/json",
            "Content-Length": "45"
        }, body='{"name": "John Doe", "email": "john@example.com"}'),
        
        HTTPRequest("GET", "/", headers={
            "Host": "example.com",
            "If-None-Match": '"123456"'  # Simulate cached version
        }),
        
        HTTPRequest("PUT", "/api/users/1234", headers={
            "Host": "api.example.com",
            "Content-Type": "application/json"
        }, body='{"name": "Jane Doe", "email": "jane@example.com"}'),
        
        HTTPRequest("DELETE", "/api/users/1234", headers={
            "Host": "api.example.com",
            "Authorization": "Bearer abc123"
        }),
        
        HTTPRequest("GET", "/nonexistent", headers={
            "Host": "example.com"
        })
    ]
    
    # Process requests
    for i, request in enumerate(requests):
        print(f"\n{'='*50}")
        print(f"HTTP Transaction {i+1}")
        print(f"{'='*50}")
        
        # Show request
        print("REQUEST:")
        print(request)
        
        # Process request
        response = server.handle_request(request)
        
        # Show response
        print("\nRESPONSE:")
        print(response)
        
        time.sleep(0.1)

def demonstrate_http_methods():
    """Demonstrate different HTTP methods and their characteristics"""
    print(f"\n=== HTTP Methods Demonstration ===")
    
    methods = [
        {
            'method': 'GET',
            'description': 'Retrieve data from server',
            'safe': True,
            'idempotent': True,
            'cacheable': True,
            'example': 'GET /api/users/123'
        },
        {
            'method': 'POST',
            'description': 'Submit data to server',
            'safe': False,
            'idempotent': False,
            'cacheable': False,
            'example': 'POST /api/users (create new user)'
        },
        {
            'method': 'PUT',
            'description': 'Update/replace resource',
            'safe': False,
            'idempotent': True,
            'cacheable': False,
            'example': 'PUT /api/users/123 (update user)'
        },
        {
            'method': 'DELETE',
            'description': 'Remove resource',
            'safe': False,
            'idempotent': True,
            'cacheable': False,
            'example': 'DELETE /api/users/123'
        },
        {
            'method': 'HEAD',
            'description': 'Get headers only (no body)',
            'safe': True,
            'idempotent': True,
            'cacheable': True,
            'example': 'HEAD /api/users/123 (check if exists)'
        },
        {
            'method': 'OPTIONS',
            'description': 'Get allowed methods',
            'safe': True,
            'idempotent': True,
            'cacheable': False,
            'example': 'OPTIONS /api/users (CORS preflight)'
        }
    ]
    
    print(f"{'Method':<8} {'Safe':<6} {'Idempotent':<12} {'Cacheable':<10} {'Description'}")
    print("-" * 70)
    
    for method in methods:
        safe = "✓" if method['safe'] else "✗"
        idempotent = "✓" if method['idempotent'] else "✗"
        cacheable = "✓" if method['cacheable'] else "✗"
        
        print(f"{method['method']:<8} {safe:<6} {idempotent:<12} {cacheable:<10} {method['description']}")
    
    print(f"\nExamples:")
    for method in methods:
        print(f"  {method['example']}")

def analyze_http_headers():
    """Analyze common HTTP headers and their purposes"""
    print(f"\n=== HTTP Headers Analysis ===")
    
    request_headers = [
        ('Host', 'example.com', 'Target server (required in HTTP/1.1)'),
        ('User-Agent', 'Mozilla/5.0...', 'Client application info'),
        ('Accept', 'application/json', 'Preferred response format'),
        ('Accept-Encoding', 'gzip, deflate', 'Supported compression'),
        ('Authorization', 'Bearer token123', 'Authentication credentials'),
        ('Content-Type', 'application/json', 'Request body format'),
        ('Content-Length', '42', 'Request body size in bytes'),
        ('If-None-Match', '"etag123"', 'Conditional request (caching)'),
        ('Connection', 'keep-alive', 'Connection management')
    ]
    
    response_headers = [
        ('Content-Type', 'application/json', 'Response body format'),
        ('Content-Length', '156', 'Response body size'),
        ('Cache-Control', 'max-age=3600', 'Caching directives'),
        ('ETag', '"abc123"', 'Resource version identifier'),
        ('Last-Modified', 'Wed, 21 Oct 2015 07:28:00 GMT', 'Last modification time'),
        ('Location', '/api/users/123', 'Resource location (redirects)'),
        ('Set-Cookie', 'session=abc123', 'Set client cookie'),
        ('Access-Control-Allow-Origin', '*', 'CORS policy'),
        ('Server', 'nginx/1.18.0', 'Server software info')
    ]
    
    print("Common Request Headers:")
    for name, example, description in request_headers:
        print(f"  {name:<20}: {example:<25} # {description}")
    
    print(f"\nCommon Response Headers:")
    for name, example, description in response_headers:
        print(f"  {name:<20}: {example:<25} # {description}")

def demonstrate_http_caching():
    """Demonstrate HTTP caching mechanisms"""
    print(f"\n=== HTTP Caching Demonstration ===")
    
    print("Caching Scenario: Client requests /api/products")
    
    # First request
    print(f"\n1. Initial Request:")
    print(f"   GET /api/products HTTP/1.1")
    print(f"   Host: api.example.com")
    
    print(f"\n   Response:")
    print(f"   HTTP/1.1 200 OK")
    print(f"   Content-Type: application/json")
    print(f"   ETag: \"products-v1\"")
    print(f"   Cache-Control: max-age=300")
    print(f"   Last-Modified: Wed, 21 Oct 2015 07:28:00 GMT")
    print(f"   [Product data...]")
    
    # Subsequent request within cache period
    print(f"\n2. Request within cache period (< 5 minutes):")
    print(f"   → Client serves from cache (no request sent)")
    
    # Conditional request after cache expiry
    print(f"\n3. Request after cache expiry:")
    print(f"   GET /api/products HTTP/1.1")
    print(f"   Host: api.example.com")
    print(f"   If-None-Match: \"products-v1\"")
    print(f"   If-Modified-Since: Wed, 21 Oct 2015 07:28:00 GMT")
    
    print(f"\n   Response (if not modified):")
    print(f"   HTTP/1.1 304 Not Modified")
    print(f"   ETag: \"products-v1\"")
    print(f"   Cache-Control: max-age=300")
    print(f"   (No body - client uses cached version)")

if __name__ == "__main__":
    # HTTP communication simulation
    simulate_http_communication()
    
    # HTTP methods demonstration
    demonstrate_http_methods()
    
    # HTTP headers analysis
    analyze_http_headers()
    
    # HTTP caching demonstration
    demonstrate_http_caching()
