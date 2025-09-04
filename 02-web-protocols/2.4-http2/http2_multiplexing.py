#!/usr/bin/env python3
"""
HTTP/2 Stream Multiplexing Simulation
Demonstrates HTTP/2 binary framing, stream multiplexing, and performance benefits
"""

import time
import random
import json
from collections import defaultdict, deque
from datetime import datetime

class HTTP2Frame:
    def __init__(self, frame_type, flags=0, stream_id=0, payload=b''):
        self.length = len(payload)
        self.frame_type = frame_type
        self.flags = flags
        self.stream_id = stream_id
        self.payload = payload
        self.timestamp = time.time()
    
    def __str__(self):
        return f"Frame(type={self.frame_type}, stream={self.stream_id}, len={self.length}, flags={self.flags})"

class HTTP2Stream:
    def __init__(self, stream_id, priority=16):
        self.stream_id = stream_id
        self.state = 'idle'
        self.priority = priority
        self.dependency = 0
        self.weight = 16
        self.window_size = 65535  # Initial flow control window
        self.headers = {}
        self.data_frames = []
        self.created_at = time.time()
        self.completed_at = None
        
    def add_headers(self, headers):
        self.headers.update(headers)
        self.state = 'open'
    
    def add_data(self, data):
        self.data_frames.append(data)
    
    def close(self):
        self.state = 'closed'
        self.completed_at = time.time()
    
    def get_duration(self):
        if self.completed_at:
            return self.completed_at - self.created_at
        return time.time() - self.created_at

class HTTP2Connection:
    def __init__(self, is_server=False):
        self.is_server = is_server
        self.streams = {}
        self.next_stream_id = 2 if is_server else 1
        self.connection_window_size = 65535
        self.max_concurrent_streams = 100
        self.frame_queue = deque()
        self.settings = {
            'HEADER_TABLE_SIZE': 4096,
            'ENABLE_PUSH': 1,
            'MAX_CONCURRENT_STREAMS': 100,
            'INITIAL_WINDOW_SIZE': 65535,
            'MAX_FRAME_SIZE': 16384,
            'MAX_HEADER_LIST_SIZE': 8192
        }
        self.hpack_table = []
        self.connection_stats = {
            'frames_sent': 0,
            'frames_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'streams_created': 0,
            'streams_completed': 0
        }
    
    def create_stream(self, priority=16):
        """Create a new stream"""
        stream_id = self.next_stream_id
        self.next_stream_id += 2  # Odd for client, even for server
        
        stream = HTTP2Stream(stream_id, priority)
        self.streams[stream_id] = stream
        self.connection_stats['streams_created'] += 1
        
        return stream
    
    def send_frame(self, frame):
        """Send an HTTP/2 frame"""
        self.frame_queue.append(frame)
        self.connection_stats['frames_sent'] += 1
        self.connection_stats['bytes_sent'] += frame.length + 9  # 9-byte frame header
        
        # Simulate network transmission time
        transmission_time = (frame.length + 9) / (1024 * 1024)  # 1MB/s
        time.sleep(min(transmission_time, 0.01))  # Cap at 10ms for demo
        
        return frame
    
    def receive_frame(self, frame):
        """Receive an HTTP/2 frame"""
        self.connection_stats['frames_received'] += 1
        self.connection_stats['bytes_received'] += frame.length + 9
        
        # Process frame based on type
        if frame.frame_type == 'HEADERS':
            self._process_headers_frame(frame)
        elif frame.frame_type == 'DATA':
            self._process_data_frame(frame)
        elif frame.frame_type == 'SETTINGS':
            self._process_settings_frame(frame)
        elif frame.frame_type == 'WINDOW_UPDATE':
            self._process_window_update_frame(frame)
    
    def _process_headers_frame(self, frame):
        """Process HEADERS frame"""
        if frame.stream_id not in self.streams:
            self.streams[frame.stream_id] = HTTP2Stream(frame.stream_id)
        
        # Simulate header decompression
        headers = json.loads(frame.payload.decode()) if frame.payload else {}
        self.streams[frame.stream_id].add_headers(headers)
    
    def _process_data_frame(self, frame):
        """Process DATA frame"""
        if frame.stream_id in self.streams:
            self.streams[frame.stream_id].add_data(frame.payload)
            
            # Check if END_STREAM flag is set
            if frame.flags & 0x1:  # END_STREAM
                self.streams[frame.stream_id].close()
                self.connection_stats['streams_completed'] += 1
    
    def _process_settings_frame(self, frame):
        """Process SETTINGS frame"""
        if frame.payload:
            settings = json.loads(frame.payload.decode())
            self.settings.update(settings)
    
    def _process_window_update_frame(self, frame):
        """Process WINDOW_UPDATE frame"""
        if frame.stream_id == 0:
            # Connection-level window update
            increment = int.from_bytes(frame.payload, 'big') if frame.payload else 0
            self.connection_window_size += increment
        elif frame.stream_id in self.streams:
            # Stream-level window update
            increment = int.from_bytes(frame.payload, 'big') if frame.payload else 0
            self.streams[frame.stream_id].window_size += increment

