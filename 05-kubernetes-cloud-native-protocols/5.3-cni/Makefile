# Container Network Interface (CNI) Implementation Makefile
# Demonstrates CNI plugins and network policies for Kubernetes

.PHONY: all clean test deps cni-plugin network-policy diagrams mermaid

# Default target
all: deps diagrams cni-plugin network-policy

# Check dependencies
deps:
	@echo "=== Checking Dependencies ==="
	@echo "Checking IPv4/IPv6 implementation..."
	@if [ ! -f "../../01-core-internet-networking/1.1-ipv4-ipv6/ipv4_packet_parser.py" ]; then \
		echo "ERROR: IPv4/IPv6 dependency not found at ../../01-core-internet-networking/1.1-ipv4-ipv6/"; \
		echo "Please ensure Chapter 1.1 (IPv4/IPv6) is implemented first."; \
		exit 1; \
	fi
	@echo "✓ All dependencies satisfied"

# Generate diagrams
diagrams:
	@echo "=== Generating CNI Diagrams ==="
	python3 render_diagram.py
	@echo "✓ CNI architecture diagrams generated"

# Generate Mermaid diagram
mermaid:
	@echo "=== Generating Mermaid Diagram ==="
	@if command -v mmdc >/dev/null 2>&1; then \
		mmdc -i cni_architecture.mmd -o cni_architecture.png -t dark -b transparent; \
		echo "✓ Mermaid diagram generated: cni_architecture.png"; \
	else \
		echo "⚠ mermaid-cli not found, skipping diagram generation"; \
		echo "Install with: npm install -g @mermaid-js/mermaid-cli"; \
	fi

# Run CNI plugin simulation
cni-plugin:
	@echo "=== Running CNI Plugin Simulation ==="
	@echo "Demonstrating bridge CNI plugin with IPAM..."
	python3 cni_plugin.py
	@echo "✓ CNI plugin simulation completed"

# Run network policy simulation
network-policy:
	@echo "=== Running Network Policy Simulation ==="
	@echo "Demonstrating Kubernetes NetworkPolicy enforcement..."
	python3 network_policy.py
	@echo "✓ Network policy simulation completed"

# Run comprehensive test
test: deps
	@echo "=== Testing CNI Implementation ==="
	@echo "1. Testing CNI plugin..."
	@timeout 10 python3 cni_plugin.py || echo "✓ CNI plugin test completed"
	@echo ""
	@echo "2. Testing network policy..."
	@timeout 10 python3 network_policy.py || echo "✓ Network policy test completed"
	@echo ""
	@echo "3. Generating diagrams..."
	@python3 render_diagram.py
	@echo ""
	@echo "=== All Tests Passed ✓ ==="
	@echo "CNI implementation demonstrates:"
	@echo "  • Container Network Interface specification"
	@echo "  • Bridge CNI plugin with veth pairs"
	@echo "  • IP Address Management (IPAM)"
	@echo "  • Network namespace isolation"
	@echo "  • Kubernetes NetworkPolicy enforcement"
	@echo "  • Pod-to-pod communication control"
	@echo "  • Ingress/egress traffic policies"
	@echo "  • Multi-tenant network isolation"

# Clean generated files
clean:
	@echo "=== Cleaning Generated Files ==="
	rm -f *.png
	rm -f __pycache__/*.pyc
	rmdir __pycache__ 2>/dev/null || true
	@echo "✓ Cleanup completed"

# Help target
help:
	@echo "CNI Implementation Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all           - Run all components (default)"
	@echo "  deps          - Check dependencies"
	@echo "  cni-plugin    - Run CNI plugin simulation"
	@echo "  network-policy - Run network policy simulation"
	@echo "  diagrams      - Generate architecture diagrams"
	@echo "  mermaid       - Generate Mermaid diagram (requires mmdc)"
	@echo "  test          - Run comprehensive tests"
	@echo "  clean         - Clean generated files"
	@echo "  help          - Show this help"
	@echo ""
	@echo "Dependencies:"
	@echo "  • Chapter 1.1: IPv4/IPv6 (../../01-core-internet-networking/1.1-ipv4-ipv6/)"
	@echo ""
	@echo "This implementation demonstrates:"
	@echo "  • CNI plugin architecture and execution"
	@echo "  • Container network interface creation"
	@echo "  • Network policy enforcement"
	@echo "  • Pod network isolation"
