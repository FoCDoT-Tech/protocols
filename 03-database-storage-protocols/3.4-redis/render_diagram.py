#!/usr/bin/env python3
"""
Redis RESP Protocol Diagram Renderer
Generates visual diagrams for Redis RESP protocol concepts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_redis_protocol_diagram():
    """Create Redis RESP protocol operations diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    ax.text(7, 9.5, 'Redis RESP Protocol Operations', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Client section
    client_box = FancyBboxPatch((0.5, 7.5), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor="#e3f2fd", edgecolor='blue', linewidth=2)
    ax.add_patch(client_box)
    ax.text(2, 8.25, "Redis Client\n(RESP)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # Protocol operations
    operations = [
        ("GET/SET", 5, 8.5, "#e1f5fe"),
        ("HGET/HSET", 5, 7.5, "#e8f5e8"),
        ("LPUSH/RPOP", 5, 6.5, "#fff3e0"),
        ("SADD/SMEMBERS", 5, 5.5, "#fce4ec"),
        ("ZADD/ZRANGE", 5, 4.5, "#f3e5f5"),
        ("PUB/SUB", 5, 3.5, "#e0f2f1")
    ]
    
    for op_name, x, y, color in operations:
        op_box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                               boxstyle="round,pad=0.05", 
                               facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(op_box)
        ax.text(x, y, op_name, ha='center', va='center', 
               fontsize=9, fontweight='bold')
    
    # Redis server
    server_box = FancyBboxPatch((9.5, 5.5), 3.5, 3, 
                               boxstyle="round,pad=0.1", 
                               facecolor="#ffebee", edgecolor='red', linewidth=2)
    ax.add_patch(server_box)
    ax.text(11.25, 7, "Redis Server\n(In-Memory)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('redis_protocol.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_redis_data_structures_diagram():
    """Create Redis data structures diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    ax.text(8, 11.5, 'Redis Data Structures', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Data structures
    structures = [
        ("String", 2, 9.5, "#ffcdd2", "Key-Value\nCaching"),
        ("Hash", 5, 9.5, "#c8e6c9", "Object\nStorage"),
        ("List", 8, 9.5, "#bbdefb", "Queue\nStack"),
        ("Set", 11, 9.5, "#f8bbd9", "Unique\nItems"),
        ("Sorted Set", 14, 9.5, "#fff3e0", "Leaderboard\nRanking")
    ]
    
    for name, x, y, color, use_case in structures:
        struct_box = FancyBboxPatch((x-1, y-0.8), 2, 1.6, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=color, edgecolor='gray', linewidth=2)
        ax.add_patch(struct_box)
        ax.text(x, y+0.3, name, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        ax.text(x, y-0.3, use_case, ha='center', va='center', 
               fontsize=8)
    
    # Performance characteristics
    ax.text(8, 7.5, 'Performance Characteristics', 
           fontsize=14, fontweight='bold', ha='center')
    
    perf_data = [
        ("Operation", "Latency", "Throughput"),
        ("GET", "0.1ms", "100K ops/sec"),
        ("SET", "0.15ms", "85K ops/sec"),
        ("HGET", "0.12ms", "95K ops/sec"),
        ("LPUSH", "0.13ms", "90K ops/sec"),
        ("ZADD", "0.18ms", "75K ops/sec")
    ]
    
    for i, (op, lat, tput) in enumerate(perf_data):
        y_pos = 6.5 - i * 0.4
        if i == 0:  # Header
            ax.text(4, y_pos, op, ha='center', va='center', fontweight='bold')
            ax.text(8, y_pos, lat, ha='center', va='center', fontweight='bold')
            ax.text(12, y_pos, tput, ha='center', va='center', fontweight='bold')
        else:
            ax.text(4, y_pos, op, ha='center', va='center')
            ax.text(8, y_pos, lat, ha='center', va='center')
            ax.text(12, y_pos, tput, ha='center', va='center')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('redis_data_structures.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_redis_pubsub_diagram():
    """Create Redis pub/sub messaging diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'Redis Pub/Sub Messaging', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Publishers
    ax.text(2, 8.5, 'Publishers', fontsize=12, fontweight='bold', ha='center')
    
    publishers = ["Web App", "Analytics", "Logger"]
    for i, pub in enumerate(publishers):
        pub_box = FancyBboxPatch((0.5 + i*1.2, 7), 1, 0.8, 
                                boxstyle="round,pad=0.05", 
                                facecolor="#e3f2fd", edgecolor='blue', linewidth=1)
        ax.add_patch(pub_box)
        ax.text(1 + i*1.2, 7.4, pub, ha='center', va='center', fontsize=9)
    
    # Redis server
    redis_box = FancyBboxPatch((6.5, 6.5), 3, 2, 
                              boxstyle="round,pad=0.1", 
                              facecolor="#ffebee", edgecolor='red', linewidth=2)
    ax.add_patch(redis_box)
    ax.text(8, 7.5, "Redis\nPub/Sub", ha='center', va='center', 
           fontsize=12, fontweight='bold')
    
    # Subscribers
    ax.text(14, 8.5, 'Subscribers', fontsize=12, fontweight='bold', ha='center')
    
    subscribers = ["Dashboard", "Mobile App", "Email Service"]
    for i, sub in enumerate(subscribers):
        sub_box = FancyBboxPatch((12.5 + i*1.2, 7), 1, 0.8, 
                                boxstyle="round,pad=0.05", 
                                facecolor="#c8e6c9", edgecolor='green', linewidth=1)
        ax.add_patch(sub_box)
        ax.text(13 + i*1.2, 7.4, sub, ha='center', va='center', fontsize=9)
    
    # Channels
    channels = ["notifications", "analytics", "logs"]
    for i, channel in enumerate(channels):
        y_pos = 5 - i * 0.8
        ax.text(8, y_pos, f"Channel: {channel}", ha='center', va='center', 
               fontsize=10, bbox=dict(boxstyle="round,pad=0.2", facecolor="#fff3e0"))
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('redis_pubsub.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_redis_cluster_diagram():
    """Create Redis cluster architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    ax.text(8, 11.5, 'Redis Cluster Architecture', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Master nodes
    ax.text(4, 10.5, 'Master Nodes', fontsize=14, fontweight='bold', ha='center')
    
    masters = [
        ("Master 1", 2, 9, "Slots 0-5461"),
        ("Master 2", 4, 9, "Slots 5462-10922"),
        ("Master 3", 6, 9, "Slots 10923-16383")
    ]
    
    for name, x, y, slots in masters:
        master_box = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor="#ffcdd2", edgecolor='red', linewidth=2)
        ax.add_patch(master_box)
        ax.text(x, y+0.2, name, ha='center', va='center', fontsize=9, fontweight='bold')
        ax.text(x, y-0.2, slots, ha='center', va='center', fontsize=7)
    
    # Replica nodes
    ax.text(12, 10.5, 'Replica Nodes', fontsize=14, fontweight='bold', ha='center')
    
    replicas = [
        ("Replica 1", 10, 9),
        ("Replica 2", 12, 9),
        ("Replica 3", 14, 9)
    ]
    
    for name, x, y in replicas:
        replica_box = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, 
                                    boxstyle="round,pad=0.05", 
                                    facecolor="#c8e6c9", edgecolor='green', linewidth=2)
        ax.add_patch(replica_box)
        ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Replication arrows
    for i in range(3):
        master_x = 2 + i * 2
        replica_x = 10 + i * 2
        ax.annotate('', xy=(replica_x-0.8, 9), xytext=(master_x+0.8, 9),
                   arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    
    # Hash slot distribution
    ax.text(8, 6.5, 'Hash Slot Distribution (16,384 slots)', 
           fontsize=14, fontweight='bold', ha='center')
    
    # Visual representation of slot distribution
    slot_colors = ['#ffcdd2', '#c8e6c9', '#bbdefb']
    slot_widths = [5461, 5461, 5462]  # Approximately equal
    
    x_start = 2
    for i, (width, color) in enumerate(zip(slot_widths, slot_colors)):
        normalized_width = width / 16384 * 12  # Scale to fit diagram
        slot_rect = FancyBboxPatch((x_start, 5), normalized_width, 0.8, 
                                  boxstyle="round,pad=0.02", 
                                  facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(slot_rect)
        ax.text(x_start + normalized_width/2, 5.4, f"{width} slots", 
               ha='center', va='center', fontsize=8)
        x_start += normalized_width
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('redis_cluster.png', dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all Redis RESP protocol diagrams"""
    print("🎨 Rendering Redis RESP Protocol diagrams...")
    
    diagrams = [
        ("Redis Protocol", create_redis_protocol_diagram),
        ("Redis Data Structures", create_redis_data_structures_diagram),
        ("Redis Pub/Sub", create_redis_pubsub_diagram),
        ("Redis Cluster", create_redis_cluster_diagram)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All Redis protocol diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
