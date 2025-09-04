#!/usr/bin/env python3
"""
S3 Multipart Upload Simulation
Demonstrates S3 multipart upload operations for large files
including parallel uploads and error handling.
"""

import hashlib
import random
import time
import threading
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class S3Part:
    """S3 multipart upload part"""
    part_number: int
    etag: str
    size: int
    upload_time: float

class S3MultipartUploader:
    """S3 multipart upload manager"""
    
    def __init__(self, s3_client, key: str, chunk_size: int = 5 * 1024 * 1024):
        self.s3_client = s3_client
        self.key = key
        self.chunk_size = chunk_size  # Minimum 5MB for S3
        self.upload_id = None
        self.parts = []
        self.total_size = 0
        self.start_time = None
        self.completed_parts = {}
        self.failed_parts = {}
        
        print(f"📦 S3 Multipart Uploader initialized")
        print(f"   Key: {self.key}")
        print(f"   Chunk Size: {self.chunk_size:,} bytes")
    
    def initiate_upload(self, content_type: str = 'application/octet-stream',
                       metadata: Dict[str, str] = None) -> bool:
        """Initiate multipart upload"""
        print(f"\n🚀 Initiating multipart upload")
        
        headers = {
            'Content-Type': content_type
        }
        
        if metadata:
            for k, v in metadata.items():
                headers[f'x-amz-meta-{k}'] = v
        
        query_params = {'uploads': ''}
        path = f"/{self.s3_client.bucket}/{self.key}"
        
        status_code, response_headers, response_body = self.s3_client._simulate_http_request(
            'POST', path, headers, query_params
        )
        
        if status_code == 200:
            # Parse upload ID from XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response_body.decode())
            self.upload_id = root.find('.//{http://s3.amazonaws.com/doc/2006-03-01/}UploadId').text
            
            print(f"   ✅ Upload initiated")
            print(f"   Upload ID: {self.upload_id}")
            return True
        else:
            print(f"   ❌ Failed to initiate upload: {status_code}")
            return False
    
    def upload_part(self, part_number: int, data: bytes) -> Optional[S3Part]:
        """Upload a single part"""
        if not self.upload_id:
            raise ValueError("Upload not initiated")
        
        start_time = time.time()
        
        headers = {
            'Content-Length': str(len(data))
        }
        
        query_params = {
            'partNumber': str(part_number),
            'uploadId': self.upload_id
        }
        
        path = f"/{self.s3_client.bucket}/{self.key}"
        
        # Simulate network issues occasionally
        if random.random() < 0.05:  # 5% failure rate
            print(f"   ❌ Part {part_number} failed (network error)")
            return None
        
        status_code, response_headers, response_body = self.s3_client._simulate_http_request(
            'PUT', path, headers, query_params, data
        )
        
        upload_time = time.time() - start_time
        
        if status_code == 200:
            etag = response_headers.get('ETag', '').strip('"')
            part = S3Part(
                part_number=part_number,
                etag=etag,
                size=len(data),
                upload_time=upload_time
            )
            
            print(f"   ✅ Part {part_number}: {len(data):,} bytes ({upload_time:.2f}s)")
            return part
        else:
            print(f"   ❌ Part {part_number} failed: {status_code}")
            return None
    
    def upload_parts_parallel(self, data: bytes, max_workers: int = 4) -> bool:
        """Upload parts in parallel"""
        if not self.upload_id:
            print("❌ Upload not initiated")
            return False
        
        self.total_size = len(data)
        self.start_time = time.time()
        
        # Split data into chunks
        chunks = []
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i + self.chunk_size]
            chunks.append((len(chunks) + 1, chunk))
        
        print(f"\n📤 Uploading {len(chunks)} parts in parallel")
        print(f"   Total Size: {self.total_size:,} bytes")
        print(f"   Workers: {max_workers}")
        
        # Upload parts in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_part = {
                executor.submit(self.upload_part, part_num, chunk_data): part_num
                for part_num, chunk_data in chunks
            }
            
            for future in as_completed(future_to_part):
                part_number = future_to_part[future]
                try:
                    part = future.result()
                    if part:
                        self.completed_parts[part_number] = part
                    else:
                        self.failed_parts[part_number] = "Upload failed"
                except Exception as exc:
                    self.failed_parts[part_number] = str(exc)
        
        # Retry failed parts
        if self.failed_parts:
            print(f"\n🔄 Retrying {len(self.failed_parts)} failed parts")
            retry_chunks = [(part_num, chunks[part_num - 1][1]) for part_num in self.failed_parts.keys()]
            self.failed_parts.clear()
            
            for part_num, chunk_data in retry_chunks:
                part = self.upload_part(part_num, chunk_data)
                if part:
                    self.completed_parts[part_num] = part
                else:
                    self.failed_parts[part_num] = "Retry failed"
        
        success = len(self.failed_parts) == 0
        elapsed = time.time() - self.start_time
        
        print(f"\n📊 Upload Summary")
        print(f"   Completed Parts: {len(self.completed_parts)}")
        print(f"   Failed Parts: {len(self.failed_parts)}")
        print(f"   Total Time: {elapsed:.2f}s")
        print(f"   Throughput: {(self.total_size / elapsed / 1024 / 1024):.1f} MB/s")
        
        return success
    
    def complete_upload(self) -> bool:
        """Complete multipart upload"""
        if not self.upload_id or not self.completed_parts:
            print("❌ Cannot complete upload: missing upload ID or parts")
            return False
        
        print(f"\n✅ Completing multipart upload")
        
        # Generate completion XML
        parts_xml = ""
        for part_num in sorted(self.completed_parts.keys()):
            part = self.completed_parts[part_num]
            parts_xml += f"""
    <Part>
        <PartNumber>{part.part_number}</PartNumber>
        <ETag>"{part.etag}"</ETag>
    </Part>"""
        
        complete_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<CompleteMultipartUpload>{parts_xml}
