#!/usr/bin/env python3
"""
SAML 2.0 Diagram Renderer
Generates visual diagrams for SAML protocol flows, federation scenarios, and security features
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_saml_flow_diagram():
    """Create SAML SSO flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Define positions
    user_pos = (1, 8)
    browser_pos = (3, 8)
    sp_pos = (6, 8)
    idp_pos = (10, 8)
    
    # Draw entities
    entities = [
        (user_pos, "👤 User", "#e1f5fe"),
        (browser_pos, "🌐 Browser", "#e8f5e8"),
        (sp_pos, "📱 Service Provider", "#fff3e0"),
        (idp_pos, "🏢 Identity Provider", "#f3e5f5")
    ]
    
    for pos, label, color in entities:
        box = FancyBboxPatch((pos[0]-0.8, pos[1]-0.4), 1.6, 0.8,
                            boxstyle="round,pad=0.1", 
                            facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(pos[0], pos[1], label, ha='center', va='center', fontsize=10, fontweight='bold')
    
    # SAML flow steps
    steps = [
        (user_pos[0], browser_pos[0], 7.2, "1. Access Resource", "#4CAF50"),
        (browser_pos[0], sp_pos[0], 6.4, "2. Redirect to IdP", "#FF9800"),
        (sp_pos[0], idp_pos[0], 5.6, "3. AuthnRequest", "#2196F3"),
        (idp_pos[0], idp_pos[0]-0.5, 4.8, "4. User Authentication", "#9C27B0"),
        (idp_pos[0], sp_pos[0], 4.0, "5. SAML Response", "#F44336"),
        (sp_pos[0], browser_pos[0], 3.2, "6. Access Granted", "#4CAF50"),
        (browser_pos[0], user_pos[0], 2.4, "7. Resource Delivered", "#607D8B")
    ]
    
    for i, (x1, x2, y, label, color) in enumerate(steps):
        if x1 == x2:  # Self-loop for authentication
            ax.annotate('', xy=(x1+0.5, y), xytext=(x1-0.5, y),
                       arrowprops=dict(arrowstyle='->', color=color, lw=2))
        else:
            ax.annotate('', xy=(x2, y), xytext=(x1, y),
                       arrowprops=dict(arrowstyle='->', color=color, lw=2))
        
        # Add step label
        mid_x = (x1 + x2) / 2 if x1 != x2 else x1
        ax.text(mid_x, y + 0.2, label, ha='center', va='bottom', 
               fontsize=9, color=color, fontweight='bold')
    
    # Add SAML assertion details
    assertion_box = FancyBboxPatch((7, 1), 6, 1.5,
                                  boxstyle="round,pad=0.1",
                                  facecolor="#ffebee", edgecolor='red', linewidth=1.5)
    ax.add_patch(assertion_box)
    
    assertion_text = """SAML Assertion Contains:
• Authentication Statement
• Attribute Statement  
• Digital Signature
• Time Bounds & Audience"""
    
    ax.text(10, 1.75, assertion_text, ha='center', va='center', 
           fontsize=9, fontweight='bold')
    
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.set_title('SAML 2.0 SSO Flow', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.10-saml/saml_flow.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_saml_vs_oauth_diagram():
    """Create SAML vs OAuth comparison diagram"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
    
    # SAML side
    ax1.set_title('SAML 2.0', fontsize=14, fontweight='bold', color='#2196F3')
    
    saml_features = [
        ("🎯 Primary Use", "Enterprise SSO", 8.5),
        ("📄 Format", "XML-based", 7.5),
        ("🔐 Authentication", "Strong assertion-based", 6.5),
        ("👥 Target", "Enterprise users", 5.5),
        ("🔒 Security", "XML signatures & encryption", 4.5),
        ("🏢 Federation", "Cross-domain trust", 3.5),
        ("📋 Attributes", "Rich attribute exchange", 2.5),
        ("⚡ Performance", "Heavier payload", 1.5)
    ]
    
    for feature, desc, y in saml_features:
        ax1.text(0.1, y, feature, fontsize=11, fontweight='bold', color='#1976D2')
        ax1.text(0.1, y-0.3, desc, fontsize=10, color='#424242')
    
    # OAuth side
    ax2.set_title('OAuth 2.0', fontsize=14, fontweight='bold', color='#4CAF50')
    
    oauth_features = [
        ("🎯 Primary Use", "API authorization", 8.5),
        ("📄 Format", "JSON-based tokens", 7.5),
        ("🔐 Authentication", "Token-based access", 6.5),
        ("👥 Target", "Web/mobile apps", 5.5),
        ("🔒 Security", "Bearer tokens + HTTPS", 4.5),
        ("🌐 Scope", "Resource-specific access", 3.5),
        ("📋 Attributes", "Limited user info", 2.5),
        ("⚡ Performance", "Lightweight", 1.5)
    ]
    
    for feature, desc, y in oauth_features:
        ax2.text(0.1, y, feature, fontsize=11, fontweight='bold', color='#388E3C')
        ax2.text(0.1, y-0.3, desc, fontsize=10, color='#424242')
    
    # Add comparison summary
    fig.suptitle('SAML 2.0 vs OAuth 2.0 Comparison', fontsize=16, fontweight='bold', y=0.95)
    
    for ax in [ax1, ax2]:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 9)
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.10-saml/saml_vs_oauth.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_federation_scenarios_diagram():
    """Create SAML federation scenarios diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Central IdP
    idp_pos = (7, 5)
    idp_box = FancyBboxPatch((idp_pos[0]-1.5, idp_pos[1]-0.8), 3, 1.6,
                            boxstyle="round,pad=0.2",
                            facecolor="#f3e5f5", edgecolor='purple', linewidth=2)
    ax.add_patch(idp_box)
    ax.text(idp_pos[0], idp_pos[1], "🏢 Corporate\nIdentity Provider", 
           ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Service Providers
    sps = [
        ((3, 8), "📊 Salesforce", "#e8f5e8"),
        ((11, 8), "📧 Office 365", "#e1f5fe"),
        ((3, 2), "☁️ AWS Console", "#fff3e0"),
        ((11, 2), "📱 Custom App", "#ffebee")
    ]
    
    for pos, label, color in sps:
        sp_box = FancyBboxPatch((pos[0]-1, pos[1]-0.6), 2, 1.2,
                               boxstyle="round,pad=0.1",
                               facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(sp_box)
        ax.text(pos[0], pos[1], label, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        
        # Draw connection to IdP
        ax.annotate('', xy=idp_pos, xytext=pos,
                   arrowprops=dict(arrowstyle='<->', color='#666', lw=2, alpha=0.7))
    
    # Partner IdP
    partner_pos = (1, 5)
    partner_box = FancyBboxPatch((partner_pos[0]-0.8, partner_pos[1]-0.6), 1.6, 1.2,
                                boxstyle="round,pad=0.1",
                                facecolor="#fff8e1", edgecolor='orange', linewidth=2)
    ax.add_patch(partner_box)
    ax.text(partner_pos[0], partner_pos[1], "🤝 Partner\nIdP", 
           ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Trust relationship
    ax.annotate('', xy=idp_pos, xytext=partner_pos,
               arrowprops=dict(arrowstyle='<->', color='orange', lw=3))
    ax.text(4, 5.5, "Trust Relationship", ha='center', va='center',
           fontsize=9, color='orange', fontweight='bold')
    
    # Federation features
    features_box = FancyBboxPatch((0.5, 0.5), 13, 1,
                                 boxstyle="round,pad=0.1",
                                 facecolor="#f5f5f5", edgecolor='gray', linewidth=1)
    ax.add_patch(features_box)
    
    features_text = """🔐 Single Sign-On (SSO)  •  🤝 Cross-Domain Trust  •  📋 Attribute Exchange  •  🚪 Single Logout  •  🔒 Security Assertions"""
    ax.text(7, 1, features_text, ha='center', va='center', 
           fontsize=10, fontweight='bold', color='#333')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_title('SAML 2.0 Federation Architecture', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.10-saml/federation_scenarios.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_saml_security_diagram():
    """Create SAML security features diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Security layers
    layers = [
        (6, 7, "🔐 XML Digital Signatures", "#ffebee", "Assertion integrity & authenticity"),
        (6, 5.5, "🔒 XML Encryption", "#e8f5e8", "Sensitive data protection"),
        (6, 4, "⏰ Time-based Validation", "#e1f5fe", "Assertion validity windows"),
        (6, 2.5, "🎯 Audience Restriction", "#fff3e0", "Intended recipient validation"),
        (6, 1, "🤝 Trust Relationships", "#f3e5f5", "Certificate-based trust")
    ]
    
    for x, y, title, color, desc in layers:
        # Main security feature box
        main_box = FancyBboxPatch((x-4, y-0.4), 8, 0.8,
                                 boxstyle="round,pad=0.1",
                                 facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(main_box)
        ax.text(x, y, title, ha='center', va='center', 
               fontsize=12, fontweight='bold')
        
        # Description box
        desc_box = FancyBboxPatch((x-3.5, y-0.8), 7, 0.3,
                                 boxstyle="round,pad=0.05",
                                 facecolor='white', edgecolor='gray', linewidth=1)
        ax.add_patch(desc_box)
        ax.text(x, y-0.65, desc, ha='center', va='center', 
               fontsize=9, color='#666')
    
    # Security threats and mitigations
    threats_box = FancyBboxPatch((0.5, 8), 11, 0.8,
                                boxstyle="round,pad=0.1",
                                facecolor="#ffcdd2", edgecolor='red', linewidth=2)
    ax.add_patch(threats_box)
    
    threats_text = "🛡️ Protects Against: Man-in-the-Middle • Replay Attacks • Assertion Tampering • Unauthorized Access"
    ax.text(6, 8.4, threats_text, ha='center', va='center', 
           fontsize=11, fontweight='bold', color='#d32f2f')
    
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.set_title('SAML 2.0 Security Features', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.10-saml/saml_security.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_saml_performance_diagram():
    """Create SAML performance characteristics diagram"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Authentication latency comparison
    protocols = ['SAML 2.0', 'OAuth 2.0', 'OpenID Connect', 'Basic Auth']
    latencies = [450, 200, 250, 50]  # milliseconds
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']
    
    bars1 = ax1.bar(protocols, latencies, color=colors, alpha=0.7)
    ax1.set_ylabel('Latency (ms)', fontsize=12)
    ax1.set_title('Authentication Latency', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, 500)
    
    # Add value labels on bars
    for bar, latency in zip(bars1, latencies):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'{latency}ms', ha='center', va='bottom', fontweight='bold')
    
    # Security vs Performance trade-off
    security_scores = [9, 7, 8, 3]
    performance_scores = [6, 9, 8, 10]
    
    for i, (protocol, sec, perf, color) in enumerate(zip(protocols, security_scores, performance_scores, colors)):
        ax2.scatter(perf, sec, s=200, c=color, alpha=0.7, label=protocol)
        ax2.annotate(protocol, (perf, sec), xytext=(5, 5), 
                    textcoords='offset points', fontsize=10)
    
    ax2.set_xlabel('Performance Score', fontsize=12)
    ax2.set_ylabel('Security Score', fontsize=12)
    ax2.set_title('Security vs Performance Trade-off', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 11)
    ax2.set_ylim(0, 10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/focdot/01Projects/LEARN/Protocols/02-web-protocols/2.10-saml/saml_performance.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all SAML diagrams"""
    print("🎨 Rendering SAML 2.0 diagrams...")
    
    diagrams = [
        ("SAML SSO Flow", create_saml_flow_diagram),
        ("SAML vs OAuth Comparison", create_saml_vs_oauth_diagram),
        ("Federation Scenarios", create_federation_scenarios_diagram),
        ("Security Features", create_saml_security_diagram),
        ("Performance Analysis", create_saml_performance_diagram)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All SAML diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
