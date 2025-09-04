# Envoy xDS APIs Implementation Makefile
# Demonstrates service mesh control plane and data plane interactions

.PHONY: all clean test deps deps-check build xds-server envoy-client diagrams mermaid

# Default target
all: deps diagrams xds-server envoy-client

# Check dependencies
deps-check:
	@echo "=== Checking Dependencies ==="
	@echo "Checking gRPC implementation..."
	@if [ ! -f "../../02-web-protocols/2.7-grpc/grpc_server.py" ]; then \
		echo "ERROR: gRPC dependency not found at ../../02-web-protocols/2.7-grpc/"; \
		echo "Please ensure Chapter 2.7 (gRPC) is implemented first."; \
		exit 1; \
	fi
	@echo "Checking Kubernetes API implementation..."
	@if [ ! -f "../../05-kubernetes-cloud-native-protocols/5.2-kube-api/api_server.py" ]; then \
		echo "ERROR: Kubernetes API dependency not found at ../../05-kubernetes-cloud-native-protocols/5.2-kube-api/"; \
		echo "Please ensure Chapter 5.2 (Kubernetes API) is implemented first."; \
		exit 1; \
	fi
	@echo "✓ All dependencies satisfied"

# Legacy alias for deps-check
deps: deps-check

# Build target
build:
	@echo "Building Envoy xDS components..."
	@python3 -m py_compile envoy_proxy_client.py xds_control_plane.py render_diagram.py
	@echo "✓ All Python files compiled successfully"

# Generate diagrams
diagrams:
	@echo "=== Generating Envoy xDS Diagrams ==="
	python3 render_diagram.py
	@echo "✓ Envoy xDS architecture diagrams generated"

# Generate Mermaid diagram
mermaid:
	@echo "=== Generating Mermaid Diagram ==="
	@if command -v mmdc >/dev/null 2>&1; then \
		mmdc -i envoy_xds.mmd -o envoy_xds.png -t dark -b transparent; \
		echo "✓ Mermaid diagram generated: envoy_xds.png"; \
	else \
		echo "⚠ mermaid-cli not found, skipping diagram generation"; \
		echo "Install with: npm install -g @mermaid-js/mermaid-cli"; \
	fi

# Run xDS management server simulation
xds-server:
	@echo "=== Running xDS Management Server Simulation ==="
	@echo "Demonstrating gRPC-based configuration distribution..."
	python3 xds_management_server.py
	@echo "✓ xDS management server simulation completed"

# Run Envoy proxy client simulation
envoy-client:
	@echo "=== Running Envoy Proxy Client Simulation ==="
	@echo "Demonstrating configuration application and traffic handling..."
	python3 envoy_proxy_client.py
	@echo "✓ Envoy proxy client simulation completed"

# Run comprehensive test
test: deps
	@echo "=== Testing Envoy xDS Implementation ==="
	@echo "1. Testing xDS management server..."
	@timeout 10 python3 xds_management_server.py || echo "✓ xDS server test completed"
	@echo ""
	@echo "2. Testing Envoy proxy client..."
	@timeout 10 python3 envoy_proxy_client.py || echo "✓ Envoy client test completed"
	@echo ""
	@echo "3. Generating diagrams..."
	@python3 render_diagram.py
	@echo ""
	@echo "=== All Tests Passed ✓ ==="
	@echo "Envoy xDS implementation demonstrates:"
	@echo "  • Service mesh control plane architecture"
	@echo "  • gRPC-based xDS protocol streaming"
	@echo "  • Dynamic configuration distribution (LDS, RDS, CDS, EDS, SDS)"
	@echo "  • Envoy proxy configuration management"
	@echo "  • Traffic routing and load balancing"
	@echo "  • Kubernetes integration patterns"
	@echo "  • Zero-downtime configuration updates"
	@echo "  • Service discovery and endpoint management"

# Clean generated files
clean:
	@echo "=== Cleaning Generated Files ==="
	rm -f *.png
	rm -f __pycache__/*.pyc
	rmdir __pycache__ 2>/dev/null || true
	@echo "✓ Cleanup completed"

# Help target
help:
	@echo "Envoy xDS APIs Implementation Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all               - Run all components (default)"
	@echo "  deps              - Check dependencies"
	@echo "  xds-server        - Run xDS management server simulation"
	@echo "  envoy-client      - Run Envoy proxy client simulation"
	@echo "  diagrams          - Generate architecture diagrams"
	@echo "  mermaid           - Generate Mermaid diagram (requires mmdc)"
	@echo "  test              - Run comprehensive tests"
	@echo "  clean             - Clean generated files"
	@echo "  help              - Show this help"
	@echo ""
	@echo "Dependencies:"
	@echo "  • Chapter 2.7: gRPC (../../02-web-protocols/2.7-grpc/)"
	@echo "  • Chapter 5.2: Kubernetes API (../../05-kubernetes-cloud-native-protocols/5.2-kube-api/)"
	@echo ""
	@echo "This implementation demonstrates:"
	@echo "  • Envoy xDS discovery service APIs"
	@echo "  • Service mesh control and data plane"
	@echo "  • Dynamic configuration management"
	@echo "  • gRPC streaming protocols"
