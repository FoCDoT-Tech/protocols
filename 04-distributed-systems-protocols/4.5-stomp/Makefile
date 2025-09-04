.PHONY: all clean test broker client chat diagrams deps

# STOMP (Simple Text Oriented Messaging Protocol) Subchapter
# Dependencies: TCP (1.3)

all: deps broker client chat diagrams test

deps:
	@echo "🔍 Checking dependencies for STOMP..."
	@if [ ! -f "../../01-core-internet-networking/1.3-tcp/tcp_client_server.py" ]; then \
		echo "❌ Missing dependency: TCP (1.3) - run 'make' in 01-core-internet-networking/1.3-tcp first"; \
		exit 1; \
	fi
	@echo "✅ All dependencies satisfied"

broker:
	@echo "🏭 Running STOMP broker simulation..."
	@python3 stomp_broker.py

client:
	@echo "📱 Running STOMP client demonstration..."
	@python3 stomp_client.py

chat:
	@echo "💬 Running STOMP chat application..."
	@timeout 30s python3 chat_application.py || true

diagrams:
	@echo "🎨 Generating STOMP diagrams..."
	@python3 render_diagram.py
	@if command -v mmdc >/dev/null 2>&1; then \
		echo "📊 Rendering Mermaid diagram..."; \
		mmdc -i stomp_architecture.mmd -o stomp_architecture_mermaid.png; \
	else \
		echo "⚠️  Mermaid CLI not found, skipping .mmd rendering"; \
	fi

test:
	@echo "🧪 Testing STOMP implementations..."
	@python3 -c "\
import stomp_broker as sb; \
import stomp_client as sc; \
import chat_application as ca; \
from stomp_broker import StompBroker, StompFrame, StompCommand; \
from stomp_client import StompClient, StompClientConfig; \
broker = sb.StompBroker(); \
assert broker.host == 'localhost'; \
assert broker.port == 61613; \
assert len(broker.clients) == 0; \
print('✅ STOMP Broker: initialization tests passed'); \
config = sc.StompClientConfig(); \
client = sc.StompClient(config); \
assert config.broker_host == 'localhost'; \
assert config.broker_port == 61613; \
assert not client.is_connected(); \
print('✅ STOMP Client: connection tests passed'); \
frame = sb.StompFrame(StompCommand.CONNECT, {'accept-version': '1.2'}); \
assert frame.command == StompCommand.CONNECT; \
assert frame.headers['accept-version'] == '1.2'; \
print('✅ STOMP Frame: frame tests passed'); \
chat_app = ca.ChatApplication(broker); \
assert len(chat_app.rooms) == 3; \
assert 'general' in chat_app.rooms; \
print('✅ Chat Application: initialization tests passed'); \
print('🎯 All STOMP tests passed!')"

clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f *.png
	@rm -rf __pycache__/
	@echo "✅ Cleanup completed"

summary:
	@echo ""
	@echo "=== STOMP Summary ==="
	@echo "📋 Protocol: Simple Text Oriented Messaging Protocol"
	@echo "🎯 Purpose: Simple, text-based messaging for cross-language integration"
	@echo "🔧 Features: Frame-based protocol, transactions, acknowledgments"
	@echo "⚡ Benefits: Human-readable, WebSocket compatible, easy debugging"
	@echo "🌐 Use Cases: Web applications, real-time chat, enterprise integration"
	@echo ""
