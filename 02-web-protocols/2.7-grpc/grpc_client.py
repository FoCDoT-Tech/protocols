#!/usr/bin/env python3
"""
gRPC Client Implementation
Demonstrates client-side gRPC communication patterns and features
"""

import time
import random
import json
import threading
from datetime import datetime, timedelta
from collections import deque

class GRPCClient:
    def __init__(self, server_host="localhost", server_port=50051):
        self.server_host = server_host
        self.server_port = server_port
        self.connection_pool = []
        self.request_history = deque(maxlen=1000)
        self.client_id = f"client_{random.randint(1000, 9999)}"
        
    def connect_to_server(self):
        """Establish gRPC connection to server"""
        print(f"=== gRPC Client Connection ===")
        print(f"Client ID: {self.client_id}")
        print(f"Connecting to: {self.server_host}:{self.server_port}")
        print(f"Protocol: gRPC over HTTP/2")
        
        # Simulate HTTP/2 connection establishment
        connection_info = {
            'client_id': self.client_id,
            'server': f"{self.server_host}:{self.server_port}",
            'protocol': 'HTTP/2',
            'tls_enabled': True,
            'connection_time': datetime.now().isoformat(),
            'multiplexing': True,
            'header_compression': 'HPACK'
        }
        
        print(f"✅ Connected successfully")
        print(f"🔒 TLS encryption: Enabled")
        print(f"🔄 HTTP/2 multiplexing: Active")
        print(f"📦 Header compression: HPACK")
        
        return connection_info
    
    def demonstrate_unary_calls(self):
        """Demonstrate unary RPC calls"""
        print(f"\n=== Unary RPC Calls ===")
        
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
        results = []
        
        for symbol in symbols:
            print(f"\n📞 Calling GetMarketPrice for {symbol}")
            
            # Create request
            request = {
                'symbol': symbol,
                'request_id': f"req_{len(self.request_history) + 1}",
                'timestamp': int(time.time() * 1000)
            }
            
            # Simulate gRPC call
            start_time = time.time()
            
            # Simulate network latency and processing
            time.sleep(random.uniform(0.001, 0.005))  # 1-5ms latency
            
            # Mock response
            response = {
                'symbol': symbol,
                'price': round(random.uniform(100, 3000), 2),
                'bid': 0,
                'ask': 0,
                'volume': random.randint(1000000, 10000000),
                'timestamp': int(time.time() * 1000)
            }
            response['bid'] = round(response['price'] * 0.999, 2)
            response['ask'] = round(response['price'] * 1.001, 2)
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            print(f"📈 Response: {symbol} @ ${response['price']:.2f}")
            print(f"⏱️ Latency: {latency_ms:.2f}ms")
            
            # Store request info
            call_info = {
                'method': 'GetMarketPrice',
                'request': request,
                'response': response,
                'latency_ms': latency_ms,
                'success': True
            }
            
            self.request_history.append(call_info)
            results.append(call_info)
        
        return results
    
    def demonstrate_server_streaming(self):
        """Demonstrate server streaming RPC"""
        print(f"\n=== Server Streaming RPC ===")
        
        # Subscribe to market data stream
        subscription_request = {
            'symbols': ['AAPL', 'GOOGL', 'MSFT'],
            'update_interval_ms': 100,
            'client_id': self.client_id
        }
        
        print(f"📡 Subscribing to market data stream")
        print(f"📊 Symbols: {', '.join(subscription_request['symbols'])}")
        print(f"⏱️ Update interval: {subscription_request['update_interval_ms']}ms")
        
        # Simulate receiving stream of market data
        stream_updates = []
        
        print(f"\n📈 Receiving market data updates...")
        
        for update_num in range(15):
            for symbol in subscription_request['symbols']:
                # Simulate receiving update
                update = {
                    'symbol': symbol,
                    'price': round(random.uniform(100, 3000), 2),
                    'volume': random.randint(100000, 1000000),
                    'timestamp': int(time.time() * 1000),
                    'sequence': update_num,
                    'stream_id': f"stream_{self.client_id}"
                }
                
                print(f"📊 {symbol}: ${update['price']:.2f} (vol: {update['volume']:,})")
                stream_updates.append(update)
            
            time.sleep(0.1)  # 100ms interval
            
            if update_num % 5 == 4:  # Show progress every 5 updates
                print(f"   ... received {(update_num + 1) * len(subscription_request['symbols'])} updates")
        
        print(f"✅ Stream completed: {len(stream_updates)} total updates")
        
        return {
            'subscription': subscription_request,
            'total_updates': len(stream_updates),
            'symbols_count': len(subscription_request['symbols']),
            'stream_duration_seconds': 1.5
        }
    
    def demonstrate_client_streaming(self):
        """Demonstrate client streaming RPC"""
        print(f"\n=== Client Streaming RPC ===")
        
        # Prepare batch of orders to stream
        orders = [
            {'symbol': 'AAPL', 'side': 'BUY', 'quantity': 100, 'order_type': 'MARKET'},
            {'symbol': 'GOOGL', 'side': 'SELL', 'quantity': 50, 'order_type': 'LIMIT', 'price': 2800.00},
            {'symbol': 'MSFT', 'side': 'BUY', 'quantity': 200, 'order_type': 'MARKET'},
            {'symbol': 'TSLA', 'side': 'BUY', 'quantity': 75, 'order_type': 'LIMIT', 'price': 800.00},
            {'symbol': 'AMZN', 'side': 'SELL', 'quantity': 25, 'order_type': 'STOP', 'stop_price': 3200.00},
            {'symbol': 'META', 'side': 'BUY', 'quantity': 150, 'order_type': 'MARKET'},
            {'symbol': 'NVDA', 'side': 'SELL', 'quantity': 80, 'order_type': 'LIMIT', 'price': 500.00}
        ]
        
        print(f"📤 Streaming {len(orders)} orders to server")
        print(f"🔄 Using client streaming RPC: PlaceOrders")
        
        # Stream orders to server
        streamed_orders = []
        
        for i, order in enumerate(orders):
            # Add client metadata
            order_request = {
                'client_id': self.client_id,
                'order_sequence': i + 1,
                'timestamp': int(time.time() * 1000),
                **order
            }
            
            print(f"📋 Streaming order {i+1}: {order['side']} {order['quantity']} {order['symbol']}")
            
            streamed_orders.append(order_request)
            time.sleep(0.05)  # Small delay between orders
        
        # Simulate receiving final response
        time.sleep(0.2)  # Processing time
        
        order_summary = {
            'total_orders_received': len(streamed_orders),
            'successful_orders': len(streamed_orders) - 1,  # Simulate one failure
            'failed_orders': 1,
            'total_value': sum(order.get('quantity', 0) * order.get('price', 150) 
                              for order in streamed_orders),
            'processing_time_ms': len(orders) * 50 + 200,
            'client_id': self.client_id
        }
        
        print(f"\n📊 Order Summary Response:")
        print(f"   Total orders: {order_summary['total_orders_received']}")
        print(f"   Successful: {order_summary['successful_orders']}")
        print(f"   Failed: {order_summary['failed_orders']}")
        print(f"   Processing time: {order_summary['processing_time_ms']}ms")
        
        return order_summary
    
    def demonstrate_bidirectional_streaming(self):
        """Demonstrate bidirectional streaming RPC"""
        print(f"\n=== Bidirectional Streaming RPC ===")
        
        print(f"🔄 Starting live trading session")
        print(f"📡 Bidirectional stream: LiveTrading")
        
        # Simulate interactive trading session
        trading_session = []
        server_responses = []
        
        # Trading actions to send
        actions = [
            {'action': 'SUBSCRIBE', 'symbols': ['AAPL', 'GOOGL', 'MSFT']},
            {'action': 'SET_RISK_LIMITS', 'max_position': 1000, 'max_loss': 10000},
            {'action': 'PLACE_ORDER', 'symbol': 'AAPL', 'side': 'BUY', 'quantity': 100},
            {'action': 'REQUEST_QUOTE', 'symbol': 'GOOGL', 'quantity': 50},
            {'action': 'PLACE_ORDER', 'symbol': 'MSFT', 'side': 'SELL', 'quantity': 200},
            {'action': 'CANCEL_ORDER', 'order_id': 'ord_123'},
            {'action': 'GET_POSITIONS'},
            {'action': 'UNSUBSCRIBE', 'symbols': ['MSFT']}
        ]
        
        for i, action in enumerate(actions):
            # Send action to server
            client_message = {
                'client_id': self.client_id,
                'sequence': i + 1,
                'timestamp': int(time.time() * 1000),
                **action
            }
            
            print(f"📤 Sending: {action['action']}")
            trading_session.append(client_message)
            
            # Simulate small delay
            time.sleep(0.1)
            
            # Simulate server response
            if action['action'] == 'SUBSCRIBE':
                response = {
                    'type': 'SUBSCRIPTION_ACK',
                    'symbols': action['symbols'],
                    'status': 'ACTIVE'
                }
            elif action['action'] == 'PLACE_ORDER':
                response = {
                    'type': 'ORDER_ACK',
                    'order_id': f"ord_{random.randint(1000, 9999)}",
                    'symbol': action['symbol'],
                    'status': 'PENDING'
                }
            elif action['action'] == 'REQUEST_QUOTE':
                response = {
                    'type': 'QUOTE',
                    'symbol': action['symbol'],
                    'bid': round(random.uniform(100, 3000), 2),
                    'ask': round(random.uniform(100, 3000), 2),
                    'quantity': action['quantity']
                }
            elif action['action'] == 'GET_POSITIONS':
                response = {
                    'type': 'POSITIONS',
                    'positions': [
                        {'symbol': 'AAPL', 'quantity': 100, 'avg_price': 150.25},
                        {'symbol': 'GOOGL', 'quantity': -50, 'avg_price': 2800.50}
                    ]
                }
            else:
                response = {
                    'type': 'ACK',
                    'action': action['action'],
                    'status': 'SUCCESS'
                }
            
            response['timestamp'] = int(time.time() * 1000)
            response['client_id'] = self.client_id
            
            print(f"📥 Received: {response['type']}")
            server_responses.append(response)
            
            # Simulate market data updates during session
            if i % 3 == 0:
                market_update = {
                    'type': 'MARKET_DATA',
                    'symbol': random.choice(['AAPL', 'GOOGL', 'MSFT']),
                    'price': round(random.uniform(100, 3000), 2),
                    'timestamp': int(time.time() * 1000)
                }
                print(f"📊 Market update: {market_update['symbol']} @ ${market_update['price']:.2f}")
                server_responses.append(market_update)
        
        session_summary = {
            'session_duration_seconds': len(actions) * 0.1,
            'client_messages_sent': len(trading_session),
            'server_responses_received': len(server_responses),
            'actions_performed': len(actions),
            'session_type': 'bidirectional_streaming'
        }
        
        print(f"\n✅ Trading session completed")
        print(f"   Duration: {session_summary['session_duration_seconds']:.1f}s")
        print(f"   Messages sent: {session_summary['client_messages_sent']}")
        print(f"   Responses received: {session_summary['server_responses_received']}")
        
        return session_summary
    
    def analyze_connection_performance(self):
        """Analyze gRPC connection performance"""
        print(f"\n=== gRPC Connection Performance ===")
        
        # Simulate performance metrics
        performance_metrics = {
            'connection_establishment': {
                'tcp_handshake_ms': 1.2,
                'tls_handshake_ms': 2.8,
                'http2_settings_ms': 0.5,
                'total_ms': 4.5
            },
            'request_performance': {
                'avg_latency_ms': 2.3,
                'p95_latency_ms': 4.1,
                'p99_latency_ms': 7.8,
                'throughput_rps': 8500
            },
            'connection_efficiency': {
                'multiplexed_streams': 100,
                'header_compression_ratio': 0.85,
                'payload_compression_ratio': 0.65,
                'connection_reuse': True
            }
        }
        
        print(f"Connection Establishment:")
        conn = performance_metrics['connection_establishment']
        print(f"  TCP handshake: {conn['tcp_handshake_ms']}ms")
        print(f"  TLS handshake: {conn['tls_handshake_ms']}ms")
        print(f"  HTTP/2 settings: {conn['http2_settings_ms']}ms")
        print(f"  Total time: {conn['total_ms']}ms")
        
        print(f"\nRequest Performance:")
        req = performance_metrics['request_performance']
        print(f"  Average latency: {req['avg_latency_ms']}ms")
        print(f"  95th percentile: {req['p95_latency_ms']}ms")
        print(f"  99th percentile: {req['p99_latency_ms']}ms")
        print(f"  Throughput: {req['throughput_rps']:,} RPS")
        
        print(f"\nConnection Efficiency:")
        eff = performance_metrics['connection_efficiency']
        print(f"  Multiplexed streams: {eff['multiplexed_streams']}")
        print(f"  Header compression: {eff['header_compression_ratio']:.0%}")
        print(f"  Payload compression: {eff['payload_compression_ratio']:.0%}")
        print(f"  Connection reuse: {eff['connection_reuse']}")
        
        return performance_metrics
    
    def get_client_statistics(self):
        """Get client-side statistics"""
        total_requests = len(self.request_history)
        successful_requests = sum(1 for req in self.request_history if req.get('success', False))
        
        if total_requests > 0:
            avg_latency = sum(req.get('latency_ms', 0) for req in self.request_history) / total_requests
            success_rate = (successful_requests / total_requests) * 100
        else:
            avg_latency = 0
            success_rate = 0
        
        return {
            'client_id': self.client_id,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate_percent': round(success_rate, 2),
            'average_latency_ms': round(avg_latency, 2),
            'connection_info': f"{self.server_host}:{self.server_port}"
        }

