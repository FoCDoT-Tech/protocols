#!/usr/bin/env python3
"""
HTTP/1.1 Protocol Diagram Renderer
Generates visual diagrams for HTTP/1.1 protocol concepts using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_http_request_response_diagram():
    """Create HTTP request-response cycle diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Client and Server boxes
    client_box = FancyBboxPatch((1, 6), 2, 1.5, boxstyle="round,pad=0.1", 
                               facecolor='lightblue', edgecolor='blue', linewidth=2)
    server_box = FancyBboxPatch((9, 6), 2, 1.5, boxstyle="round,pad=0.1", 
                               facecolor='lightgreen', edgecolor='green', linewidth=2)
    
    ax.add_patch(client_box)
    ax.add_patch(server_box)
    
    ax.text(2, 6.75, 'HTTP Client\n(Browser)', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(10, 6.75, 'HTTP Server\n(Web Server)', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Request arrow
    request_arrow = patches.FancyArrowPatch((3.2, 7), (8.8, 7),
                                          connectionstyle="arc3", 
                                          arrowstyle='->', mutation_scale=20,
                                          color='red', linewidth=2)
    ax.add_patch(request_arrow)
    ax.text(6, 7.3, 'HTTP Request', ha='center', va='center', fontsize=10, fontweight='bold', color='red')
    
    # Response arrow
    response_arrow = patches.FancyArrowPatch((8.8, 6.5), (3.2, 6.5),
                                           connectionstyle="arc3", 
                                           arrowstyle='->', mutation_scale=20,
                                           color='blue', linewidth=2)
    ax.add_patch(response_arrow)
    ax.text(6, 6.2, 'HTTP Response', ha='center', va='center', fontsize=10, fontweight='bold', color='blue')
    
    # Request structure
    ax.text(1, 5, 'HTTP Request Structure:', fontsize=12, fontweight='bold')
    ax.text(1, 4.5, '1. Request Line: GET /api/users HTTP/1.1', fontsize=10, family='monospace')
    ax.text(1, 4.2, '2. Headers: Host, Accept, Authorization', fontsize=10, family='monospace')
    ax.text(1, 3.9, '3. Empty Line', fontsize=10, family='monospace')
    ax.text(1, 3.6, '4. Message Body (optional)', fontsize=10, family='monospace')
    
    # Response structure
    ax.text(7, 5, 'HTTP Response Structure:', fontsize=12, fontweight='bold')
    ax.text(7, 4.5, '1. Status Line: HTTP/1.1 200 OK', fontsize=10, family='monospace')
    ax.text(7, 4.2, '2. Headers: Content-Type, Content-Length', fontsize=10, family='monospace')
    ax.text(7, 3.9, '3. Empty Line', fontsize=10, family='monospace')
    ax.text(7, 3.6, '4. Message Body (response data)', fontsize=10, family='monospace')
    
    ax.set_xlim(0, 12)
    ax.set_ylim(3, 8)
    ax.set_title('HTTP/1.1 Request-Response Cycle', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.2-http1.1/http_request_response.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_http_methods_diagram():
    """Create HTTP methods comparison diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    methods = [
        {'name': 'GET', 'safe': True, 'idempotent': True, 'cacheable': True, 'body': False, 'color': 'lightgreen'},
        {'name': 'POST', 'safe': False, 'idempotent': False, 'cacheable': False, 'body': True, 'color': 'lightcoral'},
        {'name': 'PUT', 'safe': False, 'idempotent': True, 'cacheable': False, 'body': True, 'color': 'lightyellow'},
        {'name': 'DELETE', 'safe': False, 'idempotent': True, 'cacheable': False, 'body': False, 'color': 'lightpink'},
        {'name': 'HEAD', 'safe': True, 'idempotent': True, 'cacheable': True, 'body': False, 'color': 'lightblue'},
        {'name': 'OPTIONS', 'safe': True, 'idempotent': True, 'cacheable': False, 'body': False, 'color': 'lightgray'}
    ]
    
    # Headers
    headers = ['Method', 'Safe', 'Idempotent', 'Cacheable', 'Request Body', 'Use Case']
    col_widths = [1.5, 1, 1.5, 1.5, 1.5, 4]
    
    y_start = 9
    x_start = 0.5
    
    # Draw headers
    x_pos = x_start
    for i, (header, width) in enumerate(zip(headers, col_widths)):
        header_box = FancyBboxPatch((x_pos, y_start), width, 0.8, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor='darkblue', edgecolor='black')
        ax.add_patch(header_box)
        ax.text(x_pos + width/2, y_start + 0.4, header, ha='center', va='center', 
                fontsize=11, fontweight='bold', color='white')
        x_pos += width
    
    # Use cases for each method
    use_cases = [
        'Retrieve data, search, read operations',
        'Create resources, form submissions, uploads',
        'Update/replace resources, idempotent updates',
        'Remove resources, cleanup operations',
        'Check resource existence, get metadata only',
        'Discover allowed methods, CORS preflight'
    ]
    
    # Draw method rows
    for i, (method, use_case) in enumerate(zip(methods, use_cases)):
        y_pos = y_start - 1 - (i * 1)
        x_pos = x_start
        
        # Method name
        method_box = FancyBboxPatch((x_pos, y_pos), col_widths[0], 0.8,
                                   boxstyle="round,pad=0.05",
                                   facecolor=method['color'], edgecolor='black')
        ax.add_patch(method_box)
        ax.text(x_pos + col_widths[0]/2, y_pos + 0.4, method['name'], 
                ha='center', va='center', fontsize=10, fontweight='bold')
        x_pos += col_widths[0]
        
        # Properties
        properties = [method['safe'], method['idempotent'], method['cacheable'], method['body']]
        for j, prop in enumerate(properties):
            prop_box = FancyBboxPatch((x_pos, y_pos), col_widths[j+1], 0.8,
                                     boxstyle="round,pad=0.05",
                                     facecolor='lightgreen' if prop else 'lightcoral',
                                     edgecolor='black')
            ax.add_patch(prop_box)
            ax.text(x_pos + col_widths[j+1]/2, y_pos + 0.4, '✓' if prop else '✗',
                    ha='center', va='center', fontsize=12, fontweight='bold')
            x_pos += col_widths[j+1]
        
        # Use case
        use_case_box = FancyBboxPatch((x_pos, y_pos), col_widths[-1], 0.8,
                                     boxstyle="round,pad=0.05",
                                     facecolor='white', edgecolor='black')
        ax.add_patch(use_case_box)
        ax.text(x_pos + col_widths[-1]/2, y_pos + 0.4, use_case,
                ha='center', va='center', fontsize=9)
    
    ax.set_xlim(0, sum(col_widths) + 1)
    ax.set_ylim(2, 10.5)
    ax.set_title('HTTP/1.1 Methods Comparison', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.2-http1.1/http_methods.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_http_status_codes_diagram():
    """Create HTTP status codes diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    status_categories = [
        {
            'category': '1xx Informational',
            'color': 'lightblue',
            'codes': ['100 Continue', '101 Switching Protocols', '102 Processing']
        },
        {
            'category': '2xx Success',
            'color': 'lightgreen',
            'codes': ['200 OK', '201 Created', '202 Accepted', '204 No Content']
        },
        {
            'category': '3xx Redirection',
            'color': 'lightyellow',
            'codes': ['301 Moved Permanently', '302 Found', '304 Not Modified', '307 Temporary Redirect']
        },
        {
            'category': '4xx Client Error',
            'color': 'lightcoral',
            'codes': ['400 Bad Request', '401 Unauthorized', '403 Forbidden', '404 Not Found', '405 Method Not Allowed']
        },
        {
            'category': '5xx Server Error',
            'color': 'lightpink',
            'codes': ['500 Internal Server Error', '502 Bad Gateway', '503 Service Unavailable', '504 Gateway Timeout']
        }
    ]
    
    y_start = 9
    category_height = 1.5
    
    for i, category in enumerate(status_categories):
        y_pos = y_start - (i * 2)
        
        # Category header
        category_box = FancyBboxPatch((1, y_pos), 12, 0.8,
                                     boxstyle="round,pad=0.1",
                                     facecolor=category['color'], 
                                     edgecolor='black', linewidth=2)
        ax.add_patch(category_box)
        ax.text(7, y_pos + 0.4, category['category'], ha='center', va='center',
                fontsize=14, fontweight='bold')
        
        # Status codes
        codes_text = ' | '.join(category['codes'])
        ax.text(7, y_pos - 0.5, codes_text, ha='center', va='center',
                fontsize=10, family='monospace')
    
    # Add usage examples
    ax.text(1, 0.5, 'Common Usage Examples:', fontsize=12, fontweight='bold')
    examples = [
        '200 OK: Successful GET request',
        '201 Created: Successful POST request',
        '304 Not Modified: Cached resource is still valid',
        '400 Bad Request: Invalid JSON in request body',
        '401 Unauthorized: Missing or invalid authentication',
        '404 Not Found: Resource does not exist',
        '500 Internal Server Error: Server-side exception occurred'
    ]
    
    for i, example in enumerate(examples):
        ax.text(1, 0 - (i * 0.3), f'• {example}', fontsize=10)
    
    ax.set_xlim(0, 14)
    ax.set_ylim(-2.5, 10)
    ax.set_title('HTTP/1.1 Status Codes', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.2-http1.1/http_status_codes.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_http_headers_diagram():
    """Create HTTP headers diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    
    # Request headers
    ax.text(1, 11, 'HTTP Request Headers', fontsize=14, fontweight='bold', color='blue')
    request_headers = [
        ('Host', 'example.com', 'Target server (required in HTTP/1.1)'),
        ('User-Agent', 'Mozilla/5.0...', 'Client application information'),
        ('Accept', 'application/json', 'Preferred response content types'),
        ('Accept-Encoding', 'gzip, deflate', 'Supported compression algorithms'),
        ('Authorization', 'Bearer token123', 'Authentication credentials'),
        ('Content-Type', 'application/json', 'Request body content type'),
        ('Content-Length', '1234', 'Request body size in bytes'),
        ('If-None-Match', '"etag123"', 'Conditional request for caching')
    ]
    
    for i, (name, value, description) in enumerate(request_headers):
        y_pos = 10.5 - (i * 0.4)
        ax.text(1, y_pos, f'{name}:', fontsize=10, fontweight='bold', color='darkblue')
        ax.text(3, y_pos, value, fontsize=10, family='monospace', color='green')
        ax.text(6, y_pos, f'# {description}', fontsize=9, color='gray')
    
    # Response headers
    ax.text(1, 7, 'HTTP Response Headers', fontsize=14, fontweight='bold', color='red')
    response_headers = [
        ('Content-Type', 'application/json', 'Response body content type'),
        ('Content-Length', '5678', 'Response body size in bytes'),
        ('Cache-Control', 'max-age=3600', 'Caching directives'),
        ('ETag', '"abc123"', 'Resource version identifier'),
        ('Last-Modified', 'Wed, 21 Oct 2015 07:28:00 GMT', 'Last modification time'),
        ('Location', '/api/users/123', 'Resource location (redirects, created resources)'),
        ('Set-Cookie', 'session=abc123', 'Set client cookie'),
        ('Access-Control-Allow-Origin', '*', 'CORS policy')
    ]
    
    for i, (name, value, description) in enumerate(response_headers):
        y_pos = 6.5 - (i * 0.4)
        ax.text(1, y_pos, f'{name}:', fontsize=10, fontweight='bold', color='darkred')
        ax.text(3, y_pos, value, fontsize=10, family='monospace', color='green')
        ax.text(6, y_pos, f'# {description}', fontsize=9, color='gray')
    
    # Caching headers section
    ax.text(1, 3, 'HTTP Caching Headers', fontsize=14, fontweight='bold', color='purple')
    caching_info = [
        'Cache-Control: max-age=3600    # Cache for 1 hour',
        'Cache-Control: no-cache        # Must validate with server',
        'Cache-Control: private         # Only browser cache, not proxies',
        'ETag: "version123"             # Resource version for validation',
        'If-None-Match: "version123"    # Conditional request header',
        'Last-Modified: <timestamp>     # File modification time',
        'If-Modified-Since: <timestamp> # Conditional request header'
    ]
    
    for i, info in enumerate(caching_info):
        y_pos = 2.5 - (i * 0.3)
        ax.text(1, y_pos, info, fontsize=10, family='monospace')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.set_title('HTTP/1.1 Headers Reference', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.2-http1.1/http_headers.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_http_connection_diagram():
    """Create HTTP connection management diagram"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # HTTP/1.0 style (new connection per request)
    ax1.set_title('HTTP/1.0 Style: New Connection Per Request', fontsize=14, fontweight='bold')
    
    for i in range(3):
        x_offset = i * 4
        
        # Client
        client_box = FancyBboxPatch((0.5 + x_offset, 2), 1.5, 1, boxstyle="round,pad=0.1",
                                   facecolor='lightblue', edgecolor='blue')
        ax1.add_patch(client_box)
        ax1.text(1.25 + x_offset, 2.5, 'Client', ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Server
        server_box = FancyBboxPatch((0.5 + x_offset, 0.5), 1.5, 1, boxstyle="round,pad=0.1",
                                   facecolor='lightgreen', edgecolor='green')
        ax1.add_patch(server_box)
        ax1.text(1.25 + x_offset, 1, 'Server', ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Connection arrows
        connect_arrow = patches.FancyArrowPatch((1.25 + x_offset, 2), (1.25 + x_offset, 1.5),
                                              arrowstyle='<->', mutation_scale=15, color='red', linewidth=2)
        ax1.add_patch(connect_arrow)
        ax1.text(1.5 + x_offset, 1.75, f'Req {i+1}', ha='left', va='center', fontsize=9, color='red')
        
        # TCP handshake indicator
        ax1.text(1.25 + x_offset, 3.2, 'TCP\nHandshake', ha='center', va='center', fontsize=8, color='red')
    
    ax1.text(6, 3.8, 'Each request requires new TCP connection\n(3-way handshake overhead)', 
             ha='center', va='center', fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow'))
    
    ax1.set_xlim(0, 12)
    ax1.set_ylim(0, 4.5)
    ax1.axis('off')
    
    # HTTP/1.1 style (persistent connection)
    ax2.set_title('HTTP/1.1 Style: Persistent Connection (Keep-Alive)', fontsize=14, fontweight='bold')
    
    # Client
    client_box = FancyBboxPatch((1, 2), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='blue')
    ax2.add_patch(client_box)
    ax2.text(2, 2.5, 'Client', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Server
    server_box = FancyBboxPatch((9, 2), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='green')
    ax2.add_patch(server_box)
    ax2.text(10, 2.5, 'Server', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Persistent connection
    persistent_line = plt.Line2D([3.2, 8.8], [2.5, 2.5], color='blue', linewidth=4)
    ax2.add_line(persistent_line)
    ax2.text(6, 2.8, 'Persistent TCP Connection', ha='center', va='center', fontsize=11, fontweight='bold', color='blue')
    
    # Multiple requests on same connection
    request_positions = [1.8, 2.2, 2.6]
    for i, y_pos in enumerate(request_positions):
        req_arrow = patches.FancyArrowPatch((3.2, y_pos), (8.8, y_pos),
                                          arrowstyle='->', mutation_scale=12, color='green', linewidth=1.5)
        ax2.add_patch(req_arrow)
        ax2.text(6, y_pos + 0.1, f'Request {i+1}', ha='center', va='bottom', fontsize=9, color='green')
    
    # Initial handshake
    ax2.text(2, 3.5, 'Initial TCP\nHandshake Only', ha='center', va='center', fontsize=10, 
             bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgreen'))
    
    ax2.text(6, 1.2, 'Multiple requests reuse same connection\n(No handshake overhead after first)', 
             ha='center', va='center', fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'))
    
    ax2.set_xlim(0, 12)
    ax2.set_ylim(1, 4)
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.2-http1.1/http_connections.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all HTTP/1.1 diagrams"""
    print("Rendering HTTP/1.1 diagrams...")
    
    create_http_request_response_diagram()
    print("✓ HTTP request-response diagram")
    
    create_http_methods_diagram()
    print("✓ HTTP methods comparison diagram")
    
    create_http_status_codes_diagram()
    print("✓ HTTP status codes diagram")
    
    create_http_headers_diagram()
    print("✓ HTTP headers reference diagram")
    
    create_http_connection_diagram()
    print("✓ HTTP connection management diagram")
    
    print("All HTTP/1.1 diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
