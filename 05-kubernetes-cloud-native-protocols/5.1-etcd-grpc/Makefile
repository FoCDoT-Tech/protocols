.PHONY: all clean test cluster client integration diagrams deps

# etcd gRPC Subchapter
# Dependencies: gRPC (2.6), Raft (4.1)

all: deps cluster client integration diagrams test

deps:
	@echo "🔍 Checking dependencies for etcd gRPC..."
	@if [ ! -f "../../02-web-protocols/2.7-grpc/grpc_server.py" ]; then \
		echo "❌ Missing dependency: gRPC (2.7) - run 'make' in 02-web-protocols/2.7-grpc first"; \
		exit 1; \
	fi
	@if [ ! -f "../../04-distributed-systems-protocols/4.1-raft-paxos/raft_consensus.py" ]; then \
		echo "❌ Missing dependency: Raft (4.1) - run 'make' in 04-distributed-systems-protocols/4.1-raft-paxos first"; \
		exit 1; \
	fi
	@echo "✅ All dependencies satisfied"

cluster:
	@echo "🏭 Running etcd cluster simulation..."
	@python3 etcd_cluster.py

client:
	@echo "📡 Running etcd gRPC client demonstration..."
	@python3 grpc_client.py

integration:
	@echo "🔗 Running Kubernetes integration demonstration..."
	@python3 kubernetes_integration.py

diagrams:
	@echo "🎨 Generating etcd gRPC diagrams..."
	@python3 render_diagram.py
	@if command -v mmdc >/dev/null 2>&1; then \
		echo "📊 Rendering Mermaid diagram..."; \
		mmdc -i etcd_grpc.mmd -o etcd_grpc_mermaid.png; \
	else \
		echo "⚠️  Mermaid CLI not found, skipping .mmd rendering"; \
	fi

test:
	@echo "🧪 Testing etcd gRPC implementations..."
	@python3 -c "\
import etcd_cluster as ec; \
import grpc_client as gc; \
import kubernetes_integration as ki; \
from etcd_cluster import EtcdNode, EtcdCluster, NodeState; \
from grpc_client import EtcdGrpcClient, GrpcRequest, GrpcResponse; \
cluster = ec.EtcdCluster(3); \
assert len(cluster.nodes) == 3; \
assert all(node.state == NodeState.FOLLOWER for node in cluster.nodes.values()); \
print('✅ etcd Cluster: initialization tests passed'); \
client = gc.EtcdGrpcClient(['etcd-1:2379', 'etcd-2:2379']); \
assert len(client.endpoints) == 2; \
assert client.timeout == 5.0; \
assert client.retry_attempts == 3; \
print('✅ gRPC Client: initialization tests passed'); \
resource = ki.KubernetesResource('v1', 'Pod', {'name': 'test', 'namespace': 'default'}); \
assert resource.api_version == 'v1'; \
assert resource.kind == 'Pod'; \
assert resource.to_etcd_key() == '/registry/pods/default/test'; \
print('✅ Kubernetes Integration: resource tests passed'); \
print('🎯 All etcd gRPC tests passed!')"

clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f *.png
	@rm -rf __pycache__/
	@echo "✅ Cleanup completed"

summary:
	@echo ""
	@echo "=== etcd gRPC Summary ==="
	@echo "📋 Protocol: etcd Raft-backed Key-Value Store with gRPC"
	@echo "🎯 Purpose: Distributed coordination and cluster state management"
	@echo "🔧 Features: Raft consensus, gRPC API, watch streams, transactions"
	@echo "⚡ Benefits: Strong consistency, fault tolerance, high performance"
	@echo "🌐 Use Cases: Kubernetes cluster state, service discovery, configuration"
	@echo ""
