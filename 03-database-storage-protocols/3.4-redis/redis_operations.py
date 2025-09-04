#!/usr/bin/env python3
"""
Redis Operations and Data Structures Simulation
Demonstrates advanced Redis operations including pub/sub messaging,
Lua scripting, transactions, and clustering patterns.
"""

import random
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class RedisNode:
    """Redis cluster node"""
    id: str
    host: str
    port: int
    role: str  # 'master' or 'replica'
    slot_start: int
    slot_end: int
    status: str = "online"

class RedisPubSub:
    """Redis Pub/Sub messaging simulation"""
    
    def __init__(self):
        self.channels = {}
        self.patterns = {}
        self.subscribers = {}
        
    def subscribe(self, client_id: str, channel: str):
        """Subscribe client to channel"""
        if channel not in self.channels:
            self.channels[channel] = set()
        
        self.channels[channel].add(client_id)
        
        if client_id not in self.subscribers:
            self.subscribers[client_id] = {'channels': set(), 'patterns': set()}
        
        self.subscribers[client_id]['channels'].add(channel)
        
        print(f"📡 Client {client_id} subscribed to channel '{channel}'")
    
    def psubscribe(self, client_id: str, pattern: str):
        """Subscribe client to pattern"""
        if pattern not in self.patterns:
            self.patterns[pattern] = set()
        
        self.patterns[pattern].add(client_id)
        
        if client_id not in self.subscribers:
            self.subscribers[client_id] = {'channels': set(), 'patterns': set()}
        
        self.subscribers[client_id]['patterns'].add(pattern)
        
        print(f"📡 Client {client_id} subscribed to pattern '{pattern}'")
    
    def publish(self, channel: str, message: str) -> int:
        """Publish message to channel"""
        recipients = set()
        
        # Direct channel subscribers
        if channel in self.channels:
            recipients.update(self.channels[channel])
        
        # Pattern subscribers
        for pattern, subscribers in self.patterns.items():
            if self._match_pattern(pattern, channel):
                recipients.update(subscribers)
        
        # Simulate message delivery
        for client_id in recipients:
            delivery_latency = random.uniform(0.1, 2.0)
            print(f"   → {client_id}: '{message}' ({delivery_latency:.2f}ms)")
        
        return len(recipients)
    
    def _match_pattern(self, pattern: str, channel: str) -> bool:
        """Simple pattern matching simulation"""
        if '*' in pattern:
            prefix = pattern.replace('*', '')
            return channel.startswith(prefix)
        return pattern == channel
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pub/sub statistics"""
        total_subscribers = len(self.subscribers)
        total_channels = len(self.channels)
        total_patterns = len(self.patterns)
        
        channel_stats = {}
        for channel, subs in self.channels.items():
            channel_stats[channel] = len(subs)
        
        return {
            'total_subscribers': total_subscribers,
            'total_channels': total_channels,
            'total_patterns': total_patterns,
            'channel_subscribers': channel_stats
        }

class RedisLuaScript:
    """Redis Lua scripting simulation"""
    
    def __init__(self):
        self.scripts = {}
    
    def load_script(self, script: str) -> str:
        """Load Lua script and return SHA1 hash"""
        script_hash = hashlib.sha1(script.encode()).hexdigest()
        self.scripts[script_hash] = script
        
        print(f"🔧 Lua script loaded: {script_hash[:12]}...")
        return script_hash
    
    def eval_script(self, script_hash: str, keys: List[str], args: List[str]) -> Any:
        """Execute Lua script"""
        if script_hash not in self.scripts:
            return {'error': 'NOSCRIPT No matching script'}
        
        script = self.scripts[script_hash]
        
        # Simulate script execution
        execution_time = random.uniform(0.5, 5.0)
        
        # Simulate different script types
        if 'incr' in script.lower():
            result = random.randint(1, 100)
        elif 'set' in script.lower():
            result = 'OK'
        elif 'get' in script.lower():
            result = f"value_{random.randint(1000, 9999)}"
        else:
            result = random.randint(0, 1)
        
        print(f"🔧 Script executed: {script_hash[:12]}... → {result} ({execution_time:.2f}ms)")
        return result

class RedisTransaction:
    """Redis transaction (MULTI/EXEC) simulation"""
    
    def __init__(self):
        self.commands = []
        self.watching = set()
    
    def multi(self):
        """Start transaction"""
        self.commands = []
        print(f"🔄 Transaction started (MULTI)")
    
    def watch(self, *keys):
        """Watch keys for changes"""
        self.watching.update(keys)
        print(f"👁️ Watching keys: {', '.join(keys)}")
    
    def queue_command(self, command: str, *args):
        """Queue command in transaction"""
        self.commands.append((command, args))
        print(f"   Queued: {command} {' '.join(map(str, args))}")
    
    def exec(self) -> List[Any]:
        """Execute transaction"""
        if random.random() < 0.1:  # 10% chance of watched key modification
            print(f"❌ Transaction aborted (watched key modified)")
            return None
        
        results = []
        total_time = 0
        
        print(f"🔄 Executing {len(self.commands)} commands atomically...")
        
        for command, args in self.commands:
            # Simulate command execution
            exec_time = random.uniform(0.1, 1.0)
            total_time += exec_time
            
            if command.upper() == 'SET':
                result = 'OK'
            elif command.upper() == 'GET':
                result = f"value_{random.randint(1000, 9999)}"
            elif command.upper() == 'INCR':
                result = random.randint(1, 100)
            elif command.upper() == 'SADD':
                result = random.randint(0, 1)
            else:
                result = 'OK'
            
            results.append(result)
        
        print(f"✅ Transaction completed: {len(results)} commands in {total_time:.2f}ms")
        return results

class RedisCluster:
    """Redis cluster simulation"""
    
    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name
        self.nodes = []
        self.hash_slots = 16384
        self._initialize_cluster()
    
    def _initialize_cluster(self):
        """Initialize 6-node cluster (3 masters + 3 replicas)"""
        slots_per_master = self.hash_slots // 3
        
        # Master nodes
        masters = [
            RedisNode("master1", "10.0.1.10", 7000, "master", 0, slots_per_master - 1),
            RedisNode("master2", "10.0.1.11", 7000, "master", slots_per_master, 2 * slots_per_master - 1),
            RedisNode("master3", "10.0.1.12", 7000, "master", 2 * slots_per_master, self.hash_slots - 1)
        ]
        
        # Replica nodes
        replicas = [
            RedisNode("replica1", "10.0.1.13", 7000, "replica", 0, slots_per_master - 1),
            RedisNode("replica2", "10.0.1.14", 7000, "replica", slots_per_master, 2 * slots_per_master - 1),
            RedisNode("replica3", "10.0.1.15", 7000, "replica", 2 * slots_per_master, self.hash_slots - 1)
        ]
        
        self.nodes = masters + replicas
        
        print(f"🌐 Redis Cluster initialized: {self.cluster_name}")
        print(f"   Nodes: {len(self.nodes)} (3 masters + 3 replicas)")
        print(f"   Hash Slots: {self.hash_slots:,}")
    
    def calculate_slot(self, key: str) -> int:
        """Calculate hash slot for key using CRC16"""
        # Simplified CRC16 simulation
        crc = 0
        for char in key.encode():
            crc ^= char << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        
        return crc % self.hash_slots
    
    def find_node_for_key(self, key: str) -> RedisNode:
        """Find the master node responsible for a key"""
        slot = self.calculate_slot(key)
        
        for node in self.nodes:
            if node.role == "master" and node.slot_start <= slot <= node.slot_end:
                return node
        
        return self.nodes[0]  # Fallback
    
    def simulate_operation(self, operation: str, key: str) -> Dict[str, Any]:
        """Simulate cluster operation"""
        target_node = self.find_node_for_key(key)
        slot = self.calculate_slot(key)
        
        # Simulate network latency
        latency = random.uniform(0.5, 3.0)
        
        # Simulate potential redirections
        redirected = random.random() < 0.05  # 5% chance of redirection
        
        result = {
            'operation': operation,
            'key': key,
            'slot': slot,
            'target_node': f"{target_node.host}:{target_node.port}",
            'node_id': target_node.id,
            'latency_ms': latency,
            'redirected': redirected
        }
        
        if redirected:
            result['redirect_to'] = f"10.0.1.{random.randint(10, 15)}:7000"
            result['latency_ms'] += random.uniform(1.0, 2.0)  # Additional redirect latency
        
        return result
    
    def simulate_failover(self, failed_master: str) -> Dict[str, Any]:
        """Simulate master failover"""
        print(f"\n⚠️ Master Failover Simulation")
        print(f"   Failed Master: {failed_master}")
        
        # Find the failed master and its replica
        failed_node = None
        replica_node = None
        
        for node in self.nodes:
            if node.id == failed_master and node.role == "master":
                failed_node = node
                node.status = "failed"
            elif node.role == "replica" and node.slot_start == failed_node.slot_start if failed_node else False:
                replica_node = node
        
        if replica_node:
            # Promote replica to master
            replica_node.role = "master"
            replica_node.status = "online"
            
            failover_time = random.uniform(5.0, 15.0)  # seconds
            
            print(f"   Promoted Replica: {replica_node.id} → master")
            print(f"   Failover Time: {failover_time:.1f}s")
            print(f"   Affected Slots: {failed_node.slot_start}-{failed_node.slot_end}")
            
            return {
                'failed_master': failed_master,
                'new_master': replica_node.id,
                'failover_time_sec': failover_time,
                'affected_slots': failed_node.slot_end - failed_node.slot_start + 1
            }
        
        return {'error': 'No replica available for failover'}

def demonstrate_redis_operations():
    """Demonstrate comprehensive Redis operations"""
    print("=== Redis Operations Demonstration ===")
    
    # Pub/Sub messaging
    print(f"\n📡 Pub/Sub Messaging")
    pubsub = RedisPubSub()
    
    # Subscribe clients to channels
    pubsub.subscribe("web_app_1", "notifications")
    pubsub.subscribe("web_app_2", "notifications")
    pubsub.subscribe("dashboard", "analytics")
    pubsub.psubscribe("logger", "log:*")
    
    # Publish messages
    print(f"\n   Publishing messages:")
    recipients1 = pubsub.publish("notifications", "New user registered")
    recipients2 = pubsub.publish("analytics", "Page view: /dashboard")
    recipients3 = pubsub.publish("log:error", "Database connection failed")
    
    print(f"   Message delivery summary:")
    print(f"     notifications: {recipients1} recipients")
    print(f"     analytics: {recipients2} recipients")
    print(f"     log:error: {recipients3} recipients")
    
    # Lua scripting
    print(f"\n🔧 Lua Scripting")
    lua = RedisLuaScript()
    
    # Rate limiting script
    rate_limit_script = """
    local key = KEYS[1]
    local limit = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])
    
    local current = redis.call('GET', key)
    if current == false then
        redis.call('SET', key, 1)
        redis.call('EXPIRE', key, window)
        return 1
    end
    
    if tonumber(current) < limit then
        return redis.call('INCR', key)
    else
        return 0
    end
    """
    
    script_hash = lua.load_script(rate_limit_script)
    
    # Execute rate limiting
    for i in range(5):
        result = lua.eval_script(script_hash, ["rate_limit:user123"], ["10", "60"])
        status = "✅ Allowed" if result > 0 else "❌ Rate limited"
        print(f"   Request {i+1}: {status} (count: {result})")
    
    # Transactions
    print(f"\n🔄 Transactions (MULTI/EXEC)")
    transaction = RedisTransaction()
    
    transaction.watch("balance:user123", "balance:user456")
    transaction.multi()
    transaction.queue_command("DECRBY", "balance:user123", 100)
    transaction.queue_command("INCRBY", "balance:user456", 100)
    transaction.queue_command("SADD", "transactions", "transfer:123")
    
    results = transaction.exec()
    if results:
        print(f"   Results: {results}")
    
    # Redis Cluster operations
    print(f"\n🌐 Redis Cluster Operations")
    cluster = RedisCluster("production-cluster")
    
    # Simulate various operations
    test_keys = ["user:1001", "session:abc123", "cache:homepage", "counter:views"]
    
    print(f"\n   Key distribution:")
    for key in test_keys:
        op_result = cluster.simulate_operation("GET", key)
        redirect_info = f" (redirected to {op_result['redirect_to']})" if op_result['redirected'] else ""
        print(f"     {key} → slot {op_result['slot']} on {op_result['target_node']}{redirect_info}")
    
    # Simulate failover
    failover_result = cluster.simulate_failover("master2")
    
    # Performance monitoring
    print(f"\n📊 Performance Monitoring")
    
    # Simulate memory usage
    memory_stats = {
        'used_memory': random.randint(500, 2000),  # MB
        'used_memory_peak': random.randint(800, 2500),
        'connected_clients': random.randint(50, 500),
        'total_commands_processed': random.randint(1000000, 10000000),
        'instantaneous_ops_per_sec': random.randint(1000, 50000),
        'keyspace_hits': random.randint(800000, 5000000),
        'keyspace_misses': random.randint(100000, 800000)
    }
    
    hit_ratio = (memory_stats['keyspace_hits'] / 
                (memory_stats['keyspace_hits'] + memory_stats['keyspace_misses'])) * 100
    
    print(f"   Memory Usage: {memory_stats['used_memory']}MB (peak: {memory_stats['used_memory_peak']}MB)")
    print(f"   Connected Clients: {memory_stats['connected_clients']}")
    print(f"   Operations/sec: {memory_stats['instantaneous_ops_per_sec']:,}")
    print(f"   Cache Hit Ratio: {hit_ratio:.1f}%")
    print(f"   Total Commands: {memory_stats['total_commands_processed']:,}")

if __name__ == "__main__":
    demonstrate_redis_operations()
    
    print(f"\n🎯 Redis operations enable high-performance in-memory data management")
    print(f"💡 Key features: pub/sub messaging, Lua scripting, transactions, clustering")
    print(f"🚀 Production capabilities: sub-millisecond latency, horizontal scaling, persistence")
