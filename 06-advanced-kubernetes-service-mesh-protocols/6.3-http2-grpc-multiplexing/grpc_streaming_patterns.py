#!/usr/bin/env python3
"""
gRPC Streaming Patterns Implementation
Demonstrates different gRPC streaming types with HTTP/2 multiplexing
"""

import asyncio
import time
import random
import json
from dataclasses import dataclass
from typing import AsyncIterator, List, Dict, Optional
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor

class StreamingType(Enum):
    UNARY = "unary"
    SERVER_STREAMING = "server_streaming"
    CLIENT_STREAMING = "client_streaming"
    BIDIRECTIONAL_STREAMING = "bidirectional_streaming"

@dataclass
class VideoChunk:
    chunk_id: int
    video_id: str
    data: bytes
    timestamp: float
    metadata: Dict[str, str]

@dataclass
class ProcessingResult:
    chunk_id: int
    status: str
    processing_time: float
    output_size: int
    quality_score: float

@dataclass
class StreamMetrics:
    stream_id: str
    streaming_type: StreamingType
    start_time: float
    end_time: Optional[float]
    messages_sent: int
    messages_received: int
    bytes_transferred: int
    errors: int

class VideoProcessingService:
    """Simulates video processing service with different streaming patterns"""
    
    def __init__(self, service_id: str):
        self.service_id = service_id
        self.active_streams: Dict[str, StreamMetrics] = {}
        self.processing_stats = {
            'total_chunks_processed': 0,
            'total_processing_time': 0.0,
            'average_quality_score': 0.0,
            'concurrent_streams': 0
        }
        self._lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def _create_stream_metrics(self, stream_id: str, streaming_type: StreamingType) -> StreamMetrics:
        """Create metrics tracking for a stream"""
        metrics = StreamMetrics(
            stream_id=stream_id,
            streaming_type=streaming_type,
            start_time=time.time(),
            end_time=None,
            messages_sent=0,
            messages_received=0,
            bytes_transferred=0,
            errors=0
        )
        
        with self._lock:
            self.active_streams[stream_id] = metrics
            self.processing_stats['concurrent_streams'] = len(self.active_streams)
        
        return metrics
    
    def _update_stream_metrics(self, stream_id: str, sent: int = 0, received: int = 0, bytes_count: int = 0, error: bool = False):
        """Update stream metrics"""
        with self._lock:
            if stream_id in self.active_streams:
                metrics = self.active_streams[stream_id]
                metrics.messages_sent += sent
                metrics.messages_received += received
                metrics.bytes_transferred += bytes_count
                if error:
                    metrics.errors += 1
    
    def _close_stream_metrics(self, stream_id: str):
        """Close stream metrics"""
        with self._lock:
            if stream_id in self.active_streams:
                metrics = self.active_streams[stream_id]
                metrics.end_time = time.time()
                del self.active_streams[stream_id]
                self.processing_stats['concurrent_streams'] = len(self.active_streams)
                
                duration = metrics.end_time - metrics.start_time
                print(f"[{self.service_id}] Stream {stream_id} completed in {duration:.2f}s "
                      f"({metrics.messages_sent} sent, {metrics.messages_received} received)")
    
    async def process_video_unary(self, video_id: str, chunk_data: bytes) -> ProcessingResult:
        """Unary RPC: Process single video chunk"""
        stream_id = f"unary-{video_id}-{int(time.time()*1000)}"
        metrics = self._create_stream_metrics(stream_id, StreamingType.UNARY)
        
        try:
            print(f"[{self.service_id}] Processing video chunk {video_id} (unary)")
            
            # Simulate processing delay
            processing_time = random.uniform(0.1, 0.5)
            await asyncio.sleep(processing_time)
            
            # Simulate processing
            quality_score = random.uniform(0.7, 0.95)
            output_size = len(chunk_data) + random.randint(-1000, 1000)
            
            result = ProcessingResult(
                chunk_id=1,
                status="completed",
                processing_time=processing_time,
                output_size=max(0, output_size),
                quality_score=quality_score
            )
            
            self._update_stream_metrics(stream_id, sent=1, received=1, bytes_count=len(chunk_data))
            
            with self._lock:
                self.processing_stats['total_chunks_processed'] += 1
                self.processing_stats['total_processing_time'] += processing_time
            
            return result
            
        except Exception as e:
            self._update_stream_metrics(stream_id, error=True)
            raise e
        finally:
            self._close_stream_metrics(stream_id)
    
    async def stream_video_chunks(self, video_id: str, chunk_count: int) -> AsyncIterator[VideoChunk]:
        """Server Streaming RPC: Stream video chunks to client"""
        stream_id = f"server-stream-{video_id}"
        metrics = self._create_stream_metrics(stream_id, StreamingType.SERVER_STREAMING)
        
        try:
            print(f"[{self.service_id}] Streaming {chunk_count} chunks for video {video_id}")
            
            for i in range(chunk_count):
                # Simulate chunk generation
                await asyncio.sleep(0.1)
                
                chunk_size = random.randint(1024, 8192)  # 1-8KB chunks
                chunk_data = b'x' * chunk_size
                
                chunk = VideoChunk(
                    chunk_id=i,
                    video_id=video_id,
                    data=chunk_data,
                    timestamp=time.time(),
                    metadata={
                        'resolution': '1080p',
                        'codec': 'h264',
                        'bitrate': str(random.randint(2000, 8000))
                    }
                )
                
                self._update_stream_metrics(stream_id, sent=1, bytes_count=len(chunk_data))
                yield chunk
                
                print(f"[{self.service_id}] Sent chunk {i+1}/{chunk_count} ({len(chunk_data)} bytes)")
        
        except Exception as e:
            self._update_stream_metrics(stream_id, error=True)
            raise e
        finally:
            self._close_stream_metrics(stream_id)
    
    async def upload_video_stream(self, video_id: str, chunk_stream: AsyncIterator[VideoChunk]) -> ProcessingResult:
        """Client Streaming RPC: Receive video chunks from client"""
        stream_id = f"client-stream-{video_id}"
        metrics = self._create_stream_metrics(stream_id, StreamingType.CLIENT_STREAMING)
        
        try:
            print(f"[{self.service_id}] Receiving video stream for {video_id}")
            
            total_chunks = 0
            total_bytes = 0
            start_time = time.time()
            
            async for chunk in chunk_stream:
                total_chunks += 1
                total_bytes += len(chunk.data)
                
                self._update_stream_metrics(stream_id, received=1, bytes_count=len(chunk.data))
                
                # Simulate processing each chunk
                await asyncio.sleep(0.05)
                
                print(f"[{self.service_id}] Received chunk {chunk.chunk_id} ({len(chunk.data)} bytes)")
            
            processing_time = time.time() - start_time
            quality_score = random.uniform(0.8, 0.95)
            
            result = ProcessingResult(
                chunk_id=total_chunks,
                status="upload_complete",
                processing_time=processing_time,
                output_size=total_bytes,
                quality_score=quality_score
            )
            
            with self._lock:
                self.processing_stats['total_chunks_processed'] += total_chunks
                self.processing_stats['total_processing_time'] += processing_time
            
            print(f"[{self.service_id}] Upload complete: {total_chunks} chunks, {total_bytes} bytes")
            return result
            
        except Exception as e:
            self._update_stream_metrics(stream_id, error=True)
            raise e
        finally:
            self._close_stream_metrics(stream_id)
    
    async def process_live_stream(self, video_id: str, input_stream: AsyncIterator[VideoChunk]) -> AsyncIterator[ProcessingResult]:
        """Bidirectional Streaming RPC: Process live video stream"""
        stream_id = f"bidi-stream-{video_id}"
        metrics = self._create_stream_metrics(stream_id, StreamingType.BIDIRECTIONAL_STREAMING)
        
        try:
            print(f"[{self.service_id}] Starting live stream processing for {video_id}")
            
            async for chunk in input_stream:
                # Simulate real-time processing
                processing_start = time.time()
                await asyncio.sleep(0.02)  # 20ms processing latency
                processing_time = time.time() - processing_start
                
                # Generate processing result
                quality_score = random.uniform(0.75, 0.92)
                output_size = len(chunk.data) + random.randint(-100, 100)
                
                result = ProcessingResult(
                    chunk_id=chunk.chunk_id,
                    status="processed",
                    processing_time=processing_time,
                    output_size=max(0, output_size),
                    quality_score=quality_score
                )
                
                self._update_stream_metrics(stream_id, sent=1, received=1, bytes_count=len(chunk.data))
                
                print(f"[{self.service_id}] Processed live chunk {chunk.chunk_id} "
                      f"(quality: {quality_score:.2f}, latency: {processing_time*1000:.1f}ms)")
                
                yield result
                
                with self._lock:
                    self.processing_stats['total_chunks_processed'] += 1
                    self.processing_stats['total_processing_time'] += processing_time
        
        except Exception as e:
            self._update_stream_metrics(stream_id, error=True)
            raise e
        finally:
            self._close_stream_metrics(stream_id)

