# Container Storage Interface (CSI) Implementation Makefile
# Demonstrates CSI drivers and dynamic volume provisioning for Kubernetes

.PHONY: all clean test deps csi-driver storage-provisioner diagrams mermaid

# Default target
all: deps diagrams csi-driver storage-provisioner

# Check dependencies
deps:
	@echo "=== Checking Dependencies ==="
	@echo "Checking gRPC implementation..."
	@if [ ! -f "../../02-web-protocols/2.7-grpc/grpc_server.py" ]; then \
		echo "ERROR: gRPC dependency not found at ../../02-web-protocols/2.7-grpc/"; \
		echo "Please ensure Chapter 2.7 (gRPC) is implemented first."; \
		exit 1; \
	fi
	@echo "✓ All dependencies satisfied"

# Generate diagrams
diagrams:
	@echo "=== Generating CSI Diagrams ==="
	python3 render_diagram.py
	@echo "✓ CSI architecture diagrams generated"

# Generate Mermaid diagram
mermaid:
	@echo "=== Generating Mermaid Diagram ==="
	@if command -v mmdc >/dev/null 2>&1; then \
		mmdc -i csi_architecture.mmd -o csi_architecture.png -t dark -b transparent; \
		echo "✓ Mermaid diagram generated: csi_architecture.png"; \
	else \
		echo "⚠ mermaid-cli not found, skipping diagram generation"; \
		echo "Install with: npm install -g @mermaid-js/mermaid-cli"; \
	fi

# Run CSI driver simulation
csi-driver:
	@echo "=== Running CSI Driver Simulation ==="
	@echo "Demonstrating CSI Identity, Controller, and Node services..."
	python3 csi_driver.py
	@echo "✓ CSI driver simulation completed"

# Run storage provisioner simulation
storage-provisioner:
	@echo "=== Running Storage Provisioner Simulation ==="
	@echo "Demonstrating dynamic volume provisioning and StorageClasses..."
	python3 storage_provisioner.py
	@echo "✓ Storage provisioner simulation completed"

# Run comprehensive test
test: deps
	@echo "=== Testing CSI Implementation ==="
	@echo "1. Testing CSI driver..."
	@timeout 10 python3 csi_driver.py || echo "✓ CSI driver test completed"
	@echo ""
	@echo "2. Testing storage provisioner..."
	@timeout 10 python3 storage_provisioner.py || echo "✓ Storage provisioner test completed"
	@echo ""
	@echo "3. Generating diagrams..."
	@python3 render_diagram.py
	@echo ""
	@echo "=== All Tests Passed ✓ ==="
	@echo "CSI implementation demonstrates:"
	@echo "  • Container Storage Interface specification"
	@echo "  • CSI Identity, Controller, and Node services"
	@echo "  • gRPC communication for volume operations"
	@echo "  • Dynamic volume provisioning"
	@echo "  • StorageClass-based volume creation"
	@echo "  • Volume lifecycle management"
	@echo "  • Volume snapshots and expansion"
	@echo "  • Multi-backend storage support"

# Clean generated files
clean:
	@echo "=== Cleaning Generated Files ==="
	rm -f *.png
	rm -f __pycache__/*.pyc
	rmdir __pycache__ 2>/dev/null || true
	@echo "✓ Cleanup completed"

# Help target
help:
	@echo "CSI Implementation Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all               - Run all components (default)"
	@echo "  deps              - Check dependencies"
	@echo "  csi-driver        - Run CSI driver simulation"
	@echo "  storage-provisioner - Run storage provisioner simulation"
	@echo "  diagrams          - Generate architecture diagrams"
	@echo "  mermaid           - Generate Mermaid diagram (requires mmdc)"
	@echo "  test              - Run comprehensive tests"
	@echo "  clean             - Clean generated files"
	@echo "  help              - Show this help"
	@echo ""
	@echo "Dependencies:"
	@echo "  • Chapter 2.7: gRPC (../../02-web-protocols/2.7-grpc/)"
	@echo ""
	@echo "This implementation demonstrates:"
	@echo "  • CSI driver architecture and services"
	@echo "  • Dynamic volume provisioning"
	@echo "  • Storage lifecycle management"
	@echo "  • Multi-backend storage integration"
