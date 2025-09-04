#!/usr/bin/env python3
"""
GraphQL Protocol Diagram Renderer
Generates visual diagrams for GraphQL concepts using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Arrow
import numpy as np

def create_graphql_architecture_diagram():
    """Create GraphQL architecture overview diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title('GraphQL Architecture Overview', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    
    # Client and Server
    client_box = FancyBboxPatch((1, 9), 3, 2, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax.add_patch(client_box)
    ax.text(2.5, 10, 'GraphQL Client\n(Web/Mobile)', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((10, 9), 3, 2, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax.add_patch(server_box)
    ax.text(11.5, 10, 'GraphQL Server\n(Single Endpoint)', ha='center', va='center', fontweight='bold')
    
    # HTTP Connection
    ax.arrow(4, 10, 5.5, 0, head_width=0.2, head_length=0.3,
             fc='purple', ec='purple', linewidth=3)
    ax.text(7, 10.5, 'HTTP POST/GET', ha='center', va='center',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='purple', alpha=0.7),
           fontweight='bold', color='white')
    
    # Schema Layer
    schema_box = FancyBboxPatch((4.5, 7), 5, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightyellow', edgecolor='black')
    ax.add_patch(schema_box)
    ax.text(7, 7.75, 'GraphQL Schema\n(Type System)', ha='center', va='center', fontweight='bold')
    
    # Operation Types
    operations = [
        {'name': 'Query\n(Read)', 'pos': (2, 5), 'color': 'lightblue'},
        {'name': 'Mutation\n(Write)', 'pos': (7, 5), 'color': 'lightcoral'},
        {'name': 'Subscription\n(Real-time)', 'pos': (12, 5), 'color': 'lightgreen'}
    ]
    
    for op in operations:
        box = FancyBboxPatch((op['pos'][0]-1, op['pos'][1]-0.5), 2, 1, boxstyle="round,pad=0.1",
                            facecolor=op['color'], edgecolor='black')
        ax.add_patch(box)
        ax.text(op['pos'][0], op['pos'][1], op['name'], ha='center', va='center', fontweight='bold')
    
    # Benefits
    benefits_box = FancyBboxPatch((0.5, 2), 13, 1, boxstyle="round,pad=0.1",
                                 facecolor='lightcyan', edgecolor='black')
    ax.add_patch(benefits_box)
    ax.text(7, 2.5, 'Key Benefits: Single Endpoint • Flexible Queries • Strong Typing • Real-time Updates',
           ha='center', va='center', fontsize=11)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('graphql_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_graphql_vs_rest_diagram():
    """Create GraphQL vs REST comparison diagram"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
    fig.suptitle('GraphQL vs REST API Comparison', fontsize=16, fontweight='bold')
    
    # REST API (left)
    ax1.set_title('REST API Approach', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 12)
    
    # Client
    client_box = FancyBboxPatch((1, 10), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax1.add_patch(client_box)
    ax1.text(2, 10.5, 'Client', ha='center', va='center', fontweight='bold')
    
    # Multiple REST endpoints
    endpoints = ['/users/1', '/users/1/orders', '/products/123', '/reviews/123']
    
    for i, endpoint in enumerate(endpoints):
        y = 8.5 - i * 0.8
        ep_box = FancyBboxPatch((6, y-0.3), 3, 0.6, boxstyle="round,pad=0.05",
                               facecolor='lightcoral', edgecolor='black')
        ax1.add_patch(ep_box)
        ax1.text(7.5, y, endpoint, ha='center', va='center', fontsize=10)
        
        # Request arrow
        ax1.arrow(3, 10.3, 2.5, y - 10.3, head_width=0.1, head_length=0.15, 
                 fc='red', ec='red', alpha=0.7)
    
    # Issues
    ax1.text(5, 3, 'REST Issues:\n• Multiple requests\n• Over-fetching\n• Endpoint proliferation',
            ha='center', va='center', fontweight='bold', color='red')
    
    # GraphQL API (right)
    ax2.set_title('GraphQL API Approach', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 12)
    
    # Client
    client_box = FancyBboxPatch((1, 10), 2, 1, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax2.add_patch(client_box)
    ax2.text(2, 10.5, 'Client', ha='center', va='center', fontweight='bold')
    
    # Single GraphQL endpoint
    graphql_box = FancyBboxPatch((6, 7), 3, 2, boxstyle="round,pad=0.1",
                                facecolor='lightgreen', edgecolor='black')
    ax2.add_patch(graphql_box)
    ax2.text(7.5, 8, '/graphql\n(Single Endpoint)', ha='center', va='center', fontweight='bold')
    
    # Single request
    ax2.arrow(3, 10.3, 2.5, -2, head_width=0.15, head_length=0.2,
             fc='green', ec='green', linewidth=3)
    ax2.text(4.5, 9, 'Single Query', ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.2", facecolor='green', alpha=0.7),
            fontweight='bold', color='white')
    
    # Benefits
    ax2.text(5, 3, 'GraphQL Benefits:\n• Single request\n• Exact data needed\n• Schema evolution',
            ha='center', va='center', fontweight='bold', color='green')
    
    for ax in [ax1, ax2]:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('graphql_vs_rest.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_graphql_performance_chart():
    """Create GraphQL performance comparison chart"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('GraphQL Performance Analysis', fontsize=16, fontweight='bold')
    
    # Data Transfer Comparison
    ax1.set_title('Data Transfer Efficiency')
    scenarios = ['Mobile App', 'User Profile', 'Dashboard']
    rest_data = [45, 78, 120]  # KB
    graphql_data = [12, 23, 35]  # KB
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, rest_data, width, label='REST API', color='red', alpha=0.7)
    bars2 = ax1.bar(x + width/2, graphql_data, width, label='GraphQL', color='green', alpha=0.7)
    
    ax1.set_ylabel('Data Transfer (KB)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Request Count Comparison
    ax2.set_title('Number of Requests')
    rest_requests = [3, 5, 8]
    graphql_requests = [1, 1, 1]
    
    bars1 = ax2.bar(x - width/2, rest_requests, width, label='REST API', color='red', alpha=0.7)
    bars2 = ax2.bar(x + width/2, graphql_requests, width, label='GraphQL', color='green', alpha=0.7)
    
    ax2.set_ylabel('Number of Requests')
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Query Performance
    ax3.set_title('Query Performance')
    metrics = ['Parse', 'Validate', 'Execute', 'Serialize']
    times = [2, 1, 8, 3]  # milliseconds
    
    bars = ax3.bar(metrics, times, color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow'])
    ax3.set_ylabel('Time (ms)')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Subscription Performance
    ax4.set_title('Subscription Performance')
    sub_metrics = ['Setup (ms)', 'Latency (ms)', 'Throughput', 'Memory (MB)']
    values = [45, 12, 850, 25]
    
    bars = ax4.bar(sub_metrics, values, color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow'])
    ax4.set_ylabel('Performance Value')
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('graphql_performance_chart.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_graphql_subscriptions_diagram():
    """Create GraphQL subscriptions diagram"""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_title('GraphQL Subscriptions - Real-Time Updates', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    
    # Client and Server
    client_box = FancyBboxPatch((1, 7), 3, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightblue', edgecolor='black')
    ax.add_patch(client_box)
    ax.text(2.5, 7.75, 'GraphQL Client', ha='center', va='center', fontweight='bold')
    
    server_box = FancyBboxPatch((10, 7), 3, 1.5, boxstyle="round,pad=0.1",
                               facecolor='lightgreen', edgecolor='black')
    ax.add_patch(server_box)
    ax.text(11.5, 7.75, 'GraphQL Server', ha='center', va='center', fontweight='bold')
    
    # WebSocket Connection
    ax.plot([4, 10], [8, 8], 'purple', linewidth=4, alpha=0.8)
    ax.text(7, 8.3, 'WebSocket Connection', ha='center', va='center',
           bbox=dict(boxstyle="round,pad=0.2", facecolor='purple', alpha=0.7),
           fontweight='bold', color='white')
    
    # Subscription flow
    flow_steps = [
        {'step': '1. Subscribe', 'y': 6, 'direction': 'right'},
        {'step': '2. Event → Push', 'y': 5, 'direction': 'left'},
        {'step': '3. Event → Push', 'y': 4, 'direction': 'left'},
        {'step': '4. Unsubscribe', 'y': 3, 'direction': 'right'}
    ]
    
    for step in flow_steps:
        y = step['y']
        if step['direction'] == 'right':
            ax.arrow(4, y, 5.5, 0, head_width=0.1, head_length=0.2,
                    fc='blue', ec='blue', alpha=0.7)
        else:
            ax.arrow(10, y, -5.5, 0, head_width=0.1, head_length=0.2,
                    fc='green', ec='green', alpha=0.7)
        ax.text(7, y + 0.2, step['step'], ha='center', va='center', fontsize=10)
    
    # Examples
    ax.text(7, 1.5, 'Real-time Examples: Product prices • Order status • Chat messages • Live inventory',
           ha='center', va='center', fontsize=12,
           bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow'))
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('graphql_subscriptions.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Generating GraphQL protocol diagrams...")
    
    create_graphql_architecture_diagram()
    print("✓ GraphQL architecture diagram created")
    
    create_graphql_vs_rest_diagram()
    print("✓ GraphQL vs REST comparison diagram created")
    
    create_graphql_performance_chart()
    print("✓ GraphQL performance chart created")
    
    create_graphql_subscriptions_diagram()
    print("✓ GraphQL subscriptions diagram created")
    
    print("\nAll GraphQL diagrams generated successfully!")
    print("Files created:")
    print("  - graphql_architecture.png")
    print("  - graphql_vs_rest.png")
    print("  - graphql_performance_chart.png")
    print("  - graphql_subscriptions.png")
