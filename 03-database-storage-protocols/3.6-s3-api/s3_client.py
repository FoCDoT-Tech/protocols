#!/usr/bin/env python3
"""
S3 API Client Simulation
Demonstrates Amazon S3 compatible storage operations including
authentication, object operations, and multipart uploads.
"""

import hashlib
import hmac
import base64
import urllib.parse
import json
import xml.etree.ElementTree as ET
import random
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class S3StorageClass(Enum):
    STANDARD = "STANDARD"
    STANDARD_IA = "STANDARD_IA"
    ONEZONE_IA = "ONEZONE_IA"
    REDUCED_REDUNDANCY = "REDUCED_REDUNDANCY"
    GLACIER = "GLACIER"
    DEEP_ARCHIVE = "DEEP_ARCHIVE"
    INTELLIGENT_TIERING = "INTELLIGENT_TIERING"

class S3ServerSideEncryption(Enum):
    NONE = None
    AES256 = "AES256"
    KMS = "aws:kms"
    CUSTOMER = "customer"

@dataclass
class S3Object:
    """S3 object metadata"""
    key: str
    size: int
    etag: str
    last_modified: datetime
    storage_class: S3StorageClass
    owner: str
    metadata: Dict[str, str]

@dataclass
class S3Bucket:
    """S3 bucket information"""
    name: str
    creation_date: datetime
    region: str
    versioning_enabled: bool = False
    encryption_enabled: bool = False

class S3Client:
    """S3 API client implementation"""
    
    def __init__(self, endpoint: str, bucket: str, region: str = "us-east-1"):
        self.endpoint = endpoint.rstrip('/')
        self.bucket = bucket
        self.region = region
        self.access_key = None
        self.secret_key = None
        self.session_token = None
        self.authenticated = False
        self.request_count = 0
        
        print(f"☁️ S3 Client initialized")
        print(f"   Endpoint: {self.endpoint}")
        print(f"   Bucket: {self.bucket}")
        print(f"   Region: {self.region}")
    
    def authenticate(self, access_key: str, secret_key: str, session_token: Optional[str] = None):
        """Authenticate with S3 using AWS credentials"""
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token
        self.authenticated = True
        
        print(f"\n🔐 S3 Authentication")
        print(f"   Access Key: {access_key[:8]}...")
        print(f"   Secret Key: {secret_key[:8]}...")
        if session_token:
            print(f"   Session Token: {session_token[:16]}...")
        print(f"   ✅ Authentication configured")
    
    def _generate_signature_v4(self, method: str, path: str, query_params: Dict[str, str] = None,
                              headers: Dict[str, str] = None, payload: bytes = b'') -> Dict[str, str]:
        """Generate AWS Signature Version 4"""
        if not self.authenticated:
            raise ValueError("Client not authenticated")
        
        # Timestamp
        now = datetime.now(timezone.utc)
        amz_date = now.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = now.strftime('%Y%m%d')
        
        # Canonical request
        canonical_uri = urllib.parse.quote(path, safe='/')
        canonical_querystring = ''
        if query_params:
            sorted_params = sorted(query_params.items())
            canonical_querystring = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in sorted_params])
        
        # Headers
        if headers is None:
            headers = {}
        
        headers['host'] = self.endpoint.replace('https://', '').replace('http://', '')
        headers['x-amz-date'] = amz_date
        headers['x-amz-content-sha256'] = hashlib.sha256(payload).hexdigest()
        
        if self.session_token:
            headers['x-amz-security-token'] = self.session_token
        
        canonical_headers = ''
        signed_headers = ''
        for key in sorted(headers.keys()):
            canonical_headers += f"{key.lower()}:{headers[key]}\n"
            signed_headers += f"{key.lower()};"
        signed_headers = signed_headers[:-1]  # Remove trailing semicolon
        
        payload_hash = hashlib.sha256(payload).hexdigest()
        canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        
        # String to sign
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = f"{date_stamp}/{self.region}/s3/aws4_request"
        string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}"
        
        # Signing key
        def sign(key, msg):
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
        def get_signature_key(key, date_stamp, region_name, service_name):
            k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
            k_region = sign(k_date, region_name)
            k_service = sign(k_region, service_name)
            k_signing = sign(k_service, 'aws4_request')
            return k_signing
        
        signing_key = get_signature_key(self.secret_key, date_stamp, self.region, 's3')
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Authorization header
        authorization_header = f"{algorithm} Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        headers['Authorization'] = authorization_header
        
        return headers
    
    def _simulate_http_request(self, method: str, path: str, headers: Dict[str, str] = None,
                              query_params: Dict[str, str] = None, data: bytes = b'') -> Tuple[int, Dict[str, str], bytes]:
        """Simulate HTTP request to S3"""
        self.request_count += 1
        
        # Generate signed headers
        signed_headers = self._generate_signature_v4(method, path, query_params, headers, data)
        
        # Simulate network latency
        latency = random.uniform(50, 200)  # 50-200ms
        time.sleep(latency / 1000)
        
        # Generate response
        status_code, response_headers, response_body = self._generate_s3_response(method, path, query_params, data)
        
        print(f"   {method} {path} → {status_code} ({latency:.1f}ms)")
        
        return status_code, response_headers, response_body
    
    def _generate_s3_response(self, method: str, path: str, query_params: Dict[str, str] = None,
                             data: bytes = b'') -> Tuple[int, Dict[str, str], bytes]:
        """Generate simulated S3 response"""
        headers = {
            'x-amz-request-id': f"req-{random.randint(100000, 999999)}",
            'x-amz-id-2': f"id2-{random.randint(100000, 999999)}",
            'Date': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'Server': 'AmazonS3'
        }
        
        if method == 'PUT' and not query_params:
            # PUT Object
            etag = hashlib.md5(data).hexdigest()
            headers['ETag'] = f'"{etag}"'
            headers['x-amz-server-side-encryption'] = 'AES256'
            return 200, headers, b''
        
        elif method == 'GET' and not query_params:
            # GET Object
            if random.random() < 0.95:  # 95% success rate
                content_length = random.randint(1024, 1048576)
                headers['Content-Length'] = str(content_length)
                headers['Content-Type'] = 'application/octet-stream'
                headers['Last-Modified'] = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
                headers['ETag'] = f'"{hashlib.md5(data).hexdigest()}"'
                
                # Simulate file content
                response_body = b'A' * content_length
                return 200, headers, response_body
            else:
                # Object not found
                error_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<Error>
    <Code>NoSuchKey</Code>
    <Message>The specified key does not exist.</Message>
    <Key>{}</Key>
    <RequestId>{}</RequestId>
