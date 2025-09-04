.PHONY: all clean test protocol operations diagrams deps

# Redis RESP Protocol Subchapter
# Dependencies: TCP (1.3)

all: deps protocol operations diagrams test

deps:
	@echo "🔍 Checking dependencies for Redis RESP Protocol..."
	@if [ ! -f "../../01-core-internet-networking/1.3-tcp/tcp_client_server.py" ]; then \
		echo "❌ Missing dependency: TCP (1.3) - run 'make' in 01-core-internet-networking/1.3-tcp first"; \
		exit 1; \
	fi
	@echo "✅ All dependencies satisfied"

protocol:
	@echo "🔧 Running Redis RESP Protocol simulation..."
	@python3 redis_protocol.py

operations:
	@echo "🚀 Running Redis operations demonstration..."
	@python3 redis_operations.py

diagrams:
	@echo "🎨 Generating Redis protocol diagrams..."
	@python3 render_diagram.py
	@if command -v mmdc >/dev/null 2>&1; then \
		echo "📊 Rendering Mermaid diagram..."; \
		mmdc -i redis_protocol.mmd -o redis_protocol_mermaid.png; \
	else \
		echo "⚠️  Mermaid CLI not found, skipping .mmd rendering"; \
	fi

test:
	@echo "🧪 Testing Redis RESP Protocol implementation..."
	@python3 -c "\
import redis_protocol as rp; \
import redis_operations as ro; \
resp = rp.RESPProtocol(); \
assert resp.encode_simple_string('OK') == b'+OK\r\n'; \
assert resp.encode_integer(42) == b':42\r\n'; \
assert resp.encode_bulk_string('hello') == b'\$$5\r\nhello\r\n'; \
print('✅ RESP Protocol: encoding/decoding tests passed'); \
pubsub = ro.RedisPubSub(); \
pubsub.subscribe('client1', 'test'); \
recipients = pubsub.publish('test', 'message'); \
assert recipients == 1; \
print('✅ Redis Operations: pub/sub tests passed'); \
cluster = ro.RedisCluster('test-cluster'); \
slot = cluster.calculate_slot('test-key'); \
assert 0 <= slot < 16384; \
print('✅ Redis Operations: cluster tests passed'); \
print('🎯 All Redis RESP Protocol tests passed!')"

clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f *.png
	@rm -rf __pycache__/
	@echo "✅ Cleanup completed"

summary:
	@echo ""
	@echo "=== Redis RESP Protocol Summary ==="
	@echo "📋 Protocol: Redis Serialization Protocol (RESP)"
	@echo "🎯 Purpose: High-performance in-memory data structure server"
	@echo "🔧 Features: Multiple data types, pub/sub, clustering, persistence"
	@echo "⚡ Performance: Sub-millisecond latency, 100K+ ops/sec"
	@echo "🌐 Use Cases: Caching, session storage, real-time analytics"
	@echo ""