</CompleteMultipartUpload>"""
        
        query_params = {'uploadId': self.upload_id}
        path = f"/{self.s3_client.bucket}/{self.key}"
        
        headers = {
            'Content-Type': 'application/xml',
            'Content-Length': str(len(complete_xml))
        }
        
        status_code, response_headers, response_body = self.s3_client._simulate_http_request(
            'POST', path, headers, query_params, complete_xml.encode()
        )
        
        if status_code == 200:
            total_time = time.time() - self.start_time
            etag = response_headers.get('ETag', '').strip('"')
            
            print(f"   ✅ Upload completed successfully")
            print(f"   ETag: {etag}")
            print(f"   Total Time: {total_time:.2f}s")
            print(f"   Average Throughput: {(self.total_size / total_time / 1024 / 1024):.1f} MB/s")
            
            return True
        else:
            print(f"   ❌ Failed to complete upload: {status_code}")
            return False
    
    def abort_upload(self) -> bool:
        """Abort multipart upload"""
        if not self.upload_id:
            return True
        
        print(f"\n🚫 Aborting multipart upload")
        
        query_params = {'uploadId': self.upload_id}
        path = f"/{self.s3_client.bucket}/{self.key}"
        
        status_code, response_headers, response_body = self.s3_client._simulate_http_request(
            'DELETE', path, query_params=query_params
        )
        
        if status_code == 204:
            print(f"   ✅ Upload aborted")
            return True
        else:
            print(f"   ❌ Failed to abort upload: {status_code}")
            return False
    
    def get_upload_progress(self) -> Dict[str, Any]:
        """Get upload progress statistics"""
        if not self.start_time:
            return {'status': 'not_started'}
        
        elapsed = time.time() - self.start_time
        completed_size = sum(part.size for part in self.completed_parts.values())
        
        progress = {
            'status': 'in_progress' if self.failed_parts or len(self.completed_parts) == 0 else 'completed',
            'total_parts': len(self.completed_parts) + len(self.failed_parts),
            'completed_parts': len(self.completed_parts),
            'failed_parts': len(self.failed_parts),
            'total_size': self.total_size,
            'completed_size': completed_size,
            'progress_percent': (completed_size / self.total_size * 100) if self.total_size > 0 else 0,
            'elapsed_time': elapsed,
            'throughput_mbps': (completed_size / elapsed / 1024 / 1024) if elapsed > 0 else 0
        }
        
        return progress

class S3TransferManager:
    """High-level S3 transfer manager with automatic multipart"""
    
    def __init__(self, s3_client):
        self.s3_client = s3_client
        self.multipart_threshold = 100 * 1024 * 1024  # 100MB
        self.chunk_size = 10 * 1024 * 1024  # 10MB chunks
        self.max_workers = 4
    
    def upload_file(self, key: str, data: bytes, content_type: str = 'application/octet-stream',
                   metadata: Dict[str, str] = None) -> bool:
        """Upload file with automatic multipart for large files"""
        print(f"\n📁 S3 Transfer Manager Upload")
        print(f"   Key: {key}")
        print(f"   Size: {len(data):,} bytes")
        
        if len(data) < self.multipart_threshold:
            # Use simple PUT for small files
            print(f"   Using simple PUT (size < {self.multipart_threshold:,} bytes)")
            return self.s3_client.put_object(key, data, content_type, metadata)
        else:
            # Use multipart upload for large files
            print(f"   Using multipart upload (size >= {self.multipart_threshold:,} bytes)")
            
            uploader = S3MultipartUploader(self.s3_client, key, self.chunk_size)
            
            # Initiate upload
            if not uploader.initiate_upload(content_type, metadata):
                return False
            
            # Upload parts
            if not uploader.upload_parts_parallel(data, self.max_workers):
                print("❌ Part uploads failed, aborting...")
                uploader.abort_upload()
                return False
            
            # Complete upload
            return uploader.complete_upload()
    
    def download_file(self, key: str) -> Optional[bytes]:
        """Download file with range requests for large files"""
        print(f"\n📥 S3 Transfer Manager Download")
        print(f"   Key: {key}")
        
        # Get object metadata first
        metadata = self.s3_client.head_object(key)
        if not metadata:
            return None
        
        content_length = int(metadata.get('Content-Length', 0))
        
        if content_length < self.multipart_threshold:
            # Use simple GET for small files
            print(f"   Using simple GET (size < {self.multipart_threshold:,} bytes)")
            return self.s3_client.get_object(key)
        else:
            # Use range requests for large files
            print(f"   Using range requests (size >= {self.multipart_threshold:,} bytes)")
            
            chunks = []
            chunk_size = self.chunk_size
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                
                for start in range(0, content_length, chunk_size):
                    end = min(start + chunk_size - 1, content_length - 1)
                    future = executor.submit(self._download_range, key, start, end)
                    futures.append((start, future))
                
                # Collect results in order
                chunks = [None] * len(futures)
                for i, (start, future) in enumerate(futures):
                    chunk_data = future.result()
                    if chunk_data:
                        chunks[i] = chunk_data
                    else:
                        print(f"❌ Failed to download range {start}-{start + chunk_size}")
                        return None
            
            # Combine chunks
            return b''.join(chunks)
    
    def _download_range(self, key: str, start: int, end: int) -> Optional[bytes]:
        """Download a specific byte range"""
        # Simulate range request
        range_size = end - start + 1
        
        # Simulate network latency
        latency = random.uniform(50, 200)
        time.sleep(latency / 1000)
        
        # Simulate range data
        return b'A' * range_size

def demonstrate_multipart_operations():
    """Demonstrate S3 multipart upload operations"""
    print("=== S3 Multipart Upload Demonstration ===")
    
    # Import S3Client from s3_client module
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from s3_client import S3Client
    
    # Initialize S3 client
    s3_client = S3Client("https://s3.amazonaws.com", "large-files-bucket", "us-east-1")
    s3_client.authenticate("AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
    
    # Test multipart upload
    print(f"\n📦 Testing Multipart Upload")
    
    # Generate large test data (50MB)
    large_data = b"Large file content block " * (2 * 1024 * 1024)  # ~50MB
    
    uploader = S3MultipartUploader(s3_client, "large-files/video.mp4", chunk_size=10*1024*1024)
    
    metadata = {
        'content-type': 'video/mp4',
        'upload-method': 'multipart',
        'client': 'demo'
    }
    
    # Initiate upload
    if uploader.initiate_upload('video/mp4', metadata):
        # Upload parts
        if uploader.upload_parts_parallel(large_data, max_workers=3):
            # Complete upload
            uploader.complete_upload()
        else:
            # Abort on failure
            uploader.abort_upload()
    
    # Test transfer manager
    print(f"\n📁 Testing Transfer Manager")
    
    transfer_manager = S3TransferManager(s3_client)
    
    # Upload different sized files
    test_files = [
        ("small-file.txt", b"Small file content" * 1000),  # ~18KB
        ("medium-file.dat", b"Medium file content" * 100000),  # ~1.8MB
        ("large-file.bin", b"Large file content" * 5000000)  # ~90MB
    ]
    
    for filename, data in test_files:
        print(f"\n📤 Uploading {filename}")
        success = transfer_manager.upload_file(f"transfers/{filename}", data)
        
        if success:
            print(f"📥 Downloading {filename}")
            downloaded = transfer_manager.download_file(f"transfers/{filename}")
            if downloaded and len(downloaded) == len(data):
                print(f"   ✅ Download verified ({len(downloaded):,} bytes)")
            else:
                print(f"   ❌ Download verification failed")
    
    # Performance comparison
    print(f"\n⚡ Performance Comparison")
    
    test_data = b"Performance test data" * 1000000  # ~21MB
    
    # Simple upload
    start_time = time.time()
    s3_client.put_object("perf/simple.dat", test_data)
    simple_time = time.time() - start_time
    
    # Multipart upload
    start_time = time.time()
    mp_uploader = S3MultipartUploader(s3_client, "perf/multipart.dat", chunk_size=5*1024*1024)
    mp_uploader.initiate_upload()
    mp_uploader.upload_parts_parallel(test_data, max_workers=2)
    mp_uploader.complete_upload()
    multipart_time = time.time() - start_time
    
    print(f"   Simple Upload: {simple_time:.2f}s ({len(test_data)/simple_time/1024/1024:.1f} MB/s)")
    print(f"   Multipart Upload: {multipart_time:.2f}s ({len(test_data)/multipart_time/1024/1024:.1f} MB/s)")
    
    if multipart_time < simple_time:
        improvement = ((simple_time - multipart_time) / simple_time) * 100
        print(f"   Multipart is {improvement:.1f}% faster")
    else:
        overhead = ((multipart_time - simple_time) / simple_time) * 100
        print(f"   Multipart has {overhead:.1f}% overhead")

if __name__ == "__main__":
    demonstrate_multipart_operations()
    
    print(f"\n🎯 S3 multipart uploads enable efficient large file transfers")
    print(f"💡 Benefits: parallel uploads, resume capability, improved throughput")
    print(f"🚀 Use cases: video uploads, database backups, large datasets")
