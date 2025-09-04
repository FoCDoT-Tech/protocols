#!/usr/bin/env python3
"""
Cassandra Protocol Diagram Renderer
Generates visual diagrams for Cassandra CQL protocol concepts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_cassandra_protocol_diagram():
    """Create Cassandra CQL protocol operations diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    ax.text(7, 9.5, 'Cassandra Query Protocol (CQL)', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Client section
    client_box = FancyBboxPatch((0.5, 7.5), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor="#e3f2fd", edgecolor='blue', linewidth=2)
    ax.add_patch(client_box)
    ax.text(2, 8.25, "CQL Client\n(Driver)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # Protocol operations
    operations = [
        ("STARTUP", 5, 8.5, "#e1f5fe"),
        ("QUERY", 5, 7.5, "#e8f5e8"),
        ("PREPARE", 5, 6.5, "#fff3e0"),
        ("EXECUTE", 5, 5.5, "#fce4ec"),
        ("BATCH", 5, 4.5, "#f3e5f5"),
        ("REGISTER", 5, 3.5, "#e0f2f1")
    ]
    
    for op_name, x, y, color in operations:
        op_box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                               boxstyle="round,pad=0.05", 
                               facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(op_box)
        ax.text(x, y, op_name, ha='center', va='center', 
               fontsize=9, fontweight='bold')
    
    # Cassandra cluster
    cluster_box = FancyBboxPatch((9.5, 5.5), 3.5, 3, 
                                boxstyle="round,pad=0.1", 
                                facecolor="#ffebee", edgecolor='red', linewidth=2)
    ax.add_patch(cluster_box)
    ax.text(11.25, 7, "Cassandra Cluster\n(Multi-DC)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('cassandra_protocol.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_cassandra_consistency_diagram():
    """Create Cassandra consistency levels diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    ax.text(8, 11.5, 'Cassandra Consistency Levels', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Consistency levels
    consistency_levels = [
        ("ONE", 2, 9.5, "#ffcdd2", "Fastest", "1 replica"),
        ("LOCAL_QUORUM", 5, 9.5, "#c8e6c9", "Balanced", "Local DC majority"),
        ("QUORUM", 8, 9.5, "#bbdefb", "Strong", "Global majority"),
        ("ALL", 11, 9.5, "#f8bbd9", "Strongest", "All replicas"),
        ("ANY", 14, 9.5, "#fff3e0", "Eventual", "Hinted handoff OK")
    ]
    
    for level, x, y, color, speed, desc in consistency_levels:
        level_box = FancyBboxPatch((x-1, y-0.8), 2, 1.6, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=color, edgecolor='gray', linewidth=2)
        ax.add_patch(level_box)
        ax.text(x, y+0.3, level, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        ax.text(x, y-0.1, speed, ha='center', va='center', 
               fontsize=8, style='italic')
        ax.text(x, y-0.5, desc, ha='center', va='center', 
               fontsize=8)
    
    # Latency vs Consistency trade-off
    ax.text(8, 7.5, 'Latency vs Consistency Trade-off', 
           fontsize=14, fontweight='bold', ha='center')
    
    # Draw arrow showing trade-off
    ax.annotate('', xy=(13, 6.5), xytext=(3, 6.5),
               arrowprops=dict(arrowstyle='<->', color='red', lw=3))
    ax.text(3, 6, 'Lower Latency\nWeaker Consistency', ha='center', va='center', 
           fontsize=10, color='red')
    ax.text(13, 6, 'Higher Latency\nStronger Consistency', ha='center', va='center', 
           fontsize=10, color='red')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('cassandra_consistency.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_cassandra_architecture_diagram():
    """Create Cassandra cluster architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    ax.text(8, 11.5, 'Cassandra Cluster Architecture', 
           fontsize=16, fontweight='bold', ha='center')
    
    # US-East datacenter
    ax.text(3, 10.5, 'US-East Datacenter', fontsize=14, fontweight='bold', ha='center')
    
    us_east_nodes = [
        ("Node 1", 1.5, 8.5, "#ffcdd2"),
        ("Node 2", 3, 8.5, "#c8e6c9"),
        ("Node 3", 4.5, 8.5, "#bbdefb")
    ]
    
    for name, x, y, color in us_east_nodes:
        node_box = FancyBboxPatch((x-0.6, y-0.5), 1.2, 1, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, edgecolor='gray', linewidth=2)
        ax.add_patch(node_box)
        ax.text(x, y, name, ha='center', va='center', 
               fontsize=9, fontweight='bold')
    
    # US-West datacenter
    ax.text(13, 10.5, 'US-West Datacenter', fontsize=14, fontweight='bold', ha='center')
    
    us_west_nodes = [
        ("Node 4", 11.5, 8.5, "#ffcdd2"),
        ("Node 5", 13, 8.5, "#c8e6c9"),
        ("Node 6", 14.5, 8.5, "#bbdefb")
    ]
    
    for name, x, y, color in us_west_nodes:
        node_box = FancyBboxPatch((x-0.6, y-0.5), 1.2, 1, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, edgecolor='gray', linewidth=2)
        ax.add_patch(node_box)
        ax.text(x, y, name, ha='center', va='center', 
               fontsize=9, fontweight='bold')
    
    # Token ring visualization
    ax.text(8, 6.5, 'Token Ring Distribution', fontsize=14, fontweight='bold', ha='center')
    
    # Draw token ring
    center_x, center_y = 8, 4.5
    radius = 2
    
    circle = plt.Circle((center_x, center_y), radius, fill=False, 
                       edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    
    # Token ranges
    angles = np.linspace(0, 2*np.pi, 7)
    tokens = ["-9223...808", "-6148...205", "-3074...602", "0...603", 
              "3074...206", "6148...807"]
    
    for i, (angle, token) in enumerate(zip(angles[:-1], tokens)):
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        
        ax.plot([center_x, x], [center_y, y], 'k-', alpha=0.3)
        ax.text(x*1.2-center_x*0.2, y*1.2-center_y*0.2, f"Node {i+1}\n{token}", 
               ha='center', va='center', fontsize=7,
               bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('cassandra_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_cassandra_performance_diagram():
    """Create Cassandra performance characteristics diagram"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Cassandra Performance Analysis', fontsize=16, fontweight='bold')
    
    # Write throughput scaling
    nodes = [1, 3, 6, 12, 24, 48]
    write_throughput = [25000, 75000, 150000, 300000, 600000, 1200000]
    
    ax1.plot(nodes, write_throughput, 'b-o', linewidth=3, markersize=8)
    ax1.set_xlabel('Number of Nodes')
    ax1.set_ylabel('Write Throughput (ops/sec)')
    ax1.set_title('Linear Write Scaling')
    ax1.grid(True, alpha=0.3)
    
    # Consistency level latency
    consistency_levels = ['ONE', 'LOCAL_QUORUM', 'QUORUM', 'ALL']
    read_latency = [1.2, 3.5, 8.7, 25.4]
    write_latency = [0.8, 2.1, 6.3, 18.9]
    
    x = np.arange(len(consistency_levels))
    width = 0.35
    
    ax2.bar(x - width/2, read_latency, width, label='Read', color='#4caf50')
    ax2.bar(x + width/2, write_latency, width, label='Write', color='#2196f3')
    ax2.set_ylabel('Latency (ms)')
    ax2.set_title('Consistency vs Latency')
    ax2.set_xticks(x)
    ax2.set_xticklabels(consistency_levels)
    ax2.legend()
    
    # Compression effectiveness
    compression_types = ['None', 'LZ4', 'Snappy', 'DEFLATE']
    compressed_size = [100, 35, 40, 25]
    
    ax3.bar(compression_types, compressed_size, color='#ff9800')
    ax3.set_ylabel('Compressed Size (%)')
    ax3.set_title('Protocol Compression')
    
    # Multi-DC replication latency
    datacenters = ['Local', 'Cross-Region', 'Cross-Continent']
    replication_latency = [2.1, 45.3, 180.7]
    
    ax4.bar(datacenters, replication_latency, color='#9c27b0')
    ax4.set_ylabel('Replication Latency (ms)')
    ax4.set_title('Multi-Datacenter Performance')
    
    plt.tight_layout()
    plt.savefig('cassandra_performance.png', dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all Cassandra protocol diagrams"""
    print("🎨 Rendering Cassandra CQL Protocol diagrams...")
    
    diagrams = [
        ("Cassandra Protocol", create_cassandra_protocol_diagram),
        ("Cassandra Consistency", create_cassandra_consistency_diagram),
        ("Cassandra Architecture", create_cassandra_architecture_diagram),
        ("Cassandra Performance", create_cassandra_performance_diagram)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All Cassandra protocol diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
