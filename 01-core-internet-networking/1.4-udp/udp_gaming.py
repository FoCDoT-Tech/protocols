#!/usr/bin/env python3
"""
UDP Gaming Protocol Simulation
Demonstrates UDP usage in real-time multiplayer gaming
"""

import time
import random
import math

class GamePlayer:
    def __init__(self, player_id, x=0, y=0):
        self.player_id = player_id
        self.x = x
        self.y = y
        self.health = 100
        self.last_update = time.time()
        
    def move(self, dx, dy):
        """Move player and return position update packet"""
        self.x += dx
        self.y += dy
        self.last_update = time.time()
        
        return {
            'type': 'position_update',
            'player_id': self.player_id,
            'x': self.x,
            'y': self.y,
            'timestamp': self.last_update
        }
    
    def shoot(self, target_x, target_y):
        """Simulate shooting action"""
        return {
            'type': 'shoot',
            'player_id': self.player_id,
            'from_x': self.x,
            'from_y': self.y,
            'to_x': target_x,
            'to_y': target_y,
            'timestamp': time.time()
        }

class GameServer:
    def __init__(self):
        self.players = {}
        self.game_state = {}
        self.packet_loss_rate = 0.05  # 5% packet loss
        
    def add_player(self, player_id):
        """Add new player to game"""
        spawn_x = random.randint(0, 1000)
        spawn_y = random.randint(0, 1000)
        self.players[player_id] = GamePlayer(player_id, spawn_x, spawn_y)
        print(f"Player {player_id} joined at ({spawn_x}, {spawn_y})")
        
    def process_packet(self, packet, from_player):
        """Process incoming UDP packet"""
        # Simulate packet loss
        if random.random() < self.packet_loss_rate:
            print(f"Packet lost from Player {from_player}: {packet['type']}")
            return None
            
        if packet['type'] == 'position_update':
            return self.handle_position_update(packet)
        elif packet['type'] == 'shoot':
            return self.handle_shoot(packet)
        
    def handle_position_update(self, packet):
        """Handle player position update"""
        player_id = packet['player_id']
        if player_id in self.players:
            player = self.players[player_id]
            player.x = packet['x']
            player.y = packet['y']
            player.last_update = packet['timestamp']
            
            # Broadcast to other players (simplified)
            return {
                'type': 'player_moved',
                'player_id': player_id,
                'x': packet['x'],
                'y': packet['y']
            }
    
    def handle_shoot(self, packet):
        """Handle shooting action"""
        shooter_id = packet['player_id']
        
        # Check if any player is hit
        for player_id, player in self.players.items():
            if player_id != shooter_id:
                distance = math.sqrt(
                    (player.x - packet['to_x'])**2 + 
                    (player.y - packet['to_y'])**2
                )
                
                if distance < 50:  # Hit radius
                    player.health -= 25
                    return {
                        'type': 'player_hit',
                        'shooter_id': shooter_id,
                        'victim_id': player_id,
                        'damage': 25,
                        'victim_health': player.health
                    }
        
        return {'type': 'shot_missed', 'shooter_id': shooter_id}

def simulate_multiplayer_game():
    """Simulate a multiplayer game session"""
    print("=== Multiplayer Game UDP Simulation ===\n")
    
    server = GameServer()
    
    # Add players
    for i in range(1, 5):
        server.add_player(i)
    
    print("\n=== Game Session Started ===")
    
    # Simulate game loop
    for tick in range(20):
        print(f"\nGame Tick {tick + 1}:")
        
        # Each player sends position updates
        for player_id, player in server.players.items():
            # Random movement
            dx = random.randint(-10, 10)
            dy = random.randint(-10, 10)
            
            move_packet = player.move(dx, dy)
            response = server.process_packet(move_packet, player_id)
            
            if response:
                print(f"  Player {player_id} moved to ({player.x}, {player.y})")
            
            # Random shooting
            if random.random() < 0.3:  # 30% chance to shoot
                target_x = random.randint(0, 1000)
                target_y = random.randint(0, 1000)
                
                shoot_packet = player.shoot(target_x, target_y)
                response = server.process_packet(shoot_packet, player_id)
                
                if response and response['type'] == 'player_hit':
                    victim_id = response['victim_id']
                    health = response['victim_health']
                    print(f"  Player {player_id} hit Player {victim_id}! Health: {health}")
                elif response and response['type'] == 'shot_missed':
                    print(f"  Player {player_id} shot missed")
        
        time.sleep(0.05)  # 20 FPS simulation

def demonstrate_udp_reliability():
    """Demonstrate custom reliability over UDP"""
    print("\n=== Custom Reliability Over UDP ===\n")
    
    class ReliableUDPMessage:
        def __init__(self, msg_id, data, max_retries=3):
            self.msg_id = msg_id
            self.data = data
            self.max_retries = max_retries
            self.retries = 0
            self.acknowledged = False
            
    # Simulate reliable message delivery
    messages = [
        ReliableUDPMessage(1, "Critical: Player killed"),
        ReliableUDPMessage(2, "Important: Item picked up"),
        ReliableUDPMessage(3, "Critical: Game over")
    ]
    
    for msg in messages:
        print(f"Sending reliable message {msg.msg_id}: '{msg.data}'")
        
        while not msg.acknowledged and msg.retries < msg.max_retries:
            # Simulate sending
            print(f"  Attempt {msg.retries + 1}: Sending message {msg.msg_id}")
            
            # Simulate ACK (80% success rate)
            if random.random() < 0.8:
                msg.acknowledged = True
                print(f"  ✓ ACK received for message {msg.msg_id}")
            else:
                msg.retries += 1
                if msg.retries < msg.max_retries:
                    print(f"  ✗ No ACK, retrying...")
                    time.sleep(0.1)  # Retry delay
        
        if not msg.acknowledged:
            print(f"  ✗ Message {msg.msg_id} failed after {msg.max_retries} attempts")
        
        print()

def udp_performance_metrics():
    """Show UDP performance characteristics"""
    print("=== UDP Performance Metrics ===\n")
    
    # Simulate packet timing
    packet_times = []
    for i in range(100):
        # UDP has very low and consistent latency
        latency = random.uniform(0.001, 0.005)  # 1-5ms
        packet_times.append(latency)
    
    avg_latency = sum(packet_times) / len(packet_times)
    min_latency = min(packet_times)
    max_latency = max(packet_times)
    
    print(f"UDP Latency Statistics (100 packets):")
    print(f"  Average: {avg_latency*1000:.2f}ms")
    print(f"  Minimum: {min_latency*1000:.2f}ms")
    print(f"  Maximum: {max_latency*1000:.2f}ms")
    print(f"  Jitter: {(max_latency - min_latency)*1000:.2f}ms")
    
    # Bandwidth efficiency
    udp_overhead = 8  # UDP header
    ip_overhead = 20  # IP header
    data_size = 64    # Game packet
    
    total_packet = udp_overhead + ip_overhead + data_size
    efficiency = (data_size / total_packet) * 100
    
    print(f"\nBandwidth Efficiency:")
    print(f"  Data: {data_size} bytes")
    print(f"  UDP Header: {udp_overhead} bytes")
    print(f"  IP Header: {ip_overhead} bytes")
    print(f"  Total: {total_packet} bytes")
    print(f"  Efficiency: {efficiency:.1f}%")

if __name__ == "__main__":
    simulate_multiplayer_game()
    demonstrate_udp_reliability()
    udp_performance_metrics()
