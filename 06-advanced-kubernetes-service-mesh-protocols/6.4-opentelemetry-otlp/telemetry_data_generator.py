#!/usr/bin/env python3
"""
OpenTelemetry Telemetry Data Generator
Generates realistic telemetry data for OTLP demonstration
"""

import asyncio
import time
import random
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor

class InstrumentationType(Enum):
    AUTO = "auto"
    MANUAL = "manual"
    CUSTOM = "custom"

class ServiceType(Enum):
    WEB_SERVICE = "web_service"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    CACHE = "cache"
    EXTERNAL_API = "external_api"

@dataclass
class TraceContext:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    trace_flags: int = 1
    trace_state: str = ""

@dataclass
class ServiceConfig:
    name: str
    service_type: ServiceType
    instrumentation_type: InstrumentationType
    error_rate: float
    latency_mean: float
    latency_std: float
    throughput_rps: int

class TelemetryDataGenerator:
    """Generates realistic telemetry data for different service types"""
    
    def __init__(self):
        self.services = self._create_service_configs()
        self.active_traces: Dict[str, TraceContext] = {}
        self.metrics_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._lock = threading.Lock()
    
    def _create_service_configs(self) -> List[ServiceConfig]:
        """Create realistic service configurations"""
        return [
            ServiceConfig(
                name="trading-api",
                service_type=ServiceType.WEB_SERVICE,
                instrumentation_type=InstrumentationType.AUTO,
                error_rate=0.02,
                latency_mean=50.0,
                latency_std=15.0,
                throughput_rps=500
            ),
            ServiceConfig(
                name="risk-engine",
                service_type=ServiceType.WEB_SERVICE,
                instrumentation_type=InstrumentationType.MANUAL,
                error_rate=0.01,
                latency_mean=25.0,
                latency_std=8.0,
                throughput_rps=800
            ),
            ServiceConfig(
                name="order-db",
                service_type=ServiceType.DATABASE,
                instrumentation_type=InstrumentationType.AUTO,
                error_rate=0.005,
                latency_mean=10.0,
                latency_std=5.0,
                throughput_rps=2000
            ),
            ServiceConfig(
                name="redis-cache",
                service_type=ServiceType.CACHE,
                instrumentation_type=InstrumentationType.AUTO,
                error_rate=0.001,
                latency_mean=2.0,
                latency_std=1.0,
                throughput_rps=5000
            ),
            ServiceConfig(
                name="settlement-queue",
                service_type=ServiceType.MESSAGE_QUEUE,
                instrumentation_type=InstrumentationType.CUSTOM,
                error_rate=0.01,
                latency_mean=100.0,
                latency_std=30.0,
                throughput_rps=200
            ),
            ServiceConfig(
                name="market-data-api",
                service_type=ServiceType.EXTERNAL_API,
                instrumentation_type=InstrumentationType.MANUAL,
                error_rate=0.05,
                latency_mean=200.0,
                latency_std=80.0,
                throughput_rps=100
            )
        ]
    
    def generate_trace_context(self, parent_context: Optional[TraceContext] = None) -> TraceContext:
        """Generate trace context for distributed tracing"""
        if parent_context:
            return TraceContext(
                trace_id=parent_context.trace_id,
                span_id=f"{random.getrandbits(64):016x}",
                parent_span_id=parent_context.span_id,
                trace_flags=parent_context.trace_flags,
                trace_state=parent_context.trace_state
            )
        else:
            return TraceContext(
                trace_id=f"{random.getrandbits(128):032x}",
                span_id=f"{random.getrandbits(64):016x}",
                parent_span_id=None
            )
    
    def generate_span_data(self, service: ServiceConfig, context: TraceContext) -> Dict[str, Any]:
        """Generate span data for a service"""
        now_ns = time.time_ns()
        
        # Generate realistic latency
        latency_ms = max(0.1, random.normalvariate(service.latency_mean, service.latency_std))
        duration_ns = int(latency_ms * 1_000_000)
        
        # Determine if this request has an error
        has_error = random.random() < service.error_rate
        
        # Generate operation name based on service type
        operation_name = self._generate_operation_name(service)
        
        span_data = {
            "trace_id": context.trace_id,
            "span_id": context.span_id,
            "parent_span_id": context.parent_span_id,
            "name": operation_name,
            "kind": self._get_span_kind(service.service_type),
            "start_time_unix_nano": now_ns - duration_ns,
            "end_time_unix_nano": now_ns,
            "attributes": self._generate_span_attributes(service, operation_name, has_error),
            "status": {
                "code": "ERROR" if has_error else "OK",
                "message": self._generate_error_message() if has_error else ""
            },
            "events": self._generate_span_events(service, has_error),
            "links": []
        }
        
        return span_data
    
    def _generate_operation_name(self, service: ServiceConfig) -> str:
        """Generate realistic operation names"""
        operations = {
            ServiceType.WEB_SERVICE: [
                "POST /api/v1/orders", "GET /api/v1/positions", "PUT /api/v1/trades",
                "DELETE /api/v1/orders/{id}", "GET /api/v1/market-data"
            ],
            ServiceType.DATABASE: [
                "SELECT orders", "INSERT trade", "UPDATE position", 
                "DELETE expired_orders", "SELECT user_portfolio"
            ],
            ServiceType.MESSAGE_QUEUE: [
                "publish settlement_event", "consume trade_notification",
                "publish risk_alert", "consume order_update"
            ],
            ServiceType.CACHE: [
                "GET user_session", "SET market_prices", "DEL expired_data",
                "GET trading_limits", "SET user_preferences"
            ],
            ServiceType.EXTERNAL_API: [
                "GET market_data", "POST compliance_check", "GET exchange_rates",
                "POST trade_validation", "GET regulatory_data"
            ]
        }
        
        return random.choice(operations[service.service_type])
    
    def _get_span_kind(self, service_type: ServiceType) -> str:
        """Get appropriate span kind for service type"""
        kind_mapping = {
            ServiceType.WEB_SERVICE: "SERVER",
            ServiceType.DATABASE: "CLIENT",
            ServiceType.MESSAGE_QUEUE: "PRODUCER",
            ServiceType.CACHE: "CLIENT",
            ServiceType.EXTERNAL_API: "CLIENT"
        }
        return kind_mapping[service_type]
    
    def _generate_span_attributes(self, service: ServiceConfig, operation: str, has_error: bool) -> List[Dict[str, Any]]:
        """Generate realistic span attributes"""
        base_attributes = [
            {"key": "service.name", "value": {"string_value": service.name}},
            {"key": "service.version", "value": {"string_value": "1.2.3"}},
            {"key": "deployment.environment", "value": {"string_value": "production"}},
            {"key": "instrumentation.type", "value": {"string_value": service.instrumentation_type.value}}
        ]
        
        # Add service-specific attributes
        if service.service_type == ServiceType.WEB_SERVICE:
            base_attributes.extend([
                {"key": "http.method", "value": {"string_value": operation.split()[0]}},
                {"key": "http.route", "value": {"string_value": operation.split()[1]}},
                {"key": "http.status_code", "value": {"int_value": 500 if has_error else random.choice([200, 201, 202])}},
                {"key": "user.id", "value": {"string_value": f"user_{random.randint(1000, 9999)}"}},
                {"key": "request.size", "value": {"int_value": random.randint(100, 5000)}}
            ])
        elif service.service_type == ServiceType.DATABASE:
            base_attributes.extend([
                {"key": "db.system", "value": {"string_value": "postgresql"}},
                {"key": "db.name", "value": {"string_value": "trading_db"}},
                {"key": "db.operation", "value": {"string_value": operation.split()[0]}},
                {"key": "db.table", "value": {"string_value": operation.split()[1] if len(operation.split()) > 1 else "unknown"}},
                {"key": "db.rows_affected", "value": {"int_value": random.randint(1, 100)}}
            ])
        elif service.service_type == ServiceType.MESSAGE_QUEUE:
            base_attributes.extend([
                {"key": "messaging.system", "value": {"string_value": "kafka"}},
                {"key": "messaging.destination", "value": {"string_value": f"topic_{random.choice(['trades', 'orders', 'settlements'])}"}},
                {"key": "messaging.operation", "value": {"string_value": operation.split()[0]}},
                {"key": "messaging.message_id", "value": {"string_value": str(uuid.uuid4())}},
                {"key": "messaging.partition", "value": {"int_value": random.randint(0, 9)}}
            ])
        elif service.service_type == ServiceType.CACHE:
            base_attributes.extend([
                {"key": "cache.system", "value": {"string_value": "redis"}},
                {"key": "cache.operation", "value": {"string_value": operation.split()[0]}},
                {"key": "cache.key", "value": {"string_value": operation.split()[1] if len(operation.split()) > 1 else "unknown"}},
                {"key": "cache.hit", "value": {"bool_value": random.choice([True, False])}},
                {"key": "cache.ttl", "value": {"int_value": random.randint(60, 3600)}}
            ])
        elif service.service_type == ServiceType.EXTERNAL_API:
            base_attributes.extend([
                {"key": "http.url", "value": {"string_value": f"https://api.external.com{operation.split()[1] if len(operation.split()) > 1 else '/unknown'}"}},
                {"key": "http.method", "value": {"string_value": operation.split()[0]}},
                {"key": "http.status_code", "value": {"int_value": 500 if has_error else 200}},
                {"key": "external.provider", "value": {"string_value": "market_data_provider"}},
                {"key": "external.rate_limit", "value": {"int_value": random.randint(100, 1000)}}
            ])
        
        return base_attributes
    
    def _generate_span_events(self, service: ServiceConfig, has_error: bool) -> List[Dict[str, Any]]:
        """Generate span events"""
        events = []
        
        # Add start event
        events.append({
            "time_unix_nano": time.time_ns() - random.randint(1000000, 10000000),
            "name": "operation.start",
            "attributes": [
                {"key": "event.type", "value": {"string_value": "start"}}
            ]
        })
        
        # Add error event if applicable
        if has_error:
            events.append({
                "time_unix_nano": time.time_ns() - random.randint(100000, 1000000),
                "name": "exception",
                "attributes": [
                    {"key": "exception.type", "value": {"string_value": "ServiceException"}},
                    {"key": "exception.message", "value": {"string_value": self._generate_error_message()}},
                    {"key": "exception.stacktrace", "value": {"string_value": "at service.process() line 42"}}
                ]
            })
        
        return events
    
    def _generate_error_message(self) -> str:
        """Generate realistic error messages"""
        errors = [
            "Connection timeout to downstream service",
            "Invalid request parameters",
            "Database connection failed",
            "Rate limit exceeded",
            "Authentication failed",
            "Service temporarily unavailable",
            "Data validation error",
            "Circuit breaker open"
        ]
        return random.choice(errors)
    
    def generate_metrics_data(self, service: ServiceConfig) -> Dict[str, Any]:
        """Generate metrics data for a service"""
        now_ns = time.time_ns()
        
        metrics = {
            "resource_metrics": [{
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"string_value": service.name}},
                        {"key": "service.version", "value": {"string_value": "1.2.3"}},
                        {"key": "host.name", "value": {"string_value": f"host-{random.randint(1, 10)}"}}
                    ]
                },
                "scope_metrics": [{
                    "scope": {
                        "name": "opentelemetry.instrumentation.runtime",
                        "version": "1.0.0"
                    },
                    "metrics": self._generate_service_metrics(service, now_ns)
                }]
            }]
        }
        
        return metrics
    
    def _generate_service_metrics(self, service: ServiceConfig, timestamp_ns: int) -> List[Dict[str, Any]]:
        """Generate service-specific metrics"""
        metrics = []
        
        # Request rate metric
        metrics.append({
            "name": "requests_total",
            "description": "Total number of requests",
            "unit": "1",
            "sum": {
                "data_points": [{
                    "attributes": [
                        {"key": "method", "value": {"string_value": "POST"}},
                        {"key": "status", "value": {"string_value": "200"}}
                    ],
                    "time_unix_nano": timestamp_ns,
                    "as_int": random.randint(service.throughput_rps - 50, service.throughput_rps + 50)
                }],
                "aggregation_temporality": "AGGREGATION_TEMPORALITY_CUMULATIVE",
                "is_monotonic": True
            }
        })
        
        # Latency histogram
        metrics.append({
            "name": "request_duration_ms",
            "description": "Request duration in milliseconds",
            "unit": "ms",
            "histogram": {
                "data_points": [{
                    "attributes": [
                        {"key": "method", "value": {"string_value": "POST"}}
                    ],
                    "time_unix_nano": timestamp_ns,
                    "count": random.randint(50, 200),
                    "sum": random.uniform(service.latency_mean * 50, service.latency_mean * 200),
                    "bucket_counts": [5, 15, 25, 35, 20, 10, 5],
                    "explicit_bounds": [1, 5, 10, 25, 50, 100, 250, 500]
                }],
                "aggregation_temporality": "AGGREGATION_TEMPORALITY_DELTA"
            }
        })
        
        # Error rate gauge
        metrics.append({
            "name": "error_rate",
            "description": "Current error rate percentage",
            "unit": "%",
            "gauge": {
                "data_points": [{
                    "time_unix_nano": timestamp_ns,
                    "as_double": service.error_rate * 100 + random.uniform(-0.5, 0.5)
                }]
            }
        })
        
        # CPU usage gauge
        metrics.append({
            "name": "cpu_usage_percent",
            "description": "CPU usage percentage",
            "unit": "%",
            "gauge": {
                "data_points": [{
                    "attributes": [
                        {"key": "cpu", "value": {"string_value": f"cpu{random.randint(0, 7)}"}}
                    ],
                    "time_unix_nano": timestamp_ns,
                    "as_double": random.uniform(10, 80)
                }]
            }
        })
        
        # Memory usage gauge
        metrics.append({
            "name": "memory_usage_bytes",
            "description": "Memory usage in bytes",
            "unit": "By",
            "gauge": {
                "data_points": [{
                    "time_unix_nano": timestamp_ns,
                    "as_int": random.randint(100_000_000, 1_000_000_000)  # 100MB - 1GB
                }]
            }
        })
        
        return metrics
    
    def generate_logs_data(self, service: ServiceConfig) -> Dict[str, Any]:
        """Generate log data for a service"""
        now_ns = time.time_ns()
        
        log_levels = [
            (1, "TRACE"), (5, "DEBUG"), (9, "INFO"), 
            (13, "WARN"), (17, "ERROR"), (21, "FATAL")
        ]
        
        # Weight log levels based on service error rate
        if service.error_rate > 0.02:
            level_weights = [0.05, 0.1, 0.6, 0.15, 0.08, 0.02]
        else:
            level_weights = [0.1, 0.15, 0.7, 0.04, 0.01, 0.0]
        
        severity_number, severity_text = random.choices(log_levels, weights=level_weights)[0]
        
        logs = {
            "resource_logs": [{
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"string_value": service.name}},
                        {"key": "service.version", "value": {"string_value": "1.2.3"}}
                    ]
                },
                "scope_logs": [{
                    "scope": {
                        "name": "opentelemetry.instrumentation.logging",
                        "version": "1.0.0"
                    },
                    "log_records": [{
                        "time_unix_nano": now_ns,
                        "severity_number": severity_number,
                        "severity_text": severity_text,
                        "body": {"string_value": self._generate_log_message(service, severity_text)},
                        "attributes": [
                            {"key": "component", "value": {"string_value": service.name}},
                            {"key": "thread.id", "value": {"string_value": f"thread-{random.randint(1, 10)}"}},
                            {"key": "request.id", "value": {"string_value": str(uuid.uuid4())}},
                            {"key": "user.id", "value": {"string_value": f"user_{random.randint(1000, 9999)}"}}
                        ],
                        "trace_id": f"{random.getrandbits(128):032x}" if random.random() < 0.3 else "",
                        "span_id": f"{random.getrandbits(64):016x}" if random.random() < 0.3 else ""
                    }]
                }]
            }]
        }
        
        return logs
    
    def _generate_log_message(self, service: ServiceConfig, severity: str) -> str:
        """Generate realistic log messages"""
        messages = {
            "TRACE": [
                f"Entering method processRequest() in {service.name}",
                f"Variable state: processing=true, queue_size=42",
                f"Cache lookup for key: user_session_{random.randint(1000, 9999)}"
            ],
            "DEBUG": [
                f"Processing request with ID: {uuid.uuid4()}",
                f"Database query executed in {random.randint(1, 50)}ms",
                f"Cache hit ratio: {random.uniform(0.7, 0.95):.2f}"
            ],
            "INFO": [
                f"Successfully processed {random.randint(1, 100)} requests",
                f"Service {service.name} started successfully",
                f"Health check passed for all dependencies",
                f"Configuration reloaded from config server"
            ],
            "WARN": [
                f"High latency detected: {random.randint(100, 500)}ms",
                f"Connection pool utilization at {random.randint(80, 95)}%",
                f"Rate limiting applied to user_{random.randint(1000, 9999)}",
                f"Retry attempt {random.randint(1, 3)} for failed request"
            ],
            "ERROR": [
                f"Failed to connect to downstream service: {random.choice(['database', 'cache', 'api'])}",
                f"Request validation failed: invalid trade amount",
                f"Authentication failed for user_{random.randint(1000, 9999)}",
                f"Circuit breaker opened for service {random.choice(['risk-engine', 'settlement-service'])}"
            ],
            "FATAL": [
                f"Service {service.name} is shutting down due to critical error",
                f"Database connection pool exhausted",
                f"Out of memory error in {service.name}"
            ]
        }
        
        return random.choice(messages.get(severity, ["Unknown log message"]))
    
    async def generate_distributed_trace(self, num_services: int = 4) -> List[Dict[str, Any]]:
        """Generate a distributed trace across multiple services"""
        # Start with root span
        root_context = self.generate_trace_context()
        root_service = random.choice(self.services)
        
        spans = []
        spans.append(self.generate_span_data(root_service, root_context))
        
        # Generate child spans
        current_context = root_context
        for _ in range(num_services - 1):
            child_context = self.generate_trace_context(current_context)
            child_service = random.choice([s for s in self.services if s != root_service])
            
            spans.append(self.generate_span_data(child_service, child_context))
            current_context = child_context
        
        return spans
    
    async def generate_telemetry_batch(self, batch_size: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Generate a batch of mixed telemetry data"""
        batch = {
            "traces": [],
            "metrics": [],
            "logs": []
        }
        
        for _ in range(batch_size):
            service = random.choice(self.services)
            data_type = random.choices(
                ["traces", "metrics", "logs"],
                weights=[0.4, 0.3, 0.3]
            )[0]
            
            if data_type == "traces":
                context = self.generate_trace_context()
                span_data = self.generate_span_data(service, context)
                batch["traces"].append(span_data)
            elif data_type == "metrics":
                metrics_data = self.generate_metrics_data(service)
                batch["metrics"].append(metrics_data)
            else:
                logs_data = self.generate_logs_data(service)
                batch["logs"].append(logs_data)
        
        return batch

async def main():
    """Main demonstration function"""
    print("OpenTelemetry Telemetry Data Generator")
    print("=" * 50)
    
    generator = TelemetryDataGenerator()
    
    print("\n=== Service Configurations ===")
    for service in generator.services:
        print(f"{service.name}:")
        print(f"  Type: {service.service_type.value}")
        print(f"  Instrumentation: {service.instrumentation_type.value}")
        print(f"  Error Rate: {service.error_rate:.1%}")
        print(f"  Latency: {service.latency_mean}±{service.latency_std}ms")
        print(f"  Throughput: {service.throughput_rps} RPS")
        print()
    
    print("=== Generating Sample Telemetry Data ===")
    
    # Generate distributed trace
    print("\n1. Distributed Trace:")
    trace_spans = await generator.generate_distributed_trace(4)
    for i, span in enumerate(trace_spans):
        print(f"  Span {i+1}: {span['name']} ({span.get('attributes', [{}])[0].get('value', {}).get('string_value', 'unknown')})")
        print(f"    Duration: {(span['end_time_unix_nano'] - span['start_time_unix_nano']) / 1_000_000:.2f}ms")
        print(f"    Status: {span['status']['code']}")
    
    # Generate metrics batch
    print("\n2. Metrics Data:")
    for service in generator.services[:3]:
        metrics = generator.generate_metrics_data(service)
        service_metrics = metrics['resource_metrics'][0]['scope_metrics'][0]['metrics']
        print(f"  {service.name}: {len(service_metrics)} metrics generated")
        for metric in service_metrics[:2]:  # Show first 2 metrics
            print(f"    - {metric['name']}: {metric['description']}")
    
    # Generate logs batch
    print("\n3. Logs Data:")
    for service in generator.services[:3]:
        logs = generator.generate_logs_data(service)
        log_record = logs['resource_logs'][0]['scope_logs'][0]['log_records'][0]
        print(f"  {service.name}: {log_record['severity_text']} - {log_record['body']['string_value']}")
    
    # Generate mixed batch
    print("\n4. Mixed Telemetry Batch:")
    batch = await generator.generate_telemetry_batch(20)
    print(f"  Generated batch with:")
    print(f"    Traces: {len(batch['traces'])}")
    print(f"    Metrics: {len(batch['metrics'])}")
    print(f"    Logs: {len(batch['logs'])}")
    
    print("\n=== Telemetry Generation Complete ===")
    print("✓ Realistic service configurations")
    print("✓ Distributed trace generation")
    print("✓ Service-specific metrics")
    print("✓ Contextual log messages")
    print("✓ Error simulation and handling")
    print("✓ Mixed telemetry data batches")

if __name__ == "__main__":
    asyncio.run(main())
