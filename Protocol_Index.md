# Protocol Index

## 1. Core Internet & Networking Protocols
- **1.1 IPv4 & IPv6** – Internet Protocol addressing and routing (RFC 791, RFC 8200)
- **1.2 ICMP / ICMPv6** – Internet Control Message Protocol for diagnostics: ping, traceroute (RFC 792, RFC 4443)
- **1.3 TCP** – Transmission Control Protocol: reliable, ordered transport (RFC 9293)
- **1.4 UDP** – User Datagram Protocol: lightweight, fast transport (RFC 768)
- **1.5 QUIC** – Quick UDP Internet Connections: encrypted, multiplexed transport (RFC 9000)
  - *Dependencies: 1.4 UDP, 2.8 TLS concepts*

## 2. Web Protocols
- **2.1 DNS** – Domain Name System: domain resolution (RFC 1034, RFC 1035)
- **2.2 HTTP/1.1** – Hypertext Transfer Protocol: classic web protocol (RFC 9110)
  - *Dependencies: 1.3 TCP*
- **2.3 HTTP/2** – Binary, multiplexed HTTP (RFC 9113)
  - *Dependencies: 2.2 HTTP/1.1, 2.8 TLS*
- **2.4 HTTP/3** – QUIC-based HTTP for reduced latency (RFC 9114)
  - *Dependencies: 1.5 QUIC, 2.3 HTTP/2*
- **2.5 WebSocket** – Full-duplex communication over TCP (RFC 6455)
  - *Dependencies: 2.2 HTTP/1.1*
- **2.6 gRPC** – Google Remote Procedure Call over HTTP/2
  - *Dependencies: 2.3 HTTP/2*
- **2.7 GraphQL** – API query language over HTTP/WebSocket
  - *Dependencies: 2.2 HTTP/1.1, 2.5 WebSocket*
- **2.8 TLS (1.2, 1.3)** – Transport Layer Security for encrypted communication (RFC 5246, RFC 8446)
  - *Dependencies: 1.3 TCP*
- **2.9 OAuth 2.0 / OIDC** – Authorization framework and identity federation (RFC 6749, RFC 6750)
  - *Dependencies: 2.2 HTTP/1.1, 2.8 TLS*
- **2.10 SAML 2.0** – Security Assertion Markup Language for enterprise identity
  - *Dependencies: 2.2 HTTP/1.1, 2.8 TLS*

## 3. Database & Storage Protocols
- **3.1 SQL over TCP/IP** – MySQL, PostgreSQL, SQL Server wire protocols
  - *Dependencies: 1.3 TCP*
- **3.2 MongoDB Wire Protocol** – Document database binary protocol
  - *Dependencies: 1.3 TCP*
- **3.3 Cassandra Query Protocol** – Column-store database protocol
  - *Dependencies: 1.3 TCP*
- **3.4 Redis RESP** – Redis Serialization Protocol for key-value operations
  - *Dependencies: 1.3 TCP*
- **3.5 NFS / SMB** – Network File System and Server Message Block protocols
  - *Dependencies: 1.3 TCP, 1.4 UDP*
- **3.6 S3 API** – Amazon S3-compatible object storage HTTP-based API
  - *Dependencies: 2.2 HTTP/1.1, 2.8 TLS*

## 4. Distributed Systems Protocols
- **4.1 Raft / Paxos** – Consensus algorithms for distributed agreement
  - *Dependencies: 1.3 TCP*
- **4.2 Gossip Protocols** – Epidemic protocols for membership and state dissemination
  - *Dependencies: 1.4 UDP*
- **4.3 AMQP** – Advanced Message Queuing Protocol (AMQP 0.9.1, AMQP 1.0)
  - *Dependencies: 1.3 TCP*
- **4.4 MQTT** – Message Queuing Telemetry Transport for IoT lightweight messaging (MQTT 3.1.1, MQTT 5.0)
  - *Dependencies: 1.3 TCP*
- **4.5 STOMP** – Simple Text Oriented Messaging Protocol
  - *Dependencies: 1.3 TCP*
- **4.6 Kafka Protocol** – Apache Kafka distributed streaming protocol
  - *Dependencies: 1.3 TCP*

## 5. Kubernetes & Cloud-Native Protocols
- **5.1 etcd (gRPC)** – Raft-backed key-value store for Kubernetes cluster state
  - *Dependencies: 2.6 gRPC, 4.1 Raft*
- **5.2 Kube API** – Kubernetes API server RESTful interface (HTTP/JSON over TLS)
  - *Dependencies: 2.2 HTTP/1.1, 2.8 TLS*
- **5.3 CNI** – Container Network Interface specification
  - *Dependencies: 1.1 IPv4/IPv6*
- **5.4 CSI** – Container Storage Interface for persistent volumes
  - *Dependencies: 2.6 gRPC*
- **5.5 Prometheus Exposition Format** – Metrics scraping text-based format
  - *Dependencies: 2.2 HTTP/1.1*

## 6. Advanced Kubernetes & Service Mesh Protocols
- **6.1 Envoy xDS APIs** – Service mesh control plane discovery APIs
  - *Dependencies: 2.6 gRPC, 5.2 Kube API*
- **6.2 mTLS** – Mutual TLS for service-to-service authentication
  - *Dependencies: 2.8 TLS*
- **6.3 HTTP/2 & gRPC multiplexing** – Sidecar proxy communication patterns
  - *Dependencies: 2.3 HTTP/2, 2.6 gRPC*
- **6.4 OpenTelemetry Protocol (OTLP)** – Observability data collection protocol
  - *Dependencies: 2.6 gRPC, 2.2 HTTP/1.1*
- **6.5 eBPF-based protocols** – Extended Berkeley Packet Filter for advanced networking and security
  - *Dependencies: 1.1 IPv4/IPv6, 1.3 TCP, 1.4 UDP*
