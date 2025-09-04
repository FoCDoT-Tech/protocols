#!/usr/bin/env python3
"""
Kubernetes API Diagram Renderer
Generates visual diagrams for Kubernetes API architecture and operations
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def render_kube_api_architecture():
    """Render Kubernetes API Server architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Colors
    client_color = '#E3F2FD'
    api_color = '#FFF3E0'
    storage_color = '#F3E5F5'
    component_color = '#E8F5E8'
    
    # Title
    ax.text(7, 9.5, 'Kubernetes API Server Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Client Layer
    client_box = FancyBboxPatch((0.5, 7.5), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor=client_color, 
                               edgecolor='black', linewidth=1)
    ax.add_patch(client_box)
    ax.text(2, 8.2, 'Client Layer', fontsize=12, fontweight='bold', ha='center')
    ax.text(2, 7.8, 'kubectl, client-go\nHTTP/1.1 + TLS', fontsize=10, ha='center')
    
    # Load Balancer
    lb_box = FancyBboxPatch((5, 7.5), 2, 1.5, 
                           boxstyle="round,pad=0.1", 
                           facecolor='#FFECB3', 
                           edgecolor='black', linewidth=1)
    ax.add_patch(lb_box)
    ax.text(6, 8.2, 'Load Balancer', fontsize=11, fontweight='bold', ha='center')
    ax.text(6, 7.8, 'HAProxy/nginx', fontsize=10, ha='center')
    
    # API Server Components
    # Authentication
    auth_box = FancyBboxPatch((8.5, 7.5), 2.5, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor=api_color, 
                             edgecolor='black', linewidth=1)
    ax.add_patch(auth_box)
    ax.text(9.75, 8.2, 'Authentication', fontsize=11, fontweight='bold', ha='center')
    ax.text(9.75, 7.8, 'Bearer Tokens\nX.509 Certificates', fontsize=10, ha='center')
    
    # Authorization
    authz_box = FancyBboxPatch((11.5, 7.5), 2, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor=api_color, 
                              edgecolor='black', linewidth=1)
    ax.add_patch(authz_box)
    ax.text(12.5, 8.2, 'Authorization', fontsize=11, fontweight='bold', ha='center')
    ax.text(12.5, 7.8, 'RBAC\nWebhook', fontsize=10, ha='center')
    
    # Admission Control
    admission_box = FancyBboxPatch((8.5, 5.5), 2.5, 1.5, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=api_color, 
                                  edgecolor='black', linewidth=1)
    ax.add_patch(admission_box)
    ax.text(9.75, 6.2, 'Admission Control', fontsize=11, fontweight='bold', ha='center')
    ax.text(9.75, 5.8, 'Validation\nMutation', fontsize=10, ha='center')
    
    # Resource Registry
    registry_box = FancyBboxPatch((11.5, 5.5), 2, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=api_color, 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(registry_box)
    ax.text(12.5, 6.2, 'Resource Registry', fontsize=11, fontweight='bold', ha='center')
    ax.text(12.5, 5.8, 'Schema\nValidation', fontsize=10, ha='center')
    
    # Storage Layer
    etcd_box = FancyBboxPatch((2, 3.5), 3, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor=storage_color, 
                             edgecolor='black', linewidth=1)
    ax.add_patch(etcd_box)
    ax.text(3.5, 4.2, 'etcd Cluster', fontsize=12, fontweight='bold', ha='center')
    ax.text(3.5, 3.8, 'Raft Consensus\ngRPC Protocol', fontsize=10, ha='center')
    
    # Watch Streams
    watch_box = FancyBboxPatch((6, 3.5), 2.5, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#E1F5FE', 
                              edgecolor='black', linewidth=1)
    ax.add_patch(watch_box)
    ax.text(7.25, 4.2, 'Watch Streams', fontsize=11, fontweight='bold', ha='center')
    ax.text(7.25, 3.8, 'HTTP Streaming\nEvent Notifications', fontsize=10, ha='center')
    
    # Controllers
    controller_box = FancyBboxPatch((9.5, 3.5), 3.5, 1.5, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=component_color, 
                                   edgecolor='black', linewidth=1)
    ax.add_patch(controller_box)
    ax.text(11.25, 4.2, 'Controllers', fontsize=12, fontweight='bold', ha='center')
    ax.text(11.25, 3.8, 'Deployment, ReplicaSet\nService, Ingress', fontsize=10, ha='center')
    
    # Resource Types
    resources = ['Pods', 'Services', 'Deployments', 'ConfigMaps']
    for i, resource in enumerate(resources):
        x = 1 + i * 3
        res_box = FancyBboxPatch((x, 1.5), 2.5, 1, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#F0F4C3', 
                                edgecolor='black', linewidth=1)
        ax.add_patch(res_box)
        ax.text(x + 1.25, 2, resource, fontsize=10, fontweight='bold', ha='center')
    
    # Arrows
    # Client to Load Balancer
    ax.arrow(3.5, 8.2, 1.3, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Load Balancer to Auth
    ax.arrow(7, 8.2, 1.3, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Auth to Authorization
    ax.arrow(11, 8.2, 0.3, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Authorization to Admission
    ax.arrow(12.5, 7.5, 0, -0.8, head_width=0.1, head_length=0.1, fc='black', ec='black')
    ax.arrow(12.5, 6.7, -2.3, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Admission to Registry
    ax.arrow(11, 6.2, 0.3, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Registry to etcd
    ax.arrow(11.5, 5.8, -6, -1.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # etcd to Watch
    ax.arrow(5, 4.2, 0.8, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Watch to Controllers
    ax.arrow(8.5, 4.2, 0.8, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    plt.title('Kubernetes API Server - Request Processing Flow', pad=20)
    plt.tight_layout()
    plt.savefig('kube_api_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated kube_api_architecture.png")

def render_api_request_flow():
    """Render API request processing flow"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(6, 7.5, 'Kubernetes API Request Processing Flow', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Steps
    steps = [
        ('1. HTTP Request', 1, 6, '#E3F2FD'),
        ('2. TLS Termination', 3, 6, '#FFF3E0'),
        ('3. Authentication', 5, 6, '#FFECB3'),
        ('4. Authorization', 7, 6, '#E8F5E8'),
        ('5. Admission Control', 9, 6, '#F3E5F5'),
        ('6. Validation', 11, 6, '#FCE4EC'),
        ('7. etcd Storage', 9, 4, '#E1F5FE'),
        ('8. Response', 7, 4, '#F1F8E9'),
        ('9. Watch Events', 5, 4, '#FFF8E1'),
        ('10. Controller Action', 3, 4, '#EFEBE9'),
        ('11. Status Update', 1, 4, '#FAFAFA')
    ]
    
    for step, x, y, color in steps:
        box = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8, 
                            boxstyle="round,pad=0.1", 
                            facecolor=color, 
                            edgecolor='black', linewidth=1)
        ax.add_patch(box)
        ax.text(x, y, step, fontsize=9, ha='center', va='center')
    
    # Flow arrows
    arrows = [
        (1.8, 6, 0.4, 0),      # 1 -> 2
        (3.8, 6, 0.4, 0),      # 2 -> 3
        (5.8, 6, 0.4, 0),      # 3 -> 4
        (7.8, 6, 0.4, 0),      # 4 -> 5
        (9.8, 6, 0.4, 0),      # 5 -> 6
        (11, 5.6, -1.5, -1.2), # 6 -> 7
        (8.2, 4, -0.4, 0),     # 7 -> 8
        (6.2, 4, -0.4, 0),     # 8 -> 9
        (4.2, 4, -0.4, 0),     # 9 -> 10
        (2.2, 4, -0.4, 0),     # 10 -> 11
    ]
    
    for x, y, dx, dy in arrows:
        ax.arrow(x, y, dx, dy, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Add timing annotations
    ax.text(6, 2.5, 'Typical Processing Times:', fontsize=12, fontweight='bold', ha='center')
    ax.text(6, 2, 'Authentication: 1-5ms', fontsize=10, ha='center')
    ax.text(6, 1.7, 'Authorization: 1-10ms', fontsize=10, ha='center')
    ax.text(6, 1.4, 'Admission Control: 5-50ms', fontsize=10, ha='center')
    ax.text(6, 1.1, 'etcd Write: 10-100ms', fontsize=10, ha='center')
    ax.text(6, 0.8, 'Total Request: 20-200ms', fontsize=10, ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('api_request_flow.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated api_request_flow.png")

def render_resource_lifecycle():
    """Render Kubernetes resource lifecycle diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(6, 7.5, 'Kubernetes Resource Lifecycle', 
            fontsize=14, fontweight='bold', ha='center')
    
    # States
    states = [
        ('Pending', 2, 6, '#FFECB3'),
        ('Running', 6, 6, '#C8E6C9'),
        ('Succeeded', 10, 6, '#DCEDC8'),
        ('Failed', 10, 4, '#FFCDD2'),
        ('Unknown', 6, 4, '#F5F5F5'),
        ('Terminating', 2, 4, '#FFE0B2')
    ]
    
    for state, x, y, color in states:
        circle = plt.Circle((x, y), 0.8, facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        ax.text(x, y, state, fontsize=10, fontweight='bold', ha='center', va='center')
    
    # Transitions
    transitions = [
        (2.8, 6, 2.4, 0, 'Created'),           # Pending -> Running
        (6.8, 6, 2.4, 0, 'Completed'),        # Running -> Succeeded
        (6.8, 5.6, 2.4, -1.2, 'Error'),       # Running -> Failed
        (6, 5.2, 0, -0.4, 'Lost Contact'),    # Running -> Unknown
        (2, 5.2, 0, -0.4, 'Deletion'),        # Pending -> Terminating
        (5.2, 4.4, -2.4, 0, 'Cleanup'),       # Unknown -> Terminating
    ]
    
    for x, y, dx, dy, label in transitions:
        ax.arrow(x, y, dx, dy, head_width=0.15, head_length=0.2, fc='blue', ec='blue')
        # Add label
        mid_x, mid_y = x + dx/2, y + dy/2
        ax.text(mid_x, mid_y + 0.3, label, fontsize=8, ha='center', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Add controller actions
    ax.text(6, 2.5, 'Controller Actions:', fontsize=12, fontweight='bold', ha='center')
    ax.text(6, 2, '• Create: API validation → etcd storage → kubelet scheduling', fontsize=10, ha='center')
    ax.text(6, 1.6, '• Update: Spec changes → rolling updates → status reconciliation', fontsize=10, ha='center')
    ax.text(6, 1.2, '• Delete: Graceful termination → finalizers → etcd cleanup', fontsize=10, ha='center')
    ax.text(6, 0.8, '• Watch: Event streams → controller reactions → desired state', fontsize=10, ha='center')
    
    plt.tight_layout()
    plt.savefig('resource_lifecycle.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated resource_lifecycle.png")

def render_all_diagrams():
    """Render all Kubernetes API diagrams"""
    print("Rendering Kubernetes API diagrams...")
    
    render_kube_api_architecture()
    render_api_request_flow()
    render_resource_lifecycle()
    
    print("All diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
