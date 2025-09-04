#!/usr/bin/env python3
"""
S3 API Protocol Diagram Renderer
Generates visual diagrams for S3 API concepts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_s3_api_diagram():
    """Create S3 API operations diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'S3 API Architecture', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Client section
    client_box = FancyBboxPatch((1, 7.5), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor="#e3f2fd", edgecolor='blue', linewidth=2)
    ax.add_patch(client_box)
    ax.text(2.5, 8.25, "S3 Client\n(REST API)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # API Gateway
    gateway_box = FancyBboxPatch((5.5, 7.5), 3, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor="#fff3e0", edgecolor='orange', linewidth=2)
    ax.add_patch(gateway_box)
    ax.text(7, 8.25, "API Gateway\n(HTTPS/TLS)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # S3 service
    service_box = FancyBboxPatch((10, 7.5), 3, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor="#c8e6c9", edgecolor='green', linewidth=2)
    ax.add_patch(service_box)
    ax.text(11.5, 8.25, "S3 Service\n(Object Storage)", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # S3 operations
    operations = [
        ("PUT Object", 2, 6, "#ffcdd2"),
        ("GET Object", 4, 6, "#f8bbd9"),
        ("DELETE Object", 6, 6, "#e1f5fe"),
        ("LIST Objects", 8, 6, "#e8f5e8"),
        ("Multipart Upload", 10, 6, "#fff3e0"),
        ("Copy Object", 12, 6, "#f3e5f5")
    ]
    
    for op_name, x, y, color in operations:
        op_box = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8, 
                               boxstyle="round,pad=0.05", 
                               facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(op_box)
        ax.text(x, y, op_name, ha='center', va='center', 
               fontsize=8, fontweight='bold')
    
    # Performance metrics
    ax.text(8, 4.5, 'S3 Performance Characteristics', 
           fontsize=14, fontweight='bold', ha='center')
    
    perf_data = [
        ("Operation", "Latency", "Throughput"),
        ("PUT", "100-200ms", "Multi-GB/s"),
        ("GET", "10-50ms", "Multi-GB/s"),
        ("DELETE", "100-200ms", "3,500 req/s"),
        ("LIST", "100-300ms", "5,500 req/s"),
        ("Multipart", "Parallel", "10x faster")
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
    plt.savefig('s3_api.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_s3_storage_classes():
    """Create S3 storage classes diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    ax.text(8, 11.5, 'S3 Storage Classes', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Storage classes with cost and performance characteristics
    storage_classes = [
        ("S3 Standard", 2, 9.5, "#ffcdd2", "Frequent Access\n$0.023/GB/month\nms latency"),
        ("S3 Standard-IA", 5, 9.5, "#c8e6c9", "Infrequent Access\n$0.0125/GB/month\nms latency"),
        ("S3 One Zone-IA", 8, 9.5, "#bbdefb", "Single AZ\n$0.01/GB/month\nms latency"),
        ("S3 Glacier", 11, 9.5, "#f8bbd9", "Archive\n$0.004/GB/month\nminutes retrieval"),
        ("S3 Deep Archive", 14, 9.5, "#fff3e0", "Long-term Archive\n$0.00099/GB/month\nhours retrieval")
    ]
    
    for name, x, y, color, details in storage_classes:
        class_box = FancyBboxPatch((x-1.2, y-1), 2.4, 2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=color, edgecolor='gray', linewidth=2)
        ax.add_patch(class_box)
        ax.text(x, y+0.5, name, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        ax.text(x, y-0.3, details, ha='center', va='center', 
               fontsize=8)
    
    # Lifecycle transitions
    ax.text(8, 7, 'Lifecycle Management', 
           fontsize=14, fontweight='bold', ha='center')
    
    # Draw transition arrows
    transitions = [
        (3.2, 6.5, 4.8, 6.5, "30 days"),
        (6.2, 6.5, 7.8, 6.5, "90 days"),
        (9.2, 6.5, 10.8, 6.5, "180 days"),
        (12.2, 6.5, 13.8, 6.5, "365 days")
    ]
    
    for x1, y1, x2, y2, label in transitions:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', color='blue', lw=2))
        ax.text((x1+x2)/2, y1+0.3, label, ha='center', va='center', 
               fontsize=8, color='blue')
    
    # Cost comparison chart
    ax.text(8, 4.5, 'Storage Cost Comparison (per GB/month)', 
           fontsize=14, fontweight='bold', ha='center')
    
    costs = [0.023, 0.0125, 0.01, 0.004, 0.00099]
    class_names = ['Standard', 'Standard-IA', 'One Zone-IA', 'Glacier', 'Deep Archive']
    colors = ['#ffcdd2', '#c8e6c9', '#bbdefb', '#f8bbd9', '#fff3e0']
    
    # Create mini bar chart
    chart_ax = fig.add_axes([0.2, 0.1, 0.6, 0.25])
    bars = chart_ax.bar(class_names, costs, color=colors)
    chart_ax.set_ylabel('Cost ($/GB/month)')
    chart_ax.set_title('Storage Class Cost Comparison')
    
    # Add value labels on bars
    for bar, cost in zip(bars, costs):
        height = bar.get_height()
        chart_ax.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                     f'${cost}', ha='center', va='bottom', fontsize=9)
    
    chart_ax.tick_params(axis='x', rotation=45)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('s3_storage_classes.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_s3_multipart_upload():
    """Create S3 multipart upload diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'S3 Multipart Upload Process', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Client
    client_box = FancyBboxPatch((1, 7.5), 2, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor="#e3f2fd", edgecolor='blue', linewidth=2)
    ax.add_patch(client_box)
    ax.text(2, 8.25, "Client\nApplication", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # S3 service
    s3_box = FancyBboxPatch((13, 7.5), 2, 1.5, 
                           boxstyle="round,pad=0.1", 
                           facecolor="#c8e6c9", edgecolor='green', linewidth=2)
    ax.add_patch(s3_box)
    ax.text(14, 8.25, "S3\nService", ha='center', va='center', 
           fontsize=11, fontweight='bold')
    
    # Multipart upload steps
    steps = [
        ("1. Initiate", 4, 8.5, "POST /?uploads"),
        ("2. Upload Parts", 6, 7.5, "PUT /part1, /part2, ..."),
        ("3. Complete", 8, 6.5, "POST /?uploadId"),
        ("4. Combine", 10, 5.5, "Merge parts → Object")
    ]
    
    for step_name, x, y, details in steps:
        step_box = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor="#fff3e0", edgecolor='orange', linewidth=1)
        ax.add_patch(step_box)
        ax.text(x, y+0.1, step_name, ha='center', va='center', 
               fontsize=9, fontweight='bold')
        ax.text(x, y-0.2, details, ha='center', va='center', 
               fontsize=7)
    
    # Parallel upload visualization
    ax.text(8, 4, 'Parallel Part Upload', 
           fontsize=14, fontweight='bold', ha='center')
    
    # Show parallel streams
    for i in range(4):
        y_pos = 3 - i * 0.4
        part_box = FancyBboxPatch((4, y_pos-0.1), 8, 0.2, 
                                 boxstyle="round,pad=0.02", 
                                 facecolor=f"C{i}", alpha=0.7, edgecolor='gray')
        ax.add_patch(part_box)
        ax.text(3.5, y_pos, f"Part {i+1}", ha='right', va='center', fontsize=8)
        ax.text(12.5, y_pos, f"Upload Thread {i+1}", ha='left', va='center', fontsize=8)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('s3_multipart_upload.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_s3_cost_optimization():
    """Create S3 cost optimization diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    ax.text(8, 11.5, 'S3 Cost Optimization Strategies', 
           fontsize=16, fontweight='bold', ha='center')
    
    # Optimization strategies
    strategies = [
        ("Lifecycle Policies", 3, 9.5, "#ffcdd2", "Automatic transitions\nto cheaper storage"),
        ("Storage Class Analysis", 8, 9.5, "#c8e6c9", "Monitor access patterns\nOptimize placement"),
        ("Request Optimization", 13, 9.5, "#bbdefb", "Reduce API calls\nImplement caching")
    ]
    
    for name, x, y, color, details in strategies:
        strategy_box = FancyBboxPatch((x-2, y-1), 4, 2, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=color, edgecolor='gray', linewidth=2)
        ax.add_patch(strategy_box)
        ax.text(x, y+0.3, name, ha='center', va='center', 
               fontsize=11, fontweight='bold')
        ax.text(x, y-0.3, details, ha='center', va='center', 
               fontsize=9)
    
    # Cost savings timeline
    ax.text(8, 7, 'Projected Cost Savings Timeline', 
           fontsize=14, fontweight='bold', ha='center')
    
    # Create savings chart
    months = np.array([1, 3, 6, 12])
    savings_percent = np.array([20, 50, 80, 100])
    
    chart_ax = fig.add_axes([0.2, 0.35, 0.6, 0.25])
    chart_ax.plot(months, savings_percent, 'o-', linewidth=3, markersize=8, color='green')
    chart_ax.fill_between(months, 0, savings_percent, alpha=0.3, color='green')
    chart_ax.set_xlabel('Months after Implementation')
    chart_ax.set_ylabel('Cost Savings (%)')
    chart_ax.set_title('Lifecycle Policy Savings Over Time')
    chart_ax.grid(True, alpha=0.3)
    chart_ax.set_ylim(0, 110)
    
    # Add value labels
    for month, savings in zip(months, savings_percent):
        chart_ax.text(month, savings + 5, f'{savings}%', ha='center', va='bottom', fontweight='bold')
    
    # Optimization tips
    ax.text(8, 3.5, 'Key Optimization Tips', 
           fontsize=14, fontweight='bold', ha='center')
    
    tips = [
        "• Use S3 Intelligent-Tiering for automatic optimization",
        "• Implement lifecycle policies for predictable data patterns",
        "• Monitor access patterns with S3 Analytics",
        "• Use CloudFront CDN to reduce GET request costs",
        "• Enable compression for text-based content",
        "• Delete incomplete multipart uploads regularly"
    ]
    
    for i, tip in enumerate(tips):
        ax.text(1, 2.8 - i*0.3, tip, ha='left', va='center', fontsize=10)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('s3_cost_optimization.png', dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all S3 API protocol diagrams"""
    print("🎨 Rendering S3 API Protocol diagrams...")
    
    diagrams = [
        ("S3 API Architecture", create_s3_api_diagram),
        ("S3 Storage Classes", create_s3_storage_classes),
        ("S3 Multipart Upload", create_s3_multipart_upload),
        ("S3 Cost Optimization", create_s3_cost_optimization)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All S3 API protocol diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
