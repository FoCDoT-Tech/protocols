#!/usr/bin/env python3
"""
mTLS Certificate Manager Implementation
Demonstrates certificate lifecycle management and SPIFFE identity integration
"""

import time
import threading
import hashlib
import base64
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime, timedelta
import cryptography
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption

class CertificateStatus(Enum):
    """Certificate lifecycle status"""
    PENDING = "pending"
    ISSUED = "issued"
    ACTIVE = "active"
    EXPIRING = "expiring"
    EXPIRED = "expired"
    REVOKED = "revoked"

@dataclass
class SPIFFEIdentity:
    """SPIFFE identity representation"""
    trust_domain: str
    path: str
    
    @property
    def spiffe_id(self) -> str:
        return f"spiffe://{self.trust_domain}{self.path}"
    
    def __str__(self) -> str:
        return self.spiffe_id

@dataclass
class CertificateInfo:
    """Certificate information and metadata"""
    serial_number: str
    subject: str
    issuer: str
    spiffe_id: SPIFFEIdentity
    not_before: datetime
    not_after: datetime
    status: CertificateStatus
    certificate_pem: str
    private_key_pem: str
    created_at: datetime = field(default_factory=datetime.now)
    last_rotation: Optional[datetime] = None
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.not_after
    
    @property
    def is_expiring_soon(self) -> bool:
        # Consider certificate expiring if less than 25% of lifetime remains
        total_lifetime = self.not_after - self.not_before
        time_remaining = self.not_after - datetime.now()
        return time_remaining < (total_lifetime * 0.25)
    
    @property
    def days_until_expiry(self) -> int:
        return (self.not_after - datetime.now()).days

class CertificateAuthority:
    """
    Certificate Authority for issuing and managing X.509 certificates
    Simulates Istio Citadel and SPIRE Server functionality
    """
    
    def __init__(self, trust_domain: str = "cluster.local"):
        self.trust_domain = trust_domain
        self.serial_counter = 1000
        self.issued_certificates: Dict[str, CertificateInfo] = {}
        self.revoked_certificates: Set[str] = set()
        self.lock = threading.Lock()
        
        # Generate CA certificate and private key
        self.ca_private_key, self.ca_certificate = self._generate_ca_certificate()
        
        print(f"[Certificate Authority] Initialized for trust domain: {trust_domain}")
    
    def _generate_ca_certificate(self) -> Tuple[rsa.RSAPrivateKey, x509.Certificate]:
        """Generate self-signed CA certificate"""
        # Generate CA private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Create CA certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Service Mesh CA"),
            x509.NameAttribute(NameOID.COMMON_NAME, f"Service Mesh Root CA - {self.trust_domain}"),
        ])
        
        certificate = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            1
        ).not_valid_before(
            datetime.now()
        ).not_valid_after(
            datetime.now() + timedelta(days=3650)  # 10 years
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=True,
                crl_sign=True,
                digital_signature=False,
                key_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        ).sign(private_key, hashes.SHA256())
        
        return private_key, certificate
    
    def issue_certificate(self, spiffe_id: SPIFFEIdentity, 
                         validity_hours: int = 24) -> CertificateInfo:
        """Issue new X.509 certificate for service identity"""
        with self.lock:
            # Generate workload private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Create certificate subject
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Service Mesh"),
                x509.NameAttribute(NameOID.COMMON_NAME, spiffe_id.path.split('/')[-1]),
            ])
            
            # Generate serial number
            serial_number = self.serial_counter
            self.serial_counter += 1
            
            # Create certificate
            not_before = datetime.now()
            not_after = not_before + timedelta(hours=validity_hours)
            
            certificate = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                self.ca_certificate.subject
            ).public_key(
                private_key.public_key()
            ).serial_number(
                serial_number
            ).not_valid_before(
                not_before
            ).not_valid_after(
                not_after
            ).add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            ).add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    content_commitment=False,
                    data_encipherment=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True,
            ).add_extension(
                x509.ExtendedKeyUsage([
                    x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                    x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                ]),
                critical=True,
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.UniformResourceIdentifier(spiffe_id.spiffe_id),
                ]),
                critical=True,
            ).sign(self.ca_private_key, hashes.SHA256())
            
            # Convert to PEM format
            certificate_pem = certificate.public_bytes(Encoding.PEM).decode('utf-8')
            private_key_pem = private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            ).decode('utf-8')
            
            # Create certificate info
            cert_info = CertificateInfo(
                serial_number=str(serial_number),
                subject=subject.rfc4514_string(),
                issuer=self.ca_certificate.subject.rfc4514_string(),
                spiffe_id=spiffe_id,
                not_before=not_before,
                not_after=not_after,
                status=CertificateStatus.ISSUED,
                certificate_pem=certificate_pem,
                private_key_pem=private_key_pem
            )
            
            self.issued_certificates[str(serial_number)] = cert_info
            
            print(f"[Certificate Authority] Issued certificate for {spiffe_id.spiffe_id} "
                  f"(serial: {serial_number}, expires: {not_after.strftime('%Y-%m-%d %H:%M:%S')})")
            
            return cert_info
    
    def revoke_certificate(self, serial_number: str) -> bool:
        """Revoke certificate by serial number"""
        with self.lock:
            if serial_number in self.issued_certificates:
                cert_info = self.issued_certificates[serial_number]
                cert_info.status = CertificateStatus.REVOKED
                self.revoked_certificates.add(serial_number)
                
                print(f"[Certificate Authority] Revoked certificate {serial_number} "
                      f"for {cert_info.spiffe_id.spiffe_id}")
                return True
            
            return False
    
    def validate_certificate(self, certificate_pem: str) -> bool:
        """Validate certificate against CA and check revocation"""
        try:
            certificate = x509.load_pem_x509_certificate(certificate_pem.encode('utf-8'))
            
            # Check if issued by this CA
            if certificate.issuer != self.ca_certificate.subject:
                return False
            
            # Check expiration
            if datetime.now() > certificate.not_valid_after:
                return False
            
            # Check revocation
            serial_number = str(certificate.serial_number)
            if serial_number in self.revoked_certificates:
                return False
            
            # Verify signature (simplified)
            try:
                self.ca_certificate.public_key().verify(
                    certificate.signature,
                    certificate.tbs_certificate_bytes,
                    certificate.signature_algorithm_oid._name
                )
                return True
            except:
                return False
                
        except Exception as e:
            print(f"[Certificate Authority] Validation error: {e}")
            return False
    
    def get_ca_certificate_pem(self) -> str:
        """Get CA certificate in PEM format"""
        return self.ca_certificate.public_bytes(Encoding.PEM).decode('utf-8')
    
    def get_certificate_stats(self) -> Dict[str, Any]:
        """Get certificate authority statistics"""
        with self.lock:
            total_certs = len(self.issued_certificates)
            active_certs = len([c for c in self.issued_certificates.values() 
                              if c.status == CertificateStatus.ACTIVE])
            expired_certs = len([c for c in self.issued_certificates.values() 
                               if c.is_expired])
            expiring_certs = len([c for c in self.issued_certificates.values() 
                                if c.is_expiring_soon and not c.is_expired])
            revoked_certs = len(self.revoked_certificates)
            
            return {
                "total_certificates": total_certs,
                "active_certificates": active_certs,
                "expired_certificates": expired_certs,
                "expiring_certificates": expiring_certs,
                "revoked_certificates": revoked_certs,
                "trust_domain": self.trust_domain
            }

