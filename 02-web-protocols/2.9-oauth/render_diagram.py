#!/usr/bin/env python3
"""
OAuth 2.0 Protocol Diagram Renderer
Generates visual diagrams for OAuth concepts using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Arrow
import numpy as np

def create_oauth_flow_diagram():
    """Create OAuth 2.0 authorization flow diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('OAuth 2.0 Authorization Code Flow', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # Actors
    client_box = FancyBboxPatch((1, 9), 2.5, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax.add_patch(client_box)
    ax.text(2.25, 9.75, 'OAuth Client\n(Application)', ha='center', va='center', fontweight='bold')
    
    user_box = FancyBboxPatch((6, 9), 2.5, 1.5, boxstyle="round,pad=0.1",
                             facecolor='lightgreen', edgecolor='black')
    ax.add_patch(user_box)
    ax.text(7.25, 9.75, 'Resource Owner\n(User)', ha='center', va='center', fontweight='bold')
    
    auth_server_box = FancyBboxPatch((10.5, 9), 2.5, 1.5, boxstyle="round,pad=0.1",
                                    facecolor='lightcoral', edgecolor='black')
    ax.add_patch(auth_server_box)
    ax.text(11.75, 9.75, 'Authorization\nServer', ha='center', va='center', fontweight='bold')
    
    resource_server_box = FancyBboxPatch((6, 1), 2.5, 1.5, boxstyle="round,pad=0.1",
                                        facecolor='lightyellow', edgecolor='black')
    ax.add_patch(resource_server_box)
    ax.text(7.25, 1.75, 'Resource Server\n(API)', ha='center', va='center', fontweight='bold')
    
    # Flow steps
    steps = [
        {'from': (2.25, 8.5), 'to': (7.25, 8.5), 'label': '1. Authorization Request', 'color': 'blue'},
        {'from': (7.25, 8), 'to': (11.75, 8), 'label': '2. User Authorization', 'color': 'green'},
        {'from': (11.75, 7.5), 'to': (2.25, 7.5), 'label': '3. Authorization Code', 'color': 'red'},
        {'from': (2.25, 7), 'to': (11.75, 7), 'label': '4. Access Token Request', 'color': 'blue'},
        {'from': (11.75, 6.5), 'to': (2.25, 6.5), 'label': '5. Access Token', 'color': 'red'},
        {'from': (2.25, 6), 'to': (7.25, 3), 'label': '6. API Request + Token', 'color': 'blue'},
        {'from': (7.25, 2.5), 'to': (2.25, 5.5), 'label': '7. Protected Resource', 'color': 'green'}
    ]
    
    for i, step in enumerate(steps):
        if i < 5:  # Horizontal arrows
            ax.arrow(step['from'][0], step['from'][1], 
                    step['to'][0] - step['from'][0], 0,
                    head_width=0.15, head_length=0.3, 
                    fc=step['color'], ec=step['color'], alpha=0.7)
        else:  # Diagonal arrows
            dx = step['to'][0] - step['from'][0]
            dy = step['to'][1] - step['from'][1]
            ax.arrow(step['from'][0], step['from'][1], dx, dy,
                    head_width=0.15, head_length=0.3,
                    fc=step['color'], ec=step['color'], alpha=0.7)
        
        # Label positioning
        if i < 5:
            label_x = (step['from'][0] + step['to'][0]) / 2
            label_y = step['from'][1] + 0.3
        else:
            label_x = (step['from'][0] + step['to'][0]) / 2
            label_y = (step['from'][1] + step['to'][1]) / 2 + 0.5
        
        ax.text(label_x, label_y, step['label'], ha='center', va='center',
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8),
               fontsize=9)
    
    # Security features
    security_box = FancyBboxPatch((1, 3.5), 4, 1.5, boxstyle="round,pad=0.1",
                                 facecolor='lightcyan', edgecolor='black')
    ax.add_patch(security_box)
    ax.text(3, 4.25, 'Security Features:\n• HTTPS Only • State Parameter\n• PKCE • Short-lived Tokens',
           ha='center', va='center', fontsize=10)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('oauth_flow.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_oauth_grant_types():
    """Create OAuth grant types comparison diagram"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('OAuth 2.0 Grant Types', fontsize=16, fontweight='bold')
    
    # Authorization Code Flow
    ax1.set_title('Authorization Code Flow', fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 8)
    
    # Client and Server
    client_box = FancyBboxPatch((1, 6), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax1.add_patch(client_box)
    ax1.text(2, 6.5, 'Client', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((7, 6), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax1.add_patch(server_box)
    ax1.text(8, 6.5, 'Auth Server', ha='center', va='center', fontweight='bold')
    
    # Flow arrows
    ax1.arrow(3, 6.3, 3.5, 0, head_width=0.1, head_length=0.2, fc='blue', ec='blue')
    ax1.text(5, 6.6, 'Auth Request', ha='center', va='center', fontsize=9)
    
    ax1.arrow(7, 6.7, -3.5, 0, head_width=0.1, head_length=0.2, fc='red', ec='red')
    ax1.text(5, 7, 'Auth Code', ha='center', va='center', fontsize=9)
    
    ax1.arrow(3, 5.7, 3.5, 0, head_width=0.1, head_length=0.2, fc='blue', ec='blue')
    ax1.text(5, 5.4, 'Token Request', ha='center', va='center', fontsize=9)
    
    ax1.arrow(7, 5.3, -3.5, 0, head_width=0.1, head_length=0.2, fc='green', ec='green')
    ax1.text(5, 5, 'Access Token', ha='center', va='center', fontsize=9)
    
    ax1.text(5, 3, 'Use Case: Web Applications\nSecurity: High\nClient Type: Confidential',
            ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcyan'))
    
    # Client Credentials Flow
    ax2.set_title('Client Credentials Flow', fontweight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 8)
    
    service_box = FancyBboxPatch((1, 6), 2, 1, boxstyle="round,pad=0.1",
                                facecolor='lightcoral', edgecolor='black')
    ax2.add_patch(service_box)
    ax2.text(2, 6.5, 'Service', ha='center', va='center', fontweight='bold')
    
    auth_box = FancyBboxPatch((7, 6), 2, 1, boxstyle="round,pad=0.1",
                             facecolor='lightgreen', edgecolor='black')
    ax2.add_patch(auth_box)
    ax2.text(8, 6.5, 'Auth Server', ha='center', va='center', fontweight='bold')
    
    ax2.arrow(3, 6.5, 3.5, 0, head_width=0.1, head_length=0.2, fc='blue', ec='blue')
    ax2.text(5, 6.8, 'Client Credentials', ha='center', va='center', fontsize=9)
    
    ax2.arrow(7, 6.2, -3.5, 0, head_width=0.1, head_length=0.2, fc='green', ec='green')
    ax2.text(5, 5.9, 'Access Token', ha='center', va='center', fontsize=9)
    
    ax2.text(5, 3, 'Use Case: Service-to-Service\nSecurity: High\nClient Type: Confidential',
            ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcyan'))
    
    # PKCE Flow
    ax3.set_title('PKCE Flow (Enhanced Security)', fontweight='bold')
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 8)
    
    mobile_box = FancyBboxPatch((1, 6), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightyellow', edgecolor='black')
    ax3.add_patch(mobile_box)
    ax3.text(2, 6.5, 'Mobile App', ha='center', va='center', fontweight='bold')
    
    pkce_server_box = FancyBboxPatch((7, 6), 2, 1, boxstyle="round,pad=0.1",
                                    facecolor='lightgreen', edgecolor='black')
    ax3.add_patch(pkce_server_box)
    ax3.text(8, 6.5, 'Auth Server', ha='center', va='center', fontweight='bold')
    
    ax3.arrow(3, 6.3, 3.5, 0, head_width=0.1, head_length=0.2, fc='purple', ec='purple')
    ax3.text(5, 6.6, 'Auth + Challenge', ha='center', va='center', fontsize=9)
    
    ax3.arrow(7, 6.7, -3.5, 0, head_width=0.1, head_length=0.2, fc='red', ec='red')
    ax3.text(5, 7, 'Auth Code', ha='center', va='center', fontsize=9)
    
    ax3.arrow(3, 5.7, 3.5, 0, head_width=0.1, head_length=0.2, fc='purple', ec='purple')
    ax3.text(5, 5.4, 'Token + Verifier', ha='center', va='center', fontsize=9)
    
    ax3.arrow(7, 5.3, -3.5, 0, head_width=0.1, head_length=0.2, fc='green', ec='green')
    ax3.text(5, 5, 'Access Token', ha='center', va='center', fontsize=9)
    
    ax3.text(5, 3, 'Use Case: Mobile/SPA\nSecurity: Very High\nClient Type: Public',
            ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcyan'))
    
    # Refresh Token Flow
    ax4.set_title('Refresh Token Flow', fontweight='bold')
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 8)
    
    app_box = FancyBboxPatch((1, 6), 2, 1, boxstyle="round,pad=0.1",
                            facecolor='lightblue', edgecolor='black')
    ax4.add_patch(app_box)
    ax4.text(2, 6.5, 'Application', ha='center', va='center', fontweight='bold')
    
    refresh_server_box = FancyBboxPatch((7, 6), 2, 1, boxstyle="round,pad=0.1",
                                       facecolor='lightgreen', edgecolor='black')
    ax4.add_patch(refresh_server_box)
    ax4.text(8, 6.5, 'Auth Server', ha='center', va='center', fontweight='bold')
    
    ax4.arrow(3, 6.5, 3.5, 0, head_width=0.1, head_length=0.2, fc='orange', ec='orange')
    ax4.text(5, 6.8, 'Refresh Token', ha='center', va='center', fontsize=9)
    
    ax4.arrow(7, 6.2, -3.5, 0, head_width=0.1, head_length=0.2, fc='green', ec='green')
    ax4.text(5, 5.9, 'New Access Token', ha='center', va='center', fontsize=9)
    
    ax4.text(5, 3, 'Use Case: Token Renewal\nSecurity: High\nBenefit: Seamless UX',
            ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcyan'))
    
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('oauth_grant_types.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_oauth_security_diagram():
    """Create OAuth security threats and mitigations diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('OAuth 2.0 Security Threats and Mitigations', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # Threats (left side)
    threats = [
        {'name': 'Authorization Code\nInterception', 'pos': (2, 9), 'color': 'lightcoral'},
        {'name': 'CSRF\nAttacks', 'pos': (2, 7), 'color': 'lightcoral'},
        {'name': 'Token\nLeakage', 'pos': (2, 5), 'color': 'lightcoral'},
        {'name': 'Scope\nEscalation', 'pos': (2, 3), 'color': 'lightcoral'}
    ]
    
    # Mitigations (right side)
    mitigations = [
        {'name': 'PKCE\nProtection', 'pos': (12, 9), 'color': 'lightgreen'},
        {'name': 'State Parameter\nValidation', 'pos': (12, 7), 'color': 'lightgreen'},
        {'name': 'Secure Token\nStorage', 'pos': (12, 5), 'color': 'lightgreen'},
        {'name': 'Scope\nValidation', 'pos': (12, 3), 'color': 'lightgreen'}
    ]
    
    # Draw threats
    for threat in threats:
        box = FancyBboxPatch((threat['pos'][0]-1, threat['pos'][1]-0.5), 2, 1, 
                            boxstyle="round,pad=0.1", facecolor=threat['color'], edgecolor='black')
        ax.add_patch(box)
        ax.text(threat['pos'][0], threat['pos'][1], threat['name'], 
               ha='center', va='center', fontweight='bold')
    
    # Draw mitigations
    for mitigation in mitigations:
        box = FancyBboxPatch((mitigation['pos'][0]-1, mitigation['pos'][1]-0.5), 2, 1,
                            boxstyle="round,pad=0.1", facecolor=mitigation['color'], edgecolor='black')
        ax.add_patch(box)
        ax.text(mitigation['pos'][0], mitigation['pos'][1], mitigation['name'],
               ha='center', va='center', fontweight='bold')
    
    # Draw arrows from threats to mitigations
    for i, (threat, mitigation) in enumerate(zip(threats, mitigations)):
        ax.arrow(threat['pos'][0]+1, threat['pos'][1], 
                mitigation['pos'][0]-threat['pos'][0]-2, 0,
                head_width=0.15, head_length=0.3, fc='blue', ec='blue', alpha=0.6)
    
    # Central security principles
    security_box = FancyBboxPatch((5.5, 5), 3, 2, boxstyle="round,pad=0.1",
                                 facecolor='lightyellow', edgecolor='black', linewidth=2)
    ax.add_patch(security_box)
    ax.text(7, 6, 'OAuth Security\nPrinciples', ha='center', va='center', 
           fontweight='bold', fontsize=12)
    
    # Security principles
    principles = [
        'HTTPS Only',
        'Principle of Least Privilege',
        'Defense in Depth',
        'Regular Security Audits'
    ]
    
    for i, principle in enumerate(principles):
        ax.text(7, 1.5 - i*0.3, f'• {principle}', ha='center', va='center', fontsize=10)
    
    # Labels
    ax.text(2, 10.5, 'THREATS', ha='center', va='center', fontweight='bold', 
           fontsize=14, color='red')
    ax.text(12, 10.5, 'MITIGATIONS', ha='center', va='center', fontweight='bold',
           fontsize=14, color='green')
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('oauth_security.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_oauth_performance_chart():
    """Create OAuth performance metrics chart"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('OAuth 2.0 Performance Analysis', fontsize=16, fontweight='bold')
    
    # Authorization Flow Latency
    ax1.set_title('Authorization Flow Latency')
    flows = ['Auth Code', 'PKCE', 'Client Creds', 'Refresh']
    latencies = [450, 480, 120, 200]  # milliseconds
    
    bars = ax1.bar(flows, latencies, color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow'])
    ax1.set_ylabel('Latency (ms)')
    ax1.grid(True, alpha=0.3, axis='y')
    
    for bar, latency in zip(bars, latencies):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'{latency}ms', ha='center', va='bottom', fontweight='bold')
    
    # Token Validation Performance
    ax2.set_title('Token Validation Performance')
    validation_types = ['JWT Local', 'Introspection', 'Database', 'Cache']
    validation_times = [2, 45, 25, 8]  # milliseconds
    
    bars = ax2.bar(validation_types, validation_times, 
                  color=['lightgreen', 'lightcoral', 'lightyellow', 'lightblue'])
    ax2.set_ylabel('Validation Time (ms)')
    ax2.grid(True, alpha=0.3, axis='y')
    
    for bar, time in zip(bars, validation_times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{time}ms', ha='center', va='bottom', fontweight='bold')
    
    # Security Score Comparison
    ax3.set_title('Security Score by Flow Type')
    security_flows = ['Basic Auth', 'OAuth Implicit', 'OAuth Auth Code', 'OAuth + PKCE']
    security_scores = [30, 60, 85, 95]  # out of 100
    
    bars = ax3.bar(security_flows, security_scores, 
                  color=['red', 'orange', 'lightgreen', 'green'])
    ax3.set_ylabel('Security Score (0-100)')
    ax3.set_ylim(0, 100)
    ax3.grid(True, alpha=0.3, axis='y')
    
    for bar, score in zip(bars, security_scores):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{score}', ha='center', va='bottom', fontweight='bold')
    
    # OAuth Adoption Metrics
    ax4.set_title('OAuth Implementation Metrics')
    metrics = ['HTTPS Usage', 'PKCE Adoption', 'State Param', 'Token Refresh']
    percentages = [98, 75, 85, 90]  # percentages
    
    bars = ax4.bar(metrics, percentages, 
                  color=['lightblue', 'lightgreen', 'lightyellow', 'lightcoral'])
    ax4.set_ylabel('Adoption Rate (%)')
    ax4.set_ylim(0, 100)
    ax4.grid(True, alpha=0.3, axis='y')
    
    for bar, percentage in zip(bars, percentages):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{percentage}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('oauth_performance_chart.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Generating OAuth 2.0 protocol diagrams...")
    
    create_oauth_flow_diagram()
    print("✓ OAuth authorization flow diagram created")
    
    create_oauth_grant_types()
    print("✓ OAuth grant types diagram created")
    
    create_oauth_security_diagram()
    print("✓ OAuth security diagram created")
    
    create_oauth_performance_chart()
    print("✓ OAuth performance chart created")
    
    print("\nAll OAuth diagrams generated successfully!")
    print("Files created:")
    print("  - oauth_flow.png")
    print("  - oauth_grant_types.png")
    print("  - oauth_security.png")
    print("  - oauth_performance_chart.png")
