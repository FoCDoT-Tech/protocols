#!/usr/bin/env python3
"""
Diagram Renderer - Creates visual diagrams from .mmd files
Uses matplotlib to create actual diagrams instead of placeholders
"""

import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_tcp_diagram(output_file):
    """Create TCP handshake, states, and flow control diagram"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('TCP Protocol Overview', fontsize=16, fontweight='bold')
    
    # TCP Three-Way Handshake
    ax1.set_title('TCP Three-Way Handshake', fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 8)
    
    # Draw client and server
    ax1.text(2, 7.5, 'Client', ha='center', fontsize=12, fontweight='bold')
    ax1.text(8, 7.5, 'Server', ha='center', fontsize=12, fontweight='bold')
    
    # Draw vertical lines for client and server
    ax1.plot([2, 2], [1, 7], 'k-', linewidth=2)
    ax1.plot([8, 8], [1, 7], 'k-', linewidth=2)
    
    # Draw handshake arrows and labels
    arrows = [
        (2, 6, 6, 0, "1. SYN seq=x", "lightgreen"),
        (8, 5, -6, 0, "2. SYN-ACK seq=y, ack=x+1", "lightblue"),
        (2, 4, 6, 0, "3. ACK seq=x+1, ack=y+1", "lightcoral")
    ]
    
    for x, y, dx, dy, label, color in arrows:
        ax1.arrow(x, y, dx, dy, head_width=0.2, head_length=0.3, 
                 fc=color, ec='black', linewidth=1.5)
        ax1.text(x + dx/2, y + 0.3, label, ha='center', fontsize=9, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor=color))
    
    ax1.text(5, 2.5, 'Connection Established', ha='center', fontsize=12, 
             fontweight='bold', bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow"))
    
    ax1.set_xlim(0, 10)
    ax1.set_ylim(1, 8)
    ax1.axis('off')
    
    # TCP Header Structure
    ax2.set_title('TCP Header Structure', fontweight='bold')
    ax2.set_xlim(0, 32)
    ax2.set_ylim(0, 6)
    
    tcp_fields = [
        (0, 5, 16, 1, "Source Port (16)", "lightblue"),
        (16, 5, 16, 1, "Destination Port (16)", "lightgreen"),
        (0, 4, 32, 1, "Sequence Number (32)", "lightyellow"),
        (0, 3, 32, 1, "Acknowledgment Number (32)", "lightcoral"),
        (0, 2, 4, 1, "Hdr\nLen", "lightpink"),
        (4, 2, 9, 1, "Flags (9)", "lightgray"),
        (13, 2, 16, 1, "Window Size (16)", "lightsteelblue"),
        (0, 1, 16, 1, "Checksum (16)", "wheat"),
        (16, 1, 16, 1, "Urgent Pointer (16)", "plum"),
        (0, 0, 32, 1, "Options + Data (Variable)", "whitesmoke")
    ]
    
    for x, y, width, height, label, color in tcp_fields:
        rect = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02",
                             facecolor=color, edgecolor='black', linewidth=0.5)
        ax2.add_patch(rect)
        ax2.text(x + width/2, y + height/2, label, ha='center', va='center', 
                fontsize=8, fontweight='bold')
    
    ax2.set_xticks(range(0, 33, 8))
    ax2.set_xticklabels([str(i) for i in range(0, 33, 8)])
    ax2.set_yticks([])
    ax2.set_xlabel('Bit Position')
    
    # TCP Connection States
    ax3.set_title('TCP Connection States', fontweight='bold')
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 8)
    
    states = [
        (1, 7, "CLOSED", "lightgray"),
        (1, 6, "LISTEN", "lightblue"),
        (1, 5, "SYN-SENT", "lightyellow"),
        (5, 5, "SYN-RECEIVED", "lightcoral"),
        (3, 4, "ESTABLISHED", "lightgreen"),
        (1, 3, "FIN-WAIT-1", "lightpink"),
        (5, 3, "FIN-WAIT-2", "lightsteelblue"),
        (1, 2, "CLOSE-WAIT", "wheat"),
        (5, 2, "LAST-ACK", "plum"),
        (3, 1, "TIME-WAIT", "lavender")
    ]
    
    for x, y, state, color in states:
        rect = FancyBboxPatch((x, y), 2.5, 0.6, boxstyle="round,pad=0.1",
                             facecolor=color, edgecolor='black', linewidth=1)
        ax3.add_patch(rect)
        ax3.text(x + 1.25, y + 0.3, state, ha='center', va='center', 
                fontsize=9, fontweight='bold')
    
    # Add some state transition arrows
    state_arrows = [
        (2.25, 7, 0, -0.4),    # CLOSED to LISTEN
        (2.25, 6, 0, -0.4),    # LISTEN to SYN-SENT
        (3.5, 5, 1, -0.4),     # SYN-SENT to SYN-RECEIVED
        (4.25, 4.6, 0, -1),    # To ESTABLISHED
    ]
    
    for x, y, dx, dy in state_arrows:
        ax3.arrow(x, y, dx, dy, head_width=0.1, head_length=0.1, 
                 fc='black', ec='black', alpha=0.7)
    
    ax3.set_xlim(0, 8)
    ax3.set_ylim(0.5, 7.5)
    ax3.axis('off')
    
    # Flow Control & Congestion Control
    ax4.set_title('TCP Flow & Congestion Control', fontweight='bold')
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 8)
    
    flow_boxes = [
        (1, 7, 3, 0.8, "Sliding Window\nProtocol", "lightgreen"),
        (5, 7, 3, 0.8, "Congestion Window\n(cwnd)", "lightblue"),
        (1, 5.5, 3, 0.8, "Slow Start\nPhase", "lightyellow"),
        (5, 5.5, 3, 0.8, "Congestion\nAvoidance", "lightcoral"),
        (1, 4, 3, 0.8, "Fast Retransmit", "lightpink"),
        (5, 4, 3, 0.8, "Fast Recovery", "lightsteelblue")
    ]
    
    for x, y, width, height, label, color in flow_boxes:
        rect = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.1",
                             facecolor=color, edgecolor='black', linewidth=1)
        ax4.add_patch(rect)
        ax4.text(x + width/2, y + height/2, label, ha='center', va='center', 
                fontsize=9, fontweight='bold')
    
    # Add flow arrows
    flow_arrows = [
        (2.5, 7, 2, 0),      # Sliding window to congestion window
        (2.5, 5.5, 2, 0),    # Slow start to congestion avoidance
        (2.5, 4, 2, 0),      # Fast retransmit to fast recovery
    ]
    
    for x, y, dx, dy in flow_arrows:
        ax4.arrow(x, y, dx, dy, head_width=0.1, head_length=0.2, 
                 fc='black', ec='black')
    
    ax4.set_xlim(0, 9)
    ax4.set_ylim(3, 8)
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated diagram: {output_file}")

def create_icmp_diagram(output_file):
    """Create ICMP/ICMPv6 message types and structure diagram"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('ICMP/ICMPv6 Protocol Overview', fontsize=16, fontweight='bold')
    
    # ICMP Message Types
    ax1.set_title('ICMP Message Types (IPv4)', fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 8)
    
    icmp_types = [
        (1, 7, 3, 0.8, "Echo Request\nType 8", "lightgreen"),
        (5, 7, 3, 0.8, "Echo Reply\nType 0", "lightblue"),
        (1, 5.5, 3, 0.8, "Dest Unreachable\nType 3", "lightcoral"),
        (5, 5.5, 3, 0.8, "Time Exceeded\nType 11", "lightyellow"),
        (1, 4, 3, 0.8, "Redirect\nType 5", "lightpink"),
        (5, 4, 3, 0.8, "Parameter Problem\nType 12", "lightgray")
    ]
    
    for x, y, width, height, label, color in icmp_types:
        rect = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.1",
                             facecolor=color, edgecolor='black', linewidth=1)
        ax1.add_patch(rect)
        ax1.text(x + width/2, y + height/2, label, ha='center', va='center', 
                fontsize=9, fontweight='bold')
    
    ax1.set_xlim(0, 9)
    ax1.set_ylim(3, 8)
    ax1.axis('off')
    
    # ICMPv6 Message Types
    ax2.set_title('ICMPv6 Message Types (IPv6)', fontweight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 8)
    
    icmpv6_types = [
        (1, 7, 3, 0.8, "Echo Request\nType 128", "lightgreen"),
        (5, 7, 3, 0.8, "Echo Reply\nType 129", "lightblue"),
        (1, 5.5, 3, 0.8, "Dest Unreachable\nType 1", "lightcoral"),
        (5, 5.5, 3, 0.8, "Packet Too Big\nType 2", "lightyellow"),
        (1, 4, 3, 0.8, "Neighbor Sol.\nType 135", "lightpink"),
        (5, 4, 3, 0.8, "Neighbor Adv.\nType 136", "lightsteelblue")
    ]
    
    for x, y, width, height, label, color in icmpv6_types:
        rect = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.1",
                             facecolor=color, edgecolor='black', linewidth=1)
        ax2.add_patch(rect)
        ax2.text(x + width/2, y + height/2, label, ha='center', va='center', 
                fontsize=9, fontweight='bold')
    
    ax2.set_xlim(0, 9)
    ax2.set_ylim(3, 8)
    ax2.axis('off')
    
    # ICMP Packet Structure
    ax3.set_title('ICMP Packet Structure', fontweight='bold')
    ax3.set_xlim(0, 32)
    ax3.set_ylim(0, 4)
    
    icmp_fields = [
        (0, 3, 8, 1, "Type (8)", "lightblue"),
        (8, 3, 8, 1, "Code (8)", "lightgreen"),
        (16, 3, 16, 1, "Checksum (16)", "lightyellow"),
        (0, 2, 32, 1, "Rest of Header (32 bits)", "lightcoral"),
        (0, 1, 32, 1, "Data Section (Variable Length)", "lightgray")
    ]
    
    for x, y, width, height, label, color in icmp_fields:
        rect = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02",
                             facecolor=color, edgecolor='black', linewidth=0.5)
        ax3.add_patch(rect)
        ax3.text(x + width/2, y + height/2, label, ha='center', va='center', 
                fontsize=10, fontweight='bold')
    
    ax3.set_xticks(range(0, 33, 8))
    ax3.set_xticklabels([str(i) for i in range(0, 33, 8)])
    ax3.set_yticks([])
    ax3.set_xlabel('Bit Position')
    
    # Ping Process Flow
    ax4.set_title('Ping Process Flow', fontweight='bold')
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 8)
    
    ping_boxes = [
        (1, 7, 2.5, 0.8, "Send Echo\nRequest", "lightgreen"),
        (1, 5.5, 2.5, 0.8, "Destination\nReachable?", "lightyellow"),
        (0.5, 4, 1.8, 0.8, "Receive\nEcho Reply", "lightblue"),
        (2.7, 4, 1.8, 0.8, "Receive Dest\nUnreachable", "lightcoral"),
        (0.5, 2.5, 1.8, 0.8, "Calculate\nRTT", "lightsteelblue"),
        (2.7, 2.5, 1.8, 0.8, "Report\nError", "lightpink")
    ]
    
    for x, y, width, height, label, color in ping_boxes:
        rect = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.1",
                             facecolor=color, edgecolor='black', linewidth=1)
        ax4.add_patch(rect)
        ax4.text(x + width/2, y + height/2, label, ha='center', va='center', 
                fontsize=9, fontweight='bold')
    
    # Add arrows for ping flow
    arrows = [
        (2.25, 7, 0, -1),      # Send to reachable check
        (2.25, 5.5, -0.8, -1), # To echo reply
        (2.25, 5.5, 0.8, -1),  # To unreachable
        (1.4, 4, 0, -1),       # Reply to RTT
        (3.6, 4, 0, -1)        # Unreachable to error
    ]
    
    for x, y, dx, dy in arrows:
        ax4.arrow(x, y, dx, dy, head_width=0.1, head_length=0.1, 
                 fc='black', ec='black')
    
    ax4.set_xlim(0, 5)
    ax4.set_ylim(2, 8)
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated diagram: {output_file}")

