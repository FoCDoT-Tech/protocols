#!/usr/bin/env python3
"""
Diagram renderer for UDP protocol diagrams
Generates matplotlib-based visualizations from Mermaid diagram files
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
import os

def render_udp_comparison():
    """Render UDP vs TCP comparison and UDP characteristics"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('UDP Protocol Overview', fontsize=16, fontweight='bold')
    
    # UDP vs TCP Comparison
    ax1.set_title('UDP vs TCP Comparison', fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    
    # UDP side
    udp_rect = patches.Rectangle((0.5, 6), 4, 3, linewidth=2, edgecolor='blue', facecolor='lightblue')
    ax1.add_patch(udp_rect)
    ax1.text(2.5, 7.5, 'UDP', ha='center', va='center', fontsize=14, fontweight='bold')
    ax1.text(2.5, 7, 'Connectionless', ha='center', va='center', fontsize=10)
    ax1.text(2.5, 6.5, 'Fast & Lightweight', ha='center', va='center', fontsize=10)
    
    # TCP side
    tcp_rect = patches.Rectangle((5.5, 6), 4, 3, linewidth=2, edgecolor='red', facecolor='lightcoral')
    ax1.add_patch(tcp_rect)
    ax1.text(7.5, 7.5, 'TCP', ha='center', va='center', fontsize=14, fontweight='bold')
    ax1.text(7.5, 7, 'Connection-oriented', ha='center', va='center', fontsize=10)
    ax1.text(7.5, 6.5, 'Reliable & Ordered', ha='center', va='center', fontsize=10)
    
    # Characteristics comparison
    characteristics = [
        ('Latency', 'Low', 'Higher'),
        ('Reliability', 'None', 'Guaranteed'),
        ('Overhead', '8 bytes', '20+ bytes'),
        ('Use Case', 'Real-time', 'File transfer')
    ]
    
    for i, (char, udp_val, tcp_val) in enumerate(characteristics):
        y_pos = 4.5 - i * 0.8
        ax1.text(1, y_pos, char + ':', ha='left', va='center', fontweight='bold')
        ax1.text(2.5, y_pos, udp_val, ha='center', va='center', color='blue')
        ax1.text(7.5, y_pos, tcp_val, ha='center', va='center', color='red')
    
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    
    # UDP Header Structure
    ax2.set_title('UDP Header Structure (8 bytes)', fontweight='bold')
    ax2.set_xlim(0, 32)
    ax2.set_ylim(0, 4)
    
    # Header fields
    fields = [
        ('Source Port', 0, 16, 'lightblue'),
        ('Destination Port', 16, 16, 'lightgreen'),
        ('Length', 0, 16, 'lightyellow'),
        ('Checksum', 16, 16, 'lightcoral')
    ]
    
    for i, (name, start, width, color) in enumerate(fields):
        row = 1 if i < 2 else 0
        x_start = start if i < 2 else start
        y_start = 2 + row
        
        rect = patches.Rectangle((x_start, y_start), width, 1, 
                               linewidth=1, edgecolor='black', facecolor=color)
        ax2.add_patch(rect)
        ax2.text(x_start + width/2, y_start + 0.5, name, 
                ha='center', va='center', fontsize=10, fontweight='bold')
        ax2.text(x_start + width/2, y_start + 0.2, f'{width} bits', 
                ha='center', va='center', fontsize=8)
    
    # Bit markers
    for i in range(0, 33, 8):
        ax2.axvline(x=i, color='gray', linestyle='--', alpha=0.5)
        ax2.text(i, 0.5, str(i), ha='center', va='center', fontsize=8)
    
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    # UDP Use Cases
    ax3.set_title('UDP Use Cases', fontweight='bold')
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)
    
    use_cases = [
        ('DNS Queries', 2, 8.5, 'Fast name resolution'),
        ('Video Streaming', 2, 7, 'Real-time delivery'),
        ('Online Gaming', 2, 5.5, 'Low latency updates'),
        ('VoIP Calls', 2, 4, 'Voice communication'),
        ('DHCP', 2, 2.5, 'Network configuration')
    ]
    
    for name, x, y, desc in use_cases:
        # Use case box
        rect = patches.Rectangle((x-1.5, y-0.4), 3, 0.8, 
                               linewidth=1, edgecolor='blue', facecolor='lightblue')
        ax3.add_patch(rect)
        ax3.text(x, y, name, ha='center', va='center', fontweight='bold')
        
        # Arrow and description
        ax3.arrow(x+1.5, y, 2, 0, head_width=0.2, head_length=0.3, fc='gray', ec='gray')
        ax3.text(x+4.5, y, desc, ha='left', va='center', fontsize=10)
    
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['bottom'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    
    # UDP Packet Flow
    ax4.set_title('UDP Packet Flow', fontweight='bold')
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 10)
    
    # Flow steps
    steps = [
        ('Application\nData', 2, 8),
        ('Add UDP\nHeader', 2, 6),
        ('Add IP\nHeader', 2, 4),
        ('Transmit\nPacket', 2, 2),
        ('No ACK\nRequired', 8, 2)
    ]
    
    for i, (step, x, y) in enumerate(steps):
        if i < 4:
            # Vertical flow
            rect = patches.Rectangle((x-0.8, y-0.5), 1.6, 1, 
                                   linewidth=2, edgecolor='green', facecolor='lightgreen')
            ax4.add_patch(rect)
            ax4.text(x, y, step, ha='center', va='center', fontsize=10, fontweight='bold')
            
            if i < 3:
                ax4.arrow(x, y-0.5, 0, -1, head_width=0.3, head_length=0.2, fc='green', ec='green')
        else:
            # Final step
            rect = patches.Rectangle((x-0.8, y-0.5), 1.6, 1, 
                                   linewidth=2, edgecolor='orange', facecolor='lightyellow')
            ax4.add_patch(rect)
            ax4.text(x, y, step, ha='center', va='center', fontsize=10, fontweight='bold')
            
            # Arrow from transmit to no ACK
            ax4.arrow(3.2, 2, 3.6, 0, head_width=0.3, head_length=0.3, fc='orange', ec='orange')
    
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
    if 'udp' in mermaid_file.lower():
        fig = render_udp_comparison()
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