def simulate_http2_multiplexing():
    """Simulate HTTP/2 stream multiplexing"""
    print("=== HTTP/2 Stream Multiplexing Simulation ===")
    
    # Create client and server connections
    client = HTTP2Connection(is_server=False)
    server = HTTP2Connection(is_server=True)
    
    print(f"Establishing HTTP/2 connection...")
    
    # Connection preface and settings exchange
    settings_frame = HTTP2Frame('SETTINGS', payload=json.dumps({
        'MAX_CONCURRENT_STREAMS': 100,
        'INITIAL_WINDOW_SIZE': 65535
    }).encode())
    
    client.send_frame(settings_frame)
    server.receive_frame(settings_frame)
    
    # Simulate multiple concurrent requests
    requests = [
        {'path': '/api/user/profile', 'priority': 1, 'size': 512},
        {'path': '/api/products/list', 'priority': 2, 'size': 2048},
        {'path': '/css/main.css', 'priority': 3, 'size': 1024},
        {'path': '/js/app.js', 'priority': 3, 'size': 4096},
        {'path': '/images/logo.png', 'priority': 4, 'size': 8192},
        {'path': '/api/cart/items', 'priority': 1, 'size': 256},
        {'path': '/fonts/roboto.woff2', 'priority': 5, 'size': 1536}
    ]
    
    print(f"\nSending {len(requests)} concurrent requests:")
    
    # Send all requests concurrently
    start_time = time.time()
    streams = []
    
    for i, req in enumerate(requests):
        # Create stream
        stream = client.create_stream(req['priority'])
        streams.append(stream)
        
        # Send HEADERS frame
        headers = {
            ':method': 'GET',
            ':path': req['path'],
            ':scheme': 'https',
            ':authority': 'example.com',
            'user-agent': 'HTTP2-Client/1.0'
        }
        
        headers_frame = HTTP2Frame(
            'HEADERS',
            flags=0x4,  # END_HEADERS
            stream_id=stream.stream_id,
            payload=json.dumps(headers).encode()
        )
        
        client.send_frame(headers_frame)
        server.receive_frame(headers_frame)
        
        print(f"  Stream {stream.stream_id}: {req['path']} (priority {req['priority']})")
    
    # Simulate server responses
    print(f"\nReceiving responses (multiplexed):")
    
    for i, (stream, req) in enumerate(zip(streams, requests)):
        # Server sends response headers
        response_headers = {
            ':status': '200',
            'content-type': 'application/json' if '/api/' in req['path'] else 'text/html',
            'content-length': str(req['size']),
            'cache-control': 'max-age=3600'
        }
        
        headers_frame = HTTP2Frame(
            'HEADERS',
            flags=0x4,  # END_HEADERS
            stream_id=stream.stream_id,
            payload=json.dumps(response_headers).encode()
        )
        
        server.send_frame(headers_frame)
        client.receive_frame(headers_frame)
        
        # Server sends response data
        data_frame = HTTP2Frame(
            'DATA',
            flags=0x1,  # END_STREAM
            stream_id=stream.stream_id,
            payload=b'x' * req['size']  # Simulate response data
        )
        
        server.send_frame(data_frame)
        client.receive_frame(data_frame)
        
        print(f"  Stream {stream.stream_id}: {req['size']} bytes received")
    
    total_time = time.time() - start_time
    
    print(f"\n✓ All requests completed in {total_time:.3f}s")
    print(f"  Streams created: {client.connection_stats['streams_created']}")
    print(f"  Frames sent: {client.connection_stats['frames_sent'] + server.connection_stats['frames_sent']}")
    print(f"  Total bytes: {client.connection_stats['bytes_sent'] + server.connection_stats['bytes_sent']:,}")
    
    return client, server, total_time

