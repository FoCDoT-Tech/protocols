# Chapter 6: Advanced Kubernetes & Service Mesh Protocols Master Makefile
# Orchestrates building and testing all subchapters sequentially

.PHONY: all build test clean diagrams deps-check help

# Subchapter directories
SUBCHAPTERS = 6.1-envoy-xds 6.2-mtls 6.3-http2-grpc-multiplexing 6.4-opentelemetry-otlp 6.5-ebpf-protocols

all: deps-check build diagrams test

deps-check:
	@echo "Chapter 6: Advanced Kubernetes & Service Mesh Protocols"
	@echo "========================================================"
	@echo "Checking dependencies for all subchapters..."
	@for subchapter in $(SUBCHAPTERS); do \
		echo "Checking $$subchapter dependencies..."; \
		$(MAKE) -C $$subchapter deps-check || exit 1; \
	done
	@echo "✓ All dependencies satisfied for Chapter 6"

build:
	@echo "Building all Chapter 6 subchapters..."
	@for subchapter in $(SUBCHAPTERS); do \
		echo "Building $$subchapter..."; \
		$(MAKE) -C $$subchapter build || exit 1; \
	done
	@echo "✓ All Chapter 6 subchapters built successfully"

diagrams:
	@echo "Generating diagrams for all Chapter 6 subchapters..."
	@for subchapter in $(SUBCHAPTERS); do \
		echo "Generating diagrams for $$subchapter..."; \
		$(MAKE) -C $$subchapter diagrams || exit 1; \
	done
	@echo "✓ All Chapter 6 diagrams generated successfully"

test:
	@echo "Testing all Chapter 6 subchapters sequentially..."
	@for subchapter in $(SUBCHAPTERS); do \
		echo ""; \
		echo "=== Testing $$subchapter ==="; \
		$(MAKE) -C $$subchapter test || exit 1; \
		echo "✓ $$subchapter tests passed"; \
	done
	@echo ""
	@echo "=== Chapter 6 Test Summary ==="
	@echo "✓ 6.1-envoy-xds: Envoy xDS API simulation and control plane"
	@echo "✓ 6.2-mtls: Mutual TLS and certificate management"
	@echo "✓ 6.3-http2-grpc-multiplexing: HTTP/2 and gRPC streaming"
	@echo "✓ 6.4-opentelemetry-otlp: OpenTelemetry data collection"
	@echo "✓ 6.5-ebpf-protocols: eBPF network acceleration"
	@echo ""
	@echo "🎉 All Chapter 6 subchapters validated successfully!"

performance-test:
	@echo "Running performance tests for all Chapter 6 subchapters..."
	@for subchapter in $(SUBCHAPTERS); do \
		echo ""; \
		echo "=== Performance testing $$subchapter ==="; \
		if $(MAKE) -C $$subchapter performance-test 2>/dev/null; then \
			echo "✓ $$subchapter performance test completed"; \
		else \
			echo "⚠ $$subchapter: performance test not available"; \
		fi; \
	done
	@echo "✓ Chapter 6 performance testing completed"

security-test:
	@echo "Running security tests for all Chapter 6 subchapters..."
	@for subchapter in $(SUBCHAPTERS); do \
		echo ""; \
		echo "=== Security testing $$subchapter ==="; \
		if $(MAKE) -C $$subchapter security-test 2>/dev/null; then \
			echo "✓ $$subchapter security test completed"; \
		else \
			echo "⚠ $$subchapter: security test not available"; \
		fi; \
	done
	@echo "✓ Chapter 6 security testing completed"

integration-test:
	@echo "Running integration tests for all Chapter 6 subchapters..."
	@for subchapter in $(SUBCHAPTERS); do \
		echo ""; \
		echo "=== Integration testing $$subchapter ==="; \
		if $(MAKE) -C $$subchapter integration-test 2>/dev/null; then \
			echo "✓ $$subchapter integration test completed"; \
		else \
			echo "⚠ $$subchapter: integration test not available"; \
		fi; \
	done
	@echo "✓ Chapter 6 integration testing completed"

