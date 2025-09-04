#!/usr/bin/env python3
"""
GraphQL Client Implementation
Demonstrates client-side GraphQL operations and optimization techniques
"""

import time
import random
import json
import hashlib
from datetime import datetime, timedelta
from collections import deque

class GraphQLClient:
    def __init__(self, endpoint="http://localhost:4000/graphql"):
        self.endpoint = endpoint
        self.query_cache = {}
        self.request_history = deque(maxlen=1000)
        self.client_id = f"client_{random.randint(1000, 9999)}"
        self.persisted_queries = {}
        
    def connect_to_server(self):
        """Establish connection to GraphQL server"""
        print(f"=== GraphQL Client Connection ===")
        print(f"Client ID: {self.client_id}")
        print(f"GraphQL endpoint: {self.endpoint}")
        print(f"Protocol: HTTP/HTTPS")
        
        connection_info = {
            'client_id': self.client_id,
            'endpoint': self.endpoint,
            'protocol': 'HTTP',
            'connection_time': datetime.now().isoformat(),
            'features': ['Queries', 'Mutations', 'Subscriptions', 'Caching']
        }
        
        print(f"✅ Connected to GraphQL server")
        print(f"📡 Supported operations: {', '.join(connection_info['features'])}")
        
        return connection_info
    
    def execute_query(self, query, variables=None, operation_name=None):
        """Execute a GraphQL query"""
        request_payload = {
            'query': query,
            'variables': variables or {},
            'operationName': operation_name
        }
        
        # Generate query hash for caching
        query_hash = hashlib.md5(json.dumps(request_payload, sort_keys=True).encode()).hexdigest()
        
        # Check cache first
        if query_hash in self.query_cache:
            print(f"💾 Cache hit for query")
            cached_result = self.query_cache[query_hash]
            cached_result['from_cache'] = True
            return cached_result
        
        # Simulate HTTP request
        start_time = time.time()
        
        # Simulate network latency
        time.sleep(random.uniform(0.01, 0.05))  # 10-50ms latency
        
        # Mock response based on query type
        response = self.mock_graphql_response(query, variables)
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Store in cache
        response['latency_ms'] = latency_ms
        response['from_cache'] = False
        self.query_cache[query_hash] = response
        
        # Record request
        request_info = {
            'query_hash': query_hash,
            'operation_name': operation_name,
            'variables': variables,
            'latency_ms': latency_ms,
            'timestamp': datetime.now().isoformat(),
            'cached': False
        }
        self.request_history.append(request_info)
        
        return response
    
    def mock_graphql_response(self, query, variables):
        """Generate mock GraphQL response based on query"""
        if 'product(' in query:
            return {
                'data': {
                    'product': {
                        'id': variables.get('id', '1'),
                        'name': 'MacBook Pro 16"',
                        'price': 2499.00,
                        'description': 'Powerful laptop for professionals',
                        'category': {'name': 'Electronics'},
                        'reviews': [
                            {'rating': 5, 'comment': 'Excellent performance!'}
                        ]
                    }
                }
            }
        elif 'products' in query:
            return {
                'data': {
                    'products': [
                        {'id': '1', 'name': 'MacBook Pro 16"', 'price': 2499.00},
                        {'id': '2', 'name': 'iPhone 15 Pro', 'price': 999.00},
                        {'id': '3', 'name': 'AirPods Pro', 'price': 249.00}
                    ]
                }
            }
        elif 'user(' in query:
            return {
                'data': {
                    'user': {
                        'id': variables.get('id', '1'),
                        'name': 'Alice Johnson',
                        'email': 'alice@example.com',
                        'orders': [
                            {
                                'id': '1',
                                'total': 2499.00,
                                'status': 'shipped',
                                'products': [
                                    {
                                        'productId': '1',
                                        'quantity': 1,
                                        'product': {'name': 'MacBook Pro 16"', 'price': 2499.00}
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        elif 'createProduct' in query:
            return {
                'data': {
                    'createProduct': {
                        'id': '4',
                        'name': variables.get('input', {}).get('name', 'New Product'),
                        'price': variables.get('input', {}).get('price', 0),
                        'category': {'name': 'Electronics'},
                        'inventory': variables.get('input', {}).get('inventory', 0)
                    }
                }
            }
        else:
            return {'data': None}
    
    def demonstrate_basic_queries(self):
        """Demonstrate basic GraphQL queries"""
        print(f"\n=== Basic GraphQL Queries ===")
        
        # Simple product query
        print(f"\n📱 Simple Product Query")
        product_query = """
        query GetProduct($id: ID!) {
          product(id: $id) {
            id
            name
            price
            description
          }
        }
        """
        
        result = self.execute_query(product_query, {'id': '1'}, 'GetProduct')
        product = result['data']['product']
        print(f"📤 Product: {product['name']} - ${product['price']:.2f}")
        print(f"⏱️ Latency: {result['latency_ms']:.2f}ms")
        
        # Products list query
        print(f"\n📋 Products List Query")
        products_query = """
        query GetProducts($limit: Int) {
          products(limit: $limit) {
            id
            name
            price
          }
        }
        """
        
        result = self.execute_query(products_query, {'limit': 10}, 'GetProducts')
        products = result['data']['products']
        print(f"📤 Products: {len(products)} items")
        for product in products:
            print(f"   • {product['name']}: ${product['price']:.2f}")
        print(f"⏱️ Latency: {result['latency_ms']:.2f}ms")
        
        return {'simple_query': product, 'list_query': products}
    
    def demonstrate_complex_queries(self):
        """Demonstrate complex nested GraphQL queries"""
        print(f"\n=== Complex Nested Queries ===")
        
        # Complex user with orders query
        print(f"\n🔗 User with Orders Query")
        complex_query = """
        query GetUserWithOrders($userId: ID!) {
          user(id: $userId) {
            id
            name
            email
            orders {
              id
              total
              status
              items {
                productId
                quantity
                price
              }
            }
          }
        }
        """
        
        result = self.execute_query(complex_query, {'userId': '1'}, 'GetUserWithOrders')
        user = result.get('data', {}).get('user', {})
        
        if user and 'name' in user:
            print(f"📤 User: {user['name']} ({user.get('email', 'N/A')})")
            print(f"   Orders: {len(user.get('orders', []))}")
            
            total_spent = 0
            for order in user.get('orders', []):
                print(f"   • Order {order['id']}: ${order['total']:.2f} ({order['status']})")
                total_spent += order['total']
        else:
            print(f"📤 User data not available in response")
            total_spent = 0
        
        print(f"   Total spent: ${total_spent:.2f}")
        print(f"⏱️ Latency: {result['latency_ms']:.2f}ms")
        
        return user
    
    def demonstrate_mutations(self):
        """Demonstrate GraphQL mutations"""
        print(f"\n=== GraphQL Mutations ===")
        
        # Create product mutation
        print(f"\n✏️ Create Product Mutation")
        create_mutation = """
        mutation CreateProduct($input: ProductInput!) {
          createProduct(input: $input) {
            id
            name
            price
            category {
              name
            }
            inventory
          }
        }
        """
        
        product_input = {
            'name': 'iPad Pro 12.9"',
            'price': 1099.00,
            'description': 'Professional tablet with M2 chip',
            'categoryId': '1',
            'inventory': 75
        }
        
        result = self.execute_query(create_mutation, {'input': product_input}, 'CreateProduct')
        new_product = result['data']['createProduct']
        
        print(f"📤 Created product: {new_product['name']}")
        print(f"   ID: {new_product['id']}")
        print(f"   Price: ${new_product['price']:.2f}")
        print(f"   Inventory: {new_product['inventory']} units")
        print(f"⏱️ Latency: {result['latency_ms']:.2f}ms")
        
        return new_product
    
    def demonstrate_query_optimization(self):
        """Demonstrate GraphQL query optimization techniques"""
        print(f"\n=== Query Optimization Techniques ===")
        
        # Field selection optimization
        print(f"\n🎯 Field Selection Optimization")
        
        # Over-fetching example (bad)
        over_fetch_query = """
        query GetProductsOverFetch {
          products {
            id
            name
            price
            description
            category {
              id
              name
              description
            }
            reviews {
              id
              rating
              comment
              createdAt
              user {
                id
                name
                email
              }
            }
            inventory
            createdAt
            updatedAt
          }
        }
        """
        
        # Optimized query (good)
        optimized_query = """
        query GetProductsOptimized {
          products {
            id
            name
            price
          }
        }
        """
        
        print(f"📊 Comparing query efficiency:")
        
        # Execute over-fetching query
        start_time = time.time()
        over_fetch_result = self.execute_query(over_fetch_query, {}, 'GetProductsOverFetch')
        over_fetch_time = time.time() - start_time
        
        # Execute optimized query
        start_time = time.time()
        optimized_result = self.execute_query(optimized_query, {}, 'GetProductsOptimized')
        optimized_time = time.time() - start_time
        
        # Calculate data transfer savings
        over_fetch_size = len(json.dumps(over_fetch_result).encode('utf-8'))
        optimized_size = len(json.dumps(optimized_result).encode('utf-8'))
        savings = ((over_fetch_size - optimized_size) / over_fetch_size) * 100
        
        print(f"   Over-fetching query: {over_fetch_size} bytes, {over_fetch_time*1000:.2f}ms")
        print(f"   Optimized query: {optimized_size} bytes, {optimized_time*1000:.2f}ms")
        print(f"   Data savings: {savings:.1f}%")
        
        return {
            'over_fetch_size': over_fetch_size,
            'optimized_size': optimized_size,
            'savings_percent': savings
        }
    
    def demonstrate_query_batching(self):
        """Demonstrate query batching for performance"""
        print(f"\n⚡ Query Batching")
        
        # Individual queries (inefficient)
        print(f"📊 Individual vs Batched Queries:")
        
        individual_queries = [
            ('query GetProduct1 { product(id: "1") { id name price } }', {}),
            ('query GetProduct2 { product(id: "2") { id name price } }', {}),
            ('query GetProduct3 { product(id: "3") { id name price } }', {})
        ]
        
        # Execute individual queries
        start_time = time.time()
        individual_results = []
        for query, variables in individual_queries:
            result = self.execute_query(query, variables)
            individual_results.append(result)
        individual_time = time.time() - start_time
        
        # Batched query (efficient)
        batched_query = """
        query GetMultipleProducts {
          product1: product(id: "1") { id name price }
          product2: product(id: "2") { id name price }
          product3: product(id: "3") { id name price }
        }
        """
        
        start_time = time.time()
        batched_result = self.execute_query(batched_query, {})
        batched_time = time.time() - start_time
        
        efficiency_gain = ((individual_time - batched_time) / individual_time) * 100
        
        print(f"   Individual queries: {individual_time*1000:.2f}ms ({len(individual_queries)} requests)")
        print(f"   Batched query: {batched_time*1000:.2f}ms (1 request)")
        print(f"   Efficiency gain: {efficiency_gain:.1f}%")
        
        return {
            'individual_time_ms': individual_time * 1000,
            'batched_time_ms': batched_time * 1000,
            'efficiency_gain_percent': efficiency_gain
        }
    
    def demonstrate_persisted_queries(self):
        """Demonstrate persisted queries for performance"""
        print(f"\n💾 Persisted Queries")
        
        # Regular query
        regular_query = """
        query GetProductDetails($id: ID!) {
          product(id: $id) {
            id
            name
            price
            description
            category {
              name
            }
            reviews {
              rating
              comment
            }
          }
        }
        """
        
        # Generate query hash for persisted query
        query_hash = hashlib.sha256(regular_query.encode()).hexdigest()[:16]
        self.persisted_queries[query_hash] = regular_query
        
        print(f"📝 Registered persisted query: {query_hash}")
        
        # Simulate persisted query request (only hash sent)
        persisted_request = {
            'queryHash': query_hash,
            'variables': {'id': '1'}
        }
        
        # Calculate bandwidth savings
        regular_size = len(json.dumps({'query': regular_query, 'variables': {'id': '1'}}).encode('utf-8'))
        persisted_size = len(json.dumps(persisted_request).encode('utf-8'))
        bandwidth_savings = ((regular_size - persisted_size) / regular_size) * 100
        
        print(f"📊 Bandwidth comparison:")
        print(f"   Regular query: {regular_size} bytes")
        print(f"   Persisted query: {persisted_size} bytes")
        print(f"   Bandwidth savings: {bandwidth_savings:.1f}%")
        
        return {
            'query_hash': query_hash,
            'regular_size': regular_size,
            'persisted_size': persisted_size,
            'bandwidth_savings_percent': bandwidth_savings
        }
    
    def analyze_client_performance(self):
        """Analyze client-side performance metrics"""
        print(f"\n=== Client Performance Analysis ===")
        
        if not self.request_history:
            print("No requests recorded yet")
            return {}
        
        # Calculate performance metrics
        latencies = [req['latency_ms'] for req in self.request_history]
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        # Cache performance
        total_requests = len(self.request_history)
        cache_hits = len(self.query_cache)
        cache_hit_ratio = (cache_hits / total_requests) * 100 if total_requests > 0 else 0
        
        print(f"Request Performance:")
        print(f"  Total requests: {total_requests}")
        print(f"  Average latency: {avg_latency:.2f}ms")
        print(f"  Min latency: {min_latency:.2f}ms")
        print(f"  Max latency: {max_latency:.2f}ms")
        
        print(f"\nCache Performance:")
        print(f"  Cached queries: {cache_hits}")
        print(f"  Cache hit ratio: {cache_hit_ratio:.1f}%")
        
        return {
            'total_requests': total_requests,
            'avg_latency_ms': avg_latency,
            'min_latency_ms': min_latency,
            'max_latency_ms': max_latency,
            'cache_hits': cache_hits,
            'cache_hit_ratio_percent': cache_hit_ratio
        }
    
    def get_client_statistics(self):
        """Get comprehensive client statistics"""
        return {
            'client_id': self.client_id,
            'endpoint': self.endpoint,
            'total_requests': len(self.request_history),
            'cached_queries': len(self.query_cache),
            'persisted_queries': len(self.persisted_queries),
            'features_used': ['Queries', 'Mutations', 'Caching', 'Batching', 'Persisted Queries']
        }

def compare_graphql_vs_rest():
    """Compare GraphQL vs REST API approaches"""
    print(f"\n=== GraphQL vs REST Comparison ===")
    
    scenarios = [
        {
            'scenario': 'Mobile App Product List',
            'rest_requests': 3,
            'rest_data_kb': 45,
            'graphql_requests': 1,
            'graphql_data_kb': 12,
            'description': 'Product list with categories and reviews'
        },
        {
            'scenario': 'User Profile with Orders',
            'rest_requests': 5,
            'rest_data_kb': 78,
            'graphql_requests': 1,
            'graphql_data_kb': 23,
            'description': 'User info, orders, and product details'
        },
        {
            'scenario': 'Dashboard Analytics',
            'rest_requests': 8,
            'rest_data_kb': 120,
            'graphql_requests': 1,
            'graphql_data_kb': 35,
            'description': 'Multiple metrics and aggregations'
        }
    ]
    
    print(f"{'Scenario':<25} {'REST Reqs':<10} {'REST Data':<10} {'GraphQL Reqs':<12} {'GraphQL Data':<12} {'Savings'}")
    print("-" * 90)
    
    for scenario in scenarios:
        data_savings = ((scenario['rest_data_kb'] - scenario['graphql_data_kb']) / scenario['rest_data_kb']) * 100
        req_savings = ((scenario['rest_requests'] - scenario['graphql_requests']) / scenario['rest_requests']) * 100
        
        print(f"{scenario['scenario']:<25} {scenario['rest_requests']:<10} {scenario['rest_data_kb']} KB{'':<5} "
              f"{scenario['graphql_requests']:<12} {scenario['graphql_data_kb']} KB{'':<7} "
              f"{data_savings:.0f}% data, {req_savings:.0f}% reqs")
    
    return scenarios

if __name__ == "__main__":
    # Create GraphQL client
    client = GraphQLClient()
    
    # Connect to server
    connection_info = client.connect_to_server()
    
    # Demonstrate GraphQL operations
    basic_results = client.demonstrate_basic_queries()
    complex_results = client.demonstrate_complex_queries()
    mutation_results = client.demonstrate_mutations()
    
    # Demonstrate optimizations
    optimization_results = client.demonstrate_query_optimization()
    batching_results = client.demonstrate_query_batching()
    persisted_results = client.demonstrate_persisted_queries()
    
    # Analyze performance
    performance_metrics = client.analyze_client_performance()
    
    # Compare with REST
    comparison = compare_graphql_vs_rest()
    
    # Get client statistics
    stats = client.get_client_statistics()
    
    print(f"\n=== GraphQL Client Summary ===")
    print(f"Client ID: {stats['client_id']}")
    print(f"Endpoint: {stats['endpoint']}")
    print(f"Total requests: {stats['total_requests']}")
    print(f"Cached queries: {stats['cached_queries']}")
    print(f"Persisted queries: {stats['persisted_queries']}")
    print(f"Average latency: {performance_metrics.get('avg_latency_ms', 0):.2f}ms")
    print(f"Features demonstrated: {', '.join(stats['features_used'])}")
    print(f"GraphQL enables efficient, flexible APIs with powerful client-side optimizations")
