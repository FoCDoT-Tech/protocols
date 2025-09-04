#!/usr/bin/env python3
"""
OpenTelemetry OTLP Collector Simulator
Simulates OTLP data collection, processing, and export
"""

import asyncio
import time
import json
import random
import gzip
import zlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, AsyncIterator
from enum import Enum
import threading
from collections import defaultdict, deque
import uuid

class TelemetryType(Enum):
    TRACES = "traces"
    METRICS = "metrics"
    LOGS = "logs"

class SpanKind(Enum):
    INTERNAL = "SPAN_KIND_INTERNAL"
    SERVER = "SPAN_KIND_SERVER"
    CLIENT = "SPAN_KIND_CLIENT"
    PRODUCER = "SPAN_KIND_PRODUCER"
    CONSUMER = "SPAN_KIND_CONSUMER"

class StatusCode(Enum):
    OK = "STATUS_CODE_OK"
    ERROR = "STATUS_CODE_ERROR"

@dataclass
class ResourceAttributes:
    service_name: str
    service_version: str
    service_instance_id: str
    host_name: str
    container_id: str
    k8s_namespace: str
    k8s_pod_name: str
    environment: str

@dataclass
class InstrumentationScope:
    name: str
    version: str
    schema_url: Optional[str] = None

@dataclass
class KeyValue:
    key: str
    value: Any

@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    kind: SpanKind
    start_time_unix_nano: int
    end_time_unix_nano: int
    attributes: List[KeyValue]
    status_code: StatusCode
    status_message: Optional[str] = None

@dataclass
class MetricDataPoint:
    timestamp_unix_nano: int
    value: float
    attributes: List[KeyValue]

@dataclass
class Metric:
    name: str
    description: str
    unit: str
    data_points: List[MetricDataPoint]
    metric_type: str  # gauge, counter, histogram

@dataclass
class LogRecord:
    timestamp_unix_nano: int
    severity_number: int
    severity_text: str
    body: str
    attributes: List[KeyValue]
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

@dataclass
class TelemetryData:
    resource: ResourceAttributes
    scope: InstrumentationScope
    data_type: TelemetryType
    spans: List[Span] = None
    metrics: List[Metric] = None
    logs: List[LogRecord] = None

class OTLPProcessor:
    """Base class for OTLP processors"""
    
    def __init__(self, name: str):
        self.name = name
        self.processed_count = 0
        self.error_count = 0
    
    async def process(self, data: TelemetryData) -> TelemetryData:
        """Process telemetry data"""
        try:
            result = await self._process_impl(data)
            self.processed_count += 1
            return result
        except Exception as e:
            self.error_count += 1
            print(f"[{self.name}] Processing error: {e}")
            return data
    
    async def _process_impl(self, data: TelemetryData) -> TelemetryData:
        """Override in subclasses"""
        return data

class BatchProcessor(OTLPProcessor):
    """Batches telemetry data for efficient export"""
    
    def __init__(self, batch_size: int = 512, timeout_seconds: float = 1.0):
        super().__init__("BatchProcessor")
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
        self.batch_queue = deque()
        self.last_export = time.time()
        self._lock = threading.Lock()
    
    async def _process_impl(self, data: TelemetryData) -> TelemetryData:
        with self._lock:
            self.batch_queue.append(data)
            
            # Check if batch is ready
            if (len(self.batch_queue) >= self.batch_size or 
                time.time() - self.last_export > self.timeout_seconds):
                
                batch = list(self.batch_queue)
                self.batch_queue.clear()
                self.last_export = time.time()
                
                print(f"[{self.name}] Batched {len(batch)} telemetry items")
                return self._merge_batch(batch)
        
        return data
    
    def _merge_batch(self, batch: List[TelemetryData]) -> TelemetryData:
        """Merge multiple telemetry data items into a batch"""
        if not batch:
            return None
        
        # Use first item as template
        merged = batch[0]
        
        # Merge spans, metrics, logs from all items
        all_spans = []
        all_metrics = []
        all_logs = []
        
        for item in batch:
            if item.spans:
                all_spans.extend(item.spans)
            if item.metrics:
                all_metrics.extend(item.metrics)
            if item.logs:
                all_logs.extend(item.logs)
        
        merged.spans = all_spans if all_spans else None
        merged.metrics = all_metrics if all_metrics else None
        merged.logs = all_logs if all_logs else None
        
        return merged

