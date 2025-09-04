#!/usr/bin/env python3
"""
CNI Architecture Diagram Renderer
Generates visual diagrams for Container Network Interface
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle
import numpy as np

def render_cni_architecture():
    """Render CNI plugin architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Colors
    kubelet_color = '#E1F5FE'
    cni_color = '#FFF3E0'
    network_color = '#F3E5F5'
    pod_color = '#E8F5E8'
    host_color = '#FFEBEE'
    
    # Title
    ax.text(7, 9.5, 'Container Network Interface (CNI) Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Kubernetes Control Plane
    kubelet_box = FancyBboxPatch((0.5, 7.5), 3, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor=kubelet_color, 
                                edgecolor='black', linewidth=1)
    ax.add_patch(kubelet_box)
    ax.text(2, 8.2, 'kubelet', fontsize=12, fontweight='bold', ha='center')
    ax.text(2, 7.8, 'Container Runtime\nCNI Plugin Execution', fontsize=10, ha='center')
    
    # CNI Plugin Chain
    cni_main_box = FancyBboxPatch((4.5, 8), 2.5, 1, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=cni_color, 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(cni_main_box)
    ax.text(5.75, 8.5, 'Main CNI Plugin', fontsize=11, fontweight='bold', ha='center')
    ax.text(5.75, 8.2, 'bridge/calico/flannel', fontsize=9, ha='center')
    
    cni_ipam_box = FancyBboxPatch((4.5, 6.5), 2.5, 1, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=cni_color, 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(cni_ipam_box)
    ax.text(5.75, 7, 'IPAM Plugin', fontsize=11, fontweight='bold', ha='center')
    ax.text(5.75, 6.7, 'host-local/dhcp', fontsize=9, ha='center')
    
    cni_meta_box = FancyBboxPatch((7.5, 7.25), 2.5, 1, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=cni_color, 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(cni_meta_box)
    ax.text(8.75, 7.75, 'Meta Plugins', fontsize=11, fontweight='bold', ha='center')
    ax.text(8.75, 7.45, 'portmap/bandwidth', fontsize=9, ha='center')
    
    # Network Namespaces
    host_ns_box = FancyBboxPatch((10.5, 7.5), 3, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor=host_color, 
                                edgecolor='black', linewidth=1)
    ax.add_patch(host_ns_box)
    ax.text(12, 8.2, 'Host Network', fontsize=12, fontweight='bold', ha='center')
    ax.text(12, 7.8, 'Namespace', fontsize=12, fontweight='bold', ha='center')
    
    # Pod Network Namespaces
    pod_ns_y = 5.5
    for i, pod_name in enumerate(['Pod A', 'Pod B', 'Pod C']):
        x = 1 + i * 4
        pod_ns_box = FancyBboxPatch((x, pod_ns_y), 2.5, 1, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=network_color, 
                                   edgecolor='black', linewidth=1)
        ax.add_patch(pod_ns_box)
        ax.text(x + 1.25, pod_ns_y + 0.5, f'{pod_name} NetNS', fontsize=10, fontweight='bold', ha='center')
    
    # Network Interfaces
    # Host interfaces
    eth0_box = FancyBboxPatch((10.5, 5.5), 1.4, 0.8, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#DCEDC8', 
                             edgecolor='black', linewidth=1)
    ax.add_patch(eth0_box)
    ax.text(11.2, 5.9, 'eth0', fontsize=10, fontweight='bold', ha='center')
    
    cni_bridge_box = FancyBboxPatch((12.1, 5.5), 1.4, 0.8, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='#DCEDC8', 
                                   edgecolor='black', linewidth=1)
    ax.add_patch(cni_bridge_box)
    ax.text(12.8, 5.9, 'cni0', fontsize=10, fontweight='bold', ha='center')
    
    # Veth pairs
    veth_y = 4
    for i, veth_name in enumerate(['veth-a', 'veth-b', 'veth-c']):
        x = 1.5 + i * 4
        veth_box = FancyBboxPatch((x, veth_y), 1.5, 0.6, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#FFF9C4', 
                                 edgecolor='black', linewidth=1)
        ax.add_patch(veth_box)
        ax.text(x + 0.75, veth_y + 0.3, veth_name, fontsize=9, fontweight='bold', ha='center')
    
    # Pods with IP addresses
    pod_ips = ['10.244.1.2', '10.244.1.3', '10.244.2.2']
    pod_y = 2.5
    for i, (pod_name, ip) in enumerate(zip(['Pod A', 'Pod B', 'Pod C'], pod_ips)):
        x = 1 + i * 4
        pod_box = FancyBboxPatch((x, pod_y), 2.5, 1, 
                                boxstyle="round,pad=0.1", 
                                facecolor=pod_color, 
                                edgecolor='black', linewidth=1)
        ax.add_patch(pod_box)
        ax.text(x + 1.25, pod_y + 0.7, pod_name, fontsize=11, fontweight='bold', ha='center')
        ax.text(x + 1.25, pod_y + 0.3, ip, fontsize=10, ha='center')
    
    # Connection arrows
    # kubelet to CNI
    ax.arrow(3.5, 8.2, 0.8, 0, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    
    # CNI plugin chain
    ax.arrow(5.75, 8, 0, -0.3, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    ax.arrow(7, 7.25, 0.3, 0, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    
    # CNI to host network
    ax.arrow(10, 7.75, 0.3, 0, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    
    # Pod namespaces to veth
    for i in range(3):
        x = 2.25 + i * 4
        ax.arrow(x, 5.5, 0, -0.8, head_width=0.1, head_length=0.1, fc='green', ec='green')
    
    # Veth to pods
    for i in range(3):
        x = 2.25 + i * 4
        ax.arrow(x, 4, 0, -1, head_width=0.1, head_length=0.1, fc='green', ec='green')
    
    # Bridge connections
    for i in range(3):
        x_start = 2.25 + i * 4
        ax.plot([x_start, 12.8], [4.3, 5.5], 'r--', linewidth=1, alpha=0.7)
    
    # Add legend
    ax.text(7, 1.5, 'CNI Plugin Execution Flow:', fontsize=12, fontweight='bold', ha='center')
    ax.text(7, 1.1, '1. kubelet calls CNI plugin with ADD command', fontsize=10, ha='center')
    ax.text(7, 0.8, '2. Main plugin creates network interface and veth pair', fontsize=10, ha='center')
    ax.text(7, 0.5, '3. IPAM plugin allocates IP address from subnet', fontsize=10, ha='center')
    ax.text(7, 0.2, '4. Meta plugins apply additional configuration (QoS, policies)', fontsize=10, ha='center')
    
    plt.tight_layout()
    plt.savefig('cni_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated cni_architecture.png")

def render_network_policy_flow():
    """Render network policy enforcement flow"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(6, 7.5, 'Kubernetes Network Policy Enforcement', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Source pod
    source_box = FancyBboxPatch((0.5, 5.5), 2, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#E8F5E8', 
                               edgecolor='black', linewidth=1)
    ax.add_patch(source_box)
    ax.text(1.5, 6.2, 'Source Pod', fontsize=11, fontweight='bold', ha='center')
    ax.text(1.5, 5.8, 'app=web', fontsize=10, ha='center')
    
    # Policy engine
    policy_box = FancyBboxPatch((4, 5.5), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#FFF3E0', 
                               edgecolor='black', linewidth=1)
    ax.add_patch(policy_box)
    ax.text(5.5, 6.2, 'Policy Engine', fontsize=11, fontweight='bold', ha='center')
    ax.text(5.5, 5.8, 'NetworkPolicy Rules', fontsize=10, ha='center')
    
    # Target pod
    target_box = FancyBboxPatch((9, 5.5), 2, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#E3F2FD', 
                               edgecolor='black', linewidth=1)
    ax.add_patch(target_box)
    ax.text(10, 6.2, 'Target Pod', fontsize=11, fontweight='bold', ha='center')
    ax.text(10, 5.8, 'app=api', fontsize=10, ha='center')
    
    # Policy rules
    rules = [
        ('Ingress Rule', 4, 4, '#C8E6C9'),
        ('Port Match', 5.5, 4, '#DCEDC8'),
        ('Peer Match', 7, 4, '#F1F8E9')
    ]
    
    for rule, x, y, color in rules:
        rule_box = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=color, 
                                 edgecolor='black', linewidth=1)
        ax.add_patch(rule_box)
        ax.text(x, y, rule, fontsize=9, ha='center', va='center')
    
    # Decision flow
    decision_box = FancyBboxPatch((4.5, 2.5), 2, 1, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#FFCDD2', 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(decision_box)
    ax.text(5.5, 3, 'ALLOW/DENY', fontsize=11, fontweight='bold', ha='center')
    
    # Arrows
    # Source to policy engine
    ax.arrow(2.5, 6.2, 1.3, 0, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    ax.text(3.25, 6.5, 'Traffic', fontsize=9, ha='center')
    
    # Policy engine to target
    ax.arrow(7, 6.2, 1.8, 0, head_width=0.1, head_length=0.1, fc='green', ec='green')
    ax.text(7.9, 6.5, 'Allowed', fontsize=9, ha='center')
    
    # Policy evaluation flow
    ax.arrow(5.5, 5.5, 0, -1.8, head_width=0.1, head_length=0.1, fc='red', ec='red')
    
    # Rule evaluation
    for i, (_, x, y, _) in enumerate(rules):
        if i < len(rules) - 1:
            next_x = rules[i + 1][1]
            ax.arrow(x + 0.7, y, next_x - x - 1.4, 0, head_width=0.05, head_length=0.05, fc='orange', ec='orange')
    
    # Add policy example
    ax.text(6, 1.5, 'Example NetworkPolicy Rule:', fontsize=12, fontweight='bold', ha='center')
    ax.text(6, 1.1, 'Allow: app=web → app=api on port 8080/TCP', fontsize=10, ha='center')
    ax.text(6, 0.8, 'Deny: app=web → app=database (no matching rule)', fontsize=10, ha='center')
    ax.text(6, 0.5, 'Default: Deny all traffic when NetworkPolicy exists', fontsize=10, ha='center')
    
    plt.tight_layout()
    plt.savefig('network_policy_flow.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated network_policy_flow.png")

def render_cni_plugin_types():
    """Render CNI plugin types and capabilities"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(6, 7.5, 'CNI Plugin Types and Capabilities', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Main plugins
    main_plugins = [
        ('bridge', 1, 6, 'L2 Bridge\nNetworking'),
        ('ipvlan', 3.5, 6, 'L2/L3 VLAN\nNetworking'),
        ('macvlan', 6, 6, 'MAC Address\nAssignment'),
        ('host-device', 8.5, 6, 'Host Device\nMovement'),
        ('ptp', 11, 6, 'Point-to-Point\nConnections')
    ]
    
    for name, x, y, desc in main_plugins:
        plugin_box = FancyBboxPatch((x-0.7, y-0.5), 1.4, 1, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='#E3F2FD', 
                                   edgecolor='black', linewidth=1)
        ax.add_patch(plugin_box)
        ax.text(x, y + 0.2, name, fontsize=10, fontweight='bold', ha='center')
        ax.text(x, y - 0.2, desc, fontsize=8, ha='center')
    
    ax.text(6, 5.2, 'Main Plugins (Interface Creation)', fontsize=12, fontweight='bold', ha='center')
    
    # IPAM plugins
    ipam_plugins = [
        ('static', 2, 4, 'Static IP\nAssignment'),
        ('dhcp', 4.5, 4, 'DHCP Client\nIntegration'),
        ('host-local', 7, 4, 'Local Subnet\nAllocation'),
        ('whereabouts', 9.5, 4, 'Cluster-wide\nIP Management')
    ]
    
    for name, x, y, desc in ipam_plugins:
        plugin_box = FancyBboxPatch((x-0.7, y-0.5), 1.4, 1, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='#FFF3E0', 
                                   edgecolor='black', linewidth=1)
        ax.add_patch(plugin_box)
        ax.text(x, y + 0.2, name, fontsize=10, fontweight='bold', ha='center')
        ax.text(x, y - 0.2, desc, fontsize=8, ha='center')
    
    ax.text(6, 3.2, 'IPAM Plugins (IP Address Management)', fontsize=12, fontweight='bold', ha='center')
    
    # Meta plugins
    meta_plugins = [
        ('flannel', 1.5, 2, 'Overlay\nNetworking'),
        ('calico', 3.5, 2, 'Policy\nEnforcement'),
        ('weave', 5.5, 2, 'Mesh\nNetworking'),
        ('cilium', 7.5, 2, 'eBPF\nNetworking'),
        ('antrea', 9.5, 2, 'OVS\nNetworking')
    ]
    
    for name, x, y, desc in meta_plugins:
        plugin_box = FancyBboxPatch((x-0.7, y-0.5), 1.4, 1, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='#F3E5F5', 
                                   edgecolor='black', linewidth=1)
        ax.add_patch(plugin_box)
        ax.text(x, y + 0.2, name, fontsize=10, fontweight='bold', ha='center')
        ax.text(x, y - 0.2, desc, fontsize=8, ha='center')
    
    ax.text(6, 1.2, 'Meta Plugins (Advanced Networking)', fontsize=12, fontweight='bold', ha='center')
    
    # Add capability matrix
    ax.text(6, 0.5, 'Capabilities: Bridge (Simple), Calico (Policy), Flannel (Overlay), Cilium (eBPF)', 
            fontsize=10, ha='center')
    
    plt.tight_layout()
    plt.savefig('cni_plugin_types.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated cni_plugin_types.png")

def render_all_diagrams():
    """Render all CNI diagrams"""
    print("Rendering CNI diagrams...")
    
    render_cni_architecture()
    render_network_policy_flow()
    render_cni_plugin_types()
    
    print("All CNI diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
