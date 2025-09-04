#!/usr/bin/env python3
"""
HTTP/2 & gRPC Multiplexing Demonstration
Shows concurrent stream processing and flow control
"""

import asyncio
import time
import random
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, AsyncIterator
from enum import Enum
import threading
from collections import defaultdict

class StreamState(Enum):
    IDLE = "idle"
    OPEN = "open"
    HALF_CLOSED_LOCAL = "half_closed_local"
    HALF_CLOSED_REMOTE = "half_closed_remote"
    CLOSED = "closed"

class FrameType(Enum):
    HEADERS = "HEADERS"
    DATA = "DATA"
    WINDOW_UPDATE = "WINDOW_UPDATE"
    RST_STREAM = "RST_STREAM"
    SETTINGS = "SETTINGS"
    PING = "PING"

@dataclass
class HTTP2Frame:
    stream_id: int
    frame_type: FrameType
    flags: List[str]
    payload: bytes
    timestamp: float

@dataclass
class StreamInfo:
    stream_id: int
    state: StreamState
    window_size: int
    headers: Dict[str, str]
    data_received: int
    data_sent: int
    created_at: float

class HTTP2Connection:
    """Simulates HTTP/2 connection with multiplexing"""
    
    def __init__(self, connection_id: str):
        self.connection_id = connection_id
        self.streams: Dict[int, StreamInfo] = {}
        self.next_stream_id = 1
        self.connection_window = 65535
        self.max_concurrent_streams = 100
        self.settings = {
            'HEADER_TABLE_SIZE': 4096,
            'ENABLE_PUSH': 0,
            'MAX_CONCURRENT_STREAMS': 100,
            'INITIAL_WINDOW_SIZE': 65535,
            'MAX_FRAME_SIZE': 16384,
            'MAX_HEADER_LIST_SIZE': 8192
        }
        self.frame_log: List[HTTP2Frame] = []
        self.stats = {
            'streams_created': 0,
            'streams_completed': 0,
            'frames_sent': 0,
            'frames_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0
        }
        self._lock = threading.Lock()
    
    def create_stream(self, headers: Dict[str, str]) -> int:
        """Create new HTTP/2 stream"""
        with self._lock:
            if len(self.streams) >= self.max_concurrent_streams:
                raise Exception("Maximum concurrent streams exceeded")
            
            stream_id = self.next_stream_id
            self.next_stream_id += 2  # Client streams are odd
            
            stream = StreamInfo(
                stream_id=stream_id,
                state=StreamState.OPEN,
                window_size=self.settings['INITIAL_WINDOW_SIZE'],
                headers=headers,
                data_received=0,
                data_sent=0,
                created_at=time.time()
            )
            
            self.streams[stream_id] = stream
            self.stats['streams_created'] += 1
            
            # Log HEADERS frame
            frame = HTTP2Frame(
                stream_id=stream_id,
                frame_type=FrameType.HEADERS,
                flags=['END_HEADERS'],
                payload=json.dumps(headers).encode(),
                timestamp=time.time()
            )
            self.frame_log.append(frame)
            self.stats['frames_sent'] += 1
            
            print(f"[{self.connection_id}] Created stream {stream_id}: {headers.get(':method', 'UNKNOWN')} {headers.get(':path', '/')}")
            return stream_id
    
    def send_data(self, stream_id: int, data: bytes, end_stream: bool = False) -> bool:
        """Send data on stream with flow control"""
        with self._lock:
            if stream_id not in self.streams:
                return False
            
            stream = self.streams[stream_id]
            if stream.state not in [StreamState.OPEN, StreamState.HALF_CLOSED_REMOTE]:
                return False
            
            # Check flow control
            if len(data) > stream.window_size:
                print(f"[{self.connection_id}] Flow control: Stream {stream_id} window too small")
                return False
            
            if len(data) > self.connection_window:
                print(f"[{self.connection_id}] Flow control: Connection window too small")
                return False
            
            # Update windows
            stream.window_size -= len(data)
            self.connection_window -= len(data)
            stream.data_sent += len(data)
            self.stats['bytes_sent'] += len(data)
            
            # Log DATA frame
            flags = ['END_STREAM'] if end_stream else []
            frame = HTTP2Frame(
                stream_id=stream_id,
                frame_type=FrameType.DATA,
                flags=flags,
                payload=data,
                timestamp=time.time()
            )
            self.frame_log.append(frame)
            self.stats['frames_sent'] += 1
            
            if end_stream:
                stream.state = StreamState.HALF_CLOSED_LOCAL
            
            return True
    
    def receive_data(self, stream_id: int, data: bytes) -> bool:
        """Receive data on stream"""
        with self._lock:
            if stream_id not in self.streams:
                return False
            
            stream = self.streams[stream_id]
            stream.data_received += len(data)
            self.stats['bytes_received'] += len(data)
            
            # Send WINDOW_UPDATE if needed
            if stream.data_received % 32768 == 0:  # Update every 32KB
                self.send_window_update(stream_id, 32768)
            
            return True
    
    def send_window_update(self, stream_id: int, increment: int):
        """Send WINDOW_UPDATE frame"""
        if stream_id in self.streams:
            self.streams[stream_id].window_size += increment
        
        if stream_id == 0:  # Connection-level
            self.connection_window += increment
        
        frame = HTTP2Frame(
            stream_id=stream_id,
            frame_type=FrameType.WINDOW_UPDATE,
            flags=[],
            payload=increment.to_bytes(4, 'big'),
            timestamp=time.time()
        )
        self.frame_log.append(frame)
        self.stats['frames_sent'] += 1
    
    def close_stream(self, stream_id: int, error_code: int = 0):
        """Close stream"""
        with self._lock:
            if stream_id not in self.streams:
                return
            
            stream = self.streams[stream_id]
            stream.state = StreamState.CLOSED
            self.stats['streams_completed'] += 1
            
            if error_code != 0:
                frame = HTTP2Frame(
                    stream_id=stream_id,
                    frame_type=FrameType.RST_STREAM,
                    flags=[],
                    payload=error_code.to_bytes(4, 'big'),
                    timestamp=time.time()
                )
                self.frame_log.append(frame)
                self.stats['frames_sent'] += 1
            
            duration = time.time() - stream.created_at
            print(f"[{self.connection_id}] Closed stream {stream_id} after {duration:.2f}s")
    
    def get_active_streams(self) -> List[int]:
        """Get list of active stream IDs"""
        with self._lock:
            return [sid for sid, stream in self.streams.items() 
                   if stream.state in [StreamState.OPEN, StreamState.HALF_CLOSED_LOCAL, StreamState.HALF_CLOSED_REMOTE]]
    
    def get_stats(self) -> Dict:
        """Get connection statistics"""
        with self._lock:
            return {
                'connection_id': self.connection_id,
                'active_streams': len(self.get_active_streams()),
                'connection_window': self.connection_window,
                **self.stats
            }

