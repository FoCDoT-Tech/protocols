#!/usr/bin/env python3
"""
File System Performance Monitor
Monitors NFS and SMB performance characteristics including
latency, throughput, cache hit ratios, and error rates.
"""

import random
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    timestamp: datetime
    operation: str
    latency_ms: float
    throughput_mbps: float
    success: bool
    error_code: Optional[str] = None

@dataclass
class FileSystemStats:
    """File system statistics"""
    protocol: str
    server: str
    mount_point: str
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    avg_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    total_throughput_mb: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    error_counts: Dict[str, int] = field(default_factory=dict)
    recent_metrics: deque = field(default_factory=lambda: deque(maxlen=100))

class FileSystemMonitor:
    """File system performance monitor"""
    
    def __init__(self):
        self.stats = {}
        self.monitoring = False
        self.monitor_thread = None
        self.alert_thresholds = {
            'max_latency_ms': 100.0,
            'error_rate_percent': 5.0,
            'min_throughput_mbps': 10.0
        }
        
        print("📊 File System Monitor initialized")
        print(f"   Alert Thresholds:")
        print(f"     Max Latency: {self.alert_thresholds['max_latency_ms']}ms")
        print(f"     Max Error Rate: {self.alert_thresholds['error_rate_percent']}%")
        print(f"     Min Throughput: {self.alert_thresholds['min_throughput_mbps']} MB/s")
    
    def add_file_system(self, protocol: str, server: str, mount_point: str):
        """Add file system to monitor"""
        fs_key = f"{protocol}://{server}{mount_point}"
        self.stats[fs_key] = FileSystemStats(
            protocol=protocol,
            server=server,
            mount_point=mount_point
        )
        
        print(f"📁 Added file system: {fs_key}")
    
    def record_operation(self, protocol: str, server: str, mount_point: str,
                        operation: str, latency_ms: float, throughput_mbps: float,
                        success: bool, error_code: Optional[str] = None):
        """Record a file system operation"""
        fs_key = f"{protocol}://{server}{mount_point}"
        
        if fs_key not in self.stats:
            self.add_file_system(protocol, server, mount_point)
        
        stats = self.stats[fs_key]
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            operation=operation,
            latency_ms=latency_ms,
            throughput_mbps=throughput_mbps,
            success=success,
            error_code=error_code
        )
        
        # Update statistics
        stats.total_operations += 1
        if success:
            stats.successful_operations += 1
        else:
            stats.failed_operations += 1
            if error_code:
                stats.error_counts[error_code] = stats.error_counts.get(error_code, 0) + 1
        
        # Update latency statistics
        if latency_ms > stats.max_latency_ms:
            stats.max_latency_ms = latency_ms
        if latency_ms < stats.min_latency_ms:
            stats.min_latency_ms = latency_ms
        
        # Calculate rolling average latency
        stats.recent_metrics.append(metric)
        recent_latencies = [m.latency_ms for m in stats.recent_metrics if m.success]
        if recent_latencies:
            stats.avg_latency_ms = sum(recent_latencies) / len(recent_latencies)
        
        # Update throughput
        stats.total_throughput_mb += throughput_mbps * (latency_ms / 1000)  # Approximate
        
        # Check for alerts
        self._check_alerts(fs_key, stats, metric)
    
    def _check_alerts(self, fs_key: str, stats: FileSystemStats, metric: PerformanceMetric):
        """Check for performance alerts"""
        alerts = []
        
        # High latency alert
        if metric.latency_ms > self.alert_thresholds['max_latency_ms']:
            alerts.append(f"HIGH LATENCY: {metric.latency_ms:.1f}ms (threshold: {self.alert_thresholds['max_latency_ms']}ms)")
        
        # Error rate alert
        if stats.total_operations > 10:  # Need enough samples
            error_rate = (stats.failed_operations / stats.total_operations) * 100
            if error_rate > self.alert_thresholds['error_rate_percent']:
                alerts.append(f"HIGH ERROR RATE: {error_rate:.1f}% (threshold: {self.alert_thresholds['error_rate_percent']}%)")
        
        # Low throughput alert
        if metric.throughput_mbps < self.alert_thresholds['min_throughput_mbps']:
            alerts.append(f"LOW THROUGHPUT: {metric.throughput_mbps:.1f} MB/s (threshold: {self.alert_thresholds['min_throughput_mbps']} MB/s)")
        
        # Print alerts
        for alert in alerts:
            print(f"🚨 ALERT [{fs_key}]: {alert}")
    
    def simulate_nfs_workload(self, server: str, mount_point: str, duration_seconds: int = 30):
        """Simulate NFS workload"""
        print(f"\n📊 Simulating NFS workload")
        print(f"   Server: {server}")
        print(f"   Mount: {mount_point}")
        print(f"   Duration: {duration_seconds}s")
        
        start_time = time.time()
        operation_count = 0
        
        while time.time() - start_time < duration_seconds:
            # Simulate different NFS operations
            operations = [
                ("GETATTR", 0.5, 2.0, 0.1, 0.5),  # operation, min_lat, max_lat, min_tput, max_tput
                ("READ", 1.0, 5.0, 50.0, 200.0),
                ("WRITE", 1.5, 8.0, 30.0, 150.0),
                ("LOOKUP", 0.3, 1.5, 0.1, 0.3),
                ("READDIR", 2.0, 10.0, 5.0, 20.0)
            ]
            
            op_name, min_lat, max_lat, min_tput, max_tput = random.choice(operations)
            
            # Simulate operation characteristics
            latency = random.uniform(min_lat, max_lat)
            throughput = random.uniform(min_tput, max_tput)
            
            # Simulate occasional failures
            success = random.random() > 0.02  # 2% failure rate
            error_code = None if success else random.choice(["ESTALE", "EIO", "ETIMEDOUT"])
            
            # Add some network congestion simulation
            if random.random() < 0.1:  # 10% chance of network congestion
                latency *= random.uniform(2.0, 5.0)
                throughput *= random.uniform(0.2, 0.5)
            
            self.record_operation("NFS", server, mount_point, op_name, 
                                latency, throughput, success, error_code)
            
            operation_count += 1
            time.sleep(random.uniform(0.1, 0.5))  # Simulate operation interval
        
        print(f"   Completed: {operation_count} operations")
    
    def simulate_smb_workload(self, server: str, share: str, duration_seconds: int = 30):
        """Simulate SMB workload"""
        print(f"\n📊 Simulating SMB workload")
        print(f"   Server: \\\\{server}\\{share}")
        print(f"   Duration: {duration_seconds}s")
        
        start_time = time.time()
        operation_count = 0
        
        while time.time() - start_time < duration_seconds:
            # Simulate different SMB operations
            operations = [
                ("CREATE", 0.8, 3.0, 0.1, 0.5),
                ("READ", 0.5, 4.0, 80.0, 300.0),
                ("WRITE", 1.0, 6.0, 60.0, 250.0),
                ("QUERY_DIRECTORY", 1.5, 8.0, 2.0, 10.0),
                ("CLOSE", 0.3, 1.0, 0.1, 0.2)
            ]
            
            op_name, min_lat, max_lat, min_tput, max_tput = random.choice(operations)
            
            # Simulate operation characteristics
            latency = random.uniform(min_lat, max_lat)
            throughput = random.uniform(min_tput, max_tput)
            
            # Simulate occasional failures
            success = random.random() > 0.015  # 1.5% failure rate
            error_code = None if success else random.choice(["ACCESS_DENIED", "SHARING_VIOLATION", "NETWORK_ERROR"])
            
            # SMB 3.0 multichannel simulation
            if random.random() < 0.3:  # 30% chance of multichannel boost
                throughput *= random.uniform(1.5, 2.5)
                latency *= random.uniform(0.7, 0.9)
            
            self.record_operation("SMB", server, f"\\{share}", op_name, 
                                latency, throughput, success, error_code)
            
            operation_count += 1
            time.sleep(random.uniform(0.05, 0.3))  # SMB typically faster than NFS
        
        print(f"   Completed: {operation_count} operations")
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'file_systems': {},
            'summary': {}
        }
        
        total_ops = 0
        total_errors = 0
        avg_latencies = []
        avg_throughputs = []
        
        for fs_key, stats in self.stats.items():
            if stats.total_operations == 0:
                continue
            
            error_rate = (stats.failed_operations / stats.total_operations) * 100
            cache_hit_rate = 0
            if stats.cache_hits + stats.cache_misses > 0:
                cache_hit_rate = (stats.cache_hits / (stats.cache_hits + stats.cache_misses)) * 100
            
            # Calculate recent throughput
            recent_throughput = 0
            if stats.recent_metrics:
                recent_throughput = sum(m.throughput_mbps for m in stats.recent_metrics) / len(stats.recent_metrics)
            
            fs_report = {
                'protocol': stats.protocol,
                'server': stats.server,
                'mount_point': stats.mount_point,
                'total_operations': stats.total_operations,
                'success_rate_percent': ((stats.successful_operations / stats.total_operations) * 100),
                'error_rate_percent': error_rate,
                'avg_latency_ms': stats.avg_latency_ms,
                'min_latency_ms': stats.min_latency_ms,
                'max_latency_ms': stats.max_latency_ms,
                'avg_throughput_mbps': recent_throughput,
                'cache_hit_rate_percent': cache_hit_rate,
                'top_errors': dict(sorted(stats.error_counts.items(), key=lambda x: x[1], reverse=True)[:5])
            }
            
            report['file_systems'][fs_key] = fs_report
            
            # Aggregate for summary
            total_ops += stats.total_operations
            total_errors += stats.failed_operations
            avg_latencies.append(stats.avg_latency_ms)
            avg_throughputs.append(recent_throughput)
        
        # Summary statistics
        if total_ops > 0:
            report['summary'] = {
                'total_operations': total_ops,
                'overall_error_rate_percent': (total_errors / total_ops) * 100,
                'avg_latency_ms': sum(avg_latencies) / len(avg_latencies) if avg_latencies else 0,
                'avg_throughput_mbps': sum(avg_throughputs) / len(avg_throughputs) if avg_throughputs else 0,
                'monitored_file_systems': len(self.stats)
            }
        
        return report
    
    def print_performance_report(self):
        """Print formatted performance report"""
        report = self.generate_performance_report()
        
        print(f"\n📊 File System Performance Report")
        print(f"   Generated: {report['timestamp']}")
        print(f"   File Systems: {report['summary'].get('monitored_file_systems', 0)}")
        
        if 'summary' in report:
            summary = report['summary']
            print(f"\n📈 Summary Statistics")
            print(f"   Total Operations: {summary['total_operations']:,}")
            print(f"   Overall Error Rate: {summary['overall_error_rate_percent']:.2f}%")
            print(f"   Average Latency: {summary['avg_latency_ms']:.2f}ms")
            print(f"   Average Throughput: {summary['avg_throughput_mbps']:.1f} MB/s")
        
        print(f"\n📁 File System Details")
        for fs_key, fs_stats in report['file_systems'].items():
            print(f"\n   {fs_key}")
            print(f"     Protocol: {fs_stats['protocol']}")
            print(f"     Operations: {fs_stats['total_operations']:,}")
            print(f"     Success Rate: {fs_stats['success_rate_percent']:.1f}%")
            print(f"     Avg Latency: {fs_stats['avg_latency_ms']:.2f}ms")
            print(f"     Latency Range: {fs_stats['min_latency_ms']:.2f}-{fs_stats['max_latency_ms']:.2f}ms")
            print(f"     Throughput: {fs_stats['avg_throughput_mbps']:.1f} MB/s")
            
            if fs_stats['top_errors']:
                print(f"     Top Errors:")
                for error, count in fs_stats['top_errors'].items():
                    print(f"       {error}: {count}")

