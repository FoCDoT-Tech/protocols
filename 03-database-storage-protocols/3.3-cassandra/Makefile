# Cassandra Query Protocol Subchapter Makefile
# Demonstrates Cassandra CQL protocol, consistency levels, and cluster operations

.PHONY: all test clean protocol operations diagrams dependencies

# Check dependencies (TCP must exist)
dependencies:
	@echo "🔍 Checking Cassandra dependencies..."
	@if [ ! -f "../../01-core-internet-networking/1.3-tcp/Makefile" ]; then \
		echo "❌ TCP dependency missing"; exit 1; \
	fi
	@echo "✅ Dependencies satisfied: TCP"

# Run Cassandra CQL protocol simulation
protocol:
	@echo "🔷 Running Cassandra CQL protocol simulation..."
	@python3 cassandra_protocol.py

# Run Cassandra operations demonstration
operations:
	@echo "📊 Running Cassandra operations demonstration..."
	@python3 cassandra_operations.py

# Generate Cassandra protocol diagrams
diagrams:
	@echo "🎨 Generating Cassandra protocol diagrams..."
	@python3 render_diagram.py

# Run all Cassandra demonstrations
all: dependencies protocol operations diagrams
	@echo ""
	@echo "=== Cassandra Query Protocol Subchapter Complete ==="
	@echo "✅ CQL protocol operations demonstrated"
	@echo "✅ Consistency levels and cluster operations shown"
	@echo "✅ Visual diagrams generated"
	@echo "🔷 Cassandra enables massive scale distributed database operations"

# Test all components
test: all
	@echo "🧪 Testing Cassandra components..."
	@python3 -c "\
import sys; \
sys.path.append('.'); \
from cassandra_protocol import CQLProtocol, CQLConsistency; \
from cassandra_operations import CassandraCluster, ConsistencyLevel, ReplicationStrategy; \
cql_protocol = CQLProtocol(); \
results = cql_protocol.demonstrate_cql_operations(); \
assert 'startup' in results, 'Startup should be in results'; \
assert 'query' in results, 'Query should be in results'; \
cluster = CassandraCluster('test-cluster'); \
replication = ReplicationStrategy('NetworkTopologyStrategy', {'us-east': 3, 'us-west': 2}); \
cluster.create_keyspace('test_ks', replication); \
read_result = cluster.simulate_read_operation('test_key', 'test_ks', ConsistencyLevel.QUORUM); \
assert 'latency_ms' in read_result, 'Read result should contain latency'; \
write_result = cluster.simulate_write_operation('test_key', 'test_ks', ConsistencyLevel.LOCAL_QUORUM); \
assert 'latency_ms' in write_result, 'Write result should contain latency'; \
print('✅ All Cassandra tests passed')"
	@echo "✅ Cassandra CQL protocol tests completed successfully"

# Clean generated files
clean:
	@echo "🧹 Cleaning Cassandra generated files..."
	@rm -f *.png
	@echo "✅ Cleanup complete"
