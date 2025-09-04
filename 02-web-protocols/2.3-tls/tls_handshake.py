#!/usr/bin/env python3
"""
TLS Handshake Simulation
Demonstrates TLS 1.2 vs TLS 1.3 handshake process, certificate validation, and cipher negotiation
"""

import time
import random
import hashlib
import json
from datetime import datetime, timedelta

class TLSCertificate:
    def __init__(self, subject, issuer, valid_from, valid_to, public_key_size=2048):
        self.subject = subject
        self.issuer = issuer
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.public_key_size = public_key_size
        self.serial_number = random.randint(100000, 999999)
        self.signature_algorithm = "SHA256-RSA"
        self.extensions = {
            'subject_alt_names': [],
            'key_usage': ['digital_signature', 'key_encipherment'],
            'extended_key_usage': ['server_auth']
        }
    
    def is_valid(self, current_time=None):
        """Check if certificate is currently valid"""
        current_time = current_time or datetime.now()
        return self.valid_from <= current_time <= self.valid_to
    
    def matches_hostname(self, hostname):
        """Check if certificate matches hostname"""
        # Simplified hostname matching
        if hostname in self.subject:
            return True
        return hostname in self.extensions.get('subject_alt_names', [])

class TLSCipherSuite:
    def __init__(self, name, key_exchange, authentication, encryption, hash_func, security_level):
        self.name = name
        self.key_exchange = key_exchange
        self.authentication = authentication
        self.encryption = encryption
        self.hash_func = hash_func
        self.security_level = security_level  # 1-5, 5 being highest
    
    def __str__(self):
        return f"{self.name} ({self.key_exchange}-{self.authentication}-{self.encryption}-{self.hash_func})"

