#!/usr/bin/env python3
"""
Prometheus Metrics Exporter Implementation
Demonstrates metrics exposition format and HTTP/1.1 scraping
"""

import time
import threading
import random
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class MetricType(Enum):
    """Prometheus metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class MetricSample:
    """Individual metric sample"""
    name: str
    labels: Dict[str, str]
    value: float
    timestamp: Optional[float] = None

@dataclass
class Metric:
    """Prometheus metric definition"""
    name: str
    help_text: str
    metric_type: MetricType
    samples: List[MetricSample] = field(default_factory=list)

class MetricsRegistry:
    """
    Metrics registry for collecting and exposing metrics
    """
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, Dict[str, Any]] = {}
        
        # Register default metrics
        self._register_default_metrics()
        
        print("[Metrics Registry] Initialized")
    
    def _register_default_metrics(self):
        """Register default application metrics"""
        # HTTP request metrics
        self.register_counter(
            "http_requests_total",
            "Total number of HTTP requests",
            ["method", "status", "endpoint"]
        )
        
        self.register_histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # Application metrics
        self.register_gauge(
            "memory_usage_bytes",
            "Current memory usage in bytes",
            ["instance"]
        )
        
        self.register_gauge(
            "active_connections",
            "Number of active connections",
            ["service"]
        )
    
    def register_counter(self, name: str, help_text: str, labels: List[str] = None):
        """Register a counter metric"""
        metric = Metric(name, help_text, MetricType.COUNTER)
        self.metrics[name] = metric
        print(f"[Registry] Registered counter: {name}")
    
    def register_gauge(self, name: str, help_text: str, labels: List[str] = None):
        """Register a gauge metric"""
        metric = Metric(name, help_text, MetricType.GAUGE)
        self.metrics[name] = metric
        print(f"[Registry] Registered gauge: {name}")
    
    def register_histogram(self, name: str, help_text: str, labels: List[str] = None,
                          buckets: List[float] = None):
        """Register a histogram metric"""
        if buckets is None:
            buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        
        metric = Metric(name, help_text, MetricType.HISTOGRAM)
        self.metrics[name] = metric
        
        # Initialize histogram data structure
        self.histograms[name] = {
            "buckets": {str(bucket): 0 for bucket in buckets + ["+Inf"]},
            "sum": 0.0,
            "count": 0
        }
        
        print(f"[Registry] Registered histogram: {name}")
    
    def increment_counter(self, name: str, labels: Dict[str, str] = None, value: float = 1.0):
        """Increment counter metric"""
        if labels is None:
            labels = {}
        
        key = f"{name}:{json.dumps(labels, sort_keys=True)}"
        self.counters[key] = self.counters.get(key, 0) + value
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set gauge metric value"""
        if labels is None:
            labels = {}
        
        key = f"{name}:{json.dumps(labels, sort_keys=True)}"
        self.gauges[key] = value
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Observe value in histogram"""
        if name not in self.histograms:
            return
        
        if labels is None:
            labels = {}
        
        key = f"{name}:{json.dumps(labels, sort_keys=True)}"
        
        if key not in self.histograms:
            # Copy structure from base histogram
            self.histograms[key] = {
                "buckets": self.histograms[name]["buckets"].copy(),
                "sum": 0.0,
                "count": 0
            }
        
        hist = self.histograms[key]
        hist["sum"] += value
        hist["count"] += 1
        
        # Update buckets
        for bucket_str in hist["buckets"]:
            if bucket_str == "+Inf":
                hist["buckets"][bucket_str] += 1
            elif value <= float(bucket_str):
                hist["buckets"][bucket_str] += 1
    
    def generate_exposition_format(self) -> str:
        """Generate Prometheus exposition format"""
        output = []
        
        # Generate counter metrics
        for key, value in self.counters.items():
            name, labels_json = key.split(":", 1)
            labels = json.loads(labels_json)
            
            if name in self.metrics:
                metric = self.metrics[name]
                if not any(sample.name == name and sample.labels == labels for sample in metric.samples):
                    # Add help and type only once per metric
                    if not metric.samples:
                        output.append(f"# HELP {name} {metric.help_text}")
                        output.append(f"# TYPE {name} {metric.metric_type.value}")
                    
                    # Format labels
                    label_str = ""
                    if labels:
                        label_pairs = [f'{k}="{v}"' for k, v in labels.items()]
                        label_str = "{" + ",".join(label_pairs) + "}"
                    
                    output.append(f"{name}{label_str} {value}")
        
        # Generate gauge metrics
        for key, value in self.gauges.items():
            name, labels_json = key.split(":", 1)
            labels = json.loads(labels_json)
            
            if name in self.metrics:
                metric = self.metrics[name]
                if not any(sample.name == name and sample.labels == labels for sample in metric.samples):
                    # Add help and type only once per metric
                    if not metric.samples:
                        output.append(f"# HELP {name} {metric.help_text}")
                        output.append(f"# TYPE {name} {metric.metric_type.value}")
                    
                    # Format labels
                    label_str = ""
                    if labels:
                        label_pairs = [f'{k}="{v}"' for k, v in labels.items()]
                        label_str = "{" + ",".join(label_pairs) + "}"
                    
                    output.append(f"{name}{label_str} {value}")
        
        # Generate histogram metrics
        for key, hist_data in self.histograms.items():
            if ":" in key:
                name, labels_json = key.split(":", 1)
                labels = json.loads(labels_json)
            else:
                name = key
                labels = {}
                continue  # Skip base histogram definitions
            
            if name in self.metrics:
                metric = self.metrics[name]
                
                # Add help and type only once per metric
                base_key = f"{name}:{{}}"
                if base_key not in [k for k in self.histograms.keys() if ":" in k]:
                    output.append(f"# HELP {name} {metric.help_text}")
                    output.append(f"# TYPE {name} {metric.metric_type.value}")
                
                # Format labels
                label_str = ""
                if labels:
                    label_pairs = [f'{k}="{v}"' for k, v in labels.items()]
                    label_str = "{" + ",".join(label_pairs) + "}"
                
                # Bucket metrics
                for bucket, count in hist_data["buckets"].items():
                    bucket_labels = labels.copy()
                    bucket_labels["le"] = bucket
                    bucket_label_pairs = [f'{k}="{v}"' for k, v in bucket_labels.items()]
                    bucket_label_str = "{" + ",".join(bucket_label_pairs) + "}"
                    output.append(f"{name}_bucket{bucket_label_str} {count}")
                
                # Sum and count
                output.append(f"{name}_sum{label_str} {hist_data['sum']}")
                output.append(f"{name}_count{label_str} {hist_data['count']}")
        
        return "\n".join(output) + "\n"

class MetricsHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for metrics endpoint"""
    
    def __init__(self, registry: MetricsRegistry, *args, **kwargs):
        self.registry = registry
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/metrics":
            self.serve_metrics()
        elif self.path == "/health":
            self.serve_health()
        else:
            self.send_error(404, "Not Found")
    
    def serve_metrics(self):
        """Serve metrics in Prometheus format"""
        try:
            metrics_data = self.registry.generate_exposition_format()
            
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(metrics_data)))
            self.end_headers()
            
            self.wfile.write(metrics_data.encode('utf-8'))
            
            print(f"[HTTP] Served metrics to {self.client_address[0]}")
            
        except Exception as e:
            print(f"[HTTP] Error serving metrics: {e}")
            self.send_error(500, "Internal Server Error")
    
    def serve_health(self):
        """Serve health check"""
        health_data = json.dumps({"status": "healthy", "timestamp": time.time()})
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(health_data)))
        self.end_headers()
        
        self.wfile.write(health_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

class MetricsExporter:
    """
    Prometheus metrics exporter
    Exposes metrics via HTTP/1.1 endpoint
    """
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.registry = MetricsRegistry()
        self.server = None
        self.running = False
        
        print(f"[Metrics Exporter] Initialized on port {port}")
    
    def start_server(self):
        """Start HTTP server for metrics exposition"""
        def handler(*args, **kwargs):
            return MetricsHTTPHandler(self.registry, *args, **kwargs)
        
        self.server = HTTPServer(("", self.port), handler)
        self.running = True
        
        def serve_forever():
            print(f"[Metrics Exporter] Server started on port {self.port}")
            self.server.serve_forever()
        
        server_thread = threading.Thread(target=serve_forever)
        server_thread.daemon = True
        server_thread.start()
    
    def stop_server(self):
        """Stop HTTP server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            print("[Metrics Exporter] Server stopped")
    
    def get_registry(self) -> MetricsRegistry:
        """Get metrics registry"""
        return self.registry

class ApplicationSimulator:
    """
    Simulates application generating metrics
    """
    
    def __init__(self, exporter: MetricsExporter):
        self.exporter = exporter
        self.registry = exporter.get_registry()
        self.running = False
        
        print("[App Simulator] Initialized")
    
    def start_simulation(self):
        """Start generating simulated metrics"""
        self.running = True
        
        def simulate_traffic():
            methods = ["GET", "POST", "PUT", "DELETE"]
            endpoints = ["/api/users", "/api/orders", "/api/products", "/health"]
            statuses = ["200", "201", "400", "404", "500"]
            
            while self.running:
                # Simulate HTTP requests
                method = random.choice(methods)
                endpoint = random.choice(endpoints)
                status = random.choice(statuses)
                
                # Weight status codes realistically
                if random.random() < 0.8:
                    status = "200"
                elif random.random() < 0.9:
                    status = "201"
                
                # Increment request counter
                self.registry.increment_counter(
                    "http_requests_total",
                    {"method": method, "status": status, "endpoint": endpoint}
                )
                
                # Observe request duration
                duration = random.uniform(0.001, 2.0)
                if status in ["500", "404"]:
                    duration = random.uniform(0.1, 5.0)  # Errors take longer
                
                self.registry.observe_histogram(
                    "http_request_duration_seconds",
                    duration,
                    {"method": method, "endpoint": endpoint}
                )
                
                # Update gauge metrics
                memory_usage = random.uniform(100_000_000, 500_000_000)  # 100-500MB
                self.registry.set_gauge(
                    "memory_usage_bytes",
                    memory_usage,
                    {"instance": "web-server-1"}
                )
                
                active_conns = random.randint(10, 100)
                self.registry.set_gauge(
                    "active_connections",
                    active_conns,
                    {"service": "web"}
                )
                
                time.sleep(random.uniform(0.1, 1.0))
        
        sim_thread = threading.Thread(target=simulate_traffic)
        sim_thread.daemon = True
        sim_thread.start()
        
        print("[App Simulator] Started generating metrics")
    
    def stop_simulation(self):
        """Stop generating metrics"""
        self.running = False
        print("[App Simulator] Stopped generating metrics")

def demonstrate_prometheus_exporter():
    """Demonstrate Prometheus metrics exporter"""
    print("=== Prometheus Metrics Exporter Demo ===")
    
    # Initialize exporter
    exporter = MetricsExporter(port=8080)
    
    # Start HTTP server
    exporter.start_server()
    time.sleep(1)
    
    # Start application simulation
    simulator = ApplicationSimulator(exporter)
    simulator.start_simulation()
    
    print("\n1. Generating metrics...")
    print("   HTTP server running on http://localhost:8080/metrics")
    print("   Health check available at http://localhost:8080/health")
    
    # Let it run for a while
    time.sleep(5)
    
    # Show sample metrics
    print("\n2. Sample metrics output:")
    registry = exporter.get_registry()
    metrics_output = registry.generate_exposition_format()
    
    # Show first 20 lines
    lines = metrics_output.split('\n')[:20]
    for line in lines:
        if line.strip():
            print(f"   {line}")
    
    print(f"   ... ({len(metrics_output.split())} total lines)")
    
    print("\n3. Metrics can be scraped by Prometheus with configuration:")
    print("   scrape_configs:")
    print("   - job_name: 'demo-app'")
    print("     static_configs:")
    print("     - targets: ['localhost:8080']")
    print("     scrape_interval: 15s")
    print("     metrics_path: /metrics")
    
    # Cleanup
    print("\n4. Cleaning up...")
    simulator.stop_simulation()
    exporter.stop_server()
    
    print("\n=== Prometheus Exporter Demo Complete ===")

if __name__ == "__main__":
    demonstrate_prometheus_exporter()
