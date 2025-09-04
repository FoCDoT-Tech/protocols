#!/usr/bin/env python3
"""
SMB (Server Message Block) Protocol Simulation
Demonstrates SMB 2.1/3.0 operations including authentication,
file operations, and performance characteristics.
"""

import struct
import random
import time
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class SMBVersion(Enum):
    SMB1 = 0x0001
    SMB2 = 0x0202
    SMB21 = 0x0210
    SMB30 = 0x0300
    SMB302 = 0x0302
    SMB311 = 0x0311

class SMBCommand(Enum):
    NEGOTIATE = 0x0000
    SESSION_SETUP = 0x0001
    LOGOFF = 0x0002
    TREE_CONNECT = 0x0003
    TREE_DISCONNECT = 0x0004
    CREATE = 0x0005
    CLOSE = 0x0006
    FLUSH = 0x0007
    READ = 0x0008
    WRITE = 0x0009
    LOCK = 0x000A
    IOCTL = 0x000B
    CANCEL = 0x000C
    ECHO = 0x000D
    QUERY_DIRECTORY = 0x000E
    CHANGE_NOTIFY = 0x000F
    QUERY_INFO = 0x0010
    SET_INFO = 0x0011

class NTStatus(Enum):
    SUCCESS = 0x00000000
    ACCESS_DENIED = 0xC0000022
    OBJECT_NAME_NOT_FOUND = 0xC0000034
    SHARING_VIOLATION = 0xC0000043
    INSUFFICIENT_RESOURCES = 0xC000009A

@dataclass
class SMBHeader:
    """SMB2 header structure"""
    protocol_id: bytes = b'\xfeSMB'
    structure_size: int = 64
    credit_charge: int = 1
    status: int = 0
    command: int = 0
    credit_request: int = 1
    flags: int = 0
    next_command: int = 0
    message_id: int = 0
    process_id: int = 0
    tree_id: int = 0
    session_id: int = 0
    signature: bytes = b'\x00' * 16

@dataclass
class FileInfo:
    """SMB file information"""
    file_id: bytes
    name: str
    size: int
    attributes: int
    creation_time: datetime
    last_access_time: datetime
    last_write_time: datetime
    change_time: datetime

