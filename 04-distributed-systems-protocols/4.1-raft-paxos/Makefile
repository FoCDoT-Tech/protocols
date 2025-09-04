.PHONY: all clean test raft paxos comparison diagrams deps

# Raft & Paxos Consensus Protocols Subchapter
# Dependencies: TCP (1.3)

all: deps raft paxos comparison diagrams test

deps:
	@echo "🔍 Checking dependencies for Raft & Paxos Consensus..."
	@if [ ! -f "../../01-core-internet-networking/1.3-tcp/tcp_handshake.py" ]; then \
		echo "❌ Missing dependency: TCP (1.3) - run 'make' in 01-core-internet-networking/1.3-tcp first"; \
		exit 1; \
	fi
	@echo "✅ All dependencies satisfied"

raft:
	@echo "🗳️ Running Raft consensus simulation..."
	@python3 raft_consensus.py

paxos:
	@echo "🏛️ Running Paxos consensus simulation..."
	@python3 paxos_consensus.py

comparison:
	@echo "⚖️ Running Raft vs Paxos comparison..."
	@python3 consensus_comparison.py

diagrams:
	@echo "🎨 Generating consensus algorithm diagrams..."
	@python3 render_diagram.py
	@if command -v mmdc >/dev/null 2>&1; then \
		echo "📊 Rendering Mermaid diagram..."; \
		mmdc -i consensus_protocols.mmd -o consensus_protocols_mermaid.png; \
	else \
		echo "⚠️  Mermaid CLI not found, skipping .mmd rendering"; \
	fi

test:
	@echo "🧪 Testing Raft & Paxos consensus implementations..."
	@python3 -c "\
import raft_consensus as raft; \
import paxos_consensus as paxos; \
from raft_consensus import RaftCluster, NodeState; \
from paxos_consensus import PaxosCluster, Proposal; \
cluster = raft.RaftCluster(3); \
assert len(cluster.nodes) == 3; \
assert all(node.state == NodeState.FOLLOWER for node in cluster.nodes.values()); \
print('✅ Raft: cluster initialization tests passed'); \
paxos_cluster = paxos.PaxosCluster(3); \
assert len(paxos_cluster.nodes) == 3; \
assert all(node.active for node in paxos_cluster.nodes.values()); \
print('✅ Paxos: cluster initialization tests passed'); \
proposal = Proposal(1, 'test_value'); \
assert proposal.proposal_id == 1; \
assert proposal.value == 'test_value'; \
print('✅ Paxos: proposal structure tests passed'); \
print('🎯 All Raft & Paxos consensus tests passed!')"

clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f *.png
	@rm -rf __pycache__/
	@echo "✅ Cleanup completed"

summary:
	@echo ""
	@echo "=== Raft & Paxos Consensus Summary ==="
	@echo "📋 Protocols: Distributed consensus algorithms"
	@echo "🎯 Purpose: Enable agreement in distributed systems despite failures"
	@echo "🔧 Features: Leader election, log replication, fault tolerance"
	@echo "⚡ Performance: Majority consensus, partition tolerance"
	@echo "🌐 Use Cases: Distributed databases, configuration management, coordination"
	@echo ""