def compare_grpc_vs_rest():
    """Compare gRPC vs REST performance"""
    print(f"\n=== gRPC vs REST Comparison ===")
    
    comparison_metrics = [
        {
            'metric': 'Payload Size',
            'rest_json': '1.2 KB',
            'grpc_protobuf': '0.6 KB',
            'improvement': '50% smaller'
        },
        {
            'metric': 'Serialization Time',
            'rest_json': '0.8ms',
            'grpc_protobuf': '0.2ms',
            'improvement': '75% faster'
        },
        {
            'metric': 'Network Efficiency',
            'rest_json': 'HTTP/1.1 + JSON',
            'grpc_protobuf': 'HTTP/2 + Binary',
            'improvement': 'Multiplexing + Compression'
        },
        {
            'metric': 'Type Safety',
            'rest_json': 'Runtime validation',
            'grpc_protobuf': 'Compile-time',
            'improvement': 'Schema enforcement'
        },
        {
            'metric': 'Streaming Support',
            'rest_json': 'Limited (SSE)',
            'grpc_protobuf': 'Native bidirectional',
            'improvement': 'Full-duplex streaming'
        }
    ]
    
    print(f"{'Metric':<20} {'REST/JSON':<20} {'gRPC/Protobuf':<20} {'Improvement'}")
    print("-" * 85)
    
    for metric in comparison_metrics:
        print(f"{metric['metric']:<20} {metric['rest_json']:<20} "
              f"{metric['grpc_protobuf']:<20} {metric['improvement']}")
    
    return comparison_metrics

if __name__ == "__main__":
    # Create gRPC client
    client = GRPCClient()
    
    # Connect to server
    connection_info = client.connect_to_server()
    
    # Demonstrate different RPC patterns
    unary_results = client.demonstrate_unary_calls()
    streaming_results = client.demonstrate_server_streaming()
    client_streaming_results = client.demonstrate_client_streaming()
    bidirectional_results = client.demonstrate_bidirectional_streaming()
    
    # Analyze performance
    performance_metrics = client.analyze_connection_performance()
    
    # Compare with REST
    comparison = compare_grpc_vs_rest()
    
    # Get client statistics
    stats = client.get_client_statistics()
    
    print(f"\n=== gRPC Client Summary ===")
    print(f"Client ID: {stats['client_id']}")
    print(f"Server: {stats['connection_info']}")
    print(f"Total requests: {stats['total_requests']}")
    print(f"Success rate: {stats['success_rate_percent']}%")
    print(f"Average latency: {stats['average_latency_ms']}ms")
    print(f"RPC patterns demonstrated: Unary, Server streaming, Client streaming, Bidirectional")
    print(f"gRPC provides efficient, type-safe RPC with HTTP/2 and Protocol Buffers")