class TLSHandshake:
    def __init__(self, version="1.3"):
        self.version = version
        self.supported_cipher_suites = self._get_supported_ciphers()
        self.certificates = self._generate_certificate_chain()
        self.session_id = None
        self.master_secret = None
        self.handshake_messages = []
        
    def _get_supported_ciphers(self):
        """Get supported cipher suites based on TLS version"""
        if self.version == "1.3":
            return [
                TLSCipherSuite("TLS_AES_256_GCM_SHA384", "ECDHE", "ECDSA", "AES-256-GCM", "SHA384", 5),
                TLSCipherSuite("TLS_AES_128_GCM_SHA256", "ECDHE", "ECDSA", "AES-128-GCM", "SHA256", 4),
                TLSCipherSuite("TLS_CHACHA20_POLY1305_SHA256", "ECDHE", "ECDSA", "ChaCha20-Poly1305", "SHA256", 5)
            ]
        else:  # TLS 1.2
            return [
                TLSCipherSuite("TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384", "ECDHE", "RSA", "AES-256-GCM", "SHA384", 4),
                TLSCipherSuite("TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256", "ECDHE", "RSA", "AES-128-GCM", "SHA256", 4),
                TLSCipherSuite("TLS_RSA_WITH_AES_256_CBC_SHA256", "RSA", "RSA", "AES-256-CBC", "SHA256", 3),
                TLSCipherSuite("TLS_RSA_WITH_AES_128_CBC_SHA", "RSA", "RSA", "AES-128-CBC", "SHA1", 2)
            ]
    
    def _generate_certificate_chain(self):
        """Generate a certificate chain"""
        now = datetime.now()
        
        # Root CA
        root_ca = TLSCertificate(
            subject="CN=Example Root CA, O=Example Corp",
            issuer="CN=Example Root CA, O=Example Corp",  # Self-signed
            valid_from=now - timedelta(days=365*5),
            valid_to=now + timedelta(days=365*10),
            public_key_size=4096
        )
        
        # Intermediate CA
        intermediate_ca = TLSCertificate(
            subject="CN=Example Intermediate CA, O=Example Corp",
            issuer="CN=Example Root CA, O=Example Corp",
            valid_from=now - timedelta(days=365*2),
            valid_to=now + timedelta(days=365*5),
            public_key_size=2048
        )
        
        # Server certificate
        server_cert = TLSCertificate(
            subject="CN=api.example.com, O=Example Corp",
            issuer="CN=Example Intermediate CA, O=Example Corp",
            valid_from=now - timedelta(days=30),
            valid_to=now + timedelta(days=365),
            public_key_size=2048
        )
        server_cert.extensions['subject_alt_names'] = ['api.example.com', 'www.api.example.com']
        
        return [server_cert, intermediate_ca, root_ca]
    
    def client_hello(self, hostname):
        """Simulate Client Hello message"""
        message = {
            'type': 'ClientHello',
            'tls_version': f'TLS {self.version}',
            'random': hashlib.sha256(str(random.random()).encode()).hexdigest()[:32],
            'session_id': '',
            'cipher_suites': [cipher.name for cipher in self.supported_cipher_suites],
            'compression_methods': ['null'],
            'extensions': {
                'server_name': hostname,
                'supported_groups': ['secp256r1', 'secp384r1', 'x25519'],
                'signature_algorithms': ['rsa_pss_rsae_sha256', 'ecdsa_secp256r1_sha256'],
                'supported_versions': [f'TLS {self.version}']
            }
        }
        
        if self.version == "1.3":
            # TLS 1.3 includes key shares in Client Hello
            message['extensions']['key_share'] = {
                'groups': ['x25519', 'secp256r1'],
                'key_exchange_data': hashlib.sha256(str(random.random()).encode()).hexdigest()
            }
        
        self.handshake_messages.append(message)
        return message
    
    def server_hello(self, client_hello):
        """Simulate Server Hello message"""
        # Select cipher suite (choose the most secure one client supports)
        selected_cipher = self.supported_cipher_suites[0]  # Assume best one first
        
        message = {
            'type': 'ServerHello',
            'tls_version': f'TLS {self.version}',
            'random': hashlib.sha256(str(random.random()).encode()).hexdigest()[:32],
            'session_id': hashlib.sha256(str(random.random()).encode()).hexdigest()[:16],
            'cipher_suite': selected_cipher.name,
            'compression_method': 'null'
        }
        
        if self.version == "1.3":
            # TLS 1.3 includes key share in Server Hello
            message['extensions'] = {
                'key_share': {
                    'group': 'x25519',
                    'key_exchange_data': hashlib.sha256(str(random.random()).encode()).hexdigest()
                },
                'supported_versions': f'TLS {self.version}'
            }
        
        self.session_id = message['session_id']
        self.handshake_messages.append(message)
        return message, selected_cipher
    
    def certificate_message(self):
        """Simulate Certificate message"""
        message = {
            'type': 'Certificate',
            'certificate_chain': []
        }
        
        for cert in self.certificates:
            cert_data = {
                'subject': cert.subject,
                'issuer': cert.issuer,
                'serial_number': cert.serial_number,
                'valid_from': cert.valid_from.isoformat(),
                'valid_to': cert.valid_to.isoformat(),
                'public_key_size': cert.public_key_size,
                'signature_algorithm': cert.signature_algorithm,
                'extensions': cert.extensions
            }
            message['certificate_chain'].append(cert_data)
        
        self.handshake_messages.append(message)
        return message
    
    def verify_certificate_chain(self, hostname):
        """Simulate certificate chain verification"""
        verification_results = []
        
        for i, cert in enumerate(self.certificates):
            result = {
                'certificate': cert.subject,
                'checks': {}
            }
            
            # Check validity period
            result['checks']['validity_period'] = cert.is_valid()
            
            # Check hostname (only for server cert)
            if i == 0:  # Server certificate
                result['checks']['hostname_match'] = cert.matches_hostname(hostname)
            
            # Check signature (simplified - assume valid if issued by next cert in chain)
            if i < len(self.certificates) - 1:
                result['checks']['signature_valid'] = True
            else:  # Root CA
                result['checks']['signature_valid'] = True  # Self-signed root
            
            # Check if issuer is trusted
            result['checks']['issuer_trusted'] = True  # Assume in trust store
            
            verification_results.append(result)
        
        return verification_results
    
    def key_exchange(self, cipher_suite):
        """Simulate key exchange process"""
        if self.version == "1.3":
            # TLS 1.3 uses Diffie-Hellman key exchange with key shares already sent
            key_exchange_data = {
                'type': 'ECDHE_KeyExchange',
                'method': 'x25519',
                'client_key_share': 'already_sent_in_client_hello',
                'server_key_share': 'already_sent_in_server_hello',
                'shared_secret': hashlib.sha256(str(random.random()).encode()).hexdigest()
            }
        else:
            # TLS 1.2 separate key exchange message
            if cipher_suite.key_exchange == "ECDHE":
                key_exchange_data = {
                    'type': 'ServerKeyExchange',
                    'method': 'ECDHE',
                    'curve': 'secp256r1',
                    'public_key': hashlib.sha256(str(random.random()).encode()).hexdigest(),
                    'signature': hashlib.sha256(str(random.random()).encode()).hexdigest()
                }
            else:  # RSA
                key_exchange_data = {
                    'type': 'RSA_KeyExchange',
                    'method': 'RSA',
                    'encrypted_premaster_secret': hashlib.sha256(str(random.random()).encode()).hexdigest()
                }
        
        return key_exchange_data
    
    def generate_master_secret(self, key_exchange_data):
        """Generate master secret from key exchange"""
        # Simplified master secret generation
        if self.version == "1.3":
            # TLS 1.3 uses HKDF key derivation
            self.master_secret = hashlib.sha256(
                (key_exchange_data['shared_secret'] + self.session_id).encode()
            ).hexdigest()
        else:
            # TLS 1.2 uses PRF (Pseudo-Random Function)
            premaster = key_exchange_data.get('encrypted_premaster_secret', 
                                            key_exchange_data.get('public_key', ''))
            self.master_secret = hashlib.sha256(
                (premaster + self.session_id).encode()
            ).hexdigest()
        
        return self.master_secret
    
    def finished_messages(self):
        """Generate Finished messages"""
        # Hash of all handshake messages
        handshake_hash = hashlib.sha256(
            json.dumps(self.handshake_messages, sort_keys=True).encode()
        ).hexdigest()
        
        client_finished = {
            'type': 'ClientFinished',
            'verify_data': hashlib.sha256((handshake_hash + 'client' + self.master_secret).encode()).hexdigest()[:24]
        }
        
        server_finished = {
            'type': 'ServerFinished',
            'verify_data': hashlib.sha256((handshake_hash + 'server' + self.master_secret).encode()).hexdigest()[:24]
        }
        
        return client_finished, server_finished

