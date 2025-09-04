#!/usr/bin/env python3
"""
TLS Protocol Diagram Renderer
Generates visual diagrams for TLS protocol concepts using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_tls_handshake_diagram():
    """Create TLS handshake process diagram"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # TLS 1.2 Handshake (2-RTT)
    ax1.set_title('TLS 1.2 Handshake (2-RTT)', fontsize=14, fontweight='bold')
    
    # Client and Server boxes
    client_box = FancyBboxPatch((1, 8), 2, 1, boxstyle="round,pad=0.1", 
                               facecolor='lightblue', edgecolor='blue', linewidth=2)
    server_box = FancyBboxPatch((11, 8), 2, 1, boxstyle="round,pad=0.1", 
                               facecolor='lightgreen', edgecolor='green', linewidth=2)
    
    ax1.add_patch(client_box)
    ax1.add_patch(server_box)
    ax1.text(2, 8.5, 'Client', ha='center', va='center', fontsize=12, fontweight='bold')
    ax1.text(12, 8.5, 'Server', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Handshake messages
    messages = [
        (7.5, 'Client Hello', 'right', 'red'),
        (7, 'Server Hello + Certificate', 'left', 'blue'),
        (6.5, 'Server Key Exchange', 'left', 'blue'),
        (6, 'Server Hello Done', 'left', 'blue'),
        (5.5, 'Client Key Exchange', 'right', 'red'),
        (5, 'Change Cipher Spec', 'right', 'red'),
        (4.5, 'Finished', 'right', 'red'),
        (4, 'Change Cipher Spec', 'left', 'blue'),
        (3.5, 'Finished', 'left', 'blue')
    ]
    
    for y, message, direction, color in messages:
        if direction == 'right':
            arrow = patches.FancyArrowPatch((3.2, y), (10.8, y),
                                          arrowstyle='->', mutation_scale=15,
                                          color=color, linewidth=1.5)
            ax1.text(7, y + 0.15, message, ha='center', va='bottom', fontsize=9, color=color)
        else:
            arrow = patches.FancyArrowPatch((10.8, y), (3.2, y),
                                          arrowstyle='->', mutation_scale=15,
                                          color=color, linewidth=1.5)
            ax1.text(7, y + 0.15, message, ha='center', va='bottom', fontsize=9, color=color)
        ax1.add_patch(arrow)
    
    # RTT indicators
    ax1.text(14.5, 6.5, 'RTT 1', ha='center', va='center', fontsize=10, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow'))
    ax1.text(14.5, 4, 'RTT 2', ha='center', va='center', fontsize=10, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow'))
    
    ax1.set_xlim(0, 16)
    ax1.set_ylim(3, 9.5)
    ax1.axis('off')
    
    # TLS 1.3 Handshake (1-RTT)
    ax2.set_title('TLS 1.3 Handshake (1-RTT)', fontsize=14, fontweight='bold')
    
    # Client and Server boxes
    client_box2 = FancyBboxPatch((1, 6), 2, 1, boxstyle="round,pad=0.1", 
                                facecolor='lightblue', edgecolor='blue', linewidth=2)
    server_box2 = FancyBboxPatch((11, 6), 2, 1, boxstyle="round,pad=0.1", 
                                facecolor='lightgreen', edgecolor='green', linewidth=2)
    
    ax2.add_patch(client_box2)
    ax2.add_patch(server_box2)
    ax2.text(2, 6.5, 'Client', ha='center', va='center', fontsize=12, fontweight='bold')
    ax2.text(12, 6.5, 'Server', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # TLS 1.3 messages (simplified)
    messages_13 = [
        (5.5, 'Client Hello + Key Share', 'right', 'red'),
        (4.5, 'Server Hello + Certificate + Key Share + Finished', 'left', 'blue'),
        (3.5, 'Finished', 'right', 'red'),
        (2.5, 'Application Data', 'both', 'green')
    ]
    
    for y, message, direction, color in messages_13:
        if direction == 'right':
            arrow = patches.FancyArrowPatch((3.2, y), (10.8, y),
                                          arrowstyle='->', mutation_scale=15,
                                          color=color, linewidth=1.5)
            ax2.text(7, y + 0.15, message, ha='center', va='bottom', fontsize=9, color=color)
        elif direction == 'left':
            arrow = patches.FancyArrowPatch((10.8, y), (3.2, y),
                                          arrowstyle='->', mutation_scale=15,
                                          color=color, linewidth=1.5)
            ax2.text(7, y + 0.15, message, ha='center', va='bottom', fontsize=9, color=color)
        else:  # both directions
            arrow1 = patches.FancyArrowPatch((3.2, y + 0.1), (10.8, y + 0.1),
                                           arrowstyle='->', mutation_scale=12,
                                           color=color, linewidth=1.5)
            arrow2 = patches.FancyArrowPatch((10.8, y - 0.1), (3.2, y - 0.1),
                                           arrowstyle='->', mutation_scale=12,
                                           color=color, linewidth=1.5)
            ax2.add_patch(arrow1)
            ax2.add_patch(arrow2)
            ax2.text(7, y + 0.15, message, ha='center', va='bottom', fontsize=9, color=color)
            continue
        ax2.add_patch(arrow)
    
    # RTT indicator
    ax2.text(14.5, 4.5, 'RTT 1', ha='center', va='center', fontsize=10, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgreen'))
    
    ax2.set_xlim(0, 16)
    ax2.set_ylim(2, 7.5)
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.3-tls/tls_handshake.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_certificate_chain_diagram():
    """Create certificate chain validation diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Certificate chain
    certificates = [
        {'name': 'Root CA', 'y': 8, 'color': 'gold', 'self_signed': True},
        {'name': 'Intermediate CA', 'y': 6, 'color': 'orange', 'self_signed': False},
        {'name': 'Server Certificate', 'y': 4, 'color': 'lightgreen', 'self_signed': False}
    ]
    
    # Draw certificates
    for i, cert in enumerate(certificates):
        cert_box = FancyBboxPatch((2, cert['y'] - 0.5), 4, 1, boxstyle="round,pad=0.1",
                                 facecolor=cert['color'], edgecolor='black', linewidth=2)
        ax.add_patch(cert_box)
        ax.text(4, cert['y'], cert['name'], ha='center', va='center', 
                fontsize=12, fontweight='bold')
        
        # Add certificate details
        if cert['name'] == 'Root CA':
            details = ['Self-signed', 'In trust store', 'Long validity period']
        elif cert['name'] == 'Intermediate CA':
            details = ['Signed by Root CA', 'CA: TRUE', 'Medium validity']
        else:
            details = ['Signed by Intermediate', 'Subject: api.example.com', 'Short validity']
        
        for j, detail in enumerate(details):
            ax.text(6.5, cert['y'] + 0.2 - (j * 0.2), f'• {detail}', 
                   fontsize=9, va='center')
        
        # Draw signing arrows
        if not cert['self_signed']:
            arrow = patches.FancyArrowPatch((4, cert['y'] + 0.5), (4, cert['y'] + 1.5),
                                          arrowstyle='->', mutation_scale=20,
                                          color='red', linewidth=2)
            ax.add_patch(arrow)
            ax.text(4.5, cert['y'] + 1, 'signs', ha='left', va='center', 
                   fontsize=9, color='red', fontweight='bold')
    
    # Validation process
    ax.text(10, 8, 'Validation Process:', fontsize=14, fontweight='bold')
    validation_steps = [
        '1. Check certificate expiration',
        '2. Verify digital signature',
        '3. Check certificate chain',
        '4. Validate hostname match',
        '5. Check revocation status',
        '6. Verify trust anchor'
    ]
    
    for i, step in enumerate(validation_steps):
        ax.text(10, 7.5 - (i * 0.4), step, fontsize=10)
    
    # Trust store
    trust_box = FancyBboxPatch((1, 1), 5, 1.5, boxstyle="round,pad=0.1",
                              facecolor='lightblue', edgecolor='blue', linewidth=2)
    ax.add_patch(trust_box)
    ax.text(3.5, 1.75, 'Trust Store', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    ax.text(3.5, 1.25, 'Contains trusted Root CAs', ha='center', va='center', fontsize=10)
    
    # Arrow from root to trust store
    trust_arrow = patches.FancyArrowPatch((3.5, 3.5), (3.5, 2.5),
                                        arrowstyle='->', mutation_scale=20,
                                        color='blue', linewidth=2)
    ax.add_patch(trust_arrow)
    ax.text(3.8, 3, 'verified\nagainst', ha='left', va='center', 
           fontsize=9, color='blue')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.set_title('TLS Certificate Chain Validation', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.3-tls/certificate_chain.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_cipher_suites_diagram():
    """Create cipher suites comparison diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    cipher_suites = [
        {
            'name': 'TLS_AES_256_GCM_SHA384',
            'version': 'TLS 1.3',
            'security': 5,
            'components': ['ECDHE (implicit)', 'AES-256-GCM', 'SHA-384'],
            'color': 'darkgreen'
        },
        {
            'name': 'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384',
            'version': 'TLS 1.2',
            'security': 4,
            'components': ['ECDHE', 'RSA', 'AES-256-GCM', 'SHA-384'],
            'color': 'green'
        },
        {
            'name': 'TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256',
            'version': 'TLS 1.2',
            'security': 3,
            'components': ['ECDHE', 'RSA', 'AES-128-CBC', 'SHA-256'],
            'color': 'orange'
        },
        {
            'name': 'TLS_RSA_WITH_AES_128_CBC_SHA',
            'version': 'TLS 1.2',
            'security': 2,
            'components': ['RSA', 'RSA', 'AES-128-CBC', 'SHA-1'],
            'color': 'red'
        }
    ]
    
    # Header
    ax.text(7, 9.5, 'TLS Cipher Suites Comparison', ha='center', va='center',
            fontsize=16, fontweight='bold')
    
    # Column headers
    headers = ['Cipher Suite', 'Version', 'Security', 'Components']
    header_positions = [1, 6, 8.5, 10]
    
    for header, pos in zip(headers, header_positions):
        ax.text(pos, 8.5, header, ha='left', va='center', fontsize=12, fontweight='bold')
    
    # Draw cipher suites
    for i, cipher in enumerate(cipher_suites):
        y_pos = 7.5 - (i * 1.2)
        
        # Cipher suite name
        name_box = FancyBboxPatch((0.5, y_pos - 0.3), 5, 0.6, boxstyle="round,pad=0.05",
                                 facecolor=cipher['color'], alpha=0.3, edgecolor=cipher['color'])
        ax.add_patch(name_box)
        ax.text(1, y_pos, cipher['name'], ha='left', va='center', fontsize=9, fontweight='bold')
        
        # Version
        ax.text(6, y_pos, cipher['version'], ha='left', va='center', fontsize=10)
        
        # Security level (stars)
        security_stars = "★" * cipher['security'] + "☆" * (5 - cipher['security'])
        ax.text(8.5, y_pos, security_stars, ha='left', va='center', fontsize=12, color='gold')
        
        # Components
        components_text = ' + '.join(cipher['components'])
        ax.text(10, y_pos, components_text, ha='left', va='center', fontsize=9)
    
    # Security legend
    ax.text(1, 2.5, 'Security Levels:', fontsize=12, fontweight='bold')
    security_levels = [
        ('★★★★★', 'Excellent - Recommended for all use cases'),
        ('★★★★☆', 'Good - Suitable for most applications'),
        ('★★★☆☆', 'Fair - Consider upgrading'),
        ('★★☆☆☆', 'Poor - Avoid if possible'),
        ('★☆☆☆☆', 'Weak - Deprecated')
    ]
    
    for i, (stars, description) in enumerate(security_levels):
        y_pos = 2 - (i * 0.3)
        ax.text(1, y_pos, stars, ha='left', va='center', fontsize=10, color='gold')
        ax.text(2.5, y_pos, description, ha='left', va='center', fontsize=9)
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.3-tls/cipher_suites.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_mtls_diagram():
    """Create mutual TLS (mTLS) diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Title
    ax.text(7, 9.5, 'Mutual TLS (mTLS) Authentication', ha='center', va='center',
            fontsize=16, fontweight='bold')
    
    # Client service
    client_box = FancyBboxPatch((1, 7), 3, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='blue', linewidth=2)
    ax.add_patch(client_box)
    ax.text(2.5, 7.75, 'Client Service\n(user-service)', ha='center', va='center', 
            fontsize=11, fontweight='bold')
    
    # Server service
    server_box = FancyBboxPatch((10, 7), 3, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='green', linewidth=2)
    ax.add_patch(server_box)
    ax.text(11.5, 7.75, 'Server Service\n(payment-api)', ha='center', va='center', 
            fontsize=11, fontweight='bold')
    
    # Client certificate
    client_cert_box = FancyBboxPatch((0.5, 5), 4, 1, boxstyle="round,pad=0.1",
                                    facecolor='lightcyan', edgecolor='blue')
    ax.add_patch(client_cert_box)
    ax.text(2.5, 5.5, 'Client Certificate', ha='center', va='center', 
            fontsize=10, fontweight='bold')
    ax.text(2.5, 5.2, 'CN=user-service.internal', ha='center', va='center', fontsize=9)
    
    # Server certificate
    server_cert_box = FancyBboxPatch((9.5, 5), 4, 1, boxstyle="round,pad=0.1",
                                    facecolor='lightgreen', edgecolor='green')
    ax.add_patch(server_cert_box)
    ax.text(11.5, 5.5, 'Server Certificate', ha='center', va='center', 
            fontsize=10, fontweight='bold')
    ax.text(11.5, 5.2, 'CN=payment-api.internal', ha='center', va='center', fontsize=9)
    
    # mTLS handshake arrows
    # Client presents certificate
    client_arrow = patches.FancyArrowPatch((4.2, 7.5), (9.8, 7.5),
                                         arrowstyle='->', mutation_scale=20,
                                         color='blue', linewidth=2)
    ax.add_patch(client_arrow)
    ax.text(7, 7.8, 'Client presents certificate', ha='center', va='center', 
           fontsize=10, color='blue', fontweight='bold')
    
    # Server presents certificate
    server_arrow = patches.FancyArrowPatch((9.8, 7.2), (4.2, 7.2),
                                         arrowstyle='->', mutation_scale=20,
                                         color='green', linewidth=2)
    ax.add_patch(server_arrow)
    ax.text(7, 6.9, 'Server presents certificate', ha='center', va='center', 
           fontsize=10, color='green', fontweight='bold')
    
    # Certificate validation arrows
    client_val_arrow = patches.FancyArrowPatch((2.5, 6.8), (2.5, 6),
                                             arrowstyle='->', mutation_scale=15,
                                             color='blue', linewidth=1.5)
    ax.add_patch(client_val_arrow)
    
    server_val_arrow = patches.FancyArrowPatch((11.5, 6.8), (11.5, 6),
                                             arrowstyle='->', mutation_scale=15,
                                             color='green', linewidth=1.5)
    ax.add_patch(server_val_arrow)
    
    # Mutual authentication result
    auth_box = FancyBboxPatch((5, 3), 4, 1, boxstyle="round,pad=0.1",
                             facecolor='gold', edgecolor='orange', linewidth=2)
    ax.add_patch(auth_box)
    ax.text(7, 3.5, 'Mutual Authentication\nSuccessful', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    
    # Benefits
    ax.text(1, 2, 'mTLS Benefits:', fontsize=12, fontweight='bold')
    benefits = [
        '• Zero-trust security model',
        '• Service-to-service authentication',
        '• Encrypted communication',
        '• Identity verification for both parties',
        '• Protection against impersonation'
    ]
    
    for i, benefit in enumerate(benefits):
        ax.text(1, 1.5 - (i * 0.25), benefit, fontsize=10)
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.3-tls/mtls_authentication.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_tls_security_features_diagram():
    """Create TLS security features diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Title
    ax.text(7, 9.5, 'TLS Security Features', ha='center', va='center',
            fontsize=16, fontweight='bold')
    
    # Security features
    features = [
        {
            'name': 'Perfect Forward Secrecy',
            'description': 'Session keys cannot decrypt past communications',
            'implementation': 'Ephemeral key exchange (ECDHE)',
            'position': (2, 8),
            'color': 'lightblue'
        },
        {
            'name': 'Certificate Pinning',
            'description': 'Prevent man-in-the-middle attacks',
            'implementation': 'Pin certificate or public key',
            'position': (8, 8),
            'color': 'lightgreen'
        },
        {
            'name': 'HSTS',
            'description': 'Force HTTPS connections',
            'implementation': 'Strict-Transport-Security header',
            'position': (2, 6),
            'color': 'lightyellow'
        },
        {
            'name': 'OCSP Stapling',
            'description': 'Real-time certificate validation',
            'implementation': 'Server provides revocation status',
            'position': (8, 6),
            'color': 'lightcoral'
        },
        {
            'name': 'Cipher Suite Security',
            'description': 'Strong encryption algorithms only',
            'implementation': 'Disable weak ciphers (RC4, DES)',
            'position': (2, 4),
            'color': 'lightpink'
        },
        {
            'name': 'TLS 1.3 Improvements',
            'description': 'Enhanced security and performance',
            'implementation': '1-RTT handshake, encrypted handshake',
            'position': (8, 4),
            'color': 'lightsteelblue'
        }
    ]
    
    for feature in features:
        x, y = feature['position']
        
        # Feature box
        feature_box = FancyBboxPatch((x - 1.5, y - 0.8), 3, 1.6, boxstyle="round,pad=0.1",
                                    facecolor=feature['color'], edgecolor='black', linewidth=1)
        ax.add_patch(feature_box)
        
        # Feature name
        ax.text(x, y + 0.3, feature['name'], ha='center', va='center', 
                fontsize=11, fontweight='bold')
        
        # Description
        ax.text(x, y, feature['description'], ha='center', va='center', 
                fontsize=9, style='italic')
        
        # Implementation
        ax.text(x, y - 0.3, feature['implementation'], ha='center', va='center', 
                fontsize=8, family='monospace')
    
    # Attack mitigation
    ax.text(7, 2.5, 'Common Attacks Mitigated by TLS:', fontsize=12, fontweight='bold')
    
    attacks = [
        'Man-in-the-Middle (MITM) - Certificate validation',
        'Eavesdropping - Encryption',
        'Data tampering - Message authentication codes',
        'Replay attacks - Sequence numbers and timestamps',
        'Downgrade attacks - Version negotiation protection'
    ]
    
    for i, attack in enumerate(attacks):
        ax.text(1, 2 - (i * 0.25), f'• {attack}', fontsize=10)
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.3-tls/tls_security_features.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all TLS diagrams"""
    print("Rendering TLS diagrams...")
    
    create_tls_handshake_diagram()
    print("✓ TLS handshake comparison diagram")
    
    create_certificate_chain_diagram()
    print("✓ Certificate chain validation diagram")
    
    create_cipher_suites_diagram()
    print("✓ Cipher suites comparison diagram")
    
    create_mtls_diagram()
    print("✓ Mutual TLS authentication diagram")
    
    create_tls_security_features_diagram()
    print("✓ TLS security features diagram")
    
    print("All TLS diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
