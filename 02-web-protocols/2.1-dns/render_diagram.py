#!/usr/bin/env python3
"""
Diagram renderer for DNS protocol diagrams
Generates matplotlib-based visualizations from Mermaid diagram files
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
import os

def render_dns_hierarchy():
    """Render DNS hierarchy and query process"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('DNS Protocol Overview', fontsize=16, fontweight='bold')
    
    # DNS Hierarchy
    ax1.set_title('DNS Hierarchy', fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    
    # Root level
    root_rect = patches.Rectangle((3, 8), 4, 1.5, linewidth=2, edgecolor='red', facecolor='lightcoral')
    ax1.add_patch(root_rect)
    ax1.text(5, 8.75, 'Root Servers\n(.)', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # TLD level
    tld_rect = patches.Rectangle((3, 6), 4, 1.5, linewidth=2, edgecolor='blue', facecolor='lightblue')
    ax1.add_patch(tld_rect)
    ax1.text(5, 6.75, 'TLD Servers\n(.com, .org, .net)', ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Authoritative level
    auth_rect = patches.Rectangle((3, 4), 4, 1.5, linewidth=2, edgecolor='green', facecolor='lightgreen')
    ax1.add_patch(auth_rect)
    ax1.text(5, 4.75, 'Authoritative Servers\n(example.com)', ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Records level
    records_rect = patches.Rectangle((3, 2), 4, 1.5, linewidth=2, edgecolor='orange', facecolor='lightyellow')
    ax1.add_patch(records_rect)
    ax1.text(5, 2.75, 'DNS Records\n(A, AAAA, CNAME, MX)', ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Arrows
    for y in [7.5, 5.5, 3.5]:
        ax1.arrow(5, y, 0, -1, head_width=0.2, head_length=0.2, fc='black', ec='black')
    
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    
    # DNS Query Process
    ax2.set_title('DNS Query Process', fontweight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    
    # Client
    client_rect = patches.Rectangle((0.5, 4), 2, 1.5, linewidth=2, edgecolor='purple', facecolor='lavender')
    ax2.add_patch(client_rect)
    ax2.text(1.5, 4.75, 'Client\nwww.example.com?', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Recursive Resolver
    resolver_rect = patches.Rectangle((4, 4), 2, 1.5, linewidth=2, edgecolor='blue', facecolor='lightblue')
    ax2.add_patch(resolver_rect)
    ax2.text(5, 4.75, 'Recursive\nResolver', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Authoritative Server
    auth_rect = patches.Rectangle((7.5, 4), 2, 1.5, linewidth=2, edgecolor='green', facecolor='lightgreen')
    ax2.add_patch(auth_rect)
    ax2.text(8.5, 4.75, 'Authoritative\nServer', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Query arrows
    ax2.arrow(2.5, 5, 1.3, 0, head_width=0.2, head_length=0.2, fc='blue', ec='blue')
    ax2.text(3.2, 5.5, '1. Query', ha='center', va='center', fontsize=9)
    
    ax2.arrow(6, 5, 1.3, 0, head_width=0.2, head_length=0.2, fc='green', ec='green')
    ax2.text(6.7, 5.5, '2. Lookup', ha='center', va='center', fontsize=9)
    
    # Response arrows
    ax2.arrow(7.5, 4.2, -1.3, 0, head_width=0.2, head_length=0.2, fc='orange', ec='orange')
    ax2.text(6.7, 3.7, '3. Response', ha='center', va='center', fontsize=9)
    
    ax2.arrow(4, 4.2, -1.3, 0, head_width=0.2, head_length=0.2, fc='red', ec='red')
    ax2.text(3.2, 3.7, '4. IP Address', ha='center', va='center', fontsize=9)
    
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    # DNS Record Types
    ax3.set_title('DNS Record Types', fontweight='bold')
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)
    
    records = [
        ('A Record', 'IPv4: 192.0.2.1', 'lightblue', 8.5),
        ('AAAA Record', 'IPv6: 2001:db8::1', 'lightgreen', 7),
        ('CNAME Record', 'Alias: www → example.com', 'lightyellow', 5.5),
        ('MX Record', 'Mail: mail.example.com', 'lightcoral', 4),
        ('NS Record', 'Nameserver: ns1.example.com', 'lightpink', 2.5)
    ]
    
    for record_type, value, color, y in records:
        rect = patches.Rectangle((1, y-0.4), 8, 0.8, linewidth=1, edgecolor='black', facecolor=color)
        ax3.add_patch(rect)
        ax3.text(2, y, record_type, ha='left', va='center', fontsize=11, fontweight='bold')
        ax3.text(6, y, value, ha='left', va='center', fontsize=10)
    
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['bottom'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    
    # DNS Caching Layers
    ax4.set_title('DNS Caching Layers', fontweight='bold')
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 10)
    
    cache_layers = [
        ('Browser Cache', 'lightblue', 8.5, '1-5 min'),
        ('OS Cache', 'lightgreen', 7, '5-30 min'),
        ('ISP Cache', 'lightyellow', 5.5, '1-24 hours'),
        ('Recursive Resolver', 'lightcoral', 4, 'TTL based'),
        ('Authoritative Server', 'lightpink', 2.5, 'Source of truth')
    ]
    
    for i, (layer, color, y, ttl) in enumerate(cache_layers):
        rect = patches.Rectangle((1, y-0.4), 6, 0.8, linewidth=1, edgecolor='black', facecolor=color)
        ax4.add_patch(rect)
        ax4.text(1.5, y, layer, ha='left', va='center', fontsize=11, fontweight='bold')
        ax4.text(7.5, y, ttl, ha='center', va='center', fontsize=9)
        
        # Arrows between layers
        if i < len(cache_layers) - 1:
            ax4.arrow(4, y-0.4, 0, -0.7, head_width=0.2, head_length=0.1, fc='gray', ec='gray')
    
    ax4.text(8.5, 9, 'Cache TTL', ha='center', va='center', fontsize=10, fontweight='bold')
    
    ax4.set_xticks([])
    ax4.set_yticks([])
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['bottom'].set_visible(False)
    ax4.spines['left'].set_visible(False)
    
    plt.tight_layout()
    return fig

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 render_diagram.py <mermaid_file>")
        sys.exit(1)
    
    mermaid_file = sys.argv[1]
    
    if not os.path.exists(mermaid_file):
        print(f"Error: File {mermaid_file} not found")
        sys.exit(1)
    
    # Determine diagram type based on filename
    if 'dns' in mermaid_file.lower():
        fig = render_dns_hierarchy()
    else:
        print(f"Unknown diagram type for file: {mermaid_file}")
        sys.exit(1)
    
    # Save the diagram
    output_file = mermaid_file.replace('.mmd', '.png')
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"Generated diagram: {output_file}")

if __name__ == "__main__":
    main()