def simulate_tls_handshake(version="1.3", hostname="api.example.com"):
    """Simulate complete TLS handshake"""
    print(f"=== TLS {version} Handshake Simulation ===")
    print(f"Connecting to: {hostname}")
    
    handshake = TLSHandshake(version)
    start_time = time.time()
    
    # Step 1: Client Hello
    print(f"\n1. Client Hello")
    client_hello = handshake.client_hello(hostname)
    print(f"   TLS Version: {client_hello['tls_version']}")
    print(f"   Cipher Suites: {len(client_hello['cipher_suites'])} offered")
    print(f"   Extensions: {list(client_hello['extensions'].keys())}")
    if version == "1.3":
        print(f"   Key Share: {list(client_hello['extensions']['key_share']['groups'])}")
    
    # Step 2: Server Hello
    print(f"\n2. Server Hello")
    server_hello, selected_cipher = handshake.server_hello(client_hello)
    print(f"   Selected Cipher: {selected_cipher}")
    print(f"   Session ID: {server_hello['session_id']}")
    if version == "1.3":
        print(f"   Key Share: {server_hello['extensions']['key_share']['group']}")
    
    # Step 3: Certificate
    print(f"\n3. Certificate")
    cert_message = handshake.certificate_message()
    print(f"   Certificate Chain Length: {len(cert_message['certificate_chain'])}")
    for i, cert in enumerate(cert_message['certificate_chain']):
        print(f"   [{i}] {cert['subject']} (issued by {cert['issuer']})")
    
    # Step 4: Certificate Verification
    print(f"\n4. Certificate Verification")
    verification_results = handshake.verify_certificate_chain(hostname)
    for result in verification_results:
        print(f"   {result['certificate']}:")
        for check, passed in result['checks'].items():
            status = "✓" if passed else "✗"
            print(f"     {status} {check.replace('_', ' ').title()}")
    
    # Step 5: Key Exchange
    print(f"\n5. Key Exchange")
    key_exchange_data = handshake.key_exchange(selected_cipher)
    print(f"   Method: {key_exchange_data['method']}")
    print(f"   Type: {key_exchange_data['type']}")
    
    # Step 6: Master Secret Generation
    print(f"\n6. Master Secret Generation")
    master_secret = handshake.generate_master_secret(key_exchange_data)
    print(f"   Master Secret: {master_secret[:16]}... (truncated)")
    
    # Step 7: Finished Messages
    print(f"\n7. Finished Messages")
    client_finished, server_finished = handshake.finished_messages()
    print(f"   Client Finished: {client_finished['verify_data']}")
    print(f"   Server Finished: {server_finished['verify_data']}")
    
    handshake_time = time.time() - start_time
    print(f"\n✓ TLS {version} Handshake Complete!")
    print(f"   Total Time: {handshake_time:.3f}s")
    print(f"   Round Trips: {'1-RTT' if version == '1.3' else '2-RTT'}")
    
    return handshake, handshake_time

