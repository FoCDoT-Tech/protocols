#!/usr/bin/env python3
"""
GraphQL Server Implementation
Simulates a comprehensive e-commerce GraphQL API with queries, mutations, and subscriptions
"""

import time
import random
import json
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import queue

class GraphQLSchema:
    """Simplified GraphQL schema implementation"""
    
    def __init__(self):
        self.types = {}
        self.queries = {}
        self.mutations = {}
        self.subscriptions = {}
        self.data_store = self.initialize_data()
        
    def initialize_data(self):
        """Initialize sample e-commerce data"""
        return {
            'products': {
                '1': {
                    'id': '1',
                    'name': 'MacBook Pro 16"',
                    'price': 2499.00,
                    'description': 'Powerful laptop for professionals',
                    'category': {'id': '1', 'name': 'Electronics'},
                    'inventory': 50,
                    'reviews': [
                        {'id': '1', 'rating': 5, 'comment': 'Excellent performance!'},
                        {'id': '2', 'rating': 4, 'comment': 'Great build quality'}
                    ]
                },
                '2': {
                    'id': '2',
                    'name': 'iPhone 15 Pro',
                    'price': 999.00,
                    'description': 'Latest smartphone with advanced features',
                    'category': {'id': '1', 'name': 'Electronics'},
                    'inventory': 100,
                    'reviews': [
                        {'id': '3', 'rating': 5, 'comment': 'Amazing camera quality!'}
                    ]
                },
                '3': {
                    'id': '3',
                    'name': 'AirPods Pro',
                    'price': 249.00,
                    'description': 'Wireless earbuds with noise cancellation',
                    'category': {'id': '2', 'name': 'Audio'},
                    'inventory': 200,
                    'reviews': []
                }
            },
            'users': {
                '1': {
                    'id': '1',
                    'name': 'Alice Johnson',
                    'email': 'alice@example.com',
                    'orders': ['1', '2']
                },
                '2': {
                    'id': '2',
                    'name': 'Bob Smith',
                    'email': 'bob@example.com',
                    'orders': ['3']
                }
            },
            'orders': {
                '1': {
                    'id': '1',
                    'userId': '1',
                    'products': [{'productId': '1', 'quantity': 1}],
                    'total': 2499.00,
                    'status': 'shipped',
                    'createdAt': '2024-01-15T10:30:00Z'
                },
                '2': {
                    'id': '2',
                    'userId': '1',
                    'products': [{'productId': '2', 'quantity': 1}, {'productId': '3', 'quantity': 2}],
                    'total': 1497.00,
                    'status': 'processing',
                    'createdAt': '2024-01-16T14:20:00Z'
                },
                '3': {
                    'id': '3',
                    'userId': '2',
                    'products': [{'productId': '3', 'quantity': 1}],
                    'total': 249.00,
                    'status': 'delivered',
                    'createdAt': '2024-01-14T09:15:00Z'
                }
            }
        }