def compare_http1_vs_http2():
    """Compare HTTP/1.1 vs HTTP/2 performance"""
    print(f"\n=== HTTP/1.1 vs HTTP/2 Performance Comparison ===")
    
    requests = [
        {'path': '/index.html', 'size': 2048},
        {'path': '/css/main.css', 'size': 1024},
        {'path': '/js/app.js', 'size': 4096},
        {'path': '/api/data.json', 'size': 512},
        {'path': '/images/logo.png', 'size': 8192},
        {'path': '/fonts/font.woff2', 'size': 1536}
    ]
    
    # Simulate HTTP/1.1 (sequential with connection limits)
    print(f"\nHTTP/1.1 Simulation (6 connections max):")
    http1_start = time.time()
    
    # Group requests by connection (max 6 concurrent)
    connections = [[] for _ in range(6)]
    for i, req in enumerate(requests):
        connections[i % 6].append(req)
    
    connection_times = []
    for i, conn_requests in enumerate(connections):
        if not conn_requests:
            continue
            
        conn_time = 0
        print(f"  Connection {i+1}:")
        
        for req in conn_requests:
            # TCP handshake overhead (first request only)
            if conn_time == 0:
                handshake_time = random.uniform(0.02, 0.05)
                conn_time += handshake_time
                print(f"    TCP handshake: {handshake_time:.3f}s")
            
            # Request/response time
            request_time = req['size'] / (1024 * 1024) + random.uniform(0.01, 0.03)
            conn_time += request_time
            print(f"    {req['path']}: {request_time:.3f}s")
        
        connection_times.append(conn_time)
    
    http1_total = max(connection_times) if connection_times else 0
    http1_end = time.time()
    
    # Simulate HTTP/2 (single connection, multiplexed)
    print(f"\nHTTP/2 Simulation (single connection, multiplexed):")
    http2_start = time.time()
    
    # Single TCP handshake
    handshake_time = random.uniform(0.02, 0.05)
    print(f"  TCP + TLS handshake: {handshake_time:.3f}s")
    
    # All requests can be sent concurrently
    max_request_time = 0
    print(f"  Concurrent streams:")
    
    for req in requests:
        request_time = req['size'] / (1024 * 1024) + random.uniform(0.005, 0.015)
        max_request_time = max(max_request_time, request_time)
        print(f"    {req['path']}: {request_time:.3f}s")
    
    http2_total = handshake_time + max_request_time
    http2_end = time.time()
    
    # Results
    print(f"\nPerformance Comparison:")
    print(f"  HTTP/1.1 Total Time: {http1_total:.3f}s")
    print(f"  HTTP/2 Total Time: {http2_total:.3f}s")
    
    improvement = ((http1_total - http2_total) / http1_total) * 100
    print(f"  HTTP/2 Improvement: {improvement:.1f}% faster")
    
    print(f"\nHTTP/2 Advantages:")
    print(f"  • Single TCP connection reduces overhead")
    print(f"  • Stream multiplexing eliminates head-of-line blocking")
    print(f"  • Binary protocol is more efficient")
    print(f"  • Header compression reduces bandwidth")
    print(f"  • Server push can proactively send resources")
    
    return http1_total, http2_total