class WorkloadCertificateManager:
    """
    Manages certificates for individual workloads
    Simulates SPIRE Agent functionality
    """
    
    def __init__(self, workload_id: str, spiffe_id: SPIFFEIdentity, ca: CertificateAuthority):
        self.workload_id = workload_id
        self.spiffe_id = spiffe_id
        self.ca = ca
        self.current_certificate: Optional[CertificateInfo] = None
        self.rotation_enabled = True
        self.rotation_threshold_hours = 6  # Rotate when 6 hours remaining
        self.running = False
        
        print(f"[Workload Cert Manager {workload_id}] Initialized for {spiffe_id.spiffe_id}")
    
    def start(self):
        """Start certificate management"""
        self.running = True
        
        # Get initial certificate
        self._rotate_certificate()
        
        # Start rotation monitoring
        rotation_thread = threading.Thread(target=self._rotation_loop)
        rotation_thread.daemon = True
        rotation_thread.start()
        
        print(f"[Workload Cert Manager {self.workload_id}] Started certificate management")
    
    def stop(self):
        """Stop certificate management"""
        self.running = False
        print(f"[Workload Cert Manager {self.workload_id}] Stopped certificate management")
    
    def _rotation_loop(self):
        """Background loop for certificate rotation"""
        while self.running:
            try:
                if self.rotation_enabled and self._should_rotate():
                    self._rotate_certificate()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"[Workload Cert Manager {self.workload_id}] Rotation error: {e}")
    
    def _should_rotate(self) -> bool:
        """Check if certificate should be rotated"""
        if not self.current_certificate:
            return True
        
        if self.current_certificate.is_expired:
            return True
        
        # Check if within rotation threshold
        time_remaining = self.current_certificate.not_after - datetime.now()
        return time_remaining.total_seconds() < (self.rotation_threshold_hours * 3600)
    
    def _rotate_certificate(self):
        """Rotate certificate"""
        try:
            # Issue new certificate
            new_certificate = self.ca.issue_certificate(self.spiffe_id)
            
            # Update current certificate
            old_serial = self.current_certificate.serial_number if self.current_certificate else "none"
            self.current_certificate = new_certificate
            self.current_certificate.status = CertificateStatus.ACTIVE
            self.current_certificate.last_rotation = datetime.now()
            
            print(f"[Workload Cert Manager {self.workload_id}] Rotated certificate: "
                  f"{old_serial} -> {new_certificate.serial_number}")
            
        except Exception as e:
            print(f"[Workload Cert Manager {self.workload_id}] Rotation failed: {e}")
    
    def get_certificate_bundle(self) -> Optional[Dict[str, str]]:
        """Get current certificate bundle"""
        if not self.current_certificate:
            return None
        
        return {
            "certificate": self.current_certificate.certificate_pem,
            "private_key": self.current_certificate.private_key_pem,
            "ca_certificate": self.ca.get_ca_certificate_pem(),
            "spiffe_id": self.current_certificate.spiffe_id.spiffe_id,
            "serial_number": self.current_certificate.serial_number,
            "expires_at": self.current_certificate.not_after.isoformat()
        }
    
    def get_certificate_status(self) -> Dict[str, Any]:
        """Get certificate status"""
        if not self.current_certificate:
            return {"status": "no_certificate"}
        
        return {
            "workload_id": self.workload_id,
            "spiffe_id": self.current_certificate.spiffe_id.spiffe_id,
            "serial_number": self.current_certificate.serial_number,
            "status": self.current_certificate.status.value,
            "expires_at": self.current_certificate.not_after.isoformat(),
            "days_until_expiry": self.current_certificate.days_until_expiry,
            "is_expiring_soon": self.current_certificate.is_expiring_soon,
            "last_rotation": self.current_certificate.last_rotation.isoformat() if self.current_certificate.last_rotation else None
        }