class AttributesProcessor(OTLPProcessor):
    """Adds, modifies, or removes attributes"""
    
    def __init__(self, add_attributes: Dict[str, str] = None, remove_keys: List[str] = None):
        super().__init__("AttributesProcessor")
        self.add_attributes = add_attributes or {}
        self.remove_keys = remove_keys or []
    
    async def _process_impl(self, data: TelemetryData) -> TelemetryData:
        # Add attributes to resource
        for key, value in self.add_attributes.items():
            setattr(data.resource, key.replace('.', '_'), value)
        
        # Process spans
        if data.spans:
            for span in data.spans:
                self._process_attributes(span.attributes)
        
        # Process metrics
        if data.metrics:
            for metric in data.metrics:
                for data_point in metric.data_points:
                    self._process_attributes(data_point.attributes)
        
        # Process logs
        if data.logs:
            for log in data.logs:
                self._process_attributes(log.attributes)
        
        return data
    
    def _process_attributes(self, attributes: List[KeyValue]):
        """Process attribute list"""
        # Remove specified keys
        attributes[:] = [attr for attr in attributes if attr.key not in self.remove_keys]
        
        # Add new attributes
        for key, value in self.add_attributes.items():
            attributes.append(KeyValue(key=key, value=value))

class FilterProcessor(OTLPProcessor):
    """Filters telemetry data based on conditions"""
    
    def __init__(self, service_filter: List[str] = None, severity_filter: int = None):
        super().__init__("FilterProcessor")
        self.service_filter = service_filter or []
        self.severity_filter = severity_filter
    
    async def _process_impl(self, data: TelemetryData) -> TelemetryData:
        # Filter by service name
        if self.service_filter and data.resource.service_name not in self.service_filter:
            return None
        
        # Filter logs by severity
        if data.logs and self.severity_filter:
            data.logs = [log for log in data.logs if log.severity_number >= self.severity_filter]
        
        return data

class SamplingProcessor(OTLPProcessor):
    """Implements probabilistic sampling"""
    
    def __init__(self, sampling_rate: float = 0.1):
        super().__init__("SamplingProcessor")
        self.sampling_rate = sampling_rate
        self.sampled_count = 0
        self.dropped_count = 0
    
    async def _process_impl(self, data: TelemetryData) -> TelemetryData:
        if random.random() > self.sampling_rate:
            self.dropped_count += 1
            return None
        
        self.sampled_count += 1
        return data

class OTLPExporter:
    """Base class for OTLP exporters"""
    
    def __init__(self, name: str, endpoint: str):
        self.name = name
        self.endpoint = endpoint
        self.exported_count = 0
        self.error_count = 0
    
    async def export(self, data: TelemetryData) -> bool:
        """Export telemetry data"""
        try:
            success = await self._export_impl(data)
            if success:
                self.exported_count += 1
            else:
                self.error_count += 1
            return success
        except Exception as e:
            self.error_count += 1
            print(f"[{self.name}] Export error: {e}")
            return False
    
    async def _export_impl(self, data: TelemetryData) -> bool:
        """Override in subclasses"""
        return True

class JaegerExporter(OTLPExporter):
    """Exports traces to Jaeger"""
    
    def __init__(self, endpoint: str = "jaeger-collector:14250"):
        super().__init__("JaegerExporter", endpoint)
    
    async def _export_impl(self, data: TelemetryData) -> bool:
        if not data.spans:
            return True
        
        # Simulate Jaeger export
        await asyncio.sleep(0.01)  # Network latency
        
        span_count = len(data.spans)
        print(f"[{self.name}] Exported {span_count} spans to {self.endpoint}")
        return True

class PrometheusExporter(OTLPExporter):
    """Exports metrics to Prometheus"""
    
    def __init__(self, endpoint: str = "prometheus:9090"):
        super().__init__("PrometheusExporter", endpoint)
    
    async def _export_impl(self, data: TelemetryData) -> bool:
        if not data.metrics:
            return True
        
        # Simulate Prometheus export
        await asyncio.sleep(0.005)  # Network latency
        
        metric_count = len(data.metrics)
        print(f"[{self.name}] Exported {metric_count} metrics to {self.endpoint}")
        return True