class StreamingClient:
    """Client that demonstrates different streaming patterns"""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.service = VideoProcessingService("video-processor")
    
    async def test_unary_processing(self):
        """Test unary RPC pattern"""
        print(f"\n[{self.client_id}] Testing Unary RPC...")
        
        chunk_data = b'x' * 4096  # 4KB video chunk
        result = await self.service.process_video_unary("video-001", chunk_data)
        
        print(f"[{self.client_id}] Unary result: {result.status}, quality: {result.quality_score:.2f}")
    
    async def test_server_streaming(self):
        """Test server streaming RPC pattern"""
        print(f"\n[{self.client_id}] Testing Server Streaming RPC...")
        
        chunk_count = 0
        total_bytes = 0
        
        async for chunk in self.service.stream_video_chunks("video-002", 5):
            chunk_count += 1
            total_bytes += len(chunk.data)
            print(f"[{self.client_id}] Received chunk {chunk.chunk_id}: {len(chunk.data)} bytes")
        
        print(f"[{self.client_id}] Server streaming complete: {chunk_count} chunks, {total_bytes} bytes")
    
    async def test_client_streaming(self):
        """Test client streaming RPC pattern"""
        print(f"\n[{self.client_id}] Testing Client Streaming RPC...")
        
        async def generate_chunks():
            for i in range(7):
                chunk_size = random.randint(2048, 6144)
                chunk_data = b'y' * chunk_size
                
                chunk = VideoChunk(
                    chunk_id=i,
                    video_id="video-003",
                    data=chunk_data,
                    timestamp=time.time(),
                    metadata={'source': 'client_upload'}
                )
                
                print(f"[{self.client_id}] Sending chunk {i}: {len(chunk_data)} bytes")
                yield chunk
                await asyncio.sleep(0.1)
        
        result = await self.service.upload_video_stream("video-003", generate_chunks())
        print(f"[{self.client_id}] Client streaming result: {result.status}, quality: {result.quality_score:.2f}")
    
    async def test_bidirectional_streaming(self):
        """Test bidirectional streaming RPC pattern"""
        print(f"\n[{self.client_id}] Testing Bidirectional Streaming RPC...")
        
        async def generate_live_chunks():
            for i in range(6):
                chunk_size = random.randint(1024, 3072)
                chunk_data = b'z' * chunk_size
                
                chunk = VideoChunk(
                    chunk_id=i,
                    video_id="live-stream-001",
                    data=chunk_data,
                    timestamp=time.time(),
                    metadata={'stream_type': 'live', 'fps': '30'}
                )
                
                print(f"[{self.client_id}] Sending live chunk {i}: {len(chunk_data)} bytes")
                yield chunk
                await asyncio.sleep(0.15)
        
        result_count = 0
        async for result in self.service.process_live_stream("live-stream-001", generate_live_chunks()):
            result_count += 1
            print(f"[{self.client_id}] Received live result {result.chunk_id}: "
                  f"quality {result.quality_score:.2f}, latency {result.processing_time*1000:.1f}ms")
        
        print(f"[{self.client_id}] Bidirectional streaming complete: {result_count} results processed")
    
    async def run_all_tests(self):
        """Run all streaming pattern tests"""
        await self.test_unary_processing()
        await self.test_server_streaming()
        await self.test_client_streaming()
        await self.test_bidirectional_streaming()

