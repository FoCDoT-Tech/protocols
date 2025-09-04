# Container Network Interface (CNI)

## Definition

Container Network Interface (CNI) is a specification and set of libraries for configuring network interfaces in Linux containers. CNI provides a pluggable architecture for container networking, allowing different network providers to implement custom networking solutions while maintaining a consistent interface for container runtimes like Kubernetes.

## RFC and Standards

- **CNI Specification**: [CNI SPEC v1.0.0](https://github.com/containernetworking/cni/blob/main/SPEC.md)
- **Related RFCs**: 
  - RFC 791 (IPv4)
  - RFC 8200 (IPv6)
  - RFC 1918 (Private Address Space)
  - RFC 4632 (CIDR)

## Real-World Engineering Scenario

**Scenario**: Multi-tenant Kubernetes cluster requiring network isolation

You're architecting a Kubernetes platform for a SaaS company hosting multiple customer applications. Each customer requires:
- Network isolation between tenants
- Custom network policies for security
- Load balancing and service discovery
- Integration with existing VPC infrastructure
- Support for both IPv4 and IPv6

**CNI Implementation Requirements**:
1. **Network Isolation**: Each tenant gets isolated network namespaces
2. **Policy Enforcement**: NetworkPolicies control traffic between pods
3. **IPAM (IP Address Management)**: Automatic IP allocation from defined pools
4. **Service Mesh Integration**: Support for Istio/Linkerd networking
5. **Cloud Integration**: AWS VPC, GCP VPC, Azure VNET compatibility

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Pod A     │  │   Pod B     │  │   Pod C     │         │
│  │ 10.244.1.2  │  │ 10.244.1.3  │  │ 10.244.2.2  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                 │                 │              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              CNI Plugin Layer                           │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │ │
│  │  │  IPAM   │ │ Bridge  │ │ Routing │ │ Policy  │      │ │
│  │  │ Plugin  │ │ Plugin  │ │ Plugin  │ │ Plugin  │      │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Host Network                             │ │
│  │        ┌─────────┐    ┌─────────┐    ┌─────────┐       │ │
│  │        │  eth0   │    │  cni0   │    │ flannel │       │ │
│  │        │(host)   │    │(bridge) │    │ (vxlan) │       │ │
│  │        └─────────┘    └─────────┘    └─────────┘       │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Key Technical Concepts

### 1. CNI Plugin Types

**Main Plugins** (create network interfaces):
- **bridge**: Creates bridge networks for pod communication
- **ipvlan**: Uses Linux ipvlan for L2/L3 networking
- **macvlan**: Assigns unique MAC addresses to containers
- **host-device**: Moves host network device into container

**IPAM Plugins** (IP Address Management):
- **static**: Static IP assignment
- **dhcp**: DHCP-based IP allocation
- **host-local**: Local subnet IP allocation

**Meta Plugins** (modify behavior):
- **flannel**: Overlay networking with VXLAN/UDP
- **calico**: Policy-driven networking with BGP
- **weave**: Mesh networking with encryption

### 2. CNI Execution Model

```json
{
  "cniVersion": "1.0.0",
  "name": "mynet",
  "type": "bridge",
  "bridge": "cni0",
  "isGateway": true,
  "ipMasq": true,
  "ipam": {
    "type": "host-local",
    "subnet": "10.244.0.0/16",
    "routes": [
      { "dst": "0.0.0.0/0" }
    ]
  }
}
```

### 3. Network Namespace Management

CNI operates within Linux network namespaces:
- **Host Namespace**: Default network stack
- **Container Namespace**: Isolated network for each container
- **Shared Namespaces**: Pods share network namespace

### 4. Plugin Chain Execution

CNI supports plugin chaining for complex networking:
1. **Main Plugin**: Creates primary interface (e.g., bridge)
2. **IPAM Plugin**: Assigns IP addresses
3. **Meta Plugins**: Apply policies, routing, encryption

### 5. Kubernetes Integration

**kubelet** invokes CNI plugins during pod lifecycle:
- **ADD**: Create network interface when pod starts
- **DEL**: Remove network interface when pod terminates
- **CHECK**: Verify network configuration
- **VERSION**: Query plugin capabilities

## Protocol Dependencies

**Builds on Chapter 1.1 (IPv4/IPv6)**:
- IP addressing and subnetting
- Routing table management
- Network interface configuration

**Integration Points**:
- Layer 2: Ethernet bridging and VLANs
- Layer 3: IP routing and forwarding
- Layer 4: Port mapping and load balancing

## Performance Characteristics

**Latency Impact**:
- Bridge mode: ~0.1ms additional latency
- Overlay networks: 1-5ms depending on encapsulation
- Host networking: No additional latency

**Throughput**:
- Bridge: Near-native performance (95%+ of host)
- VXLAN overlay: 80-90% of native throughput
- Encrypted overlay: 60-80% depending on encryption

**Scalability**:
- IP address pool size limits pod density
- Routing table size affects performance
- Network policy complexity impacts throughput

## Security Considerations

**Network Isolation**:
- Namespace-based isolation
- VLAN segmentation
- Firewall rule integration

**Policy Enforcement**:
- Ingress/egress traffic control
- Pod-to-pod communication policies
- Service mesh integration

**Encryption**:
- Overlay network encryption (WireGuard, IPSec)
- TLS for control plane communication
- Certificate-based authentication

## Common Implementation Patterns

**Multi-CNI Setup**:
- Primary CNI for pod networking
- Secondary CNI for specialized interfaces
- SR-IOV for high-performance workloads

**Cloud Provider Integration**:
- AWS VPC CNI for native VPC networking
- GCP GKE networking with Alias IPs
- Azure CNI for VNET integration

**Service Mesh Compatibility**:
- Istio sidecar injection
- Linkerd proxy networking
- Consul Connect integration
