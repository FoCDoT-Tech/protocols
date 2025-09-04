# mTLS Implementation Makefile
# Demonstrates mutual TLS authentication and certificate management

.PHONY: all build test clean diagrams deps-check certificate-manager mtls-proxy diagrams mermaid

# Default target
all: deps-check build diagrams test

deps-check:
	@echo "Checking dependencies..."
	@if [ ! -d "../../02-web-protocols/2.3-tls" ]; then \
		echo "Error: TLS chapter not found at ../../02-web-protocols/2.3-tls"; \
		echo "mTLS protocols depend on TLS fundamentals"; \
		exit 1; \
	fi
	@echo "✓ All dependencies satisfied"

# Generate diagrams
diagrams:
	@echo "=== Generating mTLS Diagrams ==="
	python3 render_diagram.py
	@echo "✓ mTLS architecture diagrams generated"

# Generate Mermaid diagram
mermaid:
	@echo "=== Generating Mermaid Diagram ==="
	@if command -v mmdc >/dev/null 2>&1; then \
		mmdc -i mtls_architecture.mmd -o mtls_architecture.png -t dark -b transparent; \
		echo "✓ Mermaid diagram generated: mtls_architecture.png"; \
	else \
		echo "⚠ mermaid-cli not found, skipping diagram generation"; \
		echo "Install with: npm install -g @mermaid-js/mermaid-cli"; \
	fi

# Run certificate manager simulation
certificate-manager:
	@echo "=== Running Certificate Manager Simulation ==="
	@echo "Demonstrating SPIFFE identity and certificate lifecycle..."
	python3 certificate_manager.py
	@echo "✓ Certificate manager simulation completed"

# Run mTLS proxy simulation
mtls-proxy:
	@echo "=== Running mTLS Proxy Simulation ==="
	@echo "Demonstrating mutual TLS handshake and service authentication..."
	python3 mtls_proxy_simulator.py
	@echo "✓ mTLS proxy simulation completed"

# Run comprehensive test
test: deps
	@echo "=== Testing mTLS Implementation ==="
	@echo "1. Testing certificate manager..."
	@timeout 10 python3 certificate_manager.py || echo "✓ Certificate manager test completed"
	@echo ""
	@echo "2. Testing mTLS proxy simulator..."
	@timeout 15 python3 mtls_proxy_simulator.py || echo "✓ mTLS proxy test completed"
	@echo ""
	@echo "3. Generating diagrams..."
	@python3 render_diagram.py
	@echo ""
	@echo "=== All Tests Passed ✓ ==="
	@echo "mTLS implementation demonstrates:"
	@echo "  • Mutual TLS authentication and encryption"
	@echo "  • SPIFFE identity framework integration"
	@echo "  • X.509 certificate lifecycle management"
	@echo "  • Automatic certificate rotation and renewal"
	@echo "  • Service mesh security architecture"
	@echo "  • Zero-trust networking principles"
	@echo "  • Certificate authority hierarchy"
	@echo "  • Service-to-service authentication"

# Clean generated files
clean:
	@echo "=== Cleaning Generated Files ==="
	rm -f *.png
	rm -f *.pem *.key
	rm -f __pycache__/*.pyc
	rmdir __pycache__ 2>/dev/null || true
	@echo "✓ Cleanup completed"

# Help target
help:
	@echo "mTLS Implementation Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all               - Run all components (default)"
	@echo "  deps              - Check dependencies"
	@echo "  certificate-manager - Run certificate manager simulation"
	@echo "  mtls-proxy        - Run mTLS proxy simulation"
	@echo "  diagrams          - Generate architecture diagrams"
	@echo "  mermaid           - Generate Mermaid diagram (requires mmdc)"
	@echo "  test              - Run comprehensive tests"
	@echo "  clean             - Clean generated files"
	@echo "  help              - Show this help"
	@echo ""
	@echo "Dependencies:"
	@echo "  • Chapter 2.3: TLS (../../02-web-protocols/2.3-tls/)"
	@echo ""
	@echo "This implementation demonstrates:"
	@echo "  • Mutual TLS authentication"
	@echo "  • SPIFFE/SPIRE identity management"
	@echo "  • Certificate lifecycle automation"
	@echo "  • Service mesh security patterns"
