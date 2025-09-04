#!/usr/bin/env python3
"""
NFS (Network File System) Protocol Simulation
Demonstrates NFS v3 and v4 operations including RPC calls,
file operations, and performance characteristics.
"""

import struct
import random
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class NFSVersion(Enum):
    V3 = 3
    V4 = 4

class RPCMessageType(Enum):
    CALL = 0
    REPLY = 1

class NFSProcedure(Enum):
    # NFSv3 procedures
    NULL = 0
    GETATTR = 1
    SETATTR = 2
    LOOKUP = 3
    ACCESS = 4
    READLINK = 5
    READ = 6
    WRITE = 7
    CREATE = 8
    MKDIR = 9
    REMOVE = 12
    RMDIR = 13
    RENAME = 14
    READDIR = 16
    READDIRPLUS = 17
    FSSTAT = 18
    FSINFO = 19
    PATHCONF = 20
    COMMIT = 21

@dataclass
class FileHandle:
    """NFS file handle representation"""
    data: bytes
    version: NFSVersion
    
    def __post_init__(self):
        if len(self.data) > 64:  # NFSv4 max handle size
            raise ValueError("File handle too large")

@dataclass
class FileAttributes:
    """NFS file attributes"""
    file_type: str
    mode: int
    nlink: int
    uid: int
    gid: int
    size: int
    used: int
    rdev: int
    fsid: int
    fileid: int
    atime: datetime
    mtime: datetime
    ctime: datetime

class RPCMessage:
    """RPC message structure for NFS communication"""
    
    def __init__(self, xid: int, msg_type: RPCMessageType, 
                 program: int = 100003, version: int = 3, procedure: int = 0):
        self.xid = xid  # Transaction ID
        self.msg_type = msg_type
        self.program = program  # NFS program number
        self.version = version
        self.procedure = procedure
        self.auth_flavor = 1  # AUTH_SYS
        self.auth_length = 0
        self.verf_flavor = 0
        self.verf_length = 0
    
    def encode(self) -> bytes:
        """Encode RPC message header"""
        header = struct.pack('>IIIIIIIIII',
            self.xid,
            self.msg_type.value,
            2,  # RPC version
            self.program,
            self.version,
            self.procedure,
            self.auth_flavor,
            self.auth_length,
            self.verf_flavor,
            self.verf_length
        )
        return header
    
    @classmethod
    def decode(cls, data: bytes) -> 'RPCMessage':
        """Decode RPC message header"""
        if len(data) < 40:
            raise ValueError("Invalid RPC message length")
        
        fields = struct.unpack('>IIIIIIIIII', data[:40])
        msg = cls(fields[0], RPCMessageType(fields[1]))
        msg.program = fields[3]
        msg.version = fields[4]
        msg.procedure = fields[5]
        return msg