class ConcurrentStreamingDemo:
    """Demonstrates concurrent streaming across multiple clients"""
    
    def __init__(self):
        self.service = VideoProcessingService("concurrent-processor")
        self.clients = [StreamingClient(f"client-{i}") for i in range(3)]
    
    async def run_concurrent_streams(self):
        """Run multiple streaming patterns concurrently"""
        print("\n=== Concurrent Streaming Demonstration ===")
        
        tasks = []
        
        # Start multiple concurrent streams
        for i, client in enumerate(self.clients):
            if i % 4 == 0:
                task = asyncio.create_task(client.test_unary_processing())
            elif i % 4 == 1:
                task = asyncio.create_task(client.test_server_streaming())
            elif i % 4 == 2:
                task = asyncio.create_task(client.test_client_streaming())
            else:
                task = asyncio.create_task(client.test_bidirectional_streaming())
            
            tasks.append(task)
        
        # Add some additional concurrent streams
        for i in range(5):
            client = random.choice(self.clients)
            task = asyncio.create_task(client.test_unary_processing())
            tasks.append(task)
        
        # Wait for all streams to complete
        start_time = time.time()
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"\nConcurrent streaming completed in {end_time - start_time:.2f} seconds")
        self.print_service_stats()
    
    def print_service_stats(self):
        """Print service processing statistics"""
        stats = self.service.processing_stats
        
        print("\n=== Service Processing Statistics ===")
        print(f"Total Chunks Processed: {stats['total_chunks_processed']}")
        print(f"Total Processing Time: {stats['total_processing_time']:.2f}s")
        print(f"Average Processing Time per Chunk: {stats['total_processing_time']/max(1, stats['total_chunks_processed']):.3f}s")
        print(f"Current Concurrent Streams: {stats['concurrent_streams']}")
        
        if stats['total_chunks_processed'] > 0:
            throughput = stats['total_chunks_processed'] / stats['total_processing_time']
            print(f"Processing Throughput: {throughput:.1f} chunks/second")

async def main():
    """Main demonstration function"""
    print("gRPC Streaming Patterns Demonstration")
    print("=" * 50)
    
    # Test individual streaming patterns
    client = StreamingClient("demo-client")
    await client.run_all_tests()
    
    # Test concurrent streaming
    concurrent_demo = ConcurrentStreamingDemo()
    await concurrent_demo.run_concurrent_streams()
    
    print("\n=== gRPC Streaming Patterns Demonstrated ===")
    print("✓ Unary RPC: Single request → Single response")
    print("✓ Server Streaming: Single request → Multiple responses")
    print("✓ Client Streaming: Multiple requests → Single response")
    print("✓ Bidirectional Streaming: Multiple requests ↔ Multiple responses")
    print("✓ Concurrent stream processing")
    print("✓ HTTP/2 multiplexing benefits")
    print("✓ Real-time processing patterns")

if __name__ == "__main__":
    asyncio.run(main())
