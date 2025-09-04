#!/usr/bin/env python3
"""
MQTT Diagram Renderer
Generates visual diagrams for MQTT protocol concepts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, ConnectionPatch
import numpy as np

def create_mqtt_architecture_diagram():
    """Create MQTT broker architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'MQTT Broker Architecture', 
           fontsize=16, fontweight='bold', ha='center')
    
    # MQTT Broker Core
    broker_box = FancyBboxPatch((6, 7), 4, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#e1f5fe', edgecolor='#01579b', linewidth=2)
    ax.add_patch(broker_box)
    ax.text(8, 7.75, 'MQTT Broker', fontsize=12, fontweight='bold', ha='center')
    ax.text(8, 7.25, 'Message Router & Session Manager', fontsize=10, ha='center', style='italic')
    
    # Topic Management
    topic_box = FancyBboxPatch((1, 5), 4, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#e8f5e8', edgecolor='#2e7d32', linewidth=1)
    ax.add_patch(topic_box)
    ax.text(3, 6, 'Topic Tree', fontsize=11, fontweight='bold', ha='center')
    ax.text(3, 5.6, 'home/+/temperature', fontsize=9, ha='center')
    ax.text(3, 5.2, 'alerts/#', fontsize=9, ha='center')
    
    # Session Management
    session_box = FancyBboxPatch((6, 5), 4, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#fff3e0', edgecolor='#ef6c00', linewidth=1)
    ax.add_patch(session_box)
    ax.text(8, 6, 'Session Management', fontsize=11, fontweight='bold', ha='center')
    ax.text(8, 5.6, 'Clean/Persistent Sessions', fontsize=9, ha='center')
    ax.text(8, 5.2, 'Last Will & Testament', fontsize=9, ha='center')
    
    # QoS Levels
    qos_box = FancyBboxPatch((11, 5), 4, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor='#f3e5f5', edgecolor='#7b1fa2', linewidth=1)
    ax.add_patch(qos_box)
    ax.text(13, 6, 'Quality of Service', fontsize=11, fontweight='bold', ha='center')
    ax.text(13, 5.6, 'QoS 0, 1, 2', fontsize=9, ha='center')
    ax.text(13, 5.2, 'Delivery Guarantees', fontsize=9, ha='center')
    
    # IoT Devices
    devices = [
        ("Temp Sensor", 2, 2.5, "#ffcdd2"),
        ("Motion Detector", 5, 2.5, "#c8e6c9"),
        ("Smart Light", 8, 2.5, "#ffe0b2"),
        ("Thermostat", 11, 2.5, "#f8bbd9"),
        ("Door Sensor", 14, 2.5, "#e0f2f1")
    ]
    
    for name, x, y, color in devices:
        device_box = FancyBboxPatch((x-1, y-0.4), 2, 0.8, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(device_box)
        ax.text(x, y, name, fontsize=9, fontweight='bold', ha='center')
    
    # Applications
    apps = [
        ("Mobile App", 2, 0.5, "#e1f5fe"),
        ("Home Automation", 6, 0.5, "#e8f5e8"),
        ("Cloud Analytics", 10, 0.5, "#fff3e0"),
        ("Alert System", 14, 0.5, "#f3e5f5")
    ]
    
    for name, x, y, color in apps:
        app_box = FancyBboxPatch((x-1.2, y-0.3), 2.4, 0.6, 
                                boxstyle="round,pad=0.05", 
                                facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(app_box)
        ax.text(x, y, name, fontsize=9, fontweight='bold', ha='center')
    
    # Connection arrows
    connections = [
        # Broker to components
        ((6, 7.5), (5, 5.75)),  # Broker to Topic
        ((8, 7), (8, 6.5)),     # Broker to Session
        ((10, 7.5), (11, 5.75)), # Broker to QoS
        
        # Devices to broker
        ((2, 3.3), (7, 7)),
        ((5, 3.3), (7.5, 7)),
        ((8, 3.3), (8, 7)),
        ((11, 3.3), (8.5, 7)),
        ((14, 3.3), (9, 7)),
        
        # Broker to apps
        ((7, 7), (2, 1.1)),
        ((7.5, 7), (6, 1.1)),
        ((8.5, 7), (10, 1.1)),
        ((9, 7), (14, 1.1))
    ]
    
    for (x1, y1), (x2, y2) in connections:
        arrow = ConnectionPatch((x1, y1), (x2, y2), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=12, fc="gray", ec="gray", alpha=0.6)
        ax.add_patch(arrow)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('mqtt_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_qos_levels_diagram():
    """Create QoS levels comparison diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    
    ax.text(8, 7.5, 'MQTT Quality of Service Levels', 
           fontsize=16, fontweight='bold', ha='center')
    
    # QoS 0
    qos0_box = FancyBboxPatch((1, 5), 4, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#ffebee', edgecolor='#c62828', linewidth=2)
    ax.add_patch(qos0_box)
    ax.text(3, 6, 'QoS 0: At Most Once', fontsize=12, fontweight='bold', ha='center')
    ax.text(3, 5.6, 'Fire and Forget', fontsize=10, ha='center')
    ax.text(3, 5.2, 'No acknowledgment', fontsize=9, ha='center', style='italic')
    
    # QoS 1
    qos1_box = FancyBboxPatch((6, 5), 4, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#e8f5e8', edgecolor='#2e7d32', linewidth=2)
    ax.add_patch(qos1_box)
    ax.text(8, 6, 'QoS 1: At Least Once', fontsize=12, fontweight='bold', ha='center')
    ax.text(8, 5.6, 'Acknowledged Delivery', fontsize=10, ha='center')
    ax.text(8, 5.2, 'Possible duplicates', fontsize=9, ha='center', style='italic')
    
    # QoS 2
    qos2_box = FancyBboxPatch((11, 5), 4, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#e1f5fe', edgecolor='#01579b', linewidth=2)
    ax.add_patch(qos2_box)
    ax.text(13, 6, 'QoS 2: Exactly Once', fontsize=12, fontweight='bold', ha='center')
    ax.text(13, 5.6, 'Assured Delivery', fontsize=10, ha='center')
    ax.text(13, 5.2, 'Four-way handshake', fontsize=9, ha='center', style='italic')
    
    # Message flow examples
    flow_y = 3.5
    
    # QoS 0 flow
    ax.text(3, flow_y + 0.5, 'Message Flow:', fontsize=10, fontweight='bold', ha='center')
    ax.arrow(1.5, flow_y, 3, 0, head_width=0.1, head_length=0.2, fc='red', ec='red')
    ax.text(3, flow_y - 0.3, 'PUBLISH →', fontsize=9, ha='center')
    
    # QoS 1 flow
    ax.text(8, flow_y + 0.5, 'Message Flow:', fontsize=10, fontweight='bold', ha='center')
    ax.arrow(6.5, flow_y + 0.1, 3, 0, head_width=0.08, head_length=0.15, fc='green', ec='green')
    ax.arrow(9.5, flow_y - 0.1, -3, 0, head_width=0.08, head_length=0.15, fc='green', ec='green')
    ax.text(8, flow_y - 0.4, 'PUBLISH → ← PUBACK', fontsize=9, ha='center')
    
    # QoS 2 flow
    ax.text(13, flow_y + 0.5, 'Message Flow:', fontsize=10, fontweight='bold', ha='center')
    ax.text(13, flow_y + 0.1, 'PUBLISH → ← PUBREC', fontsize=8, ha='center')
    ax.text(13, flow_y - 0.1, 'PUBREL → ← PUBCOMP', fontsize=8, ha='center')
    
    # Use cases
    use_cases = [
        ("Sensor readings, logs", 3, 1.5),
        ("Commands, alerts", 8, 1.5),
        ("Financial data, billing", 13, 1.5)
    ]
    
    for use_case, x, y in use_cases:
        ax.text(x, y + 0.3, 'Use Cases:', fontsize=10, fontweight='bold', ha='center')
        ax.text(x, y, use_case, fontsize=9, ha='center', style='italic')
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('qos_levels.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_iot_topology_diagram():
    """Create IoT smart home topology diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    ax.text(8, 9.5, 'MQTT-based Smart Home IoT Topology', 
           fontsize=16, fontweight='bold', ha='center')
    
    # MQTT Broker (center)
    broker_circle = Circle((8, 5), 1, facecolor='#e1f5fe', edgecolor='#01579b', linewidth=3)
    ax.add_patch(broker_circle)
    ax.text(8, 5, 'MQTT\nBroker', fontsize=11, fontweight='bold', ha='center', va='center')
    
    # IoT Devices (sensors)
    sensors = [
        ("Temp\nSensor", 3, 8, "home/living/temp", "#ffcdd2"),
        ("Motion\nDetector", 13, 8, "home/entry/motion", "#c8e6c9"),
        ("Humidity\nSensor", 2, 5, "home/bath/humid", "#ffe0b2"),
        ("Door\nSensor", 14, 5, "home/entry/door", "#f8bbd9"),
        ("Light\nSensor", 3, 2, "home/living/light", "#e0f2f1")
    ]
    
    for name, x, y, topic, color in sensors:
        sensor_box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(sensor_box)
        ax.text(x, y+0.1, name, fontsize=9, fontweight='bold', ha='center')
        ax.text(x, y-0.3, topic, fontsize=7, ha='center', style='italic')
        
        # Arrow to broker
        arrow = ConnectionPatch((x, y-0.5), (8, 5), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=50,
                               mutation_scale=12, fc="blue", ec="blue", alpha=0.6)
        ax.add_patch(arrow)
    
    # Smart Actuators
    actuators = [
        ("Smart\nLight", 13, 2, "controls/living/light", "#fff3e0"),
        ("Smart\nThermostat", 11, 7, "controls/main/thermostat", "#f3e5f5")
    ]
    
    for name, x, y, topic, color in actuators:
        actuator_box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(actuator_box)
        ax.text(x, y+0.1, name, fontsize=9, fontweight='bold', ha='center')
        ax.text(x, y-0.3, topic, fontsize=7, ha='center', style='italic')
        
        # Arrow from broker
        arrow = ConnectionPatch((8, 5), (x, y+0.5), "data", "data",
                               arrowstyle="->", shrinkA=50, shrinkB=5,
                               mutation_scale=12, fc="orange", ec="orange", alpha=0.6)
        ax.add_patch(arrow)
    
    # Applications
    apps = [
        ("Mobile\nApp", 5, 8.5, "home/+/+", "#e8f5e8"),
        ("Home\nAutomation", 11, 3, "home/+/motion", "#e1f5fe"),
        ("Cloud\nAnalytics", 5, 1.5, "home/#", "#fff3e0")
    ]
    
    for name, x, y, subscription, color in apps:
        app_box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, 
                                boxstyle="round,pad=0.1", 
                                facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(app_box)
        ax.text(x, y+0.1, name, fontsize=9, fontweight='bold', ha='center')
        ax.text(x, y-0.3, subscription, fontsize=7, ha='center', style='italic')
        
        # Bidirectional arrow
        arrow1 = ConnectionPatch((x, y+0.5), (8, 5), "data", "data",
                                arrowstyle="->", shrinkA=5, shrinkB=50,
                                mutation_scale=12, fc="green", ec="green", alpha=0.6)
        ax.add_patch(arrow1)
        
        arrow2 = ConnectionPatch((8, 5), (x, y-0.5), "data", "data",
                                arrowstyle="->", shrinkA=50, shrinkB=5,
                                mutation_scale=12, fc="purple", ec="purple", alpha=0.6)
        ax.add_patch(arrow2)
    
    # Legend
    legend_box = FancyBboxPatch((0.5, 0.2), 6, 1.2, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#f5f5f5', edgecolor='gray', linewidth=1)
    ax.add_patch(legend_box)
    
    ax.text(3.5, 1.1, 'Message Flow Legend', fontsize=10, fontweight='bold', ha='center')
    
    legend_items = [
        ("→ Sensor Data (Publish)", "blue", 1, 0.7),
        ("→ Control Commands", "orange", 1, 0.5),
        ("→ App Subscriptions", "green", 4, 0.7),
        ("→ App Commands", "purple", 4, 0.5)
    ]
    
    for text, color, x, y in legend_items:
        ax.text(x, y, text, fontsize=8, ha='left', color=color)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('iot_topology.png', dpi=300, bbox_inches='tight')
    plt.close()

def render_all_diagrams():
    """Render all MQTT diagrams"""
    print("🎨 Rendering MQTT diagrams...")
    
    diagrams = [
        ("MQTT Architecture", create_mqtt_architecture_diagram),
        ("QoS Levels", create_qos_levels_diagram),
        ("IoT Topology", create_iot_topology_diagram)
    ]
    
    for name, func in diagrams:
        print(f"  📊 Generating {name}...")
        func()
        print(f"  ✅ {name} completed")
    
    print("🎨 All MQTT diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
