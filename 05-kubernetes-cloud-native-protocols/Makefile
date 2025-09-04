# Chapter 5: Kubernetes & Cloud-Native Protocols Master Makefile
# Orchestrates all subchapter builds and tests

.PHONY: all clean test deps help
.PHONY: etcd-grpc kube-api cni csi prometheus
.PHONY: test-etcd-grpc test-kube-api test-cni test-csi test-prometheus

# Subchapter directories
SUBCHAPTERS = 5.1-etcd-grpc 5.2-kube-api 5.3-cni 5.4-csi 5.5-prometheus

# Default target - run all subchapters
all: deps $(SUBCHAPTERS)

# Check dependencies for all subchapters
deps:
	@echo "=== Checking Chapter 5 Dependencies ==="
	@echo "Verifying all required protocol implementations..."
	@for dir in $(SUBCHAPTERS); do \
		echo "Checking dependencies for $$dir..."; \
		$(MAKE) -C $$dir deps || exit 1; \
	done
	@echo "✓ All Chapter 5 dependencies satisfied"

# Individual subchapter targets
etcd-grpc:
	@echo "=== Building 5.1 etcd gRPC ==="
	$(MAKE) -C 5.1-etcd-grpc all

kube-api:
	@echo "=== Building 5.2 Kubernetes API ==="
	$(MAKE) -C 5.2-kube-api all

cni:
	@echo "=== Building 5.3 CNI ==="
	$(MAKE) -C 5.3-cni all

csi:
	@echo "=== Building 5.4 CSI ==="
	$(MAKE) -C 5.4-csi all

prometheus:
	@echo "=== Building 5.5 Prometheus ==="
	$(MAKE) -C 5.5-prometheus all

# Individual test targets
test-etcd-grpc:
	@echo "=== Testing 5.1 etcd gRPC ==="
	$(MAKE) -C 5.1-etcd-grpc test

test-kube-api:
	@echo "=== Testing 5.2 Kubernetes API ==="
	$(MAKE) -C 5.2-kube-api test

test-cni:
	@echo "=== Testing 5.3 CNI ==="
	$(MAKE) -C 5.3-cni test

test-csi:
	@echo "=== Testing 5.4 CSI ==="
	$(MAKE) -C 5.4-csi test

test-prometheus:
	@echo "=== Testing 5.5 Prometheus ==="
	$(MAKE) -C 5.5-prometheus test

