#!/usr/bin/env python3
"""
SQL Connection Pool Implementation
Demonstrates connection pooling patterns for database wire protocols
"""

import time
import threading
import queue
import secrets
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional
import contextlib

@dataclass
class DatabaseConnection:
    id: int
    protocol: str
    created_at: datetime
    last_used: datetime
    query_count: int
    is_valid: bool
    in_use: bool = False
    
    def execute_query(self, query: str) -> Dict:
        """Simulate query execution"""
        self.last_used = datetime.now()
        self.query_count += 1
        
        # Simulate query execution time
        execution_time = secrets.randbelow(50) + 5
        time.sleep(execution_time / 1000)  # Convert to seconds
        
        return {
            'query': query,
            'execution_time_ms': execution_time,
            'rows_affected': secrets.randbelow(100),
            'connection_id': self.id
        }
    
    def validate(self) -> bool:
        """Validate connection with ping query"""
        try:
            # Simulate validation query (SELECT 1)
            time.sleep(0.001)  # 1ms validation time
            self.is_valid = secrets.choice([True, True, True, False])  # 75% success
            return self.is_valid
        except:
            self.is_valid = False
            return False

class ConnectionPool:
    def __init__(self, protocol: str, min_size: int = 5, max_size: int = 20):
        self.protocol = protocol
        self.min_size = min_size
        self.max_size = max_size
        self.connections: queue.Queue = queue.Queue()
        self.active_connections: Dict[int, DatabaseConnection] = {}
        self.connection_counter = 0
        self.lock = threading.Lock()
        
        self.metrics = {
            'total_created': 0,
            'total_destroyed': 0,
            'current_active': 0,
            'current_idle': 0,
            'pool_hits': 0,
            'pool_misses': 0,
            'validation_failures': 0
        }
        
        # Initialize minimum connections
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize pool with minimum connections"""
        print(f"🔄 Initializing {self.protocol} connection pool...")
        
        for _ in range(self.min_size):
            conn = self._create_connection()
            self.connections.put(conn)
            self.metrics['current_idle'] += 1
        
        print(f"✅ Pool initialized with {self.min_size} connections")
    
    def _create_connection(self) -> DatabaseConnection:
        """Create a new database connection"""
        with self.lock:
            self.connection_counter += 1
            conn = DatabaseConnection(
                id=self.connection_counter,
                protocol=self.protocol,
                created_at=datetime.now(),
                last_used=datetime.now(),
                query_count=0,
                is_valid=True
            )
            self.metrics['total_created'] += 1
            return conn
    
    def get_connection(self, timeout: float = 5.0) -> Optional[DatabaseConnection]:
        """Get connection from pool"""
        try:
            # Try to get existing connection
            conn = self.connections.get(timeout=timeout)
            
            # Validate connection
            if not conn.validate():
                self.metrics['validation_failures'] += 1
                # Create new connection if validation fails
                conn = self._create_connection()
                self.metrics['pool_misses'] += 1
            else:
                self.metrics['pool_hits'] += 1
            
            # Mark as active
            conn.in_use = True
            with self.lock:
                self.active_connections[conn.id] = conn
                self.metrics['current_active'] += 1
                self.metrics['current_idle'] = max(0, self.metrics['current_idle'] - 1)
            
            return conn
            
        except queue.Empty:
            # Pool exhausted, try to create new connection if under max
            if len(self.active_connections) < self.max_size:
                conn = self._create_connection()
                conn.in_use = True
                with self.lock:
                    self.active_connections[conn.id] = conn
                    self.metrics['current_active'] += 1
                self.metrics['pool_misses'] += 1
                return conn
            else:
                print(f"⚠️ Connection pool exhausted (max: {self.max_size})")
                return None
    
    def return_connection(self, conn: DatabaseConnection):
        """Return connection to pool"""
        if not conn or conn.id not in self.active_connections:
            return
        
        conn.in_use = False
        
        with self.lock:
            del self.active_connections[conn.id]
            self.metrics['current_active'] -= 1
            self.metrics['current_idle'] += 1
        
        # Return to pool if still valid
        if conn.validate():
            self.connections.put(conn)
        else:
            self.metrics['validation_failures'] += 1
            self.metrics['total_destroyed'] += 1
            self.metrics['current_idle'] -= 1
    
    @contextlib.contextmanager
    def connection(self):
        """Context manager for connection handling"""
        conn = self.get_connection()
        if not conn:
            raise Exception("Unable to acquire connection from pool")
        
        try:
            yield conn
        finally:
            self.return_connection(conn)
    
    def cleanup_idle_connections(self, max_idle_time: int = 300):
        """Clean up idle connections older than max_idle_time seconds"""
        cleaned = 0
        current_time = datetime.now()
        
        # Check connections in pool
        temp_connections = []
        
        while not self.connections.empty():
            try:
                conn = self.connections.get_nowait()
                if (current_time - conn.last_used).seconds > max_idle_time:
                    cleaned += 1
                    self.metrics['total_destroyed'] += 1
                    self.metrics['current_idle'] -= 1
                else:
                    temp_connections.append(conn)
            except queue.Empty:
                break
        
        # Return valid connections to pool
        for conn in temp_connections:
            self.connections.put(conn)
        
        return cleaned
    
    def get_pool_stats(self) -> Dict:
        """Get current pool statistics"""
        return {
            'protocol': self.protocol,
            'pool_size': f"{self.metrics['current_idle']} idle + {self.metrics['current_active']} active",
            'total_connections': self.metrics['current_idle'] + self.metrics['current_active'],
            'pool_efficiency': f"{(self.metrics['pool_hits'] / max(1, self.metrics['pool_hits'] + self.metrics['pool_misses']) * 100):.1f}%",
            'validation_failures': self.metrics['validation_failures'],
            'connections_created': self.metrics['total_created'],
            'connections_destroyed': self.metrics['total_destroyed']
        }

class DatabaseLoadTester:
    def __init__(self, pool: ConnectionPool):
        self.pool = pool
        self.results = []
        self.lock = threading.Lock()
    
    def simulate_load(self, num_requests: int = 50, concurrent_threads: int = 10):
        """Simulate database load with concurrent requests"""
        print(f"\n📈 Load Testing: {num_requests} requests with {concurrent_threads} threads")
        
        def worker():
            for _ in range(num_requests // concurrent_threads):
                start_time = time.time()
                
                try:
                    with self.pool.connection() as conn:
                        # Simulate different query types
                        queries = [
                            "SELECT * FROM users WHERE id = 123",
                            "UPDATE orders SET status = 'shipped' WHERE id = 456",
                            "INSERT INTO logs (message, timestamp) VALUES ('test', NOW())",
                            "SELECT COUNT(*) FROM products WHERE category = 'electronics'"
                        ]
                        
                        query = secrets.choice(queries)
                        result = conn.execute_query(query)
                        
                        end_time = time.time()
                        
                        with self.lock:
                            self.results.append({
                                'success': True,
                                'response_time': (end_time - start_time) * 1000,
                                'connection_id': result['connection_id'],
                                'query_time': result['execution_time_ms']
                            })
                
                except Exception as e:
                    end_time = time.time()
                    with self.lock:
                        self.results.append({
                            'success': False,
                            'response_time': (end_time - start_time) * 1000,
                            'error': str(e)
                        })
                
                # Small delay between requests
                time.sleep(0.01)
        
        # Start worker threads
        threads = []
        start_time = time.time()
        
        for _ in range(concurrent_threads):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Analyze results
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]
        
        if successful_requests:
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
            avg_query_time = sum(r['query_time'] for r in successful_requests) / len(successful_requests)
        else:
            avg_response_time = 0
            avg_query_time = 0
        
        print(f"\n📊 Load Test Results:")
        print(f"   Total Requests: {len(self.results)}")
        print(f"   Successful: {len(successful_requests)}")
        print(f"   Failed: {len(failed_requests)}")
        print(f"   Success Rate: {(len(successful_requests) / len(self.results) * 100):.1f}%")
        print(f"   Average Response Time: {avg_response_time:.2f}ms")
        print(f"   Average Query Time: {avg_query_time:.2f}ms")
        print(f"   Total Duration: {(end_time - start_time):.2f}s")
        print(f"   Throughput: {len(self.results) / (end_time - start_time):.1f} req/s")
        
        return {
            'total_requests': len(self.results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(self.results) * 100,
            'avg_response_time': avg_response_time,
            'throughput': len(self.results) / (end_time - start_time)
        }

def demonstrate_connection_pooling():
    """Demonstrate connection pooling across different database protocols"""
    protocols = ['mysql', 'postgresql', 'sqlserver']
    
    for protocol in protocols:
        print(f"\n{'='*60}")
        print(f"🗄️ {protocol.upper()} Connection Pool Demo")
        print(f"{'='*60}")
        
        # Create connection pool
        pool = ConnectionPool(protocol, min_size=3, max_size=10)
        
        # Basic connection usage
        print(f"\n🔧 Basic Connection Usage:")
        with pool.connection() as conn:
            result = conn.execute_query("SELECT * FROM users LIMIT 10")
            print(f"   Query executed on connection {result['connection_id']}")
            print(f"   Execution time: {result['execution_time_ms']}ms")
            print(f"   Rows affected: {result['rows_affected']}")
        
        # Multiple concurrent connections
        print(f"\n🔄 Concurrent Connection Usage:")
        
        def use_connection(conn_num):
            with pool.connection() as conn:
                query = f"SELECT * FROM table_{conn_num} WHERE active = 1"
                result = conn.execute_query(query)
                print(f"   Thread {conn_num}: Connection {result['connection_id']} - {result['execution_time_ms']}ms")
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=use_connection, args=(i,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        # Load testing
        load_tester = DatabaseLoadTester(pool)
        load_results = load_tester.simulate_load(num_requests=30, concurrent_threads=5)
        
        # Pool statistics
        print(f"\n📊 Pool Statistics:")
        stats = pool.get_pool_stats()
        for key, value in stats.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        # Cleanup test
        print(f"\n🧹 Cleanup Test:")
        cleaned = pool.cleanup_idle_connections(max_idle_time=1)
        print(f"   Cleaned up {cleaned} idle connections")
        
        time.sleep(0.5)

if __name__ == "__main__":
    demonstrate_connection_pooling()
    
    print(f"\n🎯 Connection pooling enables efficient database resource management")
    print(f"💡 Key benefits: reduced connection overhead, improved scalability")
    print(f"🚀 Production patterns: validation, cleanup, monitoring, load balancing")
