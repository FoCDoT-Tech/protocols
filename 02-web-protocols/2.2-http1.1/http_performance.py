#!/usr/bin/env python3
"""
HTTP/1.1 Performance Analysis and Optimization
Demonstrates connection management, pipelining, compression, and performance metrics
"""

import time
import random
import gzip
import json
from collections import defaultdict

class HTTPConnection:
    def __init__(self, host, port=80):
        self.host = host
        self.port = port
        self.is_persistent = True
        self.created_at = time.time()
        self.last_used = self.created_at
        self.request_count = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.connection_id = random.randint(1000, 9999)
    
    def send_request(self, request_size):
        """Simulate sending a request"""
        self.last_used = time.time()
        self.request_count += 1
        self.bytes_sent += request_size
        
        # Simulate network latency
        latency = random.uniform(0.01, 0.05)  # 10-50ms
        time.sleep(latency)
        return latency
    
    def receive_response(self, response_size):
        """Simulate receiving a response"""
        self.bytes_received += response_size
        
        # Simulate transfer time based on size
        transfer_time = response_size / (1024 * 1024)  # 1MB/s
        time.sleep(min(transfer_time, 0.1))  # Cap at 100ms for demo
        return transfer_time
    
    def is_expired(self, timeout=30):
        """Check if connection has expired"""
        return time.time() - self.last_used > timeout

class HTTPConnectionPool:
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.connections = {}
        self.connection_stats = defaultdict(int)
    
    def get_connection(self, host, port=80):
        """Get or create connection to host"""
        key = f"{host}:{port}"
        
        # Clean up expired connections
        self._cleanup_expired_connections()
        
        # Reuse existing connection
        if key in self.connections and not self.connections[key].is_expired():
            self.connection_stats['reused'] += 1
            return self.connections[key]
        
        # Create new connection if under limit
        if len(self.connections) < self.max_connections:
            connection = HTTPConnection(host, port)
            self.connections[key] = connection
            self.connection_stats['created'] += 1
            return connection
        
        # Pool exhausted
        self.connection_stats['pool_exhausted'] += 1
        return None
    
    def _cleanup_expired_connections(self):
        """Remove expired connections"""
        expired_keys = [
            key for key, conn in self.connections.items()
            if conn.is_expired()
        ]
        for key in expired_keys:
            del self.connections[key]
            self.connection_stats['expired'] += 1

class HTTPPerformanceAnalyzer:
    def __init__(self):
        self.connection_pool = HTTPConnectionPool()
        self.request_metrics = []
        self.compression_stats = {'enabled': 0, 'disabled': 0}
        
    def simulate_request(self, host, path, use_compression=False, request_size=500):
        """Simulate HTTP request with performance tracking"""
        start_time = time.time()
        
        # Get connection
        connection = self.connection_pool.get_connection(host)
        if not connection:
            return {'error': 'Connection pool exhausted'}
        
        # Send request
        send_latency = connection.send_request(request_size)
        
        # Simulate response
        base_response_size = random.randint(1024, 10240)  # 1-10KB
        
        if use_compression:
            # Simulate compression (typically 60-80% reduction)
            compression_ratio = random.uniform(0.6, 0.8)
            response_size = int(base_response_size * compression_ratio)
            self.compression_stats['enabled'] += 1
        else:
            response_size = base_response_size
            self.compression_stats['disabled'] += 1
        
        # Receive response
        transfer_time = connection.receive_response(response_size)
        
        total_time = time.time() - start_time
        
        # Record metrics
        metrics = {
            'host': host,
            'path': path,
            'connection_id': connection.connection_id,
            'request_size': request_size,
            'response_size': response_size,
            'base_response_size': base_response_size,
            'compressed': use_compression,
            'send_latency': send_latency,
            'transfer_time': transfer_time,
            'total_time': total_time,
            'connection_reused': connection.request_count > 1,
            'timestamp': start_time
        }
        
        self.request_metrics.append(metrics)
        return metrics
    
    def analyze_performance(self):
        """Analyze collected performance metrics"""
        if not self.request_metrics:
            return
        
        print(f"\n=== HTTP Performance Analysis ===")
        
        # Basic stats
        total_requests = len(self.request_metrics)
        total_bytes_sent = sum(m['request_size'] for m in self.request_metrics)
        total_bytes_received = sum(m['response_size'] for m in self.request_metrics)
        avg_response_time = sum(m['total_time'] for m in self.request_metrics) / total_requests
        
        print(f"Total Requests: {total_requests}")
        print(f"Total Bytes Sent: {total_bytes_sent:,} bytes")
        print(f"Total Bytes Received: {total_bytes_received:,} bytes")
        print(f"Average Response Time: {avg_response_time:.3f}s")
        
        # Connection reuse analysis
        reused_connections = sum(1 for m in self.request_metrics if m['connection_reused'])
        reuse_percentage = (reused_connections / total_requests) * 100
        print(f"Connection Reuse Rate: {reuse_percentage:.1f}%")
        
        # Compression analysis
        compressed_requests = self.compression_stats['enabled']
        if compressed_requests > 0:
            compressed_metrics = [m for m in self.request_metrics if m['compressed']]
            total_savings = sum(m['base_response_size'] - m['response_size'] for m in compressed_metrics)
            avg_compression = (total_savings / sum(m['base_response_size'] for m in compressed_metrics)) * 100
            print(f"Compression Enabled: {compressed_requests}/{total_requests} requests")
            print(f"Average Compression Ratio: {avg_compression:.1f}%")
            print(f"Total Bytes Saved: {total_savings:,} bytes")
        
        # Performance by host
        host_stats = defaultdict(list)
        for metric in self.request_metrics:
            host_stats[metric['host']].append(metric['total_time'])
        
        print(f"\nPerformance by Host:")
        for host, times in host_stats.items():
            avg_time = sum(times) / len(times)
            print(f"  {host}: {avg_time:.3f}s avg ({len(times)} requests)")