class GraphQLServer:
    def __init__(self, host="localhost", port=4000):
        self.host = host
        self.port = port
        self.schema = GraphQLSchema()
        self.subscription_clients = defaultdict(list)
        self.query_cache = {}
        self.metrics = {
            'queries_executed': 0,
            'mutations_executed': 0,
            'subscriptions_active': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
    def start_server(self):
        """Start the GraphQL server"""
        print(f"=== GraphQL E-commerce Server ===")
        print(f"Starting server on {self.host}:{self.port}")
        print(f"GraphQL endpoint: http://{self.host}:{self.port}/graphql")
        print(f"GraphiQL playground: http://{self.host}:{self.port}/graphiql")
        
        # Simulate server operations
        self.demonstrate_server_capabilities()
        
        return {
            'server_info': {
                'host': self.host,
                'port': self.port,
                'endpoint': f"http://{self.host}:{self.port}/graphql",
                'playground': f"http://{self.host}:{self.port}/graphiql"
            },
            'schema_info': {
                'types': len(self.schema.types),
                'queries': len(self.schema.queries),
                'mutations': len(self.schema.mutations),
                'subscriptions': len(self.schema.subscriptions)
            }
        }
    
    def demonstrate_server_capabilities(self):
        """Demonstrate various GraphQL server capabilities"""
        print(f"\n--- GraphQL Server Capabilities ---")
        
        # Demonstrate different operations
        self.handle_introspection_query()
        self.handle_product_query()
        self.handle_complex_query()
        self.handle_mutation()
        self.handle_subscription()
        self.demonstrate_query_optimization()
    
    def handle_introspection_query(self):
        """Handle schema introspection query"""
        print(f"\n🔍 Schema Introspection Query")
        
        introspection_query = """
        query IntrospectionQuery {
          __schema {
            types {
              name
              kind
              fields {
                name
                type {
                  name
                }
              }
            }
          }
        }
        """
        
        print(f"📨 Received introspection query")
        
        # Simulate introspection response
        schema_info = {
            '__schema': {
                'types': [
                    {
                        'name': 'Query',
                        'kind': 'OBJECT',
                        'fields': [
                            {'name': 'product', 'type': {'name': 'Product'}},
                            {'name': 'products', 'type': {'name': '[Product!]!'}},
                            {'name': 'user', 'type': {'name': 'User'}},
                            {'name': 'orders', 'type': {'name': '[Order!]!'}}
                        ]
                    },
                    {
                        'name': 'Product',
                        'kind': 'OBJECT',
                        'fields': [
                            {'name': 'id', 'type': {'name': 'ID!'}},
                            {'name': 'name', 'type': {'name': 'String!'}},
                            {'name': 'price', 'type': {'name': 'Float!'}},
                            {'name': 'description', 'type': {'name': 'String'}},
                            {'name': 'category', 'type': {'name': 'Category!'}},
                            {'name': 'reviews', 'type': {'name': '[Review!]!'}},
                            {'name': 'inventory', 'type': {'name': 'Int!'}}
                        ]
                    }
                ]
            }
        }
        
        print(f"📤 Schema introspection response: {len(schema_info['__schema']['types'])} types")
        self.metrics['queries_executed'] += 1
        
        return schema_info
    
    def handle_product_query(self):
        """Handle simple product query"""
        print(f"\n📱 Product Query")
        
        query = """
        query GetProduct($id: ID!) {
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
        
        variables = {'id': '1'}
        
        print(f"📨 Received product query for ID: {variables['id']}")
        
        # Execute query
        product_id = variables['id']
        if product_id in self.schema.data_store['products']:
            product = self.schema.data_store['products'][product_id]
            
            response = {
                'data': {
                    'product': product
                }
            }
            
            print(f"📤 Product response: {product['name']} - ${product['price']:.2f}")
            print(f"   Category: {product['category']['name']}")
            print(f"   Reviews: {len(product['reviews'])} reviews")
            
            self.metrics['queries_executed'] += 1
            return response
        else:
            error_response = {
                'errors': [
                    {
                        'message': f'Product with ID {product_id} not found',
                        'path': ['product'],
                        'extensions': {'code': 'NOT_FOUND'}
                    }
                ]
            }
            print(f"❌ Product not found: {product_id}")
            return error_response
    
    def handle_complex_query(self):
        """Handle complex nested query"""
        print(f"\n🔗 Complex Nested Query")
        
        query = """
        query GetUserWithOrders($userId: ID!) {
          user(id: $userId) {
            id
            name
            email
            orders {
              id
              total
              status
              products {
                productId
                quantity
                product {
                  name
                  price
                  category {
                    name
                  }
                }
              }
            }
          }
        }
        """
        
        variables = {'userId': '1'}
        
        print(f"📨 Received complex query for user ID: {variables['userId']}")
        
        # Execute complex query with nested resolvers
        user_id = variables['userId']
        if user_id in self.schema.data_store['users']:
            user = self.schema.data_store['users'][user_id].copy()
            
            # Resolve nested orders
            user_orders = []
            for order_id in user['orders']:
                if order_id in self.schema.data_store['orders']:
                    order = self.schema.data_store['orders'][order_id].copy()
                    
                    # Resolve nested products in orders
                    order_products = []
                    for order_product in order['products']:
                        product_id = order_product['productId']
                        if product_id in self.schema.data_store['products']:
                            product = self.schema.data_store['products'][product_id]
                            order_product_with_details = {
                                'productId': product_id,
                                'quantity': order_product['quantity'],
                                'product': product
                            }
                            order_products.append(order_product_with_details)
                    
                    order['products'] = order_products
                    user_orders.append(order)
            
            user['orders'] = user_orders
            
            response = {
                'data': {
                    'user': user
                }
            }
            
            print(f"📤 Complex query response: {user['name']}")
            print(f"   Orders: {len(user['orders'])} orders")
            total_items = sum(len(order['products']) for order in user['orders'])
            print(f"   Total items across orders: {total_items}")
            
            self.metrics['queries_executed'] += 1
            return response
        else:
            error_response = {
                'errors': [
                    {
                        'message': f'User with ID {user_id} not found',
                        'path': ['user'],
                        'extensions': {'code': 'NOT_FOUND'}
                    }
                ]
            }
            print(f"❌ User not found: {user_id}")
            return error_response
    
    def handle_mutation(self):
        """Handle mutation operation"""
        print(f"\n✏️ Mutation Operation")
        
        mutation = """
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
        
        variables = {
            'input': {
                'name': 'iPad Pro 12.9"',
                'price': 1099.00,
                'description': 'Professional tablet with M2 chip',
                'categoryId': '1',
                'inventory': 75
            }
        }
        
        print(f"📨 Received create product mutation")
        print(f"   Product: {variables['input']['name']}")
        print(f"   Price: ${variables['input']['price']:.2f}")
        
        # Execute mutation
        input_data = variables['input']
        new_product_id = str(len(self.schema.data_store['products']) + 1)
        
        new_product = {
            'id': new_product_id,
            'name': input_data['name'],
            'price': input_data['price'],
            'description': input_data['description'],
            'category': {'id': input_data['categoryId'], 'name': 'Electronics'},
            'inventory': input_data['inventory'],
            'reviews': []
        }
        
        # Add to data store
        self.schema.data_store['products'][new_product_id] = new_product
        
        response = {
            'data': {
                'createProduct': new_product
            }
        }
        
        print(f"📤 Product created successfully: ID {new_product_id}")
        print(f"   Total products in store: {len(self.schema.data_store['products'])}")
        
        self.metrics['mutations_executed'] += 1
        
        # Trigger subscription for product updates
        self.notify_subscribers('productCreated', new_product)
        
        return response
    
    def handle_subscription(self):
        """Handle subscription operation"""
        print(f"\n📡 Subscription Operation")
        
        subscription = """
        subscription ProductUpdates {
          productUpdates {
            id
            name
            price
            inventory
            updateType
          }
        }
        """
        
        print(f"📨 Client subscribed to product updates")
        
        # Simulate subscription setup
        client_id = f"client_{random.randint(1000, 9999)}"
        self.subscription_clients['productUpdates'].append(client_id)
        self.metrics['subscriptions_active'] += 1
        
        print(f"🔔 Subscription active for client: {client_id}")
        print(f"   Active subscriptions: {self.metrics['subscriptions_active']}")
        
        # Simulate real-time updates
        updates = [
            {'productId': '1', 'updateType': 'PRICE_CHANGE', 'newPrice': 2399.00},
            {'productId': '2', 'updateType': 'INVENTORY_CHANGE', 'newInventory': 95},
            {'productId': '3', 'updateType': 'PRICE_CHANGE', 'newPrice': 229.00}
        ]
        
        for update in updates:
            product_id = update['productId']
            if product_id in self.schema.data_store['products']:
                product = self.schema.data_store['products'][product_id].copy()
                
                if update['updateType'] == 'PRICE_CHANGE':
                    product['price'] = update['newPrice']
                    self.schema.data_store['products'][product_id]['price'] = update['newPrice']
                elif update['updateType'] == 'INVENTORY_CHANGE':
                    product['inventory'] = update['newInventory']
                    self.schema.data_store['products'][product_id]['inventory'] = update['newInventory']
                
                product['updateType'] = update['updateType']
                
                print(f"📤 Subscription update: {product['name']} - {update['updateType']}")
                
                # Notify all subscribers
                self.notify_subscribers('productUpdates', product)
                
                time.sleep(0.2)  # Simulate real-time delay
        
        return {
            'subscription_id': client_id,
            'updates_sent': len(updates),
            'active_subscribers': len(self.subscription_clients['productUpdates'])
        }
    
    def notify_subscribers(self, subscription_type, data):
        """Notify all subscribers of an event"""
        if subscription_type in self.subscription_clients:
            for client_id in self.subscription_clients[subscription_type]:
                # In real implementation, this would send via WebSocket
                print(f"   📨 Notifying {client_id}: {data.get('name', 'Update')}")
    
    def demonstrate_query_optimization(self):
        """Demonstrate query optimization techniques"""
        print(f"\n⚡ Query Optimization")
        
        # Simulate DataLoader pattern for N+1 problem
        print(f"🔄 DataLoader pattern for efficient data fetching")
        
        # Batch query for multiple products
        product_ids = ['1', '2', '3']
        
        print(f"📨 Batch query for products: {product_ids}")
        
        # Simulate batched database query (instead of N individual queries)
        start_time = time.time()
        
        batched_products = []
        for product_id in product_ids:
            if product_id in self.schema.data_store['products']:
                batched_products.append(self.schema.data_store['products'][product_id])
        
        end_time = time.time()
        query_time = (end_time - start_time) * 1000
        
        print(f"📤 Batched response: {len(batched_products)} products")
        print(f"⏱️ Query time: {query_time:.2f}ms (vs {len(product_ids) * 5:.2f}ms for individual queries)")
        
        # Demonstrate query complexity analysis
        print(f"\n📊 Query Complexity Analysis")
        
        complex_query_cost = {
            'query_depth': 4,
            'field_count': 12,
            'estimated_cost': 150,
            'max_allowed_cost': 1000,
            'status': 'ALLOWED'
        }
        
        print(f"   Query depth: {complex_query_cost['query_depth']}")
        print(f"   Field count: {complex_query_cost['field_count']}")
        print(f"   Estimated cost: {complex_query_cost['estimated_cost']}")
        print(f"   Status: {complex_query_cost['status']}")
        
        return {
            'batch_optimization': {
                'products_fetched': len(batched_products),
                'query_time_ms': query_time,
                'efficiency_gain': f"{((len(product_ids) * 5) - query_time) / (len(product_ids) * 5) * 100:.1f}%"
            },
            'complexity_analysis': complex_query_cost
        }
    
    def get_server_metrics(self):
        """Get server performance metrics"""
        return {
            'queries_executed': self.metrics['queries_executed'],
            'mutations_executed': self.metrics['mutations_executed'],
            'subscriptions_active': self.metrics['subscriptions_active'],
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'cache_hit_ratio': (self.metrics['cache_hits'] / max(1, self.metrics['cache_hits'] + self.metrics['cache_misses'])) * 100,
            'data_store_size': {
                'products': len(self.schema.data_store['products']),
                'users': len(self.schema.data_store['users']),
                'orders': len(self.schema.data_store['orders'])
            }
        }

def demonstrate_graphql_features():
    """Demonstrate GraphQL protocol features"""
    print(f"\n=== GraphQL Protocol Features ===")
    
    features = [
        {
            'feature': 'Single Endpoint',
            'description': 'All operations through one HTTP endpoint',
            'benefits': ['Simplified client logic', 'Reduced API surface', 'Centralized access control']
        },
        {
            'feature': 'Strong Type System',
            'description': 'Schema-first development with type safety',
            'benefits': ['Compile-time validation', 'Auto-generated documentation', 'IDE support']
        },
        {
            'feature': 'Flexible Queries',
            'description': 'Client specifies exactly what data to fetch',
            'benefits': ['No over-fetching', 'No under-fetching', 'Optimized bandwidth usage']
        },
        {
            'feature': 'Real-time Subscriptions',
            'description': 'Live data updates via WebSocket or SSE',
            'benefits': ['Real-time UX', 'Event-driven architecture', 'Efficient updates']
        }
    ]
    
    for feature in features:
        print(f"\n{feature['feature']}:")
        print(f"  Description: {feature['description']}")
        print(f"  Benefits: {', '.join(feature['benefits'])}")
    
    return features

if __name__ == "__main__":
    # Create and start GraphQL server
    server = GraphQLServer()
    server_info = server.start_server()
    
    # Demonstrate GraphQL features
    features = demonstrate_graphql_features()
    
    # Get server metrics
    metrics = server.get_server_metrics()
    
    print(f"\n=== GraphQL Server Summary ===")
    print(f"Server: {server_info['server_info']['endpoint']}")
    print(f"Playground: {server_info['server_info']['playground']}")
    print(f"Queries executed: {metrics['queries_executed']}")
    print(f"Mutations executed: {metrics['mutations_executed']}")
    print(f"Active subscriptions: {metrics['subscriptions_active']}")
    print(f"Data store: {metrics['data_store_size']['products']} products, {metrics['data_store_size']['users']} users, {metrics['data_store_size']['orders']} orders")
    print(f"GraphQL provides flexible, efficient APIs with strong typing and real-time capabilities")
