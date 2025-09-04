# Prometheus Exposition Format

## Definition

Prometheus Exposition Format is a text-based format for exposing metrics from applications and infrastructure components. It defines how metrics are structured, labeled, and transmitted over HTTP/1.1, enabling Prometheus to scrape and store time-series data for monitoring and alerting in cloud-native environments.

## RFC and Standards

- **Prometheus Exposition Format**: [Exposition Format Specification](https://prometheus.io/docs/instrumenting/exposition_formats/)
- **Related Standards**:
  - RFC 7230-7237 (HTTP/1.1)
  - RFC 3986 (URI Generic Syntax)
  - OpenMetrics Specification
  - CNCF Observability Standards

## Real-World Engineering Scenario

**Scenario**: Multi-service Kubernetes application requiring comprehensive observability

You're operating a microservices platform with hundreds of services across multiple Kubernetes clusters. You need:
- **Application metrics**: Request rates, error rates, latency percentiles
- **Infrastructure metrics**: CPU, memory, disk, network utilization
- **Business metrics**: User registrations, revenue, feature usage
- **SLA monitoring**: Service availability, performance targets
- **Alerting**: Proactive notification of issues and anomalies

**Prometheus Implementation Requirements**:
1. **Metric exposition**: Standardized format for all services
2. **Service discovery**: Automatic detection of metric endpoints
3. **Scraping configuration**: Efficient collection at scale
4. **Label management**: Consistent dimensionality and cardinality
5. **Federation**: Cross-cluster metric aggregation

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Service A  │  │  Service B  │  │  Service C  │         │
│  │ /metrics    │  │ /metrics    │  │ /metrics    │         │
│  │ HTTP/1.1    │  │ HTTP/1.1    │  │ HTTP/1.1    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                 │                 │              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Prometheus Server                          │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │ │
│  │  │ Service │ │ Scrape  │ │ Storage │ │ Query   │      │ │
│  │  │Discovery│ │ Engine  │ │ Engine  │ │ Engine  │      │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Alertmanager                            │ │
│  │        ┌─────────┐    ┌─────────┐    ┌─────────┐       │ │
│  │        │ Rules   │    │ Routing │    │ Silence │       │ │
│  │        │ Engine  │    │ Engine  │    │ Manager │       │ │
│  │        └─────────┘    └─────────┘    └─────────┘       │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Key Technical Concepts

### 1. Metric Types

**Counter**: Monotonically increasing value
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 1027
http_requests_total{method="POST",status="201"} 94
```

**Gauge**: Current value that can go up or down
```
# HELP memory_usage_bytes Current memory usage
# TYPE memory_usage_bytes gauge
memory_usage_bytes{instance="web-1"} 536870912
```

**Histogram**: Distribution of observations
```
# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 24054
http_request_duration_seconds_bucket{le="0.2"} 33444
http_request_duration_seconds_bucket{le="+Inf"} 144320
http_request_duration_seconds_sum 53423
http_request_duration_seconds_count 144320
```

**Summary**: Similar to histogram with quantiles
```
# HELP rpc_duration_seconds RPC latency quantiles
# TYPE rpc_duration_seconds summary
rpc_duration_seconds{quantile="0.01"} 3102
rpc_duration_seconds{quantile="0.05"} 3272
rpc_duration_seconds{quantile="0.5"} 4773
rpc_duration_seconds{quantile="0.9"} 9001
rpc_duration_seconds{quantile="0.99"} 76656
rpc_duration_seconds_sum 1.7560473e+07
rpc_duration_seconds_count 2693
```

### 2. Label Model

Labels provide multi-dimensional data model:
- **Metric name**: Identifies the measurement
- **Label pairs**: Key-value dimensions for filtering/aggregation
- **Sample value**: Numeric measurement
- **Timestamp**: When measurement was taken

### 3. HTTP Exposition

Metrics exposed via HTTP/1.1 GET requests:
```http
GET /metrics HTTP/1.1
Host: service.example.com
User-Agent: Prometheus/2.40.0

HTTP/1.1 200 OK
Content-Type: text/plain; version=0.0.4; charset=utf-8
Content-Length: 2847

# HELP go_memstats_alloc_bytes Number of bytes allocated
# TYPE go_memstats_alloc_bytes gauge
go_memstats_alloc_bytes 2.097152e+06
```

### 4. Service Discovery

Prometheus discovers targets through:
- **Static configuration**: Hardcoded target lists
- **Kubernetes SD**: Automatic pod/service discovery
- **Consul SD**: Service registry integration
- **DNS SD**: SRV record-based discovery
- **File SD**: Dynamic file-based configuration

### 5. Scraping and Storage

**Scrape Process**:
1. Service discovery identifies targets
2. HTTP GET request to /metrics endpoint
3. Parse exposition format
4. Apply relabeling rules
5. Store time-series data

**Storage Engine**:
- Time-series database optimized for metrics
- Compression and retention policies
- Block-based storage with indexing

## Protocol Dependencies

**Builds on HTTP/1.1 (Chapter 2.2)**:
- HTTP GET requests for metric scraping
- Content-Type negotiation
- Status codes and error handling

**Integration Points**:
- Kubernetes API for service discovery
- DNS for target resolution
- TLS for secure metric transmission

## Performance Characteristics

**Scraping Performance**:
- Default scrape interval: 15-60 seconds
- Scrape timeout: 10 seconds
- Concurrent scrapes: Configurable parallelism

**Storage Performance**:
- Ingestion rate: 1M+ samples/second
- Query latency: <100ms for simple queries
- Retention: 15 days default, configurable

**Cardinality Limits**:
- High cardinality can impact performance
- Recommended: <10 label values per label key
- Monitor series churn and growth

## Security Considerations

**Authentication**:
- Basic HTTP authentication
- Bearer token authentication
- mTLS for service-to-service communication

**Authorization**:
- RBAC for Prometheus access
- Network policies for scrape targets
- Service mesh integration

**Data Protection**:
- TLS encryption for metric transmission
- Secure storage of sensitive metrics
- Access control for query interfaces

## Common Implementation Patterns

**Multi-tenancy**:
- Namespace-based isolation
- Label-based tenant separation
- Federated Prometheus instances

**High Availability**:
- Multiple Prometheus replicas
- External storage integration
- Alert deduplication

**Scaling Patterns**:
- Horizontal sharding by service
- Hierarchical federation
- Remote storage backends

**Alerting Integration**:
- Recording rules for complex metrics
- Alerting rules with thresholds
- Notification routing and escalation