class NFSClient:
    """NFS client implementation"""
    
    def __init__(self, server: str, version: NFSVersion = NFSVersion.V3):
        self.server = server
        self.version = version
        self.port = 2049
        self.client_id = f"nfs_client_{random.randint(1000, 9999)}"
        self.xid_counter = random.randint(1, 1000000)
        self.mounted_exports = {}
        self.file_handles = {}
        self.read_cache = {}
        self.write_cache = {}
        
        print(f"📁 NFS Client initialized")
        print(f"   Server: {self.server}:{self.port}")
        print(f"   Version: NFSv{self.version.value}")
        print(f"   Client ID: {self.client_id}")
    
    def _next_xid(self) -> int:
        """Generate next transaction ID"""
        self.xid_counter += 1
        return self.xid_counter
    
    def _simulate_rpc_call(self, procedure: NFSProcedure, 
                          data: bytes = b'') -> Tuple[bytes, float]:
        """Simulate RPC call with network latency"""
        xid = self._next_xid()
        
        # Create RPC message
        rpc_msg = RPCMessage(xid, RPCMessageType.CALL, 
                           version=self.version.value, 
                           procedure=procedure.value)
        
        # Simulate network latency
        latency = random.uniform(0.5, 3.0)  # 0.5-3ms
        time.sleep(latency / 1000)  # Convert to seconds
        
        # Simulate response
        response_data = self._generate_response(procedure, data)
        
        return response_data, latency
    
    def _generate_response(self, procedure: NFSProcedure, request_data: bytes) -> bytes:
        """Generate simulated NFS response"""
        if procedure == NFSProcedure.GETATTR:
            # Return file attributes
            attrs = FileAttributes(
                file_type="regular",
                mode=0o644,
                nlink=1,
                uid=1000,
                gid=1000,
                size=random.randint(1024, 1048576),
                used=random.randint(1024, 1048576),
                rdev=0,
                fsid=12345,
                fileid=random.randint(100000, 999999),
                atime=datetime.now(),
                mtime=datetime.now(),
                ctime=datetime.now()
            )
            return self._encode_attributes(attrs)
        
        elif procedure == NFSProcedure.READ:
            # Return file data
            size = min(8192, random.randint(512, 8192))  # Typical NFS read size
            return b'A' * size  # Simulated file content
        
        elif procedure == NFSProcedure.WRITE:
            # Return write confirmation
            return struct.pack('>II', 0, len(request_data))  # Status + bytes written
        
        elif procedure == NFSProcedure.LOOKUP:
            # Return file handle
            handle_data = hashlib.md5(request_data).digest()
            return handle_data
        
        else:
            return struct.pack('>I', 0)  # Success status
    
    def _encode_attributes(self, attrs: FileAttributes) -> bytes:
        """Encode file attributes for NFS response"""
        # Simplified attribute encoding
        return struct.pack('>IIIIIIQQI',
            1,  # file type (regular)
            attrs.mode,
            attrs.nlink,
            attrs.uid,
            attrs.gid,
            attrs.size,
            int(attrs.mtime.timestamp()),
            attrs.fileid,
            0   # padding
        )
    
    def mount(self, export_path: str, mount_point: str) -> bool:
        """Mount NFS export"""
        print(f"\n🔗 Mounting NFS export")
        print(f"   Export: {self.server}:{export_path}")
        print(f"   Mount Point: {mount_point}")
        
        # Simulate mount operation
        response, latency = self._simulate_rpc_call(NFSProcedure.NULL)
        
        if response is not None:
            # Generate root file handle
            root_handle = FileHandle(
                data=hashlib.md5(export_path.encode()).digest(),
                version=self.version
            )
            
            self.mounted_exports[mount_point] = {
                'export_path': export_path,
                'root_handle': root_handle,
                'mount_time': datetime.now()
            }
            
            print(f"   ✅ Mount successful ({latency:.2f}ms)")
            return True
        
        print(f"   ❌ Mount failed")
        return False
    
    def lookup(self, path: str) -> Optional[FileHandle]:
        """Lookup file/directory by path"""
        print(f"\n🔍 NFS LOOKUP: {path}")
        
        # Find mount point
        mount_point = self._find_mount_point(path)
        if not mount_point:
            print(f"   ❌ No mount point found for {path}")
            return None
        
        # Simulate lookup RPC
        lookup_data = path.encode('utf-8')
        response, latency = self._simulate_rpc_call(NFSProcedure.LOOKUP, lookup_data)
        
        if response:
            file_handle = FileHandle(data=response[:32], version=self.version)
            self.file_handles[path] = file_handle
            
            print(f"   ✅ Lookup successful ({latency:.2f}ms)")
            print(f"   Handle: {file_handle.data[:8].hex()}...")
            return file_handle
        
        print(f"   ❌ Lookup failed")
        return None
    
    def getattr(self, file_handle: FileHandle) -> Optional[FileAttributes]:
        """Get file attributes"""
        print(f"\n📊 NFS GETATTR")
        
        response, latency = self._simulate_rpc_call(NFSProcedure.GETATTR, file_handle.data)
        
        if response and len(response) >= 36:
            # Decode attributes (simplified)
            fields = struct.unpack('>IIIIIIQQI', response[:36])
            
            attrs = FileAttributes(
                file_type="regular" if fields[0] == 1 else "directory",
                mode=fields[1],
                nlink=fields[2],
                uid=fields[3],
                gid=fields[4],
                size=fields[5],
                used=fields[5],
                rdev=0,
                fsid=12345,
                fileid=fields[7],
                atime=datetime.fromtimestamp(fields[6]),
                mtime=datetime.fromtimestamp(fields[6]),
                ctime=datetime.fromtimestamp(fields[6])
            )
            
            print(f"   ✅ Attributes retrieved ({latency:.2f}ms)")
            print(f"   Size: {attrs.size:,} bytes")
            print(f"   Mode: {oct(attrs.mode)}")
            print(f"   UID/GID: {attrs.uid}/{attrs.gid}")
            
            return attrs
        
        print(f"   ❌ Failed to get attributes")
        return None
    
    def read_file(self, path: str, offset: int = 0, count: int = 8192) -> Optional[bytes]:
        """Read file data"""
        print(f"\n📖 NFS READ: {path}")
        print(f"   Offset: {offset:,}")
        print(f"   Count: {count:,} bytes")
        
        # Check cache first
        cache_key = f"{path}:{offset}:{count}"
        if cache_key in self.read_cache:
            cached_data = self.read_cache[cache_key]
            print(f"   💾 Cache hit ({len(cached_data)} bytes)")
            return cached_data
        
        # Lookup file handle
        file_handle = self.lookup(path)
        if not file_handle:
            return None
        
        # Simulate read RPC
        read_request = struct.pack('>QI', offset, count) + file_handle.data
        response, latency = self._simulate_rpc_call(NFSProcedure.READ, read_request)
        
        if response:
            # Cache the data
            self.read_cache[cache_key] = response
            
            print(f"   ✅ Read successful ({latency:.2f}ms)")
            print(f"   Data: {len(response):,} bytes")
            return response
        
        print(f"   ❌ Read failed")
        return None
    
    def write_file(self, path: str, data: bytes, offset: int = 0) -> bool:
        """Write file data"""
        print(f"\n✏️ NFS WRITE: {path}")
        print(f"   Offset: {offset:,}")
        print(f"   Data: {len(data):,} bytes")
        
        # Lookup file handle
        file_handle = self.lookup(path)
        if not file_handle:
            return False
        
        # Simulate write RPC
        write_request = struct.pack('>QI', offset, len(data)) + file_handle.data + data
        response, latency = self._simulate_rpc_call(NFSProcedure.WRITE, write_request)
        
        if response and len(response) >= 8:
            status, bytes_written = struct.unpack('>II', response[:8])
            
            if status == 0 and bytes_written == len(data):
                # Invalidate read cache
                self._invalidate_cache(path)
                
                print(f"   ✅ Write successful ({latency:.2f}ms)")
                print(f"   Written: {bytes_written:,} bytes")
                return True
        
        print(f"   ❌ Write failed")
        return False
    
    def _find_mount_point(self, path: str) -> Optional[str]:
        """Find the mount point for a given path"""
        for mount_point in self.mounted_exports:
            if path.startswith(mount_point):
                return mount_point
        return None
    
    def _invalidate_cache(self, path: str):
        """Invalidate cache entries for a path"""
        keys_to_remove = [key for key in self.read_cache.keys() if key.startswith(path)]
        for key in keys_to_remove:
            del self.read_cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            'server': self.server,
            'version': f"NFSv{self.version.value}",
            'mounted_exports': len(self.mounted_exports),
            'cached_handles': len(self.file_handles),
            'read_cache_entries': len(self.read_cache),
            'write_cache_entries': len(self.write_cache),
            'total_xids': self.xid_counter
        }

