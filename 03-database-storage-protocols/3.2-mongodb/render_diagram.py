#!/usr/bin/env python3
"""
MongoDB Wire Protocol Diagram Renderer
Generates visual diagrams for MongoDB wire protocol concepts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_mongodb_operations_diagram():
    """Create MongoDB wire protocol operations diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    ax.text(7, 9.5, 'MongoDB Wire Protocol Operations', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Client section
    client_box = FancyBboxPatch((0.5, 7.5), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor="#e3f2fd", edgecolor='blue', linewidth=2)
    ax.add_patch(client_box)
    ax.text(2, 8.25, "MongoDB Client\n(Driver)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # Protocol operations
    operations = [
        ("OP_MSG", 5, 8.5, "#e1f5fe"),
        ("OP_QUERY", 5, 7.5, "#e8f5e8"),
        ("OP_INSERT", 5, 6.5, "#fff3e0"),
        ("OP_UPDATE", 5, 5.5, "#fce4ec"),
        ("OP_DELETE", 5, 4.5, "#f3e5f5"),
        ("OP_REPLY", 5, 3.5, "#e0f2f1")
    ]
    
    for op_name, x, y, color in operations:
        op_box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                               boxstyle="round,pad=0.05", 
                               facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(op_box)
        ax.text(x, y, op_name, ha='center', va='center', 
               fontsize=9, fontweight='bold')
    
    # MongoDB server
    server_box = FancyBboxPatch((9.5, 5.5), 3.5, 3, 
                               boxstyle="round,pad=0.1", 
                               facecolor="#ffebee", edgecolor='red', linewidth=2)
    ax.add_patch(server_box)
    ax.text(11.25, 7, "MongoDB Server\n(mongod)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('mongodb_operations.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_mongodb_architecture_diagram():
    """Create MongoDB cluster architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    ax.text(8, 11.5, 'MongoDB Cluster Architecture', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Replica Set
    ax.text(3, 10.5, 'Replica Set', fontsize=14, fontweight='bold', ha='center')
    
    primary_box = FancyBboxPatch((1.5, 8.5), 3, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor="#ffcdd2", edgecolor='red', linewidth=2)
    ax.add_patch(primary_box)
    ax.text(3, 9.25, "Primary\n(Read/Write)", ha='center', va='center', 
           fontsize=10, fontweight='bold')
    
    # Sharded Cluster
    ax.text(12, 10.5, 'Sharded Cluster', fontsize=14, fontweight='bold', ha='center')
    
    for i, x in enumerate([9.5, 11.5, 13.5]):
        mongos_box = FancyBboxPatch((x, 8.5), 1.5, 1, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor="#e1f5fe", edgecolor='blue', linewidth=2)
        ax.add_patch(mongos_box)
        ax.text(x+0.75, 9, f"mongos\n{i+1}", ha='center', va='center', 
               fontsize=9, fontweight='bold')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('mongodb_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_mongodb_performance_diagram():
    """Create MongoDB performance comparison diagram"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('MongoDB Performance Analysis', fontsize=16, fontweight='bold')
    
    # Operation latency
    operations = ['Find', 'Insert', 'Update', 'Delete', 'Aggregate']
    indexed_latency = [0.8, 1.2, 1.5, 1.1, 15.2]
    unindexed_latency = [125.3, 2.1, 89.7, 67.4, 234.8]
    
    x = np.arange(len(operations))
    width = 0.35
    
    ax1.bar(x - width/2, indexed_latency, width, label='With Index', color='#4caf50')
    ax1.bar(x + width/2, unindexed_latency, width, label='Without Index', color='#f44336')
    ax1.set_ylabel('Latency (ms)')
    ax1.set_title('Query Performance')
    ax1.set_xticks(x)
    ax1.set_xticklabels(operations)
    ax1.legend()
    ax1.set_yscale('log')
    
    # Throughput
    op_types = ['CRUD', 'Aggregation', 'Text Search', 'Geospatial']
    throughput = [85000, 12000, 8500, 15000]
    
    ax2.bar(op_types, throughput, color=['#2196f3', '#ff9800', '#9c27b0', '#00bcd4'])
    ax2.set_ylabel('Operations/sec')
    ax2.set_title('Throughput by Operation Type')
    
    # Compression
    compression_types = ['None', 'Snappy', 'zlib', 'zstd']
    compressed_size = [100, 42, 31, 28]
    
    ax3.bar(compression_types, compressed_size, color='#4caf50')
    ax3.set_ylabel('Compressed Size (%)')
    ax3.set_title('Compression Effectiveness')
    
    # Scaling
    shard_counts = [1, 2, 4, 8, 16]
    throughput_scaling = [25000, 48000, 92000, 175000, 320000]
    
    ax4.plot(shard_counts, throughput_scaling, 'b-o', linewidth=3, markersize=8)
    ax4.set_xlabel('Number of Shards')
    ax4.set_ylabel('Throughput (ops/sec)')
    ax4.set_title('Horizontal Scaling Performance')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('mongodb_performance.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_mongodb_sharding_diagram():
    """Create MongoDB sharding strategy diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'MongoDB Sharding Strategies', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Hashed sharding
    ax.text(2, 8.5, 'Hashed Sharding', fontsize=14, fontweight='bold', ha='center')
    
    hash_ranges = ['0000-3FFF', '4000-7FFF', '8000-BFFF', 'C000-FFFF']
    shard_colors = ['#ffcdd2', '#c8e6c9', '#bbdefb', '#f8bbd9']
    
    for i, (range_val, color) in enumerate(zip(hash_ranges, shard_colors)):
        shard_box = FancyBboxPatch((0.5 + i*0.8, 7), 0.7, 1, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(shard_box)
        ax.text(0.85 + i*0.8, 7.5, f"Shard {i+1}\n{range_val}", ha='center', va='center', 
               fontsize=8, fontweight='bold')
    
    # Range sharding
    ax.text(8, 8.5, 'Range Sharding', fontsize=14, fontweight='bold', ha='center')
    
    ranges = ['A-F', 'G-M', 'N-S', 'T-Z']
    for i, (range_val, color) in enumerate(zip(ranges, shard_colors)):
        shard_box = FancyBboxPatch((6.5 + i*0.8, 7), 0.7, 1, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(shard_box)
        ax.text(6.85 + i*0.8, 7.5, f"Shard {i+1}\n{range_val}", ha='center', va='center', 
               fontsize=8, fontweight='bold')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('mongodb_sharding.png', dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all MongoDB wire protocol diagrams"""
    print("🎨 Rendering MongoDB Wire Protocol diagrams...")
    
    diagrams = [
        ("MongoDB Operations", create_mongodb_operations_diagram),
        ("MongoDB Architecture", create_mongodb_architecture_diagram),
        ("MongoDB Performance", create_mongodb_performance_diagram),
        ("MongoDB Sharding", create_mongodb_sharding_diagram)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All MongoDB protocol diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
