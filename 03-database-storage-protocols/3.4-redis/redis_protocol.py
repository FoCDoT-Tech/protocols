#!/usr/bin/env python3
"""
Redis RESP Protocol Simulation
Demonstrates Redis Serialization Protocol (RESP) including message encoding,
data types, pipelining, and pub/sub operations.
"""

import time
import random
import socket
from typing import Dict, List, Any, Optional, Union
from enum import Enum

class RESPType(Enum):
    """RESP data types"""
    SIMPLE_STRING = '+'
    ERROR = '-'
    INTEGER = ':'
    BULK_STRING = '$'
    ARRAY = '*'

class RESPProtocol:
    """Redis RESP Protocol implementation"""
    
    def __init__(self, host: str = "localhost", port: int = 6379):
        self.host = host
        self.port = port
        self.connection_id = random.randint(1000, 9999)
        
        print(f"🔴 Redis RESP Protocol initialized")
        print(f"   Host: {self.host}:{self.port}")
        print(f"   Connection ID: {self.connection_id}")
        print(f"   Protocol: RESP2")
    
    def encode_simple_string(self, value: str) -> bytes:
        """Encode RESP simple string: +OK\r\n"""
        return f"+{value}\r\n".encode('utf-8')
    
    def encode_error(self, error_type: str, message: str) -> bytes:
        """Encode RESP error: -ERR message\r\n"""
        return f"-{error_type} {message}\r\n".encode('utf-8')
    
    def encode_integer(self, value: int) -> bytes:
        """Encode RESP integer: :1000\r\n"""
        return f":{value}\r\n".encode('utf-8')
    
    def encode_bulk_string(self, value: Optional[str]) -> bytes:
        """Encode RESP bulk string: $6\r\nfoobar\r\n or $-1\r\n for null"""
        if value is None:
            return b"$-1\r\n"
        
        value_bytes = value.encode('utf-8')
        return f"${len(value_bytes)}\r\n".encode('utf-8') + value_bytes + b"\r\n"
    
    def encode_array(self, items: Optional[List[Any]]) -> bytes:
        """Encode RESP array: *2\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"""
        if items is None:
            return b"*-1\r\n"
        
        result = f"*{len(items)}\r\n".encode('utf-8')
        
        for item in items:
            if isinstance(item, str):
                result += self.encode_bulk_string(item)
            elif isinstance(item, int):
                result += self.encode_integer(item)
            elif isinstance(item, list):
                result += self.encode_array(item)
            elif item is None:
                result += self.encode_bulk_string(None)
        
        return result
    
    def decode_resp(self, data: bytes) -> Any:
        """Decode RESP message"""
        if not data:
            return None
        
        data_str = data.decode('utf-8')
        type_char = data_str[0]
        
        if type_char == '+':
            # Simple string
            return data_str[1:].rstrip('\r\n')
        elif type_char == '-':
            # Error
            error_msg = data_str[1:].rstrip('\r\n')
            return {'error': error_msg}
        elif type_char == ':':
            # Integer
            return int(data_str[1:].rstrip('\r\n'))
        elif type_char == '$':
            # Bulk string
            lines = data_str.split('\r\n')
            length = int(lines[0][1:])
            if length == -1:
                return None
            return lines[1]
        elif type_char == '*':
            # Array
            lines = data_str.split('\r\n')
            array_length = int(lines[0][1:])
            if array_length == -1:
                return None
            
            # Simplified array parsing for demo
            result = []
            line_idx = 1
            for i in range(array_length):
                if lines[line_idx].startswith('$'):
                    bulk_length = int(lines[line_idx][1:])
                    if bulk_length == -1:
                        result.append(None)
                        line_idx += 1
                    else:
                        result.append(lines[line_idx + 1])
                        line_idx += 2
                elif lines[line_idx].startswith(':'):
                    result.append(int(lines[line_idx][1:]))
                    line_idx += 1
            
            return result
        
        return data_str
    
    def create_command(self, *args) -> bytes:
        """Create RESP command array"""
        return self.encode_array([str(arg) for arg in args])
    
    def simulate_get_operation(self, key: str) -> Dict[str, Any]:
        """Simulate GET operation"""
        command = self.create_command("GET", key)
        
        # Simulate response
        if random.choice([True, False]):
            # Key exists
            value = f"value_for_{key}_{random.randint(1000, 9999)}"
            response = self.encode_bulk_string(value)
            decoded_response = value
        else:
            # Key doesn't exist
            response = self.encode_bulk_string(None)
            decoded_response = None
        
        return {
            'command': command,
            'response': response,
            'decoded': decoded_response,
            'latency_ms': random.uniform(0.1, 2.0)
        }
    
    def simulate_set_operation(self, key: str, value: str, ttl: Optional[int] = None) -> Dict[str, Any]:
        """Simulate SET operation"""
        if ttl:
            command = self.create_command("SET", key, value, "EX", ttl)
        else:
            command = self.create_command("SET", key, value)
        
        # SET always returns OK
        response = self.encode_simple_string("OK")
        decoded_response = "OK"
        
        return {
            'command': command,
            'response': response,
            'decoded': decoded_response,
            'latency_ms': random.uniform(0.1, 1.5)
        }
    
    def simulate_hash_operations(self, key: str) -> Dict[str, Any]:
        """Simulate hash operations (HSET, HGET, HGETALL)"""
        operations = []
        
        # HSET operation
        hset_cmd = self.create_command("HSET", key, "field1", "value1", "field2", "value2")
        hset_response = self.encode_integer(2)  # Number of fields added
        operations.append({
            'operation': 'HSET',
            'command': hset_cmd,
            'response': hset_response,
            'decoded': 2
        })
        
        # HGET operation
        hget_cmd = self.create_command("HGET", key, "field1")
        hget_response = self.encode_bulk_string("value1")
        operations.append({
            'operation': 'HGET',
            'command': hget_cmd,
            'response': hget_response,
            'decoded': "value1"
        })
        
        # HGETALL operation
        hgetall_cmd = self.create_command("HGETALL", key)
        hgetall_response = self.encode_array(["field1", "value1", "field2", "value2"])
        operations.append({
            'operation': 'HGETALL',
            'command': hgetall_cmd,
            'response': hgetall_response,
            'decoded': ["field1", "value1", "field2", "value2"]
        })
        
        return {
            'key': key,
            'operations': operations,
            'total_latency_ms': sum(random.uniform(0.1, 1.0) for _ in operations)
        }
    
    def simulate_list_operations(self, key: str) -> Dict[str, Any]:
        """Simulate list operations (LPUSH, RPOP, LRANGE)"""
        operations = []
        
        # LPUSH operation
        lpush_cmd = self.create_command("LPUSH", key, "item1", "item2", "item3")
        lpush_response = self.encode_integer(3)  # New length of list
        operations.append({
            'operation': 'LPUSH',
            'command': lpush_cmd,
            'response': lpush_response,
            'decoded': 3
        })
        
        # RPOP operation
        rpop_cmd = self.create_command("RPOP", key)
        rpop_response = self.encode_bulk_string("item1")
        operations.append({
            'operation': 'RPOP',
            'command': rpop_cmd,
            'response': rpop_response,
            'decoded': "item1"
        })
        
        # LRANGE operation
        lrange_cmd = self.create_command("LRANGE", key, 0, -1)
        lrange_response = self.encode_array(["item3", "item2"])
        operations.append({
            'operation': 'LRANGE',
            'command': lrange_cmd,
            'response': lrange_response,
            'decoded': ["item3", "item2"]
        })
        
        return {
            'key': key,
            'operations': operations,
            'total_latency_ms': sum(random.uniform(0.1, 1.0) for _ in operations)
        }
    
    def simulate_sorted_set_operations(self, key: str) -> Dict[str, Any]:
        """Simulate sorted set operations (ZADD, ZRANGE, ZRANK)"""
        operations = []
        
        # ZADD operation
        zadd_cmd = self.create_command("ZADD", key, 100, "player1", 200, "player2", 150, "player3")
        zadd_response = self.encode_integer(3)  # Number of elements added
        operations.append({
            'operation': 'ZADD',
            'command': zadd_cmd,
            'response': zadd_response,
            'decoded': 3
        })
        
        # ZRANGE operation (by rank)
        zrange_cmd = self.create_command("ZRANGE", key, 0, -1, "WITHSCORES")
        zrange_response = self.encode_array(["player1", "100", "player3", "150", "player2", "200"])
        operations.append({
            'operation': 'ZRANGE',
            'command': zrange_cmd,
            'response': zrange_response,
            'decoded': ["player1", "100", "player3", "150", "player2", "200"]
        })
        
        # ZRANK operation
        zrank_cmd = self.create_command("ZRANK", key, "player2")
        zrank_response = self.encode_integer(2)  # Rank (0-based)
        operations.append({
            'operation': 'ZRANK',
            'command': zrank_cmd,
            'response': zrank_response,
            'decoded': 2
        })
        
        return {
            'key': key,
            'operations': operations,
            'total_latency_ms': sum(random.uniform(0.1, 1.0) for _ in operations)
        }
    
    def simulate_pipelining(self, commands: List[str]) -> Dict[str, Any]:
        """Simulate pipelined operations"""
        pipeline_commands = []
        pipeline_responses = []
        
        for cmd in commands:
            if cmd.startswith("GET"):
                key = cmd.split()[1]
                command = self.create_command("GET", key)
                response = self.encode_bulk_string(f"value_{key}")
            elif cmd.startswith("SET"):
                parts = cmd.split()
                key, value = parts[1], parts[2]
                command = self.create_command("SET", key, value)
                response = self.encode_simple_string("OK")
            elif cmd.startswith("INCR"):
                key = cmd.split()[1]
                command = self.create_command("INCR", key)
                response = self.encode_integer(random.randint(1, 100))
            else:
                command = self.create_command(*cmd.split())
                response = self.encode_simple_string("OK")
            
            pipeline_commands.append(command)
            pipeline_responses.append(response)
        
        # Simulate network round trip savings
        single_latency = len(commands) * random.uniform(0.5, 2.0)  # Individual commands
        pipeline_latency = random.uniform(1.0, 3.0)  # Single round trip
        
        return {
            'commands': pipeline_commands,
            'responses': pipeline_responses,
            'command_count': len(commands),
            'single_latency_ms': single_latency,
            'pipeline_latency_ms': pipeline_latency,
            'improvement': (single_latency / pipeline_latency)
        }
    
    def demonstrate_resp_protocol(self) -> Dict[str, Any]:
        """Demonstrate comprehensive RESP protocol operations"""
        results = {}
        
        print(f"\n=== Redis RESP Protocol Operations ===")
        
        # Basic GET/SET operations
        print(f"\n🔑 Basic Key-Value Operations")
        
        # SET operation
        set_result = self.simulate_set_operation("user:1001", "john_doe", ttl=3600)
        print(f"   SET user:1001 'john_doe' EX 3600")
        print(f"   Command: {len(set_result['command'])} bytes")
        print(f"   Response: {set_result['decoded']}")
        print(f"   Latency: {set_result['latency_ms']:.2f}ms")
        
        # GET operation
        get_result = self.simulate_get_operation("user:1001")
        print(f"   GET user:1001")
        print(f"   Command: {len(get_result['command'])} bytes")
        print(f"   Response: {get_result['decoded'] or 'nil'}")
        print(f"   Latency: {get_result['latency_ms']:.2f}ms")
        
        results['basic_ops'] = {'set': set_result, 'get': get_result}
        
        # Hash operations
        print(f"\n🗂️ Hash Operations")
        hash_result = self.simulate_hash_operations("session:abc123")
        
        for op in hash_result['operations']:
            print(f"   {op['operation']}: {op['decoded']}")
        
        print(f"   Total Latency: {hash_result['total_latency_ms']:.2f}ms")
        results['hash_ops'] = hash_result
        
        # List operations
        print(f"\n📝 List Operations")
        list_result = self.simulate_list_operations("queue:tasks")
        
        for op in list_result['operations']:
            print(f"   {op['operation']}: {op['decoded']}")
        
        print(f"   Total Latency: {list_result['total_latency_ms']:.2f}ms")
        results['list_ops'] = list_result
        
        # Sorted set operations
        print(f"\n🏆 Sorted Set Operations (Leaderboard)")
        zset_result = self.simulate_sorted_set_operations("leaderboard:game1")
        
        for op in zset_result['operations']:
            print(f"   {op['operation']}: {op['decoded']}")
        
        print(f"   Total Latency: {zset_result['total_latency_ms']:.2f}ms")
        results['zset_ops'] = zset_result
        
        # Pipelining demonstration
        print(f"\n⚡ Pipelining Operations")
        pipeline_commands = [
            "SET counter:page_views 1000",
            "INCR counter:page_views",
            "GET counter:page_views",
            "SET user:active true",
            "GET user:active"
        ]
        
        pipeline_result = self.simulate_pipelining(pipeline_commands)
        print(f"   Commands: {pipeline_result['command_count']}")
        print(f"   Individual Latency: {pipeline_result['single_latency_ms']:.2f}ms")
        print(f"   Pipeline Latency: {pipeline_result['pipeline_latency_ms']:.2f}ms")
        print(f"   Performance Improvement: {pipeline_result['improvement']:.1f}x")
        
        results['pipelining'] = pipeline_result
        
        return results