def demonstrate_nfs_operations():
    """Demonstrate NFS client operations"""
    print("=== NFS Protocol Demonstration ===")
    
    # Initialize NFS client
    nfs_client = NFSClient("fileserver.example.com", NFSVersion.V4)
    
    # Mount file system
    success = nfs_client.mount("/export/data", "/mnt/nfs")
    if not success:
        print("Failed to mount NFS export")
        return
    
    # File operations
    test_files = [
        "/mnt/nfs/document.txt",
        "/mnt/nfs/logs/application.log",
        "/mnt/nfs/config/settings.conf"
    ]
    
    for file_path in test_files:
        # Lookup and get attributes
        file_handle = nfs_client.lookup(file_path)
        if file_handle:
            attrs = nfs_client.getattr(file_handle)
        
        # Read file
        data = nfs_client.read_file(file_path, offset=0, count=4096)
        
        # Write file (simulate log append)
        if "log" in file_path:
            log_entry = f"[{datetime.now()}] Application event logged\n"
            nfs_client.write_file(file_path, log_entry.encode(), offset=1000)
    
    # Performance test
    print(f"\n⚡ Performance Test")
    start_time = time.time()
    
    for i in range(10):
        test_path = f"/mnt/nfs/test_file_{i}.dat"
        nfs_client.read_file(test_path, count=1024)
    
    elapsed = time.time() - start_time
    ops_per_sec = 10 / elapsed
    
    print(f"   Operations: 10 reads")
    print(f"   Total Time: {elapsed:.2f}s")
    print(f"   Ops/sec: {ops_per_sec:.1f}")
    
    # Client statistics
    stats = nfs_client.get_stats()
    print(f"\n📊 Client Statistics")
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    demonstrate_nfs_operations()
    
    print(f"\n🎯 NFS enables transparent remote file access over networks")
    print(f"💡 Key features: stateless operation, caching, POSIX semantics")
    print(f"🚀 Enterprise use: distributed storage, home directories, application data")
