#!/usr/bin/env python3
"""
WebSocket Protocol Diagram Renderer
Generates visual diagrams for WebSocket concepts using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Arrow
import numpy as np

def create_websocket_handshake_diagram():
    """Create WebSocket handshake sequence diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('WebSocket Handshake Process', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # Client and Server
    client_box = FancyBboxPatch((1, 10), 3, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax.add_patch(client_box)
    ax.text(2.5, 10.75, 'Web Client\n(Browser)', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((10, 10), 3, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax.add_patch(server_box)
    ax.text(11.5, 10.75, 'WebSocket\nServer', ha='center', va='center', fontweight='bold')
    
    # Timeline
    ax.plot([2.5, 2.5], [1, 9.5], 'k-', linewidth=2)
    ax.plot([11.5, 11.5], [1, 9.5], 'k-', linewidth=2)
    
    # Handshake steps
    steps = [
        {
            'y': 8.5,
            'direction': 'right',
            'label': '1. HTTP Upgrade Request',
            'details': 'GET /chat HTTP/1.1\nUpgrade: websocket\nConnection: Upgrade\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\nSec-WebSocket-Version: 13',
            'color': 'lightblue'
        },
        {
            'y': 6.5,
            'direction': 'left',
            'label': '2. HTTP 101 Response',
            'details': 'HTTP/1.1 101 Switching Protocols\nUpgrade: websocket\nConnection: Upgrade\nSec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=',
            'color': 'lightgreen'
        },
        {
            'y': 4.5,
            'direction': 'both',
            'label': '3. WebSocket Connection Established',
            'details': 'Protocol switched from HTTP to WebSocket\nFull-duplex communication enabled',
            'color': 'lightyellow'
        },
        {
            'y': 2.5,
            'direction': 'both',
            'label': '4. WebSocket Frames Exchange',
            'details': 'Text frames, Binary frames\nPing/Pong for keepalive\nClose frames for termination',
            'color': 'lightcoral'
        }
    ]
    
    for step in steps:
        y = step['y']
        
        if step['direction'] == 'right':
            # Client to Server
            ax.arrow(2.5, y, 8.5, 0, head_width=0.15, head_length=0.3,
                    fc='blue', ec='blue', alpha=0.7)
            ax.text(7, y + 0.7, step['label'], ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=step['color']),
                   fontweight='bold')
            ax.text(7, y - 0.5, step['details'], ha='center', va='center',
                   fontsize=9, style='italic')
            
        elif step['direction'] == 'left':
            # Server to Client
            ax.arrow(11.5, y, -8.5, 0, head_width=0.15, head_length=0.3,
                    fc='green', ec='green', alpha=0.7)
            ax.text(7, y + 0.7, step['label'], ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=step['color']),
                   fontweight='bold')
            ax.text(7, y - 0.5, step['details'], ha='center', va='center',
                   fontsize=9, style='italic')
            
        else:  # both directions
            # Bidirectional
            ax.arrow(2.5, y + 0.1, 8.5, 0, head_width=0.1, head_length=0.2,
                    fc='orange', ec='orange', alpha=0.7)
            ax.arrow(11.5, y - 0.1, -8.5, 0, head_width=0.1, head_length=0.2,
                    fc='orange', ec='orange', alpha=0.7)
            ax.text(7, y + 0.7, step['label'], ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=step['color']),
                   fontweight='bold')
            ax.text(7, y - 0.5, step['details'], ha='center', va='center',
                   fontsize=9, style='italic')
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('websocket_handshake.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_websocket_frame_structure():
    """Create WebSocket frame structure diagram"""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_title('WebSocket Frame Structure', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    
    # Frame structure
    frame_y = 7
    frame_components = [
        {'name': 'FIN\n(1 bit)', 'width': 1, 'color': 'lightblue'},
        {'name': 'RSV\n(3 bits)', 'width': 1, 'color': 'lightgray'},
        {'name': 'Opcode\n(4 bits)', 'width': 1.5, 'color': 'lightgreen'},
        {'name': 'MASK\n(1 bit)', 'width': 1, 'color': 'lightyellow'},
        {'name': 'Payload Len\n(7 bits)', 'width': 1.5, 'color': 'lightcoral'},
        {'name': 'Extended Payload Length\n(16 or 64 bits)', 'width': 3, 'color': 'lightpink'},
        {'name': 'Masking Key\n(32 bits)', 'width': 2, 'color': 'lightcyan'},
        {'name': 'Payload Data\n(variable)', 'width': 3, 'color': 'lavender'}
    ]
    
    x_start = 0.5
    for component in frame_components:
        rect = FancyBboxPatch((x_start, frame_y), component['width'], 1,
                             boxstyle="round,pad=0.02",
                             facecolor=component['color'], edgecolor='black')
        ax.add_patch(rect)
        ax.text(x_start + component['width']/2, frame_y + 0.5, component['name'],
               ha='center', va='center', fontsize=9, fontweight='bold')
        x_start += component['width']
    
    # Opcode values
    ax.text(7, 5.5, 'WebSocket Frame Types (Opcode Values)', ha='center', va='center',
           fontsize=14, fontweight='bold')
    
    opcodes = [
        {'code': '0x0', 'name': 'Continuation Frame', 'description': 'Continuation of fragmented message'},
        {'code': '0x1', 'name': 'Text Frame', 'description': 'UTF-8 text data'},
        {'code': '0x2', 'name': 'Binary Frame', 'description': 'Binary data'},
        {'code': '0x8', 'name': 'Close Frame', 'description': 'Connection close'},
        {'code': '0x9', 'name': 'Ping Frame', 'description': 'Ping for keepalive'},
        {'code': '0xA', 'name': 'Pong Frame', 'description': 'Pong response'}
    ]
    
    y_start = 4.5
    for i, opcode in enumerate(opcodes):
        y = y_start - i * 0.6
        
        # Opcode box
        code_box = FancyBboxPatch((1, y), 1, 0.4, boxstyle="round,pad=0.05",
                                 facecolor='lightgreen', edgecolor='black')
        ax.add_patch(code_box)
        ax.text(1.5, y + 0.2, opcode['code'], ha='center', va='center',
               fontweight='bold', fontsize=10)
        
        # Name and description
        ax.text(2.5, y + 0.2, f"{opcode['name']}: {opcode['description']}",
               ha='left', va='center', fontsize=10)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('websocket_frame_structure.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_websocket_vs_http_comparison():
    """Create WebSocket vs HTTP comparison diagram"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
    
    # HTTP Polling (left)
    ax1.set_title('HTTP Polling', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 12)
    
    # Client and Server for HTTP
    client_box = FancyBboxPatch((1, 10), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax1.add_patch(client_box)
    ax1.text(2, 10.5, 'Client', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((7, 10), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax1.add_patch(server_box)
    ax1.text(8, 10.5, 'Server', ha='center', va='center', fontweight='bold')
    
    # HTTP polling requests
    polling_requests = [
        {'y': 9, 'response': 'No new data'},
        {'y': 8, 'response': 'No new data'},
        {'y': 7, 'response': 'New data!'},
        {'y': 6, 'response': 'No new data'},
        {'y': 5, 'response': 'No new data'},
        {'y': 4, 'response': 'New data!'}
    ]
    
    for i, req in enumerate(polling_requests):
        y = req['y']
        
        # Request arrow
        ax1.arrow(3, y + 0.1, 3.5, 0, head_width=0.1, head_length=0.2,
                 fc='blue', ec='blue', alpha=0.7)
        ax1.text(4.75, y + 0.3, f'GET /api/data', ha='center', va='center',
                fontsize=8)
        
        # Response arrow
        color = 'green' if 'New data!' in req['response'] else 'gray'
        ax1.arrow(7, y - 0.1, -3.5, 0, head_width=0.1, head_length=0.2,
                 fc=color, ec=color, alpha=0.7)
        ax1.text(4.75, y - 0.3, req['response'], ha='center', va='center',
                fontsize=8, color=color)
    
    # HTTP overhead
    ax1.text(5, 2.5, 'HTTP Polling Issues:', ha='center', va='center',
            fontweight='bold', fontsize=12)
    issues = [
        '• High server load (constant requests)',
        '• Bandwidth waste (empty responses)',
        '• Latency (polling interval delay)',
        '• Resource inefficiency'
    ]
    
    for i, issue in enumerate(issues):
        ax1.text(5, 2 - i * 0.3, issue, ha='center', va='center', fontsize=10)
    
    # WebSocket (right)
    ax2.set_title('WebSocket Real-Time', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 12)
    
    # Client and Server for WebSocket
    client_box = FancyBboxPatch((1, 10), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax2.add_patch(client_box)
    ax2.text(2, 10.5, 'Client', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((7, 10), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax2.add_patch(server_box)
    ax2.text(8, 10.5, 'Server', ha='center', va='center', fontweight='bold')
    
    # WebSocket connection
    ax2.plot([3, 7], [9.5, 9.5], 'purple', linewidth=3, alpha=0.7)
    ax2.text(5, 9.7, 'Persistent WebSocket Connection', ha='center', va='center',
            fontweight='bold', color='purple')
    
    # Real-time messages
    messages = [
        {'y': 8.5, 'direction': 'right', 'text': 'Initial data request'},
        {'y': 8, 'direction': 'left', 'text': 'Data stream started'},
        {'y': 7.5, 'direction': 'left', 'text': 'New data (instant)'},
        {'y': 7, 'direction': 'right', 'text': 'User action'},
        {'y': 6.5, 'direction': 'left', 'text': 'New data (instant)'},
        {'y': 6, 'direction': 'left', 'text': 'New data (instant)'}
    ]
    
    for msg in messages:
        y = msg['y']
        
        if msg['direction'] == 'right':
            ax2.arrow(3, y, 3.5, 0, head_width=0.1, head_length=0.2,
                     fc='blue', ec='blue', alpha=0.7)
            ax2.text(4.75, y + 0.2, msg['text'], ha='center', va='center',
                    fontsize=8)
        else:
            ax2.arrow(7, y, -3.5, 0, head_width=0.1, head_length=0.2,
                     fc='green', ec='green', alpha=0.7)
            ax2.text(4.75, y + 0.2, msg['text'], ha='center', va='center',
                    fontsize=8, color='green')
    
    # WebSocket benefits
    ax2.text(5, 4.5, 'WebSocket Benefits:', ha='center', va='center',
            fontweight='bold', fontsize=12)
    benefits = [
        '• Real-time data push',
        '• Minimal overhead per message',
        '• Instant updates (no polling delay)',
        '• Efficient resource usage',
        '• Bidirectional communication'
    ]
    
    for i, benefit in enumerate(benefits):
        ax2.text(5, 4 - i * 0.3, benefit, ha='center', va='center', fontsize=10,
                color='green')
    
    for ax in [ax1, ax2]:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('websocket_vs_http_polling.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_websocket_applications_diagram():
    """Create WebSocket applications and use cases diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('WebSocket Applications and Use Cases', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # Central WebSocket node
    center_box = FancyBboxPatch((6, 5.5), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='gold', edgecolor='black', linewidth=2)
    ax.add_patch(center_box)
    ax.text(7, 6, 'WebSocket\nProtocol', ha='center', va='center', 
           fontweight='bold', fontsize=12)
    
    # Application categories
    applications = [
        {
            'name': 'Real-Time\nCommunication',
            'examples': ['Chat Apps', 'Video Calls', 'Voice Chat'],
            'position': (2, 9),
            'color': 'lightblue'
        },
        {
            'name': 'Live Data\nFeeds',
            'examples': ['Stock Prices', 'Sports Scores', 'News Updates'],
            'position': (12, 9),
            'color': 'lightgreen'
        },
        {
            'name': 'Interactive\nGaming',
            'examples': ['Multiplayer Games', 'Real-time Strategy', 'Casual Games'],
            'position': (2, 3),
            'color': 'lightcoral'
        },
        {
            'name': 'Collaborative\nTools',
            'examples': ['Document Editing', 'Whiteboards', 'Code Editors'],
            'position': (12, 3),
            'color': 'lightyellow'
        },
        {
            'name': 'IoT &\nMonitoring',
            'examples': ['Sensor Networks', 'Device Control', 'System Alerts'],
            'position': (7, 1),
            'color': 'lightpink'
        }
    ]
    
    for app in applications:
        x, y = app['position']
        
        # Main category box
        app_box = FancyBboxPatch((x-1, y-0.5), 2, 1, boxstyle="round,pad=0.1",
                                facecolor=app['color'], edgecolor='black')
        ax.add_patch(app_box)
        ax.text(x, y, app['name'], ha='center', va='center', 
               fontweight='bold', fontsize=10)
        
        # Connection to center
        ax.plot([x, 7], [y, 6], 'k--', alpha=0.5, linewidth=1)
        
        # Examples
        for i, example in enumerate(app['examples']):
            ex_y = y - 1.5 - i * 0.3
            example_box = FancyBboxPatch((x-0.8, ex_y-0.1), 1.6, 0.2, 
                                       boxstyle="round,pad=0.02",
                                       facecolor='white', edgecolor=app['color'])
            ax.add_patch(example_box)
            ax.text(x, ex_y, example, ha='center', va='center', fontsize=8)
    
    # Key features
    features_box = FancyBboxPatch((0.5, 10.5), 13, 1, boxstyle="round,pad=0.1",
                                 facecolor='lightcyan', edgecolor='black')
    ax.add_patch(features_box)
    ax.text(7, 11, 'Key WebSocket Features', ha='center', va='center',
           fontweight='bold', fontsize=12)
    
    features = [
        'Full-Duplex Communication',
        'Low Latency',
        'Persistent Connection',
        'Binary & Text Support',
        'Minimal Overhead'
    ]
    
    feature_text = ' • '.join(features)
    ax.text(7, 10.7, feature_text, ha='center', va='center', fontsize=10)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('websocket_applications.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_websocket_performance_chart():
    """Create WebSocket performance comparison chart"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('WebSocket Performance Analysis', fontsize=16, fontweight='bold')
    
    # Latency comparison
    ax1.set_title('Message Latency Comparison')
    protocols = ['HTTP Polling\n(1s interval)', 'HTTP Polling\n(100ms interval)', 'WebSocket\n(Real-time)']
    latencies = [500, 50, 5]  # milliseconds
    colors = ['red', 'orange', 'green']
    
    bars = ax1.bar(protocols, latencies, color=colors, alpha=0.7)
    ax1.set_ylabel('Latency (ms)')
    ax1.set_yscale('log')
    
    # Add value labels
    for bar, latency in zip(bars, latencies):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height * 1.1,
                f'{latency}ms', ha='center', va='bottom', fontweight='bold')
    
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Bandwidth efficiency
    ax2.set_title('Bandwidth Efficiency (100 messages)')
    scenarios = ['HTTP Polling', 'WebSocket']
    overhead_kb = [80, 0.6]  # KB of overhead
    
    bars = ax2.bar(scenarios, overhead_kb, color=['red', 'green'], alpha=0.7)
    ax2.set_ylabel('Protocol Overhead (KB)')
    
    for bar, overhead in zip(bars, overhead_kb):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{overhead} KB', ha='center', va='bottom', fontweight='bold')
    
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Connection overhead
    ax3.set_title('Connection Establishment')
    connection_types = ['HTTP Request', 'WebSocket\nHandshake', 'WebSocket\nReuse']
    setup_times = [3, 1, 0]  # RTTs
    
    bars = ax3.bar(connection_types, setup_times, color=['red', 'orange', 'green'], alpha=0.7)
    ax3.set_ylabel('Setup Time (RTTs)')
    
    for bar, time in zip(bars, setup_times):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{time} RTT', ha='center', va='bottom', fontweight='bold')
    
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Scalability comparison
    ax4.set_title('Server Resource Usage (1000 clients)')
    resources = ['Memory\n(MB)', 'CPU\n(%)', 'Network\n(Mbps)']
    http_usage = [100, 80, 50]
    websocket_usage = [30, 20, 10]
    
    x = np.arange(len(resources))
    width = 0.35
    
    ax4.bar(x - width/2, http_usage, width, label='HTTP Polling', color='red', alpha=0.7)
    ax4.bar(x + width/2, websocket_usage, width, label='WebSocket', color='green', alpha=0.7)
    
    ax4.set_ylabel('Resource Usage')
    ax4.set_xticks(x)
    ax4.set_xticklabels(resources)
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add improvement percentages
    for i, (http, ws) in enumerate(zip(http_usage, websocket_usage)):
        improvement = ((http - ws) / http) * 100
        ax4.text(i, max(http, ws) + 5, f'-{improvement:.0f}%', 
                ha='center', va='bottom', fontweight='bold', color='green')
    
    plt.tight_layout()
    plt.savefig('websocket_performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Generating WebSocket protocol diagrams...")
    
    # Generate all diagrams
    create_websocket_handshake_diagram()
    print("✓ WebSocket handshake diagram created")
    
    create_websocket_frame_structure()
    print("✓ WebSocket frame structure diagram created")
    
    create_websocket_vs_http_comparison()
    print("✓ WebSocket vs HTTP comparison diagram created")
    
    create_websocket_applications_diagram()
    print("✓ WebSocket applications diagram created")
    
    create_websocket_performance_chart()
    print("✓ WebSocket performance analysis chart created")
    
    print("\nAll WebSocket diagrams generated successfully!")
    print("Files created:")
    print("  - websocket_handshake.png")
    print("  - websocket_frame_structure.png")
    print("  - websocket_vs_http_polling.png")
    print("  - websocket_applications.png")
    print("  - websocket_performance_analysis.png")