# Comprehensive test suite
test: deps
	@echo "=========================================="
	@echo "Chapter 5: Kubernetes & Cloud-Native Protocols"
	@echo "Comprehensive Test Suite"
	@echo "=========================================="
	@echo ""
	
	@echo "Testing subchapter 5.1: etcd gRPC..."
	@$(MAKE) -C 5.1-etcd-grpc test
	@echo ""
	
	@echo "Testing subchapter 5.2: Kubernetes API..."
	@$(MAKE) -C 5.2-kube-api test
	@echo ""
	
	@echo "Testing subchapter 5.3: CNI..."
	@$(MAKE) -C 5.3-cni test
	@echo ""
	
	@echo "Testing subchapter 5.4: CSI..."
	@$(MAKE) -C 5.4-csi test
	@echo ""
	
	@echo "Testing subchapter 5.5: Prometheus..."
	@$(MAKE) -C 5.5-prometheus test
	@echo ""
	
	@echo "=========================================="
	@echo "✅ Chapter 5 Complete Test Results ✅"
	@echo "=========================================="
	@echo ""
	@echo "All Kubernetes & Cloud-Native Protocol implementations:"
	@echo ""
	@echo "🔹 5.1 etcd gRPC:"
	@echo "   • Raft-backed distributed key-value store"
	@echo "   • gRPC protocol for client-server communication"
	@echo "   • Kubernetes control plane data persistence"
	@echo "   • Leader election and consensus algorithms"
	@echo ""
	@echo "🔹 5.2 Kubernetes API Server:"
	@echo "   • RESTful HTTP/1.1 + TLS API interface"
	@echo "   • Authentication, authorization, admission control"
	@echo "   • Resource lifecycle management"
	@echo "   • Watch streams for real-time updates"
	@echo ""
	@echo "🔹 5.3 Container Network Interface (CNI):"
	@echo "   • Container networking specification"
	@echo "   • Network namespace isolation"
	@echo "   • IPAM and bridge networking"
	@echo "   • NetworkPolicy enforcement"
	@echo ""
	@echo "🔹 5.4 Container Storage Interface (CSI):"
	@echo "   • Storage driver specification"
	@echo "   • Dynamic volume provisioning"
	@echo "   • Volume lifecycle management"
	@echo "   • Multi-backend storage support"
	@echo ""
	@echo "🔹 5.5 Prometheus Exposition Format:"
	@echo "   • Metrics exposition over HTTP/1.1"
	@echo "   • Time-series data collection"
	@echo "   • Service discovery and scraping"
	@echo "   • Multi-dimensional monitoring"
	@echo ""
	@echo "🎯 Protocol Dependencies Validated:"
	@echo "   • Chapter 1.1: IPv4/IPv6 (networking foundation)"
	@echo "   • Chapter 2.2: HTTP/1.1 (API and metrics transport)"
	@echo "   • Chapter 2.3: TLS (secure communication)"
	@echo "   • Chapter 2.7: gRPC (high-performance RPC)"
	@echo "   • Chapter 4.1: Raft (consensus algorithms)"
	@echo ""
	@echo "🚀 Real-world Engineering Applications:"
	@echo "   • Production Kubernetes cluster management"
	@echo "   • Cloud-native application deployment"
	@echo "   • Container orchestration at scale"
	@echo "   • Microservices architecture patterns"
	@echo "   • DevOps and SRE operational practices"
	@echo ""
	@echo "=========================================="

# Clean all subchapters
clean:
	@echo "=== Cleaning Chapter 5 ==="
	@for dir in $(SUBCHAPTERS); do \
		echo "Cleaning $$dir..."; \
		$(MAKE) -C $$dir clean; \
	done
	@echo "✓ Chapter 5 cleanup completed"

# Help target
help:
	@echo "Chapter 5: Kubernetes & Cloud-Native Protocols"
	@echo "=============================================="
	@echo ""
	@echo "Available targets:"
	@echo "  all              - Build all subchapters (default)"
	@echo "  test             - Run comprehensive test suite"
	@echo "  deps             - Check all dependencies"
	@echo "  clean            - Clean all generated files"
	@echo ""
	@echo "Individual subchapter targets:"
	@echo "  etcd-grpc        - Build 5.1 etcd gRPC"
	@echo "  kube-api         - Build 5.2 Kubernetes API"
	@echo "  cni              - Build 5.3 CNI"
	@echo "  csi              - Build 5.4 CSI"
	@echo "  prometheus       - Build 5.5 Prometheus"
	@echo ""
	@echo "Individual test targets:"
	@echo "  test-etcd-grpc   - Test 5.1 etcd gRPC"
	@echo "  test-kube-api    - Test 5.2 Kubernetes API"
	@echo "  test-cni         - Test 5.3 CNI"
	@echo "  test-csi         - Test 5.4 CSI"
	@echo "  test-prometheus  - Test 5.5 Prometheus"
	@echo ""
	@echo "Chapter 5 covers essential Kubernetes and cloud-native protocols:"
	@echo "• etcd: Distributed key-value store with Raft consensus"
	@echo "• Kubernetes API: RESTful control plane interface"
	@echo "• CNI: Container networking specification"
	@echo "• CSI: Container storage interface"
	@echo "• Prometheus: Metrics exposition and monitoring"
	@echo ""
	@echo "Dependencies:"
	@echo "• Chapter 1.1: IPv4/IPv6"
	@echo "• Chapter 2.2: HTTP/1.1"
	@echo "• Chapter 2.3: TLS"
	@echo "• Chapter 2.7: gRPC"
	@echo "• Chapter 4.1: Raft consensus"