def demonstrate_mtls_certificate_management():
    """Demonstrate mTLS certificate management"""
    print("=== mTLS Certificate Management Demo ===")
    
    # Initialize Certificate Authority
    ca = CertificateAuthority("example.org")
    
    print("\n1. Certificate Authority initialized...")
    print(f"   Trust Domain: {ca.trust_domain}")
    print(f"   CA Certificate Subject: {ca.ca_certificate.subject.rfc4514_string()}")
    
    # Create SPIFFE identities for services
    service_identities = [
        SPIFFEIdentity("example.org", "/ns/production/sa/web-service"),
        SPIFFEIdentity("example.org", "/ns/production/sa/api-service"),
        SPIFFEIdentity("example.org", "/ns/production/sa/db-service")
    ]
    
    # Create workload certificate managers
    print("\n2. Creating workload certificate managers...")
    managers = []
    for i, identity in enumerate(service_identities):
        manager = WorkloadCertificateManager(f"workload-{i+1}", identity, ca)
        manager.start()
        managers.append(manager)
        time.sleep(0.5)
    
    # Show initial certificate status
    print("\n3. Initial certificate status...")
    for manager in managers:
        status = manager.get_certificate_status()
        print(f"   {status['workload_id']}: {status['spiffe_id']} "
              f"(serial: {status['serial_number']}, expires in {status['days_until_expiry']} days)")
    
    # Simulate certificate validation
    print("\n4. Certificate validation...")
    for manager in managers:
        bundle = manager.get_certificate_bundle()
        if bundle:
            is_valid = ca.validate_certificate(bundle["certificate"])
            print(f"   {manager.workload_id}: Certificate validation = {is_valid}")
    
    # Show CA statistics
    print("\n5. Certificate Authority statistics...")
    stats = ca.get_certificate_stats()
    print(f"   Total certificates: {stats['total_certificates']}")
    print(f"   Active certificates: {stats['active_certificates']}")
    print(f"   Expired certificates: {stats['expired_certificates']}")
    print(f"   Expiring certificates: {stats['expiring_certificates']}")
    print(f"   Revoked certificates: {stats['revoked_certificates']}")
    
    # Simulate certificate revocation
    print("\n6. Certificate revocation...")
    if managers:
        first_manager = managers[0]
        bundle = first_manager.get_certificate_bundle()
        if bundle:
            ca.revoke_certificate(bundle["serial_number"])
            
            # Validate revoked certificate
            is_valid = ca.validate_certificate(bundle["certificate"])
            print(f"   Revoked certificate validation = {is_valid}")
    
    # Simulate time passage for rotation
    print("\n7. Simulating certificate rotation...")
    print("   (In production, certificates would rotate automatically based on expiration)")
    
    # Force rotation for demonstration
    for manager in managers[1:]:  # Skip the revoked one
        manager._rotate_certificate()
    
    # Show updated status
    print("\n8. Updated certificate status...")
    for manager in managers:
        status = manager.get_certificate_status()
        print(f"   {status['workload_id']}: {status['status']} "
              f"(serial: {status['serial_number']})")
    
    # Cleanup
    print("\n9. Stopping certificate managers...")
    for manager in managers:
        manager.stop()
    
    print("\n=== mTLS Certificate Management Demo Complete ===")

if __name__ == "__main__":
    demonstrate_mtls_certificate_management()
