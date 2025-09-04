#!/usr/bin/env python3
"""
CSI Architecture Diagram Renderer
Generates visual diagrams for Container Storage Interface
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle
import numpy as np

def render_csi_architecture():
    """Render CSI driver architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Colors
    control_plane_color = '#E1F5FE'
    csi_color = '#FFF3E0'
    node_color = '#F3E5F5'
    storage_color = '#E8F5E8'
    grpc_color = '#FFEBEE'
    
    # Title
    ax.text(7, 9.5, 'Container Storage Interface (CSI) Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Kubernetes Control Plane
    control_plane_box = FancyBboxPatch((0.5, 7.5), 4, 1.5, 
                                      boxstyle="round,pad=0.1", 
                                      facecolor=control_plane_color, 
                                      edgecolor='black', linewidth=1)
    ax.add_patch(control_plane_box)
    ax.text(2.5, 8.2, 'Kubernetes Control Plane', fontsize=12, fontweight='bold', ha='center')
    ax.text(2.5, 7.8, 'API Server, Scheduler\nController Manager', fontsize=10, ha='center')
    
    # CSI External Components
    external_components = [
        ('External\nProvisioner', 5.5, 8.5),
        ('External\nAttacher', 7, 8.5),
        ('External\nSnapshotter', 8.5, 8.5),
        ('External\nResizer', 10, 8.5)
    ]
    
    for name, x, y in external_components:
        comp_box = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=csi_color, 
                                 edgecolor='black', linewidth=1)
        ax.add_patch(comp_box)
        ax.text(x, y, name, fontsize=9, fontweight='bold', ha='center')
    
    # CSI Driver Pod
    driver_box = FancyBboxPatch((11, 7.5), 2.5, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor=csi_color, 
                               edgecolor='black', linewidth=1)
    ax.add_patch(driver_box)
    ax.text(12.25, 8.2, 'CSI Driver Pod', fontsize=12, fontweight='bold', ha='center')
    ax.text(12.25, 7.8, 'Identity, Controller\nNode Services', fontsize=10, ha='center')
    
    # Node Components
    node_box = FancyBboxPatch((0.5, 5.5), 4, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor=node_color, 
                             edgecolor='black', linewidth=1)
    ax.add_patch(node_box)
    ax.text(2.5, 6.2, 'Kubernetes Node', fontsize=12, fontweight='bold', ha='center')
    ax.text(2.5, 5.8, 'kubelet, Volume Manager', fontsize=10, ha='center')
    
    # Volume Lifecycle
    lifecycle_stages = [
        ('Volume\nCreation', 5.5, 6.2),
        ('Volume\nAttachment', 7, 6.2),
        ('Volume\nStaging', 8.5, 6.2),
        ('Volume\nPublishing', 10, 6.2)
    ]
    
    for name, x, y in lifecycle_stages:
        stage_box = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#E3F2FD', 
                                  edgecolor='black', linewidth=1)
        ax.add_patch(stage_box)
        ax.text(x, y, name, fontsize=9, fontweight='bold', ha='center')
    
    # Pod Volume Mounts
    pod_box = FancyBboxPatch((11, 5.5), 2.5, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor='#F1F8E9', 
                            edgecolor='black', linewidth=1)
    ax.add_patch(pod_box)
    ax.text(12.25, 6.2, 'Pod Volume Mounts', fontsize=12, fontweight='bold', ha='center')
    ax.text(12.25, 5.8, '/var/lib/app/data', fontsize=10, ha='center')
    
    # Storage Backend
    storage_backends = [
        ('Cloud Block\nStorage', 2, 3.5),
        ('Network\nStorage', 5, 3.5),
        ('Local\nStorage', 8, 3.5),
        ('Object\nStorage', 11, 3.5)
    ]
    
    for name, x, y in storage_backends:
        storage_box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor=storage_color, 
                                    edgecolor='black', linewidth=1)
        ax.add_patch(storage_box)
        ax.text(x, y, name, fontsize=10, fontweight='bold', ha='center')
    
    # gRPC Communication
    grpc_box = FancyBboxPatch((5, 1.5), 4, 1, 
                             boxstyle="round,pad=0.1", 
                             facecolor=grpc_color, 
                             edgecolor='black', linewidth=1)
    ax.add_patch(grpc_box)
    ax.text(7, 2, 'gRPC Communication Layer', fontsize=12, fontweight='bold', ha='center')
    ax.text(7, 1.7, 'Identity, Controller, Node Services', fontsize=10, ha='center')
    
    # Connection arrows
    # Control plane to external components
    for _, x, y in external_components:
        ax.arrow(4.5, 8.2, x-5, y-8.2, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    
    # External components to driver
    ax.arrow(10.6, 8.5, 0.2, -0.8, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    
    # Node to lifecycle
    ax.arrow(4.5, 6.2, 0.8, 0, head_width=0.1, head_length=0.1, fc='green', ec='green')
    
    # Lifecycle flow
    for i in range(len(lifecycle_stages) - 1):
        x1 = lifecycle_stages[i][1]
        x2 = lifecycle_stages[i + 1][1]
        ax.arrow(x1 + 0.6, 6.2, x2 - x1 - 1.2, 0, head_width=0.1, head_length=0.1, fc='green', ec='green')
    
    # Lifecycle to pod
    ax.arrow(10.6, 6.2, 0.2, 0, head_width=0.1, head_length=0.1, fc='green', ec='green')
    
    # Driver to storage backends
    for name, x, y in storage_backends:
        ax.arrow(12.25, 7.5, x - 12.25, y - 7.5 + 0.5, head_width=0.1, head_length=0.1, fc='red', ec='red', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('csi_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated csi_architecture.png")

def render_volume_lifecycle():
    """Render volume lifecycle diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(6, 7.5, 'CSI Volume Lifecycle', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Lifecycle stages
    stages = [
        ('1. PVC\nCreated', 1, 6, '#E3F2FD'),
        ('2. Volume\nProvisioned', 3, 6, '#FFF3E0'),
        ('3. Volume\nAttached', 5, 6, '#F3E5F5'),
        ('4. Volume\nStaged', 7, 6, '#E8F5E8'),
        ('5. Volume\nPublished', 9, 6, '#FFEBEE'),
        ('6. Pod\nRunning', 11, 6, '#F1F8E9')
    ]
    
    for stage, x, y, color in stages:
        stage_box = FancyBboxPatch((x-0.7, y-0.5), 1.4, 1, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=color, 
                                  edgecolor='black', linewidth=1)
        ax.add_patch(stage_box)
        ax.text(x, y, stage, fontsize=10, fontweight='bold', ha='center')
    
    # Flow arrows
    for i in range(len(stages) - 1):
        x1 = stages[i][1]
        x2 = stages[i + 1][1]
        ax.arrow(x1 + 0.7, 6, x2 - x1 - 1.4, 0, head_width=0.15, head_length=0.2, fc='blue', ec='blue')
    
    # CSI Operations
    operations = [
        ('CreateVolume', 3, 4.5),
        ('ControllerPublishVolume', 5, 4.5),
        ('NodeStageVolume', 7, 4.5),
        ('NodePublishVolume', 9, 4.5)
    ]
    
    for op, x, y in operations:
        op_box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#FFFDE7', 
                               edgecolor='orange', linewidth=1)
        ax.add_patch(op_box)
        ax.text(x, y, op, fontsize=9, ha='center')
        
        # Arrow from stage to operation
        ax.arrow(x, 5.5, 0, -0.7, head_width=0.1, head_length=0.1, fc='orange', ec='orange')
    
    # Cleanup flow
    cleanup_stages = [
        ('Pod\nTerminated', 11, 3),
        ('Volume\nUnpublished', 9, 3),
        ('Volume\nUnstaged', 7, 3),
        ('Volume\nDetached', 5, 3),
        ('Volume\nDeleted', 3, 3)
    ]
    
    for stage, x, y in cleanup_stages:
        stage_box = FancyBboxPatch((x-0.7, y-0.5), 1.4, 1, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#FFCDD2', 
                                  edgecolor='black', linewidth=1)
        ax.add_patch(stage_box)
        ax.text(x, y, stage, fontsize=10, fontweight='bold', ha='center')
    
    # Cleanup arrows (reverse direction)
    for i in range(len(cleanup_stages) - 1):
        x1 = cleanup_stages[i][1]
        x2 = cleanup_stages[i + 1][1]
        ax.arrow(x1 - 0.7, 3, x2 - x1 + 1.4, 0, head_width=0.15, head_length=0.2, fc='red', ec='red')
    
    # Add timing information
    ax.text(6, 1.5, 'Typical Timing:', fontsize=12, fontweight='bold', ha='center')
    ax.text(6, 1.1, 'Volume Creation: 10-60 seconds', fontsize=10, ha='center')
    ax.text(6, 0.8, 'Volume Attachment: 5-30 seconds', fontsize=10, ha='center')
    ax.text(6, 0.5, 'Volume Staging/Publishing: 1-5 seconds', fontsize=10, ha='center')
    
    plt.tight_layout()
    plt.savefig('volume_lifecycle.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated volume_lifecycle.png")

def render_storage_classes():
    """Render storage classes and provisioning diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(6, 7.5, 'Storage Classes and Dynamic Provisioning', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Storage Classes
    storage_classes = [
        ('fast-ssd', 2, 6, 'gp3, 3000 IOPS\nEncrypted', '#E8F5E8'),
        ('standard', 6, 6, 'gp2, Standard\nPerformance', '#FFF3E0'),
        ('archive', 10, 6, 'sc1, Cold Storage\nCost Optimized', '#F3E5F5')
    ]
    
    for name, x, y, desc, color in storage_classes:
        sc_box = FancyBboxPatch((x-1, y-0.7), 2, 1.4, 
                               boxstyle="round,pad=0.1", 
                               facecolor=color, 
                               edgecolor='black', linewidth=1)
        ax.add_patch(sc_box)
        ax.text(x, y + 0.3, name, fontsize=11, fontweight='bold', ha='center')
        ax.text(x, y - 0.3, desc, fontsize=9, ha='center')
    
    # PVCs
    pvcs = [
        ('web-data\n10Gi', 2, 4),
        ('database\n50Gi', 6, 4),
        ('backup\n100Gi', 10, 4)
    ]
    
    for name, x, y in pvcs:
        pvc_box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#E1F5FE', 
                                edgecolor='black', linewidth=1)
        ax.add_patch(pvc_box)
        ax.text(x, y, name, fontsize=10, fontweight='bold', ha='center')
    
    # PVs
    pvs = [
        ('pvc-abc123\n10Gi', 2, 2),
        ('pvc-def456\n50Gi', 6, 2),
        ('pvc-ghi789\n100Gi', 10, 2)
    ]
    
    for name, x, y in pvs:
        pv_box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#FFEBEE', 
                               edgecolor='black', linewidth=1)
        ax.add_patch(pv_box)
        ax.text(x, y, name, fontsize=10, fontweight='bold', ha='center')
    
    # Arrows showing provisioning flow
    for i, (_, x, _, _, _) in enumerate(storage_classes):
        # StorageClass to PVC
        ax.arrow(x, 5.3, 0, -0.6, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
        
        # PVC to PV
        ax.arrow(x, 3.5, 0, -0.8, head_width=0.1, head_length=0.1, fc='green', ec='green')
    
    # Add provisioning flow labels
    ax.text(1, 0.5, 'Dynamic Provisioning Flow:', fontsize=12, fontweight='bold', ha='left')
    ax.text(1, 0.2, '1. User creates PVC with StorageClass', fontsize=10, ha='left')
    ax.text(1, -0.1, '2. Provisioner creates volume in storage backend', fontsize=10, ha='left')
    ax.text(1, -0.4, '3. PV is created and bound to PVC', fontsize=10, ha='left')
    
    plt.tight_layout()
    plt.savefig('storage_classes.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated storage_classes.png")

def render_all_diagrams():
    """Render all CSI diagrams"""
    print("Rendering CSI diagrams...")
    
    render_csi_architecture()
    render_volume_lifecycle()
    render_storage_classes()
    
    print("All CSI diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
