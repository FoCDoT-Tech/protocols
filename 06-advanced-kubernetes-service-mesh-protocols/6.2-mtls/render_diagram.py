#!/usr/bin/env python3
"""
mTLS Architecture Diagram Renderer
Generates visual diagrams for mutual TLS and certificate management
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle, Arrow
import numpy as np

def render_mtls_architecture():
    """Render mTLS service mesh architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Colors
    ca_color = '#E3F2FD'
    control_plane_color = '#F3E5F5'
    data_plane_color = '#E8F5E8'
    cert_color = '#FFF3E0'
    mtls_color = '#FFEBEE'
    
    # Title
    ax.text(8, 11.5, 'Mutual TLS (mTLS) Service Mesh Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Certificate Authority Hierarchy
    ca_box = FancyBboxPatch((1, 9), 4, 2.5, 
                           boxstyle="round,pad=0.1", 
                           facecolor=ca_color, 
                           edgecolor='black', linewidth=2)
    ax.add_patch(ca_box)
    ax.text(3, 10.8, 'Certificate Authority', fontsize=14, fontweight='bold', ha='center')
    
    # CA components
    ca_components = [
        ('Root CA\n(HSM)', 1.8, 10.2),
        ('Intermediate CA\n(Citadel)', 3, 10.2),
        ('Workload CA\n(SPIRE)', 4.2, 10.2)
    ]
    
    for name, x, y in ca_components:
        ca_comp_box = FancyBboxPatch((x-0.5, y-0.4), 1, 0.8, 
                                    boxstyle="round,pad=0.05", 
                                    facecolor='white', 
                                    edgecolor='blue', linewidth=1)
        ax.add_patch(ca_comp_box)
        ax.text(x, y, name, fontsize=9, ha='center', fontweight='bold')
    
    # Control Plane
    control_box = FancyBboxPatch((6, 9), 4, 2.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor=control_plane_color, 
                                edgecolor='black', linewidth=2)
    ax.add_patch(control_box)
    ax.text(8, 10.8, 'Service Mesh Control Plane', fontsize=14, fontweight='bold', ha='center')
    
    # Control plane components
    control_components = [
        ('Citadel\n(Cert Mgmt)', 6.8, 10.2),
        ('Pilot\n(Config)', 8, 10.2),
        ('SPIRE Server\n(Identity)', 9.2, 10.2)
    ]
    
    for name, x, y in control_components:
        control_comp_box = FancyBboxPatch((x-0.5, y-0.4), 1, 0.8, 
                                         boxstyle="round,pad=0.05", 
                                         facecolor='white', 
                                         edgecolor='purple', linewidth=1)
        ax.add_patch(control_comp_box)
        ax.text(x, y, name, fontsize=9, ha='center', fontweight='bold')
    
    # Certificate Distribution
    cert_box = FancyBboxPatch((11, 9), 4, 2.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor=cert_color, 
                             edgecolor='black', linewidth=2)
    ax.add_patch(cert_box)
    ax.text(13, 10.8, 'Certificate Distribution', fontsize=14, fontweight='bold', ha='center')
    
    # Certificate components
    cert_components = [
        ('SDS\n(Secret Discovery)', 11.8, 10.2),
        ('SPIRE Agent\n(Node Agent)', 13, 10.2),
        ('Workload API\n(gRPC)', 14.2, 10.2)
    ]
    
    for name, x, y in cert_components:
        cert_comp_box = FancyBboxPatch((x-0.5, y-0.4), 1, 0.8, 
                                      boxstyle="round,pad=0.05", 
                                      facecolor='white', 
                                      edgecolor='orange', linewidth=1)
        ax.add_patch(cert_comp_box)
        ax.text(x, y, name, fontsize=9, ha='center', fontweight='bold')
    
    # Data Plane Services
    services = [
        ('Service A\nWeb Frontend', 2, 6, 'spiffe://domain/ns/prod/sa/web'),
        ('Service B\nAPI Gateway', 6, 6, 'spiffe://domain/ns/prod/sa/api'),
        ('Service C\nDatabase', 10, 6, 'spiffe://domain/ns/prod/sa/db'),
        ('Service D\nAuth Service', 14, 6, 'spiffe://domain/ns/prod/sa/auth')
    ]
    
    for name, x, y, spiffe_id in services:
        # Service container
        service_box = FancyBboxPatch((x-1.2, y-1.5), 2.4, 3, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor=data_plane_color, 
                                    edgecolor='black', linewidth=1)
        ax.add_patch(service_box)
        
        # Envoy proxy
        envoy_box = FancyBboxPatch((x-1, y+0.5), 2, 0.6, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor='lightblue', 
                                  edgecolor='blue', linewidth=1)
        ax.add_patch(envoy_box)
        ax.text(x, y+0.8, 'Envoy Proxy', fontsize=9, ha='center', fontweight='bold')
        
        # Application
        app_box = FancyBboxPatch((x-1, y-0.3), 2, 0.6, 
                                boxstyle="round,pad=0.05", 
                                facecolor='lightgreen', 
                                edgecolor='green', linewidth=1)
        ax.add_patch(app_box)
        ax.text(x, y, name.split('\n')[1], fontsize=9, ha='center', fontweight='bold')
        
        # Certificate
        cert_box = FancyBboxPatch((x-1, y-1.2), 2, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=cert_color, 
                                 edgecolor='orange', linewidth=1)
        ax.add_patch(cert_box)
        ax.text(x, y-0.9, 'X.509 Certificate', fontsize=8, ha='center', fontweight='bold')
        
        # Service name
        ax.text(x, y+1.7, name.split('\n')[0], fontsize=10, ha='center', fontweight='bold')
        
        # SPIFFE ID
        ax.text(x, y-1.7, spiffe_id.split('/')[-1], fontsize=7, ha='center', style='italic')
    
    # mTLS connections between services
    mtls_connections = [
        (2, 6, 6, 6, 'mTLS'),
        (6, 6, 10, 6, 'mTLS'),
        (10, 6, 14, 6, 'mTLS'),
        (2, 6, 14, 6, 'mTLS')
    ]
    
    for x1, y1, x2, y2, label in mtls_connections:
        if x1 != x2:  # Horizontal connections
            # mTLS arrow
            ax.annotate('', xy=(x2-1.2, y1), xytext=(x1+1.2, y1),
                       arrowprops=dict(arrowstyle='<->', color='red', lw=2))
            
            # Label
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, y1+0.3, label, fontsize=8, ha='center', fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor=mtls_color, alpha=0.7))
        else:  # Diagonal connection
            ax.annotate('', xy=(x2-1, y2-1), xytext=(x1+1, y1+1),
                       arrowprops=dict(arrowstyle='<->', color='red', lw=2, alpha=0.5))
    
    # Certificate distribution arrows
    for _, x, y, _ in services:
        ax.arrow(13, 9, x-13, y-9+1.5, head_width=0.1, head_length=0.1, 
                fc='orange', ec='orange', alpha=0.7)
    
    # Control plane to certificate distribution
    ax.arrow(10, 10.2, 0.8, 0, head_width=0.1, head_length=0.1, fc='purple', ec='purple')
    
    # CA to control plane
    ax.arrow(5, 10.2, 0.8, 0, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    
    # mTLS handshake details
    ax.text(8, 3.5, 'mTLS Handshake Process:', fontsize=12, fontweight='bold', ha='center')
    
    handshake_steps = [
        '1. Client Hello with supported cipher suites',
        '2. Server Hello + Server Certificate',
        '3. Client Certificate Request',
        '4. Client Certificate + Certificate Verify',
        '5. Mutual certificate validation',
        '6. Encrypted application data exchange'
    ]
    
    for i, step in enumerate(handshake_steps):
        ax.text(8, 3 - i*0.3, step, fontsize=9, ha='center')
    
    # Legend
    legend_elements = [
        ('Certificate Authority', ca_color),
        ('Control Plane', control_plane_color),
        ('Data Plane Services', data_plane_color),
        ('Certificate Distribution', cert_color),
        ('mTLS Communication', mtls_color)
    ]
    
    for i, (label, color) in enumerate(legend_elements):
        legend_box = FancyBboxPatch((0.5, 0.5 - i*0.3), 0.3, 0.2, 
                                   boxstyle="round,pad=0.02", 
                                   facecolor=color, 
                                   edgecolor='black', linewidth=0.5)
        ax.add_patch(legend_box)
        ax.text(1, 0.6 - i*0.3, label, fontsize=9, va='center')
    
    plt.tight_layout()
    plt.savefig('mtls_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated mtls_architecture.png")

def render_certificate_lifecycle():
    """Render certificate lifecycle and rotation diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'Certificate Lifecycle and Rotation', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Timeline
    timeline_y = 8
    ax.plot([1, 13], [timeline_y, timeline_y], 'k-', linewidth=2)
    
    # Lifecycle stages
    stages = [
        (2, 'Certificate\nRequest', '#E3F2FD'),
        (4, 'Identity\nVerification', '#F3E5F5'),
        (6, 'Certificate\nIssuance', '#E8F5E8'),
        (8, 'Certificate\nDeployment', '#FFF3E0'),
        (10, 'Certificate\nRotation', '#FFEBEE'),
        (12, 'Certificate\nRevocation', '#F1F8E9')
    ]
    
    for x, label, color in stages:
        # Stage circle
        circle = Circle((x, timeline_y), 0.3, facecolor=color, edgecolor='black', linewidth=1)
        ax.add_patch(circle)
        ax.text(x, timeline_y, str(stages.index((x, label, color)) + 1), 
               fontsize=10, fontweight='bold', ha='center', va='center')
        
        # Stage label
        ax.text(x, timeline_y - 0.8, label, fontsize=10, ha='center', fontweight='bold')
    
    # Detailed process flow
    # SPIRE Server
    spire_box = FancyBboxPatch((1, 5.5), 3, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#E3F2FD', 
                              edgecolor='black', linewidth=1)
    ax.add_patch(spire_box)
    ax.text(2.5, 6.25, 'SPIRE Server\n(Identity Provider)', fontsize=12, fontweight='bold', ha='center')
    
    # SPIRE Agent
    agent_box = FancyBboxPatch((5.5, 5.5), 3, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#F3E5F5', 
                              edgecolor='black', linewidth=1)
    ax.add_patch(agent_box)
    ax.text(7, 6.25, 'SPIRE Agent\n(Node Agent)', fontsize=12, fontweight='bold', ha='center')
    
    # Workload
    workload_box = FancyBboxPatch((10, 5.5), 3, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#E8F5E8', 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(workload_box)
    ax.text(11.5, 6.25, 'Workload\n(Envoy Proxy)', fontsize=12, fontweight='bold', ha='center')
    
    # Flow arrows and messages
    flows = [
        (4, 6.5, 5.5, 6.5, 'Node Attestation\n& Registration', 'right'),
        (8.5, 6.5, 10, 6.5, 'Certificate Request\n(Workload API)', 'right'),
        (10, 6, 8.5, 6, 'X.509 Certificate\n+ Private Key', 'left'),
        (5.5, 5.8, 4, 5.8, 'Certificate Validation\n& Renewal', 'left')
    ]
    
    for x1, y1, x2, y2, label, direction in flows:
        if direction == 'right':
            ax.annotate('', xy=(x2, y1), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', color='blue', lw=2))
            ax.text((x1 + x2) / 2, y1 + 0.2, label, fontsize=9, ha='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='lightblue', alpha=0.7))
        else:
            ax.annotate('', xy=(x2, y1), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', color='green', lw=2))
            ax.text((x1 + x2) / 2, y1 - 0.3, label, fontsize=9, ha='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgreen', alpha=0.7))
    
    # Certificate properties
    ax.text(7, 4.5, 'Certificate Properties:', fontsize=12, fontweight='bold', ha='center')
    
    properties = [
        '• SPIFFE ID: spiffe://trust-domain/path/service-name',
        '• Validity Period: 24-48 hours (short-lived)',
        '• Key Usage: Digital Signature, Key Encipherment',
        '• Extended Key Usage: Client Auth, Server Auth',
        '• Subject Alternative Name: SPIFFE ID URI',
        '• Automatic Rotation: 25% before expiration'
    ]
    
    for i, prop in enumerate(properties):
        ax.text(7, 4 - i*0.3, prop, fontsize=10, ha='center')
    
    # Rotation timeline
    ax.text(7, 1.8, 'Certificate Rotation Timeline:', fontsize=11, fontweight='bold', ha='center')
    
    # Rotation phases
    rotation_phases = [
        (2, 'Active\n(75% lifetime)', '#4CAF50'),
        (5, 'Pre-Rotation\n(25% lifetime)', '#FF9800'),
        (8, 'Rotation\n(New cert issued)', '#2196F3'),
        (11, 'Grace Period\n(Old cert valid)', '#9C27B0')
    ]
    
    for x, label, color in rotation_phases:
        phase_box = FancyBboxPatch((x-0.8, 0.8), 1.6, 0.6, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=color, 
                                  edgecolor='black', linewidth=1, alpha=0.7)
        ax.add_patch(phase_box)
        ax.text(x, 1.1, label, fontsize=9, fontweight='bold', ha='center', color='white')
    
    # Rotation arrows
    for i in range(len(rotation_phases) - 1):
        x1 = rotation_phases[i][0] + 0.8
        x2 = rotation_phases[i + 1][0] - 0.8
        ax.annotate('', xy=(x2, 1.1), xytext=(x1, 1.1),
                   arrowprops=dict(arrowstyle='->', color='black', lw=1))
    
    plt.tight_layout()
    plt.savefig('certificate_lifecycle.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated certificate_lifecycle.png")

def render_mtls_handshake_flow():
    """Render detailed mTLS handshake flow"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(6, 9.5, 'mTLS Handshake Flow', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Client and Server
    client_box = FancyBboxPatch((1, 7.5), 2, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#E3F2FD', 
                               edgecolor='black', linewidth=1)
    ax.add_patch(client_box)
    ax.text(2, 8.25, 'Client\n(Service A)', fontsize=11, fontweight='bold', ha='center')
    
    server_box = FancyBboxPatch((9, 7.5), 2, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#E8F5E8', 
                               edgecolor='black', linewidth=1)
    ax.add_patch(server_box)
    ax.text(10, 8.25, 'Server\n(Service B)', fontsize=11, fontweight='bold', ha='center')
    
    # Handshake steps
    steps = [
        (7.5, 'ClientHello\n(Cipher Suites, Extensions)', 'right'),
        (7, 'ServerHello + Certificate\n+ CertificateRequest', 'left'),
        (6.5, 'Client Certificate\n+ CertificateVerify', 'right'),
        (6, 'Certificate Validation\n(Both Sides)', 'both'),
        (5.5, 'Finished\n(Handshake Complete)', 'both'),
        (5, 'Encrypted Application Data', 'both')
    ]
    
    for y, message, direction in steps:
        if direction == 'right':
            ax.annotate('', xy=(8.5, y), xytext=(3.5, y),
                       arrowprops=dict(arrowstyle='->', color='blue', lw=2))
            ax.text(6, y + 0.1, message, fontsize=9, ha='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='lightblue', alpha=0.7))
        elif direction == 'left':
            ax.annotate('', xy=(3.5, y), xytext=(8.5, y),
                       arrowprops=dict(arrowstyle='->', color='green', lw=2))
            ax.text(6, y + 0.1, message, fontsize=9, ha='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgreen', alpha=0.7))
        else:  # both
            ax.annotate('', xy=(8.5, y), xytext=(3.5, y),
                       arrowprops=dict(arrowstyle='<->', color='red', lw=2))
            ax.text(6, y + 0.1, message, fontsize=9, ha='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='#FFEBEE', alpha=0.7))
    
    # Certificate validation details
    validation_box = FancyBboxPatch((1, 3), 10, 1.5, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='#FFF3E0', 
                                   edgecolor='black', linewidth=1)
    ax.add_patch(validation_box)
    ax.text(6, 4.2, 'Certificate Validation Process', fontsize=12, fontweight='bold', ha='center')
    
    validation_steps = [
        '1. Verify certificate signature against trusted CA',
        '2. Check certificate validity period (not expired)',
        '3. Validate SPIFFE ID in Subject Alternative Name',
        '4. Check certificate revocation status (CRL/OCSP)',
        '5. Verify certificate chain up to root CA'
    ]
    
    for i, step in enumerate(validation_steps):
        ax.text(6, 3.9 - i*0.15, step, fontsize=9, ha='center')
    
    # Security benefits
    benefits_box = FancyBboxPatch((1, 1), 10, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#E8F5E8', 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(benefits_box)
    ax.text(6, 2.2, 'mTLS Security Benefits', fontsize=12, fontweight='bold', ha='center')
    
    benefits = [
        '• Mutual Authentication: Both client and server verify identity',
        '• Zero-Trust Architecture: No implicit trust based on network location',
        '• Encryption in Transit: All communication is encrypted end-to-end',
        '• Service Identity: Cryptographically verified service identities',
        '• Automatic Certificate Management: No manual key distribution'
    ]
    
    for i, benefit in enumerate(benefits):
        ax.text(6, 1.9 - i*0.15, benefit, fontsize=9, ha='center')
    
    plt.tight_layout()
    plt.savefig('mtls_handshake_flow.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated mtls_handshake_flow.png")

def render_all_diagrams():
    """Render all mTLS diagrams"""
    print("Rendering mTLS diagrams...")
    
    render_mtls_architecture()
    render_certificate_lifecycle()
    render_mtls_handshake_flow()
    
    print("All mTLS diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
