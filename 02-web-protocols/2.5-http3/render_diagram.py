#!/usr/bin/env python3
"""
HTTP/3 Protocol Diagram Renderer
Generates visual diagrams for HTTP/3 and QUIC concepts using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle
import numpy as np

def create_http3_vs_http2_comparison():
    """Create HTTP/3 vs HTTP/2 comparison diagram"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
    
    # HTTP/2 diagram (left)
    ax1.set_title('HTTP/2 over TCP + TLS', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 12)
    
    # Protocol stack for HTTP/2
    layers_http2 = [
        {'name': 'HTTP/2', 'y': 10, 'color': 'lightblue'},
        {'name': 'TLS 1.3', 'y': 8.5, 'color': 'lightgreen'},
        {'name': 'TCP', 'y': 7, 'color': 'lightyellow'},
        {'name': 'IP', 'y': 5.5, 'color': 'lightcoral'},
        {'name': 'Ethernet', 'y': 4, 'color': 'lightgray'}
    ]
    
    for layer in layers_http2:
        rect = FancyBboxPatch((1, layer['y']), 8, 1.2, boxstyle="round,pad=0.1",
                             facecolor=layer['color'], edgecolor='black')
        ax1.add_patch(rect)
        ax1.text(5, layer['y'] + 0.6, layer['name'], ha='center', va='center', 
                fontweight='bold', fontsize=12)
    
    # Handshake steps for HTTP/2
    handshake_steps = [
        '1. TCP SYN/ACK (1 RTT)',
        '2. TLS Handshake (1 RTT)', 
        '3. HTTP/2 Settings (1 RTT)',
        'Total: 3 RTT'
    ]
    
    for i, step in enumerate(handshake_steps):
        color = 'red' if 'Total' in step else 'black'
        weight = 'bold' if 'Total' in step else 'normal'
        ax1.text(5, 2.5 - i * 0.4, step, ha='center', va='center', 
                fontsize=10, color=color, fontweight=weight)
    
    # HTTP/3 diagram (right)
    ax2.set_title('HTTP/3 over QUIC', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 12)
    
    # Protocol stack for HTTP/3
    layers_http3 = [
        {'name': 'HTTP/3', 'y': 10, 'color': 'lightblue'},
        {'name': 'QUIC (Transport + Crypto)', 'y': 8, 'color': 'lightgreen'},
        {'name': 'UDP', 'y': 6, 'color': 'lightyellow'},
        {'name': 'IP', 'y': 4.5, 'color': 'lightcoral'},
        {'name': 'Ethernet', 'y': 3, 'color': 'lightgray'}
    ]
    
    for layer in layers_http3:
        height = 1.8 if 'QUIC' in layer['name'] else 1.2
        rect = FancyBboxPatch((1, layer['y']), 8, height, boxstyle="round,pad=0.1",
                             facecolor=layer['color'], edgecolor='black')
        ax2.add_patch(rect)
        ax2.text(5, layer['y'] + height/2, layer['name'], ha='center', va='center', 
                fontweight='bold', fontsize=12)
    
    # Handshake steps for HTTP/3
    handshake_steps_h3 = [
        '1. QUIC Handshake (1 RTT)',
        '   - Transport + Crypto',
        '   - HTTP/3 Settings',
        'Total: 1 RTT (67% faster)'
    ]
    
    for i, step in enumerate(handshake_steps_h3):
        color = 'green' if 'Total' in step else 'black'
        weight = 'bold' if 'Total' in step else 'normal'
        ax2.text(5, 1.8 - i * 0.3, step, ha='center', va='center', 
                fontsize=10, color=color, fontweight=weight)
    
    for ax in [ax1, ax2]:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('http3_vs_http2_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_quic_connection_migration_diagram():
    """Create QUIC connection migration flow diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('QUIC Connection Migration Process', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # Client device
    client_box = FancyBboxPatch((1, 9), 3, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax.add_patch(client_box)
    ax.text(2.5, 9.75, 'Mobile Client', ha='center', va='center', fontweight='bold')
    
    # Server
    server_box = FancyBboxPatch((10, 9), 3, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax.add_patch(server_box)
    ax.text(11.5, 9.75, 'Server', ha='center', va='center', fontweight='bold')
    
    # Network paths
    wifi_box = FancyBboxPatch((1, 6.5), 3, 1, boxstyle="round,pad=0.1",
                             facecolor='lightyellow', edgecolor='blue')
    ax.add_patch(wifi_box)
    ax.text(2.5, 7, 'WiFi Network\n192.168.1.x', ha='center', va='center', fontsize=10)
    
    cellular_box = FancyBboxPatch((1, 4.5), 3, 1, boxstyle="round,pad=0.1",
                                 facecolor='lightpink', edgecolor='red')
    ax.add_patch(cellular_box)
    ax.text(2.5, 5, 'Cellular Network\n10.0.0.x', ha='center', va='center', fontsize=10)
    
    # Migration steps
    steps = [
        {'y': 8, 'text': '1. Active connection on WiFi', 'color': 'blue'},
        {'y': 7.3, 'text': '2. Network change detected', 'color': 'orange'},
        {'y': 6.6, 'text': '3. PATH_CHALLENGE on cellular', 'color': 'red'},
        {'y': 5.9, 'text': '4. PATH_RESPONSE received', 'color': 'red'},
        {'y': 5.2, 'text': '5. Connection migrated', 'color': 'green'},
        {'y': 4.5, 'text': '6. Old path cleaned up', 'color': 'gray'}
    ]
    
    for step in steps:
        ax.text(7, step['y'], step['text'], ha='center', va='center', 
               bbox=dict(boxstyle="round,pad=0.3", facecolor=step['color'], alpha=0.3),
               fontsize=11)
    
    # Connection lines
    # WiFi connection (initial)
    ax.plot([4, 10], [7, 9.75], 'b-', linewidth=3, alpha=0.7, label='WiFi Path')
    
    # Cellular connection (after migration)
    ax.plot([4, 10], [5, 9.75], 'r-', linewidth=3, alpha=0.7, label='Cellular Path')
    
    # Connection ID preservation
    conn_id_box = FancyBboxPatch((5.5, 2.5), 3, 1, boxstyle="round,pad=0.1",
                                facecolor='lightcyan', edgecolor='black')
    ax.add_patch(conn_id_box)
    ax.text(7, 3, 'Connection ID\nPreserved\n(No reconnection)', 
           ha='center', va='center', fontweight='bold', fontsize=10)
    
    # Benefits box
    benefits_box = FancyBboxPatch((1, 1), 12, 1.5, boxstyle="round,pad=0.1",
                                 facecolor='lightgreen', alpha=0.3, edgecolor='black')
    ax.add_patch(benefits_box)
    ax.text(7, 1.75, 'Migration Benefits', ha='center', va='center', 
           fontweight='bold', fontsize=12)
    
    benefits = "• Seamless network transitions  • Zero data loss  • Preserved connection state\n• ~100ms migration time  • No application interruption  • Better mobile experience"
    ax.text(7, 1.25, benefits, ha='center', va='center', fontsize=10)
    
    ax.legend(loc='upper right')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('quic_connection_migration.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_http3_stream_independence_diagram():
    """Create HTTP/3 stream independence diagram"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # HTTP/2 HOL blocking (left)
    ax1.set_title('HTTP/2: Head-of-Line Blocking', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    
    # TCP connection
    tcp_box = FancyBboxPatch((2, 8), 6, 1, boxstyle="round,pad=0.1",
                            facecolor='lightcoral', edgecolor='black')
    ax1.add_patch(tcp_box)
    ax1.text(5, 8.5, 'Single TCP Connection', ha='center', va='center', fontweight='bold')
    
    # HTTP/2 streams affected by packet loss
    streams_h2 = [
        {'name': 'Stream 1 (HTML)', 'y': 6.5, 'blocked': False},
        {'name': 'Stream 3 (CSS)', 'y': 5.5, 'blocked': True},  # Packet lost
        {'name': 'Stream 5 (JS)', 'y': 4.5, 'blocked': True},   # Blocked
        {'name': 'Stream 7 (IMG)', 'y': 3.5, 'blocked': True}   # Blocked
    ]
    
    for stream in streams_h2:
        color = 'lightgreen' if not stream['blocked'] else 'mistyrose'
        border_color = 'green' if not stream['blocked'] else 'red'
        
        stream_box = FancyBboxPatch((1, stream['y']), 8, 0.8, boxstyle="round,pad=0.05",
                                   facecolor=color, edgecolor=border_color)
        ax1.add_patch(stream_box)
        
        status = '✓ Delivered' if not stream['blocked'] else '❌ Blocked'
        ax1.text(5, stream['y'] + 0.4, f"{stream['name']}: {status}", 
                ha='center', va='center', fontsize=10)
    
    # Packet loss indicator
    ax1.text(5, 2.5, '📦❌ Packet Loss in Stream 3', ha='center', va='center', 
            fontsize=12, color='red', fontweight='bold')
    ax1.text(5, 2, 'All subsequent streams blocked!', ha='center', va='center', 
            fontsize=11, color='red')
    
    # HTTP/3 independent streams (right)
    ax2.set_title('HTTP/3: Independent Streams', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    
    # QUIC connection
    quic_box = FancyBboxPatch((2, 8), 6, 1, boxstyle="round,pad=0.1",
                             facecolor='lightgreen', edgecolor='black')
    ax2.add_patch(quic_box)
    ax2.text(5, 8.5, 'QUIC Connection', ha='center', va='center', fontweight='bold')
    
    # HTTP/3 streams with independent recovery
    streams_h3 = [
        {'name': 'Stream 0 (HTML)', 'y': 6.5, 'affected': False},
        {'name': 'Stream 4 (CSS)', 'y': 5.5, 'affected': True},   # Packet lost
        {'name': 'Stream 8 (JS)', 'y': 4.5, 'affected': False},   # Not blocked
        {'name': 'Stream 12 (IMG)', 'y': 3.5, 'affected': False}  # Not blocked
    ]
    
    for stream in streams_h3:
        if stream['affected']:
            color = 'lightyellow'
            border_color = 'orange'
            status = '⚠️ Recovering'
        else:
            color = 'lightgreen'
            border_color = 'green'
            status = '✓ Delivered'
        
        stream_box = FancyBboxPatch((1, stream['y']), 8, 0.8, boxstyle="round,pad=0.05",
                                   facecolor=color, edgecolor=border_color)
        ax2.add_patch(stream_box)
        
        ax2.text(5, stream['y'] + 0.4, f"{stream['name']}: {status}", 
                ha='center', va='center', fontsize=10)
    
    # Packet loss indicator
    ax2.text(5, 2.5, '📦❌ Packet Loss in Stream 4', ha='center', va='center', 
            fontsize=12, color='orange', fontweight='bold')
    ax2.text(5, 2, 'Other streams continue normally!', ha='center', va='center', 
            fontsize=11, color='green')
    
    for ax in [ax1, ax2]:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('http3_stream_independence.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_http3_handshake_timeline():
    """Create HTTP/3 handshake timeline comparison"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('HTTP/3 vs HTTP/2 Handshake Timeline', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # Timeline for HTTP/2
    ax.text(2, 11, 'HTTP/2 over TCP + TLS', fontweight='bold', fontsize=14)
    
    # HTTP/2 timeline steps
    http2_steps = [
        {'time': 0, 'event': 'TCP SYN', 'color': 'lightblue'},
        {'time': 1, 'event': 'TCP SYN-ACK', 'color': 'lightblue'},
        {'time': 2, 'event': 'TCP ACK', 'color': 'lightblue'},
        {'time': 3, 'event': 'TLS ClientHello', 'color': 'lightgreen'},
        {'time': 4, 'event': 'TLS ServerHello + Cert', 'color': 'lightgreen'},
        {'time': 5, 'event': 'TLS Finished', 'color': 'lightgreen'},
        {'time': 6, 'event': 'HTTP/2 Settings', 'color': 'lightyellow'},
        {'time': 7, 'event': 'Application Data', 'color': 'lightcoral'}
    ]
    
    y_http2 = 9.5
    for step in http2_steps:
        x = step['time'] * 1.5 + 1
        
        # Draw step box
        step_box = FancyBboxPatch((x, y_http2), 1.2, 0.6, boxstyle="round,pad=0.05",
                                 facecolor=step['color'], edgecolor='black')
        ax.add_patch(step_box)
        ax.text(x + 0.6, y_http2 + 0.3, step['event'], ha='center', va='center', 
               fontsize=8, rotation=45)
        
        # Draw timeline arrow
        if step['time'] < 7:
            ax.arrow(x + 1.2, y_http2 + 0.3, 0.25, 0, head_width=0.1, head_length=0.05, 
                    fc='black', ec='black')
    
    # RTT markers for HTTP/2
    rtt_positions = [2.5, 5.5, 8.5]
    for i, pos in enumerate(rtt_positions):
        ax.text(pos, y_http2 - 0.8, f'RTT {i+1}', ha='center', va='center', 
               fontweight='bold', color='red')
        ax.plot([pos-0.5, pos+0.5], [y_http2 - 0.6, y_http2 - 0.6], 'r-', linewidth=2)
    
    # Timeline for HTTP/3
    ax.text(2, 7, 'HTTP/3 over QUIC', fontweight='bold', fontsize=14)
    
    # HTTP/3 timeline steps
    http3_steps = [
        {'time': 0, 'event': 'QUIC Initial\n+ ClientHello', 'color': 'lightgreen'},
        {'time': 1, 'event': 'QUIC Handshake\n+ ServerHello', 'color': 'lightgreen'},
        {'time': 2, 'event': 'QUIC 1-RTT\n+ HTTP/3 Data', 'color': 'lightcoral'}
    ]
    
    y_http3 = 5.5
    for step in http3_steps:
        x = step['time'] * 3 + 1
        
        # Draw step box
        step_box = FancyBboxPatch((x, y_http3), 2.5, 0.8, boxstyle="round,pad=0.05",
                                 facecolor=step['color'], edgecolor='black')
        ax.add_patch(step_box)
        ax.text(x + 1.25, y_http3 + 0.4, step['event'], ha='center', va='center', 
               fontsize=9)
        
        # Draw timeline arrow
        if step['time'] < 2:
            ax.arrow(x + 2.5, y_http3 + 0.4, 0.4, 0, head_width=0.1, head_length=0.1, 
                    fc='black', ec='black')
    
    # RTT marker for HTTP/3
    ax.text(2.5, y_http3 - 0.8, 'RTT 1', ha='center', va='center', 
           fontweight='bold', color='green')
    ax.plot([1, 4], [y_http3 - 0.6, y_http3 - 0.6], 'g-', linewidth=2)
    
    # 0-RTT scenario
    ax.text(2, 3.5, 'HTTP/3 with 0-RTT (Session Resumption)', fontweight='bold', fontsize=14)
    
    y_0rtt = 2
    # 0-RTT step
    step_box = FancyBboxPatch((1, y_0rtt), 4, 0.8, boxstyle="round,pad=0.05",
                             facecolor='gold', edgecolor='black')
    ax.add_patch(step_box)
    ax.text(3, y_0rtt + 0.4, 'QUIC Initial + 0-RTT Data\n(Immediate application data)', 
           ha='center', va='center', fontsize=10, fontweight='bold')
    
    ax.text(3, y_0rtt - 0.8, '0 RTT', ha='center', va='center', 
           fontweight='bold', color='gold', fontsize=12)
    
    # Performance comparison
    perf_box = FancyBboxPatch((8, 1), 5, 3, boxstyle="round,pad=0.1",
                             facecolor='lightcyan', edgecolor='black')
    ax.add_patch(perf_box)
    ax.text(10.5, 3.5, 'Performance Comparison', ha='center', va='center', 
           fontweight='bold', fontsize=12)
    
    comparison_text = """HTTP/2: 3 RTT to first data
HTTP/3: 1 RTT to first data
HTTP/3 0-RTT: 0 RTT to first data

Improvement:
• 67% faster than HTTP/2
• 100% faster with 0-RTT"""
    
    ax.text(10.5, 2.2, comparison_text, ha='center', va='center', fontsize=10)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('http3_handshake_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_http3_performance_benefits():
    """Create HTTP/3 performance benefits chart"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('HTTP/3 Performance Benefits', fontsize=16, fontweight='bold')
    
    # Connection establishment time
    ax1.set_title('Connection Establishment Time')
    protocols = ['HTTP/1.1', 'HTTP/2', 'HTTP/3\n1-RTT', 'HTTP/3\n0-RTT']
    times = [3.0, 2.0, 1.0, 0.1]
    colors = ['red', 'orange', 'lightgreen', 'green']
    
    bars = ax1.bar(protocols, times, color=colors, alpha=0.7)
    ax1.set_ylabel('Time (RTT)')
    ax1.set_ylim(0, 3.5)
    
    # Add value labels on bars
    for bar, time in zip(bars, times):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{time}', ha='center', va='bottom', fontweight='bold')
    
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Head-of-line blocking impact
    ax2.set_title('Head-of-Line Blocking Impact')
    scenarios = ['No Packet Loss', '1% Loss', '2% Loss', '5% Loss']
    http2_impact = [1.0, 2.5, 4.0, 8.0]
    http3_impact = [1.0, 1.1, 1.2, 1.5]
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    ax2.bar(x - width/2, http2_impact, width, label='HTTP/2', color='red', alpha=0.7)
    ax2.bar(x + width/2, http3_impact, width, label='HTTP/3', color='green', alpha=0.7)
    
    ax2.set_xlabel('Packet Loss Rate')
    ax2.set_ylabel('Relative Load Time')
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Mobile network performance
    ax3.set_title('Mobile Network Performance')
    networks = ['WiFi', 'Fast 4G', 'Slow 4G', '3G']
    http2_mobile = [1.2, 2.8, 5.5, 12.0]
    http3_mobile = [1.0, 1.8, 3.2, 7.5]
    
    x = np.arange(len(networks))
    
    ax3.bar(x - width/2, http2_mobile, width, label='HTTP/2', color='red', alpha=0.7)
    ax3.bar(x + width/2, http3_mobile, width, label='HTTP/3', color='green', alpha=0.7)
    
    ax3.set_xlabel('Network Type')
    ax3.set_ylabel('Page Load Time (seconds)')
    ax3.set_xticks(x)
    ax3.set_xticklabels(networks)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Connection migration benefits
    ax4.set_title('Connection Migration Benefits')
    migration_scenarios = ['Video Call', 'File Upload', 'Web Browsing', 'Gaming']
    tcp_downtime = [8.0, 6.0, 4.0, 2.0]
    quic_downtime = [0.1, 0.2, 0.1, 0.05]
    
    x = np.arange(len(migration_scenarios))
    
    bars1 = ax4.bar(x - width/2, tcp_downtime, width, label='TCP (HTTP/2)', color='red', alpha=0.7)
    bars2 = ax4.bar(x + width/2, quic_downtime, width, label='QUIC (HTTP/3)', color='green', alpha=0.7)
    
    ax4.set_xlabel('Use Case')
    ax4.set_ylabel('Downtime per Migration (seconds)')
    ax4.set_xticks(x)
    ax4.set_xticklabels(migration_scenarios, rotation=45)
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add improvement percentages
    for i, (tcp, quic) in enumerate(zip(tcp_downtime, quic_downtime)):
        improvement = ((tcp - quic) / tcp) * 100
        ax4.text(i, max(tcp, quic) + 0.5, f'-{improvement:.0f}%', 
                ha='center', va='bottom', fontweight='bold', color='green')
    
    plt.tight_layout()
    plt.savefig('http3_performance_benefits.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Generating HTTP/3 protocol diagrams...")
    
    # Generate all diagrams
    create_http3_vs_http2_comparison()
    print("✓ HTTP/3 vs HTTP/2 comparison diagram created")
    
    create_quic_connection_migration_diagram()
    print("✓ QUIC connection migration diagram created")
    
    create_http3_stream_independence_diagram()
    print("✓ HTTP/3 stream independence diagram created")
    
    create_http3_handshake_timeline()
    print("✓ HTTP/3 handshake timeline diagram created")
    
    create_http3_performance_benefits()
    print("✓ HTTP/3 performance benefits diagram created")
    
    print("\nAll HTTP/3 diagrams generated successfully!")
    print("Files created:")
    print("  - http3_vs_http2_comparison.png")
    print("  - quic_connection_migration.png")
    print("  - http3_stream_independence.png")
    print("  - http3_handshake_timeline.png")
    print("  - http3_performance_benefits.png")
