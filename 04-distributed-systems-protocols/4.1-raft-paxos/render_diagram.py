#!/usr/bin/env python3
"""
Raft & Paxos Consensus Diagram Renderer
Generates visual diagrams for consensus algorithms.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_raft_algorithm_diagram():
    """Create Raft algorithm flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'Raft Consensus Algorithm', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Raft phases
    phases = [
        ("Leader Election", 3, 8, "#e1f5fe", "Randomized timeouts\nMajority vote required"),
        ("Log Replication", 8, 8, "#e8f5e8", "Leader receives entries\nReplicates to followers"),
        ("Commitment", 13, 8, "#fff3e0", "Majority acknowledgment\nEntry becomes committed")
    ]
    
    for name, x, y, color, details in phases:
        phase_box = FancyBboxPatch((x-1.5, y-1), 3, 2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=color, edgecolor='gray', linewidth=2)
        ax.add_patch(phase_box)
        ax.text(x, y+0.3, name, ha='center', va='center', 
               fontsize=11, fontweight='bold')
        ax.text(x, y-0.3, details, ha='center', va='center', 
               fontsize=8)
    
    # Flow arrows
    arrow1 = ConnectionPatch((4.5, 8), (6.5, 8), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5, 
                            mutation_scale=20, fc="blue", lw=2)
    ax.add_patch(arrow1)
    
    arrow2 = ConnectionPatch((9.5, 8), (11.5, 8), "data", "data",
                            arrowstyle="->", shrinkA=5, shrinkB=5, 
                            mutation_scale=20, fc="blue", lw=2)
    ax.add_patch(arrow2)
    
    # Node states
    ax.text(8, 6, 'Node States', fontsize=14, fontweight='bold', ha='center')
    
    states = [
        ("Follower", 3, 5, "#ffcdd2", "Receives heartbeats\nVotes in elections"),
        ("Candidate", 8, 5, "#f8bbd9", "Requests votes\nTries to become leader"),
        ("Leader", 13, 5, "#c8e6c9", "Sends heartbeats\nReplicates log entries")
    ]
    
    for name, x, y, color, details in states:
        state_box = FancyBboxPatch((x-1.2, y-0.8), 2.4, 1.6, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(state_box)
        ax.text(x, y+0.2, name, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        ax.text(x, y-0.3, details, ha='center', va='center', 
               fontsize=8)
    
    # Safety properties
    ax.text(8, 3, 'Safety Properties', fontsize=14, fontweight='bold', ha='center')
    
    properties = [
        "• Election Safety: At most one leader per term",
        "• Leader Append-Only: Leader never overwrites log entries",
        "• Log Matching: Identical entries at same index/term",
        "• Leader Completeness: Committed entries in future leaders",
        "• State Machine Safety: Same log → same state"
    ]
    
    for i, prop in enumerate(properties):
        ax.text(1, 2.3 - i*0.3, prop, ha='left', va='center', fontsize=9)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('raft_algorithm.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_paxos_algorithm_diagram():
    """Create Paxos algorithm flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'Paxos Consensus Algorithm', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Paxos phases
    phases = [
        ("Phase 1: Prepare", 2, 8, "#f3e5f5", "Proposer sends\nprepare(n)"),
        ("Phase 1: Promise", 6, 8, "#e0f2f1", "Acceptors promise\nnot to accept < n"),
        ("Phase 2: Accept", 10, 8, "#ffebee", "Proposer sends\naccept(n, v)"),
        ("Phase 2: Accepted", 14, 8, "#f1f8e9", "Acceptors accept\nif n ≥ promised")
    ]
    
    for name, x, y, color, details in phases:
        phase_box = FancyBboxPatch((x-1.5, y-1), 3, 2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=color, edgecolor='gray', linewidth=2)
        ax.add_patch(phase_box)
        ax.text(x, y+0.3, name, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        ax.text(x, y-0.3, details, ha='center', va='center', 
               fontsize=8)
    
    # Flow arrows
    for i in range(3):
        start_x = 2 + i * 4 + 1.5
        end_x = start_x + 1
        arrow = ConnectionPatch((start_x, 8), (end_x, 8), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5, 
                               mutation_scale=20, fc="blue", lw=2)
        ax.add_patch(arrow)
    
    # Roles
    ax.text(8, 6, 'Paxos Roles', fontsize=14, fontweight='bold', ha='center')
    
    roles = [
        ("Proposer", 3, 5, "#e3f2fd", "Initiates consensus\nSends proposals"),
        ("Acceptor", 8, 5, "#e8f5e8", "Votes on proposals\nMaintains promises"),
        ("Learner", 13, 5, "#fff3e0", "Learns chosen value\nNotifies clients")
    ]
    
    for name, x, y, color, details in roles:
        role_box = FancyBboxPatch((x-1.2, y-0.8), 2.4, 1.6, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(role_box)
        ax.text(x, y+0.2, name, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        ax.text(x, y-0.3, details, ha='center', va='center', 
               fontsize=8)
    
    # Properties
    ax.text(8, 3, 'Paxos Properties', fontsize=14, fontweight='bold', ha='center')
    
    properties = [
        "• Safety: Only proposed values can be chosen",
        "• Safety: Only one value is chosen",
        "• Liveness: Some proposed value is eventually chosen",
        "• Validity: If majority non-faulty, progress guaranteed",
        "• Agreement: All learners learn the same value"
    ]
    
    for i, prop in enumerate(properties):
        ax.text(1, 2.3 - i*0.3, prop, ha='left', va='center', fontsize=9)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('paxos_algorithm.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_consensus_comparison():
    """Create Raft vs Paxos comparison diagram"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
    
    fig.suptitle('Raft vs Paxos Comparison', fontsize=16, fontweight='bold')
    
    # Raft characteristics
    ax1.set_title('Raft Algorithm', fontsize=14, fontweight='bold')
    
    raft_metrics = ['Understandability', 'Implementation', 'Performance', 'Debugging', 'Leadership']
    raft_scores = [9, 8, 8, 9, 9]
    
    y_pos = np.arange(len(raft_metrics))
    bars1 = ax1.barh(y_pos, raft_scores, color='#4CAF50', alpha=0.7)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(raft_metrics)
    ax1.set_xlim(0, 10)
    ax1.set_xlabel('Score (1-10)')
    
    # Add value labels
    for i, bar in enumerate(bars1):
        width = bar.get_width()
        ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{raft_scores[i]}', ha='left', va='center')
    
    # Paxos characteristics
    ax2.set_title('Paxos Algorithm', fontsize=14, fontweight='bold')
    
    paxos_metrics = ['Theoretical Foundation', 'Fault Tolerance', 'Flexibility', 'Correctness', 'No Single Point']
    paxos_scores = [10, 9, 9, 10, 10]
    
    y_pos = np.arange(len(paxos_metrics))
    bars2 = ax2.barh(y_pos, paxos_scores, color='#2196F3', alpha=0.7)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(paxos_metrics)
    ax2.set_xlim(0, 10)
    ax2.set_xlabel('Score (1-10)')
    
    # Add value labels
    for i, bar in enumerate(bars2):
        width = bar.get_width()
        ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{paxos_scores[i]}', ha='left', va='center')
    
    plt.tight_layout()
    plt.savefig('consensus_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_consensus_timeline():
    """Create consensus algorithm timeline and usage"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    
    ax.text(8, 7.5, 'Consensus Algorithms: Timeline and Real-World Usage', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Timeline
    timeline_data = [
        (1989, "Paxos", "Leslie Lamport", "#2196F3"),
        (2013, "Raft", "Diego Ongaro & John Ousterhout", "#4CAF50"),
        (2014, "etcd", "CoreOS (Raft)", "#FF9800"),
        (2015, "Consul", "HashiCorp (Raft)", "#9C27B0"),
        (2016, "CockroachDB", "Cockroach Labs (Raft)", "#F44336"),
        (2019, "TiDB", "PingCAP (Raft)", "#00BCD4")
    ]
    
    for i, (year, name, org, color) in enumerate(timeline_data):
        y_pos = 6 - i * 0.8
        
        # Timeline dot
        ax.scatter(year, y_pos, s=100, c=color, zorder=3)
        
        # Timeline line
        if i > 0:
            prev_year = timeline_data[i-1][0]
            ax.plot([prev_year, year], [6 - (i-1) * 0.8, y_pos], 
                   'k-', alpha=0.3, zorder=1)
        
        # Labels
        ax.text(year + 1, y_pos, f"{name}\n{org}", 
               fontsize=10, va='center', fontweight='bold')
        ax.text(year - 1, y_pos, str(year), 
               fontsize=9, va='center', ha='right', color='gray')
    
    # Usage statistics
    usage_box = FancyBboxPatch((2020, 1), 8, 4, 
                              boxstyle="round,pad=0.2", 
                              facecolor='#f5f5f5', edgecolor='gray', linewidth=1)
    ax.add_patch(usage_box)
    
    ax.text(2024, 4.5, 'Current Usage in Production', 
           fontsize=12, fontweight='bold', ha='center')
    
    usage_stats = [
        "🏢 Kubernetes: etcd (Raft) - 100M+ clusters",
        "🔍 Service Discovery: Consul (Raft) - 10M+ nodes",
        "🗄️ Distributed SQL: CockroachDB, TiDB (Raft)",
        "📊 Message Queues: Kafka (Raft-like) - 80% Fortune 100",
        "🔒 Secret Management: Vault (Raft) - Enterprise standard"
    ]
    
    for i, stat in enumerate(usage_stats):
        ax.text(2021, 3.8 - i*0.4, stat, fontsize=9, va='center')
    
    ax.set_xlim(1985, 2030)
    ax.set_ylim(0, 8)
    ax.set_xlabel('Year')
    ax.set_ylabel('')
    ax.grid(True, alpha=0.3)
    ax.set_yticks([])
    
    plt.tight_layout()
    plt.savefig('consensus_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all consensus algorithm diagrams"""
    print("🎨 Rendering Raft & Paxos consensus diagrams...")
    
    diagrams = [
        ("Raft Algorithm", create_raft_algorithm_diagram),
        ("Paxos Algorithm", create_paxos_algorithm_diagram),
        ("Consensus Comparison", create_consensus_comparison),
        ("Consensus Timeline", create_consensus_timeline)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All consensus algorithm diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
