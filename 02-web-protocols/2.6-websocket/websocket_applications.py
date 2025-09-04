#!/usr/bin/env python3
"""
WebSocket Real-World Applications and Use Cases
Demonstrates practical WebSocket implementations for various real-time scenarios
"""

import time
import random
import json
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque

class ChatApplication:
    def __init__(self):
        self.rooms = defaultdict(list)
        self.users = {}
        self.message_history = defaultdict(deque)
        self.user_count = 0
        
    def simulate_chat_room(self):
        """Simulate a real-time chat room"""
        print("=== Real-Time Chat Application ===")
        
        # Simulate users joining
        users = ['Alice', 'Bob', 'Charlie', 'Diana']
        room_name = 'general'
        
        print(f"Chat room: #{room_name}")
        
        for user in users:
            self.user_join(user, room_name)
            time.sleep(0.1)
        
        # Simulate chat messages
        messages = [
            {'user': 'Alice', 'message': 'Hello everyone! 👋'},
            {'user': 'Bob', 'message': 'Hey Alice! How are you?'},
            {'user': 'Charlie', 'message': 'Good morning all!'},
            {'user': 'Diana', 'message': 'Anyone up for a game later?'},
            {'user': 'Alice', 'message': 'Sure! What game?'},
            {'user': 'Diana', 'message': 'How about online chess?'},
            {'user': 'Bob', 'message': 'Count me in! ♟️'}
        ]
        
        for msg in messages:
            self.send_message(msg['user'], room_name, msg['message'])
            time.sleep(0.5)
        
        # Show typing indicators
        print(f"\n--- Typing Indicators ---")
        self.show_typing(users[0], room_name)
        time.sleep(1)
        self.hide_typing(users[0], room_name)
        
        # User leaves
        self.user_leave(users[-1], room_name)
        
        return self.get_room_stats(room_name)
    
    def user_join(self, username, room):
        """Handle user joining room"""
        self.user_count += 1
        user_id = f"user_{self.user_count}"
        
        self.users[user_id] = {
            'username': username,
            'room': room,
            'joined_at': datetime.now(),
            'last_seen': datetime.now()
        }
        
        self.rooms[room].append(user_id)
        
        # Broadcast join message
        join_msg = {
            'type': 'user_joined',
            'username': username,
            'room': room,
            'timestamp': datetime.now().isoformat(),
            'user_count': len(self.rooms[room])
        }
        
        print(f"📥 {username} joined #{room}")
        self.broadcast_to_room(room, join_msg, exclude_user=user_id)
        
        return user_id
    
    def user_leave(self, username, room):
        """Handle user leaving room"""
        user_id = None
        for uid, user in self.users.items():
            if user['username'] == username and user['room'] == room:
                user_id = uid
                break
        
        if user_id:
            self.rooms[room].remove(user_id)
            del self.users[user_id]
            
            # Broadcast leave message
            leave_msg = {
                'type': 'user_left',
                'username': username,
                'room': room,
                'timestamp': datetime.now().isoformat(),
                'user_count': len(self.rooms[room])
            }
            
            print(f"📤 {username} left #{room}")
            self.broadcast_to_room(room, leave_msg)
    
    def send_message(self, username, room, message):
        """Send chat message"""
        user_id = None
        for uid, user in self.users.items():
            if user['username'] == username:
                user_id = uid
                break
        
        if user_id:
            msg = {
                'type': 'chat_message',
                'username': username,
                'message': message,
                'room': room,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in history
            self.message_history[room].append(msg)
            if len(self.message_history[room]) > 100:
                self.message_history[room].popleft()
            
            print(f"💬 {username}: {message}")
            self.broadcast_to_room(room, msg, exclude_user=user_id)
    
    def show_typing(self, username, room):
        """Show typing indicator"""
        typing_msg = {
            'type': 'typing_start',
            'username': username,
            'room': room,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✍️ {username} is typing...")
        self.broadcast_to_room(room, typing_msg)
    
    def hide_typing(self, username, room):
        """Hide typing indicator"""
        typing_msg = {
            'type': 'typing_stop',
            'username': username,
            'room': room,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✍️ {username} stopped typing")
        self.broadcast_to_room(room, typing_msg)
    
    def broadcast_to_room(self, room, message, exclude_user=None):
        """Broadcast message to all users in room"""
        recipients = [uid for uid in self.rooms[room] if uid != exclude_user]
        
        # Simulate WebSocket message sending
        for user_id in recipients:
            username = self.users[user_id]['username']
            # In real implementation, this would send via WebSocket
            # websocket.send(json.dumps(message))
        
        return len(recipients)
    
    def get_room_stats(self, room):
        """Get room statistics"""
        return {
            'room': room,
            'active_users': len(self.rooms[room]),
            'total_messages': len(self.message_history[room]),
            'users': [self.users[uid]['username'] for uid in self.rooms[room]]
        }

class LiveDataFeed:
    def __init__(self):
        self.subscribers = {}
        self.data_sources = {}
        self.update_interval = 0.1  # 100ms updates
        
    def simulate_trading_platform(self):
        """Simulate real-time trading data feed"""
        print(f"\n=== Real-Time Trading Platform ===")
        
        # Initialize stock prices
        stocks = {
            'AAPL': 150.00,
            'GOOGL': 2800.00,
            'MSFT': 300.00,
            'TSLA': 800.00,
            'AMZN': 3200.00
        }
        
        self.data_sources['stocks'] = stocks
        
        # Simulate clients subscribing
        clients = ['trader_1', 'trader_2', 'analyst_1', 'bot_1']
        
        for client in clients:
            self.subscribe_client(client, 'stocks')
        
        print(f"📊 {len(clients)} clients subscribed to stock feed")
        
        # Simulate price updates
        print(f"\n--- Live Price Updates ---")
        
        for update_cycle in range(10):
            # Update stock prices
            for symbol in stocks:
                # Random price movement (-2% to +2%)
                change_percent = random.uniform(-0.02, 0.02)
                stocks[symbol] *= (1 + change_percent)
                
                # Create update message
                update = {
                    'type': 'price_update',
                    'symbol': symbol,
                    'price': round(stocks[symbol], 2),
                    'change': round(change_percent * 100, 2),
                    'timestamp': datetime.now().isoformat(),
                    'volume': random.randint(1000, 10000)
                }
                
                print(f"📈 {symbol}: ${update['price']:.2f} ({update['change']:+.2f}%)")
                self.broadcast_update('stocks', update)
            
            time.sleep(self.update_interval)
            print()
        
        return self.get_feed_stats('stocks')
    
    def simulate_iot_monitoring(self):
        """Simulate IoT sensor monitoring"""
        print(f"\n=== IoT Sensor Monitoring ===")
        
        # Initialize sensor data
        sensors = {
            'temperature': 22.5,
            'humidity': 60.0,
            'pressure': 1013.25,
            'light': 500,
            'motion': False
        }
        
        self.data_sources['sensors'] = sensors
        
        # Simulate monitoring clients
        clients = ['dashboard_1', 'mobile_app', 'alert_system']
        
        for client in clients:
            self.subscribe_client(client, 'sensors')
        
        print(f"🏠 {len(clients)} clients monitoring sensors")
        
        # Simulate sensor readings
        print(f"\n--- Sensor Readings ---")
        
        for reading_cycle in range(8):
            # Update sensor values
            sensors['temperature'] += random.uniform(-0.5, 0.5)
            sensors['humidity'] += random.uniform(-2.0, 2.0)
            sensors['pressure'] += random.uniform(-1.0, 1.0)
            sensors['light'] = max(0, sensors['light'] + random.randint(-50, 50))
            sensors['motion'] = random.random() < 0.3  # 30% chance of motion
            
            # Create sensor update
            update = {
                'type': 'sensor_reading',
                'sensors': {
                    'temperature': round(sensors['temperature'], 1),
                    'humidity': round(sensors['humidity'], 1),
                    'pressure': round(sensors['pressure'], 2),
                    'light': int(sensors['light']),
                    'motion': sensors['motion']
                },
                'timestamp': datetime.now().isoformat(),
                'device_id': 'sensor_hub_001'
            }
            
            print(f"🌡️ Temp: {update['sensors']['temperature']}°C, "
                  f"💧 Humidity: {update['sensors']['humidity']}%, "
                  f"🚶 Motion: {'Yes' if update['sensors']['motion'] else 'No'}")
            
            self.broadcast_update('sensors', update)
            
            # Simulate alert condition
            if sensors['temperature'] > 25.0:
                alert = {
                    'type': 'alert',
                    'level': 'warning',
                    'message': f"High temperature detected: {sensors['temperature']:.1f}°C",
                    'timestamp': datetime.now().isoformat()
                }
                print(f"⚠️ ALERT: {alert['message']}")
                self.broadcast_update('sensors', alert)
            
            time.sleep(0.2)
        
        return self.get_feed_stats('sensors')
    
    def subscribe_client(self, client_id, feed_type):
        """Subscribe client to data feed"""
        if feed_type not in self.subscribers:
            self.subscribers[feed_type] = []
        
        self.subscribers[feed_type].append({
            'client_id': client_id,
            'subscribed_at': datetime.now(),
            'messages_sent': 0
        })
        
        print(f"🔔 {client_id} subscribed to {feed_type} feed")
    
    def broadcast_update(self, feed_type, update):
        """Broadcast update to all subscribers"""
        if feed_type in self.subscribers:
            for subscriber in self.subscribers[feed_type]:
                # In real implementation, send via WebSocket
                # websocket.send(json.dumps(update))
                subscriber['messages_sent'] += 1
    
    def get_feed_stats(self, feed_type):
        """Get feed statistics"""
        if feed_type not in self.subscribers:
            return {}
        
        total_messages = sum(s['messages_sent'] for s in self.subscribers[feed_type])
        
        return {
            'feed_type': feed_type,
            'subscribers': len(self.subscribers[feed_type]),
            'total_messages': total_messages,
            'avg_messages_per_client': total_messages / len(self.subscribers[feed_type]) if self.subscribers[feed_type] else 0
        }

class CollaborativeEditor:
    def __init__(self):
        self.document = ""
        self.operations = []
        self.cursors = {}
        self.users = {}
        
    def simulate_collaborative_editing(self):
        """Simulate real-time collaborative document editing"""
        print(f"\n=== Collaborative Document Editor ===")
        
        # Initialize users
        users = ['Alice', 'Bob', 'Charlie']
        
        for i, user in enumerate(users):
            self.add_user(user, cursor_position=i * 10)
        
        print(f"📝 {len(users)} users joined document")
        
        # Simulate editing operations
        operations = [
            {'user': 'Alice', 'type': 'insert', 'position': 0, 'text': 'Hello '},
            {'user': 'Bob', 'type': 'insert', 'position': 6, 'text': 'World! '},
            {'user': 'Charlie', 'type': 'insert', 'position': 13, 'text': 'This is '},
            {'user': 'Alice', 'type': 'insert', 'position': 21, 'text': 'a collaborative '},
            {'user': 'Bob', 'type': 'insert', 'position': 36, 'text': 'document.'},
            {'user': 'Charlie', 'type': 'delete', 'position': 13, 'length': 8},  # Remove "This is "
            {'user': 'Alice', 'type': 'insert', 'position': 13, 'text': 'our '},
        ]
        
        print(f"\n--- Editing Operations ---")
        
        for op in operations:
            self.apply_operation(op)
            self.broadcast_operation(op)
            time.sleep(0.3)
        
        # Simulate cursor movements
        print(f"\n--- Cursor Movements ---")
        
        for user in users:
            new_position = random.randint(0, len(self.document))
            self.update_cursor(user, new_position)
            time.sleep(0.1)
        
        return self.get_document_stats()
    
    def add_user(self, username, cursor_position=0):
        """Add user to collaborative session"""
        self.users[username] = {
            'joined_at': datetime.now(),
            'operations_count': 0
        }
        
        self.cursors[username] = {
            'position': cursor_position,
            'color': f"#{random.randint(0, 0xFFFFFF):06x}",
            'last_update': datetime.now()
        }
        
        print(f"👤 {username} joined (cursor at position {cursor_position})")
    
    def apply_operation(self, operation):
        """Apply editing operation to document"""
        op_type = operation['type']
        position = operation['position']
        user = operation['user']
        
        if op_type == 'insert':
            text = operation['text']
            self.document = self.document[:position] + text + self.document[position:]
            print(f"✏️ {user} inserted '{text}' at position {position}")
            
        elif op_type == 'delete':
            length = operation['length']
            deleted_text = self.document[position:position + length]
            self.document = self.document[:position] + self.document[position + length:]
            print(f"🗑️ {user} deleted '{deleted_text}' at position {position}")
        
        # Update operation count
        self.users[user]['operations_count'] += 1
        
        # Store operation in history
        operation['timestamp'] = datetime.now().isoformat()
        operation['document_version'] = len(self.operations) + 1
        self.operations.append(operation)
        
        print(f"📄 Document: '{self.document}'")
    
    def update_cursor(self, username, position):
        """Update user cursor position"""
        if username in self.cursors:
            old_position = self.cursors[username]['position']
            self.cursors[username]['position'] = position
            self.cursors[username]['last_update'] = datetime.now()
            
            print(f"🖱️ {username} moved cursor: {old_position} → {position}")
            
            # Broadcast cursor update
            cursor_update = {
                'type': 'cursor_update',
                'user': username,
                'position': position,
                'color': self.cursors[username]['color'],
                'timestamp': datetime.now().isoformat()
            }
            
            self.broadcast_cursor_update(cursor_update)
    
    def broadcast_operation(self, operation):
        """Broadcast operation to all users"""
        # In real implementation, send via WebSocket to all connected users
        # except the one who made the operation
        other_users = [u for u in self.users.keys() if u != operation['user']]
        
        for user in other_users:
            # websocket.send(json.dumps(operation))
            pass
    
    def broadcast_cursor_update(self, cursor_update):
        """Broadcast cursor update to all users"""
        # In real implementation, send via WebSocket
        other_users = [u for u in self.users.keys() if u != cursor_update['user']]
        
        for user in other_users:
            # websocket.send(json.dumps(cursor_update))
            pass
    
    def get_document_stats(self):
        """Get document statistics"""
        return {
            'document_length': len(self.document),
            'total_operations': len(self.operations),
            'active_users': len(self.users),
            'final_document': self.document,
            'user_contributions': {
                user: data['operations_count'] 
                for user, data in self.users.items()
            }
        }

def demonstrate_websocket_performance():
    """Demonstrate WebSocket performance characteristics"""
    print(f"\n=== WebSocket Performance Analysis ===")
    
    scenarios = [
        {
            'name': 'High-Frequency Trading',
            'messages_per_second': 10000,
            'message_size_bytes': 50,
            'latency_requirement': '< 1ms',
            'use_case': 'Market data feeds, order execution'
        },
        {
            'name': 'Online Gaming',
            'messages_per_second': 60,
            'message_size_bytes': 100,
            'latency_requirement': '< 50ms',
            'use_case': 'Player position updates, game state'
        },
        {
            'name': 'Chat Application',
            'messages_per_second': 10,
            'message_size_bytes': 200,
            'latency_requirement': '< 100ms',
            'use_case': 'Text messages, typing indicators'
        },
        {
            'name': 'IoT Monitoring',
            'messages_per_second': 1,
            'message_size_bytes': 150,
            'latency_requirement': '< 1000ms',
            'use_case': 'Sensor readings, alerts'
        }
    ]
    
    print(f"{'Scenario':<20} {'Msg/sec':<10} {'Size':<10} {'Latency':<12} {'Use Case'}")
    print("-" * 80)
    
    for scenario in scenarios:
        print(f"{scenario['name']:<20} {scenario['messages_per_second']:<10} "
              f"{scenario['message_size_bytes']} bytes{'':<4} {scenario['latency_requirement']:<12} "
              f"{scenario['use_case']}")
    
    # Calculate bandwidth requirements
    print(f"\nBandwidth Analysis:")
    
    for scenario in scenarios:
        # WebSocket frame overhead: ~6 bytes per frame
        frame_overhead = 6
        total_bytes_per_msg = scenario['message_size_bytes'] + frame_overhead
        bandwidth_bps = scenario['messages_per_second'] * total_bytes_per_msg * 8
        bandwidth_kbps = bandwidth_bps / 1024
        
        print(f"  {scenario['name']}: {bandwidth_kbps:.1f} Kbps")
    
    return scenarios

def analyze_websocket_use_cases():
    """Analyze different WebSocket use cases"""
    print(f"\n=== WebSocket Use Case Analysis ===")
    
    use_cases = [
        {
            'category': 'Real-Time Communication',
            'examples': ['Chat applications', 'Video conferencing', 'Voice calls', 'Screen sharing'],
            'key_requirements': ['Low latency', 'Bidirectional', 'Persistent connection'],
            'websocket_benefits': ['Instant message delivery', 'No polling overhead', 'Server push capability']
        },
        {
            'category': 'Live Data Feeds',
            'examples': ['Stock prices', 'Sports scores', 'News updates', 'Social media feeds'],
            'key_requirements': ['Real-time updates', 'High throughput', 'Scalability'],
            'websocket_benefits': ['Push-based updates', 'Efficient bandwidth usage', 'Reduced server load']
        },
        {
            'category': 'Interactive Applications',
            'examples': ['Online gaming', 'Collaborative editing', 'Drawing apps', 'Virtual whiteboards'],
            'key_requirements': ['Ultra-low latency', 'Frequent updates', 'State synchronization'],
            'websocket_benefits': ['Minimal frame overhead', 'Instant state updates', 'Smooth user experience']
        },
        {
            'category': 'IoT and Monitoring',
            'examples': ['Sensor networks', 'Device control', 'System monitoring', 'Alert systems'],
            'key_requirements': ['Reliable delivery', 'Efficient protocol', 'Scalable connections'],
            'websocket_benefits': ['Persistent connections', 'Binary data support', 'Connection health monitoring']
        }
    ]
    
    for use_case in use_cases:
        print(f"\n{use_case['category']}:")
        print(f"  Examples: {', '.join(use_case['examples'])}")
        print(f"  Requirements: {', '.join(use_case['key_requirements'])}")
        print(f"  WebSocket Benefits: {', '.join(use_case['websocket_benefits'])}")
    
    return use_cases

if __name__ == "__main__":
    # Chat application simulation
    chat_app = ChatApplication()
    chat_stats = chat_app.simulate_chat_room()
    
    # Live data feed simulation
    data_feed = LiveDataFeed()
    trading_stats = data_feed.simulate_trading_platform()
    iot_stats = data_feed.simulate_iot_monitoring()
    
    # Collaborative editor simulation
    editor = CollaborativeEditor()
    editor_stats = editor.simulate_collaborative_editing()
    
    # Performance analysis
    performance_scenarios = demonstrate_websocket_performance()
    
    # Use case analysis
    use_cases = analyze_websocket_use_cases()
    
    print(f"\n=== WebSocket Applications Summary ===")
    print(f"Chat room: {chat_stats['active_users']} users, {chat_stats['total_messages']} messages")
    print(f"Trading feed: {trading_stats['subscribers']} subscribers, {trading_stats['total_messages']} updates")
    print(f"IoT monitoring: {iot_stats['subscribers']} clients, {iot_stats['total_messages']} readings")
    print(f"Collaborative editor: {editor_stats['active_users']} users, {editor_stats['total_operations']} operations")
    print(f"Final document: '{editor_stats['final_document']}'")
    print(f"WebSocket enables real-time, interactive, and efficient communication for modern web applications")