def demonstrate_redis_features():
    """Demonstrate advanced Redis features"""
    print(f"\n=== Advanced Redis Features ===")
    
    # Pub/Sub messaging
    print(f"\n📡 Pub/Sub Messaging")
    
    channels = ["notifications", "chat:room1", "analytics:events"]
    subscribers = random.randint(5, 50)
    messages_per_sec = random.randint(100, 1000)
    
    print(f"   Active Channels: {len(channels)}")
    print(f"   Total Subscribers: {subscribers}")
    print(f"   Message Rate: {messages_per_sec}/sec")
    
    for channel in channels:
        channel_subs = random.randint(1, 20)
        print(f"     {channel}: {channel_subs} subscribers")
    
    # Memory usage and optimization
    print(f"\n💾 Memory Usage & Optimization")
    
    data_structures = {
        'Strings': {'count': 50000, 'memory_mb': 45.2},
        'Hashes': {'count': 15000, 'memory_mb': 78.9},
        'Lists': {'count': 8000, 'memory_mb': 23.1},
        'Sets': {'count': 12000, 'memory_mb': 34.7},
        'Sorted Sets': {'count': 5000, 'memory_mb': 67.3}
    }
    
    total_memory = sum(ds['memory_mb'] for ds in data_structures.values())
    total_keys = sum(ds['count'] for ds in data_structures.values())
    
    print(f"   Total Keys: {total_keys:,}")
    print(f"   Total Memory: {total_memory:.1f}MB")
    print(f"   Memory per Key: {(total_memory * 1024 * 1024 / total_keys):.0f} bytes")
    
    for ds_type, stats in data_structures.items():
        percentage = (stats['memory_mb'] / total_memory) * 100
        print(f"     {ds_type}: {stats['count']:,} keys, {stats['memory_mb']:.1f}MB ({percentage:.1f}%)")
    
    # Persistence strategies
    print(f"\n💿 Persistence Strategies")
    
    persistence_configs = [
        ("RDB Snapshot", "save 900 1", "Point-in-time backup", "Low overhead"),
        ("AOF Always", "appendfsync always", "Every command logged", "Maximum durability"),
        ("AOF Every Sec", "appendfsync everysec", "Fsync every second", "Balanced approach"),
        ("Hybrid", "RDB + AOF", "Best of both worlds", "Redis 4.0+ default")
    ]
    
    for strategy, config, description, benefit in persistence_configs:
        print(f"   {strategy}:")
        print(f"     Config: {config}")
        print(f"     {description} - {benefit}")
    
    # Performance characteristics
    print(f"\n📊 Performance Characteristics")
    
    operations = ['GET', 'SET', 'HGET', 'LPUSH', 'ZADD', 'PUBLISH']
    throughput = [100000, 85000, 95000, 90000, 75000, 80000]  # ops/sec
    latency = [0.1, 0.15, 0.12, 0.13, 0.18, 0.14]  # ms
    
    print(f"   Single-threaded performance:")
    for op, tput, lat in zip(operations, throughput, latency):
        print(f"     {op}: {tput:,} ops/sec, {lat}ms avg latency")
    
    # Redis Cluster simulation
    print(f"\n🌐 Redis Cluster")
    
    cluster_nodes = 6
    hash_slots = 16384
    slots_per_node = hash_slots // cluster_nodes
    
    print(f"   Cluster Nodes: {cluster_nodes}")
    print(f"   Hash Slots: {hash_slots:,}")
    print(f"   Slots per Node: {slots_per_node:,}")
    print(f"   Replication Factor: 1 (each master has 1 replica)")
    
    for i in range(cluster_nodes // 2):
        master_start = i * slots_per_node
        master_end = master_start + slots_per_node - 1
        print(f"     Master {i+1}: slots {master_start}-{master_end}")
        print(f"     Replica {i+1}: backup for Master {i+1}")

if __name__ == "__main__":
    # Initialize Redis RESP protocol
    redis_protocol = RESPProtocol()
    
    # Demonstrate core operations
    operation_results = redis_protocol.demonstrate_resp_protocol()
    
    # Demonstrate advanced features
    demonstrate_redis_features()
    
    print(f"\n🎯 Redis RESP protocol enables high-performance in-memory data operations")
    print(f"💡 Key benefits: simple protocol, sub-millisecond latency, rich data types")
    print(f"🚀 Production features: pub/sub messaging, clustering, persistence, Lua scripting")
