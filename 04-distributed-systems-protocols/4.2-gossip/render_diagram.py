#!/usr/bin/env python3
"""
Gossip Protocols Diagram Renderer
Generates visual diagrams for gossip protocol concepts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, ConnectionPatch
import numpy as np
import networkx as nx

def create_gossip_network_diagram():
    """Create gossip network topology diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'Gossip Protocol Network Topology', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Create network graph
    G = nx.erdos_renyi_graph(8, 0.3, seed=42)
    pos = nx.spring_layout(G, seed=42, k=3, iterations=50)
    
    # Scale positions to fit the plot
    for node in pos:
        pos[node] = (pos[node][0] * 6 + 8, pos[node][1] * 4 + 5)
    
    # Draw nodes
    node_colors = ['#e1f5fe', '#e8f5e8', '#fff3e0', '#f3e5f5', 
                   '#e0f2f1', '#ffebee', '#f1f8e9', '#fce4ec']
    
    for i, (node, (x, y)) in enumerate(pos.items()):
        circle = Circle((x, y), 0.4, facecolor=node_colors[i], 
                       edgecolor='gray', linewidth=2)
        ax.add_patch(circle)
        ax.text(x, y, f'N{node}', ha='center', va='center', 
               fontsize=10, fontweight='bold')
    
    # Draw edges with gossip flow
    for edge in G.edges():
        x1, y1 = pos[edge[0]]
        x2, y2 = pos[edge[1]]
        
        # Draw connection line
        ax.plot([x1, x2], [y1, y2], 'k-', alpha=0.3, linewidth=1)
        
        # Add gossip flow arrows (random selection)
        if np.random.random() < 0.4:
            arrow = ConnectionPatch((x1, y1), (x2, y2), "data", "data",
                                   arrowstyle="->", shrinkA=20, shrinkB=20,
                                   mutation_scale=15, fc="blue", alpha=0.7)
            ax.add_patch(arrow)
    
    # Add gossip round information
    gossip_box = FancyBboxPatch((1, 1), 6, 2.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#f5f5f5', edgecolor='gray', linewidth=1)
    ax.add_patch(gossip_box)
    
    ax.text(4, 2.7, 'Gossip Round Process', fontsize=12, fontweight='bold', ha='center')
    gossip_steps = [
        "1. Each node selects random peers",
        "2. Exchange state information",
        "3. Merge and update local state",
        "4. Propagate changes to network"
    ]
    
    for i, step in enumerate(gossip_steps):
        ax.text(1.2, 2.3 - i*0.3, step, fontsize=9, va='center')
    
    # Add failure detection info
    failure_box = FancyBboxPatch((10, 1), 5, 2.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#ffebee', edgecolor='red', linewidth=1)
    ax.add_patch(failure_box)
    
    ax.text(12.5, 2.7, 'Failure Detection', fontsize=12, fontweight='bold', ha='center')
    failure_steps = [
        "• SWIM-style ping/ack",
        "• Suspicion timeouts",
        "• Gossip failure notifications",
        "• Automatic recovery"
    ]
    
    for i, step in enumerate(failure_steps):
        ax.text(10.2, 2.3 - i*0.3, step, fontsize=9, va='center')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('gossip_network.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_epidemic_spread_diagram():
    """Create epidemic information spread diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    
    ax.text(8, 7.5, 'Epidemic Information Spread in Gossip Networks', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Time steps for epidemic spread
    time_steps = [0, 1, 2, 3, 4]
    infected_counts = [1, 3, 7, 15, 31]  # Exponential growth
    
    # Create subplot for each time step
    step_width = 3
    for t, infected in enumerate(infected_counts):
        x_offset = t * step_width
        
        # Draw time step label
        ax.text(x_offset + 1.5, 6.5, f'Round {t}', 
               fontsize=12, fontweight='bold', ha='center')
        ax.text(x_offset + 1.5, 6, f'{infected} nodes', 
               fontsize=10, ha='center', color='red')
        
        # Draw nodes
        total_nodes = 32
        rows, cols = 4, 8
        node_size = 0.15
        
        for i in range(rows):
            for j in range(cols):
                node_idx = i * cols + j
                x = x_offset + 0.3 + j * 0.3
                y = 5 - i * 0.3
                
                # Color based on infection status
                if node_idx < infected:
                    color = '#ff5722'  # Infected (has information)
                else:
                    color = '#e0e0e0'  # Susceptible (no information)
                
                circle = Circle((x, y), node_size, facecolor=color, 
                               edgecolor='gray', linewidth=0.5)
                ax.add_patch(circle)
    
    # Add growth curve
    curve_ax = fig.add_axes([0.1, 0.1, 0.8, 0.3])
    curve_ax.plot(time_steps, infected_counts, 'ro-', linewidth=3, markersize=8)
    curve_ax.set_xlabel('Gossip Rounds')
    curve_ax.set_ylabel('Informed Nodes')
    curve_ax.set_title('Exponential Information Spread')
    curve_ax.grid(True, alpha=0.3)
    curve_ax.set_ylim(0, 35)
    
    # Add exponential equation
    curve_ax.text(2, 25, 'Growth ≈ 2^round', fontsize=12, 
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('epidemic_spread.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_swim_protocol_diagram():
    """Create SWIM protocol failure detection diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'SWIM Protocol: Failure Detection Mechanism', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Draw nodes
    nodes = [
        ("A", 2, 7, "#e1f5fe", "Monitoring"),
        ("B", 6, 7, "#ffcdd2", "Target"),
        ("C", 10, 7, "#e8f5e8", "Proxy 1"),
        ("D", 14, 7, "#fff3e0", "Proxy 2")
    ]
    
    for name, x, y, color, role in nodes:
        node_box = FancyBboxPatch((x-0.8, y-0.8), 1.6, 1.6, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=color, edgecolor='gray', linewidth=2)
        ax.add_patch(node_box)
        ax.text(x, y+0.3, f"Node {name}", ha='center', va='center', 
               fontsize=11, fontweight='bold')
        ax.text(x, y-0.3, role, ha='center', va='center', 
               fontsize=9, style='italic')
    
    # SWIM protocol steps
    steps = [
        (1, "Direct Ping", 2, 6, 6, 6, "blue", "PING"),
        (2, "Timeout", 6, 5.5, 6, 5.5, "red", "No ACK"),
        (3, "Indirect Ping", 2, 5, 10, 5, "orange", "Ping-Req(B)"),
        (4, "Proxy Ping", 10, 4.5, 6, 4.5, "green", "PING"),
        (5, "Proxy Response", 6, 4, 10, 4, "green", "ACK"),
        (6, "Indirect Response", 10, 3.5, 2, 3.5, "orange", "ACK via C"),
    ]
    
    for step_num, desc, x1, y1, x2, y2, color, label in steps:
        # Draw arrow
        arrow = ConnectionPatch((x1, y1), (x2, y2), "data", "data",
                               arrowstyle="->", shrinkA=10, shrinkB=10,
                               mutation_scale=20, fc=color, ec=color, lw=2)
        ax.add_patch(arrow)
        
        # Add step label
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.2, f"{step_num}. {label}", 
               ha='center', va='bottom', fontsize=8, 
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Add protocol explanation
    explanation_box = FancyBboxPatch((1, 1), 14, 1.5, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor='#f5f5f5', edgecolor='gray', linewidth=1)
    ax.add_patch(explanation_box)
    
    ax.text(8, 2, 'SWIM Protocol Benefits', fontsize=12, fontweight='bold', ha='center')
    benefits = [
        "• Constant per-node overhead regardless of cluster size",
        "• Indirect probing reduces false positives from network issues", 
        "• Gossip-based dissemination ensures rapid failure notification",
        "• Configurable timeouts balance detection speed vs accuracy"
    ]
    
    for i, benefit in enumerate(benefits):
        ax.text(1.5, 1.7 - i*0.2, benefit, fontsize=9, va='center')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('swim_protocol.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_anti_entropy_diagram():
    """Create anti-entropy synchronization diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'Anti-Entropy State Synchronization', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Before synchronization
    ax.text(4, 8.5, 'Before Sync', fontsize=14, fontweight='bold', ha='center')
    
    # Node A state
    nodeA_box = FancyBboxPatch((1, 6.5), 3, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#e1f5fe', edgecolor='blue', linewidth=2)
    ax.add_patch(nodeA_box)
    ax.text(2.5, 7.6, 'Node A', fontsize=11, fontweight='bold', ha='center')
    ax.text(2.5, 7.2, 'State: {x:1, y:2}', fontsize=9, ha='center')
    ax.text(2.5, 6.8, 'Version: [A:2, B:1]', fontsize=9, ha='center')
    
    # Node B state
    nodeB_box = FancyBboxPatch((5, 6.5), 3, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#e8f5e8', edgecolor='green', linewidth=2)
    ax.add_patch(nodeB_box)
    ax.text(6.5, 7.6, 'Node B', fontsize=11, fontweight='bold', ha='center')
    ax.text(6.5, 7.2, 'State: {y:3, z:4}', fontsize=9, ha='center')
    ax.text(6.5, 6.8, 'Version: [A:1, B:2]', fontsize=9, ha='center')
    
    # Synchronization process
    sync_arrow = ConnectionPatch((4, 7.25), (5, 7.25), "data", "data",
                                arrowstyle="<->", shrinkA=5, shrinkB=5,
                                mutation_scale=20, fc="orange", ec="orange", lw=3)
    ax.add_patch(sync_arrow)
    ax.text(4.5, 7.6, 'Sync', fontsize=10, fontweight='bold', ha='center', color='orange')
    
    # After synchronization
    ax.text(12, 8.5, 'After Sync', fontsize=14, fontweight='bold', ha='center')
    
    # Node A after sync
    nodeA_after_box = FancyBboxPatch((9, 6.5), 3, 1.5, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor='#c8e6c9', edgecolor='blue', linewidth=2)
    ax.add_patch(nodeA_after_box)
    ax.text(10.5, 7.6, 'Node A', fontsize=11, fontweight='bold', ha='center')
    ax.text(10.5, 7.2, 'State: {x:1, y:3, z:4}', fontsize=9, ha='center')
    ax.text(10.5, 6.8, 'Version: [A:2, B:2]', fontsize=9, ha='center')
    
    # Node B after sync
    nodeB_after_box = FancyBboxPatch((13, 6.5), 3, 1.5, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor='#c8e6c9', edgecolor='green', linewidth=2)
    ax.add_patch(nodeB_after_box)
    ax.text(14.5, 7.6, 'Node B', fontsize=11, fontweight='bold', ha='center')
    ax.text(14.5, 7.2, 'State: {x:1, y:3, z:4}', fontsize=9, ha='center')
    ax.text(14.5, 6.8, 'Version: [A:2, B:2]', fontsize=9, ha='center')
    
    # Conflict resolution strategies
    ax.text(8, 5.5, 'Conflict Resolution Strategies', 
           fontsize=14, fontweight='bold', ha='center')
    
    strategies = [
        ("Last Write Wins", 2, 4.5, "#ffcdd2", "Use timestamp to resolve conflicts"),
        ("Vector Clocks", 6, 4.5, "#f8bbd9", "Causal ordering of events"),
        ("Application-Specific", 10, 4.5, "#e1f5fe", "Custom merge functions"),
        ("Multi-Value", 14, 4.5, "#fff3e0", "Keep all conflicting values")
    ]
    
    for name, x, y, color, desc in strategies:
        strategy_box = FancyBboxPatch((x-1.5, y-0.8), 3, 1.6, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(strategy_box)
        ax.text(x, y+0.3, name, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        ax.text(x, y-0.3, desc, ha='center', va='center', 
               fontsize=8)
    
    # Performance characteristics
    perf_box = FancyBboxPatch((2, 1), 12, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#f5f5f5', edgecolor='gray', linewidth=1)
    ax.add_patch(perf_box)
    
    ax.text(8, 2.2, 'Anti-Entropy Performance', fontsize=12, fontweight='bold', ha='center')
    perf_metrics = [
        "• Convergence Time: O(log N) rounds for full synchronization",
        "• Network Overhead: Configurable based on sync frequency and fanout",
        "• Partition Tolerance: Automatic recovery when network heals",
        "• Scalability: Constant per-node overhead regardless of cluster size"
    ]
    
    for i, metric in enumerate(perf_metrics):
        ax.text(2.5, 1.9 - i*0.2, metric, fontsize=9, va='center')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('anti_entropy.png', dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all gossip protocol diagrams"""
    print("🎨 Rendering Gossip Protocol diagrams...")
    
    diagrams = [
        ("Gossip Network Topology", create_gossip_network_diagram),
        ("Epidemic Information Spread", create_epidemic_spread_diagram),
        ("SWIM Protocol", create_swim_protocol_diagram),
        ("Anti-Entropy Synchronization", create_anti_entropy_diagram)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All gossip protocol diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
