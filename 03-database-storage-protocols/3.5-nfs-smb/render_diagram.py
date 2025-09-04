#!/usr/bin/env python3
"""
NFS & SMB Protocol Diagram Renderer
Generates visual diagrams for NFS and SMB protocol concepts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_nfs_protocol_diagram():
    """Create NFS protocol operations diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'NFS Protocol Architecture', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Client section
    client_box = FancyBboxPatch((1, 7.5), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor="#e3f2fd", edgecolor='blue', linewidth=2)
    ax.add_patch(client_box)
    ax.text(2.5, 8.25, "NFS Client\n(Linux/Unix)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # RPC layer
    rpc_box = FancyBboxPatch((5.5, 7.5), 3, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor="#fff3e0", edgecolor='orange', linewidth=2)
    ax.add_patch(rpc_box)
    ax.text(7, 8.25, "RPC Layer\n(XDR/TCP/UDP)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # NFS server
    server_box = FancyBboxPatch((10, 7.5), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor="#c8e6c9", edgecolor='green', linewidth=2)
    ax.add_patch(server_box)
    ax.text(11.5, 8.25, "NFS Server\n(NFSv3/v4)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # NFS operations
    operations = [
        ("LOOKUP", 2, 6, "#ffcdd2"),
        ("GETATTR", 4, 6, "#f8bbd9"),
        ("READ", 6, 6, "#e1f5fe"),
        ("WRITE", 8, 6, "#e8f5e8"),
        ("READDIR", 10, 6, "#fff3e0"),
        ("CREATE", 12, 6, "#f3e5f5")
    ]
    
    for op_name, x, y, color in operations:
        op_box = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8, 
                               boxstyle="round,pad=0.05", 
                               facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(op_box)
        ax.text(x, y, op_name, ha='center', va='center', 
               fontsize=9, fontweight='bold')
    
    # Performance metrics
    ax.text(8, 4.5, 'NFS Performance Characteristics', 
           fontsize=14, fontweight='bold', ha='center')
    
    perf_data = [
        ("Operation", "Latency", "Throughput"),
        ("GETATTR", "0.5-2ms", "N/A"),
        ("READ", "1-5ms", "50-200 MB/s"),
        ("WRITE", "2-8ms", "30-150 MB/s"),
        ("LOOKUP", "0.3-1.5ms", "N/A"),
        ("READDIR", "2-10ms", "5-20 MB/s")
    ]
    
    for i, (op, lat, tput) in enumerate(perf_data):
        y_pos = 3.5 - i * 0.3
        if i == 0:  # Header
            ax.text(4, y_pos, op, ha='center', va='center', fontweight='bold')
            ax.text(8, y_pos, lat, ha='center', va='center', fontweight='bold')
            ax.text(12, y_pos, tput, ha='center', va='center', fontweight='bold')
        else:
            ax.text(4, y_pos, op, ha='center', va='center')
            ax.text(8, y_pos, lat, ha='center', va='center')
            ax.text(12, y_pos, tput, ha='center', va='center')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('nfs_protocol.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_smb_protocol_diagram():
    """Create SMB protocol operations diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'SMB Protocol Architecture', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Client section
    client_box = FancyBboxPatch((1, 7.5), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor="#e3f2fd", edgecolor='blue', linewidth=2)
    ax.add_patch(client_box)
    ax.text(2.5, 8.25, "SMB Client\n(Windows/Samba)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # SMB protocol stack
    smb_box = FancyBboxPatch((5.5, 7.5), 3, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor="#fff3e0", edgecolor='orange', linewidth=2)
    ax.add_patch(smb_box)
    ax.text(7, 8.25, "SMB Protocol\n(SMB 2.1/3.0)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # SMB server
    server_box = FancyBboxPatch((10, 7.5), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor="#c8e6c9", edgecolor='green', linewidth=2)
    ax.add_patch(server_box)
    ax.text(11.5, 8.25, "SMB Server\n(Windows/Samba)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # SMB operations
    operations = [
        ("NEGOTIATE", 1.5, 6, "#ffcdd2"),
        ("SESSION_SETUP", 3.5, 6, "#f8bbd9"),
        ("TREE_CONNECT", 5.5, 6, "#e1f5fe"),
        ("CREATE", 7.5, 6, "#e8f5e8"),
        ("READ/WRITE", 9.5, 6, "#fff3e0"),
        ("CLOSE", 11.5, 6, "#f3e5f5")
    ]
    
    for op_name, x, y, color in operations:
        op_box = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8, 
                               boxstyle="round,pad=0.05", 
                               facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(op_box)
        ax.text(x, y, op_name, ha='center', va='center', 
               fontsize=8, fontweight='bold')
    
    # Performance metrics
    ax.text(8, 4.5, 'SMB Performance Characteristics', 
           fontsize=14, fontweight='bold', ha='center')
    
    perf_data = [
        ("Operation", "Latency", "Throughput"),
        ("NEGOTIATE", "0.8-3ms", "N/A"),
        ("CREATE", "0.5-4ms", "N/A"),
        ("READ", "0.5-4ms", "80-300 MB/s"),
        ("WRITE", "1-6ms", "60-250 MB/s"),
        ("QUERY_DIR", "1.5-8ms", "2-10 MB/s")
    ]
    
    for i, (op, lat, tput) in enumerate(perf_data):
        y_pos = 3.5 - i * 0.3
        if i == 0:  # Header
            ax.text(4, y_pos, op, ha='center', va='center', fontweight='bold')
            ax.text(8, y_pos, lat, ha='center', va='center', fontweight='bold')
            ax.text(12, y_pos, tput, ha='center', va='center', fontweight='bold')
        else:
            ax.text(4, y_pos, op, ha='center', va='center')
            ax.text(8, y_pos, lat, ha='center', va='center')
            ax.text(12, y_pos, tput, ha='center', va='center')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('smb_protocol.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_file_system_comparison():
    """Create NFS vs SMB comparison diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    ax.text(8, 11.5, 'NFS vs SMB Protocol Comparison', 
           fontsize=16, fontweight='bold', ha='center')
    
    # NFS section
    ax.text(4, 10.5, 'NFS (Network File System)', 
           fontsize=14, fontweight='bold', ha='center')
    
    nfs_box = FancyBboxPatch((1, 8), 6, 2, 
                            boxstyle="round,pad=0.1", 
                            facecolor="#e8f5e8", edgecolor='green', linewidth=2)
    ax.add_patch(nfs_box)
    
    nfs_features = [
        "• Unix/Linux native",
        "• Stateless (NFSv3)",
        "• POSIX semantics",
        "• UDP/TCP transport",
        "• Strong consistency"
    ]
    
    for i, feature in enumerate(nfs_features):
        ax.text(1.2, 9.5 - i*0.3, feature, ha='left', va='center', fontsize=10)
    
    # SMB section
    ax.text(12, 10.5, 'SMB (Server Message Block)', 
           fontsize=14, fontweight='bold', ha='center')
    
    smb_box = FancyBboxPatch((9, 8), 6, 2, 
                            boxstyle="round,pad=0.1", 
                            facecolor="#e3f2fd", edgecolor='blue', linewidth=2)
    ax.add_patch(smb_box)
    
    smb_features = [
        "• Windows native",
        "• Stateful protocol",
        "• Rich metadata",
        "• TCP transport",
        "• Opportunistic locking"
    ]
    
    for i, feature in enumerate(smb_features):
        ax.text(9.2, 9.5 - i*0.3, feature, ha='left', va='center', fontsize=10)
    
    # Performance comparison
    ax.text(8, 7, 'Performance Comparison', 
           fontsize=14, fontweight='bold', ha='center')
    
    # Create comparison table
    comparison_data = [
        ("Metric", "NFS", "SMB"),
        ("Typical Latency", "1-5ms", "0.5-4ms"),
        ("Max Throughput", "200 MB/s", "300 MB/s"),
        ("Concurrent Clients", "1000+", "500+"),
        ("CPU Overhead", "Low", "Medium"),
        ("Network Efficiency", "Good", "Excellent"),
        ("Caching", "Client-side", "Opportunistic"),
        ("Security", "Kerberos/IPSec", "NTLM/Kerberos")
    ]
    
    for i, (metric, nfs_val, smb_val) in enumerate(comparison_data):
        y_pos = 6 - i * 0.4
        if i == 0:  # Header
            ax.text(4, y_pos, metric, ha='center', va='center', fontweight='bold', fontsize=11)
            ax.text(8, y_pos, nfs_val, ha='center', va='center', fontweight='bold', fontsize=11)
            ax.text(12, y_pos, smb_val, ha='center', va='center', fontweight='bold', fontsize=11)
        else:
            ax.text(4, y_pos, metric, ha='center', va='center', fontsize=10)
            ax.text(8, y_pos, nfs_val, ha='center', va='center', fontsize=10)
            ax.text(12, y_pos, smb_val, ha='center', va='center', fontsize=10)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('nfs_smb_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_file_system_performance():
    """Create file system performance monitoring diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'File System Performance Monitoring', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Monitoring components
    components = [
        ("Latency Monitor", 2, 8, "#ffcdd2"),
        ("Throughput Monitor", 6, 8, "#c8e6c9"),
        ("Error Rate Monitor", 10, 8, "#fff3e0"),
        ("Cache Monitor", 14, 8, "#e1f5fe")
    ]
    
    for comp_name, x, y, color in components:
        comp_box = FancyBboxPatch((x-1.2, y-0.5), 2.4, 1, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(comp_box)
        ax.text(x, y, comp_name, ha='center', va='center', 
               fontsize=10, fontweight='bold')
    
    # Metrics visualization
    ax.text(8, 6.5, 'Key Performance Metrics', 
           fontsize=14, fontweight='bold', ha='center')
    
    # Simulated performance data
    time_points = np.linspace(0, 10, 50)
    nfs_latency = 2 + 0.5 * np.sin(time_points) + 0.2 * np.random.randn(50)
    smb_latency = 1.5 + 0.3 * np.sin(time_points + 1) + 0.15 * np.random.randn(50)
    
    # Mini performance chart
    chart_ax = fig.add_axes([0.2, 0.15, 0.6, 0.35])
    chart_ax.plot(time_points, nfs_latency, 'g-', linewidth=2, label='NFS Latency')
    chart_ax.plot(time_points, smb_latency, 'b-', linewidth=2, label='SMB Latency')
    chart_ax.set_xlabel('Time (minutes)')
    chart_ax.set_ylabel('Latency (ms)')
    chart_ax.set_title('Real-time Latency Monitoring')
    chart_ax.legend()
    chart_ax.grid(True, alpha=0.3)
    
    # Alert thresholds
    ax.text(2, 3, 'Alert Thresholds:', fontsize=12, fontweight='bold')
    ax.text(2, 2.5, '• Latency > 100ms', fontsize=10)
    ax.text(2, 2.2, '• Error rate > 5%', fontsize=10)
    ax.text(2, 1.9, '• Throughput < 10 MB/s', fontsize=10)
    
    ax.text(10, 3, 'Optimization Tips:', fontsize=12, fontweight='bold')
    ax.text(10, 2.5, '• Enable client-side caching', fontsize=10)
    ax.text(10, 2.2, '• Use jumbo frames', fontsize=10)
    ax.text(10, 1.9, '• Optimize network topology', fontsize=10)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('file_system_performance.png', dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all NFS & SMB protocol diagrams"""
    print("🎨 Rendering NFS & SMB Protocol diagrams...")
    
    diagrams = [
        ("NFS Protocol", create_nfs_protocol_diagram),
        ("SMB Protocol", create_smb_protocol_diagram),
        ("NFS vs SMB Comparison", create_file_system_comparison),
        ("File System Performance", create_file_system_performance)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All NFS & SMB protocol diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
