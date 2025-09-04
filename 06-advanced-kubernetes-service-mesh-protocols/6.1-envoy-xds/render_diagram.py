#!/usr/bin/env python3
"""
Envoy xDS Architecture Diagram Renderer
Generates visual diagrams for service mesh control and data plane interactions
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle, Arrow
import numpy as np

def render_xds_architecture():
    """Render Envoy xDS service mesh architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Colors
    control_plane_color = '#E3F2FD'
    data_plane_color = '#E8F5E8'
    k8s_color = '#FFF3E0'
    xds_color = '#F3E5F5'
    traffic_color = '#FFEBEE'
    
    # Title
    ax.text(8, 11.5, 'Envoy xDS Service Mesh Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Control Plane
    control_plane_box = FancyBboxPatch((1, 8.5), 6, 2.5, 
                                      boxstyle="round,pad=0.1", 
                                      facecolor=control_plane_color, 
                                      edgecolor='black', linewidth=2)
    ax.add_patch(control_plane_box)
    ax.text(4, 10.5, 'Istio Control Plane', fontsize=14, fontweight='bold', ha='center')
    
    # Control plane components
    components = [
        ('Pilot\n(xDS Server)', 2, 9.5),
        ('Galley\n(Config)', 4, 9.5),
        ('Citadel\n(Security)', 6, 9.5)
    ]
    
    for name, x, y in components:
        comp_box = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor='white', 
                                 edgecolor='blue', linewidth=1)
        ax.add_patch(comp_box)
        ax.text(x, y, name, fontsize=10, ha='center', fontweight='bold')
    
    # Kubernetes API
    k8s_box = FancyBboxPatch((9, 8.5), 6, 2.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor=k8s_color, 
                            edgecolor='black', linewidth=2)
    ax.add_patch(k8s_box)
    ax.text(12, 10.5, 'Kubernetes API Server', fontsize=14, fontweight='bold', ha='center')
    
    # Kubernetes resources
    k8s_resources = [
        ('VirtualService', 10, 9.5),
        ('DestinationRule', 12, 9.5),
        ('ServiceEntry', 14, 9.5)
    ]
    
    for name, x, y in k8s_resources:
        resource_box = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8, 
                                     boxstyle="round,pad=0.05", 
                                     facecolor='white', 
                                     edgecolor='orange', linewidth=1)
        ax.add_patch(resource_box)
        ax.text(x, y, name, fontsize=9, ha='center', fontweight='bold')
    
    # xDS APIs
    xds_box = FancyBboxPatch((1, 6), 14, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor=xds_color, 
                            edgecolor='black', linewidth=2)
    ax.add_patch(xds_box)
    ax.text(8, 7.2, 'xDS Discovery APIs (gRPC Streaming)', fontsize=14, fontweight='bold', ha='center')
    
    # xDS services
    xds_services = [
        ('LDS\nListener', 2.5, 6.5),
        ('RDS\nRoute', 5, 6.5),
        ('CDS\nCluster', 7.5, 6.5),
        ('EDS\nEndpoint', 10, 6.5),
        ('SDS\nSecret', 12.5, 6.5)
    ]
    
    for name, x, y in xds_services:
        xds_service_box = FancyBboxPatch((x-0.6, y-0.3), 1.2, 0.6, 
                                        boxstyle="round,pad=0.05", 
                                        facecolor='white', 
                                        edgecolor='purple', linewidth=1)
        ax.add_patch(xds_service_box)
        ax.text(x, y, name, fontsize=9, ha='center', fontweight='bold')
    
    # Data Plane - Service Pods
    pods = [
        ('Pod A\nWeb Service', 2, 3.5),
        ('Pod B\nAPI Service', 6, 3.5),
        ('Pod C\nDB Service', 10, 3.5),
        ('Pod D\nAuth Service', 14, 3.5)
    ]
    
    for name, x, y in pods:
        # Pod container
        pod_box = FancyBboxPatch((x-1.2, y-1), 2.4, 2, 
                                boxstyle="round,pad=0.1", 
                                facecolor=data_plane_color, 
                                edgecolor='black', linewidth=1)
        ax.add_patch(pod_box)
        
        # Envoy sidecar
        envoy_box = FancyBboxPatch((x-1, y-0.3), 2, 0.6, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor='lightblue', 
                                  edgecolor='blue', linewidth=1)
        ax.add_patch(envoy_box)
        ax.text(x, y, 'Envoy Proxy', fontsize=9, ha='center', fontweight='bold')
        
        # Application
        app_box = FancyBboxPatch((x-1, y-0.8), 2, 0.4, 
                                boxstyle="round,pad=0.05", 
                                facecolor='lightgreen', 
                                edgecolor='green', linewidth=1)
        ax.add_patch(app_box)
        ax.text(x, y-0.6, name.split('\n')[1], fontsize=9, ha='center', fontweight='bold')
        
        ax.text(x, y+1.2, name.split('\n')[0], fontsize=10, ha='center', fontweight='bold')
    
    # Traffic flow between services
    traffic_flows = [
        (2, 3.5, 6, 3.5, 'HTTP/gRPC'),
        (6, 3.5, 10, 3.5, 'HTTP/gRPC'),
        (10, 3.5, 14, 3.5, 'HTTP/gRPC')
    ]
    
    for x1, y1, x2, y2, label in traffic_flows:
        # Traffic arrow
        ax.annotate('', xy=(x2-1.2, y1), xytext=(x1+1.2, y1),
                   arrowprops=dict(arrowstyle='->', color='red', lw=2))
        
        # Label
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, y1+0.3, label, fontsize=8, ha='center', 
               bbox=dict(boxstyle="round,pad=0.2", facecolor=traffic_color, alpha=0.7))
    
    # Control plane to xDS arrows
    ax.arrow(4, 8.5, 0, -1, head_width=0.2, head_length=0.1, fc='blue', ec='blue')
    
    # Kubernetes to control plane arrow
    ax.arrow(9, 9.75, -1.8, 0, head_width=0.15, head_length=0.2, fc='orange', ec='orange')
    
    # xDS to data plane arrows
    for _, x, _ in pods:
        ax.arrow(x, 6, 0, -1.3, head_width=0.15, head_length=0.1, fc='purple', ec='purple', alpha=0.7)
    
    # Legend
    legend_elements = [
        ('Control Plane', control_plane_color),
        ('Data Plane', data_plane_color),
        ('Kubernetes API', k8s_color),
        ('xDS APIs', xds_color),
        ('Service Traffic', traffic_color)
    ]
    
    for i, (label, color) in enumerate(legend_elements):
        legend_box = FancyBboxPatch((0.5, 1.5 - i*0.3), 0.3, 0.2, 
                                   boxstyle="round,pad=0.02", 
                                   facecolor=color, 
                                   edgecolor='black', linewidth=0.5)
        ax.add_patch(legend_box)
        ax.text(1, 1.6 - i*0.3, label, fontsize=9, va='center')
    
    plt.tight_layout()
    plt.savefig('xds_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated xds_architecture.png")

def render_xds_protocol_flow():
    """Render xDS protocol flow and lifecycle diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'xDS Protocol Flow and Lifecycle', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Timeline
    timeline_y = 8
    ax.plot([1, 13], [timeline_y, timeline_y], 'k-', linewidth=2)
    
    # Protocol steps
    steps = [
        (2, 'Subscribe\nRequest', '#E3F2FD'),
        (4, 'Discovery\nResponse', '#F3E5F5'),
        (6, 'Config\nValidation', '#FFF3E0'),
        (8, 'ACK/NACK\nResponse', '#E8F5E8'),
        (10, 'Config\nApplication', '#FFEBEE'),
        (12, 'Update\nNotification', '#F1F8E9')
    ]
    
    for x, label, color in steps:
        # Step circle
        circle = Circle((x, timeline_y), 0.3, facecolor=color, edgecolor='black', linewidth=1)
        ax.add_patch(circle)
        ax.text(x, timeline_y, str(steps.index((x, label, color)) + 1), 
               fontsize=10, fontweight='bold', ha='center', va='center')
        
        # Step label
        ax.text(x, timeline_y - 0.8, label, fontsize=10, ha='center', fontweight='bold')
    
    # Detailed flow diagram
    # Management Server
    server_box = FancyBboxPatch((1, 5.5), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#E3F2FD', 
                               edgecolor='black', linewidth=1)
    ax.add_patch(server_box)
    ax.text(2.5, 6.25, 'xDS Management\nServer', fontsize=12, fontweight='bold', ha='center')
    
    # Envoy Proxy
    proxy_box = FancyBboxPatch((10, 5.5), 3, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#E8F5E8', 
                              edgecolor='black', linewidth=1)
    ax.add_patch(proxy_box)
    ax.text(11.5, 6.25, 'Envoy Proxy\nClient', fontsize=12, fontweight='bold', ha='center')
    
    # Flow arrows and messages
    flows = [
        (4, 6.5, 10, 6.5, 'DiscoveryRequest\n(Subscribe)', 'right'),
        (10, 6, 4, 6, 'DiscoveryResponse\n(Config)', 'left'),
        (4, 5.8, 10, 5.8, 'DiscoveryRequest\n(ACK/NACK)', 'right')
    ]
    
    for x1, y1, x2, y2, label, direction in flows:
        if direction == 'right':
            ax.annotate('', xy=(x2, y1), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', color='blue', lw=2))
            ax.text((x1 + x2) / 2, y1 + 0.2, label, fontsize=9, ha='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='lightblue', alpha=0.7))
        else:
            ax.annotate('', xy=(x2, y1), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', color='green', lw=2))
            ax.text((x1 + x2) / 2, y1 - 0.3, label, fontsize=9, ha='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgreen', alpha=0.7))
    
    # Resource types
    ax.text(7, 4.5, 'xDS Resource Types:', fontsize=12, fontweight='bold', ha='center')
    
    resource_types = [
        'LDS: Listener Discovery Service',
        'RDS: Route Discovery Service', 
        'CDS: Cluster Discovery Service',
        'EDS: Endpoint Discovery Service',
        'SDS: Secret Discovery Service'
    ]
    
    for i, resource_type in enumerate(resource_types):
        ax.text(7, 4 - i*0.4, f"• {resource_type}", fontsize=10, ha='center')
    
    # Configuration states
    ax.text(2.5, 1.5, 'Configuration States:', fontsize=11, fontweight='bold')
    states = ['PENDING', 'WARMING', 'ACTIVE', 'DRAINING']
    colors = ['#FFEB3B', '#FF9800', '#4CAF50', '#F44336']
    
    for i, (state, color) in enumerate(zip(states, colors)):
        state_box = FancyBboxPatch((2.5 + i*2.5, 0.8), 2, 0.4, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=color, 
                                  edgecolor='black', linewidth=1, alpha=0.7)
        ax.add_patch(state_box)
        ax.text(3.5 + i*2.5, 1, state, fontsize=10, fontweight='bold', ha='center')
    
    plt.tight_layout()
    plt.savefig('xds_protocol_flow.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated xds_protocol_flow.png")

def render_service_mesh_traffic_management():
    """Render service mesh traffic management patterns"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'Service Mesh Traffic Management Patterns', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Ingress Gateway
    gateway_box = FancyBboxPatch((1, 7.5), 2.5, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#E3F2FD', 
                                edgecolor='black', linewidth=2)
    ax.add_patch(gateway_box)
    ax.text(2.25, 8.25, 'Ingress\nGateway', fontsize=11, fontweight='bold', ha='center')
    
    # Services with different versions
    services = [
        ('Service A\nv1 (90%)', 6, 8, '#E8F5E8'),
        ('Service A\nv2 (10%)', 8.5, 8, '#FFEBEE'),
        ('Service B\nv1', 6, 6, '#E8F5E8'),
        ('Service C\nv1', 10.5, 7, '#E8F5E8')
    ]
    
    for name, x, y, color in services:
        service_box = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor=color, 
                                    edgecolor='black', linewidth=1)
        ax.add_patch(service_box)
        ax.text(x, y, name, fontsize=10, fontweight='bold', ha='center')
    
    # Traffic splitting arrows
    # 90% to v1
    ax.annotate('', xy=(5.2, 8), xytext=(3.5, 8.25),
               arrowprops=dict(arrowstyle='->', color='green', lw=3))
    ax.text(4.3, 8.3, '90%', fontsize=10, fontweight='bold', color='green')
    
    # 10% to v2
    ax.annotate('', xy=(7.7, 8), xytext=(3.5, 8.25),
               arrowprops=dict(arrowstyle='->', color='red', lw=1))
    ax.text(5.5, 8.5, '10%', fontsize=10, fontweight='bold', color='red')
    
    # Service-to-service communication
    ax.annotate('', xy=(5.2, 6), xytext=(6, 7.4),
               arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    
    ax.annotate('', xy=(9.7, 7), xytext=(6.8, 6),
               arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    
    # Circuit breaker
    cb_box = FancyBboxPatch((11.5, 5), 2, 1, 
                           boxstyle="round,pad=0.1", 
                           facecolor='#FFF3E0', 
                           edgecolor='orange', linewidth=2)
    ax.add_patch(cb_box)
    ax.text(12.5, 5.5, 'Circuit\nBreaker', fontsize=10, fontweight='bold', ha='center')
    
    # Traffic policies
    policies_box = FancyBboxPatch((1, 4), 12, 2, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#F3E5F5', 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(policies_box)
    ax.text(7, 5.5, 'Traffic Management Policies', fontsize=12, fontweight='bold', ha='center')
    
    policy_items = [
        '• Canary Deployments: Gradual traffic shifting (1% → 10% → 50% → 100%)',
        '• Blue-Green Deployments: Instant traffic switching between versions',
        '• Circuit Breaking: Automatic failure isolation and recovery',
        '• Retry Policies: Configurable retry logic with exponential backoff',
        '• Timeout Management: Request-level and service-level timeouts',
        '• Rate Limiting: Request rate control and quota management'
    ]
    
    for i, policy in enumerate(policy_items):
        ax.text(1.5, 5.2 - i*0.2, policy, fontsize=9, va='center')
    
    # Observability
    obs_box = FancyBboxPatch((1, 1.5), 12, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor='#E1F5FE', 
                            edgecolor='black', linewidth=1)
    ax.add_patch(obs_box)
    ax.text(7, 2.7, 'Observability & Security', fontsize=12, fontweight='bold', ha='center')
    
    obs_items = [
        '• Distributed Tracing: End-to-end request visibility with Jaeger/Zipkin',
        '• Metrics Collection: Prometheus integration for service mesh metrics',
        '• Access Logs: Detailed request/response logging with custom formats',
        '• mTLS: Automatic mutual TLS for service-to-service encryption',
        '• Authorization Policies: Fine-grained access control rules'
    ]
    
    for i, item in enumerate(obs_items):
        ax.text(1.5, 2.5 - i*0.2, item, fontsize=9, va='center')
    
    # External traffic indicator
    ax.text(0.5, 8.25, 'External\nTraffic', fontsize=10, fontweight='bold', ha='center')
    ax.annotate('', xy=(1, 8.25), xytext=(0.2, 8.25),
               arrowprops=dict(arrowstyle='->', color='black', lw=2))
    
    plt.tight_layout()
    plt.savefig('service_mesh_traffic_management.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated service_mesh_traffic_management.png")

def render_all_diagrams():
    """Render all Envoy xDS diagrams"""
    print("Rendering Envoy xDS diagrams...")
    
    render_xds_architecture()
    render_xds_protocol_flow()
    render_service_mesh_traffic_management()
    
    print("All Envoy xDS diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