def demonstrate_http2_server_push():
    """Demonstrate HTTP/2 server push feature"""
    print(f"\n=== HTTP/2 Server Push Demonstration ===")
    
    client = HTTP2Connection(is_server=False)
    server = HTTP2Connection(is_server=True)
    
    print(f"Client requests: GET /index.html")
    
    # Client requests index.html
    stream = client.create_stream()
    headers_frame = HTTP2Frame(
        'HEADERS',
        flags=0x5,  # END_HEADERS + END_STREAM
        stream_id=stream.stream_id,
        payload=json.dumps({
            ':method': 'GET',
            ':path': '/index.html',
            ':scheme': 'https',
            ':authority': 'example.com'
        }).encode()
    )
    
    client.send_frame(headers_frame)
    server.receive_frame(headers_frame)
    
    # Server analyzes request and decides to push resources
    push_resources = [
        {'path': '/css/main.css', 'type': 'text/css', 'size': 1024},
        {'path': '/js/app.js', 'type': 'application/javascript', 'size': 2048},
        {'path': '/images/logo.png', 'type': 'image/png', 'size': 4096}
    ]
    
    print(f"\nServer decides to push {len(push_resources)} resources:")
    
    pushed_streams = []
    for resource in push_resources:
        # Server sends PUSH_PROMISE frame
        push_stream = server.create_stream()
        pushed_streams.append(push_stream)
        
        push_promise_frame = HTTP2Frame(
            'PUSH_PROMISE',
            stream_id=stream.stream_id,  # Associated with original request
            payload=json.dumps({
                'promised_stream_id': push_stream.stream_id,
                ':method': 'GET',
                ':path': resource['path'],
                ':scheme': 'https',
                ':authority': 'example.com'
            }).encode()
        )
        
        server.send_frame(push_promise_frame)
        client.receive_frame(push_promise_frame)
        
        print(f"  PUSH_PROMISE: {resource['path']} (stream {push_stream.stream_id})")
    
    # Server sends original response
    print(f"\nServer sends responses:")
    
    # Original HTML response
    html_headers = HTTP2Frame(
        'HEADERS',
        flags=0x4,  # END_HEADERS
        stream_id=stream.stream_id,
        payload=json.dumps({
            ':status': '200',
            'content-type': 'text/html',
            'content-length': '2048'
        }).encode()
    )
    
    server.send_frame(html_headers)
    client.receive_frame(html_headers)
    
    html_data = HTTP2Frame(
        'DATA',
        flags=0x1,  # END_STREAM
        stream_id=stream.stream_id,
        payload=b'<html>...</html>' * 100  # Simulate HTML content
    )
    
    server.send_frame(html_data)
    client.receive_frame(html_data)
    
    print(f"  Original response: /index.html (stream {stream.stream_id})")
    
    # Pushed resource responses
    for push_stream, resource in zip(pushed_streams, push_resources):
        # Headers
        push_headers = HTTP2Frame(
            'HEADERS',
            flags=0x4,  # END_HEADERS
            stream_id=push_stream.stream_id,
            payload=json.dumps({
                ':status': '200',
                'content-type': resource['type'],
                'content-length': str(resource['size'])
            }).encode()
        )
        
        server.send_frame(push_headers)
        client.receive_frame(push_headers)
        
        # Data
        push_data = HTTP2Frame(
            'DATA',
            flags=0x1,  # END_STREAM
            stream_id=push_stream.stream_id,
            payload=b'x' * resource['size']
        )
        
        server.send_frame(push_data)
        client.receive_frame(push_data)
        
        print(f"  Pushed response: {resource['path']} (stream {push_stream.stream_id})")
    
    print(f"\nServer Push Benefits:")
    print(f"  • Eliminates round trips for critical resources")
    print(f"  • Resources arrive before browser requests them")
    print(f"  • Improves perceived performance")
    print(f"  • Reduces time to first meaningful paint")
    
    print(f"\nServer Push Considerations:")
    print(f"  • Only push resources the client will definitely need")
    print(f"  • Respect client cache (don't push cached resources)")
    print(f"  • Monitor push effectiveness and adjust strategy")
    print(f"  • Client can send RST_STREAM to reject unwanted pushes")
    
    return client, server, pushed_streams

