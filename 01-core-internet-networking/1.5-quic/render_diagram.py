#!/usr/bin/env python3
"""
Diagram renderer for QUIC protocol diagrams
Generates matplotlib-based visualizations from Mermaid diagram files
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
import os

def render_quic_architecture():
    """Render QUIC architecture and performance comparison"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('QUIC Protocol Architecture', fontsize=16, fontweight='bold')
    
    # QUIC vs TCP+TLS Architecture
    ax1.set_title('QUIC vs TCP+TLS Architecture', fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    
    # QUIC side
    quic_rect = patches.Rectangle((0.5, 6), 4, 3, linewidth=2, edgecolor='blue', facecolor='lightblue')
    ax1.add_patch(quic_rect)
    ax1.text(2.5, 7.5, 'QUIC', ha='center', va='center', fontsize=14, fontweight='bold')
    ax1.text(2.5, 7, 'Transport + Security', ha='center', va='center', fontsize=10)
    ax1.text(2.5, 6.5, '1-RTT Handshake', ha='center', va='center', fontsize=10)
    
    # TCP+TLS side
    tcp_tls_rect = patches.Rectangle((5.5, 6), 4, 3, linewidth=2, edgecolor='red', facecolor='lightcoral')
    ax1.add_patch(tcp_tls_rect)
    ax1.text(7.5, 7.5, 'TCP + TLS', ha='center', va='center', fontsize=14, fontweight='bold')
    ax1.text(7.5, 7, 'Layered Protocols', ha='center', va='center', fontsize=10)
    ax1.text(7.5, 6.5, '3-RTT Handshake', ha='center', va='center', fontsize=10)
    
    # Performance comparison
    perf_data = [
        ('Handshake Time', '50ms', '150ms'),
        ('Head-of-Line Block', 'No', 'Yes'),
        ('Connection Migration', 'Yes', 'No'),
        ('Built-in Encryption', 'Yes', 'Optional')
    ]
    
    for i, (metric, quic_val, tcp_val) in enumerate(perf_data):
        y_pos = 4.5 - i * 0.8
        ax1.text(1, y_pos, metric + ':', ha='left', va='center', fontweight='bold')
        ax1.text(2.5, y_pos, quic_val, ha='center', va='center', color='blue')
        ax1.text(7.5, y_pos, tcp_val, ha='center', va='center', color='red')
    
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    
    # QUIC Stream Multiplexing
    ax2.set_title('QUIC Stream Multiplexing', fontweight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    
    # Connection box
    conn_rect = patches.Rectangle((1, 8), 8, 1.5, linewidth=2, edgecolor='green', facecolor='lightgreen')
    ax2.add_patch(conn_rect)
    ax2.text(5, 8.75, 'QUIC Connection', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Streams
    streams = [
        ('Stream 0: Control', 2, 6.5, 'orange'),
        ('Stream 4: Video', 2, 5, 'red'),
        ('Stream 8: Audio', 2, 3.5, 'blue'),
        ('Stream 12: Chat', 2, 2, 'purple')
    ]
    
    for stream_name, x, y, color in streams:
        rect = patches.Rectangle((x-0.5, y-0.3), 6, 0.6, 
                               linewidth=1, edgecolor=color, facecolor=color, alpha=0.3)
        ax2.add_patch(rect)
        ax2.text(x, y, stream_name, ha='left', va='center', fontsize=10, fontweight='bold')
        
        # Arrow from connection
        ax2.arrow(5, 8, 0, y-7.5, head_width=0.2, head_length=0.2, fc=color, ec=color)
    
    ax2.text(8.5, 4, 'Independent\nFlow Control', ha='center', va='center', 
             fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow'))
    
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    # QUIC Connection Migration
    ax3.set_title('QUIC Connection Migration', fontweight='bold')
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)
    
    # Client networks
    wifi_rect = patches.Rectangle((1, 7), 3, 1.5, linewidth=2, edgecolor='blue', facecolor='lightblue')
    ax3.add_patch(wifi_rect)
    ax3.text(2.5, 7.75, 'WiFi\n192.168.1.100', ha='center', va='center', fontsize=10, fontweight='bold')
    
    cellular_rect = patches.Rectangle((1, 4.5), 3, 1.5, linewidth=2, edgecolor='green', facecolor='lightgreen')
    ax3.add_patch(cellular_rect)
    ax3.text(2.5, 5.25, 'Cellular\n10.0.0.50', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Connection ID
    conn_id_rect = patches.Rectangle((5, 6), 2, 1, linewidth=2, edgecolor='orange', facecolor='lightyellow')
    ax3.add_patch(conn_id_rect)
    ax3.text(6, 6.5, 'Connection ID\nABC123', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Server
    server_rect = patches.Rectangle((8, 6), 1.5, 1, linewidth=2, edgecolor='red', facecolor='lightcoral')
    ax3.add_patch(server_rect)
    ax3.text(8.75, 6.5, 'Server\n203.0.113.1', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Arrows
    ax3.arrow(4, 7.75, 1, -1, head_width=0.15, head_length=0.15, fc='blue', ec='blue')
    ax3.arrow(4, 5.25, 1, 1, head_width=0.15, head_length=0.15, fc='green', ec='green')
    ax3.arrow(7, 6.5, 1, 0, head_width=0.15, head_length=0.15, fc='orange', ec='orange')
    
    ax3.text(2.5, 2.5, 'Seamless Migration\nSame Connection ID', ha='center', va='center', 
             fontsize=11, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow'))
    
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['bottom'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    
    # QUIC Packet Structure
    ax4.set_title('QUIC Packet Structure', fontweight='bold')
    ax4.set_xlim(0, 32)
    ax4.set_ylim(0, 8)
    
    # Packet header fields
    fields = [
        ('Header Form\n1 bit', 0, 1, 'lightblue'),
        ('Fixed Bit\n1 bit', 1, 1, 'lightgreen'),
        ('Packet Type\n2 bits', 2, 2, 'lightyellow'),
        ('Connection ID Len\n4 bits', 4, 4, 'lightcoral'),
        ('Version\n32 bits', 8, 24, 'lightpink')
    ]
    
    y_start = 6
    for name, start, width, color in fields:
        rect = patches.Rectangle((start, y_start), width, 1, 
                               linewidth=1, edgecolor='black', facecolor=color)
        ax4.add_patch(rect)
        ax4.text(start + width/2, y_start + 0.5, name, 
                ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Connection ID and Packet Number (variable length)
    var_fields = [
        ('Connection ID (Variable)', 0, 16, 'lightsteelblue'),
        ('Packet Number (Variable)', 16, 16, 'lightgray')
    ]
    
    y_start = 4.5
    for name, start, width, color in var_fields:
        rect = patches.Rectangle((start, y_start), width, 1, 
                               linewidth=1, edgecolor='black', facecolor=color)
        ax4.add_patch(rect)
        ax4.text(start + width/2, y_start + 0.5, name, 
                ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Payload
    payload_rect = patches.Rectangle((0, 2.5), 32, 1.5, 
                                   linewidth=2, edgecolor='purple', facecolor='lavender')
    ax4.add_patch(payload_rect)
    ax4.text(16, 3.25, 'Encrypted Payload + Authentication Tag', 
            ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Bit markers
    for i in range(0, 33, 4):
        ax4.axvline(x=i, color='gray', linestyle='--', alpha=0.5)
        ax4.text(i, 1, str(i), ha='center', va='center', fontsize=8)
    
    ax4.text(16, 0.5, 'Bit Position', ha='center', va='center', fontsize=10, fontweight='bold')
    
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
    if 'quic' in mermaid_file.lower():
        fig = render_quic_architecture()
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