class GRPCService:
    """Simulates gRPC service with different streaming patterns"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.connection = HTTP2Connection(f"grpc-{service_name}")
        self.request_count = 0
        self.active_streams = {}
    
    async def unary_rpc(self, method: str, request_data: bytes) -> bytes:
        """Unary RPC: Single request → Single response"""
        headers = {
            ':method': 'POST',
            ':path': f'/{self.service_name}/{method}',
            ':scheme': 'https',
            ':authority': 'api.example.com',
            'content-type': 'application/grpc',
            'grpc-encoding': 'gzip',
            'grpc-accept-encoding': 'gzip'
        }
        
        stream_id = self.connection.create_stream(headers)
        
        # Send request
        self.connection.send_data(stream_id, request_data, end_stream=True)
        
        # Simulate processing delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Generate response
        response_data = f"Response for {method}: {len(request_data)} bytes processed".encode()
        
        # Simulate receiving response
        self.connection.receive_data(stream_id, response_data)
        self.connection.close_stream(stream_id)
        
        return response_data
    
    async def server_streaming_rpc(self, method: str, request_data: bytes) -> AsyncIterator[bytes]:
        """Server Streaming RPC: Single request → Multiple responses"""
        headers = {
            ':method': 'POST',
            ':path': f'/{self.service_name}/{method}',
            ':scheme': 'https',
            ':authority': 'api.example.com',
            'content-type': 'application/grpc'
        }
        
        stream_id = self.connection.create_stream(headers)
        self.connection.send_data(stream_id, request_data, end_stream=True)
        
        # Stream multiple responses
        for i in range(5):
            await asyncio.sleep(0.2)
            response_data = f"Chunk {i+1} for {method}".encode()
            self.connection.receive_data(stream_id, response_data)
            yield response_data
        
        self.connection.close_stream(stream_id)
    
    async def client_streaming_rpc(self, method: str, request_stream: AsyncIterator[bytes]) -> bytes:
        """Client Streaming RPC: Multiple requests → Single response"""
        headers = {
            ':method': 'POST',
            ':path': f'/{self.service_name}/{method}',
            ':scheme': 'https',
            ':authority': 'api.example.com',
            'content-type': 'application/grpc'
        }
        
        stream_id = self.connection.create_stream(headers)
        total_bytes = 0
        
        # Send multiple requests
        async for request_data in request_stream:
            self.connection.send_data(stream_id, request_data)
            total_bytes += len(request_data)
            await asyncio.sleep(0.1)
        
        self.connection.send_data(stream_id, b'', end_stream=True)
        
        # Generate final response
        response_data = f"Processed {total_bytes} bytes total".encode()
        self.connection.receive_data(stream_id, response_data)
        self.connection.close_stream(stream_id)
        
        return response_data
    
    async def bidirectional_streaming_rpc(self, method: str, request_stream: AsyncIterator[bytes]) -> AsyncIterator[bytes]:
        """Bidirectional Streaming RPC: Multiple requests ↔ Multiple responses"""
        headers = {
            ':method': 'POST',
            ':path': f'/{self.service_name}/{method}',
            ':scheme': 'https',
            ':authority': 'api.example.com',
            'content-type': 'application/grpc'
        }
        
        stream_id = self.connection.create_stream(headers)
        
        # Process requests and yield responses concurrently
        async for request_data in request_stream:
            self.connection.send_data(stream_id, request_data)
            
            # Generate immediate response
            response_data = f"Echo: {request_data.decode()}".encode()
            self.connection.receive_data(stream_id, response_data)
            yield response_data
            
            await asyncio.sleep(0.05)
        
        self.connection.close_stream(stream_id)

class MultiplexingDemo:
    """Demonstrates HTTP/2 multiplexing with concurrent streams"""
    
    def __init__(self):
        self.services = {
            'video': GRPCService('VideoService'),
            'analytics': GRPCService('AnalyticsService'),
            'content': GRPCService('ContentService'),
            'auth': GRPCService('AuthService')
        }
        self.demo_stats = defaultdict(int)
    
    async def simulate_concurrent_requests(self):
        """Simulate concurrent requests across multiple services"""
        print("=== Starting Concurrent Request Simulation ===")
        
        tasks = []
        
        # Unary RPCs
        for i in range(10):
            service = random.choice(list(self.services.values()))
            task = asyncio.create_task(
                service.unary_rpc(f"GetData{i}", f"Request {i} data".encode())
            )
            tasks.append(task)
            self.demo_stats['unary_requests'] += 1
        
        # Server streaming RPCs
        for i in range(3):
            service = random.choice(list(self.services.values()))
            task = asyncio.create_task(
                self.consume_server_stream(service, f"StreamData{i}")
            )
            tasks.append(task)
            self.demo_stats['server_streaming_requests'] += 1
        
        # Client streaming RPCs
        for i in range(2):
            service = random.choice(list(self.services.values()))
            task = asyncio.create_task(
                self.send_client_stream(service, f"UploadData{i}")
            )
            tasks.append(task)
            self.demo_stats['client_streaming_requests'] += 1
        
        # Bidirectional streaming RPCs
        for i in range(2):
            service = random.choice(list(self.services.values()))
            task = asyncio.create_task(
                self.bidirectional_stream(service, f"ProcessStream{i}")
            )
            tasks.append(task)
            self.demo_stats['bidirectional_requests'] += 1
        
        # Wait for all requests to complete
        await asyncio.gather(*tasks)
        
        print(f"\n=== Completed {len(tasks)} concurrent requests ===")
    
    async def consume_server_stream(self, service: GRPCService, method: str):
        """Consume server streaming RPC"""
        request_data = f"Stream request for {method}".encode()
        async for response in service.server_streaming_rpc(method, request_data):
            print(f"[{service.service_name}] Received: {response.decode()}")
    
    async def send_client_stream(self, service: GRPCService, method: str):
        """Send client streaming RPC"""
        async def request_generator():
            for i in range(5):
                yield f"Upload chunk {i} for {method}".encode()
                await asyncio.sleep(0.1)
        
        response = await service.client_streaming_rpc(method, request_generator())
        print(f"[{service.service_name}] Upload complete: {response.decode()}")
    
    async def bidirectional_stream(self, service: GRPCService, method: str):
        """Handle bidirectional streaming RPC"""
        async def request_generator():
            for i in range(3):
                yield f"Bidirectional message {i} for {method}".encode()
                await asyncio.sleep(0.15)
        
        async for response in service.bidirectional_streaming_rpc(method, request_generator()):
            print(f"[{service.service_name}] Bidirectional response: {response.decode()}")
    
    def print_connection_stats(self):
        """Print statistics for all connections"""
        print("\n=== HTTP/2 Connection Statistics ===")
        
        total_stats = defaultdict(int)
        for service_name, service in self.services.items():
            stats = service.connection.get_stats()
            print(f"\n{service_name.upper()} Service:")
            print(f"  Active Streams: {stats['active_streams']}")
            print(f"  Streams Created: {stats['streams_created']}")
            print(f"  Streams Completed: {stats['streams_completed']}")
            print(f"  Frames Sent: {stats['frames_sent']}")
            print(f"  Bytes Sent: {stats['bytes_sent']:,}")
            print(f"  Bytes Received: {stats['bytes_received']:,}")
            print(f"  Connection Window: {stats['connection_window']:,}")
            
            for key, value in stats.items():
                if isinstance(value, int):
                    total_stats[key] += value
        
        print(f"\nTOTAL ACROSS ALL CONNECTIONS:")
        print(f"  Total Streams Created: {total_stats['streams_created']}")
        print(f"  Total Frames Sent: {total_stats['frames_sent']}")
        print(f"  Total Bytes Transferred: {total_stats['bytes_sent'] + total_stats['bytes_received']:,}")
        
        print(f"\nDEMO STATISTICS:")
        for stat_name, count in self.demo_stats.items():
            print(f"  {stat_name.replace('_', ' ').title()}: {count}")
    
    def demonstrate_flow_control(self):
        """Demonstrate HTTP/2 flow control mechanisms"""
        print("\n=== Flow Control Demonstration ===")
        
        service = self.services['video']
        connection = service.connection
        
        # Create stream with small window
        headers = {':method': 'POST', ':path': '/test', 'content-type': 'application/grpc'}
        stream_id = connection.create_stream(headers)
        
        # Try to send large data
        large_data = b'x' * 100000  # 100KB
        print(f"Attempting to send {len(large_data):,} bytes...")
        
        success = connection.send_data(stream_id, large_data)
        if not success:
            print("❌ Send failed due to flow control limits")
            
            # Send in smaller chunks
            chunk_size = 16384  # 16KB chunks
            for i in range(0, len(large_data), chunk_size):
                chunk = large_data[i:i+chunk_size]
                if connection.send_data(stream_id, chunk):
                    print(f"✓ Sent chunk {i//chunk_size + 1}: {len(chunk)} bytes")
                    # Simulate window update
                    connection.send_window_update(stream_id, len(chunk))
                else:
                    print(f"❌ Chunk {i//chunk_size + 1} failed")
                    break
        else:
            print("✓ Large data sent successfully")
        
        connection.close_stream(stream_id)

async def main():
    """Main demonstration function"""
    demo = MultiplexingDemo()
    
    print("HTTP/2 & gRPC Multiplexing Demonstration")
    print("=" * 50)
    
    # Show initial connection state
    print("\nInitial connection state:")
    demo.print_connection_stats()
    
    # Simulate concurrent requests
    start_time = time.time()
    await demo.simulate_concurrent_requests()
    end_time = time.time()
    
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
    
    # Show final statistics
    demo.print_connection_stats()
    
    # Demonstrate flow control
    demo.demonstrate_flow_control()
    
    print("\n=== Multiplexing Benefits Demonstrated ===")
    print("✓ Multiple concurrent streams over single connection")
    print("✓ Different gRPC streaming patterns")
    print("✓ HTTP/2 flow control mechanisms")
    print("✓ Frame-level multiplexing")
    print("✓ Connection efficiency and resource sharing")

if __name__ == "__main__":
    asyncio.run(main())
