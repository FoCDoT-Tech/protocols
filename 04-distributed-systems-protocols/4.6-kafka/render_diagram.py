#!/usr/bin/env python3
"""
Kafka Diagram Renderer
Generates visual diagrams for Kafka streaming platform concepts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, ConnectionPatch, Arrow
import numpy as np

def create_kafka_architecture_diagram():
    """Create Kafka cluster architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    
    ax.text(9, 11.5, 'Kafka Distributed Streaming Platform', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Kafka Cluster
    cluster_box = FancyBboxPatch((1, 8), 16, 2.5, 
                                boxstyle="round,pad=0.2", 
                                facecolor='#e1f5fe', edgecolor='#01579b', linewidth=2)
    ax.add_patch(cluster_box)
    ax.text(9, 10, 'Kafka Cluster', fontsize=14, fontweight='bold', ha='center')
    
    # Brokers
    brokers = [
        ("Broker 1", 3, 9, "Leader: orders-0"),
        ("Broker 2", 9, 9, "Leader: orders-1"),
        ("Broker 3", 15, 9, "Leader: orders-2")
    ]
    
    for name, x, y, role in brokers:
        broker_box = FancyBboxPatch((x-1.2, y-0.6), 2.4, 1.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='#e8f5e8', edgecolor='#2e7d32', linewidth=1)
        ax.add_patch(broker_box)
        ax.text(x, y+0.2, name, fontsize=10, fontweight='bold', ha='center')
        ax.text(x, y-0.3, role, fontsize=8, ha='center', style='italic')
    
    # ZooKeeper
    zk_box = FancyBboxPatch((7.5, 7), 3, 0.8, 
                           boxstyle="round,pad=0.1", 
                           facecolor='#fff3e0', edgecolor='#ef6c00', linewidth=1)
    ax.add_patch(zk_box)
    ax.text(9, 7.4, 'ZooKeeper Ensemble', fontsize=10, fontweight='bold', ha='center')
    ax.text(9, 7.1, 'Cluster Coordination', fontsize=8, ha='center', style='italic')
    
    # Topics and Partitions
    ax.text(4, 6.2, 'Topic: orders (3 partitions)', fontsize=12, fontweight='bold', ha='left')
    
    partitions = [
        ("P0", 2, 5.5, "Replicas: [1,2,3]", "#ffcdd2"),
        ("P1", 6, 5.5, "Replicas: [2,3,1]", "#c8e6c9"),
        ("P2", 10, 5.5, "Replicas: [3,1,2]", "#ffe0b2")
    ]
    
    for name, x, y, replicas, color in partitions:
        part_box = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(part_box)
        ax.text(x, y+0.1, name, fontsize=9, fontweight='bold', ha='center')
        ax.text(x, y-0.2, replicas, fontsize=7, ha='center', style='italic')
    
    # Producers
    ax.text(1, 4, 'Producers', fontsize=12, fontweight='bold', ha='left')
    
    producers = [
        ("Order Service", 2, 3.2, "#e1f5fe"),
        ("Payment Service", 2, 2.4, "#e8f5e8"),
        ("User Service", 2, 1.6, "#fff3e0")
    ]
    
    for name, x, y, color in producers:
        prod_box = FancyBboxPatch((x-1, y-0.3), 2, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(prod_box)
        ax.text(x, y, name, fontsize=9, fontweight='bold', ha='center')
    
    # Consumer Groups
    ax.text(13, 4, 'Consumer Groups', fontsize=12, fontweight='bold', ha='left')
    
    # Group 1
    group1_box = FancyBboxPatch((12, 2.8), 5, 1.2, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#f3e5f5', edgecolor='#7b1fa2', linewidth=1)
    ax.add_patch(group1_box)
    ax.text(14.5, 3.7, 'order-processing-group', fontsize=10, fontweight='bold', ha='center')
    
    consumers1 = [
        ("C1", 13, 3.2),
        ("C2", 14.5, 3.2),
        ("C3", 16, 3.2)
    ]
    
    for name, x, y in consumers1:
        cons_box = FancyBboxPatch((x-0.3, y-0.2), 0.6, 0.4, 
                                 boxstyle="round,pad=0.02", 
                                 facecolor='white', edgecolor='gray', linewidth=1)
        ax.add_patch(cons_box)
        ax.text(x, y, name, fontsize=8, fontweight='bold', ha='center')
    
    # Group 2
    group2_box = FancyBboxPatch((12, 1.2), 5, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#e0f2f1', edgecolor='#2e7d32', linewidth=1)
    ax.add_patch(group2_box)
    ax.text(14.5, 1.8, 'analytics-group', fontsize=10, fontweight='bold', ha='center')
    
    consumers2 = [
        ("A1", 13.5, 1.4),
        ("A2", 15.5, 1.4)
    ]
    
    for name, x, y in consumers2:
        cons_box = FancyBboxPatch((x-0.3, y-0.2), 0.6, 0.4, 
                                 boxstyle="round,pad=0.02", 
                                 facecolor='white', edgecolor='gray', linewidth=1)
        ax.add_patch(cons_box)
        ax.text(x, y, name, fontsize=8, fontweight='bold', ha='center')
    
    # Connection arrows
    connections = [
        # Producers to brokers
        ((3, 3.2), (3, 8.4)),
        ((3, 2.4), (9, 8.4)),
        ((3, 1.6), (15, 8.4)),
        
        # Brokers to ZooKeeper
        ((3, 8.4), (8, 7.4)),
        ((9, 8.4), (9, 7.8)),
        ((15, 8.4), (10, 7.4)),
        
        # Partitions to brokers
        ((2, 6.3), (3, 8.4)),
        ((6, 6.3), (9, 8.4)),
        ((10, 6.3), (15, 8.4)),
        
        # Brokers to consumers
        ((3, 8.4), (13, 3.2)),
        ((9, 8.4), (14.5, 3.2)),
        ((15, 8.4), (16, 3.2)),
        ((9, 8.4), (13.5, 1.4)),
        ((15, 8.4), (15.5, 1.4))
    ]
    
    for (x1, y1), (x2, y2) in connections:
        arrow = ConnectionPatch((x1, y1), (x2, y2), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=10, fc="gray", ec="gray", alpha=0.6)
        ax.add_patch(arrow)
    
    # Legend
    legend_box = FancyBboxPatch((0.5, 0.2), 8, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#f5f5f5', edgecolor='gray', linewidth=1)
    ax.add_patch(legend_box)
    
    ax.text(4.5, 0.8, 'Message Flow', fontsize=10, fontweight='bold', ha='center')
    ax.text(1, 0.5, '→ Produce', fontsize=8, ha='left', color='blue')
    ax.text(3, 0.5, '→ Replicate', fontsize=8, ha='left', color='green')
    ax.text(5, 0.5, '→ Consume', fontsize=8, ha='left', color='purple')
    ax.text(7, 0.5, '→ Coordinate', fontsize=8, ha='left', color='orange')
    
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('kafka_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_partition_replication_diagram():
    """Create partition replication and leader election diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'Kafka Partition Replication & Leader Election', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Topic partition
    topic_box = FancyBboxPatch((6, 8), 4, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#e8f5e8', edgecolor='#2e7d32', linewidth=2)
    ax.add_patch(topic_box)
    ax.text(8, 8.5, 'orders-topic-partition-0', fontsize=12, fontweight='bold', ha='center')
    
    # Broker replicas
    brokers = [
        ("Broker 1 (Leader)", 2, 6, "#ffcdd2", "Leader"),
        ("Broker 2 (Follower)", 8, 6, "#c8e6c9", "In-Sync Replica"),
        ("Broker 3 (Follower)", 14, 6, "#ffe0b2", "In-Sync Replica")
    ]
    
    for name, x, y, color, role in brokers:
        broker_box = FancyBboxPatch((x-1.5, y-1), 3, 2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(broker_box)
        ax.text(x, y+0.5, name, fontsize=10, fontweight='bold', ha='center')
        ax.text(x, y, role, fontsize=9, ha='center', style='italic')
        
        # Log segments
        for i, offset in enumerate([100, 101, 102]):
            log_box = Rectangle((x-1.2 + i*0.8, y-0.7), 0.7, 0.3, 
                               facecolor='white', edgecolor='black', linewidth=1)
            ax.add_patch(log_box)
            ax.text(x-0.85 + i*0.8, y-0.55, str(offset), fontsize=8, ha='center')
    
    # Producer
    producer_box = FancyBboxPatch((1, 3), 2, 1, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#e1f5fe', edgecolor='#01579b', linewidth=1)
    ax.add_patch(producer_box)
    ax.text(2, 3.5, 'Producer', fontsize=10, fontweight='bold', ha='center')
    
    # Consumer
    consumer_box = FancyBboxPatch((13, 3), 2, 1, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#f3e5f5', edgecolor='#7b1fa2', linewidth=1)
    ax.add_patch(consumer_box)
    ax.text(14, 3.5, 'Consumer', fontsize=10, fontweight='bold', ha='center')
    
    # Arrows
    # Producer to leader
    arrow1 = ConnectionPatch((2, 4), (2, 5), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5,
                            mutation_scale=12, fc="blue", ec="blue")
    ax.add_patch(arrow1)
    ax.text(2.5, 4.5, 'Produce\n(acks=all)', fontsize=8, ha='left')
    
    # Leader to followers (replication)
    arrow2 = ConnectionPatch((3.5, 6), (6.5, 6), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5,
                            mutation_scale=12, fc="green", ec="green")
    ax.add_patch(arrow2)
    ax.text(5, 6.3, 'Replicate', fontsize=8, ha='center')
    
    arrow3 = ConnectionPatch((3.5, 6), (12.5, 6), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5,
                            mutation_scale=12, fc="green", ec="green")
    ax.add_patch(arrow3)
    ax.text(8, 6.8, 'Replicate', fontsize=8, ha='center')
    
    # Leader to consumer
    arrow4 = ConnectionPatch((2, 5), (14, 4), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5,
                            mutation_scale=12, fc="purple", ec="purple")
    ax.add_patch(arrow4)
    ax.text(8, 4.5, 'Consume\n(from leader only)', fontsize=8, ha='center')
    
    # Replication flow
    ax.text(8, 2, 'Replication Flow', fontsize=14, fontweight='bold', ha='center')
    
    flow_steps = [
        ("1. Producer sends", 1, 1, "#e1f5fe"),
        ("2. Leader writes", 4, 1, "#ffcdd2"),
        ("3. Followers fetch", 7, 1, "#c8e6c9"),
        ("4. Leader commits", 10, 1, "#ffe0b2"),
        ("5. Consumer reads", 13, 1, "#f3e5f5")
    ]
    
    for i, (step, x, y, color) in enumerate(flow_steps):
        step_box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(step_box)
        ax.text(x, y, step, fontsize=8, fontweight='bold', ha='center')
        
        # Arrow to next step
        if i < len(flow_steps) - 1:
            next_x = flow_steps[i + 1][1]
            arrow = ConnectionPatch((x + 0.8, y), (next_x - 0.8, y), "data", "data",
                                   arrowstyle="->", shrinkA=2, shrinkB=2,
                                   mutation_scale=10, fc="gray", ec="gray")
            ax.add_patch(arrow)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('partition_replication.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_stream_processing_diagram():
    """Create Kafka Streams processing topology diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'Kafka Streams Processing Topology', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Input topics
    input_topics = [
        ("raw-events", 2, 8, "#e1f5fe"),
        ("user-profiles", 2, 7, "#e8f5e8")
    ]
    
    for name, x, y, color in input_topics:
        topic_box = FancyBboxPatch((x-1, y-0.3), 2, 0.6, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(topic_box)
        ax.text(x, y, name, fontsize=9, fontweight='bold', ha='center')
    
    # Stream processors
    processors = [
        ("Filter", 5, 8, "filter valid events", "#ffcdd2"),
        ("Map", 5, 7, "enrich with metadata", "#c8e6c9"),
        ("Join", 8, 7.5, "join events + profiles", "#ffe0b2"),
        ("Aggregate", 11, 7.5, "windowed count", "#f8bbd9"),
        ("Branch", 8, 6, "route by type", "#e0f2f1")
    ]
    
    for name, x, y, desc, color in processors:
        proc_box = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(proc_box)
        ax.text(x, y+0.1, name, fontsize=9, fontweight='bold', ha='center')
        ax.text(x, y-0.2, desc, fontsize=7, ha='center', style='italic')
    
    # State stores
    stores = [
        ("User Store", 11, 6, "#fff3e0"),
        ("Window Store", 11, 5, "#f3e5f5")
    ]
    
    for name, x, y, color in stores:
        store_box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(store_box)
        ax.text(x, y, name, fontsize=8, fontweight='bold', ha='center')
    
    # Output topics
    output_topics = [
        ("processed-events", 6, 4, "#e1f5fe"),
        ("user-metrics", 10, 4, "#e8f5e8"),
        ("alerts", 14, 4, "#ffebee")
    ]
    
    for name, x, y, color in output_topics:
        topic_box = FancyBboxPatch((x-1, y-0.3), 2, 0.6, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(topic_box)
        ax.text(x, y, name, fontsize=9, fontweight='bold', ha='center')
    
    # Processing flow arrows
    flow_connections = [
        # Input to processors
        ((3, 8), (4.2, 8)),
        ((3, 7), (4.2, 7)),
        
        # Processor chain
        ((5.8, 8), (7.2, 7.7)),
        ((5.8, 7), (7.2, 7.3)),
        ((8.8, 7.5), (10.2, 7.5)),
        ((8, 6.6), (8, 6.4)),
        
        # To outputs
        ((8, 5.6), (6, 4.3)),
        ((8, 5.6), (10, 4.3)),
        ((8, 5.6), (14, 4.3)),
        
        # State store connections
        ((8.8, 7.3), (10.2, 6)),
        ((11.8, 7.3), (11, 5.6))
    ]
    
    for (x1, y1), (x2, y2) in flow_connections:
        arrow = ConnectionPatch((x1, y1), (x2, y2), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=10, fc="blue", ec="blue", alpha=0.7)
        ax.add_patch(arrow)
    
    # Windowing example
    ax.text(2, 3, 'Windowing Example', fontsize=12, fontweight='bold', ha='left')
    
    # Time windows
    windows = [
        ("Window 1\n10:00-10:05", 2, 2, "#e1f5fe"),
        ("Window 2\n10:05-10:10", 4.5, 2, "#e8f5e8"),
        ("Window 3\n10:10-10:15", 7, 2, "#fff3e0")
    ]
    
    for name, x, y, color in windows:
        win_box = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8, 
                                boxstyle="round,pad=0.05", 
                                facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(win_box)
        ax.text(x, y, name, fontsize=8, fontweight='bold', ha='center')
    
    # Events in windows
    events = [
        (2, 1.3, "3 events"),
        (4.5, 1.3, "7 events"),
        (7, 1.3, "2 events")
    ]
    
    for x, y, count in events:
        ax.text(x, y, count, fontsize=8, ha='center', style='italic')
    
    # Aggregation result
    result_box = FancyBboxPatch((10, 1.7), 2, 0.6, 
                               boxstyle="round,pad=0.05", 
                               facecolor='#f3e5f5', edgecolor='gray', linewidth=1)
    ax.add_patch(result_box)
    ax.text(11, 2, 'Aggregated\nResults', fontsize=8, fontweight='bold', ha='center')
    
    # Arrows to aggregation
    for x in [2, 4.5, 7]:
        arrow = ConnectionPatch((x, 1.6), (10, 2), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=8, fc="purple", ec="purple", alpha=0.6)
        ax.add_patch(arrow)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('stream_processing.png', dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all Kafka diagrams"""
    print("🎨 Rendering Kafka diagrams...")
    
    diagrams = [
        ("Kafka Architecture", create_kafka_architecture_diagram),
        ("Partition Replication", create_partition_replication_diagram),
        ("Stream Processing", create_stream_processing_diagram)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All Kafka diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
