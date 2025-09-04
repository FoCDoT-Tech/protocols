# MongoDB Wire Protocol Subchapter Makefile
# Demonstrates MongoDB wire protocol, operations, and cluster management

.PHONY: all test clean protocol operations diagrams dependencies

# Check dependencies (TCP must exist)
dependencies:
	@echo "🔍 Checking MongoDB dependencies..."
	@if [ ! -f "../../01-core-internet-networking/1.3-tcp/Makefile" ]; then \
		echo "❌ TCP dependency missing"; exit 1; \
	fi
	@echo "✅ Dependencies satisfied: TCP"

# Run MongoDB wire protocol simulation
protocol:
	@echo "🍃 Running MongoDB wire protocol simulation..."
	@python3 mongodb_wire_protocol.py

# Run MongoDB operations demonstration
operations:
	@echo "📊 Running MongoDB operations demonstration..."
	@python3 mongodb_operations.py

# Generate MongoDB protocol diagrams
diagrams:
	@echo "🎨 Generating MongoDB protocol diagrams..."
	@python3 render_diagram.py

# Run all MongoDB demonstrations
all: dependencies protocol operations diagrams
	@echo ""
	@echo "=== MongoDB Wire Protocol Subchapter Complete ==="
	@echo "✅ Wire protocol operations demonstrated"
	@echo "✅ Advanced operations and clustering shown"
	@echo "✅ Visual diagrams generated"
	@echo "🍃 MongoDB enables scalable document database operations"

# Test all components
test: all
	@echo "🧪 Testing MongoDB components..."
	@python3 -c "\
import sys; \
sys.path.append('.'); \
from mongodb_wire_protocol import MongoWireProtocol; \
from mongodb_operations import MongoAggregationPipeline, MongoReplicaSet, MongoShardedCluster; \
mongo_protocol = MongoWireProtocol(); \
results = mongo_protocol.demonstrate_operations(); \
assert 'authentication' in results, 'Authentication should be in results'; \
assert 'query' in results, 'Query should be in results'; \
pipeline = MongoAggregationPipeline(); \
pipeline_result = pipeline.match({'status': 'active'}).group({'_id': '$$category', 'count': {'$$sum': 1}}).execute('products'); \
assert 'results' in pipeline_result, 'Pipeline should return results'; \
replica_set = MongoReplicaSet('rs0', ['mongo1:27017', 'mongo2:27017', 'mongo3:27017']); \
cluster = MongoShardedCluster('test-cluster'); \
print('✅ All MongoDB tests passed')"
	@echo "✅ MongoDB wire protocol tests completed successfully"

# Clean generated files
clean:
	@echo "🧹 Cleaning MongoDB generated files..."
	@rm -f *.png
	@echo "✅ Cleanup complete"