class SMBClient:
    """SMB client implementation"""
    
    def __init__(self, server: str, share: str, version: SMBVersion = SMBVersion.SMB30):
        self.server = server
        self.share = share
        self.version = version
        self.port = 445
        self.client_guid = uuid.uuid4().bytes
        self.session_id = 0
        self.tree_id = 0
        self.message_id = 1
        self.authenticated = False
        self.open_files = {}
        self.capabilities = []
        
        print(f"🖥️ SMB Client initialized")
        print(f"   Server: \\\\{self.server}\\{self.share}")
        print(f"   Version: SMB {self.version.name}")
        print(f"   Port: {self.port}")
        print(f"   Client GUID: {uuid.UUID(bytes=self.client_guid)}")
    
    def _next_message_id(self) -> int:
        """Generate next message ID"""
        self.message_id += 1
        return self.message_id
    
    def _create_header(self, command: SMBCommand, status: int = 0) -> SMBHeader:
        """Create SMB2 header"""
        header = SMBHeader()
        header.command = command.value
        header.status = status
        header.message_id = self._next_message_id()
        header.session_id = self.session_id
        header.tree_id = self.tree_id
        return header
    
    def _encode_header(self, header: SMBHeader) -> bytes:
        """Encode SMB2 header"""
        return struct.pack('<4sHHIHHIIQIII16s',
            header.protocol_id,
            header.structure_size,
            header.credit_charge,
            header.status,
            header.command,
            header.credit_request,
            header.flags,
            header.next_command,
            header.message_id,
            header.process_id,
            header.tree_id,
            header.session_id,
            header.signature
        )
    
    def _simulate_smb_request(self, header: SMBHeader, data: bytes = b'') -> Tuple[bytes, float]:
        """Simulate SMB request with network latency"""
        # Encode request
        request = self._encode_header(header) + data
        
        # Simulate network latency
        latency = random.uniform(0.3, 2.0)  # 0.3-2ms
        time.sleep(latency / 1000)  # Convert to seconds
        
        # Generate response
        response = self._generate_response(header, data)
        
        return response, latency
    
    def _generate_response(self, header: SMBHeader, request_data: bytes) -> bytes:
        """Generate simulated SMB response"""
        response_header = header
        response_header.flags |= 0x01  # SMB2_FLAGS_SERVER_TO_REDIR
        
        if header.command == SMBCommand.NEGOTIATE.value:
            # Negotiate response
            response_data = struct.pack('<HHIHH16sIIIQQ',
                65,  # StructureSize
                0,   # SecurityMode
                self.version.value,  # DialectRevision
                0,   # NegotiateContextCount
                0,   # Reserved
                self.client_guid[:16],  # ServerGuid (reuse client for simulation)
                0x01,  # Capabilities
                0x100000,  # MaxTransactSize
                0x100000,  # MaxReadSize
                0x100000,  # MaxWriteSize
                int(time.time() * 10000000),  # SystemTime
                int(time.time() * 10000000)   # ServerStartTime
            )
            
        elif header.command == SMBCommand.SESSION_SETUP.value:
            # Session setup response
            self.session_id = random.randint(1, 0xFFFFFFFFFFFFFFFF)
            response_header.session_id = self.session_id
            response_data = struct.pack('<HH',
                9,   # StructureSize
                0    # SessionFlags
            )
            
        elif header.command == SMBCommand.TREE_CONNECT.value:
            # Tree connect response
            self.tree_id = random.randint(1, 0xFFFFFFFF)
            response_header.tree_id = self.tree_id
            response_data = struct.pack('<HHII',
                16,  # StructureSize
                1,   # ShareType (disk)
                0,   # ShareFlags
                0x1F01FF  # Capabilities
            )
            
        elif header.command == SMBCommand.CREATE.value:
            # Create response (file open)
            file_id = random.randbytes(16)
            response_data = struct.pack('<HB16sQQQQII',
                89,  # StructureSize
                0,   # OplockLevel
                file_id,  # FileId
                0,   # CreationAction
                int(time.time() * 10000000),  # CreationTime
                int(time.time() * 10000000),  # LastAccessTime
                int(time.time() * 10000000),  # LastWriteTime
                int(time.time() * 10000000),  # ChangeTime
                random.randint(1024, 1048576),  # AllocationSize
                random.randint(1024, 1048576)   # EndOfFile
            )
            
        elif header.command == SMBCommand.READ.value:
            # Read response
            data_size = min(65536, random.randint(512, 65536))
            response_data = struct.pack('<HHII',
                17,  # StructureSize
                0,   # DataOffset
                data_size,  # DataLength
                0    # DataRemaining
            ) + b'A' * data_size  # Simulated file content
            
        elif header.command == SMBCommand.WRITE.value:
            # Write response
            bytes_written = len(request_data) - 64  # Subtract header size
            response_data = struct.pack('<HHII',
                17,  # StructureSize
                0,   # Reserved
                bytes_written,  # BytesWritten
                0    # BytesRemaining
            )
            
        else:
            response_data = b''
        
        return self._encode_header(response_header) + response_data
    
    def negotiate(self) -> bool:
        """Negotiate SMB protocol version"""
        print(f"\n🤝 SMB NEGOTIATE")
        
        header = self._create_header(SMBCommand.NEGOTIATE)
        
        # Negotiate request data
        negotiate_data = struct.pack('<HHIHH',
            36,  # StructureSize
            1,   # DialectCount
            0,   # SecurityMode
            0,   # Reserved
            0    # Capabilities
        ) + struct.pack('<H', self.version.value)  # Dialects
        
        response, latency = self._simulate_smb_request(header, negotiate_data)
        
        if len(response) >= 64:
            print(f"   ✅ Protocol negotiated ({latency:.2f}ms)")
            print(f"   Version: SMB {self.version.name}")
            return True
        
        print(f"   ❌ Negotiation failed")
        return False
    
    def authenticate(self, username: str, password: str, domain: str = "") -> bool:
        """Authenticate with SMB server"""
        print(f"\n🔐 SMB SESSION_SETUP")
        print(f"   User: {domain}\\{username}" if domain else f"   User: {username}")
        
        header = self._create_header(SMBCommand.SESSION_SETUP)
        
        # Session setup request (simplified)
        session_data = struct.pack('<HHBBHQ',
            25,  # StructureSize
            0,   # Flags
            0,   # SecurityMode
            0,   # Capabilities
            0,   # Channel
            0,   # SecurityBufferOffset
            0    # SecurityBufferLength
        )
        
        response, latency = self._simulate_smb_request(header, session_data)
        
        if len(response) >= 64:
            # Extract session ID from response
            session_id_bytes = response[44:52]
            self.session_id = struct.unpack('<Q', session_id_bytes)[0]
            self.authenticated = True
            
            print(f"   ✅ Authentication successful ({latency:.2f}ms)")
            print(f"   Session ID: {self.session_id:016x}")
            return True
        
        print(f"   ❌ Authentication failed")
        return False
    
    def tree_connect(self) -> bool:
        """Connect to SMB share"""
        print(f"\n🌳 SMB TREE_CONNECT")
        print(f"   Share: \\\\{self.server}\\{self.share}")
        
        if not self.authenticated:
            print(f"   ❌ Not authenticated")
            return False
        
        header = self._create_header(SMBCommand.TREE_CONNECT)
        
        # Tree connect request
        share_path = f"\\\\{self.server}\\{self.share}".encode('utf-16le')
        tree_data = struct.pack('<HHH',
            9,   # StructureSize
            0,   # Flags
            len(share_path)  # PathLength
        ) + share_path
        
        response, latency = self._simulate_smb_request(header, tree_data)
        
        if len(response) >= 64:
            # Extract tree ID from response
            tree_id_bytes = response[40:44]
            self.tree_id = struct.unpack('<I', tree_id_bytes)[0]
            
            print(f"   ✅ Tree connect successful ({latency:.2f}ms)")
            print(f"   Tree ID: {self.tree_id:08x}")
            return True
        
        print(f"   ❌ Tree connect failed")
        return False
    
    def create_file(self, filename: str, desired_access: int = 0x80000000) -> Optional[bytes]:
        """Create/open file"""
        print(f"\n📁 SMB CREATE: {filename}")
        
        if not self.tree_id:
            print(f"   ❌ Not connected to share")
            return None
        
        header = self._create_header(SMBCommand.CREATE)
        
        # Create request
        filename_utf16 = filename.encode('utf-16le')
        create_data = struct.pack('<HBBIIIQQIIIHH',
            57,  # StructureSize
            0,   # SecurityFlags
            0,   # RequestedOplockLevel
            0,   # ImpersonationLevel
            0,   # SmbCreateFlags
            0,   # Reserved
            desired_access,  # DesiredAccess
            0,   # FileAttributes
            3,   # ShareAccess (read/write)
            1,   # CreateDisposition (open if exists, create if not)
            0,   # CreateOptions
            120, # NameOffset
            len(filename_utf16)  # NameLength
        ) + b'\x00' * (120 - 57) + filename_utf16  # Padding + filename
        
        response, latency = self._simulate_smb_request(header, create_data)
        
        if len(response) >= 89:
            # Extract file ID
            file_id = response[75:91]  # 16 bytes
            self.open_files[filename] = file_id
            
            print(f"   ✅ File opened ({latency:.2f}ms)")
            print(f"   File ID: {file_id[:8].hex()}...")
            return file_id
        
        print(f"   ❌ File open failed")
        return None
    
    def read_file(self, file_id: bytes, offset: int = 0, length: int = 65536) -> Optional[bytes]:
        """Read file data"""
        print(f"\n📖 SMB READ")
        print(f"   Offset: {offset:,}")
        print(f"   Length: {length:,} bytes")
        
        header = self._create_header(SMBCommand.READ)
        
        # Read request
        read_data = struct.pack('<HHIIIQ16s',
            49,  # StructureSize
            0,   # Padding
            length,  # Length
            offset,  # Offset
            file_id,  # FileId
            0,   # MinimumCount
            0,   # Channel
            0,   # RemainingBytes
            0    # ReadChannelInfoOffset
        )
        
        response, latency = self._simulate_smb_request(header, read_data)
        
        if len(response) >= 81:
            # Extract data length and data
            data_length = struct.unpack('<I', response[70:74])[0]
            data = response[81:81+data_length]
            
            print(f"   ✅ Read successful ({latency:.2f}ms)")
            print(f"   Data: {len(data):,} bytes")
            return data
        
        print(f"   ❌ Read failed")
        return None
    
    def write_file(self, file_id: bytes, data: bytes, offset: int = 0) -> bool:
        """Write file data"""
        print(f"\n✏️ SMB WRITE")
        print(f"   Offset: {offset:,}")
        print(f"   Data: {len(data):,} bytes")
        
        header = self._create_header(SMBCommand.WRITE)
        
        # Write request
        write_data = struct.pack('<HHIIQ16sI',
            49,  # StructureSize
            112, # DataOffset
            len(data),  # Length
            offset,  # Offset
            file_id,  # FileId
            0,   # Channel
            0,   # RemainingBytes
            0,   # WriteChannelInfoOffset
            0    # Flags
        ) + data
        
        response, latency = self._simulate_smb_request(header, write_data)
        
        if len(response) >= 81:
            # Extract bytes written
            bytes_written = struct.unpack('<I', response[70:74])[0]
            
            if bytes_written == len(data):
                print(f"   ✅ Write successful ({latency:.2f}ms)")
                print(f"   Written: {bytes_written:,} bytes")
                return True
        
        print(f"   ❌ Write failed")
        return False
    
    def close_file(self, file_id: bytes) -> bool:
        """Close file"""
        print(f"\n🔒 SMB CLOSE")
        
        header = self._create_header(SMBCommand.CLOSE)
        
        # Close request
        close_data = struct.pack('<HH16s',
            24,  # StructureSize
            0,   # Flags
            file_id  # FileId
        )
        
        response, latency = self._simulate_smb_request(header, close_data)
        
        if len(response) >= 64:
            print(f"   ✅ File closed ({latency:.2f}ms)")
            return True
        
        print(f"   ❌ Close failed")
        return False
    
    def list_directory(self, directory: str = "\\") -> List[FileInfo]:
        """List directory contents"""
        print(f"\n📂 SMB QUERY_DIRECTORY: {directory}")
        
        # First open the directory
        dir_file_id = self.create_file(directory, desired_access=0x00000001)  # FILE_LIST_DIRECTORY
        if not dir_file_id:
            return []
        
        header = self._create_header(SMBCommand.QUERY_DIRECTORY)
        
        # Query directory request
        query_data = struct.pack('<HBBIIH16s',
            33,  # StructureSize
            1,   # FileInformationClass (FileDirectoryInformation)
            0,   # Flags
            0,   # FileIndex
            dir_file_id,  # FileId
            0,   # FileNameOffset
            0    # FileNameLength
        )
        
        response, latency = self._simulate_smb_request(header, query_data)
        
        # Simulate directory entries
        files = []
        for i in range(random.randint(3, 8)):
            file_info = FileInfo(
                file_id=random.randbytes(16),
                name=f"file_{i}.txt" if i % 2 == 0 else f"folder_{i}",
                size=random.randint(1024, 1048576) if i % 2 == 0 else 0,
                attributes=0x20 if i % 2 == 0 else 0x10,  # FILE_ATTRIBUTE_ARCHIVE or DIRECTORY
                creation_time=datetime.now(),
                last_access_time=datetime.now(),
                last_write_time=datetime.now(),
                change_time=datetime.now()
            )
            files.append(file_info)
        
        print(f"   ✅ Directory listed ({latency:.2f}ms)")
        print(f"   Entries: {len(files)}")
        
        for file_info in files:
            file_type = "DIR" if file_info.attributes & 0x10 else "FILE"
            print(f"     {file_type:4} {file_info.size:>10,} {file_info.name}")
        
        # Close directory
        self.close_file(dir_file_id)
        
        return files
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            'server': f"\\\\{self.server}\\{self.share}",
            'version': self.version.name,
            'authenticated': self.authenticated,
            'session_id': f"{self.session_id:016x}" if self.session_id else None,
            'tree_id': f"{self.tree_id:08x}" if self.tree_id else None,
            'open_files': len(self.open_files),
            'message_id': self.message_id
        }