def simulate_http_keep_alive():
    """Demonstrate HTTP keep-alive vs new connections"""
    print("=== HTTP Keep-Alive vs New Connections ===")
    
    # Simulate requests without keep-alive (HTTP/1.0 style)
    print(f"\nWithout Keep-Alive (new connection per request):")
    start_time = time.time()
    
    for i in range(5):
        # Simulate TCP handshake overhead
        handshake_time = random.uniform(0.02, 0.08)  # 20-80ms
        request_time = random.uniform(0.01, 0.03)    # 10-30ms
        total_time = handshake_time + request_time
        
        print(f"  Request {i+1}: {handshake_time:.3f}s handshake + {request_time:.3f}s = {total_time:.3f}s")
        time.sleep(0.01)  # Small delay for demo
    
    no_keepalive_total = time.time() - start_time
    
    # Simulate requests with keep-alive (HTTP/1.1 style)
    print(f"\nWith Keep-Alive (persistent connection):")
    start_time = time.time()
    
    # Initial handshake only
    handshake_time = random.uniform(0.02, 0.08)
    print(f"  Initial handshake: {handshake_time:.3f}s")
    
    for i in range(5):
        request_time = random.uniform(0.01, 0.03)
        print(f"  Request {i+1}: {request_time:.3f}s (no handshake)")
        time.sleep(0.01)
    
    keepalive_total = time.time() - start_time
    
    savings = ((no_keepalive_total - keepalive_total) / no_keepalive_total) * 100
    print(f"\nTotal time without keep-alive: {no_keepalive_total:.3f}s")
    print(f"Total time with keep-alive: {keepalive_total:.3f}s")
    print(f"Time savings: {savings:.1f}%")

def demonstrate_http_pipelining():
    """Demonstrate HTTP pipelining concept"""
    print(f"\n=== HTTP Pipelining Demonstration ===")
    
    print("Sequential Requests (traditional HTTP/1.1):")
    print("  Client → Server: Request 1")
    print("  Client ← Server: Response 1")
    print("  Client → Server: Request 2")
    print("  Client ← Server: Response 2")
    print("  Client → Server: Request 3")
    print("  Client ← Server: Response 3")
    print("  Total: 6 round trips")
    
    print(f"\nPipelined Requests (HTTP/1.1 with pipelining):")
    print("  Client → Server: Request 1")
    print("  Client → Server: Request 2")
    print("  Client → Server: Request 3")
    print("  Client ← Server: Response 1")
    print("  Client ← Server: Response 2")
    print("  Client ← Server: Response 3")
    print("  Total: 3 round trips (responses must be in order)")
    
    print(f"\nPipelining Limitations:")
    print("  • Responses must be returned in order (head-of-line blocking)")
    print("  • Only safe methods (GET, HEAD) should be pipelined")
    print("  • Many proxies and servers don't support it properly")
    print("  • Largely superseded by HTTP/2 multiplexing")

