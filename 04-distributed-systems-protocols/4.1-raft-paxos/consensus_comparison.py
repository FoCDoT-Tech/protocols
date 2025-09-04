#!/usr/bin/env python3
"""
Raft vs Paxos Consensus Comparison
Performance and behavior analysis of both algorithms.
"""

import time
import random
import statistics
from typing import List, Dict, Tuple
from raft_consensus import RaftCluster
from paxos_consensus import PaxosCluster

class ConsensusComparison:
    def __init__(self):
        self.results = {
            'raft': {
                'latency': [],
                'throughput': [],
                'leader_elections': 0,
                'success_rate': 0,
                'partition_tolerance': 0
            },
            'paxos': {
                'latency': [],
                'throughput': [],
                'proposals': 0,
                'success_rate': 0,
                'partition_tolerance': 0
            }
        }
    
    def benchmark_raft(self, node_count: int = 5, operations: int = 10) -> Dict:
        """Benchmark Raft consensus performance"""
        print(f"🔬 Benchmarking Raft with {node_count} nodes, {operations} operations")
        
        cluster = RaftCluster(node_count)
        cluster.start_election(0)
        time.sleep(0.1)  # Wait for leader election
        
        latencies = []
        successes = 0
        
        for i in range(operations):
            leader_id = cluster.get_leader()
            if leader_id is None:
                continue
            
            start_time = time.time()
            success = cluster.replicate_log(leader_id, f"operation_{i}")
            end_time = time.time()
            
            if success:
                latencies.append((end_time - start_time) * 1000)  # ms
                successes += 1
            
            time.sleep(0.05)  # Small delay between operations
        
        # Test partition tolerance
        cluster.simulate_partition([0, 1])
        partition_successes = 0
        for i in range(3):
            leader_id = cluster.get_leader()
            if leader_id is not None and leader_id not in [0, 1]:
                if cluster.replicate_log(leader_id, f"partition_op_{i}"):
                    partition_successes += 1
            time.sleep(0.05)
        
        cluster.heal_partition()
        
        return {
            'avg_latency': statistics.mean(latencies) if latencies else 0,
            'throughput': successes / (operations * 0.05) if operations > 0 else 0,
            'success_rate': successes / operations if operations > 0 else 0,
            'partition_tolerance': partition_successes / 3,
            'leader_elections': cluster.stats['elections']
        }
    
    def benchmark_paxos(self, node_count: int = 5, operations: int = 10) -> Dict:
        """Benchmark Paxos consensus performance"""
        print(f"🔬 Benchmarking Paxos with {node_count} nodes, {operations} operations")
        
        cluster = PaxosCluster(node_count)
        
        latencies = []
        successes = 0
        
        for i in range(operations):
            proposer_id = random.randint(0, node_count - 1)
            
            start_time = time.time()
            success = cluster.propose_value(proposer_id, f"operation_{i}")
            end_time = time.time()
            
            if success:
                latencies.append((end_time - start_time) * 1000)  # ms
                successes += 1
            
            time.sleep(0.05)  # Small delay between operations
        
        # Test partition tolerance
        cluster.simulate_partition([0, 1])
        partition_successes = 0
        for i in range(3):
            proposer_id = random.choice([0, 1])  # Majority partition
            if cluster.propose_value(proposer_id, f"partition_op_{i}"):
                partition_successes += 1
            time.sleep(0.05)
        
        cluster.heal_partition()
        
        return {
            'avg_latency': statistics.mean(latencies) if latencies else 0,
            'throughput': successes / (operations * 0.05) if operations > 0 else 0,
            'success_rate': successes / operations if operations > 0 else 0,
            'partition_tolerance': partition_successes / 3,
            'proposals': cluster.stats['proposals']
        }
    
    def run_comparison(self):
        """Run comprehensive comparison between Raft and Paxos"""
        print("=== Raft vs Paxos Consensus Comparison ===\n")
        
        # Test different cluster sizes
        cluster_sizes = [3, 5, 7]
        operations_per_test = 10
        
        for size in cluster_sizes:
            print(f"📊 Testing with {size} nodes:")
            
            # Benchmark Raft
            raft_results = self.benchmark_raft(size, operations_per_test)
            self.results['raft']['latency'].append(raft_results['avg_latency'])
            self.results['raft']['throughput'].append(raft_results['throughput'])
            self.results['raft']['success_rate'] += raft_results['success_rate']
            self.results['raft']['partition_tolerance'] += raft_results['partition_tolerance']
            self.results['raft']['leader_elections'] += raft_results['leader_elections']
            
            # Benchmark Paxos
            paxos_results = self.benchmark_paxos(size, operations_per_test)
            self.results['paxos']['latency'].append(paxos_results['avg_latency'])
            self.results['paxos']['throughput'].append(paxos_results['throughput'])
            self.results['paxos']['success_rate'] += paxos_results['success_rate']
            self.results['paxos']['partition_tolerance'] += paxos_results['partition_tolerance']
            self.results['paxos']['proposals'] += paxos_results['proposals']
            
            print(f"   Raft - Latency: {raft_results['avg_latency']:.1f}ms, "
                  f"Throughput: {raft_results['throughput']:.1f} ops/s, "
                  f"Success: {raft_results['success_rate']:.1%}")
            print(f"   Paxos - Latency: {paxos_results['avg_latency']:.1f}ms, "
                  f"Throughput: {paxos_results['throughput']:.1f} ops/s, "
                  f"Success: {paxos_results['success_rate']:.1%}")
            print()
        
        # Average results
        num_tests = len(cluster_sizes)
        self.results['raft']['success_rate'] /= num_tests
        self.results['raft']['partition_tolerance'] /= num_tests
        self.results['paxos']['success_rate'] /= num_tests
        self.results['paxos']['partition_tolerance'] /= num_tests
        
        self.print_comparison_summary()
    
    def print_comparison_summary(self):
        """Print detailed comparison summary"""
        print("📈 Comprehensive Comparison Summary:")
        print("=" * 60)
        
        # Performance metrics
        raft_avg_latency = statistics.mean(self.results['raft']['latency'])
        paxos_avg_latency = statistics.mean(self.results['paxos']['latency'])
        raft_avg_throughput = statistics.mean(self.results['raft']['throughput'])
        paxos_avg_throughput = statistics.mean(self.results['paxos']['throughput'])
        
        print(f"⚡ Performance Metrics:")
        print(f"   Raft Average Latency:    {raft_avg_latency:.1f}ms")
        print(f"   Paxos Average Latency:   {paxos_avg_latency:.1f}ms")
        print(f"   Raft Average Throughput: {raft_avg_throughput:.1f} ops/s")
        print(f"   Paxos Average Throughput: {paxos_avg_throughput:.1f} ops/s")
        
        # Reliability metrics
        print(f"\n🛡️  Reliability Metrics:")
        print(f"   Raft Success Rate:       {self.results['raft']['success_rate']:.1%}")
        print(f"   Paxos Success Rate:      {self.results['paxos']['success_rate']:.1%}")
        print(f"   Raft Partition Tolerance: {self.results['raft']['partition_tolerance']:.1%}")
        print(f"   Paxos Partition Tolerance: {self.results['paxos']['partition_tolerance']:.1%}")
        
        # Algorithm characteristics
        print(f"\n🔍 Algorithm Characteristics:")
        print(f"   Raft Leader Elections:   {self.results['raft']['leader_elections']}")
        print(f"   Paxos Total Proposals:   {self.results['paxos']['proposals']}")
        
        # Comparison analysis
        print(f"\n📊 Analysis:")
        
        if raft_avg_latency < paxos_avg_latency:
            print(f"   🏃 Raft has {((paxos_avg_latency / raft_avg_latency - 1) * 100):.1f}% lower latency")
        else:
            print(f"   🏃 Paxos has {((raft_avg_latency / paxos_avg_latency - 1) * 100):.1f}% lower latency")
        
        if raft_avg_throughput > paxos_avg_throughput:
            print(f"   🚀 Raft has {((raft_avg_throughput / paxos_avg_throughput - 1) * 100):.1f}% higher throughput")
        else:
            print(f"   🚀 Paxos has {((paxos_avg_throughput / raft_avg_throughput - 1) * 100):.1f}% higher throughput")
        
        # Trade-offs summary
        print(f"\n⚖️  Trade-offs Summary:")
        print(f"   Raft Advantages:")
        print(f"     • Simpler to understand and implement")
        print(f"     • Strong leadership model reduces conflicts")
        print(f"     • Better performance in stable networks")
        print(f"     • Easier debugging and operational management")
        
        print(f"   Paxos Advantages:")
        print(f"     • No single point of failure (no leader)")
        print(f"     • Theoretical foundation for correctness")
        print(f"     • Better handling of network asymmetry")
        print(f"     • More flexible for various consensus scenarios")
        
        print(f"\n🎯 Use Case Recommendations:")
        print(f"   Choose Raft for:")
        print(f"     • Systems requiring operational simplicity")
        print(f"     • Applications with stable network conditions")
        print(f"     • Teams prioritizing implementation speed")
        
        print(f"   Choose Paxos for:")
        print(f"     • Systems requiring maximum theoretical guarantees")
        print(f"     • Networks with asymmetric partitions")
        print(f"     • Research or academic implementations")

def demonstrate_comparison():
    """Demonstrate consensus algorithm comparison"""
    comparison = ConsensusComparison()
    comparison.run_comparison()

if __name__ == "__main__":
    demonstrate_comparison()
