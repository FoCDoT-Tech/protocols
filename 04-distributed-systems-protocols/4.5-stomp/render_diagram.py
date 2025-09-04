#!/usr/bin/env python3
"""
STOMP Diagram Renderer
Generates visual diagrams for STOMP protocol concepts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, ConnectionPatch, Arrow
import numpy as np

def create_stomp_architecture_diagram():
    """Create STOMP broker architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'STOMP Protocol Architecture', 
           fontsize=16, fontweight='bold', ha='center')
    
    # STOMP Broker Core
    broker_box = FancyBboxPatch((6, 7), 4, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#e1f5fe', edgecolor='#01579b', linewidth=2)
    ax.add_patch(broker_box)
    ax.text(8, 7.75, 'STOMP Broker', fontsize=12, fontweight='bold', ha='center')
    ax.text(8, 7.25, 'Frame Router & Session Manager', fontsize=10, ha='center', style='italic')
    
    # Frame Parser
    parser_box = FancyBboxPatch((1, 5.5), 3, 1, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#e8f5e8', edgecolor='#2e7d32', linewidth=1)
    ax.add_patch(parser_box)
    ax.text(2.5, 6, 'Frame Parser', fontsize=11, fontweight='bold', ha='center')
    ax.text(2.5, 5.7, 'Text Protocol', fontsize=9, ha='center', style='italic')
    
    # Destination Manager
    dest_box = FancyBboxPatch((5, 5.5), 3, 1, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#fff3e0', edgecolor='#ef6c00', linewidth=1)
    ax.add_patch(dest_box)
    ax.text(6.5, 6, 'Destinations', fontsize=11, fontweight='bold', ha='center')
    ax.text(6.5, 5.7, '/queue/* /topic/*', fontsize=9, ha='center', style='italic')
    
    # Transaction Manager
    trans_box = FancyBboxPatch((9, 5.5), 3, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#f3e5f5', edgecolor='#7b1fa2', linewidth=1)
    ax.add_patch(trans_box)
    ax.text(10.5, 6, 'Transactions', fontsize=11, fontweight='bold', ha='center')
    ax.text(10.5, 5.7, 'BEGIN/COMMIT/ABORT', fontsize=9, ha='center', style='italic')
    
    # Session Manager
    session_box = FancyBboxPatch((13, 5.5), 3, 1, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#ffebee', edgecolor='#c62828', linewidth=1)
    ax.add_patch(session_box)
    ax.text(14.5, 6, 'Sessions', fontsize=11, fontweight='bold', ha='center')
    ax.text(14.5, 5.7, 'Client Connections', fontsize=9, ha='center', style='italic')
    
    # Client Types
    clients = [
        ("Web Client\n(WebSocket)", 2, 3, "#e1f5fe"),
        ("Java Client\n(Spring)", 6, 3, "#e8f5e8"),
        ("Python Client\n(stomp.py)", 10, 3, "#fff3e0"),
        ("Ruby Client\n(stomp gem)", 14, 3, "#f3e5f5")
    ]
    
    for name, x, y, color in clients:
        client_box = FancyBboxPatch((x-1, y-0.5), 2, 1, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(client_box)
        ax.text(x, y, name, fontsize=9, fontweight='bold', ha='center')
    
    # Frame Types
    frames = [
        ("CONNECT", 2, 1, "#ffcdd2"),
        ("SEND", 4.5, 1, "#c8e6c9"),
        ("SUBSCRIBE", 7, 1, "#ffe0b2"),
        ("MESSAGE", 9.5, 1, "#f8bbd9"),
        ("ACK/NACK", 12, 1, "#e0f2f1"),
        ("DISCONNECT", 14.5, 1, "#d1c4e9")
    ]
    
    for name, x, y, color in frames:
        frame_box = FancyBboxPatch((x-0.7, y-0.3), 1.4, 0.6, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(frame_box)
        ax.text(x, y, name, fontsize=8, fontweight='bold', ha='center')
    
    # Connection arrows
    connections = [
        # Broker to components
        ((6.5, 7), (4, 6)),    # Broker to Parser
        ((8, 7), (6.5, 6.5)),  # Broker to Destinations
        ((9.5, 7), (10.5, 6.5)), # Broker to Transactions
        ((10, 7), (14.5, 6.5)), # Broker to Sessions
        
        # Clients to broker
        ((2, 3.5), (7, 7)),
        ((6, 3.5), (7.5, 7)),
        ((10, 3.5), (8.5, 7)),
        ((14, 3.5), (9, 7))
    ]
    
    for (x1, y1), (x2, y2) in connections:
        arrow = ConnectionPatch((x1, y1), (x2, y2), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=12, fc="gray", ec="gray", alpha=0.6)
        ax.add_patch(arrow)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('stomp_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_frame_structure_diagram():
    """Create STOMP frame structure diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    
    ax.text(7, 7.5, 'STOMP Frame Structure', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Frame components
    frame_y = 5.5
    
    # Command line
    cmd_box = Rectangle((2, frame_y + 1), 10, 0.8, 
                       facecolor='#ffcdd2', edgecolor='black', linewidth=1)
    ax.add_patch(cmd_box)
    ax.text(7, frame_y + 1.4, 'COMMAND', fontsize=12, fontweight='bold', ha='center')
    ax.text(7, frame_y + 1.1, 'SEND, SUBSCRIBE, MESSAGE, etc.', fontsize=10, ha='center', style='italic')
    
    # Headers
    header_box = Rectangle((2, frame_y), 10, 0.8, 
                          facecolor='#c8e6c9', edgecolor='black', linewidth=1)
    ax.add_patch(header_box)
    ax.text(7, frame_y + 0.4, 'HEADERS', fontsize=12, fontweight='bold', ha='center')
    ax.text(7, frame_y + 0.1, 'destination:/topic/chat\\ncontent-type:text/plain', fontsize=10, ha='center', style='italic')
    
    # Empty line
    empty_box = Rectangle((2, frame_y - 0.5), 10, 0.4, 
                         facecolor='#ffe0b2', edgecolor='black', linewidth=1)
    ax.add_patch(empty_box)
    ax.text(7, frame_y - 0.3, 'EMPTY LINE', fontsize=10, fontweight='bold', ha='center')
    
    # Body
    body_box = Rectangle((2, frame_y - 1.5), 10, 0.8, 
                        facecolor='#f8bbd9', edgecolor='black', linewidth=1)
    ax.add_patch(body_box)
    ax.text(7, frame_y - 1.1, 'BODY', fontsize=12, fontweight='bold', ha='center')
    ax.text(7, frame_y - 1.4, 'Message content (text, JSON, binary)', fontsize=10, ha='center', style='italic')
    
    # NULL terminator
    null_box = Rectangle((2, frame_y - 2.2), 10, 0.4, 
                        facecolor='#e0f2f1', edgecolor='black', linewidth=1)
    ax.add_patch(null_box)
    ax.text(7, frame_y - 2, 'NULL TERMINATOR (\\x00)', fontsize=10, fontweight='bold', ha='center')
    
    # Example frame
    example_x = 14.5
    ax.text(example_x, 7, 'Example SEND Frame:', fontsize=12, fontweight='bold', ha='left')
    
    example_text = """SEND
destination:/topic/chat
content-type:text/plain
content-length:13

Hello, World!\\x00"""
    
    example_box = FancyBboxPatch((example_x - 0.5, 3), 6, 3.5, 
                                boxstyle="round,pad=0.2", 
                                facecolor='#f5f5f5', edgecolor='gray', linewidth=1)
    ax.add_patch(example_box)
    ax.text(example_x, 4.7, example_text, fontsize=10, ha='left', va='center', 
           fontfamily='monospace', linespacing=1.5)
    
    # Frame flow
    ax.text(7, 2, 'Frame Processing Flow', fontsize=14, fontweight='bold', ha='center')
    
    flow_steps = [
        ("Parse Command", 2, 0.5, "#ffcdd2"),
        ("Parse Headers", 5, 0.5, "#c8e6c9"),
        ("Extract Body", 8, 0.5, "#ffe0b2"),
        ("Process Frame", 11, 0.5, "#f8bbd9"),
        ("Send Response", 14, 0.5, "#e0f2f1")
    ]
    
    for i, (step, x, y, color) in enumerate(flow_steps):
        step_box = FancyBboxPatch((x-1, y-0.3), 2, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(step_box)
        ax.text(x, y, step, fontsize=9, fontweight='bold', ha='center')
        
        # Arrow to next step
        if i < len(flow_steps) - 1:
            next_x = flow_steps[i + 1][1]
            arrow = ConnectionPatch((x + 1, y), (next_x - 1, y), "data", "data",
                                   arrowstyle="->", shrinkA=5, shrinkB=5,
                                   mutation_scale=12, fc="blue", ec="blue")
            ax.add_patch(arrow)
    
    ax.set_xlim(0, 21)
    ax.set_ylim(-1, 8)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('frame_structure.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_messaging_patterns_diagram():
    """Create STOMP messaging patterns diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'STOMP Messaging Patterns', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Point-to-Point (Queue)
    ax.text(4, 8.5, 'Point-to-Point (/queue/*)', fontsize=14, fontweight='bold', ha='center')
    
    # Producer
    producer_box = FancyBboxPatch((1, 7), 2, 1, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#e1f5fe', edgecolor='#01579b', linewidth=1)
    ax.add_patch(producer_box)
    ax.text(2, 7.5, 'Producer', fontsize=10, fontweight='bold', ha='center')
    
    # Queue
    queue_box = FancyBboxPatch((4.5, 7), 2, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#fff3e0', edgecolor='#ef6c00', linewidth=1)
    ax.add_patch(queue_box)
    ax.text(5.5, 7.5, '/queue/orders', fontsize=10, fontweight='bold', ha='center')
    
    # Consumer
    consumer_box = FancyBboxPatch((8, 7), 2, 1, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#e8f5e8', edgecolor='#2e7d32', linewidth=1)
    ax.add_patch(consumer_box)
    ax.text(9, 7.5, 'Consumer', fontsize=10, fontweight='bold', ha='center')
    
    # Arrows
    arrow1 = ConnectionPatch((3, 7.5), (4.5, 7.5), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5,
                            mutation_scale=12, fc="blue", ec="blue")
    ax.add_patch(arrow1)
    ax.text(3.75, 7.8, 'SEND', fontsize=8, ha='center')
    
    arrow2 = ConnectionPatch((6.5, 7.5), (8, 7.5), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5,
                            mutation_scale=12, fc="green", ec="green")
    ax.add_patch(arrow2)
    ax.text(7.25, 7.8, 'MESSAGE', fontsize=8, ha='center')
    
    # Publish-Subscribe (Topic)
    ax.text(4, 5.5, 'Publish-Subscribe (/topic/*)', fontsize=14, fontweight='bold', ha='center')
    
    # Publisher
    publisher_box = FancyBboxPatch((1, 4), 2, 1, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#e1f5fe', edgecolor='#01579b', linewidth=1)
    ax.add_patch(publisher_box)
    ax.text(2, 4.5, 'Publisher', fontsize=10, fontweight='bold', ha='center')
    
    # Topic
    topic_box = FancyBboxPatch((4.5, 4), 2, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#f3e5f5', edgecolor='#7b1fa2', linewidth=1)
    ax.add_patch(topic_box)
    ax.text(5.5, 4.5, '/topic/chat', fontsize=10, fontweight='bold', ha='center')
    
    # Subscribers
    subscribers = [
        ("Sub A", 8, 5),
        ("Sub B", 8, 4),
        ("Sub C", 8, 3)
    ]
    
    for name, x, y in subscribers:
        sub_box = FancyBboxPatch((x, y), 1.5, 0.8, 
                                boxstyle="round,pad=0.05", 
                                facecolor='#e8f5e8', edgecolor='#2e7d32', linewidth=1)
        ax.add_patch(sub_box)
        ax.text(x + 0.75, y + 0.4, name, fontsize=9, fontweight='bold', ha='center')
        
        # Arrow from topic
        arrow = ConnectionPatch((6.5, 4.5), (x, y + 0.4), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=10, fc="green", ec="green", alpha=0.7)
        ax.add_patch(arrow)
    
    # Arrow from publisher to topic
    arrow3 = ConnectionPatch((3, 4.5), (4.5, 4.5), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5,
                            mutation_scale=12, fc="blue", ec="blue")
    ax.add_patch(arrow3)
    ax.text(3.75, 4.8, 'SEND', fontsize=8, ha='center')
    
    # Transaction Pattern
    ax.text(13, 8.5, 'Transaction Pattern', fontsize=14, fontweight='bold', ha='center')
    
    trans_steps = [
        ("BEGIN", 12, 7.5, "#ffcdd2"),
        ("SEND", 12, 6.8, "#c8e6c9"),
        ("SEND", 12, 6.1, "#c8e6c9"),
        ("COMMIT", 12, 5.4, "#ffe0b2")
    ]
    
    for i, (step, x, y, color) in enumerate(trans_steps):
        step_box = FancyBboxPatch((x, y-0.2), 2, 0.4, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(step_box)
        ax.text(x + 1, y, step, fontsize=9, fontweight='bold', ha='center')
        
        # Arrow to next step
        if i < len(trans_steps) - 1:
            arrow = ConnectionPatch((x + 1, y - 0.2), (x + 1, trans_steps[i + 1][2] + 0.2), 
                                   "data", "data", arrowstyle="->", shrinkA=2, shrinkB=2,
                                   mutation_scale=10, fc="purple", ec="purple")
            ax.add_patch(arrow)
    
    # Acknowledgment Modes
    ax.text(13, 4, 'Acknowledgment Modes', fontsize=14, fontweight='bold', ha='center')
    
    ack_modes = [
        ("auto", "Automatic", 12, 3.2, "#e1f5fe"),
        ("client", "Manual ACK", 12, 2.6, "#e8f5e8"),
        ("client-individual", "Per-message ACK", 12, 2, "#fff3e0")
    ]
    
    for mode, desc, x, y, color in ack_modes:
        mode_box = FancyBboxPatch((x, y-0.15), 3, 0.3, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(mode_box)
        ax.text(x + 0.3, y, mode, fontsize=9, fontweight='bold', ha='left')
        ax.text(x + 1.2, y, desc, fontsize=8, ha='left', style='italic')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(1, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('messaging_patterns.png', dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all STOMP diagrams"""
    print("🎨 Rendering STOMP diagrams...")
    
    diagrams = [
        ("STOMP Architecture", create_stomp_architecture_diagram),
        ("Frame Structure", create_frame_structure_diagram),
        ("Messaging Patterns", create_messaging_patterns_diagram)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All STOMP diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
