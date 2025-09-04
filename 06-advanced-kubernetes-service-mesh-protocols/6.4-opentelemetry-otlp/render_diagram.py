#!/usr/bin/env python3
"""
OpenTelemetry OTLP Diagram Renderer
Generates visual diagrams for OTLP architecture and data flow
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle, Rectangle, Arrow
import numpy as np
import matplotlib.gridspec as gridspec

def render_otlp_architecture():
    """Render OTLP architecture and data flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Colors
    app_color = '#E3F2FD'
    transport_color = '#F3E5F5'
    collector_color = '#E8F5E8'
    backend_color = '#FFF3E0'
    data_color = '#FFEBEE'
    
    # Title
    ax.text(8, 11.5, 'OpenTelemetry Protocol (OTLP) Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Application Layer
    app_box = FancyBboxPatch((1, 9), 3, 2, 
                            boxstyle="round,pad=0.1", 
                            facecolor=app_color, 
                            edgecolor='black', linewidth=2)
    ax.add_patch(app_box)
    ax.text(2.5, 10.5, 'Application Services', fontsize=12, fontweight='bold', ha='center')
    
    # Application components
    apps = [
        ('Trading API\nAuto-Instrumentation', 1.5, 9.7),
        ('Risk Engine\nManual Instrumentation', 3.5, 9.7),
        ('OTel SDK', 2.5, 9.3)
    ]
    
    for name, x, y in apps:
        app_comp = FancyBboxPatch((x-0.4, y-0.2), 0.8, 0.4, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor='white', 
                                 edgecolor='blue', linewidth=1)
        ax.add_patch(app_comp)
        ax.text(x, y, name, fontsize=8, ha='center', fontweight='bold')
    
    # OTLP Transport Layer
    transport_box = FancyBboxPatch((5.5, 9), 5, 2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=transport_color, 
                                  edgecolor='black', linewidth=2)
    ax.add_patch(transport_box)
    ax.text(8, 10.5, 'OTLP Transport Layer', fontsize=12, fontweight='bold', ha='center')
    
    # Transport components
    transports = [
        ('gRPC\nBinary Protocol', 6.5, 9.7),
        ('HTTP/JSON\nText Protocol', 8, 9.7),
        ('Compression\ngzip/zstd', 9.5, 9.7),
        ('Authentication\nAPI Keys/mTLS', 8, 9.3)
    ]
    
    for name, x, y in transports:
        transport_comp = FancyBboxPatch((x-0.4, y-0.2), 0.8, 0.4, 
                                       boxstyle="round,pad=0.05", 
                                       facecolor='white', 
                                       edgecolor='purple', linewidth=1)
        ax.add_patch(transport_comp)
        ax.text(x, y, name, fontsize=8, ha='center', fontweight='bold')
    
    # OpenTelemetry Collector
    collector_box = FancyBboxPatch((12, 9), 3, 2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=collector_color, 
                                  edgecolor='black', linewidth=2)
    ax.add_patch(collector_box)
    ax.text(13.5, 10.5, 'OTel Collector', fontsize=12, fontweight='bold', ha='center')
    
    # Collector components
    collectors = [
        ('OTLP Receivers\n:4317/:4318', 12.5, 9.7),
        ('Processors\nPipeline', 14.5, 9.7),
        ('Exporters\nBackends', 13.5, 9.3)
    ]
    
    for name, x, y in collectors:
        collector_comp = FancyBboxPatch((x-0.4, y-0.2), 0.8, 0.4, 
                                       boxstyle="round,pad=0.05", 
                                       facecolor='white', 
                                       edgecolor='green', linewidth=1)
        ax.add_patch(collector_comp)
        ax.text(x, y, name, fontsize=8, ha='center', fontweight='bold')
    
    # Data Types
    data_box = FancyBboxPatch((1, 6.5), 14, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor=data_color, 
                             edgecolor='black', linewidth=1)
    ax.add_patch(data_box)
    ax.text(8, 7.7, 'OTLP Data Types', fontsize=12, fontweight='bold', ha='center')
    
    # Data type components
    data_types = [
        ('Traces\nSpans & Context', 3, 7.2),
        ('Metrics\nCounters/Gauges', 6, 7.2),
        ('Logs\nStructured Events', 9, 7.2),
        ('Resource Attributes\nService Metadata', 12, 7.2)
    ]
    
    for name, x, y in data_types:
        data_comp = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor='white', 
                                  edgecolor='red', linewidth=1)
        ax.add_patch(data_comp)
        ax.text(x, y, name, fontsize=9, ha='center', fontweight='bold')
    
    # Processing Pipeline
    pipeline_box = FancyBboxPatch((1, 4.5), 14, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#F1F8E9', 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(pipeline_box)
    ax.text(8, 5.7, 'Collector Processing Pipeline', fontsize=12, fontweight='bold', ha='center')
    
    # Pipeline stages
    pipeline_stages = [
        ('Receive\nOTLP Data', 2.5, 5.2),
        ('Batch\nProcessor', 4.5, 5.2),
        ('Filter\nProcessor', 6.5, 5.2),
        ('Attributes\nProcessor', 8.5, 5.2),
        ('Sampling\nProcessor', 10.5, 5.2),
        ('Export\nBackends', 12.5, 5.2)
    ]
    
    for i, (name, x, y) in enumerate(pipeline_stages):
        stage_color = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#607D8B'][i]
        stage_comp = FancyBboxPatch((x-0.6, y-0.3), 1.2, 0.6, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor=stage_color, 
                                   edgecolor='black', linewidth=1, alpha=0.8)
        ax.add_patch(stage_comp)
        ax.text(x, y, name, fontsize=8, ha='center', fontweight='bold', color='white')
        
        # Add arrows between stages
        if i < len(pipeline_stages) - 1:
            next_x = pipeline_stages[i + 1][1]
            ax.arrow(x + 0.6, y, next_x - x - 1.2, 0, 
                    head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Observability Backends
    backend_box = FancyBboxPatch((1, 2.5), 14, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor=backend_color, 
                                edgecolor='black', linewidth=1)
    ax.add_patch(backend_box)
    ax.text(8, 3.7, 'Observability Backends', fontsize=12, fontweight='bold', ha='center')
    
    # Backend systems
    backends = [
        ('Jaeger\nTraces', 3, 3.2),
        ('Prometheus\nMetrics', 6, 3.2),
        ('Loki\nLogs', 9, 3.2),
        ('Vendor SaaS\nDataDog/NewRelic', 12, 3.2)
    ]
    
    for name, x, y in backends:
        backend_comp = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, 
                                     boxstyle="round,pad=0.05", 
                                     facecolor='white', 
                                     edgecolor='orange', linewidth=1)
        ax.add_patch(backend_comp)
        ax.text(x, y, name, fontsize=9, ha='center', fontweight='bold')
    
    # Connection arrows
    # App to Transport
    ax.arrow(4, 10, 1.3, 0, head_width=0.1, head_length=0.1, fc='blue', ec='blue', lw=2)
    
    # Transport to Collector
    ax.arrow(10.7, 10, 1.1, 0, head_width=0.1, head_length=0.1, fc='purple', ec='purple', lw=2)
    
    # Collector to Pipeline
    ax.arrow(13.5, 8.8, 0, -2.5, head_width=0.1, head_length=0.1, fc='green', ec='green', lw=2)
    
    # Pipeline to Backends
    ax.arrow(8, 4.3, 0, -0.5, head_width=0.1, head_length=0.1, fc='orange', ec='orange', lw=2)
    
    # Performance metrics
    perf_box = FancyBboxPatch((1, 0.5), 14, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#E8EAF6', 
                             edgecolor='black', linewidth=1)
    ax.add_patch(perf_box)
    ax.text(8, 1.7, 'OTLP Performance Characteristics', fontsize=12, fontweight='bold', ha='center')
    
    performance_metrics = [
        '• Binary Protocol: 60-80% smaller than JSON',
        '• Throughput: 100,000+ spans/second per collector',
        '• Latency: Sub-millisecond serialization overhead',
        '• Compression: 70-90% size reduction with gzip/zstd',
        '• Batching: Configurable batch sizes for efficiency',
        '• Multiplexing: HTTP/2 concurrent streams support'
    ]
    
    for i, metric in enumerate(performance_metrics):
        col = i % 2
        row = i // 2
        x = 3 + col * 8
        y = 1.4 - row * 0.2
        ax.text(x, y, metric, fontsize=9, ha='left', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('otlp_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated otlp_architecture.png")

def render_otlp_data_model():
    """Render OTLP data model and protocol structure"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'OTLP Data Model and Protocol Structure', 
            fontsize=14, fontweight='bold', ha='center')
    
    # Resource layer
    resource_box = FancyBboxPatch((1, 7.5), 12, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#E3F2FD', 
                                 edgecolor='black', linewidth=2)
    ax.add_patch(resource_box)
    ax.text(7, 8.7, 'Resource Attributes (Service Identity)', fontsize=12, fontweight='bold', ha='center')
    
    resource_attrs = [
        'service.name: "trading-api"',
        'service.version: "1.2.3"',
        'host.name: "k8s-node-1"',
        'k8s.namespace: "trading"',
        'k8s.pod.name: "trading-api-7d8f"',
        'deployment.environment: "prod"'
    ]
    
    for i, attr in enumerate(resource_attrs):
        col = i % 3
        row = i // 3
        x = 2.5 + col * 3.5
        y = 8.4 - row * 0.2
        ax.text(x, y, attr, fontsize=8, ha='left', fontweight='bold')
    
    # Instrumentation Scope
    scope_box = FancyBboxPatch((1, 6), 12, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor='#F3E5F5', 
                              edgecolor='black', linewidth=1)
    ax.add_patch(scope_box)
    ax.text(7, 6.7, 'Instrumentation Scope', fontsize=11, fontweight='bold', ha='center')
    ax.text(7, 6.3, 'name: "opentelemetry.instrumentation.requests" | version: "1.0.0" | schema_url: "https://opentelemetry.io/schemas/1.21.0"', 
           fontsize=9, ha='center')
    
    # Telemetry data types
    # Traces
    traces_box = FancyBboxPatch((1, 4), 4, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#E8F5E8', 
                               edgecolor='black', linewidth=1)
    ax.add_patch(traces_box)
    ax.text(3, 5.2, 'Traces (Spans)', fontsize=11, fontweight='bold', ha='center')
    
    trace_fields = [
        'trace_id: 32 bytes',
        'span_id: 8 bytes',
        'parent_span_id: 8 bytes',
        'name: "POST /api/orders"',
        'kind: SERVER',
        'start_time_unix_nano',
        'end_time_unix_nano',
        'attributes: [key-value pairs]',
        'status: OK/ERROR'
    ]
    
    for i, field in enumerate(trace_fields):
        ax.text(3, 4.9 - i * 0.1, field, fontsize=7, ha='center')
    
    # Metrics
    metrics_box = FancyBboxPatch((5.5, 4), 4, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#FFF3E0', 
                                edgecolor='black', linewidth=1)
    ax.add_patch(metrics_box)
    ax.text(7.5, 5.2, 'Metrics', fontsize=11, fontweight='bold', ha='center')
    
    metric_fields = [
        'name: "requests_total"',
        'description: "Total requests"',
        'unit: "1"',
        'data_type: Counter/Gauge/Histogram',
        'data_points: [timestamp, value, attrs]',
        'aggregation_temporality',
        'exemplars: [trace links]'
    ]
    
    for i, field in enumerate(metric_fields):
        ax.text(7.5, 4.9 - i * 0.1, field, fontsize=7, ha='center')
    
    # Logs
    logs_box = FancyBboxPatch((10, 4), 3, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor='#FFEBEE', 
                             edgecolor='black', linewidth=1)
    ax.add_patch(logs_box)
    ax.text(11.5, 5.2, 'Logs', fontsize=11, fontweight='bold', ha='center')
    
    log_fields = [
        'timestamp_unix_nano',
        'severity_number: 1-24',
        'severity_text: "INFO"',
        'body: "Request processed"',
        'attributes: [key-value]',
        'trace_id: correlation',
        'span_id: correlation'
    ]
    
    for i, field in enumerate(log_fields):
        ax.text(11.5, 4.9 - i * 0.1, field, fontsize=7, ha='center')
    
    # Protocol encoding
    encoding_box = FancyBboxPatch((1, 2), 12, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#F1F8E9', 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(encoding_box)
    ax.text(7, 3.2, 'Protocol Encoding Options', fontsize=12, fontweight='bold', ha='center')
    
    # gRPC encoding
    grpc_box = FancyBboxPatch((2, 2.3), 4, 0.8, 
                             boxstyle="round,pad=0.05", 
                             facecolor='#4CAF50', 
                             edgecolor='black', linewidth=1, alpha=0.8)
    ax.add_patch(grpc_box)
    ax.text(4, 2.7, 'gRPC + Protocol Buffers', fontsize=10, fontweight='bold', ha='center', color='white')
    ax.text(4, 2.5, '• Binary encoding\n• HTTP/2 transport\n• Efficient compression', 
           fontsize=8, ha='center', color='white')
    
    # HTTP encoding
    http_box = FancyBboxPatch((8, 2.3), 4, 0.8, 
                             boxstyle="round,pad=0.05", 
                             facecolor='#2196F3', 
                             edgecolor='black', linewidth=1, alpha=0.8)
    ax.add_patch(http_box)
    ax.text(10, 2.7, 'HTTP + JSON', fontsize=10, fontweight='bold', ha='center', color='white')
    ax.text(10, 2.5, '• Text encoding\n• HTTP/1.1 or HTTP/2\n• Human readable', 
           fontsize=8, ha='center', color='white')
    
    # Benefits
    benefits_box = FancyBboxPatch((1, 0.2), 12, 1.3, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#E8EAF6', 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(benefits_box)
    ax.text(7, 1.3, 'OTLP Protocol Benefits', fontsize=11, fontweight='bold', ha='center')
    
    benefits = [
        '• Vendor Neutral: No lock-in to specific observability vendors',
        '• Standardized: Consistent data model across all telemetry types',
        '• Efficient: Binary encoding reduces bandwidth and processing overhead',
        '• Extensible: Support for custom attributes and metadata',
        '• Interoperable: Works with all major observability backends',
        '• Future-Proof: Evolving standard with backward compatibility'
    ]
    
    for i, benefit in enumerate(benefits):
        col = i % 2
        row = i // 2
        x = 2 + col * 6
        y = 1.0 - row * 0.15
        ax.text(x, y, benefit, fontsize=9, ha='left', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('otlp_data_model.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated otlp_data_model.png")

def render_otlp_performance_comparison():
    """Render OTLP performance comparison with other protocols"""
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig)
    
    # Payload size comparison
    ax1 = fig.add_subplot(gs[0, 0])
    
    protocols = ['OTLP\n(gRPC)', 'OTLP\n(HTTP/JSON)', 'Jaeger\n(Thrift)', 'Zipkin\n(JSON)']
    payload_sizes = [100, 280, 150, 320]  # Relative sizes
    colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']
    
    bars = ax1.bar(protocols, payload_sizes, color=colors, alpha=0.8)
    ax1.set_ylabel('Payload Size (KB)')
    ax1.set_title('Payload Size Comparison', fontsize=12, fontweight='bold')
    
    # Add value labels
    for bar, size in zip(bars, payload_sizes):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{size}KB', ha='center', va='bottom', fontweight='bold')
    
    # Throughput comparison
    ax2 = fig.add_subplot(gs[0, 1])
    
    throughput = [120000, 80000, 90000, 60000]  # spans/second
    bars2 = ax2.bar(protocols, throughput, color=colors, alpha=0.8)
    ax2.set_ylabel('Throughput (spans/second)')
    ax2.set_title('Throughput Comparison', fontsize=12, fontweight='bold')
    
    # Add value labels
    for bar, tput in zip(bars2, throughput):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2000,
                f'{tput:,}', ha='center', va='bottom', fontweight='bold')
    
    # Latency over time
    ax3 = fig.add_subplot(gs[1, 0])
    
    time_points = np.linspace(0, 60, 100)  # 60 seconds
    otlp_grpc_latency = 2 + 0.5 * np.sin(time_points * 0.1) + np.random.normal(0, 0.2, 100)
    otlp_http_latency = 5 + 1.0 * np.sin(time_points * 0.1) + np.random.normal(0, 0.3, 100)
    jaeger_latency = 3 + 0.8 * np.sin(time_points * 0.1) + np.random.normal(0, 0.4, 100)
    zipkin_latency = 8 + 2.0 * np.sin(time_points * 0.1) + np.random.normal(0, 0.5, 100)
    
    ax3.plot(time_points, otlp_grpc_latency, label='OTLP gRPC', color='#4CAF50', linewidth=2)
    ax3.plot(time_points, otlp_http_latency, label='OTLP HTTP', color='#2196F3', linewidth=2)
    ax3.plot(time_points, jaeger_latency, label='Jaeger Thrift', color='#FF9800', linewidth=2)
    ax3.plot(time_points, zipkin_latency, label='Zipkin JSON', color='#9C27B0', linewidth=2)
    
    ax3.set_xlabel('Time (seconds)')
    ax3.set_ylabel('Latency (ms)')
    ax3.set_title('Export Latency Over Time', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Compression efficiency
    ax4 = fig.add_subplot(gs[1, 1])
    
    compression_methods = ['None', 'gzip', 'zstd', 'snappy']
    compression_ratios = [0, 0.7, 0.75, 0.6]  # Compression ratio
    compression_speeds = [100, 85, 80, 95]  # Relative speed
    
    x = np.arange(len(compression_methods))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, compression_ratios, width, label='Compression Ratio', 
                   color='#4CAF50', alpha=0.8)
    
    ax4_twin = ax4.twinx()
    bars2 = ax4_twin.bar(x + width/2, compression_speeds, width, label='Speed (relative)', 
                        color='#FF9800', alpha=0.8)
    
    ax4.set_xlabel('Compression Method')
    ax4.set_ylabel('Compression Ratio', color='#4CAF50')
    ax4_twin.set_ylabel('Speed (relative)', color='#FF9800')
    ax4.set_title('Compression Performance', fontsize=12, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(compression_methods)
    
    # Add legends
    ax4.legend(loc='upper left')
    ax4_twin.legend(loc='upper right')
    
    plt.suptitle('OTLP Performance Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('otlp_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Generated otlp_performance_comparison.png")

def render_all_diagrams():
    """Render all OTLP diagrams"""
    print("Rendering OpenTelemetry OTLP diagrams...")
    
    render_otlp_architecture()
    render_otlp_data_model()
    render_otlp_performance_comparison()
    
    print("All OpenTelemetry OTLP diagrams rendered successfully!")

if __name__ == "__main__":
    render_all_diagrams()