class LokiExporter(OTLPExporter):
    """Exports logs to Grafana Loki"""
    
    def __init__(self, endpoint: str = "loki:3100"):
        super().__init__("LokiExporter", endpoint)
    
    async def _export_impl(self, data: TelemetryData) -> bool:
        if not data.logs:
            return True
        
        # Simulate Loki export
        await asyncio.sleep(0.008)  # Network latency
        
        log_count = len(data.logs)
        print(f"[{self.name}] Exported {log_count} logs to {self.endpoint}")
        return True

class OTLPCollector:
    """OpenTelemetry Collector simulation"""
    
    def __init__(self, collector_id: str):
        self.collector_id = collector_id
        self.processors: List[OTLPProcessor] = []
        self.exporters: List[OTLPExporter] = []
        self.stats = {
            'received_count': 0,
            'processed_count': 0,
            'exported_count': 0,
            'error_count': 0,
            'bytes_received': 0,
            'compression_ratio': 0.0
        }
        self._lock = threading.Lock()
    
    def add_processor(self, processor: OTLPProcessor):
        """Add processor to pipeline"""
        self.processors.append(processor)
        print(f"[{self.collector_id}] Added processor: {processor.name}")
    
    def add_exporter(self, exporter: OTLPExporter):
        """Add exporter to pipeline"""
        self.exporters.append(exporter)
        print(f"[{self.collector_id}] Added exporter: {exporter.name}")
    
    async def receive_otlp_data(self, data: TelemetryData, compressed: bool = False) -> bool:
        """Receive and process OTLP data"""
        with self._lock:
            self.stats['received_count'] += 1
            
            # Simulate compression
            if compressed:
                original_size = self._estimate_size(data)
                compressed_size = original_size * 0.3  # 70% compression
                self.stats['bytes_received'] += compressed_size
                self.stats['compression_ratio'] = 0.7
            else:
                self.stats['bytes_received'] += self._estimate_size(data)
        
        try:
            # Process through pipeline
            processed_data = data
            for processor in self.processors:
                if processed_data is None:
                    break
                processed_data = await processor.process(processed_data)
            
            if processed_data is None:
                return True  # Filtered out
            
            # Export to all configured exporters
            export_tasks = []
            for exporter in self.exporters:
                task = asyncio.create_task(exporter.export(processed_data))
                export_tasks.append(task)
            
            results = await asyncio.gather(*export_tasks, return_exceptions=True)
            
            success_count = sum(1 for result in results if result is True)
            
            with self._lock:
                self.stats['processed_count'] += 1
                self.stats['exported_count'] += success_count
                if success_count < len(self.exporters):
                    self.stats['error_count'] += 1
            
            return success_count > 0
            
        except Exception as e:
            with self._lock:
                self.stats['error_count'] += 1
            print(f"[{self.collector_id}] Processing error: {e}")
            return False
    
    def _estimate_size(self, data: TelemetryData) -> int:
        """Estimate serialized size of telemetry data"""
        # Rough estimation based on data content
        size = 100  # Base overhead
        
        if data.spans:
            size += len(data.spans) * 200  # ~200 bytes per span
        if data.metrics:
            size += len(data.metrics) * 100  # ~100 bytes per metric
        if data.logs:
            size += len(data.logs) * 150  # ~150 bytes per log
        
        return size
    
    def get_stats(self) -> Dict:
        """Get collector statistics"""
        with self._lock:
            stats = self.stats.copy()
            
            # Add processor stats
            for processor in self.processors:
                stats[f'{processor.name}_processed'] = processor.processed_count
                stats[f'{processor.name}_errors'] = processor.error_count
            
            # Add exporter stats
            for exporter in self.exporters:
                stats[f'{exporter.name}_exported'] = exporter.exported_count
                stats[f'{exporter.name}_errors'] = exporter.error_count
            
            return stats

