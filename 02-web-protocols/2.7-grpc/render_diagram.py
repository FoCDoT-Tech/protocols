#!/usr/bin/env python3
"""
gRPC Protocol Diagram Renderer
Generates visual diagrams for gRPC concepts using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Arrow
import numpy as np

def create_grpc_architecture_diagram():
    """Create gRPC architecture overview diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('gRPC Architecture Overview', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # Client and Server
    client_box = FancyBboxPatch((1, 9), 3, 2, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax.add_patch(client_box)
    ax.text(2.5, 10, 'gRPC Client\n(Any Language)', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((10, 9), 3, 2, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax.add_patch(server_box)
    ax.text(11.5, 10, 'gRPC Server\n(Any Language)', ha='center', va='center', fontweight='bold')
    
    # HTTP/2 Connection
    ax.arrow(4, 10, 5.5, 0, head_width=0.2, head_length=0.3,
             fc='purple', ec='purple', linewidth=3)
    ax.text(7, 10.5, 'HTTP/2 + TLS', ha='center', va='center',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='purple', alpha=0.7),
           fontweight='bold', color='white')
    
    # Protocol Buffers Layer
    protobuf_box = FancyBboxPatch((4.5, 7), 5, 1.5, boxstyle="round,pad=0.1",
                                 facecolor='lightyellow', edgecolor='black')
    ax.add_patch(protobuf_box)
    ax.text(7, 7.75, 'Protocol Buffers\n(Schema + Serialization)', ha='center', va='center', fontweight='bold')
    
    # Service Definition
    service_box = FancyBboxPatch((4.5, 5), 5, 1.5, boxstyle="round,pad=0.1",
                                facecolor='lightcoral', edgecolor='black')
    ax.add_patch(service_box)
    ax.text(7, 5.75, 'Service Definition\n(.proto files)', ha='center', va='center', fontweight='bold')
    
    # RPC Types
    rpc_types = [
        {'name': 'Unary', 'pos': (1, 3), 'color': 'lightblue'},
        {'name': 'Server\nStreaming', 'pos': (4, 3), 'color': 'lightgreen'},
        {'name': 'Client\nStreaming', 'pos': (7, 3), 'color': 'lightcoral'},
        {'name': 'Bidirectional\nStreaming', 'pos': (10, 3), 'color': 'lightyellow'}
    ]
    
    for rpc in rpc_types:
        box = FancyBboxPatch((rpc['pos'][0], rpc['pos'][1]), 2.5, 1.2, boxstyle="round,pad=0.1",
                            facecolor=rpc['color'], edgecolor='black')
        ax.add_patch(box)
        ax.text(rpc['pos'][0] + 1.25, rpc['pos'][1] + 0.6, rpc['name'], 
               ha='center', va='center', fontweight='bold', fontsize=10)
    
    # Features
    features_y = 1
    features = ['Type Safety', 'Cross-Language', 'High Performance', 'Streaming', 'Authentication']
    
    for i, feature in enumerate(features):
        x = 1 + i * 2.4
        feature_box = FancyBboxPatch((x, features_y), 2.2, 0.8, boxstyle="round,pad=0.05",
                                    facecolor='lightcyan', edgecolor='black')
        ax.add_patch(feature_box)
        ax.text(x + 1.1, features_y + 0.4, feature, ha='center', va='center', fontsize=9)
    
    # Connections
    ax.plot([2.5, 2.5], [9, 4.2], 'k--', alpha=0.5)
    ax.plot([11.5, 11.5], [9, 4.2], 'k--', alpha=0.5)
    ax.plot([7, 7], [7, 6.5], 'k-', linewidth=2)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('grpc_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_grpc_streaming_patterns():
    """Create gRPC streaming patterns diagram"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('gRPC Streaming Patterns', fontsize=16, fontweight='bold')
    
    # Unary RPC
    ax1.set_title('Unary RPC', fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 6)
    
    # Client and Server for Unary
    client_box = FancyBboxPatch((1, 4), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax1.add_patch(client_box)
    ax1.text(2, 4.5, 'Client', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((7, 4), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax1.add_patch(server_box)
    ax1.text(8, 4.5, 'Server', ha='center', va='center', fontweight='bold')
    
    # Request/Response
    ax1.arrow(3, 4.7, 3.5, 0, head_width=0.1, head_length=0.2, fc='blue', ec='blue')
    ax1.text(5, 5, 'Request', ha='center', va='center', fontsize=10)
    ax1.arrow(7, 4.3, -3.5, 0, head_width=0.1, head_length=0.2, fc='green', ec='green')
    ax1.text(5, 3.9, 'Response', ha='center', va='center', fontsize=10)
    
    ax1.text(5, 2, 'Single request → Single response\nExample: GetPrice(symbol)', 
            ha='center', va='center', fontsize=10, style='italic')
    
    # Server Streaming
    ax2.set_title('Server Streaming', fontweight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 6)
    
    client_box = FancyBboxPatch((1, 4), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax2.add_patch(client_box)
    ax2.text(2, 4.5, 'Client', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((7, 4), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax2.add_patch(server_box)
    ax2.text(8, 4.5, 'Server', ha='center', va='center', fontweight='bold')
    
    # Request and multiple responses
    ax2.arrow(3, 4.7, 3.5, 0, head_width=0.1, head_length=0.2, fc='blue', ec='blue')
    ax2.text(5, 5, 'Request', ha='center', va='center', fontsize=10)
    
    for i, y in enumerate([4.3, 4.0, 3.7]):
        ax2.arrow(7, y, -3.5, 0, head_width=0.05, head_length=0.15, fc='green', ec='green')
        ax2.text(4.5, y, f'Stream {i+1}', ha='center', va='center', fontsize=8)
    
    ax2.text(5, 2, 'Single request → Stream of responses\nExample: StreamMarketData(symbols)', 
            ha='center', va='center', fontsize=10, style='italic')
    
    # Client Streaming
    ax3.set_title('Client Streaming', fontweight='bold')
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 6)
    
    client_box = FancyBboxPatch((1, 4), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax3.add_patch(client_box)
    ax3.text(2, 4.5, 'Client', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((7, 4), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax3.add_patch(server_box)
    ax3.text(8, 4.5, 'Server', ha='center', va='center', fontweight='bold')
    
    # Multiple requests and single response
    for i, y in enumerate([4.7, 4.4, 4.1]):
        ax3.arrow(3, y, 3.5, 0, head_width=0.05, head_length=0.15, fc='blue', ec='blue')
        ax3.text(5.5, y, f'Stream {i+1}', ha='center', va='center', fontsize=8)
    
    ax3.arrow(7, 3.7, -3.5, 0, head_width=0.1, head_length=0.2, fc='green', ec='green')
    ax3.text(5, 3.4, 'Response', ha='center', va='center', fontsize=10)
    
    ax3.text(5, 2, 'Stream of requests → Single response\nExample: PlaceOrders(order_stream)', 
            ha='center', va='center', fontsize=10, style='italic')
    
    # Bidirectional Streaming
    ax4.set_title('Bidirectional Streaming', fontweight='bold')
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 6)
    
    client_box = FancyBboxPatch((1, 4), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax4.add_patch(client_box)
    ax4.text(2, 4.5, 'Client', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((7, 4), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax4.add_patch(server_box)
    ax4.text(8, 4.5, 'Server', ha='center', va='center', fontweight='bold')
    
    # Bidirectional streams
    for i, (y1, y2) in enumerate([(4.7, 4.3), (4.4, 4.0), (4.1, 3.7)]):
        ax4.arrow(3, y1, 3.5, 0, head_width=0.05, head_length=0.15, fc='blue', ec='blue')
        ax4.arrow(7, y2, -3.5, 0, head_width=0.05, head_length=0.15, fc='green', ec='green')
    
    ax4.text(5, 2, 'Stream of requests ↔ Stream of responses\nExample: LiveTrading(actions)', 
            ha='center', va='center', fontsize=10, style='italic')
    
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('grpc_streaming_patterns.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_grpc_vs_rest_comparison():
    """Create gRPC vs REST performance comparison"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('gRPC vs REST Performance Comparison', fontsize=16, fontweight='bold')
    
    # Payload Size Comparison
    ax1.set_title('Payload Size Comparison')
    protocols = ['REST\n(JSON)', 'gRPC\n(Protobuf)']
    sizes = [1200, 600]  # bytes
    colors = ['red', 'green']
    
    bars = ax1.bar(protocols, sizes, color=colors, alpha=0.7)
    ax1.set_ylabel('Payload Size (bytes)')
    
    for bar, size in zip(bars, sizes):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 20,
                f'{size} bytes', ha='center', va='bottom', fontweight='bold')
    
    # Add savings annotation
    savings = ((sizes[0] - sizes[1]) / sizes[0]) * 100
    ax1.text(0.5, max(sizes) * 0.8, f'{savings:.0f}% smaller', 
            ha='center', va='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'))
    
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Serialization Speed
    ax2.set_title('Serialization Performance')
    protocols = ['REST\n(JSON)', 'gRPC\n(Protobuf)']
    times = [0.8, 0.2]  # milliseconds
    
    bars = ax2.bar(protocols, times, color=colors, alpha=0.7)
    ax2.set_ylabel('Serialization Time (ms)')
    
    for bar, time in zip(bars, times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{time} ms', ha='center', va='bottom', fontweight='bold')
    
    # Add improvement annotation
    improvement = ((times[0] - times[1]) / times[0]) * 100
    ax2.text(0.5, max(times) * 0.8, f'{improvement:.0f}% faster', 
            ha='center', va='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'))
    
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Throughput Comparison
    ax3.set_title('Request Throughput')
    protocols = ['REST\n(HTTP/1.1)', 'gRPC\n(HTTP/2)']
    throughput = [500, 8500]  # requests per second
    
    bars = ax3.bar(protocols, throughput, color=colors, alpha=0.7)
    ax3.set_ylabel('Requests per Second')
    
    for bar, rps in zip(bars, throughput):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 200,
                f'{rps:,} RPS', ha='center', va='bottom', fontweight='bold')
    
    # Add improvement annotation
    improvement = throughput[1] / throughput[0]
    ax3.text(0.5, max(throughput) * 0.8, f'{improvement:.0f}x faster', 
            ha='center', va='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'))
    
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Feature Comparison
    ax4.set_title('Feature Comparison')
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 10)
    
    features = [
        {'name': 'Streaming Support', 'rest': 2, 'grpc': 9, 'y': 8.5},
        {'name': 'Type Safety', 'rest': 3, 'grpc': 9, 'y': 7.5},
        {'name': 'Performance', 'rest': 5, 'grpc': 9, 'y': 6.5},
        {'name': 'Browser Support', 'rest': 9, 'grpc': 6, 'y': 5.5},
        {'name': 'Simplicity', 'rest': 8, 'grpc': 6, 'y': 4.5},
        {'name': 'Tooling', 'rest': 9, 'grpc': 7, 'y': 3.5}
    ]
    
    for feature in features:
        # Feature name
        ax4.text(0.5, feature['y'], feature['name'], ha='left', va='center', fontweight='bold')
        
        # REST bar
        rest_bar = FancyBboxPatch((3, feature['y']-0.15), feature['rest']*0.6, 0.3,
                                 boxstyle="round,pad=0.02", facecolor='red', alpha=0.7)
        ax4.add_patch(rest_bar)
        ax4.text(3 + feature['rest']*0.6 + 0.1, feature['y'], f"REST: {feature['rest']}/10",
                ha='left', va='center', fontsize=9)
        
        # gRPC bar
        grpc_bar = FancyBboxPatch((3, feature['y']-0.45), feature['grpc']*0.6, 0.3,
                                 boxstyle="round,pad=0.02", facecolor='green', alpha=0.7)
        ax4.add_patch(grpc_bar)
        ax4.text(3 + feature['grpc']*0.6 + 0.1, feature['y']-0.3, f"gRPC: {feature['grpc']}/10",
                ha='left', va='center', fontsize=9)
    
    ax4.set_xticks([])
    ax4.set_yticks([])
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('grpc_vs_rest_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_grpc_use_cases_diagram():
    """Create gRPC use cases diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('gRPC Use Cases and Applications', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # Central gRPC node
    center_box = FancyBboxPatch((6, 5.5), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='gold', edgecolor='black', linewidth=2)
    ax.add_patch(center_box)
    ax.text(7, 6, 'gRPC', ha='center', va='center', fontweight='bold', fontsize=14)
    
    # Use case categories
    use_cases = [
        {
            'name': 'Microservices\nCommunication',
            'examples': ['Service Mesh', 'API Gateway', 'Load Balancing'],
            'position': (2, 9),
            'color': 'lightblue'
        },
        {
            'name': 'Real-Time\nStreaming',
            'examples': ['Market Data', 'IoT Telemetry', 'Live Updates'],
            'position': (12, 9),
            'color': 'lightgreen'
        },
        {
            'name': 'Mobile &\nWeb APIs',
            'examples': ['Mobile Apps', 'Web Clients', 'PWAs'],
            'position': (2, 3),
            'color': 'lightcoral'
        },
        {
            'name': 'High-Performance\nComputing',
            'examples': ['ML Training', 'Data Processing', 'Analytics'],
            'position': (12, 3),
            'color': 'lightyellow'
        }
    ]
    
    for use_case in use_cases:
        x, y = use_case['position']
        
        # Main category box
        case_box = FancyBboxPatch((x-1.5, y-0.5), 3, 1, boxstyle="round,pad=0.1",
                                 facecolor=use_case['color'], edgecolor='black')
        ax.add_patch(case_box)
        ax.text(x, y, use_case['name'], ha='center', va='center', 
               fontweight='bold', fontsize=11)
        
        # Connection to center
        ax.plot([x, 7], [y, 6], 'k--', alpha=0.5, linewidth=1)
        
        # Examples
        for i, example in enumerate(use_case['examples']):
            ex_y = y - 1.5 - i * 0.4
            example_box = FancyBboxPatch((x-1.2, ex_y-0.1), 2.4, 0.25, 
                                       boxstyle="round,pad=0.02",
                                       facecolor='white', edgecolor=use_case['color'])
            ax.add_patch(example_box)
            ax.text(x, ex_y, example, ha='center', va='center', fontsize=9)
    
    # Benefits section
    benefits_box = FancyBboxPatch((1, 0.5), 12, 1, boxstyle="round,pad=0.1",
                                 facecolor='lightcyan', edgecolor='black')
    ax.add_patch(benefits_box)
    ax.text(7, 1, 'Key Benefits', ha='center', va='center',
           fontweight='bold', fontsize=12)
    
    benefits = [
        'Type-Safe APIs',
        'High Performance',
        'Streaming Support',
        'Cross-Language',
        'HTTP/2 Transport'
    ]
    
    benefit_text = ' • '.join(benefits)
    ax.text(7, 0.7, benefit_text, ha='center', va='center', fontsize=10)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('grpc_use_cases.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_grpc_performance_metrics():
    """Create gRPC performance metrics chart"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('gRPC Performance Metrics', fontsize=16, fontweight='bold')
    
    # Latency Distribution
    ax1.set_title('Response Latency Distribution')
    latencies = np.random.gamma(2, 1.5, 1000)  # Simulated latency data
    ax1.hist(latencies, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    ax1.axvline(np.percentile(latencies, 95), color='red', linestyle='--', 
               label=f'P95: {np.percentile(latencies, 95):.1f}ms')
    ax1.axvline(np.percentile(latencies, 99), color='orange', linestyle='--',
               label=f'P99: {np.percentile(latencies, 99):.1f}ms')
    ax1.set_xlabel('Latency (ms)')
    ax1.set_ylabel('Frequency')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Throughput over Time
    ax2.set_title('Throughput Over Time')
    time_points = np.arange(0, 60, 1)
    throughput = 8000 + 1000 * np.sin(time_points * 0.1) + np.random.normal(0, 200, len(time_points))
    ax2.plot(time_points, throughput, 'g-', linewidth=2, alpha=0.8)
    ax2.fill_between(time_points, throughput, alpha=0.3, color='green')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('Requests per Second')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(6000, 10000)
    
    # Connection Efficiency
    ax3.set_title('Connection Efficiency')
    scenarios = ['HTTP/1.1\nREST', 'gRPC\nHTTP/2']
    connections = [100, 1]  # Number of connections needed
    
    bars = ax3.bar(scenarios, connections, color=['red', 'green'], alpha=0.7)
    ax3.set_ylabel('Connections Required')
    ax3.set_yscale('log')
    
    for bar, conn in zip(bars, connections):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height * 1.5,
                f'{conn}', ha='center', va='bottom', fontweight='bold')
    
    # Add efficiency note
    ax3.text(0.5, 50, '100x more\nefficient', ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'),
            fontweight='bold')
    
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Resource Usage
    ax4.set_title('Resource Usage Comparison')
    resources = ['CPU\nUsage', 'Memory\nUsage', 'Network\nBandwidth']
    rest_usage = [80, 120, 150]  # Relative units
    grpc_usage = [40, 60, 75]   # Relative units
    
    x = np.arange(len(resources))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, rest_usage, width, label='REST', color='red', alpha=0.7)
    bars2 = ax4.bar(x + width/2, grpc_usage, width, label='gRPC', color='green', alpha=0.7)
    
    ax4.set_ylabel('Resource Usage (relative)')
    ax4.set_xticks(x)
    ax4.set_xticklabels(resources)
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add improvement percentages
    for i, (rest, grpc) in enumerate(zip(rest_usage, grpc_usage)):
        improvement = ((rest - grpc) / rest) * 100
        ax4.text(i, max(rest, grpc) + 10, f'-{improvement:.0f}%', 
                ha='center', va='bottom', fontweight='bold', color='green')
    
    plt.tight_layout()
    plt.savefig('grpc_performance_metrics.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Generating gRPC protocol diagrams...")
    
    # Generate all diagrams
    create_grpc_architecture_diagram()
    print("✓ gRPC architecture diagram created")
    
    create_grpc_streaming_patterns()
    print("✓ gRPC streaming patterns diagram created")
    
    create_grpc_vs_rest_comparison()
    print("✓ gRPC vs REST comparison diagram created")
    
    create_grpc_use_cases_diagram()
    print("✓ gRPC use cases diagram created")
    
    create_grpc_performance_metrics()
    print("✓ gRPC performance metrics chart created")
    
    print("\nAll gRPC diagrams generated successfully!")
    print("Files created:")
    print("  - grpc_architecture.png")
    print("  - grpc_streaming_patterns.png")
    print("  - grpc_vs_rest_comparison.png")
    print("  - grpc_use_cases.png")
    print("  - grpc_performance_metrics.png")
