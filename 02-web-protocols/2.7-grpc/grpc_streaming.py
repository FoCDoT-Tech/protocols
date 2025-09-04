#!/usr/bin/env python3
"""
gRPC Streaming Patterns and Performance Analysis
Demonstrates advanced streaming capabilities and real-world scenarios
"""

import time
import random
import json
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque

class StreamingPatterns:
    def __init__(self):
        self.message_count = 0
        
    def demonstrate_streaming_patterns(self):
        """Demonstrate all gRPC streaming patterns"""
        print(f"=== gRPC Streaming Patterns ===")
        
        results = []
        
        # Server streaming
        server_result = self.server_streaming_demo()
        results.append(server_result)
        
        # Client streaming  
        client_result = self.client_streaming_demo()
        results.append(client_result)
        
        # Bidirectional streaming
        bidirectional_result = self.bidirectional_streaming_demo()
        results.append(bidirectional_result)
        
        return results
    
    def server_streaming_demo(self):
        """Demonstrate server streaming with market data"""
        print(f"\n📈 Server Streaming: Market Data Feed")
        
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
        updates_sent = 0
        start_time = time.time()
        
        print(f"🔄 Streaming market data for {len(symbols)} symbols")
        
        # Simulate high-frequency market data
        for tick in range(15):
            for symbol in symbols:
                price_update = {
                    'symbol': symbol,
                    'price': round(random.uniform(100, 3000), 2),
                    'volume': random.randint(1000, 100000),
                    'timestamp': int(time.time() * 1000),
                    'sequence': updates_sent + 1
                }
                
                if updates_sent % 10 == 0:
                    print(f"📊 {symbol}: ${price_update['price']:.2f}")
                
                updates_sent += 1
                self.message_count += 1
            
            time.sleep(0.02)  # 50 updates/sec
        
        duration = time.time() - start_time
        throughput = updates_sent / duration
        
        print(f"✅ Server streaming: {updates_sent} updates, {throughput:.0f}/sec")
        
        return {
            'pattern': 'server_streaming',
            'updates_sent': updates_sent,
            'throughput_per_second': throughput,
            'symbols': len(symbols)
        }
    
    def client_streaming_demo(self):
        """Demonstrate client streaming with bulk orders"""
        print(f"\n📤 Client Streaming: Bulk Order Upload")
        
        order_count = 50
        orders_sent = 0
        start_time = time.time()
        
        print(f"🔄 Streaming {order_count} orders to server")
        
        for order_num in range(order_count):
            order = {
                'order_id': f"ord_{order_num + 1:04d}",
                'symbol': random.choice(['AAPL', 'GOOGL', 'MSFT', 'TSLA']),
                'side': random.choice(['BUY', 'SELL']),
                'quantity': random.randint(10, 1000),
                'order_type': 'MARKET',
                'timestamp': int(time.time() * 1000)
            }
            
            if order_num % 10 == 0:
                print(f"📋 Order {order_num + 1}: {order['side']} {order['quantity']} {order['symbol']}")
            
            orders_sent += 1
            self.message_count += 1
            time.sleep(0.01)  # 10ms per order
        
        duration = time.time() - start_time
        throughput = orders_sent / duration
        
        # Simulate server response
        summary = {
            'total_orders': orders_sent,
            'successful': orders_sent - 1,
            'failed': 1,
            'processing_time_ms': int(duration * 1000)
        }
        
        print(f"✅ Client streaming: {orders_sent} orders, {throughput:.0f}/sec")
        print(f"📊 Server response: {summary['successful']}/{summary['total_orders']} successful")
        
        return {
            'pattern': 'client_streaming',
            'orders_sent': orders_sent,
            'throughput_per_second': throughput,
            'server_summary': summary
        }
    
    def bidirectional_streaming_demo(self):
        """Demonstrate bidirectional streaming with live trading"""
        print(f"\n🔄 Bidirectional Streaming: Live Trading Session")
        
        session_id = f"session_{random.randint(1000, 9999)}"
        client_messages = 0
        server_responses = 0
        
        print(f"🔄 Starting trading session {session_id}")
        
        # Simulate interactive trading
        actions = [
            {'action': 'SUBSCRIBE', 'symbols': ['AAPL', 'GOOGL']},
            {'action': 'PLACE_ORDER', 'symbol': 'AAPL', 'side': 'BUY', 'quantity': 100},
            {'action': 'REQUEST_QUOTE', 'symbol': 'GOOGL'},
            {'action': 'MODIFY_ORDER', 'order_id': 'ord_123', 'new_price': 151.00},
            {'action': 'CANCEL_ORDER', 'order_id': 'ord_124'},
            {'action': 'GET_POSITIONS'},
            {'action': 'UNSUBSCRIBE', 'symbols': ['GOOGL']}
        ]
        
        for action in actions:
            # Client sends action
            client_msg = {
                'session_id': session_id,
                'timestamp': int(time.time() * 1000),
                **action
            }
            
            print(f"📤 Client: {action['action']}")
            client_messages += 1
            
            # Server responds
            if action['action'] == 'SUBSCRIBE':
                response = {'type': 'SUBSCRIPTION_ACK', 'status': 'ACTIVE'}
            elif action['action'] == 'PLACE_ORDER':
                response = {'type': 'ORDER_ACK', 'order_id': f"ord_{random.randint(1000, 9999)}"}
            elif action['action'] == 'REQUEST_QUOTE':
                response = {'type': 'QUOTE', 'bid': 150.25, 'ask': 150.27}
            else:
                response = {'type': 'ACK', 'status': 'SUCCESS'}
            
            print(f"📥 Server: {response['type']}")
            server_responses += 1
            
            self.message_count += 2
            time.sleep(0.2)
        
        total_messages = client_messages + server_responses
        
        print(f"✅ Bidirectional streaming: {total_messages} total messages")
        print(f"   Client messages: {client_messages}")
        print(f"   Server responses: {server_responses}")
        
        return {
            'pattern': 'bidirectional_streaming',
            'client_messages': client_messages,
            'server_responses': server_responses,
            'total_messages': total_messages,
            'session_id': session_id
        }
    
    def analyze_streaming_performance(self):
        """Analyze gRPC streaming performance"""
        print(f"\n=== gRPC Streaming Performance ===")
        
        scenarios = [
            {
                'pattern': 'High-Frequency Market Data',
                'messages_per_second': 10000,
                'latency_p99_ms': 2,
                'use_case': 'Financial trading platforms'
            },
            {
                'pattern': 'IoT Sensor Telemetry',
                'messages_per_second': 1000,
                'latency_p99_ms': 10,
                'use_case': 'Industrial monitoring'
            },
            {
                'pattern': 'Real-Time Gaming',
                'messages_per_second': 60,
                'latency_p99_ms': 16,
                'use_case': 'Multiplayer games'
            },
            {
                'pattern': 'Video Streaming',
                'messages_per_second': 30,
                'latency_p99_ms': 33,
                'use_case': 'Video conferencing'
            }
        ]
        
        print(f"{'Pattern':<25} {'Msg/sec':<10} {'P99 Latency':<12} {'Use Case'}")
        print("-" * 70)
        
        for scenario in scenarios:
            print(f"{scenario['pattern']:<25} {scenario['messages_per_second']:<10} "
                  f"{scenario['latency_p99_ms']} ms{'':<7} {scenario['use_case']}")
        
        return scenarios
    
    def compare_streaming_vs_unary(self):
        """Compare streaming vs unary RPC performance"""
        print(f"\n=== Streaming vs Unary RPC Comparison ===")
        
        comparison = [
            {
                'metric': 'Connection Overhead',
                'unary_rpc': 'New connection per request',
                'streaming': 'Single persistent connection',
                'benefit': '90% reduction in overhead'
            },
            {
                'metric': 'Latency',
                'unary_rpc': '50-100ms per request',
                'streaming': '1-5ms per message',
                'benefit': '95% latency reduction'
            },
            {
                'metric': 'Throughput',
                'unary_rpc': '100-500 RPS',
                'streaming': '10,000+ MPS',
                'benefit': '20x throughput increase'
            },
            {
                'metric': 'Resource Usage',
                'unary_rpc': 'High CPU/memory per request',
                'streaming': 'Amortized across stream',
                'benefit': '80% resource savings'
            }
        ]
        
        print(f"{'Metric':<18} {'Unary RPC':<25} {'Streaming':<25} {'Benefit'}")
        print("-" * 85)
        
        for comp in comparison:
            print(f"{comp['metric']:<18} {comp['unary_rpc']:<25} "
                  f"{comp['streaming']:<25} {comp['benefit']}")
        
        return comparison
    
    def get_streaming_statistics(self):
        """Get streaming statistics"""
        return {
            'total_messages_processed': self.message_count,
            'patterns_demonstrated': ['server_streaming', 'client_streaming', 'bidirectional_streaming'],
            'use_cases_covered': ['market_data', 'bulk_orders', 'live_trading'],
            'performance_benefits': ['low_latency', 'high_throughput', 'efficient_resources']
        }

if __name__ == "__main__":
    # Create streaming patterns demo
    streaming = StreamingPatterns()
    
    # Demonstrate all streaming patterns
    results = streaming.demonstrate_streaming_patterns()
    
    # Analyze performance
    performance_scenarios = streaming.analyze_streaming_performance()
    
    # Compare with unary RPC
    comparison = streaming.compare_streaming_vs_unary()
    
    # Get statistics
    stats = streaming.get_streaming_statistics()
    
    print(f"\n=== gRPC Streaming Summary ===")
    print(f"Total messages processed: {stats['total_messages_processed']}")
    print(f"Patterns demonstrated: {len(stats['patterns_demonstrated'])}")
    print(f"Use cases covered: {len(stats['use_cases_covered'])}")
    print(f"Performance scenarios: {len(performance_scenarios)}")
    print(f"gRPC streaming enables efficient, real-time communication for high-performance applications")