class TelemetryGenerator:
    """Generates sample telemetry data for testing"""
    
    def __init__(self):
        self.services = [
            "trading-service",
            "risk-engine", 
            "order-matching",
            "settlement-service",
            "auth-service"
        ]
        self.trace_id_counter = 0
        self.span_id_counter = 0
    
    def generate_resource(self, service_name: str) -> ResourceAttributes:
        """Generate resource attributes"""
        return ResourceAttributes(
            service_name=service_name,
            service_version="1.2.3",
            service_instance_id=str(uuid.uuid4()),
            host_name=f"host-{random.randint(1, 10)}",
            container_id=f"container-{uuid.uuid4().hex[:12]}",
            k8s_namespace="trading-platform",
            k8s_pod_name=f"{service_name}-{random.randint(1000, 9999)}",
            environment="production"
        )
    
    def generate_trace_data(self, service_name: str) -> TelemetryData:
        """Generate trace data"""
        resource = self.generate_resource(service_name)
        scope = InstrumentationScope(name="opentelemetry.instrumentation.requests", version="1.0.0")
        
        trace_id = f"{self.trace_id_counter:032x}"
        self.trace_id_counter += 1
        
        spans = []
        for i in range(random.randint(1, 5)):
            span_id = f"{self.span_id_counter:016x}"
            self.span_id_counter += 1
            
            start_time = time.time_ns() - random.randint(1000000, 10000000)  # 1-10ms ago
            duration = random.randint(100000, 5000000)  # 0.1-5ms duration
            
            span = Span(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=None if i == 0 else f"{self.span_id_counter-2:016x}",
                name=f"process_{random.choice(['order', 'trade', 'settlement', 'risk_check'])}",
                kind=random.choice(list(SpanKind)),
                start_time_unix_nano=start_time,
                end_time_unix_nano=start_time + duration,
                attributes=[
                    KeyValue(key="http.method", value="POST"),
                    KeyValue(key="http.status_code", value=random.choice([200, 201, 400, 500])),
                    KeyValue(key="trade.amount", value=random.uniform(100, 10000)),
                    KeyValue(key="trade.currency", value=random.choice(["USD", "EUR", "GBP"]))
                ],
                status_code=random.choice(list(StatusCode))
            )
            spans.append(span)
        
        return TelemetryData(
            resource=resource,
            scope=scope,
            data_type=TelemetryType.TRACES,
            spans=spans
        )
    
    def generate_metrics_data(self, service_name: str) -> TelemetryData:
        """Generate metrics data"""
        resource = self.generate_resource(service_name)
        scope = InstrumentationScope(name="opentelemetry.instrumentation.system", version="1.0.0")
        
        metrics = []
        
        # Counter metric
        counter_metric = Metric(
            name="requests_total",
            description="Total number of requests",
            unit="1",
            metric_type="counter",
            data_points=[
                MetricDataPoint(
                    timestamp_unix_nano=time.time_ns(),
                    value=random.randint(100, 1000),
                    attributes=[
                        KeyValue(key="method", value="POST"),
                        KeyValue(key="status", value="200")
                    ]
                )
            ]
        )
        metrics.append(counter_metric)
        
        # Gauge metric
        gauge_metric = Metric(
            name="cpu_usage_percent",
            description="CPU usage percentage",
            unit="%",
            metric_type="gauge",
            data_points=[
                MetricDataPoint(
                    timestamp_unix_nano=time.time_ns(),
                    value=random.uniform(10, 90),
                    attributes=[
                        KeyValue(key="core", value=f"cpu{random.randint(0, 7)}")
                    ]
                )
            ]
        )
        metrics.append(gauge_metric)
        
        return TelemetryData(
            resource=resource,
            scope=scope,
            data_type=TelemetryType.METRICS,
            metrics=metrics
        )
    
    def generate_logs_data(self, service_name: str) -> TelemetryData:
        """Generate log data"""
        resource = self.generate_resource(service_name)
        scope = InstrumentationScope(name="opentelemetry.instrumentation.logging", version="1.0.0")
        
        log_messages = [
            "Processing trade order",
            "Risk check completed",
            "Settlement initiated",
            "Authentication successful",
            "Database connection established",
            "Cache miss for key",
            "Request validation failed",
            "Circuit breaker opened"
        ]
        
        logs = []
        for _ in range(random.randint(1, 3)):
            severity = random.choice([1, 5, 9, 13, 17])  # DEBUG, INFO, WARN, ERROR, FATAL
            severity_text = {1: "DEBUG", 5: "INFO", 9: "WARN", 13: "ERROR", 17: "FATAL"}[severity]
            
            log = LogRecord(
                timestamp_unix_nano=time.time_ns(),
                severity_number=severity,
                severity_text=severity_text,
                body=random.choice(log_messages),
                attributes=[
                    KeyValue(key="component", value=service_name),
                    KeyValue(key="thread_id", value=f"thread-{random.randint(1, 10)}"),
                    KeyValue(key="request_id", value=str(uuid.uuid4()))
                ]
            )
            logs.append(log)
        
        return TelemetryData(
            resource=resource,
            scope=scope,
            data_type=TelemetryType.LOGS,
            logs=logs
        )

