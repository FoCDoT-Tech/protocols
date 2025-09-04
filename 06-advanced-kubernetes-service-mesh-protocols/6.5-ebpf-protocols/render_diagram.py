#!/usr/bin/env python3
"""
eBPF Protocols Diagram Renderer
Creates visual diagrams for eBPF architecture and performance
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_ebpf_architecture_diagram():
    """Create eBPF architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Define colors
    colors = {
        'user_space': '#E3F2FD',
        'ebpf_programs': '#F3E5F5',
        'kernel': '#E8F5E8',
        'maps': '#FFF3E0',
        'service_mesh': '#FFEBEE',
        'observability': '#F1F8E9'
    }
    
    # User Space Applications (top)
    user_space_y = 0.85
    user_boxes = [
        ('Trading App\n(Ultra-Low Latency)', 0.1, 0.15),
        ('Control Plane\n(Program Mgmt)', 0.3, 0.15),
        ('Metrics Collector\n(Monitoring)', 0.5, 0.15),
        ('Debug Tools\n(bpftool/BCC)', 0.7, 0.15)
    ]
    
    for label, x, width in user_boxes:
        box = FancyBboxPatch((x, user_space_y), width, 0.08,
                           boxstyle="round,pad=0.01",
                           facecolor=colors['user_space'],
                           edgecolor='#1976D2', linewidth=2)
        ax.add_patch(box)
        ax.text(x + width/2, user_space_y + 0.04, label,
               ha='center', va='center', fontsize=9, weight='bold')
    
    # eBPF Programs (middle-upper)
    programs_y = 0.65
    program_boxes = [
        ('XDP\nLoad Balancer', 0.05, 0.12),
        ('TC Traffic\nShaper', 0.22, 0.12),
        ('Socket\nFilter', 0.39, 0.12),
        ('Kprobe\nTracer', 0.56, 0.12),
        ('Tracepoint\nCollector', 0.73, 0.12)
    ]
    
    for label, x, width in program_boxes:
        box = FancyBboxPatch((x, programs_y), width, 0.08,
                           boxstyle="round,pad=0.01",
                           facecolor=colors['ebpf_programs'],
                           edgecolor='#7B1FA2', linewidth=2)
        ax.add_patch(box)
        ax.text(x + width/2, programs_y + 0.04, label,
               ha='center', va='center', fontsize=9, weight='bold')
    
    # Kernel Hooks & Network Stack (middle)
    kernel_y = 0.35
    
    # Network stack flow
    network_boxes = [
        ('NIC', 0.05, 0.08),
        ('Driver', 0.18, 0.08),
        ('XDP Hook', 0.31, 0.08),
        ('TC Hook', 0.44, 0.08),
        ('IP Layer', 0.57, 0.08),
        ('TCP Layer', 0.70, 0.08),
        ('Socket', 0.83, 0.08)
    ]
    
    for i, (label, x, width) in enumerate(network_boxes):
        box = FancyBboxPatch((x, kernel_y), width, 0.06,
                           boxstyle="round,pad=0.01",
                           facecolor=colors['kernel'],
                           edgecolor='#388E3C', linewidth=2)
        ax.add_patch(box)
        ax.text(x + width/2, kernel_y + 0.03, label,
               ha='center', va='center', fontsize=8, weight='bold')
        
        # Add arrows between network stack components
        if i < len(network_boxes) - 1:
            next_x = network_boxes[i + 1][1]
            arrow = ConnectionPatch((x + width, kernel_y + 0.03),
                                  (next_x, kernel_y + 0.03),
                                  "data", "data",
                                  arrowstyle="->", shrinkA=0, shrinkB=0,
                                  mutation_scale=20, fc="black")
            ax.add_patch(arrow)
    
    # eBPF Maps (lower-middle)
    maps_y = 0.15
    map_boxes = [
        ('Connection\nMap', 0.1, 0.12),
        ('Policy\nMap', 0.27, 0.12),
        ('Metrics\nMap', 0.44, 0.12),
        ('Ring\nBuffer', 0.61, 0.12),
        ('LRU\nCache', 0.78, 0.12)
    ]
    
    for label, x, width in map_boxes:
        box = FancyBboxPatch((x, maps_y), width, 0.08,
                           boxstyle="round,pad=0.01",
                           facecolor=colors['maps'],
                           edgecolor='#F57C00', linewidth=2)
        ax.add_patch(box)
        ax.text(x + width/2, maps_y + 0.04, label,
               ha='center', va='center', fontsize=9, weight='bold')
    
    # Service Mesh Integration (right side)
    mesh_x = 0.92
    mesh_boxes = [
        ('Cilium\nCNI', 0.75),
        ('Istio\nAmbient', 0.60),
        ('Linkerd\n+ eBPF', 0.45),
        ('Envoy\nAccel', 0.30)
    ]
    
    for label, y in mesh_boxes:
        box = FancyBboxPatch((mesh_x, y), 0.07, 0.08,
                           boxstyle="round,pad=0.01",
                           facecolor=colors['service_mesh'],
                           edgecolor='#D32F2F', linewidth=2)
        ax.add_patch(box)
        ax.text(mesh_x + 0.035, y + 0.04, label,
               ha='center', va='center', fontsize=8, weight='bold')
    
    # Add connection arrows
    # User space to eBPF programs
    for i in range(len(user_boxes)):
        if i < len(program_boxes):
            user_x = user_boxes[i][1] + user_boxes[i][2]/2
            prog_x = program_boxes[i][1] + program_boxes[i][2]/2
            arrow = ConnectionPatch((user_x, user_space_y),
                                  (prog_x, programs_y + 0.08),
                                  "data", "data",
                                  arrowstyle="->", shrinkA=0, shrinkB=0,
                                  mutation_scale=15, fc="blue", alpha=0.6)
            ax.add_patch(arrow)
    
    # eBPF programs to kernel hooks
    for i in range(min(len(program_boxes), len(network_boxes))):
        prog_x = program_boxes[i][1] + program_boxes[i][2]/2
        kernel_x = network_boxes[min(i+2, len(network_boxes)-1)][1] + network_boxes[min(i+2, len(network_boxes)-1)][2]/2
        arrow = ConnectionPatch((prog_x, programs_y),
                              (kernel_x, kernel_y + 0.06),
                              "data", "data",
                              arrowstyle="->", shrinkA=0, shrinkB=0,
                              mutation_scale=15, fc="purple", alpha=0.6)
        ax.add_patch(arrow)
    
    # Programs to maps (bidirectional)
    for i in range(min(len(program_boxes), len(map_boxes))):
        prog_x = program_boxes[i][1] + program_boxes[i][2]/2
        map_x = map_boxes[i][1] + map_boxes[i][2]/2
        
        # Down arrow
        arrow1 = ConnectionPatch((prog_x, programs_y),
                               (map_x, maps_y + 0.08),
                               "data", "data",
                               arrowstyle="->", shrinkA=0, shrinkB=0,
                               mutation_scale=12, fc="orange", alpha=0.6)
        ax.add_patch(arrow1)
        
        # Up arrow (offset slightly)
        arrow2 = ConnectionPatch((map_x + 0.01, maps_y + 0.08),
                               (prog_x + 0.01, programs_y),
                               "data", "data",
                               arrowstyle="->", shrinkA=0, shrinkB=0,
                               mutation_scale=12, fc="orange", alpha=0.4,
                               linestyle="--")
        ax.add_patch(arrow2)
    
    # Add title and labels
    ax.set_title('eBPF Architecture for Service Mesh Acceleration', 
                fontsize=16, weight='bold', pad=20)
    
    # Add layer labels
    ax.text(0.02, user_space_y + 0.04, 'User Space', rotation=90, 
           ha='center', va='center', fontsize=12, weight='bold', color='#1976D2')
    ax.text(0.02, programs_y + 0.04, 'eBPF Programs', rotation=90,
           ha='center', va='center', fontsize=12, weight='bold', color='#7B1FA2')
    ax.text(0.02, kernel_y + 0.03, 'Kernel Space', rotation=90,
           ha='center', va='center', fontsize=12, weight='bold', color='#388E3C')
    ax.text(0.02, maps_y + 0.04, 'eBPF Maps', rotation=90,
           ha='center', va='center', fontsize=12, weight='bold', color='#F57C00')
    
    # Remove axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('ebpf_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_ebpf_performance_comparison():
    """Create eBPF performance comparison chart"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Processing latency comparison
    methods = ['eBPF XDP', 'eBPF TC', 'Netfilter', 'Userspace\nProxy', 'DPDK']
    latencies = [0.05, 0.1, 2.5, 50, 0.02]  # microseconds
    colors_lat = ['#2E7D32', '#388E3C', '#FFA000', '#D32F2F', '#1976D2']
    
    bars1 = ax1.bar(methods, latencies, color=colors_lat, alpha=0.8)
    ax1.set_ylabel('Latency (μs)', fontsize=12)
    ax1.set_title('Packet Processing Latency', fontsize=14, weight='bold')
    ax1.set_yscale('log')
    
    # Add value labels on bars
    for bar, latency in zip(bars1, latencies):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{latency}μs', ha='center', va='bottom', fontsize=10)
    
    # Throughput comparison
    throughputs = [100, 95, 20, 5, 120]  # Mpps (Million packets per second)
    bars2 = ax2.bar(methods, throughputs, color=colors_lat, alpha=0.8)
    ax2.set_ylabel('Throughput (Mpps)', fontsize=12)
    ax2.set_title('Maximum Throughput', fontsize=14, weight='bold')
    
    for bar, throughput in zip(bars2, throughputs):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{throughput}M', ha='center', va='bottom', fontsize=10)
    
    # CPU usage comparison
    cpu_usage = [2, 5, 15, 80, 1]  # CPU percentage
    bars3 = ax3.bar(methods, cpu_usage, color=colors_lat, alpha=0.8)
    ax3.set_ylabel('CPU Usage (%)', fontsize=12)
    ax3.set_title('CPU Overhead', fontsize=14, weight='bold')
    
    for bar, cpu in zip(bars3, cpu_usage):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{cpu}%', ha='center', va='bottom', fontsize=10)
    
    # Memory usage comparison
    memory_usage = [0.5, 1, 10, 100, 2]  # MB
    bars4 = ax4.bar(methods, memory_usage, color=colors_lat, alpha=0.8)
    ax4.set_ylabel('Memory Usage (MB)', fontsize=12)
    ax4.set_title('Memory Overhead', fontsize=14, weight='bold')
    ax4.set_yscale('log')
    
    for bar, memory in zip(bars4, memory_usage):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{memory}MB', ha='center', va='bottom', fontsize=10)
    
    # Rotate x-axis labels for better readability
    for ax in [ax1, ax2, ax3, ax4]:
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('eBPF vs Traditional Networking Performance', 
                fontsize=16, weight='bold')
    plt.tight_layout()
    plt.savefig('ebpf_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_ebpf_program_lifecycle():
    """Create eBPF program lifecycle diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Define stages
    stages = [
        ('Source Code\n(.c/.py)', 0.1, 0.8, '#E3F2FD'),
        ('Compilation\n(clang/LLVM)', 0.1, 0.65, '#F3E5F5'),
        ('Bytecode\n(eBPF)', 0.1, 0.5, '#E8F5E8'),
        ('Verifier\n(Safety Check)', 0.4, 0.5, '#FFF3E0'),
        ('JIT Compiler\n(Native Code)', 0.7, 0.5, '#FFEBEE'),
        ('Kernel\n(Execution)', 0.7, 0.35, '#F1F8E9'),
        ('Maps\n(State)', 0.4, 0.35, '#FCE4EC'),
        ('User Space\n(Control)', 0.1, 0.35, '#E0F2F1')
    ]
    
    # Draw stages
    for stage, x, y, color in stages:
        box = FancyBboxPatch((x, y), 0.15, 0.08,
                           boxstyle="round,pad=0.01",
                           facecolor=color,
                           edgecolor='black', linewidth=2)
        ax.add_patch(box)
        ax.text(x + 0.075, y + 0.04, stage,
               ha='center', va='center', fontsize=10, weight='bold')
    
    # Define connections
    connections = [
        (0, 1, 'Compile'),
        (1, 2, 'Generate'),
        (2, 3, 'Verify'),
        (3, 4, 'Pass'),
        (4, 5, 'Load'),
        (5, 6, 'Access'),
        (6, 7, 'Control'),
        (7, 5, 'Manage')
    ]
    
    # Draw connections
    for start_idx, end_idx, label in connections:
        start_stage = stages[start_idx]
        end_stage = stages[end_idx]
        
        start_x = start_stage[1] + 0.075
        start_y = start_stage[2]
        end_x = end_stage[1] + 0.075
        end_y = end_stage[2] + 0.08
        
        if start_idx == 7 and end_idx == 5:  # Control loop
            # Curved arrow for feedback loop
            arrow = ConnectionPatch((start_x, start_y + 0.04),
                                  (end_x - 0.05, end_y - 0.04),
                                  "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=5,
                                  mutation_scale=20, fc="red", alpha=0.7,
                                  connectionstyle="arc3,rad=0.3")
        else:
            arrow = ConnectionPatch((start_x, start_y),
                                  (end_x, end_y),
                                  "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=5,
                                  mutation_scale=20, fc="blue", alpha=0.7)
        ax.add_patch(arrow)
        
        # Add label
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        if start_idx != 7 or end_idx != 5:
            ax.text(mid_x, mid_y, label, ha='center', va='center',
                   fontsize=8, bbox=dict(boxstyle="round,pad=0.2",
                   facecolor='white', alpha=0.8))
    
    # Add verification details
    verify_details = [
        'Memory bounds check',
        'Loop termination',
        'Helper function validation',
        'Stack overflow protection',
        'Pointer arithmetic safety'
    ]
    
    for i, detail in enumerate(verify_details):
        ax.text(0.4, 0.42 - i*0.02, f'• {detail}', fontsize=8,
               ha='left', va='center')
    
    # Add performance metrics
    perf_box = FancyBboxPatch((0.75, 0.65), 0.2, 0.15,
                            boxstyle="round,pad=0.01",
                            facecolor='#E8F5E8',
                            edgecolor='green', linewidth=2)
    ax.add_patch(perf_box)
    
    perf_metrics = [
        'Load time: <1ms',
        'Execution: <100ns',
        'Memory: <1MB',
        'Verification: <10ms'
    ]
    
    ax.text(0.85, 0.75, 'Performance', ha='center', va='center',
           fontsize=11, weight='bold')
    for i, metric in enumerate(perf_metrics):
        ax.text(0.77, 0.71 - i*0.02, metric, fontsize=8,
               ha='left', va='center')
    
    ax.set_title('eBPF Program Lifecycle and Verification', 
                fontsize=16, weight='bold', pad=20)
    ax.set_xlim(0, 1)
    ax.set_ylim(0.2, 0.9)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('ebpf_program_lifecycle.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Generate all eBPF diagrams"""
    print("Generating eBPF architecture diagrams...")
    
    # Create diagrams
    create_ebpf_architecture_diagram()
    print("✓ eBPF architecture diagram created")
    
    create_ebpf_performance_comparison()
    print("✓ eBPF performance comparison created")
    
    create_ebpf_program_lifecycle()
    print("✓ eBPF program lifecycle diagram created")
    
    print("\nAll eBPF diagrams generated successfully!")
    print("Files created:")
    print("  - ebpf_architecture.png")
    print("  - ebpf_performance_comparison.png")
    print("  - ebpf_program_lifecycle.png")

if __name__ == "__main__":
    main()