</Error>'''.format(path.split('/')[-1], headers['x-amz-request-id'])
                return 404, headers, error_xml.encode()
        
        elif method == 'DELETE':
            # DELETE Object
            return 204, headers, b''
        
        elif method == 'HEAD':
            # HEAD Object
            headers['Content-Length'] = str(random.randint(1024, 1048576))
            headers['Content-Type'] = 'application/octet-stream'
            headers['Last-Modified'] = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
            headers['ETag'] = f'"{hashlib.md5(data).hexdigest()}"'
            return 200, headers, b''
        
        elif method == 'GET' and query_params and 'list-type' in query_params:
            # List Objects V2
            objects_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <Name>{}</Name>
    <Prefix></Prefix>
    <KeyCount>3</KeyCount>
    <MaxKeys>1000</MaxKeys>
    <IsTruncated>false</IsTruncated>
    <Contents>
        <Key>document1.pdf</Key>
        <LastModified>2023-01-01T12:00:00.000Z</LastModified>
        <ETag>"d41d8cd98f00b204e9800998ecf8427e"</ETag>
        <Size>1024</Size>
        <StorageClass>STANDARD</StorageClass>
    </Contents>
    <Contents>
        <Key>image.jpg</Key>
        <LastModified>2023-01-02T12:00:00.000Z</LastModified>
        <ETag>"e99a18c428cb38d5f260853678922e03"</ETag>
        <Size>2048</Size>
        <StorageClass>STANDARD</StorageClass>
    </Contents>
    <Contents>
        <Key>data.csv</Key>
        <LastModified>2023-01-03T12:00:00.000Z</LastModified>
        <ETag>"ab07acbb1e496801937adfa772424bf7"</ETag>
        <Size>4096</Size>
        <StorageClass>STANDARD_IA</StorageClass>
    </Contents>
</ListBucketResult>'''.format(self.bucket)
            return 200, headers, objects_xml.encode()
        
        elif method == 'POST' and query_params and 'uploads' in query_params:
            # Initiate Multipart Upload
            upload_id = f"upload-{random.randint(100000, 999999)}"
            response_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<InitiateMultipartUploadResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <Bucket>{}</Bucket>
    <Key>{}</Key>
    <UploadId>{}</UploadId>
