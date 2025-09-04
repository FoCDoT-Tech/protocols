# gRPC (Google Remote Procedure Call)

## Definition
gRPC is a high-performance, open-source universal RPC framework developed by Google. It uses HTTP/2 for transport, Protocol Buffers as the interface description language, and provides features like authentication, bidirectional streaming, flow control, blocking/non-blocking bindings, and cancellation/timeouts.

## RFCs and Standards
- **gRPC Specification**: https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md
- **HTTP/2 RFC 7540**: Underlying transport protocol
- **Protocol Buffers**: Language-neutral, platform-neutral serialization mechanism
- **gRPC Core Concepts**: https://grpc.io/docs/what-is-grpc/core-concepts/

## Real-World Engineering Scenario
You're building a microservices architecture for a financial trading platform. Services need to communicate with strict performance requirements, type safety, and support for streaming data. Traditional REST APIs over HTTP/1.1 introduce latency and lack efficient streaming. gRPC over HTTP/2 provides:

- **Type-safe APIs** with Protocol Buffers schema
- **High performance** with binary serialization and HTTP/2 multiplexing
- **Streaming support** for real-time market data feeds
- **Load balancing** and service discovery integration
- **Cross-language compatibility** for polyglot microservices

## Key Features

### 1. Protocol Buffers (protobuf)
- Binary serialization format
- Language-agnostic schema definition
- Backward/forward compatibility
- Smaller payload size than JSON

### 2. HTTP/2 Transport
- Multiplexing multiple calls over single connection
- Header compression with HPACK
- Server push capabilities
- Flow control and prioritization

### 3. Four Types of Service Methods
- **Unary RPC**: Single request → single response
- **Server streaming**: Single request → stream of responses
- **Client streaming**: Stream of requests → single response
- **Bidirectional streaming**: Stream of requests ↔ stream of responses

### 4. Built-in Features
- Authentication (TLS, token-based)
- Load balancing and service discovery
- Deadlines/timeouts
- Cancellation
- Error handling with status codes

## Code Examples

### Protocol Buffer Definition
```protobuf
// trading.proto
syntax = "proto3";

package trading;

service TradingService {
  // Unary RPC
  rpc GetMarketPrice(PriceRequest) returns (PriceResponse);
  
  // Server streaming
  rpc StreamMarketData(MarketDataRequest) returns (stream MarketData);
  
  // Client streaming
  rpc PlaceOrders(stream OrderRequest) returns (OrderSummary);
  
  // Bidirectional streaming
  rpc LiveTrading(stream TradeAction) returns (stream TradeResult);
}

message PriceRequest {
  string symbol = 1;
}

message PriceResponse {
  string symbol = 1;
  double price = 2;
  int64 timestamp = 3;
}
```

### Python Implementation
See `grpc_server.py`, `grpc_client.py`, and `grpc_streaming.py` for complete implementations.

## Performance Benefits

### vs REST/HTTP
- **50-90% smaller payloads** (protobuf vs JSON)
- **2-10x faster serialization/deserialization**
- **HTTP/2 multiplexing** eliminates head-of-line blocking
- **Binary framing** reduces parsing overhead

### vs Traditional RPC
- **Type safety** with schema validation
- **Cross-platform compatibility**
- **Built-in streaming** without custom protocols
- **Standardized error handling**

## Real-World Use Cases

### 1. Microservices Communication
- Service-to-service calls in distributed systems
- API gateways and service mesh integration
- Load balancing and circuit breaker patterns

### 2. Real-Time Data Streaming
- Financial market data feeds
- IoT sensor data collection
- Live gaming state synchronization

### 3. Mobile and Web Applications
- Efficient mobile app backends
- Progressive web app APIs
- Reduced bandwidth usage

## Run Instructions

```bash
# Run all gRPC demonstrations
make test

# Individual components
make server    # Start gRPC server
make client    # Run gRPC client examples
make streaming # Demonstrate streaming patterns
make diagrams  # Generate visual diagrams
```

The simulations demonstrate unary calls, streaming patterns, performance characteristics, and real-world trading platform scenarios using gRPC's advanced features.
