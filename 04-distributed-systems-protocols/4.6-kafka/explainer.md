# Kafka (Apache Kafka)

## Definition

Apache Kafka is a distributed streaming platform designed for high-throughput, fault-tolerant, real-time data streaming. Built as a distributed commit log, Kafka provides publish-subscribe messaging with strong durability guarantees, horizontal scalability, and low-latency data processing capabilities for modern data-driven applications.

## Core References

- **Apache Kafka Protocol**: Binary protocol specification
- **Kafka Improvement Proposals (KIPs)**: Protocol evolution
- **Apache Kafka Documentation**: Official implementation guide
- **Confluent Platform**: Enterprise Kafka distribution

## Real-World Impact

Kafka powers real-time data infrastructure at massive scale:

**Streaming Analytics**: Real-time data processing and analytics
- Netflix processes 8+ trillion events daily through Kafka
- LinkedIn handles 7+ million messages per second

**Event Sourcing**: Immutable event logs for microservices
- Uber uses Kafka for real-time trip tracking and pricing
- Airbnb leverages Kafka for booking and payment events

**Data Integration**: Connecting diverse data systems
- Goldman Sachs uses Kafka for trade settlement and risk management
- Spotify streams music recommendation events through Kafka

## Engineering Scenario

You're building a real-time e-commerce platform that needs:
- High-throughput order processing (100k+ orders/second)
- Real-time inventory updates across multiple warehouses
- Customer activity tracking for recommendations
- Fault-tolerant message delivery with replay capability
- Horizontal scaling for peak traffic periods

**Challenge**: Traditional message queues can't handle the throughput and durability requirements. You need:
- Persistent message storage with configurable retention
- Partitioned topics for parallel processing
- Consumer groups for load balancing
- Exactly-once delivery semantics
- Stream processing capabilities

**Kafka Solution**: Provides a distributed streaming platform with:
- **Partitioned Topics**: Horizontal scaling through topic partitions
- **Replication**: Fault tolerance with configurable replication factor
- **Consumer Groups**: Load balancing and failover for consumers
- **Offset Management**: Replay capability and exactly-once processing
- **Stream Processing**: Real-time data transformation with Kafka Streams

## Kafka Architecture

```mermaid
graph TB
    subgraph "Kafka Cluster"
        BROKER1[Kafka Broker 1<br/>Leader for Partition 0]
        BROKER2[Kafka Broker 2<br/>Leader for Partition 1]
        BROKER3[Kafka Broker 3<br/>Leader for Partition 2]
        
        ZK[ZooKeeper<br/>Cluster Coordination]
        
        BROKER1 --> ZK
        BROKER2 --> ZK
        BROKER3 --> ZK
    end
    
    subgraph "Topics & Partitions"
        TOPIC[orders Topic]
        PART0[Partition 0<br/>Replicas: 1,2]
        PART1[Partition 1<br/>Replicas: 2,3]
        PART2[Partition 2<br/>Replicas: 3,1]
        
        TOPIC --> PART0
        TOPIC --> PART1
        TOPIC --> PART2
        
        PART0 --> BROKER1
        PART1 --> BROKER2
        PART2 --> BROKER3
    end
    
    subgraph "Producers"
        PROD1[Order Service<br/>Producer]
        PROD2[Inventory Service<br/>Producer]
        PROD3[Payment Service<br/>Producer]
    end
    
    subgraph "Consumer Groups"
        GROUP1[Processing Group<br/>Consumer 1, 2, 3]
        GROUP2[Analytics Group<br/>Consumer A, B]
        GROUP3[Audit Group<br/>Consumer X]
    end
    
    PROD1 --> BROKER1
    PROD2 --> BROKER2
    PROD3 --> BROKER3
    
    BROKER1 --> GROUP1
    BROKER2 --> GROUP1
    BROKER3 --> GROUP1
    
    BROKER1 --> GROUP2
    BROKER2 --> GROUP2
    
    BROKER1 --> GROUP3
    
    style BROKER1 fill:#e1f5fe,stroke:#01579b
    style BROKER2 fill:#e1f5fe,stroke:#01579b
    style BROKER3 fill:#e1f5fe,stroke:#01579b
    style ZK fill:#fff3e0,stroke:#ef6c00
    style TOPIC fill:#e8f5e8,stroke:#2e7d32
    style GROUP1 fill:#f3e5f5,stroke:#7b1fa2
```

## Key Features

**Distributed Architecture**:
- Horizontal scaling through partitioning
- Fault tolerance via replication
- Leader election and failover

**Durability & Performance**:
- Persistent storage with configurable retention
- Sequential disk I/O for high throughput
- Zero-copy data transfer

**Consumer Semantics**:
- At-least-once, at-most-once, exactly-once delivery
- Consumer groups for load balancing
- Offset management for replay capability

**Stream Processing**:
- Kafka Streams for real-time processing
- Exactly-once processing semantics
- Stateful stream transformations

## Example Code

See the following implementations:

- `kafka_broker.py` - Kafka broker simulation with partitioning and replication
- `kafka_producer.py` - Producer implementation with batching and compression
- `kafka_consumer.py` - Consumer with group coordination and offset management
- `stream_processing.py` - Stream processing examples with windowing and aggregation

## Run Instructions

```bash
# Run Kafka broker simulation
python3 kafka_broker.py

# Run producer examples
python3 kafka_producer.py

# Run consumer examples
python3 kafka_consumer.py

# Run stream processing demo
python3 stream_processing.py

# Generate diagrams
python3 render_diagram.py

# Run all tests
make test
```

Kafka provides the foundation for building real-time, scalable data streaming applications with strong durability and consistency guarantees.
