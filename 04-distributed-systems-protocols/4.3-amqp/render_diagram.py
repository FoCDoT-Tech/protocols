#!/usr/bin/env python3
"""
AMQP Diagram Renderer
Generates visual diagrams for AMQP protocol concepts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, ConnectionPatch
import numpy as np

def create_amqp_architecture_diagram():
    """Create AMQP broker architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'AMQP Broker Architecture', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Connection Layer
    conn_box = FancyBboxPatch((1, 7.5), 6, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#e3f2fd', edgecolor='#1976d2', linewidth=2)
    ax.add_patch(conn_box)
    ax.text(4, 8.25, 'TCP Connection & Channels', fontsize=12, fontweight='bold', ha='center')
    
    # Exchange Types
    exchanges = [
        ("Direct", 2, 6, "#e1f5fe"),
        ("Topic", 4, 6, "#e8f5e8"),
        ("Fanout", 6, 6, "#fff3e0"),
        ("Headers", 8, 6, "#f3e5f5")
    ]
    
    for name, x, y, color in exchanges:
        ex_box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, 
                               boxstyle="round,pad=0.1", 
                               facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(ex_box)
        ax.text(x, y, name, fontsize=10, fontweight='bold', ha='center')
    
    # Queues
    queues = [
        ("Order Queue", 2, 3.5, "#ffcdd2"),
        ("User Queue", 5, 3.5, "#c8e6c9"),
        ("Alert Queue", 8, 3.5, "#ffe0b2"),
        ("DLQ", 11, 3.5, "#f8bbd9")
    ]
    
    for name, x, y, color in queues:
        q_box = FancyBboxPatch((x-1, y-0.5), 2, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(q_box)
        ax.text(x, y, name, fontsize=10, fontweight='bold', ha='center')
    
    # Routing arrows
    for i, (_, ex_x, ex_y, _) in enumerate(exchanges[:3]):
        q_x, q_y = queues[i][1], queues[i][2]
        arrow = ConnectionPatch((ex_x, ex_y-0.5), (q_x, q_y+0.5), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=15, fc="blue", ec="blue", alpha=0.7)
        ax.add_patch(arrow)
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('amqp_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_exchange_types_diagram():
    """Create diagram showing different exchange types"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    
    ax.text(8, 7.5, 'AMQP Exchange Types', fontsize=16, fontweight='bold', ha='center')
    
    # Direct Exchange Example
    ax.text(2, 6.5, 'Direct Exchange', fontsize=12, fontweight='bold', ha='center')
    direct_box = FancyBboxPatch((0.5, 5), 3, 1, boxstyle="round,pad=0.1", 
                               facecolor='#e1f5fe', edgecolor='blue', linewidth=2)
    ax.add_patch(direct_box)
    ax.text(2, 5.5, 'Exact key match\norder → order_queue', fontsize=9, ha='center')
    
    # Topic Exchange Example
    ax.text(6, 6.5, 'Topic Exchange', fontsize=12, fontweight='bold', ha='center')
    topic_box = FancyBboxPatch((4.5, 5), 3, 1, boxstyle="round,pad=0.1", 
                              facecolor='#e8f5e8', edgecolor='green', linewidth=2)
    ax.add_patch(topic_box)
    ax.text(6, 5.5, 'Pattern matching\nuser.* → user_queue', fontsize=9, ha='center')
    
    # Fanout Exchange Example
    ax.text(10, 6.5, 'Fanout Exchange', fontsize=12, fontweight='bold', ha='center')
    fanout_box = FancyBboxPatch((8.5, 5), 3, 1, boxstyle="round,pad=0.1", 
                               facecolor='#fff3e0', edgecolor='orange', linewidth=2)
    ax.add_patch(fanout_box)
    ax.text(10, 5.5, 'Broadcast all\nto all queues', fontsize=9, ha='center')
    
    # Headers Exchange Example
    ax.text(14, 6.5, 'Headers Exchange', fontsize=12, fontweight='bold', ha='center')
    headers_box = FancyBboxPatch((12.5, 5), 3, 1, boxstyle="round,pad=0.1", 
                                facecolor='#f3e5f5', edgecolor='purple', linewidth=2)
    ax.add_patch(headers_box)
    ax.text(14, 5.5, 'Header matching\nformat=pdf', fontsize=9, ha='center')
    
    # Message flow examples
    flow_box = FancyBboxPatch((2, 2), 12, 2, boxstyle="round,pad=0.1", 
                             facecolor='#f5f5f5', edgecolor='gray', linewidth=1)
    ax.add_patch(flow_box)
    
    ax.text(8, 3.5, 'Message Routing Examples', fontsize=12, fontweight='bold', ha='center')
    examples = [
        "Direct: routing_key='order.created' → exactly matches binding 'order.created'",
        "Topic: routing_key='user.john.created' → matches pattern 'user.*'",
        "Fanout: any message → delivered to all bound queues",
        "Headers: {format: 'pdf', type: 'report'} → matches header requirements"
    ]
    
    for i, example in enumerate(examples):
        ax.text(2.5, 3.2 - i*0.2, example, fontsize=9, va='center')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('exchange_types.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_message_patterns_diagram():
    """Create common messaging patterns diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'Common AMQP Messaging Patterns', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Work Queue Pattern
    ax.text(2, 8.5, 'Work Queue', fontsize=12, fontweight='bold', ha='center')
    wq_box = FancyBboxPatch((0.5, 7), 3, 1, boxstyle="round,pad=0.1", 
                           facecolor='#ffcdd2', edgecolor='red', linewidth=2)
    ax.add_patch(wq_box)
    ax.text(2, 7.5, 'Task distribution\nRound-robin workers', fontsize=9, ha='center')
    
    # Publish-Subscribe Pattern
    ax.text(6, 8.5, 'Pub-Sub', fontsize=12, fontweight='bold', ha='center')
    ps_box = FancyBboxPatch((4.5, 7), 3, 1, boxstyle="round,pad=0.1", 
                           facecolor='#c8e6c9', edgecolor='green', linewidth=2)
    ax.add_patch(ps_box)
    ax.text(6, 7.5, 'Broadcast messages\nMultiple subscribers', fontsize=9, ha='center')
    
    # RPC Pattern
    ax.text(10, 8.5, 'RPC', fontsize=12, fontweight='bold', ha='center')
    rpc_box = FancyBboxPatch((8.5, 7), 3, 1, boxstyle="round,pad=0.1", 
                            facecolor='#ffe0b2', edgecolor='orange', linewidth=2)
    ax.add_patch(rpc_box)
    ax.text(10, 7.5, 'Request-Response\nCorrelation ID', fontsize=9, ha='center')
    
    # Priority Queue Pattern
    ax.text(14, 8.5, 'Priority', fontsize=12, fontweight='bold', ha='center')
    pq_box = FancyBboxPatch((12.5, 7), 3, 1, boxstyle="round,pad=0.1", 
                           facecolor='#f8bbd9', edgecolor='purple', linewidth=2)
    ax.add_patch(pq_box)
    ax.text(14, 7.5, 'Priority ordering\nx-max-priority', fontsize=9, ha='center')
    
    # Delivery Guarantees
    dg_box = FancyBboxPatch((2, 4), 12, 2, boxstyle="round,pad=0.1", 
                           facecolor='#f0f0f0', edgecolor='gray', linewidth=1)
    ax.add_patch(dg_box)
    
    ax.text(8, 5.5, 'Delivery Guarantees', fontsize=12, fontweight='bold', ha='center')
    
    guarantees = [
        ("At-Most-Once", 3, 4.8, "#ffebee"),
        ("At-Least-Once", 6, 4.8, "#e8f5e8"),
        ("Exactly-Once", 9, 4.8, "#e1f5fe"),
        ("Transactional", 12, 4.8, "#fff3e0")
    ]
    
    for name, x, y, color in guarantees:
        g_box = FancyBboxPatch((x-1, y-0.3), 2, 0.6, boxstyle="round,pad=0.05", 
                              facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(g_box)
        ax.text(x, y, name, fontsize=9, fontweight='bold', ha='center')
    
    # QoS Features
    qos_text = [
        "• Message Acknowledgments: Consumer confirms processing",
        "• Publisher Confirms: Broker confirms receipt",
        "• Message Persistence: Survive broker restarts",
        "• Prefetch Control: Limit unacknowledged messages"
    ]
    
    for i, feature in enumerate(qos_text):
        ax.text(2.5, 2.5 - i*0.3, feature, fontsize=10, va='center')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('message_patterns.png', dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all AMQP diagrams"""
    print("🎨 Rendering AMQP diagrams...")
    
    diagrams = [
        ("AMQP Architecture", create_amqp_architecture_diagram),
        ("Exchange Types", create_exchange_types_diagram),
        ("Message Patterns", create_message_patterns_diagram)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All AMQP diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
