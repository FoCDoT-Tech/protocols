#!/usr/bin/env python3
"""
Prometheus Architecture Diagram Renderer
Generates visual diagrams for Prometheus monitoring and metrics collection
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle
import numpy as np

def render_prometheus_architecture():
    """Render Prometheus monitoring architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Colors
    service_color = '#E8F5E8'
    prometheus_color = '#E1F5FE'
    alert_color = '#FFEBEE'
    visual_color = '#F3E5F5'
    infra_color = '#FFF3E0'
    
    # Title
    ax.text(7, 9.5, 'Prometheus Monitoring Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Application Services
    services = [
        ('Web Service\n/metrics', 1.5, 7.5),
        ('API Service\n/metrics', 3.5, 7.5),
        ('Worker Service\n/metrics', 5.5, 7.5)
    ]
    
    for name, x, y in services:
        service_box = FancyBboxPatch((x-0.7, y-0.5), 1.4, 1, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor=service_color, 
                                    edgecolor='black', linewidth=1)
        ax.add_patch(service_box)
        ax.text(x, y, name, fontsize=10, fontweight='bold', ha='center')
    
    # Infrastructure Exporters
    exporters = [
        ('Node\nExporter', 8, 7.5),
        ('kube-state\nMetrics', 9.5, 7.5),
        ('cAdvisor', 11, 7.5)
    ]
    
    for name, x, y in exporters:
        exporter_box = FancyBboxPatch((x-0.6, y-0.5), 1.2, 1, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=infra_color, 
                                     edgecolor='black', linewidth=1)
        ax.add_patch(exporter_box)
        ax.text(x, y, name, fontsize=9, fontweight='bold', ha='center')
    
    # Prometheus Server
    prometheus_box = FancyBboxPatch((2, 5), 8, 1.5, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=prometheus_color, 
                                   edgecolor='black', linewidth=2)
    ax.add_patch(prometheus_box)
    ax.text(6, 5.75, 'Prometheus Server', fontsize=14, fontweight='bold', ha='center')
    
    # Prometheus components
    components = [
        ('Service\nDiscovery', 2.8, 5.3),
        ('Scrape\nEngine', 4.2, 5.3),
        ('Storage\nEngine', 5.6, 5.3),
        ('Query\nEngine', 7, 5.3),
        ('Rule\nEngine', 8.4, 5.3)
    ]
    
    for name, x, y in components:
        comp_box = FancyBboxPatch((x-0.5, y-0.25), 1, 0.5, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor='white', 
                                 edgecolor='blue', linewidth=1)
        ax.add_patch(comp_box)
        ax.text(x, y, name, fontsize=8, ha='center')
    
    # Alertmanager
    alert_box = FancyBboxPatch((11, 5), 2.5, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor=alert_color, 
                              edgecolor='black', linewidth=1)
    ax.add_patch(alert_box)
    ax.text(12.25, 5.75, 'Alertmanager', fontsize=12, fontweight='bold', ha='center')
    ax.text(12.25, 5.35, 'Routing & Silencing', fontsize=10, ha='center')
    
    # Visualization
    visual_components = [
        ('Grafana\nDashboards', 2, 2.5),
        ('Prometheus\nUI', 4.5, 2.5)
    ]
    
    for name, x, y in visual_components:
        visual_box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=visual_color, 
                                   edgecolor='black', linewidth=1)
        ax.add_patch(visual_box)
        ax.text(x, y, name, fontsize=10, fontweight='bold', ha='center')
    
    # Notification channels
    notifications = [
        ('Slack', 11, 2.5),
        ('Email', 12.25, 2.5),
        ('PagerDuty', 13.5, 2.5)
    ]
    
    for name, x, y in notifications:
        notif_box = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#FFFDE7', 
                                  edgecolor='orange', linewidth=1)
        ax.add_patch(notif_box)
        ax.text(x, y, name, fontsize=9, ha='center')
    
    # Arrows - Scraping
    for name, x, y in services + exporters:
        ax.arrow(x, y-0.5, 0, -1, head_width=0.1, head_length=0.1, fc='blue', ec='blue')
    
    # Arrows - Alerting
    ax.arrow(10, 5.75, 0.8, 0, head_width=0.1, head_length=0.1, fc='red', ec='red')
    
    # Arrows - Notifications
    for name, x, y in notifications:
        ax.arrow(12.25, 4.5, x-12.25, y-4.5+0.3, head_width=0.1, head_length=0.1, fc='orange', ec='orange')
    
    # Arrows - Visualization
    ax.arrow(6, 5, -3.2, -2, head_width=0.1, head_length=0.1, fc='purple', ec='purple')
    ax.arrow(6, 5, -1, -2, head_width=0.1, head_length=0.1, fc='purple', ec='purple')
    
    # Add HTTP/1.1 labels
    ax.text(3.5, 6.8, 'HTTP/1.1\nGET /metrics', fontsize=8, ha='center', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
    
    ax.text(9.5, 6.8, 'HTTP/1.1\nGET /metrics', fontsize=8, ha='center',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('prometheus_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated prometheus_architecture.png")

def render_metrics_exposition_format():
    """Render metrics exposition format diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(6, 7.5, 'Prometheus Exposition Format', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Metric types
    metric_types = [
        ('Counter', 2, 6, 'Monotonic\nIncreasing', '#E8F5E8'),
        ('Gauge', 4.5, 6, 'Current\nValue', '#FFF3E0'),
        ('Histogram', 7, 6, 'Distribution\nBuckets', '#F3E5F5'),
        ('Summary', 9.5, 6, 'Quantiles\nPercentiles', '#E1F5FE')
    ]
    
    for name, x, y, desc, color in metric_types:
        type_box = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=color, 
                                 edgecolor='black', linewidth=1)
        ax.add_patch(type_box)
        ax.text(x, y + 0.2, name, fontsize=11, fontweight='bold', ha='center')
        ax.text(x, y - 0.2, desc, fontsize=9, ha='center')
    
    # Example metrics
    examples = [
        ('http_requests_total{method="GET"} 1027', 2, 4.5),
        ('memory_usage_bytes 536870912', 4.5, 4.5),
        ('http_duration_seconds_bucket{le="0.1"} 24054', 7, 4.5),
        ('rpc_duration_seconds{quantile="0.9"} 9001', 9.5, 4.5)
    ]
    
    for example, x, y in examples:
        example_box = FancyBboxPatch((x-1.2, y-0.4), 2.4, 0.8, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor='white', 
                                    edgecolor='gray', linewidth=1)
        ax.add_patch(example_box)
        ax.text(x, y, example, fontsize=8, ha='center', family='monospace')
    
    # HTTP exposition
    http_box = FancyBboxPatch((1, 2.5), 10, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#FFFDE7', 
                             edgecolor='black', linewidth=1)
    ax.add_patch(http_box)
    ax.text(6, 3.6, 'HTTP/1.1 Exposition', fontsize=12, fontweight='bold', ha='center')
    
    http_text = """GET /metrics HTTP/1.1
Content-Type: text/plain; version=0.0.4; charset=utf-8"""
    ax.text(6, 3, http_text, fontsize=10, ha='center', family='monospace')
    
    # Format structure
    ax.text(6, 1.5, 'Format Structure:', fontsize=12, fontweight='bold', ha='center')
    ax.text(6, 1.1, '# HELP metric_name Description of metric', fontsize=10, ha='center', family='monospace')
    ax.text(6, 0.8, '# TYPE metric_name counter|gauge|histogram|summary', fontsize=10, ha='center', family='monospace')
    ax.text(6, 0.5, 'metric_name{label1="value1",label2="value2"} value [timestamp]', fontsize=10, ha='center', family='monospace')
    
    plt.tight_layout()
    plt.savefig('metrics_exposition_format.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated metrics_exposition_format.png")

def render_scraping_lifecycle():
    """Render Prometheus scraping lifecycle diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(6, 7.5, 'Prometheus Scraping Lifecycle', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Lifecycle stages
    stages = [
        ('1. Service\nDiscovery', 1.5, 6, '#E1F5FE'),
        ('2. Target\nSelection', 3.5, 6, '#FFF3E0'),
        ('3. HTTP\nRequest', 5.5, 6, '#F3E5F5'),
        ('4. Parse\nMetrics', 7.5, 6, '#E8F5E8'),
        ('5. Store\nSamples', 9.5, 6, '#FFEBEE'),
        ('6. Apply\nRules', 11, 6, '#F1F8E9')
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
    
    # Details for each stage
    details = [
        ('Kubernetes API\nConsul, DNS\nStatic Config', 1.5, 4.5),
        ('Filter by\nJob Config\nRelabeling', 3.5, 4.5),
        ('GET /metrics\nTimeout: 10s\nUser-Agent', 5.5, 4.5),
        ('Exposition\nFormat\nValidation', 7.5, 4.5),
        ('Time Series\nDatabase\nCompression', 9.5, 4.5),
        ('Recording\nAlerting\nEvaluation', 11, 4.5)
    ]
    
    for detail, x, y in details:
        detail_box = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='white', 
                                   edgecolor='gray', linewidth=1)
        ax.add_patch(detail_box)
        ax.text(x, y, detail, fontsize=9, ha='center')
        
        # Arrow from stage to detail
        ax.arrow(x, 5.5, 0, -0.4, head_width=0.1, head_length=0.1, fc='gray', ec='gray')
    
    # Timing information
    ax.text(6, 2.5, 'Typical Scraping Configuration:', fontsize=12, fontweight='bold', ha='center')
    ax.text(6, 2.1, 'Scrape Interval: 15-60 seconds', fontsize=10, ha='center')
    ax.text(6, 1.8, 'Scrape Timeout: 10 seconds', fontsize=10, ha='center')
    ax.text(6, 1.5, 'Evaluation Interval: 15 seconds', fontsize=10, ha='center')
    ax.text(6, 1.2, 'Retention: 15 days (configurable)', fontsize=10, ha='center')
    
    # Error handling
    ax.text(6, 0.7, 'Error Handling: Timeout, HTTP errors, parse failures', fontsize=10, ha='center', style='italic')
    
    plt.tight_layout()
    plt.savefig('scraping_lifecycle.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated scraping_lifecycle.png")

def render_all_diagrams():
    """Render all Prometheus diagrams"""
    print("Rendering Prometheus diagrams...")
    
    render_prometheus_architecture()
    render_metrics_exposition_format()
    render_scraping_lifecycle()
    
    print("All Prometheus diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
