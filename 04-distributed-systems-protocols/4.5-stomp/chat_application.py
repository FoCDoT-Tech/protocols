#!/usr/bin/env python3
"""
STOMP Chat Application
Real-time chat application demonstrating STOMP messaging patterns.
"""

import time
import threading
import json
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime

from stomp_broker import StompBroker, StompFrame, StompCommand
from stomp_client import StompClient, StompClientConfig, AckMode

@dataclass
class ChatUser:
    user_id: str
    username: str
    room: str
    client: StompClient
    last_seen: datetime = field(default_factory=datetime.now)
    message_count: int = 0

@dataclass
class ChatMessage:
    message_id: str
    user_id: str
    username: str
    room: str
    content: str
    timestamp: datetime
    message_type: str = "text"  # text, join, leave, system

class ChatRoom:
    def __init__(self, room_name: str, broker: StompBroker):
        self.room_name = room_name
        self.broker = broker
        self.users: Dict[str, ChatUser] = {}
        self.message_history: List[ChatMessage] = []
        self.topic = f"/topic/chat/{room_name}"
        self.user_topic = f"/topic/chat/{room_name}/users"
        
        # Room statistics
        self.stats = {
            'created_at': datetime.now(),
            'total_messages': 0,
            'peak_users': 0,
            'current_users': 0
        }
    
    def add_user(self, user: ChatUser) -> bool:
        """Add user to chat room"""
        if user.user_id in self.users:
            return False
        
        self.users[user.user_id] = user
        self.stats['current_users'] = len(self.users)
        self.stats['peak_users'] = max(self.stats['peak_users'], self.stats['current_users'])
        
        # Send join message
        join_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            user_id=user.user_id,
            username=user.username,
            room=self.room_name,
            content=f"{user.username} joined the room",
            timestamp=datetime.now(),
            message_type="join"
        )
        
        self._broadcast_message(join_message)
        self._broadcast_user_list()
        
        print(f"👤 {user.username} joined room '{self.room_name}'")
        return True
    
    def remove_user(self, user_id: str) -> bool:
        """Remove user from chat room"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        del self.users[user_id]
        self.stats['current_users'] = len(self.users)
        
        # Send leave message
        leave_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            user_id=user_id,
            username=user.username,
            room=self.room_name,
            content=f"{user.username} left the room",
            timestamp=datetime.now(),
            message_type="leave"
        )
        
        self._broadcast_message(leave_message)
        self._broadcast_user_list()
        
        print(f"👤 {user.username} left room '{self.room_name}'")
        return True
    
    def send_message(self, user_id: str, content: str) -> bool:
        """Send message from user"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        user.last_seen = datetime.now()
        user.message_count += 1
        
        message = ChatMessage(
            message_id=str(uuid.uuid4()),
            user_id=user_id,
            username=user.username,
            room=self.room_name,
            content=content,
            timestamp=datetime.now(),
            message_type="text"
        )
        
        self._broadcast_message(message)
        return True
    
    def _broadcast_message(self, message: ChatMessage):
        """Broadcast message to all users in room"""
        self.message_history.append(message)
        self.stats['total_messages'] += 1
        
        # Keep only last 100 messages
        if len(self.message_history) > 100:
            self.message_history = self.message_history[-100:]
        
        # Create STOMP message
        message_data = {
            'message_id': message.message_id,
            'user_id': message.user_id,
            'username': message.username,
            'room': message.room,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'type': message.message_type
        }
        
        # Send via STOMP broker
        send_frame = StompFrame(
            command=StompCommand.SEND,
            headers={
                'destination': self.topic,
                'content-type': 'application/json'
            },
            body=json.dumps(message_data)
        )
        
        # Simulate sending through broker
        if self.broker:
            self.broker.process_frame("chat_room", send_frame)
    
    def _broadcast_user_list(self):
        """Broadcast current user list"""
        user_list = {
            'type': 'user_list',
            'room': self.room_name,
            'users': [
                {
                    'user_id': user.user_id,
                    'username': user.username,
                    'last_seen': user.last_seen.isoformat(),
                    'message_count': user.message_count
                }
                for user in self.users.values()
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        send_frame = StompFrame(
            command=StompCommand.SEND,
            headers={
                'destination': self.user_topic,
                'content-type': 'application/json'
            },
            body=json.dumps(user_list)
        )
        
        if self.broker:
            self.broker.process_frame("chat_room", send_frame)
    
    def get_stats(self) -> Dict:
        """Get room statistics"""
        return {
            'room_name': self.room_name,
            'current_users': self.stats['current_users'],
            'peak_users': self.stats['peak_users'],
            'total_messages': self.stats['total_messages'],
            'uptime': (datetime.now() - self.stats['created_at']).total_seconds(),
            'recent_messages': len([m for m in self.message_history 
                                  if (datetime.now() - m.timestamp).total_seconds() < 300])
        }

class ChatApplication:
    def __init__(self, broker: StompBroker):
        self.broker = broker
        self.rooms: Dict[str, ChatRoom] = {}
        self.users: Dict[str, ChatUser] = {}
        
        # Default rooms
        self.create_room("general")
        self.create_room("random")
        self.create_room("tech")
        
        print("💬 Chat Application initialized")
    
    def create_room(self, room_name: str) -> bool:
        """Create new chat room"""
        if room_name in self.rooms:
            return False
        
        self.rooms[room_name] = ChatRoom(room_name, self.broker)
        print(f"🏠 Created chat room '{room_name}'")
        return True
    
    def join_room(self, username: str, room_name: str) -> Optional[str]:
        """Join user to chat room"""
        if room_name not in self.rooms:
            return None
        
        # Create client for user
        config = StompClientConfig()
        client = StompClient(config)
        
        if not client.connect(self.broker):
            return None
        
        user_id = str(uuid.uuid4())
        user = ChatUser(
            user_id=user_id,
            username=username,
            room=room_name,
            client=client
        )
        
        # Subscribe to room messages
        def message_handler(frame: StompFrame):
            try:
                message_data = json.loads(frame.body)
                if message_data.get('type') == 'user_list':
                    print(f"👥 Users in {room_name}: {len(message_data['users'])}")
                else:
                    timestamp = datetime.fromisoformat(message_data['timestamp'])
                    print(f"[{timestamp.strftime('%H:%M:%S')}] {message_data['username']}: {message_data['content']}")
            except Exception as e:
                print(f"❌ Error handling message: {e}")
        
        def user_list_handler(frame: StompFrame):
            try:
                user_data = json.loads(frame.body)
                if user_data.get('type') == 'user_list':
                    usernames = [u['username'] for u in user_data['users']]
                    print(f"👥 Online users: {', '.join(usernames)}")
            except Exception as e:
                print(f"❌ Error handling user list: {e}")
        
        # Subscribe to topics
        room = self.rooms[room_name]
        client.subscribe(room.topic, message_handler, AckMode.AUTO)
        client.subscribe(room.user_topic, user_list_handler, AckMode.AUTO)
        
        # Add user to room
        self.users[user_id] = user
        room.add_user(user)
        
        return user_id
    
    def leave_room(self, user_id: str) -> bool:
        """Remove user from chat room"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        room = self.rooms[user.room]
        
        # Remove from room
        room.remove_user(user_id)
        
        # Disconnect client
        user.client.disconnect()
        
        # Remove from users
        del self.users[user_id]
        
        return True
    
    def send_message(self, user_id: str, content: str) -> bool:
        """Send message from user"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        room = self.rooms[user.room]
        
        return room.send_message(user_id, content)
    
    def get_room_stats(self, room_name: str) -> Optional[Dict]:
        """Get statistics for room"""
        if room_name not in self.rooms:
            return None
        
        return self.rooms[room_name].get_stats()
    
    def get_application_stats(self) -> Dict:
        """Get overall application statistics"""
        total_users = sum(room.stats['current_users'] for room in self.rooms.values())
        total_messages = sum(room.stats['total_messages'] for room in self.rooms.values())
        
        return {
            'total_rooms': len(self.rooms),
            'total_users': total_users,
            'total_messages': total_messages,
            'rooms': {name: room.get_stats() for name, room in self.rooms.items()}
        }

def demonstrate_chat_application():
    """Demonstrate STOMP chat application"""
    print("=== STOMP Chat Application Demonstration ===")
    
    # Start broker
    broker = StompBroker()
    broker.start()
    
    try:
        # Create chat application
        chat_app = ChatApplication(broker)
        
        # Simulate users joining
        print(f"\n👤 Users joining chat rooms...")
        
        alice_id = chat_app.join_room("Alice", "general")
        bob_id = chat_app.join_room("Bob", "general")
        charlie_id = chat_app.join_room("Charlie", "tech")
        diana_id = chat_app.join_room("Diana", "tech")
        
        time.sleep(0.5)  # Let join messages process
        
        # Simulate conversation
        print(f"\n💬 Simulating chat conversation...")
        
        chat_app.send_message(alice_id, "Hello everyone!")
        time.sleep(0.2)
        
        chat_app.send_message(bob_id, "Hi Alice! How's everyone doing?")
        time.sleep(0.2)
        
        chat_app.send_message(alice_id, "Great! Just discussing the new STOMP protocol implementation.")
        time.sleep(0.2)
        
        # Tech room conversation
        chat_app.send_message(charlie_id, "Anyone working with STOMP messaging?")
        time.sleep(0.2)
        
        chat_app.send_message(diana_id, "Yes! It's really simple compared to other protocols.")
        time.sleep(0.2)
        
        chat_app.send_message(charlie_id, "The text-based frames make debugging so much easier.")
        time.sleep(0.2)
        
        # More general room messages
        chat_app.send_message(bob_id, "That sounds interesting. Maybe I should check it out.")
        time.sleep(0.2)
        
        chat_app.send_message(alice_id, "Definitely! The transaction support is really useful too.")
        time.sleep(0.5)
        
        # Display room statistics
        print(f"\n📊 Chat Room Statistics:")
        
        for room_name in ["general", "tech"]:
            stats = chat_app.get_room_stats(room_name)
            if stats:
                print(f"   Room '{room_name}':")
                print(f"     Current users: {stats['current_users']}")
                print(f"     Peak users: {stats['peak_users']}")
                print(f"     Total messages: {stats['total_messages']}")
                print(f"     Recent messages (5min): {stats['recent_messages']}")
        
        # Application-wide statistics
        print(f"\n📊 Application Statistics:")
        app_stats = chat_app.get_application_stats()
        print(f"   Total rooms: {app_stats['total_rooms']}")
        print(f"   Total users: {app_stats['total_users']}")
        print(f"   Total messages: {app_stats['total_messages']}")
        
        # Simulate users leaving
        print(f"\n👋 Users leaving...")
        
        chat_app.leave_room(charlie_id)
        time.sleep(0.2)
        
        chat_app.send_message(diana_id, "Charlie left, but the conversation continues!")
        time.sleep(0.2)
        
        chat_app.leave_room(bob_id)
        chat_app.leave_room(alice_id)
        chat_app.leave_room(diana_id)
        
        time.sleep(0.5)  # Let leave messages process
        
        # Final statistics
        print(f"\n📊 Final Statistics:")
        final_stats = chat_app.get_application_stats()
        print(f"   Active users: {final_stats['total_users']}")
        print(f"   Messages exchanged: {final_stats['total_messages']}")
    
    finally:
        broker.stop()
    
    print("\n🎯 STOMP Chat Application demonstrates:")
    print("💡 Real-time messaging with STOMP protocol")
    print("💡 Topic-based chat rooms and user management")
    print("💡 JSON message serialization over STOMP frames")
    print("💡 User presence and activity tracking")
    print("💡 Scalable pub-sub messaging patterns")

if __name__ == "__main__":
    demonstrate_chat_application()
