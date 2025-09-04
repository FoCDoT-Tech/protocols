#!/usr/bin/env python3
"""
HTTP/2 & gRPC Multiplexing Diagram Renderer
Generates visual diagrams for stream multiplexing and performance comparisons
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle, Rectangle
import numpy as np
import matplotlib.gridspec as gridspec

def render_http2_multiplexing_architecture():
    """Render HTTP/2 multiplexing architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Colors
    client_color = '#E3F2FD'
    connection_color = '#F3E5F5'
    stream_color = '#E8F5E8'
    server_color = '#FFF3E0'
    frame_color = '#FFEBEE'
    
    # Title
    ax.text(8, 11.5, 'HTTP/2 & gRPC Stream Multiplexing Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Client Side
    client_box = FancyBboxPatch((1, 8.5), 3, 2.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor=client_color, 
                               edgecolor='black', linewidth=2)
    ax.add_patch(client_box)
    ax.text(2.5, 10.5, 'gRPC Client', fontsize=14, fontweight='bold', ha='center')
    
    # Client components
    client_components = [
        ('Connection\nManager', 1.5, 9.8),
        ('Stream\nPool', 2.5, 9.8),
        ('Request\nQueue', 3.5, 9.8),
        ('Flow Control', 2.5, 9.2)
    ]
    
    for name, x, y in client_components:
        comp_box = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor='white', 
                                 edgecolor='blue', linewidth=1)
        ax.add_patch(comp_box)
        ax.text(x, y, name, fontsize=8, ha='center', fontweight='bold')
    
    # HTTP/2 Connection
    connection_box = FancyBboxPatch((5.5, 6), 5, 5, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=connection_color, 
                                   edgecolor='black', linewidth=2)
    ax.add_patch(connection_box)
    ax.text(8, 10.5, 'HTTP/2 Connection', fontsize=14, fontweight='bold', ha='center')
    
    # Individual Streams
    streams = [
        ('Stream 1\nGetVideo', 6, 9.5, '#4CAF50'),
        ('Stream 2\nProcessChunk', 7, 9.5, '#2196F3'),
        ('Stream 3\nUploadData', 8, 9.5, '#FF9800'),
        ('Stream 4\nLiveStream', 9, 9.5, '#9C27B0'),
        ('Stream 5\nHeartbeat', 10, 9.5, '#F44336')
    ]
    
    for name, x, y, color in streams:
        stream_box = FancyBboxPatch((x-0.4, y-0.4), 0.8, 0.8, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor=color, 
                                   edgecolor='black', linewidth=1, alpha=0.7)
        ax.add_patch(stream_box)
        ax.text(x, y, name, fontsize=7, ha='center', fontweight='bold', color='white')
    
    # HTTP/2 Features
    features = [
        ('HPACK\nCompression', 6.5, 8.5),
        ('Flow Control\nWINDOW_UPDATE', 8, 8.5),
        ('Stream Priority\nDependencies', 9.5, 8.5),
        ('Server Push\n(Optional)', 6.5, 7.5),
        ('Binary Framing\nProtocol', 8, 7.5),
        ('Connection\nMultiplexing', 9.5, 7.5)
    ]
    
    for name, x, y in features:
        feature_box = FancyBboxPatch((x-0.5, y-0.3), 1, 0.6, 
                                    boxstyle="round,pad=0.05", 
                                    facecolor='white', 
                                    edgecolor='purple', linewidth=1)
        ax.add_patch(feature_box)
        ax.text(x, y, name, fontsize=7, ha='center', fontweight='bold')
    
    # Frame Types
    frame_box = FancyBboxPatch((6, 6.5), 4, 0.8, 
                              boxstyle="round,pad=0.05", 
                              facecolor=frame_color, 
                              edgecolor='black', linewidth=1)
    ax.add_patch(frame_box)
    ax.text(8, 6.9, 'HTTP/2 Frame Types: HEADERS | DATA | WINDOW_UPDATE | RST_STREAM | SETTINGS | PING', 
            fontsize=9, ha='center', fontweight='bold')
    
    # Server Side
    server_box = FancyBboxPatch((12, 8.5), 3, 2.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor=server_color, 
                               edgecolor='black', linewidth=2)
    ax.add_patch(server_box)
    ax.text(13.5, 10.5, 'gRPC Server', fontsize=14, fontweight='bold', ha='center')
    
    # Server components
    server_components = [
        ('Stream\nHandler', 12.5, 9.8),
        ('Worker\nPool', 13.5, 9.8),
        ('Response\nGenerator', 14.5, 9.8),
        ('Load Balancer', 13.5, 9.2)
    ]
    
    for name, x, y in server_components:
        comp_box = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor='white', 
                                 edgecolor='orange', linewidth=1)
        ax.add_patch(comp_box)
        ax.text(x, y, name, fontsize=8, ha='center', fontweight='bold')
    
    # Connection arrows
    ax.arrow(4, 9.7, 1.3, 0, head_width=0.1, head_length=0.1, fc='blue', ec='blue', lw=2)
    ax.arrow(10.7, 9.7, 1.1, 0, head_width=0.1, head_length=0.1, fc='orange', ec='orange', lw=2)
    
    # Stream flow indicators
    for i, (_, x, y, color) in enumerate(streams):
        # Bidirectional arrows for streams
        ax.annotate('', xy=(x+0.5, y), xytext=(x-0.5, y),
                   arrowprops=dict(arrowstyle='<->', color=color, lw=1.5, alpha=0.8))
    
    # gRPC Streaming Types
    ax.text(8, 5.5, 'gRPC Streaming Patterns', fontsize=12, fontweight='bold', ha='center')
    
    streaming_types = [
        ('Unary RPC\n1 Request → 1 Response', 2, 4.5, '#4CAF50'),
        ('Server Streaming\n1 Request → N Responses', 5.5, 4.5, '#2196F3'),
        ('Client Streaming\nN Requests → 1 Response', 9, 4.5, '#FF9800'),
        ('Bidirectional\nN Requests ↔ N Responses', 12.5, 4.5, '#9C27B0')
    ]
    
    for name, x, y, color in streaming_types:
        type_box = FancyBboxPatch((x-1, y-0.5), 2, 1, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=color, 
                                 edgecolor='black', linewidth=1, alpha=0.8)
        ax.add_patch(type_box)
        ax.text(x, y, name, fontsize=9, ha='center', fontweight='bold', color='white')
    
    # Performance Benefits
    benefits_box = FancyBboxPatch((1, 2.5), 14, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#F1F8E9', 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(benefits_box)
    ax.text(8, 3.7, 'HTTP/2 Multiplexing Benefits', fontsize=12, fontweight='bold', ha='center')
    
    benefits = [
        '• Single TCP connection eliminates connection overhead',
        '• No head-of-line blocking at HTTP level',
        '• Concurrent request/response processing',
        '• Header compression reduces bandwidth usage',
        '• Stream prioritization for critical requests',
        '• Flow control prevents receiver overload'
    ]
    
    for i, benefit in enumerate(benefits):
        col = i % 2
        row = i // 2
        x = 3 + col * 8
        y = 3.4 - row * 0.2
        ax.text(x, y, benefit, fontsize=9, ha='left')
    
    # Metrics
    metrics_box = FancyBboxPatch((1, 0.5), 14, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#E8EAF6', 
                                edgecolor='black', linewidth=1)
    ax.add_patch(metrics_box)
    ax.text(8, 1.7, 'Performance Metrics', fontsize=12, fontweight='bold', ha='center')
    
    metrics = [
        'Concurrent Streams: 100-1000+ per connection',
        'Header Compression: 85-90% size reduction',
        'Latency Reduction: 50-80% vs HTTP/1.1',
        'Connection Efficiency: 90%+ utilization',
        'Throughput Increase: 2-10x improvement',
        'Memory Usage: 60% reduction per request'
    ]
    
    for i, metric in enumerate(metrics):
        col = i % 2
        row = i // 2
        x = 3 + col * 8
        y = 1.4 - row * 0.2
        ax.text(x, y, metric, fontsize=9, ha='left', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('http2_multiplexing_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated http2_multiplexing_architecture.png")

def render_stream_lifecycle_diagram():
    """Render HTTP/2 stream lifecycle and state transitions"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'HTTP/2 Stream Lifecycle and State Transitions', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Stream states
    states = [
        ('idle', 2, 7, '#E0E0E0'),
        ('reserved\n(local)', 4, 8.5, '#FFEB3B'),
        ('reserved\n(remote)', 4, 5.5, '#FFEB3B'),
        ('open', 7, 7, '#4CAF50'),
        ('half closed\n(local)', 10, 8.5, '#FF9800'),
        ('half closed\n(remote)', 10, 5.5, '#FF9800'),
        ('closed', 12, 7, '#F44336')
    ]
    
    for name, x, y, color in states:
        state_circle = Circle((x, y), 0.8, facecolor=color, edgecolor='black', linewidth=2, alpha=0.8)
        ax.add_patch(state_circle)
        ax.text(x, y, name, fontsize=10, ha='center', va='center', fontweight='bold')
    
    # State transitions
    transitions = [
        # From idle
        (2.8, 7.4, 3.2, 8.1, 'HEADERS\n(send)'),
        (2.8, 6.6, 3.2, 5.9, 'HEADERS\n(recv)'),
        (2.8, 7, 6.2, 7, 'HEADERS\n(send/recv)'),
        
        # From reserved to open
        (4.8, 8.5, 6.2, 7.4, 'HEADERS\n(recv)'),
        (4.8, 5.5, 6.2, 6.6, 'HEADERS\n(send)'),
        
        # From open to half-closed
        (7.8, 7.4, 9.2, 8.1, 'END_STREAM\n(send)'),
        (7.8, 6.6, 9.2, 5.9, 'END_STREAM\n(recv)'),
        
        # From half-closed to closed
        (10.8, 8.5, 11.2, 7.4, 'END_STREAM\n(recv)'),
        (10.8, 5.5, 11.2, 6.6, 'END_STREAM\n(send)'),
        
        # Direct to closed
        (2.8, 7, 11.2, 7, 'RST_STREAM'),
        (7.8, 7, 11.2, 7, 'RST_STREAM')
    ]
    
    for x1, y1, x2, y2, label in transitions:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', color='blue', lw=1.5))
        
        # Add label
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.2, label, fontsize=7, ha='center', 
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Frame sequence example
    ax.text(7, 4, 'Typical Stream Frame Sequence', fontsize=12, fontweight='bold', ha='center')
    
    # Timeline
    timeline_y = 3
    ax.plot([1, 13], [timeline_y, timeline_y], 'k-', linewidth=2)
    
    # Frame sequence
    frames = [
        (2, 'HEADERS\n(request)', '#4CAF50'),
        (4, 'DATA\n(payload)', '#2196F3'),
        (6, 'DATA\n(more)', '#2196F3'),
        (8, 'HEADERS\n(response)', '#FF9800'),
        (10, 'DATA\n(response)', '#9C27B0'),
        (12, 'DATA\nEND_STREAM', '#F44336')
    ]
    
    for x, label, color in frames:
        # Frame marker
        frame_rect = Rectangle((x-0.3, timeline_y-0.2), 0.6, 0.4, 
                              facecolor=color, edgecolor='black', linewidth=1, alpha=0.8)
        ax.add_patch(frame_rect)
        
        # Frame label
        ax.text(x, timeline_y - 0.8, label, fontsize=8, ha='center', fontweight='bold')
        
        # Timeline marker
        ax.plot([x, x], [timeline_y-0.1, timeline_y+0.1], 'k-', linewidth=2)
    
    # Flow control example
    ax.text(7, 1.5, 'Flow Control Window Management', fontsize=11, fontweight='bold', ha='center')
    
    # Window visualization
    window_y = 0.8
    window_width = 8
    window_height = 0.4
    
    # Total window
    total_window = Rectangle((3, window_y), window_width, window_height, 
                           facecolor='lightblue', edgecolor='black', linewidth=1)
    ax.add_patch(total_window)
    
    # Used portion
    used_width = window_width * 0.6
    used_window = Rectangle((3, window_y), used_width, window_height, 
                          facecolor='blue', edgecolor='black', linewidth=1, alpha=0.7)
    ax.add_patch(used_window)
    
    # Labels
    ax.text(7, window_y + 0.2, f'Flow Control Window: {used_width/window_width*100:.0f}% Used', 
           fontsize=9, ha='center', fontweight='bold', color='white')
    ax.text(3, window_y - 0.3, 'Available', fontsize=8, ha='left')
    ax.text(11, window_y - 0.3, 'Used', fontsize=8, ha='right')
    
    plt.tight_layout()
    plt.savefig('stream_lifecycle_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated stream_lifecycle_diagram.png")

def render_performance_comparison():
    """Render HTTP/1.1 vs HTTP/2 performance comparison"""
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig)
    
    # HTTP/1.1 vs HTTP/2 Connection Usage
    ax1 = fig.add_subplot(gs[0, 0])
    
    # HTTP/1.1 - Multiple connections
    requests = 10
    connections_http1 = 6
    
    for i in range(connections_http1):
        y_pos = i * 0.8
        ax1.barh(y_pos, 1, height=0.6, color='red', alpha=0.7, label='HTTP/1.1' if i == 0 else '')
        ax1.text(0.5, y_pos, f'Conn {i+1}', ha='center', va='center', fontweight='bold', color='white')
    
    ax1.set_ylim(-0.5, connections_http1 * 0.8)
    ax1.set_xlim(0, 2)
    ax1.set_title('HTTP/1.1: Multiple Connections', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Connection Usage')
    ax1.legend()
    
    # HTTP/2 - Single connection with streams
    ax2 = fig.add_subplot(gs[0, 1])
    
    # Single connection with multiple streams
    ax2.barh(0, 1, height=0.6, color='green', alpha=0.7, label='HTTP/2')
    ax2.text(0.5, 0, 'Single Connection\n10 Streams', ha='center', va='center', fontweight='bold', color='white')
    
    ax2.set_ylim(-0.5, 1)
    ax2.set_xlim(0, 2)
    ax2.set_title('HTTP/2: Single Connection', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Connection Usage')
    ax2.legend()
    
    # Latency comparison
    ax3 = fig.add_subplot(gs[1, 0])
    
    scenarios = ['1 Request', '5 Requests', '10 Requests', '50 Requests']
    http1_latency = [100, 300, 600, 3000]  # ms
    http2_latency = [100, 150, 200, 800]   # ms
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, http1_latency, width, label='HTTP/1.1', color='red', alpha=0.7)
    bars2 = ax3.bar(x + width/2, http2_latency, width, label='HTTP/2', color='green', alpha=0.7)
    
    ax3.set_xlabel('Request Scenarios')
    ax3.set_ylabel('Latency (ms)')
    ax3.set_title('Latency Comparison', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(scenarios)
    ax3.legend()
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'{int(height)}ms', ha='center', va='bottom', fontsize=8)
    
    for bar in bars2:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'{int(height)}ms', ha='center', va='bottom', fontsize=8)
    
    # Throughput comparison
    ax4 = fig.add_subplot(gs[1, 1])
    
    time_points = np.linspace(0, 10, 100)
    http1_throughput = 50 + 10 * np.sin(time_points) + np.random.normal(0, 5, 100)
    http2_throughput = 120 + 20 * np.sin(time_points * 0.5) + np.random.normal(0, 3, 100)
    
    ax4.plot(time_points, http1_throughput, label='HTTP/1.1', color='red', linewidth=2)
    ax4.plot(time_points, http2_throughput, label='HTTP/2', color='green', linewidth=2)
    ax4.fill_between(time_points, http1_throughput, alpha=0.3, color='red')
    ax4.fill_between(time_points, http2_throughput, alpha=0.3, color='green')
    
    ax4.set_xlabel('Time (seconds)')
    ax4.set_ylabel('Requests/second')
    ax4.set_title('Throughput Over Time', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('HTTP/1.1 vs HTTP/2 Performance Comparison', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated performance_comparison.png")

def render_all_diagrams():
    """Render all HTTP/2 & gRPC multiplexing diagrams"""
    print("Rendering HTTP/2 & gRPC multiplexing diagrams...")
    
    render_http2_multiplexing_architecture()
    render_stream_lifecycle_diagram()
    render_performance_comparison()
    
    print("All HTTP/2 & gRPC multiplexing diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