def analyze_http_compression():
    """Analyze HTTP compression benefits"""
    print(f"\n=== HTTP Compression Analysis ===")
    
    # Sample content types and their compression ratios
    content_types = [
        ('text/html', 0.75, 'HTML markup with repetitive tags'),
        ('text/css', 0.80, 'CSS with repeated selectors and properties'),
        ('application/javascript', 0.70, 'JavaScript with variable names and whitespace'),
        ('application/json', 0.85, 'JSON with repeated keys and structure'),
        ('text/plain', 0.60, 'Plain text with natural language redundancy'),
        ('image/jpeg', 0.05, 'Already compressed binary format'),
        ('image/png', 0.10, 'Compressed binary format'),
        ('application/pdf', 0.15, 'Compressed document format')
    ]
    
    print(f"{'Content Type':<25} {'Compression':<12} {'Description'}")
    print("-" * 70)
    
    for content_type, ratio, description in content_types:
        compression_pct = (1 - ratio) * 100
        print(f"{content_type:<25} {compression_pct:>6.1f}%     {description}")
    
    print(f"\nCompression Algorithms:")
    print(f"  • gzip: Most widely supported, good compression ratio")
    print(f"  • deflate: Similar to gzip, less common")
    print(f"  • br (Brotli): Better compression than gzip, newer standard")
    
    print(f"\nCompression Headers:")
    print(f"  Request:  Accept-Encoding: gzip, deflate, br")
    print(f"  Response: Content-Encoding: gzip")
    print(f"  Response: Vary: Accept-Encoding")

def simulate_real_world_scenarios():
    """Simulate real-world HTTP performance scenarios"""
    print(f"\n=== Real-World Performance Scenarios ===")
    
    analyzer = HTTPPerformanceAnalyzer()
    
    # Scenario 1: E-commerce product catalog
    print(f"\nScenario 1: E-commerce Product Catalog")
    for i in range(10):
        analyzer.simulate_request(
            'api.shop.com',
            f'/api/products?page={i+1}',
            use_compression=True,
            request_size=400
        )
    
    # Scenario 2: Social media feed
    print(f"Scenario 2: Social Media Feed")
    for i in range(15):
        analyzer.simulate_request(
            'api.social.com',
            f'/api/feed?offset={i*20}',
            use_compression=True,
            request_size=300
        )
    
    # Scenario 3: Image CDN (no compression)
    print(f"Scenario 3: Image CDN")
    for i in range(5):
        analyzer.simulate_request(
            'cdn.images.com',
            f'/images/photo_{i}.jpg',
            use_compression=False,
            request_size=200
        )
    
    # Analyze results
    analyzer.analyze_performance()
    
    # Connection pool stats
    print(f"\nConnection Pool Statistics:")
    for stat, count in analyzer.connection_pool.connection_stats.items():
        print(f"  {stat.replace('_', ' ').title()}: {count}")

def demonstrate_http_caching_strategies():
    """Demonstrate HTTP caching strategies"""
    print(f"\n=== HTTP Caching Strategies ===")
    
    strategies = [
        {
            'name': 'Cache-Control: max-age',
            'header': 'Cache-Control: max-age=3600',
            'behavior': 'Cache for 1 hour, no validation needed',
            'use_case': 'Static assets (CSS, JS, images)'
        },
        {
            'name': 'ETag Validation',
            'header': 'ETag: "abc123"',
            'behavior': 'Validate with server using If-None-Match',
            'use_case': 'Dynamic content that changes infrequently'
        },
        {
            'name': 'Last-Modified',
            'header': 'Last-Modified: Wed, 21 Oct 2015 07:28:00 GMT',
            'behavior': 'Validate with server using If-Modified-Since',
            'use_case': 'File-based resources'
        },
        {
            'name': 'Cache-Control: no-cache',
            'header': 'Cache-Control: no-cache',
            'behavior': 'Must validate with server before use',
            'use_case': 'Sensitive or frequently changing data'
        },
        {
            'name': 'Cache-Control: private',
            'header': 'Cache-Control: private, max-age=300',
            'behavior': 'Only browser cache, not shared proxies',
            'use_case': 'User-specific content'
        }
    ]
    
    for strategy in strategies:
        print(f"\n{strategy['name']}:")
        print(f"  Header: {strategy['header']}")
        print(f"  Behavior: {strategy['behavior']}")
        print(f"  Use Case: {strategy['use_case']}")

if __name__ == "__main__":
    # HTTP keep-alive demonstration
    simulate_http_keep_alive()
    
    # HTTP pipelining
    demonstrate_http_pipelining()
    
    # HTTP compression
    analyze_http_compression()
    
    # Real-world scenarios
    simulate_real_world_scenarios()
    
    # Caching strategies
    demonstrate_http_caching_strategies()