def compare_tls_versions():
    """Compare TLS 1.2 vs TLS 1.3 handshakes"""
    print(f"\n=== TLS Version Comparison ===")
    
    hostname = "secure.example.com"
    
    # TLS 1.2 handshake
    print(f"\nTesting TLS 1.2...")
    tls12_handshake, tls12_time = simulate_tls_handshake("1.2", hostname)
    
    # TLS 1.3 handshake
    print(f"\nTesting TLS 1.3...")
    tls13_handshake, tls13_time = simulate_tls_handshake("1.3", hostname)
    
    # Comparison
    print(f"\n=== Performance Comparison ===")
    print(f"TLS 1.2 Handshake Time: {tls12_time:.3f}s")
    print(f"TLS 1.3 Handshake Time: {tls13_time:.3f}s")
    improvement = ((tls12_time - tls13_time) / tls12_time) * 100
    print(f"TLS 1.3 Improvement: {improvement:.1f}% faster")
    
    print(f"\n=== Security Comparison ===")
    print(f"TLS 1.2 Features:")
    print(f"  • 2-RTT handshake")
    print(f"  • Supports legacy cipher suites")
    print(f"  • Optional perfect forward secrecy")
    print(f"  • Vulnerable to downgrade attacks")
    
    print(f"\nTLS 1.3 Features:")
    print(f"  • 1-RTT handshake (0-RTT with resumption)")
    print(f"  • Only secure cipher suites")
    print(f"  • Always perfect forward secrecy")
    print(f"  • Protection against downgrade attacks")
    print(f"  • Encrypted handshake messages")

def demonstrate_cipher_suites():
    """Demonstrate different cipher suites and their security levels"""
    print(f"\n=== Cipher Suite Analysis ===")
    
    handshake_12 = TLSHandshake("1.2")
    handshake_13 = TLSHandshake("1.3")
    
    print(f"TLS 1.2 Cipher Suites:")
    for cipher in handshake_12.supported_cipher_suites:
        security_stars = "★" * cipher.security_level + "☆" * (5 - cipher.security_level)
        print(f"  {cipher.name}")
        print(f"    Security: {security_stars} ({cipher.security_level}/5)")
        print(f"    Key Exchange: {cipher.key_exchange}")
        print(f"    Authentication: {cipher.authentication}")
        print(f"    Encryption: {cipher.encryption}")
        print(f"    Hash: {cipher.hash_func}")
        print()
    
    print(f"TLS 1.3 Cipher Suites:")
    for cipher in handshake_13.supported_cipher_suites:
        security_stars = "★" * cipher.security_level + "☆" * (5 - cipher.security_level)
        print(f"  {cipher.name}")
        print(f"    Security: {security_stars} ({cipher.security_level}/5)")
        print(f"    Encryption: {cipher.encryption}")
        print(f"    Hash: {cipher.hash_func}")
        print()

def simulate_certificate_validation_scenarios():
    """Simulate various certificate validation scenarios"""
    print(f"\n=== Certificate Validation Scenarios ===")
    
    scenarios = [
        {
            'name': 'Valid Certificate',
            'hostname': 'api.example.com',
            'expected': 'Success'
        },
        {
            'name': 'Hostname Mismatch',
            'hostname': 'different.example.com',
            'expected': 'Failure - Hostname mismatch'
        },
        {
            'name': 'Expired Certificate',
            'hostname': 'api.example.com',
            'cert_expired': True,
            'expected': 'Failure - Certificate expired'
        }
    ]
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"Hostname: {scenario['hostname']}")
        
        handshake = TLSHandshake("1.3")
        
        # Modify certificate for testing
        if scenario.get('cert_expired'):
            handshake.certificates[0].valid_to = datetime.now() - timedelta(days=1)
        
        verification_results = handshake.verify_certificate_chain(scenario['hostname'])
        
        all_passed = True
        for result in verification_results:
            for check, passed in result['checks'].items():
                if not passed:
                    all_passed = False
                    break
        
        status = "✓ PASS" if all_passed else "✗ FAIL"
        print(f"Result: {status}")
        print(f"Expected: {scenario['expected']}")

if __name__ == "__main__":
    # Basic TLS handshake simulation
    simulate_tls_handshake("1.3", "api.example.com")
    
    # Compare TLS versions
    compare_tls_versions()
    
    # Cipher suite analysis
    demonstrate_cipher_suites()
    
    # Certificate validation scenarios
    simulate_certificate_validation_scenarios()