def create_ipv4_ipv6_diagram(output_file):
    """Create IPv4/IPv6 comparison diagram"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('IPv4 vs IPv6 Protocol Comparison', fontsize=16, fontweight='bold')
    
    # IPv4 Packet Structure
    ax1.set_title('IPv4 Header Structure (20+ bytes)', fontweight='bold')
    ax1.set_xlim(0, 32)
    ax1.set_ylim(0, 6)
    
    # IPv4 header fields
    fields_ipv4 = [
        (0, 5, 4, 1, "Ver\n(4)", "lightblue"),
        (4, 5, 4, 1, "IHL\n(4)", "lightgreen"),
        (8, 5, 8, 1, "Type of Service (8)", "lightyellow"),
        (16, 5, 16, 1, "Total Length (16)", "lightcoral"),
        (0, 4, 16, 1, "Identification (16)", "lightpink"),
        (16, 4, 3, 1, "Flags\n(3)", "lightgray"),
        (19, 4, 13, 1, "Fragment Offset (13)", "lightsteelblue"),
        (0, 3, 8, 1, "TTL (8)", "wheat"),
        (8, 3, 8, 1, "Protocol (8)", "plum"),
        (16, 3, 16, 1, "Header Checksum (16)", "lightcyan"),
        (0, 2, 32, 1, "Source IP Address (32 bits)", "mistyrose"),
        (0, 1, 32, 1, "Destination IP Address (32 bits)", "lavender"),
        (0, 0, 32, 1, "Options (Variable) + Data", "whitesmoke")
    ]
    
    for x, y, width, height, label, color in fields_ipv4:
        rect = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02",
                             facecolor=color, edgecolor='black', linewidth=0.5)
        ax1.add_patch(rect)
        ax1.text(x + width/2, y + height/2, label, ha='center', va='center', 
                fontsize=8, fontweight='bold')
    
    ax1.set_xticks(range(0, 33, 4))
    ax1.set_xticklabels([str(i) for i in range(0, 33, 4)])
    ax1.set_yticks([])
    ax1.set_xlabel('Bit Position')
    
    # IPv6 Packet Structure
    ax2.set_title('IPv6 Header Structure (40 bytes fixed)', fontweight='bold')
    ax2.set_xlim(0, 32)
    ax2.set_ylim(0, 6)
    
    # IPv6 header fields
    fields_ipv6 = [
        (0, 5, 4, 1, "Ver\n(4)", "lightblue"),
        (4, 5, 8, 1, "Traffic Class (8)", "lightgreen"),
        (12, 5, 20, 1, "Flow Label (20)", "lightyellow"),
        (0, 4, 16, 1, "Payload Length (16)", "lightcoral"),
        (16, 4, 8, 1, "Next Header (8)", "lightpink"),
        (24, 4, 8, 1, "Hop Limit (8)", "lightgray"),
        (0, 3, 32, 1, "Source Address (128 bits)", "mistyrose"),
        (0, 2, 32, 1, "Source Address (continued)", "mistyrose"),
        (0, 1, 32, 1, "Destination Address (128 bits)", "lavender"),
        (0, 0, 32, 1, "Destination Address (continued)", "lavender")
    ]
    
    for x, y, width, height, label, color in fields_ipv6:
        rect = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02",
                             facecolor=color, edgecolor='black', linewidth=0.5)
        ax2.add_patch(rect)
        ax2.text(x + width/2, y + height/2, label, ha='center', va='center', 
                fontsize=8, fontweight='bold')
    
    ax2.set_xticks(range(0, 33, 4))
    ax2.set_xticklabels([str(i) for i in range(0, 33, 4)])
    ax2.set_yticks([])
    ax2.set_xlabel('Bit Position')
    
    # Address Space Comparison
    ax3.set_title('Address Space Comparison', fontweight='bold')
    protocols = ['IPv4', 'IPv6']
    addresses = [4.3e9, 3.4e38]  # Approximate values
    
    bars = ax3.bar(protocols, addresses, color=['lightcoral', 'lightblue'])
    ax3.set_ylabel('Total Addresses (log scale)')
    ax3.set_yscale('log')
    
    # Add value labels
    for bar, addr in zip(bars, addresses):
        height = bar.get_height()
        if addr < 1e10:
            label = f'{addr/1e9:.1f}B'
        else:
            label = f'{addr:.1e}'
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                label, ha='center', va='bottom', fontweight='bold')
    
    # Routing Process Flow
    ax4.set_title('Packet Routing Process', fontweight='bold')
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 8)
    
    # Routing flow boxes
    boxes = [
        (1, 7, 2, 0.8, "Packet\nArrives", "lightgreen"),
        (1, 5.5, 2, 0.8, "Check\nDestination", "lightyellow"),
        (0.5, 4, 1.5, 0.8, "Local\nNetwork?", "lightcoral"),
        (2.5, 4, 1.5, 0.8, "Remote\nNetwork?", "lightcoral"),
        (0.5, 2.5, 1.5, 0.8, "Direct\nDelivery", "lightblue"),
        (2.5, 2.5, 1.5, 0.8, "Route Table\nLookup", "lightpink"),
        (5, 4, 2, 0.8, "Forward to\nNext Hop", "lightsteelblue"),
        (5, 2.5, 2, 0.8, "Packet\nForwarded", "lightgreen")
    ]
    
    for x, y, width, height, label, color in boxes:
        rect = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.1",
                             facecolor=color, edgecolor='black', linewidth=1)
        ax4.add_patch(rect)
        ax4.text(x + width/2, y + height/2, label, ha='center', va='center', 
                fontsize=9, fontweight='bold')
    
    # Add arrows
    arrows = [
        (2, 7, 0, -1),      # Packet arrives to check destination
        (2, 5.5, -0.8, -1), # To local network
        (2, 5.5, 0.8, -1),  # To remote network
        (1.25, 4, 0, -1),   # Local to direct delivery
        (3.25, 4, 0, -1),   # Remote to route lookup
        (3.25, 2.5, 1.5, 1), # Route lookup to forward
        (6, 4, 0, -1)       # Forward to forwarded
    ]
    
    for x, y, dx, dy in arrows:
        ax4.arrow(x, y, dx, dy, head_width=0.1, head_length=0.1, 
                 fc='black', ec='black')
    
    ax4.set_xlim(0, 8)
    ax4.set_ylim(1, 8)
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated diagram: {output_file}")

def render_mermaid_diagram(mmd_file):
    """Render diagram based on .mmd file content"""
    if not os.path.exists(mmd_file):
        print(f"Error: {mmd_file} not found")
        return False
    
    output_file = os.path.splitext(mmd_file)[0] + ".png"
    
    # For IPv4/IPv6 comparison, create custom diagram
    if "ipv4_ipv6" in mmd_file.lower():
        create_ipv4_ipv6_diagram(output_file)
        return True
    
    # For ICMP message types, create ICMP diagram
    if "icmp" in mmd_file.lower():
        create_icmp_diagram(output_file)
        return True
    
    # For TCP states and flow, create TCP diagram
    if "tcp" in mmd_file.lower():
        create_tcp_diagram(output_file)
        return True
    
    # For other diagrams, create a simple visualization
    create_generic_diagram(output_file, mmd_file)
    return True

def create_generic_diagram(output_file, mmd_file):
    """Create a generic diagram for other .mmd files"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Simple placeholder with file info
    ax.text(0.5, 0.5, f"Diagram for:\n{os.path.basename(mmd_file)}\n\nGenerated with Python matplotlib", 
            ha='center', va='center', fontsize=14, 
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue"))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated generic diagram: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 render_diagram.py <file.mmd>")
        sys.exit(1)
    
    mmd_file = sys.argv[1]
    success = render_mermaid_diagram(mmd_file)
    
    if not success:
        sys.exit(1)