async def main():
    """Main demonstration function"""
    print("OpenTelemetry OTLP Collector Simulation")
    print("=" * 50)
    
    # Create collector
    collector = OTLPCollector("otel-collector-1")
    
    # Configure processing pipeline
    collector.add_processor(BatchProcessor(batch_size=10, timeout_seconds=0.5))
    collector.add_processor(AttributesProcessor(
        add_attributes={"environment": "production", "cluster": "trading-cluster"},
        remove_keys=["sensitive_data"]
    ))
    collector.add_processor(FilterProcessor(severity_filter=5))  # INFO and above
    collector.add_processor(SamplingProcessor(sampling_rate=0.8))  # 80% sampling
    
    # Configure exporters
    collector.add_exporter(JaegerExporter())
    collector.add_exporter(PrometheusExporter())
    collector.add_exporter(LokiExporter())
    
    # Generate and process telemetry data
    generator = TelemetryGenerator()
    
    print("\n=== Generating Telemetry Data ===")
    
    tasks = []
    for _ in range(20):  # Generate 20 telemetry items
        service = random.choice(generator.services)
        data_type = random.choice([
            generator.generate_trace_data,
            generator.generate_metrics_data,
            generator.generate_logs_data
        ])
        
        telemetry_data = data_type(service)
        compressed = random.choice([True, False])
        
        task = asyncio.create_task(
            collector.receive_otlp_data(telemetry_data, compressed=compressed)
        )
        tasks.append(task)
        
        # Add some delay between requests
        await asyncio.sleep(0.05)
    
    # Wait for all processing to complete
    results = await asyncio.gather(*tasks)
    successful_count = sum(results)
    
    print(f"\n=== Processing Complete ===")
    print(f"Successfully processed: {successful_count}/{len(tasks)} items")
    
    # Print collector statistics
    stats = collector.get_stats()
    print(f"\n=== Collector Statistics ===")
    print(f"Received: {stats['received_count']}")
    print(f"Processed: {stats['processed_count']}")
    print(f"Exported: {stats['exported_count']}")
    print(f"Errors: {stats['error_count']}")
    print(f"Bytes Received: {stats['bytes_received']:,}")
    print(f"Compression Ratio: {stats['compression_ratio']:.1%}")
    
    # Print processor statistics
    print(f"\n=== Processor Statistics ===")
    for key, value in stats.items():
        if '_processed' in key or '_errors' in key:
            print(f"{key}: {value}")
    
    # Print exporter statistics
    print(f"\n=== Exporter Statistics ===")
    for key, value in stats.items():
        if '_exported' in key:
            print(f"{key}: {value}")
    
    print("\n=== OTLP Benefits Demonstrated ===")
    print("✓ Efficient binary protocol with Protocol Buffers")
    print("✓ Configurable processing pipeline")
    print("✓ Batch processing for improved throughput")
    print("✓ Attribute enrichment and filtering")
    print("✓ Probabilistic sampling for scale")
    print("✓ Multiple export destinations")
    print("✓ Compression for network efficiency")
    print("✓ Standardized telemetry data model")

if __name__ == "__main__":
    asyncio.run(main())
