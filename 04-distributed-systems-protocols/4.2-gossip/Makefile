.PHONY: all clean test gossip membership anti-entropy diagrams deps

# Gossip Protocols Subchapter
# Dependencies: UDP (1.4)

all: deps gossip membership anti-entropy diagrams test

deps:
	@echo "🔍 Checking dependencies for Gossip Protocols..."
	@if [ ! -f "../../01-core-internet-networking/1.4-udp/udp_client_server.py" ]; then \
		echo "❌ Missing dependency: UDP (1.4) - run 'make' in 01-core-internet-networking/1.4-udp first"; \
		exit 1; \
	fi
	@echo "✅ All dependencies satisfied"

gossip:
	@echo "📡 Running gossip protocol simulation..."
	@python3 gossip_protocol.py

membership:
	@echo "🤝 Running membership manager demonstration..."
	@python3 membership_manager.py

anti-entropy:
	@echo "🔄 Running anti-entropy mechanisms..."
	@python3 anti_entropy.py

diagrams:
	@echo "🎨 Generating gossip protocol diagrams..."
	@python3 render_diagram.py
	@if command -v mmdc >/dev/null 2>&1; then \
		echo "📊 Rendering Mermaid diagram..."; \
		mmdc -i gossip_protocols.mmd -o gossip_protocols_mermaid.png; \
	else \
		echo "⚠️  Mermaid CLI not found, skipping .mmd rendering"; \
	fi

test:
	@echo "🧪 Testing gossip protocol implementations..."
	@python3 -c "\
import gossip_protocol as gp; \
import membership_manager as mm; \
import anti_entropy as ae; \
from gossip_protocol import GossipNode, NodeState; \
from membership_manager import MembershipManager, Member; \
from anti_entropy import AntiEntropyManager, StateEntry; \
node = gp.GossipNode('test_node', '127.0.0.1', 9000); \
assert node.node_id == 'test_node'; \
assert node.address == '127.0.0.1'; \
assert node.port == 9000; \
assert len(node.members) == 1; \
print('✅ Gossip: node initialization tests passed'); \
manager = mm.MembershipManager('test_member', '192.168.1.1'); \
assert manager.local_member_id == 'test_member'; \
assert manager.local_address == '192.168.1.1'; \
assert len(manager.members) == 1; \
print('✅ Membership: manager initialization tests passed'); \
entropy = ae.AntiEntropyManager('test_entropy'); \
assert entropy.node_id == 'test_entropy'; \
entropy.put('test_key', 'test_value'); \
assert entropy.get('test_key') == 'test_value'; \
print('✅ Anti-entropy: state management tests passed'); \
print('🎯 All gossip protocol tests passed!')"

clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f *.png
	@rm -rf __pycache__/
	@echo "✅ Cleanup completed"

summary:
	@echo ""
	@echo "=== Gossip Protocols Summary ==="
	@echo "📋 Protocols: Epidemic information dissemination"
	@echo "🎯 Purpose: Decentralized membership and state management"
	@echo "🔧 Features: SWIM failure detection, anti-entropy, eventual consistency"
	@echo "⚡ Performance: O(log N) convergence, partition tolerance"
	@echo "🌐 Use Cases: Service discovery, cluster membership, distributed caching"
	@echo ""
