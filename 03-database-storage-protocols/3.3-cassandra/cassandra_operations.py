#!/usr/bin/env python3
"""
Cassandra Operations and Cluster Management Simulation
Demonstrates advanced Cassandra operations including consistency levels,
token-aware routing, multi-datacenter replication, and repair operations.
"""

import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ConsistencyLevel(Enum):
    """Cassandra consistency levels"""
    ANY = "ANY"
    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    QUORUM = "QUORUM"
    ALL = "ALL"
    LOCAL_QUORUM = "LOCAL_QUORUM"
    EACH_QUORUM = "EACH_QUORUM"
    SERIAL = "SERIAL"
    LOCAL_SERIAL = "LOCAL_SERIAL"
    LOCAL_ONE = "LOCAL_ONE"

@dataclass
class CassandraNode:
    """Cassandra cluster node"""
    ip: str
    datacenter: str
    rack: str
    token_start: int
    token_end: int
    status: str = "UP"
    load: float = 0.0  # GB

@dataclass
class ReplicationStrategy:
    """Cassandra replication strategy"""
    strategy_class: str
    replication_factors: Dict[str, int]

class CassandraCluster:
    """Cassandra cluster simulation"""
    
    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name
        self.nodes = []
        self.keyspaces = {}
        self.token_ring = {}
        self.repair_sessions = []
        
        # Initialize cluster topology
        self._initialize_cluster()
        
        print(f"🔷 Cassandra Cluster initialized")
        print(f"   Cluster: {self.cluster_name}")
        print(f"   Nodes: {len(self.nodes)}")
        print(f"   Datacenters: {len(set(node.datacenter for node in self.nodes))}")
    
    def _initialize_cluster(self):
        """Initialize cluster with nodes across multiple datacenters"""
        # US-East datacenter
        us_east_nodes = [
            CassandraNode("10.1.1.10", "us-east", "rack1", -9223372036854775808, -6148914691236517206),
            CassandraNode("10.1.1.11", "us-east", "rack2", -6148914691236517205, -3074457345618258603),
            CassandraNode("10.1.1.12", "us-east", "rack3", -3074457345618258602, 0)
        ]
        
        # US-West datacenter
        us_west_nodes = [
            CassandraNode("10.2.1.10", "us-west", "rack1", 1, 3074457345618258603),
            CassandraNode("10.2.1.11", "us-west", "rack2", 3074457345618258604, 6148914691236517206),
            CassandraNode("10.2.1.12", "us-west", "rack3", 6148914691236517207, 9223372036854775807)
        ]
        
        self.nodes = us_east_nodes + us_west_nodes
        
        # Simulate node loads
        for node in self.nodes:
            node.load = random.uniform(50.0, 200.0)  # GB
    
    def create_keyspace(self, keyspace: str, replication: ReplicationStrategy):
        """Create keyspace with replication strategy"""
        self.keyspaces[keyspace] = replication
        
        print(f"🗄️ Keyspace Created: {keyspace}")
        print(f"   Strategy: {replication.strategy_class}")
        for dc, rf in replication.replication_factors.items():
            print(f"   {dc}: RF={rf}")
    
    def get_token_for_key(self, partition_key: str) -> int:
        """Calculate token for partition key using Murmur3 hash simulation"""
        # Simplified hash simulation
        hash_value = hash(partition_key)
        # Map to Cassandra token range
        return hash_value % (2**63)
    
    def find_replica_nodes(self, partition_key: str, keyspace: str) -> List[CassandraNode]:
        """Find replica nodes for a given partition key"""
        if keyspace not in self.keyspaces:
            raise ValueError(f"Keyspace {keyspace} not found")
        
        token = self.get_token_for_key(partition_key)
        replication = self.keyspaces[keyspace]
        replicas = []
        
        # Find nodes that should hold replicas
        for dc, rf in replication.replication_factors.items():
            dc_nodes = [node for node in self.nodes if node.datacenter == dc]
            
            # Find primary node for this token in datacenter
            primary_node = None
            for node in dc_nodes:
                if node.token_start <= token <= node.token_end:
                    primary_node = node
                    break
            
            if not primary_node:
                # Wrap around the ring
                primary_node = min(dc_nodes, key=lambda n: n.token_start)
            
            # Add primary and next RF-1 nodes
            primary_idx = dc_nodes.index(primary_node)
            for i in range(rf):
                replica_idx = (primary_idx + i) % len(dc_nodes)
                replicas.append(dc_nodes[replica_idx])
        
        return replicas
    
    def simulate_read_operation(self, partition_key: str, keyspace: str, 
                              consistency: ConsistencyLevel) -> Dict[str, Any]:
        """Simulate read operation with consistency level"""
        replicas = self.find_replica_nodes(partition_key, keyspace)
        
        # Determine required responses based on consistency level
        if consistency == ConsistencyLevel.ONE:
            required_responses = 1
        elif consistency == ConsistencyLevel.QUORUM:
            required_responses = (len(replicas) // 2) + 1
        elif consistency == ConsistencyLevel.ALL:
            required_responses = len(replicas)
        elif consistency == ConsistencyLevel.LOCAL_QUORUM:
            local_replicas = [r for r in replicas if r.datacenter == replicas[0].datacenter]
            required_responses = (len(local_replicas) // 2) + 1
        else:
            required_responses = 1
        
        # Simulate response times
        response_times = []
        for i, replica in enumerate(replicas[:required_responses]):
            # Simulate network latency based on datacenter
            if replica.datacenter == "us-east":
                latency = random.uniform(1, 5)  # Local DC
            else:
                latency = random.uniform(50, 100)  # Cross-DC
            
            response_times.append(latency)
        
        total_latency = max(response_times)  # Slowest response determines total time
        
        result = {
            'partition_key': partition_key,
            'replicas_contacted': len(replicas[:required_responses]),
            'total_replicas': len(replicas),
            'consistency_level': consistency.value,
            'latency_ms': total_latency,
            'coordinator_node': replicas[0].ip
        }
        
        return result
    
    def simulate_write_operation(self, partition_key: str, keyspace: str, 
                               consistency: ConsistencyLevel) -> Dict[str, Any]:
        """Simulate write operation with consistency level"""
        replicas = self.find_replica_nodes(partition_key, keyspace)
        
        # Determine required acknowledgments
        if consistency == ConsistencyLevel.ANY:
            required_acks = 1  # Can be hinted handoff
        elif consistency == ConsistencyLevel.ONE:
            required_acks = 1
        elif consistency == ConsistencyLevel.QUORUM:
            required_acks = (len(replicas) // 2) + 1
        elif consistency == ConsistencyLevel.ALL:
            required_acks = len(replicas)
        elif consistency == ConsistencyLevel.LOCAL_QUORUM:
            local_replicas = [r for r in replicas if r.datacenter == replicas[0].datacenter]
            required_acks = (len(local_replicas) // 2) + 1
        else:
            required_acks = 1
        
        # Simulate write latencies
        ack_times = []
        for i, replica in enumerate(replicas):
            if replica.datacenter == "us-east":
                latency = random.uniform(0.5, 3)  # Local writes are faster
            else:
                latency = random.uniform(25, 75)  # Cross-DC writes
            
            ack_times.append(latency)
        
        # Sort by response time and take required acknowledgments
        ack_times.sort()
        write_latency = ack_times[required_acks - 1]
        
        result = {
            'partition_key': partition_key,
            'replicas_written': len(replicas),
            'acks_required': required_acks,
            'consistency_level': consistency.value,
            'latency_ms': write_latency,
            'coordinator_node': replicas[0].ip
        }
        
        return result

class CassandraRepairManager:
    """Cassandra repair operations manager"""
    
    def __init__(self, cluster: CassandraCluster):
        self.cluster = cluster
        self.repair_history = []
    
    def simulate_incremental_repair(self, keyspace: str, table: str) -> Dict[str, Any]:
        """Simulate incremental repair operation"""
        print(f"\n🔧 Incremental Repair")
        print(f"   Keyspace: {keyspace}")
        print(f"   Table: {table}")
        
        # Simulate repair across all nodes
        repair_sessions = []
        total_data_repaired = 0
        
        for node in self.cluster.nodes:
            # Simulate repair work
            data_repaired = random.uniform(0.1, 5.0)  # GB
            repair_time = random.uniform(30, 300)  # seconds
            
            session = {
                'node': node.ip,
                'datacenter': node.datacenter,
                'data_repaired_gb': data_repaired,
                'repair_time_sec': repair_time,
                'inconsistencies_found': random.randint(0, 50)
            }
            
            repair_sessions.append(session)
            total_data_repaired += data_repaired
            
            print(f"   {node.ip}: {data_repaired:.2f}GB in {repair_time:.1f}s")
        
        repair_result = {
            'keyspace': keyspace,
            'table': table,
            'repair_type': 'incremental',
            'total_data_repaired_gb': total_data_repaired,
            'total_time_sec': max(session['repair_time_sec'] for session in repair_sessions),
            'sessions': repair_sessions
        }
        
        self.repair_history.append(repair_result)
        print(f"   Total: {total_data_repaired:.2f}GB repaired")
        
        return repair_result
    
    def simulate_full_repair(self, keyspace: str) -> Dict[str, Any]:
        """Simulate full repair operation"""
        print(f"\n🔧 Full Repair")
        print(f"   Keyspace: {keyspace}")
        
        # Full repair takes longer and processes more data
        repair_sessions = []
        total_data_repaired = 0
        
        for node in self.cluster.nodes:
            data_repaired = random.uniform(10, 50)  # GB
            repair_time = random.uniform(1800, 7200)  # 30min - 2hrs
            
            session = {
                'node': node.ip,
                'datacenter': node.datacenter,
                'data_repaired_gb': data_repaired,
                'repair_time_sec': repair_time,
                'inconsistencies_found': random.randint(100, 1000)
            }
            
            repair_sessions.append(session)
            total_data_repaired += data_repaired
            
            print(f"   {node.ip}: {data_repaired:.1f}GB in {repair_time/60:.1f}min")
        
        repair_result = {
            'keyspace': keyspace,
            'repair_type': 'full',
            'total_data_repaired_gb': total_data_repaired,
            'total_time_sec': max(session['repair_time_sec'] for session in repair_sessions),
            'sessions': repair_sessions
        }
        
        self.repair_history.append(repair_result)
        print(f"   Total: {total_data_repaired:.1f}GB repaired in {repair_result['total_time_sec']/60:.1f}min")
        
        return repair_result

def demonstrate_cassandra_operations():
    """Demonstrate comprehensive Cassandra operations"""
    print("=== Cassandra Operations Demonstration ===")
    
    # Initialize cluster
    cluster = CassandraCluster("production-cluster")
    
    # Create keyspaces with different replication strategies
    print(f"\n🗄️ Keyspace Management")
    
    # IoT sensor data keyspace
    iot_replication = ReplicationStrategy(
        strategy_class="NetworkTopologyStrategy",
        replication_factors={"us-east": 3, "us-west": 2}
    )
    cluster.create_keyspace("iot_sensors", iot_replication)
    
    # User data keyspace
    user_replication = ReplicationStrategy(
        strategy_class="NetworkTopologyStrategy", 
        replication_factors={"us-east": 3, "us-west": 3}
    )
    cluster.create_keyspace("user_data", user_replication)
    
    # Demonstrate read operations with different consistency levels
    print(f"\n📖 Read Operations")
    
    read_scenarios = [
        ("device_12345", ConsistencyLevel.ONE),
        ("device_67890", ConsistencyLevel.LOCAL_QUORUM),
        ("device_11111", ConsistencyLevel.QUORUM),
        ("device_22222", ConsistencyLevel.ALL)
    ]
    
    for partition_key, consistency in read_scenarios:
        result = cluster.simulate_read_operation(partition_key, "iot_sensors", consistency)
        print(f"   {partition_key} ({consistency.value}): {result['latency_ms']:.2f}ms")
        print(f"     Replicas: {result['replicas_contacted']}/{result['total_replicas']}")
        print(f"     Coordinator: {result['coordinator_node']}")
    
    # Demonstrate write operations
    print(f"\n✏️ Write Operations")
    
    write_scenarios = [
        ("user_alice", ConsistencyLevel.ONE),
        ("user_bob", ConsistencyLevel.LOCAL_QUORUM),
        ("user_charlie", ConsistencyLevel.QUORUM),
        ("user_diana", ConsistencyLevel.ALL)
    ]
    
    for partition_key, consistency in write_scenarios:
        result = cluster.simulate_write_operation(partition_key, "user_data", consistency)
        print(f"   {partition_key} ({consistency.value}): {result['latency_ms']:.2f}ms")
        print(f"     Acknowledgments: {result['acks_required']}/{result['replicas_written']}")
        print(f"     Coordinator: {result['coordinator_node']}")
    
    # Token-aware routing demonstration
    print(f"\n🎯 Token-Aware Routing")
    
    test_keys = ["sensor_001", "sensor_002", "sensor_003"]
    for key in test_keys:
        token = cluster.get_token_for_key(key)
        replicas = cluster.find_replica_nodes(key, "iot_sensors")
        
        print(f"   Key: {key}")
        print(f"     Token: {token}")
        print(f"     Replicas: {[f'{r.ip}({r.datacenter})' for r in replicas]}")
    
    # Repair operations
    print(f"\n🔧 Repair Operations")
    repair_manager = CassandraRepairManager(cluster)
    
    # Incremental repair
    repair_manager.simulate_incremental_repair("iot_sensors", "sensor_readings")
    
    # Full repair
    repair_manager.simulate_full_repair("user_data")
    
    # Cluster health monitoring
    print(f"\n📊 Cluster Health")
    
    total_load = sum(node.load for node in cluster.nodes)
    avg_load = total_load / len(cluster.nodes)
    
    print(f"   Total Cluster Load: {total_load:.1f}GB")
    print(f"   Average Node Load: {avg_load:.1f}GB")
    print(f"   Load Distribution:")
    
    for node in cluster.nodes:
        load_percentage = (node.load / total_load) * 100
        status_icon = "✅" if node.status == "UP" else "❌"
        print(f"     {node.ip} ({node.datacenter}): {node.load:.1f}GB ({load_percentage:.1f}%) {status_icon}")

if __name__ == "__main__":
    demonstrate_cassandra_operations()
    
    print(f"\n🎯 Cassandra operations enable massive scale distributed database management")
    print(f"💡 Key features: tunable consistency, token-aware routing, multi-DC replication")
    print(f"🚀 Production capabilities: linear scalability, automatic repair, high availability")