def demonstrate_smb_operations():
    """Demonstrate SMB client operations"""
    print("=== SMB Protocol Demonstration ===")
    
    # Initialize SMB client
    smb_client = SMBClient("fileserver", "shared", SMBVersion.SMB30)
    
    # Protocol negotiation
    if not smb_client.negotiate():
        print("Failed to negotiate SMB protocol")
        return
    
    # Authentication
    if not smb_client.authenticate("john.doe", "password123", "DOMAIN"):
        print("Failed to authenticate")
        return
    
    # Connect to share
    if not smb_client.tree_connect():
        print("Failed to connect to share")
        return
    
    # List root directory
    files = smb_client.list_directory("\\")
    
    # File operations
    test_files = ["document.docx", "presentation.pptx", "data.xlsx"]
    
    for filename in test_files:
        # Open file
        file_id = smb_client.create_file(filename)
        if file_id:
            # Read file
            data = smb_client.read_file(file_id, offset=0, length=4096)
            
            # Write file (simulate modification)
            new_data = f"Modified at {datetime.now()}\n".encode()
            smb_client.write_file(file_id, new_data, offset=0)
            
            # Close file
            smb_client.close_file(file_id)
    
    # Performance test
    print(f"\n⚡ Performance Test")
    start_time = time.time()
    
    for i in range(5):
        file_id = smb_client.create_file(f"test_{i}.dat")
        if file_id:
            smb_client.read_file(file_id, length=8192)
            smb_client.close_file(file_id)
    
    elapsed = time.time() - start_time
    ops_per_sec = 15 / elapsed  # 5 creates + 5 reads + 5 closes
    
    print(f"   Operations: 15 (5 create/read/close cycles)")
    print(f"   Total Time: {elapsed:.2f}s")
    print(f"   Ops/sec: {ops_per_sec:.1f}")
    
    # Client statistics
    stats = smb_client.get_stats()
    print(f"\n📊 Client Statistics")
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    demonstrate_smb_operations()
    
    print(f"\n🎯 SMB enables Windows-native file sharing and collaboration")
    print(f"💡 Key features: authentication, encryption, multichannel, clustering")
    print(f"🚀 Enterprise use: file servers, domain storage, application data")
