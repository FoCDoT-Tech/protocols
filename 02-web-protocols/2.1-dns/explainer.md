# DNS - Domain Name System

## Definition

DNS (Domain Name System) is a hierarchical, distributed naming system that translates human-readable domain names (like www.example.com) into IP addresses that computers use to communicate. DNS operates as the internet's phone book, enabling users to access websites using memorable names instead of numeric IP addresses.

DNS uses a client-server architecture where DNS resolvers query authoritative name servers in a hierarchical manner. The system is distributed across millions of servers worldwide, providing redundancy, load distribution, and fast response times. DNS queries typically use UDP for speed, falling back to TCP for large responses or zone transfers.

## Core RFC References

- **RFC 1034** - Domain Names - Concepts and Facilities
- **RFC 1035** - Domain Names - Implementation and Specification
- **RFC 2181** - Clarifications to the DNS Specification
- **RFC 8484** - DNS Queries over HTTPS (DoH)
- **RFC 7858** - Specification for DNS over Transport Layer Security (DoT)

## Why It Matters

DNS is fundamental to internet functionality and modern web architecture:

- **User Experience**: Enables memorable domain names instead of IP addresses
- **Load Balancing**: Distributes traffic across multiple servers via DNS responses
- **Service Discovery**: Microservices use DNS for dynamic service location
- **Security**: DNS filtering blocks malicious domains and implements parental controls
- **Performance**: CDNs use DNS to direct users to geographically closest servers

## Real World Scenario for Engineers

**Scenario**: Building a global e-commerce platform with microservices architecture

You're architecting a scalable e-commerce system serving millions of users across multiple regions:

- **Multi-region Deployment**: DNS directs users to nearest data center (us-east, eu-west, asia-pacific)
- **Service Discovery**: Internal services (payment, inventory, user-auth) resolve via internal DNS
- **Load Balancing**: DNS round-robin distributes traffic across multiple application servers
- **Failover**: Health checks update DNS records to remove failed servers automatically
- **CDN Integration**: Static assets served from edge locations via DNS-based routing

**Engineering Decisions**:
- Use short TTL (60s) for dynamic services, longer TTL (1h) for static content
- Implement DNS-based canary deployments for gradual rollouts
- Monitor DNS query patterns to detect traffic anomalies and attacks
- Use private DNS zones for internal service communication

**Implementation Considerations**:
- DNS propagation delays affect deployment strategies
- DNS caching at multiple levels (browser, OS, ISP) impacts real-time changes
- DNS security (DNSSEC) prevents cache poisoning attacks

## Mermaid Diagram

```mermaid
graph TB
    subgraph "DNS Hierarchy"
        A[Root Servers] --> B[TLD Servers (.com)]
        B --> C[Authoritative Servers (example.com)]
        C --> D[Resource Records (A, AAAA, CNAME, MX)]
    end
    
    subgraph "DNS Query Process"
        E[Client: www.example.com] --> F[Recursive Resolver]
        F --> G[Root Server Query]
        G --> H[TLD Server Query]
        H --> I[Authoritative Server Query]
        I --> J[IP Address Response]
        J --> E
    end
    
    subgraph "DNS Record Types"
        K[A Record: IPv4 Address] --> L[192.0.2.1]
        M[AAAA Record: IPv6 Address] --> N[2001:db8::1]
        O[CNAME Record: Alias] --> P[www → example.com]
        Q[MX Record: Mail Exchange] --> R[mail.example.com]
        S[NS Record: Name Server] --> T[ns1.example.com]
    end
    
    subgraph "DNS Caching Layers"
        U[Browser Cache] --> V[OS Cache]
        V --> W[ISP Cache]
        W --> X[Recursive Resolver Cache]
        X --> Y[Authoritative Server]
    end
```