def analyze_http2_flow_control():
    """Analyze HTTP/2 flow control mechanisms"""
    print(f"\n=== HTTP/2 Flow Control Analysis ===")
    
    connection = HTTP2Connection()
    
    print(f"Flow Control Levels:")
    print(f"  • Connection-level: Controls total data flow")
    print(f"  • Stream-level: Controls individual stream data flow")
    print(f"  • Both use sliding window protocol")
    
    print(f"\nInitial Window Sizes:")
    print(f"  Connection window: {connection.connection_window_size:,} bytes")
    print(f"  Stream window: {connection.settings['INITIAL_WINDOW_SIZE']:,} bytes")
    
    # Simulate flow control scenario
    print(f"\nFlow Control Scenario:")
    
    # Create a stream
    stream = connection.create_stream()
    print(f"  Stream {stream.stream_id} created with {stream.window_size:,} byte window")
    
    # Simulate sending data that exceeds window
    data_to_send = 100000  # 100KB
    chunk_size = 16384     # 16KB chunks
    
    print(f"  Attempting to send {data_to_send:,} bytes in {chunk_size:,} byte chunks")
    
    bytes_sent = 0
    chunk_count = 0
    
    while bytes_sent < data_to_send:
        # Check available window space
        available_window = min(stream.window_size, connection.connection_window_size)
        
        if available_window <= 0:
            print(f"    Flow control: Window exhausted, waiting for WINDOW_UPDATE")
            
            # Simulate receiving WINDOW_UPDATE
            window_update = random.randint(16384, 32768)
            stream.window_size += window_update
            connection.connection_window_size += window_update
            
            print(f"    Received WINDOW_UPDATE: +{window_update:,} bytes")
            continue
        
        # Send data chunk
        chunk_to_send = min(chunk_size, data_to_send - bytes_sent, available_window)
        
        data_frame = HTTP2Frame(
            'DATA',
            stream_id=stream.stream_id,
            payload=b'x' * chunk_to_send
        )
        
        connection.send_frame(data_frame)
        
        # Update windows
        stream.window_size -= chunk_to_send
        connection.connection_window_size -= chunk_to_send
        bytes_sent += chunk_to_send
        chunk_count += 1
        
        print(f"    Chunk {chunk_count}: {chunk_to_send:,} bytes sent "
              f"(stream window: {stream.window_size:,}, "
              f"connection window: {connection.connection_window_size:,})")
    
    print(f"  ✓ Successfully sent {bytes_sent:,} bytes in {chunk_count} chunks")
    
    print(f"\nFlow Control Benefits:")
    print(f"  • Prevents fast senders from overwhelming slow receivers")
    print(f"  • Allows prioritization of important streams")
    print(f"  • Provides backpressure mechanism")
    print(f"  • Enables fair resource allocation")
    
    return connection, bytes_sent, chunk_count

if __name__ == "__main__":
    # HTTP/2 multiplexing simulation
    client, server, http2_time = simulate_http2_multiplexing()
    
    # HTTP/1.1 vs HTTP/2 comparison
    http1_time, http2_comparison_time = compare_http1_vs_http2()
    
    # Server push demonstration
    push_client, push_server, pushed_streams = demonstrate_http2_server_push()
    
    # Flow control analysis
    flow_connection, bytes_sent, chunks = analyze_http2_flow_control()