def demonstrate_file_system_monitoring():
    """Demonstrate file system performance monitoring"""
    print("=== File System Performance Monitoring ===")
    
    # Initialize monitor
    monitor = FileSystemMonitor()
    
    # Add file systems to monitor
    monitor.add_file_system("NFS", "nfs-server.example.com", "/export/data")
    monitor.add_file_system("NFS", "nfs-server.example.com", "/export/home")
    monitor.add_file_system("SMB", "smb-server.example.com", "shared")
    monitor.add_file_system("SMB", "smb-server.example.com", "users")
    
    # Simulate concurrent workloads
    print(f"\n🚀 Starting concurrent workload simulation...")
    
    # Create threads for different workloads
    threads = []
    
    # NFS workloads
    nfs_thread1 = threading.Thread(
        target=monitor.simulate_nfs_workload,
        args=("nfs-server.example.com", "/export/data", 15)
    )
    nfs_thread2 = threading.Thread(
        target=monitor.simulate_nfs_workload,
        args=("nfs-server.example.com", "/export/home", 15)
    )
    
    # SMB workloads
    smb_thread1 = threading.Thread(
        target=monitor.simulate_smb_workload,
        args=("smb-server.example.com", "shared", 15)
    )
    smb_thread2 = threading.Thread(
        target=monitor.simulate_smb_workload,
        args=("smb-server.example.com", "users", 15)
    )
    
    threads = [nfs_thread1, nfs_thread2, smb_thread1, smb_thread2]
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    print(f"\n✅ Workload simulation completed")
    
    # Generate and print report
    monitor.print_performance_report()
    
    # Performance comparison
    print(f"\n⚖️ Protocol Comparison")
    nfs_stats = []
    smb_stats = []
    
    for fs_key, stats in monitor.stats.items():
        if stats.protocol == "NFS":
            nfs_stats.append(stats)
        elif stats.protocol == "SMB":
            smb_stats.append(stats)
    
    if nfs_stats and smb_stats:
        nfs_avg_latency = sum(s.avg_latency_ms for s in nfs_stats) / len(nfs_stats)
        smb_avg_latency = sum(s.avg_latency_ms for s in smb_stats) / len(smb_stats)
        
        nfs_total_ops = sum(s.total_operations for s in nfs_stats)
        smb_total_ops = sum(s.total_operations for s in smb_stats)
        
        nfs_error_rate = sum(s.failed_operations for s in nfs_stats) / nfs_total_ops * 100 if nfs_total_ops > 0 else 0
        smb_error_rate = sum(s.failed_operations for s in smb_stats) / smb_total_ops * 100 if smb_total_ops > 0 else 0
        
        print(f"   NFS vs SMB:")
        print(f"     Average Latency: {nfs_avg_latency:.2f}ms vs {smb_avg_latency:.2f}ms")
        print(f"     Total Operations: {nfs_total_ops:,} vs {smb_total_ops:,}")
        print(f"     Error Rate: {nfs_error_rate:.2f}% vs {smb_error_rate:.2f}%")

if __name__ == "__main__":
    demonstrate_file_system_monitoring()
    
    print(f"\n🎯 File system monitoring enables proactive performance management")
    print(f"💡 Key metrics: latency, throughput, error rates, cache efficiency")
    print(f"🚀 Production benefits: capacity planning, troubleshooting, optimization")
