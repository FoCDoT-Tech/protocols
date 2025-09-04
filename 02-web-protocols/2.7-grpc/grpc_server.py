#!/usr/bin/env python3
"""
gRPC Server Implementation
Simulates a high-performance trading platform using gRPC with Protocol Buffers
"""

import time
import random
import json
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import queue

class ProtocolBuffer:
    """Simplified Protocol Buffer implementation for demonstration"""
    
    @staticmethod
    def serialize_message(message_type, data):
        """Simulate protobuf binary serialization"""
        # In real implementation, this would use actual protobuf
        serialized = {
            'type': message_type,
            'data': data,
            'timestamp': time.time(),
            'size_bytes': len(json.dumps(data).encode('utf-8')) // 2  # Binary is ~50% smaller
        }
        return serialized
    
    @staticmethod
    def deserialize_message(serialized_data):
        """Simulate protobuf binary deserialization"""
        return serialized_data

class GRPCServer:
    def __init__(self, host="localhost", port=50051):
        self.host = host
        self.port = port
        self.running = False
        self.clients = {}
        self.market_data = {}
        self.orders = []
        self.streams = defaultdict(list)
        
        # Initialize market data
        self.initialize_market_data()
        
    def initialize_market_data(self):
        """Initialize trading market data"""
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX']
        
        for symbol in symbols:
            self.market_data[symbol] = {
                'price': random.uniform(100, 3000),
                'volume': random.randint(1000000, 10000000),
                'bid': 0,
                'ask': 0,
                'last_update': datetime.now()
            }
            
            # Set bid/ask spread
            price = self.market_data[symbol]['price']
            spread = price * 0.001  # 0.1% spread
            self.market_data[symbol]['bid'] = price - spread/2
            self.market_data[symbol]['ask'] = price + spread/2
    
    def start_server(self):
        """Start the gRPC server simulation"""
        print(f"=== gRPC Trading Server ===")
        print(f"Starting server on {self.host}:{self.port}")
        print(f"Protocol: gRPC over HTTP/2")
        print(f"Serialization: Protocol Buffers")
        
        self.running = True
        
        # Start market data update thread
        market_thread = threading.Thread(target=self.update_market_data)
        market_thread.daemon = True
        market_thread.start()
        
        # Simulate server operations
        self.simulate_server_operations()
        
        return {
            'server_info': {
                'host': self.host,
                'port': self.port,
                'protocol': 'gRPC/HTTP2',
                'serialization': 'Protocol Buffers'
            },
            'services': [
                'TradingService.GetMarketPrice',
                'TradingService.StreamMarketData',
                'TradingService.PlaceOrders',
                'TradingService.LiveTrading'
            ]
        }
    
    def update_market_data(self):
        """Continuously update market data"""
        while self.running:
            for symbol in self.market_data:
                # Random price movement
                current_price = self.market_data[symbol]['price']
                change_percent = random.uniform(-0.02, 0.02)  # ±2%
                new_price = current_price * (1 + change_percent)
                
                self.market_data[symbol]['price'] = new_price
                self.market_data[symbol]['bid'] = new_price * 0.999
                self.market_data[symbol]['ask'] = new_price * 1.001
                self.market_data[symbol]['volume'] += random.randint(-10000, 50000)
                self.market_data[symbol]['last_update'] = datetime.now()
            
            time.sleep(0.1)  # Update every 100ms
    
    def simulate_server_operations(self):
        """Simulate various gRPC server operations"""
        print(f"\n--- gRPC Service Methods ---")
        
        # Simulate different types of RPC calls
        operations = [
            self.handle_unary_rpc,
            self.handle_server_streaming,
            self.handle_client_streaming,
            self.handle_bidirectional_streaming
        ]
        
        for operation in operations:
            operation()
            time.sleep(0.5)
    
    def handle_unary_rpc(self):
        """Handle unary RPC: GetMarketPrice"""
        print(f"\n🔄 Unary RPC: GetMarketPrice")
        
        # Simulate client request
        request = {
            'symbol': 'AAPL',
            'request_id': 'req_001'
        }
        
        print(f"📨 Received request: {request}")
        
        # Process request
        symbol = request['symbol']
        if symbol in self.market_data:
            response_data = {
                'symbol': symbol,
                'price': round(self.market_data[symbol]['price'], 2),
                'bid': round(self.market_data[symbol]['bid'], 2),
                'ask': round(self.market_data[symbol]['ask'], 2),
                'volume': self.market_data[symbol]['volume'],
                'timestamp': int(time.time() * 1000)
            }
            
            # Serialize with Protocol Buffers
            response = ProtocolBuffer.serialize_message('PriceResponse', response_data)
            
            print(f"📤 Sending response: {response_data}")
            print(f"📊 Serialized size: {response['size_bytes']} bytes (protobuf)")
            
            # Compare with JSON size
            json_size = len(json.dumps(response_data).encode('utf-8'))
            savings = ((json_size - response['size_bytes']) / json_size) * 100
            print(f"💾 Size savings vs JSON: {savings:.1f}%")
            
            return response
        else:
            # Error response
            error_response = {
                'code': 5,  # NOT_FOUND
                'message': f'Symbol {symbol} not found',
                'details': []
            }
            print(f"❌ Error response: {error_response}")
            return error_response
    
    def handle_server_streaming(self):
        """Handle server streaming RPC: StreamMarketData"""
        print(f"\n📡 Server Streaming RPC: StreamMarketData")
        
        # Simulate client subscription
        request = {
            'symbols': ['AAPL', 'GOOGL', 'MSFT'],
            'update_interval_ms': 100
        }
        
        print(f"📨 Received subscription: {request}")
        print(f"🔄 Starting market data stream...")
        
        # Stream market data updates
        for update_count in range(10):
            for symbol in request['symbols']:
                if symbol in self.market_data:
                    market_update = {
                        'symbol': symbol,
                        'price': round(self.market_data[symbol]['price'], 2),
                        'volume': self.market_data[symbol]['volume'],
                        'timestamp': int(time.time() * 1000),
                        'sequence': update_count
                    }
                    
                    # Serialize and send
                    stream_message = ProtocolBuffer.serialize_message('MarketData', market_update)
                    print(f"📤 Stream update: {symbol} @ ${market_update['price']:.2f}")
            
            time.sleep(0.1)  # 100ms interval
        
        print(f"✅ Stream completed: 30 updates sent")
        
        return {
            'stream_type': 'server_streaming',
            'total_updates': 30,
            'symbols': request['symbols']
        }
    
    def handle_client_streaming(self):
        """Handle client streaming RPC: PlaceOrders"""
        print(f"\n📈 Client Streaming RPC: PlaceOrders")
        
        # Simulate multiple order requests from client
        orders = [
            {'symbol': 'AAPL', 'side': 'BUY', 'quantity': 100, 'price': 150.50},
            {'symbol': 'GOOGL', 'side': 'SELL', 'quantity': 50, 'price': 2800.00},
            {'symbol': 'MSFT', 'side': 'BUY', 'quantity': 200, 'price': 300.25},
            {'symbol': 'TSLA', 'side': 'BUY', 'quantity': 75, 'price': 800.00},
            {'symbol': 'AMZN', 'side': 'SELL', 'quantity': 25, 'price': 3200.00}
        ]
        
        print(f"📨 Receiving order stream...")
        
        processed_orders = []
        total_value = 0
        
        for order in orders:
            print(f"📋 Processing order: {order['side']} {order['quantity']} {order['symbol']} @ ${order['price']:.2f}")
            
            # Simulate order processing
            order_result = {
                'order_id': f"ord_{len(processed_orders) + 1:03d}",
                'symbol': order['symbol'],
                'side': order['side'],
                'quantity': order['quantity'],
                'price': order['price'],
                'status': 'FILLED',
                'fill_time': datetime.now().isoformat()
            }
            
            processed_orders.append(order_result)
            total_value += order['quantity'] * order['price']
            
            time.sleep(0.1)  # Processing delay
        
        # Send summary response
        summary = {
            'total_orders': len(processed_orders),
            'total_value': round(total_value, 2),
            'successful_orders': len([o for o in processed_orders if o['status'] == 'FILLED']),
            'processing_time_ms': len(orders) * 100
        }
        
        print(f"📤 Order summary: {summary}")
        
        return summary
    
    def handle_bidirectional_streaming(self):
        """Handle bidirectional streaming RPC: LiveTrading"""
        print(f"\n🔄 Bidirectional Streaming RPC: LiveTrading")
        
        # Simulate real-time trading session
        print(f"📨 Starting live trading session...")
        
        # Simulate client actions and server responses
        trading_actions = [
            {'action': 'SUBSCRIBE', 'symbols': ['AAPL', 'GOOGL']},
            {'action': 'PLACE_ORDER', 'symbol': 'AAPL', 'side': 'BUY', 'quantity': 100},
            {'action': 'CANCEL_ORDER', 'order_id': 'ord_001'},
            {'action': 'MODIFY_ORDER', 'order_id': 'ord_002', 'new_price': 151.00},
            {'action': 'UNSUBSCRIBE', 'symbols': ['GOOGL']}
        ]
        
        session_results = []
        
        for action in trading_actions:
            print(f"📨 Client action: {action}")
            
            # Process action and generate response
            if action['action'] == 'SUBSCRIBE':
                result = {
                    'type': 'SUBSCRIPTION_CONFIRMED',
                    'symbols': action['symbols'],
                    'timestamp': datetime.now().isoformat()
                }
            elif action['action'] == 'PLACE_ORDER':
                result = {
                    'type': 'ORDER_PLACED',
                    'order_id': f"ord_{random.randint(100, 999)}",
                    'symbol': action['symbol'],
                    'status': 'PENDING',
                    'timestamp': datetime.now().isoformat()
                }
            elif action['action'] == 'CANCEL_ORDER':
                result = {
                    'type': 'ORDER_CANCELLED',
                    'order_id': action['order_id'],
                    'status': 'CANCELLED',
                    'timestamp': datetime.now().isoformat()
                }
            elif action['action'] == 'MODIFY_ORDER':
                result = {
                    'type': 'ORDER_MODIFIED',
                    'order_id': action['order_id'],
                    'new_price': action['new_price'],
                    'status': 'MODIFIED',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                result = {
                    'type': 'UNSUBSCRIBED',
                    'symbols': action['symbols'],
                    'timestamp': datetime.now().isoformat()
                }
            
            print(f"📤 Server response: {result}")
            session_results.append(result)
            
            time.sleep(0.2)  # Response delay
        
        session_summary = {
            'session_duration': len(trading_actions) * 0.2,
            'total_actions': len(trading_actions),
            'total_responses': len(session_results),
            'session_type': 'bidirectional_streaming'
        }
        
        print(f"✅ Trading session completed: {session_summary}")
        
        return session_summary
    
    def get_server_stats(self):
        """Get server performance statistics"""
        return {
            'active_connections': len(self.clients),
            'total_orders': len(self.orders),
            'market_symbols': len(self.market_data),
            'active_streams': sum(len(streams) for streams in self.streams.values()),
            'uptime_seconds': time.time() - getattr(self, 'start_time', time.time())
        }
    
    def stop_server(self):
        """Stop the gRPC server"""
        self.running = False
        print(f"🛑 gRPC server stopped")

def demonstrate_grpc_features():
    """Demonstrate gRPC protocol features"""
    print(f"\n=== gRPC Protocol Features ===")
    
    features = [
        {
            'feature': 'HTTP/2 Transport',
            'benefits': ['Multiplexing', 'Header compression', 'Server push', 'Flow control'],
            'description': 'Efficient binary protocol with stream multiplexing'
        },
        {
            'feature': 'Protocol Buffers',
            'benefits': ['Binary serialization', 'Schema evolution', 'Cross-language', 'Compact size'],
            'description': 'Language-neutral serialization with strong typing'
        },
        {
            'feature': 'Streaming Support',
            'benefits': ['Real-time data', 'Efficient bulk operations', 'Bidirectional communication'],
            'description': 'Four types of streaming patterns for different use cases'
        },
        {
            'feature': 'Built-in Features',
            'benefits': ['Authentication', 'Load balancing', 'Deadlines', 'Cancellation'],
            'description': 'Production-ready features out of the box'
        }
    ]
    
    for feature in features:
        print(f"\n{feature['feature']}:")
        print(f"  Description: {feature['description']}")
        print(f"  Benefits: {', '.join(feature['benefits'])}")
    
    return features

def analyze_grpc_performance():
    """Analyze gRPC performance characteristics"""
    print(f"\n=== gRPC Performance Analysis ===")
    
    # Simulate performance metrics
    scenarios = [
        {
            'name': 'Microservice Communication',
            'requests_per_second': 10000,
            'latency_p99_ms': 5,
            'payload_size_kb': 2,
            'use_case': 'Service-to-service calls'
        },
        {
            'name': 'Real-time Data Streaming',
            'requests_per_second': 50000,
            'latency_p99_ms': 2,
            'payload_size_kb': 0.5,
            'use_case': 'Market data feeds'
        },
        {
            'name': 'Mobile API Backend',
            'requests_per_second': 5000,
            'latency_p99_ms': 10,
            'payload_size_kb': 5,
            'use_case': 'Mobile app communication'
        },
        {
            'name': 'Bulk Data Processing',
            'requests_per_second': 1000,
            'latency_p99_ms': 50,
            'payload_size_kb': 100,
            'use_case': 'Batch operations'
        }
    ]
    
    print(f"{'Scenario':<25} {'RPS':<8} {'P99 Latency':<12} {'Payload':<10} {'Use Case'}")
    print("-" * 80)
    
    for scenario in scenarios:
        print(f"{scenario['name']:<25} {scenario['requests_per_second']:<8} "
              f"{scenario['latency_p99_ms']} ms{'':<7} {scenario['payload_size_kb']} KB{'':<5} "
              f"{scenario['use_case']}")
    
    # Performance benefits
    print(f"\nPerformance Benefits:")
    benefits = [
        "50-90% smaller payloads vs JSON (Protocol Buffers)",
        "2-10x faster serialization/deserialization",
        "HTTP/2 multiplexing eliminates head-of-line blocking",
        "Binary framing reduces parsing overhead",
        "Built-in compression and flow control"
    ]
    
    for benefit in benefits:
        print(f"  • {benefit}")
    
    return scenarios

if __name__ == "__main__":
    # Create and start gRPC server
    server = GRPCServer()
    server_info = server.start_server()
    
    # Demonstrate gRPC features
    features = demonstrate_grpc_features()
    
    # Analyze performance
    performance_scenarios = analyze_grpc_performance()
    
    # Get server statistics
    stats = server.get_server_stats()
    
    print(f"\n=== gRPC Server Summary ===")
    print(f"Server: {server_info['server_info']['host']}:{server_info['server_info']['port']}")
    print(f"Protocol: {server_info['server_info']['protocol']}")
    print(f"Services: {len(server_info['services'])} available")
    print(f"Features demonstrated: {len(features)}")
    print(f"Performance scenarios: {len(performance_scenarios)}")
    print(f"gRPC provides high-performance, type-safe RPC with streaming support over HTTP/2")
