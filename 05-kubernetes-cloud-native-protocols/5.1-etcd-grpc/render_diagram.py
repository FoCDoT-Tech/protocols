#!/usr/bin/env python3
"""
Render etcd gRPC Architecture Diagrams
Generates visual diagrams for etcd cluster architecture and operations.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_etcd_architecture_diagram():
    """Create etcd cluster architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Colors
    leader_color = '#ff9999'
    follower_color = '#99ccff'
    client_color = '#99ff99'
    grpc_color = '#ffcc99'
    
    # etcd Cluster
    cluster_box = FancyBboxPatch((1, 3), 10, 5, boxstyle="round,pad=0.1", 
                                facecolor='lightgray', edgecolor='black', linewidth=2)
    ax.add_patch(cluster_box)
    ax.text(6, 7.5, 'etcd Cluster (Raft)', ha='center', va='center', fontsize=14, fontweight='bold')
    
    # etcd Nodes
    # Leader Node
    leader_box = FancyBboxPatch((1.5, 5.5), 2.5, 2, boxstyle="round,pad=0.05",
                               facecolor=leader_color, edgecolor='red', linewidth=2)
    ax.add_patch(leader_box)
    ax.text(2.75, 6.8, 'etcd-1', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(2.75, 6.5, '(Leader)', ha='center', va='center', fontsize=9)
    ax.text(2.75, 6.2, 'gRPC Server', ha='center', va='center', fontsize=8)
    ax.text(2.75, 5.9, 'Raft Engine', ha='center', va='center', fontsize=8)
    ax.text(2.75, 5.6, 'KV Store', ha='center', va='center', fontsize=8)
    
    # Follower Nodes
    follower1_box = FancyBboxPatch((4.5, 5.5), 2.5, 2, boxstyle="round,pad=0.05",
                                  facecolor=follower_color, edgecolor='blue', linewidth=1)
    ax.add_patch(follower1_box)
    ax.text(5.75, 6.8, 'etcd-2', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(5.75, 6.5, '(Follower)', ha='center', va='center', fontsize=9)
    ax.text(5.75, 6.2, 'gRPC Server', ha='center', va='center', fontsize=8)
    ax.text(5.75, 5.9, 'Raft Engine', ha='center', va='center', fontsize=8)
    ax.text(5.75, 5.6, 'KV Store', ha='center', va='center', fontsize=8)
    
    follower2_box = FancyBboxPatch((7.5, 5.5), 2.5, 2, boxstyle="round,pad=0.05",
                                  facecolor=follower_color, edgecolor='blue', linewidth=1)
    ax.add_patch(follower2_box)
    ax.text(8.75, 6.8, 'etcd-3', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(8.75, 6.5, '(Follower)', ha='center', va='center', fontsize=9)
    ax.text(8.75, 6.2, 'gRPC Server', ha='center', va='center', fontsize=8)
    ax.text(8.75, 5.9, 'Raft Engine', ha='center', va='center', fontsize=8)
    ax.text(8.75, 5.6, 'KV Store', ha='center', va='center', fontsize=8)
    
    # Raft Replication arrows
    # Leader to Follower 1
    ax.annotate('', xy=(4.3, 6.5), xytext=(4.2, 6.5),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(4.25, 6.8, 'Log\nReplication', ha='center', va='center', fontsize=7, color='red')
    
    # Leader to Follower 2
    ax.annotate('', xy=(7.3, 6.5), xytext=(7.2, 6.5),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(7.25, 6.8, 'Log\nReplication', ha='center', va='center', fontsize=7, color='red')
    
    # Kubernetes Control Plane
    k8s_box = FancyBboxPatch((1, 9), 10, 1.5, boxstyle="round,pad=0.1",
                            facecolor='lightblue', edgecolor='navy', linewidth=2)
    ax.add_patch(k8s_box)
    ax.text(6, 9.75, 'Kubernetes Control Plane', ha='center', va='center', fontsize=14, fontweight='bold')
    
    # K8s Components
    api_box = FancyBboxPatch((1.5, 9.2), 2, 1.1, boxstyle="round,pad=0.05",
                            facecolor='white', edgecolor='navy', linewidth=1)
    ax.add_patch(api_box)
    ax.text(2.5, 9.75, 'API Server', ha='center', va='center', fontsize=10, fontweight='bold')
    
    ctrl_box = FancyBboxPatch((4, 9.2), 2, 1.1, boxstyle="round,pad=0.05",
                             facecolor='white', edgecolor='navy', linewidth=1)
    ax.add_patch(ctrl_box)
    ax.text(5, 9.75, 'Controllers', ha='center', va='center', fontsize=10, fontweight='bold')
    
    sched_box = FancyBboxPatch((6.5, 9.2), 2, 1.1, boxstyle="round,pad=0.05",
                              facecolor='white', edgecolor='navy', linewidth=1)
    ax.add_patch(sched_box)
    ax.text(7.5, 9.75, 'Scheduler', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # gRPC connections from K8s to etcd
    ax.annotate('', xy=(2.75, 8.8), xytext=(2.5, 9.2),
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax.text(2.2, 8.5, 'gRPC/HTTP2', ha='center', va='center', fontsize=8, color='green', rotation=70)
    
    ax.annotate('', xy=(2.75, 8.8), xytext=(5, 9.2),
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax.text(4, 8.5, 'gRPC/HTTP2', ha='center', va='center', fontsize=8, color='green', rotation=45)
    
    ax.annotate('', xy=(2.75, 8.8), xytext=(7.5, 9.2),
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax.text(5.5, 8.5, 'gRPC/HTTP2', ha='center', va='center', fontsize=8, color='green', rotation=30)
    
    # Client Operations
    client_box = FancyBboxPatch((1, 1), 10, 1.5, boxstyle="round,pad=0.1",
                               facecolor=client_color, edgecolor='darkgreen', linewidth=2)
    ax.add_patch(client_box)
    ax.text(6, 1.75, 'Client Operations', ha='center', va='center', fontsize=14, fontweight='bold')
    
    # Operation types
    put_box = FancyBboxPatch((1.5, 1.2), 1.8, 1.1, boxstyle="round,pad=0.05",
                            facecolor='white', edgecolor='darkgreen', linewidth=1)
    ax.add_patch(put_box)
    ax.text(2.4, 1.75, 'Put\nRequest', ha='center', va='center', fontsize=9, fontweight='bold')
    
    get_box = FancyBboxPatch((3.6, 1.2), 1.8, 1.1, boxstyle="round,pad=0.05",
                            facecolor='white', edgecolor='darkgreen', linewidth=1)
    ax.add_patch(get_box)
    ax.text(4.5, 1.75, 'Get\nRequest', ha='center', va='center', fontsize=9, fontweight='bold')
    
    watch_box = FancyBboxPatch((5.7, 1.2), 1.8, 1.1, boxstyle="round,pad=0.05",
                              facecolor='white', edgecolor='darkgreen', linewidth=1)
    ax.add_patch(watch_box)
    ax.text(6.6, 1.75, 'Watch\nStream', ha='center', va='center', fontsize=9, fontweight='bold')
    
    txn_box = FancyBboxPatch((7.8, 1.2), 1.8, 1.1, boxstyle="round,pad=0.05",
                            facecolor='white', edgecolor='darkgreen', linewidth=1)
    ax.add_patch(txn_box)
    ax.text(8.7, 1.75, 'Transaction', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Client to etcd connections
    ax.annotate('', xy=(2.75, 5.3), xytext=(2.4, 2.3),
                arrowprops=dict(arrowstyle='->', color='purple', lw=2))
    
    ax.annotate('', xy=(2.75, 5.3), xytext=(4.5, 2.3),
                arrowprops=dict(arrowstyle='->', color='purple', lw=2))
    
    ax.annotate('', xy=(2.75, 5.3), xytext=(6.6, 2.3),
                arrowprops=dict(arrowstyle='->', color='purple', lw=2))
    
    ax.annotate('', xy=(2.75, 5.3), xytext=(8.7, 2.3),
                arrowprops=dict(arrowstyle='->', color='purple', lw=2))
    
    # Read-only connections to followers
    ax.annotate('', xy=(5.75, 5.3), xytext=(4.5, 2.3),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1, linestyle='dashed'))
    ax.text(5, 3.5, 'Read-only', ha='center', va='center', fontsize=7, color='gray', rotation=45)
    
    ax.annotate('', xy=(8.75, 5.3), xytext=(6.6, 2.3),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1, linestyle='dashed'))
    ax.text(7.5, 3.5, 'Read-only', ha='center', va='center', fontsize=7, color='gray', rotation=45)
    
    # WAL and Storage
    wal_box = FancyBboxPatch((1.5, 3.5), 2.5, 0.8, boxstyle="round,pad=0.05",
                            facecolor='lightyellow', edgecolor='orange', linewidth=1)
    ax.add_patch(wal_box)
    ax.text(2.75, 3.9, 'Write-Ahead Log', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Connection from leader to WAL
    ax.annotate('', xy=(2.75, 4.3), xytext=(2.75, 5.5),
                arrowprops=dict(arrowstyle='->', color='orange', lw=1))
    
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 11)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('etcd Cluster Architecture with gRPC', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('etcd_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ etcd Architecture completed")

def create_grpc_operations_diagram():
    """Create gRPC operations flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Client
    client_box = FancyBboxPatch((1, 6), 2, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='darkgreen', linewidth=2)
    ax.add_patch(client_box)
    ax.text(2, 6.75, 'gRPC Client', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # etcd Server
    server_box = FancyBboxPatch((8, 6), 2, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='darkblue', linewidth=2)
    ax.add_patch(server_box)
    ax.text(9, 6.75, 'etcd Server', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Operations
    operations = [
        ('Put(/key, value)', 5.5, 'green'),
        ('Get(/key)', 4.5, 'blue'),
        ('Watch(/prefix)', 3.5, 'purple'),
        ('Transaction', 2.5, 'red'),
        ('Lease Grant/Revoke', 1.5, 'orange')
    ]
    
    for i, (op, y, color) in enumerate(operations):
        # Request arrow
        ax.annotate('', xy=(7.8, y), xytext=(3.2, y),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2))
        ax.text(5.5, y + 0.1, op, ha='center', va='bottom', fontsize=10, color=color, fontweight='bold')
        
        # Response arrow
        ax.annotate('', xy=(3.2, y - 0.3), xytext=(7.8, y - 0.3),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1, linestyle='dashed'))
        ax.text(5.5, y - 0.4, 'Response', ha='center', va='top', fontsize=8, color=color)
    
    # HTTP/2 and Protocol Buffers
    protocol_box = FancyBboxPatch((4.5, 0.2), 2, 0.6, boxstyle="round,pad=0.05",
                                 facecolor='lightyellow', edgecolor='gold', linewidth=1)
    ax.add_patch(protocol_box)
    ax.text(5.5, 0.5, 'HTTP/2 + ProtoBuf', ha='center', va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title('etcd gRPC Operations Flow', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('grpc_operations.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ gRPC Operations completed")

def create_raft_consensus_diagram():
    """Create Raft consensus flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    
    # Timeline
    ax.plot([1, 13], [4, 4], 'k-', linewidth=2)
    ax.text(7, 3.5, 'Time →', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Nodes
    nodes = ['Leader', 'Follower 1', 'Follower 2']
    colors = ['red', 'blue', 'blue']
    
    for i, (node, color) in enumerate(zip(nodes, colors)):
        y = 6 - i * 1.5
        ax.plot([1, 13], [y, y], color=color, linewidth=3, alpha=0.3)
        ax.text(0.5, y, node, ha='right', va='center', fontsize=12, fontweight='bold', color=color)
    
    # Raft operations
    operations = [
        (2, 'Client Request', 'green'),
        (3, 'Append Entry', 'red'),
        (4, 'Replicate to Followers', 'orange'),
        (6, 'Majority Acknowledgment', 'blue'),
        (8, 'Commit Entry', 'green'),
        (10, 'Apply to State Machine', 'purple'),
        (12, 'Response to Client', 'green')
    ]
    
    for x, op, color in operations:
        # Vertical line
        ax.plot([x, x], [3.5, 7], color=color, linewidth=2, alpha=0.7)
        ax.text(x, 7.2, op, ha='center', va='bottom', fontsize=9, color=color, fontweight='bold', rotation=45)
        
        # Operation markers
        if 'Replicate' in op:
            # Leader to followers
            ax.plot(x, 6, 'ro', markersize=8)
            ax.plot(x, 4.5, 'bo', markersize=8)
            ax.plot(x, 3, 'bo', markersize=8)
            
            # Arrows
            ax.annotate('', xy=(x + 0.5, 4.5), xytext=(x, 6),
                        arrowprops=dict(arrowstyle='->', color='orange', lw=2))
            ax.annotate('', xy=(x + 0.5, 3), xytext=(x, 6),
                        arrowprops=dict(arrowstyle='->', color='orange', lw=2))
        
        elif 'Acknowledgment' in op:
            # Followers to leader
            ax.plot(x, 6, 'ro', markersize=8)
            ax.plot(x, 4.5, 'bo', markersize=8)
            ax.plot(x, 3, 'bo', markersize=8)
            
            # Arrows
            ax.annotate('', xy=(x, 6), xytext=(x - 0.5, 4.5),
                        arrowprops=dict(arrowstyle='->', color='blue', lw=2))
            ax.annotate('', xy=(x, 6), xytext=(x - 0.5, 3),
                        arrowprops=dict(arrowstyle='->', color='blue', lw=2))
        
        else:
            # Single operation
            ax.plot(x, 6, 'o', color=color, markersize=8)
    
    # Consensus achieved box
    consensus_box = FancyBboxPatch((9, 1), 3, 1, boxstyle="round,pad=0.1",
                                  facecolor='lightgreen', edgecolor='darkgreen', linewidth=2)
    ax.add_patch(consensus_box)
    ax.text(10.5, 1.5, 'Consensus Achieved\nData Committed', ha='center', va='center', 
            fontsize=11, fontweight='bold')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title('Raft Consensus Protocol in etcd', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('raft_consensus.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Raft Consensus completed")

def render_all_diagrams():
    """Render all etcd gRPC diagrams"""
    print("🎨 Rendering etcd gRPC diagrams...")
    
    create_etcd_architecture_diagram()
    create_grpc_operations_diagram()
    create_raft_consensus_diagram()
    
    print("🎨 All etcd gRPC diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