</InitiateMultipartUploadResult>'''.format(self.bucket, path.split('/')[-1], upload_id)
            return 200, headers, response_xml.encode()
        
        else:
            # Default success response
            return 200, headers, b''
    
    def put_object(self, key: str, data: bytes, content_type: str = 'application/octet-stream',
                   metadata: Dict[str, str] = None, storage_class: S3StorageClass = S3StorageClass.STANDARD) -> bool:
        """Upload object to S3"""
        print(f"\n📤 S3 PUT Object: {key}")
        print(f"   Size: {len(data):,} bytes")
        print(f"   Content-Type: {content_type}")
        print(f"   Storage Class: {storage_class.value}")
        
        headers = {
            'Content-Type': content_type,
            'Content-Length': str(len(data)),
            'x-amz-storage-class': storage_class.value
        }
        
        if metadata:
            for k, v in metadata.items():
                headers[f'x-amz-meta-{k}'] = v
        
        path = f"/{self.bucket}/{key}"
        status_code, response_headers, response_body = self._simulate_http_request('PUT', path, headers, data=data)
        
        if status_code == 200:
            etag = response_headers.get('ETag', '').strip('"')
            print(f"   ✅ Upload successful")
            print(f"   ETag: {etag}")
            return True
        else:
            print(f"   ❌ Upload failed: {status_code}")
            return False
    
    def get_object(self, key: str) -> Optional[bytes]:
        """Download object from S3"""
        print(f"\n📥 S3 GET Object: {key}")
        
        path = f"/{self.bucket}/{key}"
        status_code, response_headers, response_body = self._simulate_http_request('GET', path)
        
        if status_code == 200:
            content_length = int(response_headers.get('Content-Length', 0))
            etag = response_headers.get('ETag', '').strip('"')
            
            print(f"   ✅ Download successful")
            print(f"   Size: {content_length:,} bytes")
            print(f"   ETag: {etag}")
            return response_body
        else:
            print(f"   ❌ Download failed: {status_code}")
            return None
    
    def delete_object(self, key: str) -> bool:
        """Delete object from S3"""
        print(f"\n🗑️ S3 DELETE Object: {key}")
        
        path = f"/{self.bucket}/{key}"
        status_code, response_headers, response_body = self._simulate_http_request('DELETE', path)
        
        if status_code == 204:
            print(f"   ✅ Delete successful")
            return True
        else:
            print(f"   ❌ Delete failed: {status_code}")
            return False
    
    def head_object(self, key: str) -> Optional[Dict[str, str]]:
        """Get object metadata"""
        print(f"\n📋 S3 HEAD Object: {key}")
        
        path = f"/{self.bucket}/{key}"
        status_code, response_headers, response_body = self._simulate_http_request('HEAD', path)
        
        if status_code == 200:
            content_length = response_headers.get('Content-Length', '0')
            etag = response_headers.get('ETag', '').strip('"')
            last_modified = response_headers.get('Last-Modified', '')
            
            print(f"   ✅ Metadata retrieved")
            print(f"   Size: {content_length} bytes")
            print(f"   ETag: {etag}")
            print(f"   Last Modified: {last_modified}")
            
            return response_headers
        else:
            print(f"   ❌ Metadata retrieval failed: {status_code}")
            return None
    
    def list_objects(self, prefix: str = '', max_keys: int = 1000) -> List[S3Object]:
        """List objects in bucket"""
        print(f"\n📂 S3 List Objects")
        print(f"   Bucket: {self.bucket}")
        print(f"   Prefix: {prefix or '(all)'}")
        print(f"   Max Keys: {max_keys}")
        
        query_params = {
            'list-type': '2',
            'max-keys': str(max_keys)
        }
        if prefix:
            query_params['prefix'] = prefix
        
        path = f"/{self.bucket}"
        status_code, response_headers, response_body = self._simulate_http_request('GET', path, query_params=query_params)
        
        if status_code == 200:
            # Parse XML response
            root = ET.fromstring(response_body.decode())
            objects = []
            
            for content in root.findall('.//{http://s3.amazonaws.com/doc/2006-03-01/}Contents'):
                key = content.find('{http://s3.amazonaws.com/doc/2006-03-01/}Key').text
                size = int(content.find('{http://s3.amazonaws.com/doc/2006-03-01/}Size').text)
                etag = content.find('{http://s3.amazonaws.com/doc/2006-03-01/}ETag').text.strip('"')
                last_modified = content.find('{http://s3.amazonaws.com/doc/2006-03-01/}LastModified').text
                storage_class = content.find('{http://s3.amazonaws.com/doc/2006-03-01/}StorageClass').text
                
                obj = S3Object(
                    key=key,
                    size=size,
                    etag=etag,
                    last_modified=datetime.fromisoformat(last_modified.replace('Z', '+00:00')),
                    storage_class=S3StorageClass(storage_class),
                    owner='owner',
                    metadata={}
                )
                objects.append(obj)
            
            print(f"   ✅ Listed {len(objects)} objects")
            for obj in objects:
                print(f"     {obj.key} ({obj.size:,} bytes, {obj.storage_class.value})")
            
            return objects
        else:
            print(f"   ❌ List failed: {status_code}")
            return []
    
    def copy_object(self, source_key: str, dest_key: str, dest_bucket: str = None) -> bool:
        """Copy object within or between buckets"""
        if dest_bucket is None:
            dest_bucket = self.bucket
        
        print(f"\n📋 S3 Copy Object")
        print(f"   Source: {self.bucket}/{source_key}")
        print(f"   Destination: {dest_bucket}/{dest_key}")
        
        headers = {
            'x-amz-copy-source': f"/{self.bucket}/{source_key}"
        }
        
        path = f"/{dest_bucket}/{dest_key}"
        status_code, response_headers, response_body = self._simulate_http_request('PUT', path, headers)
        
        if status_code == 200:
            print(f"   ✅ Copy successful")
            return True
        else:
            print(f"   ❌ Copy failed: {status_code}")
            return False
    
    def generate_presigned_url(self, key: str, method: str = 'GET', expires_in: int = 3600) -> str:
        """Generate pre-signed URL for object access"""
        print(f"\n🔗 S3 Generate Pre-signed URL")
        print(f"   Key: {key}")
        print(f"   Method: {method}")
        print(f"   Expires: {expires_in}s")
        
        # Simulate URL generation
        timestamp = int(time.time()) + expires_in
        signature = hashlib.md5(f"{key}{method}{timestamp}{self.secret_key}".encode()).hexdigest()[:16]
        
        url = f"{self.endpoint}/{self.bucket}/{key}?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential={self.access_key}&X-Amz-Date={datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}&X-Amz-Expires={expires_in}&X-Amz-Signature={signature}"
        
        print(f"   ✅ Pre-signed URL generated")
        print(f"   URL: {url[:80]}...")
        
        return url
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            'endpoint': self.endpoint,
            'bucket': self.bucket,
            'region': self.region,
            'authenticated': self.authenticated,
            'request_count': self.request_count,
            'access_key': self.access_key[:8] + '...' if self.access_key else None
        }

def demonstrate_s3_operations():
    """Demonstrate S3 client operations"""
    print("=== S3 API Demonstration ===")
    
    # Initialize S3 client
    s3_client = S3Client("https://s3.amazonaws.com", "my-application-bucket", "us-east-1")
    
    # Authenticate
    s3_client.authenticate("AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
    
    # Upload objects
    test_objects = [
        ("documents/report.pdf", b"PDF content here" * 100, "application/pdf"),
        ("images/logo.png", b"PNG image data" * 200, "image/png"),
        ("data/analytics.csv", b"CSV,data,here\n" * 500, "text/csv"),
        ("backups/database.sql", b"SQL backup data" * 1000, "application/sql")
    ]
    
    uploaded_keys = []
    for key, data, content_type in test_objects:
        metadata = {
            'uploaded-by': 'demo-application',
            'environment': 'production',
            'version': '1.0'
        }
        
        storage_class = S3StorageClass.STANDARD_IA if 'backup' in key else S3StorageClass.STANDARD
        
        success = s3_client.put_object(key, data, content_type, metadata, storage_class)
        if success:
            uploaded_keys.append(key)
    
    # List objects
    all_objects = s3_client.list_objects()
    
    # Get object metadata
    for key in uploaded_keys[:2]:  # Check first 2 objects
        s3_client.head_object(key)
    
    # Download objects
    for key in uploaded_keys[:2]:  # Download first 2 objects
        data = s3_client.get_object(key)
        if data:
            print(f"     Downloaded {len(data):,} bytes")
    
    # Copy object
    if uploaded_keys:
        source_key = uploaded_keys[0]
        dest_key = f"copies/{source_key.split('/')[-1]}"
        s3_client.copy_object(source_key, dest_key)
    
    # Generate pre-signed URLs
    for key in uploaded_keys[:2]:
        s3_client.generate_presigned_url(key, 'GET', 3600)
    
    # Performance test
    print(f"\n⚡ Performance Test")
    start_time = time.time()
    
    for i in range(5):
        test_key = f"performance/test-{i}.dat"
        test_data = b"Performance test data" * 100
        s3_client.put_object(test_key, test_data)
        s3_client.get_object(test_key)
    
    elapsed = time.time() - start_time
    ops_per_sec = 10 / elapsed  # 5 puts + 5 gets
    
    print(f"   Operations: 10 (5 PUT + 5 GET)")
    print(f"   Total Time: {elapsed:.2f}s")
    print(f"   Ops/sec: {ops_per_sec:.1f}")
    
    # Delete test objects
    print(f"\n🧹 Cleanup")
    for key in uploaded_keys + [f"performance/test-{i}.dat" for i in range(5)]:
        s3_client.delete_object(key)
    
    # Client statistics
    stats = s3_client.get_stats()
    print(f"\n📊 Client Statistics")
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    demonstrate_s3_operations()
    
    print(f"\n🎯 S3 API enables scalable cloud object storage")
    print(f"💡 Key features: REST API, authentication, metadata, lifecycle management")
    print(f"🚀 Use cases: web assets, backups, data lakes, content distribution")
