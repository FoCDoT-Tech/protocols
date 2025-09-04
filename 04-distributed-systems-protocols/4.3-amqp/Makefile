.PHONY: all clean test broker client patterns diagrams deps

# AMQP (Advanced Message Queuing Protocol) Subchapter
# Dependencies: TCP (1.3)

all: deps broker client patterns diagrams test

deps:
	@echo "🔍 Checking dependencies for AMQP..."
	@if [ ! -f "../../01-core-internet-networking/1.3-tcp/tcp_client_server.py" ]; then \
		echo "❌ Missing dependency: TCP (1.3) - run 'make' in 01-core-internet-networking/1.3-tcp first"; \
		exit 1; \
	fi
	@echo "✅ All dependencies satisfied"

broker:
	@echo "🏭 Running AMQP broker simulation..."
	@python3 amqp_broker.py

client:
	@echo "📱 Running AMQP client demonstration..."
	@python3 amqp_client.py

patterns:
	@echo "🎯 Running AMQP messaging patterns..."
	@python3 message_patterns.py

diagrams:
	@echo "🎨 Generating AMQP diagrams..."
	@python3 render_diagram.py
	@if command -v mmdc >/dev/null 2>&1; then \
		echo "📊 Rendering Mermaid diagram..."; \
		mmdc -i amqp_architecture.mmd -o amqp_architecture_mermaid.png; \
	else \
		echo "⚠️  Mermaid CLI not found, skipping .mmd rendering"; \
	fi

test:
	@echo "🧪 Testing AMQP implementations..."
	@python3 -c "\
import amqp_broker as ab; \
import amqp_client as ac; \
import message_patterns as mp; \
from amqp_broker import AMQPBroker, Message, ExchangeType; \
from amqp_client import AMQPConnection, ConnectionParams; \
broker = ab.AMQPBroker(); \
assert len(broker.exchanges) == 5; \
assert '' in broker.exchanges; \
assert 'amq.direct' in broker.exchanges; \
print('✅ AMQP Broker: initialization tests passed'); \
params = ac.ConnectionParams(); \
conn = ac.AMQPConnection(params); \
assert params.host == 'localhost'; \
assert params.port == 5672; \
assert not conn.is_open(); \
print('✅ AMQP Client: connection tests passed'); \
msg = ab.Message('test body', 'test.key'); \
assert msg.body == 'test body'; \
assert msg.routing_key == 'test.key'; \
assert not msg.is_expired(); \
print('✅ AMQP Message: message tests passed'); \
print('🎯 All AMQP tests passed!')"

clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f *.png
	@rm -rf __pycache__/
	@echo "✅ Cleanup completed"

summary:
	@echo ""
	@echo "=== AMQP Summary ==="
	@echo "📋 Protocol: Advanced Message Queuing Protocol"
	@echo "🎯 Purpose: Reliable, interoperable message-oriented middleware"
	@echo "🔧 Features: Multiple exchange types, delivery guarantees, QoS"
	@echo "⚡ Patterns: Work queues, pub-sub, routing, topics, RPC"
	@echo "🌐 Use Cases: Financial systems, e-commerce, telecommunications"
	@echo ""
