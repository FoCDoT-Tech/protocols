#!/usr/bin/env python3
"""
HTTP/2 Protocol Diagram Renderer
Generates visual diagrams for HTTP/2 concepts using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_http2_multiplexing_diagram():
    """Create HTTP/2 stream multiplexing diagram"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # HTTP/1.1 diagram (left)
    ax1.set_title('HTTP/1.1 - Multiple Connections', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    
    # Client
    client_box = FancyBboxPatch((1, 8), 2, 1, boxstyle="round,pad=0.1", 
                               facecolor='lightblue', edgecolor='black')
    ax1.add_patch(client_box)
    ax1.text(2, 8.5, 'Client', ha='center', va='center', fontweight='bold')
    
    # Multiple servers/connections
    colors = ['lightcoral', 'lightgreen', 'lightyellow', 'lightpink']
    resources = ['HTML', 'CSS', 'JS', 'IMG']
    
    for i, (color, resource) in enumerate(zip(colors, resources)):
        server_box = FancyBboxPatch((7, 7.5 - i * 1.5), 2, 1, boxstyle="round,pad=0.1",
                                   facecolor=color, edgecolor='black')
        ax1.add_patch(server_box)
        ax1.text(8, 8 - i * 1.5, f'Server\n({resource})', ha='center', va='center', fontweight='bold')
        
        # Connection lines
        ax1.arrow(3, 8.5, 3.5, -0.5 - i * 1.5, head_width=0.1, head_length=0.2, 
                 fc='black', ec='black')
        ax1.text(5, 8 - i * 0.7, f'TCP {i+1}', ha='center', va='center', 
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white'))
    
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.text(5, 1, 'Multiple TCP connections\nHead-of-line blocking\nConnection overhead', 
             ha='center', va='center', fontsize=10, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor='mistyrose'))
    
    # HTTP/2 diagram (right)
    ax2.set_title('HTTP/2 - Single Connection Multiplexing', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    
    # Client
    client_box = FancyBboxPatch((1, 8), 2, 1, boxstyle="round,pad=0.1", 
                               facecolor='lightblue', edgecolor='black')
    ax2.add_patch(client_box)
    ax2.text(2, 8.5, 'Client', ha='center', va='center', fontweight='bold')
    
    # Single server
    server_box = FancyBboxPatch((7, 8), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax2.add_patch(server_box)
    ax2.text(8, 8.5, 'Server', ha='center', va='center', fontweight='bold')
    
    # Single connection with multiple streams
    ax2.arrow(3, 8.5, 3.5, 0, head_width=0.1, head_length=0.2, 
             fc='black', ec='black', linewidth=3)
    ax2.text(5, 9, 'Single TCP Connection', ha='center', va='center', fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgreen'))
    
    # Stream representations
    stream_colors = ['red', 'blue', 'green', 'orange']
    stream_names = ['Stream 1 (HTML)', 'Stream 3 (CSS)', 'Stream 5 (JS)', 'Stream 7 (IMG)']
    
    for i, (color, name) in enumerate(zip(stream_colors, stream_names)):
        y_pos = 7 - i * 0.8
        # Stream line
        ax2.plot([3, 7], [y_pos, y_pos], color=color, linewidth=2, alpha=0.7)
        ax2.text(5, y_pos + 0.2, name, ha='center', va='center', fontsize=9,
                bbox=dict(boxstyle="round,pad=0.1", facecolor=color, alpha=0.3))
    
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.text(5, 1, 'Single TCP connection\nNo head-of-line blocking\nStream prioritization\nBinary framing', 
             ha='center', va='center', fontsize=10,
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig('http2_multiplexing.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_http2_binary_framing_diagram():
    """Create HTTP/2 binary framing diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('HTTP/2 Binary Framing Layer', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # HTTP/1.1 text representation
    ax.text(7, 11, 'HTTP/1.1 vs HTTP/2 Message Format', ha='center', va='center', 
            fontsize=14, fontweight='bold')
    
    # HTTP/1.1 section
    http1_box = FancyBboxPatch((0.5, 8.5), 6, 2, boxstyle="round,pad=0.1",
                              facecolor='mistyrose', edgecolor='black')
    ax.add_patch(http1_box)
    ax.text(3.5, 10, 'HTTP/1.1 (Text-based)', ha='center', va='center', fontweight='bold')
    
    http1_text = """GET /index.html HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0...
Accept: text/html,application/xhtml+xml"""
    
    ax.text(3.5, 9.2, http1_text, ha='center', va='center', fontsize=9, 
            fontfamily='monospace')
    
    # HTTP/2 section
    http2_box = FancyBboxPatch((7.5, 8.5), 6, 2, boxstyle="round,pad=0.1",
                              facecolor='lightcyan', edgecolor='black')
    ax.add_patch(http2_box)
    ax.text(10.5, 10, 'HTTP/2 (Binary Frames)', ha='center', va='center', fontweight='bold')
    
    # Binary frame representation
    frame_data = [
        ['Length (24)', 'Type (8)', 'Flags (8)', 'R (1)', 'Stream ID (31)'],
        ['Frame Payload (Length octets)']
    ]
    
    # Frame header
    colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightpink', 'lightcoral']
    x_start = 8
    for i, (field, color) in enumerate(zip(frame_data[0], colors)):
        width = 1 if i < 3 else 0.5 if i == 3 else 1.5
        rect = FancyBboxPatch((x_start, 9.5), width, 0.4, boxstyle="round,pad=0.02",
                             facecolor=color, edgecolor='black')
        ax.add_patch(rect)
        ax.text(x_start + width/2, 9.7, field, ha='center', va='center', fontsize=7)
        x_start += width
    
    # Frame payload
    payload_rect = FancyBboxPatch((8, 9), 5, 0.4, boxstyle="round,pad=0.02",
                                 facecolor='lavender', edgecolor='black')
    ax.add_patch(payload_rect)
    ax.text(10.5, 9.2, 'Frame Payload (Length octets)', ha='center', va='center', fontsize=8)
    
    # Frame types section
    ax.text(7, 7.5, 'HTTP/2 Frame Types', ha='center', va='center', 
            fontsize=14, fontweight='bold')
    
    frame_types = [
        {'name': 'HEADERS', 'desc': 'Header information', 'color': 'lightblue'},
        {'name': 'DATA', 'desc': 'Message body data', 'color': 'lightgreen'},
        {'name': 'SETTINGS', 'desc': 'Connection settings', 'color': 'lightyellow'},
        {'name': 'PUSH_PROMISE', 'desc': 'Server push notification', 'color': 'lightpink'},
        {'name': 'WINDOW_UPDATE', 'desc': 'Flow control', 'color': 'lightcoral'},
        {'name': 'GOAWAY', 'desc': 'Connection termination', 'color': 'lavender'}
    ]
    
    for i, frame_type in enumerate(frame_types):
        x = (i % 3) * 4.5 + 1
        y = 5.5 - (i // 3) * 1.5
        
        frame_box = FancyBboxPatch((x, y), 4, 1, boxstyle="round,pad=0.1",
                                  facecolor=frame_type['color'], edgecolor='black')
        ax.add_patch(frame_box)
        ax.text(x + 2, y + 0.7, frame_type['name'], ha='center', va='center', 
                fontweight='bold', fontsize=10)
        ax.text(x + 2, y + 0.3, frame_type['desc'], ha='center', va='center', 
                fontsize=9)
    
    # Benefits section
    benefits_box = FancyBboxPatch((2, 1), 10, 1.5, boxstyle="round,pad=0.1",
                                 facecolor='lightgreen', alpha=0.3, edgecolor='black')
    ax.add_patch(benefits_box)
    ax.text(7, 2, 'Binary Framing Benefits', ha='center', va='center', 
            fontweight='bold', fontsize=12)
    
    benefits = "• More efficient parsing  • Smaller message size  • Less error-prone\n• Enables multiplexing  • Better compression  • Stream prioritization"
    ax.text(7, 1.5, benefits, ha='center', va='center', fontsize=10)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('http2_binary_framing.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_http2_server_push_diagram():
    """Create HTTP/2 server push flow diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('HTTP/2 Server Push Flow', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # Client and Server
    client_box = FancyBboxPatch((1, 10), 2.5, 1, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax.add_patch(client_box)
    ax.text(2.25, 10.5, 'Client', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((10.5, 10), 2.5, 1, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax.add_patch(server_box)
    ax.text(11.75, 10.5, 'Server', ha='center', va='center', fontweight='bold')
    
    # Timeline
    ax.plot([2.25, 2.25], [1, 9.5], 'k-', linewidth=2)
    ax.plot([11.75, 11.75], [1, 9.5], 'k-', linewidth=2)
    
    # Flow steps
    steps = [
        {'y': 9, 'client_text': '1. GET /index.html', 'direction': 'right', 'color': 'blue'},
        {'y': 8.2, 'server_text': '2. Analyze request\n   Identify push candidates', 'direction': 'left', 'color': 'green'},
        {'y': 7.4, 'server_text': '3. PUSH_PROMISE\n   /css/main.css', 'direction': 'left', 'color': 'orange'},
        {'y': 6.6, 'server_text': '4. PUSH_PROMISE\n   /js/app.js', 'direction': 'left', 'color': 'orange'},
        {'y': 5.8, 'server_text': '5. HEADERS + DATA\n   index.html', 'direction': 'left', 'color': 'blue'},
        {'y': 5, 'server_text': '6. HEADERS + DATA\n   main.css (pushed)', 'direction': 'left', 'color': 'red'},
        {'y': 4.2, 'server_text': '7. HEADERS + DATA\n   app.js (pushed)', 'direction': 'left', 'color': 'red'},
        {'y': 3.4, 'client_text': '8. Parse HTML\n   Resources already available!', 'direction': 'right', 'color': 'green'}
    ]
    
    for step in steps:
        y = step['y']
        
        if 'client_text' in step:
            # Client action
            if step['direction'] == 'right':
                ax.arrow(2.25, y, 8.5, 0, head_width=0.1, head_length=0.3,
                        fc=step['color'], ec=step['color'], alpha=0.7)
            ax.text(2.25, y + 0.3, step['client_text'], ha='left', va='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor=step['color'], alpha=0.3))
        
        if 'server_text' in step:
            # Server action
            if step['direction'] == 'left':
                ax.arrow(11.75, y, -8.5, 0, head_width=0.1, head_length=0.3,
                        fc=step['color'], ec=step['color'], alpha=0.7)
            ax.text(11.75, y + 0.3, step['server_text'], ha='right', va='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor=step['color'], alpha=0.3))
    
    # Benefits box
    benefits_box = FancyBboxPatch((4, 1.5), 6, 1.5, boxstyle="round,pad=0.1",
                                 facecolor='lightyellow', edgecolor='black')
    ax.add_patch(benefits_box)
    ax.text(7, 2.7, 'Server Push Benefits', ha='center', va='center', 
            fontweight='bold', fontsize=12)
    
    benefits = """• Eliminates round trips for critical resources
• Resources available when HTML parsing completes
• Faster time to first meaningful paint
• Proactive resource delivery"""
    
    ax.text(7, 2, benefits, ha='center', va='center', fontsize=10)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('http2_server_push.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_http2_hpack_compression_diagram():
    """Create HPACK header compression diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('HTTP/2 HPACK Header Compression', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # Static table section
    static_box = FancyBboxPatch((0.5, 8), 6, 3.5, boxstyle="round,pad=0.1",
                               facecolor='lightblue', alpha=0.3, edgecolor='black')
    ax.add_patch(static_box)
    ax.text(3.5, 11, 'HPACK Static Table', ha='center', va='center', 
            fontweight='bold', fontsize=12)
    
    static_entries = [
        '1: :authority',
        '2: :method GET',
        '3: :method POST',
        '4: :path /',
        '5: :scheme http',
        '6: :scheme https',
        '7: :status 200',
        '8: :status 204',
        '...',
        '61: www-authenticate'
    ]
    
    for i, entry in enumerate(static_entries):
        ax.text(1, 10.5 - i * 0.25, entry, ha='left', va='center', fontsize=9,
               fontfamily='monospace')
    
    # Dynamic table section
    dynamic_box = FancyBboxPatch((7.5, 8), 6, 3.5, boxstyle="round,pad=0.1",
                                facecolor='lightgreen', alpha=0.3, edgecolor='black')
    ax.add_patch(dynamic_box)
    ax.text(10.5, 11, 'HPACK Dynamic Table', ha='center', va='center', 
            fontweight='bold', fontsize=12)
    
    dynamic_entries = [
        '62: user-agent Mozilla/5.0...',
        '63: accept application/json',
        '64: authorization Bearer...',
        '65: cache-control no-cache',
        '66: custom-header value123',
        '',
        'Updated per connection',
        'FIFO eviction',
        'Size limited'
    ]
    
    for i, entry in enumerate(dynamic_entries):
        ax.text(8, 10.5 - i * 0.25, entry, ha='left', va='center', fontsize=9,
               fontfamily='monospace')
    
    # Compression example
    ax.text(7, 7, 'Header Compression Example', ha='center', va='center', 
            fontweight='bold', fontsize=14)
    
    # Original headers
    original_box = FancyBboxPatch((0.5, 4.5), 6, 2, boxstyle="round,pad=0.1",
                                 facecolor='mistyrose', edgecolor='black')
    ax.add_patch(original_box)
    ax.text(3.5, 6, 'Original Headers (HTTP/1.1)', ha='center', va='center', 
            fontweight='bold')
    
    original_headers = """:method: GET
:path: /api/users
:scheme: https
:authority: api.example.com
user-agent: Mozilla/5.0 (Windows...)
accept: application/json
authorization: Bearer eyJhbGc..."""
    
    ax.text(3.5, 5.2, original_headers, ha='center', va='center', fontsize=9,
           fontfamily='monospace')
    
    # Compressed headers
    compressed_box = FancyBboxPatch((7.5, 4.5), 6, 2, boxstyle="round,pad=0.1",
                                   facecolor='lightcyan', edgecolor='black')
    ax.add_patch(compressed_box)
    ax.text(10.5, 6, 'HPACK Compressed', ha='center', va='center', 
            fontweight='bold')
    
    compressed_headers = """Index 2 (:method GET)
Literal /api/users
Index 6 (:scheme https)
Literal api.example.com
Index 62 (user-agent cached)
Index 63 (accept cached)
Index 64 (auth cached)"""
    
    ax.text(10.5, 5.2, compressed_headers, ha='center', va='center', fontsize=9,
           fontfamily='monospace')
    
    # Compression ratio
    ax.arrow(6.5, 5.5, 1, 0, head_width=0.1, head_length=0.2, fc='red', ec='red')
    ax.text(7, 5.8, '~70% reduction', ha='center', va='center', fontweight='bold',
           bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow'))
    
    # Huffman encoding section
    huffman_box = FancyBboxPatch((2, 1.5), 10, 2, boxstyle="round,pad=0.1",
                                facecolor='lightyellow', alpha=0.5, edgecolor='black')
    ax.add_patch(huffman_box)
    ax.text(7, 3, 'Huffman Encoding', ha='center', va='center', 
            fontweight='bold', fontsize=12)
    
    huffman_text = """Additional compression layer for string literals
Optimized for HTTP header patterns
Typically achieves 20-30% additional compression
Example: "application/json" → binary representation"""
    
    ax.text(7, 2.2, huffman_text, ha='center', va='center', fontsize=10)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('http2_hpack_compression.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_http2_performance_comparison():
    """Create HTTP/2 vs HTTP/1.1 performance comparison"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('HTTP/2 vs HTTP/1.1 Performance Comparison', fontsize=16, fontweight='bold')
    
    # Connection usage comparison
    ax1.set_title('Connection Usage')
    
    # HTTP/1.1 connections
    http1_connections = [1, 2, 3, 4, 5, 6, 6, 6, 6, 6]
    http1_requests = list(range(1, 11))
    
    # HTTP/2 connections (always 1)
    http2_connections = [1] * 10
    
    ax1.plot(http1_requests, http1_connections, 'r-o', label='HTTP/1.1', linewidth=2)
    ax1.plot(http1_requests, http2_connections, 'g-o', label='HTTP/2', linewidth=2)
    ax1.set_xlabel('Number of Requests')
    ax1.set_ylabel('TCP Connections')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Latency comparison
    ax2.set_title('Request Latency')
    
    # Simulate latency (HTTP/1.1 has head-of-line blocking)
    http1_latency = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
    http2_latency = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]
    
    ax2.plot(http1_requests, http1_latency, 'r-o', label='HTTP/1.1', linewidth=2)
    ax2.plot(http1_requests, http2_latency, 'g-o', label='HTTP/2', linewidth=2)
    ax2.set_xlabel('Request Number')
    ax2.set_ylabel('Latency (ms)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Header size comparison
    ax3.set_title('Header Compression Efficiency')
    
    requests = list(range(1, 11))
    http1_header_size = [800] * 10  # No compression
    http2_header_size = [800, 400, 300, 250, 200, 180, 160, 150, 140, 130]  # HPACK compression improves
    
    ax3.plot(requests, http1_header_size, 'r-o', label='HTTP/1.1 (no compression)', linewidth=2)
    ax3.plot(requests, http2_header_size, 'g-o', label='HTTP/2 (HPACK)', linewidth=2)
    ax3.set_xlabel('Request Number')
    ax3.set_ylabel('Header Size (bytes)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Page load time comparison
    ax4.set_title('Page Load Time (100 resources)')
    
    scenarios = ['Slow 3G', 'Fast 3G', 'WiFi', 'Broadband']
    http1_times = [8.5, 4.2, 2.1, 1.5]
    http2_times = [5.8, 2.8, 1.4, 1.0]
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    ax4.bar(x - width/2, http1_times, width, label='HTTP/1.1', color='red', alpha=0.7)
    ax4.bar(x + width/2, http2_times, width, label='HTTP/2', color='green', alpha=0.7)
    
    ax4.set_xlabel('Network Condition')
    ax4.set_ylabel('Load Time (seconds)')
    ax4.set_xticks(x)
    ax4.set_xticklabels(scenarios)
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add improvement percentages
    for i, (h1, h2) in enumerate(zip(http1_times, http2_times)):
        improvement = ((h1 - h2) / h1) * 100
        ax4.text(i, max(h1, h2) + 0.2, f'-{improvement:.0f}%', 
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('http2_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Generating HTTP/2 protocol diagrams...")
    
    # Generate all diagrams
    create_http2_multiplexing_diagram()
    print("✓ HTTP/2 multiplexing diagram created")
    
    create_http2_binary_framing_diagram()
    print("✓ HTTP/2 binary framing diagram created")
    
    create_http2_server_push_diagram()
    print("✓ HTTP/2 server push diagram created")
    
    create_http2_hpack_compression_diagram()
    print("✓ HTTP/2 HPACK compression diagram created")
    
    create_http2_performance_comparison()
    print("✓ HTTP/2 performance comparison diagram created")
    
    print("\nAll HTTP/2 diagrams generated successfully!")
    print("Files created:")
    print("  - http2_multiplexing.png")
    print("  - http2_binary_framing.png") 
    print("  - http2_server_push.png")
    print("  - http2_hpack_compression.png")
    print("  - http2_performance_comparison.png")
