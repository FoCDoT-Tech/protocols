# GraphQL

## Definition
GraphQL is a query language for APIs and a runtime for executing those queries with existing data. Developed by Facebook in 2012 and open-sourced in 2015, GraphQL provides a complete and understandable description of the data in your API, gives clients the power to ask for exactly what they need, and enables powerful developer tools.

## RFCs and Standards
- **GraphQL Specification**: https://spec.graphql.org/
- **GraphQL over HTTP**: https://graphql.github.io/graphql-over-http/
- **GraphQL Foundation**: https://graphql.org/
- **RFC 7231 (HTTP/1.1)**: Underlying transport protocol

## Real-World Engineering Scenario
You're building a modern e-commerce platform with multiple client applications (web, mobile, admin dashboard). Traditional REST APIs create challenges:

- **Over-fetching**: Mobile apps get unnecessary data, wasting bandwidth
- **Under-fetching**: Multiple round trips needed for related data
- **API versioning**: Breaking changes when adding/removing fields
- **Client-specific endpoints**: Proliferation of custom endpoints

GraphQL solves these problems by providing:
- **Single endpoint** for all data operations
- **Client-specified queries** to fetch exactly needed data
- **Strong type system** with introspection capabilities
- **Real-time subscriptions** for live data updates
- **Backward compatibility** through schema evolution

## Key Features

### 1. Query Language
- Declarative data fetching
- Hierarchical structure matching response shape
- Field selection and aliasing
- Variables and directives

### 2. Type System
- Strong typing with schema definition
- Scalar types, object types, interfaces, unions
- Input types and enums
- Schema introspection

### 3. Single Endpoint
- All operations through one HTTP endpoint
- POST requests with query in body
- GET requests for simple queries
- Eliminates REST endpoint proliferation

### 4. Real-time Capabilities
- Subscriptions for live data updates
- WebSocket or Server-Sent Events transport
- Event-driven data synchronization

## Code Examples

### GraphQL Schema Definition
```graphql
# E-commerce schema
type Query {
  product(id: ID!): Product
  products(filter: ProductFilter, limit: Int): [Product!]!
  user(id: ID!): User
  orders(userId: ID!): [Order!]!
}

type Mutation {
  createProduct(input: ProductInput!): Product!
  updateProduct(id: ID!, input: ProductInput!): Product!
  placeOrder(input: OrderInput!): Order!
}

type Subscription {
  orderUpdates(userId: ID!): Order!
  productPriceChanges(productId: ID!): Product!
}

type Product {
  id: ID!
  name: String!
  price: Float!
  description: String
  category: Category!
  reviews: [Review!]!
  inventory: Int!
}
```

### Python Implementation
See `graphql_server.py`, `graphql_client.py`, and `graphql_subscriptions.py` for complete implementations.

## GraphQL vs REST Comparison

### Data Fetching
- **REST**: Multiple endpoints, fixed data structure
- **GraphQL**: Single endpoint, flexible data selection

### Network Efficiency
- **REST**: Over-fetching common, multiple round trips
- **GraphQL**: Precise data fetching, single request

### Versioning
- **REST**: URL versioning, breaking changes
- **GraphQL**: Schema evolution, backward compatibility

### Caching
- **REST**: HTTP caching, URL-based
- **GraphQL**: Query-based caching, more complex

## Performance Characteristics

### Advantages
- **Reduced bandwidth**: 20-50% less data transfer
- **Fewer round trips**: Single request for complex data
- **Mobile optimization**: Critical for bandwidth-constrained clients
- **Developer productivity**: Strong typing and tooling

### Considerations
- **Query complexity**: N+1 problem without proper resolvers
- **Caching complexity**: Query-based invalidation needed
- **Learning curve**: Different paradigm from REST
- **Server-side optimization**: DataLoader patterns required

## Real-World Use Cases

### 1. Mobile Applications
- Bandwidth optimization for mobile networks
- Battery life preservation
- Offline-first architectures

### 2. Microservices Aggregation
- API gateway pattern
- Service composition
- Cross-service data fetching

### 3. Real-time Applications
- Live dashboards and analytics
- Collaborative tools
- Gaming and social platforms

## Run Instructions

```bash
# Run all GraphQL demonstrations
make test

# Individual components
make server        # Start GraphQL server
make client        # Run GraphQL client examples
make subscriptions # Demonstrate real-time subscriptions
make diagrams      # Generate visual diagrams
```

The simulations demonstrate query execution, mutations, subscriptions, schema introspection, and performance optimization techniques for modern API development.