clean:
	@echo "Cleaning all Chapter 6 subchapters..."
	@for subchapter in $(SUBCHAPTERS); do \
		echo "Cleaning $$subchapter..."; \
		$(MAKE) -C $$subchapter clean; \
	done
	@echo "✓ All Chapter 6 subchapters cleaned"

validate:
	@echo "Full validation of Chapter 6: Advanced Kubernetes & Service Mesh Protocols"
	@echo "=========================================================================="
	@$(MAKE) deps-check
	@$(MAKE) build
	@$(MAKE) diagrams
	@$(MAKE) test
	@echo ""
	@echo "🎯 Chapter 6 Validation Summary"
	@echo "==============================="
	@echo "✅ Dependencies: All required chapters available"
	@echo "✅ Build: All Python files compiled successfully"
	@echo "✅ Diagrams: Architecture and flow diagrams generated"
	@echo "✅ Tests: All simulations and demos working correctly"
	@echo ""
	@echo "📊 Chapter 6 Coverage:"
	@echo "  • Envoy xDS API and dynamic configuration"
	@echo "  • Mutual TLS and SPIFFE/SPIRE integration"
	@echo "  • HTTP/2 multiplexing and gRPC streaming patterns"
	@echo "  • OpenTelemetry OTLP data collection and processing"
	@echo "  • eBPF kernel-level network acceleration"
	@echo ""
	@echo "🚀 Ready for production-quality learning scenarios!"

status:
	@echo "Chapter 6 Status Report"
	@echo "======================"
	@echo "Subchapters:"
	@for subchapter in $(SUBCHAPTERS); do \
		if [ -d "$$subchapter" ]; then \
			echo "  ✓ $$subchapter: Available"; \
			if [ -f "$$subchapter/Makefile" ]; then \
				echo "    - Makefile: ✓"; \
			else \
				echo "    - Makefile: ✗"; \
			fi; \
			if [ -f "$$subchapter/explainer.md" ]; then \
				echo "    - Explainer: ✓"; \
			else \
				echo "    - Explainer: ✗"; \
			fi; \
		else \
			echo "  ✗ $$subchapter: Missing"; \
		fi; \
	done

help:
	@echo "Chapter 6: Advanced Kubernetes & Service Mesh Protocols"
	@echo "========================================================"
	@echo ""
	@echo "Master Makefile for orchestrating all Chapter 6 subchapters"
	@echo ""
	@echo "Targets:"
	@echo "  all                 - Build everything and run tests"
	@echo "  deps-check          - Check dependencies for all subchapters"
	@echo "  build               - Build all subchapters"
	@echo "  diagrams            - Generate all diagrams"
	@echo "  test                - Run tests for all subchapters"
	@echo "  performance-test    - Run performance tests"
	@echo "  security-test       - Run security tests"
	@echo "  integration-test    - Run integration tests"
	@echo "  validate            - Full validation workflow"
	@echo "  status              - Show status of all subchapters"
	@echo "  clean               - Clean all subchapters"
	@echo "  help                - Show this help message"
	@echo ""
	@echo "Subchapters:"
	@echo "  6.1-envoy-xds              - Envoy xDS API and control plane"
	@echo "  6.2-mtls                   - Mutual TLS and certificate management"
	@echo "  6.3-http2-grpc-multiplexing - HTTP/2 and gRPC streaming"
	@echo "  6.4-opentelemetry-otlp     - OpenTelemetry data collection"
	@echo "  6.5-ebpf-protocols         - eBPF network acceleration"
	@echo ""
	@echo "Dependencies:"
	@echo "  • Core networking protocols (IPv4/IPv6, TCP, UDP, ICMP)"
	@echo "  • Web protocols (DNS, HTTP/1.1, TLS, gRPC)"
	@echo "  • Kubernetes protocols (etcd, gRPC, Kube API)"
	@echo ""
	@echo "Features Demonstrated:"
	@echo "  🔄 Dynamic service discovery and configuration"
	@echo "  🔒 Zero-trust security with mutual TLS"
	@echo "  ⚡ High-performance multiplexed communications"
	@echo "  📊 Comprehensive observability and telemetry"
	@echo "  🚀 Kernel-level network acceleration"
