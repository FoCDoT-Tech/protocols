#!/usr/bin/env python3
"""
mTLS Proxy Simulator
Demonstrates mutual TLS handshake and service-to-service authentication
"""

import time
import threading
import socket
import ssl
import tempfile
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

class TLSMode(Enum):
    """TLS configuration modes"""
    DISABLED = "disabled"
    PERMISSIVE = "permissive"
    STRICT = "strict"

class HandshakeResult(Enum):
    """mTLS handshake results"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CERTIFICATE_ERROR = "certificate_error"
    AUTHENTICATION_ERROR = "authentication_error"

@dataclass
class TLSConfig:
    """TLS configuration for proxy"""
    mode: TLSMode
    certificate_path: str
    private_key_path: str
    ca_certificate_path: str
    verify_client: bool = True
    verify_server: bool = True

@dataclass
class ConnectionInfo:
    """Connection information"""
    source_service: str
    destination_service: str
    source_spiffe_id: str
    destination_spiffe_id: str
    handshake_result: HandshakeResult
    handshake_duration_ms: float
    cipher_suite: str = ""
    protocol_version: str = ""
    timestamp: float = field(default_factory=time.time)

class MTLSProxy:
    """
    mTLS-enabled proxy simulator
    Demonstrates Envoy sidecar proxy behavior with mutual TLS
    """
    
    def __init__(self, service_name: str, spiffe_id: str, port: int = 0):
        self.service_name = service_name
        self.spiffe_id = spiffe_id
        self.port = port
        self.tls_config: Optional[TLSConfig] = None
        self.connections: List[ConnectionInfo] = []
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "successful_handshakes": 0,
            "failed_handshakes": 0,
            "certificate_errors": 0,
            "authentication_errors": 0
        }
        
        print(f"[mTLS Proxy {service_name}] Initialized with SPIFFE ID: {spiffe_id}")
    
    def configure_tls(self, tls_config: TLSConfig):
        """Configure TLS settings"""
        self.tls_config = tls_config
        print(f"[mTLS Proxy {self.service_name}] Configured TLS mode: {tls_config.mode.value}")
    
    def start_server(self):
        """Start mTLS server"""
        if not self.tls_config:
            print(f"[mTLS Proxy {self.service_name}] No TLS configuration provided")
            return
        
        self.running = True
        
        # Create server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('localhost', self.port))
        
        # Get actual port if auto-assigned
        if self.port == 0:
            self.port = self.server_socket.getsockname()[1]
        
        self.server_socket.listen(5)
        
        # Start server thread
        server_thread = threading.Thread(target=self._server_loop)
        server_thread.daemon = True
        server_thread.start()
        
        print(f"[mTLS Proxy {self.service_name}] Server started on port {self.port}")
    
    def stop_server(self):
        """Stop mTLS server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print(f"[mTLS Proxy {self.service_name}] Server stopped")
    
    def _server_loop(self):
        """Server loop handling incoming connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                
                # Handle connection in separate thread
                connection_thread = threading.Thread(
                    target=self._handle_connection,
                    args=(client_socket, address)
                )
                connection_thread.daemon = True
                connection_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"[mTLS Proxy {self.service_name}] Server error: {e}")
                break
    
    def _handle_connection(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Handle individual client connection"""
        start_time = time.time()
        handshake_result = HandshakeResult.FAILED
        cipher_suite = ""
        protocol_version = ""
        client_spiffe_id = "unknown"
        
        try:
            self.stats["total_connections"] += 1
            
            if self.tls_config.mode == TLSMode.DISABLED:
                # Handle plaintext connection
                handshake_result = HandshakeResult.SUCCESS
                client_spiffe_id = "plaintext"
                
                # Simple HTTP response
                response = "HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, World!"
                client_socket.send(response.encode())
                
            else:
                # Handle TLS connection
                ssl_context = self._create_ssl_context()
                
                try:
                    # Wrap socket with TLS
                    tls_socket = ssl_context.wrap_socket(
                        client_socket,
                        server_side=True
                    )
                    
                    # Extract certificate information
                    peer_cert = tls_socket.getpeercert()
                    if peer_cert:
                        # Extract SPIFFE ID from SAN
                        client_spiffe_id = self._extract_spiffe_id(peer_cert)
                    
                    # Get TLS information
                    cipher_suite = tls_socket.cipher()[0] if tls_socket.cipher() else ""
                    protocol_version = tls_socket.version() or ""
                    
                    handshake_result = HandshakeResult.SUCCESS
                    self.stats["successful_handshakes"] += 1
                    
                    # Simple HTTP response over TLS
                    response = "HTTP/1.1 200 OK\r\nContent-Length: 18\r\n\r\nSecure Hello mTLS!"
                    tls_socket.send(response.encode())
                    
                    tls_socket.close()
                    
                except ssl.SSLError as e:
                    handshake_result = HandshakeResult.CERTIFICATE_ERROR
                    self.stats["certificate_errors"] += 1
                    print(f"[mTLS Proxy {self.service_name}] SSL error: {e}")
                    
                except Exception as e:
                    handshake_result = HandshakeResult.AUTHENTICATION_ERROR
                    self.stats["authentication_errors"] += 1
                    print(f"[mTLS Proxy {self.service_name}] Authentication error: {e}")
            
        except Exception as e:
            handshake_result = HandshakeResult.FAILED
            self.stats["failed_handshakes"] += 1
            print(f"[mTLS Proxy {self.service_name}] Connection error: {e}")
            
        finally:
            client_socket.close()
            
            # Record connection info
            handshake_duration = (time.time() - start_time) * 1000  # Convert to ms
            
            connection_info = ConnectionInfo(
                source_service="unknown",
                destination_service=self.service_name,
                source_spiffe_id=client_spiffe_id,
                destination_spiffe_id=self.spiffe_id,
                handshake_result=handshake_result,
                handshake_duration_ms=handshake_duration,
                cipher_suite=cipher_suite,
                protocol_version=protocol_version
            )
            
            self.connections.append(connection_info)
            
            # Keep only recent connections
            if len(self.connections) > 100:
                self.connections = self.connections[-100:]
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for mTLS"""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # Load server certificate and private key
        context.load_cert_chain(
            self.tls_config.certificate_path,
            self.tls_config.private_key_path
        )
        
        # Load CA certificate for client verification
        context.load_verify_locations(self.tls_config.ca_certificate_path)
        
        # Configure client certificate verification
        if self.tls_config.verify_client:
            context.verify_mode = ssl.CERT_REQUIRED
        else:
            context.verify_mode = ssl.CERT_NONE
        
        # Set TLS version
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        return context
    
    def _extract_spiffe_id(self, cert: Dict[str, Any]) -> str:
        """Extract SPIFFE ID from certificate SAN"""
        try:
            san_list = cert.get('subjectAltName', [])
            for san_type, san_value in san_list:
                if san_type == 'URI' and san_value.startswith('spiffe://'):
                    return san_value
        except:
            pass
        
        return "unknown"
    
    def make_request(self, target_proxy: 'MTLSProxy', path: str = "/") -> Dict[str, Any]:
        """Make mTLS request to another proxy"""
        start_time = time.time()
        
        try:
            if not target_proxy.tls_config or target_proxy.tls_config.mode == TLSMode.DISABLED:
                # Plaintext connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('localhost', target_proxy.port))
                
                request = f"GET {path} HTTP/1.1\r\nHost: {target_proxy.service_name}\r\n\r\n"
                sock.send(request.encode())
                
                response = sock.recv(1024).decode()
                sock.close()
                
                return {
                    "status": "success",
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "tls_enabled": False,
                    "response": response[:100]
                }
            
            else:
                # mTLS connection
                ssl_context = ssl.create_default_context()
                
                # Load client certificate
                ssl_context.load_cert_chain(
                    self.tls_config.certificate_path,
                    self.tls_config.private_key_path
                )
                
                # Load CA certificate
                ssl_context.load_verify_locations(self.tls_config.ca_certificate_path)
                
                # Configure server verification
                if self.tls_config.verify_server:
                    ssl_context.check_hostname = False  # SPIFFE IDs don't match hostnames
                    ssl_context.verify_mode = ssl.CERT_REQUIRED
                else:
                    ssl_context.verify_mode = ssl.CERT_NONE
                
                # Create TLS connection
                with socket.create_connection(('localhost', target_proxy.port)) as sock:
                    with ssl_context.wrap_socket(sock) as tls_sock:
                        request = f"GET {path} HTTP/1.1\r\nHost: {target_proxy.service_name}\r\n\r\n"
                        tls_sock.send(request.encode())
                        
                        response = tls_sock.recv(1024).decode()
                        
                        # Get TLS information
                        cipher_suite = tls_sock.cipher()[0] if tls_sock.cipher() else ""
                        protocol_version = tls_sock.version() or ""
                        
                        return {
                            "status": "success",
                            "response_time_ms": (time.time() - start_time) * 1000,
                            "tls_enabled": True,
                            "cipher_suite": cipher_suite,
                            "protocol_version": protocol_version,
                            "response": response[:100]
                        }
            
        except Exception as e:
            return {
                "status": "error",
                "response_time_ms": (time.time() - start_time) * 1000,
                "error": str(e)
            }
    
    def get_proxy_stats(self) -> Dict[str, Any]:
        """Get proxy statistics"""
        recent_connections = [c for c in self.connections if time.time() - c.timestamp < 300]  # Last 5 minutes
        
        return {
            "service_name": self.service_name,
            "spiffe_id": self.spiffe_id,
            "port": self.port,
            "tls_mode": self.tls_config.mode.value if self.tls_config else "none",
            "total_connections": self.stats["total_connections"],
            "successful_handshakes": self.stats["successful_handshakes"],
            "failed_handshakes": self.stats["failed_handshakes"],
            "certificate_errors": self.stats["certificate_errors"],
            "authentication_errors": self.stats["authentication_errors"],
            "recent_connections": len(recent_connections),
            "success_rate": (
                self.stats["successful_handshakes"] / max(1, self.stats["total_connections"])
            ) * 100
        }

def create_temp_certificates() -> Tuple[str, str, str]:
    """Create temporary certificates for testing"""
    from certificate_manager import CertificateAuthority, SPIFFEIdentity
    
    # Create CA
    ca = CertificateAuthority("test.local")
    
    # Create service certificate
    spiffe_id = SPIFFEIdentity("test.local", "/ns/default/sa/test-service")
    cert_info = ca.issue_certificate(spiffe_id)
    
    # Write certificates to temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as cert_file:
        cert_file.write(cert_info.certificate_pem)
        cert_path = cert_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.key', delete=False) as key_file:
        key_file.write(cert_info.private_key_pem)
        key_path = key_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as ca_file:
        ca_file.write(ca.get_ca_certificate_pem())
        ca_path = ca_file.name
    
    return cert_path, key_path, ca_path

def demonstrate_mtls_proxy():
    """Demonstrate mTLS proxy functionality"""
    print("=== mTLS Proxy Simulator Demo ===")
    
    # Create temporary certificates
    print("\n1. Creating temporary certificates...")
    cert_path, key_path, ca_path = create_temp_certificates()
    
    try:
        # Create TLS configuration
        tls_config = TLSConfig(
            mode=TLSMode.STRICT,
            certificate_path=cert_path,
            private_key_path=key_path,
            ca_certificate_path=ca_path
        )
        
        # Create mTLS proxies
        print("\n2. Creating mTLS proxies...")
        proxies = []
        
        services = [
            ("web-service", "spiffe://test.local/ns/default/sa/web-service"),
            ("api-service", "spiffe://test.local/ns/default/sa/api-service"),
            ("db-service", "spiffe://test.local/ns/default/sa/db-service")
        ]
        
        for service_name, spiffe_id in services:
            proxy = MTLSProxy(service_name, spiffe_id)
            proxy.configure_tls(tls_config)
            proxy.start_server()
            proxies.append(proxy)
            time.sleep(0.5)
        
        print(f"   Created {len(proxies)} mTLS proxies")
        
        # Test service-to-service communication
        print("\n3. Testing service-to-service mTLS communication...")
        
        # Web service calls API service
        result = proxies[0].make_request(proxies[1], "/api/users")
        print(f"   web-service -> api-service: {result['status']} "
              f"({result['response_time_ms']:.1f}ms)")
        
        # API service calls DB service
        result = proxies[1].make_request(proxies[2], "/db/query")
        print(f"   api-service -> db-service: {result['status']} "
              f"({result['response_time_ms']:.1f}ms)")
        
        # Wait for connections to be processed
        time.sleep(1)
        
        # Show proxy statistics
        print("\n4. Proxy statistics...")
        for proxy in proxies:
            stats = proxy.get_proxy_stats()
            print(f"   {stats['service_name']}: {stats['total_connections']} connections, "
                  f"{stats['success_rate']:.1f}% success rate")
        
        # Test with different TLS modes
        print("\n5. Testing permissive mode...")
        
        # Configure one proxy in permissive mode
        permissive_config = TLSConfig(
            mode=TLSMode.PERMISSIVE,
            certificate_path=cert_path,
            private_key_path=key_path,
            ca_certificate_path=ca_path
        )
        
        proxies[0].configure_tls(permissive_config)
        
        # Test mixed mode communication
        result = proxies[1].make_request(proxies[0], "/health")
        print(f"   Mixed mode communication: {result['status']}")
        
        # Show connection details
        print("\n6. Recent connection details...")
        for proxy in proxies:
            if proxy.connections:
                latest = proxy.connections[-1]
                print(f"   {proxy.service_name}: {latest.handshake_result.value} "
                      f"({latest.handshake_duration_ms:.1f}ms, {latest.cipher_suite})")
        
        # Cleanup
        print("\n7. Stopping proxies...")
        for proxy in proxies:
            proxy.stop_server()
        
    finally:
        # Clean up temporary files
        for path in [cert_path, key_path, ca_path]:
            try:
                os.unlink(path)
            except:
                pass
    
    print("\n=== mTLS Proxy Simulator Demo Complete ===")

if __name__ == "__main__":
    demonstrate_mtls_proxy()
